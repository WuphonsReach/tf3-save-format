# The game's profile files

The files outside the saves that decide what goes into a new save: the game's `settings.lua`, which remembers the last New Game choices, and the named mod presets of the Mods tab. They sit in the game's `local/` folder in Steam userdata, next to `save/` and `save_maps/` ([editor-saves.md](editor-saves.md)). They are not part of the save format, but the values a new game starts with come from them. Checked on format 605 unless a line says otherwise, on one player's profile.

## In short

- **`settings.lua` remembers the last New Game screen (Observed, 605, one profile).** Its `mainMenuState` table keeps the game settings and the mod options in the shape of a save's params list ([mods.md](mods.md#mod-options)), the terrain sliders that no save stores, and the seed, start year and terrain generator.
- **A game started from the main menu got the remembered mod options (Observed, 605, one game).** The one mod with an entry in the profile had exactly those values in the new save.
- **A named preset is a file of its own (Observed, 605, four files).** `mod_presets/<name>.preset.lua` holds a mod list and a params table of the same shape, with an entry for every mod.
- **Open.** Why the profile kept options for only one mod of 26 and listed only one active mod; when the game writes these tables (on start, on leaving the dialog, on Load Game); whether loading a preset overwrites them.

## `settings.lua`

A Lua file whose `data()` returns one table, about 140 keys on 605. Most are graphics, audio, unit, camera and notification settings. Keys that bear on saves:

- `autosaveIntervalMinutes` and `autosaveKeepNumber`: how often the game autosaves and how many autosaves it keeps. What the interval counts is in [calendar.md](calendar.md#the-game-clock).
- `crashSaveEnabled` and `crashSaveSingleFile`: whether the game writes a save when it crashes ([header.md](header.md#preview) has the crash save's empty preview).
- `mainMenuState`: the remembered New Game choices, below. There is no calendar speed key ([calendar-speed.md](calendar-speed.md)).

### `mainMenuState`

| Table | What it holds |
|---|---|
| `activeModsParamsState` | Keyed like a save's params list. `[""]` holds the game settings, the same keys as a save's settings entry less `isMapEditor` ([settings.md](settings.md)). Other entries are keyed by mod id and hold that mod's options as list positions plus 1. |
| `activeModsState` | A list of mod ids. |
| `mapGenParamsState` | The terrain generator's sliders: `islands`, `lakes`, `mountains`, `ocean`, `oceans`, `swamps`, `water`, plus keys a generator mod adds (`mz_islands`, `mz_layout` from Mapzilla, [terrain.md](terrain.md)). No save stores them. |
| `newGameState` | `seed` (a string), `startYearIndex` and `terrainGenerator`, a resource path of the form `<mod id>::/<path>.gen`. |

- **Which mods get an entry (Open).** Only one mod had an entry under `activeModsParamsState`, with its five keys, while the last new game had 26 mods. The mods without one may have been left on their defaults, which would mean the table keeps only changed values, but the game settings under `[""]` are all there, defaults included. Checking each missing mod's `defaultIndex` against the new save would settle it.
- **What `activeModsState` tracks (Open).** It held only the Deluxe Upgrade pack's id (`urbangames_deluxe_upgrade_pack`) though the last new game had 26 mods.
- **Mods can keep menu state here (Observed).** A mod's own table (`deadeye_vehicle_pull_stats`) sits beside the four above. That is all it shows: one mod used the place.

## Mod presets

**Save Preset on the Mods tab writes one file per preset (Observed, 605, four files),** `mod_presets/<name>.preset.lua` in the same `local/` folder, where the name is the one typed. Its `data()` returns a table with two keys:

- `modParams`: the same shape as `activeModsParamsState`, with `[""]` for the game settings and one entry per mod. Unlike the profile, every mod of the preset has an entry: an empty table for a mod without options, all its keys for a mod with options.
- `mods`: the list of mod ids in the preset.

## Open

- When `activeModsParamsState` is written: on starting a new game, on closing the gear dialog, or also on Load Game.
- Whether Load Preset writes into `mainMenuState`.
- Why only one mod had options in the profile and only one id was in `activeModsState`.

## Evidence and tests

- **One profile, 605 (2026-11-08).** Keys and table shapes read from the player's `settings.lua` and four preset files; values were not copied here. The preset files held 4, 10, 11 and 21 mod ids.
- **Profile against a new save (Observed, 605, one game).** A dry game started from the main menu on an editor map. Its save held exactly the five values of the `best_before_1` entry in the profile (`bestBefore.bonusDownTo` 12, `breakeven` 10, `freshPay` 3, `penaltyBelow` 7, `spoiledPay` 19). The other mods' values looked like defaults, not checked against their `mod.json`.
