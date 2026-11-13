#!/usr/bin/env python3
"""Read the terrain record and heightmap of a TF3 save, and compare the heightmaps of two saves.

Usage:
  terrain_heights.py SAVE.sav [NEW.sav] [--stream]

With one save it prints the terrain record (tiles, offsetZ, metres per height unit, waterLevel), the lowest and
highest ground, and the biome and layer grid (docs/biome-grid.md): the share of points per biome and per layer bit.
With two it compares the grids point by point (docs/terrain-edits.md): how many points changed, the
box they lie in (in map metres, the centre 0, 0) and the smallest and largest change in metres, and how many points
of the biome grid changed. `--stream` takes
streams already decompressed. Only reads: no save is written. The layout is in docs/terrain.md; drawing the
terrain is tf3map's job (the tf3-save-mapper repo).

`read_terrain`, `read_heightmap` and `read_biome_grid` are the readers other scripts import.
"""
import argparse
import os
import struct
import sys
from array import array

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tf3save import decompress  # noqa: E402

RESOLUTION = bytes.fromhex("0000804000008040cdcc4c3d")      # 4.0, 4.0, 0.05
TILE_POINTS = 65 * 65


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
    """The stitched grid as a list of `array('H')` rows, row r (y rising with r) of
    64 * tiles_x + 1 points (x rising along the row). Found by `0e 00 00 00`, 12 zero bytes, the tile count and 4225
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


def read_biome_grid(data, tiles_x, tiles_y):
    """(offset of the header, rows) of the biome and layer grid (docs/biome-grid.md), or None when the save
    has none. One `u16` per heightmap point in a single grid, not in tiles: rows as in `read_heightmap`
    (row r, y rising with r, of 64 * tiles_x + 1 points, x rising along the row). Found by its header, the
    width, the height and their product as three `u32`. The low four bits of a value are the biome id, bit
    4 + n is the climate's data layer with id n."""
    width, height = 64 * tiles_x + 1, 64 * tiles_y + 1
    pos = data.find(struct.pack("<III", width, height, width * height))
    if pos < 0 or pos + 12 + 2 * width * height > len(data):
        return None
    grid = array("H")
    grid.frombytes(data[pos + 12:pos + 12 + 2 * width * height])
    if sys.byteorder == "big":
        grid.byteswap()
    return pos, [grid[r * width:(r + 1) * width] for r in range(height)]


def grid_shares(rows):
    """({biome id: share}, {layer id: share}) over all points of a biome grid."""
    counts = {}
    for r in rows:
        for v in set(r):
            counts[v] = counts.get(v, 0) + r.count(v)
    total = sum(counts.values())
    biomes, layers = {}, {}
    for v, k in counts.items():
        biomes[v & 15] = biomes.get(v & 15, 0) + k / total
        for n in range(12):
            if v >> (4 + n) & 1:
                layers[n] = layers.get(n, 0) + k / total
    return dict(sorted(biomes.items())), dict(sorted(layers.items()))


def load(path, stream):
    raw = open(path, "rb").read()
    data = raw if stream else decompress(raw)
    terrain = read_terrain(data)
    return terrain, read_heightmap(data, terrain[0], terrain[1])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("save")
    ap.add_argument("new", nargs="?")
    ap.add_argument("--stream", action="store_true", help="the files are decompressed streams")
    args = ap.parse_args()
    raw = open(args.save, "rb").read()
    data = raw if args.stream else decompress(raw)
    del raw
    tx, ty, off_z, unit, water = read_terrain(data)
    rows = read_heightmap(data, tx, ty)
    grid = read_biome_grid(data, tx, ty)
    del data
    print("tiles %d x %d  offsetZ %.2f  unit %.3f m  waterLevel %.2f" % (tx, ty, off_z, unit, water))
    if not args.new:
        lo, hi = min(min(r) for r in rows), max(max(r) for r in rows)
        print("ground %.1f to %.1f m" % (off_z + lo * unit, off_z + hi * unit))
        if grid is None:
            print("biome grid: none")
        else:
            biomes, layers = grid_shares(grid[1])
            print("biome grid: biomes " + "  ".join("%d %.1f%%" % (b, 100 * x) for b, x in biomes.items())
                  + ";  layers " + ("  ".join("%d (bit %d) %.1f%%" % (n, 4 + n, 100 * x) for n, x in layers.items()) or "none"))
        return
    raw = open(args.new, "rb").read()
    data = raw if args.stream else decompress(raw)
    del raw
    tx2, ty2, _, _, _ = read_terrain(data)
    new = read_heightmap(data, tx2, ty2)
    grid2 = read_biome_grid(data, tx2, ty2)
    del data
    if (tx2, ty2) != (tx, ty):
        sys.exit("terrain_heights.py: the saves have %d x %d and %d x %d tiles" % (tx, ty, tx2, ty2))
    half_w, half_h = 128 * tx, 128 * ty                     # 64 points of 4 m a tile
    changed, box, lo, hi = 0, None, 0, 0
    for r, (a, b) in enumerate(zip(rows, new)):
        if a == b:
            continue
        for c, (u, v) in enumerate(zip(a, b)):
            if u != v:
                changed += 1
                lo, hi = min(lo, v - u), max(hi, v - u)
                x, y = 4 * c - half_w, 4 * r - half_h
                box = (x, y, x, y) if box is None else (min(box[0], x), min(box[1], y), max(box[2], x), max(box[3], y))
    total = len(rows) * len(rows[0])
    print("changed %d of %d points (%.2f%%)" % (changed, total, 100.0 * changed / total))
    if box:
        print("box x %d to %d, y %d to %d m; change %+.2f to %+.2f m" % (box[0], box[2], box[1], box[3],
                                                                          lo * unit, hi * unit))
    if grid is None or grid2 is None:
        print("biome grid: %s" % ("none in either save" if grid is grid2 else "in one save only"))
    else:
        diff = sum(sum(1 for u, v in zip(a, b) if u != v) for a, b in zip(grid[1], grid2[1]) if a != b)
        print("biome grid: %d of %d points changed" % (diff, total))


if __name__ == "__main__":
    main()
