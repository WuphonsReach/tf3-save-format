# Script states: basics, weather, achievements, mods

What the game keeps in script states, and how to find them. The container is described in [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md). The states with a note of their own are listed [below](#states-seen); this note covers how to read them and the states that have no note of their own. The game clock, the calendar speed and the date shown are not script states; they are in [calendar.md](calendar.md).

Checked on 604 (one game played into 2061, and catalog saves [6417707](https://mod.io/g/transportfever3/m/333151), [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1) and [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) compared with the game's windows) and 585 (two saves). 568 was not read for this note, apart from the counter keys under Counters and achievements.

## Finding a table

- In the saves checked, a script's path string (for example `game_mechanics/game_time/game_time.gs`) is followed by that script's state table. **Observed**.
- Search for a key as in [lua-values.md](lua-values.md) and read the value after it. Numbers are tag 2 and an f64, so `experience` is the key string, then `02 00 00 00`, then 8 bytes.
- **The body layout.** After the path string comes the state table without its tag 4: one byte (the table flag), a u32 pair count, then the pairs ([lua-values.md](lua-values.md)). **Observed** for the base game's scripts and for mod scripts, 585 to 604.
- Key names repeat across scripts (`level`, `experience`, `amount`, `birthDay`). Take the hit that sits under the right script path, not the first hit in the file. Offsets move from save to save.

## States seen

Script paths as they appear in the stream, and where each is described. A mod's states are listed under its own id ([Mod script states](#mod-script-states-and-stored-errors)); what else a save records about a mod is in [mods.md](mods.md).

| Script | Described in |
|---|---|
| `game_mechanics/game_time/game_time.gs` | [Weather and time of day](#weather-and-time-of-day) |
| `game_mechanics/company/company.gs`, `company_progression.gs` | [company.md](company.md) |
| `game_mechanics/achievements/achievements.gs` | [Counters and achievements](#counters-and-achievements) |
| `game_mechanics/notifications/notifications.gs`, `availability_notifications.gs` | [notifications.md](notifications.md) |
| `game_mechanics/subventions/subventions.gs` | [subsidies.md](subsidies.md) |
| `game_mechanics/towns/town.gs` | [town-states.md](town-states.md) |
| `game_mechanics/towns/town_cargo.gs` | `cargoDemandsSorted`, in [cargo-ids.md](cargo-ids.md) |
| `landmarks/landmarks.gs` | [landmarks.md](landmarks.md) |
| `game_mechanics/fun_elements/fun_elements.gs`, `fireworks.gs` | [fun-elements.md](fun-elements.md#other-fun-element-states) |
| `game_mechanics/industries/industries.gs` | [Industries](#industries) |
| the music player's table (not a script path) | [The music player state](#the-music-player-state) |

`game_mechanics/celebrations/celebrations.gs`, `industries/industry_workers.gs`, `mission/mission.gs`, `terrain/reforestation.gs` and `vehicle/vehicle_modifier.gs` also occur and are not described in these notes. In the saves of [landmarks.md](landmarks.md#finding-it) they sat near the end of the stream in that order, with `landmarks/landmarks.gs` between the second and the third (**Observed**, 604).

### Industries

The state of `game_mechanics/industries/industries.gs` was empty in the editor saves checked. In a played 604 game (catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3), over 300 industries) it held only `industryFailedExtensions`, `tick` and `triangles`, so the Industries tab's input, output, workload and shipment figures are not kept there (**Observed**). They are presumably in the entity data, which was not read.

## Times

Times in the script states are values of the game clock: the game's own milliseconds since the start date, 4000 a day at calendar speed 1.00x. The clock, the calendar speed and how to turn a time into a date are in [calendar.md](calendar.md).

- Keys that hold a time: `lastIncomeUpdateTime`, `birthDay` and `lastPayDay` (loans), `nextChange`, `nextTimeOfDayChange`, `spawnNextUfoAtGameTime`, `nextSpawnTime` (the hot air balloon, [fun-elements.md](fun-elements.md)), and `timestamp` and `lastApplyTime` in notification entries. `lastIncomeUpdateTime` trailed the save time by 1 to 4 days, so it is not "now".
- No Lua number holds the current date or the calendar speed (**Observed**, see [calendar.md](calendar.md#the-game-clock)).

## Weather and time of day

State of `game_mechanics/game_time/game_time.gs`. **Observed** on 585 and 604.

| Key | Holds |
|---|---|
| `timeOfDayMode`, `weatherMode` | Strings. Seen: `Dynamic`, `Constant`, and for time of day only `Automatic` and `Local`. The game's Cycle menu showed Dynamic, Continuous and Custom. Time of day: `Dynamic` is `Dynamic`, `Continuous` is `Automatic`, `Custom` is `Constant`. Weather: `Dynamic` is `Dynamic`, `Custom` is `Constant`. A Continuous weather option was not tried. `Local` was seen only in catalog saves (568 to 604) and not set in the game; the time-of-day setting's option list has a Local Time entry, so it is probably that (**Open**) |
| `timeOfDayTarget` | Number from 0 to 86,400, seconds of the day (43,200 in a map pinned to noon) |
| `timeOfDayTargetSpeed` | 60 or 90 seen |
| `cloudCoverageTarget` | 0 to 1, clear to rain |
| `cloudCoverageTargetSpeed` | 0.001 or 0.0025 seen |
| `currentTimeOfDayState`, `currentWeatherState` | Small whole numbers |
| `nextChange`, `nextTimeOfDayChange` | Times (game clock). `nextTimeOfDayChange` was 0 with `Automatic` |

- The state is a snapshot at save time. With the cycles set to Custom and Continuous, the sliders matched the stored targets: `cloudCoverageTarget` 0.29 sat at 0.29 of the weather slider, and `timeOfDayTarget` 26,357 sat at 0.31 of the time slider (26,357 / 86,400 = 0.305), which supports seconds of the day. With both cycles on Dynamic the sliders were close but not equal, because the game moves them while it runs.
- A save with both cycles on Dynamic (catalog save [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1), 604, and a paused re-save of it a day of stored time later, **Observed**): `timeOfDayTarget` 33,736 (0.39 of a day) and the time slider sat at 0.39 on the Weather and Time window, but `cloudCoverageTarget` 0.26 (speed 0.001) with the weather slider at about 0.54, so only the time slider matched. `nextChange` 94,691,800 and `nextTimeOfDayChange` 94,542,400 were 363,000 and 213,600 units after the newest list timestamp (94,328,800). The state was identical in the two saves.
- The Calendar Speed row of the same window is covered in [calendar.md](calendar.md#calendar-speed-in-the-games-windows).
- The settings table (see [settings.md](settings.md)) has `gameTimeConfig.timeOfDayMode` and `weatherConfig.dynamicWeather`. Both were 1 in saves whose state said `Constant`, `Automatic` and `Dynamic`, and they did not change when the cycles were changed in the game, so they hold the game's starting settings and don't mirror the state. Read the state for the mode.

## Counters and achievements

State of `game_mechanics/achievements/achievements.gs`. **Observed** on 585 and 604.

| Key | Holds |
|---|---|
| `passengerTransportedCount`, `cargoDeliveredCount` | Totals for this game |
| `companyLevelUpCount`, `companyReachedMaxRankCount`, `highAltitudeStopUsedCount`, `oilPlatformLandings` | Counters |
| `cargoTypesDelivered` | Table |
| `totalIncome`, `subventionSuccess`, `subventionSuccessStreak`, `townLevelUpCount`, `placedTrees`, `vehiclesUsed` | More counters in the same area (not all present in every save) |
| `townExcellentDeliveryRatingCount`, `townLowRatingCount`, `townNewCargoTypeDemandCount`, `shipsUsed` | Present in the catalog saves and maps summarised by [tools/mine_saves.py](../tools/mine_saves.py) (568 to 604). Not compared with the game. `shipsUsed`, like `vehiclesUsed` and `cargoTypesDelivered`, is a table |

- **Confirmed** on one 604 save: the game's bottom bar showed the same passenger and cargo totals as `passengerTransportedCount` and `cargoDeliveredCount`. In a second save the cargo total on screen was one higher than in the file; the screenshot was taken with the game running again, which fits a delivery after the save. In a third, screenshotted while still paused, both totals matched exactly.
- **Confirmed** on a paused re-save (604, catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) saved again with the game paused): `passengerTransportedCount` 444,636 and `cargoDeliveredCount` 1,016,977 matched the bottom bar exactly, and the original catalog save's counts (444,627 and 1,016,962) were a little lower, from play between its save and the pause.
- The game's Done marks for achievements are **not** in the save: no achievement names or flags were found, and two saves with very different counters (zero deliveries and thousands) showed the same seven achievements as Done. So completion looks account-wide, not per save. **Observed** on two 585 saves (an inference from the screens).

## The music player state

The last thing in the stream is a table with the music player's state, with the same layout in a save with no mods and one with seven. **Observed** on 604, two saves. It starts about 4.5 KB before the end of the stream and the key `trackLists` lies 4,317 bytes from the end in both. Its keys:

- `contextTags` and `ProgressPage` (with a `saved` flag), which belong to the game's music logic.
- `trackLists`: per list a `playlist` (a path such as `::/music/...plist`), `repeat`, a `state` with `currentTrackTime`, `isPlaying`, `trackIndex` and `variantIndex` (-1 when none), and a `tracks` list whose entries hold `enableRepeat`, `filepath`, `instantTransition`, `name` and `variants`.

Deluxe Upgrade adds its own playlist and tracks, whose paths start with the mod's id and `::`, so its id occurs a few times at the very end of the stream. That is the music, not a script state. Which of the keys changes while music plays is **Open**.

## Mod script states and stored errors

Mods with scripts keep state the same way the game's scripts do: the script's path string, then its table (see [Finding a table](#finding-a-table)). The mod's id string sat just before the path in the saves looked at, for example `dome_wagon_cameras` before `camera_bridge.gs` and `epod_pay_your_tolls_tf3_1` before `pyt/pyt_toll.gs` (**Observed**, 601 and 604, a few mods). What the table holds is up to the mod. Strings are kept as the mod wrote them.

A mod can keep a Lua error message there, and that message can include a local path from the player's machine:

- The message has Lua's usual form, `[string "<chunk>"]:<line>: <message>`. The chunk name is the full path of the mod's script file on disk: `<path>/mod.io/10640/mods/<mod id>/content/<file>.lua`. In a Windows save the path ran through a user folder, so it held that Windows account's name. In an Xbox save it started `R:/`. **Observed**, two saves.
- In both cases the message was kept by the mod and not by the game. They are in the state of `camera_bridge.gs` from the mod "Auto Passenger Cameras" (`dome_wagon_cameras`, mod.io id 6422630). That state has `version` (2) and a `models` table keyed by a number written as a string (`4393`, `4398`, `4430`), and each entry holds only `error`, with the same message (an index of a nil `metadata` field at line 55). The mod seems to catch a failure for each model and keep the message.
- Catalog saves [6429325](https://mod.io/g/transportfever3/m/my-rail-network) (Windows, 604) and [6431316](https://mod.io/g/transportfever3/m/1990-2) (Xbox, 601). All 244 catalog saves and maps of [versions.md](versions.md) were searched (2026-10-10) for `[string "`, `attempt to`, `.lua"]:` and `.lua:` followed by a line number, and for absolute paths (`C:/Users/`, `/home/`, `/Users/`). These two were the only hits. None of 70 of our own saves (604) had any. **Observed**, 568 to 604.
- No error log of the game's own was found in the stream. A table key `error` is not a fixed name, so a mod could also keep messages under another key. **Open**.
- To check a save before sharing it, decompress it and search for `[string "`. The path follows. Don't copy these paths or names into notes.
