#!/usr/bin/env python3
"""Summarise TF3 savegames (for example ones from the mod.io catalog) as JSON facts.

Usage: mine_saves.py OUT_DIR SAVE_OR_MODDIR [...]

Reads only. For every save it writes OUT_DIR/<id>-<name>/summary.json and
rebuilds OUT_DIR/index.csv from every summary there. A SAVE_OR_MODDIR can be a
.sav or a mod.io mod directory (.../mods/<id>) whose savegames/ folder holds
one. Catalog name, tags, author and link come from mod.io's metadata/state.json
when it is found next to the mods directory.

Safe to re-run while mod.io is still downloading: a save whose size and mtime
match the last run is skipped, and a save that fails to read gets an error
summary and is retried next run. The size and mtime are kept in a
.mine_state.json next to each summary, not in the summary, so summaries hold
no local paths or timestamps. About 8 s per save; for many saves run several
at once, for example with `xargs -P4`.

What is read:
- the header (save_header.py): format version, start year, map size in metres,
  climate, economy, name list, mods, a few settings
- town records: the validated scan in tf3save.py (docs/town-records.md).
  `records` is every record found; `starting_layout` those whose four floats
  are all 1.0 (cargo counts use these). Towns that have run for a while use
  other record shapes and are missed.
"""
import collections
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from save_header import read_header  # noqa: E402
from tf3save import TEMPERATE_NAMES, decompress, scan_records  # noqa: E402


def summarise_records(recs, economy):
    start = [r for r in recs if r["floats"] == (1.0, 1.0, 1.0, 1.0)]
    run, best = 0, 0
    for a, b in zip(recs, recs[1:]):
        run = run + 1 if b["offset"] - a["offset"] == 78 else 0
        best = max(best, run + 1)
    out = {"records": len(recs), "starting_layout": len(start), "longest_78_byte_run": best}
    if start:
        names = TEMPERATE_NAMES if economy.endswith("temperate.eco") else {}
        for kind in ("com", "ind"):
            c = collections.Counter(r["id"][kind] for r in start)
            out[f"{kind}_cargo"] = {str(names.get(i, i)): n for i, n in sorted(c.items())}
        out["capacity_totals"] = [sum(r["caps"][k] for r in start) for k in range(3)]
    return out


def catalog_profiles(mods_dir):
    state = os.path.join(os.path.dirname(mods_dir), "metadata", "state.json")
    try:
        mods = json.load(open(state, encoding="utf-8"))["Mods"]
    except (OSError, KeyError, ValueError):
        return {}
    return {str(m["ID"]): m["Profile"] for m in mods}


def find_saves(arg):
    if arg.endswith(".sav"):
        return [(arg, None, None)]
    mods_dir = os.path.dirname(os.path.abspath(arg.rstrip("/")))
    mod_id = os.path.basename(os.path.abspath(arg.rstrip("/")))
    sav_dir = os.path.join(arg, "savegames")
    if not os.path.isdir(sav_dir):
        return []  # a content mod, not a savegame
    return [(os.path.join(sav_dir, f), mod_id, mods_dir) for f in sorted(os.listdir(sav_dir)) if f.endswith(".sav")]


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower() or "save"


INDEX_COLS = ["mod_id", "name", "author", "version", "start_year", "map_w_m", "map_h_m", "climate",
              "name_list", "mods", "is_map_editor", "start_layout_towns", "records", "stream_bytes", "header"]


def summarise_save(path, mod_id, mods_dir):
    profile = catalog_profiles(mods_dir).get(mod_id, {}) if mods_dir else {}
    name = profile.get("name") or os.path.splitext(os.path.basename(path))[0]
    summary = {
        "name": name,
        "mod_id": mod_id,
        "source_name": os.path.basename(path),
        "source_size": os.stat(path).st_size,
        "author": (profile.get("submitted_by") or {}).get("username"),
        "tags": [t["name"] for t in profile.get("tags", [])],
        "url": profile.get("profile_url"),
    }
    try:
        data = decompress(open(path, "rb").read())
        h = read_header(path, data)
        s = h.get("settings", {})
        res = dict(h.get("resources", []))
        summary.update({
            "version": h["version"],
            "start_year": h["start_year"],
            "map_w_m": h["map_w_m"],
            "map_h_m": h["map_h_m"],
            "header_money": h["money"],
            "header_counter": h["counter"],
            "climate": os.path.basename(res.get("climate", "")),
            "economy": res.get("economy"),
            "name_list": res.get("nameList"),
            "is_map_editor": s.get("isMapEditor"),
            "map_size_setting": s.get("map.size"),
            "mods": [m["id"] for m in h["mods"]],
            "header_partial": h["partial"],
            "stream_bytes": h["stream_len"],
            "town_records": summarise_records(scan_records(data), res.get("economy") or ""),
        })
        del data
    except Exception as e:  # truncated download, unknown format, ...
        summary["error"] = f"{type(e).__name__}: {e}"
    return summary


def index_row(sm):
    tr = sm.get("town_records", {})
    if "error" in sm:
        return [sm["mod_id"], sm["name"], sm["author"], "", "", "", "", "", "", "", "", "", "", "", "error"]
    return [sm["mod_id"], sm["name"], sm["author"], sm["version"], sm["start_year"],
            sm["map_w_m"], sm["map_h_m"], sm["climate"], sm["name_list"],
            len(sm["mods"]), sm["is_map_editor"], tr["starting_layout"], tr["records"],
            sm["stream_bytes"], "partial" if sm["header_partial"] else "ok"]


# Size and mtime of the save last read, one file per summary so parallel runs do not clash.
STATE_FILE = ".mine_state.json"


def file_key(path):
    st = os.stat(path)
    return [st.st_size, int(st.st_mtime)]


def up_to_date(d, path):
    try:
        return json.load(open(os.path.join(d, STATE_FILE), encoding="utf-8")) == file_key(path)
    except (OSError, ValueError):
        return False


def main():
    out_dir, args = sys.argv[1], sys.argv[2:]
    os.makedirs(out_dir, exist_ok=True)
    done = skipped = failed = 0
    for arg in args:
        for path, mod_id, mods_dir in find_saves(arg):
            profile = catalog_profiles(mods_dir).get(mod_id, {}) if mods_dir else {}
            name = profile.get("name") or os.path.splitext(os.path.basename(path))[0]
            d = os.path.join(out_dir, f"{mod_id or 'local'}-{slug(name)}")
            sp = os.path.join(d, "summary.json")
            if os.path.isfile(sp) and up_to_date(d, path):
                skipped += 1
                continue
            print("reading", path, file=sys.stderr)
            summary = summarise_save(path, mod_id, mods_dir)
            os.makedirs(d, exist_ok=True)
            with open(sp, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
                f.write("\n")
            state = os.path.join(d, STATE_FILE)
            if "error" in summary:
                failed += 1
                if os.path.exists(state):
                    os.remove(state)  # retry next run
                print("  FAILED:", summary["error"], file=sys.stderr)
            else:
                done += 1
                with open(state, "w", encoding="utf-8") as f:
                    json.dump(file_key(path), f)
    rows = []
    for sub in sorted(os.listdir(out_dir)):
        sp = os.path.join(out_dir, sub, "summary.json")
        if os.path.isfile(sp):
            rows.append(index_row(json.load(open(sp, encoding="utf-8"))))
    idx = os.path.join(out_dir, "index.csv")
    with open(idx, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(INDEX_COLS)
        w.writerows(rows)
    print(f"{done} read, {skipped} unchanged, {failed} failed; {len(rows)} rows in {idx}", file=sys.stderr)


if __name__ == "__main__":
    main()
