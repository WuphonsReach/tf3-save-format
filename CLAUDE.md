# tf3-save-format

Public documentation of the Transport Fever 3 `.sav` format. Licensed MIT OR Apache-2.0, matching tf3-save-editor. The notes in `docs/` are the product; `tools/` holds read-only reference scripts with no support (see `tools/README.md`).

## Related local repos

| Repo | Role |
|---|---|
| `../tf3-save-editor` | Fork of TBK/tf3-save-editor (MIT OR Apache-2.0, used here under both). Its `docs/FORMAT.md` is the base layout for container, header and Lua states. Code in `tools/` follows its readers (`header.rs`, `lua.rs`); the notice is in `THIRD_PARTY_NOTICES.md`. |

## Rules for what goes in

- Facts about the format only. Never commit `.sav` files or decompressed streams; `.gitignore` blocks the common ones.
- Working files go in `local/` (gitignored), not loose in the repo: pictures, screenshots, extracted previews, scratch output, working notes. Temporary files go in the scratchpad directory. A picture made into `local/` (or any other folder git excludes) needs no permission: make it when it helps. The ask-first rule below is for images that go into the repo.
- Images in the repo are only our own work (diagrams, or screenshots of our own saves), in `docs/images/`, and only when the user asks for that file. Never extracted previews or screenshots of other people's maps. `.gitignore` blocks `*.jpg`, `*.jpeg` and `*.webp` (the game's preview next to each save) but not `*.png`, so a stray PNG is not caught: write one outside `local/` or the scratchpad only for such a diagram, and read `git status` before every `git add`. Never `git add -A` or `git add .`; name the files.
- Use the game's internal name for a thing, not the player's word or the on-screen label: `cement` for "concrete", `vegetables` for cabbage or lettuce, `ship` for boat or trawler. `docs/glossary.md` lists keys, labels and common aliases, and the words that could be two keys (ask, do not guess). Add a word to it when the user corrects one.
- Write notes in our own words. Do not copy text from `tf3-save-editor`'s `FORMAT.md`. Link to it and credit it instead. Code ported from it keeps a pointer to `THIRD_PARTY_NOTICES.md`.
- Cite mod.io catalog saves by mod id and URL. Record only facts read from them (version, map size, start year, mod list, counts). No per-save dumps in the repo.
- Strip local details before committing: home paths, file mtimes, Steam user ids, install paths. Tool output must not contain them either (`mine_saves.py` keeps size and mtime in a gitignored `.mine_state.json`).
- Saves carry other people's local details. A mod's script state can keep a Lua error message whose chunk name is the mod's full install path on the player's machine, often with their OS account name in it (see `docs/script-states.md`). The company name defaults to the player's account display name (see `docs/entity-names.md`). Never copy either into a note, commit message or tool output, from catalog saves or the user's own. Write the path as `<path>/mod.io/10640/mods/<id>/...` and the name as `<name> Transport`, and mask them the same way when printing strings from a save while working.
- Tag each claim with the format versions it was checked on (for example "568 to 604" or "604 only").
- Label how sure a format claim is: Confirmed, Observed or Open (defined in `docs/README.md`). `docs/versions.md` (dated counts) is exempt.
- Offsets move between saves. Describe how to find a structure by pattern, never by a fixed offset.

## Keeping the indexes current

`docs/README.md` (notes) and `tools/README.md` (scripts) are the navigation layer: read them first to find where a fact lives, and grep from there.

- A new note in `docs/` gets a row in the `docs/README.md` table in the same commit. The "Covers" cell names what the note holds, not just its topic. Add a row for a new script to `tools/README.md` the same way.
- When a note's scope changes (a section added, split or moved to another note), update its "Covers" cell and the links that pointed at the old place.
- Before adding a fact, grep for it. Each fact has one home note; other notes link to it instead of repeating it.
- Renaming or deleting a note: fix every link to it and its row in the index.
- Run `python3 -I tools/lint_docs.py` before committing a change to any `.md` file (add `--since REV` to check a series of commits). It must report 0 errors: dead links and anchors, notes or scripts missing from an index (`check_links.py`), a note or section that crossed its word limit, a link to a note that lost the fact it names. Its warnings are leads, not defects: open the lines it names (with `find_dupes.py --where TERM` for a term) and judge whether a fact is stated twice. Do not reword to make a warning go away.
- To find where a fact lives, or before a consistency pass or a split, use the index scripts and not whole-note reads (a pass that read most of `docs/` several times cost over 350,000 tokens):
  - `python3 -I tools/facts_index.py` lists note sizes, link counts, notes over the word limit and long sections. `--outline docs/NOTE.md` gives a note's headings with line numbers and word counts; open only the sections you need. Add `--bullets` for a row per paragraph or bullet (first words and size): use it to plan a split instead of printing the section.
  - `python3 -I tools/find_dupes.py` lists terms shared by several notes and note pairs that share terms without linking; `--note docs/NOTE.md` narrows it to one note, `--where TERM` lists every mention of one term, `--prose` finds the same wording in two notes, `--since REV` compares with an older revision (a split's new note counted with the note it came from).
  - A shared term is a lead: a pointer to the home note shares terms with it, and a split raises the count, so it is not a score to minimise. Only `--prose` compares wording: for a stale claim, grep the phrase (and its variants) across `docs/`.
- Put no counts or dates in the README tables (see Conventions); they belong in `docs/versions.md`.
- A graph or index tool's output (for example a generated knowledge graph) stays out of git. Add its output folder to `.gitignore` before the first run.

## Tools

- Never write or modify a `.sav`. Output (PNGs, JSON summaries) goes to a directory the caller names.
- Standard library first (Python 3.14 for zstd; older Python needs `zstandard`). numpy, Pillow and the `tesseract` program are accepted when a job needs image work or OCR (`town_centre.py`, `screenshot_index.py`; the user is happy with them as long as their licences cause no problem: numpy BSD-3-Clause, Pillow MIT-CMU/HPND, tesseract Apache-2.0, nothing bundled). Import them at run time so the commands that do not need them still work without them, and say in the script's docstring and its `tools/README.md` row what needs them. Any other package or program: ask first. Shared code is in `tools/tf3save.py`; new scripts import it. Some private scripts import it too, so keep its function names and return shapes stable.
- To read an SVG a script wrote, convert it with `rsvg-convert -w 1400 in.svg -o PNG` into the scratchpad; it is a viewing aid and no script depends on it. Which tool for which job, and the headless Firefox hang: `docs/developer/tooling.md`.
- To show a place with named segments and vehicles ("which segment?"), follow `.claude/skills/area-map/SKILL.md`: `terrain_map.py --crop --label --vehicles --name`, pictures to `local/games/<game>/maps/<topic>/`.
- VS Code flags the `$schema` URL in summaries as untrusted; the local `.vscode/settings.json` fix is in `docs/developer/vscode-schema.md`. Do not change `SCHEMA_URL` for it.
- Test against real saves before committing, with output to a scratch directory outside the repo.

## Game install

- Modder-facing files may be read: `api/tealdef/`, `base/tealdef/`, `base/mod.json`, `vscode-template/`.
- The `base/content/` archives and the loose `.lua`/`.tl` files beside them may be opened to learn facts. Urban Games' modding wiki treats that folder as base content for modders and requires the source to be named when game files are used. Conditions:
  - Data and script archives (`economy`, `scripts`, `climates`, `game_mechanics`, `mission`, `gui`, `names`, `base`): read for facts.
  - `locale.zip`: match string keys to on-screen labels. Never republish string tables, and never extract the fonts (third-party works).
  - Media archives (`animal`, `characters`, `warehouses`, `placeholders`, `model_editor`): only for a specific question, and only text metadata (`.mdl`, `.lua`). Never meshes, textures or audio.
  - `music.zip`: do not open.
  - Publish only facts in our own words, with short identifiers: resource paths, key names, ids, numbers. No pasted code, no copied tables, no line-by-line walk through a script's logic. Name the file a fact came from (for example `economy/dry.eco.lua` in `base/content/economy.zip`).
  - Never commit extracted files, and never bundle base data in a tool. A tool may read the user's install at run time.
  - If an entry is encrypted or needs a key, stop and ask.
- Never read, dump or analyse the native binaries: the `TransportFever3` executable, `model_editor/ModelEditor`, `extra/` and the bundled `.so` libraries. No `strings`, hex dumps, disassemblers, debuggers, or greps that scan them (use `grep -I` in the install). `.claude/hooks/tf3-install-guard.py` blocks the common forms and `music.zip`. It is best effort and cannot check the publishing conditions, so the rules stand without it.

## Testing in the game

- The user's own saves (tests, re-saves) are in the game's `local/save/` folder under Steam userdata for app id 3493540, next to `settings.lua`. The full path on this machine, and how to find it again, are in the gitignored `local/README.md`; never write it, or the Steam id in it, into a committed file. Read these saves, never write them.
- Tests are saves the user makes in the game, one change per save, named by what changed. Compare a save with the one it was loaded from, not with the New Game screen: the Load Game screen rewrites settings and mods in the next save.
- To find what an unnamed field holds, ask for a save made with a distinctive typed value and search the decompressed stream for it. The map seed sat in an undescribed header field (`id`) until a typed seed was searched for; searching for the word "seed" found only construction records.
- Hash a save (sha256) before it is loaded again, so a later re-hash shows whether a load changed it.
- The user's screenshots come in clusters of one subject. Before reading a picture, look the topic or time up with `tools/screenshot_index.py` (`find` searches the text read off the pictures; the index and the OCR cache live in the gitignored `local/screenshots/`). When new unlabelled clusters appear, ask the user for a one-line note per cluster (what they were testing): a note, the OCR text and the saves written around the cluster usually label it, and reading pictures costs far more context (a first pass over 371 shots cost about 200,000 tokens). Zoom a crop to read a number, never a thumbnail. The workflow is in `.claude/skills/screenshot-index/SKILL.md`.

## Test maps and reference maps

- A **test map** is a game the user loads in the game and re-saves, one change per save. A **reference map** is a save we only read, or run scripts against, to check an idea: mostly mod.io catalog saves, never loaded or re-saved. A reference map becomes a test map when the user starts re-saving it.
- A game is identified by its map seed plus climate (header `map_seed` and the `climate` resource), not by the save-name prefix: series letters repeat across games, and one seed can be played in two climates.
- The gitignored `local/games/` holds one folder per test map, `<seed>-<climate>-<label>/part-N.md`. Reference maps get no folder; they live in `local/saves.txt`, `local/mined/` and `local/recheck/`. Both are indexed in `local/README.md`; `local/games_by_seed.py` lists saves by seed.
- Before asking the user for a new test save, or when a claim rests on one save, search `local/mined/index.csv` and the summaries for a catalog save that already shows it (recipes: `local/README.md`, "Finding things in `mined/`"). A hit is a reference map: cite it by mod id.
- Facts from either kind go to `docs/` as format facts. Cite a reference map by mod id (see the catalog rule above).

## Conventions

- Integers are little-endian unless stated. Use the notation `str` (u32 length + bytes) and `vec<T>` (u32 count + items), matching `FORMAT.md`, so readers can move between the two.
- Hex dumps: lowercase, space-separated bytes, short enough to show the point.
- Put numbers that change (counts of saves, versions seen) in dated notes such as `docs/versions.md`, not in this file or the README.
