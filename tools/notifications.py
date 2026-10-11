#!/usr/bin/env python3
"""List the notifications of a TF3 save: type, clock, flags, entities, names, parameters.

Usage:
  notifications.py SAVE.sav [--type REGEX] [--since CLOCK] [--last N] [--open] [--json]
  notifications.py SAVE.sav --summary
  notifications.py SAVE.sav --lines

SAVE may also be a stream already decompressed to a file (add --stream). Output goes to the
terminal. Only reads: no save is written.

Default: one line per entry, oldest first (the state's `history` order): id, clock, type (the
script name without its folder and `.script`), flags (D dismissed, E expired, T tracked, P has a
`persisting` list), the entity ids in `params`, the names the entry kept in `simParams`
(`id=name`, or `name=...` for a line, town or similar), and the remaining params. `--type` keeps
types whose name matches the regex, `--since` entries at or after a clock value, `--last` the
newest N, `--open` the entries not dismissed, `--json` prints the simplified entries as JSON.

`--summary`: entries per type with first and last clock and flag counts, then the size of the
bookkeeping tables. `--lines`: the line entities named by `line_warning` entries (`entity` and
`simParams.lineName`), whether each is a key of `line2problemTimestamp`, and each entry's
`lineProblem` and `lineIssues`. It does not pair vehicles with lines.

The game trims the table to about 100 entries but keeps those with a `persisting` list, so a long
game shows mostly its recent ones (docs/notifications.md). Layout and what each type holds: docs/notifications.md. A name taken from a save can be a
player's own text; the output masks anything that looks like a path.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tf3save import decompress, script_state  # noqa: E402

STATE_PATH = "game_mechanics/notifications/notifications.gs"
TYPE_FOLDER = re.compile(r".*/")
PATHLIKE = re.compile(r"(?:^|\s)(?:/[A-Za-z0-9_.-]+){2,}|[A-Za-z]:\\|\\\\")


def read_notifications(data):
    """The notifications state (docs/notifications.md) as a dict, or None if it is not found."""
    return script_state(data, STATE_PATH)


def as_list(value):
    """A Lua list (a table keyed 1.0, 2.0, ...) as a Python list; anything else unchanged."""
    if isinstance(value, dict) and value and all(isinstance(k, float) for k in value):
        keys = sorted(value)
        if keys == [float(i) for i in range(1, len(keys) + 1)]:
            return [value[k] for k in keys]
    return value


def clean(value):
    """Plain Python for a Lua value: whole floats become ints, lists become lists, an
    `{entity, revision}` pair becomes the entity id, and a path-like string is masked."""
    value = as_list(value)
    if isinstance(value, float):
        return int(value) if value == int(value) else value
    if isinstance(value, str):
        return "<masked>" if PATHLIKE.search(value) else value
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, dict):
        if set(value) == {"entity", "revision"}:
            return clean(value["entity"])
        return {(int(k) if isinstance(k, float) and k == int(k) else k): clean(v) for k, v in value.items()}
    return value


def kind(entry):
    """The type's script name without its folder: `line_warning`, `overcrowding`, ..."""
    path = entry["notification"].get("type", "")
    return TYPE_FOLDER.sub("", path).removesuffix(".script")


def entities(value, out=None):
    """Every entity id in a cleaned params value: lists of ids under `entity`, `entities` and any
    key ending in `Entity`."""
    out = [] if out is None else out
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(k, str) and (k in ("entity", "entities") or k.endswith("Entity")):
                out.extend(v if isinstance(v, list) else [v])
            else:
                entities(v, out)
    elif isinstance(value, list):
        for v in value:
            entities(v, out)
    return [e for e in out if isinstance(e, int)]


def names(sim):
    """(entity id or label, name) pairs from a cleaned `simParams`: `mapping` entries, and the
    single-name keys `lineName`, `townName`, `name`."""
    out = []
    for k, v in sim.items():
        if k == "mapping" and isinstance(v, dict):
            for e, n in v.items():
                out.append((e, n[0] if isinstance(n, list) and n else n))
        elif k == "typeMapping":
            continue
        elif isinstance(v, str):
            out.append((k, v))
    return out


def entries(state):
    """The entries in `history` order (oldest first) as dicts: id, timestamp, kind, flags,
    entities, names, params (without the entity lists), persisting."""
    table = state.get("notifications", {})
    order = as_list(state.get("history", {}))
    order = order if isinstance(order, list) else []
    out = []
    for nid in order + [i for i in table if i not in order]:
        e = table.get(nid)
        if e is None:
            continue
        note = e["notification"]
        params = clean(note.get("params", {}))
        out.append({
            "id": int(nid),
            "timestamp": int(e.get("timestamp", 0)),
            "kind": kind(e),
            "dismissed": bool(e.get("dismissed")),
            "expired": bool(e.get("expired")),
            "tracked": bool(e.get("tracked")),
            "persisting": "persisting" in e,
            "entities": entities(params),
            "names": names(clean(note.get("simParams", {}))),
            "params": params,
        })
    return out


def flags(e):
    return "".join(c if e[k] else "-" for c, k in (("D", "dismissed"), ("E", "expired"), ("T", "tracked"), ("P", "persisting")))


def line_text(e):
    """The remaining params, with the entity lists left out (they have their own column)."""
    p = e["params"]
    if isinstance(p, dict):
        p = {k: v for k, v in p.items() if k not in ("entity", "entities") and not str(k).endswith("Entity")}
    return json.dumps(p, separators=(",", ":"), sort_keys=True) if p not in ({}, [], None) else ""


def print_entry(e):
    nm = ",".join(f"{k}={v}" for k, v in e["names"])
    print(f"{e['id']:>7} {e['timestamp']:>11} {e['kind']:<32} {flags(e)} ents {e['entities']} {nm} {line_text(e)}".rstrip())


def summary(state, es):
    by = {}
    for e in es:
        s = by.setdefault(e["kind"], [0, e["timestamp"], e["timestamp"], 0, 0, 0])
        s[0] += 1
        s[1] = min(s[1], e["timestamp"])
        s[2] = max(s[2], e["timestamp"])
        s[3] += e["dismissed"]
        s[4] += e["expired"]
        s[5] += e["persisting"]
    print(f"{len(es)} entries, maxId {clean(state.get('maxId'))}, version {clean(state.get('version'))}")
    print(f"{'type':<34}{'count':>6}{'first':>12}{'last':>12} dismissed expired persisting")
    for k, (n, lo, hi, d, x, p) in sorted(by.items(), key=lambda kv: -kv[1][0]):
        print(f"{k:<34}{n:>6}{lo:>12}{hi:>12} {d:>9} {x:>7} {p:>10}")
    for key in ("wastedVehicles", "vehicle2problem", "stationGroup2overflowResolvedTimestamp",
                "noRoadConnectionUpdateTimestamp", "line2problemTimestamp"):
        v = state.get(key)
        print(f"{key}: {len(v) if isinstance(v, dict) else clean(v)}")


def lines(state, es):
    """Print each line entity named by a line_warning entry, with its problem timestamp."""
    stamps = {int(k): int(v) for k, v in state.get("line2problemTimestamp", {}).items()}
    seen = {}
    for e in es:
        if e["kind"] != "line_warning" or not e["entities"]:
            continue
        line = e["entities"][0]
        name = next((n for k, n in e["names"] if k == "lineName"), "")
        p = e["params"].get("param", {}) if isinstance(e["params"], dict) else {}
        issues = p.get("lineIssues", []) if isinstance(p, dict) else []
        problem = p.get("lineProblem") if isinstance(p, dict) else None
        seen.setdefault(line, (name, []))[1].append((e["id"], e["timestamp"], problem, issues))
    print(f"{'line':>8}  {'in line2problemTimestamp':<26} name")
    for line, (name, hits) in sorted(seen.items()):
        mark = stamps[line] if line in stamps else "no"
        print(f"{line:>8}  {str(mark):<26} {name}")
        for nid, ts, problem, issues in hits:
            print(f"{'':>8}  entry {nid} at {ts}: lineProblem {problem}, lineIssues [type, stop index, cargo id] {issues}")
    missing = sorted(set(stamps) - set(seen))
    if missing:
        print(f"in line2problemTimestamp without a line_warning entry in the table: {missing}")


def main():
    ap = argparse.ArgumentParser(description="List the notifications of a TF3 save.")
    ap.add_argument("save")
    ap.add_argument("--stream", action="store_true", help="SAVE is an already decompressed stream")
    ap.add_argument("--type", help="regex a type name must match (search, not full match)")
    ap.add_argument("--since", type=int, help="only entries at or after this clock value")
    ap.add_argument("--last", type=int, help="only the newest N entries")
    ap.add_argument("--open", action="store_true", help="only entries not dismissed")
    ap.add_argument("--json", action="store_true", help="print the entries as JSON")
    ap.add_argument("--summary", action="store_true", help="entries per type and the bookkeeping tables")
    ap.add_argument("--lines", action="store_true", help="line entities named by line_warning entries")
    args = ap.parse_args()

    with open(args.save, "rb") as f:
        raw = f.read()
    data = raw if args.stream else decompress(raw)
    state = read_notifications(data)
    if state is None:
        sys.exit("no notifications state found")
    es = entries(state)

    if args.summary:
        summary(state, es)
        return
    if args.lines:
        lines(state, es)
        return
    if args.type:
        want = re.compile(args.type)
        es = [e for e in es if want.search(e["kind"])]
    if args.since is not None:
        es = [e for e in es if e["timestamp"] >= args.since]
    if args.open:
        es = [e for e in es if not e["dismissed"]]
    if args.last:
        es = es[-args.last:]
    if args.json:
        json.dump(es, sys.stdout, indent=1)
        print()
    else:
        for e in es:
            print_entry(e)


if __name__ == "__main__":
    main()
