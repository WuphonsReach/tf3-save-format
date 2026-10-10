# Format notes

Unofficial notes on Transport Fever 3 `.sav` files, worked out from the outside: reading saves, testing changes in the game, and looking at the game's moddable data files. Each note says which format versions it was checked on.

| File | Covers |
|---|---|
| [container.md](container.md) | zstd framing, writing a save back |
| [header.md](header.md) | Header fields in order, preview image, settings |
| [tf3-save-editor.md](tf3-save-editor.md) | Where these notes read a field differently from tf3-save-editor's FORMAT.md or its reader, and why |
| [mods.md](mods.md) | What a save records about a mod: the mod list entry, options, switching mods on and off when loading, script states |
| [seed.md](seed.md) | The map seed: the `id` field, the catalog's seeds, the seed in the game's log |
| [settings.md](settings.md) | The game settings: how they are stored, option lists and defaults, the difficulty presets, changing them on load |
| [climates-economies.md](climates-economies.md) | The climate and economy resources and how they pair, what each economy leaves out |
| [versions.md](versions.md) | Format versions seen in the wild, with dated counts |
| [platform.md](platform.md) | Whether a save says which platform made it |
| [calendar.md](calendar.md) | Game clock (and its rate against real time at each play speed), calendar speed, what the autosave interval counts, the day table that turns clock values into dates, the date in the header |
| [lua-values.md](lua-values.md) | How Lua values are encoded (settings, script states) |
| [script-states.md](script-states.md) | Script states: how to find one, the list of states seen, weather and time of day, achievements, mod states and the error messages they can hold |
| [company.md](company.md) | Company experience, the rank earned and claimed, rank thresholds, loans |
| [inflation.md](inflation.md) | The Inflation option's income cut and the year cost table |
| [notifications.md](notifications.md) | The notification entries, their types, the industry-spawn, industry-closing (deadline field on the industry) and stuck-vehicle entries |
| [subsidies.md](subsidies.md) | Subsidy offers, active and completed subsidies |
| [town-states.md](town-states.md) | The town script's `townStates` table: ratings and penalties |
| [landmarks.md](landmarks.md) | Landmark (wonder) construction: delivered amounts per cargo, town modifiers |
| [fun-elements.md](fun-elements.md) | The Deluxe Upgrade hot air balloon: script state, sighting notification, position and model instance; the UFO timer |
| [finances.md](finances.md) | The Finances tab against the money journal: periods, rows and booking categories; the balance history |
| [cargo-ids.md](cargo-ids.md) | Cargo type ids, tiers and weights, starting cargo |
| [town-records.md](town-records.md) | The 78-byte town record: capacities, starting cargo, the town building component and its Historic Preservation flag |
| [warehouses.md](warehouses.md) | Warehouse construction records: modules, cargo per module, running cost |
| [statistics-lists.md](statistics-lists.md) | The `items*` statistics lists: warehouse stock as unloaded minus loaded, yearly bars from the running totals, industry production lists, spoiled cargo and the `itemsLost` list |
| [entity-stats.md](entity-stats.md) | Searches for stocks and yearly figures as plain numbers that failed, with what was tried |
| [entity-names.md](entity-names.md) | The table of entity names: layout, how to find it, default name patterns |
| [lines.md](lines.md) | Line stops' configuration record: force unload, stop times; what a new line adds, the passenger records (line, origin and destination stop, vehicle), the stop names in vehicle windows |
| [models.md](models.md) | The model table and the model instance records, vehicles, people and animals in one run, matching road vehicles to instance slots by depot and maintenance-station positions |
| [terrain.md](terrain.md) | What the map seed and the terrain sliders do to the data after the header: same-seed and changed-slider comparisons, simulation state, the terrain record and the heightmap, generators |
| [animals.md](animals.md) | The animals list, which animals they are, how many there are |
| [editor-saves.md](editor-saves.md) | Map editor saves vs regular saves, converting one to the other |
| [developer/vscode-schema.md](developer/vscode-schema.md) | Clearing VS Code's "untrusted schema" warning on the summaries' `$schema` line |

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
