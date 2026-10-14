# Town rating state

The script state of `game_mechanics/towns/town.gs` holds a `townStates` table. Checked on 604.

- Editor saves: empty.
- A new game (**Observed**, 604, eight of our games saved at once, 2 to 5 towns): the table holds one entry for 2 towns, two for 3 towns and two for 5 towns, while the town records, the names run of [entity-names.md](entity-names.md#town-names-604) and the `townState` entries of the `town_cargo.gs` state all give the town count, and the count on the New Game screen is the same ([industries.md](industries.md#the-industry-count-on-the-new-game-screen-and-in-the-save-604)). The count to trust for a new game is the town records, not this table.
- Played saves: one entry per town that has state, so not every town is in it. 34 in a 34-town save of ours; 13 in catalog save [6421140](https://mod.io/g/transportfever3/m/marschbahn-westerland-niebll-ohne-mods) and 11 in [6430076](https://mod.io/g/transportfever3/m/gigantomanisch-fjpjcl8aod-start-bearbeitet).

## Fields per town

| Key | Holds |
|---|---|
| `townEntity.entity` | The town's entity id |
| `authorityScore` | Number from 0 to 1 |
| `cachedRatings` | Six ratings, each `{value, critical}`: `cargo_delivery`, `noise`, `people_happiness`, `pollution`, `traffic_congestion`, `urban_care`. A seventh, `growth_level`, was present in the played saves of the [new Small game](#a-new-games-three-towns-against-their-windows-604) (see below) |
| `eventFactors.score` | Number from 0 to 1 |
| `eventFactors.reasonToPenalty` | Penalties by reason: `DemolishedTownBuilding`, `Rocks`, `TerrainModification`, `Trees` |
| `constructionBoni` | **Open** |
| `deliveryRating` | Sometimes present. A name such as `VeryPoor` |

## What the numbers do

- **Observed**: `authorityScore` is the lowest of the six cached ratings in all 58 entries checked.
- **Observed**: `urban_care` follows `eventFactors.score` (one exception in 58: 0.666 against 0.9994), and `score` falls as penalties rise.
- **Confirmed**: in [6430076](https://mod.io/g/transportfever3/m/gigantomanisch-fjpjcl8aod-start-bearbeitet) two towns have `TerrainModification` at 1.0, score 0.0 and authority 0.0. They are the only two towns with a red alert and an empty Reputation bar in the game. So terraforming near a town can take its Reputation to zero. The entity ids were not matched to town names; the pairing is by count.

## Not here

Town size, cargo demand and positions are not in the script states. They are in the entity data, see [town-records.md](town-records.md). The industries' script state is just as bare, see [industries.md](industries.md#the-industries-script-state).

## A new game's three towns against their windows (604)

**Observed** on 604 in the [Small subarctic game](test-games.md#small-subarctic-game), paused at clock 5,997,000 (save `1246`), with the three town windows read right after. The table has three entries.

- **Entry order is the entity order, which is the names order.** The three `townEntity.entity` ids (17,912, 17,913, 17,914) are in the same order as the names table's town slots (Retford, Bromsgrove, Todmorden, see [subsidies.md](subsidies.md#a-new-game-an-offer-its-expiry-and-an-accepted-subsidy-604)). The growth labels below tie each entry to a window on their own, and the entity order then gives the same pairing. The table itself lists them in the order 17,913, 17,914, 17,912.
- **`growth_level` is the growth label of the town window.** It is a rating of its own in `cachedRatings`, worked out in the game's `town_util` (`game_mechanics/towns/town_util.tl` in `base/content/game_mechanics.zip`) from the authority and the supplies, not the town's size class. Values against the label in the window: 0 for Bromsgrove ("Stagnant", 161 residents, growth rate 0%), 1 for Retford ("Growing Very Slowly", rate 20%), 3 for Todmorden ("Growing"). In the earlier save described in [subsidies.md](subsidies.md#completion-604) the same field read 4 for Todmorden, when its window said "Growing Fast". So 4 is Growing Fast and 3 Growing; 2 was not seen with its label. The field was lower in this save than in that one, so a town's growth can fall as well as rise.
- **`noise` matches the window's noise chart.** Retford's `noise` is 0.486 and the noise chart in its window ended just under 50%; its Noise rating read "Mediocre" and it is the lowest rating, so its `authorityScore` is 0.486 too (Town Authority "Mediocre"). Todmorden's noise is 0.633 and Bromsgrove's 0.859. Bromsgrove's Town Authority read "None" in the window while its state holds a score of 0.859, so that label is not the score alone. **Open**.
- **The window's noise sources** (Retford: company vehicles 79%, residents' vehicles 18%, stations 2%) were not found in the state.

## The window's Reputation and how it recovers (604)

**Observed** on 604 in one Medium dry game, one town, after the player demolished many of its buildings and then watched it with the game paused. Its entity id is the fourth of five consecutive ids and the town is the fourth in the names table's town order; it is the only one of the five entries with penalties.

- **The window's Reputation is `eventFactors.score`.** The window read 79%, 71% and 74% at three pauses where the state held 0.7889, 0.7055 and 0.7388. The same number is `cachedRatings.urban_care`.
- **"Demolished Buildings" is the `DemolishedTownBuilding` penalty.** The window read -21%, -29% and -26% at the same three pauses against 0.2111, 0.2933 and 0.2601. Taking one minus that penalty gives the score in those three. Terrain and tree penalties of 0.001 or less were also set and were not subtracted. In two earlier autosaves of the town the score was 0.6033 with four penalties (it equals one minus their sum) and 0.3111 with three (one minus their sum is 0.3064). So the score is not always one minus the sum. **Open**.
- **Recovery follows the game clock, not the calendar.** Every figure here is in the clock unit of [calendar.md](calendar.md#the-game-clock). At the calendar 0.25x (16,000 units a day) the demolish penalty fell by about 4.5e-7 to 4.7e-7 per unit over two stretches of 0.6 and 1.0 million units (whether the player demolished anything in them is not known, so these two are the weaker figures). At 4x (1,000 units a day) it fell 0.0332 over 64,000 units between two paused saves, 5.2e-7 per unit, and by the window's figures (-29%, -26%, -16%, -7% on four dates up to 10 January 1902) at 4.6e-7 to 5.0e-7 over the stretches between them. That is the same rate per unit and 14 times apart per game day. The window's "Annual Recovery 33%" is therefore not a calendar year: at 4x a calendar year is 365,250 units and would remove about 0.18. A fall of 0.33 takes roughly 650,000 to 700,000 units. The rate crept up as the penalty fell (4.5, 4.7, 5.2e-7); the cause is **open**.
- **Fully recovered** 810,400 units after the last of those saves, with no penalties left and a score of 1.0.
- **Reputation at zero** was seen once: a score of 0.0222 with the penalty at 0.9778.
- **The window hides both rows once the penalty is gone.** On 6 February 1902 (4x calendar) the window read -6% for Demolished Buildings and the final chart point 94%. By 3 July 1902 the Demolished Buildings and Annual Recovery rows were blank and the final point read 100%. At about 4.7e-7 per unit, 0.06 takes about 128,000 units, 128 days at 4x, which is mid-June: consistent. The save from 25 February 1903 has no penalties and a score of 1.0.
- **The Reputation chart** ends in a point that is the live score (71% with -29%, 84% with -16%, 94% with -6%, 100% with none). The points before it are older data thinned by merging, in the way old bookings are merged ([finances.md](finances.md#periods)): the chart does not keep a fixed number of points, and the long stretch since the early spike became one straight segment between a few points. So the spike's height depends on how the old samples fall into merged buckets when you look, not only on the past: by eye it read about 80% to 84% in the first views, then 79%, 59%, 57%, 80% and 76% (from May 1900 to April 1904 on the calendar). The point just before the live one kept rising while the live value was 100%: 34%, 43%, 54%, 56%, 62%, 73% from January 1902 to April 1903. Later views (October 1904 and April 1905) put the history at 72% to 82% for 1903 and 1904 with small dips (79%, 73%, 77%, 80%) while the live point read 100%, and an autosave from April 1904 holds a score of 1.0, no penalties and a lowest rating of 0.433, so the history is not an average of the score: an average over a span that is 100% since mid-1902 would approach 100%. By February 1906 (score 1.0 since mid-1902) the history had climbed from its 2% dip in 1900 in a nearly straight line to 79% in the 1902 point (about 77 points over about two years, close to the window's 33% a year), then flatter with a 73% dip in 1903 to 97% in 1905, against a live 100%. A slow recovery curve that is its own quantity is the open guess. The first two points matched saved scores (60% and 2%), the rest could not be matched, and no earlier score occurs as a value in a later save's stream. Treat the chart's past as a rough view, not a record. **Open** (the merge rule and bucket sizes were not read).
