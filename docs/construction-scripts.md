# Construction scripts and rebuilds

How a construction (a depot, station, industry or warehouse) gets its values from its update script, what of that the save keeps, and what a rebuild does. Depots were the test case. The construction record in the stream (the `.con` path, then a Lua table of params) is described for warehouses in [warehouses.md](warehouses.md#the-construction-record). Checked on 605, while the Depot Retrofits mod was built. Its written source is the mod's [findings.md](https://github.com/WuphonsReach/tf3-depot-retrofits/blob/4d35bf96b195c42aed55bc8fd15d0ade44139499/docs/design/findings.md) (tf3-depot-retrofits, at commit 4d35bf9).

## In short

- **The update script runs at build and rebuild, not at load (Observed, 605).** A depot's pool, radius, emission states and upkeep come from its construction's update script. After save, quit and reload, rebuilt buildings kept their values, and a wrapper round the script logged no call. So the values are stored with the construction, and a change to a script reaches a building only at its next rebuild.
- **The params table is stored in the construction record (Confirmed, 605, one save).** In a save where the mod had levelled 36 depots and maintenance buildings, each of their `depots/...con` records held the mod's five level params next to `modules`, `seed`, `upgrade` and `year`. Params count from 1, like mod options ([mods.md](mods.md#mod-options)).
- **A param can be stored without being in the build menu (Observed, 605).** A param declared with `yearFrom` 9999, or not declared at all, does not show in the menu and is not passed when the building is placed. A rebuild stores it all the same.
- **A rebuild keeps the ids (Observed, 605).** Rebuilding with new params keeps the construction and depot entity ids and the vehicles' lines, and costs nothing. It clears every maintained vehicle's maintenance link ([depots.md](depots.md#which-building-maintains-a-vehicle)). The game's own upgrade tools (electrifying, catenary) rebuild the same way and keep the other params.
- **Modules add their own part (Confirmed in the files, Observed, 605).** A module's update script runs after the construction's, and its `metadata.maintenanceCost` and `metadata.price` are added to the building's.
- **Open.**
  - Where the stored pool, radius, emission states and upkeep sit in the stream. The embedded tables with `emissionConfig`, `maintenanceCost` and `price` keys ([lua-overview.md](lua-overview.md)) are a lead, but the levelled save held no `maintenancePool` or `emissionConfig` string.
  - Whether a module script is handed the same table the construction script returned.

## What an update script returns

- **The depot values.** Subconstructions carry the depot values. Each has a `depot` table (`maintenancePool`, `catchmentArea.radius`) and `metadata.emissions` (two states, [emissions.md](emissions.md#emitters-and-their-states)). The result's `cost` and `maintenanceCost` are the build price and yearly upkeep.
- **The engine side.** The depot entity is a subconstruction with a `VEHICLE_DEPOT` component ([depots.md](depots.md#the-depot-entity)). The construction's `MAINTENANCE_COST` component holds the script's `maintenanceCost`.
- **The script file.** A `.con` names its update script relative to its own folder (`"rail_depot.script@updateFn"`), and `scripts/util.tl` `useFn` loads an absolute `file@function` reference. A construction script can be Teal: the heliport's module script is `stations/air/heliport/modules.script.tl`.
- **No command changes the values later.** `api/tealdef/api/cmd.d.tl` has no command that changes a depot's pool or radius, or a vehicle's maintenance station. The only maintenance command sets a maintenance cost and is marked debug. So a rebuild is the only way to change them.

## Params

- **Params count from 1.** The rail depot's catenary param has `defaultIndex = 2` for "Yes", and `rail/rail_depot.script.lua` tests `params.catenary == 2` (`scripts/construction/param_util.tl` in `scripts.zip`).
- **The keys seen.** A rebuilt depot's params read back as `modules`, `seed`, `year` and `upgrade`, plus any extra params. A placed depot also has `constructOpt56` and `constructOpt78`, as warehouses do.
- **Params outside the build menu.** A param's `yearFrom` hides it from the build menu until that year. Declared with 3000 or 9999, or not declared at all, a param is not passed when a building is placed, yet a rebuild stores it and passes it to the update script. A building placed by hand starts without it. A declared param with a single value still shows in the menu. The date card goes up to the year 5000, so 3000 can be reached.
- **Changing a param after building.** `ConstructionScriptParam` has a `postConstructionModifiable` field (`api/tealdef/api/type.d.tl`). None of the base depot or maintenance `.con` files sets it, so the build window cannot change their params after building.

## Modules

- **When a module's script runs.** The game runs a module's update script once per built module, after the construction's (`ModuleDesc.updateScript` in `type.d.tl`). It passes the capture params, the result, the transform, the tag, the slot id, `addModel` and the construction's params (`stations/street/modular_street_station/modules.script.lua`).
- **What a module adds.** A module's upkeep and price are its `metadata.maintenanceCost` and `metadata.price`, and the game adds them to the building's; no module script adds them. The construction's own script sees every built module's metadata in `params.modules` (`modular_terminal.script.lua` reads it). [warehouses.md](warehouses.md#cost) and [running-costs.md](running-costs.md) show the same sums for warehouses and cargo stations.
- **A modular mod depot.** In the Roundhouse mod's depot, the construction script makes a base with pool 1 and $60,000 upkeep. Each stall, and each segment without a stall, adds 1 to the pool in its module script and $100 upkeep through its metadata. The chimney adds $50 and no vehicle. With 28 stalls the pool was 29 and the upkeep $62,850 (Observed, 605).

## Rebuilds

- **From a game script.** `api.engine.util.proposal.createProposalReplaceConstruction(entity, params)` builds a proposal that replaces a construction with new params (`api/tealdef/api/engine/util.d.tl`). A game script sends it with `api.cmd.makeWorldBuildProposalCmd(proposal, nil, false, false, false)` from `update`, without a callback ([game-scripts.md](game-scripts.md#rules-for-a-game-script)). It lands at once, even while the game is paused.
- **What a rebuild keeps and clears.**
  - It keeps the construction and depot entity ids and the vehicles' lines, and nothing is charged.
  - It sets the accumulated part of the building's upkeep back to 0 ([running-costs.md](running-costs.md#a-road-depots-upkeep-against-its-window-604)).
  - It clears the maintenance link of every vehicle the building kept, even when nothing changes.
- **Rebuilds the game starts.** Electrifying a rail depot, converting a tram depot's track to catenary, a track edit at a tram depot's entrance, and adding or removing modules all run the construction's update script again. The game's upgrade script changes only its own keys (`catenary` and `streetTemplate` in `depots/rail/rail_depot.script.lua`, `tramCatenary` in `depots/road/tram_depot/tram_depot.script.lua`) and returns every other param as it was. So params a mod added survive them. Electrifying a rail depot cost $618.

## Mod hooks

- **`loadConstruction`.** A mod's `runFn` can register `addModifier("loadConstruction", fn)` and change any construction definition as it loads. The base game does this itself (`base/base_mod.lua` in `base.zip`). The modifier is given names in the form `::/depots/road/road_depot/road_depot.con.lua`, and relative update-script references resolve against them.
- **`loadModule`.** `addModifier("loadModule", fn)` is called by TF3 with each module's file name and definition, as TF2 did. The base game registers none.
- **Several mods chain.** Each modifier gets the definition as the mod before it left it. Two mods both wrapping an update script work together if each calls the script it found. A mod that replaces the script outright drops the earlier wrapper. This was read from the code; no test with two such mods was made.
- **A whole window of its own.** A construction can name an `entityWindowScript` that returns a window with its own tabs. The base Cleaning Plant does (`game_mechanics/emission/pollution_cleanup_facility_hud.script.tl`); the base depots have none. A card can also be added to every maintenance building's window through a `react-plugin` resource on `MaintenanceStationEowExtensionPoint` (base cards: `maintenance_station_balance.res.lua` and others, ordered by `order`).
- **Telling a depot construction apart.**
  - Every base depot and maintenance `.con` names `configureDepotHudIconsFn` with a `depotType`. The base path signals (`infrastructure/signal/signal_path_a.con.lua`) name the same script, but they are edge objects.
  - The engine's `ConstructionType` has three depot values: `STREET_DEPOT`, `RAIL_DEPOT` and `WATER_DEPOT` (`type.d.tl`). The base depot files do not set it. The Roundhouse and Modern Railway Depot mods declare `RAIL_DEPOT`, and the Boathouse mod's maintenance building `WATER_DEPOT`.

## Evidence and tests

All on 605, in the mod's 1900 test save and the Giga temperate game ([test-games.md](test-games.md#giga-temperate-game-wr26a)). The probe tables are in the mod's findings.md under "Test results" (tf3-depot-retrofits, at commit 4d35bf9).

- **Stored params in the save (Confirmed).** Save `WR26A Giga-Tv3 1915` (740 MB decompressed) holds 36 of each `depotRetrofits*` key. Every one sits in a `depots/...con` record's params, after the path. The keys come in name order: the five level keys, then `modules`, `seed`, `upgrade`, `year`. The stream's other `depots/...con` strings have none.
- **Reload.** Three rebuilt buildings were saved, the game quit and the save reloaded. Pool, radius, upkeep, emitter power and params all came back, and the wrapper logged nothing at load.
- **A changed formula is not applied on load.** After the mod's upkeep step changed from 25% to 15%, seven buildings kept their old upkeep until each was bought up again. One tram depot's script upkeep of 168,000 gave exactly its 60,000 base under the old factor.
- **Rebuilds at scale.** 18 of 24 buildings in the 1900 save were rebuilt with levels 0 to 15 in five trees. Pool, radius, upkeep and stored levels matched the formulas at every check up to a game month, and the emitter power followed the scaled emission states.
- **Game-started rebuilds.** A track edit at a tram depot's entrance ran its update script 4 times and kept levels 0/0/0/0/3. A tram catenary conversion rebuilt it twice (420 m, upkeep unchanged). Rail depot electrification kept levels 2/1/1/1/5.
