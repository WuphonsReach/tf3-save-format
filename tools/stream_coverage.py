#!/usr/bin/env python3
"""Estimate how much of a save's decompressed stream the readers in tools/ account for.

Each known structure is found with the reader that already exists for it, and its byte range is
put in one of two tiers:

- `read`: a reader parses the fields (header, model table, terrain record and heightmap, the
  fields of each model instance and street edge, road strips, parcels, building and town records,
  the entity table, the names table, the `items*` statistics lists, the script states).
- `located`: the notes place the structure and say what it holds, but no reader parses it byte
  by byte (the bytes between neighbouring instance or street-edge records, the lane-path region,
  the ground-texture polygon lists found by their `.gtex` names).

Everything else is `unaccounted`. The biggest unaccounted gaps are listed with a rough character:
share of zero bytes, share of 4-byte words that read as ordinary floats or as small integers, share
of u16 values under 256 (a grid of small values, such as a map layer), and
how many resource names of each kind (`.gtex`, `.mdl`, ...) they hold. No string from the save is
printed, so the output carries no names or paths from the player's machine.

It is an estimate. A reader's pattern can miss records (a run of town records in another shape),
and a `located` range can hold bytes of another structure. Some readers scan the whole stream, so
a large save (700 MB of stream) takes a few minutes and a few GB of memory.

    stream_coverage.py SAVE.sav [SAVE.sav ...] [--gaps N] [--json] [--stream]
"""
import argparse
import json
import math
import os
import re
import struct
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tf3save  # noqa: E402
import items_lists  # noqa: E402
import lane_paths  # noqa: E402
import model_instances  # noqa: E402
import parcels  # noqa: E402
import street_edges  # noqa: E402
import terrain_heights  # noqa: E402
import town_places  # noqa: E402

INSTANCE_LEN = 68           # the bytes model_instances._INSTANCE matches
INSTANCE_GAP = 400          # neighbouring instance records closer than this are one run
EDGE_LEN = 87               # ".street" plus the two ids and four vec3 street_edges._START reads
EDGE_GAP = 2000             # street-edge records closer than this are one run
GTEX_GAP = 1 << 16          # `.gtex` names closer than this belong to one polygon list
STATE_TAIL = 0.10           # script states are looked for in the last tenth of the stream
TILE_POINTS = 65 * 65

_GTEX = re.compile(rb"([\x05-\xc8])\x00\x00\x00([a-z0-9_/]+\.gtex)")
_STATE_PATH = re.compile(rb"([\x05-\x80])\x00\x00\x00([a-z0-9_]+(?:/[a-z0-9_]+)+\.(?:gs|lua))")
_RESOURCE = re.compile(rb"[a-z0-9_]/[a-z0-9_]+(\.(?:gtex|mdl|con|street_template|street|lua|gs|module|mtl|msh))\b")


class Cover:
    """Byte ranges per (tier, label)."""

    def __init__(self):
        self.ranges = defaultdict(list)
        self.notes = []

    def add(self, tier, label, start, end):
        if end > start:
            self.ranges[(tier, label)].append((start, end))

    def run(self, tier, label, offsets, rec_len, gap):
        """One range per run of records whose starts lie less than `gap` apart."""
        offs = sorted(offsets)
        if not offs:
            return
        first = prev = offs[0]
        for o in offs[1:]:
            if o - prev > gap:
                self.add(tier, label, first, prev + rec_len)
                first = o
            prev = o
        self.add(tier, label, first, prev + rec_len)


def merge(ranges):
    out = []
    for a, b in sorted(ranges):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def size(ranges):
    return sum(b - a for a, b in ranges)


def subtract(ranges, taken):
    """`ranges` minus `taken`, both merged and sorted."""
    out, j = [], 0
    for a, b in ranges:
        while j < len(taken) and taken[j][1] <= a:
            j += 1
        k, cur = j, a
        while k < len(taken) and taken[k][0] < b:
            if taken[k][0] > cur:
                out.append([cur, taken[k][0]])
            cur = max(cur, taken[k][1])
            k += 1
        if cur < b:
            out.append([cur, b])
    return out


def _try(cover, label, fn):
    try:
        fn()
    except Exception as e:                     # one reader failing must not stop the estimate
        cover.notes.append(f"{label}: not found ({type(e).__name__})")


def find_all(data):
    c = Cover()
    n = len(data)
    table_end = [None]

    def model_table():
        paths, end = model_instances.read_model_table(data)
        first = data.find(b"animal/")
        start = data.rfind(struct.pack("<I", len(paths)), 0, first)
        c.add("read", "header", 0, start)
        c.add("read", "model table", start, end)
        table_end[0] = (paths, end)

    def terrain():
        tx, ty, *_ = terrain_heights.read_terrain(data)
        p = data.find(terrain_heights.RESOLUTION)
        c.add("read", "terrain record", p - 12, p + 24)
        key = b"\x0e\x00\x00\x00" + bytes(12) + struct.pack("<II", tx * ty, TILE_POINTS)
        h = data.find(key)
        if h < 0:
            raise ValueError("no heightmap")
        c.add("read", "heightmap", h, h + len(key) + tx * ty * (4 + 2 * TILE_POINTS))

    def instances():
        end = table_end[0][1] if table_end[0] else 0
        starts = []
        for m in model_instances._INSTANCE.finditer(data, end):
            starts.append(m.start())
            c.add("read", "model instances", m.start(), m.end())
        c.run("located", "model instances", starts, INSTANCE_LEN, INSTANCE_GAP)

    def edges():
        es = street_edges.read_edges(data)
        for e in es:
            c.add("read", "street edges", e["offset"] - 7, e["offset"] - 7 + EDGE_LEN)
        c.run("located", "street edges", [e["offset"] - 7 for e in es], EDGE_LEN, EDGE_GAP)
        region = lane_paths.find_region(data, es)
        if region:
            c.add("located", "lane paths", *region)
        else:
            c.notes.append("lane paths: not found")

    def strips():
        for m in street_edges._STRIP.finditer(data):
            c.add("read", "road strips", m.start(), m.end())

    def parcel_table():
        s, ps = parcels.read_parcels(data)
        if s is None:
            raise ValueError("no parcel table")
        c.add("read", "parcels", s, s + 4 + sum(parcels.HEAD.size + len(p["faces"]) * parcels.FACE.size
                                                 + parcels.TAIL.size for p in ps))

    def buildings():
        for m in town_places._BUILDING.finditer(data):
            a, b = struct.unpack("<II", m.group(1) + m.group(2))
            if b not in (a, 0xffffffff) or a == 0:
                continue
            p = m.start()
            k = data[p + 17]
            q = p + 21 + 4 * k
            if q + 20 > n:
                continue
            ids = struct.unpack_from("<%dI" % k, data, p + 21)
            depth, height, town = struct.unpack_from("<IfI", data, q)
            if 1 <= depth <= 4 and 2 < height < 120 and town and all(ids):
                c.add("read", "building records", p, q + 20)

    def towns():
        for r in tf3save.scan_records(data):
            c.add("read", "town records", r["offset"], r["offset"] + 78)

    def entities():
        found = town_places.find_entity_table(data)
        if not found:
            raise ValueError("no entity table")
        start, count = found
        q = start
        for _ in range(count):
            q += 4 + 8 * struct.unpack_from("<I", data, q)[0]
        c.add("read", "entity table", start - 4, q + 4)

    def names():
        found = tf3save.entity_names_at(data)
        if not found:
            raise ValueError("no names table")
        start, ns = found
        c.add("read", "names table", start, start + sum(4 + len(s.encode()) for s in ns))

    def items():
        for hit in items_lists.NAME_AT.finditer(data):
            try:
                f = items_lists.read_field(data, hit.start())
            except (struct.error, ValueError):
                continue
            if f:
                c.add("read", "items lists", hit.start(), f[3])

    def states():
        lo = int(n * (1 - STATE_TAIL))
        for m in _STATE_PATH.finditer(data, lo):
            if m.group(1)[0] != len(m.group(2)):
                continue
            try:
                state, end = tf3save._lua_pairs(data, m.end() + 1)
            except (ValueError, struct.error, IndexError, RecursionError):
                continue
            if state and all(isinstance(k, str) for k in state):
                c.add("read", "script states", m.start(), end)

    def gtex():
        ends = {}
        for m in _GTEX.finditer(data):
            if m.group(1)[0] == len(m.group(2)):
                ends[m.start()] = m.end()
        c.run("located", "ground-texture polygons", list(ends), 0, GTEX_GAP)
        # A run ends at its last name. Add that polygon's vertex list (a byte, a u32 count, x and y
        # f32 pairs) and the per-vertex pairs after it when their count matches (docs/town-leftovers.md).
        key = ("located", "ground-texture polygons")
        runs = []
        for a, b in c.ranges.get(key, []):
            e = ends[b]
            if e + 5 <= n:
                nv = struct.unpack_from("<I", data, e + 1)[0]
                if nv < 1 << 20 and e + 9 + 8 * nv <= n:
                    e += 5 + 8 * nv
                    if struct.unpack_from("<I", data, e)[0] == nv:
                        e = min(n, e + 4 + 8 * nv)
            runs.append((a, e))
        c.ranges[key] = runs

    for label, fn in [("model table", model_table), ("terrain", terrain), ("model instances", instances),
                      ("street edges", edges), ("road strips", strips), ("parcels", parcel_table),
                      ("building records", buildings), ("town records", towns), ("entity table", entities),
                      ("names table", names), ("items lists", items), ("script states", states),
                      ("ground-texture polygons", gtex)]:
        _try(c, label, fn)
    return c


def character(chunk):
    """Rough look at a gap: zeros, float-like and small-integer words (the first MB, best 4-byte
    alignment of each), u16 values under 256, resource names by kind."""
    words = floats = ints = 0
    for al in range(4):                        # records need not keep a 4-byte alignment: take the best
        sample = chunk[al:al + 1_000_000]
        w = len(sample) // 4
        if not w:
            continue
        f = sum(1 for (v,) in struct.iter_unpack("<f", sample[:4 * w])
                if v != 0 and math.isfinite(v) and 1e-3 <= abs(v) <= 1e6)
        i = sum(1 for (v,) in struct.iter_unpack("<I", sample[:4 * w]) if 0 < v < 65536)
        if words == 0 or f / w > floats / words:
            floats, words = f, w
        ints = max(ints, i * words // w)
    u16 = 0.0
    for al in range(2):                        # grids of small u16 values (a map layer) show here
        sample = chunk[al:al + 1_000_000]
        w = len(sample) // 2
        if w:
            u16 = max(u16, sum(1 for (v,) in struct.iter_unpack("<H", sample[:2 * w]) if 0 < v < 256) / w)
    kinds = Counter(m.group(1).decode() for m in _RESOURCE.finditer(chunk))
    return {"zeros": round(chunk.count(0) / len(chunk), 3) if chunk else 0,
            "float_words": round(floats / words, 3) if words else 0,
            "small_int_words": round(ints / words, 3) if words else 0,
            "small_u16": round(u16, 3),
            "resources": dict(kinds.most_common(5))}


def estimate(data, gaps=10):
    c = find_all(data)
    n = len(data)
    read = merge(r for (tier, _), rs in c.ranges.items() if tier == "read" for r in rs)
    located = subtract(merge(r for (tier, _), rs in c.ranges.items() if tier == "located" for r in rs), read)
    covered = merge(read + located)
    holes, prev = [], 0
    for a, b in covered:
        if a > prev:
            holes.append((prev, a))
        prev = max(prev, b)
    if prev < n:
        holes.append((prev, n))
    by_label = []
    for (tier, label), rs in sorted(c.ranges.items()):
        m = merge(rs)
        if tier == "located":
            m = subtract(m, read)
        by_label.append({"tier": tier, "label": label, "bytes": size(m), "share": round(size(m) / n, 5)})
    big = sorted(holes, key=lambda h: h[0] - h[1])[:gaps]
    return {
        "stream_bytes": n,
        "read": round(size(read) / n, 5),
        "located": round(size(located) / n, 5),
        "unaccounted": round(1 - size(covered) / n, 5),
        "gaps_under_1mb": round(sum(b - a for a, b in holes if b - a < 1 << 20) / n, 5),
        "structures": by_label,
        "largest_gaps": [{"at": round(a / n, 5), "bytes": b - a, **character(data[a:b])} for a, b in big],
        "notes": c.notes,
    }


def print_report(name, r):
    n = r["stream_bytes"]
    print(f"{name}: stream {n / 1e6:.1f} MB")
    print(f"  read {r['read']:6.1%}   located {r['located']:6.1%}   unaccounted {r['unaccounted']:6.1%}"
          f"   (in gaps under 1 MB: {r['gaps_under_1mb']:.1%})")
    for s in sorted(r["structures"], key=lambda s: (s["tier"] != "read", -s["bytes"])):
        print(f"    {s['tier']:8} {s['label']:24} {s['share']:6.2%} {s['bytes'] / 1e6:8.1f} MB")
    print("  largest unaccounted gaps:")
    for g in r["largest_gaps"]:
        res = ", ".join(f"{k} x{v}" for k, v in g["resources"].items()) or "no resource names"
        print(f"    {g['bytes'] / 1e6:7.1f} MB at {g['at']:6.1%}  zeros {g['zeros']:4.0%}"
              f"  floats {g['float_words']:4.0%}  small ints {g['small_int_words']:4.0%}"
              f"  small u16 {g['small_u16']:4.0%}  {res}")
    for note in r["notes"]:
        print("  note:", note)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("saves", nargs="+", metavar="SAVE")
    ap.add_argument("--gaps", type=int, default=10, help="how many of the largest gaps to describe")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--stream", action="store_true", help="the files are decompressed streams")
    args = ap.parse_args()
    out = {}
    for path in args.saves:
        raw = open(path, "rb").read()
        data = raw if args.stream else tf3save.decompress(raw)
        del raw
        r = estimate(data, args.gaps)
        name = os.path.basename(path)
        if args.json:
            out[name] = r
        else:
            print_report(name, r)
    if args.json:
        print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
