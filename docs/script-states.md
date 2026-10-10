# Script states: weather, company, achievements, subsidies

What the game keeps in a few script states, and how it ties to the header. The container is described in [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md). Here only the contents are covered. The game clock, the calendar speed and the date shown are not script states; they are in [calendar.md](calendar.md).

Checked on 604 (one game played into 2061, and catalog saves [6417707](https://mod.io/g/transportfever3/m/333151), [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1) and [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) compared with the game's windows) and 585 (two saves). The `experience` key was also compared with the header on 599 and 601 saves. 568 was not read for this note, apart from the counter keys under Counters and achievements.

## Finding a table

- In the saves checked, a script's path string (for example `game_mechanics/game_time/game_time.gs`) is followed by that script's state table. **Observed**.
- Search for a key as in [lua-values.md](lua-values.md) and read the value after it. Numbers are tag 2 and an f64, so `experience` is the key string, then `02 00 00 00`, then 8 bytes.
- Key names repeat across scripts (`level`, `experience`, `amount`, `birthDay`). Take the hit that sits under the right script path, not the first hit in the file. Offsets move from save to save.

## Times

Times in the script states are values of the game clock: the game's own milliseconds since the start date, 4000 a day at calendar speed 1.00x. The clock, the calendar speed and how to turn a time into a date are in [calendar.md](calendar.md).

- Keys that hold a time: `lastIncomeUpdateTime`, `birthDay` and `lastPayDay` (loans), `nextChange`, `nextTimeOfDayChange`, `spawnNextUfoAtGameTime`, and `timestamp` and `lastApplyTime` in notification entries. `lastIncomeUpdateTime` trailed the save time by 1 to 4 days, so it is not "now".
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

## Company and rank

Two states, both **Observed** on 585 and 604.

- `game_mechanics/company/company.gs`: `basePopulation`, `companyStates` and `companyEntity`.
- `game_mechanics/company/company_progression.gs`: `companyState` with `experience`, `level` and `potentialLevel`, plus loan tables (below).

What goes with what:

- The header's counter equals the first `experience` after the progression path, or trails it: by 1 to 4 points in the saves of [header.md](header.md), by 242 in catalog save 6417707 (below).
- `potentialLevel` followed the rank shown in the game (rank 2 was shown as Mechanic). `level` was 1 in a 585 save and 2 after the same game was re-saved by a 604 game, so it may be the rank applied after the game has run (see the Vice President save below, where `level` stayed behind).
- The game's company window lists 15 ranks in this order: Junior, Mechanic, Engineer, Coordinator, Expert, Team Leader, Supervisor, Manager, Director, Senior Director, CEO, Chairperson, Vice President, President, Tycoon. Rank 2 is Mechanic, as above, and the last is Tycoon, rank 15 (listed in a 604 game; names are the English UI).
- **Confirmed** on catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) (604, start year 1960, no mods): `level` 10, `potentialLevel` 13, `experience` 15,808 (equal to the header counter). The game showed Vice President, which is rank 13 in the list above, so `potentialLevel` is the rank shown and `level` is not. `companyLevelUpCount` in the achievements state was 12, which is 13 minus the starting rank 1. A second save, 6429423, has the same split (7 and 8) and was not loaded in the game.
- In the same game the Vice President entry read "Reach a Population of 14,842" with the bar full, and `basePopulation` was 1,685. The ratio is 8.81. One point only, so the formula is still **Open**.
- `experience` did not change over two weeks of play in which `cargoDeliveredCount` rose by 9. It moved with population, not with deliveries or time.
- **Observed** on catalog save [6417707](https://mod.io/g/transportfever3/m/333151) (604): `experience` 23,547 equalled the rank screen's progress figure ("23,547/24,037" toward President), `level` and `potentialLevel` were both 13 (Vice President, which the bottom bar showed), and `basePopulation` was 2,301. The header counter was 23,305, 242 behind `experience`, so "a few points behind" above is not a fixed gap. The President entry's 24,037 is 10.45 times `basePopulation`, against 8.81 for the Vice President entry in the other save, so the thresholds are not one multiple of it. The bottom bar read 88%, not 23,547 / 24,037 (98%). If it shows progress inside the current rank, the Vice President threshold would be about 19,800 to 20,100, which is 8.6 to 8.7 times `basePopulation`. That was not checked against the game's own Vice President entry. **Open**.
- The rank thresholds the game shows ("Reach a Population of N") were not found as stored numbers. **Open**. In one game the first rank's number (1,355) equalled both `basePopulation` and `experience`; in another, `basePopulation` was 1,443 and the second rank's number was 1,622. How the thresholds derive from `basePopulation` is **open**.

## Loans

In the progression state, under `availableLoans` and the table after it. Fields seen: `amount`, `birthDay`, `duration`, `percentage`, `type` (`Small`, `Medium`, `Large`, `ExtraLarge`), `freeId`, and on a taken loan `lastPayDay` and `timesPaid`. **Observed** on 585 and 604. Which table is which is **open**.

- **Observed** on catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) (604, calendar speed 0.50x, no loans taken), compared with the Loans tab. The four offers were stored as `Small` 12,000,000, `Medium` 59,000,000, `Large` 82,000,000 and `ExtraLarge` 124,000,000, in that order, with `percentage` 0.03, 0.05, 0.08 and 0.12 (a fraction, shown as 3%, 5%, 8%, 12%).
- `duration` is in the game clock ([calendar.md](calendar.md)): 1,461,000, 5,844,000, 17,532,000 and 20,454,000. That is 1, 4, 12 and 14 times 365.25 days. The tab showed 6, 24, 72 and 84 months, exactly half of that in years, which is the 0.50x calendar speed applied to the stored duration. So the months shown are the stored duration times the calendar speed, the same rule as for the date. Only 0.50x was seen, so whether the shown months follow the speed at the time of looking was not tested. **Open**.
- `percentage` is a total, not a yearly rate: the "per Year" figure on each offer was `amount` times (1 + `percentage`) divided by the length in years shown, with one year as the least (12,360,000, 30,975,000, 14,760,000 and 19,840,000).
- `birthDay` is when the offer was made, as a clock value. The four were 383,174,000, 383,247,200, 383,259,800 and 382,834,400, against a newest timestamp of about 383,515,000 in the same save: 64 to 170 days of stored time before the save.

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

## Notification types

The state of `game_mechanics/notifications/availability_notifications.gs` has a `lastYear` number that matched the year on screen (2060, then 2061). It tracks the year but is not the clock. **Observed** on 604.

Path strings for notification scripts under `::/game_mechanics/notifications/types/` appear in the stream. A played 604 game had 21 different ones: `animaldespawn`, `availability`, `cargo_rtc_warning`, `con_availability`, `industry_close`, `industry_spawn`, `line_station_warning`, `line_warning`, `newcargodemand`, `noroadconnection`, `overcrowding`, `station_useless`, `stuck_vehicle`, `subvention`, `subvention_missed`, `subvention_notification`, `town_rating_warning`, `town_rating_warning_nonperistent`, `town_warning`, `vehicle_warning`, `vehiclecondition`. **Observed**; which one drives which message in the game was not matched, for example the "Town Rating Decreasing" popup most likely uses one of the two `town_rating_warning` types.

## Subsidies

State of the notifications script. A subsidy is a notification entry, **Observed** on 585 and 604:

- `type` is `::/game_mechanics/notifications/types/subvention_notification.script`.
- `params` holds a resource path under `::/game_mechanics/subventions/` (for example `deliver_cargo/deliver_cargo.res`), `stockListEntity`, and `simParams.mapping` with the name of the industry or town.
- Also `dismissed`, `hidden`, `hideInLogAndPopups`, `playedInitialSound` and `timestamp`.
- The notification type string appears once in a game near its start and 9 and 10 times in a game 160 years in. The game showed both an industry request ("looking for a reputable transportation company") and a town request ("requires a skilled logistics firm"). How the two kinds are told apart in the file is **open**.

## Active and completed subsidies

State of `game_mechanics/subventions/subventions.gs`, read from catalog save [6417707](https://mod.io/g/transportfever3/m/333151) (604, start year 1900, calendar speed 1.00x, loaded paused as 17 April 2000) and compared with the game's subsidy popups. **Observed**, one save. The state is a table body with no leading tag: after the path string comes one byte, then a u32 pair count (8 here) and the pairs.

- Top-level keys: `activeSubventions`, `completedSubventions`, `failedSubventions` (16 entries), `proposedSubventions` (empty), `lastSpawnTime`, `spawnIntervalModifier`, `usedUids` and `version` (2).
- An entry has `id` (a resource path under `::/game_mechanics/subventions/`, for example `deliver_workers/deliver_workers.res`), `uid`, `spawnTime`, `acceptedTime`, on a completed one `completedTime`, and a `data` table. In `data`: `name`, `upfront`, `complete`, `failure`, `effectDuration`, `expireDuration`, `expireDurationProposed`, and the targets (`to`, `from`, `lineEntity`, `townEntity`, `cargoType`, `toDeliver`, `delivered`, depending on the kind).
- Targets are `{entity, revision.num}` with an entity id and three numbers. Entity ids here ran up to 135,964.
- Payments match the popup to the dollar. For an active worker-transport subsidy, `upfront` 16,950,000 was "On Acceptance", `complete` 27,980,000 was "On Fulfillment", and the two `failure` amounts (16,950,000 and 31,130,000) added up to the 48,080,000 fine. In every entry here the first `failure` amount equalled `upfront`. In the other `failure` slot the money fine and a `Reputation` entry with a `townEntity` (a fraction such as 0.7) both occurred.
- Reward types seen in `complete`: `Money`, and `TownExperience` with a fraction (0.55 and 0.8) and a `townEntity`. A completed "Connect Towns" entry held 0.55 and 0.8 for its two towns, and the popup showed "55% Level Progress" and "80% Level Progress" for them.
- Times use the game clock ([calendar.md](calendar.md)). At 1.00x, with the shown date taken as 17 April 2000 (146,524,000, which is 36,631 days from 1 January 1900), the numbers fit the screens: `expireDuration` 2,556,750 is 639 days and showed as "1 Year 9 Months"; `acceptedTime` + `expireDuration` fell 93 days after the save and the progress bar read "3 Months"; `effectDuration` 365,250 is a quarter of a year and showed as "3 Months"; a completed entry's `completedTime` + `effectDuration` (a 5-year effect, 7,305,000) fell 1,633.3 days after, and the popup showed "4 Years 5 Months 19 Days", which is 1,633 days. The date was taken from the screen, so this checks the unit and the 1.00x rule against one save, not the start of the count.
- Which `data` keys each kind uses, and what `failedSubventions` holds, were not worked out. **Open**.

### The offer itself

State of `game_mechanics/subventions/subventions.gs`. **Observed** on 604, one save with a proposed industry-supply offer checked against the game's offer window.

- A proposed entry has `id` (a resource path such as `::/game_mechanics/subventions/deliver_cargo/deliver_cargo.res`), `uid`, `spawnTime`, and a `data` table. In `data`: `name` (the offer's title, "Supply Industry"), `stockListEntity` (the industry's entity id), `toDeliver` (the amount of cargo, 80 in the offer checked), `cargosToDeliver`, `delivered`, `upfront`, `failure`, `effectDuration`, `expireDuration` and `expireDurationProposed`.
- `upfront` and `failure` hold `params` tables of `amount` and `type` (`Money` in the ones seen). In the offer checked, the payment on acceptance equalled `upfront`'s 6,300,000, and the fine shown (27,000,000) equalled the two `failure` amounts added, 6,300,000 and 20,700,000. In other saves the `failure` list also held small non-money amounts (under 1), which were not decoded.
- Durations shown in the offer window equalled the stored numbers divided by 4000 (days) and then multiplied by the calendar speed, 0.50x at the time: `expireDuration` 4,626,500 showed as "1 Year 7 Months" and `effectDuration` 7,305,000 as "2 Years 6 Months". That is consistent with the calendar-speed rule in [calendar.md](calendar.md#the-game-clock). A difficulty setting that scales time could give the same factor, and one save can't tell the two apart. **Open**.
- The `advancedOptions.*` settings (see [settings.md](settings.md)) are stored as small level numbers (1 to 5 seen in the catalog saves, not multipliers): the option's position in the settings list plus 1, see [header.md](header.md). Whether a level scales the stored money amounts was not shown: at the levels in the save checked (`subventionRisk` 2, `subventionMode` 3) the shown money equalled the stored money. Across a few other 604 saves with the default levels the fine against the payment varied from offer to offer, so the fine is not a fixed multiple of the payment. **Open**.
