#!/usr/bin/env python3
"""Draw a save's terrain as an SVG, with its roads and rails on top.

Usage: terrain_map.py OUT_DIR SAVE.sav [...] [--mpp M] [--crop X,Y,R] [--grid N] [--png]
       [--game DIR] [--no-network] [--depots] [--coverage] [--stream]

Read only: no save is written. The picture goes to OUT_DIR/<save name>-terrain.svg and the script
prints its size, the metres per pixel and the edge counts. The SVG holds the terrain as an
embedded PNG and the roads and rails as vector paths on top. Every layer is a group with
`class="layer"`, its id repeated in `data-layer` and Inkscape's layer attributes, so a page script can list
them with `g.layer` and toggle `display`. Layers, bottom to top: `terrain`, `grid`, `roads` and `rails` (each a
parent with one sublayer per street or track type, `road-TYPE` / `rail-TYPE`, holding one `<path>` per edge with
`data-a` and `data-b` (the end node ids in hex), class `road` or `rail` plus the type name, and `data-edge` where
the strip table gave the edge's entity id), `vehicles` (a sublayer per class, `vehicles-train` (wagons included),
`-tram`, `-truck`, `-bus`, `-car`, `-ship`, ...; each vehicle one `<g class="vehicle CLASS" id="vehicle-SLOT">` with
`data-slot`, `data-model`, `data-class`, `data-x`, `data-y`, holding its shape and name), `labels` (`edge-labels`:
one `<g class="edge-label" data-a data-b>` each; `nodes`: one `<g class="node" data-x data-y data-edges>` per
end node), `maintenance-buildings`, `road-depots` and `tram-depots` (`--depots`), `coverage` (`--coverage`) and
`grid-labels`. The grid layers ignore the pointer. The colours and widths are also set on the
groups and paths, since Krita ignores the style sheet. The root's size and `viewBox` are the terrain image's pixels (so an editor such as Krita opens
it at that size, taking 96 PPI); each layer scales by 1 / (metres per pixel), so inside a layer
the units are map metres with the image's top-left corner at 0, 0. The line width is in metres too (1.5 terrain pixels, at least
3 m), so the lines scale with the terrain in every viewer; a width that stays fixed on screen
(`vector-effect: non-scaling-stroke`) turned short edges into blobs in VS Code's preview.
A `<metadata>` element
(namespace `urn:tf3-save-format:terrain-map:1`, one `view` element with attributes) records the
save's file name, the map size, the metres per pixel, the map point at the picture's top-left
corner and the x and y range the picture covers, the crop (X, Y, R) if any and the grid step.
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
             look at a station or a junction. X and Y are the map's own coordinates, not the
             picture's.
--png        write one flat PNG instead of the SVG, with the lines drawn into the pixels about 4 m
             wide (at least one pixel).
--grid N     (SVG only) add a `grid` layer: a line at every multiple of N metres of map x and y,
             labelled `y 4500` along the top (the lines that run up the picture) and `x -3000`
             along the left (the lines that run across it), so a place seen in the
             picture can be turned into the coordinates `--crop` wants. The map's centre is 0, 0.
             Lines at multiples of 1000 are darker and thicker, the others dotted and faint; the
             lines are one layer under the roads and the labels another over everything.
--game DIR   the game's install folder. A road is drawn with a stroke in proportion to its vehicle
             lane count over two (two lanes keep the base width, a track has one lane), read from
             the install's street and track templates when the script runs (nothing is copied
             into the tool or the picture). Without an install, or for a type the install lacks
             (a mod's), the width is the two-lane one. Default: the usual Steam folders.
--no-network leave the roads and rails out.
--label A>B[=TEXT]
             (SVG only, repeatable) add the edge with end nodes A and B (hex entity ids, in either
             order, the notation of docs/signals.md: `2a619>342aa`) to a `labels` layer: its name
             is written along it (TEXT if given, else `A>B`) and its end nodes are dotted. Only
             the edges named get a label: an edge is the one handle the table gives, but a curve
             is many short chords and a label on each would hide the picture, so the caller picks
             (`street_edges.py --near X,Y,R` lists the edges and their ids). A name that matches
             no edge in the picture is reported.
--edge-ids   with --label, add the edge's own entity id (`e1b50b`) to the text where the road-
             surface strip table has an entry for it (street_edges.py `--ids`; many edges have
             none, and the scan reads the whole stream).
--zoom N     (SVG only) the root's width and height are N times the picture's pixels, so a viewer
             opens a small crop larger; the `viewBox` and the layers do not change.
--vehicles   (SVG only) add a `vehicles` layer: every model instance under `vehicle/` in the
             picture, drawn as one five-sided shape, a rectangle with a pointed front end, a white outline (mid-dark grey for trains and trams, which run on the red track) and an interior by class: train engine dark orange, trailing unpowered train car light orange, tram purple, truck dark blue, bus dark green, ship dark grey (the water is blue), car and the rest mid grey (the facing is the
             first row of the instance's transform, docs/models.md), sized by class (the save
             holds no vehicle length: train 20 x 3 m, wagon and tram 14 x 3, truck 7 x 2.5, bus
             10 x 2.6, car 4.5 x 1.8, ship 40 x 8, other 6 x 2.5), and labelled only if named.
             `--name SLOT=TEXT` (repeat it) sets the name of one instance, such as
             `--name 48700="Road Vehicle 40"`: the save does not link an instance to the vehicle's number (docs/
             vehicles.md), so that is the caller's reading, for instance from a screenshot and a
             position. A default name is shortened in the label: `Road Vehicle 279`
             is `RV279`, `Train 58` `RR58`, `Ship 106` `S106`, `Tram 62` `TRM62`, `Aircraft 6`
             `AIR6`; any other text is written as given. The scan reads the whole stream (model_instances.py). Only the instances
             named get a text label; the run prints every instance drawn (slot, model, position,
             facing), so the caller can pick slots and run again.
--depots     (SVG only) add three layers, `maintenance-buildings` (the road maintenance building, `road_maint_station`),
             `road-depots` and `tram-depots`: each building's ground face as a dull orange (maintenance), teal (road
             depot) or purple (tram depot) rectangle with a black outline, its origin as a white dot and a red line along the
             model's x axis, one `<g class="depot KIND" id="depot-SLOT" data-slot data-model data-x data-y data-pool
             data-radius data-modes>` each. The rectangle is the first `ground_face` of the building's script in the
             install (`base/content/depots/road.zip`), placed from the instance's origin and facing as in docs/models.md;
             nothing of it is copied into the tool, so without an install no building is drawn. A road depot's second
             instance (`road_depot_sm`) and a mod's depots are left out. Reads the whole stream; no `--crop` needed.
--coverage   (SVG only) add a `coverage` layer under the roads, a sublayer per building kind
             (`coverage-maintenance-buildings`, `coverage-road-depots`, `coverage-tram-depots`) holding one dashed circle
             per building, centred on its origin, with the `catchmentArea` radius of its script (a maintenance building
             600 m, a depot 400 m: a default the script lets a caller change, which no save was checked for). The pool
             and the transport modes in `data-pool` and `data-modes` are the script's: a road depot
             covers buses and trucks, a tram depot trams, the maintenance building all three. Rail, ship and
             aircraft maintenance have their own scripts and are not drawn. Needs the install like `--depots`.
--stream     the files are decompressed streams, not saves.

Layout read (docs/terrain.md): the terrain record gives the map in 256 m tiles and the height
scale; the heightmap is one `vec<u16>` of 65 x 65 per tile, tile `ty * tiles_x + tx`. Grid point
(c, r) of the stitched grid is at x = -width / 2 + 4c, y = -height / 2 + 4r. The picture is turned
so that north is up and east is right: image up is +x and image right is -y, which is the grid
turned a quarter turn anticlockwise (docs/terrain.md, "Which way is north"). So a grid row is a
picture column, and the picture's width is the map's y extent.

The roads and rails are the street-edge table (docs/road-network.md, street_edges.py), straight
chords between the end positions: roads dark grey, rails red. Bridges and tunnels
are not told apart from the rest. A deleted road can stay in the table for one save.
"""
import argparse
import base64
import math
import os
import re
import struct
import sys
import zipfile
from array import array
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from save_preview import png_bytes  # noqa: E402
from model_instances import read_instances, short_model  # noqa: E402
from street_edges import edge_ids, read_edges, read_strips  # noqa: E402
from tf3save import decompress  # noqa: E402

RESOLUTION = bytes.fromhex("0000804000008040cdcc4c3d")      # 4.0, 4.0, 0.05
TILE_POINTS = 65 * 65
GRID_STEP = 4.0                                              # metres per grid step
MAX_PIXELS = 64_000_000

ROAD = (50, 50, 50)
RAIL = (205, 30, 30)
LABEL_TINTS = ("#ffffff", "#ffe34d", "#5fe0ff", "#ff9ee0")   # edge label halo and node dot colours, in turn
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


# road-vehicle maintenance buildings: (layer id, label, script path in depots/road.zip, model path, colour)
DEPOT_KINDS = (
    ("maintenance-buildings", "Road maintenance buildings", "road/road_maint_station.script.lua",
     "depots/road/road_maint_station/road_maint_station.mdl", "#f5a300"),
    ("road-depots", "Road depots", "road/road_depot/road_depot.script.lua",
     "depots/road/road_depot/road_depot.mdl", "#2a9d8f"),
    ("tram-depots", "Tram depots", "road/tram_depot/tram_depot.script.lua",
     "depots/road/tram_depot/tram_depot.mdl", "#8e5ea2"),
)
_FACE = re.compile(r'\["ground_face"\]\s*=\s*\{\s*\{((?:\s*\{[^}]*\},?)+)')
_POINT = re.compile(r"\{\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)")
_RADIUS = re.compile(r"catchmentArea\s*=\s*\{\s*radius\s*=\s*(?:captureParams\.radius or )?(\d+)")
_POOL = re.compile(r"maintenancePool\s*=\s*(\d+)")
_DEPOT_MODES = re.compile(r"transportModes\s*=\s*\{([^}]*)\}")


def read_depot_specs(content):
    """{layer id: {"face": [(a, b) ...], "radius", "pool", "modes"}} for the road maintenance building,
    the road depot and the tram depot, read when the script runs from the install's `depots/road.zip`
    (`content` is the `infrastructure` folder `find_content` returns): the first `ground_face` rectangle of the
    building's script in its own axes, the `catchmentArea` radius, the `maintenancePool` and the transport
    modes. A kind whose script or fields are missing is left out. Nothing is stored."""
    out = {}
    if not content:
        return out
    try:
        zf = zipfile.ZipFile(os.path.join(os.path.dirname(content), "depots", "road.zip"))
    except (OSError, zipfile.BadZipFile):
        return out
    for lid, _label, script, _model, _colour in DEPOT_KINDS:
        try:
            text = zf.read(script).decode("utf-8", "replace")
        except KeyError:
            continue
        face, radius, pool, modes = _FACE.search(text), _RADIUS.search(text), _POOL.search(text), _DEPOT_MODES.search(text)
        if face and radius:
            out[lid] = {"face": [(float(a), float(b)) for a, b in _POINT.findall(face.group(1))],
                        "radius": int(radius.group(1)), "pool": int(pool.group(1)) if pool else 0,
                        "modes": ",".join(re.findall(r'"(\w+)"', modes.group(1))) if modes else ""}
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
    """The part of the grid within `radius` metres of (cx, cy), and the map coordinates (x_top,
    y_left) of its top-left pixel in the north-up picture: the largest x and the largest y."""
    w, h = tx * 256, ty * 256
    c0 = max(0, int((cx - radius + w / 2) // GRID_STEP))
    c1 = min(64 * tx, int(-(-(cx + radius + w / 2) // GRID_STEP)))
    r0 = max(0, int((cy - radius + h / 2) // GRID_STEP))
    r1 = min(64 * ty, int(-(-(cy + radius + h / 2) // GRID_STEP)))
    if c1 - c0 < 2 or r1 - r0 < 2:
        raise ValueError("the crop lies outside the map")
    return [r[c0:c1 + 1] for r in rows[r0:r1 + 1]], (-w / 2 + GRID_STEP * c1, -h / 2 + GRID_STEP * r1)


def to_picture(rows, step):
    """The grid in the picture's order, every `step`th point: picture row j (top first, x falling)
    is grid column `last - j * step`, and along it y falls from the grid's last row."""
    width = len(rows[0])
    flat = array("H")
    for r in rows:
        flat.extend(r)
    picture = []
    for c in range(width - 1, -1, -step):
        col = flat[c::width]                                 # the column, y rising
        col.reverse()
        picture.append(col[::step])
    return picture


def render(rows, step, off_z, unit, water, spacing=None):
    """RGB bytes (top row first) and (width, height) of the grid sampled every `step` points,
    turned north up and east right. Hill shading from the north-west, vertical scale doubled."""
    picked = to_picture(rows, step)
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
                dzdy = (up[i] - down[i]) * k                 # rises towards the top of the picture
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


def draw_network(img, size, x_top, y_left, mpp, edges, lanes):
    """Draw roads, then rails over them. Returns (roads drawn, rails drawn). Picture x is
    `y_left - y` and picture y is `x_top - x` (north up, east right)."""
    w, h = size
    n = {"street": 0, "track": 0}
    for fam, colour in (("street", ROAD), ("track", RAIL)):
        for e in edges:
            if e["family"] != fam and not (fam == "street" and e["family"] is None):
                continue
            (x0, y0, _), (x1, y1, _) = e["p0"], e["p1"]
            _line(img, w, h, (y_left - y0) / mpp, (x_top - x0) / mpp,
                  (y_left - y1) / mpp, (x_top - x1) / mpp, colour,
                  max(1, round(edge_width(e, lanes, max(3.0, 1.5 * mpp), mpp) / mpp)))
            n[fam] += 1
    return n["street"], n["track"]


def layer(lid, label, attrs=""):
    """The opening tag of a layer: a group Inkscape shows as a layer, with `class="layer"` and
    `data-layer` holding its id so a script can list and toggle layers with `g.layer`."""
    return ('<g id="%s" class="layer" data-layer="%s" inkscape:groupmode="layer" inkscape:label="%s"%s>'
            % (lid, lid, label, attrs))


def safe_id(text):
    """`text` with anything but letters, digits, `_` and `-` replaced by `_`, for an element id."""
    return re.sub(r"[^A-Za-z0-9_-]+", "_", str(text))


def grid_layers(size, mpp, x_top, y_left, step):
    """The grid as two layers, `grid` (the lines) and `grid-labels` (the coordinates, at the top
    and left edges, meant to be drawn last so they sit over the network). A line at every
    multiple of `step` metres in map x and y: those at multiples of 1000 m are darker and
    thicker, the others dotted and faint. The lines of constant y run up the picture (y falls
    to the right) and are labelled along the top; those of constant x run across it (x falls
    downwards) and are labelled along the left. Coordinates inside are metres from the image's
    top-left corner, like the other layers."""
    w, h = size[0] * mpp, size[1] * mpp
    size_t = max(min(7 * mpp, 0.03 * max(w, h)), step * 0.07)   # label size in metres, smaller on a close crop
    major = 'fill="none" stroke="#000" stroke-opacity="0.6" stroke-width="%g"' % max(mpp, 1.0)
    minor = ('fill="none" stroke="#000" stroke-opacity="0.3" stroke-width="%g" stroke-dasharray="%g %g"'
             % (max(0.5 * mpp, 0.5), 2 * mpp, 4 * mpp))
    text = ('font-family="sans-serif" font-size="%g" fill="#000" stroke="#fff" stroke-width="%g"'
            ' paint-order="stroke"' % (size_t, size_t / 5))
    scale = "scale(%g)" % (1.0 / mpp)
    lines = [layer("grid", "Grid %d m" % step, ' transform="%s" pointer-events="none"' % scale)]
    labels = [layer("grid-labels", "Grid labels", ' transform="%s" pointer-events="none"' % scale)]
    y = (y_left // step) * step                          # the first multiple of step at or below y_left
    while y >= y_left - w:
        px = y_left - y
        lines.append('<path d="M%g 0V%g" %s/>' % (px, h, major if y % 1000 == 0 else minor))
        labels.append('<text x="%g" y="%g" %s>y %d</text>' % (px + size_t * 0.3, size_t * 1.1, text, y))
        y -= step
    x = (x_top // step) * step
    while x >= x_top - h:
        py = x_top - x
        lines.append('<path d="M0 %gH%g" %s/>' % (py, w, major if x % 1000 == 0 else minor))
        labels.append('<text x="%g" y="%g" %s>x %d</text>' % (size_t * 0.3, py - size_t * 0.3, text, x))
        x -= step
    return lines + ["</g>"], labels + ["</g>"]


META_NS = "urn:tf3-save-format:terrain-map:1"


def svg_metadata(size, mpp, x_top, y_left, map_size, crop=None, grid=None, source=None):
    """A `<metadata>` element recording where the picture sits on the map, so the SVG can be
    turned back into map coordinates (or redrawn) without the command line that made it. All
    values are map metres: `x-top` and `y-left` are the map point at the picture's top-left
    corner, and the picture spans x from `x-min` to `x-top` and y from `y-min` to `y-left`."""
    w, h = size[0] * mpp, size[1] * mpp
    attrs = [("source", source), ("map-width", map_size[0]), ("map-height", map_size[1]),
             ("metres-per-pixel", mpp), ("orientation", "north-up: image up is +x, image right is -y"),
             ("x-top", "%g" % x_top), ("x-min", "%g" % (x_top - h)),
             ("y-left", "%g" % y_left), ("y-min", "%g" % (y_left - w)),
             ("cropped", "true" if crop else "false")]
    if crop:
        attrs += [("crop-x", "%g" % crop[0]), ("crop-y", "%g" % crop[1]), ("crop-radius", "%g" % crop[2])]
    if grid:
        attrs.append(("grid-step", grid))
    return ('<metadata><tf3map:view xmlns:tf3map="%s" %s/></metadata>'
            % (META_NS, " ".join("%s=%s" % (k, quoteattr(str(v))) for k, v in attrs if v is not None)))


VEHICLE_SIZE = (("vehicle/train/", (20, 3)), ("vehicle/waggon/", (14, 3)), ("vehicle/tram/", (14, 3)),
                ("vehicle/truck/", (7, 2.5)), ("vehicle/bus/", (10, 2.6)), ("vehicle/car/", (4.5, 1.8)),
                ("vehicle/ship/", (40, 8)))
VEHICLE_FILL = (("vehicle/train/", "#d96a00"), ("vehicle/waggon/", "#ffc27a"), ("vehicle/tram/", "#8a4fc0"),
                ("vehicle/truck/", "#1f4fa8"), ("vehicle/bus/", "#1f7a3a"), ("vehicle/ship/", "#3c3c3c"))
RAIL_BOUND = ("vehicle/train/", "vehicle/waggon/", "vehicle/tram/")     # these get a grey outline: the track under them is red
RAIL_OUTLINE = "#5c5c5c"
VEHICLE_GREY = "#808080"                         # cars and anything else


SHORT_NAME = re.compile(r"^(Road Vehicle|Train|Ship|Tram|Aircraft) (\d+)(\??)$")
SHORT_PREFIX = {"Road Vehicle": "RV", "Train": "RR", "Ship": "S", "Tram": "TRM", "Aircraft": "AIR"}


def short_name(text):
    """A vehicle's default name shortened for a label: `Road Vehicle 279` -> `RV279`, `Train 58` ->
    `RR58`, `Ship 106` -> `S106`, `Tram 62` -> `TRM62`, `Aircraft 6` -> `AIR6` (a trailing `?`,
    for an unsure reading, is kept). Any other text, such as a name the player gave, stays as it is."""
    m = SHORT_NAME.match(text)
    return SHORT_PREFIX[m.group(1)] + m.group(2) + m.group(3) if m else text



def vehicle_class(model):
    """The folder a vehicle model sits in (`train`, `waggon`, `tram`, `truck`, `bus`, `car`, `ship`,
    ...), or `other`. A wagon is drawn on the `train` layer."""
    m = re.match(r"vehicle/([a-z_]+)/", model)
    return m.group(1) if m else "other"


def overlay_layers(size, mpp, x_top, y_left, edges, vehicles, labels=False, names=None):
    """SVG text for the `labels` layer (edge node pairs and their end nodes) and the `vehicles` layer (a
    five-sided shape (the body with a pointed front) per vehicle instance, with a text only for a slot in `names`),
    in the same metre units as the other layers. `edges` and `vehicles` may be empty. Each vehicle is a
    `<g class="vehicle CLASS" id="vehicle-SLOT" data-...>` in the sublayer of its class, each label a
    `<g class="edge-label">`, each end node a `<g class="node">`. Returns the
    SVG lines and the set of requested edge labels that matched no edge. `labels` is
    {frozenset of two node ids: text or None}."""
    names = names or {}
    fs = 4 * mpp + 4                                  # label size in metres: 8 px at 1 m/px
    halo = ' paint-order="stroke" stroke="#fff" stroke-width="%g" stroke-linejoin="round"' % (fs / 4)
    out, top = [], []                                 # `top` is the labels layer, drawn above the vehicles
    unmatched = set(labels or {})
    if labels:
        lfs = fs * 0.7
        top.append(layer("labels", "Labels", ' transform="scale(%g)" font-family="monospace" font-size="%g"'
                         ' text-anchor="middle" fill="#000"' % (1.0 / mpp, lfs)))
        picked = [e for e in edges if frozenset((e["a"], e["b"])) in labels]
        tint = {}                                                   # one light colour per labelled edge
        for e in picked:
            tint.setdefault(frozenset((e["a"], e["b"])), LABEL_TINTS[len(tint) % len(LABEL_TINTS)])
        ends = {}                                         # node point -> [(tint, direction along the edge, edge name)]
        for e in picked:
            c = tint[frozenset((e["a"], e["b"]))]
            for (x, y, _), (xo, yo, _) in ((e["p0"], e["p1"]), (e["p1"], e["p0"])):
                ends.setdefault((round(x, 1), round(y, 1)), []).append((c, (y - yo, xo - x), "%x>%x" % (e["a"], e["b"])))
        top.append(layer("edge-labels", "Edge labels"))
        for e in picked:
            key = frozenset((e["a"], e["b"]))
            unmatched.discard(key)
            (x0, y0, _), (x1, y1, _) = e["p0"], e["p1"]
            text = labels[key] or "%x>%x" % (e["a"], e["b"])
            if e.get("e"):
                text += " e%x" % e["e"]
            angle = math.degrees(math.atan2(x0 - x1, y0 - y1))     # the edge in picture axes
            if angle > 90 or angle < -90:                           # keep the text upright
                angle -= 180 if angle > 0 else -180
            top.append('<g class="edge-label" data-a="%x" data-b="%x"><text transform="translate(%.1f %.1f) rotate(%.1f)"'
                       ' y="%g" paint-order="stroke" stroke="%s" stroke-width="%g" stroke-linejoin="round">%s</text></g>'
                       % (e["a"], e["b"], y_left - (y0 + y1) / 2, x_top - (x0 + x1) / 2, angle, lfs * 1.1,
                          tint[key], fs / 4, escape(text)))
        top.append("</g>")
        r = lfs * 0.3
        ring = 'stroke="#000" stroke-width="%g"' % (lfs * 0.08)
        top.append(layer("nodes", "Edge end nodes"))
        for (x, y), parts in ends.items():
            cx, cy = y_left - y, x_top - x
            top.append('<g class="node" data-x="%g" data-y="%g" data-edges="%s">' % (x, y, " ".join(p[2] for p in parts)))
            top.append('<circle cx="%.1f" cy="%.1f" r="%g" fill="%s" %s/>' % (cx, cy, r, parts[-1][0], ring))
            if len(parts) > 1:                                      # a join: the half toward the first edge in its colour
                dx, dy = parts[0][1]
                n = math.hypot(dx, dy) or 1
                px_, py_ = -dy / n * r, dx / n * r
                top.append('<path d="M%.1f %.1f A%g %g 0 0 0 %.1f %.1f Z" fill="%s" %s/>'
                           % (cx + px_, cy + py_, r, r, cx - px_, cy - py_, parts[0][0], ring))
            top.append("</g>")
        top.append("</g>")
        top.append("</g>")
    if vehicles:
        out.append(layer("vehicles", "Vehicles", ' transform="scale(%g)" font-family="sans-serif" font-size="%g"'
                         % (1.0 / mpp, fs)))
        by_class = {}
        for v in vehicles:
            cls = vehicle_class(v["model"])
            by_class.setdefault("train" if cls == "waggon" else cls, []).append((cls, v))
        for layer_cls in sorted(by_class):
            out.append(layer("vehicles-" + safe_id(layer_cls), "Vehicles: " + layer_cls))
            for cls, v in by_class[layer_cls]:
                length, width = next((sz for pre, sz in VEHICLE_SIZE if v["model"].startswith(pre)), (6, 2.5))
                px, py = y_left - v["y"], x_top - v["x"]
                angle = math.degrees(math.atan2(-v["fx"], -v["fy"]))      # the facing in picture axes
                tip = min(width * 0.9, length / 2)                        # the point's length comes out of the body's
                fill = next((c for pre, c in VEHICLE_FILL if v["model"].startswith(pre)), VEHICLE_GREY)
                edge = RAIL_OUTLINE if v["model"].startswith(RAIL_BOUND) else "#fff"
                x0, x1, hw = -length / 2, length / 2, width / 2
                out.append('<g id="vehicle-%s" class="vehicle %s" data-slot="%s" data-model=%s data-class="%s"'
                           ' data-x="%.1f" data-y="%.1f">'
                           % (v["slot"], safe_id(cls), v["slot"], quoteattr(v["model"]), safe_id(cls), v["x"], v["y"]))
                out.append('<polygon transform="translate(%.1f %.1f) rotate(%.1f)" points="%g,%g %g,%g %g,0 %g,%g %g,%g"'
                           ' fill="%s" stroke="%s" stroke-width="0.5" stroke-linejoin="round"/>'
                           % (px, py, angle, x0, -hw, x1 - tip, -hw, x1, x1 - tip, hw, x0, hw, fill, edge))
                if v["slot"] in names:
                    out.append('<text x="%.1f" y="%.1f"%s>%s</text>'
                               % (px + max(length, 8) / 2 + 2, py - width / 2 - 1, halo, escape(short_name(names[v["slot"]]))))
                out.append("</g>")
            out.append("</g>")
        out.append("</g>")
    return out + top, unmatched


def depot_layers(mpp, x_top, y_left, instances, specs, footprints, coverage):
    """SVG lines for the depot layers: (`under`, `over`). `under` is the `coverage` layer (one circle per building,
    a sublayer per kind) and `over` the `maintenance-buildings`, `road-depots` and `tram-depots` layers (the
    ground face placed from the instance's origin and facing, its origin, a line along the model's x axis).
    `instances` are `read_instances` rows; only the exact model path of each kind is drawn, so a road depot's
    `road_depot_sm` twin is not. Units are metres like the other layers."""
    k = max(1.0, mpp / 2.0)
    under, over = [], []
    cover = []
    for lid, label, _script, model, colour in DEPOT_KINDS:
        spec = specs.get(lid)
        rows = [i for i in instances if i["model"] == model]
        if not spec or not rows:
            continue
        attrs = lambda i: ('id="depot-%s" class="depot %s" data-slot="%s" data-model=%s data-x="%.1f" data-y="%.1f"'
                           ' data-pool="%d" data-radius="%d" data-modes="%s"'
                           % (i["slot"], lid, i["slot"], quoteattr(model), i["x"], i["y"], spec["pool"], spec["radius"], spec["modes"]))
        if footprints:
            over.append(layer(lid, label, ' transform="scale(%g)" pointer-events="none"' % (1.0 / mpp)))
            for i in rows:
                n = math.hypot(i["fx"], i["fy"]) or 1.0
                fx, fy = i["fx"] / n, i["fy"] / n
                local = lambda a, b: (y_left - (i["y"] + a * fy + b * fx), x_top - (i["x"] + a * fx - b * fy))
                pts = " ".join("%.2f,%.2f" % local(a, b) for a, b in spec["face"])
                o, tip = local(0, 0), local(10 * k, 0)
                over.append("<g %s>" % attrs(i))
                over.append('<polygon points="%s" fill="%s" fill-opacity="0.28" stroke="#000" stroke-width="%g"/>'
                            % (pts, colour, 0.35 * k))
                over.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#c00" stroke-width="%g"/>'
                            % (o[0], o[1], tip[0], tip[1], 0.35 * k))
                over.append('<circle cx="%.2f" cy="%.2f" r="%g" fill="#fff" stroke="#000" stroke-width="%g"/>'
                            % (o[0], o[1], 0.9 * k, 0.3 * k))
                over.append("</g>")
            over.append("</g>")
        if coverage:
            cover.append(layer("coverage-" + lid, "Coverage: " + label))
            for i in rows:
                cx, cy = y_left - i["y"], x_top - i["x"]
                cover.append('<g %s><circle cx="%.2f" cy="%.2f" r="%d" fill="%s" fill-opacity="0.06" stroke="%s"'
                             ' stroke-width="%g" stroke-dasharray="%g %g"/></g>'
                             % (attrs(i), cx, cy, spec["radius"], colour, colour, 1.5 * mpp, 10 * mpp, 6 * mpp))
            cover.append("</g>")
    if cover:
        under.append(layer("coverage", "Coverage", ' transform="scale(%g)" pointer-events="none"' % (1.0 / mpp)))
        under += cover
        under.append("</g>")
    return under, over


def svg_document(png, size, mpp, x_top, y_left, edges, lanes, grid=None, metadata=None, overlay=(), zoom=1, under=(), over=()):
    """SVG text in layers (groups that Inkscape shows as layers, each `class="layer"` with its id in
    `data-layer`): `terrain` (the PNG as a data URI), `roads` and `rails`, each holding a sublayer per
    street or track type (`road-TYPE`, `rail-TYPE`) with one `<path data-a data-b>` per edge. `metadata` is the `svg_metadata` element, if wanted. Coordinates inside the layers are metres from the image's top-left corner, north up and east
    right (picture x is `y_left - y`, picture y is `x_top - x`)."""
    w, h = size[0] * mpp, size[1] * mpp
    unit = max(3.0, 1.5 * mpp)       # metres: two vehicle lanes wide, 1.5 terrain pixels and at least 3 m
    groups = {"road": {}, "rail": {}}                    # family -> type -> one <path> per edge
    for e in edges:
        fam = "rail" if e["family"] == "track" else "road"
        (x0, y0, _), (x1, y1, _) = e["p0"], e["p1"]
        groups[fam].setdefault(e["type"] or "unknown", []).append(
            '<path class="%s %s" data-a="%x" data-b="%x"%s stroke-width="%g" d="M%.1f %.1fL%.1f %.1f"/>'
            % (fam, safe_id(e["type"] or "unknown"), e["a"], e["b"], ' data-edge="%x"' % e["e"] if e.get("e") else "",
               edge_width(e, lanes, unit, mpp), y_left - y0, x_top - x0, y_left - y1, x_top - x1))
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
             ' xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"'
             ' width="%d" height="%d" viewBox="0 0 %d %d">' % (size[0] * zoom, size[1] * zoom, size[0], size[1]),
             '<title>Terrain, roads and rails</title>'] + ([metadata] if metadata else []) + [
             '<style>.road{stroke:%s}.rail{stroke:%s}'
             '.road,.rail{fill:none;stroke-linecap:round;stroke-linejoin:round}</style>'
             % (ROAD_HEX, RAIL_HEX),
             layer("terrain", "Terrain", ' transform="scale(%g)"' % (1.0 / mpp)),
             '<image width="%d" height="%d" xlink:href="data:image/png;base64,%s"/>'
             % (w, h, base64.b64encode(png).decode()),
             '</g>']
    grid_labels = []
    if grid:                                             # the lines above the terrain, under the network
        grid_lines, grid_labels = grid_layers(size, mpp, x_top, y_left, grid)
        parts += grid_lines
    parts += under                                       # coverage circles under the network
    for fam, label in (("road", "Roads"), ("rail", "Rails")):     # rails last, so they draw on top
        parts.append(layer(fam + "s", label, ' transform="scale(%g)"' % (1.0 / mpp)))
        for t, paths in sorted(groups[fam].items()):         # a sublayer per street or track type
            parts.append(layer("%s-%s" % (fam, safe_id(t)), "%s: %s" % (label, t),
                               ' data-type=%s fill="none" stroke="%s" stroke-linecap="round" stroke-linejoin="round"'
                               % (quoteattr(t), ROAD_HEX if fam == "road" else RAIL_HEX)))
            parts += paths
            parts.append("</g>")
        parts.append("</g>")
    parts += over                                        # depot footprints over the network
    parts += overlay                                     # edge labels and vehicles over the network
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
    ap.add_argument("--label", action="append", default=[], metavar="A>B[=TEXT]",
                    help="SVG only: label the edge with end nodes A and B (hex ids); repeatable")
    ap.add_argument("--edge-ids", action="store_true", help="with --label, add edge entity ids where known")
    ap.add_argument("--zoom", type=int, default=1, help="SVG only: show the picture this many times larger "
                    "(its width and height, not the viewBox)")
    ap.add_argument("--vehicles", action="store_true", help="SVG only: draw the vehicle model instances")
    ap.add_argument("--name", action="append", default=[], metavar="SLOT=TEXT",
                    help="rename one vehicle instance in the picture (repeatable)")
    ap.add_argument("--depots", action="store_true", help="SVG only: draw the road maintenance buildings, road depots "
                    "and tram depots (ground faces from the install)")
    ap.add_argument("--coverage", action="store_true", help="SVG only: draw their maintenance coverage circles")
    ap.add_argument("--stream", action="store_true")
    ap.add_argument("--force-size", action="store_true")
    args = ap.parse_args()
    if args.mpp not in (1, 2) and (args.mpp < 4 or args.mpp % 4):
        ap.error("--mpp must be 1, 2 or a multiple of 4 (the heightmap spacing)")
    if (args.label or args.vehicles or args.depots or args.coverage) and args.png:
        ap.error("--label, --vehicles, --depots and --coverage only work with the SVG")
    labels = {}
    for item in args.label:
        pair, _, text = item.partition("=")
        try:
            a, b = (int(v, 16) for v in pair.split(">"))
        except ValueError:
            ap.error("--label wants A>B[=TEXT] with hex node ids, not %r" % item)
        labels[frozenset((a, b))] = text or None
    if args.vehicles and not args.crop:
        ap.error("--vehicles needs --crop")
    try:
        names = {int(k): v for k, v in (n.split("=", 1) for n in args.name)}
    except ValueError:
        ap.error("--name wants SLOT=TEXT, with a number for the slot")
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
    depot_specs = read_depot_specs(content) if args.depots or args.coverage else {}
    if (args.depots or args.coverage) and not depot_specs:
        print("no install found (--game DIR): no depot layers drawn")
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
            x_top, y_left = map_w / 2, map_h / 2
            if crop:
                rows, (x_top, y_left) = crop_grid(rows, tx, ty, *crop)
            if fine > 1:
                rows = upsample(rows, fine)
            img, size = render(rows, step, off_z, unit, water, args.mpp)
            roads = rails = 0
            edges = [] if args.no_network else read_edges(data)
            if crop:                                  # only the edges that touch the picture
                x_bot, y_right = x_top - size[1] * args.mpp, y_left - size[0] * args.mpp
                edges = [e for e in edges
                         if max(e["p0"][0], e["p1"][0]) >= x_bot and min(e["p0"][0], e["p1"][0]) <= x_top
                         and max(e["p0"][1], e["p1"][1]) >= y_right and min(e["p0"][1], e["p1"][1]) <= y_left]
            vehicles = []
            if args.vehicles and crop:
                vehicles = [v for v in read_instances(data)
                            if x_bot <= v["x"] <= x_top and y_right <= v["y"] <= y_left]
            depot_rows = []
            if depot_specs:
                px_bot, px_right = x_top - size[1] * args.mpp, y_left - size[0] * args.mpp
                for i in read_instances(data, ("depots/road/",)):
                    spec = next((depot_specs[k[0]] for k in DEPOT_KINDS if k[3] == i["model"] and k[0] in depot_specs), None)
                    if not spec:
                        continue
                    r = spec["radius"] if args.coverage else 40       # the circle or the footprint may reach the picture
                    if px_bot - r <= i["x"] <= x_top + r and px_right - r <= i["y"] <= y_left + r:
                        depot_rows.append(i)
            if args.edge_ids and labels:
                edge_ids(edges, read_strips(data))
            if not args.png:
                roads = sum(e["family"] != "track" for e in edges)
                rails = len(edges) - roads
            elif edges:
                roads, rails = draw_network(img, size, x_top, y_left, args.mpp, edges, lanes)
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
            meta = svg_metadata(size, args.mpp, x_top, y_left, (map_w, map_h), crop, args.grid,
                                os.path.basename(path))
            overlay, unmatched = overlay_layers(size, args.mpp, x_top, y_left, edges, vehicles, labels, names)
            for key in unmatched:
                print("no edge between %s in the picture" % " and ".join("%x" % n for n in sorted(key)))
            under, over = depot_layers(args.mpp, x_top, y_left, depot_rows, depot_specs, args.depots, args.coverage)
            open(dest, "w").write(svg_document(png, size, args.mpp, x_top, y_left, edges, lanes, args.grid, meta,
                                               overlay, args.zoom, under, over))
            for i in depot_rows:
                print("depot slot %-6d %-22s x %8.1f y %8.1f facing %5.2f %5.2f"
                      % (i["slot"], short_model(i["model"]), i["x"], i["y"], i["fx"], i["fy"]))
            for v in vehicles:
                print("vehicle slot %-6d %-28s x %8.1f y %8.1f facing %5.2f %5.2f"
                      % (v["slot"], short_model(v["model"]), v["x"], v["y"], v["fx"], v["fy"]))
        else:
            open(dest, "wb").write(png)
        print("%s  %d x %d px, %d m/px, map %d x %d m%s, %d road and %d rail edges%s"
              % (dest, size[0], size[1], args.mpp, map_w, map_h, ", cropped" if crop else "", roads, rails,
                 ", %d vehicles" % len(vehicles) if args.vehicles else ""))


if __name__ == "__main__":
    main()
