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
- So the table above works for subarctic, tropical and dry saves too, for the cargo it lists. The other ids (about 1 to 5, 10 to 12, 17 to 19, 21 to 26, 29, 34 to 37) are the remaining cargo (coal, steel, grain and so on). Steel 10, sheet metal 11 and chemicals 19 come from the statistics lists (above). The rest follow from the cargo list, see [the last section](#the-id-is-the-position-in-the-cargo-list), where the steel and sheet metal pair is in doubt and a cargo mod shifts the ids. A few of them turn up in town records in every economy in small numbers, which is not explained.
- **Observed** on 604 (three saves): cargo names are in the save, but not as ids. The achievements state's `cargoTypesDelivered` is a table from 1, 2, 3 and so on to a cargo resource path (`::/cargos/wool/wool.cargo`). The numbering is the order the cargo was first delivered in that game, not the town-record id: it holds 28, 29 and 18 entries in three saves, and fish is 4, 2 and 1. Two saves of one game agree. So it gives the list of cargo a game has used, and nothing that fixes an id.
- **Observed**: the town cargo state (`game_mechanics/towns/town_cargo.gs`) has `cargoDemandsSorted`, a table from 1 to 11 of the town-record ids in this order: 6, 7, 9, 13, 14, 16, 20, 27, 28, 30, 31 (catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3), `tropic.eco`). These are the same ids as in the table above, so they match without adding new ones, and no names go with them. Beverages (8), cement (15) and bricks (33) are missing, as `tropic.eco` leaves them out.

- **Observed** on 604 (one new subarctic game): stone is id 24. A quarry's `itemsProduced24` matched its window's Produced bars, and the cement plant's `itemsConsumed24` (36 and 28) fed its `itemsProduced15` (18 and 14), so the plant makes 1 cement from 2 stone in these figures.

## The id is the position in the cargo list

**Observed**, 604 (a base-only save and one with a cargo mod; the id table also checked against 244 catalog summaries, 568 to 604). A save has a list of the game's cargo near the start of the stream, and a cargo's id is its position in that list, counting from 0. The list is sorted by the `order` value in each cargo's file (`cargos/<name>.zip`, `<name>/<name>.cargo.lua` in the install, 604 build), which runs 0 for passengers, 10 for grain and so on up to 360 for tires. In a game with only base cargo the id is therefore `order` / 10:

| Id | Cargo | Id | Cargo | Id | Cargo |
|---|---|---|---|---|---|
| 0 | passengers | 13 | planks | 26 | fabric |
| 1 | grain | 14 | vehicles | 27 | clothes |
| 2 | dyes | 15 | cement | 28 | tinned_food |
| 3 | fertilizer | 16 | machines | 29 | plastic |
| 4 | sawdust | 17 | rubber | 30 | tools |
| 5 | sand | 18 | crude_oil | 31 | furniture |
| 6 | fish | 19 | chemicals | 32 | glass |
| 7 | meat | 20 | fuel | 33 | bricks |
| 8 | beverages | 21 | iron_ore | 34 | paper |
| 9 | vegetables | 22 | coal | 35 | books |
| 10 | sheet_metal (see Open) | 23 | clay | 36 | tires |
| 11 | steel (see Open) | 24 | stone | | |
| 12 | logs | 25 | wool | | |

**Finding the list.** **Observed** in the first and last two saves of each format version, 568 to 604, one small save per sample (10 saves), all with 37 entries. Search the stream for the `str` `cargos/passengers/passengers.cargo` (length 34, no `::/` in front; the paths with `::/` elsewhere are other tables, and a one-entry `cargos/passengers` string turns up in other places too). The list is `u32 count` and then that many entries of:

| Field | Meaning |
|---|---|
| `str` source | the id of the mod that adds the cargo, empty (a zero u32) for base cargo |
| `str` path | `cargos/<name>/<name>.cargo` |
| `u32` id | the cargo's id, equal to its position in the list from 0 |

So the u32 right after the count is passengers' empty source. The list ends at the last cargo (tires in the base game); an unrelated list of edge add-on paths follows. In a subarctic base save the list held all 37 cargo, tires and rubber included, so it is not cut down to the economy, which is why the ids are the same in every economy (above). `tf3save.cargo_entries(stream)` reads it as `(id, name, source)` and `cargo_list(stream)` as the names by id.

**Mods shift the ids.** A save with the Sugar Cane Industry mod (`kussie_sugar_industry_1`, mod.io 6417537) has a list of 41: sugarcane sits after grain, sugar after beverages, rum after sugar and molasses after fuel, each at the place its `order` gives, and each carries the mod's id in its source field. Every base cargo after an inserted one moves up, so in that game fish is 7, vegetables 12 and bricks 37. The towns of that save ([6436164](https://mod.io/g/transportfever3/m/222222)) check it: their cargo ids 7, 8 and 12 (commercial) and 16, 23 and 37 (industrial) are fish, meat and vegetables, then planks, fuel and bricks, exactly the tier 0 cargo. Read with the base table they would be meat, beverages, logs, machines, clay and nothing. So **a cargo id means nothing without that save's own list**. The table above and `KNOWN_IDS` in `tools/tf3save.py` are right for base-only games and wrong for a game with a cargo mod. The `mine_saves.py` summaries from schema version 3 name town cargo from each save's list and carry it as `cargo_list` and `cargo_from_mods`; version 2 used the base table, and only for temperate economies. The ids called unknown above in modded maps may be shifted known ones; a rebuild of the catalog summaries shows which.

**Evidence for the order rule in base games**:

- Of the 19 ids settled earlier by other means, 17 equal `order` / 10; the other two are steel and sheet metal (below).
- Id 29 sat on a purple-cube goods icon in a second game (above); plastic is `order` 290.
- Town records in the 244 catalog summaries with a known economy used these ids 379 times, and 376 fall in an economy that has the named cargo. Ids 34 (paper) and 35 (books) turn up only in subarctic and all-industries games, 36 (tires) in a tropical one. The three misfits are one town each, in an editor map, in a map with 45 mods, and in the sugar mod map above (where the base table does not apply).
- `cargoDemandsSorted` (above) lists its ids in rising order.

**Open**:

- **Steel and sheet metal.** In the list, sheet metal (`order` 100) comes before steel (110), so sheet metal is 10 and steel is 11. That is the other way round from the statistics-lists reading above, a flatbed warehouse window (steel 411 and sheet metal 420). The list is the stronger evidence, but neither was tested in the game. A game's steel mill makes 3 steel for 4 sheet metal, so its `itemsProduced10` against `itemsProduced11` would settle it. A subarctic save with a steel mill had no `itemsProduced` list for either id, so it did not.
- **Ties and mods with equal `order`.** Where two cargo share an `order` value the list position is not known.
- **The statistics lists in a mod game.** The list stores each id, and the town records of the one mod game agree with it. The ids in `itemsUnloaded<id>` and `itemsProduced<id>` of a mod game were not read.
