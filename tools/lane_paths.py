#!/usr/bin/env python3
"""Lane-path records: the game's own arc length and curve speed per edge, and the connections inside a node (docs/lane-paths.md).

Usage:
  lane_paths.py SAVE.sav [--near X,Y,RADIUS] [--family street|track|all] [--nodes] [--json]

The save keeps, apart from the street-edge table, a table of path records. One kind runs along an
edge (node a, a slot number, node b, a slot number) and one kind lies inside a node (the same node
twice, two slot numbers). Both start with five u32 (node, slot, node, slot, 2) and carry, at the same places, the
path's length in metres, the type's speed and the speed the path's bend allows (in m/s). The bend
speed is the number the speed-limit layer shows, before rounding to a whole number (a straight
path holds a huge value, 213.9 m/s). This prints, per edge, that stored speed next to the value the
rule in docs/road-speeds.md gives, and with --nodes the connections inside each node.

  --near X,Y,R   only edges with an end within R metres of (X, Y)
  --family F     track (default), street or all (street edges mostly have no record of this kind)
  --nodes        list the node connections instead (node, slot pair, length, stored speed)
  --json         JSON instead of a table

Reads a save, writes nothing. Standard library only; edges are read as in street_edges.py.
"""
import argparse
import json
import math
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edge_speeds import edge_speed  # noqa: E402
from street_edges import load, read_edges  # noqa: E402

HEAD = rb"([\x01-\xff][\x00-\xff]{2}\x00)(.{4})([\x01-\xff][\x00-\xff]{2}\x00)(.{4})\x02\x00\x00\x00"
LENGTH, TYPE_SPEED, CURVE_SPEED = 12, 15, 16     # float index after the five u32
NO_LIMIT = 200.0                                  # m/s: a straight path holds 213.9
SAMPLE = 24                                       # edges used to find where the table lies
MARGIN = 6 << 20


def find_region(data, edges):
    """(start, end) of the stream that holds the path records, found by looking for the edge-path
    pattern of a spread of edges; None when none of them is found."""
    hits = []
    step = max(1, len(edges) // SAMPLE)
    for e in edges[::step]:
        i = data.find(struct.pack("<IIII", e["a"], 0, e["b"], 0) + b"\x02\x00\x00\x00")   # a plain edge has slot 0 at both ends
        if i >= 0:
            hits.append(i)
    if not hits:
        return None
    hits.sort()
    mid = hits[len(hits) // 2]
    near = [h for h in hits if abs(h - mid) < 64 << 20]
    return max(0, min(near) - MARGIN), min(len(data), max(near) + MARGIN)


def _record(data, o):
    f = struct.unpack_from("<24f", data, o + 20)
    curve = f[CURVE_SPEED]
    return {"length": f[LENGTH], "type_kmh": f[TYPE_SPEED] * 3.6,
            "curve_kmh": None if curve >= NO_LIMIT or curve <= 0 else curve * 3.6, "offset": o}


def read_paths(data, edges, region=None):
    """{(a, b): record} for the edges that have a path record, a record being a dict with `length`
    (m), `type_kmh`, `curve_kmh` (None for no limit) and `offset`; and the region used."""
    region = region or find_region(data, edges)
    if region is None:
        return {}, None
    wanted = {(e["a"], e["b"]) for e in edges}
    out = {}
    for m in re.finditer(HEAD, data[region[0]:region[1]], re.S):
        a, sa, b, sb = struct.unpack("<I4sI4s", m.group(1) + m.group(2) + m.group(3) + m.group(4))
        if a != b and (a, b) in wanted:
            rec = _record(data, region[0] + m.start())
            rec["slots"] = struct.unpack("<II", sa + sb)
            old = out.get((a, b))
            if old is None or (rec["curve_kmh"] or 1e9) < (old["curve_kmh"] or 1e9):
                out[(a, b)] = rec                  # the lowest, where an edge has several paths
    return out, region


def read_node_links(data, region):
    """{node: [(slot a, slot b, record)]} for the path records that start and end at one node."""
    out = {}
    for m in re.finditer(HEAD, data[region[0]:region[1]], re.S):
        a, sa, b, sb = struct.unpack("<I4sI4s", m.group(1) + m.group(2) + m.group(3) + m.group(4))
        if a == b and 0 < a < 1 << 24:
            sl = struct.unpack("<II", sa + sb)
            if sl[0] < 64 and sl[1] < 64:
                out.setdefault(a, []).append((sl[0], sl[1], _record(data, region[0] + m.start())))
    return out


def main():
    ap = argparse.ArgumentParser(description="Lane-path records of a TF3 save")
    ap.add_argument("save")
    ap.add_argument("--near")
    ap.add_argument("--family", choices=("street", "track", "all"), default="track")
    ap.add_argument("--nodes", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    data = load(args.save, False)
    all_edges = read_edges(data)
    edges = [e for e in all_edges if args.family == "all" or e["family"] == args.family]
    near = None
    if args.near:
        x, y, r = (float(v) for v in args.near.split(","))

        def near(p):
            return math.hypot(p[0] - x, p[1] - y) <= r
    paths, region = read_paths(data, all_edges)
    if region is None:
        sys.exit("no path records found")
    if args.nodes:
        rows = []
        pos = {}
        for e in all_edges:
            pos[e["a"]], pos[e["b"]] = e["p0"], e["p1"]
        for node, links in sorted(read_node_links(data, region).items()):
            if node not in pos or (near and not near(pos[node])):
                continue
            for sa, sb, rec in links:
                rows.append({"node": node, "slots": [sa, sb], "length": round(rec["length"], 2),
                             "curve_kmh": None if rec["curve_kmh"] is None else round(rec["curve_kmh"], 2)})
        if args.json:
            print(json.dumps(rows, indent=1))
        else:
            print("%d node connections" % len(rows))
            for r in rows:
                print("%x  slots %d-%d  %6.2f m  stored %s" % (
                    r["node"], r["slots"][0], r["slots"][1], r["length"], r["curve_kmh"] or "none"))
        return
    rows = []
    for e in edges:
        rec = paths.get((e["a"], e["b"]))
        if rec is None or (near and not (near(e["p0"]) or near(e["p1"]))):
            continue
        _, rule, kmax, turn = edge_speed(data, e)
        rows.append({"a": e["a"], "b": e["b"], "type": e["type"], "chord": round(e["length"], 1),
                     "arc": round(rec["length"], 1), "turn_deg": round(turn, 1),
                     "stored_kmh": None if rec["curve_kmh"] is None else round(rec["curve_kmh"], 2),
                     "rule_kmh": None if rule is None else round(rule, 1)})
    if args.json:
        print(json.dumps(rows, indent=1))
        return
    print("%d of %d edges have a path record" % (len(rows), len(edges)))
    for r in rows:
        print("%x > %x  %-14s chord %6.1f arc %6.1f turn %5.1f  stored %-7s rule %s" % (
            r["a"], r["b"], r["type"] or "?", r["chord"], r["arc"], r["turn_deg"],
            r["stored_kmh"] if r["stored_kmh"] is not None else "none", r["rule_kmh"]))


if __name__ == "__main__":
    main()
