#!/usr/bin/env python3
"""Turn a heightmap grid into vector shapes: the water as filled rings and the land's height lines.

Library for `terrain_map.py --vector` (standard library only). Read only; it writes nothing.

`water_rings` and `height_lines` take the grid in picture order (the list of `array('H')` rows that
`terrain_map.to_picture` returns) and give polylines in metres from the picture's top-left corner,
point (i, j) of the grid being at (i * spacing, j * spacing), the same frame the road layers use.
Both use marching squares: a cell whose four corners fall on both sides of a level is cut by a line,
the line's end on a cell edge sits where the height reaches the level (linear between the two
corners), and the pieces of the cells are chained into whole lines through the edges they share.
A saddle (two opposite corners high) is settled by the cell's mean. A corner counts as high when its
height is at or above the level.

`water_rings` cuts the grid at the water level. The grid is padded by one ring of land first, so a
lake or sea that reaches the map's edge still closes (the padding's points are clamped onto the edge),
and the rings fill with the even-odd rule: an island is a ring inside a ring. A river is part of the
same shape, since the game carves rivers below the water level (docs/terrain.md).

`height_lines` cuts the land at every multiple of a step above the water level (levels at or below the
water level are the shore, which `water_rings` has). Its lines end at the picture's edge.

`simplify` thins a polyline with Douglas-Peucker to a tolerance in metres.
"""
import math

PAD = 1                # cells of land padded round the grid for the water fill


def _cut(rows, buckets, level_of, spacing, offset, kmin):
    """({level index: {edge key: [neighbour keys]}}, {edge key: (u, v)}) for a grid of height rows (lists of
    ints). `buckets[v]` is the level band of height v: the cut for level k lies between bands k - 1 and k, and
    `level_of(k)` is its height. Only levels from `kmin` up are cut. `offset` is the grid index of the
    picture's origin (1 when the grid is padded). An edge key is the grid index of its first corner times 2,
    plus 1 for a vertical edge, so two cells that share an edge agree on it."""
    h, w = len(rows), len(rows[0])
    band_rows = [[buckets[v] for v in r] for r in rows]
    adj, pos = {}, {}

    def cut(e, i, j, z, level):
        """Key of edge `e` (T, B, L or R) of cell (i, j), its point added to `pos` if new. `z` are the
        corner heights TL, TR, BR, BL."""
        if e == "T":
            key, a, b, u, v, du, dv = (j * w + i) * 2, z[0], z[1], i, j, 1, 0
        elif e == "B":
            key, a, b, u, v, du, dv = ((j + 1) * w + i) * 2, z[3], z[2], i, j + 1, 1, 0
        elif e == "L":
            key, a, b, u, v, du, dv = (j * w + i) * 2 + 1, z[0], z[3], i, j, 0, 1
        else:
            key, a, b, u, v, du, dv = (j * w + i + 1) * 2 + 1, z[1], z[2], i + 1, j, 0, 1
        if key not in pos:
            t = (level - a) / (b - a)
            pos[key] = ((u + du * t - offset) * spacing, (v + dv * t - offset) * spacing)
        return key

    for j in range(h - 1):
        ra, rb = rows[j], rows[j + 1]
        ba, bb = band_rows[j], band_rows[j + 1]
        for i in range(w - 1):
            q0, q1, q2, q3 = ba[i], ba[i + 1], bb[i + 1], bb[i]       # TL, TR, BR, BL
            if q0 == q1 == q2 == q3:
                continue
            z = (ra[i], ra[i + 1], rb[i + 1], rb[i])
            for k in range(max(min(q0, q1, q2, q3) + 1, kmin), max(q0, q1, q2, q3) + 1):
                level = level_of(k)
                case = (z[0] >= level) | ((z[1] >= level) << 1) | ((z[2] >= level) << 2) | ((z[3] >= level) << 3)
                if case in (0, 15):
                    continue
                pairs = _CASES[case]
                if case in (5, 10):
                    pairs = pairs[0 if sum(z) / 4 >= level else 1]
                lines = adj.setdefault(k, {})
                for e1, e2 in pairs:
                    a, b = cut(e1, i, j, z, level), cut(e2, i, j, z, level)
                    lines.setdefault(a, []).append(b)
                    lines.setdefault(b, []).append(a)
    return adj, pos


# segments of a cell by case (TL = 1, TR = 2, BR = 4, BL = 8): pairs of the edges T, R, B, L that a line joins
_CASES = {
    1: (("L", "T"),), 2: (("T", "R"),), 3: (("L", "R"),), 4: (("R", "B"),),
    6: (("T", "B"),), 7: (("L", "B"),), 8: (("B", "L"),), 9: (("T", "B"),),
    11: (("R", "B"),), 12: (("L", "R"),), 13: (("T", "R"),), 14: (("L", "T"),),
    5: ((("L", "B"), ("T", "R")), (("L", "T"), ("R", "B"))),      # centre high, centre low
    10: ((("L", "T"), ("R", "B")), (("T", "R"), ("L", "B"))),
}


def _chain(lines, pos):
    """The cells' pieces as polylines [(points, closed)], open ones first (they start at an edge of the grid)."""
    seen = set()
    out = []

    def walk(start, first):
        pts = [pos[start]]
        seen.add(start)
        prev, cur = None, start
        nxt = first
        while True:
            if nxt in seen:
                return pts, nxt == start and len(pts) > 2
            seen.add(nxt)
            pts.append(pos[nxt])
            prev, cur = cur, nxt
            options = [n for n in lines[cur] if n != prev]
            if not options:
                return pts, False
            nxt = options[0]
            if nxt == start and len(pts) > 2:
                return pts, True

    for key, nb in lines.items():          # open lines: a point with one neighbour
        if len(nb) == 1 and key not in seen:
            pts, _ = walk(key, nb[0])
            out.append((pts, False))
    for key, nb in lines.items():          # what is left is rings
        if key not in seen:
            pts, closed = walk(key, nb[0])
            out.append((pts, closed))
    return out


def water_rings(rows, spacing, water_v, min_perimeter=0.0):
    """Closed rings round the water (everything below `water_v`, in height units) for even-odd filling,
    as lists of (u, v) in metres. Rings shorter than `min_perimeter` metres are left out."""
    pad = int(math.ceil(water_v))
    padded = [[pad] * (len(rows[0]) + 2)] + [[pad] + list(r) + [pad] for r in rows] + [[pad] * (len(rows[0]) + 2)]
    table = [0 if v < water_v else 1 for v in range(65536)]
    adj, pos = _cut(padded, table, lambda k: water_v, spacing, PAD, 1)
    right, bottom = len(rows[0]) * spacing, len(rows) * spacing      # the padding's own column and row
    rings = []
    for pts, _closed in _chain(adj.get(1, {}), pos):
        pts = [(min(max(u, 0.0), right), min(max(v, 0.0), bottom)) for u, v in pts]
        if _length(pts) >= min_perimeter:
            rings.append(pts)
    return rings


def height_lines(rows, spacing, water_v, step_v, min_length=0.0):
    """{k: [polylines]} for the land lines at water level + k * `step_v` (k from 1), each a list of (u, v)
    in metres with a flag for a closed ring: [(points, closed)]. Lines shorter than `min_length` are left out."""
    table = [max(0, int(math.floor((v - water_v) / step_v))) for v in range(65536)]
    adj, pos = _cut([list(r) for r in rows], table, lambda k: water_v + k * step_v, spacing, 0, 1)
    out = {}
    for k, lines in sorted(adj.items()):
        kept = [(pts, closed) for pts, closed in _chain(lines, pos) if _length(pts) >= min_length]
        if kept:
            out[k] = kept
    return out


def _length(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def simplify(pts, tol, closed=False):
    """Douglas-Peucker: `pts` thinned so that no dropped point lies further than `tol` metres from the
    line that replaces it. A closed ring (first point = last point is not required) keeps its first point."""
    if len(pts) < 3 or tol <= 0:
        return list(pts)
    work = list(pts) + ([pts[0]] if closed else [])
    keep = [False] * len(work)
    keep[0] = keep[-1] = True
    stack = [(0, len(work) - 1)]
    while stack:
        lo, hi = stack.pop()
        (x0, y0), (x1, y1) = work[lo], work[hi]
        dx, dy = x1 - x0, y1 - y0
        norm = math.hypot(dx, dy)
        far, far_d = -1, tol
        for i in range(lo + 1, hi):
            x, y = work[i]
            d = abs(dy * (x - x0) - dx * (y - y0)) / norm if norm else math.hypot(x - x0, y - y0)
            if d > far_d:
                far, far_d = i, d
        if far >= 0:
            keep[far] = True
            stack += [(lo, far), (far, hi)]
    out = [p for p, k in zip(work, keep) if k]
    return out[:-1] if closed else out


def path_data(polylines, closed=False):
    """SVG path data for polylines of (u, v): one `M ... L ...` subpath each (`Z` closes it). Coordinates
    are rounded to a tenth of a metre, and a point that rounds onto the one before is dropped."""
    parts = []
    for pts in polylines:
        last, seg = None, []
        for u, v in pts:
            p = (round(u, 1), round(v, 1))
            if p != last:
                seg.append("%g %g" % p)
                last = p
        if len(seg) >= 2:
            parts.append("M" + "L".join(seg) + ("Z" if closed else ""))
    return "".join(parts)
