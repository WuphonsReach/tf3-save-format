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


# What followed the table's closing count: u32 1, 1, x, 1, 1, y, 1. x and y were 0 in most saves
# read (editor maps, played games) and other values in two catalog saves.
_TABLE_TRAILER = re.compile(rb"(?s)(.{4})\x01\0\0\0\x01\0\0\0.{4}\x01\0\0\0\x01\0\0\0.{4}\x01\0\0\0")


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


def names_table(data, ents=None):
    """(names, type id, set of free slots) of the entity names table, or None.

    In front of the table's `u32 n` is the component's type id and a `vec<u32>` of free slots
    (docs/entity-names.md). A free slot keeps the text its last owner had. Several vecs can end at
    `n` and hold only distinct slots below n, since the type id and the words before it can parse
    as one. With `ents` (from read_entities), the vec is taken whose type id is carried by exactly
    n minus its length entities; without, or if none fits, the longest.
    """
    found = tf3save.entity_names_at(data)
    if not found:
        return None
    nat, names = found[0] - 4, found[1]
    if nat < 0:
        return None
    n = struct.unpack_from("<I", data, nat)[0]
    if n > len(names):
        return None
    found = []
    for f in range(0, n + 1):
        q = nat - 4 - 4 * f
        if q < 4:
            break
        if struct.unpack_from("<I", data, q)[0] == f:
            v = struct.unpack_from("<%dI" % f, data, q + 4)
            if all(x < n for x in v) and len(set(v)) == f:
                found.append((struct.unpack_from("<I", data, q - 4)[0], set(v)))
    if not found:
        return None
    if ents is not None:
        carried = {}
        for e in ents:
            if e:
                for t in e:
                    carried[t] = carried.get(t, 0) + 1
        fits = [c for c in found if carried.get(c[0], 0) == n - len(c[1])]
        found = fits or found
    best = found[-1]
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
    table = find_entity_table(data)
    if table is None:
        return None
    ents = read_entities(data, *table)
    nt = names_table(data, ents)
    if nt is None:
        return None
    towns = _towns(data, ents, *nt)[0]
    for t in towns:
        t.pop("_mean", None)
    return towns


def _towns(data, ents, names, name_type, free):
    """(towns as town_places gives them, the town type id or None)."""
    blds = building_records(data)
    owners = {t for t, _ in blds if t < len(ents) and ents[t] and name_type in ents[t]}
    if not owners:
        return [], None
    # The town type: on every building owner, and on the fewest entities of all such types.
    shared = set.intersection(*(set(ents[t]) for t in owners)) - {name_type}
    if not shared:
        return [], None
    count = {t: 0 for t in shared}
    for e in ents:
        if e:
            for t in shared & e.keys():
                count[t] += 1
    town_type = min(sorted(shared), key=lambda t: count[t])   # the lowest id on a tie
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
            t.update(x=round(x, 1), y=round(y, 1), spread=round(max(math.hypot(p[0] - x, p[1] - y) for p in pts), 1),
                     _mean=(x, y))
        towns.append(t)
    return towns, town_type


def line_count(ents, name_type):
    """The number of lines: entities with exactly six types, among them 10 and the name type N, N + 1
    and N + 2 (docs/line-ids.md, Observed 601 to 605)."""
    want = {10, name_type, name_type + 1, name_type + 2}
    return sum(1 for e in ents if e and len(e) == 6 and want <= e.keys())


def town_table_header(data, town_type, live, before=None):
    """The town array's header (docs/town-records.md#table-header) as a dict, or None.

    The header is `u32 word, u32 type, vec<u32> free, u32 n`. It is found as `type, f, f slots, n`
    where n = len(live) + f and the free slots are exactly the rows no live town uses (`live`: the
    town entities' record slots). Of several matches, the last one before `before` (the first town
    record found by scan_records) is taken, else the first.
    """
    live = set(live)
    pat = struct.pack("<I", town_type)
    hits = []
    p = data.find(pat, 4)
    while p >= 0:
        f = struct.unpack_from("<I", data, p + 4)[0] if p + 8 <= len(data) else None
        if f is not None and f <= 4096 and p + 12 + 4 * f <= len(data):
            n = struct.unpack_from("<I", data, p + 8 + 4 * f)[0]
            if n == len(live) + f:
                slots = struct.unpack_from("<%dI" % f, data, p + 8)
                if len(set(slots)) == f and set(slots) == set(range(n)) - live:
                    hits.append((p, slots, n))
        p = data.find(pat, p + 1)
    if not hits:
        return None
    early = [h for h in hits if before is not None and h[0] < before]
    p, slots, n = early[-1] if early else hits[0]
    return {"first_word": struct.unpack_from("<I", data, p - 4)[0], "type": town_type,
            "free": sorted(slots), "rows": n}


def entity_summary(data, first_record=None):
    """What the mined summary takes from the entity table (tools/mine_summary.py), or None when no
    table is found: entity counts, the name type, the line count, the towns and the town array header.
    `first_record` is the offset of the first town record scan_records found, to pick the header."""
    table = find_entity_table(data)
    if table is None:
        return None
    ents = read_entities(data, *table)
    out = {"count": len(ents), "free": sum(1 for e in ents if e is None),
           "name_type": None, "lines": None, "towns": None, "town_type": None, "town_header": None}
    nt = names_table(data, ents)
    if nt is None:
        return out
    out["name_type"] = nt[1]
    out["lines"] = line_count(ents, nt[1])
    towns, town_type = _towns(data, ents, *nt)
    out["towns"], out["town_type"] = towns, town_type
    if town_type is not None and towns:
        out["town_header"] = town_table_header(data, town_type, [t["record"] & SLOT for t in towns], first_record)
    return out


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
