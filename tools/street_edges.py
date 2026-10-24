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
# more vec3 (the tangents), the object and lane lists, and four strings: a mod name, the street type,
# a mod name and the base type (docs/road-network.md).
# A lookahead, so a match does not use up the bytes of the next record's own `.street`.
_START = re.compile(rb"\.street(?=(....)(....)(.{12})(.{12})(.{12})(.{12}))", re.S)
_SUFFIX = b".street_template"
CLUSTER_GAP = 1 << 20         # records less than this far apart belong to one table
TEMPLATE_WINDOW = 800         # the type string ends within this many bytes of the record's start (441 the most seen)
TRAIN_MODES = (1 << 7) | (1 << 8)  # TRAIN and ELECTRIC_TRAIN, by their place in the game's TransportMode list
MAX_ID = 1 << 24
MAX_X, MAX_Y = 40000.0, 60000.0


def _vec3(raw):
    return struct.unpack("<3f", raw)


def _u32(data, p):
    return struct.unpack_from("<I", data, p)[0]


MAX_LANE_WIDTH = 500.0       # metres: a sum of lane widths above this is not a width


def _lanes(data, start, tpl_at):
    """(the transport-mode bits of all the record's lanes together, the lanes' widths added up in metres or
    None when that is no sensible width), or None when the bytes from the tangents up
    to the street type's `str` at `tpl_at` do not read as: u32, u32, vec<(u32 id, u32 value)> (the objects on
    the edge), vec<(u32, u8)>, vec<lane>, 9 bytes, str (a mod name, empty for the game's own type). A lane
    is 21 bytes: f32 speed, f32 width, f32 height, u8, u32 modes, f32 offset."""
    p = start + 64
    n = _u32(data, p)
    if n > 64:
        return None
    p += 4 + 8 * n
    m = _u32(data, p)
    if m > 64:
        return None
    p += 4 + 5 * m
    lanes = _u32(data, p)
    if not 1 <= lanes <= 32:
        return None
    p += 4
    modes, width = 0, 0.0
    for k in range(lanes):
        modes |= _u32(data, p + 21 * k + 13)
        width += struct.unpack_from("<f", data, p + 21 * k + 4)[0]
    p += 21 * lanes
    if p + 13 + _u32(data, p + 9) != tpl_at:
        return None
    return modes, (width if 0 < width < MAX_LANE_WIDTH else None)


def _record_type(data, start):
    """(type, family, template, width) of the record whose first node id is at `start`, as `read_edges` describes
    them, or four Nones. The street type is the record's first `.street_template` string after the tangents,
    and the next two strings (a mod name and the base type) must follow it; no later string is tried, as that
    is the next record's."""
    j = data.find(_SUFFIX, start + 56, start + TEMPLATE_WINDOW)
    if j < 0:
        return None, None, None, None
    end = j + len(_SUFFIX)
    q = j
    while q > start + 60 and data[q - 1] >= 0x20:  # back over the text to the length word, whose top byte is 0
        q -= 1
    q -= 4
    if _u32(data, q) != end - q - 4:
        return None, None, None, None
    mod = _u32(data, end)
    if mod > 256:
        return None, None, None, None
    base = _u32(data, end + 4 + mod)
    if base > 512 or not data[end + 8 + mod:end + 8 + mod + base].endswith(b".street"):
        return None, None, None, None
    path = data[q + 4:j].decode("utf-8", "replace")
    template = path[len("infrastructure/"):] if path.startswith("infrastructure/") else path
    lanes = _lanes(data, start, q)
    modes, width = lanes if lanes else (None, None)
    if modes is not None:
        family = "track" if modes & TRAIN_MODES else "street"
    else:
        family = template.split("/")[0] if path.startswith(("infrastructure/street/", "infrastructure/track/")) else None
    return template.split("/")[-1], family, template, width


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
    string was not found), `family` (`track` when a lane carries trains, else `street`; from the
    folder when the lanes do not read, None if that is not `infrastructure/street` or `track`),
    `template` (the type's resource path without `.street_template`, and without `infrastructure/`
    for the types under it: `street/town/town_old_small`, but `industries/shared/industry_track/industry`;
    None with the type), `width` (the sum of the record's lane widths in metres, sidewalks and shoulders included, so the strip
    the road is built on; None when the lanes do not read) and `offset` (of the record's first node id in the stream)."""
    out = []
    for m in _START.finditer(data):
        a, b = struct.unpack("<II", m.group(1) + m.group(2))
        p0, p1, t0, t1 = (_vec3(m.group(i)) for i in range(3, 7))
        if not _plausible(a, b, p0, p1, t0, t1):
            continue
        start = m.start() + len(b".street")
        t, family, template, width = _record_type(data, start)
        out.append({"a": a, "b": b, "p0": p0, "p1": p1, "t0": t0, "t1": t1, "type": t, "family": family,
                    "template": template, "width": width, "length": math.hypot(p1[0] - p0[0], p1[1] - p0[1]), "offset": start})
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
    t, family, template, width = _record_type(data, start)
    return {"a": a, "b": b, "p0": p0, "p1": p1, "t0": t0, "t1": t1, "type": t, "family": family,
            "template": template, "width": width, "length": math.hypot(p1[0] - p0[0], p1[1] - p0[1]), "offset": start}


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
    """True when an inner control point of the centre line lies more than `tol` metres from the chord.
    The curve stays inside its control points' hull, so no bend that leaves the chord by more is missed.
    The curve's middle alone would miss an S-bend, whose middle can lie on the chord (docs/edge-curves.md)."""
    c = edge_bezier(e)
    return max(_along(c[1], c[0], c[3])[0], _along(c[2], c[0], c[3])[0]) > tol


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


TAIL = 4_000_000              # the free-id list sits within the last few megabytes (its end at most 2.3 MB from the stream's end)
FREE_MIN_RUN = 1000           # shortest ascending run taken for the list's sorted part
FREE_MAX_ID = MAX_ID          # an id is below this (node ids pass 1,000,000 in long games)


def read_free_ids(data):
    """The free-id list (docs/town-leftovers.md) as a set, or None if it is not found. It is a
    vec<u32> near the end of the stream, followed by u32 2, a u32 and a short `str` of digits. Its
    longest ascending stretch of small values (in the stream's last TAIL bytes, at any 4-byte alignment)
    lies inside the list, mostly at its end. The list ends at the first such trailer from the run's end
    on, and the count word is the word before the run that reaches that trailer exactly; a candidate
    with an id twice is not taken. A node or edge id in it belongs to an entity the game no longer has."""
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
        for j in range(s + best[0], len(words) - 3):   # the trailer: 2, a u32, str of digits
            if words[j] != 2 or not 1 <= words[j + 2] <= 32:
                continue
            p = al + 4 * (j + 3)
            if not tail[p:p + words[j + 2]].isdigit():
                continue
            for i in range(s - 1, -1, -1):              # the count word: i + 1 + count is the trailer
                if i + 1 + words[i] == j:
                    ids = set(words[i + 1:j])
                    if len(ids) == words[i] and max(ids) < FREE_MAX_ID:  # a free-id list has no id twice
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
