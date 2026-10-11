# Tools

Small read-only Python scripts used to check the notes in `docs/`. They are reference code, not a supported product: no releases, no promise they work on your saves. Bug reports with evidence (format version, what you saw) are very welcome. We aren't taking feature requests for the scripts, sorry.

Python 3.14 or later, standard library only. Older Python works with the `zstandard` package installed.

None of these scripts write a save. For editing, see [tf3-save-editor](https://github.com/TBK/tf3-save-editor).

| Script | What it does |
|---|---|
| `tf3save.py` | Shared code: zstd helpers, the empty trailing frame, temperate cargo ids, `scan_records` (the town record scan), `cargo_entries` and `cargo_list` (the save's own cargo list, which gives the cargo ids), the calendar speed field and day table, a Lua value reader and `script_state(stream, path)`, and the New Game option labels (`setting_label`). Imported by the others |
| `save_header.py SAVE.sav [...]` | Print a save's header: version, start year, map size, money, counter, preview, mods, resources, a few settings. Importable as `read_header(path)` |
| `calendar_speed.py SAVE.sav [...]` | Print the calendar speed (`millisPerDay`), play speed and current day stored in a save. Importable as `tf3save.find_game_speed(stream)` and `find_day_table(stream)` |
| `town_states.py SAVE.sav [...]` | Print the per-town rating state from the `townStates` table |
| `schema/tf3-save-summary.v<N>.schema.json` | JSON Schema (draft 2020-12) of the summaries `mine_saves.py` writes, one file per `schema_version`: every field, its meaning, when it is null, and the `"3 (100%, default)"` labels. Any change to the layout gets a new version and a new file; a committed schema file is never edited, so a summary's `$schema` link keeps matching it |
| `check_links.py [REPO_ROOT]` | Check the repo's Markdown files: relative links and `#anchors` that point nowhere, notes in `docs/` missing from `docs/README.md`, scripts missing from this table. Reads no saves. Exit status 1 when it reports anything |
| `facts_index.py [REPO_ROOT] [--max-words N] [--max-section-words N] [--outline NOTE]` | Outline the notes in `docs/`: words, headings, links in and out per note, biggest first, with a mark on notes over the word limit (default 3500) as split candidates, then the sections over 1500 words. `--outline docs/NOTE.md` lists that note's headings with line numbers and the words under each, so one section can be opened and not the whole note. Run it before a split or a consistency pass. Reads no saves |
| `find_dupes.py [REPO_ROOT] [--note NOTE] [--kind code\|number] [--where TERM] [--prose] [--since REV]` | Find what more than one note in `docs/` mentions: code spans and numbers of four or more digits shared by 2 to 6 notes (test save names left out), the pairs of notes sharing the most, and the pairs sharing terms with no link between them. `--note` keeps what involves one note; `--where TERM` lists every line with the term, its note and heading. `--prose` finds the same wording in two notes (runs of eight words). `--since REV` compares with `docs/` at an older revision: shared terms before and after (a split's new note counted with the note it came from), terms in more notes than before, and links that name a term their target note has lost. A shared term is a lead, not a defect: pointers to a home note share terms with it, and a split raises the count. Reads no saves |
| `lint_docs.py [REPO_ROOT] [--since REV]` | Check a change to `docs/` before committing it (the working tree against `HEAD`, or against an older revision for a series of commits). Errors, exit status 1: anything `check_links.py` reports, a note or section that crossed its word limit, a link to a note that lost the term it names. Warnings, on the changed lines only: the same wording in two notes, terms in more notes than before, notes that share terms without linking. One line per finding. Reads no saves |
| `industry_chains.py [--content DIR] [--json] [--out DIR]` | Print the install's industry chains as Markdown tables (or JSON): recipes, boosters, climates per industry and per cargo, cargo classes, industries by rank. Reads the install's text files at run time (finds the Steam library itself, or pass `--content` with its `base/content` folder) and prints no install path. Warns on stderr where the industry and economy files disagree. See [docs/industry-chains.md](../docs/industry-chains.md) |
| `save_preview.py OUT_DIR SAVE.sav [...]` | Write each save's preview as a PNG, right way up |
| `mine_saves.py OUT_DIR SAVE_OR_MODDIR [...]` | Summarise many saves (or mod.io mod directories, including their editor `maps/`) into `OUT_DIR/<id>-<name>/tf3-save-summary.json` and `OUT_DIR/index.csv`: header (including the map seed), the cargo list and any cargo a mod adds, settings as `"3 (100%, default)"`, shown date, calendar and play speed, rank, counters, subsidies. Each summary names the commit of the `tools/` scripts that built it and is rebuilt when that changes. Facts only, no local paths |

## Editor setup

VS Code shows an "untrusted schema" warning on the `$schema` line of the summaries. How to clear it: [docs/developer/vscode-schema.md](../docs/developer/vscode-schema.md).

## Using them on other people's saves

Previews and saves belong to the people who made them. The scripts read them on your machine; do not republish their output without checking. The summaries from `mine_saves.py` hold only facts (version, sizes, counts) plus the catalog name, author and link that mod.io already shows publicly.
