# Inflation and cost scaling

Two separate things move prices in a game, and both get called inflation:

- The **Inflation option** cuts income as the company's rank rises. Its effect is stored in the save, in the company state.
- A **table of cost multipliers by year** raises what things cost as the game's date passes. It is a game script setting and is not stored in the save.

The settings option itself is in [settings.md](settings.md). The rank the cut depends on is in [company.md](company.md).

## The income multiplier

`ticketPriceMultiplier` in `companyState` is the cut that the Inflation option (`advancedOptions.inflationFactor`, see [settings.md](settings.md)) makes to income. In the game's scripts (604 build) it is applied to every vehicle's ticket price, which covers passengers and cargo alike. Each Inflation level sets the multiplier reached at Tycoon. Between rank 1 (no cut) and rank 15 the multiplier falls in a straight line: 1 + (rank − 1) × (f − 1) / 14, where f is the value at Tycoon. It is computed from `potentialLevel`, the rank earned, not the rank claimed. (Sources: `base/difficulty_util.tl` and `base/mod.script.tl` in `base.zip`, which write f into `game_mechanics/company/company_growth_config.res`; `company_progression_util.tl` and `company_growth.script.tl` in `game_mechanics.zip`.)

| Inflation | f in the 604 scripts | f seen in 599 and 601 saves |
|---|---|---|
| None | 1 (key absent) | 1 (key absent) |
| Low | 0.9 | 0.8 |
| Normal | 0.75 | 0.6 |
| High | 0.6 | not seen |
| Very High | 0.5 | not seen |

- **Observed** in 120 catalog saves (one per catalog entry, 568 to 604), 117 of which hold the state:
  - **604**: 51 saves hold the key, and every value equals the formula with the 604 values above (Low 13, Normal 33, High 5 saves). No Very High save had reached rank 2.
  - **599 and 601**: 11 saves hold the key, and every value fits the same straight line with f = 0.6 for Normal (9 saves) and 0.8 for Low (2). So the cut was harsher before 604.
  - The key is **absent** at rank 1 and when Inflation is None, as the scripts say (the multiplier is then nil, which removes the key). The 568 and 585 saves have no key even at ranks up to 15. Their header settings were not read (see [header.md](header.md)), so whether the mechanism postdates them or Inflation was None in all ten is **Open**.
- An absent key means no cut, not a missing value.
- The Inflation option does not touch upkeep (**Observed**, 604, warehouse upkeep in two games). Upkeep that rises with the date is a separate mechanism, see [below](#the-year-cost-table).

## The year cost table

Warehouse upkeep in two games, 1937 against 2000, differed by a factor that the Infrastructure Upkeep setting explains only in part ([warehouses.md](warehouses.md#a-second-game-records-without-cargo-tags)). The 3.3 left over is **Open**, and the date probably explains it.

The game's Lua API definitions (`api/tealdef/api/type.d.tl`, install that writes 604) give each construction a `costsYearProgression` flag and the game config a `treeCostYearMultipliers` table keyed by year. The base game fills that table in `base/mod.script.tl` (in `base/content/base.zip`, 604 build) with one multiplier every 20 years: 1900 ×1.0, 1920 ×1.5, 1940 ×2.2, 1960 ×3.2, 1980 ×4.0, 2000 ×5.0, 2020 ×6.0. If a cost takes the value of the last step reached, 1937 gets ×1.5 and 2000 gets ×5.0, and 5.0 / 1.5 = 3.33, the factor left over above. Which constructions set the flag is not in any readable file. Despite its name, the table evidently scales more than trees. A road depot's own file has era templates with other steps (×3 from 1940, ×9 from 1980); whether a depot takes the table's multiplier on top is **Open** ([running-costs.md](running-costs.md#a-road-depots-upkeep-against-its-window-604)).

Players report the same steps: building upkeep that stays flat for 20 years and jumps at 1960 and 1980, by about a quarter at 1980 (4.0 / 3.2 = 1.25), and by about a fifth at 2000 and 2020 (1.25 and 1.2). Players also report that a new game's prices depend on its start year in the same 20-year steps, and not on the Inflation option. The author of the script mod Inflation (USD) ([6436200](https://mod.io/g/transportfever3/m/inflation-usd)) says the base game charges the same prices every year; the table contradicts that for upkeep, while three port pieces kept their purchase price through 1920 ([below](#upkeep-and-prices-at-the-1920-step)). The same-game test was run at 1920 ([below](#upkeep-and-prices-at-the-1920-step)); the 1940 and later marks are untested.

### Upkeep and prices at the 1920 step

**Observed** on 604, one game (subarctic, start 1900, Infrastructure Upkeep 100%), first paused on 7 November 1919, 55 days before the table's first step, then on 1 January 1920.

- **Every figure read was still the file's base value.** Window upkeep: warehouse $50,000 a year (two warehouses, one specialized module each), a station with two bulk terminals $42,000, a station with one cargo platform $21,000, a port $24,000, a road depot $30,928 (30,000 plus 928 accumulated, see [running-costs.md](running-costs.md#a-road-depots-upkeep-against-its-window-604)), a port with three terminals and extra buildings $68,000. Build menu: the port's small building $12,000 with $2,000 a year, the small dock and the small landing $60,000 with $10,000 a year. The harbour files (`stations/water.zip`: `water/harbor_modular.tl`, `small_pier.module.lua`, `passenger_dock_50_12.module.lua`) give 24,000 upkeep for the small port and 60,000 price with 10,000 upkeep for a pier or dock module, so nothing rose between 1900 and 1919 (the first step of the table is ×1.0).
- **The journal agrees.** Upkeep batches stay on the 60,000-unit grid up to the save (174 `MAINTENANCE` bookings each) and repeat the first-year values: 2 x -2,053 (warehouses), -1,724, 2 x -1,232 (depots), -985 (port), 2 x -862, 2 x -616, 2 x -4,106 and the 205 halves of the maintenance buildings.
- **Both older warehouse readings now fit the table exactly.** 50,000 per specialized module is the base: 1937 (50% upkeep setting) gave 50,000 x 1.5 x 0.5 = 37,500 and 2000 (100%) gave 50,000 x 5.0 = 250,000. This makes the table a step function that the warehouse follows, **Observed** in three games, and the 1920 step was then caught inside one game (next bullet).
- **The step comes on the day, ×1.5 (Observed, 604, one game).** A save paused 1,000 ticks into 1 January 1920 (clock 72,529,000, the day began at 72,528,000) showed four windows at exactly 1.5 times their 1919 figures: warehouse $75,000 (two warehouses, both read), the two-terminal station $63,000, the three-terminal port $102,000 and the one-platform cargo station $31,500. The journal's last upkeep batch was still the old one (72,480,000).
- **The journal steps at the next batch, every building by 1.5 (Observed, 604).** A save paused on 2 January (clock 72,544,800) holds the batch at 72,540,000. Its 50 `INFRASTRUCTURE` bookings that are not street upkeep are the 1919 amounts times 1.5, to the unit (a year is 24.35 batches, so $75,000 is -3,080): 2 x -2,053 to -3,080 (warehouses), -1,724 to -2,587 (two-terminal station), 2 x -1,232 to -1,848 (road depots, so a depot takes the table's ×1.5 and not its own file's era steps), -985 to -1,478 (port), 2 x -862 to -1,293, 2 x -616 to -924, 2 x -4,106 to -6,160 (ship depots), -2,792 to -4,188 (the three-terminal port, 68,000 to 102,000), -1,642 to -2,464 (the boat maintenance building, see below), and the maintenance buildings' 36 halves of -205 to -308. The batch has the same 174 bookings as before.
- **The boat maintenance building steps with the rest (Observed, 604, window and file).** Its window read $60,610 a year on 2 January 1920 (9 of 12 in the pool, nine ships listed): 40,000 x 1.5 = 60,000 plus an accumulated 610. The file (`depots/water.zip`, `water/water_maint_station.script.lua`) gives a base upkeep of 40,000, a price of 240,000 and a pool of 12, and 60,000 / 24.35 is the -2,464 booking (from -1,642). The window's accumulated 610 did not match any booking of that batch; the water vehicle-maintenance bookings were -5,010, -4,675 and -435.
- **Street upkeep did not step.** The one `STREET` booking (-347, 8,450 a year) is the same in both batches, so the year flag is on buildings and not on roads. The vehicle bookings (running costs and vehicle maintenance, 123 per batch) stayed at the same total within the usual variation (-173,802 to -173,882), so vehicles' running costs did not step either.
- **A mod's building follows the table too (Observed, 604, one window).** The Todmorden Boathouse, a building from the Boathouse mod (`ingo_boathouse_asset`, [mods.md](mods.md)), read $22,558 a year on 2 January 1920 with one ship in its pool (1 of 2): 15,000 x 1.5 = 22,500 plus an accumulated 58. The batch at 72,540,000 has two water `INFRASTRUCTURE` bookings of -924 (from -616), 22,500 / 24.35; which of the two is this building was not matched. So the multiplier is not limited to the base game's own files, and whether the mod sets a flag or the game applies it to every construction's upkeep is **Open**.
- **Purchase prices of three port pieces did not step, their upkeep did (Observed, 604, save paused 2 January 1920).** The build menu read $12,000 for the small building, $60,000 for the small dock and $60,000 for the small landing, the same as on 7 November 1919, while the upkeep beside each rose by 1.5: $2,000 to $3,000, $10,000 to $15,000, $10,000 to $15,000. So the year multiplier acts on upkeep here and not on the price. Prices of other buildings, of vehicles and of roads were not read after the step; whether any construction's price takes the table (the players' report above) is **Open**.
- The stream holds no table of multipliers (a search for the 1920 and 1940 keys found only unrelated time lists), so the multiplier is likely applied when the game reads the construction.
