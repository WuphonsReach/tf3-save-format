# Script states: clock, company, achievements, subsidies

What the game keeps in a few script states, and how it ties to the header. The container is described in [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md). Here only the contents are covered.

Checked on 604 (three saves of one game) and 585 (two saves). The `experience` key was also compared with the header on 599 and 601 saves. 568 was not read for this note.

## Finding a table

- In the saves checked, a script's path string (for example `game_mechanics/game_time/game_time.gs`) is followed by that script's state table. **Observed**.
- Search for a key as in [lua-values.md](lua-values.md) and read the value after it. Numbers are tag 2 and an f64, so `experience` is the key string, then `02 00 00 00`, then 8 bytes.
- Key names repeat across scripts (`level`, `experience`, `amount`, `birthDay`). Take the hit that sits under the right script path, not the first hit in the file. Offsets move from save to save.

## Game clock

Times in the script states are numbers of **1/4000 of a game day**, counted from 1 January of the start year (**Observed** on 604, three saves of one game saved on 6 February, 20 February and 18 March 2060 with start year 1900; every timestamp of a past event fell on or before the save day, and the newest was 0.7 of a day into the last one, saved while paused). The 585 saves give dates in the right year but were not checked to the day.

- Every save checked here started in 1900, so "from 1 January 1900" and "from the start year" can't be told apart. **Open**.
- Whether the scale depends on the calendar speed setting is **Open**. Both games ran at 1.00x.
- No field holding the current time was found. The newest timestamp in the file is a lower bound for the save time.
- Keys that hold a time: `lastIncomeUpdateTime`, `birthDay` and `lastPayDay` (loans), `nextChange`, `nextTimeOfDayChange`, `spawnNextUfoAtGameTime`, and `timestamp` and `lastApplyTime` in notification entries. `lastIncomeUpdateTime` trailed the save time by 1 to 4 days, so it is not "now".
- The header's start year is the only calendar value in the header. The date shown in the game is not stored there.

## Weather and time of day

State of `game_mechanics/game_time/game_time.gs`. **Observed** on 585 and 604.

| Key | Holds |
|---|---|
| `timeOfDayMode`, `weatherMode` | Strings, `Dynamic` or `Constant` |
| `timeOfDayTarget` | Number from 0 to 86,400, seconds of the day (43,200 in a map pinned to noon) |
| `timeOfDayTargetSpeed` | 60 or 90 seen |
| `cloudCoverageTarget` | 0 to 1, clear to rain |
| `cloudCoverageTargetSpeed` | 0.001 or 0.0025 seen |
| `currentTimeOfDayState`, `currentWeatherState` | Small whole numbers |
| `nextChange`, `nextTimeOfDayChange` | Times, see above |

- The state is a snapshot at save time. Slider positions in the game's Weather and Time window were close to the stored targets but not equal, because the game keeps running after the load.
- The settings table (see [header.md](header.md)) has `gameTimeConfig.timeOfDayMode` and `weatherConfig.dynamicWeather`. Both were 1 in saves whose state said `Constant` and in saves whose state said `Dynamic`, so they don't mirror the state. Read the state for the mode.
- **Open**: calendar speed (the 1.00x slider). No key was found for it in either save.

## Company and rank

Two states, both **Observed** on 585 and 604.

- `game_mechanics/company/company.gs`: `basePopulation`, `companyStates` and `companyEntity`.
- `game_mechanics/company/company_progression.gs`: `companyState` with `experience`, `level` and `potentialLevel`, plus loan tables (below).

What goes with what:

- The header's counter equals the first `experience` after the progression path, or is a few points behind it. See [header.md](header.md).
- `potentialLevel` followed the rank shown in the game (rank 2 was shown as Mechanic). `level` was 1 in a 585 save and 2 after the same game was re-saved by a 604 game, so it may be the rank applied after the game has run. **Open**.
- `experience` did not change over two weeks of play in which `cargoDeliveredCount` rose by 9. It moved with population, not with deliveries or time.
- The rank thresholds the game shows ("Reach a Population of N") were not found as stored numbers. **Open**. In one game the first rank's number (1,355) equalled both `basePopulation` and `experience`; in another, `basePopulation` was 1,443 and the second rank's number was 1,622. How the thresholds derive from `basePopulation` is **open**.

## Loans

In the progression state, under `availableLoans` and the table after it. Fields seen: `amount`, `birthDay`, `duration`, `percentage`, `type` (`Small`, `Medium`, `Large`, `ExtraLarge`), `freeId`, and on a taken loan `lastPayDay` and `timesPaid`. **Observed** on 585 and 604. Which table is which, and the meaning of `duration`, are **open**.

## Counters and achievements

State of `game_mechanics/achievements/achievements.gs`. **Observed** on 585 and 604.

| Key | Holds |
|---|---|
| `passengerTransportedCount`, `cargoDeliveredCount` | Totals for this game |
| `companyLevelUpCount`, `companyReachedMaxRankCount`, `highAltitudeStopUsedCount`, `oilPlatformLandings` | Counters |
| `cargoTypesDelivered` | Table |
| `totalIncome`, `subventionSuccess`, `subventionSuccessStreak`, `townLevelUpCount`, `placedTrees`, `vehiclesUsed` | More counters in the same area (not all present in every save) |

- **Confirmed** on one 604 save: the game's bottom bar showed the same passenger and cargo totals as `passengerTransportedCount` and `cargoDeliveredCount`. In a second save the cargo total on screen was one higher than in the file, which fits a delivery between the save and the screenshot. In a third, taken while the game was paused, both totals matched exactly.
- The game's Done marks for achievements are **not** in the save: no achievement names or flags were found, and two saves with very different counters (zero deliveries and thousands) showed the same seven achievements as Done. So completion looks account-wide, not per save. **Observed** on two 585 saves (an inference from the screens).

## Notification types

Path strings for notification scripts under `::/game_mechanics/notifications/types/` appear in the stream. A played 604 game had 21 different ones: `animaldespawn`, `availability`, `cargo_rtc_warning`, `con_availability`, `industry_close`, `industry_spawn`, `line_station_warning`, `line_warning`, `newcargodemand`, `noroadconnection`, `overcrowding`, `station_useless`, `stuck_vehicle`, `subvention`, `subvention_missed`, `subvention_notification`, `town_rating_warning`, `town_rating_warning_nonperistent`, `town_warning`, `vehicle_warning`, `vehiclecondition`. **Observed**; which one drives which message in the game was not matched, for example the "Town Rating Decreasing" popup most likely uses one of the two `town_rating_warning` types.

## Subsidies

State of the notifications script. A subsidy is a notification entry, **Observed** on 585 and 604:

- `type` is `::/game_mechanics/notifications/types/subvention_notification.script`.
- `params` holds a resource path under `::/game_mechanics/subventions/` (for example `deliver_cargo/deliver_cargo.res`), `stockListEntity`, and `simParams.mapping` with the name of the industry or town.
- Also `dismissed`, `hidden`, `hideInLogAndPopups`, `playedInitialSound` and `timestamp`.
- The notification type string appears once in a game near its start and 9 and 10 times in a game 160 years in. The game showed both an industry request ("looking for a reputable transportation company") and a town request ("requires a skilled logistics firm"). How the two kinds are told apart in the file is **open**.

## Money

**Observed** on 604: in three saves of one game the header money equalled the Account figure in the game exactly, including once when the account was negative. See [header.md](header.md) for the cases where the header disagrees.
