# Format notes

Unofficial notes on Transport Fever 3 `.sav` files, worked out from the outside: reading saves, testing changes in the game, and looking at the game's moddable data files. Each note says which format versions it was checked on.

| File | Covers |
|---|---|
| [container.md](container.md) | zstd framing, writing a save back |
| [header.md](header.md) | Header fields in order, preview image, settings |
| [settings.md](settings.md) | The game settings: how they are stored, option lists and defaults, the difficulty presets, changing them on load |
| [calendar.md](calendar.md) | Game clock, calendar speed, the day table that turns clock values into dates, the date in the header |
| [lua-values.md](lua-values.md) | How Lua values are encoded (settings, script states) |
| [script-states.md](script-states.md) | Script states: weather and time of day, company rank, loans, counters, achievements, subsidies |
| [landmarks.md](landmarks.md) | Landmark (wonder) construction: delivered amounts per cargo, town modifiers |
| [warehouses.md](warehouses.md) | Warehouse construction records: modules, cargo per module, running cost |
| [statistics-lists.md](statistics-lists.md) | The `items*` statistics lists: warehouse stock as unloaded minus loaded, yearly bars from the running totals |
| [entity-stats.md](entity-stats.md) | Searches for stocks and yearly figures as plain numbers that failed, with what was tried |
| [town-states.md](town-states.md) | The town script's `townStates` table: ratings and penalties |
| [town-records.md](town-records.md) | The 78-byte town record: capacities, starting cargo |
| [entity-names.md](entity-names.md) | The table of entity names: layout, how to find it, default name patterns |
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
