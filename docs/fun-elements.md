# Fun elements: the hot air balloon

The Deluxe Upgrade mod (`urbangames_deluxe_upgrade_pack`) sends an Urban Games hot air balloon over the map now and then. The game raises a "Hot Air Balloon Sighting" notification, and its window, titled "Urban Games Hot Air Balloon", thanks the player for buying the Deluxe Edition. A save holds the balloon in three places: the mod's script state, a notification entry ([notifications.md](notifications.md)), and a model instance like the animals' ([models.md](models.md#the-model-instance-record)).

All of it is **Observed** on 604 in one game (the [Tiny temperate game](test-games.md#tiny-temperate-games): temperate, Tiny 1 : 4, 2048 x 6144 m, start 1900, calendar speed 1.00x throughout). Five saves were read: the new game on 1 January 1900, an autosave on 11 May, a save made paused on 20 September 1900 just after the sighting, an autosave of the same paused moment (same clock), and a save on 2 January 1901 after the game had run on and the balloon had gone. Times are game-clock values, 4000 per day at 1.00x ([calendar.md](calendar.md)).

## The script state

The state of the mod script `fun_elements/balloon.gs`. In the stream the path `str` follows a `str` holding the mod id, then the table body as for the base game's scripts ([script-states.md](script-states.md#finding-a-table)):

```
1e 00 00 00 urbangames_deluxe_upgrade_pack
17 00 00 00 fun_elements/balloon.gs 00 02 00 00 00 ...
```

| Key | Content |
|---|---|
| `balloons` | Table keyed 1, 2, … with one entry per balloon in the air. Empty before the balloon came. |
| `nextSpawnTime` | Game-clock time of the next balloon |

A balloon entry:

| Key | Content | Seen |
|---|---|---|
| `entity` | The balloon's entity id | 6786 |
| `position` | `x`, `y`, `z` in metres. `x` and `y` are map coordinates, with the map's centre at 0, 0 (the grid in [terrain.md](terrain.md#the-heightmap)). `z` is the height above the ground, not the world height | -404.43, 2820.87, 200 |
| `velocity` | `x`, `y`, `z` in metres per second | 8.193, -5.734, 0 (10.0 m/s level flight) |
| `sighted` | `true` once the notification has been raised | `true` |

- The state exists from the start of a game with the mod, with `balloons` empty. `nextSpawnTime` was 1,006,587 (9 September 1900) in the new game and the May autosave. By the September save it was 10,455,186 (27 February 1907), about six and a half years later. How the next time is chosen is **Open** (one interval seen).
- The balloon was about 250 m from the map's edge at y = +3072, and 620 m from its edge at x = -1024. Which edge that is on screen was not checked.
- The script's `z` of 200 is the height above the ground. The model instance (below) has a world `z` of 209.45, and the heightmap gives a ground height of 9.45 m at that x and y (bilinear between the four grid points), so world `z` = ground + 200.
- Right after the table, the stream has the string `spawnBalloon` and some binary data. In the September save that data also holds a copy of the velocity numbers, and the copy is still there in January, after the balloon has gone. So it does not follow the live balloon. What it is, perhaps a scheduled call, is **Open**.

## The notification

An entry in the `notifications` table of `game_mechanics/notifications/notifications.gs`, the same table as the subsidy entries. The fields are in [notifications.md](notifications.md#entry-layout): `type`, `params`, `simParams` and `autoDismissDuration` sit inside the entry's `notification` table. That layout was read in a later game; this entry was read before it was known and very likely has it too (**Open**). What this entry held:

- `type` is `urbangames_deluxe_upgrade_pack::/fun_elements/balloon_notification.script`.
- `params.entity` is `{entity, revision.num}` for the balloon (6786, revision 5). `params.townEntity` is a town (3784, the town that the subsidy entries' `simParams.mapping` in the same save names Middleham). So the sighting is tied to a town, not to an industry. How the town is picked, for example the nearest one, is **Open**.
- `autoDismissDuration` 60,000 (15 days at 1.00x), `simParams` empty, `playedInitialSound` `true`.
- `timestamp` 1,044,400 is 19 September 1900, the day before the save. That is ten days after `nextSpawnTime`, so the balloon flew for a while before the sighting.
- The table `ignored.types` lists the balloon notification type with `false`.

## The model instance

The balloon has a model instance record of the shape described in [models.md](models.md#the-model-instance-record), with one instance. Both matrices are the identity rotation with the translation -404.43, 2820.87, 209.45, which equals the script's `x` and `y` to f32 precision.

- The model id is the balloon model's entry in the model table ([models.md](models.md#the-model-table)). Its path is `vehicle/zeppelin/hot_air_balloon/hot_air_balloon.mdl`, from the mod `urbangames_deluxe_upgrade_pack`. Its id was 4503 (`97 11 00 00`) in this game. Like any model id, it depends on the models installed, so read it from the table.
- Find the instance by searching for that model id with a plausible position 52 bytes after it, or for the 8 bytes of the script's `x` and `y` as `f32`. In the September saves it sat 3.0 MB after the header, among the animals' records. The saves from before the balloon came have no instance with that model id.
- The rest of the balloon entity, and whether it has other components, is **Open**.

## After the balloon leaves

In the January 1901 save, run on from the September one at 1.00x:

- `balloons` is empty again, and `nextSpawnTime` is unchanged (27 February 1907). The departure did not set a new spawn time.
- No model instance uses the balloon's model id.
- The notification entry stays in the `notifications` table, with `dismissed` and `expired` both `true` and its `timestamp`, `entity` and `townEntity` unchanged. The game removes the balloon but keeps the log entry.
- When the balloon left, between 20 September 1900 and 2 January 1901, is **Open**.

## Other fun-element states

On the same saves, `game_mechanics/fun_elements/fun_elements.gs` held only `spawnNextUfoAtGameTime` (5,302,823, 19 August 1903), unchanged from January to September. `game_mechanics/fun_elements/fireworks.gs` was an empty table. Neither was tested in play. **Observed**.

## Open

- How spawn times and the town in the notification are chosen, and whether more than one balloon can be up at once (`balloons` is a list).
- Whether `position` moves along `velocity` while the game runs. Both September saves are the same paused moment.
- When and how the balloon leaves: after a fixed time, at the map's edge, or on another rule.
- The UFO: what it does, and what the save holds while one is on the map.
