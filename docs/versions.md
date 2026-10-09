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

The difference after the preview in 568 and 585 is **open**. Nothing after the header (script states, journal, entity data) was checked on any version other than 604.

## Calendar speed in the catalog (2026-10-09)

The 120 saves above, read with [tools/calendar_speed.py](../tools/calendar_speed.py) (field described in [script-states.md](script-states.md#the-calendar-speed-field)). The field was found exactly once in each, on every version.

| `millisPerDay` | Meaning | Saves |
|---|---|---|
| 4000 | 1.00x | 70 |
| 16000 | 0.25x (by the rule, not read in the game) | 22 |
| 0 | Paused | 11 |
| 1000 | 4.00x | 10 |
| 8000 | 0.50x | 6 |
| 1,440,000 | no slider step | 1 |

`playSpeed` in the same saves: 0 in 49 (written paused), 1 in 35, 2 in 3, 3 in 3, 4 in 29, 8 in 1.
