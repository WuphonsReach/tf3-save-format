# Notifications

State of `game_mechanics/notifications/notifications.gs`. The game's popups and its log keep one entry per notification here. Subsidy offers are notifications ([subsidies.md](subsidies.md)), and so is the hot air balloon sighting ([fun-elements.md](fun-elements.md#the-notification)). The state is read like any script state ([script-states.md](script-states.md#finding-a-table)).

## Entry fields

**Observed** on 585 and 604 for subsidy entries, on 604 for the balloon entry.

| Key | Holds |
|---|---|
| `type` | A script path. The base game's start with `::/game_mechanics/notifications/types/` (for example `subvention_notification.script`). A mod's carries the mod id before `::` (`urbangames_deluxe_upgrade_pack::/fun_elements/balloon_notification.script`) |
| `params` | What the type needs. Subsidies: a resource path under `::/game_mechanics/subventions/`, `stockListEntity`, and `simParams.mapping` with the name of the industry or town. Balloon: `entity` and `townEntity`, each `{entity, revision.num}` |
| `simParams` | Empty in the balloon entry |
| `timestamp` | Game-clock time ([calendar.md](calendar.md)) |
| `dismissed`, `hidden`, `hideInLogAndPopups`, `playedInitialSound` | Booleans |
| `autoDismissDuration`, `expired` | Seen on the balloon entry: 60,000 (15 days at 1.00x) and `true` after it left |

- The table `ignored.types` lists notification types with a boolean, next to the base game's types. The balloon's type is in it with `false`.
- An entry stays in the table after it is dismissed or has expired (**Observed**, balloon).
- The subsidy type string appears once in a game near its start and 9 and 10 times in a game 160 years in. The game showed both an industry request ("looking for a reputable transportation company") and a town request ("requires a skilled logistics firm"). How the two kinds are told apart in the file is **Open**.

## Types

Path strings for notification scripts under `::/game_mechanics/notifications/types/` appear in the stream. A played 604 game had 21 different ones: `animaldespawn`, `availability`, `cargo_rtc_warning`, `con_availability`, `industry_close`, `industry_spawn`, `line_station_warning`, `line_warning`, `newcargodemand`, `noroadconnection`, `overcrowding`, `station_useless`, `stuck_vehicle`, `subvention`, `subvention_missed`, `subvention_notification`, `town_rating_warning`, `town_rating_warning_nonperistent`, `town_warning`, `vehicle_warning`, `vehiclecondition`. **Observed**; which one drives which message in the game was not matched, for example the "Town Rating Decreasing" popup most likely uses one of the two `town_rating_warning` types.

## The availability state

The state of `game_mechanics/notifications/availability_notifications.gs` has a `lastYear` number that matched the year on screen (2060, then 2061). It tracks the year but is not the clock. **Observed** on 604.

## Dismissing a notification, and what else changes (604)

**Observed** on 604, one new game, two saves 46,400 clock units apart (2,246,600 and 2,293,000) with the player dismissing notifications between them and a new subsidy offer arriving.

- **Dismissing sets `dismissed` and nothing else.** The "active reward effect" banner of the completed subsidy ([subsidies.md](subsidies.md#completion-604)), entry 15 of the notification state (`subvention_notification.script`, timestamp 2,196,600, 600 units after the subsidy's `completedTime`), went from `dismissed = false` to `true`. Its `expired` stayed `false`, `tracked` stayed `true` and the entry stayed in the table. The subsidy's own state and its effect were unchanged.
- **A dismissed offer is still on offer.** The second subsidy offer (a "Supply Industry" offer, `deliver_cargo`, spawned at clock 2,253,000) appeared as a new entry 17 with timestamp 2,253,400 (400 after the spawn), already `dismissed = true` and `expired = false` when saved. In the subsidies state it was still in `proposedSubventions` and its uid was in `usedUids`. So dismissing the popup does not decline or remove the offer. The entry's `simParams.mapping` names the industry the offer is about, as in the other subsidy notifications. `maxId` rose from 16 to 17, and a new id was added to the list of ids just before it, so the ids are kept in two places.
- **Entries expire with a `persisting` reference.** Entry 12 (a `vehiclecondition.script` notification for one road vehicle) went from `expired = false` to `true` between the saves, and its `persisting` list (one entity reference, the vehicle's) disappeared at the same time. An expired entry keeps its place and flags but drops the reference. Why this one expired is **Open**. An industry-spawn entry (16) went from `dismissed = false`, `expired = false` to `true`, `true`.
- Another table in the same state (a list of ids with a `problemSince` clock value, 10 to 14 entries) changed entirely: ids appeared and disappeared with `problemSince` set to the clock of the save or a little before. It looks like the set of entities that currently have a problem (the vehicle-condition warnings), refreshed each time. **Open**.

## Industry spawn notifications (604)

**Observed** on 604 in the new Small 1 : 3 game of [subsidies.md](subsidies.md#a-new-game-an-offer-its-expiry-and-an-accepted-subsidy-604), in saves `1208` to `1312`.

- **Every industry that appeared in play has a notification.** Its type is `::/game_mechanics/notifications/types/industry_spawn.script`, its params hold `simParams.mapping` with the industry's name, and it has a `timestamp` like the subsidy ones. The game had 12 by clock 5,997,000, none in the save at 570,600 and one (Bromsgrove Quarry North, 734,600) in `1208`: 10 primaries (the quarries North and West, three fishing industries (West, South and East), an oil platform, two crop farms, a coal mine and an iron ore mine) and 2 secondaries (a canning factory and a steel mill). The map's own industries have none.
- **Times.** 734,600; 1,473,800; 2,197,800; 2,937,800; 3,657,800; 3,737,000 (the canning factory and the steel mill at the same time); 3,745,000; 3,762,600; 4,401,000; 5,117,000; 5,861,800. They are 4,100 to 110,000 units after the half-year boundary at which the industry's production list was created ([statistics-lists.md](statistics-lists.md#when-an-industrys-lists-begin-and-industries-that-appear-in-play-604)): 730,500, 1,461,000, 2,191,500, 2,922,000, 3,652,500 (fishery East, a coal mine and an iron ore mine), 4,383,000, 5,113,500 and 5,844,000. So the industry exists from the boundary and the notification comes later. The two secondaries have no production list and their notification times (3,737,000) are not on a boundary, so when they were created is **Open**.
- **A rename changes the name in the notification.** The four fishing industries were renamed in the player's next save (`1312`), and the `mapping` names of their spawn notifications read the new names (Todmorden Fishing 2, 3 and 4; the original Fishing Grounds, which is not a spawn, was renamed inside a subsidy notification the same way). So the name in `simParams.mapping` is not a copy from the time of the notification, or the game rewrites it on rename. Which of the two was not tested.

## Industry closing notifications (604)

**Observed** on 604 in the Small 1 : 3 game of [subsidies.md](subsidies.md#a-new-game-an-offer-its-expiry-and-an-accepted-subsidy-604): saves `1438` and `1439` (no alert) and `1440` (clock 11,791,000, paused, the saw mill's "Industry Closing" popup on screen with 47m 11s left). One closing in one game.

- **The entry.** Type `::/game_mechanics/notifications/types/industry_close.script`. Its `params` hold `entity` (the industry's entity id, 13,865, as `{entity, revision}`) and `resName` (the industry's `.con` path), `simParams.mapping` holds the name, and `persisting` lists the same entity. `timestamp` was 11,700,600; `tracked` and `playedInitialSound` were `true`, `dismissed` and `expired` `false`. The entry holds no countdown, so the time left is not read from the notification.
- **The deadline is a field of the industry.** The game's own script (`game_mechanics/industries/industries.script.tl` in `base/content/game_mechanics.zip`) keeps a `closureTimeStamp` on the industry. A value of 0 or less means not closing. When it decides to close an industry it sets the field to the game time plus `closureCountdownTimeSpanYears` (2, from `game_mechanics/industries/industries_config.res.lua`) times the default year length, and a command (`makeIndustrySetDespawnTimeCmd`, `api/cmd.d.tl`) writes it. It tests every 100 ticks, and only industries whose last delivery or shipment is `unusedTimeSpanYears` (5) years back are candidates. The same file also names an `extendTimeSpanYears` of 0.5, not tested here.
- **Where it is in the file.** In `1440` the value 14,622,000 appears once in the whole stream, as an `i64` in a small record that starts with the industry's entity id (a `u32`), followed by a `u32` (8,480 for the saw mill), a `u32` 1, a `u32` 0 and the `i64`. The same record in `1439` and `1438` held 0 in that place. Find it by searching for the entity id taken from the notification, then checking the shape. The records of the other industries in the same run (the cement plant, canning factory and steel mill with the third value 1; a livestock farm, a quarry, a crop farm and a fishing industry with 5) held 0, as none was closing. What the third value means is **Open**.
- **The numbers agree.** 14,622,000 minus the countdown of 2 x 1,461,000 (a year, [finances.md](finances.md#periods)) is 11,700,000, 600 units before the notification's timestamp. The popup's 47m 11s is 2,831,000 units, which is 14,622,000 minus the save's clock. So the notification is written 600 units after the field is set, and the popup counts down to the field at the game clock.

## Stuck-vehicle notifications (604)

**Observed** on 604 in the Small 1 : 3 game of [subsidies.md](subsidies.md#a-new-game-an-offer-its-expiry-and-an-accepted-subsidy-604), in a save at clock 10,026,200 (`1401`), made while ships queued for the one terminal of a port.

- **Type.** `::/game_mechanics/notifications/types/stuck_vehicle.script`. The string occurred once in the save 3.6 million units earlier (clock 6,428,600, only in the type list) and six times in `1401`: once in the type list and five in notification entries.
- **The five entries** carry `timestamp` 7,747,800, 8,017,400, 8,166,200, 8,322,200 and 9,392,600, and in `params` an `entity` (a plain number, 17,914 in the first, which is also the entity id of the largest of the game's three towns in the town building records of [town-records.md](town-records.md#town-buildings-and-historic-preservation-604), so at least that entry's entity may be a town and not the ship, and 33,629 in the last; in the other three it was not a plain number and was not read). The player's screenshots from before the save showed a ship window with the line "Ship 8 has been stuck for a while without moving" and 0 km/h, with three fishing lines on one port terminal. Which entity id is Ship 8, and whether one of the five entries is that message, was not worked out. The entries give the time the warning was raised, not how long the vehicle had stood. Spoiled cargo seen in the same window: [statistics-lists.md](statistics-lists.md#spoiled-cargo-and-itemslost-604).
