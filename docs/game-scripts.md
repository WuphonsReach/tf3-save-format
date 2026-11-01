# Game scripts in play

What a mod's game script can reach while the game runs: the rules it must follow, what it sees of a cargo unit and its pay, and how it books money. A game script's state is saved with the game ([script-states.md](script-states.md#mod-script-states-and-stored-errors)). Its event answers and bookings end up in the journal ([finances.md](finances.md)), so these limits bound what a mod can leave in a save. Everything here was learnt on 605 while the Best Before freshness mod was built, and the rebuilds, events, booking categories and proposal checks while the Depot Retrofits mod was built (its [findings.md](https://github.com/WuphonsReach/tf3-depot-retrofits/blob/7ca11e7aed5eb97a66715088c449f53d20d0940c/docs/design/findings.md#what-a-mod-can-and-cannot-change), tf3-depot-retrofits, at commit 7ca11e7). The written source is that mod's [findings.md](https://github.com/WuphonsReach/tf3-best-before-mod/blob/5f4b203e701cda7de243e0d16bdc8997e298dadc/docs/findings.md), with the limits listed in its [needs-game-support.md](https://github.com/WuphonsReach/tf3-best-before-mod/blob/5f4b203e701cda7de243e0d16bdc8997e298dadc/docs/future/needs-game-support.md) (tf3-best-before-mod, at commit 5f4b203).

## In short

- **Commands go out from `update`, not from `handleEvent` (Observed, 605).** A command sent inside an event handler trips an engine assertion, and a command with a result callback does not run. A script judges success from the state it can read afterwards ([Rules](#rules-for-a-game-script)).
- **A game script's memory is its `state` (Observed, 605).** Module-level Lua variables do not survive between calls. What a script keeps goes in its state table, which the save stores.
- **A script cannot see a unit's age in the pay function (Observed, 605).** The replaceable income function gets only the difficulty factor, the cargo's price factor and the distance. A script changes a unit's pay through the ticket price event instead ([finances.md](finances.md#the-ticket-price-event)).
- **A cargo unit is an entity with its own pickup time and legs (Observed, 605)** ([Cargo units](#cargo-units-as-a-script-sees-them)).
- **A script can rebuild a construction but not change a depot or a vehicle's maintenance link directly (Confirmed in the files, Observed, 605).** See [Commands a script can send](#commands-a-script-can-send).
- **Only the game's `ProposalViewer` judges a rebuild as the game does (Observed, 605).** The script check `makeProposalData` wants a `SimpleProposal`, and a stand-in for a rebuild built that way calls some buildings blocked that the game rebuilds. The viewer agreed with the game on every building tried ([Checking a proposal](#checking-a-proposal-from-a-window)).
- **The only real clock is `os.time`, in whole seconds (Observed, 605).** `os.clock` is processor time and runs several times too fast.
- **A journal booking goes to the one account it names (Observed, 605).** The player, each vehicle and each line keep their own account ([finances.md](finances.md#accounts-of-vehicles-and-lines)).
- **Open.** The game's own age for a unit is not exposed (only the spoiled flag is), so what `deliveryExtensionDuration` equals stays inferred ([spoilage.md](spoilage.md)). A script cannot see how a unit's pay is shared between the lines that carried it.

## Rules for a game script

- **No commands from `handleEvent`.** `sendCommand` called inside an event handler trips the engine assertion `!m_betweenChanges`. Send from the script's `update`.
- **No result callbacks from `update`.** `sendCommand` with a result callback raises "Callbacks are currently disallowed"; without one it works. Success can only be read from the state afterwards.
- **State lives in the script's `state`.** Module-level variables do not survive between calls, so counters and queues go in the game script's state table. State the handler writes is visible to `update`. The game runs a game script on its simulation thread and on worker threads, each with its own copy of the module: a module-level "loaded" flag fired about 14 times per load. The Depot Retrofits log showed its buy queue written from the simulation thread and everything else from about ten worker threads. Two of 144 quick buys landed without the record the script had written for them, which may be a write from one thread lost to another (not proven).
- **A vanished entity aborts the whole event.** `getComponent` on a vehicle sold while its cargo is still on the way raises "Invalid entity" (8 times in 15 minutes on a large save), and every unit of that event is lost to the script. Guard lookups with `api.engine.entityExists`, and read a leg's carrier from `PickupPoint.carrier`, not from the vehicle.
- **Clocks.** `os.clock` is the process's processor time summed over the game's threads, not real time: in a window script, a check meant for every 2 seconds ran 2 to 3 times a second, and a 30-second watch ended after about 5 seconds. `os.time` is real time in whole seconds, and the game API has no finer clock. A window tab's steps are frames, not time: at the fastest game speed 45 steps passed within one second. The game clock is the `GAME_TIME` component of the world entity (`api.engine.util.getWorld()`), field `gameTime` ([calendar.md](calendar.md#the-game-clock)).
- **Journal entries carry `time = -1`.** An entry sent with `api.cmd.makeJournalBookAssetCmd` must have its time set to -1. The entry has no text field, only its time, amount and category with its carrier.

How a mod's files and modules are found at load is in [mods.md](mods.md#loading-a-mods-files).

## Commands a script can send

- **Rebuild a construction.** `createProposalReplaceConstruction` and `makeWorldBuildProposalCmd` from `update` rebuild a construction with new params, free of charge, even while paused ([construction-scripts.md](construction-scripts.md#rebuilds)).
- **No command for a depot's pool or radius, or a vehicle's maintenance station** (`api/tealdef/api/cmd.d.tl`). Only a rebuild changes the first two ([depots.md](depots.md#which-building-maintains-a-vehicle)).
- **An event from the GUI.** A GUI script sends `api.cmd.makeScriptingSendEventCmd("", id, name, param)`; the game script receives it in `handleEvent` after `state:subscribeToEvent(name)`. The company window's rank claim goes this way (`game_mechanics/company/company.tl`, [company.md](company.md#company-and-rank)).
- **Read the rank.** `company_progression_util.getCompanyProgressionState(player)` works from a game script ([company.md](company.md#company-and-rank)).
- **Wind.** `api.cmd.makeWorldChangeWindCmd` exists, but no base script sends it ([emissions.md](emissions.md#wind)).
- **Emitters.** `makeEntitySetEmissionsCmd` sets an emitter's noise power, pollution power and radius in metres, and is not marked debug. `makeComponentExchangeCmd` swaps a component such as `EmissionEmitter` or `ModelInstanceList`, and `makeMaintenanceCostUpdateCmd` sets a maintenance cost; both are marked debug (`api/tealdef/api/cmd.d.tl`). None was tried. A value set this way lasts only until the building's next rebuild ([construction-scripts.md](construction-scripts.md#what-an-update-script-returns)).

## Checking a proposal from a window

What a window script can learn before it sends a rebuild. Observed on 605 in a re-save of catalog save [6417707](https://mod.io/g/transportfever3/m/333151) and in the Giga temperate game, five buildings checked both ways.

- **`makeProposalData` takes a `SimpleProposal`.** Its type definition says `Proposal` (`api/tealdef/api/engine/util.d.tl`). Handed the `Proposal` from `createProposalReplaceConstruction`, it raises `bad argument #2 to 'makeProposalData' (SimpleProposal expected, got Proposal)`. It returns a `ProposalData` with an `errorState` (`critical`, `messages`, `warnings`) and a `collisionInfo` with `collisionEntities`. The base GUI counts a proposal with no messages as buildable (`gui/entity_window/bridge_and_tunnel.tl`).
- **A stand-in rebuild is judged wrongly.** A rebuild as a `SimpleProposal` removes the construction and adds one with the same `fileName` and `transf` and the new params, as the base landmarks script levels up a landmark (`landmarks/landmarks.script.tl`). On that stand-in, `makeProposalData` called several buildings blocked that the game then rebuilt:
  - a road depot, colliding with its own entrance road;
  - two rail depots, with "Construction Not Possible" and nothing named;
  - a road depot, colliding with the road at its exit.

  It found the real obstacles too (a house on the next lot, a tall building).
- **`builtin.ProposalViewer` judges the real proposal.** Given the replace proposal, it reports its `ProposalData` through `onCreateProposalData`, as the base bridge and tunnel window uses it. It agreed with the game on every building tried. It must sit in the window's action area (`setActionFn`, inside a `builtin.ActionDescriptor`). Placed among a tab's own widgets, it stopped the game with `Assertion '!IsTransformWithContext(node.recipeId)'`.
- **What a viewer does in the world.** It previews the rebuilt building: the greenery around it regrows and its road connection flashes blue. It draws what is in the way in red, and often the building's own entrance as well, which is not in the way. It answers once, so it does not notice an obstacle being bulldozed. When a rebuild lands under a viewer that still holds the old proposal, the building flashes red ("Construction Not Possible").
- **A GUI command can take a result callback.** The bridge window sends its build command with a function that gets `success` and the result's proposal data. A game script cannot do this ([Rules](#rules-for-a-game-script)).
- **A window's tab is built anew each time it is shown.** A tab's step function runs only while the tab shows. Switching tabs or closing the window stops it, and showing the tab again starts it fresh. Opening a second building's window flipped a first, pinned window back to its first tab. A greyed button shows no tooltip.

## Cargo units as a script sees them

- **Each cargo unit is a `SimCargo` entity** with `startTime` (when it was made), `pickupTime`, a source entity, `deliveryExtensionDuration` and `pickupPoints`. The pickup points have one entry per vehicle and line the unit travelled on, each with its own carrier and its start position. `api.engine.util.cargo.isGoodQuality(unit)` tells whether it is spoiled. How the spoiled flag follows the age is in [spoilage.md](spoilage.md), and the limit, `api.engine.util.stock.getAdjustedDeliveryTime(cargoType)`, in [delivery-times.md](delivery-times.md).
- **A unit's age runs from its own `pickupTime`.** The age counted that way matches the game's spoiled flag ([Evidence](#evidence-and-tests)). So cargo waiting in an industry's stock has not started to age. Units are picked up one at a time, so on a train that waits for a full load the first units loaded are the first to pass the limit.
- **The income function sees no unit.** `baseConfig.economy.cargoIncomeScript` can be replaced by one mod at a time. The game calls it once per delivered unit, before the unit's arrival event, with only `difficultyFactor`, the price factor and the distance.
- **A cargo type's price function cannot be swapped at run time.** Its `scriptRef` can be read through `api.res.cargoTypeRep.get(id)`, but changing it there has no effect. The eleven cargo types seen all use `incomeFactors.constantFn` with initial price 4, final price 3.2, decay rate 0.01 and decay mod 0.1; only the decay start differs (100 for one cargo, 50 for the others).

## Bookings from a script

- `api.cmd.makeJournalBookAssetCmd` with an INCOME entry, sent from `update`, changes the named account by exactly the booked amount, negative or positive. Its first argument is the entity whose account takes the entry: the player, a vehicle or a line ([finances.md](finances.md#accounts-of-vehicles-and-lines)).
- For income and maintenance, the entry's carrier is the row it shows under in the Finances tab. A `CONSTRUCTION` / `DEPOT` entry lands in Investments, Infrastructure whatever its carrier, as that row has no carrier split ([finances.md](finances.md#rows-against-the-booking-categories)).
- The categories are in `scripts/journal.d.tl` (base tealdef): for example type `CONSTRUCTION` with subcategory `DEPOT`, and type `MAINTENANCE` with `INFRASTRUCTURE`. The base marketing tool charges for a campaign with the same command (`gui/construction/tools/marketing_campaign_tool.script.tl`). Two test charges to the player, $12,345 as depot construction and $23,456 as infrastructure maintenance, lowered the balance by exactly $35,801. The first showed in the Finances tab's construction rows; where the second shows was not found (Observed, 605). Later, 73 depot construction entries on seven buildings (carriers WATER, RAIL and TRAM) moved Investments, Infrastructure and the account by exactly their sum, while no carrier row moved ([finances.md](finances.md#rows-against-the-booking-categories)).
- A vehicle's logbook and a line's hold counters (items transported and the like), not money, so a mod cannot show a booking there.

## Evidence and tests

All on 605, in the Best Before mod's test saves (its findings.md, "Test saves"; the Giga temperate game is [in test-games.md](test-games.md#giga-temperate-game-wr26a)), from the game's log and the mod's own log lines.

- **Bookings.** On the small save at 4x, 104 units: every tracked vehicle, line and player account moved by pay minus running costs minus the bookings, within 3%. A later run booked 42 bonuses and 60 deductions to the player, and 97 of the 102 entries showed as an exact step of the balance.
- **Logbooks.** Listed in the mod's [discarded.md](https://github.com/WuphonsReach/tf3-best-before-mod/blob/5f4b203e701cda7de243e0d16bdc8997e298dadc/docs/future/discarded.md) (tf3-best-before-mod, at commit 5f4b203).
- **Age from pickup.** On WR26A, a grain train's 64 units arrived with ages spread over about a minute (1,711,800 to 1,770,200 ms), the same in two runs of the same trip. The mod's age (now minus `pickupTime`, less `deliveryExtensionDuration`) agreed with the game's flag on all but 7 of 69,907 units ([spoilage.md](spoilage.md)).
