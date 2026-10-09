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
