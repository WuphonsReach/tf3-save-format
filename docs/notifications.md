# Notifications

State of `game_mechanics/notifications/notifications.gs`. The game's popups and its log keep one entry per notification here. Subsidy offers are notifications ([subsidies.md](subsidies.md)), and so is the hot air balloon sighting ([fun-elements.md](fun-elements.md#the-notification)). The state is read like any script state ([script-states.md](script-states.md#finding-a-table)).

## The state and its entries

**Observed** on 604, in the latest autosave of the [Small subarctic game](test-games.md#small-subarctic-game) (start year 1900, clock 45,001,200, 1914). The balloon and subsidy entries were first read on 585 and 604 in other games, see [Entry layout](#entry-layout).

### Top-level keys

| Key | Holds |
|---|---|
| `notifications` | The entries, keyed by id |
| `history` | A list: position 1, 2, ... to the id of the entry at that place, oldest first. Its ids are exactly the keys of `notifications` |
| `maxId` | The id of the newest entry |
| `version` | 24 here. The game's script names 24 as the current schema and converts older states on load |
| `ignored` | `fully` (boolean) and `types`, a table from a type path to a boolean |
| `wastedVehicles`, `vehicle2problem`, `stationGroup2overflowResolvedTimestamp`, `noRoadConnectionUpdateTimestamp`, `line2problemTimestamp` | Bookkeeping that decides when a warning is raised ([below](#bookkeeping-tables)) |

- **The table holds at most 100 entries.** The game's script (`game_mechanics/notifications/notification_util.tl` in `base/content/game_mechanics.zip`) names the limit `maxEntries` = 100. When a new entry is added the oldest ones are dropped, except one that still has a `persisting` list. The save had exactly 100 entries with the consecutive ids 765 to 864 and `maxId` 864, and the oldest `timestamp` was 2.4 million clock units (about 3 game years at 2,000 units a day) before the save. An entry therefore stays in the table only while newer ones are few; in this game (start year 1900) the oldest entry was from late 1910, so the first ten years were gone and a long game cannot be read for its early notifications from this table.
- `ignored.types` held a boolean for 30 types: the base game's notification types, the company, town, landmark and mission ones, and the balloon mod's. `true` means ignored by default: the 11 types that the game's own `.res.lua` files mark `initiallyIgnoredType = true` were the 11 that read `true` here (`company_notification_greenify`, `_marketing`, `_prospection`, `cargo_rtc_warning`, `noroadconnection`, `overcrowding`, `station_useless`, `stuck_vehicle`, `town_warning`, `vehicle_warning`, `vehiclecondition`), and all the others `false`. Whether this save's player had changed any is not known; the game's notification settings window was not compared. `fully` was `false`.
- **An entry's `tracked` is the negation of its type's `ignored.types` value at the time it was made** (the game's script: `tracked = not ignored.types[type]`). All 69 overcrowding and 9 vehicle-condition entries had `tracked` false; the other 22 had it true. An ignored type still gets entries, they are just not shown as popups.

### Entry layout

Each entry is `{notification, timestamp, dismissed, expired, tracked, playedInitialSound}`, plus `persisting` when there is one. The entry's kind is inside `notification`:

| Key | Holds |
|---|---|
| `notification.type` | A script path. The base game's start with `::/game_mechanics/notifications/types/` (for example `subvention_notification.script`); company, town and mission types have their own folders (`::/game_mechanics/company/company_notification_rank_up.script`, `::/game_mechanics/towns/town_notification.script`, `::/mission/notification.script`). A mod's carries the mod id before `::` (`urbangames_deluxe_upgrade_pack::/fun_elements/balloon_notification.script`) |
| `notification.params` | What the type needs ([per type](#params-by-type)) |
| `notification.simParams` | What the game's sim script has looked up for the text, usually `simParams.mapping` from an entity id to its name. Rewritten on a rename ([notifications-in-play.md](notifications-in-play.md#industry-spawn-notifications-604)). Empty for the types that need no name |
| `notification.autoDismissDuration` | Only on some types: 60,000 clock units (30 game days at 2,000 units a day, 15 at 1.00x) |
| `timestamp` | Game-clock time ([calendar.md](calendar.md)) |
| `dismissed`, `expired`, `tracked`, `playedInitialSound` | Booleans. `hidden` and `hideInLogAndPopups` were seen on the balloon entry and not here |
| `persisting` | A list of `{entity, revision}`: the entities a still-open warning is about. See [below](#persistent-warnings) |

- **Open:** the balloon entry of [fun-elements.md](fun-elements.md#the-notification) was read in another game, before this layout was known, and not re-read. In this save `type` and `params` sit under `notification` for every type, and the balloon entry very likely does too.
- **Expiring sets `dismissed` too.** No entry had `expired` true with `dismissed` false. An entry expires when `timestamp` + `autoDismissDuration` has passed, or when every entity in `params.entities` has changed (the script's `entityChanged0`, which compares only the first revision number). `dismissed` true with `expired` false is the player closing the popup.
- **`revision.num` has three numbers.** The warnings that are raised from a periodic check (overcrowding, vehicle condition, town rating, industry closing) store `{n, 0, 0}`, the first number of the entity's revision. The ones raised by an event (industry spawn, town level, new cargo demand) store all three (`3, 14, 1` for an industry, `1, 6, 247187` for a town). What the second and third numbers are is **Open**. A subsidy entry keeps only the first, as a pair under `entitiesAndRevisions0`.
- The subsidy type string appears once in a game near its start and 9 and 10 times in a game 160 years in. The game showed both an industry request ("looking for a reputable transportation company") and a town request ("requires a skilled logistics firm"). In the file they are told apart by `params.id`, a `.res` path under `::/game_mechanics/subventions/`: `deliver_cargo` for an industry (its `params.params` is `stockListEntity`) and `deliver_cargo_town` for a town (`cargoType` and `townEntity`). **Observed** on 604.

## Types

Path strings for notification scripts under `::/game_mechanics/notifications/types/` appear in the stream. A played 604 game had 21 different ones: `animaldespawn`, `availability`, `cargo_rtc_warning`, `con_availability`, `industry_close`, `industry_spawn`, `line_station_warning`, `line_warning`, `newcargodemand`, `noroadconnection`, `overcrowding`, `station_useless`, `stuck_vehicle`, `subvention`, `subvention_missed`, `subvention_notification`, `town_rating_warning`, `town_rating_warning_nonperistent`, `town_warning`, `vehicle_warning`, `vehiclecondition`. **Observed**. Others live outside that folder: `company_notification_greenify`, `_marketing`, `_prospection` and `_rank_up` (`::/game_mechanics/company/`), `town_notification` (`::/game_mechanics/towns/`), the two landmark ones (`::/landmarks/landmarks_notification.script` and `_nonpersistent`) and `::/mission/notification.script`. With the balloon mod's, these are the 30 keys of `ignored.types` in the 604 game above.

### Params by type

**Observed** on 604 in the latest autosave. Its 100 entries held 11 types, which are the first 11 rows of the table; the last row is from the game's script only. The popup titles are the game's English UI text (the `useDataState` function of each type in `base/content/game_mechanics.zip`; blank where that script was not read). A cargo id is a position in the save's own cargo list ([cargo-ids.md](cargo-ids.md)).

| Type | Popup title | `params` | `simParams` |
|---|---|---|---|
| `overcrowding` | Station Overcrowded | `entity`: a **station group** entity | `mapping`: entity to the group's name |
| `vehiclecondition` | Vehicle Condition | `entities`: list of one vehicle | `mapping` (entity to "Road Vehicle 79") and `typeMapping` (entity to "Truck" or "Bus") |
| `town_rating_warning_nonperistent` | Town Rating Decreasing | `entities`: list of one town; `param.key`: the rating (`noise`, `cargo_delivery`) | `mapping` |
| `town_notification` | Town Level Up | `townEntity` and `level` | `townName` |
| `newcargodemand` | New Cargo Demand | `entity` (the town) and `cargoTypeId` | `name`: the town |
| `company_notification_rank_up` | Time To Celebrate | `companyEntity` and `rank` | empty |
| `industry_spawn` | | `entity`, `resName` (the `.con` path) | `mapping` |
| `industry_close` | | `entity`, `resName` | `mapping` |
| `availability` | | `models`, `multipleUnits` | empty |
| `subvention_notification` | | `id`, `uid`, `status`, `params`, `entitiesAndRevisions0` | `mapping` |
| `subvention_missed` | | `subventionId`, `reason`, `params`, `entitiesAndRevisions0` | `mapping` |
| `town_rating_warning` | Town Rating Very Poor | the same shape as the `_nonperistent` one | |

- **`line_warning` and `cargo_rtc_warning` (604, **Observed**, one played game, catalog [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1); meanings from the game's own scripts `line_warning.script.tl` and `cargo_rtc_warning.script.tl`, `base/content/game_mechanics.zip`).** A `line_warning` entry's `params.param` holds `lineProblem` (-1 when the entry is about cargo) and `lineIssues`, a list of `{type, stop index, cargo id}`. The script words the issue types as: cargo configured but loaded nowhere, cargo loaded at a stop but unloaded nowhere, no vehicle on the line can carry a configured cargo, a vehicle that can carry none of it, and a line configured to load nothing. In the 12 entries with `lineIssues` (of 14 line warnings), type 0 always had stop index -1 and type 1 a stop index of 0 or 1, which fits the script (the "loaded nowhere" text names no stop, the "unloaded nowhere" text names the stop index plus 1); type 1 is **Confirmed** as the unloaded-nowhere issue: the line window of a wool line read "A cargo type cannot be unloaded anywhere, despite being loaded at stop 1. Cargo Type: Wool", and the save holds a type 1 entry with stop index 0 and cargo 25 (the pairing of entry and line is by those values, since the entry names no line). Type 0 is probably loaded-nowhere and the other numbers are **Open**. Cargo ids seen were 6, 7, 13, 25 and 30 (fish, meat, planks, wool, tools). The entries' timestamps equal the values in `line2problemTimestamp` ([bookkeeping tables](#bookkeeping-tables)), whose keys are line entities, so a warning can be tied to a line's entity id but not to its name. `lineProblem` 4 appeared in two entries at the same clock as a `vehicle_warning` for a train whose window read "There is no electrified path" and "No Path". The two lines then showing a problem marker were both lines with a train in that queue, and hovering the line's colour band on the track (the line overlay) read "Could Not Connect Stations". In the script's list of line problems that is the fourth (counting from 1), so 4 is that problem (**Observed**, one game; the entries do not name the line, the pairing is by clock and by the two flagged lines). The `cargo_rtc_warning` popup is titled "Cargo Unload Problem" and says that some cargo of a named vehicle was not unloaded on its line: `params.entities` is the vehicle, and `simParams.mapping` maps it to `{name, number}`, the number being the figure the popup shows as the cargo not unloaded (72 and 60 for the first two trains in the game above). Road Vehicle 255, 256 and 257 had such entries (88.27M, 92.33M and 90.25M), and in the line window those three trucks of the wool line above carry the unload-problem icon, so the named vehicles can be placed on a line.
- **The "Town Rating Decreasing" popup is `town_rating_warning_nonperistent`** and "Town Rating Very Poor" is `town_rating_warning` (from the scripts' titles). Despite the "nonperistent" in its name, one of the five entries of the first had a `persisting` list. `param.key` is one of the six rating keys of [town-states.md](town-states.md); the popup text names the rating.
- **`rank` is the rank number counted from 1** and is the `potentialLevel` of the company ([company.md](company.md#company-and-rank)): the one rank-up entry had `rank` 6, the game's role table (`company_static_util.tl`) has Team Leader at place 6, and the save's `potentialLevel` was 6 (`level`, the rank claimed, was 3).
- **`level` of a town notification is a place in the game's town-level names, from 1**: Small Hamlet, Hamlet, Large Hamlet, Small Village, Village, Large Village, Small Town, and so on, so 7 is Small Town. Read from the script's list; the town's own level was not compared.
- **`cargoTypeId` 31 was furniture**, the 32nd place of the save's 37-entry cargo list. A second anchor: the next entry (11,400 clock units later) is a town subsidy offer for the same town whose `params.params.cargoType` is `::/cargos/furniture/furniture.cargo`.
- **`uid` of a subsidy offer is the entity id times 10,000 plus a counter.** In the `usedUids` of `subventions.gs`, the industry offers (`deliver_cargo`) all ended in 0000 (497,020,000 for entity 49,702), and the town offers (`deliver_cargo_town`) read 179,120,006, 179,120,015, 179,120,031 and 179,120,035 for town 17,912. The saw mill offer of the game in [Industry closing notifications](notifications-in-play.md#industry-closing-notifications-604) fits too (13,865 times 10,000). The second offer in [subsidies.md](subsidies.md) (uid 35,826) does not, so this is **Observed**, not a rule. `status` was 1 in both subsidy entries; its meaning is **Open**.
- **A missed offer.** The `subvention_missed` entry (`reason` `"Timeout"`) names the same town and cargo as the town offer 607,600 units earlier, and that offer's uid (179,120,031) reads `false` in `usedUids`, like any offer that is no longer open. The live industry offer (uid 497,020,000, `true`) is the one with the entry stamped 400 after its `spawnTime`, as under [Dismissing a notification](notifications-in-play.md#dismissing-a-notification-and-what-else-changes-604).

### One kind can fill the table

69 of the 100 entries were `overcrowding`, for just two station groups (44 and 25 entries), spread over the whole span of the table. 67 were `dismissed` and `expired`; the latest of each group (ids 862 and 864) was `dismissed` with `expired` false, and only those two carried `persisting`. Why the game makes a new entry for a group that already had one, and why the old ones expire, was not worked out: **Open**. The effect is that the 100 slots held 31 entries of every other kind.

### Persistent warnings

A warning that follows a state (a vehicle in poor condition, a full station, an industry about to close) is made with a `persisting` list naming its entities. The game's script re-checks the state periodically, sets the list when it makes the warning and clears it when the problem is gone or the parameters change; if the problem returns it makes a new entry. **Observed** on 604: 10 of the 100 entries had one (5 vehicle condition, 2 overcrowding, 1 town rating, 1 industry closing, 1 industry subsidy offer), and an entry that has one is not dropped when the table is trimmed.

### Bookkeeping tables

**Observed** on 604, same save. The rules are from the game's `notifications.script.tl` in `base/content/game_mechanics.zip`.

- **`wastedVehicles`**: vehicle entity to `true`. A transport vehicle of the player enters when its maintenance state is 0.2 or less and leaves only once it is above 0.3. The save had 5 entries, and they were exactly the 5 vehicles with a `vehiclecondition` entry that carried `persisting`. One of them (38,667) also had an older entry that had expired: a vehicle that recovers and falls again gets a new entry.
- **`vehicle2problem`**: vehicle entity to `{problemSince}`. A vehicle on its way, not stopped by the player, with speed 0 enters with the clock value at which it is first seen so. The `stuck_vehicle` warning is made once it has stood 300,000 units (the script's `1000 * 60 * 5`). The save had 3 entries, stamped 44,981,400, 44,983,800 and 45,000,600, 600 to 19,800 units before the save's clock (45,001,200), so none had reached the limit and there was no stuck-vehicle entry.
- **`stationGroup2overflowResolvedTimestamp`**: station group entity to a clock value, set the first time the group is seen not full and not changed again (the cooldown code that would use it is commented out in the script). 95 entries; the values run from 600 to 44,560,600, many of them 600. Both groups that have overcrowding entries are keys.
- **`noRoadConnectionUpdateTimestamp`** (44,819,800 here): when the no-road-connection check last ran. It runs again after 75 game days (75 times the default day length of 4,000 units, so 300,000); the save was 181,400 later.
- **`line2problemTimestamp`**: line entity to the clock value its problem was first seen. Empty in this save, which had no line warnings.

## The availability state

The state of `game_mechanics/notifications/availability_notifications.gs` has a `lastYear` number that matched the year on screen (2060, then 2061). It tracks the year but is not the clock. **Observed** on 604.

## Notifications in play

What the game wrote in our test games' saves (604): the "New Vehicles Available" popups and the model years behind them, what dismissing a notification changes, and the industry-spawn, industry-closing and stuck-vehicle entries, are in [notifications-in-play.md](notifications-in-play.md).
