#!/usr/bin/env python3
"""Summarise TF3 savegames (for example ones from the mod.io catalog) as JSON facts and draw each one's map.

Usage: mine_saves.py [--no-maps] [--no-nice] OUT_DIR SAVE_OR_MODDIR [...]

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
Next to each summary this script also writes terrain-map.svg, the picture terrain_map.py draws with no options (the
vector terrain, the roads and rails, the default grid and compass rose; docs/terrain.md), so the picture follows that
script's current defaults. `--no-maps` skips the pictures. A save the script cannot draw (it prints REFUSED or FAILED)
gets no picture; the reason is kept in .map_state.json beside the summary. Pictures are other people's maps: they
stay in OUT_DIR, which is never committed. The script needs about 2.5 GB of memory for a Giant map, so keep the
parallel runs few (xargs -P4) on a small machine. The script lowers its own priority at start (nice 19, and idle I/O
when `ionice` is installed; the map-drawing child processes inherit it) so a long run leaves the machine usable;
`--no-nice` keeps the normal priority.

Two things are rebuilt separately, each when the save changed or its own scripts did:
- the summary, when the commit of mine_summary.py and the modules it imports (save_header.py, tf3save.py) differs
  from the one in the summary's `tools_commit`;
- the map, when the commit of terrain_map.py and the modules it imports differs from the one in .map_state.json.
A change to tf3save.py is in both sets and rebuilds both; one to terrain_map.py, terrain_vector.py or street_edges.py
redraws the maps and leaves the summaries; one to mine_summary.py rebuilds the summaries only. A set with uncommitted
changes ("-dirty") is always rebuilt. `script_commits.py SCRIPT` lists a set and its commit.

Safe to re-run while mod.io is still downloading: a save whose size and mtime
match the last run is skipped, and a save that fails to read gets an error
summary and is retried next run. The size and mtime are kept in a
.mine_state.json (summary) and .map_state.json (map) next to each summary, not in the summary, so summaries hold
no local paths or timestamps. About 8 s per save for the summary, up to 40 s more for a Giant map; for many saves
run several at once, for example with `xargs -P4`.
"""
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
    if not commit or commit.endswith("-dirty"):
        return False
    try:
        return json.load(open(os.path.join(d, STATE_FILE), encoding="utf-8")) == file_key(path, commit)
    except (OSError, ValueError):
        return False


def map_up_to_date(d, path, commit):
    if not commit or commit.endswith("-dirty"):
        return False
    try:
        return json.load(open(os.path.join(d, MAP_STATE_FILE), encoding="utf-8"))["key"] == file_key(path, commit)
    except (OSError, ValueError, KeyError):
        return False


def draw_map(d, path, commit):
    """Run terrain_map.py with its defaults on one save and put the SVG in d. Returns an error text or None."""
    error = None
    with tempfile.TemporaryDirectory() as tmp:
        run = subprocess.run([sys.executable, "-I", os.path.join(TOOLS_DIR, MAP_SCRIPT), tmp, path],
                             capture_output=True, text=True)
        made = [f for f in os.listdir(tmp) if f.endswith(".svg")]
        if made:
            shutil.move(os.path.join(tmp, made[0]), os.path.join(d, MAP_FILE))
        else:
            lines = [ln for ln in (run.stdout + run.stderr).splitlines() if ln.startswith(("REFUSED", "FAILED", "Traceback"))]
            error = (lines[0] if lines else (run.stderr.strip().splitlines() or ["no picture written"])[-1])
            error = error.replace(path, os.path.basename(path))
    if error and os.path.exists(os.path.join(d, MAP_FILE)):
        os.remove(os.path.join(d, MAP_FILE))  # a stale picture from an older run
    with open(os.path.join(d, MAP_STATE_FILE), "w", encoding="utf-8") as f:
        json.dump({"key": file_key(path, commit), "error": error}, f)
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


def main():
    argv = sys.argv[1:]
    maps = "--no-maps" not in argv
    if "--no-nice" not in argv:
        lower_priority()
    argv = [a for a in argv if a not in ("--no-maps", "--no-nice")]
    out_dir, args = argv[0], argv[1:]
    os.makedirs(out_dir, exist_ok=True)
    done = skipped = failed = drawn = unmapped = 0
    scommit, mcommit = closure_commit(SUMMARY_SCRIPT), closure_commit(MAP_SCRIPT)
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
                if draw_map(d, path, mcommit):
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
