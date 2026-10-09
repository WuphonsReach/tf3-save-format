# Format notes

Unofficial notes on Transport Fever 3 `.sav` files, worked out from the outside: reading saves, testing changes in the game, and looking at the game's moddable data files. Each note says which format versions it was checked on.

| File | Covers |
|---|---|
| [container.md](container.md) | zstd framing, writing a save back |
| [header.md](header.md) | Header fields in order, preview image, settings |
| [lua-values.md](lua-values.md) | How Lua values are encoded (settings, script states) |
| [script-states.md](script-states.md) | Script states: game clock, weather and time, company rank, loans, counters, achievements, subsidies |
| [town-states.md](town-states.md) | The town script's `townStates` table: ratings and penalties |
| [town-records.md](town-records.md) | The 78-byte town record: capacities, starting cargo |
| [finances.md](finances.md) | The Finances tab against the money journal: periods, rows and booking categories |
| [cargo-ids.md](cargo-ids.md) | Cargo type ids, and how climates and economies pair |
| [editor-saves.md](editor-saves.md) | Map editor saves vs regular saves, converting one to the other |
| [versions.md](versions.md) | Format versions seen in the wild |

The money journal and the script-state container are documented in [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md). These notes do not repeat them.

## Notation

- Integers and floats are little-endian.
- `str` is a u32 byte length followed by the bytes (UTF-8 in practice).
- `vec<T>` is a u32 count followed by that many `T`.
- The stream has no offset tables or section sizes. Fields follow each other, so finding a structure deep in the stream means scanning for a pattern. Offsets move from save to save.

## Evidence labels

- **Confirmed**: changed or checked in the game and seen to have the stated effect.
- **Observed**: holds in every save checked, not tested in the game.
- **Open**: unknown or a guess.
