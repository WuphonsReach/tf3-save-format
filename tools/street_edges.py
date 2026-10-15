#!/usr/bin/env python3
"""List the street edges of a TF3 save, and compare two saves.

Usage:
  street_edges.py SAVE.sav [--near X,Y,RADIUS] [--type REGEX] [--nodes] [--ids] [--json]
  street_edges.py --diff OLD.sav NEW.sav [--near X,Y,RADIUS] [--type REGEX] [--ids] [--json]

SAVE may also be a stream already decompressed to a file (add --stream). Output goes to the
terminal. Only reads: no save is written.

An edge is one record of the street-edge table (docs/road-network.md): the entity ids of its two
end nodes, the two end positions (x, y, z in metres) and the street type. Default output is one
line per edge: both node ids (hex), the street type without its folder and `.street_template`,
the two positions, the length in metres, and the record's offset in the stream. `--near X,Y,R`
keeps the edges with an end within R metres of (X, Y). `--type` keeps the street types matching a
regex. `--nodes` prints one line per node instead: id, position, the number of edges and their
other ends.

`--ids` adds each edge's own entity id (`e=` in the text output) by matching the edge to an entry
of the road-surface strip table, which is keyed by that id: the entry's strips have to run along
the edge's line. It scans the whole stream for that table. Many edges have no such entry (162 of
359 matched in the map the notes were written from), and they show `e=?`; see docs/road-network.md.

`--diff` pairs the edges of two saves by their two node ids and prints those only in the old save
(`-`), only in the new one (`+`) and those whose end positions or street type changed (`~`).
A node's id can be reused for a new node after the old one is deleted (docs/road-network.md), so
an edge that keeps its ids but moved is shown as `~`, not as a removal and an addition.

A record can outlast its road by one save: a deleted road was still listed in the next save
(docs/road-network.md). Node ids, positions and street types are facts about the map, not about
the player, so the output needs no masking.
"""
import argparse
from array import array
import json
import math
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tf3save import decompress  # noqa: E402

# An edge record starts right after the `.street` string that ends the previous record (or the
# table's first string): u32 node a, u32 node b, then two vec3 f32 (the end positions), then two
# more vec3 (the tangents), lane data, and the record's own two strings (docs/road-network.md).
# A lookahead, so a match does not use up the bytes of the next record's own `.street`.
_START = re.compile(rb"\.street(?=(....)(....)(.{12})(.{12})(.{12})(.{12}))", re.S)
_TEMPLATE = re.compile(rb"([\x20-\x80])\x00\x00\x00(infrastructure/(?:street|track)/[A-Za-z0-9_/]+)\.street_template")
CLUSTER_GAP = 1 << 20         # records less than this far apart belong to one table
TEMPLATE_WINDOW = 800         # the type string follows the lane data within this many bytes
MAX_ID = 1 << 24
MAX_X, MAX_Y = 40000.0, 60000.0


def _vec3(raw):
    return struct.unpack("<3f", raw)


def _plausible(a, b, p0, p1, t0, t1):
    if not (0 < a < MAX_ID and 0 < b < MAX_ID) or a == b:
        return False
    for v in (p0, p1):
        if not all(math.isfinite(c) for c in v):
            return False
        if abs(v[0]) > MAX_X or abs(v[1]) > MAX_Y or not -1000.0 < v[2] < 8000.0:
            return False
    length = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    if not 1.0 < length < 5000.0:
        return False
    # the first tangent points from p0 towards p1 (the tangents of a straight edge are its
    # difference vector), so its horizontal part is as long as the edge, within a few percent
    # for a curve
    if not all(math.isfinite(c) for c in t0 + t1):
        return False
    return math.hypot(t0[0], t0[1]) < 5.0 * length


def read_edges(data):
    """The street-edge table as a list of dicts: `a`, `b` (node entity ids), `p0`, `p1` (x, y, z), `t0`, `t1` (the end tangents, x, y, z),
    `length` (horizontal, metres), `type` (street or track type without folder, or None if the type
    string was not found), `family` (`street` or `track`, from the folder; None with the type),
    `template` (the path under `infrastructure/` without the suffix, such as
    `street/town/town_old_small`; None with the type) and `offset` (of the record's first node id
    in the stream)."""
    out = []
    for m in _START.finditer(data):
        a, b = struct.unpack("<II", m.group(1) + m.group(2))
        p0, p1, t0, t1 = (_vec3(m.group(i)) for i in range(3, 7))
        if not _plausible(a, b, p0, p1, t0, t1):
            continue
        start = m.start() + len(b".street")
        window = data[start:start + TEMPLATE_WINDOW]
        t = family = template = None
        for tm in _TEMPLATE.finditer(window):
            if len(tm.group(2)) == tm.group(1)[0] - len(b".street_template"):
                parts = tm.group(2).decode().split("/")
                t, family, template = parts[-1], parts[1], "/".join(parts[1:])
                break
        out.append({"a": a, "b": b, "p0": p0, "p1": p1, "t0": t0, "t1": t1, "type": t, "family": family,
                    "template": template, "length": math.hypot(p1[0] - p0[0], p1[1] - p0[1]), "offset": start})
    out = _largest_cluster(out)
    first = _record_before(data, out[0]["offset"]) if out else None
    return [first] + out if first else out


def _parse_record(data, start):
    """The record whose first node id is at `start`, as `read_edges` returns it, or None when the bytes
    there do not read as one (same checks as `read_edges`, no `.street` needed before it)."""
    a, b = struct.unpack_from("<II", data, start)
    p0, p1, t0, t1 = (_vec3(data[start + 8 + 12 * i:start + 20 + 12 * i]) for i in range(4))
    if not _plausible(a, b, p0, p1, t0, t1):
        return None
    t = family = template = None
    for tm in _TEMPLATE.finditer(data[start:start + TEMPLATE_WINDOW]):
        if len(tm.group(2)) == tm.group(1)[0] - len(b".street_template"):
            parts = tm.group(2).decode().split("/")
            t, family, template = parts[-1], parts[1], "/".join(parts[1:])
            break
    return {"a": a, "b": b, "p0": p0, "p1": p1, "t0": t0, "t1": t1, "type": t, "family": family,
            "template": template, "length": math.hypot(p1[0] - p0[0], p1[1] - p0[1]), "offset": start}


def _record_before(data, offset):
    """The table's first record. Every other record starts right after the previous record's last
    `.street`, which is what `read_edges` matches on; the first one follows other bytes (a run of
    small counters in the 604 save checked), so it is found from the second: a record that reads as
    one, starts 250 to 400 bytes earlier and whose own last string ends exactly where the second
    begins. Bytes at the wrong alignment can also pass the plausibility checks, so the candidates are
    told apart by their tangents: the horizontal length of each is within 20 % of the edge's own
    length (true of every edge checked, curved ones included). None if no candidate, or if more
    than one remains."""
    if data[offset - len(b".street"):offset] != b".street":
        return None
    found = []
    for start in range(max(0, offset - 400), offset - 250):
        e = _parse_record(data, start)
        if e and e["type"] and all(abs(math.hypot(t[0], t[1]) - e["length"]) < 0.2 * e["length"] for t in (e["t0"], e["t1"])):
            found.append(e)
    return found[0] if len(found) == 1 else None


def edge_bezier(e):
    """The four control points ((x, y) each) of the edge's centre line as a cubic Bezier: the end
    positions and each end moved a third of its tangent inward. This is the cubic Hermite curve through
    the ends with the stored tangents (docs/road-speeds.md), and a straight line when both tangents
    are the difference vector. An edge without tangents (`t0` missing) is the straight line."""
    (x0, y0, _), (x1, y1, _) = e["p0"], e["p1"]
    if "t0" not in e:
        return (x0, y0), (x0, y0), (x1, y1), (x1, y1)
    t0, t1 = e["t0"], e["t1"]
    return ((x0, y0), (x0 + t0[0] / 3, y0 + t0[1] / 3), (x1 - t1[0] / 3, y1 - t1[1] / 3), (x1, y1))


def bezier_point(c, t):
    """The point of `edge_bezier` control points `c` at parameter `t` (0 to 1)."""
    u = 1 - t
    w = (u * u * u, 3 * u * u * t, 3 * u * t * t, t * t * t)
    return (sum(w[i] * c[i][0] for i in range(4)), sum(w[i] * c[i][1] for i in range(4)))


def edge_is_curved(e, tol=0.25):
    """True when the centre line leaves the chord by more than `tol` metres: the distance of the
    curve's middle from the chord's middle is (t0 - t1) / 8, and that bounds the bulge to within a
    small factor for the bends the game allows."""
    c = edge_bezier(e)
    mid = bezier_point(c, 0.5)
    return math.hypot(mid[0] - (c[0][0] + c[3][0]) / 2, mid[1] - (c[0][1] + c[3][1]) / 2) > tol


def _largest_cluster(edges):
    """The table is one run of records; a stray match far from it (another structure that happens to
    look like a record) is dropped by keeping only the biggest group of records whose neighbours lie
    less than CLUSTER_GAP apart."""
    best = cur = []
    for e in edges:
        if cur and e["offset"] - cur[-1]["offset"] >= CLUSTER_GAP:
            cur = []
        cur.append(e)
        if len(cur) > len(best):
            best = cur
    return best


_STRIP = re.compile(rb"\x41(....)([\x00\x01])....\x04\x00\x00\x00\x04\x00\x00\x00(.{8})", re.S)
STRIP_OFF_M = 6.0              # a strip run's ends lie this close to the edge's line
STRIP_COVER = 0.4              # and the run covers this share of the edge's length


def read_strips(data):
    """The road-surface strip table (docs/road-network.md) as {edge entity id: [(side, x, y)]},
    each id's strips in stream order. Scans the whole stream."""
    out = {}
    for m in _STRIP.finditer(data):
        eid = struct.unpack("<I", m.group(1))[0]
        if not 0 < eid < MAX_ID:
            continue
        x, y = struct.unpack("<ff", m.group(3))
        if abs(x) < MAX_X and abs(y) < MAX_Y:
            out.setdefault(eid, []).append((m.group(2)[0], x, y))
    return out


TAIL = 4_000_000              # the free-id list sits within the last few megabytes (1 to 1.5 MB from the end in a 900 MB stream)
FREE_MIN_RUN = 1000           # shortest ascending run taken for the list's sorted part
FREE_MAX_ID = 1_000_000       # an id is below this; the words after the list are not


def read_free_ids(data):
    """The free-id list (docs/town-leftovers.md) as a set, or None if it is not found. It is a
    vec<u32> near the end of the stream: a head of small ascending groups and then one long
    ascending run. The run is the longest ascending stretch of small values in the stream's last TAIL bytes
    (at any 4-byte alignment); the count word is the one before the list that reaches the run's end, and a candidate with an id twice is not taken.
    A node or edge id in it belongs to an entity the game no longer has."""
    tail = data[-TAIL:]
    for al in range(4):
        words = array("I")
        words.frombytes(tail[al:len(tail) - (len(tail) - al) % 4])
        if sys.byteorder == "big":
            words.byteswap()
        best = None                                   # (length, start) of the longest ascending run
        start = 0
        for i in range(1, len(words) + 1):
            if i == len(words) or words[i] <= words[i - 1] or words[i] >= FREE_MAX_ID:
                if i - start >= FREE_MIN_RUN and words[start] < FREE_MAX_ID and (best is None or i - start > best[0]):
                    best = (i - start, start)
                start = i
        if best is None:
            continue
        s = best[1]
        end = s
        while end < len(words) and words[end] < FREE_MAX_ID and (end == s or words[end] > words[end - 1]):
            end += 1
        for i in range(max(0, s - 100_000), s):       # the count word: i + 1 + count is the run's end
            if abs(i + 1 + words[i] - end) <= 3 and words[i] > best[0]:
                ids = set(words[i + 1:i + 1 + words[i]])
                if len(ids) == words[i]:                  # a free-id list has no id twice
                    return ids
    return None


def _along(p, a, b):
    """(distance of p from the segment a-b, position of p's foot along it as a share 0..1)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)
    t = min(1.0, max(0.0, t))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy)), t


def edge_ids(edges, strips):
    """Set `e` on each edge to the entity id of the strip-table entry that runs along it, or None.
    An entry's centre line (its two sides averaged at the first and last strip) has to lie within
    a few metres of the edge's line and cover a good part of its length. Dead-end edges and the
    stretch next to a junction can have no entry or a short one (docs/road-network.md)."""
    runs = {}
    for eid, rows in strips.items():
        sides = [[(x, y) for s, x, y in rows if s == side] for side in (0, 1)]
        if sides[0] and len(sides[0]) == len(sides[1]):
            runs[eid] = (((sides[0][0][0] + sides[1][0][0]) / 2, (sides[0][0][1] + sides[1][0][1]) / 2),
                         ((sides[0][-1][0] + sides[1][-1][0]) / 2, (sides[0][-1][1] + sides[1][-1][1]) / 2))
    for e in edges:
        best = None
        for eid, (f, l) in runs.items():
            (df, tf), (dl, tl) = _along(f, e["p0"], e["p1"]), _along(l, e["p0"], e["p1"])
            cover = abs(tl - tf)
            if df < STRIP_OFF_M and dl < STRIP_OFF_M and cover >= STRIP_COVER and (best is None or cover > best[0]):
                best = (cover, eid)
        e["e"] = best[1] if best else None


def nodes(edges):
    """{node id: {"pos": (x, y, z), "edges": [(other node id, edge index)]}} built from the
    edges' ends. A node's position is read from the ends that name it; edges disagreeing by more
    than a metre would show up in `check_nodes`."""
    out = {}
    for i, e in enumerate(edges):
        for me, other, pos in ((e["a"], e["b"], e["p0"]), (e["b"], e["a"], e["p1"])):
            n = out.setdefault(me, {"pos": pos, "edges": []})
            n["edges"].append((other, i))
    return out


def check_nodes(edges):
    """Node ids whose edges give positions more than a metre apart (should be empty)."""
    seen, bad = {}, []
    for e in edges:
        for nid, pos in ((e["a"], e["p0"]), (e["b"], e["p1"])):
            old = seen.setdefault(nid, pos)
            if math.hypot(old[0] - pos[0], old[1] - pos[1]) > 1.0 and nid not in bad:
                bad.append(nid)
    return bad


def near(edge, box):
    x, y, r = box
    return any(math.hypot(p[0] - x, p[1] - y) <= r for p in (edge["p0"], edge["p1"]))


def load_edges(path, args):
    data = load(path, args.stream)
    edges = read_edges(data)
    if args.ids:
        edge_ids(edges, read_strips(data))
    return select(edges, args)


def load(path, is_stream):
    with open(path, "rb") as f:
        raw = f.read()
    return raw if is_stream else decompress(raw)


def parse_near(text):
    try:
        x, y, r = (float(v) for v in text.split(","))
    except ValueError:
        sys.exit("--near wants X,Y,RADIUS in metres, for example --near -3400,12400,150")
    return x, y, r


def select(edges, args):
    if args.near:
        edges = [e for e in edges if near(e, args.near)]
    if args.type:
        want = re.compile(args.type)
        edges = [e for e in edges if e["type"] and want.search(e["type"])]
    return edges


def fmt_pos(p):
    return "(%.1f, %.1f, %.1f)" % p


def fmt_edge(e):
    eid = "" if "e" not in e else "e=%s  " % ("?" if e["e"] is None else "%x" % e["e"])
    return "%s%x > %x  %-28s %s > %s  %.1f m  @%#x" % (
        eid, e["a"], e["b"], e["type"] or "?", fmt_pos(e["p0"]), fmt_pos(e["p1"]), e["length"], e["offset"])


def print_nodes(edges):
    for nid, n in sorted(nodes(edges).items()):
        others = " ".join("%x" % o for o, _ in n["edges"])
        print("%x  %s  %d edge%s: %s" % (nid, fmt_pos(n["pos"]), len(n["edges"]),
                                         "" if len(n["edges"]) == 1 else "s", others))


def diff(old, new, as_json):
    key = lambda e: (e["a"], e["b"])
    o = {key(e): e for e in old}
    n = {key(e): e for e in new}
    gone = [o[k] for k in o if k not in n]
    added = [n[k] for k in n if k not in o]
    changed = []
    for k in o:
        if k in n:
            same_pos = all(abs(c1 - c2) < 0.01 for c1, c2 in zip(o[k]["p0"] + o[k]["p1"], n[k]["p0"] + n[k]["p1"]))
            if not same_pos or o[k]["type"] != n[k]["type"]:
                changed.append((o[k], n[k]))
    if as_json:
        json.dump({"removed": gone, "added": added, "changed": [{"old": x, "new": y} for x, y in changed]},
                  sys.stdout, indent=1)
        print()
        return
    for e in gone:
        print("-", fmt_edge(e))
    for e in added:
        print("+", fmt_edge(e))
    for x, y in changed:
        print("~", fmt_edge(x))
        print("  ", fmt_edge(y))
    print("%d removed, %d added, %d changed" % (len(gone), len(added), len(changed)))


def main():
    ap = argparse.ArgumentParser(description="List the street edges of a TF3 save, or compare two saves.")
    ap.add_argument("saves", nargs="+", metavar="SAVE", help="a save (with --diff: OLD then NEW)")
    ap.add_argument("--diff", action="store_true", help="compare two saves")
    ap.add_argument("--stream", action="store_true", help="the files are already decompressed streams")
    ap.add_argument("--near", type=parse_near, metavar="X,Y,RADIUS", help="only edges with an end this close, in metres")
    ap.add_argument("--type", help="regex the street type must match (search, not full match)")
    ap.add_argument("--nodes", action="store_true", help="one line per node instead of per edge")
    ap.add_argument("--ids", action="store_true", help="add each edge's entity id (scans the whole stream)")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args()

    if args.diff:
        if len(args.saves) != 2:
            ap.error("--diff takes two saves, OLD then NEW")
        diff(load_edges(args.saves[0], args), load_edges(args.saves[1], args), args.json)
        return
    if len(args.saves) != 1:
        ap.error("give one save, or --diff OLD NEW")
    edges = load_edges(args.saves[0], args)
    if not edges:
        sys.exit("no street edges found")
    if args.nodes:
        print_nodes(edges)
    elif args.json:
        json.dump(edges, sys.stdout, indent=1)
        print()
    else:
        for e in edges:
            print(fmt_edge(e))


if __name__ == "__main__":
    main()
