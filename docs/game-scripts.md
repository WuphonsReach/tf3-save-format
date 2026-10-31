# Game scripts in play

What a mod's game script can reach while the game runs: the rules it must follow, what it sees of a cargo unit and its pay, and how it books money. A game script's state is saved with the game ([script-states.md](script-states.md#mod-script-states-and-stored-errors)). Its event answers and bookings end up in the journal ([finances.md](finances.md)), so these limits bound what a mod can leave in a save. Everything here was learnt on 605 while the Best Before freshness mod was built. The written source is that mod's [findings.md](https://github.com/WuphonsReach/tf3-best-before-mod/blob/5f4b203e701cda7de243e0d16bdc8997e298dadc/docs/findings.md), with the limits listed in its [needs-game-support.md](https://github.com/WuphonsReach/tf3-best-before-mod/blob/5f4b203e701cda7de243e0d16bdc8997e298dadc/docs/future/needs-game-support.md) (tf3-best-before-mod, at commit 5f4b203).

## In short

- **Commands go out from `update`, not from `handleEvent` (Observed, 605).** A command sent inside an event handler trips an engine assertion, and a command with a result callback does not run. A script judges success from the state it can read afterwards ([Rules](#rules-for-a-game-script)).
- **A game script's memory is its `state` (Observed, 605).** Module-level Lua variables do not survive between calls. What a script keeps goes in its state table, which the save stores.
- **A script cannot see a unit's age in the pay function (Observed, 605).** The replaceable income function gets only the difficulty factor, the cargo's price factor and the distance. A script changes a unit's pay through the ticket price event instead ([finances.md](finances.md#the-ticket-price-event)).
- **A cargo unit is an entity with its own pickup time and legs (Observed, 605)** ([Cargo units](#cargo-units-as-a-script-sees-them)).
- **A journal booking goes to the one account it names (Observed, 605).** The player, each vehicle and each line keep their own account ([finances.md](finances.md#accounts-of-vehicles-and-lines)).
- **Open.** The game's own age for a unit is not exposed (only the spoiled flag is), so what `deliveryExtensionDuration` equals stays inferred ([spoilage.md](spoilage.md)). A script cannot see how a unit's pay is shared between the lines that carried it.

## Rules for a game script

- **No commands from `handleEvent`.** `sendCommand` called inside an event handler trips the engine assertion `!m_betweenChanges`. Send from the script's `update`.
- **No result callbacks from `update`.** `sendCommand` with a result callback raises "Callbacks are currently disallowed"; without one it works. Success can only be read from the state afterwards.
- **State lives in the script's `state`.** Module-level variables do not survive between calls, so counters and queues go in the game script's state table. State the handler writes is visible to `update`.
- **A vanished entity aborts the whole event.** `getComponent` on a vehicle sold while its cargo is still on the way raises "Invalid entity" (8 times in 15 minutes on a large save), and every unit of that event is lost to the script. Guard lookups with `api.engine.entityExists`, and read a leg's carrier from `PickupPoint.carrier`, not from the vehicle.
- **Journal entries carry `time = -1`.** An entry sent with `api.cmd.makeJournalBookAssetCmd` must have its time set to -1. The entry has no text field, only its time, amount and category with its carrier.

How a mod's files and modules are found at load is in [mods.md](mods.md#loading-a-mods-files).

## Cargo units as a script sees them

- **Each cargo unit is a `SimCargo` entity** with `startTime` (when it was made), `pickupTime`, a source entity, `deliveryExtensionDuration` and `pickupPoints`. The pickup points have one entry per vehicle and line the unit travelled on, each with its own carrier and its start position. `api.engine.util.cargo.isGoodQuality(unit)` tells whether it is spoiled. How the spoiled flag follows the age is in [spoilage.md](spoilage.md), and the limit, `api.engine.util.stock.getAdjustedDeliveryTime(cargoType)`, in [delivery-times.md](delivery-times.md).
- **A unit's age runs from its own `pickupTime`.** The age counted that way matches the game's spoiled flag ([Evidence](#evidence-and-tests)). So cargo waiting in an industry's stock has not started to age. Units are picked up one at a time, so on a train that waits for a full load the first units loaded are the first to pass the limit.
- **The income function sees no unit.** `baseConfig.economy.cargoIncomeScript` can be replaced by one mod at a time. The game calls it once per delivered unit, before the unit's arrival event, with only `difficultyFactor`, the price factor and the distance.
- **A cargo type's price function cannot be swapped at run time.** Its `scriptRef` can be read through `api.res.cargoTypeRep.get(id)`, but changing it there has no effect. The eleven cargo types seen all use `incomeFactors.constantFn` with initial price 4, final price 3.2, decay rate 0.01 and decay mod 0.1; only the decay start differs (100 for one cargo, 50 for the others).

## Bookings from a script

- `api.cmd.makeJournalBookAssetCmd` with an INCOME entry, sent from `update`, changes the named account by exactly the booked amount, negative or positive. Its first argument is the entity whose account takes the entry: the player, a vehicle or a line ([finances.md](finances.md#accounts-of-vehicles-and-lines)).
- The entry's carrier is the row it shows under in the Finances tab ([finances.md](finances.md#rows-against-the-booking-categories)).
- A vehicle's logbook and a line's hold counters (items transported and the like), not money, so a mod cannot show a booking there.

## Evidence and tests

All on 605, in the Best Before mod's test saves (its findings.md, "Test saves"; the Giga temperate game is [in test-games.md](test-games.md#giga-temperate-game-wr26a)), from the game's log and the mod's own log lines.

- **Bookings.** On the small save at 4x, 104 units: every tracked vehicle, line and player account moved by pay minus running costs minus the bookings, within 3%. A later run booked 42 bonuses and 60 deductions to the player, and 97 of the 102 entries showed as an exact step of the balance.
- **Logbooks.** Listed in the mod's [discarded.md](https://github.com/WuphonsReach/tf3-best-before-mod/blob/5f4b203e701cda7de243e0d16bdc8997e298dadc/docs/future/discarded.md) (tf3-best-before-mod, at commit 5f4b203).
- **Age from pickup.** On WR26A, a grain train's 64 units arrived with ages spread over about a minute (1,711,800 to 1,770,200 ms), the same in two runs of the same trip. The mod's age (now minus `pickupTime`, less `deliveryExtensionDuration`) agreed with the game's flag on all but 7 of 69,907 units ([spoilage.md](spoilage.md)).
