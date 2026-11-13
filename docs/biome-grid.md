# The biome and layer grid

Most saves hold a second grid on the heightmap's points: one `u16` per 4 m point that records the biome and the climate's data layers (rivers, mountains, swamps and so on) the map generator assigned there. It is as large as the heightmap, so 8 to 33 MB in the saves checked. Labels as in [README.md](README.md#evidence-labels).

## In short

- **One `u16` per heightmap point, in a single grid, not in tiles (Observed, 601 to 605).** It has the same points and row order as the stitched heightmap in [terrain.md](terrain.md#the-heightmap). A header of three `u32` (width, height, width x height) comes before it.
- **The low four bits are the biome id, 0 to 4 (Observed, 604 and 605).** The biome id follows the `biome0` to `biome4` weight maps of the terrain record ([terrain.md](terrain.md#the-terrain-record)). It matched the strongest weight at 94% of points on a fresh map and 51 to 80% on others. Where `biome4` is strongest the id steps up with height, so it is not just the strongest weight. The exact rule is **Open**.
- **Bit 4 + n is the climate's data layer with id n (Observed on temperate, subarctic and dry, 604 and 605).** The layers and their ids are in each climate's `dataMaps.layers` list (below). Wherever a flag was off, the matching 32 m mask in the terrain record read 0.000 to 0.001.
- **The grid is fixed when the map is made (Observed, two pairs).** Sculpting in the map editor changed 698,266 heightmap points and no grid point. Twenty game years of play changed none either.
- **Some saves have no grid (Observed, 3 saves).** A generated tropical map with 20 mods, a campaign mission map and a published subarctic map have none. Why is **Open**.
- **Open:** what the game uses the grid for, the rule for the biome id, and why some saves lack it. The climate's ground-material tree has `material_index_output` nodes that read the biome masks, so ground materials are a guess.

## Finding and reading it

Read the tile counts from the terrain record, then search for the header: `u32` width = 64 x tiles in x + 1, `u32` height = 64 x tiles in y + 1, `u32` their product. Then width x height `u16` follow, row by row, y rising from row to row and x rising along a row. On an 18 x 54 tile map (1153 x 3457 points) the header and first values are:

```
81 04 00 00 81 0d 00 00 01 d2 3c 00 01 00 01 00 01 00
```

The grid sat 37% to 53% into the stream, well before the heightmap. Zero bytes come before the header; what follows the grid was not traced. `read_biome_grid` in [terrain_heights.py](../tools/terrain_heights.py) reads it, and `terrain_heights.py SAVE` prints the share of points per biome and per layer. [stream_coverage.py](../tools/stream_coverage.py) counts it among the read structures.

### The layer bits per climate

From `dataMaps.layers` in `climates/<climate>/<climate>.clima.lua` (`base/content/climates.zip`, 604 build). The layer with id n sets bit 4 + n.

| Climate | Bit 4 (16) | Bit 5 (32) | Bit 6 (64) | Bit 7 (128) | Bit 8 (256) |
|---|---|---|---|---|---|
| temperate | `rivers` | `mountains` | | | |
| subarctic | `swamps` | `lakes` | `mountains` | | |
| dry | `rivers` | `coast_hills` | `monument_valley` | `mountains` | `mesas` |
| tropical | `volcano` | `mountains` | `islands` | | |

The terrain record's mask maps carry other names (`river_mask`, `biome4_mountains`, `swamp_mask`, `mountain_mask`, `monument_valley`). The tropical bits were not checked against a save.

## Evidence and tests

The grid turned up as the largest unaccounted block of small `u16` values in [stream_coverage.py](../tools/stream_coverage.py) at commit 2cc2e55. In each save the block was as large as the heightmap. All checks used every fifth point in x and y.

### The biome id and the layer flags (604 and 605)

**Observed.** Each grid point was matched to the 32 m data map cell it lies in.

| Save | Version, climate | Grid | Biome id = strongest weight | Flags against masks |
|---|---|---|---|---|
| catalog [6417290](https://mod.io/g/transportfever3/m/akgame) | 604 temperate, start date | 1153 x 3457 | 94% | 16 (`rivers`): `river_mask` 0.79 on, 0.000 off; 32 (`mountains`): `biome4_mountains` 0.73 on, 0.000 off |
| catalog [6429195](https://mod.io/g/transportfever3/m/hometown-of-overseas-chineseli-shui-city1) | 604 temperate, 11 mods, played | 2049 x 2049 | 51% | the same two, 0.001 and 0.000 off |
| catalog [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1) | 604 temperate, played | 2817 x 5633 | 79% | the same two, 0.001 and 0.000 off |
| own Small subarctic game, last save (1920) | 604 subarctic | 1153 x 3457 | 75% | 16 (`swamps`): `swamp_mask` 0.31 on, 0.000 off; 64 (`mountains`): `mountain_mask` 0.97 on, 0.001 off; 32 (`lakes`): 76% of its points below the water level (no lakes mask stored) |
| catalog [6436878](https://mod.io/g/transportfever3/m/new-game-af) | 604 dry | 3585 x 3585 | 75% | only 64 (`monument_valley`) set: that map 26.4 on, 0.002 off; the other masks all zero on this map |
| own giant dry editor map (1108-1233) | 605 dry | 4097 x 12289 | not checked | bits 4 (`rivers`) and 6 (`monument_valley`) set, not checked against masks |

- **The biome ids are height bands.** On 6417290, biome 0 lay under water (median -99 m), 1 at 2 m, 2 at 51 m, 3 at 89 m and 4 higher up. The share of points per id matched the mean weight of each biome map (63.8% against 63.4% for biome 1, 17.5% against 17.3% for biome 2).
- **Where `biome4` is strongest, the id follows height.** On 6429195, points whose strongest weight was `biome4` read id 1 at a median height of 117 m, 2 at 166 m, 3 at 231 m and 4 at 276 m. At 40% of that map's points the id named a biome whose weight was 0.
- **The values are bit fields.** The commonest values were 1, 2, 0, 3, 33, 4 and 36 on the temperate maps, and 2, 68, 67, 3 and 18 on the subarctic one. No value had bits above the climate's highest layer.

### Edits and play leave it alone (604)

**Observed**, two pairs, compared point by point with `terrain_heights.py OLD NEW`.

- **Editor sculpting:** the pair in [terrain-edits.md](terrain-edits.md) (own giant temperate editor map, saves 1110 and 1111). 698,266 of 52.4 million heightmap points changed, by up to -57 m, and 0 grid points changed.
- **Play:** the first (1900) and last (1920) saves of the own Small subarctic game. Neither the heightmap nor the grid changed.

### Saves without a grid (601 to 605)

**Observed.** A grid header was found in three of five tropical saves: catalog [6445949](https://mod.io/g/transportfever3/m/no-cities) (604) and [6431135](https://mod.io/g/transportfever3/m/autosave-test-2-1966-11-12) (601), and two own tropical saves (604). None was found in:

- catalog [6422633](https://mod.io/g/transportfever3/m/na263651): 604, tropical, Medium 1 : 3, 20 mods.
- catalog [6430671](https://mod.io/g/transportfever3/m/19811): 604, the climate `mission6_tropical.clima`, the campaign mission mod in its mod list.
- catalog [6440375](https://mod.io/g/transportfever3/m/hatchet-river-valley-1945): 604, subarctic, no mods, and its re-save in 605.

None of the three is marked as a map-editor save. A search for the width and height as two `u32`, or for their product, found nothing in 6422633. So the grid is absent there, not stored in another shape.
