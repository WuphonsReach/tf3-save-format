# Expected delivery times

The expected delivery time of each cargo, as the company window's Delivery Time tab shows it, against the `timeToDeliverInSeconds` of the cargo files. Cargo that went bad on the way, and how its age may compare with these times, is in [spoilage.md](spoilage.md). Checked on 604 in one game, the [Small subarctic game](test-games.md#small-subarctic-game), and the year dependence on 605 in the [Giga temperate game](test-games.md#giga-temperate-game-wr26a).

## In short

- **The tab shows the cargo file's time times 1.5 (Observed, 604, one game).** Each bar's tooltip in the company window's Delivery Time tab equals the `timeToDeliverInSeconds` of the cargo's file multiplied by 1.5, from 22 m 30 s for meat to 1 h 52 m for stone. The three tallest bars are clipped at the axis top but their tooltips give the real value.
- **The 1.5 is not a constant: the factor shrinks with the game year (Observed, 605, one game).** The tab's value is the engine's `getAdjustedDeliveryTime(cargoTypeId)` in seconds (script `finance/finances_cargo_lifetime.tl` in `game_mechanics.zip`). Its factor over the cargo file's time was 1.5 in 1900, 1.4 in 1916 and 1.39375 in 1917 (a step at the year boundary), and about 0.84 in 2000 and 0.75 in 2191 (those two read from where units turned spoiled, so less direct). Difficulty is not the driver: Very High delivery sensitivity at 1900 still gave 1.5.
- **A vehicle's cargo-quality bar is 1 minus the load's age over the adjusted time (Observed, 605),** matched to 0.0006 on logged units.
- **Open.** Whether anything besides the year moves the factor (only the year was seen to), and the formula between the years sampled.

## The Delivery Time tab (604)

The company window's "Delivery Time" tab draws one bar per cargo type of the game, "the expected delivery time", with a note that food has a low expected time, that bulk cargo is less time sensitive and that late delivery affects town ratings. Each bar shows its value in a tooltip. **Observed**, one game, with these tooltips read by the player, each equal to the cargo file's `timeToDeliverInSeconds` (in the `cargos/` archives of `base/content`) times 1.5:

| Bar (icon) | Tooltip | File value x 1.5 |
|---|---|---|
| meat | 22 m 30 s | 900 s = 1,350 s |
| fish | 28 m 7 s | 1,125 s = 1,687.5 s |
| grain (ears of wheat) | 32 m 9 s | 1,286 s = 1,929 s |
| fertilizer (leaf sack) | 37 m 30 s | 1,500 s = 2,250 s |
| flask icon, 1,800 s class | 45 m 0 s | 1,800 s = 2,700 s |
| cement | 56 m 15 s | 2,250 s = 3,375 s |
| drop icon (oil class, 3,000 s) | 1 h 15 m | 3,000 s = 4,500 s |
| stone, and the orange (ore) and light blue-grey bars beside it | 1 h 52 m each | 4,500 s = 6,750 s (1 h 52 m 30 s) |

The five bars at the 3,000 s class stand at the 1 h 15 m level, as the drop icon's tooltip says. The three tallest bars (the 4,500 s class) are clipped at the 1 h 50 m top of the axis, but their tooltips still give the real value, 1 h 52 m, so the clipping only affects the drawing. The cargo behind a bar is told by its icon and by the number, not by a name: the cement bar has the 2,250 s of the `cement` file, which `sawdust`, `dyes`, `vehicles`, `tools`, `machines`, `glass` and `fuel` share, and the flask is one of the 1,800 s cargos. The 1.5 holds for 1900 only (see [the year dependence](#the-factor-follows-the-game-year)). The save's `townConfig.sensitivityCargoDelivery` was 4.0 (with the other settings listed in [settings.md](settings.md)), and no test in this game changed any setting.

## Evidence and tests

### The factor follows the game year

**Observed**, 605, the Giga temperate game ([test-games.md](test-games.md#giga-temperate-game-wr26a)), read from a mod's log of the engine's adjusted time per cargo type, saves 1024-1818 to 1024-1904. The factor over `timeToDeliverInSeconds` was 1.5 in 1900, 1.4 in 1916 and 1.39375 in 1917; later values (about 0.84 in 2000, 0.75 in 2191) come from the age at which units turned spoiled and are less direct. Raising delivery sensitivity to Very High at 1900 left it at 1.5, so the difficulty presets (which only set stored values) are not what shrinks it. The cargo-quality bar of a vehicle window equals 1 minus the unit's age over this adjusted time. Source: the sibling Best Before mod's findings notes (pin to a commit on its `main` once the branch merges).
