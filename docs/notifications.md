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
