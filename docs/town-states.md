# Town rating state

The script state of `game_mechanics/towns/town.gs` holds a `townStates` table. Checked on 604.

- Editor saves: empty.
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

Town size, cargo demand and positions are not in the script states. They are in the entity data, see [town-records.md](town-records.md). The industries' script state is just as bare, see [script-states.md](industries.md#the-industries-script-state).

## A new game's three towns against their windows (604)

**Observed** on 604 in a new Small 1 : 3 subarctic game, paused at clock 5,997,000 (save `1246`), with the three town windows read right after. The table has three entries.

- **Entry order is the entity order, which is the names order.** The three `townEntity.entity` ids (17,912, 17,913, 17,914) are in the same order as the names table's town slots (Retford, Bromsgrove, Todmorden, see [subsidies.md](subsidies.md#a-new-game-an-offer-its-expiry-and-an-accepted-subsidy-604)). The growth labels below tie each entry to a window on their own, and the entity order then gives the same pairing. The table itself lists them in the order 17,913, 17,914, 17,912.
- **`growth_level` is the growth label of the town window.** It is a rating of its own in `cachedRatings`, worked out in the game's `town_util` (`game_mechanics/towns/town_util.tl` in `base/content/game_mechanics.zip`) from the authority and the supplies, not the town's size class. Values against the label in the window: 0 for Bromsgrove ("Stagnant", 161 residents, growth rate 0%), 1 for Retford ("Growing Very Slowly", rate 20%), 3 for Todmorden ("Growing"). In the earlier save described in [subsidies.md](subsidies.md#completion-604) the same field read 4 for Todmorden, when its window said "Growing Fast". So 4 is Growing Fast and 3 Growing; 2 was not seen with its label. The field was lower in this save than in that one, so a town's growth can fall as well as rise.
- **`noise` matches the window's noise chart.** Retford's `noise` is 0.486 and the noise chart in its window ended just under 50%; its Noise rating read "Mediocre" and it is the lowest rating, so its `authorityScore` is 0.486 too (Town Authority "Mediocre"). Todmorden's noise is 0.633 and Bromsgrove's 0.859. Bromsgrove's Town Authority read "None" in the window while its state holds a score of 0.859, so that label is not the score alone. **Open**.
- **The window's noise sources** (Retford: company vehicles 79%, residents' vehicles 18%, stations 2%) were not found in the state.
