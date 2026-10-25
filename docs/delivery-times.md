# Expected delivery times

The expected delivery time of each cargo, as the company window's Delivery Time tab shows it, against the `timeToDeliverInSeconds` of the cargo files. Cargo that went bad on the way, and how its age may compare with these times, is in [spoilage.md](spoilage.md). Checked on 604 in one game, the [Small subarctic game](test-games.md#small-subarctic-game), and the year dependence on 605 in the [Giga temperate game](test-games.md#giga-temperate-game-wr26a).

## In short

- **The tab shows the cargo file's time times 1.5 (Observed, 604, one game).** Each bar's tooltip in the company window's Delivery Time tab equals the `timeToDeliverInSeconds` of the cargo's file multiplied by 1.5, from 22 m 30 s for meat to 1 h 52 m for stone. The three tallest bars are clipped at the axis top but their tooltips give the real value.
- **The 1.5 is not a constant: the factor shrinks with the game year, then holds at 0.75 (Observed, 605, one game, 1900 to 2032).** The tab's value is the engine's `getAdjustedDeliveryTime(cargoTypeId)` in seconds (script `finance/finances_cargo_lifetime.tl` in `game_mechanics.zip`). It is the cargo file's time x `1.5 - (year - 1900) / 160`, cut to whole seconds, through 2019; that line reaches 0.75 in 2020, and from then to 2032 (the last year logged) the time is the file's x 0.75, cut. One factor serves every cargo type and steps once a year: grain reads 1,929 s in 1900, 1,125 s in 2000 and 964 s from 2020 on.
- **The year is the calendar year shown, not the game clock (Observed, one pair of saves).** A copy of a 1919 save with the date set back to 1900 and the clock nearly the same read 1.5 again.
- **Difficulty does not move it (Observed, two settings).** Hard and Easy at 1919 gave the same times, and Very High delivery sensitivity at 1900 still gave 1.5.
- **A vehicle's cargo-quality bar is 1 minus the load's age over the adjusted time (Observed, 605),** matched to 0.0006 on logged units. The spoiled flag uses the same time, less any paused warehouse time ([spoilage.md](spoilage.md)).
- **Open.** Years after 2032 (a 2191 save's spoiled units fit 0.75, but indirectly), difficulty options other than the two tried, calendar speeds other than 4x, whether the 0.75 floor depends on anything but the year, and why 61 of 3,030 readings from 1900 to 2000 are 1 s under the rule (all where the product is a whole number; float rounding is likely).

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

The five bars at the 3,000 s class stand at the 1 h 15 m level, as the drop icon's tooltip says. The three tallest bars (the 4,500 s class) are clipped at the 1 h 50 m top of the axis, but their tooltips still give the real value, 1 h 52 m, so the clipping only affects the drawing. The cargo behind a bar is told by its icon and by the number, not by a name: the cement bar has the 2,250 s of the `cement` file, which `sawdust`, `dyes`, `vehicles`, `tools`, `machines`, `glass` and `fuel` share, and the flask is one of the 1,800 s cargos. 1.5 is the 1900 value (see [the year dependence](#the-factor-follows-the-game-year)). The save's `townConfig.sensitivityCargoDelivery` was 4.0 (with the other settings listed in [settings.md](settings.md)), and no test in this game changed any setting.

## Evidence and tests

### The factor follows the game year

**Observed**, 605, the Giga temperate game ([test-games.md](test-games.md#giga-temperate-game-wr26a)), read from a mod's log of the engine's adjusted time per cargo type: one line per cargo type once a game month and at each year change. Source: tf3-best-before-mod `d203e95`, `docs/future/delivery-limit-tests.md` (the branch is not merged yet; pin the link once it is).

- **The run.** Save `1900 1025-0722` played at calendar speed 4x to 1973, then `1974-test 1025-1103` from June 1974 to 2032 (about nine game months between the two logs are in neither). All 133 years from 1900 to 2032 are logged, in 427 snapshots, and no (year, cargo) pair ever logged two values. Between year changes the clock advanced a steady 365,000 or 366,000 units a year.
- **1900 to 2019.** Of the 3,030 (year, cargo) readings from 1900 to 2000 with a nonzero file time (passengers have none), 2,969 equal `timeToDeliverInSeconds` x `1.5 - (year - 1900) / 160` cut to whole seconds and 61 are 1 s less. All 61 are among the 443 readings whose product is a whole number, in 1932 (12), 1952 (7), 1964 (26) and 1972 (16). The 1,830 readings from 2001 to 2019 all equal the rule. Grain (1,286 s) reads 1,929 s in 1900, 1,768 in 1920, 1,607 in 1940, 1,446 in 1960, 1,125 in 2000 and 972 in 2019. The earlier saves 1024-1818 to 1024-1904 gave 1.4 in 1916 and 1.39375 in 1917, on the same line.
- **2020 to 2032.** All 390 readings are the file time x 0.75, cut (grain 964 s, fuel 2,250 s gives 1,687 s). The line would give 0.6813 in 2031, so the factor stops at 0.75.
- **Calendar year, not clock.** Save `1919 1025-0722` (clock 554,250,400) logged year 1919 and grain 1,776 s; its copy `1900 1025-0722`, with the date set back and the clock at 554,181,200, logged year 1900 and grain 1,929 s.
- **Difficulty.** Save `1918 1024-2036` loaded on Hard and on Easy at 1919 logged the same times (grain 1,776 s, the 900 s class 1,243 s, the 4,500 s class 6,215 s). Raising delivery sensitivity to Very High at 1900 left the factor at 1.5 (from the age at which units turned spoiled), so the difficulty presets (which only set stored values) are not what shrinks it.
- **Earlier indirect readings.** "About 0.84 in 2000", read from where units turned spoiled, was wrong: the log reads 0.875. A 2191 save's spoiled units gave about 0.75, which fits the floor.
- **The cargo bar.** A vehicle window's cargo-quality bar equals 1 minus the unit's age over this adjusted time.
