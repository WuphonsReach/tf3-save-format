#!/usr/bin/env python3
"""Draw a save's terrain as an SVG, with its roads and rails on top.

Usage: terrain_map.py OUT_DIR SAVE.sav [...] [--mpp M] [--crop X,Y,R] [--grid N] [--grid-lines auto|none|dots|faint] [--png | --raster]
       [--contour M] [--index N] [--no-bands] [--tolerance M]
       [--rose WHERE] [--rose-size M] [--game DIR] [--no-network] [--keep-dead] [--depots] [--stations] [--coverage] [--industries] [--industry-size M] [--stream]

Read only: no save is written. The picture goes to OUT_DIR/<save name>-terrain.svg and the script
prints its size, the metres per pixel and the edge counts. The SVG holds the terrain as vector shapes (coloured
height bands, water, height lines) and the roads and rails as vector paths on top; `--raster` draws the terrain as a
shaded embedded PNG instead. Every layer is a group with
`class="layer"`, its id repeated in `data-layer` and Inkscape's layer attributes, so a page script can list
them with `g.layer` and toggle `display`. Layers, bottom to top: `terrain`, `grid`, `roads` and `rails` (each a
parent with one sublayer per street or track type, `road-TYPE` / `rail-TYPE`, holding one `<path>` per edge with
`data-a` and `data-b` (the end node ids in hex), class `road` or `rail` plus the type name, and `data-edge` where
the strip table gave the edge's entity id), `vehicles` (a sublayer per class, `vehicles-train` (wagons included),
`-tram`, `-truck`, `-bus`, `-car`, `-ship`, ...; each vehicle one `<g class="vehicle CLASS" id="vehicle-SLOT">` with
`data-slot`, `data-model`, `data-class`, `data-x`, `data-y`, holding its shape and name), `labels` (`edge-labels`:
one `<g class="edge-label" data-a data-b>` each; `nodes`: one `<g class="node" data-x data-y data-edges>` per
end node), `maintenance-buildings`, `road-depots`, `tram-depots`, `rail-maintenance-buildings`, `rail-depots`, `ship-maintenance-buildings`, `ship-depots` and `boathouses` (`--depots`), `stations` and `stations-street` (`--stations`, a sublayer per kind), `coverage` (`--coverage`), `industries` (`--industries`) and
`grid-labels`. The grid layers ignore the pointer. The colours and widths are also set on the
groups and paths, since Krita ignores the style sheet. The root's size and `viewBox` are the terrain image's pixels (so an editor such as Krita opens
it at that size, taking 96 PPI); each layer scales by 1 / (metres per pixel), so inside a layer
the units are map metres with the image's top-left corner at 0, 0. The line width is in metres too (the template's real
width, `--game`), so the lines scale with the terrain in every viewer; a width that stays fixed on screen
(`vector-effect: non-scaling-stroke`) turned short edges into blobs in VS Code's preview.
A `<metadata>` element
(namespace `urn:tf3-save-format:terrain-map:1`, one `view` element with attributes) records the
save's file name, the map size, the metres per pixel, the map point at the picture's top-left
corner and the x and y range the picture covers, which way north is drawn (`north`: `game` or `sun`, and a sentence
saying which way is up, since a compass word such as "north building" points differently in the two), the crop (X, Y, R) if any and the grid step if `--grid` gave one,
and which script made it: `generator`, `generator-commit` (the last commit that changed a `tools/*.py`, with `-dirty` added if one has
uncommitted changes, as in `script_commits.py`) and `generated-utc` (the time of the run, ISO 8601, to the second).
A setting left at its default (vector terrain, contour 20, index 5, bands, the default grid, industries, `--grid-lines auto`) is not
recorded; only a setting changed from it is (`terrain="raster"`, `contour-step`, `index-every`, `tolerance`, `bands="false"`, `grid="off"`,
`industries="off"`, `grid-lines`).
The terrain colours are a plain
height ramp (water below the save's `waterLevel` in blue; hill shading in the raster picture only); they are not the
game's own palette.

--mpp M      metres per pixel of the picture: 1 or 2, or a multiple of 4 (default 8 for the vector terrain, 4 on a
             crop and with --raster or --png; 4 is the heightmap's own spacing). Larger values keep every (M / 4)th
             grid point. 1 and 2 need --crop; they only scale the picture and the line widths for the vector terrain,
             which is cut from the 4 m grid (a vector terrain over 16 million grid points is refused unless --mpp is raised or
             --force-size is given), and interpolate the raster terrain between grid points (no new height detail).
             A raster picture over 64 million pixels (a 4 m map of 32 x 32 km, or the 20 x 41 km
             Giant map at 4 m, 52 million) is refused unless --mpp is raised or --force-size is
             given. A 52 million pixel map took 42 s and 1.3 GB, and its SVG was 81 MB.
--crop X,Y,R draw only the square of half-width R metres around map point (X, Y), for a close
             look at a station or a junction. X and Y are the map's own coordinates, not the
             picture's.
(default) the terrain is vector (terrain_vector.py): the `terrain` layer holds sublayers `land` (a plain
             rectangle in the lowest band's colour), `bands` (one `<path class="band" data-height>` for each `--contour` metres of
             height above the water, filled with the height ramp's colour and covering all ground from there up, so the
             higher bands paint over the lower), `water` (one even-odd path of rings, the shore stroked: lakes, sea and
             rivers are one shape, since the game carves them below the water level) and `contours` (`contours-minor` and
             `contours-index`, one `<path class="contour" data-height>` per level, the height in metres above the water).
             No hill shading, so the file is hundreds of kilobytes where the raster one is megabytes (the 20 x 41 km
             Giant map: 0.6 MB without roads, 81 MB raster). The metadata gains `contour-step`,
             `index-every`, `tolerance` and `bands="false"` only when set away from their defaults. `--contour M` is the metres between lines and bands (default 20),
             `--index N` makes every Nth line heavier (default 5), `--no-bands` leaves the fills out, `--tolerance M`
             thins the lines (default 0.4 x `--mpp`). The height lines are half `--mpp` wide, in metres.
--raster     (SVG only) draw the terrain as the shaded embedded PNG instead (height ramp, hill shading, water), as before
             the vector terrain existed; the output name ends `-terrain-raster.svg` and the metadata says `terrain="raster"` (a vector picture has no `terrain` attribute).
--png        write one flat PNG instead of the SVG, with the lines drawn into the pixels about 4 m
             wide (at least one pixel). The PNG carries the SVG's view record (below) as an `iTXt` chunk `tf3map:view`, a UTF-8
             JSON object with the same names, so a picture says which way north is drawn (`north=game` or `sun`) without its command line.
(default grid) with no `--grid`, the SVG gets major marks only: a large cross where two grid lines meet, a line of dots along
             each, and labels, at a step of a third of the picture's shorter side rounded down to 1, 2 or 5 times a power of ten (a
             whole map: at least 1000 m, so Tiny and Small 1 km, Medium and Large 2 km, Giant 5 km; a `--crop` has no minimum). No minor
             marks. `--no-grid` leaves the grid out; a flat `--png` has none.
--grid N     (SVG only) add minor marks as well, for fine work: a `grid` layer with a small cross where the lines at every multiple of N metres of map x
             and y would meet (a larger one where two 1000 m lines meet), and a line of dots at each multiple of 1000, labelled `y 4500` along the top (the
             lines that run up the picture) and `x -3000` along the left (the lines that run across it), so a place
             seen in the picture can be turned into the coordinates `--crop` wants. The map's centre is 0, 0.
             The grid is violet, a colour no road, rail or terrain uses, and the crosses keep it from running along
             the roads. Sublayers `grid-minor` (the crosses) and `grid-major`; the grid is one layer under the roads
             and the labels another over everything.
--grid-lines auto|none|dots|faint   with --grid: `auto` (default) draws the crosses and the dotted 1000 m lines, but crosses only on a
             picture of 1 m per pixel or finer, where a dot is a speck; `none` draws crosses only; `dots` and `faint` also draw the minor
             lines between the crosses, `dots` (a round dot every
             `--grid-dot-step` metres, default 25, at least 10 pixels apart and rounded so a whole number fit between two crosses;
             a small cross's arm is a sixth of the gap, a larger cross's 0.4 of it; the 1000 m lines have twice as many dots; the 1000 m lines are
             always dots unless `none` or an `auto` close-up, darker than the minor ones; every dot and small cross arm is one pixel wide, a large cross's arm 1.5) or `faint` (a thin
             solid line).
--game DIR   the game's install folder. A road or track is drawn as wide as its template's profile (the sum of
             its lanes' `width`, footpaths and shoulders included: a small town street 16 m, a medium one 24 m, a
             track 4 m), read from the install's street and track templates when the script runs (nothing is copied
             into the tool or the picture). Without an install, or for a type the install lacks (a mod's), a road is
             16 m and a track 4 m. Default: the usual Steam folders.
--rose WHERE (SVG only) a `compass` layer, the top one: a white circle with a black outline and a black compass rose (the
             shape of tools/icons/compass_rose.svg: north an arrow, E, S and W on shorter arms, the letters upright). The arms point
             where north and east lie in the picture, so under `--north sun` north is left. WHERE is `lower-right` (the default),
             `lower-left`, `upper-left`, `upper-right`, `off`, or `X,Y` in map metres for the circle's centre.
--rose-size M the rose circle's diameter in metres (default 250, but at most an eighth of the picture's short side, so a
             close crop is not covered).
--min-width M (SVG only) draw no road or rail narrower than M metres (default 0, the real widths). A picture of the
             whole map shows a 4 m track as a hairline; `--min-width 12` keeps it visible there.
--no-network leave the roads and rails out.
--keep-dead  draw the edges of deleted towns and roads too. By default an edge with an end node in the save's free-id
             list is left out (docs/town-leftovers.md): the table keeps a deleted town's roads, and the list catches most
             of them (not a town whose ids a later road took). The script prints how many it dropped; if the list is not
             found it says so and draws every edge.
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
--depots     (SVG only) add eight layers, `maintenance-buildings` (the road maintenance building, `road_maint_station`),
             `road-depots`, `tram-depots`, `rail-maintenance-buildings`, `rail-depots`, `ship-maintenance-buildings`, `ship-depots` and `boathouses` (the Boathouse
             mod's `ingo_bootsschuppen`): each building's ground face as a rectangle or polygon, one colour per carrier
             (road orange, tram purple, rail teal, ship pink; provisional), with a black outline, its origin as a white dot and a red line along the
             model's x axis, one `<g class="depot KIND" id="depot-SLOT" data-slot data-model data-x data-y data-pool
             data-radius data-modes>` each. The rectangle is the first `ground_face` of the building's script in the
             install (`base/content/depots/road.zip`), placed from the instance's origin and facing as in docs/models.md;
             nothing of it is copied into the tool, so without an install no building is drawn. A road depot's second
             instance (`road_depot_sm`, likewise the rail depot's `rail_depot_sm`) is left out. The boathouse's script is read from the mod's folder (`--mods DIR`, default the
             usual mod.io places) and it has no ground face, so only its origin dot and facing line are drawn; the free
             decorative Boathouse asset uses the same model and cannot be told apart by it. Reads the whole stream; no `--crop` needed.
--stations   (SVG only) add a `stations` layer for the platforms and buildings of water, rail and street (bus and tram) stations, a
             sublayer per group: `station-water-decks` (wood brown) and `station-water-buildings` (darker brown),
             `station-rail-platforms` (grey) and `station-rail-buildings` (dark grey), `station-street-platforms` (light grey;
             the modular station's platform tiles and the small stops) and `station-street-buildings` (grey); all colours
             provisional. The street groups, with the border below, are in a `stations-street` layer above the roads, so the
             border hides the ends of a station's own road lanes. Each placed piece is the box of its model's `boundingInfo`, placed from the instance's origin and facing as
             the depots are (docs/models.md); a deck piece, rail building or other piece with thin `_con_` and `_end_` edge pieces is
             its cell, the box that holds those too (they are not drawn themselves). One
             `<g class="station-piece" data-slot data-model data-x data-y>` each, and in each sublayer `station-outer`, the group's outer
             edge at an industry's outline width (1.5 m), with no line where two boxes touch. A bus, tram or cargo (modular) station also gets a `station-street-ground` sublayer (an opaque light grey fill) and a
             `station-street-borders` sublayer (the black border, 1.5 m): both are the outline of the union of its platform tiles and
             centre, path and entrance pieces, grown by 3 m and shrunk again so a gap of up to 6 m between pieces leaves no line inside
             (`STREET_BORDER`, `STREET_BORDER_CLOSE`). The border is a little under the game's own line, which also takes in the road
             loop round the platforms. A `station-landings` sublayer stamps an
             anchor (tools/icons/anchor_small.svg (11 m) or anchor_large.svg (24 m), very dark grey, no disc, moved out from the nearest deck edge so it does not overlap the outline and turned so its ring points at the deck; the small icon's own 35 degree tilt is taken out) on each landing marker, the
             `tn_small_pier_passenger*` models small and the `tn_medium_pier_passenger*` ones large. The boxes come from
             `stations/*.zip` in the install at run time and are never stored, so without an install nothing is drawn. Railings, roofs,
             lamps, paths, entrances and the freight terminals' add-ons are left out; the pieces are listed in docs/station-pieces.md.
             Reads the whole stream; no `--crop` needed.
--coverage   (SVG only) add a `coverage` layer under the roads, a sublayer per building kind
             (`coverage-` plus each layer id above) holding one dashed circle
             per building, centred on its origin, with the `catchmentArea` radius of its script (a maintenance building
             600 m, a depot 400 m: a default the script lets a caller change, which no save was checked for). The pool
             and the transport modes in `data-pool` and `data-modes` are the script's: a road depot
             covers buses and trucks, a tram depot trams, the maintenance building all three; ship depot 1000 m, ship
             maintenance building 1400 m, boathouse 600 m, rail depot and rail maintenance building 800 m. Aircraft maintenance is not drawn. Needs the install like `--depots`.
--industries (SVG only, the default; `--no-industries` leaves it out) add an `industries` layer: a footprint sublayer
             (`industry-footprints`) and a sublayer per industry key (`industry-KEY`), each industry a badge: a white
             disc with a grey border and the key's icon from tools/icons/industries/ in dark grey. The footprint is the
             industry's `ground_face` polygon from its script (`<key>/<key>.script.lua` in the install's `industries/<key>.zip`,
             read when the script runs and never stored; needs the install like `--depots`), placed from the origin and facing
             of the industry's main model (the one `industry_compass.py` uses), drawn under the badges with a dark purple
             outline and a translucent light purple fill, as the game's Towns layer paints an industry. A badge with a
             footprint is 0.4 of the polygon's shorter side across (40 to 93 m for the base game's land industries) and sits
             on the polygon's area centroid, or on the origin when the centroid falls outside the polygon; the icon, the border
             and the margin scale with it. The land industries declare a footprint; the fishing grounds and sand excavator
             get one measured off the game's Towns layer (`MEASURED_FACES`, good to about 2 m); the oil platform (the game
             tints its meshes and draws no outline) gets a stand-in for the tinted deck (a box of its `oil_platform_sm` model's size
             with the helipad's octagon and the big crane's boom, which show which way it faces) and a circle on each docking
             station (`MEASURED_DISCS`); a mod's
             industry gets a 64 m badge on the origin. `--industry-size M` sets every badge's diameter
             instead. On a whole-map picture a badge is a few pixels, so zoom
             in. Each badge is a `<g class="industry" data-slot data-key data-model data-x data-y data-diameter>` (data-x and
             data-y are the origin), each footprint a `<polygon class="industry-footprint" data-slot data-key>`; the icons are
             `<symbol>`s in the layer's `<defs>`. Drawn upright whatever `--north` says. Reads the whole stream; no `--crop` needed.
--stream     the files are decompressed streams, not saves.

Layout read (docs/terrain.md): the terrain record gives the map in 256 m tiles and the height
scale; the heightmap is one `vec<u16>` of 65 x 65 per tile, tile `ty * tiles_x + tx`. Grid point
(c, r) of the stitched grid is at x = -width / 2 + 4c, y = -height / 2 + 4r. The picture is turned
so that north is up and east is right, and `--north` says which way north is (docs/compass.md). `game` (the default) is the game's own: image up is +y and image right is +x,
the grid as stored with its rows running up, as the compass words in the game's names have it (docs/compass.md).
`sun` is the one the sun's path gives: image up is +x and image right is -y, the grid turned a quarter
turn anticlockwise, so a grid row is a picture column and the picture's width is the map's y extent.

The roads and rails are the street-edge table (docs/road-network.md, street_edges.py), straight
chords between the end positions: roads dark grey, rails red. Bridges and tunnels
are not told apart from the rest. A deleted road can stay in the table for one save.
"""
import argparse
import base64
import bisect
import collections
import datetime
import glob
import json
import math
import os
import re
import struct
import sys
import zipfile
import zlib
from array import array
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from save_preview import png_bytes  # noqa: E402
from model_instances import read_instances, read_model_table, short_model  # noqa: E402
from industry_compass import main_models  # noqa: E402
from street_edges import bezier_point, edge_bezier, edge_ids, edge_is_curved, read_edges, read_free_ids, read_strips  # noqa: E402
from terrain_vector import level_rings, path_data, simplify, split_at_border  # noqa: E402
from tf3save import decompress  # noqa: E402

RESOLUTION = bytes.fromhex("0000804000008040cdcc4c3d")      # 4.0, 4.0, 0.05
TILE_POINTS = 65 * 65
GRID_STEP = 4.0                                              # metres per grid step
MAX_PIXELS = 64_000_000
MAX_VECTOR_POINTS = 16_000_000                               # the vector terrain holds the grid as Python lists

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
_LANES = re.compile(r"laneConfigs\s*=\s*\{(.*?)\n\t\t\},", re.S)
_WIDTH = re.compile(r"\bwidth\s*=\s*([\d.]+)")
DEFAULT_WIDTH = {"street": 16.0, "track": 4.0}      # a template the install lacks (a mod's, or no install): a small town street, a track


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


def read_profile_widths(content):
    """{template: width in metres} for every street and track template in the install's
    `infrastructure/street.zip` and `track.zip`, read when the script runs (nothing is stored). The width is
    the sum of the `width` of every entry of the template's `laneConfigs` list: carriageway lanes, footpaths and the
    lanes with no mode (a highway's shoulders and median), the strip the game builds the road on. A small town street
    is 16 m (5 + 5 and a 3 m footpath each side), a track 4 m."""
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
            widths = [float(w) for w in _WIDTH.findall(m.group(1))] if m else []
            if widths:
                out[member[:-len(".street_template.lua")]] = sum(widths)
    return out


# maintenance buildings and depots: (layer id, label, archive in the install's depots folder, script path, model path,
# colour). An archive of None is a mod's building: the script is read from the mod's folder (`find_mod_script`) and
# its ground face is not drawn (the script's ground faces are a 4 m patch beside the model, not its footprint).
DEPOT_KINDS = (
    ("maintenance-buildings", "Road maintenance buildings", "road.zip", "road/road_maint_station.script.lua",
     "depots/road/road_maint_station/road_maint_station.mdl", "#f5a300"),
    ("road-depots", "Road depots", "road.zip", "road/road_depot/road_depot.script.lua",
     "depots/road/road_depot/road_depot.mdl", "#f5a300"),
    ("tram-depots", "Tram depots", "road.zip", "road/tram_depot/tram_depot.script.lua",
     "depots/road/tram_depot/tram_depot.mdl", "#8e5ea2"),
    ("rail-maintenance-buildings", "Rail maintenance buildings", "rail.zip", "rail/rail_maint_station.script.lua",
     "depots/rail/rail_maint_station/rail_maint_station.mdl", "#2a9d8f"),
    ("rail-depots", "Rail depots", "rail.zip", "rail/rail_depot.script.lua",
     "depots/rail/rail_depot.mdl", "#2a9d8f"),
    ("ship-maintenance-buildings", "Ship maintenance buildings", "water.zip", "water/water_maint_station.script.lua",
     "depots/water/water_maint_station/water_maint_station.mdl", "#d6336c"),
    ("ship-depots", "Ship depots", "water.zip", "water/water_depot.script.lua",
     "depots/water/water_depot.mdl", "#d6336c"),
    ("boathouses", "Boathouses (Boathouse mod)", None,
     "content/assets/ingo_bootsschuppen/ingo_bootsschuppen_maint.script.lua",
     "assets/ingo_bootsschuppen/ingo_bootsschuppen.mdl", "#d6336c"),
)
MOD_DIRS = ("~/snap/steam/common/mod.io/common/10640/mods", "~/.local/share/mod.io/common/10640/mods")
DEPOT_PREFIXES = ("depots/", "assets/ingo_bootsschuppen/")
# station pieces (docs/station-pieces.md): each kind is a group of model instances drawn as boxes, (layer id, label, names, joined to
# edge pieces, fill, opacity of the group). A name is the model's path under `stations/` without `.mdl`; its box is the `boundingInfo`
# of that model's `.mdl` in the install's `stations/<first folder>.zip`, read when the script runs and never stored. A piece "joined to
# its edge pieces" is drawn as its cell, the box that holds its own and those of the thin `_con_` and `_end_` pieces beside it
# (railings and borders, which fill the gap to the next piece), so neighbours abut and the edge pieces are not drawn themselves.
# Water stations are brown (decks wood, buildings darker); rail grey (platforms mid, buildings dark); street (bus and tram) lighter
# grey. All are provisional. Left out: railings, roofs, clocks, lamps, paths and entrances, and the freight terminals' add-on models.
STATION_PREFIXES = ("stations/water/", "stations/rail/", "stations/street/")
_STREET_STATION = "street/modular_street_station/models/era_a/"
STATION_KINDS = (
    ("station-water-decks", "Water stations: docks and platforms",
     ("water/models/dock_100_25", "water/models/dock_50_12", "water/models/platform_100", "water/models/platform_25"),
     True, "#a0622d", 0.65),
    ("station-rail-platforms", "Rail stations: platforms",
     tuple("rail/era_a/" + n for n in ("perron_5", "perron_10", "perron_5_underpass", "perron_5_head", "perron_5_head_con",
                                       "station_3_perron_head", "station_3_perron_side", "station_3_perron_side_main")),
     False, "#8c8c8c", 0.85),
    ("station-street-platforms", "Street stations: platforms and stops",
     tuple(_STREET_STATION + "%spltfrm_%s_%s" % (c, side, part) for c in ("", "cargo_") for side in "lr"
           for part in ("rep",))
     + ("street/small_stops/small_old", "street/small_stops/small_mid"),
     False, "#c8c8c8", 0.9),
    ("station-water-buildings", "Water stations: main buildings", ("water/models/main_building_s0", "water/models/main_building_s2"),
     False, "#5a3512", 0.85),
    ("station-rail-buildings", "Rail stations: buildings",
     tuple("rail/%s/station_%d%s" % (folder, n, main) for folder in ("era_a", "cargo") for n in (1, 2, 3) for main in ("", "_main")),
     True, "#4a4a4a", 0.9),
    ("station-street-buildings", "Street stations: buildings", (_STREET_STATION.replace("era_a/", "sidebuildings/") + "streetstation_sidebuilding_era_a_s2",),
     False, "#9a9a9a", 0.9),
)
# The border of a bus, tram or cargo station (the black line the game draws round it): drawn as the outer edge of the boxes of the
# modular station's platform tiles and its centre, path and entrance pieces, which fill the polygon the game's script lays out.
# The thin edge strips, the 5 m ramp ends (`_spcl`), the path extensions and the zero-size markers are not part of it.
STREET_BORDER = re.compile(r"^street/modular_street_station/models/era_[abc]/"
                           r"((cargo_)?pltfrm_[lr]_rep|cargo_path_rep|(cntr|entr|path)_(?!.*(spcl|pers)).*)\.mdl$")
STREET_BORDER_FILL, STREET_BORDER_OPACITY = "#e3e3e3", 1.0
STREET_BORDER_CLOSE = 3.0                                    # metres: gaps up to twice this between pieces are closed in the border
# Landings: a `tn_*_pier_passenger*` model is the marker of one landing a ship docks at (docs/station-pieces.md), drawn as an anchor icon
# from tools/icons/, small or large by the model, upright, centred on the marker. (model name under `stations/water/models/`, size)
LANDING_MODELS = {"tn_small_pier_passenger": "small", "tn_small_pier_passenger_l": "small", "tn_small_pier_passenger_r": "small",
                  "tn_small_pier_passenger_dual": "small", "tn_small_pier_passenger_dual_l": "small",
                  "tn_small_pier_passenger_dual_r": "small", "tn_medium_pier_passenger": "large", "tn_medium_pier_passenger_dual": "large"}
LANDING_SIZE = {"small": 11.0, "large": 24.0}                # metres across the icon
LANDING_CLEARANCE = {"small": 0.35, "large": 0.5}            # of the icon's size, from the deck edge to its centre (the small icon's glyph is smaller than its box)
LANDING_TILT = {"small": 35.0, "large": 0.0}                  # degrees the icon file turns its anchor, taken back out so it starts vertical
LANDING_INK = "#1f1f1f"                                      # very dark grey, a plain stamp with no disc
STATION_OUTLINE = 1.5                                        # metres at 2 m per pixel and finer: an industry's outline width
_BBOX = re.compile(r"bbM(ax|in)\s*=\s*\{\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)")
_FACE = re.compile(r'\["ground_face"\]\s*=\s*\{\s*\{((?:\s*\{[^}]*\},?)+)')
_POINT = re.compile(r"\{\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)")
_RADIUS = re.compile(r"catchmentArea\s*=\s*\{\s*radius\s*=\s*(?:captureParams\.radius or )?(\d+)")
_POOL = re.compile(r"maintenancePool\s*=\s*(\d+)")
_DEPOT_MODES = re.compile(r"transportModes\s*=\s*\{([^}]*)\}")


def read_station_boxes(content):
    """{model path: (x0, y0, x1, y1)} for the pieces of `STATION_KINDS`: the x and y range of the `boundingInfo` of each model's `.mdl`
    in the install's `stations/*.zip` (`content` is the `infrastructure` folder `find_content` returns), in the model's own axes; for a
    piece joined to its edge pieces the range holds theirs too (the `NAME_con...` and `NAME_end...` files beside it). A piece whose file is
    missing is left out; without an install the result is empty. Nothing is stored."""
    out = {}
    if not content:
        return out
    zips = {}
    for _lid, _label, names, edges, _colour, _opacity in STATION_KINDS:
        for name in names:
            folder, _, base = name.rpartition("/")
            archive = name.split("/", 1)[0]
            if archive not in zips:
                try:
                    zf = zipfile.ZipFile(os.path.join(os.path.dirname(content), "stations", archive + ".zip"))
                    zips[archive] = (zf, set(zf.namelist()))
                except (OSError, zipfile.BadZipFile):
                    zips[archive] = None
            if not zips[archive]:
                continue
            zf, members = zips[archive]
            files = [name + ".mdl"]
            if edges:
                pat = re.compile(r"^%s/%s_(con|end)[^/]*\.mdl$" % (re.escape(folder), re.escape(base)))
                files += sorted(m for m in members if pat.match(m))
            parts = []
            for f in files:
                if f not in members:
                    continue
                box = {k: (float(a), float(b)) for k, a, b in _BBOX.findall(zf.read(f).decode("utf-8", "replace"))}
                if "ax" in box and "in" in box:
                    parts.append((box["in"][0], box["in"][1], box["ax"][0], box["ax"][1]))
            if parts:
                out["stations/%s.mdl" % name] = (min(q[0] for q in parts), min(q[1] for q in parts),
                                                 max(q[2] for q in parts), max(q[3] for q in parts))
    if "street" in zips and zips["street"]:
        zf, members = zips["street"]
        for m in sorted(members):
            if STREET_BORDER.match(m):
                box = {k: (float(a), float(b)) for k, a, b in _BBOX.findall(zf.read(m).decode("utf-8", "replace"))}
                if "ax" in box and "in" in box and box["ax"] != box["in"]:
                    out.setdefault("stations/" + m, (box["in"][0], box["in"][1], box["ax"][0], box["ax"][1]))
    return out


def find_mod_script(rel, mods_dir=None):
    """The text of the script at `content/...` path `rel` inside any mod folder of `mods_dir` (or the usual
    mod.io places), or None."""
    for d in ([mods_dir] if mods_dir else MOD_DIRS):
        for mod in sorted(glob.glob(os.path.join(os.path.expanduser(d), "*", rel))):
            try:
                with open(mod, encoding="utf-8", errors="replace") as f:
                    return f.read()
            except OSError:
                pass
    return None


def read_depot_specs(content, mods_dir=None):
    """{layer id: {"face": [(a, b) ...], "radius", "pool", "modes"}} for every kind in `DEPOT_KINDS`, read when the
    script runs from the install's `depots/` archives (`content` is the `infrastructure` folder `find_content`
    returns) or, for a mod's building, from the mod's folder: the first `ground_face` rectangle of the building's
    script in its own axes (none for a mod's), the `catchmentArea` radius, the `maintenancePool` and the transport
    modes. A kind whose script or fields are missing is left out. Nothing is stored."""
    out = {}
    zips = {}
    for lid, _label, archive, script, _model, _colour in DEPOT_KINDS:
        if archive:
            if not content:
                continue
            if archive not in zips:
                try:
                    zips[archive] = zipfile.ZipFile(os.path.join(os.path.dirname(content), "depots", archive))
                except (OSError, zipfile.BadZipFile):
                    zips[archive] = None
            if not zips[archive]:
                continue
            try:
                text = zips[archive].read(script).decode("utf-8", "replace")
            except KeyError:
                continue
        else:
            text = find_mod_script(script, mods_dir)
            if text is None:
                continue
        face, radius, pool, modes = _FACE.search(text), _RADIUS.search(text), _POOL.search(text), _DEPOT_MODES.search(text)
        if radius and (face or not archive):
            out[lid] = {"face": [(float(a), float(b)) for a, b in _POINT.findall(face.group(1))] if face else [],
                        "radius": int(radius.group(1)), "pool": int(pool.group(1)) if pool else 0,
                        "modes": ",".join(re.findall(r'"(\w+)"', modes.group(1))) if modes else ""}
    return out


def read_industry_faces(content):
    """{industry key: [(a, b) ...]} for every industry of the install whose script declares a `ground_face`, in the
    industry's own axes (a along the model's x axis): `<key>/<key>.script.lua` in `industries/<key>.zip`, read when the
    script runs (`content` is the `infrastructure` folder `find_content` returns). An industry with no face (the water
    ones keep a `collider` box only; `MEASURED_FACES` stands in for two of them) or no archive is left out. Nothing is stored."""
    out = {}
    if not content:
        return out
    for path in sorted(glob.glob(os.path.join(os.path.dirname(content), "industries", "*.zip"))):
        key = os.path.basename(path)[:-len(".zip")]
        try:
            text = zipfile.ZipFile(path).read("%s/%s.script.lua" % (key, key)).decode("utf-8", "replace")
        except (OSError, KeyError, zipfile.BadZipFile):
            continue
        face = _FACE.search(text)
        if face:
            out[key] = [(float(a), float(b)) for a, b in _POINT.findall(face.group(1))]
    return out


def edge_width(edge, widths, floor=0.0):
    """Stroke width in metres: the template's profile width (`read_profile_widths`), at least `floor`. A template
    with no entry gets `DEFAULT_WIDTH` for its family."""
    w = widths.get(edge["template"]) or DEFAULT_WIDTH["track" if edge["family"] == "track" else "street"]
    return max(w, floor)


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


class Frame:
    """Where the map's x and y fall in the picture. `kind` is `game` (image up is +y, image right is +x) or
    `sun` (image up is +x, image right is -y). (`ax`, `ay`) is the map point at the picture's top-left corner:
    for `game` the smallest x and the largest y, for `sun` the largest x and the largest y. Everything that
    draws takes one of these, so only this class knows which way north is."""

    def __init__(self, kind, ax, ay):
        self.kind, self.ax, self.ay = kind, ax, ay

    @classmethod
    def from_bounds(cls, kind, x_min, x_max, y_max):
        return cls(kind, x_max if kind == "sun" else x_min, y_max)

    def pic(self, x, y):
        """Picture (u, v) in metres from the top-left corner: u to the right, v down."""
        return (self.ay - y, self.ax - x) if self.kind == "sun" else (x - self.ax, self.ay - y)

    def vec(self, dx, dy):
        """A map-space vector as a picture vector."""
        return (-dy, -dx) if self.kind == "sun" else (dx, -dy)

    def box(self, size, mpp):
        """(x_min, x_max, y_min, y_max) of the map the picture shows."""
        w, h = size[0] * mpp, size[1] * mpp
        if self.kind == "sun":
            return self.ax - h, self.ax, self.ay - w, self.ay
        return self.ax, self.ax + w, self.ay - h, self.ay


def crop_grid(rows, tx, ty, cx, cy, radius):
    """The part of the grid within `radius` metres of (cx, cy), and its map bounds (x_min, x_max, y_min, y_max)."""
    w, h = tx * 256, ty * 256
    c0 = max(0, int((cx - radius + w / 2) // GRID_STEP))
    c1 = min(64 * tx, int(-(-(cx + radius + w / 2) // GRID_STEP)))
    r0 = max(0, int((cy - radius + h / 2) // GRID_STEP))
    r1 = min(64 * ty, int(-(-(cy + radius + h / 2) // GRID_STEP)))
    if c1 - c0 < 2 or r1 - r0 < 2:
        raise ValueError("the crop lies outside the map")
    return ([r[c0:c1 + 1] for r in rows[r0:r1 + 1]],
            (-w / 2 + GRID_STEP * c0, -w / 2 + GRID_STEP * c1, -h / 2 + GRID_STEP * r0, -h / 2 + GRID_STEP * r1))


def to_picture(rows, step, kind="game"):
    """The grid in the picture's order, every `step`th point. `game`: picture row j (top first, y falling)
    is grid row `last - j * step`, along it x rises from the first column. `sun`: picture row j (x falling)
    is grid column `last - j * step`, and along it y falls from the grid's last row."""
    if kind == "game":
        return [array("H", r[::step]) for r in rows[::-1][::step]]
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


def render(rows, step, off_z, unit, water, spacing=None, kind="game"):
    """RGB bytes (top row first) and (width, height) of the grid sampled every `step` points,
    turned north up and east right. Hill shading from the north-west, vertical scale doubled."""
    picked = to_picture(rows, step, kind)
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


def draw_network(img, size, fr, mpp, edges, widths):
    """Draw roads, then rails over them. Returns (roads drawn, rails drawn). Picture position
    from `fr.pic` (north up, east right)."""
    w, h = size
    n = {"street": 0, "track": 0}
    for fam, colour in (("street", ROAD), ("track", RAIL)):
        for e in edges:
            if e["family"] != fam and not (fam == "street" and e["family"] is None):
                continue
            c = edge_bezier(e)
            steps = max(1, math.ceil(e["length"] / (8 * mpp))) if edge_is_curved(e) else 1
            pts = [fr.pic(*bezier_point(c, i / steps)) for i in range(steps + 1)]
            for (u0, v0), (u1, v1) in zip(pts, pts[1:]):
                _line(img, w, h, u0 / mpp, v0 / mpp, u1 / mpp, v1 / mpp, colour,
                      max(1, round(edge_width(e, widths) / mpp)))
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


GRID_HEX = "#6b3fa0"                                   # violet: no terrain, road or rail colour is near it
GRID_MIN_DOT_PX = 10                                   # the closest two dots on a dotted line may be, in pixels (a cross is a third to a half of it)


def auto_grid_step(short_side, cropped):
    """The default major grid step in metres: a third of the picture's shorter side (map metres) rounded down to 1, 2 or
    5 times a power of ten. A whole map is never finer than 1000 m, so the smallest maps get a mark every km."""
    third = short_side / 3
    power = 10 ** math.floor(math.log10(third))
    step = max(m * power for m in (1, 2, 5) if m * power <= third)
    return step if cropped else max(step, 1000)


LABEL_EM = 0.62                                              # a grid label's average character width, in font sizes (a safe overestimate)


def grid_layers(size, mpp, fr, step, lines="auto", dot_step=25, major=1000):
    """The grid as two layers, `grid` (the marks) and `grid-labels` (the coordinates, at the top
    and left edges, meant to be drawn last so they sit over the network). The `grid` layer has sublayers
    `grid-minor` (under) and `grid-major` (over). At every multiple of `step` metres in map x and y,
    where two lines would cross, there is a small cross (`grid-minor`, its arm a sixth of the dot step), or a larger one
    (`grid-major`, 0.4 of it, just short of the first dot) where both lines are at a multiple of `major` metres (1000, or `step`
    itself for the default grid, which has no minor marks), so the grid reads as a set of marks that do not run along the roads. The
    lines at multiples of `major` are dotted, twice as close as the minor dots (unless `lines` is `none`, or `auto` on a picture of 1 m per pixel or finer, where
    a dot is a speck and the crosses are enough), a round dot every `dot_step` / 2 metres of map x or y (`dot_step` at least
    `GRID_MIN_DOT_PX` pixels apart, and a whole number of them between two crosses, so
    the step is nudged to `step / n`), as big as a cross's arm is wide (one pixel) and darker than the minor ones. `lines` is `auto` (the default: those dots and the crosses), `none` (crosses only), or adds the minor lines to the 1000 m dots: `dots`
    (the same dots) or `faint` (a thin solid line). The lines that run up the
    picture are labelled along the
    top (`game`: constant x, x rising to the right; `sun`: constant y, y falling to the right) and
    those that run across it along the left (`game`: constant y, falling downwards; `sun`: constant x,
    falling downwards). A label is never moved to keep it legible: a left one that would sit in the top row of labels, and a top
    one that would run off the right edge, are left out. Coordinates inside are metres from the image's top-left corner, like the other layers."""
    w, h = size[0] * mpp, size[1] * mpp
    size_t = max(min(7 * mpp, 0.03 * max(w, h)), min(step * 0.07, 70))   # label size in metres, smaller on a close crop, no bigger for a wide step
    ink = 'fill="none" stroke="%s"' % GRID_HEX
    sw = mpp                                                    # one pixel: the width of a small cross's arm and the diameter of every dot
    mark = '%s stroke-opacity="0.65" stroke-width="%g"' % (ink, sw)
    big_mark = '%s stroke-opacity="0.85" stroke-width="%g"' % (ink, 1.5 * sw)
    text = ('font-family="sans-serif" font-size="%g" fill="#000" stroke="#fff" stroke-width="%g"'
            ' paint-order="stroke"' % (size_t, size_t / 5))
    scale = "scale(%g)" % (1.0 / mpp)
    dot_step = max(dot_step, GRID_MIN_DOT_PX * mpp)
    dot_step = step / max(1, round(step / dot_step))            # a whole number of dots between two crosses
    gap = dot_step / 2                                          # the dots of a 1000 m line are twice as close as the others, so the line reads as a line
    big_arm = 0.8 * gap                                         # a cross where two 1000 m lines meet stops just short of the first dot,
    arm = dot_step / 6                                          # a small cross reaches a sixth of the way to the first dot of a minor line
    x_min, x_max, y_min, y_max = fr.box(size, mpp)
    if fr.kind == "sun":
        up_axis, (lo, hi) = "y", (y_min, y_max)
    else:
        up_axis, (lo, hi) = "x", (x_min, x_max)
    first = -((-int(math.floor(lo))) // step) * step         # the first multiple of step at or above lo
    ups = list(range(first, int(math.floor(hi)) + 1, step))
    if fr.kind == "sun":
        ups.reverse()                                       # y falls to the right
    across_axis, (lo, hi) = ("x", (x_min, x_max)) if fr.kind == "sun" else ("y", (y_min, y_max))
    acrosses = list(range(int(math.floor(hi) // step) * step, int(math.ceil(lo)) - 1, -step))
    # where a line's map coordinate, counted along it from the picture's top or left edge, runs: the dots sit at
    # multiples of dot_step in map metres, so the dots of crossing lines meet at the crosses
    up_start = x_max if fr.kind == "sun" else y_max           # map coordinate at the top edge, falling downwards
    across_start = y_max if fr.kind == "sun" else x_min        # at the left edge, falling (sun) or rising (game) to the right
    across_sign = -1 if fr.kind == "sun" else 1
    up_offset = (-up_start) % dot_step
    across_offset = (-across_start) % dot_step if across_sign < 0 else across_start % dot_step
    up_offset_major = (-up_start) % gap
    across_offset_major = (-across_start) % gap if across_sign < 0 else across_start % gap
    dash = 'stroke-linecap="round" stroke-dasharray="0 %g"' % dot_step
    dots = '%s stroke-opacity="0.65" stroke-width="%g" %s' % (ink, sw, dash)
    big_dots = ('%s stroke-opacity="0.85" stroke-width="%g" stroke-linecap="round" stroke-dasharray="0 %g"'
                % (ink, sw, gap))
    faint = '%s stroke-opacity="0.3" stroke-width="%g"' % (ink, sw)
    style = {"dots": dots, "faint": faint}.get(lines)
    dashed = lines == "dots"
    major_dots = lines != "none" and not (lines == "auto" and mpp <= 1)
    minor = [layer("grid-minor", "Grid minor")]
    majors = [layer("grid-major", "Grid major")]
    labels = [layer("grid-labels", "Grid labels", ' transform="%s" pointer-events="none"' % scale)]
    crosses, big_crosses = [], []
    top_band = size_t * 1.4                                     # the height of the row of x labels along the top edge
    ups_px = [(val, fr.pic(0, val)[0] if up_axis == "y" else fr.pic(val, 0)[0]) for val in ups]
    across_py = [(val, fr.pic(val, 0)[1] if across_axis == "x" else fr.pic(0, val)[1]) for val in acrosses]
    for val, px in ups_px:
        if val % major == 0:
            if major_dots:
                majors.append('<path d="M%g 0V%g" %s stroke-dashoffset="%g"/>' % (px, h, big_dots, up_offset_major))
        elif style:
            extra = ' stroke-dashoffset="%g"' % up_offset if dashed else ""
            minor.append('<path d="M%g 0V%g" %s%s/>' % (px, h, style, extra))
        word = "%s %d" % (up_axis, val)
        if px + size_t * 0.3 + len(word) * LABEL_EM * size_t <= w:   # one that would run off the right edge is left out
            labels.append('<text x="%g" y="%g" %s>%s</text>' % (px + size_t * 0.3, size_t * 1.1, text, word))
    for val, py in across_py:
        if val % major == 0:
            if major_dots:
                majors.append('<path d="M0 %gH%g" %s stroke-dashoffset="%g"/>' % (py, w, big_dots, across_offset_major))
        elif style:
            extra = ' stroke-dashoffset="%g"' % across_offset if dashed else ""
            minor.append('<path d="M0 %gH%g" %s%s/>' % (py, w, style, extra))
        if py - size_t * 1.4 >= top_band:                       # one in the top row of labels is left out, not moved
            labels.append('<text x="%g" y="%g" %s>%s %d</text>' % (size_t * 0.3, py - size_t * 0.3, text, across_axis, val))
    for uv, px in ups_px:
        for av, py in across_py:
            big = uv % major == 0 and av % major == 0
            a = big_arm if big else arm
            (big_crosses if big else crosses).append("M%g %gh%gM%g %gv%g" % (px - a, py, 2 * a, px, py - a, 2 * a))
    if crosses:
        minor.append('<path d="%s" %s/>' % ("".join(crosses), mark))
    if big_crosses:
        majors.append('<path d="%s" %s/>' % ("".join(big_crosses), big_mark))
    group = [layer("grid", "Grid %d m" % step, ' transform="%s" pointer-events="none"' % scale)]
    return group + minor + ["</g>"] + majors + ["</g>", "</g>"], labels + ["</g>"]


META_NS = "urn:tf3-save-format:terrain-map:1"


def generator_attrs():
    """[(name, value)] saying which script run made the picture: the script, the commit of `tools/` it ran from (None
    outside a git checkout, so the attribute is left out) and the UTC time, so a map can be told from one made by an older
    version of the drawing."""
    from script_commits import tools_commit
    return [("generator", "terrain_map.py"), ("generator-commit", tools_commit()),
            ("generated-utc", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))]


def view_attrs(size, mpp, fr, map_size, crop=None, grid=None, source=None, extra=()):
    """[(name, value)] recording where the picture sits on the map, so it can be turned back into map
    coordinates (or redrawn) without the command line that made it. All values are map metres. `x-min`,
    `x-max`, `y-min` and `y-max` are the map the picture spans; `north` (`game` or `sun`) and `orientation` say
    which way is up, and so which way a compass word such as "north building" points in the picture. For `sun`
    the old `x-top` and `y-left` (the map point at the top-left corner) are kept as well."""
    x_min, x_max, y_min, y_max = fr.box(size, mpp)
    orient = ("north-up (game): image up is +y, image right is +x" if fr.kind == "game"
              else "north-up (sun): image up is +x, image right is -y")
    attrs = [("source", source), ("map-width", map_size[0]), ("map-height", map_size[1]),
             ("metres-per-pixel", mpp), ("orientation", orient), ("north", fr.kind),
             ("x-min", "%g" % x_min), ("x-max", "%g" % x_max), ("y-min", "%g" % y_min), ("y-max", "%g" % y_max)]
    if fr.kind == "sun":
        attrs += [("x-top", "%g" % x_max), ("y-left", "%g" % y_max)]
    if crop:
        attrs += [("crop-x", "%g" % crop[0]), ("crop-y", "%g" % crop[1]), ("crop-radius", "%g" % crop[2])]
    if grid:
        attrs.append(("grid-step", grid))
    attrs += list(extra) + generator_attrs()
    return [(k, v) for k, v in attrs if v is not None]


def svg_metadata(*args, **kw):
    """The `view_attrs` as a `<metadata>` element holding one `tf3map:view`."""
    return ('<metadata><tf3map:view xmlns:tf3map="%s" %s/></metadata>'
            % (META_NS, " ".join("%s=%s" % (k, quoteattr(str(v))) for k, v in view_attrs(*args, **kw))))


def png_with_view(png, attrs):
    """`png` with an `iTXt` chunk `tf3map:view` before its pixel data: the view record as one UTF-8 JSON object with the
    SVG `<metadata>`'s attribute names, numbers and `true` / `false` as JSON values. The PNG's counterpart of the SVG's
    `<metadata>`."""
    def typed(v):
        if isinstance(v, str):
            if v in ("true", "false"):
                return v == "true"
            try:
                return int(v) if re.fullmatch(r"-?\d+", v) else float(v) if re.fullmatch(r"-?\d+\.\d*(e-?\d+)?", v) else v
            except ValueError:
                return v
        return v
    text = json.dumps({k: typed(v) for k, v in attrs}, ensure_ascii=False).encode("utf-8")
    body = b"tf3map:view\x00\x00\x00\x00\x00" + text           # keyword, no compression, method 0, no language tag, no translation
    chunk = struct.pack(">I", len(body)) + b"iTXt" + body + struct.pack(">I", zlib.crc32(b"iTXt" + body) & 0xFFFFFFFF)
    cut = png.index(b"IDAT") - 4
    return png[:cut] + chunk + png[cut:]


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


def overlay_layers(size, mpp, fr, edges, vehicles, labels=False, names=None):
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
            bz = edge_bezier(e)
            for (x, y), (xo, yo) in ((bz[0], bz[1]), (bz[3], bz[2])):        # leaving each end along the curve
                ends.setdefault((round(x, 1), round(y, 1)), []).append((c, fr.vec(xo - x, yo - y), "%x>%x" % (e["a"], e["b"])))
        top.append(layer("edge-labels", "Edge labels"))
        for e in picked:
            key = frozenset((e["a"], e["b"]))
            unmatched.discard(key)
            bz = edge_bezier(e)
            (xm, ym), (xn, yn) = bezier_point(bz, 0.5), bezier_point(bz, 0.51)   # the middle of the curve and its direction there
            text = labels[key] or "%x>%x" % (e["a"], e["b"])
            if e.get("e"):
                text += " e%x" % e["e"]
            ex, ey = fr.vec(xn - xm, yn - ym)
            angle = math.degrees(math.atan2(ey, ex))               # the edge in picture axes
            if angle > 90 or angle < -90:                           # keep the text upright
                angle -= 180 if angle > 0 else -180
            top.append('<g class="edge-label" data-a="%x" data-b="%x"><text transform="translate(%.1f %.1f) rotate(%.1f)"'
                       ' y="%g" paint-order="stroke" stroke="%s" stroke-width="%g" stroke-linejoin="round">%s</text></g>'
                       % ((e["a"], e["b"]) + fr.pic(xm, ym) + (angle, lfs * 1.1,
                          tint[key], fs / 4, escape(text))))
        top.append("</g>")
        r = lfs * 0.3
        ring = 'stroke="#000" stroke-width="%g"' % (lfs * 0.08)
        top.append(layer("nodes", "Edge end nodes"))
        for (x, y), parts in ends.items():
            cx, cy = fr.pic(x, y)
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
                px, py = fr.pic(v["x"], v["y"])
                ux, uy = fr.vec(v["fx"], v["fy"])
                angle = math.degrees(math.atan2(uy, ux))                  # the facing in picture axes
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


def _inside(poly, x, y):
    """Whether (x, y) lies in the convex polygon `poly` (a list of points in either winding)."""
    sign = 0
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        c = (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)
        if c:
            if sign and (c > 0) != (sign > 0):
                return False
            sign = 1 if c > 0 else -1
    return True


def _clear_of_edge(pt, clearance, polys, outer, reach=40.0):
    """(`pt` moved away from the nearest stretch of the deck outline (`outer`, a list of polylines; `polys` the deck boxes) until it is
    `clearance` metres from it, on the side that is not deck, and the nearest point of that outline), or (`pt`, None) when no outline
    lies within `reach` metres."""
    best = None
    for run in outer:
        for (x0, y0), (x1, y1) in zip(run, run[1:]):
            dx, dy = x1 - x0, y1 - y0
            n2 = dx * dx + dy * dy
            if not n2:
                continue
            t = max(0.0, min(1.0, ((pt[0] - x0) * dx + (pt[1] - y0) * dy) / n2))
            px, py = x0 + t * dx, y0 + t * dy
            dist = math.hypot(pt[0] - px, pt[1] - py)
            if dist <= reach and (best is None or dist < best[0]):
                n = math.sqrt(n2)
                best = (dist, px, py, -dy / n, dx / n)
    if best is None:
        return pt, None
    _d, px, py, nx, ny = best
    if any(_inside(c, px + 0.5 * nx, py + 0.5 * ny) for c in polys):
        nx, ny = -nx, -ny                                    # the normal that leaves the deck
    return (px + clearance * nx, py + clearance * ny), (px, py)


def _closed_outline(polys, g=STREET_BORDER_CLOSE):
    """Closed loops (lists of points) round the union of the boxes `polys` (four corners each) with every gap up to 2 g metres
    closed, so the thin gaps between a station's pieces leave no line inside: each box is grown by g, the union is taken and shrunk
    by g again, in the frame of the boxes' own axes (a station's pieces share one heading, a quarter turn aside at most), on the
    grid of the boxes' edge coordinates and their multiples of g. Boxes within 2 g of each other are one station."""
    n = len(polys)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    aabb = [(min(q[0] for q in c) - g, max(q[0] for q in c) + g, min(q[1] for q in c) - g, max(q[1] for q in c) + g) for c in polys]
    for a in range(n):
        for b in range(a + 1, n):
            if aabb[a][0] <= aabb[b][1] and aabb[b][0] <= aabb[a][1] and aabb[a][2] <= aabb[b][3] and aabb[b][2] <= aabb[a][3]:
                parent[find(a)] = find(b)
    groups = collections.defaultdict(list)
    for a in range(n):
        groups[find(a)].append(a)
    loops = []
    for members in groups.values():
        c0 = polys[members[0]]
        ang = math.atan2(c0[1][1] - c0[0][1], c0[1][0] - c0[0][0])
        ca, sa = math.cos(-ang), math.sin(-ang)
        rects = []
        for m in members:
            pts = [(q[0] * ca - q[1] * sa, q[0] * sa + q[1] * ca) for q in polys[m]]
            rects.append((min(q[0] for q in pts), max(q[0] for q in pts), min(q[1] for q in pts), max(q[1] for q in pts)))
        axis = [sorted({round(v + k * g, 3) for r in rects for v in (r[idx], r[idx + 1]) for k in (-2, -1, 0, 1, 2)}) for idx in (0, 2)]
        xs, ys = axis
        nx_, ny_ = len(xs) - 1, len(ys) - 1
        grown = [[False] * ny_ for _ in range(nx_)]
        for r in rects:
            for ix in range(bisect.bisect_left(xs, round(r[0] - g, 3)), bisect.bisect_left(xs, round(r[1] + g, 3))):
                col = grown[ix]
                for iy in range(bisect.bisect_left(ys, round(r[2] - g, 3)), bisect.bisect_left(ys, round(r[3] + g, 3))):
                    col[iy] = True
        pre = [[0] * (ny_ + 1) for _ in range(nx_ + 1)]
        for ix in range(nx_):
            for iy in range(ny_):
                pre[ix + 1][iy + 1] = pre[ix][iy + 1] + pre[ix + 1][iy] - pre[ix][iy] + grown[ix][iy]
        e = [[False] * ny_ for _ in range(nx_)]
        for ix in range(nx_):
            ia, ib = max(0, bisect.bisect_right(xs, xs[ix] - g + 1e-6) - 1), bisect.bisect_left(xs, xs[ix + 1] + g - 1e-6)
            if xs[ix] - g < xs[0] - 1e-6 or xs[ix + 1] + g > xs[-1] + 1e-6:
                continue
            for iy in range(ny_):
                ja, jb = max(0, bisect.bisect_right(ys, ys[iy] - g + 1e-6) - 1), bisect.bisect_left(ys, ys[iy + 1] + g - 1e-6)
                if ys[iy] - g < ys[0] - 1e-6 or ys[iy + 1] + g > ys[-1] + 1e-6:
                    continue
                total = pre[ib][jb] - pre[ia][jb] - pre[ib][ja] + pre[ia][ja]
                e[ix][iy] = total == (ib - ia) * (jb - ja)
        edges = {}                                       # directed boundary edges with the filled cell on the left
        for ix in range(nx_):
            for iy in range(ny_):
                if not e[ix][iy]:
                    continue
                if iy == 0 or not e[ix][iy - 1]:
                    edges.setdefault((ix, iy), []).append((ix + 1, iy))
                if ix == nx_ - 1 or not e[ix + 1][iy]:
                    edges.setdefault((ix + 1, iy), []).append((ix + 1, iy + 1))
                if iy == ny_ - 1 or not e[ix][iy + 1]:
                    edges.setdefault((ix + 1, iy + 1), []).append((ix, iy + 1))
                if ix == 0 or not e[ix - 1][iy]:
                    edges.setdefault((ix, iy + 1), []).append((ix, iy))
        ca, sa = math.cos(ang), math.sin(ang)
        while edges:
            start = next(iter(edges))
            loop, cur = [start], start
            while True:
                nxt = edges[cur].pop()
                if not edges[cur]:
                    del edges[cur]
                if nxt == start:
                    break
                loop.append(nxt)
                cur = nxt
            pts = []
            for k, v in enumerate(loop):                 # keep only the corners
                a, b = loop[k - 1], loop[(k + 1) % len(loop)]
                if (a[0] == v[0] == b[0]) or (a[1] == v[1] == b[1]):
                    continue
                pts.append((xs[v[0]] * ca - ys[v[1]] * sa, xs[v[0]] * sa + ys[v[1]] * ca))
            if len(pts) >= 3:
                loops.append(pts)
    return loops


def _outer_runs(polys):
    """The stretches of the boxes' edges that no other box of the group covers just outside, as lists of points: the group's outline,
    with no line where two boxes touch (every metre of an edge is tested for a box 0.3 m beyond it)."""
    boxes_xy = [(min(q[0] for q in c), max(q[0] for q in c), min(q[1] for q in c), max(q[1] for q in c)) for c in polys]
    buckets = collections.defaultdict(list)              # 50 m cells holding the boxes that reach them, so a test looks only nearby
    for n, (bx0, bx1, by0, by1) in enumerate(boxes_xy):
        for gx in range(int(bx0 // 50), int(bx1 // 50) + 1):
            for gy in range(int(by0 // 50), int(by1 // 50) + 1):
                buckets[gx, gy].append(n)
    outer = []
    for me, c in enumerate(polys):
        cx, cy = sum(q[0] for q in c) / 4, sum(q[1] for q in c) / 4
        for (x0, y0), (x1, y1) in zip(c, c[1:] + c[:1]):
            length = math.hypot(x1 - x0, y1 - y0)
            steps = max(1, int(length))                  # test every metre of the edge
            nx, ny = (y1 - y0) / (length or 1.0), -(x1 - x0) / (length or 1.0)
            if nx * (x0 - cx) + ny * (y0 - cy) < 0:
                nx, ny = -nx, -ny                        # the normal that points away from this box
            run, last = None, None
            for st in range(steps):
                t0, t1 = st / steps, (st + 1) / steps
                mx, my = x0 + (x1 - x0) * (t0 + t1) / 2 + 0.3 * nx, y0 + (y1 - y0) * (t0 + t1) / 2 + 0.3 * ny
                inside = any(other != me and boxes_xy[other][0] <= mx <= boxes_xy[other][1]
                             and boxes_xy[other][2] <= my <= boxes_xy[other][3] and _inside(polys[other], mx, my)
                             for other in buckets.get((int(mx // 50), int(my // 50)), ()))
                if run is None or inside != last:
                    if run and not last:
                        outer.append(run)
                    run, last = [(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0)], inside
                run.append((x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1))
            if run and not last:
                outer.append(run)
    return outer


def station_layers(mpp, fr, instances, boxes):
    """SVG lines for the `stations` layer (below the roads) and the `stations-street` layer (above them, so the border hides the
    ends of the station's own road lanes), as (`under`, `over`), a sublayer per `STATION_KINDS` entry that has a piece in the picture. Each placed piece is
    its box in the model's own axes (`boxes`, from `read_station_boxes`), turned by the instance's facing and moved to its origin. A
    sublayer holds the fills (one `<g class="station-piece" data-slot data-model data-x data-y>` each, opaque inside a group that is
    partly transparent as a whole, so overlapping boxes do not darken) and the kind's outline, `station-outer`, at `STATION_OUTLINE`,
    the width of an industry's: a stretch of a box's edge with another box of the kind just outside it is inside the group and is
    not drawn, so touching boxes show no line between them. `instances` are `read_instances` rows. Units are metres like the other
    layers; kinds are drawn in the table's order, so buildings lie over platforms."""
    k = max(1.0, mpp / 2.0)
    out, top = [], []
    deck_polys, deck_outer = [], []
    border_polys = []
    for i in instances:
        if i["model"].startswith("stations/street/") and STREET_BORDER.match(i["model"][len("stations/"):]) and i["model"] in boxes:
            x0, y0, x1, y1 = boxes[i["model"]]
            h = math.hypot(i["fx"], i["fy"]) or 1.0
            fx, fy = i["fx"] / h, i["fy"] / h
            border_polys.append([fr.pic(i["x"] + a * fx - b * fy, i["y"] + a * fy + b * fx) for a, b in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))])
    border_loops = _closed_outline(border_polys) if border_polys else []

    def loops_d(loops):
        return "".join("M" + "L".join("%.2f %.2f" % q for q in lp) + "Z" for lp in loops)
    for lid, label, names, _edges, colour, opacity in STATION_KINDS:
        models = {"stations/%s.mdl" % n for n in names}
        polys, rows = [], []
        for i in instances:
            if i["model"] in models and i["model"] in boxes:
                x0, y0, x1, y1 = boxes[i["model"]]
                h = math.hypot(i["fx"], i["fy"]) or 1.0
                fx, fy = i["fx"] / h, i["fy"] / h
                polys.append([fr.pic(i["x"] + a * fx - b * fy, i["y"] + a * fy + b * fx) for a, b in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))])
                rows.append(i)
        if not polys:
            continue
        out_kind = top if lid.startswith("station-street") else out    # street stations lie over the roads
        if not out_kind:
            out_kind.append(layer("stations-street" if out_kind is top else "stations", "Street stations" if out_kind is top else "Stations",
                                  ' transform="scale(%g)" pointer-events="none"' % (1.0 / mpp)))
        if lid == "station-street-platforms" and border_loops:
            out_kind.append(layer("station-street-ground", "Street stations: ground inside the border"))
            out_kind.append('<path class="station-ground" d="%s" fill="%s" fill-rule="evenodd" fill-opacity="%g" stroke="%s" stroke-width="%g"'
                       ' stroke-opacity="%g"/></g>' % (loops_d(border_loops), STREET_BORDER_FILL, STREET_BORDER_OPACITY, STREET_BORDER_FILL,
                                                       0.5 * k, STREET_BORDER_OPACITY))
        out_kind.append(layer(lid, label))
        out_kind.append('<g opacity="%g">' % opacity)
        for i, c in zip(rows, polys):
            out_kind.append('<g class="station-piece" data-slot="%s" data-model=%s data-x="%.1f" data-y="%.1f"><polygon points="%s" fill="%s" '
                       'stroke="%s" stroke-width="%g"/></g>'    # a same-colour edge hides the seam between two boxes
                       % (i["slot"], quoteattr(i["model"]), i["x"], i["y"], " ".join("%.2f,%.2f" % q for q in c), colour, colour, 0.5 * k))
        out_kind.append("</g>")
        if lid == "station-street-platforms" and border_loops:
            outer = _outer_runs([c for i, c in zip(rows, polys) if "/small_stops/" in i["model"]] or [])
        else:
            outer = _outer_runs(polys)
        if lid == "station-water-decks":
            deck_polys, deck_outer = polys, outer
        if outer:
            d = "".join("M%.2f %.2f" % r[0] + "".join("L%.2f %.2f" % q for q in r[1:]) for r in outer)
            out_kind.append('<path class="station-outer" d="%s" fill="none" stroke="#000" stroke-width="%g" stroke-linecap="round"'
                       ' stroke-linejoin="round"/>' % (d, STATION_OUTLINE * k))
        out_kind.append("</g>")
        if lid == "station-street-platforms" and border_loops:
            out_kind.append(layer("station-street-borders", "Street stations: border"))
            out_kind.append('<path class="station-outer" d="%s" fill="none" stroke="#000" stroke-width="%g" stroke-linecap="round"'
                       ' stroke-linejoin="round"/></g>' % (loops_d(border_loops), STATION_OUTLINE * k))
    landings = [i for i in instances if i["model"].startswith("stations/water/models/")
                and LANDING_MODELS.get(i["model"].rsplit("/", 1)[-1][:-4])]
    if landings:
        if not out:
            out.append(layer("stations", "Stations", ' transform="scale(%g)" pointer-events="none"' % (1.0 / mpp)))
        out.append("<defs>")
        for size in sorted({LANDING_MODELS[i["model"].rsplit("/", 1)[-1][:-4]] for i in landings}):
            body = re.search(r"<svg[^>]*>(.*)</svg>", open(os.path.join(ICON_DIR, "..", "anchor_%s.svg" % size)).read(), re.S)
            out.append('<symbol id="station-anchor-%s" viewBox="0 0 64 64">%s</symbol>' % (size, body.group(1)))
        out.append("</defs>")
        out.append(layer("station-landings", "Water stations: landings"))
        for i in landings:
            size = LANDING_MODELS[i["model"].rsplit("/", 1)[-1][:-4]]
            d = LANDING_SIZE[size]
            (cx, cy), edge = _clear_of_edge(fr.pic(i["x"], i["y"]), LANDING_CLEARANCE[size] * d + 0.75 * k, deck_polys, deck_outer)
            turn = ""
            if edge:                                         # the ring at the top of an anchor points at its dock
                turn = ' transform="rotate(%.1f %.2f %.2f)"' % (math.degrees(math.atan2(edge[0] - cx, cy - edge[1])) - LANDING_TILT[size], cx, cy)
            out.append('<use class="station-landing" data-slot="%s" data-model=%s data-size="%s" data-x="%.1f" data-y="%.1f" xlink:href="#station-anchor-%s" '
                       'x="%.2f" y="%.2f" width="%g" height="%g" color="%s"%s/>'
                       % (i["slot"], quoteattr(i["model"]), size, i["x"], i["y"], size, cx - d / 2, cy - d / 2, d, d, LANDING_INK, turn))
        out.append("</g>")
    if out:
        out.append("</g>")
    if top:
        top.append("</g>")
    return out, top


def depot_layers(mpp, fr, instances, specs, footprints, coverage):
    """SVG lines for the depot layers: (`under`, `over`). `under` is the `coverage` layer (one circle per building,
    a sublayer per kind) and `over` the `maintenance-buildings`, `road-depots` and `tram-depots` layers (the
    ground face placed from the instance's origin and facing, its origin, a line along the model's x axis).
    `instances` are `read_instances` rows; only the exact model path of each kind is drawn, so a road depot's
    `road_depot_sm` twin is not. Units are metres like the other layers."""
    k = max(1.0, mpp / 2.0)
    under, over = [], []
    cover = []
    for lid, label, _archive, _script, model, colour in DEPOT_KINDS:
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
                local = lambda a, b: fr.pic(i["x"] + a * fx - b * fy, i["y"] + a * fy + b * fx)
                pts = " ".join("%.2f,%.2f" % local(a, b) for a, b in spec["face"])
                o, tip = local(0, 0), local(10 * k, 0)
                over.append("<g %s>" % attrs(i))
                if pts:
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
                cx, cy = fr.pic(i["x"], i["y"])
                cover.append('<g %s><circle cx="%.2f" cy="%.2f" r="%d" fill="%s" fill-opacity="0.06" stroke="%s"'
                             ' stroke-width="%g" stroke-dasharray="%g %g"/></g>'
                             % (attrs(i), cx, cy, spec["radius"], colour, colour, 1.5 * mpp, 10 * mpp, 6 * mpp))
            cover.append("</g>")
    if cover:
        under.append(layer("coverage", "Coverage", ' transform="scale(%g)" pointer-events="none"' % (1.0 / mpp)))
        under += cover
        under.append("</g>")
    return under, over


ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "industries")
INDUSTRY_DIAMETER = 64.0                                 # metres, the badge of an industry with no footprint (`--industry-size` sets all)
FOOTPRINT_SHARE = 0.4                                    # a badge is this share of its footprint's shorter side
INDUSTRY_BORDER, INDUSTRY_INK = "#8c8c8c", "#3a3a3a"
FOOTPRINT_FILL, FOOTPRINT_LINE = "#b44fe8", "#5b1a8f"     # the Towns layer paints an industry purple: light fill, dark line
# The water industries declare no `ground_face`. These outlines (metres, the industry's own axes, counter-clockwise) were read off
# Towns-layer screenshots of one 604 game, registered on the industries' corner buoys (docs/models.md, "Industry footprints"),
# good to about 2 m. The oil platform has no outline in the game (its meshes are tinted); its stand-in is the deck (the
# `oil_platform_sm` model's box) with the helipad as an octagon at a corner and the big crane's boom as a thin strip along +b, a
# few metres coarse (the picture is tilted, so the boom's tip is the least certain).
MEASURED_FACES = {
    "fishing_grounds": [(-40.0, -28.0), (22.0, -28.0), (22.0, -12.8), (38.5, -12.8), (38.5, 20.7), (-30.0, 20.7), (-40.0, 15.5)],
    "sand_excavator": [(-18.2, -43.5), (45.5, -43.5), (45.5, 65.0), (-18.2, 65.0)],
    "oil_platform": [(-24.5, 24.7), (-24.5, -29.5), (13.7, -29.5), (15.5, -31.3), (24.2, -31.3), (30.3, -25.2), (30.3, -16.5),
                     (24.7, -10.9), (24.7, 24.7), (4.0, 24.7), (7.0, 52.0), (3.0, 52.0), (0.0, 24.7)],
}
# Round parts the Towns layer tints beside a footprint, (a, b, radius) in metres in the industry's axes: the oil platform's two
# docking stations (the big orange drums, about 10 m across). Its four large buoys are tinted too, but at 2 to 3 m they are left out.
MEASURED_DISCS = {
    "oil_platform": [(55.0, 0.0, 5.5), (-55.0, 0.0, 5.5)],
}


def face_centre(face):
    """The area centroid of a polygon (a list of (a, b) points) when it lies inside the polygon, else None (a shape bent
    round its own centroid, or a polygon with no area)."""
    area = cx = cy = 0.0
    for (a0, b0), (a1, b1) in zip(face, face[1:] + face[:1]):
        cross = a0 * b1 - a1 * b0
        area += cross
        cx += (a0 + a1) * cross
        cy += (b0 + b1) * cross
    if abs(area) < 1e-6:
        return None
    cx, cy = cx / (3 * area), cy / (3 * area)
    inside = False
    for (a0, b0), (a1, b1) in zip(face, face[1:] + face[:1]):
        if (b0 > cy) != (b1 > cy) and cx < a0 + (cy - b0) * (a1 - a0) / (b1 - b0):
            inside = not inside
    return (cx, cy) if inside else None


def face_badge(face):
    """(centre (a, b) in the industry's axes, diameter in metres) of the badge for a footprint: the centroid when it lies
    inside the polygon, else the origin, and `FOOTPRINT_SHARE` of the polygon's shorter bounding-box side."""
    xs, ys = [a for a, _ in face], [b for _, b in face]
    return face_centre(face) or (0.0, 0.0), FOOTPRINT_SHARE * min(max(xs) - min(xs), max(ys) - min(ys))


def industry_layers(mpp, fr, rows, diameter=None, faces=None):
    """SVG lines for the `industries` layer: a badge per industry, a white disc with a grey border and
    the industry's icon (tools/icons/industries/KEY.svg, 64 x 64, in `currentColor`) in dark grey. `rows` are `read_instances` rows
    with a `key` added. `faces` is `read_industry_faces`' result: an industry whose key has one gets its ground face, placed from
    the instance's origin and facing, in a `industry-footprints` sublayer under the badges (dark purple outline, translucent light
    purple fill), and its badge is `FOOTPRINT_SHARE` of the face's shorter side across and sits on the face's centroid (the origin
    when the centroid falls outside the face). The others (no face) get `INDUSTRY_DIAMETER` on the origin. `diameter` fixes every
    badge's size instead. One sublayer per key, one `<symbol>` per key used; a key without an icon gets the disc only. The badge is
    upright whatever the north. Units are metres like the other layers."""
    if not rows:
        return []
    out = [layer("industries", "Industries", ' transform="scale(%g)" pointer-events="none"' % (1.0 / mpp)), "<defs>"]
    have = set()
    for key in sorted({i["key"] for i in rows}):
        try:
            text = open(os.path.join(ICON_DIR, key + ".svg")).read()
        except OSError:
            continue
        body = re.search(r"<svg[^>]*>(.*)</svg>", text, re.S)
        if body:
            have.add(key)
            out.append('<symbol id="industry-icon-%s" viewBox="0 0 64 64">%s</symbol>' % (safe_id(key), body.group(1)))
    out.append("</defs>")
    shapes = [i for i in rows if faces and i["key"] in faces]
    if shapes:
        out.append(layer("industry-footprints", "Industries: footprints"))
        for i in shapes:
            n = math.hypot(i["fx"], i["fy"]) or 1.0
            fx, fy = i["fx"] / n, i["fy"] / n
            for a, b, rad in MEASURED_DISCS.get(i["key"], ()):
                cx, cy = fr.pic(i["x"] + a * fx - b * fy, i["y"] + a * fy + b * fx)
                out.append('<circle class="industry-footprint" data-slot="%d" data-key="%s" cx="%.2f" cy="%.2f" r="%.2f" fill="%s" fill-opacity="0.45"'
                           ' stroke="%s" stroke-width="%g"/>'
                           % (i["slot"], i["key"], cx, cy, rad, FOOTPRINT_FILL, FOOTPRINT_LINE, 1.5 * max(1.0, mpp / 2.0)))
            pts = " ".join("%.2f,%.2f" % fr.pic(i["x"] + a * fx - b * fy, i["y"] + a * fy + b * fx) for a, b in faces[i["key"]])
            out.append('<polygon class="industry-footprint" data-slot="%d" data-key="%s" points="%s" fill="%s" fill-opacity="0.45"'
                       ' stroke="%s" stroke-width="%g" stroke-linejoin="round"/>'
                       % (i["slot"], i["key"], pts, FOOTPRINT_FILL, FOOTPRINT_LINE, 1.5 * max(1.0, mpp / 2.0)))
        out.append("</g>")
    for key in sorted({i["key"] for i in rows}):
        out.append(layer("industry-" + safe_id(key), "Industries: " + key, ' data-key="%s"' % key))
        for i in (i for i in rows if i["key"] == key):
            centre, d = (0.0, 0.0), INDUSTRY_DIAMETER
            if faces and key in faces:
                centre, d = face_badge(faces[key])
            d = diameter or d
            n = math.hypot(i["fx"], i["fy"]) or 1.0
            fx, fy = i["fx"] / n, i["fy"] / n
            cx, cy = fr.pic(i["x"] + centre[0] * fx - centre[1] * fy, i["y"] + centre[0] * fy + centre[1] * fx)
            border, side = d / 32.0, 0.72 * d             # 2 m on a 64 m badge; the icon sits inside the disc with a margin
            out.append('<g class="industry" data-slot="%d" data-key="%s" data-model=%s data-x="%.1f" data-y="%.1f" data-diameter="%.1f">'
                       '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="#ffffff" stroke="%s" stroke-width="%g"/>'
                       % (i["slot"], key, quoteattr(i["model"]), i["x"], i["y"], d, cx, cy, d / 2 - border / 2, INDUSTRY_BORDER, border))
            if key in have:
                out.append('<use xlink:href="#industry-icon-%s" x="%.2f" y="%.2f" width="%g" height="%g" color="%s"/>'
                           % (safe_id(key), cx - side / 2, cy - side / 2, side, side, INDUSTRY_INK))
            out.append("</g>")
        out.append("</g>")
    out.append("</g>")
    return out


WATER_FILL, SHORE_LINE = "#78afdc", "#4a86b8"
LAND_FILL = "#ece9d2"
CONTOUR_MINOR, CONTOUR_INDEX = "#b8996a", "#7a5230"


def hex_colour(c):
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in c)


def vector_terrain(picked, spacing, size, mpp, off_z, unit, water, step_m, every, tol, bands=True):
    """The terrain as vector layers (the default, in place of the raster PNG): (the layer lines of `terrain` in metres from the picture's
    top-left corner, (water rings, height lines, bands)). `picked` is the grid in picture order (`to_picture`); a
    point is `spacing` metres apart; `size` is the picture in pixels of `mpp` metres. Sublayers, bottom to top: `land` (a plain rectangle), `bands` (with `bands`: a path
    for each height step, filled with the colour of the height ramp and covering all ground from there up, so
    the higher ones paint over the lower), `water` (the even-odd path of rings, the shore stroked) and `contours`
    (`contours-minor`, `contours-index` every `every`th level: one `<path data-height>` per level, the height in
    metres above the water). Lines are thinned to `tol` metres."""
    w, h = size
    rings, extent = level_rings(picked, spacing, (water - off_z) / unit, step_m / unit, min_perimeter=4 * spacing)
    rings = {k: [simplify(r, tol, True) for r in rs] for k, rs in rings.items()}
    rect = "M0 0H%gV%gH0Z" % (w * mpp, h * mpp)
    thin = 0.5 * mpp                                     # metres, so a line stays thinner than a road on a close crop
    land = hex_colour(_land_colour(step_m / 2)) if bands else LAND_FILL
    out = [layer("terrain", "Terrain", ' transform="scale(%g)"' % (1.0 / mpp)),
           layer("land", "Land", ""), '<rect width="%g" height="%g" fill="%s"/>' % (w * mpp, h * mpp, land), "</g>"]
    n_bands = 0
    if bands:
        out.append(layer("bands", "Height bands", ' stroke="none"'))
        for k, rs in sorted(rings.items()):
            if k:
                out.append('<path class="band" data-height="%g" fill="%s" fill-rule="evenodd" d="%s%s"/>'
                           % (k * step_m, hex_colour(_land_colour((k + 0.5) * step_m)), rect,
                              path_data(rs, closed=True)))
                n_bands += 1
        out.append("</g>")
    out += [layer("water", "Water", ""),
            '<path class="water" fill="%s" fill-rule="evenodd" stroke="%s" stroke-width="%g" stroke-linejoin="round" d="%s"/>'
            % (WATER_FILL, SHORE_LINE, thin, path_data(rings.get(0, []), closed=True)), "</g>",
            layer("contours", "Height lines", "")]
    n_lines = 0
    for sub, label, colour, width, pick in (("contours-minor", "Height lines", CONTOUR_MINOR, thin, lambda k: k % every),
                                            ("contours-index", "Index height lines", CONTOUR_INDEX, 2 * thin, lambda k: not k % every)):
        out.append(layer(sub, label, ' fill="none" stroke="%s" stroke-width="%g" stroke-linejoin="round" stroke-linecap="round"'
                         % (colour, width)))
        for k, rs in sorted(rings.items()):
            if k and pick(k):
                polylines = [pc for r in rs for pc in split_at_border(r, extent)]
                d = path_data([p for p, c in polylines if c], closed=True) + path_data([p for p, c in polylines if not c])
                if d:
                    out.append('<path class="contour" data-height="%g" d="%s"/>' % (k * step_m, d))
                    n_lines += len(polylines)
        out.append("</g>")
    out += ["</g>", "</g>"]
    return out, (len(rings.get(0, [])), n_lines, n_bands)


ROSE_CORNERS = ("lower-left", "lower-right", "upper-left", "upper-right")
ROSE_SIZE = 250.0                                            # metres across the circle, at most an eighth of the picture's short side


def rose_layer(size, mpp, fr, where="lower-right", diameter=None):
    """The `compass` layer: a white circle with a black outline and a black compass rose in it, in map metres from the picture's
    top-left corner. `where` is a corner of the picture (`ROSE_CORNERS`) or `X,Y` in map metres for the centre, `diameter` the circle's
    width in metres (default `ROSE_SIZE`, at most an eighth of the picture's short side). The rose is the shape of tools/icons/
    compass_rose.svg: north an arrow, the other three arms half as long with E, S and W at their ends. The arms point where north
    and east lie in the picture (`fr.vec`), so under `--north sun` north is left; the letters stay upright. Returns lines of SVG."""
    w, h = size[0] * mpp, size[1] * mpp
    d = diameter or min(ROSE_SIZE, min(w, h) / 8)
    r = d / 2.0
    if where in ROSE_CORNERS:
        gap = 0.15 * r
        cx = gap + r if where.endswith("left") else w - gap - r
        cy = gap + r if where.startswith("upper") else h - gap - r
    else:
        cx, cy = fr.pic(*where)
    k = 0.0495 * r                                           # the icon's unit: its arrow is 15 k long
    out = [layer("compass", "Compass rose", ' transform="scale(%g)"' % (1.0 / mpp)),
           '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#ffffff" stroke="#000000" stroke-width="%.2f"/>' % (cx, cy, r, 0.03 * r)]
    north, east = fr.vec(0, 1), fr.vec(1, 0)
    south, west = (-north[0], -north[1]), (-east[0], -east[1])

    def at(vec, dist):
        return "%.1f %.1f" % (cx + vec[0] * dist, cy + vec[1] * dist)
    arms = "".join("M%.1f %.1fL%s" % (cx, cy, at(v, n * k)) for v, n in ((north, 15), (south, 7.5), (east, 7.5), (west, 7.5)))
    out.append('<path d="%s" stroke="#000000" stroke-width="%.2f" fill="none"/>' % (arms, 2.34 / 1.8 * k))
    perp = (-north[1], north[0])
    out.append('<path d="M%sL%sL%sz" fill="#000000"/>' % (at(north, 18 * k), "%.1f %.1f" % (
        cx + north[0] * 11 * k + perp[0] * 3 * k, cy + north[1] * 11 * k + perp[1] * 3 * k), "%.1f %.1f" % (
        cx + north[0] * 11 * k - perp[0] * 3 * k, cy + north[1] * 11 * k - perp[1] * 3 * k)))
    for label, vec in (("E", east), ("S", south), ("W", west)):
        out.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-family="sans-serif" font-size="%.1f" font-weight="bold" '
                   'fill="#000000">%s</text>' % (cx + vec[0] * 12.6 * k, cy + vec[1] * 12.6 * k + 0.35 * 8.5 * k, 8.5 * k, label))
    out.append("</g>")
    return out


def svg_document(png, size, mpp, fr, edges, widths, grid=None, metadata=None, overlay=(), zoom=1, under=(), over=(), terrain=None, min_width=0.0, rose=(), grid_lines="auto", dot_step=25, grid_major=1000):
    """SVG text in layers (groups that Inkscape shows as layers, each `class="layer"` with its id in
    `data-layer`): `terrain` (the PNG as a data URI), `roads` and `rails`, each holding a sublayer per
    street or track type (`road-TYPE`, `rail-TYPE`) with one `<path data-a data-b>` per edge. `metadata` is the `svg_metadata` element, if wanted. Coordinates inside the layers are metres from the image's top-left corner, north up and east
    right (`fr.pic` gives the position)."""
    w, h = size[0] * mpp, size[1] * mpp
    groups = {"road": {}, "rail": {}}                    # family -> type -> one <path> per edge
    for e in edges:
        fam = "rail" if e["family"] == "track" else "road"
        c = [fr.pic(*q) for q in edge_bezier(e)]
        if edge_is_curved(e):                            # the stored tangents bend it: a cubic through both ends
            d = "M%.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1f" % (c[0] + c[1] + c[2] + c[3])
        else:
            d = "M%.1f %.1fL%.1f %.1f" % (c[0] + c[3])
        groups[fam].setdefault(e["type"] or "unknown", []).append(
            '<path class="%s %s" data-a="%x" data-b="%x"%s stroke-width="%g" d="%s"/>'
            % (fam, safe_id(e["type"] or "unknown"), e["a"], e["b"], ' data-edge="%x"' % e["e"] if e.get("e") else "",
               edge_width(e, widths, min_width), d))
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
             ' xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"'
             ' width="%d" height="%d" viewBox="0 0 %d %d">' % (size[0] * zoom, size[1] * zoom, size[0], size[1]),
             '<title>Terrain, roads and rails</title>'] + ([metadata] if metadata else []) + [
             '<style>.road{stroke:%s}.rail{stroke:%s}'
             '.road,.rail{fill:none;stroke-linecap:round;stroke-linejoin:round}</style>'
             % (ROAD_HEX, RAIL_HEX),
             ] + (terrain if terrain else [
             layer("terrain", "Terrain", ' transform="scale(%g)"' % (1.0 / mpp)),
             '<image width="%d" height="%d" xlink:href="data:image/png;base64,%s"/>'
             % (w, h, base64.b64encode(png).decode()),
             '</g>'])
    grid_labels = []
    if grid:                                             # the lines above the terrain, under the network
        grid_lines, grid_labels = grid_layers(size, mpp, fr, grid, grid_lines, dot_step, grid_major)
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
    parts += rose                                        # the compass rose over the lot
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out_dir")
    ap.add_argument("saves", nargs="+")
    ap.add_argument("--mpp", type=int, default=None, help="metres per pixel (default 8 for the vector terrain, 4 "
                    "on a crop; 4 with --raster or --png)")
    ap.add_argument("--raster", action="store_true", help="SVG only: draw the terrain as the shaded embedded PNG "
                    "instead of vector bands, water and height lines")
    ap.add_argument("--contour", type=float, default=20.0, metavar="M",
                    help="vector terrain: metres between height lines and bands (default 20)")
    ap.add_argument("--index", type=int, default=5, metavar="N",
                    help="vector terrain: every Nth height line is drawn heavier (default 5)")
    ap.add_argument("--no-bands", action="store_true",
                    help="vector terrain: leave out the coloured height bands (a plain land colour)")
    ap.add_argument("--tolerance", type=float, metavar="M",
                    help="vector terrain: thin lines to this many metres (default 0.4 x metres per pixel)")
    ap.add_argument("--north", choices=("game", "sun"), default="game",
                    help="which way north is drawn: game (default: up is +y, right is +x, as the game's name "
                    "compass has it) or sun (up is +x, right is -y, from the sun's path); see docs/terrain.md")
    ap.add_argument("--crop", help="X,Y,R: the square of half-width R metres around (X, Y)")
    ap.add_argument("--png", action="store_true")
    ap.add_argument("--grid", type=int, metavar="N", help="SVG only: a labelled line every N metres of map x and y")
    ap.add_argument("--no-grid", action="store_true", help="SVG only: leave out the default grid (major marks every third of the "
                    "shorter side, rounded down to 1, 2 or 5 x a power of ten; at least 1000 m on a whole map)")
    ap.add_argument("--grid-lines", choices=("auto", "none", "dots", "faint"), default="auto",
                    help="SVG only, with --grid: auto (default) crosses and dotted 1000 m lines, but crosses only at 1 m per pixel "
                    "or finer; none crosses only; dots or faint also draw the minor lines, as sparse dots or faint solid lines")
    ap.add_argument("--grid-dot-step", type=float, default=25, metavar="M",
                    help="metres between the dots of --grid-lines dots (default 25, at least %d pixels)" % GRID_MIN_DOT_PX)
    ap.add_argument("--game", help="the game's install folder, for the street and track widths "
                    "(default: the usual Steam places)")
    ap.add_argument("--min-width", type=float, default=0.0, metavar="M", help="SVG only: draw no road or rail "
                    "narrower than M metres, so a whole-map picture keeps them visible (default 0: real widths)")
    ap.add_argument("--rose", default="lower-right", metavar="WHERE",
                    help="SVG only: where the compass rose goes: lower-right (default), lower-left, upper-left, "
                    "upper-right, off, or X,Y (map metres) for its centre")
    ap.add_argument("--rose-size", type=float, metavar="M", help="SVG only: the rose circle's diameter in metres "
                    "(default 250, at most an eighth of the picture's short side)")
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--keep-dead", action="store_true", help="draw edges whose end node is in the free-id list too")
    ap.add_argument("--label", action="append", default=[], metavar="A>B[=TEXT]",
                    help="SVG only: label the edge with end nodes A and B (hex ids); repeatable")
    ap.add_argument("--edge-ids", action="store_true", help="with --label, add edge entity ids where known")
    ap.add_argument("--zoom", type=int, default=1, help="SVG only: show the picture this many times larger "
                    "(its width and height, not the viewBox)")
    ap.add_argument("--vehicles", action="store_true", help="SVG only: draw the vehicle model instances")
    ap.add_argument("--name", action="append", default=[], metavar="SLOT=TEXT",
                    help="rename one vehicle instance in the picture (repeatable)")
    ap.add_argument("--stations", action="store_true", help="SVG only: draw the water stations' docks, platforms and "
                    "main buildings as boxes (sizes from the install)")
    ap.add_argument("--depots", action="store_true", help="SVG only: draw the road maintenance buildings, road depots "
                    "and tram depots (ground faces from the install)")
    ap.add_argument("--industries", action=argparse.BooleanOptionalAction, default=True,
                    help="SVG only, on by default (--no-industries leaves it out): stamp each industry's icon on a white disc "
                    "with a grey border, 96 m across by default, at its origin (see the icon files in tools/icons/industries)")
    ap.add_argument("--industry-size", type=float, metavar="M",
                    help="with --industries: every badge's diameter in metres (default: %g of the footprint's shorter side, %g m "
                    "for an industry with no footprint)" % (FOOTPRINT_SHARE, INDUSTRY_DIAMETER))
    ap.add_argument("--mods", help="the mod.io game's mods folder, for a mod's depots (default: the usual places)")
    ap.add_argument("--coverage", action="store_true", help="SVG only: draw their maintenance coverage circles")
    ap.add_argument("--stream", action="store_true")
    ap.add_argument("--force-size", action="store_true")
    args = ap.parse_args()
    if args.raster and args.png:
        ap.error("--raster and --png are two ways to draw the terrain as pixels: pick one")
    vector = not (args.raster or args.png)
    rose_at = args.rose
    if rose_at not in ROSE_CORNERS + ("off",):
        try:
            rose_at = tuple(float(v) for v in args.rose.split(","))
            assert len(rose_at) == 2
        except (ValueError, AssertionError):
            ap.error("--rose wants off, a corner (%s) or X,Y in metres" % ", ".join(ROSE_CORNERS))
    if args.rose_size is not None and args.rose_size <= 0:
        ap.error("--rose-size wants a diameter above 0")
    if args.contour <= 0 or args.index < 1:
        ap.error("--contour wants a step above 0 and --index 1 or more")
    if args.mpp is None:
        args.mpp = 8 if vector and not args.crop else 4
    if args.mpp not in (1, 2) and (args.mpp < 4 or args.mpp % 4):
        ap.error("--mpp must be 1, 2 or a multiple of 4 (the heightmap spacing)")
    if (args.label or args.vehicles or args.depots or args.coverage or args.stations) and args.png:
        ap.error("--label, --vehicles, --depots, --stations and --coverage only work with the SVG")
    if args.no_grid and args.grid:
        ap.error("--no-grid and --grid exclude each other")
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
    if args.grid_lines != "auto" and args.no_grid:
        ap.error("--grid-lines needs a grid")
    if args.grid_lines == "dots" and args.grid_dot_step < GRID_MIN_DOT_PX * args.mpp:
        print("--grid-dot-step %g is under %d pixels at %g m per pixel; dots will be %g m apart"
              % (args.grid_dot_step, GRID_MIN_DOT_PX, args.mpp, GRID_MIN_DOT_PX * args.mpp))
    crop = None
    if args.crop:
        try:
            crop = tuple(float(v) for v in args.crop.split(","))
            assert len(crop) == 3 and crop[2] > 0
        except (ValueError, AssertionError):
            ap.error("--crop wants X,Y,R in metres")
    if args.industry_size is not None and args.industry_size <= 0:
        ap.error("--industry-size wants a diameter above 0")
    os.makedirs(args.out_dir, exist_ok=True)
    content = find_content(args.game)
    widths = read_profile_widths(content) if content else {}
    depot_specs = read_depot_specs(content, args.mods) if args.depots or args.coverage else {}
    station_boxes = read_station_boxes(content) if args.stations else {}
    if args.stations and not station_boxes:
        print("no install found (--game DIR): no station layer drawn")
    industry_faces = dict(MEASURED_FACES, **read_industry_faces(content)) if args.industries and not args.png else {}
    if (args.depots or args.coverage) and not depot_specs:
        print("no install found (--game DIR): no depot layers drawn")
    print("widths: %s" % (("%d templates read from the install" % len(widths)) if widths else
                          "no install found (--game DIR), roads drawn 16 m wide and tracks 4 m"))
    step, fine = max(1, args.mpp // 4), (4 // args.mpp if args.mpp < 4 and not vector else 1)
    spacing = GRID_STEP * step                            # metres between the points the vector terrain is cut from
    for path in args.saves:
        try:
            raw = open(path, "rb").read()
            data = raw if args.stream else decompress(raw)
            tx, ty, off_z, unit, water = read_terrain(data)
            map_w, map_h = tx * 256, ty * 256
            res = spacing if vector else args.mpp                 # metres per grid point or pixel
            if crop:
                pixels = (2 * crop[2] // res + 1) ** 2
            else:
                pixels = (map_w // res + 1) * (map_h // res + 1)
            limit = MAX_VECTOR_POINTS if vector else MAX_PIXELS
            if pixels > limit and not args.force_size:
                print("REFUSED %s: %d x %d m at %d m per %s is %d million %s; raise --mpp"
                      % (os.path.basename(path), map_w, map_h, res, "point" if vector else "pixel",
                         pixels // 1000000, "points" if vector else "pixels"))
                continue
            if args.mpp < 4 and not crop:
                print("REFUSED %s: --mpp %d needs --crop" % (os.path.basename(path), args.mpp))
                continue
            rows = read_heightmap(data, tx, ty)
            bounds = (-map_w / 2, map_w / 2, -map_h / 2, map_h / 2)
            if crop:
                rows, bounds = crop_grid(rows, tx, ty, *crop)
            fr = Frame.from_bounds(args.north, bounds[0], bounds[1], bounds[3])
            if fine > 1:
                rows = upsample(rows, fine)
            if vector:
                picked = to_picture(rows, step, args.north)
                size = (int(math.ceil((len(picked[0]) - 1) * spacing / args.mpp)) + 1,
                        int(math.ceil((len(picked) - 1) * spacing / args.mpp)) + 1)
                img = b""
            else:
                img, size = render(rows, step, off_z, unit, water, args.mpp, args.north)
            x_lo, x_hi, y_lo, y_hi = fr.box(size, args.mpp)
            roads = rails = 0
            edges = [] if args.no_network else read_edges(data)
            if edges and not args.keep_dead:
                free = read_free_ids(data)
                if free is None:
                    print("free-id list not found: every edge is drawn")
                else:
                    live = [e for e in edges if e["a"] not in free and e["b"] not in free]
                    print("%d of %d edges have an end node in the free-id list and are left out (--keep-dead draws them)"
                          % (len(edges) - len(live), len(edges)))
                    edges = live
            if crop:                                  # only the edges that touch the picture
                def touches(e):                       # the bounding box of the control points covers the curve
                    c = edge_bezier(e)
                    return (max(q[0] for q in c) >= x_lo and min(q[0] for q in c) <= x_hi
                            and max(q[1] for q in c) >= y_lo and min(q[1] for q in c) <= y_hi)
                edges = [e for e in edges if touches(e)]
            vehicles = []
            if args.vehicles and crop:
                vehicles = [v for v in read_instances(data)
                            if x_lo <= v["x"] <= x_hi and y_lo <= v["y"] <= y_hi]
            depot_rows, station_rows = [], []
            if depot_specs or station_boxes:
                try:
                    found = read_instances(data, (DEPOT_PREFIXES if depot_specs else ()) + (STATION_PREFIXES if station_boxes else ()))
                except ValueError as e:                   # an older save: no model table, so no instances
                    print("no depot or station layers: %s" % e)
                    found = []
                for i in found:
                    if i["model"] in station_boxes or (i["model"].startswith("stations/water/") and i["model"].rsplit("/", 1)[-1][:-4] in LANDING_MODELS):
                        x0, y0, x1, y1 = station_boxes.get(i["model"], (-1.0, -1.0, 1.0, 1.0))
                        r = math.hypot(max(abs(x0), abs(x1)), max(abs(y0), abs(y1)))
                        if x_lo - r <= i["x"] <= x_hi + r and y_lo - r <= i["y"] <= y_hi + r:
                            station_rows.append(i)
                        continue
                    spec = next((depot_specs[k[0]] for k in DEPOT_KINDS if k[4] == i["model"] and k[0] in depot_specs), None)
                    if not spec:
                        continue
                    r = spec["radius"] if args.coverage else 40       # the circle or the footprint may reach the picture
                    if x_lo - r <= i["x"] <= x_hi + r and y_lo - r <= i["y"] <= y_hi + r:
                        depot_rows.append(i)
            industry_rows = []
            if args.industries and not args.png:
                try:
                    table = read_model_table(data)
                    mains = main_models(table[0])
                    found = list(read_instances(data, ("industries/",), table))
                    seen = {i["model"] for i in found}
                    for path, key in list(mains.items()):    # a main model with no instance (the sand excavator's particles): the key's own model stands in
                        own = "industries/%s/%s.mdl" % (key, key)
                        if path not in seen and own in seen:
                            mains[own] = key
                    for i in found:
                        if i["model"] not in mains:
                            continue
                        key = mains[i["model"]]
                        r = max([(args.industry_size or INDUSTRY_DIAMETER) / 2] + [math.hypot(a, b) for a, b in industry_faces.get(key, ())]
                                 + [math.hypot(a, b) + rad for a, b, rad in MEASURED_DISCS.get(key, ())])
                        if x_lo - r <= i["x"] <= x_hi + r and y_lo - r <= i["y"] <= y_hi + r:
                            industry_rows.append(dict(i, key=key))
                except ValueError as e:                   # an older save: no model table
                    print("no industry layer: %s" % e)
            if args.edge_ids and labels:
                edge_ids(edges, read_strips(data))
            if not args.png:
                roads = sum(e["family"] != "track" for e in edges)
                rails = len(edges) - roads
            elif edges:
                roads, rails = draw_network(img, size, fr, args.mpp, edges, widths)
        except Exception as e:  # report and carry on with the next save
            print(f"FAILED {os.path.basename(path)}: {e}")
            continue
        name = re.sub(r"\s+", "_", os.path.splitext(os.path.basename(path))[0])
        dest = os.path.join(args.out_dir, name
                            + ("-crop%d_%d_%d" % crop if crop else "")
                            + ("-grid%d" % args.grid if args.grid else "") + "-terrain.png")
        png = None if vector else png_bytes(size[0], size[1], bytes(img))
        if not args.png:
            dest = dest[:-len(".png")] + ".svg"
            terrain, extra = None, ()
            if vector:
                tol = args.tolerance if args.tolerance is not None else 0.4 * args.mpp
                terrain, (n_rings, n_lines, n_bands) = vector_terrain(picked, spacing, size, args.mpp, off_z, unit, water,
                                                                      args.contour, args.index, tol, not args.no_bands)
                extra = (("contour-step", "%g" % args.contour if args.contour != ap.get_default("contour") else None),
                         ("index-every", args.index if args.index != ap.get_default("index") else None),
                         ("tolerance", "%g" % tol if args.tolerance is not None else None),
                         ("bands", "false" if args.no_bands else None))
                print("vector terrain: %d water rings, %d height lines, %d height bands" % (n_rings, n_lines, n_bands))
            else:
                extra = (("terrain", "raster"),)
                dest = dest[:-len("-terrain.svg")] + "-terrain-raster.svg"
            if args.grid:                                 # minor marks asked for: the 1000 m marks stay the major ones
                grid_step, grid_major = args.grid, 1000
            elif args.no_grid:
                grid_step = grid_major = None
            else:                                         # the default: major marks only
                grid_step = grid_major = auto_grid_step(2 * crop[2] if crop else min(map_w, map_h), bool(crop))
            extra += (("grid", "off" if args.no_grid else None), ("industries", "off" if not args.industries else None),
                      ("grid-lines", args.grid_lines if args.grid_lines != "auto" else None))
            meta = svg_metadata(size, args.mpp, fr, (map_w, map_h), crop, args.grid,
                                os.path.basename(path), extra)
            overlay, unmatched = overlay_layers(size, args.mpp, fr, edges, vehicles, labels, names)
            for key in unmatched:
                print("no edge between %s in the picture" % " and ".join("%x" % n for n in sorted(key)))
            under, over = depot_layers(args.mpp, fr, depot_rows, depot_specs, args.depots, args.coverage)
            station_under, station_over = station_layers(args.mpp, fr, station_rows, station_boxes)
            under += station_under
            over += station_over
            over += industry_layers(args.mpp, fr, industry_rows, args.industry_size, industry_faces)
            open(dest, "w").write(svg_document(png, size, args.mpp, fr, edges, widths, grid_step, meta,
                                               overlay, args.zoom, under, over, terrain, args.min_width,
                                               [] if rose_at == "off" else rose_layer(size, args.mpp, fr, rose_at, args.rose_size),
                                               args.grid_lines, args.grid_dot_step, grid_major))
            for i in depot_rows:
                print("depot slot %-6d %-22s x %8.1f y %8.1f facing %5.2f %5.2f"
                      % (i["slot"], short_model(i["model"]), i["x"], i["y"], i["fx"], i["fy"]))
            for i in industry_rows:
                print("industry slot %-6d %-18s x %8.1f y %8.1f" % (i["slot"], i["key"], i["x"], i["y"]))
            for v in vehicles:
                print("vehicle slot %-6d %-28s x %8.1f y %8.1f facing %5.2f %5.2f"
                      % (v["slot"], short_model(v["model"]), v["x"], v["y"], v["fx"], v["fy"]))
        else:
            open(dest, "wb").write(png_with_view(png, view_attrs(size, args.mpp, fr, (map_w, map_h), crop, None,
                                                                 os.path.basename(path))))
        print("%s  %d x %d px, %d m/px, map %d x %d m%s, %d road and %d rail edges%s"
              % (dest, size[0], size[1], args.mpp, map_w, map_h, ", cropped" if crop else "", roads, rails,
                 ", %d vehicles" % len(vehicles) if args.vehicles else ""))


if __name__ == "__main__":
    main()
