# Format versions

The u32 after the `tf**` magic. The game reads older versions; what it does when it re-saves one (upgrade or keep) is **open**.

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
