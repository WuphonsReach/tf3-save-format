#!/usr/bin/env python3
"""Summarise TF3 savegames (for example ones from the mod.io catalog) as JSON facts and draw each one's map.

Usage: mine_saves.py [--no-maps] [--no-nice] [--mapper tf3map|python] [--tf3map BIN] [--game DIR] [--mods DIR]
                     OUT_DIR SAVE_OR_MODDIR [...]

Reads only. For every save it writes OUT_DIR/<c>/<seed>/<id>-<name>/tf3-save-summary.json
(layout: schema/tf3-save-summary.v<N>.schema.json next to this script) and rebuilds
OUT_DIR/index.csv from every summary there (it has the map's size name and format ratio as stored in the
settings, with their positions, next to the width and height in metres, the save's file name in `source_name` (the load list shows it, not the
catalog `name`), and the mod keys as a `;`-separated list in `mod_list`). <seed> is the map seed from the header and <c>
its first character, so OUT_DIR holds few folders and the saves of one game (and the editor
maps made from the same seed) sit together. A save without a seed (truncated, or a format
that has none) goes to OUT_DIR/_noseed/<id>-<name>. A summary found in another place (an
older flat layout, or after a changed seed) is moved, not read again; a run with no save
arguments moves every summary and rewrites index.csv. A summary.json left by an older
version in the same folder is removed. A SAVE_OR_MODDIR can be a
.sav or a mod.io mod directory (.../mods/<id>) whose savegames/ or maps/
folder holds one. A map-editor map (maps/) is written to <id>-<name>-map, so a
mod that ships both a savegame and a map keeps two summaries. Catalog name, tags, author and link come from mod.io's metadata/state.json
when it is found next to the mods directory.

The summary is built by mine_summary.py (what is read from a save is described there; run alone it prints one).
Next to each summary this script also writes terrain-map.svg, the default map of the drawer `--mapper` names (the
vector terrain, the roads and rails, the stations, depots and industries when the game install is found, the default
grid and compass rose; docs/terrain-drawing.md), so the picture follows that drawer's current defaults:
- `tf3map` (the default): the Rust mapper of the tf3-save-mapper repo, one `tf3map SAVE -o terrain-map.svg` child per
  save (well under 2 s a save). The binary is `--tf3map BIN`, else $TF3MAP, else `tf3map` on the PATH, else the
  release build in the sibling tf3-save-mapper checkout (target/release/tf3map). It needs a build whose SVG carries
  the `tf3map:view` metadata record and whose exit status tells a refused save (3) from other failures (1, 2):
  mapper 0.5.0 or later;
- `python`: terrain_map.py with no options, one `python3 -I terrain_map.py` child per save (44 to 310 s a save).
`--game DIR` (the install folder that holds base/) and `--mods DIR` (the mod.io game's mods folder) are passed to
the drawer, for the footprints and a mod depot's catchment, when its child would not find the usual Steam folders on
its own (a different HOME); the summary does not use them. `--no-maps` skips the pictures. A save the drawer cannot
draw gets no picture (a stale one is removed); .map_state.json beside the summary says which drawer ran and how it
ended, as `status`: `ok`, `refused: REASON` (the reader refused the save) or `failed: REASON` (anything else), with
the same text in `error` (null when ok) and the drawer's other stderr lines, warnings of a run that worked, in
`notes`. A path in REASON or a note is cut to the save's file name or `~`; the state stays in OUT_DIR all the same.
Pictures are other people's maps: they stay in OUT_DIR, which is never committed. terrain_map.py needs about 2.5 GB
of memory for a Giant map, so keep the parallel runs few (xargs -P4) on a small machine. The script lowers its own
priority at start (nice 19, and idle I/O when `ionice` is installed; the map-drawing child processes inherit it) so
a long run leaves the machine usable; `--no-nice` keeps the normal priority.

Two things are rebuilt separately, each when the save changed or its own scripts did:
- the summary, when the commit of mine_summary.py and the modules it imports (save_header.py, tf3save.py) differs
  from the one in the summary's `tools_commit`;
- the map, when the drawer's key differs from the one in .map_state.json. For `python` the key is the commit of
  terrain_map.py and the modules it imports; for `tf3map` it is the git commit the binary names in `tf3map --version`
  (`tf3map 0.5.0 (bfe77c7388)`): use a build of the mapper's main branch, so the key is main's commit, and a new
  main commit redraws the maps. Changing drawer redraws them too. The run says so when the commit is not on main
  of the sibling mapper checkout.
A change to tf3save.py is in both sets and rebuilds both; one to terrain_map.py, terrain_vector.py or street_edges.py
redraws the python maps and leaves the summaries; one to mine_summary.py rebuilds the summaries only. A set with
uncommitted changes ("-dirty", also after the tf3map commit) is always rebuilt. A tf3map built without git
prints only its version, so its maps are redrawn only when the version changes: mine one set with one kind of
build. `script_commits.py SCRIPT` lists a set and its commit.

Safe to re-run while mod.io is still downloading: a save whose size and mtime
match the last run is skipped, and a save that fails to read gets an error
summary and is retried next run. The size and mtime are kept in a
.mine_state.json (summary) and .map_state.json (map) next to each summary, not in the summary, so summaries hold
no local paths or timestamps. The summary takes about 8 s for a small save; the map with tf3map about 0.1 s for
a small save and 1.3 s for a busy 190 MB one, with terrain_map.py minutes (2026-10-24, tf3map at 0c82fa4). For
many saves run several at once, for example with `xargs -P8 -n4`.
"""
import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mine_summary import (INDEX_COLS, OLD_SUMMARY_FILE, SUMMARY_FILE, catalog_profiles, index_row,  # noqa: E402
                          summarise_save)
from script_commits import TOOLS_DIR, closure_commit  # noqa: E402

SUMMARY_SCRIPT = "mine_summary.py"
MAP_SCRIPT = "terrain_map.py"
MAPPER_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "tf3-save-mapper"))


def find_saves(arg):
    if arg.endswith(".sav"):
        return [(arg, None, None, "savegame")]
    mods_dir = os.path.dirname(os.path.abspath(arg.rstrip("/")))
    mod_id = os.path.basename(os.path.abspath(arg.rstrip("/")))
    found = []
    for kind, sub in (("savegame", "savegames"), ("map", "maps")):
        sav_dir = os.path.join(arg, sub)
        if os.path.isdir(sav_dir):
            found += [(os.path.join(sav_dir, f), mod_id, mods_dir, kind)
                      for f in sorted(os.listdir(sav_dir)) if f.endswith(".sav")]
    return found  # empty for a content mod


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower() or "save"

# Size and mtime of the save last read and the commit of the scripts that read it (the summary's, or the map's in
# .map_state.json), one file per summary so parallel runs do not clash.
STATE_FILE = ".mine_state.json"
MAP_STATE_FILE = ".map_state.json"
MAP_FILE = "terrain-map.svg"


def file_key(path, commit):
    st = os.stat(path)
    return [st.st_size, int(st.st_mtime), commit]


def up_to_date(d, path, commit):
    if not commit or "-dirty" in commit:
        return False
    try:
        return json.load(open(os.path.join(d, STATE_FILE), encoding="utf-8")) == file_key(path, commit)
    except (OSError, ValueError):
        return False


def map_up_to_date(d, path, commit):
    """commit is the drawer's key: a commit for terrain_map.py, the `tf3map --version` text for tf3map."""
    if not commit or "-dirty" in commit:
        return False
    try:
        return json.load(open(os.path.join(d, MAP_STATE_FILE), encoding="utf-8"))["key"] == file_key(path, commit)
    except (OSError, ValueError, KeyError):
        return False


def tf3map_binary(given=None):
    """The tf3map to run: the one given, else $TF3MAP, else tf3map on the PATH; None when there is none."""
    b = given or os.environ.get("TF3MAP")
    if b:
        return shutil.which(os.path.expanduser(b))
    return shutil.which("tf3map") or shutil.which(os.path.join(MAPPER_REPO, "target", "release", "tf3map"))


def tf3map_version(binary):
    """`tf3map --version`: `tf3map 0.5.0 (bfe77c7388)` or, with uncommitted changes, `(bfe77c7388-dirty)`."""
    return subprocess.run([binary, "--version"], capture_output=True, text=True, check=True).stdout.strip()


def tf3map_commit(version):
    """The rebuild key of tf3map's maps: the build's commit from its version text (with `-dirty` kept), or the whole
    text when it names none (a build without git)."""
    m = re.search(r"\(([0-9a-f]{7,40}(?:-dirty)?)\)\s*$", version)
    return m.group(1) if m else version


def on_mapper_main(commit):
    """False when the sibling mapper checkout is there and its main branch does not hold `commit`; True otherwise."""
    if not os.path.isdir(os.path.join(MAPPER_REPO, ".git")):
        return True
    run = subprocess.run(["git", "-C", MAPPER_REPO, "merge-base", "--is-ancestor", commit.replace("-dirty", ""), "main"],
                         capture_output=True)
    return run.returncode != 1


def mask(text, path, dirs=()):
    """text with the save's path cut to its file name and the other paths named (tmp, --game, --mods, home) cut."""
    text = text.replace(path, os.path.basename(path))
    for p, short in dirs:
        if p:
            text = text.replace(p, short)
    home = os.path.expanduser("~")
    return text.replace(home, "~") if home not in ("", "/") else text


def run_python_map(tmp, path, game=None, mods=None):
    """terrain_map.py with its defaults: (svg path or None, status, notes)."""
    cmd = [sys.executable, "-I", os.path.join(TOOLS_DIR, MAP_SCRIPT), tmp, path]
    cmd += ["--game", game] if game else []
    cmd += ["--mods", mods] if mods else []
    run = subprocess.run(cmd, capture_output=True, text=True)
    made = [f for f in os.listdir(tmp) if f.endswith(".svg")]
    if made:
        return os.path.join(tmp, made[0]), "ok", run.stderr.splitlines()
    lines = (run.stdout + run.stderr).splitlines()
    for ln in lines:
        if ln.startswith("REFUSED"):
            return None, "refused: " + ln[len("REFUSED"):].strip(), []
        if ln.startswith("FAILED"):
            return None, "failed: " + ln[len("FAILED"):].strip(), []
    err = run.stderr.strip().splitlines()                      # a traceback: its last line says what went wrong
    return None, "failed: " + (err[-1] if err else "no picture written"), []


def run_tf3map(tmp, path, binary, game=None, mods=None):
    """tf3map with its defaults: (svg path or None, status, notes). Exit 0 is a map, 3 a save the reader refused,
    1 any other failure, 2 wrong arguments; on non-zero the reason is the stderr line `tf3map: REASON`."""
    out = os.path.join(tmp, MAP_FILE)
    cmd = [binary, path, "-o", out]
    cmd += ["--game", game] if game else []
    cmd += ["--mods", mods] if mods else []
    run = subprocess.run(cmd, capture_output=True, text=True)
    lines = run.stderr.splitlines()
    if run.returncode == 0:
        if os.path.isfile(out):
            return out, "ok", lines
        return None, "failed: exit status 0 but no picture written", lines
    said = [ln for ln in lines if ln.startswith("tf3map: ")]
    reason = said[-1][len("tf3map: "):] if said else (lines[-1] if lines else f"exit status {run.returncode}")
    notes = [ln for ln in lines if not said or ln != said[-1]]
    return None, ("refused: " if run.returncode == 3 else "failed: ") + reason, notes


def draw_map(d, path, commit, mapper="python", binary=None, game=None, mods=None):
    """Draw one save's default map with the given drawer (python: terrain_map.py; tf3map: the binary) and put the
    SVG in d as terrain-map.svg; commit is the drawer's key (see map_up_to_date). Records the outcome in
    .map_state.json and returns an error text (`refused: ...` or `failed: ...`), or None when the map was drawn."""
    with tempfile.TemporaryDirectory() as tmp:
        if mapper == "tf3map":
            made, status, notes = run_tf3map(tmp, path, binary, game, mods)
        else:
            made, status, notes = run_python_map(tmp, path, game, mods)
        if made:
            shutil.move(made, os.path.join(d, MAP_FILE))
        dirs = ((tmp, "<tmp>"), (game, "<game>"), (mods, "<mods>"))
        status = mask(status, path, dirs)
        notes = [mask(n, path, dirs) for n in notes if n.strip()][:20]
    error = None if status == "ok" else status
    if error and os.path.exists(os.path.join(d, MAP_FILE)):
        os.remove(os.path.join(d, MAP_FILE))  # a stale picture from an older run
    with open(os.path.join(d, MAP_STATE_FILE), "w", encoding="utf-8") as f:
        json.dump({"key": file_key(path, commit), "mapper": "tf3map" if mapper == "tf3map" else MAP_SCRIPT,
                   "status": status, "error": error, "notes": notes}, f)
    return error


def seed_parts(seed):
    """Folders under OUT_DIR for a map seed: (first character, seed), or ("_noseed",) without one."""
    seed = re.sub(r"[^A-Za-z0-9]", "_", seed or "")
    return (seed[0], seed) if seed else ("_noseed",)


def summary_dirs(out_dir):
    """Folders under out_dir that hold a summary, by leaf name, in any layout this script has written."""
    found = {}
    for top in os.listdir(out_dir):
        t = os.path.join(out_dir, top)
        if not os.path.isdir(t):
            continue
        if os.path.isfile(os.path.join(t, SUMMARY_FILE)):  # flat layout
            found[top] = t
            continue
        for mid in os.listdir(t):
            m = os.path.join(t, mid)
            if os.path.isfile(os.path.join(m, SUMMARY_FILE)):  # _noseed/<leaf>
                found[mid] = m
            elif os.path.isdir(m):
                for leaf in os.listdir(m):
                    if os.path.isfile(os.path.join(m, leaf, SUMMARY_FILE)):
                        found[leaf] = os.path.join(m, leaf)
    return found


def place(out_dir, leaf, seed):
    return os.path.join(out_dir, *seed_parts(seed), leaf)


def move_to(old, new):
    """Move a summary folder, then remove the seed folders it emptied."""
    if os.path.abspath(old) == os.path.abspath(new):
        return
    os.makedirs(os.path.dirname(new), exist_ok=True)
    shutil.move(old, new)
    up = os.path.dirname(old)
    for _ in range(2):
        try:
            os.rmdir(up)
        except OSError:
            break
        up = os.path.dirname(up)


def lower_priority():
    """Nice 19 and idle I/O for this process (and the children it starts); best effort."""
    try:
        os.nice(19)
        subprocess.run(["ionice", "-c3", "-p", str(os.getpid())], check=False, stderr=subprocess.DEVNULL)
    except (OSError, AttributeError):
        pass


def parse_args(argv):
    ap = argparse.ArgumentParser(description="Summarise many saves and draw each one's default map.")
    ap.add_argument("out_dir")
    ap.add_argument("saves", nargs="*", help=".sav files or mod.io mod directories")
    ap.add_argument("--no-maps", action="store_true", help="summaries only")
    ap.add_argument("--no-nice", action="store_true", help="keep the normal priority")
    ap.add_argument("--mapper", choices=("python", "tf3map"), help="the map drawer (default tf3map)")
    ap.add_argument("--tf3map", metavar="BIN", help="the tf3map binary (selects --mapper tf3map)")
    ap.add_argument("--game", metavar="DIR", help="the game's install folder, passed to the drawer")
    ap.add_argument("--mods", metavar="DIR", help="the mod.io game's mods folder, passed to the drawer")
    a = ap.parse_intermixed_args(argv)
    if a.tf3map and a.mapper == "python":
        ap.error("--tf3map names the tf3map drawer; leave out --mapper python")
    a.mapper = "tf3map" if a.tf3map else (a.mapper or "tf3map")
    return a


def mapper_key(a):
    """(binary, key) of the drawer: tf3map's binary and --version text, or (None, terrain_map.py's commit)."""
    if a.mapper == "python":
        return None, closure_commit(MAP_SCRIPT)
    binary = tf3map_binary(a.tf3map)
    if not binary:
        sys.exit("mine_saves.py: no tf3map found (give --tf3map BIN, set TF3MAP, put it on the PATH or build the "
                 "sibling tf3-save-mapper with cargo build --release; or use --mapper python)")
    try:
        version = tf3map_version(binary)
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit(f"mine_saves.py: tf3map --version did not run: {e}")
    key = tf3map_commit(version)
    if key == version:
        print(f"note: {key!r} names no commit (a build without git): its maps are redrawn only when the version "
              "changes", file=sys.stderr)
    elif "-dirty" in key:
        print(f"note: {version} is a build with uncommitted changes: every map is redrawn on each run", file=sys.stderr)
    elif not on_mapper_main(key):
        print(f"note: commit {key} is not on main of the tf3-save-mapper checkout: the key is not main's commit",
              file=sys.stderr)
    return binary, key


def main():
    a = parse_args(sys.argv[1:])
    maps = not a.no_maps
    if not a.no_nice:
        lower_priority()
    out_dir, args = a.out_dir, a.saves
    os.makedirs(out_dir, exist_ok=True)
    done = skipped = failed = drawn = unmapped = 0
    scommit = closure_commit(SUMMARY_SCRIPT)
    binary, mcommit = mapper_key(a) if maps and args else (None, None)
    for arg in args:
        for path, mod_id, mods_dir, kind in find_saves(arg):
            profile = catalog_profiles(mods_dir).get(mod_id, {}) if mods_dir else {}
            name = profile.get("name") or os.path.splitext(os.path.basename(path))[0]
            leaf = f"{mod_id or 'local'}-{slug(name)}" + ("-map" if kind == "map" else "")
            d = summary_dirs(out_dir).get(leaf)
            readable = False                          # the summary is there and the save could be read
            if d:
                try:
                    seed = json.load(open(os.path.join(d, SUMMARY_FILE), encoding="utf-8")).get("map_seed")
                except (OSError, ValueError):
                    seed = None
                new = place(out_dir, leaf, seed)
                move_to(d, new)
                d = new
                readable = up_to_date(d, path, scommit)
                skipped += readable
            if not readable:
                print("reading", os.path.basename(path), file=sys.stderr)
                summary = summarise_save(path, mod_id, mods_dir, kind)
                new = place(out_dir, leaf, summary["map_seed"])
                if d:
                    move_to(d, new)
                d = new
                os.makedirs(d, exist_ok=True)
                sp = os.path.join(d, SUMMARY_FILE)
                with open(sp, "w", encoding="utf-8") as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)
                    f.write("\n")
                old = os.path.join(d, OLD_SUMMARY_FILE)
                if os.path.exists(old):
                    os.remove(old)
                state = os.path.join(d, STATE_FILE)
                if summary["error"]:
                    failed += 1
                    if os.path.exists(state):
                        os.remove(state)  # retry next run
                    print("  FAILED:", summary["error"], file=sys.stderr)
                else:
                    done += 1
                    readable = True
                    with open(state, "w", encoding="utf-8") as f:
                        json.dump(file_key(path, summary["tools_commit"]), f)
            if maps and readable and not map_up_to_date(d, path, mcommit):
                print("drawing", os.path.basename(path), file=sys.stderr)
                error = draw_map(d, path, mcommit, a.mapper, binary, a.game, a.mods)
                if error:
                    print("  no map:", error, file=sys.stderr)
                    unmapped += 1
                else:
                    drawn += 1
    if not args:  # alone at the end of a run: put every summary where its seed says
        for leaf, d in summary_dirs(out_dir).items():
            seed = json.load(open(os.path.join(d, SUMMARY_FILE), encoding="utf-8")).get("map_seed")
            move_to(d, place(out_dir, leaf, seed))
    rows = []
    for d in sorted(summary_dirs(out_dir).values(), key=lambda d: os.path.relpath(d, out_dir)):
        rows.append(index_row(json.load(open(os.path.join(d, SUMMARY_FILE), encoding="utf-8"))))
    idx = os.path.join(out_dir, "index.csv")
    with open(idx, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(INDEX_COLS)
        w.writerows(rows)
    print(f"{done} read, {skipped} unchanged, {failed} failed; {len(rows)} rows in {idx}", file=sys.stderr)
    if maps:
        print(f"{drawn} maps drawn, {unmapped} without a map (reason in .map_state.json)", file=sys.stderr)


if __name__ == "__main__":
    main()
