# Cargo type ids

Checked on 604 (the town-record counts in [climates-economies.md](climates-economies.md) also use 599 to 604 saves). The ids are not stored with names anywhere in the save, so the table comes from comparing town records with the game. Mods can add cargo; check the ids against a Towns export of the same save before relying on them.

## The ids in the table (`temperate.eco` and the other economies)

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
| 0 | fish, meat, vegetables | planks, fuel, bricks, cement | 1.0 |
| 1 | beverages, clothes, tinned_food | furniture, machines, tools | 0.5 |
| 2 | none | vehicles | 0.25 |

## Starting cargo in new towns

A new town starts with one commercial and one industrial cargo. In a 34-town game started in 1900, every town got tier 0 cargo, spread almost evenly (11 / 12 / 11 commercial, 11 / 11 / 12 industrial). The map editor's Town Builder allows any cargo, so editor-made maps can start towns on tier 1 or vehicles.

## Ids from the statistics lists

The statistics lists in [statistics-lists.md](statistics-lists.md) carry the cargo id in a name such as `itemsUnloaded19`. In a subarctic game (catalog save [6417707](https://mod.io/g/transportfever3/m/333151)) they gave steel 10, sheet metal 11 and chemicals 19, matched to a flatbed warehouse's window and to a ship's chemicals, and agreed with meat 7, cement 15, clothes 27, tinned food 28 and furniture 31 from the table above. **Observed**, one save series. A second game put id 29 on a purple-cube goods icon ([statistics-lists.md](statistics-lists.md)); the icons seen with 9 and 29 did not settle which cargo they are.

## The ids across economies

- **The ids are the same in every economy** (**Observed**, 599 to 604; 568 and 585 headers stop before the economy). The cargo a town record uses in one economy has the same id in all of them. What each economy leaves out of its town cargo lines up with this, see [climates-economies.md](climates-economies.md#what-each-economy-leaves-out-of-town-cargo).
- So the table above works for subarctic, tropical and dry saves too, for the cargo it lists. The other ids (about 1 to 5, 10 to 12, 17 to 19, 21 to 26, 29, 34 to 37) are the remaining cargo (coal, steel, grain and so on). Steel 10, sheet metal 11 and chemicals 19 come from the statistics lists (above). Which of the rest is which is **Open**. A few of them turn up in town records in every economy in small numbers, which is not explained.
- **Observed** on 604 (three saves): cargo names are in the save, but not as ids. The achievements state's `cargoTypesDelivered` is a table from 1, 2, 3 and so on to a cargo resource path (`::/cargos/wool/wool.cargo`). The numbering is the order the cargo was first delivered in that game, not the town-record id: it holds 28, 29 and 18 entries in three saves, and fish is 4, 2 and 1. Two saves of one game agree. So it gives the list of cargo a game has used, and nothing that fixes an id.
- **Observed**: the town cargo state (`game_mechanics/towns/town_cargo.gs`) has `cargoDemandsSorted`, a table from 1 to 11 of the town-record ids in this order: 6, 7, 9, 13, 14, 16, 20, 27, 28, 30, 31 (catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3), `tropic.eco`). These are the same ids as in the table above, so they match without adding new ones, and no names go with them. Beverages (8), cement (15) and bricks (33) are missing, as `tropic.eco` leaves them out.

- **Observed** on 604 (one new subarctic game): stone is id 24. A quarry's `itemsProduced24` matched its window's Produced bars, and the cement plant's `itemsConsumed24` (36 and 28) fed its `itemsProduced15` (18 and 14), so the plant makes 1 cement from 2 stone in these figures.
