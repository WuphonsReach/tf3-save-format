# Tools

Small read-only Python scripts used to check the notes in `docs/`. They are reference code, not a supported product: no releases, no promise they work on your saves. Bug reports with evidence (format version, what you saw) are very welcome. We aren't taking feature requests for the scripts, sorry.

Python 3.14 or later, standard library only. Older Python works with the `zstandard` package installed.

None of these scripts write a save. For editing, see [tf3-save-editor](https://github.com/TBK/tf3-save-editor).

| Script | What it does |
|---|---|
| `tf3save.py` | Shared code: zstd helpers, the empty trailing frame, temperate cargo ids, `scan_records` (the town record scan). Imported by the others |
| `save_header.py SAVE.sav [...]` | Print a save's header: version, start year, map size, money, counter, preview, mods, resources, a few settings. Importable as `read_header(path)` |
| `calendar_speed.py SAVE.sav [...]` | Print the calendar speed (`millisPerDay`), play speed and current day stored in a save. Importable as `tf3save.find_game_speed(stream)` and `find_day_table(stream)` |
| `town_states.py SAVE.sav [...]` | Print the per-town rating state from the `townStates` table |
| `save_preview.py OUT_DIR SAVE.sav [...]` | Write each save's preview as a PNG, right way up |
| `mine_saves.py OUT_DIR SAVE_OR_MODDIR [...]` | Summarise many saves (or mod.io mod directories, including their editor `maps/`) into `OUT_DIR/<id>-<name>/summary.json` and `OUT_DIR/index.csv`. Facts only, no local paths |

## Using them on other people's saves

Previews and saves belong to the people who made them. The scripts read them on your machine; do not republish their output without checking. The summaries from `mine_saves.py` hold only facts (version, sizes, counts) plus the catalog name, author and link that mod.io already shows publicly.
