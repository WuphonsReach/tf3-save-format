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
