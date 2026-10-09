# Cargo type ids

Checked on 604 (the town-record counts below also use 585 to 604 saves). The ids are not stored with names anywhere in the save, so the table comes from comparing town records with the game. Mods can add cargo; check the ids against a Towns export of the same save before relying on them.

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
- The statistics lists in [statistics-lists.md](statistics-lists.md) carry the cargo id in a name such as `itemsUnloaded19`. In a subarctic game (catalog save [6417707](https://mod.io/g/transportfever3/m/333151)) they gave steel 10, sheet metal 11 and chemicals 19 (matched to a flatbed warehouse's window and to a ship's chemicals), and agreed with meat 7, cement 15, clothes 27, tinned food 28 and furniture 31 from the table above. **Observed**, one save series.

## Tiers and weights

The weight stored with each cargo in a town record is the cargo's `townConsumptionFactor` from the economy:

| Tier | Commercial | Industrial | Weight |
|---|---|---|---|
| 0 | fish, meat, vegetables | planks, fuel, bricks, cement | 1.0 |
| 1 | beverages, clothes, tinned_food | furniture, machines, tools | 0.5 |
| 2 | none | vehicles | 0.25 |

## Starting cargo in new towns

A new town starts with one commercial and one industrial cargo. In a 34-town game started in 1900, every town got tier 0 cargo, spread almost evenly (11 / 12 / 11 commercial, 11 / 11 / 12 industrial). The map editor's Town Builder allows any cargo, so editor-made maps can start towns on tier 1 or vehicles.

## Climates and economies

The header names a climate and an economy (see [header.md](header.md)). They come in matched pairs, plus the all-industries economy:

| Climate | Economy | Saves and maps seen (the 244 of [versions.md](versions.md), 2026-10-09) |
|---|---|---|
| `temperate.clima` | `temperate.eco` | 151 |
| `temperate.clima` | `all.eco` | 16 |
| `subarctic.clima` | `subarctic.eco` | 36 |
| `subarctic.clima` | `all.eco` | 3 |
| `tropical.clima` | `tropic.eco` | 21 (note `tropic`, not `tropical`) |
| `tropical.clima` | `all.eco` | 2 |
| `dry.clima` | `dry.eco` | 4 |
| `mission6_tropical.clima` | `tropic.eco` | 1 |
| none (568 and 585 headers, which parse only partly) | none | 10 |

- **The ids are the same in every economy** (**Observed**, 599 to 604; 568 and 585 headers stop before the economy). The cargo a town record uses in one economy has the same id in all of them. The ids also line up with what each economy leaves out of its town cargo:
  - `subarctic.eco` has no bricks and no vegetables: its town records use 6, 7 (commercial tier 0) and 13, 15, 20 (industrial tier 0), never 9 or 33.
  - `tropic.eco` has no bricks, cement or beverages: commercial 6, 7, 9 and 27, 28 (tier 1), industrial 13, 20, never 15, 33 or 8.
  - `dry.eco` has no fish: commercial 7, 9 only (never 6), industrial 13, 20, 33.
  - `temperate.eco` has no cement: 15 never appeared in a temperate economy record, while 33 is common.
  - `all.eco` has everything, and its records used 15 and 33 both.
- Each of those economy files was read in the game install to see which cargo it removes. The ids themselves are not in those files and are not in the save: no cargo name string sits next to an id in any of the four climates' saves.
- So the table above works for subarctic, tropical and dry saves too, for the cargo it lists. The other ids (about 1 to 5, 10 to 12, 17 to 19, 21 to 26, 29, 34 to 37) are the remaining cargo (coal, steel, grain and so on). Steel 10, sheet metal 11 and chemicals 19 come from the statistics lists (above, **Observed**, one game). Which of the rest is which is **Open**; [statistics-lists.md](statistics-lists.md) records the icons seen with 9 and 29 in a second game, which did not settle them. A few of them turn up in town records in every economy in small numbers, which is not explained.
- **Observed** on 604 (three saves): cargo names are in the save, but not as ids. The achievements state's `cargoTypesDelivered` is a table from 1, 2, 3 and so on to a cargo resource path (`::/cargos/wool/wool.cargo`). The numbering is the order the cargo was first delivered in that game, not the town-record id: it holds 28, 29 and 18 entries in three saves, and fish is 4, 2 and 1. Two saves of one game agree. So it gives the list of cargo a game has used, and nothing that fixes an id.
- **Observed**: the town cargo state (`game_mechanics/towns/town_cargo.gs`) has `cargoDemandsSorted`, a table from 1 to 11 of the town-record ids in this order: 6, 7, 9, 13, 14, 16, 20, 27, 28, 30, 31 (catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3), `tropic.eco`). These are the same ids as in the table above, so they match without adding new ones, and no names go with them. Beverages (8), cement (15) and bricks (33) are missing, as `tropic.eco` leaves them out.
- What the climate changes in the save beyond this (terrain, vegetation, which industries spawn) was not looked at. **Open**.
