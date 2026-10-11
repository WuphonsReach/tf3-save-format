# Gaps: header, settings, map and clock

Format of an entry: see [README.md](README.md).

## Seed, terrain and the map

- **Whether the seed alone rebuilds the map** (604) The sliders are not stored, so a rebuild would need the same sliders; whether default sliders reproduce the New Game screen's map is untested. Home: [seed.md](../seed.md), [terrain.md](../terrain.md#open). Needs: new save pair (two new games, same seed and sliders; then one with only Mountains changed), each saved at once.
- **Seed edge cases** (599 to 604) What `id` stores for an empty seed, 40 characters, spaces, accents or CJK. Home: [seed.md](../seed.md). Needs: new saves.
- **A map editor seed** (604) Whether a new editor map with a typed seed keeps it in `id`. Home: [seed.md](../seed.md), [editor-saves.md](../editor-saves.md). Needs: new save.
- **Map size against format** (604) Tiny 1 : 4, Tiny 1 : 3 (8 x 24 tiles) and Small 1 : 3 (18 x 54) were read; in all three the tile count is the map's metres divided by 256. Medium, and 1 : 1 at every size, are untested. Home: [terrain.md](../terrain.md#open), [header.md](../header.md). Needs: new saves (Tiny, Small, Medium at 1 : 1 and 1 : 3); header width and height already give the metres.
- **What the Ocean, Islands and Lakes and Rivers sliders change** (604) Lakes moved from Medium to Packed changed nothing on a desert map, yet the generator's node graph has lake nodes; whether any desert map ever shows a lake is open. Home: [terrain.md](../terrain.md#open). Needs: new save (Lakes on a temperate map, then Rivers on desert).
- **Which way the game means north** (604) The sun puts north at +x (or south at +x); a real-world editor map is laid by its maker and does not decide it. The sun's hemisphere and a few degrees of misalignment are untested. Home: [terrain.md](../terrain.md#which-way-is-north). Needs: a real map on a square size, or the editor's own import dialog.
- **The terrain values after the header** (604) What `baseLevels` and `highLevels` mean, what the float-like record stretch holds, and whether the list after the heightmap is the per-tile brush record. Home: [terrain.md](../terrain.md#open). Needs: existing saves and game files (`TerrainTileBrush` in the API definitions).
- **The 13 records of 16 floats** (604) Sites move between saves of one seed; whether the 13 are the first kind in a longer list (count prefix 0x27 or 0x4e) is unknown. Home: [terrain.md](../terrain.md). Needs: existing saves.
- **What the climate changes on load** (604) Whether the terrain and existing industries change when the climate is switched on the Load Game screen. Home: [settings.md](../settings.md#open). Needs: new save pair.

## Settings

- **Whether setting changes act in play** (604) For example on buildings that already exist. See also [vehicles-and-costs.md](vehicles-and-costs.md#running-costs-and-upkeep). Home: [settings.md](../settings.md#open). Needs: new save.
- **Whether a loaded save stays byte for byte as it was** (604) The first test save was not hashed before its load. Home: [settings.md](../settings.md#open). Needs: new save (hash first, load, hash the same file again).
- **Where "Achievements cannot be earned" is kept, if at all** (604) Suggested: diff the script states of a New Game save against one loaded with six options changed. Home: [settings.md](../settings.md#open). Needs: existing saves.
- **What `sensitivityUrbanCare`, `cargoNeedsPerTown` and `trafficSpeedSensitivityScale` appear as on a screen** (604) `sensitivityUrbanCare` is the unverified pairing for the Reputation toggle. Home: [settings.md](../settings.md#open). Needs: new save with the toggle changed.
- **Whether the other presets change the sliders at 100%** (604) Population, passenger and cargo income stayed at 100% across all four presets, and only Easy moved them. Home: [settings.md](../settings.md). Needs: game window.
- **A mod with options removed on load** (604) Whether the options go with it. Home: [mods.md](../mods.md#open). Needs: new save.

## Calendar and clock

- **Whether the calendar speed changes how many clock units a year spans** (604) All saves seen were at 1.00x; the year-to-tick mapping across speed changes is untested. Home: [calendar-speed.md](../calendar-speed.md), [calendar.md](../calendar.md). Needs: new saves across a speed change.
- **The Paused setting in the game** (604, one game) Home: [calendar-speed.md](../calendar-speed.md). Needs: new save.
- **Whether a stored duration follows the speed at the time of looking** (604, 0.50x only) Home: [calendar.md](../calendar.md). Needs: game window at another speed.
- **What `t2` is** (568 to 604) It equals `t1` in a paused save and trails it by 200 times `playSpeed`. Home: [calendar.md](../calendar.md). Needs: existing saves.
- **Catalog calendars that do not fit** (568 to 604) One save at a speed of 1,440,000 that is not a slider step; three saves whose header start year and table's first day disagree; tables with jumps or backward steps. Home: [calendar.md](../calendar.md). Needs: existing saves.
- **Whether difficulty scales time** (604, one game) A difficulty setting that scaled time would give the same factor as the calendar speed. Home: [calendar.md](../calendar.md). Needs: new save on another preset.
- **What the autosave interval counts, and clock gaps between saves** (604) Wall-clock gaps of 54 and 16 minutes gave 10 and 8 minutes of game clock; two saves 16 wall-minutes apart differed by only 62 seconds of game clock. Home: [calendar.md](../calendar.md). Needs: new saves with the interval and pauses logged.

## Mods

- **Whether a deactivated mod with options loses them** (604) Only mods without options were switched. Home: [mods.md](../mods.md#open). Needs: new save.
- **Whether mod options follow the position-plus-1 rule** (604) And what `flags` in a mod entry (0, 1 or 2) means. Home: [mods.md](../mods.md#open). Needs: new save with a mod that has options.
- **What a mod adds to the script states once it has run** (604) Whether any stream difference in the Overpass Builder test is mod related was not checked. Home: [mods.md](../mods.md#open). Needs: existing saves.

## Script states and the stream

- **The tail of the script-state block, and where four states are declared** (604) Details in the home note. Home: [lua-overview.md](../lua-overview.md#open). Needs: existing saves and game files.
- **State counts on versions other than 604, and with mods** (568 to 604) Older saves hold fewer states and which ones they lack was not looked at. Home: [lua-overview.md](../lua-overview.md#open). Needs: existing saves.
- **Owners of the embedded `noise`/`pollution` and `name`/`variant` tables** (604) And why 604 has more `.mdl` ids than the older versions. Home: [lua-overview.md](../lua-overview.md#open). Needs: existing saves.
- **The time-of-day `Local` value, a Continuous weather option, music keys, and any game error log** (604) `Local` was seen only in catalog saves; which music keys change while a track plays; whether a mod keeps messages under another key than `error`. Home: [script-states.md](../script-states.md). Needs: new save and existing saves.

## Animals, platform, versions

- **Animals: the list after them, scaling with map size, species per climate** (604) A Small or Medium game saved at once would settle the scaling. Home: [animals.md](../animals.md#open). Needs: new saves.
- **A platform code in a field not yet described, and mods from outside mod.io as a PC marker** (568 to 604) Home: [platform.md](../platform.md). Needs: existing saves.
