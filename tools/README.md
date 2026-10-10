# Tools

Small read-only Python scripts used to check the notes in `docs/`. They are reference code, not a supported product: no releases, no promise they work on your saves. Bug reports with evidence (format version, what you saw) are very welcome. We aren't taking feature requests for the scripts, sorry.

Python 3.14 or later, standard library only. Older Python works with the `zstandard` package installed.

None of these scripts write a save. For editing, see [tf3-save-editor](https://github.com/TBK/tf3-save-editor).

| Script | What it does |
|---|---|
| `tf3save.py` | Shared code: zstd helpers, the empty trailing frame, temperate cargo ids, `scan_records` (the town record scan), the calendar speed field and day table, a Lua value reader and `script_state(stream, path)`, and the New Game option labels (`setting_label`). Imported by the others |
| `save_header.py SAVE.sav [...]` | Print a save's header: version, start year, map size, money, counter, preview, mods, resources, a few settings. Importable as `read_header(path)` |
| `calendar_speed.py SAVE.sav [...]` | Print the calendar speed (`millisPerDay`), play speed and current day stored in a save. Importable as `tf3save.find_game_speed(stream)` and `find_day_table(stream)` |
| `town_states.py SAVE.sav [...]` | Print the per-town rating state from the `townStates` table |
| `schema/tf3-save-summary.v<N>.schema.json` | JSON Schema (draft 2020-12) of the summaries `mine_saves.py` writes, one file per `schema_version`: every field, its meaning, when it is null, and the `"3 (100%, default)"` labels. Any change to the layout gets a new version and a new file; a committed schema file is never edited, so a summary's `$schema` link keeps matching it |
| `save_preview.py OUT_DIR SAVE.sav [...]` | Write each save's preview as a PNG, right way up |
| `mine_saves.py OUT_DIR SAVE_OR_MODDIR [...]` | Summarise many saves (or mod.io mod directories, including their editor `maps/`) into `OUT_DIR/<id>-<name>/tf3-save-summary.json` and `OUT_DIR/index.csv`: header (including the map seed), settings as `"3 (100%, default)"`, shown date, calendar and play speed, rank, counters, subsidies. Each summary names the commit of the `tools/` scripts that built it and is rebuilt when that changes. Facts only, no local paths |

## Editor setup

VS Code shows an "untrusted schema" warning on the `$schema` line of the summaries. How to clear it: [docs/developer/vscode-schema.md](../docs/developer/vscode-schema.md).

## Using them on other people's saves

Previews and saves belong to the people who made them. The scripts read them on your machine; do not republish their output without checking. The summaries from `mine_saves.py` hold only facts (version, sizes, counts) plus the catalog name, author and link that mod.io already shows publicly.
