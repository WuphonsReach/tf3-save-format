# Animals

The list of the map's animals, which animals they are, and how many. Cases A to G are the test saves of [terrain.md](terrain.md#what-was-compared). All of it is **Observed** on 604 unless marked.

About 283 KB after the header, after the tables of resource names (models, cargos, edge add-ons; the last name is an edge add-on such as `barrier_track_b.edge`), there is a list of the map's **animals**. This was found by comparing saves and then matching the layout to the `Animal` record in the game's `api/tealdef/api/engine.d.tl`; the field order and the values agree. **Observed** on 604 in three desert saves (B, D, E) and two temperate ones.

Layout, all little-endian:

| Part | Content |
|---|---|
| prefix | `u32 1`, `u32 0xffffffff`, a `u32` that differs between maps (49, 50 and 51 seen), `u32 0`, then `u32 N`, the number of animals |
| each animal | 15 values of 4 bytes, then `vec<vec3 f32>` (a `u32` count and 12 bytes per item) |

The 15 values, in the order of the `Animal` record:

| Index | Field | Seen |
|---|---|---|
| 0 to 2 | `worldPosition` x, y, z (metres) | x within about plus or minus 900, y within about plus or minus 3000; z is the ground height, or a fixed height above it for the first 13 (see the list below) |
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
- z follows the terrain. Checked against the [heightmap](terrain.md#the-heightmap) in nine saves: every animal after the first 13 stands on the ground (within 0.4 m of a straight interpolation between grid points), and the first 13 sit at a fixed height above it, 60 m on the desert map and 40 m on the temperate one (one of them is 1 m off in three saves). The first 13 are also the ones with a speed and a turn rate in a fresh save; the others start at speed 0 and only move after time has run (E). The first 13 are birds (see [which animals](#which-animals-they-are)), and the height above the ground is the bird model's `heightOffset`. The first animal's z followed the Mountains slider (123 m on Sparse, 154 on Scattered, 226 on Dense, 227 on Packed) because the ground under it did.
- Save A, the one without the mod, has 26 animals (13 and 13) where B to G have 39. The extra 13 are bison from the Deluxe Upgrade mod (see [which animals](#which-animals-they-are)).
- On the temperate map, Lakes Packed against Lakes Sparse moved some animals by under a metre and changed their direction, which fits animals being put somewhere slightly different, not a change of the animals themselves.
- The animal list is not the heightmap; that is a separate grid, described in [terrain.md](terrain.md#the-heightmap).

Find it by the prefix `01 00 00 00 ff ff ff ff ?? 00 00 00 00 00 00 00`, then the count, at the end of the name tables; the first match after the model table is the one. The `??` byte was 50 (`32`) in every save of seed `ktb5aEVwZg`, desert and temperate, 49 (`31`) in a desert save of seed `sJn73SmfYh` and 51 (`33`) in the tropical saves of seed `RaazVnK55w`; what it holds is **Open**. What the second list of `u32` after the animals holds (it starts with the same count, then 16 and a short list of numbers up to about 3,100) is **Open**.

### Which animals they are

The `Animal` record has no model. Each animal also has a model instance ([models.md](models.md#the-model-instance-record)), and its model id indexes the model table at the start of the stream. **Observed** on 604 in eighteen test saves: A to G, a desert save of another seed, the temperate pair and eight tropical saves of one seed.

- **The model table** at the start of the stream maps a model id to a path ([models.md](models.md#the-model-table)). The 28 models under `animal/` are ids 0 to 27 and a mod's follow, for example `urbangames_deluxe_upgrade_pack` with `animal/bison/bison.mdl` and `animal/boar_m/boar_m.mdl`.
- **The link.** There is one record per animal, in the same order as the animal list, in the layout of [models.md](models.md#the-model-instance-record). The model id of the animal is the `u32` 52 bytes before its position.
- **What they are**, in list order:

| Map | Animals |
|---|---|
| Desert, no mods (A) | `bird_eagle`, `cougar` |
| Desert, Deluxe Upgrade (B to G) | `bird_eagle`, `cougar`, `bison` (mod) |
| Temperate, Deluxe Upgrade | `bird_crane`, `wildlife_bear`, `wildlife_deer`, `wildlife_fox`, `wolf`, `boar_m` (mod) |
| Tropical, Deluxe Upgrade | `bird_crane` 13, `bird_gull` 4, `cr_fish_01` to `_04` 7, 8, 7 and 9, `wildlife_fox` 13, `comodo_dragon` (mod) 13 |

Each species on the desert and temperate maps has exactly 13, and so does the desert save of the other seed. The count is explained [below](#how-many-animals).

The 26 temperate animals with flock offsets are the cranes and the boars.

The model files' metadata matches the values in the animal list (`base/content/animal.zip`, read for these facts only): `bird_eagle.mdl` has `heightOffset` 60 and a flying speed of 4.5 at 80 degrees per second, `bird_crane.mdl` has `heightOffset` 40, speed 4 at 40 degrees and a flock name, and the base game's ground animals (`cougar`, `wildlife_bear`, `wildlife_deer`, `wildlife_fox`, `wolf`) have `heightOffset` 0; the mod's model files were not read. The water animals in the archive (`fish_salmon`, `cr_fish_01` to `_04`) have `heightOffset` -1.6. Only the tropical saves hold fish. Which species a climate picks is **Open**.

### How many animals

The count follows a density per km², not the seed. Facts from the game's files: `base/mod.script.tl` in `base/content/base.zip` sets `baseConfig.animal` with `populationDensityMultiplier = 1`, `useLocalSpawning = true` and `localTileSize = 1000`. The `BaseConfig.Animal` record in `api/tealdef/api/type.d.tl` describes the multiplier as applying to each animal's density in exemplars per km², and local spawning as filling boxes of `localTileSize` squared. In `animal.zip` every land and bird model above has `density` 1, `cr_fish_01` to `_04` have 2 each, and `fish_salmon` has 4.

- **Where the habitat allows it, a species reaches its density times the map area.** The Tiny map is 2.048 x 6.144 km = 12.58 km², so density 1 gives 12.6, and every density-1 land or bird species has 13: eagle, cougar, crane, bear, deer, fox, wolf, and the mod's bison, boar and Komodo dragon (their model files were not read, so their density of 1 is inferred). The same 13 in a desert save of another seed shows that the seed does not set the count. Whether the game rounds up or to the nearest whole number cannot be told from 12.58. **Observed**, 604, Tiny only.
- **Water animals fall short.** On the tropical map the gull (density 1) has 4, not 13, and the four discus models (density 2 each, so 25 each by area) have 31 between them. Each model has a block of spawn weights (`bias`, `civilisation`, `fish`, `forest`, `predator`, `ship`, `shore`, `water`). The discus fish have `bias` -2000, `shore` -5000 and `water` 2001; the gull has `water` 300, `shore` 200 and `ship` 60000; the fox (the one land animal whose block was read) has -1000 for `water`, `shore` and `ship`. So the density is a target that the habitat can hold a species below. How the weights turn into a count, and how much water the tropical map has, are **Open**.
- **Not herds.** The 13 are separate animals spread over the whole map; a herd or flock is one entry with `flock` offsets. `animal/animal.script.lua` only shapes those flocks (a crane V of 3 to 5 birds per side, a discus school of 10 to 15 fish, each a random one of the four models) and sets no count.

To confirm, a Small or Medium game saved at once should hold about its area in km² (from the header's map size) of each land species. **Open** until then.

## Open

- What the second list of `u32` after the animals holds.
- How the animal count scales with map size. Only Tiny was checked, see [how many animals](#how-many-animals).
- Which species a climate picks.
