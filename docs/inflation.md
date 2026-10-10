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

The game's Lua API definitions (`api/tealdef/api/type.d.tl`, install that writes 604) give each construction a `costsYearProgression` flag and the game config a `treeCostYearMultipliers` table keyed by year. The base game fills that table in `base/mod.script.tl` (in `base/content/base.zip`, 604 build) with one multiplier every 20 years: 1900 ×1.0, 1920 ×1.5, 1940 ×2.2, 1960 ×3.2, 1980 ×4.0, 2000 ×5.0, 2020 ×6.0. If a cost takes the value of the last step reached, 1937 gets ×1.5 and 2000 gets ×5.0, and 5.0 / 1.5 = 3.33, the factor left over above. Which constructions set the flag is not in any readable file. Despite its name, the table evidently scales more than trees.

Players report the same steps: building upkeep that stays flat for 20 years and jumps at 1960 and 1980, by about a quarter at 1980 (4.0 / 3.2 = 1.25), and by about a fifth at 2000 and 2020 (1.25 and 1.2). Players also report that a new game's prices depend on its start year in the same 20-year steps, and not on the Inflation option. The author of the script mod Inflation (USD) ([6436200](https://mod.io/g/transportfever3/m/inflation-usd)) says the base game charges the same prices every year, which the table contradicts. A test that holds settings and rank fixed: read one warehouse's upkeep in the same game just before and just after 1 January of a 20-year mark (1940, 1960 and so on).
