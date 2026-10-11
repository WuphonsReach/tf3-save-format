#!/usr/bin/env python3
"""List the parcels of a TF3 save, and compare two saves.

Usage:
  parcels.py SAVE.sav [--near X,Y,RADIUS] [--json] [--points]
  parcels.py --diff OLD.sav NEW.sav [--near X,Y,RADIUS] [--json]

SAVE may also be a stream already decompressed to a file (add --stream). Output goes to the
terminal. Only reads: no save is written.

A parcel is a strip along a street edge where a town building can stand (docs/parcels.md): the
entity id of the street edge, a side, a position along the edge, and a list of faces. A face is an
8 m square given as four (x, y, z) points, followed by a flag word (bit 1 something stands on the
cell, bit 2 another parcel overlaps it). Default output is a summary: where the table starts, how
many parcels, edges and faces, and how often each flag word occurs. `--near X,Y,R` prints one line
per parcel whose first face is within R metres of (X, Y): the parcel's index in the table, the
edge id, the side (L or R), the position along the edge, the flag words of its faces and the
centre of its first face (L is the left of the edge, side byte 1; checked on one edge). `--points`
adds the four corners of every face to the JSON output.

`--diff` compares two saves of one game by table index and prints the parcels whose flag words
changed (with the first face's centre), and says how many parcels were appended. A parcel's index
is only a name inside one game: the table only appended in the tests the notes were written from
(docs/parcels.md), but a save of another game has another table.

The parcel's own entity id is not in the table (docs/parcels.md), so the output has the index
and the street edge's id, not a parcel id. Edge ids, positions and flags are facts about the map,
not about the player, so the output needs no masking.
"""
import argparse
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tf3save import decompress  # noqa: E402

# A record starts with the edge id, a side byte, the position along the edge and the face count;
# the first face's point count (4) follows, so two u32 fours in a row mark the first record.
# The table itself starts with a u32 count, 13 bytes before that pair.
_MARK = struct.pack("<II", 4, 4)
HEAD = struct.Struct("<IBfI")   # edge id, side, position along the edge, face count
FACE = struct.Struct("<I12fI")  # point count (4), four (x, y, z), flag word
TAIL = struct.Struct("<f")      # 8.0 or 7.0 in every parcel seen
MAX_EDGE = 1 << 24
MAX_COORD = 40000.0


def _face_ok(face):
    if face[0] != 4:
        return False
    pts = face[1:13]
    if not all(math.isfinite(v) and abs(v) < MAX_COORD for v in pts):
        return False
    return face[13] < 8


def read_parcels(data, start=None):
    """Return (offset of the count, parcels). Each parcel is a dict: `edge` (entity id of the street
    edge), `left` (0 or 1), `curve` (position along the edge, 0 to 1, falling along the table's
    order), `tail` (the f32 after the faces), `faces` (a list of (points, flags) where points are
    four (x, y, z) tuples) and `index` (position in the table). Returns (None, []) if no table is
    found. `start` is the count's offset if already known."""
    if start is not None:
        parcels = _chain(data, start)
        return (start, parcels) if parcels else (None, [])
    pos = data.find(_MARK)
    while pos >= 0:
        s = pos - 13
        if s >= 0:
            parcels = _chain(data, s)
            if parcels:
                return s, parcels
        pos = data.find(_MARK, pos + 1)
    return None, []


def _chain(data, s):
    n = struct.unpack_from("<I", data, s)[0]
    if not 1 <= n <= 2_000_000:
        return None
    p = s + 4
    out = []
    try:
        for i in range(n):
            edge, left, curve, nf = HEAD.unpack_from(data, p)
            if edge >= MAX_EDGE or left > 1 or not 0.0 <= curve <= 1.0001 or not 1 <= nf <= 8:
                return None
            p += HEAD.size
            faces = []
            for _ in range(nf):
                f = FACE.unpack_from(data, p)
                if not _face_ok(f):
                    return None
                faces.append((tuple(tuple(f[1 + 3 * k:4 + 3 * k]) for k in range(4)), f[13]))
                p += FACE.size
            tail = TAIL.unpack_from(data, p)[0]
            p += TAIL.size
            out.append({"index": i, "edge": edge, "left": left, "curve": curve, "tail": tail, "faces": faces})
    except struct.error:
        return None
    return out


def centre(face):
    pts = face[0]
    return (sum(p[0] for p in pts) / 4, sum(p[1] for p in pts) / 4)


def _near(parcel, box):
    cx, cy, r = box
    x, y = centre(parcel["faces"][0])
    return math.hypot(x - cx, y - cy) <= r


def parse_near(text):
    try:
        x, y, r = (float(v) for v in text.split(","))
    except ValueError:
        raise SystemExit("--near wants X,Y,RADIUS in map metres")
    return x, y, r


def load(path, is_stream):
    raw = open(path, "rb").read()
    data = raw if is_stream else decompress(raw)
    start, parcels = read_parcels(data)
    if not parcels:
        raise SystemExit(f"{os.path.basename(path)}: no parcel table found")
    return start, parcels


def fmt(p):
    x, y = centre(p["faces"][0])
    flags = " ".join(str(f) for _, f in p["faces"])
    return (f"#{p['index']:<5} edge {p['edge']:<6} {'L' if p['left'] else 'R'} pos {p['curve']:.3f}"
            f"  flags {flags:<8} first face ({x:.1f}, {y:.1f})")


def summary(start, parcels, name):
    flags = {}
    for p in parcels:
        for _, f in p["faces"]:
            flags[f] = flags.get(f, 0) + 1
    edges = {p["edge"] for p in parcels}
    faces = sum(len(p["faces"]) for p in parcels)
    print(f"{name}: parcel table count at stream offset {start}")
    print(f"  {len(parcels)} parcels on {len(edges)} street edges, {faces} faces")
    print("  flag words: " + ", ".join(f"{k}: {v}" for k, v in sorted(flags.items())))
    tails = {}
    for p in parcels:
        tails[p["tail"]] = tails.get(p["tail"], 0) + 1
    print("  tail values: " + ", ".join(f"{k:g}: {v}" for k, v in sorted(tails.items())))


def diff(old, new, box):
    out = []
    n = min(len(old), len(new))
    for a, b in zip(old[:n], new[:n]):
        if a["edge"] != b["edge"] or a["left"] != b["left"] or len(a["faces"]) != len(b["faces"]):
            out.append(("layout", a, b))
        elif [f for _, f in a["faces"]] != [f for _, f in b["faces"]]:
            out.append(("flags", a, b))
    out = [o for o in out if box is None or _near(o[2], box)]
    return out, len(new) - len(old)


def main():
    ap = argparse.ArgumentParser(description="List the parcels of a save, or compare two saves.")
    ap.add_argument("save", nargs="*", help="SAVE.sav (or OLD NEW with --diff)")
    ap.add_argument("--near", help="X,Y,RADIUS: only parcels whose first face is within RADIUS of (X, Y)")
    ap.add_argument("--stream", action="store_true", help="the files are already decompressed streams")
    ap.add_argument("--diff", action="store_true", help="compare OLD with NEW by table index")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--points", action="store_true", help="with --json, add the corners of every face")
    args = ap.parse_args()
    box = parse_near(args.near) if args.near else None
    if args.diff:
        if len(args.save) != 2:
            ap.error("--diff wants OLD and NEW")
        _, old = load(args.save[0], args.stream)
        _, new = load(args.save[1], args.stream)
        rows, appended = diff(old, new, box)
        if args.json:
            json.dump({"appended": appended,
                       "changed": [{"kind": k, "index": b["index"], "edge": b["edge"], "left": b["left"],
                                    "old_flags": [f for _, f in a["faces"]], "new_flags": [f for _, f in b["faces"]],
                                    "centre": centre(b["faces"][0])} for k, a, b in rows]}, sys.stdout, indent=1)
            print()
            return
        print(f"{len(old)} parcels in OLD, {len(new)} in NEW ({appended:+d} appended)")
        for kind, a, b in rows:
            x, y = centre(b["faces"][0])
            before = " ".join(str(f) for _, f in a["faces"])
            after = " ".join(str(f) for _, f in b["faces"])
            print(f"{kind:<6} #{b['index']:<5} edge {b['edge']:<6} {'L' if b['left'] else 'R'} pos {b['curve']:.3f}"
                  f"  flags {before} -> {after}  first face ({x:.1f}, {y:.1f})")
        if not rows:
            print("no parcel changed")
        return
    if len(args.save) != 1:
        ap.error("give one save (or two with --diff)")
    start, parcels = load(args.save[0], args.stream)
    name = os.path.basename(args.save[0])
    sel = [p for p in parcels if box is None or _near(p, box)]
    if args.json:
        rows = []
        for p in sel:
            row = {"index": p["index"], "edge": p["edge"], "left": p["left"], "curve": p["curve"],
                   "tail": p["tail"], "flags": [f for _, f in p["faces"]], "first_face_centre": centre(p["faces"][0])}
            if args.points:
                row["faces"] = [[list(pt) for pt in pts] for pts, _ in p["faces"]]
            rows.append(row)
        json.dump({"table_offset": start, "parcels": rows}, sys.stdout, indent=1)
        print()
        return
    if box is None:
        summary(start, parcels, name)
        return
    for p in sel:
        print(fmt(p))
    print(f"{len(sel)} parcels within {box[2]:g} m of ({box[0]:g}, {box[1]:g})")


if __name__ == "__main__":
    main()
