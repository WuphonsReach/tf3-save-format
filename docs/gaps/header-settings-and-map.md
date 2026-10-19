# Gaps: header, settings, map and clock

Format of an entry: see [README.md](README.md).

## In short

Everything here is **Open**, seen on 604 unless a range is given.

- The biggest block is the seed, terrain and map size: whether the seed alone rebuilds a map, what the width and height rule does outside the sizes seen, and what the water sliders change. Each needs a pair of New Game saves taken at once.
- The sun against the compass is a quarter turn off, and the town centre the name words use is not stored anywhere found.
- Calendar: the mapping from year to clock units at any speed other than 1.00x is untested, and what the autosave interval counts is unclear.
- Settings and mods: whether a change acts on what already exists, and what happens to a removed mod's options.
- Script states, animals and platform: mostly reading work on saves we hold.

## Seed, terrain and the map

- **Why a Tutorial On game's industry count differs from the New Game screen** (604) The Small tropical game read 8 industries on the screen and held 15 in the save and in the loaded Industries tab; the Tutorial Off games differ by 0 or 1. Whether the tutorial adds industries or the preview is simply built before placement is untested. Home: [tutorial.md](../tutorial.md#open-the-town-and-industry-counts), [industry-lifecycle.md](../industry-lifecycle.md#the-industry-count-on-the-new-game-screen-and-in-the-save-604). Needs: new save pair (two New Games, same seed and sliders, Tutorial On and Off), each saved at once.
- **Whether the seed alone rebuilds the map** (604) The sliders are not stored, so a rebuild would need the same sliders; whether default sliders reproduce the New Game screen's map is untested. Home: [seed.md](../seed.md), [terrain.md](../terrain.md#open). Needs: new save pair (two new games, same seed and sliders; then one with only Mountains changed), each saved at once.
- **Seed edge cases** (599 to 604) What `id` stores for an empty seed, 40 characters, spaces, accents or CJK. Home: [seed.md](../seed.md). Needs: new saves.
- **What the editor now calls the seed field** (604) `tf3-save-editor` names the last header field `id` in every branch and in upstream 0.4.0; an update may have renamed it, but none was found. Our tools use `map_seed`. Home: [seed.md](../seed.md#the-id-field), [tf3-save-editor.md](../tf3-save-editor.md). Needs: the editor's newest source or release notes.
- **What writes the model preview block near 0,0 in an editor save** (604, one Giant editor map) A block of about 1,300 model records at x 0 to 50, y -7 to 7 (not drawn by the game) appeared between two editor saves, after the Towns / Industries tool had already generated industries. Home: [editor-saves.md](../editor-saves.md#the-model-preview-block-near-00). Needs: a save made straight after loading the generated-industries save, then one after opening each tool or palette.
- **A map editor seed** (604) Whether a new editor map with a typed seed keeps it in `id`. Home: [seed.md](../seed.md), [editor-saves.md](../editor-saves.md). Needs: new save.
- **Map size against format** (604) Tiny 1 : 4, Tiny 1 : 3 (8 x 24 tiles), Tiny 1 : 5 (6 x 30) and Small 1 : 3 (18 x 54) were read; in all four the tile count is the map's metres divided by 256. Medium, and 1 : 1 at every size, are untested. Home: [terrain.md](../terrain.md#open), [header.md](../header.md). Needs: new saves (Tiny, Small, Medium at 1 : 1 and 1 : 3); header width and height already give the metres.
- **What sets the width and height: the 512 m rounding and its exceptions** (599 to 604) A rule of nearest 512 m of sqrt(area / n), height n times the width, with one area per Map Size, fits every seen size but Megalomaniac, whose 1 : 1 needs a slightly larger area than its other formats. Tiny 1 : 4 keeps the 1 : 3 height (6144 m, not 8192 m). Whether the game uses another rounding or a per-size tweak is untested, and Small, Medium, Large, Very Large and Huge at 1 : 4 and 1 : 5 are unseen. Home: [map-sizes.md](../map-sizes.md#the-rule). Needs: new saves or New Game screen readouts (Megalomaniac 1 : 4, a Tiny 1 : 4 repeat, 1 : 4 and 1 : 5 at other sizes).
- **What the Ocean, Islands and Lakes and Rivers sliders change** (604) Lakes moved from Medium to Packed changed nothing on a desert map, yet the generator's node graph has lake nodes; whether any desert map ever shows a lake is open. Home: [terrain.md](../terrain.md#open). Needs: new save (Lakes on a temperate map, then Rivers on desert).
- **Why the sun is a quarter turn off the game's compass, and the town centre the name words use** (604) The compass words in names and the New Game preview put east at +x and north at +y (real-place maps are turned by their authors and settle nothing); the sun rises towards -y. Whether the sun's hemisphere or a few degrees of misalignment matter is untested, as is a Morning, Day, Evening series in a tropical game; the noon heading is known to about 20 degrees only, and a finer reading with roads along shadows, in a second climate and date, is planned. The point a name's word is judged from is not stored anywhere found; the label above a town gives a town centre on screen, and whether that is the point the words use is untested ([town-centre.md](../town-centre.md)). Home: [compass.md](../compass.md). Needs: a tropical sun series; a save with a town renamed to a typed string to find the town entity's position.
- **The terrain values after the header** (604) What `baseLevels` and `highLevels` mean, what the float-like record stretch holds, and whether the list after the heightmap is the per-tile brush record. Home: [terrain.md](../terrain.md#open). Needs: existing saves and game files (`TerrainTileBrush` in the API definitions).
- **The 13 records of 16 floats** (604) Sites move between saves of one seed; whether the 13 are the first kind in a longer list (count prefix 0x27 or 0x4e) is unknown. Home: [terrain.md](../terrain.md). Needs: existing saves.
- **What the climate changes on load** (604) Whether the terrain and existing industries change when the climate is switched on the Load Game screen. Home: [settings.md](../settings.md#open). Needs: new save pair.

## Settings

- **Whether setting changes act in play** (604) For example on buildings that already exist. See also [vehicles-and-costs.md](vehicles-and-costs.md#running-costs-and-upkeep). Home: [settings.md](../settings.md#open). Needs: new save.
- **Whether a loaded save stays byte for byte as it was** (604) The first test save was not hashed before its load. Home: [settings.md](../settings.md#open). Needs: new save (hash first, load, hash the same file again).
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
