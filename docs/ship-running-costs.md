# Ship running costs

What a ship's running-cost booking depends on: whether it is parked in a depot, and its condition. How the money journal books upkeep and running costs in batches, and how a vehicle's yearly figure is rebuilt from its place in the batch, is in [running-costs.md](running-costs.md#upkeep-and-running-costs-are-booked-in-batches-604). Checked on 604 in one game, the [Small subarctic game](test-games.md#small-subarctic-game).

## In short

- **Parked.** A ship "In Depot" on no line pays 5% of its running cost. Observed, 604, two ships: -200 against 4,006 for a `dunara_castle`, -88 against 1,752 for a `british_columbia`. The reduced rate follows the "In Depot" state, not the position: a ship waiting at the spawn point on a line pays in full.
- **Condition.** The booking is the model's base cost times a tier of 1.00, 1.05, 1.10 or 1.20, which the window shows as Very Good, Good, ... Very Bad. Observed, 604, one game; no 1.15 tier was seen. The game's API names a per-vehicle maintenance state behind it.
- **Reading it.** A ship's window yearly figure is its booking times about 24.35; the nth water running-cost booking of a batch is the nth ship (Observed, 604).
- **Not known.** Where the condition state is stored (the ship's instance and journal rows carry nothing of it), and whether the odd single values among the bookings are parked-for-part-of-a-batch cases (not checked against positions).

## Evidence and tests

### A ship parked in a depot pays 5% of its running costs (604)

**Observed** on 604, the same game, saves `1333` to `1339` (clock 6,428,600 for the last), the journal from 5,940,000 to 6,420,000 and the windows of Ship 5 and Ship 18. Both ships were "In Depot" (Todmorden Ship Depot East) and on no line.

- **The windows.** Ship 5 (a `dunara_castle`, bought for the first fishing line and sent to the depot when it proved too big for the `STATIONS_WATER_SMALL_PIER` (Small Landing) beside the first `HARBOR_SMALL`) showed $97,537/Year and "Last Year $-5,000", its bars at 1,500 to 5,000 per period. Ship 18 (a `british_columbia`) showed $42,672/Year and "Last Year $-10,134" in one bar. The year figure is the ship's own running cost at the full rate: 97,537 / 24.35 batches a year is 4,006, and 42,672 / 24.35 is 1,752, the figure a working `british_columbia` books each batch.
- **A parked ship has a booking every batch.** The `Maintenance - vehicle running costs (Water)` bookings of a batch number one per ship, parked or not: 6 per batch before the 13 purchases (Ships 1 to 6, with Ship 5 parked) and 19 from the batch at 6,000,000 on (the 13 new ships were still sitting at the depot's spawn point on their lines, none had sailed). The bookings come in ship order: the fifth is Ship 5, the eighteenth is Ship 18.
- **The parked rate is 5%.** Ship 5's booking was -200 in every batch checked (5,940,000, 6,000,000 to 6,420,000), against 4,006 at the full rate (200 / 4,006 = 0.050), and 24.35 x 200 is 4,870, the 4,800 and 5,000 of its yearly bars. Ship 18's eighteenth booking read -1,752 at 6,240,000, -1,198 at 6,300,000 and -88 at 6,360,000 and 6,420,000: 88 / 1,752 is 0.050. The -1,198 is a batch in which it spent part of the period running and part parked: with a full rate of 1,752 and a parked rate of 88, 1,198 is two thirds of the 60,000 units at the full rate, so it went into the depot about 40,000 units into that period, around clock 6,280,000. It was still sailing in `1333` (6,242,200) and in the depot by `1334` (6,287,000), which agrees.
- **A ship waiting at the spawn point on a line pays in full.** At 6,000,000 the five new `sydfart` booked -3,004 and the eight new `british_columbia` -1,752 each, the full rates, while sitting at the depot, Ship 8 and Ship 18 among them (they had been taken off their lines while the game was paused, see [vehicles.md](vehicles.md#vehicle-instances-604), and were back on them). So the reduced rate follows the vehicle's "In Depot" state (a ship parked on no line) and not its position.
- **The window number is the ship's own.** Whether the cost the player saw in the depot window might be other ships' upkeep: it is not, the figures match this ship's own bookings (Ship 5 and Ship 18 in the journal order) and its own year figure.

The -200 among the -1,752s and -3,004s of every batch is therefore Ship 5. The other variations (-1,262, -1,402, -1,472 and -1,682 against -1,752 for a small ship, -2,403 to -2,764 against -3,004 for a large one) are taken up in the next section.

### A ship's running cost follows its condition (604)

**Observed** on 604 in the Small subarctic game, from the journal of save `1416` (clock 10,720,600, paused; batches at 10,440,000 to 10,680,000) and the ship windows in the player's screenshots of 14:21. The window's "Condition" bar has five steps and a label; its yearly cost line (`$N/Year`) is the batch booking times about 24.35 (a year of 1,461,000 units in 60,000-unit batches).

| Ship (nth water running-cost booking) | Window label | Window `$/Year` | Booking | Against the same model at Very Good |
|---|---|---|---|---|
| Ships 2 and 4, Canadian Trawler (2nd, 4th) | Very Good | 42,672 | -1,752 | 1.00 |
| Ships 6, 9 and 10, Sydfart (6th, 9th, 10th) | Very Good | 73,152 | -3,004 | 1.00 |
| Ships 8 and 11, Sydfart (8th, 11th) | Good | 76,810 | -3,154 | 1.05 |
| Ship 16, Canadian Trawler (16th) | Very Bad, with the warning "The condition of Ship 16 is very bad" | 51,206 | -2,103 | 1.20 |

- **The tiers are exact.** 3,154 / 3,004 = 1.050 and 2,103 / 1,752 = 1.200. Two more tiers show in the bookings without a window read: -3,305 (1.100 of 3,004: Ship 8 from the batch at 10,560,000 on, after -3,154 at 10,500,000, so its condition fell one step within one batch period) and -1,928 (1.100 of 1,752: Ship 17 in all five batches). No 1.15 booking was seen. A booking is the model's base cost times a tier, not a smooth function of wear.
- **Ships 12 to 16 and 19 sat at the 1.20 tier in all five batches** (-2,103 each) and Ship 17 at 1.10. These are the eight `british_columbia` ships bought together at 6,000,000 for TOD Fishery 3, which each booked the base -1,752 then (the base figure). Ships 1 to 4 stayed at -1,752 apart from short dips. The game's API names the quantity: a maintenance state number per vehicle (`getVehicleMaintenanceState`) with emission, comfort, top-speed and running-cost penalties derived from it (`api/engine/util.d.tl`), and a `maintenanceStation` entity in the vehicle's transport component (`api/engine.d.tl`).
- **This explains part of the variation noted at the end of the previous section.** A run of -2,103 in place of -1,752 is a condition penalty. The odd single values (-2,644, -2,884 and -2,776 against -3,004; -1,766 and -1,935 against -2,103) are in the range of a ship that spent part of a batch parked at the 5% rate, but that was not checked against positions.
- **Where the state is kept is Open.** The ship's model instance and its journal rows carry nothing of it. A test: send one of the very-bad ships to a depot (or its maintenance station) and make a save just before and one just after, paused each time; the value that moves from near zero to near one in that vehicle's record is the state.
