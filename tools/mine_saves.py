#!/usr/bin/env python3
"""Summarise TF3 savegames (for example ones from the mod.io catalog) as JSON facts.

Usage: mine_saves.py OUT_DIR SAVE_OR_MODDIR [...]

Reads only. For every save it writes OUT_DIR/<id>-<name>/tf3-save-summary.json
(layout: tf3-save-summary.schema.json next to this script) and rebuilds
OUT_DIR/index.csv from every summary there. A summary.json left by an older
version in the same folder is removed. A SAVE_OR_MODDIR can be a
.sav or a mod.io mod directory (.../mods/<id>) whose savegames/ or maps/
folder holds one. A map-editor map (maps/) is written to <id>-<name>-map, so a
mod that ships both a savegame and a map keeps two summaries. Catalog name, tags, author and link come from mod.io's metadata/state.json
when it is found next to the mods directory.

Safe to re-run while mod.io is still downloading: a save whose size and mtime
match the last run is skipped, and a save that fails to read gets an error
summary and is retried next run. The size and mtime are kept in a
.mine_state.json next to each summary, not in the summary, so summaries hold
no local paths or timestamps. About 8 s per save; for many saves run several
at once, for example with `xargs -P4`.

Each summary records `tools_commit`, the last git commit that changed a script
in tools/ (with "-dirty" if one has uncommitted changes, null outside a git
checkout). Changes to the README or the schema alone do not count.
A save is read again when that commit differs from the one its summary was
built with, so summaries follow the scripts; a dirty build is always redone.

What is read:
- the header (save_header.py): format version, start year, map size in metres,
  climate, economy, name list, mods, a few settings
- town records: the validated scan in tf3save.py (docs/town-records.md).
  `records` is every record found; `starting_layout` those whose four floats
  are all 1.0 (cargo counts use these). Towns that have run for a while use
  other record shapes and are missed.
- settings: every New Game setting as "stored (label)", for example
  "3 (100%, default)", from tf3save.SETTING_OPTIONS. Needs the full header
  (599 to 604); 568 and 585 have none.
- calendar (docs/calendar.md): the date shown, the start date, the
  calendar speed (millisPerDay) and play speed, the clock and the day table.
- company, counters, cycles, subsidies, town_states: from the script states
  of the company, achievements, game time, subsidy and town scripts. A save
  without one of them (editor maps) has null there.

Every key of the schema is written, null where the save has no value or could
not be read (then `error` says why).
"""
import collections
import csv
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from save_header import read_header  # noqa: E402
from tf3save import (RANKS, TEMPERATE_NAMES, calendar_speed_label, date_of_day, day_table_regular,  # noqa: E402
                     decompress, find_day_table, find_game_speed, scan_records, script_state, setting_label)

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))


def tools_commit():
    """Short hash of the last commit that changed a tools/*.py, "-dirty" if one has changes, or None."""
    try:
        git = ["git", "-C", TOOLS_DIR]
        h = subprocess.run(git + ["log", "-1", "--format=%h", "--", "*.py"], capture_output=True, text=True, check=True)
        st = subprocess.run(git + ["status", "--porcelain", "--", "*.py"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return (h.stdout.strip() or None) and h.stdout.strip() + ("-dirty" if st.stdout.strip() else "")


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


def num(v):
    """Lua numbers are floats; whole ones as int for the JSON."""
    return int(v) if isinstance(v, float) and v.is_integer() else v


def rank(level):
    level = num(level)
    if isinstance(level, int) and 1 <= level <= len(RANKS):
        return f"{level} ({RANKS[level - 1]})"
    return level


def summarise_calendar(data):
    g = find_game_speed(data)
    if g is None:
        return None
    table = find_day_table(data) or []
    mpd, ps = g["millis_per_day"], g["play_speed"]
    first, last = (date_of_day(table[0][1]), date_of_day(table[-1][1])) if table else (None, None)
    return {
        "date": last and last.isoformat(),
        "start_date": first and first.isoformat(),
        "calendar_speed": f"{mpd} ({'Paused' if mpd == 0 else calendar_speed_label(mpd) or 'not a slider step'})",
        "play_speed": f"{ps} ({'paused' if ps == 0 else f'{ps}x'})",
        "clock": g["t1"],
        "day_table_entries": len(table),
        "day_table_regular": day_table_regular(table),
    }


# Script states as the game stores them; see docs/script-states.md and docs/town-states.md.
# game_time.gs mode names to the Cycle menu's names.
TIME_OF_DAY_MODES = {"Dynamic": "Dynamic", "Automatic": "Continuous", "Constant": "Custom"}
WEATHER_MODES = {"Dynamic": "Dynamic", "Constant": "Custom"}


def summarise_states(data):
    out = {}
    prog = script_state(data, "game_mechanics/company/company_progression.gs") or {}
    company = script_state(data, "game_mechanics/company/company.gs") or {}
    states = [s for s in (prog.get("companyState") or {}).values() if isinstance(s, dict)]
    if states or company:
        cs = states[0] if states else {}
        out["company"] = {
            "rank": rank(cs.get("potentialLevel")),
            "level": rank(cs.get("level")),
            "experience": num(cs.get("experience")),
            "base_population": num(company.get("basePopulation")),
        }
    else:
        out["company"] = None
    ach = script_state(data, "game_mechanics/achievements/achievements.gs")
    if ach is not None:
        skip = {"version", "lastIncomeUpdateTime", "stationGroupEntity"}
        counters = {k: num(v) for k, v in sorted(ach.items()) if isinstance(v, float) and k not in skip}
        for k in ("cargoTypesDelivered", "vehiclesUsed", "shipsUsed"):
            if isinstance(ach.get(k), dict):
                counters[k] = len(ach[k])
        out["counters"] = counters
    else:
        out["counters"] = None
    gt = script_state(data, "game_mechanics/game_time/game_time.gs")
    if gt is not None:
        tod, wx = gt.get("timeOfDayMode"), gt.get("weatherMode")
        out["cycles"] = {
            "time_of_day": f"{tod} ({TIME_OF_DAY_MODES[tod]})" if TIME_OF_DAY_MODES.get(tod, tod) != tod else tod,
            "weather": f"{wx} ({WEATHER_MODES[wx]})" if WEATHER_MODES.get(wx, wx) != wx else wx,
        }
    else:
        out["cycles"] = None
    sub = script_state(data, "game_mechanics/subventions/subventions.gs")
    if sub is not None:
        out["subsidies"] = {k: len(t) if isinstance(t := sub.get(k + "Subventions"), dict) else 0
                            for k in ("proposed", "active", "completed", "failed")}
    else:
        out["subsidies"] = None
    town = script_state(data, "game_mechanics/towns/town.gs")
    ts = (town or {}).get("townStates")
    out["town_states"] = len(ts) if isinstance(ts, dict) else (0 if town is not None else None)
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


SUMMARY_FILE = "tf3-save-summary.json"
OLD_SUMMARY_FILE = "summary.json"
SCHEMA_URL = "https://raw.githubusercontent.com/WuphonsReach/tf3-save-format/main/tools/tf3-save-summary.schema.json"
SCHEMA_VERSION = 1
# Every key, in the order written (tf3-save-summary.schema.json).
FIELDS = ["$schema", "schema_version", "name", "mod_id", "kind", "source_name", "source_size", "author", "tags",
          "url", "tools_commit", "error", "version", "first_version", "start_year", "map_w_m", "map_h_m",
          "header_money", "header_counter", "climate", "economy", "name_list", "is_map_editor", "header_partial",
          "stream_bytes", "calendar", "company", "counters", "cycles", "subsidies", "town_states", "town_records",
          "settings", "mods"]

INDEX_COLS = ["mod_id", "name", "author", "version", "start_year", "map_w_m", "map_h_m", "climate",
              "name_list", "mods", "is_map_editor", "start_layout_towns", "records", "stream_bytes", "header", "kind",
              "date", "calendar_speed", "play_speed", "rank", "tools_commit"]


def summarise_save(path, mod_id, mods_dir, kind="savegame"):
    profile = catalog_profiles(mods_dir).get(mod_id, {}) if mods_dir else {}
    name = profile.get("name") or os.path.splitext(os.path.basename(path))[0]
    summary = dict.fromkeys(FIELDS)
    summary.update({
        "$schema": SCHEMA_URL,
        "schema_version": SCHEMA_VERSION,
        "name": name,
        "mod_id": mod_id,
        "kind": kind,
        "source_name": os.path.basename(path),
        "source_size": os.stat(path).st_size,
        "author": (profile.get("submitted_by") or {}).get("username"),
        "tags": [t["name"] for t in profile.get("tags", [])],
        "url": profile.get("profile_url"),
        "tools_commit": tools_commit(),
    })
    try:
        data = decompress(open(path, "rb").read())
        h = read_header(path, data)
        s = h.get("settings", {})
        res = dict(h.get("resources", []))
        summary.update({
            "version": h["version"],
            "first_version": h.get("value"),
            "start_year": h["start_year"],
            "map_w_m": h["map_w_m"],
            "map_h_m": h["map_h_m"],
            "header_money": h["money"],
            "header_counter": h["counter"],
            "climate": os.path.basename(res["climate"]) if "climate" in res else None,
            "economy": res.get("economy"),
            "name_list": res.get("nameList"),
            "is_map_editor": s.get("isMapEditor"),
            "header_partial": h["partial"],
            "stream_bytes": h["stream_len"],
            "calendar": summarise_calendar(data),
            **summarise_states(data),
            "town_records": summarise_records(scan_records(data), res.get("economy") or ""),
            "settings": {k: setting_label(k, v) for k, v in sorted(s.items())} if s else None,
            "mods": [m["id"] for m in h["mods"]],
        })
        del data
    except Exception as e:  # truncated download, unknown format, ...
        summary["error"] = f"{type(e).__name__}: {e}"
    return summary


def index_row(sm):
    tr = sm.get("town_records") or {}
    if sm.get("error"):
        return ([sm["mod_id"], sm["name"], sm["author"]] + [""] * 11 + ["error", sm.get("kind", "savegame")]
                + [""] * 4 + [sm.get("tools_commit")])
    cal = sm.get("calendar") or {}
    return [sm["mod_id"], sm["name"], sm["author"], sm["version"], sm["start_year"],
            sm["map_w_m"], sm["map_h_m"], sm["climate"], sm["name_list"],
            len(sm["mods"]), sm["is_map_editor"], tr["starting_layout"], tr["records"],
            sm["stream_bytes"], "partial" if sm["header_partial"] else "ok", sm.get("kind", "savegame"),
            cal.get("date"), cal.get("calendar_speed"), cal.get("play_speed"),
            (sm.get("company") or {}).get("rank"), sm.get("tools_commit")]


# Size and mtime of the save last read and the tools commit that read it, one file per summary
# so parallel runs do not clash.
STATE_FILE = ".mine_state.json"


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


def main():
    out_dir, args = sys.argv[1], sys.argv[2:]
    os.makedirs(out_dir, exist_ok=True)
    done = skipped = failed = 0
    commit = tools_commit()
    for arg in args:
        for path, mod_id, mods_dir, kind in find_saves(arg):
            profile = catalog_profiles(mods_dir).get(mod_id, {}) if mods_dir else {}
            name = profile.get("name") or os.path.splitext(os.path.basename(path))[0]
            d = os.path.join(out_dir, f"{mod_id or 'local'}-{slug(name)}" + ("-map" if kind == "map" else ""))
            sp = os.path.join(d, SUMMARY_FILE)
            if os.path.isfile(sp) and up_to_date(d, path, commit):
                skipped += 1
                continue
            print("reading", path, file=sys.stderr)
            summary = summarise_save(path, mod_id, mods_dir, kind)
            os.makedirs(d, exist_ok=True)
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
                with open(state, "w", encoding="utf-8") as f:
                    json.dump(file_key(path, summary["tools_commit"]), f)
    rows = []
    for sub in sorted(os.listdir(out_dir)):
        sp = os.path.join(out_dir, sub, SUMMARY_FILE)
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
