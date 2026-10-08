# Cargo type ids

Checked on 604. Ids come from the economy the save uses, so mods and other climates can change them. Check them against a Towns export of the same save before relying on them.

## Temperate economy (`temperate.eco`)

| Id | Cargo | Id | Cargo |
|---|---|---|---|
| 6 | fish | 16 | machines |
| 7 | meat | 20 | fuel |
| 8 | beverages | 27 | clothes |
| 9 | vegetables | 28 | tinned_food |
| 13 | planks | 30 | tools |
| 14 | vehicles | 31 | furniture |
| 15 | cement | 32 | glass |
| | | 33 | bricks |

- Cement (15) was seen as a starting industrial cargo in catalog save [6430076](https://mod.io/g/transportfever3/m/gigantomanisch-fjpjcl8aod-start-bearbeitet), which uses `::/economy/all.eco`. That save's towns use 6, 7, 9 (commercial) and 13, 15, 20, 33 (industrial).
- Glass (32) was seen in one hand-built town in [6421140](https://mod.io/g/transportfever3/m/marschbahn-westerland-niebll-ohne-mods).

## Tiers and weights

The weight stored with each cargo in a town record is the cargo's `townConsumptionFactor` from the economy:

| Tier | Commercial | Industrial | Weight |
|---|---|---|---|
| 0 | fish, meat, vegetables | planks, fuel, bricks | 1.0 |
| 1 | beverages, clothes, tinned_food | furniture, machines, tools | 0.5 |
| 2 | none | vehicles | 0.25 |

## Starting cargo in new towns

A new town starts with one commercial and one industrial cargo. In a 34-town game started in 1900, every town got tier 0 cargo, spread almost evenly (11 / 12 / 11 commercial, 11 / 11 / 12 industrial). The map editor's Town Builder allows any cargo, so editor-made maps can start towns on tier 1 or vehicles.
