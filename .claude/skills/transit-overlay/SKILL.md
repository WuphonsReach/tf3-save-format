---
name: transit-overlay
description: Decide when to ask the user to load a save with the Transit Overlay mod enabled and press its Export button, and how to read the result. The mod runs inside the game and prints ids, names, routes and catchments into the game's log, which the save alone does not give. Use when a question needs a line, stop group, town, building, industry, cargo or vehicle-route id tied to a name or position, or when a console command would otherwise be needed.
---

# Transit Overlay export: ask for it when the save cannot name the thing

The mod (mod.io 6449851, GitHub `axelferb/Transport-Fever-3---Transit-Overlay`, MIT) adds a **Transit Overlay** button at the top left of the game screen, next to the Layers button. A click prints the player's network as `TFO|` lines into the game's log. It runs in the game, so it reads through the game's own mod API. For most of what it covers that is easier and safer than the game console (typing a command, pasting its text, no way to test a query against a running game from here). It only reads: nothing in the save changes. Record codes and what is checked against a save: [docs/transit-overlay.md](../../../docs/transit-overlay.md). Rules in `CLAUDE.md` apply.

## When it is worth asking

Ask when the question is "which id is this" or "what is this id" and the stream has the id but not the name, or the position, or the link.

| Need | Record | Why the save is not enough |
|---|---|---|
| A line's id with its name | `L` (and `R`) | The line record does not hold its own id; only its vehicles do ([docs/line-ids.md](../../../docs/line-ids.md)) |
| Which vehicles run on which line, and the route's edge ids | `R` | One record per vehicle: line id then the movement path |
| Stop group id, name, centre, catchment radius, the buildings in reach | `G`, `C`, `K` | The stream has the group id once or twice, with no name or radius beside it |
| A town's id and name; building ids with position, capacity, town | `T`, `B` | Cross-checks the names table order and the building `town` field |
| An industry's id, position, level, name and stock; a town building's stock | `I`, `S` | Ties a stock record to a place |
| Cargo index to name, as this game has it | `N` | Ids are list positions, shifted by cargo mods: ask for it in any modded cargo game |
| What a town wants and has had delivered | `D` | The three numbers per cargo are Open; a known-input test fixes them |
| Edge ids with both node ids, ends and tangents | `E` | Compare against `street_edges.py` (are `R` ids the edge table's ids is Open) |
| Terrain heights and water level | `W`, `H` | A cross-check of the terrain tools, 2x height rounded |

Good fits: a known-input test with one change per save (add a stop, then a line, then a vehicle) where each step's ids matter; a line or stop whose name the user mentioned and we cannot find; a catchment, coverage or "which buildings does this stop serve" question; a cargo-id question in a modded game.

## When not to ask

- The save already answers it. Read it first (names table, `street_edges.py`, `model_instances.py`); the export costs the user a game load.
- The question is about a **stored** value the overlay does not print (vehicle speed, condition, income, signal state). The overlay lists the network, not the vehicles' state.
- The save is a catalog save (mod.io): we never load those, and the user cannot export from them without loading.
- The export must match a save: it describes the **running game at the click**, not a file. If the user will keep playing, ask for a manual save made right at the export (build from a manual save, not an autosave: autosaves get pruned).

## What to ask the user for

1. Enable **Transit Overlay** for the game (it is stored in the save's mod list, so a save made with it on carries it; loading from the Load Game screen rewrites mods in the next save, see `CLAUDE.md` Testing in the game).
2. Load the game (or play to the state to be checked), **save by hand**, then press **Export**. Pause is not required, but nothing should change between the save and the click.
3. **Copy the log's folder at once** and tell us the copy's name. The game rewrites `crash_dump/` when it starts, so a later session loses the lines. Best practice we use:
   - Copy the whole `crash_dump/` folder (without the `.dmp` files) to `local/games/<game>/gamelog-<hhmm of the save>/`. The `stdout.txt` in that copy is the static file to read; never read the live one, which the game may still be writing.
   - One export per copy. When there are several steps, copy after each click and name each copy for its save, so the series can be matched (`gamelog-0930` held one export taken with four buses on the line).
   - The log's path on this machine is in `local/README.md`; never write it, or the Steam id in it, into a committed file.
4. A short note of what was on screen or done (which line was selected, what was built last) helps; the export has no time stamp of its own.

If the export does not show: the button prints one `TFO|BEGIN` ... `TFO|END|<n>` block, and a failed section prints `TFO|ERR|<section>|<message>`. No `BEGIN` in the copy means the click came before the copy or the log was rewritten.

## Reading the copy

- Work on the copy. Filter by record code: `grep -a '^TFO|L|' stdout.txt`. The terrain rows (`H`) are most of the lines (341 of 477 in the first export); leave them out when printing: `grep -a '^TFO|' stdout.txt | grep -av '^TFO|H|'`.
- Fields are `|` separated; names have their separators replaced by spaces. Long lists are chunked (400 ids, 150 buildings, 120 edges per line): join chunks of one group before counting.
- **Mask what the log carries.** Names in the export are the player's own text (line, stop and town names from the user's own published saves may go in notes; account-derived and company names stay masked). A mod's Lua error in the rest of the log can hold a full install path with the OS account name: do not copy it into a note, commit or tool output (CLAUDE.md, saves carry other people's details). Write `<path>/mod.io/10640/mods/<id>/...`.
- Match the export to the **save made at the click** (a file, a stream). To tie an id to the stream: search the id as a `u32` and say how many hits it has and where (pattern, never a fixed offset); `docs/transit-overlay.md` shows the stride method that found a line id in each bus.
- Record what you learn in `docs/transit-overlay.md` (or the note the fact belongs to) with its version and a label: Observed for one export, Confirmed only after a known-input test. Cite the mod by id and URL, no export dumps in the repo, and name the script commit if a script made a number.
- A field the mod's source does not explain stays **Open**; give it a positional name, not a guess (the repo's neutral-naming rule for unknown fields).

## Limits

- Needs a game load by the user and the mod enabled; no way to run it from here.
- Manual refresh only: one export per click, no stream.
- The mod's page does not list field layouts; ours come from reading its exporter source plus one export. Recheck after a mod update.
- Checked on 604 only, one export, one Tiny subarctic bus-line game.
