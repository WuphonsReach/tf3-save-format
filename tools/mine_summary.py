#!/usr/bin/env python3
"""Summarise one TF3 savegame as JSON facts: the part of mine_saves.py that reads a save.

Usage: mine_summary.py SAVE.sav            (prints the summary as JSON)

mine_saves.py imports `summarise_save` and `index_row` from here and writes the summaries into a folder; this
script alone prints one. Reads only. It is separate from the map drawing so that a change to what the summary holds
(this file, save_header.py, tf3save.py) rebuilds the summaries and a change to terrain_map.py (and what it imports)
redraws the maps, with the other left alone (see mine_saves.py).

Each summary records `tools_commit`, the last git commit that changed this script or a module it imports (with
"-dirty" if one has uncommitted changes, null outside a git checkout). Changes to the README, the schema or the
map drawing do not count.

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
- journal (journal.py, docs/finances.md): the money journal's bookings and how many 1,461,000-unit periods hold
  play (building, buying, upkeep, income); null where no journal was found. It ranks a save by how much it was played.
- vehicles (vehicle_counts.py, docs/vehicle-classes.md): the count of vehicle units by carrier, power and load; null where
  the save has no model table. Reads the game install's model metadata at run time when there is one.
- industries (industry_counts.py): the number of industries in total and per kind; null where the save has no model table.
- company, counters, cycles, subsidies, town_states: from the script states
  of the company, achievements, game time, subsidy and town scripts. A save
  without one of them (editor maps) has null there.

Every key of the schema is written, null where the save has no value or could
not be read (then `error` says why).
"""
import collections
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from industry_counts import count_industries  # noqa: E402
from journal import play_summary  # noqa: E402
from save_header import read_header  # noqa: E402
from script_commits import closure_commit  # noqa: E402
from vehicle_counts import INDEX_NAMES, count_vehicles, index_values  # noqa: E402
from tf3save import (RANKS, calendar_speed_label, cargo_entries, date_of_day, day_table_regular,  # noqa: E402
                     decompress, find_day_table, find_game_speed, scan_records, script_state, setting_label,
                     town_names)

def summarise_records(recs, cargo_names, data=None):
    start = [r for r in recs if r["floats"] == (1.0, 1.0, 1.0, 1.0)]
    run, best = 0, 0
    for a, b in zip(recs, recs[1:]):
        run = run + 1 if b["offset"] - a["offset"] == 78 else 0
        best = max(best, run + 1)
    out = {"records": len(recs), "starting_layout": len(start), "longest_78_byte_run": best}
    # the last of the four u32s before the first record, which docs/town-records.md calls the town count; 0 in some saves
    out["table_count"] = struct.unpack_from("<I", data, recs[0]["offset"] - 4)[0] if data and recs and recs[0]["offset"] >= 4 else None
    if start:
        for kind in ("com", "ind"):
            c = collections.Counter(r["id"][kind] for r in start)
            out[f"{kind}_cargo"] = {str(cargo_names[i] if cargo_names and i < len(cargo_names) else i): n
                                    for i, n in sorted(c.items())}
        out["capacity_totals"] = [sum(r["caps"][k] for r in start) for k in range(3)]
    return out


def summarise_towns(data, recs, states):
    """Town names from the entity names table (town_names in tf3save.py); null where they cannot be told."""
    names = town_names(data, max(len(recs), states or 0))
    return {"count": len(names), "names": names} if names else None


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
            "rank_earned": rank(cs.get("potentialLevel")),
            "rank_claimed": rank(cs.get("level")),
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


SUMMARY_FILE = "tf3-save-summary.json"
OLD_SUMMARY_FILE = "summary.json"
# Any layout change raises the version and adds a new schema file; committed ones are never edited.
SCHEMA_VERSION = 8
SCHEMA_URL = ("https://raw.githubusercontent.com/WuphonsReach/tf3-save-format/main/tools/schema/"
              f"tf3-save-summary.v{SCHEMA_VERSION}.schema.json")
# Every key, in the order written (the schema file of SCHEMA_VERSION).
FIELDS = ["$schema", "schema_version", "name", "mod_id", "kind", "source_name", "source_size", "author", "tags",
          "url", "tools_commit", "error", "version", "first_version", "map_seed", "start_year", "map_w_m", "map_h_m",
          "header_money", "header_counter", "climate", "economy", "name_list", "is_map_editor", "header_partial",
          "stream_bytes", "calendar", "journal", "vehicles", "industries", "company", "counters", "cycles", "subsidies", "town_states", "town_records", "towns",
          "settings", "mods", "cargo_list", "cargo_from_mods"]

INDEX_COLS = ["map_seed", "mod_id", "name", "author", "source_name", "version", "start_year", "map_size", "map_size_name",
              "map_format", "map_ratio", "map_w_m", "map_h_m", "climate",
              "name_list", "mods", "mod_list", "is_map_editor", "start_layout_towns", "records", "towns_names", "towns_header", "towns_states", "industries", "stream_bytes", "header", "kind",
              "date", "calendar_speed", "play_speed", "rank", "journal_bookings", "play_periods", "income_periods",
              *INDEX_NAMES, "tools_commit"]


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
        "tools_commit": closure_commit("mine_summary.py"),
    })
    try:
        data = decompress(open(path, "rb").read())
        h = read_header(path, data)
        s = h.get("settings", {})
        res = dict(h.get("resources", []))
        entries = cargo_entries(data)
        cargo_names = [n for _, n, _ in entries] if entries else None
        states = summarise_states(data)
        summary.update({
            "version": h["version"],
            "first_version": h.get("first_version"),
            "map_seed": h.get("map_seed"),
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
            "journal": play_summary(data, h["money"]),
            "vehicles": summarise_vehicles(data),
            "industries": count_industries(data),
            **states,
            "town_records": summarise_records(recs := scan_records(data), cargo_names, data),
            "towns": summarise_towns(data, recs, states["town_states"]),
            "settings": {k: setting_label(k, v) for k, v in sorted(s.items())} if s else None,
            "mods": [m["id"] for m in h["mods"]],
            "cargo_list": cargo_names,
            "cargo_from_mods": {n: m for _, n, m in entries if m} if entries else None,
        })
        del data
    except Exception as e:  # truncated download, unknown format, ...
        summary["error"] = f"{type(e).__name__}: {e}"
    return summary


def summarise_vehicles(data):
    try:
        return count_vehicles(data)
    except ValueError:        # no model table found (the reader raises ValueError)
        return None


def setting_position_name(settings, key):
    """('3', 'Medium') from a settings label like "3 (Medium, default)"; ('', '') where there is none."""
    label = (settings or {}).get(key)
    if not label:
        return "", ""
    pos, _, rest = str(label).partition(" (")
    return pos, rest.rstrip(")").split(", default")[0]


def index_row(sm):
    tr = sm.get("town_records") or {}
    if sm.get("error"):
        return ([sm.get("map_seed"), sm["mod_id"], sm["name"], sm["author"], sm.get("source_name")] + [""] * 20
                + ["error", sm.get("kind", "savegame")] + [""] * (7 + len(INDEX_NAMES)) + [sm.get("tools_commit")])
    cal = sm.get("calendar") or {}
    jr = sm.get("journal")
    size, fmt = (setting_position_name(sm.get("settings"), k) for k in ("map.size", "map.format"))
    return [sm.get("map_seed"), sm["mod_id"], sm["name"], sm["author"], sm.get("source_name"), sm["version"], sm["start_year"],
            *size, *fmt, sm["map_w_m"], sm["map_h_m"], sm["climate"], sm["name_list"],
            len(sm["mods"]), ";".join(sm["mods"]), sm["is_map_editor"], tr["starting_layout"], tr["records"],
            (sm.get("towns") or {}).get("count"), tr.get("table_count"), sm.get("town_states"),
            (sm.get("industries") or {}).get("count"),
            sm["stream_bytes"], "partial" if sm["header_partial"] else "ok", sm.get("kind", "savegame"),
            cal.get("date"), cal.get("calendar_speed"), cal.get("play_speed"),
            (sm.get("company") or {}).get("rank_earned"),
            *((jr[k] if jr else "") for k in ("bookings", "play_periods", "income_periods")),
            *index_values(sm.get("vehicles")), sm.get("tools_commit")]


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".sav"):
        sys.exit("usage: mine_summary.py SAVE.sav")
    json.dump(summarise_save(sys.argv[1], None, None), sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
