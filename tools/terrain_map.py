#!/usr/bin/env python3
"""Draw a save's terrain as a PNG, with its roads and rails on top.

Usage: terrain_map.py OUT_DIR SAVE.sav [...] [--mpp M] [--no-network] [--stream]

Read only: no save is written. The image goes to OUT_DIR/<save name>-terrain.png and the script
prints its size, the metres per pixel and the edge counts. The terrain colours are a plain
height ramp with hill shading (water below the save's `waterLevel` in blue); they are not the
game's own palette.

--mpp M      metres per pixel, a multiple of 4 (default 4, the heightmap's own spacing). Larger
             values keep every (M / 4)th grid point. A map that would come out wider or taller
             than 8,000 pixels is refused unless --mpp is raised or --force-size is given.
--no-network leave the roads and rails out.
--stream     the files are decompressed streams, not saves.

Layout read (docs/terrain.md): the terrain record gives the map in 256 m tiles and the height
scale; the heightmap is one `vec<u16>` of 65 x 65 per tile, tile `ty * tiles_x + tx`. Grid point
(c, r) of the stitched grid is at x = -width / 2 + 4c, y = -height / 2 + 4r. North is up in the
image: row 0 is the largest y. That y points north is the usual top-down reading of a right-handed
map and was not checked against the game's compass.

The roads and rails are the street-edge table (docs/road-network.md, street_edges.py), straight
chords between the end positions, one pixel wide: roads dark grey, rails red. Bridges and tunnels
are not told apart from the rest. A deleted road can stay in the table for one save.
"""
import argparse
import os
import struct
import sys
from array import array

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from save_preview import png_bytes  # noqa: E402
from street_edges import read_edges  # noqa: E402
from tf3save import decompress  # noqa: E402

RESOLUTION = bytes.fromhex("0000804000008040cdcc4c3d")      # 4.0, 4.0, 0.05
TILE_POINTS = 65 * 65
GRID_STEP = 4.0                                              # metres per grid step
MAX_SIDE = 8000

ROAD = (50, 50, 50)
RAIL = (205, 30, 30)

# height ramp (metres, colour), interpolated; water and land are told apart by waterLevel
LAND = [(0, (190, 205, 140)), (30, (130, 175, 105)), (100, (165, 155, 105)),
        (200, (140, 120, 100)), (300, (235, 235, 235))]
SHALLOW, DEEP = (120, 175, 220), (30, 75, 125)


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


def render(rows, step, off_z, unit, water):
    """RGB bytes (top row first) and (width, height) of the grid sampled every `step` points.
    Hill shading from the north-west, vertical scale doubled."""
    # image row j is grid row (last - j * step), north first
    last = len(rows) - 1
    picked = [rows[last - j * step][::step] for j in range((last // step) + 1)]
    w, h = len(picked[0]), len(picked)
    spacing = GRID_STEP * step
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


def _line(img, w, h, x0, y0, x1, y1, colour):
    """Bresenham line in pixel coordinates, clipped to the image by skipping outside points."""
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    px = bytes(colour)
    while True:
        if 0 <= x0 < w and 0 <= y0 < h:
            o = (y0 * w + x0) * 3
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


def draw_network(img, size, map_w, map_h, mpp, edges):
    """Draw roads, then rails over them. Returns (roads drawn, rails drawn)."""
    w, h = size
    n = {"street": 0, "track": 0}
    for fam, colour in (("street", ROAD), ("track", RAIL)):
        for e in edges:
            if e["family"] != fam and not (fam == "street" and e["family"] is None):
                continue
            (x0, y0, _), (x1, y1, _) = e["p0"], e["p1"]
            _line(img, w, h, (x0 + map_w / 2) / mpp, (map_h / 2 - y0) / mpp,
                  (x1 + map_w / 2) / mpp, (map_h / 2 - y1) / mpp, colour)
            n[fam] += 1
    return n["street"], n["track"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out_dir")
    ap.add_argument("saves", nargs="+")
    ap.add_argument("--mpp", type=int, default=4)
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--stream", action="store_true")
    ap.add_argument("--force-size", action="store_true")
    args = ap.parse_args()
    if args.mpp < 4 or args.mpp % 4:
        ap.error("--mpp must be a multiple of 4 (the heightmap spacing)")
    os.makedirs(args.out_dir, exist_ok=True)
    step = args.mpp // 4
    for path in args.saves:
        try:
            raw = open(path, "rb").read()
            data = raw if args.stream else decompress(raw)
            tx, ty, off_z, unit, water = read_terrain(data)
            map_w, map_h = tx * 256, ty * 256
            side = max(map_w, map_h) // args.mpp + 1
            if side > MAX_SIDE and not args.force_size:
                print("REFUSED %s: %d x %d m at %d m/px is %d px on a side; raise --mpp"
                      % (os.path.basename(path), map_w, map_h, args.mpp, side))
                continue
            rows = read_heightmap(data, tx, ty)
            img, size = render(rows, step, off_z, unit, water)
            roads = rails = 0
            if not args.no_network:
                roads, rails = draw_network(img, size, map_w, map_h, args.mpp, read_edges(data))
        except Exception as e:  # report and carry on with the next save
            print(f"FAILED {os.path.basename(path)}: {e}")
            continue
        dest = os.path.join(args.out_dir, os.path.splitext(os.path.basename(path))[0] + "-terrain.png")
        open(dest, "wb").write(png_bytes(size[0], size[1], bytes(img)))
        print("%s  %d x %d px, %d m/px, map %d x %d m, %d road and %d rail edges"
              % (dest, size[0], size[1], args.mpp, map_w, map_h, roads, rails))


if __name__ == "__main__":
    main()
