#!/usr/bin/env python3
"""The speed limit the game's speed layer shows for each street edge (docs/road-speeds.md).

Usage:
  edge_speeds.py SAVE.sav [--near X,Y,RADIUS] [--family street|track|all] [--curved] [--json] [--accel A]

Each edge record stores its type's speed (the sixth float after the two tangents, in m/s). On a
curved edge the layer shows a lower number. This prints, per edge, the stored speed and the
number the rule in the note predicts: the lower of the stored speed and 3.6 * sqrt(A / k) km/h,
k being the largest curvature of the cubic Hermite curve through the edge's two end positions
with its two stored tangents, A a lateral acceleration (default 2.5 m/s^2). The rule was read
off about 45 labels (road and rail) in screenshots of one game; treat the curved values as +-1 km/h.

  --near X,Y,R   only edges with an end within R metres of (X, Y)
  --family F     street (default), track (rails) or all
  --curved       only edges the rule lowers
  --accel A      the acceleration in m/s^2
  --json         JSON instead of a table

Reads a save, writes nothing. Standard library only; the edge table is read as in street_edges.py.
"""
import argparse
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from street_edges import load, read_edges  # noqa: E402

LANE_SPEED_WORD = 5     # float index after the tangents (record offset + 56), seen on 604 saves
ACCEL = 2.5


def hermite_curvature(p0, p1, t0, t1, n=200):
    """(largest curvature, length) of the cubic Hermite curve with those end points and tangents."""
    kmax = 0.0
    length = 0.0
    prev = None
    for i in range(n + 1):
        t = i / n
        d1 = [(6 * t * t - 6 * t) * p0[k] + (3 * t * t - 4 * t + 1) * t0[k]
              + (-6 * t * t + 6 * t) * p1[k] + (3 * t * t - 2 * t) * t1[k] for k in (0, 1)]
        d2 = [(12 * t - 6) * p0[k] + (6 * t - 4) * t0[k] + (-12 * t + 6) * p1[k] + (6 * t - 2) * t1[k]
              for k in (0, 1)]
        speed = math.hypot(d1[0], d1[1])
        if speed > 1e-9:
            kmax = max(kmax, abs(d1[0] * d2[1] - d1[1] * d2[0]) / speed ** 3)
        if prev is not None:
            length += (speed + prev) / 2 / n
        prev = speed
    return kmax, length


def edge_speed(data, e, accel=ACCEL):
    """(stored km/h or None, predicted shown km/h or None, largest curvature, turn in degrees)."""
    o = e["offset"]
    t0 = struct.unpack_from("<3f", data, o + 32)[:2]
    t1 = struct.unpack_from("<3f", data, o + 44)[:2]
    word = struct.unpack_from("<f", data, o + 56 + 4 * LANE_SPEED_WORD)[0]
    stored = word * 3.6 if 1.0 < word < 60.0 else None
    kmax, _ = hermite_curvature(e["p0"][:2], e["p1"][:2], t0, t1)
    a0, a1 = math.atan2(t0[1], t0[0]), math.atan2(t1[1], t1[0])
    turn = math.degrees(abs((a1 - a0 + math.pi) % (2 * math.pi) - math.pi))
    if stored is None:
        return None, None, kmax, turn
    shown = min(stored, 3.6 * math.sqrt(accel / max(kmax, 1e-9)))
    return stored, shown, kmax, turn


def main():
    ap = argparse.ArgumentParser(description="Speed limits of the street edges of a TF3 save")
    ap.add_argument("save")
    ap.add_argument("--near")
    ap.add_argument("--family", choices=("street", "track", "all"), default="street")
    ap.add_argument("--curved", action="store_true")
    ap.add_argument("--accel", type=float, default=ACCEL)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    data = load(args.save, False)
    edges = [e for e in read_edges(data) if args.family == "all" or e["family"] == args.family]
    if args.near:
        x, y, r = (float(v) for v in args.near.split(","))
        edges = [e for e in edges if any(math.hypot(p[0] - x, p[1] - y) <= r for p in (e["p0"], e["p1"]))]
    rows = []
    for e in edges:
        stored, shown, kmax, turn = edge_speed(data, e, args.accel)
        if args.curved and (shown is None or shown >= stored - 0.01):
            continue
        rows.append({"a": e["a"], "b": e["b"], "type": e["type"], "length": round(e["length"], 1),
                     "turn_deg": round(turn, 1), "max_curvature": kmax,
                     "stored_kmh": None if stored is None else round(stored, 1),
                     "shown_kmh": None if shown is None else round(shown, 1),
                     "mid": [round((e["p0"][0] + e["p1"][0]) / 2, 1), round((e["p0"][1] + e["p1"][1]) / 2, 1)]})
    if args.json:
        print(json.dumps(rows, indent=1))
        return
    print(f"{len(rows)} edges (of {len(edges)} edges), lateral acceleration {args.accel} m/s^2")
    for r in rows:
        print(f"{r['a']:x} > {r['b']:x}  {r['type'] or '?':<22} {r['length']:6.1f} m  turn {r['turn_deg']:5.1f}  "
              f"stored {r['stored_kmh']}  shown {r['shown_kmh']}  mid ({r['mid'][0]}, {r['mid'][1]})")


if __name__ == "__main__":
    main()
