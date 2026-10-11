# Gaps: what the notes do not know yet

One place to see what is still **Open**, grouped by theme, with the test or reading that would settle each item. The facts stay in their home notes; an entry here only names the question, points to the note, and says what it needs.

## Files

| File | Covers |
|---|---|
| [owners-and-links.md](owners-and-links.md) | Which thing a record belongs to: statistics groups, lines and their stops and vehicles, vehicle names and entity ids, people and trip records, the entity-name table |
| [vehicles-and-costs.md](vehicles-and-costs.md) | A vehicle's stored state (speed, condition, parked-ship instance, income), running-cost bookings that do not fit, depot upkeep, vehicle prices |
| [cargo-and-warehouses.md](cargo-and-warehouses.md) | Spoilage storage, lists that do not reconcile, stop and edge counters, warehouse modules and their claiming rule, cargo id order and cargo mods |
| [towns-and-buildings.md](towns-and-buildings.md) | Town record floats and columns, town building fields and boundary, stock records, landmarks, roads and a building's position |
| [economy-and-events.md](economy-and-events.md) | Subsidies, industry spawning and closing, notification decoding, company offers and ranks, Finances columns, inflation, the balloon and the UFO |
| [header-settings-and-map.md](header-settings-and-map.md) | Header fields, settings in play, the seed and what rebuilds from it, terrain and heightmap, calendar and clock, mods, script states, animals, platform |
| [tools-and-analysis.md](tools-and-analysis.md) | Steps that still need a private script, tool defects, saves not yet compared |

## An entry

```
- **Short title** (versions) What is not known, in a sentence or two. Home: link. Needs: how to settle it.
```

- **Versions** are the format versions the question was seen on, as in the notes. Where an entry says "one game", the evidence is a single game.
- **Home** is the note that holds what is known and the **Open** line itself. If the fact moves, fix the link here.
- **Needs** is one or more of:
  - *existing saves*: can be settled by reading saves already at hand (catalog saves, earlier test saves).
  - *new save*: needs a test save the user makes, one change per save, named by what changed; hash the source save before it is loaded.
  - *game window*: needs a number read from a window in the game, usually a screenshot, to tie a stored value to what the player sees.
  - *game files*: the answer may be in the readable base content (see the root `CLAUDE.md` for what may be opened).
  - Where a test is suggested, it is a suggestion, not a plan the user agreed to.
- **Tried** names a method that failed, so nobody repeats it.

## Keeping it current

- Closing a gap: write the fact into its home note (with a label and version), then delete the entry here. Git history keeps the old text; there is no archive and no "done" list.
- A new **Open** in a note that has a test or a reading attached gets an entry here. A one-off remark in a note that nobody can act on stays in the note.
- Entries carry no counts or dates and no local details (see the root `CLAUDE.md`). Names of things in published catalog saves may be used; cite the save by mod id.
- Run `python3 -I tools/lint_docs.py` after editing.
