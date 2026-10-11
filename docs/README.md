# Format notes

Unofficial notes on Transport Fever 3 `.sav` files, worked out from the outside: reading saves, testing changes in the game, and looking at the game's moddable data files. Each note says which format versions it was checked on.

| File | Covers |
|---|---|
| [container.md](container.md) | zstd framing, writing a save back |
| [header.md](header.md) | Header fields in order, preview image (and a crash save's empty one), the vehicle, ship, station and line counts the load dialog shows, settings |
| [tf3-save-editor.md](tf3-save-editor.md) | Where these notes read a field differently from tf3-save-editor's FORMAT.md or its reader, and why |
| [mods.md](mods.md) | What a save records about a mod: the mod list entry, options, switching mods on and off when loading, script states |
| [seed.md](seed.md) | The map seed: the `id` field, the catalog's seeds, the seed in the game's log |
| [settings.md](settings.md) | The game settings: how they are stored, option lists and defaults, the difficulty presets, changing them on load |
| [climates-economies.md](climates-economies.md) | The climate and economy resources and how they pair, what each economy leaves out |
| [industry-chains.md](industry-chains.md) | Base-game recipes (what each industry takes and gives), boosters, which climates have which industry, the rank-to-industry table, each cargo's transport class, and why mods can change all of it |
| [glossary.md](glossary.md) | The game's internal names against labels and what players call things: cargo, industries, stops, stations, ports, depots, warehouses and vehicles, with the aliases players use for each and the loose words that could be two keys |
| [versions.md](versions.md) | Format versions seen in the wild, with dated counts |
| [platform.md](platform.md) | Whether a save says which platform made it |
| [calendar.md](calendar.md) | Game clock (and its rate against real time at each play speed), the calendar speed field and its values, what the autosave interval counts, the day table that turns clock values into dates, the date in the header |
| [calendar-speed.md](calendar-speed.md) | The calendar speed in play: one save holds the setting at save time, not a history; Paused; a calendar started again after a long stop; a speed change while running and how to place it; the speed and date in the game's windows |
| [lua-values.md](lua-values.md) | How Lua values are encoded (settings, script states) |
| [lua-overview.md](lua-overview.md) | Where Lua sits in the stream, layers and depth of the 28 script states in a 604 game, the markers in the binary middle (named strings, counts, embedded Lua tables) across 568 to 604, what the file labels and what it does not, what the game's script files say about the states (declarations, state types, the `version` key) |
| [script-states.md](script-states.md) | Script states: how to find one, the list of states seen, weather and time of day, achievements, mod states and the error messages they can hold |
| [company.md](company.md) | Company experience, the rank earned and claimed, rank thresholds, loans |
| [inflation.md](inflation.md) | The Inflation option's income cut and the year cost table |
| [notifications.md](notifications.md) | The notifications state: the limit on entries, `history`, entry layout and flags, `ignored.types` (the game's defaults) and `tracked`, params of each type seen, persistent warnings and the bookkeeping tables (`wastedVehicles`, `vehicle2problem` and others), subsidy `uid`, the availability state's `lastYear` |
| [notifications-in-play.md](notifications-in-play.md) | Notification entries seen in play (604): the "New Vehicles Available" popups and the model years behind them, what dismissing changes, the industry-spawn, industry-closing and stuck-vehicle entries |
| [subsidies.md](subsidies.md) | Subsidy offers, active and completed subsidies |
| [town-states.md](town-states.md) | The town script's `townStates` table: ratings and penalties, a new game's three towns against their windows, the window's Reputation as `eventFactors.score`, the demolish penalty and its recovery by game clock |
| [landmarks.md](landmarks.md) | Landmark (wonder) construction: delivered amounts per cargo, town modifiers |
| [fun-elements.md](fun-elements.md) | The Deluxe Upgrade hot air balloon: script state, sighting notification, position and model instance; the UFO timer |
| [finances.md](finances.md) | The Finances tab against the money journal: periods, rows and booking categories, old bookings merged by month and later by year, a new game's first bookings, loan payments, income per carrier, vehicle purchase and sale bookings (booked price below the buy window's, sale price per model); the balance history |
| [running-costs.md](running-costs.md) | How upkeep and vehicle running costs are booked: batches every 60,000 clock units, yearly figures from them, a depot's base and accumulated upkeep, a cargo station's upkeep as platform modules plus an entrance (universal against specialized terminals), maintenance buildings booked as Road and Tram halves, a parked ship's 5% rate, cost steps by condition |
| [cargo-ids.md](cargo-ids.md) | Cargo type ids: the save's own cargo list (id = position, cargo mods shift the ids), the base-game id table, tiers and weights, starting cargo, the town levels at which the game adds a cargo slot and how it picks the cargo |
| [town-records.md](town-records.md) | The 78-byte town record: capacities, starting cargo, how to find the records, the floats that follow population, a town gaining a cargo, the Towns tab's population, car and demand columns against the record |
| [town-buildings.md](town-buildings.md) | The town building record: level, parcels, height, build time, owning town and the Historic Preservation flag; finding and listing the records, what a tick changes, buildings replaced or changing level in play, the town boundary |
| [building-stocks.md](building-stocks.md) | The stock records of town buildings: the pattern that finds them, cargo id and capacity inside, a constant block between them, a record patch that leaves existing buildings on their old cargo, one town changed in the Editor tab compared stream to stream |
| [warehouses.md](warehouses.md) | Warehouse construction records: modules, cargo per module, running cost |
| [statistics-lists.md](statistics-lists.md) | The `items*` statistics lists: field and group layout, warehouse stock as unloaded minus loaded, yearly bars as 1,461,000-unit periods, how entries are added, the first fish line read window by window |
| [fish-chain.md](fish-chain.md) | The fish chain read with the statistics lists: window by window (port, warehouse, truck line), reading a list's total at an earlier clock, the `itemsAtEdge` totals that show a queue, per-stop arrival lists on a two-stop line, the warehouse running empty, the port's surplus going to town buildings through destination keys |
| [cement-chain.md](cement-chain.md) | The cement chain read with the statistics lists: quarry, plant, warehouse and town groups, a line carrying two cargos, in-transit cargo against the Lines window's Load, bunched vehicles, edge totals that place vehicles along a route, keyed groups as consumer buildings' tallies, both lines' vehicles replaced, timing a vehicle's loop from an arrival list, cargo gone with sold vehicles, jams on a shared road, two convoys on one line, a jam's bunch spreading out over several loops, consumer buildings added and building lists that lose cargo between saves |
| [industries.md](industries.md) | What a save keeps about an industry: the `industries.gs` state, the output stock as start plus produced less destroyed and loaded, destroyed cargo at a full stock, industries created in play at half-year boundaries, the closing deadline record |
| [spoilage.md](spoilage.md) | Spoiled cargo: the windows' spoiled counters, `itemsLost` (and a lead that it counts fish dropped for age), the "unsatisfied" lists at stops and edges, a warehouse keeping spoiled fish |
| [delivery-times.md](delivery-times.md) | Expected delivery time per cargo: the Delivery Time tab's tooltips equal the cargo files' `timeToDeliverInSeconds` times 1.5, bars clipped at the axis top, cargo told by icon |
| [entity-stats.md](entity-stats.md) | Searches for stocks and yearly figures as plain numbers that failed, with what was tried |
| [entity-names.md](entity-names.md) | The table of entity names: layout, how to find it, default name patterns, how town names are read from it (the run after the company), what a rename of an industry, line, stop or person does, households in consecutive slots |
| [lines.md](lines.md) | Line stops' configuration record: force unload, stop times; what a new line adds, the trip-plan records (a line with two stops and a vehicle, or a building), the stop names in vehicle windows, the Lines window's Frequency, Rate and Load columns |
| [line-ids.md](line-ids.md) | A line's entity id and name (the `line_warning` entry), its vehicles while they carry cargo (cargo-unit records of line id and vehicle id), why name slots do not give the link, and the per-cargo byte vector at the end of a stop record that holds the cargo the stop loads |
| [models.md](models.md) | The model table (ids by position, mods' models after the base game's) and the model instance record; vehicles, people and animals in one run |
| [vehicles.md](vehicles.md) | A vehicle's model instance: finding it, slot order and vehicle numbers, positions and headings, depots and lines and when a vehicle has an instance, matching road vehicles to slots by depot and maintenance-station positions, purchases and sales; pointers to a vehicle's name, count, bookings and warnings |
| [terrain.md](terrain.md) | What the map seed and the terrain sliders do to the data after the header: same-seed and changed-slider comparisons, simulation state, the terrain record and the heightmap, generators |
| [animals.md](animals.md) | The animals list, which animals they are, how many there are |
| [editor-saves.md](editor-saves.md) | Map editor saves vs regular saves, converting one to the other |
| [editor-map-buildings.md](editor-map-buildings.md) | Historic Preservation ticks made in the map editor (one flag byte each, nothing else in the record), where a ticked house stood from its lot polygon, why the building record's `town` value is probably not a town id, a tick counter that resets on load |
| [road-network.md](road-network.md) | The street-edge table (a record per road edge: end node ids, positions, street type; how to find and read it), what deleting a road, splitting one and building one did to it, the junction table, the road-surface strips, the ground polygons and the free-id list, and how to place a road with a landmark |
| [street-templates.md](street-templates.md) | Vehicle lane counts of the street and track types, read from the game's templates (small 2, medium 4, large 6, highways 1 to 3, tracks 1), why a save's edge record does not need them, mods' types |
| [test-games.md](test-games.md) | Our own test games, each described once: seed, climate, map size, mods, save names and the notes that use it; the catalog games we re-saved |
| [analysis-examples/CLAUDE.md](analysis-examples/CLAUDE.md) | Working rules for the analysis-examples folder: its goal, the file-name pattern with the mod.io id suffix, what each example holds, the support table |
| [analysis-examples/clothes-train2-supply-chain-starvation-6425796.md](analysis-examples/clothes-train2-supply-chain-starvation-6425796.md) | Worked examples that test whether the notes and tools can support a player-style analysis, with a table of what is supported and what is a gap. First: "where is the bottleneck on this line?" from the statistics lists (per-period differences to the save's clock, last-entry times, matching a line by its loads, a backlog that turned into lost cargo) |
| [gaps/README.md](gaps/README.md) | How the gaps index works: the entry format, what "Needs" can say (existing saves, new save, game window, game files), and how to close an entry |
| [gaps/owners-and-links.md](gaps/owners-and-links.md) | Open questions of the form "which record belongs to what": statistics-group owners, a line's stops and vehicles, a vehicle's line, a stop record's fields, people and trip records, entity ids against name slots |
| [gaps/vehicles-and-costs.md](gaps/vehicles-and-costs.md) | Open questions on a vehicle's stored speed, condition, income and parked-ship instance; running-cost bookings that do not fit, depot upkeep, the inflation multiplier on depots, vehicle prices |
| [gaps/cargo-and-warehouses.md](gaps/cargo-and-warehouses.md) | Open questions on spoilage storage and `itemsLost`, chains whose lists do not reconcile, warehouse module cargo and the claiming rule, cargo id order and cargo mods, recipe details |
| [gaps/towns-and-buildings.md](gaps/towns-and-buildings.md) | Open questions on town record floats, the Towns tab columns, town building fields and the boundary, stock records, landmarks, the road tables and a building's position |
| [gaps/economy-and-events.md](gaps/economy-and-events.md) | Open questions on subsidies, industry spawning and closing, notification decoding, company offers and ranks, Finances columns, inflation, the balloon and the UFO |
| [gaps/header-settings-and-map.md](gaps/header-settings-and-map.md) | Open questions on the seed and what rebuilds from it, terrain and heightmap, settings in play, calendar and clock, mods, script states, animals, platform |
| [gaps/tools-and-analysis.md](gaps/tools-and-analysis.md) | Steps that still need a private script, tool defects (cargo ids in mod games), saves not yet compared |
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
