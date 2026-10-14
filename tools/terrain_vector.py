#!/usr/bin/env python3
"""Turn a heightmap grid into vector shapes: the water and the land's height bands as closed rings, and the height lines.

Library for `terrain_map.py --vector` (standard library only). Read only; it writes nothing.

`level_rings` takes the grid in picture order (the list of `array('H')` rows that `terrain_map.to_picture`
returns) and gives, for the water level and for every multiple of a step above it, the closed rings round
the ground below that level, in metres from the picture's top-left corner, point (i, j) of the grid being at
(i * spacing, j * spacing), the same frame the road layers use. Level 0 is the water level, so its rings
are the lakes, the sea and the rivers (the game carves rivers below the water level, docs/terrain.md);
fill them with the even-odd rule, an island being a ring inside a ring. The ground at or above level k is the
whole picture minus level k's rings, which is how a band is filled. `split_at_border` turns a ring back into
the open height lines by dropping the pieces that run along the picture's edge, which the padding put there.

It is marching squares: a cell whose four corners fall on both sides of a level is cut by a line, the line's
end on a cell edge sits where the height reaches the level (linear between the two corners), and the pieces
of the cells are chained into whole lines through the edges they share. A saddle (two opposite corners high)
is settled by the cell's mean. A corner counts as high when its height is at or above the level. The grid is
padded by one ring of its own highest value, so every ring closes at the edge (an edge from a real point to a
padding point is cut at the padding point, which is then clamped onto the picture's edge).

`simplify` thins a polyline with Douglas-Peucker to a tolerance in metres.
"""
import math

PAD = 1                # cells of land padded round the grid for the water fill


def _cut(rows, buckets, level_of, spacing, offset, kmin, padded=False):
    """({level index: {edge key: [neighbour keys]}}, {edge key: (u, v)}) for a grid of height rows (lists of
    ints). `buckets[v]` is the level band of height v: the cut for level k lies between bands k - 1 and k, and
    `level_of(k)` is its height. Only levels from `kmin` up are cut. `offset` is the grid index of the
    picture's origin (1 when the grid is padded; `padded` says the outer ring of points is padding, and a cut
    on an edge that ends in one lies at that padding point). An edge key is the grid index of its first corner times 2,
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
            if padded:                                       # an edge from a real point to a padding point
                pad_a = u in (0, w - 1) or v in (0, h - 1)
                pad_b = u + du in (0, w - 1) or v + dv in (0, h - 1)
                if pad_a != pad_b:
                    t = 0.0 if pad_a else 1.0
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


def level_rings(rows, spacing, water_v, step_v, min_perimeter=0.0):
    """{k: [rings]} for the water level (k = 0) and the land levels water + k * `step_v` (k from 1, up to the
    highest point): each ring a list of (u, v) in metres, closed by the picture's edge where the ground
    below the level reaches it. Rings shorter than `min_perimeter` metres are left out."""
    w, h = len(rows[0]), len(rows)
    top = max(max(r) for r in rows)
    top = max(top, int(math.ceil(water_v)))                         # a picture wholly under water still gets a land border, so its water closes
    padded = [[top] * (w + 2)] + [[top] + list(r) + [top] for r in rows] + [[top] * (w + 2)]
    # band 0 is the ground below the water, band m (m >= 1) starts at water + (m - 1) * step, and the cut that
    # `_cut` calls m is the one between bands m - 1 and m, so ring set k of the result is cut m = k + 1
    table = [0 if v < water_v else 1 + int(math.floor((v - water_v) / step_v)) for v in range(65536)]
    adj, pos = _cut(padded, table, lambda m: water_v + (m - 1) * step_v, spacing, PAD, 1, padded=True)
    right, bottom = w * spacing, h * spacing                        # the padding's own column and row
    out = {}
    for m, lines in sorted(adj.items()):
        rings = []
        for pts, _closed in _chain(lines, pos):
            pts = [(min(max(u, 0.0), right), min(max(v, 0.0), bottom)) for u, v in pts]
            if _length(pts) >= min_perimeter:
                rings.append(pts)
        if rings:
            out[m - 1] = rings
    return out, (right, bottom)


def split_at_border(ring, extent):
    """A ring (list of points, closed implicitly) as the open polylines left when the pieces that run along the
    picture's edge (`extent` = (right, bottom)) are dropped: [(points, closed)]. A ring that never touches the
    edge is returned whole and closed."""
    right, bottom = extent
    n = len(ring)

    def on_edge(a, b):
        return (a[0] == b[0] and a[0] in (0.0, right)) or (a[1] == b[1] and a[1] in (0.0, bottom))

    border = [on_edge(ring[i], ring[(i + 1) % n]) for i in range(n)]
    if not any(border):
        return [(ring, True)]
    first = border.index(True)
    out, run = [], []
    for t in range(1, n + 1):
        i = (first + t) % n
        if border[i]:
            if len(run) > 1:
                out.append((run, False))
            run = []
        else:
            if not run:
                run = [ring[i]]
            run.append(ring[(i + 1) % n])
    if len(run) > 1:
        out.append((run, False))
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
