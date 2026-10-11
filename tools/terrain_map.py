#!/usr/bin/env python3
"""Draw a save's terrain as an SVG, with its roads and rails on top.

Usage: terrain_map.py OUT_DIR SAVE.sav [...] [--mpp M] [--crop X,Y,R] [--grid N] [--png]
       [--game DIR] [--no-network] [--stream]

Read only: no save is written. The picture goes to OUT_DIR/<save name>-terrain.svg and the script
prints its size, the metres per pixel and the edge counts. The SVG holds the terrain as an
embedded PNG and the roads and rails as vector paths on top, in three layers (`terrain`,
`roads`, `rails`; groups with Inkscape's layer attributes) with one path per street or track type
(class `road` or `rail` plus the type name, for styling; the colours and width are also set
on each path, since Krita ignores the style sheet). The root's size and `viewBox` are the terrain image's pixels (so an editor such as Krita opens
it at that size, taking 96 PPI); each layer scales by 1 / (metres per pixel), so inside a layer
the units are map metres with the image's top-left corner at 0, 0. The line width is in metres too (1.5 terrain pixels, at least
3 m), so the lines scale with the terrain in every viewer; a width that stays fixed on screen
(`vector-effect: non-scaling-stroke`) turned short edges into blobs in VS Code's preview.
The terrain colours are a plain
height ramp with hill shading (water below the save's `waterLevel` in blue); they are not the
game's own palette.

--mpp M      metres per pixel of the terrain image: 1 or 2, or a multiple of 4 (default 4, the
             heightmap's own spacing). Larger values keep every (M / 4)th grid point. 1 and 2
             interpolate the terrain between grid points (no new height detail) and need --crop.
             A picture over 64 million pixels (a 4 m map of 32 x 32 km, or the 20 x 41 km
             Giant map at 4 m, 52 million) is refused unless --mpp is raised or --force-size is
             given. A 52 million pixel map took 42 s and 1.3 GB, and its SVG was 81 MB.
--crop X,Y,R draw only the square of half-width R metres around map point (X, Y), for a close
             look at a station or a junction.
--png        write one flat PNG instead of the SVG, with the lines drawn into the pixels about 4 m
             wide (at least one pixel).
--grid N     (SVG only) add a `grid` layer: a line at every multiple of N metres of map x and y,
             labelled `x -3000` along the top and `y 4500` along the left, so a place seen in the
             picture can be turned into the coordinates `--crop` wants. The map's centre is 0, 0.
             Lines at multiples of 1000 are darker and thicker, the others dotted and faint; the
             lines are one layer under the roads and the labels another over everything.
--game DIR   the game's install folder. A road is drawn with a stroke in proportion to its vehicle
             lane count over two (two lanes keep the base width, a track has one lane), read from
             the install's street and track templates when the script runs (nothing is copied
             into the tool or the picture). Without an install, or for a type the install lacks
             (a mod's), the width is the two-lane one. Default: the usual Steam folders.
--no-network leave the roads and rails out.
--stream     the files are decompressed streams, not saves.

Layout read (docs/terrain.md): the terrain record gives the map in 256 m tiles and the height
scale; the heightmap is one `vec<u16>` of 65 x 65 per tile, tile `ty * tiles_x + tx`. Grid point
(c, r) of the stitched grid is at x = -width / 2 + 4c, y = -height / 2 + 4r. North is up in the
image: row 0 is the largest y. That y points north is the usual top-down reading of a right-handed
map and was not checked against the game's compass.

The roads and rails are the street-edge table (docs/road-network.md, street_edges.py), straight
chords between the end positions: roads dark grey, rails red. Bridges and tunnels
are not told apart from the rest. A deleted road can stay in the table for one save.
"""
import argparse
import base64
import os
import re
import struct
import sys
import zipfile
from array import array

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from save_preview import png_bytes  # noqa: E402
from street_edges import read_edges  # noqa: E402
from tf3save import decompress  # noqa: E402

RESOLUTION = bytes.fromhex("0000804000008040cdcc4c3d")      # 4.0, 4.0, 0.05
TILE_POINTS = 65 * 65
GRID_STEP = 4.0                                              # metres per grid step
MAX_PIXELS = 64_000_000

ROAD = (50, 50, 50)
RAIL = (205, 30, 30)
ROAD_HEX, RAIL_HEX = "#323232", "#cd1e1e"      # the same two colours, for the SVG

# height ramp (metres, colour), interpolated; water and land are told apart by waterLevel
LAND = [(0, (190, 205, 140)), (30, (130, 175, 105)), (100, (165, 155, 105)),
        (200, (140, 120, 100)), (300, (235, 235, 235))]
SHALLOW, DEEP = (120, 175, 220), (30, 75, 125)


GAME_DIRS = ("~/.steam/steam", "~/.local/share/Steam", "~/snap/steam/common/.local/share/Steam",
             "~/.var/app/com.valvesoftware.Steam/.local/share/Steam")
VEHICLE_MODES = re.compile(r'"(?:CAR|BUS|TRUCK|TRAM|ELECTRIC_TRAM|TRAIN|ELECTRIC_TRAIN)"')   # whole names: "CARGO" is not "CAR"
_LANES = re.compile(r"laneConfigs\s*=\s*\{(.*?)\n\t\t\},", re.S)
_MODES = re.compile(r"transportModes\s*=\s*\{([^}]*)\}")


def find_content(game_dir=None):
    """The game's `base/content/infrastructure` folder, from `game_dir` (the install folder) or
    the usual Steam places, or None."""
    roots = [os.path.expanduser(game_dir)] if game_dir else \
        [os.path.join(os.path.expanduser(d), "steamapps", "common", "Transport Fever 3") for d in GAME_DIRS]
    for root in roots:
        path = os.path.join(root, "base", "content", "infrastructure")
        if os.path.isdir(path):
            return path
    return None


def read_lane_counts(content):
    """{template: vehicle lane count} for every street and track template in the install's
    `infrastructure/street.zip` and `track.zip`, read when the script runs (nothing is stored).
    A template's `laneConfigs` list has one entry per lane; lanes that only take people and cargo
    (the footpaths) and lanes with no mode do not count."""
    out = {}
    for name in ("street", "track"):
        try:
            zf = zipfile.ZipFile(os.path.join(content, name + ".zip"))
        except (OSError, zipfile.BadZipFile):
            continue
        for member in zf.namelist():
            if not member.endswith(".street_template.lua"):
                continue
            m = _LANES.search(zf.read(member).decode("utf-8", "replace"))
            lanes = _MODES.findall(m.group(1)) if m else []
            out[member[:-len(".street_template.lua")]] = sum(1 for modes in lanes if VEHICLE_MODES.search(modes))
    return out


def edge_width(edge, lanes, unit, mpp):
    """Stroke width in metres: `unit` for two vehicle lanes, in proportion to the lane count over
    two (a track has one lane, so half), never under one terrain pixel. A type with no lane count
    (a mod's, or no install) counts as two lanes."""
    n = lanes.get(edge["template"]) or 2
    return max(unit * n / 2.0, mpp)


def read_terrain(data):
    """(tiles_x, tiles_y, offset_z, metres per height unit, water_level) from the terrain record,
    found by its resolution triple. Raises ValueError when no plausible record is found."""
    pos = data.find(RESOLUTION)
    while pos >= 0:
        if pos >= 12:
            tx, ty, _levels = struct.unpack_from("<III", data, pos - 12)
            _high, off_z, water = struct.unpack_from("<Iff", data, pos + 12)
            if 0 < tx < 1000 and 0 < ty < 1000 and -1000 < off_z < 1000 and -1000 < water < 1000:
                return tx, ty, off_z, struct.unpack_from("<f", data, pos + 8)[0], water
        pos = data.find(RESOLUTION, pos + 1)
    raise ValueError("no terrain record")


def read_heightmap(data, tiles_x, tiles_y):
    """The stitched grid as a list of `array('H')` rows, row r (y rising from the map's south edge)
    of 64 * tiles_x + 1 points. Found by `0e 00 00 00`, 12 zero bytes, the tile count and 4225
    together. The u32 before the `0e` is `ff ff ff ff` in some saves and a small number in others,
    so it is not part of the key."""
    count = tiles_x * tiles_y
    key = struct.pack("<II", count, TILE_POINTS)
    prefix = b"\x0e\x00\x00\x00" + bytes(12)
    pos = data.find(prefix + key)
    if pos < 0:
        raise ValueError("no heightmap with %d tiles" % count)
    p = pos + len(prefix) + 4                                # at the first tile's length
    width, height = 64 * tiles_x + 1, 64 * tiles_y + 1
    rows = [array("H", bytes(2 * width)) for _ in range(height)]
    for i in range(count):
        n = struct.unpack_from("<I", data, p)[0]
        if n != TILE_POINTS:
            raise ValueError("tile %d has %d points" % (i, n))
        tile = array("H")
        tile.frombytes(data[p + 4:p + 4 + 2 * n])
        if sys.byteorder == "big":
            tile.byteswap()
        ty, tx = divmod(i, tiles_x)
        for r in range(65):
            rows[64 * ty + r][64 * tx:64 * tx + 65] = tile[r * 65:(r + 1) * 65]
        p += 4 + 2 * n
    return rows


def _lerp(a, b, t):
    return tuple(a[k] + (b[k] - a[k]) * t for k in range(3))


def _land_colour(z):
    if z <= LAND[0][0]:
        return LAND[0][1]
    for (z0, c0), (z1, c1) in zip(LAND, LAND[1:]):
        if z <= z1:
            return _lerp(c0, c1, (z - z0) / (z1 - z0))
    return LAND[-1][1]


def upsample(rows, f):
    """The grid with `f` points per original step, interpolated bilinearly (rounded to `u16`)."""
    def stretch(row):
        out = array("H")
        for a, b in zip(row, row[1:]):
            out.extend(a + (b - a) * k // f for k in range(f))
        out.append(row[-1])
        return out
    wide = [stretch(r) for r in rows]
    out = []
    for r0, r1 in zip(wide, wide[1:]):
        for k in range(f):
            out.append(array("H", (a + (b - a) * k // f for a, b in zip(r0, r1))))
    out.append(wide[-1])
    return out


def crop_grid(rows, tx, ty, cx, cy, radius):
    """The part of the grid within `radius` metres of (cx, cy), and the map coordinates of its
    top-left pixel (x_left, y_top)."""
    w, h = tx * 256, ty * 256
    c0 = max(0, int((cx - radius + w / 2) // GRID_STEP))
    c1 = min(64 * tx, int(-(-(cx + radius + w / 2) // GRID_STEP)))
    r0 = max(0, int((cy - radius + h / 2) // GRID_STEP))
    r1 = min(64 * ty, int(-(-(cy + radius + h / 2) // GRID_STEP)))
    if c1 - c0 < 2 or r1 - r0 < 2:
        raise ValueError("the crop lies outside the map")
    return [r[c0:c1 + 1] for r in rows[r0:r1 + 1]], (-w / 2 + GRID_STEP * c0, -h / 2 + GRID_STEP * r1)


def render(rows, step, off_z, unit, water, spacing=None):
    """RGB bytes (top row first) and (width, height) of the grid sampled every `step` points.
    Hill shading from the north-west, vertical scale doubled."""
    # image row j is grid row (last - j * step), north first
    last = len(rows) - 1
    picked = [rows[last - j * step][::step] for j in range((last // step) + 1)]
    w, h = len(picked[0]), len(picked)
    spacing = spacing or GRID_STEP * step
    water_v = (water - off_z) / unit
    cache = {}

    def base(v):
        c = cache.get(v)
        if c is None:
            z = off_z + v * unit
            if v < water_v:
                c = (False, _lerp(SHALLOW, DEEP, min(1.0, (water - z) / 100.0)))
            else:
                c = (True, _land_colour(z - water))
            cache[v] = c
        return c

    lx, ly, lz = -0.55, 0.55, 0.63                           # towards the light (north-west, up)
    out = bytearray(w * h * 3)
    k = 2.0 * unit / (2 * spacing)
    for j in range(h):
        row = picked[j]
        up = picked[j - 1] if j else row                     # north of it
        down = picked[j + 1] if j + 1 < h else row
        o = j * w * 3
        for i in range(w):
            is_land, col = base(row[i])
            if is_land:
                dzdx = (row[i + 1 if i + 1 < w else i] - row[i - 1 if i else i]) * k
                dzdy = (up[i] - down[i]) * k                 # y rises towards the top of the image
                s = (-dzdx * lx - dzdy * ly + lz) / (1 + dzdx * dzdx + dzdy * dzdy) ** 0.5
                f = max(0.55, min(1.25, 0.5 + 0.75 * s))
                out[o:o + 3] = bytes(min(255, int(c * f)) for c in col)
            else:
                out[o:o + 3] = bytes(int(c) for c in col)
            o += 3
    return out, (w, h)


def _line(img, w, h, x0, y0, x1, y1, colour, width=1):
    """Bresenham line in pixel coordinates, clipped to the image by skipping outside points."""
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    px = bytes(colour)
    lo, hi = -((width - 1) // 2), width // 2 + 1
    while True:
        for yy in range(y0 + lo, y0 + hi):
            for xx in range(x0 + lo, x0 + hi):
                if 0 <= xx < w and 0 <= yy < h:
                    o = (yy * w + xx) * 3
                    img[o:o + 3] = px
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def draw_network(img, size, x_left, y_top, mpp, edges, lanes):
    """Draw roads, then rails over them. Returns (roads drawn, rails drawn)."""
    w, h = size
    n = {"street": 0, "track": 0}
    for fam, colour in (("street", ROAD), ("track", RAIL)):
        for e in edges:
            if e["family"] != fam and not (fam == "street" and e["family"] is None):
                continue
            (x0, y0, _), (x1, y1, _) = e["p0"], e["p1"]
            _line(img, w, h, (x0 - x_left) / mpp, (y_top - y0) / mpp,
                  (x1 - x_left) / mpp, (y_top - y1) / mpp, colour,
                  max(1, round(edge_width(e, lanes, max(3.0, 1.5 * mpp), mpp) / mpp)))
            n[fam] += 1
    return n["street"], n["track"]


def grid_layers(size, mpp, x_left, y_top, step):
    """The grid as two layers, `grid` (the lines) and `grid-labels` (the coordinates, at the top
    and left edges, meant to be drawn last so they sit over the network). A line at every
    multiple of `step` metres in map x and y: those at multiples of 1000 m are darker and
    thicker, the others dotted and faint. Coordinates inside are metres from the image's
    top-left corner, like the other layers."""
    w, h = size[0] * mpp, size[1] * mpp
    size_t = max(7 * mpp, step * 0.07)                   # label size in metres
    major = 'fill="none" stroke="#000" stroke-opacity="0.6" stroke-width="%g"' % max(mpp, 1.0)
    minor = ('fill="none" stroke="#000" stroke-opacity="0.3" stroke-width="%g" stroke-dasharray="%g %g"'
             % (max(0.5 * mpp, 0.5), 2 * mpp, 4 * mpp))
    text = ('font-family="sans-serif" font-size="%g" fill="#000" stroke="#fff" stroke-width="%g"'
            ' paint-order="stroke"' % (size_t, size_t / 5))
    scale = "scale(%g)" % (1.0 / mpp)
    lines = ['<g id="grid" inkscape:groupmode="layer" inkscape:label="Grid %d m" transform="%s">' % (step, scale)]
    labels = ['<g id="grid-labels" inkscape:groupmode="layer" inkscape:label="Grid labels" transform="%s">' % scale]
    x = -(-x_left // step) * step                        # the first multiple of step at or after x_left
    while x <= x_left + w:
        px = x - x_left
        lines.append('<path d="M%g 0V%g" %s/>' % (px, h, major if x % 1000 == 0 else minor))
        labels.append('<text x="%g" y="%g" %s>x %d</text>' % (px + size_t * 0.3, size_t * 1.1, text, x))
        x += step
    y = -(-(y_top - h) // step) * step
    while y <= y_top:
        py = y_top - y
        lines.append('<path d="M0 %gH%g" %s/>' % (py, w, major if y % 1000 == 0 else minor))
        labels.append('<text x="%g" y="%g" %s>y %d</text>' % (size_t * 0.3, py - size_t * 0.3, text, y))
        y += step
    return lines + ["</g>"], labels + ["</g>"]


def svg_document(png, size, mpp, x_left, y_top, edges, lanes, grid=None):
    """SVG text in three layers (groups that Inkscape shows as layers): `terrain` (the PNG as a
    data URI), `roads` and `rails`, each holding one path per street or track type.
    Coordinates inside the layers are metres from the image's top-left corner."""
    w, h = size[0] * mpp, size[1] * mpp
    unit = max(3.0, 1.5 * mpp)       # metres: two vehicle lanes wide, 1.5 terrain pixels and at least 3 m
    groups = {"road": {}, "rail": {}}
    for e in edges:
        fam = "rail" if e["family"] == "track" else "road"
        (x0, y0, _), (x1, y1, _) = e["p0"], e["p1"]
        groups[fam].setdefault((e["type"] or "unknown", edge_width(e, lanes, unit, mpp)), []).append(
            "M%.1f %.1fL%.1f %.1f" % (x0 - x_left, y_top - y0, x1 - x_left, y_top - y1))
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
             ' xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"'
             ' width="%d" height="%d" viewBox="0 0 %d %d">' % (size[0], size[1], size[0], size[1]),
             '<title>Terrain, roads and rails</title>',
             '<style>.road{stroke:%s}.rail{stroke:%s}'
             '.road,.rail{fill:none;stroke-linecap:round;stroke-linejoin:round}</style>'
             % (ROAD_HEX, RAIL_HEX),
             '<g id="terrain" inkscape:groupmode="layer" inkscape:label="Terrain" transform="scale(%g)">' % (1.0 / mpp),
             '<image width="%d" height="%d" xlink:href="data:image/png;base64,%s"/>'
             % (w, h, base64.b64encode(png).decode()),
             '</g>']
    grid_labels = []
    if grid:                                             # the lines above the terrain, under the network
        grid_lines, grid_labels = grid_layers(size, mpp, x_left, y_top, grid)
        parts += grid_lines
    for fam, label in (("road", "Roads"), ("rail", "Rails")):     # rails last, so they draw on top
        parts.append('<g id="%ss" inkscape:groupmode="layer" inkscape:label="%s" transform="scale(%g)">'
                     % (fam, label, 1.0 / mpp))
        for (t, width), segs in sorted(groups[fam].items()):
            parts.append('<path class="%s %s" d="%s" fill="none" stroke="%s" stroke-width="%g"'
                         ' stroke-linecap="round" stroke-linejoin="round"/>'
                         % (fam, t, "".join(segs), ROAD_HEX if fam == "road" else RAIL_HEX, width))
        parts.append("</g>")
    parts += grid_labels                                 # the coordinates over everything
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out_dir")
    ap.add_argument("saves", nargs="+")
    ap.add_argument("--mpp", type=int, default=4)
    ap.add_argument("--crop", help="X,Y,R: the square of half-width R metres around (X, Y)")
    ap.add_argument("--png", action="store_true")
    ap.add_argument("--grid", type=int, metavar="N", help="SVG only: a labelled line every N metres of map x and y")
    ap.add_argument("--game", help="the game's install folder, for the lane counts "
                    "(default: the usual Steam places)")
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--stream", action="store_true")
    ap.add_argument("--force-size", action="store_true")
    args = ap.parse_args()
    if args.mpp not in (1, 2) and (args.mpp < 4 or args.mpp % 4):
        ap.error("--mpp must be 1, 2 or a multiple of 4 (the heightmap spacing)")
    if args.grid is not None and (args.grid < 1 or args.png):
        ap.error("--grid wants a step of 1 metre or more, and only works with the SVG")
    crop = None
    if args.crop:
        try:
            crop = tuple(float(v) for v in args.crop.split(","))
            assert len(crop) == 3 and crop[2] > 0
        except (ValueError, AssertionError):
            ap.error("--crop wants X,Y,R in metres")
    os.makedirs(args.out_dir, exist_ok=True)
    content = find_content(args.game)
    lanes = read_lane_counts(content) if content else {}
    print("lane counts: %s" % (("%d templates read from the install" % len(lanes)) if lanes else
                               "no install found (--game DIR), every road drawn at two-lane width"))
    step, fine = max(1, args.mpp // 4), (4 // args.mpp if args.mpp < 4 else 1)
    for path in args.saves:
        try:
            raw = open(path, "rb").read()
            data = raw if args.stream else decompress(raw)
            tx, ty, off_z, unit, water = read_terrain(data)
            map_w, map_h = tx * 256, ty * 256
            if crop:
                pixels = (2 * crop[2] // args.mpp + 1) ** 2
            else:
                pixels = (map_w // args.mpp + 1) * (map_h // args.mpp + 1)
            if pixels > MAX_PIXELS and not args.force_size:
                print("REFUSED %s: %d x %d m at %d m/px is %d million pixels; raise --mpp"
                      % (os.path.basename(path), map_w, map_h, args.mpp, pixels // 1000000))
                continue
            if args.mpp < 4 and not crop:
                print("REFUSED %s: --mpp %d needs --crop" % (os.path.basename(path), args.mpp))
                continue
            rows = read_heightmap(data, tx, ty)
            x_left, y_top = -map_w / 2, map_h / 2
            if crop:
                rows, (x_left, y_top) = crop_grid(rows, tx, ty, *crop)
            if fine > 1:
                rows = upsample(rows, fine)
            img, size = render(rows, step, off_z, unit, water, args.mpp)
            roads = rails = 0
            edges = [] if args.no_network else read_edges(data)
            if crop:                                  # only the edges that touch the picture
                x1, y1 = x_left + size[0] * args.mpp, y_top - size[1] * args.mpp
                edges = [e for e in edges
                         if max(e["p0"][0], e["p1"][0]) >= x_left and min(e["p0"][0], e["p1"][0]) <= x1
                         and max(e["p0"][1], e["p1"][1]) >= y1 and min(e["p0"][1], e["p1"][1]) <= y_top]
            if not args.png:
                roads = sum(e["family"] != "track" for e in edges)
                rails = len(edges) - roads
            elif edges:
                roads, rails = draw_network(img, size, x_left, y_top, args.mpp, edges, lanes)
        except Exception as e:  # report and carry on with the next save
            print(f"FAILED {os.path.basename(path)}: {e}")
            continue
        name = re.sub(r"\s+", "_", os.path.splitext(os.path.basename(path))[0])
        dest = os.path.join(args.out_dir, name
                            + ("-crop%d_%d_%d" % crop if crop else "")
                            + ("-grid%d" % args.grid if args.grid else "") + "-terrain.png")
        png = png_bytes(size[0], size[1], bytes(img))
        if not args.png:
            dest = dest[:-len(".png")] + ".svg"
            open(dest, "w").write(svg_document(png, size, args.mpp, x_left, y_top, edges, lanes, args.grid))
        else:
            open(dest, "wb").write(png)
        print("%s  %d x %d px, %d m/px, map %d x %d m%s, %d road and %d rail edges"
              % (dest, size[0], size[1], args.mpp, map_w, map_h, ", cropped" if crop else "", roads, rails))


if __name__ == "__main__":
    main()
