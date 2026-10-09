# Format versions

The u32 after the `tf**` magic. The game reads older versions. When it re-saves one it writes the current version: a 585 save came back as 604 (**Observed**, one save; the header's `value` field kept 585, see [header.md](header.md)).

## Seen in the mod.io catalog (2026-10-08)

120 public savegames from the Transport Fever 3 catalog on mod.io, read with [tools/save_header.py](../tools/save_header.py):

| Version | Saves | Header |
|---|---|---|
| 604 | 79 | Reads in full |
| 601 | 27 | Reads in full, same layout as 604 |
| 599 | 4 | Reads in full, same layout as 604 |
| 585 | 3 | Same up to the preview, then differs |
| 568 | 7 | Same up to the preview, then differs (fails in the stats block) |

The difference after the preview in 568 and 585 is **open**. After the header, the script states, the calendar speed field and the day table were read on all five versions (see [script-states.md](script-states.md) and [calendar.md](calendar.md)). The money journal and the rest of the entity data were checked on 604 only, apart from the town record counts in [cargo-ids.md](cargo-ids.md).

## Calendar speed in the catalog (2026-10-09)

The 120 saves above, read with [tools/calendar_speed.py](../tools/calendar_speed.py) (field described in [calendar.md](calendar.md#the-calendar-speed-field)). The field was found exactly once in each, on every version.

| `millisPerDay` | Meaning | Saves |
|---|---|---|
| 4000 | 1.00x | 70 |
| 16000 | 0.25x (by the rule, not read in the game) | 22 |
| 0 | Paused | 11 |
| 1000 | 4.00x | 10 |
| 8000 | 0.50x | 6 |
| 1,440,000 | no slider step | 1 |

`playSpeed` in the same saves: 0 in 49 (written paused), 1 in 35, 2 in 3, 3 in 3, 4 in 29, 8 in 1.

The day table that follows the field ([calendar.md](calendar.md#the-day-table)) parsed in all 120. 88 had consecutive day numbers and rising ticks; 32 had jumps or repeats. 50 were exactly 4000 ticks per day throughout. Start years: 1900 in 64, 2020 in 20, the rest 1910 to 2010 (two saves start on a day other than 1 January). The header's date field equalled the table's last day in all 120.

## Summarised catalog (2026-10-09)

Every savegame and editor map in the catalog's mod directories, summarised with [tools/mine_saves.py](../tools/mine_saves.py): 244 entries, 180 savegames and 64 editor maps. The catalog had grown since the 120 saves above, which are all among them. Notes that say "the 120 catalog saves" mean the tables above; [cargo-ids.md](cargo-ids.md) counts the 244.

| Version | Savegames | Editor maps |
|---|---|---|
| 604 | 130 | 59 |
| 601 | 36 | 5 |
| 599 | 4 | 0 |
| 585 | 3 | 0 |
| 568 | 7 | 0 |
