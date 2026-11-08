#!/usr/bin/env python3
"""Name each town of a TF3 save and place it on the map, from the entity table (docs/town-places.md).

Usage: town_places.py SAVE.sav [--export towns-export.lua] [--json] [--stream]

Prints one line per live town: its entity id, its name slot and name, its town record (the
row of the town array), the number of its buildings and of their parcels, and a point: the mean
of the centres of the parcels its buildings stand on (x, y in metres, the game frame), with the
largest distance from that point to one of the parcels. `--export` reads the map editor's
Towns export of the same save (`towns-export.lua`) and adds the distance from each point to the
export's position for that name.

The chain (docs/town-places.md): the entity table gives each entity a list of (component type,
slot) pairs. A town's entity has a town slot and a name slot; the names table's free list tells
the live names from stale ones. Each building record names its town by entity id and lists its
parcel entities, and a parcel's slot is its row in the parcel table, which holds the parcel's
faces in map metres. No industry, label or street cluster is used.

A town with no building gets no point. The point is not the game's own town position (the
midpoint of the town's first street in the editor's export), which no record found here marks.
Only reads: no save is written. Standard library only.
"""
import argparse
import json
import math
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tf3save  # noqa: E402
from parcels import read_parcels  # noqa: E402

SLOT = 0x3fffffff          # the top bits of a slot are a flag some component types always set
FREE = 0xffffffff          # a free entity is one pair (FREE, FREE)
MAX_PAIRS = 300
MAX_TYPE = 4096


def _entity_end(data, q, n_max=None):
    """End offset of the entity at q, or None when it does not parse as one."""
    if q + 4 > len(data):
        return None
    k = struct.unpack_from("<I", data, q)[0]
    if k == 0 or k > MAX_PAIRS or q + 4 + 8 * k > len(data):
        return None
    types = struct.unpack_from("<%dI" % (2 * k), data, q + 4)[::2]
    if any(t >= MAX_TYPE and t != FREE for t in types) or len(set(types)) != k:
        return None
    return q + 4 + 8 * k


# What followed the table's closing count in every save read (editor maps and a played game).
_TABLE_TRAILER = re.compile(rb"(?s)(.{4})\x01\0\0\0\x01\0\0\0\0\0\0\0\x01\0\0\0\x01\0\0\0\0\0\0\0\x01\0\0\0")


def _parses_to(data, q, n, end):
    for _ in range(n):
        q = _entity_end(data, q)
        if q is None or q > end:
            return False
    return q == end


def find_entity_table(data, tail=0.12):
    """(offset of the first entity, count) of the entity table, or None.

    The table is `u32 n`, n entities, then `u32 n` again, followed by `1, 1, 0, 1, 1, 0, 1`; it sat
    97 to 98 % into the stream. The scan takes each such trailer in the last `tail` of the stream,
    from the end backwards, and looks for an earlier `u32 n` whose n entities end exactly at it.
    """
    lo = int(len(data) * (1 - tail))
    hits = list(_TABLE_TRAILER.finditer(data, lo))
    for m in reversed(hits):
        n = struct.unpack("<I", m.group(1))[0]
        if not 1000 <= n <= 20_000_000:
            continue
        end = m.start()
        pat = m.group(1)
        p = data.rfind(pat, max(0, end - (4 + 8 * MAX_PAIRS) * n), end)
        while p >= 0:
            if _parses_to(data, p + 4, n, end):
                return p + 4, n
            p = data.rfind(pat, max(0, end - (4 + 8 * MAX_PAIRS) * n), p)
    return None


def read_entities(data, start, n):
    """The n entities from `start`: a list of {type: slot} dicts, None for a free entity."""
    out, q = [], start
    for _ in range(n):
        k = struct.unpack_from("<I", data, q)[0]
        v = struct.unpack_from("<%dI" % (2 * k), data, q + 4)
        q += 4 + 8 * k
        pairs = dict(zip(v[::2], v[1::2]))
        out.append(None if FREE in pairs else pairs)
    return out


def names_table(data):
    """(names, type id, set of free slots) of the entity names table, or None.

    In front of the table's `u32 n` is the component's type id and a `vec<u32>` of free slots
    (docs/entity-names.md). A free slot keeps the text its last owner had. The longest vec that
    ends at `n` and holds only distinct slots below n is taken.
    """
    names = tf3save.entity_names(data)
    if not names:
        return None
    first = struct.pack("<I", len(names[0].encode())) + names[0].encode()
    nat = data.find(first) - 4
    n = struct.unpack_from("<I", data, nat)[0]
    best = None
    for f in range(0, n + 1):
        q = nat - 4 - 4 * f
        if q < 4:
            break
        if struct.unpack_from("<I", data, q)[0] == f:
            v = struct.unpack_from("<%dI" % f, data, q + 4)
            if all(x < n for x in v) and len(set(v)) == f:
                best = (struct.unpack_from("<I", data, q - 4)[0], set(v))
    if best is None:
        return None
    return names[:n], best[0], best[1]


# A building record (docs/town-buildings.md): u32 a, u32 b (a or all ones), u32 level 1..4, u32 d,
# u8 flag, vec<u32> parcels (1..4 here), u32 depth 1..4, f32 height, u32 town, u64 timeBuilt.
_BUILDING = re.compile(rb"(?s)(.{4})(.{4})[\x01-\x04]\0\0\0.{4}[\0\x01][\x01-\x04]\0\0\0")


def building_records(data):
    """[(town entity id, [parcel entity ids])] for every building record found by pattern."""
    out = []
    for m in _BUILDING.finditer(data):
        a, b = struct.unpack("<II", m.group(1) + m.group(2))
        if b not in (a, 0xffffffff) or a == 0:
            continue
        p = m.start()
        n = data[p + 17]
        q = p + 21 + 4 * n
        if q + 20 > len(data):
            continue
        parcels = struct.unpack_from("<%dI" % n, data, p + 21)
        depth, height, town = struct.unpack_from("<IfI", data, q)
        if 1 <= depth <= 4 and 2 < height < 120 and town and all(parcels):
            out.append((town, parcels))
    return out


def read_export(path):
    """{name: (x, y)} from the map editor's Towns export (`towns-export.lua`)."""
    text = open(path, encoding="utf-8").read()
    towns = text.split("towns", 1)[-1]
    pat = re.compile(r'name\s*=\s*"((?:[^"\\]|\\.)*)"\s*,\s*position\s*=\s*\{\s*x\s*=\s*([-0-9.e]+)\s*,\s*y\s*=\s*([-0-9.e]+)')
    return {m.group(1): (float(m.group(2)), float(m.group(3))) for m in pat.finditer(towns)}


def town_places(data):
    """One dict per live town: id, name_slot, name, record, buildings, parcels, x, y, spread."""
    nt = names_table(data)
    table = find_entity_table(data)
    if nt is None or table is None:
        return None
    names, name_type, free = nt
    ents = read_entities(data, *table)
    blds = building_records(data)
    owners = {t for t, _ in blds if t < len(ents) and ents[t] and name_type in ents[t]}
    if not owners:
        return []
    # The town type: on every building owner, and on the fewest entities of all such types.
    shared = set.intersection(*(set(ents[t]) for t in owners)) - {name_type}
    count = {t: 0 for t in shared}
    for e in ents:
        if e:
            for t in shared & e.keys():
                count[t] += 1
    town_type = min(shared, key=lambda t: count[t])
    # The parcel type: the one type of the entities a building lists as its parcels.
    kinds = {}
    for _, ps in blds[:500]:
        for p in ps:
            if p < len(ents) and ents[p] and len(ents[p]) == 1:
                k = next(iter(ents[p]))
                kinds[k] = kinds.get(k, 0) + 1
    parcel_type = max(kinds, key=kinds.get) if kinds else None
    _, parcels = read_parcels(data)
    towns = []
    for tid, e in enumerate(ents):
        if not e or town_type not in e:
            continue
        slot = e.get(name_type)
        name = names[slot] if slot is not None and slot < len(names) and slot not in free else None
        pts, nb = [], 0
        for town, ps in blds:
            if town != tid:
                continue
            nb += 1
            for p in ps:
                pe = ents[p] if p < len(ents) else None
                if pe and parcel_type in pe and (pe[parcel_type] & SLOT) < len(parcels) \
                        and parcels[pe[parcel_type] & SLOT]["faces"]:
                    face = parcels[pe[parcel_type] & SLOT]["faces"][0][0]
                    pts.append((sum(c[0] for c in face) / len(face), sum(c[1] for c in face) / len(face)))
        t = {"id": tid, "name_slot": slot, "name": name, "record": e[town_type], "buildings": nb, "parcels": len(pts)}
        if pts:
            x = sum(p[0] for p in pts) / len(pts)
            y = sum(p[1] for p in pts) / len(pts)
            t.update(x=round(x, 1), y=round(y, 1), spread=round(max(math.hypot(p[0] - x, p[1] - y) for p in pts), 1))
        towns.append(t)
    return towns


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("save")
    ap.add_argument("--export", help="the map editor's towns-export.lua of the same save")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--stream", action="store_true", help="the file is an already decompressed stream")
    args = ap.parse_args()
    raw = open(args.save, "rb").read()
    data = raw if args.stream else tf3save.decompress(raw)
    towns = town_places(data)
    if towns is None:
        sys.exit("no names table or entity table found")
    exp = read_export(args.export) if args.export else {}
    for t in towns:
        if t["name"] in exp and "x" in t:
            ex, ey = exp[t["name"]]
            t["export_dist"] = round(math.hypot(t["x"] - ex, t["y"] - ey), 1)
    if args.json:
        print(json.dumps(towns, indent=1, ensure_ascii=False))
        return
    for t in towns:
        place = "%9.1f %9.1f  spread %5.0f m" % (t["x"], t["y"], t["spread"]) if "x" in t else "no buildings"
        extra = "  export %5.0f m" % t["export_dist"] if "export_dist" in t else ("  not in export" if exp else "")
        print("%8d  slot %6s  record %3d  %-24s %4d buildings %5d parcels  %s%s"
              % (t["id"], t["name_slot"], t["record"], t["name"] if t["name"] is not None else "(stale or none)",
                 t["buildings"], t["parcels"], place, extra))
    if exp:
        named = {t["name"] for t in towns}
        missing = sorted(set(exp) - named)
        print("export towns not found: %d %s" % (len(missing), missing))


if __name__ == "__main__":
    main()
