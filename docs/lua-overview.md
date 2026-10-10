# Lua data in a save: the big picture

A short map of the Lua part of a save: where it sits, how many layers it has, what the file labels itself and what we had to work out. The details are in [lua-values.md](lua-values.md) (the byte encoding) and [script-states.md](script-states.md) (the states one by one). Checked on 604 (one played game of ours, no mods; the header and settings points also on 599 to 604, 22 catalog saves). Counts and depths are for that save. The survey of the middle of the stream ([below](#what-marks-the-middle)) also covers three catalog saves: [6105772](https://mod.io/g/transportfever3/m/autosave-map-1-2003-10-13) (568, 8 mods), [6204931](https://mod.io/g/transportfever3/m/empty-quarter) (585, no mods) and [6420121](https://mod.io/g/transportfever3/m/subarctic-002) (601, 1 mod).

## Where Lua sits in the stream

Most of a save is not Lua. The header holds two Lua tables, and one block of script states sits near the end. Everything between them (entities, vehicles, people, the map) is binary records. They are not wrapped in the Lua value tags, but they are not unmarked either: see [What marks the middle](#what-marks-the-middle).

```mermaid
flowchart LR
    H["Header<br/>fixed fields, preview, stats"] --> I["info table<br/>(Lua)"]
    I --> P["config params<br/>settings + mod options<br/>(Lua)"]
    P --> E["Entity data, map, journals<br/>binary records, named strings,<br/>a few thousand embedded Lua tables<br/>about 99.9% of the stream"]
    E --> S["Script-state block<br/>28 states in a 604 game<br/>(Lua, about 1 MB)"]
```

| Part | Lua? | Notes |
|---|---|---|
| Header fixed fields | no | [header.md](header.md) |
| `info` | yes | One table, `company` then `level`: two layers |
| `config params` | yes | A list of (id, table). The empty id holds the game settings, other ids are mods' options ([mods.md](mods.md#mod-options)) |
| Entity data and the rest of the middle | mostly no | Not self-describing. Read record by record, see [town-records.md](town-records.md), [models.md](models.md), [lines.md](lines.md). A few thousand small Lua tables sit inside it, see [below](#what-marks-the-middle) |
| Script states | yes | One block, about 98% of the way into a 946 MB stream, the states nearly back to back (**Observed**, 604) |

The settings table is flat: its keys are the dotted names (`map.size`, `advancedOptions.cargoIncome`), one layer, no nested tables. **Observed** on 599 to 604 (22 catalog saves and ours). [settings.md](settings.md) has the options.

## The layers inside a value

A value is a tag and a payload. Only a table holds other values, so depth is the depth of tables inside tables. Arrays are tables with numbers as keys and count as a layer.

```mermaid
flowchart TD
    V["value<br/>u32 tag"] -->|0| N[nil]
    V -->|1| B[boolean]
    V -->|2| F[number f64]
    V -->|3| ST["string<br/>u32 length + bytes"]
    V -->|4| T["table<br/>flag, u32 count"]
    T --> PR["count pairs of<br/>key value, value value"]
    PR --> V
```

## A script state on disk

```mermaid
flowchart LR
    A["path string<br/>game_mechanics/towns/town.gs"] --> B["flag byte<br/>(the table's tag 4 is left off)"]
    B --> C["u32 pair count"]
    C --> D["pairs: key, value<br/>keys are mostly strings"]
```

States follow each other in the block, each starting at its own path string, and a state ends where its last pair ends. In the 604 save the block was about 3 KB longer than its 28 states added up, so a few bytes sit between some states (not looked at). **Observed**, 604.

## How many and how deep (604, one save)

Depth counts the state table as layer 1.

| Group | States | Layers | Examples |
|---|---|---|---|
| Flat | 5 | 1 | `game_time.gs`, `reforestation.gs`, `context_helper.gs` |
| Shallow | 11 | 2 to 3 | `achievements.gs`, `loan.gs`, `mission.gs`, the small HUD states |
| Medium | 9 | 4 to 6 | `landmarks.gs`, `vehicle_modifier.gs`, `company.gs`, `town.gs`, `industries.gs` |
| Deep | 3 | 8 to 10 | `industry_workers.gs` (8), `notifications.gs` (9), `subventions.gs` (10) |

The 28 states take about 1.05 MB together. `industries.gs` is two thirds of that. The deep ones are lists of records, each record a table whose fields hold further tables. The music player's table has no script path and is not counted here ([script-states.md](script-states.md#the-music-player-state)).

## What marks the middle

The middle has no section table and no Lua wrapper, but three kinds of marker show up in every save surveyed. **Observed**, 568 to 604 (the four saves above; the survey is a byte scan of each stream, not a parse of the middle).

| Marker | What it looks like | What it gives |
|---|---|---|
| Length-prefixed strings | A `str` (u32 length, then bytes) inside a record. The u32 before the length is not the Lua string tag: it was often 0 or 1, and the float 1.0 (`00 00 80 3f`) before some building names | Resource ids (`.mdl`, `.gtex`, `.con`, `.street_template` and similar paths) that records point at, and field names that repeat per record (the statistics list keys of [statistics-lists.md](statistics-lists.md), the `happiness_*` names). Good anchors to search for |
| Counts and fixed prefixes | A `vec<T>` count in front of a list, or a prefix such as the heightmap's `ff ff ff ff 0e 00 00 00` | Lets a list be walked once its start is found. Nothing records where it ends in the stream |
| Embedded Lua tables | A real Lua table (`04 00 00 00 01`, a count, then pairs) in the middle of binary data | Parses with the reader of [lua-values.md](lua-values.md), no schema needed |

Counts per save (the string scan counts runs of printable bytes of 3 to 200 whose preceding u32 equals their length, so it misses strings that run into other printable bytes and may count a few by chance):

| Save | Stream | Length-prefixed strings | Distinct resource-id-like strings | `.mdl` ids | Embedded Lua tables | Where the tables sit |
|---|---|---|---|---|---|---|
| 568 ([6105772](https://mod.io/g/transportfever3/m/autosave-map-1-2003-10-13)) | 180 MB | 59,290 | 5,374 | 2,752 | 750 | 45 to 50% |
| 585 ([6204931](https://mod.io/g/transportfever3/m/empty-quarter)) | 83 MB | 27,515 | 4,170 | 2,769 | 319 | 40 to 45% |
| 601 ([6420121](https://mod.io/g/transportfever3/m/subarctic-002)) | 113 MB | 23,426 | 3,948 | 2,769 | 483 | 40 to 45% |
| 604 (ours) | 946 MB | about 1.07 million | 13,469 | 2,937 | 8,910 | 50 to 60% |

- **Strings come in bursts.** In 585 and 601 whole stretches of 5% hold none; in 568 almost every stretch holds some.
- **The model list is a fixed table.** The `.mdl` count is the same in 585 and 601 and within 17 in 568, so most of it is the game's own list (the model table of [models.md](models.md#the-model-table)). 604 has more; why is **open**.
- **The embedded tables come in two shapes**, found in every save. One has the keys `noise` and `pollution`. The other has `name` and `variant` (in 604 also a variant with a `metadata` key). In 568 they are nearly equal in number (374 and 375); in 585 (264 and 54), 601 (384 and 98) and 604 (4,676 and 3,588 plus 494) they are not, so one of each per object is not a rule. A few hundred in 604 hold `emissionConfig`, `maintenanceCost` and `price`, which look like construction or vehicle configs. All of them sit together in one stretch of the stream (about 840 KB in 604, 22 to 70 KB in the older saves).
- **What they belong to is open.** They look like per-building or per-construction data, since they sit as one block, but they were not matched to entities.
- **They are not script states.** The scan for these tables stopped at the script-state block, and they have no path string before them.

## What the file labels and what it does not

| In the stream | Not in the stream |
|---|---|
| Each state's script path | What a number means (seconds, a day count, an index) |
| Every key name, as a string | Which time base a time uses, see [calendar.md](calendar.md) |
| The type of every value (the tag) | That a numeric key is an array position rather than an id |
| How long every table is | Where the block starts: found by searching for a path |
| | Names for numeric ids, see [cargo-ids.md](cargo-ids.md) |

So a reader needs no schema to walk a state, but needs the game's files or a test in the game to say what a field is.

## Where the game explains the states

The game's script archives (`base/content`, modder-facing) say a good deal about the saved states. These are facts read from them, in our words:

- **A state is a game script's table.** The script API has a `getState` call on the game script repository that returns a table (`api/tealdef/api/res.d.tl`). A game script is described by up to five hooks: update, post-update, handle event, GUI update and GUI handle event (`GameScriptDesc` in `api/tealdef/api/type.d.tl`).
- **Each saved path has a declaration file.** The stored `x.gs` matches an `x.gs.lua` in the archives, which only names the script functions the game calls. For example `game_mechanics/game_time/game_time.gs.lua` in `game_mechanics.zip`. 24 of the 28 states have one: 17 in `game_mechanics.zip`, 5 in `gui.zip` and 2 in `mission.zip`. `industry_workers.gs`, `landmarks.gs`, `reforestation.gs` and `vehicle_modifier.gs` have none in the data archives; where they are declared is **open**.
- **The key names are declared as types.** The `.d.tl` files beside a script declare a record for its state. `game_mechanics/game_time/game_time.d.tl` lists the keys of the weather and time state with their types, matching what the save holds. They also list the allowed values of the mode strings (`Constant`, `Automatic`, `Local`, `Dynamic`), so `Local` is a real value of the time-of-day mode.
- **`version` is a schema number.** 10 of the 28 states have a `version` key (604 values: `game_time` 1, `emissions` 2, `subventions` 2, `achievements` 4, `company` 4, `celebrations` 5, `mission` 5, `guide_system` 5, `town` 8, `notifications` 24). The game's scripts compare it with the current number when they start and upgrade an older state (seen in `game_time.script.tl` and `towns.script.tl`). The other 18 have none. A save from an older game version can therefore hold older state shapes.

Facts about what each key means still come from tests in the game; the type files give names and types, not units.

## Open

- Where `industry_workers.gs`, `landmarks.gs`, `reforestation.gs` and `vehicle_modifier.gs` are declared.
- What follows the script-state block, and whether the music player state sits inside it.
- Depth and state counts on versions other than 604, and with mods (a mod adds its own states). The scan above parsed 19 states in the 568 save, 25 in 585 and 28 in 601 and 604; which ones the older saves lack was not looked at.
- Which entities the embedded `noise`/`pollution` and `name`/`variant` tables belong to, and why 604 has more `.mdl` ids than 585 and 601.
