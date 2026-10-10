# Terrain, the seed and the map sliders

What a save holds of the generated map, found by comparing saves of one seed. All of it is **Observed** on format 604 (Tiny 1 : 4, a 2 x 6 km map, start year 1900), from one save per case, so none of it is **Confirmed**. Sizes are counted from the end of the header (see [header.md](header.md)) to the end of the stream. The terrain record and the heightmap are described [below](#the-terrain-record). The animals have a note of their own, [animals.md](animals.md).

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
- **Height.** z = `offsetZ` + v x `baseResolution` z, so z = -100 + 0.05 v metres, and v = 2000 is the water level. The non-flying animals all fall on this to within 0.4 m ([animals.md](animals.md)). Heights seen: 0.8 to 262 m on the desert map with Mountains Dense, 1.6 to 142 m on Sparse, 0.15 to 478 m on the temperate map.
- **What changes it.** The grid is identical for the same seed and sliders (A against B), after 11 days of play (D against E), and with Lakes moved (F against G, and the temperate pair). Mountains Scattered against Sparse (B against C) changes 45% of the values; another seed changes nearly all.

Find it by its count and first length together, `c0 00 00 00 81 10 00 00` here (192 and 4225), then step 8,454 bytes per tile. It ends 0.46 to 0.63 MB before the end of the stream in these saves, long after the terrain record.

The map format setting does not change the grid here: the tropical saves store `map.format` 3 and the others 4, and both have 8 x 24 tiles of 2048 x 6144 m (**Observed**, Tiny only; a Small 1 : 3 map has 18 x 54 tiles, see [below](#a-small-subarctic-map)).

## A Small subarctic map

One new game on the stock Subarctic generator, **Small** 1 : 3 (4608 x 13824 m), saved at once, format 604, Normal difficulty, seven mods. The sliders were Water Small, Swamps Medium and Mountains Dense, the seed was typed, and every value was read back against the New Game screen. **Observed**, one save, so it adds sizes and names but cannot tie a slider to a map.

- **The sliders are not stored.** The seed occurs once in the stream, in the header. None of the slider keys (`water`, `swamps`, `mountains`) occurs in it as a string of its own (`water` appears only inside longer words, `swamps` and `mountains` not at all). The generator file `climates/subarctic/subarctic.gen.lua` (in `climates.zip`) lists exactly these three, each with five steps and the third as default; Water runs Very Small to Very Large, the other two Sparse to Packed. The picks were steps 2, 3 and 4. Their effect is only in the generated data below, as on the other climates.
- **The terrain record** has the fields of [the table above](#the-terrain-record), starting 26.7 MB after the header: `size` 18 x 54 (4608 / 256 and 13824 / 256), `baseLevels` 6, the usual resolution, `highLevels` 8, `offsetZ` -100 and `waterLevel` 0. The eight data maps are 144 x 432 (one value per 32 m), as 4608 / 32 by 13824 / 32. Their names, in stored order: `forest_mask`, `biome3`, `biome1`, `biome4`, `biome0`, `mountain_mask`, `swamp_mask`, `biome2`. So this climate has a mask for mountains and one for swamps but none for water.
- **Their values.** All stay between 0 and 1 (`swamp_mask` up to 1.005). `mountain_mask` is non-zero in 38% of the cells, `swamp_mask` in 9.5%, `forest_mask` in 43%.
- **The heightmap** follows the layout of [the heightmap section](#the-heightmap) with 972 tiles (18 x 54) of 65 x 65 `u16`. Its count and first length are `cc 03 00 00 81 10 00 00`; it starts 54.4 MB after the header and ends 2.5 MB before the end of the stream. Heights run from -100 m (value 0, deep water) to 299.5 m; the median is 44 m, the 10th percentile -3 m and the 90th 197 m, and 11.7% of the points are below the water level (value 2000).
- **What the next saves would show.** Which map each slider moves needs three saves with this seed, each changing one slider. The Water slider is the unclear one, since no map carries its name.

## Lakes on a temperate map

Two new games on the stock Temperate generator (see below), seed `ktb5aEVwZg`, Tiny 1 : 4, Rivers Scattered, Mountains Dense, European names, saved at once: one with Lakes Sparse, one with Lakes Packed. **Observed**, 604, one pair.

- The headers are identical, but the body is 10,784 bytes longer with Lakes Packed (13,976,271 against 13,987,055).
- 257 of 3,412 4 KB blocks differ, against 35 for the same change on a desert map. About 195 of them are the simulation arrays (the stretch near 0.67 to 1.48 MB), which also differ on a desert map when the two saves are made at different moments, so they do not count as an effect of Lakes.
- The rest: a stretch of about 650 KB (3.48 to 4.12 MB) that starts with one record whose count changes from 2 to 1 and then runs shifted by the length change, so most of its bytes differ, and short differences (55 bytes each, about 150 bytes apart) in the list of 78 animals that starts 283 KB after the header, where an animal's position moved by under a metre and its direction changed.
- So Lakes does something on a temperate map (it changes how much data the save holds) and nothing on a desert map. The heightmap and the terrain data maps are identical in the two saves (see [below](#the-terrain-record)), so the extra 10.8 KB are not terrain shape; what they are is **Open**.

## Generators and the Mapzilla mod

On a temperate New Game screen a **Generator** dropdown appears (not on the desert screen). It comes from the Mapzilla mod (mod.io 6423494, source <https://github.com/AmbachtIT/mapzilla>), which ships generator files of its own. Read from the mod's files, not from a save: its `mod.json` has `"cosmetic": true` and `"autoActivate": false`, it adds a generator under `climates/mapzilla/` whose climate is the stock `temperate.clima`, and that generator has sliders keyed `mz_layout` (Layout: Random, Single shore, Island, Inland sea, Isthmus, Strait, Peninsula, Bay), `mz_coast` and others. So the `mz_*` keys that the game's user settings file keeps for the New Game dialog belong to this mod, not to the stock generators. The other mod notes are in [mods.md](mods.md).

A game made with the stock **Temperate** generator while the mod was installed (one save, 604) lists only Deluxe Upgrade in its header mod list and has no sign of Mapzilla, so installing it adds nothing to the save (**Observed**). What a save lists when a Mapzilla generator is chosen is **Open**.

## Open

- What `baseLevels` (6) and `highLevels` (8) mean, and whether the heightmap has coarser levels stored elsewhere. 1.5 MB to 6.1 MB after the header is still float-like records (periods of 24, 72 and 73 bytes) of unknown purpose.
- The list that follows the heightmap. It also starts with the tile count (`c0 00 00 00 16 00 00 00 ...`). The API has a per-tile brush record (`TerrainTileBrush`); that this list is it is a guess.
- How the tile count follows map size and format. Tiny 1 : 4 and 1 : 3 (8 x 24) and Small 1 : 3 (18 x 54) were checked; in all three it is the map's metres divided by 256.
- Whether the Ocean and Islands sliders change the same stretches as Mountains, and what Lakes and Rivers do. The Desert (dry) generator in the game's `climates` data lists exactly three sliders, keyed `lakes`, `water` (shown as Rivers) and `mountains`, five steps each with Medium the default, and its node graph has nodes named for lakes, so the Lakes slider is wired in, but moving it from Medium to Packed changed nothing on the desert map (see F against G); whether any desert map ever shows a lake is **Open**.
- Whether the seed alone, with sliders at their defaults, gives the same map as the New Game screen.
