# Terrain, the seed and the map sliders

What a save holds of the generated map, found by comparing saves of one seed. All of it is **Observed** on format 604 (Tiny 1 : 4, a 2 x 6 km map, start year 1900), from one save per case, so none of it is **Confirmed**. Sizes are counted from the end of the header (see [header.md](header.md)) to the end of the stream. The terrain record and the heightmap are described [below](#the-terrain-record).

## What was compared

| Case | What changed from the one before |
|---|---|
| A | New game, seed `ktb5aEVwZg`, Lakes Medium, Rivers Scattered, Mountains Scattered, no mods. Saved at once. |
| B | The same seed and settings again. The game listed one mod (Deluxe Upgrade), so the mod list differs from A. |
| C | B with only Mountains moved to Sparse. |
| D | C with only Mountains moved to Packed. |
| E | D loaded and run to 12 Jan 1900 (4000 ms per day, 11 days), then saved paused. |
| F | A new game as in B, but Mountains Dense (between Scattered and Packed on the slider). |
| G | F again with only Lakes moved from Medium to Packed, saved at once. |

The header differs between cases only in the save counter and, between A and B, the mod list. The sliders do not show up there, so they are not stored in the header.

## Results

- **The same seed and sliders give the same bulk (A against B).** About 92% of the body matches byte for byte, including every large block. It shifts by a few KB at several points, where variable-length data differs.
- **A moved slider changes nearly all of it (B against C).** The first 283 KB after the header are identical. After that about 88% of the bytes differ over the next 6.2 MB, a stretch that has the same length in both saves. Later stretches shift by +207 KB and +116 KB, so C is 354 KB longer than B.
- **The body length does not follow the slider (B, C, D, F).** The body is 14.99 MB for Sparse, 14.64 MB for Scattered, 19.31 MB for Dense and 16.96 MB for Packed. F against D, and F against B, differ from byte 282,774 on as well (98% of the 4 KB blocks differ in both). D against C first differs at the same place as B against C (byte 282,774), then shifts by +149 KB near 6.7 MB, -48 KB, -441 KB near 7.1 MB, and +2.0 MB twice from 13.1 MB.
- **Lakes did nothing on a desert map (F against G).** The headers are identical, the bodies have the same length, and 35 of 4,714 4 KB blocks differ (35,937 bytes in 153 short stretches, 100 KB of them at the very end of the data; none in the four simulation arrays). The terrain, the animals and everything between are identical. The New Game preview showed no lakes at Packed either. One pair, **Observed**.
- **Time changes only simulation state (D against E).** 258 of 4,140 4 KB blocks differ. They are one stretch of about 800 KB (four arrays of about 200 KB of tiny floats, around 1e-15, with long runs of one value) and six stretches of 16 to 33 KB. The same four arrays are the only large difference between A and B. The rest, terrain included, is identical.

## The animals (first component after the name tables)

About 283 KB after the header, after the tables of resource names (models, cargos, edge add-ons; the last name is an edge add-on such as `barrier_track_b.edge`), there is a list of the map's **animals**. This was found by comparing saves and then matching the layout to the `Animal` record in the game's `api/tealdef/api/engine.d.tl`; the field order and the values agree. **Observed** on 604 in three desert saves (B, D, E) and two temperate ones.

Layout, all little-endian:

| Part | Content |
|---|---|
| prefix | `u32 1`, `u32 0xffffffff`, `u32 50`, `u32 0`, then `u32 N`, the number of animals |
| each animal | 15 values of 4 bytes, then `vec<vec3 f32>` (a `u32` count and 12 bytes per item) |

The 15 values, in the order of the `Animal` record:

| Index | Field | Seen |
|---|---|---|
| 0 to 2 | `worldPosition` x, y, z (metres) | x within about plus or minus 900, y within about plus or minus 3000; z is the ground height, or a fixed height above it for the first 13 (see below) |
| 3, 4 | `lookingAt` (a unit vector) | |
| 5, 6 | `targetCoord` x, y | 3 to 4 m from the position when an animal has just been placed |
| 7 | `movementSpeed` | 4.5 on the desert map, 4.0 on temperate, 1.0, 2.0 and 4.0 later in play |
| 8 | `angularSpeed` (radians per second) | 1.396 (80 degrees) or 0.698 (40 degrees) at first, 1.047 and 2.618 later |
| 9, 10 | `lastUpdateElapsed`, `targetChangedElapsed` (seconds) | 1.0 or 0.8 at once; 43 after the 11-day run |
| 11 | `invalidTileElapsed` | 0 |
| 12 | `movementType` (integer) | 0 |
| 13, 14 | `roll`, `scaling` | 0.04 or 0.05, 1.0 |

The trailing `vec<vec3>` is the `flock`: an offset for each further animal of a herd, relative to the position. It is empty for every animal on the desert map (39 animals) and has 4 to 10 offsets for 26 of the 78 animals on the temperate map. The offsets are a few metres in x and y with z 0 (for example -1.4 / 1.4 and -2.8 / 2.8).

The list parses cleanly with this layout in all five (39 animals on the desert map, 78 on the temperate one; the other desert saves have the same count prefix), and another component with the same count follows it.

What this explains:

- The positions move: 17 of 39 desert animals were more than 50 m away after the 11-day run (D against E), and a save made a few seconds after another differs by a few metres. So the animals' places are not fixed by the seed, and the "feature points" I first took them for were animals.
- z follows the terrain. Checked against the heightmap (below) in nine saves: every animal after the first 13 stands on the ground (within 0.4 m of a straight interpolation between grid points), and the first 13 sit at a fixed height above it, 60 m on the desert map and 40 m on the temperate one (one of them is 1 m off in three saves). The first 13 are also the ones with a speed and a turn rate in a fresh save; the others start at speed 0 and only move after time has run (E). So the first 13 are probably flying animals (**Open** until the models are known). The first animal's z followed the Mountains slider (123 m on Sparse, 154 on Scattered, 226 on Dense, 227 on Packed) because the ground under it did.
- Save A, the one without the mod, has 26 animals (13 and 13) where B to G have 39. Whether the mod or something else sets the count is **Open**.
- On the temperate map, Lakes Packed against Lakes Sparse moved some animals by under a metre and changed their direction, which fits animals being put somewhere slightly different, not a change of the animals themselves.
- The animal list is not the heightmap; that is a separate grid, described below.

Find it by the prefix (`01 00 00 00 ff ff ff ff 32 00 00 00 00 00 00 00` and then the count) at the end of the name tables. Which animals (models) they are, and what the second list of `u32` after the animals holds (it starts with the same count, then 16 and a short list of numbers up to about 3,100), are **Open**.

## The terrain record

The fields match the `Terrain` record in `api/tealdef/api/engine.d.tl`, in its order. **Observed** on 604 in eighteen test saves (eight desert, two temperate, eight tropical; all Tiny, 2048 x 6144 m), 5.2 to 7.5 MB after the header:

| Field | Type | Seen |
|---|---|---|
| `size` | 2 x `u32` | 8, 24: the map in tiles of 256 m (2048 / 256, 6144 / 256) |
| `baseLevels` | `u32` | 6 |
| `baseResolution` | 3 x `f32` | 4.0, 4.0, 0.05: metres per grid step in x and y, metres per height unit |
| `highLevels` | `u32` | 8 |
| `offsetZ` | `f32` | -100.0 |
| `waterLevel` | `f32` | 0.0 |
| `dataMaps` | `vec` of (`str` name, `u32` w, `u32` h, `vec<f32>` of w x h) | 9 to 11 maps of 64 x 192, one value per 32 m |

Find it by the resolution, `00 00 80 40 00 00 80 40 cd cc 4c 3d`; the two `u32` of the size sit 12 bytes before it. On this map:

```
08 00 00 00 18 00 00 00 06 00 00 00 00 00 80 40 00 00 80 40 cd cc 4c 3d
08 00 00 00 00 00 c8 c2 00 00 00 00 0b 00 00 00 0a 00 00 00 72 69 76 65 72 5f 6d 61 73 6b
```

The data maps are named by the climate's generator. Desert (`dry`): `river_mask`, `lakes`, `mesas`, `coast_hills`, `mountains`, `monument_valley` and `biome0` to `biome4`. Temperate: `forest_mask`, `river_mask`, `biome4_mountains`, `biome4_no_mountains` and `biome0` to `biome4`. Tropical: `highway`, `forest_mask`, `volcano`, `mountains` and `biome0` to `biome4`. The `biome` maps hold weights from 0 to 1; `mesas`, `mountains` and `monument_valley` hold values up to about 195. Their order is not fixed (`biome0` and `mountains` swap places between B and C). What each map does in the game is **Open**.

Moving Mountains from Scattered to Sparse (B against C) changed `mesas`, `mountains` and three of the biome maps; on Sparse `mesas` and `mountains` are all zero. Lakes changed none of them on either climate (F against G, and the temperate pair).

## The heightmap

The ground height is a grid of `u16` per tile, matching the `TerrainTileHeightmap` record in `api/tealdef/api/engine.d.tl` (a list of integers per 256 m tile on a 4 m grid). **Observed** on 604 in the same eighteen saves, all with 192 tiles.

| Part | Content |
|---|---|
| prefix | `ff ff ff ff 0e 00 00 00` and 12 zero bytes |
| count | `u32`: the number of tiles, `size` x times y (192 here) |
| each tile | `vec<u16>` of 4225 values (65 x 65), 8,454 bytes |

- **Order.** Tiles go in rows along x: tile `ty * 8 + tx`. Inside a tile, value `r * 65 + c` is column c (x) of row r (y). Each tile has 65 points per side, so it repeats the last row and column of its neighbours; in every save checked, all 352 shared edges match exactly. Stitched together this gives a 513 x 1537 grid.
- **Position.** Grid point (c, r) of the whole map is at x = -1024 + 4c, y = -3072 + 4r, the map's centre being 0, 0. This orientation (not flipped) is the only one that puts the animals on the ground.
- **Height.** z = `offsetZ` + v x `baseResolution` z, so z = -100 + 0.05 v metres, and v = 2000 is the water level. The non-flying animals all fall on this to within 0.4 m (see above). Heights seen: 0.8 to 262 m on the desert map with Mountains Dense, 1.6 to 142 m on Sparse, 0.15 to 478 m on the temperate map.
- **What changes it.** The grid is identical for the same seed and sliders (A against B), after 11 days of play (D against E), and with Lakes moved (F against G, and the temperate pair). Mountains Scattered against Sparse (B against C) changes 45% of the values; another seed changes nearly all.

Find it by its count and first length together, `c0 00 00 00 81 10 00 00` here (192 and 4225), then step 8,454 bytes per tile. It ends 0.46 to 0.63 MB before the end of the stream in these saves, long after the terrain record.

The map format setting does not change the grid here: the tropical saves store `map.format` 3 and the others 4, and both have 8 x 24 tiles of 2048 x 6144 m (**Observed**, Tiny only).

## Lakes on a temperate map

Two new games on the stock Temperate generator (see below), seed `ktb5aEVwZg`, Tiny 1 : 4, Rivers Scattered, Mountains Dense, European names, saved at once: one with Lakes Sparse, one with Lakes Packed. **Observed**, 604, one pair.

- The headers are identical, but the body is 10,784 bytes longer with Lakes Packed (13,976,271 against 13,987,055).
- 257 of 3,412 4 KB blocks differ, against 35 for the same change on a desert map. About 195 of them are the simulation arrays (the stretch near 0.67 to 1.48 MB), which also differ on a desert map when the two saves are made at different moments, so they do not count as an effect of Lakes.
- The rest: a stretch of about 650 KB (3.48 to 4.12 MB) that starts with one record whose count changes from 2 to 1 and then runs shifted by the length change, so most of its bytes differ, and short differences (55 bytes each, about 150 bytes apart) in the list of 78 animals that starts 283 KB after the header, where an animal's position moved by under a metre and its direction changed.
- So Lakes does something on a temperate map (it changes how much data the save holds) and nothing on a desert map. The heightmap and the terrain data maps are identical in the two saves (see [below](#the-terrain-record)), so the extra 10.8 KB are not terrain shape; what they are is **Open**.

## Generators and the Mapzilla mod

On a temperate New Game screen a **Generator** dropdown appears (not on the desert screen). It comes from the Mapzilla mod (mod.io 6423494, source <https://github.com/AmbachtIT/mapzilla>), which ships generator files of its own. Read from the mod's files, not from a save: its `mod.json` has `"cosmetic": true` and `"autoActivate": false`, it adds a generator under `climates/mapzilla/` whose climate is the stock `temperate.clima`, and that generator has sliders keyed `mz_layout` (Layout: Random, Single shore, Island, Inland sea, Isthmus, Strait, Peninsula, Bay), `mz_coast` and others. So the `mz_*` keys that the game's user settings file keeps for the New Game dialog belong to this mod, not to the stock generators.

A game made with the stock **Temperate** generator while the mod was installed (one save, 604) lists only Deluxe Upgrade in its header mod list and has no sign of Mapzilla, so installing it adds nothing to the save (**Observed**). What a save lists when a Mapzilla generator is chosen is **Open**.

## Open

- What `baseLevels` (6) and `highLevels` (8) mean, and whether the heightmap has coarser levels stored elsewhere. 1.5 MB to 6.1 MB after the header is still float-like records (periods of 24, 72 and 73 bytes) of unknown purpose.
- The list that follows the heightmap. It also starts with the tile count (`c0 00 00 00 16 00 00 00 ...`). The API has a per-tile brush record (`TerrainTileBrush`); that this list is it is a guess.
- How the tile count follows map size and format; only Tiny was checked.
- Which animal models the list holds, and what the list after it holds.
- Whether the Ocean and Islands sliders change the same stretches as Mountains, and what Lakes and Rivers do. The Desert (dry) generator in the game's `climates` data lists exactly three sliders, keyed `lakes`, `water` (shown as Rivers) and `mountains`, five steps each with Medium the default, and its node graph has nodes named for lakes, so the Lakes slider is wired in, but moving it from Medium to Packed changed nothing on the desert map (see F against G); whether any desert map ever shows a lake is **Open**.
- Whether the seed alone, with sliders at their defaults, gives the same map as the New Game screen.
