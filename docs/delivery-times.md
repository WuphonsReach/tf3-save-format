# Expected delivery times

The expected delivery time of each cargo, as the company window's Delivery Time tab shows it, against the `timeToDeliverInSeconds` of the cargo files. Cargo that went bad on the way, and how its age may compare with these times, is in [spoilage.md](spoilage.md). Checked on 604 in one game, the [Small subarctic game](test-games.md#small-subarctic-game).

## The Delivery Time tab (604)

The company window's "Delivery Time" tab draws one bar per cargo type of the game, "the expected delivery time", with a note that food has a low expected time, that bulk cargo is less time sensitive and that late delivery affects town ratings. Each bar shows its value in a tooltip. **Observed**, one game, with these tooltips read by the player, each equal to the cargo file's `timeToDeliverInSeconds` (in the `cargos/` archives of `base/content`) times 1.5:

| Bar (icon) | Tooltip | File value x 1.5 |
|---|---|---|
| meat | 22 m 30 s | 900 s = 1,350 s |
| fish | 28 m 7 s | 1,125 s = 1,687.5 s |
| grain (ears of wheat) | 32 m 9 s | 1,286 s = 1,929 s |
| fertilizer (leaf sack) | 37 m 30 s | 1,500 s = 2,250 s |
| flask icon, 1,800 s class | 45 m 0 s | 1,800 s = 2,700 s |
| concrete | 56 m 15 s | 2,250 s = 3,375 s |
| drop icon (oil class, 3,000 s) | 1 h 15 m | 3,000 s = 4,500 s |
| stone, and the orange (ore) and light blue-grey bars beside it | 1 h 52 m each | 4,500 s = 6,750 s (1 h 52 m 30 s) |

The five bars at the 3,000 s class stand at the 1 h 15 m level, as the drop icon's tooltip says. The three tallest bars (the 4,500 s class) are clipped at the 1 h 50 m top of the axis, but their tooltips still give the real value, 1 h 52 m, so the clipping only affects the drawing. The cargo behind a bar is told by its icon and by the number, not by a name: the "concrete" bar has the 2,250 s of the `cement` file, which `sawdust`, `dyes`, `vehicles`, `tools`, `machines`, `glass` and `fuel` share, and the flask is one of the 1,800 s cargos. Where the 1.5 comes from is **Open**: the player's view is that the game difficulty may also change the spoil time, so 1.5 may hold only for this game's settings. The save's `townConfig.sensitivityCargoDelivery` was 4.0 (with the other settings listed in [settings.md](settings.md)), and no test changed any setting. A test would be the same tab read in a game made with another difficulty preset, or with that one slider moved.
