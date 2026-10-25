#!/usr/bin/env python3
"""Rank mined saves by play periods, keeping only those whose mods you have; or list which mods you have.

Usage: top_saves.py INDEX_CSV [-n 10] [--out FILE.md] [--lack KEY ...] [--have KEY ...] [--mods DIR] [--game DIR]
                    [--corpus NAME[,NAME] | all]
       top_saves.py INDEX_CSV --owned [--prefix urbangames_ --prefix ug_]

INDEX_CSV is the `index.csv` that mine_saves.py writes (columns `play_periods`, `mod_list`, `header`, `map_seed`,
`name`, `source_name`, ...). Reads only; the one output is the table on stdout, or the markdown file with `--out`.

What "have" means (read at run time from the folders, nothing stored):
- the mod.io mods folder: the `modId` of every `mod.json` in it (`--mods`, default the usual places);
- the install: the `modId` of every `mod.json` under `mods/release/` (the game's own modes such as the sandbox) and
  `dlcs/` (a pack you own has a folder here; the pre-order pack has none unless you own it) (`--game`, default the
  usual Steam places). Only `modId` is read.
`--have KEY` adds a key by hand, `--lack KEY` removes one (for a pack the folders cannot show).

Corpus: `index.csv` has a `corpus` column (`catalog-saves`, `catalog-maps`, `own-saves`, `own-maps`). The default
is `catalog-saves,catalog-maps`, the mod.io catalog (the own saves are many re-saves of a few games and would crowd
the ranking); `--corpus all` or a list picks others.

Ranking: rows with `header` ok only (a partial header gives no mod list); a save needing a mod you lack is left
out; one save per map seed (the one with most periods, the lower mod id on a tie; a save with no seed stands alone). The table gives both
names: the mod.io title (`name`) and the file name the game's load list shows (`source_name`), since several
catalog saves share one file name.

`--owned` lists every mod key in the index that starts with a prefix (default `urbangames_` and `ug_`), how many
saves use it and whether you have it.
"""
import argparse
import collections
import csv
import datetime
import glob
import json
import os
import sys

MOD_DIRS = ("~/snap/steam/common/mod.io/common/10640/mods", "~/.local/share/mod.io/common/10640/mods")
GAME_DIRS = ("~/.steam/steam", "~/.local/share/Steam", "~/snap/steam/common/.local/share/Steam",
             "~/.var/app/com.valvesoftware.Steam/.local/share/Steam")


def mod_ids(pattern):
    """The `modId` of every mod.json matching the glob pattern."""
    out = set()
    for path in glob.glob(pattern):
        try:
            with open(path, encoding="utf-8") as f:
                out.add(json.load(f)["modId"])
        except (OSError, ValueError, KeyError, TypeError):
            pass
    return out


def installed(mods_dir=None, game_dir=None):
    """(keys you have, where they came from) from the mod.io folder and the install."""
    mods = [os.path.expanduser(mods_dir)] if mods_dir else [os.path.expanduser(d) for d in MOD_DIRS]
    games = ([os.path.expanduser(game_dir)] if game_dir else
             [os.path.join(os.path.expanduser(d), "steamapps", "common", "Transport Fever 3") for d in GAME_DIRS])
    have, src = set(), {"mod.io folder": 0, "install mods/release": 0, "install dlcs": 0}
    for d in mods:
        ids = mod_ids(os.path.join(d, "*", "mod.json"))
        src["mod.io folder"] += len(ids)
        have |= ids
    for d in games:
        for label, sub in (("install mods/release", "mods/release"), ("install dlcs", "dlcs")):
            ids = mod_ids(os.path.join(d, sub, "*", "mod.json"))
            src[label] += len(ids)
            have |= ids
    return have, src


def read_index(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mods_of(row):
    return [m for m in row["mod_list"].split(";") if m]


def rank(rows, have):
    """Rows with a good header and no mod you lack, most periods first, one per map seed."""
    kept = sorted((r for r in rows if r["header"] == "ok" and all(m in have for m in mods_of(r))),
                  key=lambda r: (-int(r["play_periods"] or 0), r["mod_id"]))
    seen, out = set(), []
    for r in kept:
        key = r["map_seed"] or r["mod_id"]
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def table(top):
    lines = ["| # | Periods | Mod id | mod.io title | Load-list file name | Seed | Size | Save date | Mods |",
             "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(top, 1):
        mods = "; ".join(mods_of(r)) or "none"
        lines.append(f"| {i} | {r['play_periods']} | {r['mod_id']} | {r['name']} | {r['source_name']} | "
                     f"{r['map_seed']} | {r['map_size_name']} | {r['date']} | {mods} |")
    return lines


def owned_report(rows, have, prefixes):
    use = collections.Counter(m for r in rows for m in mods_of(r) if m.startswith(prefixes))
    lines = [f"{'saves':>6}  {'have':<5} key"]
    lines += [f"{n:>6}  {'yes' if m in have else 'NO':<5} {m}" for m, n in sorted(use.items(), key=lambda kv: (-kv[1], kv[0]))]
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("index", help="index.csv from mine_saves.py")
    ap.add_argument("-n", type=int, default=10, help="how many rows (default 10)")
    ap.add_argument("--out", help="write the table as a markdown file (with the date and the rules)")
    ap.add_argument("--have", action="append", default=[], metavar="KEY", help="count this mod key as owned")
    ap.add_argument("--lack", action="append", default=[], metavar="KEY", help="count this mod key as not owned")
    ap.add_argument("--mods", help="the mod.io mods folder (default: the usual places)")
    ap.add_argument("--game", help="the install folder (default: the usual Steam places)")
    ap.add_argument("--owned", action="store_true", help="list the prefixed mod keys and whether you have them")
    ap.add_argument("--prefix", action="append", help="key prefix for --owned (default urbangames_ and ug_)")
    ap.add_argument("--corpus", default="catalog-saves,catalog-maps", help="corpora to use, comma-separated, or all")
    args = ap.parse_args()

    rows = read_index(args.index)
    if args.corpus != "all" and rows and "corpus" in rows[0]:
        rows = [r for r in rows if r["corpus"] in args.corpus.split(",")]
    if rows and "mod_list" not in rows[0]:
        sys.exit("index.csv has no mod_list column: rewrite it with `mine_saves.py OUT_DIR` (no save arguments)")
    have, src = installed(args.mods, args.game)
    if not any(src.values()):
        print("warning: found no mod.json in any mod.io or install folder; pass --mods and --game", file=sys.stderr)
    have = (have | set(args.have)) - set(args.lack)

    if args.owned:
        print("\n".join(owned_report(rows, have, tuple(args.prefix or ("urbangames_", "ug_")))))
        return
    top = rank(rows, have)[:args.n]
    lines = table(top)
    if not args.out:
        print("\n".join(lines))
        return
    head = [f"# Top {len(top)} catalog saves by play_periods, no missing mods ({datetime.date.today()})", "",
            "Made by `tools/top_saves.py` from `index.csv` (columns `play_periods`, `mod_list`).", "",
            "Rules:",
            f"- A save is kept only when every mod it lists is one you have ({sum(src.values())} `modId` read from the "
            "mod.io folder, the install's `mods/release` and `dlcs`).",
            f"- Added by hand: {', '.join(args.have) or 'none'}. Removed by hand: {', '.join(args.lack) or 'none'}.",
            "- Only rows with `header` ok; one save per map seed (most periods wins).", ""]
    foot = ["", "The game lists a save by its file name, not the mod.io title (columns `name` and `source_name`). "
            "Several catalog saves share a file name; tell them apart by save date, map size and seed."]
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(head + lines + foot) + "\n")
    print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
