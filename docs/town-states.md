# Town rating state

The script state of `game_mechanics/towns/town.gs` holds a `townStates` table. Checked on 604.

- Editor saves: empty.
- Played saves: one entry per town that has state, so not every town is in it. 34 in a 34-town save of ours; 13 in catalog save [6421140](https://mod.io/g/transportfever3/m/marschbahn-westerland-niebll-ohne-mods) and 11 in [6430076](https://mod.io/g/transportfever3/m/gigantomanisch-fjpjcl8aod-start-bearbeitet).

## Fields per town

| Key | Holds |
|---|---|
| `townEntity.entity` | The town's entity id |
| `authorityScore` | Number from 0 to 1 |
| `cachedRatings` | Six ratings, each `{value, critical}`: `cargo_delivery`, `noise`, `people_happiness`, `pollution`, `traffic_congestion`, `urban_care` |
| `eventFactors.score` | Number from 0 to 1 |
| `eventFactors.reasonToPenalty` | Penalties by reason: `DemolishedTownBuilding`, `Rocks`, `TerrainModification`, `Trees` |
| `constructionBoni` | **Open** |
| `deliveryRating` | Sometimes present. A name such as `VeryPoor` |

## What the numbers do

- **Observed**: `authorityScore` is the lowest of the six cached ratings in all 58 entries checked.
- **Observed**: `urban_care` follows `eventFactors.score` (one exception in 58: 0.666 against 0.9994), and `score` falls as penalties rise.
- **Confirmed**: in [6430076](https://mod.io/g/transportfever3/m/gigantomanisch-fjpjcl8aod-start-bearbeitet) two towns have `TerrainModification` at 1.0, score 0.0 and authority 0.0. They are the only two towns with a red alert and an empty Reputation bar in the game. So terraforming near a town can take its Reputation to zero. The entity ids were not matched to town names; the pairing is by count.

## Not here

Town size, cargo demand and positions are not in the script states. They are in the entity data, see [town-records.md](town-records.md). Industries' script state (`game_mechanics/industries/industries.gs`) was empty in the editor saves checked. In a played 604 game (catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3), over 300 industries) it held only `industryFailedExtensions`, `tick` and `triangles`, so the Industries tab's input, output, workload and shipment figures are not kept there (**Observed**). They are presumably in the entity data, which was not read.
