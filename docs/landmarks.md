# Landmarks: construction sites and their modifiers

State of the script `landmarks/landmarks.gs`. Checked on 604, catalog save [6417707](https://mod.io/g/transportfever3/m/333151) in two states: as downloaded (paused on 17 April 2000, **A**) and a later manual save of the same game after a few weeks of play (**B**). Both were compared with the game's construction site window for the Summer Palace wonder. The script-state container is in [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md); the Lua encoding is in [lua-values.md](lua-values.md).

## Finding it

The path string `landmarks/landmarks.gs` has no `game_mechanics/` prefix. In both saves it sat close to the end of the stream (about 98%), among other script states. Seen in this order: `game_mechanics/celebrations/celebrations.gs`, `industries/industry_workers.gs`, `landmarks/landmarks.gs`, `mission/mission.gs`, `terrain/reforestation.gs`, `vehicle/vehicle_modifier.gs`. As for the subsidies state in [script-states.md](script-states.md), the body follows the path string as one byte, a u32 pair count and the pairs, with no leading tag 4. **Observed**.

The state was 996 bytes in both saves and has two keys.

## `entity2cargoType2count`

A table `site entity id -> cargo id -> amount`, all numbers f64.

- **Confirmed**: for the Summer Palace site, the stored amounts equalled the per-cargo progress the window showed, in both states. A: `{2: 264, 13: 264, 24: 528, 31: 264}` against 264/300 on three cargos and 528/600 on one. B: `{2: 267, 13: 267, 24: 534, 31: 267}` against 267/300 and 534/600.
- Cargo 13 is planks and 31 is furniture ([cargo-ids.md](cargo-ids.md)). The window's other two cargos were dyes and stone, and the stored 528 against 264 puts stone (needing 600, twice the others' 300) on id 24, which leaves dyes on id 2. That pairing is **Observed**, from the window's numbers alone.
- Between A and B only these four numbers in the whole state changed (+3, +3, +6 and +3). They equal what left the site's input stocks in the window: planks 56 to 53, furniture 97 to 94, stone 116 to 110. The dye stock went 0 to 2 while dye progress rose by 3, which fits 5 delivered and 3 used (the truck's window showed 5 of 30 dye on board before it unloaded). So the stock is used up one for one as progress. **Observed**, one delivery.
- The save held six more sites, with round totals: 200, 400, 600, 800, 1,000 or 1,200 per cargo. Whether these are finished sites was not checked. **Open**.
- The requirements (300 and 600 here) were not found as stored numbers. **Open**.
- The input stocks themselves (0/150 dyes, 56/150 planks, 116/300 stone, 97/150 furniture) were not found. Searching for the four values and capacities as f32, f64 or u32 close together found nothing in either save. They are probably in the site's entity data. **Open**.

## `town2carrier2modifiers`

A table `town entity id -> carrier id -> modifier name -> multiplier`. Seen in this save: `pollution` 0.8, `noise` 0.75, `comfort` 1.25 and `topSpeed` 1.2, across four town and carrier pairs. The site window said a finished Summer Palace "grants pollution reduction to all air vehicles within the municipal area", so these are most likely the effects of finished landmarks. It did not change between A and B, with the Summer Palace unfinished. Which carrier number is which, and which landmark gave which entry, was not worked out. **Open**.

## Not tested

- What completing a site writes. Both saves are from before the Summer Palace was finished.
- Whether other landmarks use the same table shape.
