# Entity table

The table that says which components each entity has and where each component's data sits. An entity's id is its position in this table, and each of its entries names a component type and a slot, the row of that component's own array. It turns an entity id into its name, its town record, its parcel rows or its street-edge row. What it ties for towns is in [town-places.md](town-places.md). Labels are as in [README.md](README.md).

## In short

- **One table, one entry per entity id (Observed, 568 to 605).** `u32 n`, then n entries, then `u32 n` again. An entry is `u32 k` and k pairs `(u32 type, u32 slot)`. The id is the entry's index: the town ids that building records carry are the indexes of the town entries (Observed, seven games, every live town), and the line and vehicle ids of notifications and a mod's log are the indexes of entries whose name slot holds that line's or vehicle's name (Observed, 604 and 605, two games, [line-ids.md](line-ids.md#the-entity-table-names-every-line-604-and-605)).
- **A free id is one pair `(ffffffff, ffffffff)` (Observed).** A deleted town's id reads so, while its buildings and roads stay in the save.
- **A slot is a row of that type's array (Observed).** The town slot is the town record's row, the name slot the names table's, the parcel slot the parcel table's, the edge slot the street-edge table's. Some types always set the top bit of the slot (`0x40000000`): mask it with `0x3fffffff`.
- **Type ids are numbers per save, not fixed (Observed).** The town type was 27 and the name type 16 in our 605 editor maps, 25 and 22 in a played 604 game with seven mods. Read them from the arrays, not from a list.
- **The arrays keep free lists (Observed).** The names table and the town array start with their type id and a `vec<u32>` of free slots; a free slot keeps its old contents.
- **Open.** Most type ids, the arrays of the types that carry a position, the trailer in the one catalog save where the table was not found, and whether the layout holds before 568.

## Layout

```
u32  n
n x
  u32  k                    pairs in this entry
  k x (u32 type, u32 slot)  a component type and its row in that type's array
u32  n                      the same count again
u32  1, 1, 0, 1, 1, 0, 1    what followed in every save where the table was found
```

- **Where it is (Observed).** 97 to 98 % of the way into the stream, about 1 to 4 MB before its end, ahead of the free-id list of [town-leftovers.md](town-leftovers.md). It is 10 MB for 320,312 entities on a Gigantomaniac editor map and 2 MB for 63,712 in a Small played game.
- **To find it,** search the last eighth of the stream for a `u32` followed by `01 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00`, take that `u32` as n, and look back for an earlier `u32` n from which n entries parse and end exactly at it. An entry parses when k is 1 to 300 and its types are distinct and small (under 4,096) or all ones. `tools/town_places.py` (`find_entity_table`) does this in under two seconds. The backward step must not walk entry by entry: entries vary in size, and a walk from a known entry took a wrong step within 700 entries.
- **Free ids.** A free entry is `1, (ffffffff, ffffffff)`: 81,343 of 319,657 in a fresh editor map. The free-id list near the end of the stream ([town-leftovers.md](town-leftovers.md)) holds such ids, but not only them: ids are reused, and a town id in that list can be live again.
- **No id is stored.** Nothing in an entry repeats its index, and a town's id occurs as a `u32` only in the building records: none of the eleven town ids of a fresh editor map appeared anywhere else as a whole word (one appeared once, inside an unrelated string). Earlier searches for an entity's id next to its name or record ([entity-names.md](entity-names.md), [line-ids.md](line-ids.md)) failed for that reason.

## Component types seen

Numbers from one fresh 605 editor map (11 towns, 753 street edges, 617 nodes, 14,915 parcels, 7,664 live names); the meaning comes from the slot's array.

| Type there | Entities | What the slot is |
|---|---|---|
| 16 | 7,664 | Row of the entity names table ([entity-names.md](entity-names.md)) |
| 27 | 11 | Row of the town array ([town-records.md](town-records.md)) |
| 29, 30, 31 | 753 each | Street edge: 29 is the row of the street-edge table ([road-network.md](road-network.md)) |
| 28, 32 | 617 each | Street node |
| 34 | 14,915 | Row of the parcel table ([parcels.md](parcels.md)), flag bit set |
| 35 to 38 | 2,440 | Town building |
| 0 | 205,867 | Almost every entity; its array was not found |
| 10 | 7,181 | Towns, edges, some buildings and named entities; an array holding statistic names (`townResidentialCount`, `roadTotalLength`) has this type and count |

- A town entry had four pairs in every save read: town, name, and the types numbered 0 and 10 in the table above.
- A line's entry had six pairs, one of them of a type that only lines carried, in a 604 and a 605 game; vehicles carried 8 to 10 types ([line-ids.md](line-ids.md#the-entity-table-names-every-line-604-and-605)).
- In the played game (seven mods, 604) the three towns were `{25: record, 22: name, 0, 10, 54}`, the company just before them with the name slot 0, and the parcel type was 45 in a 605 catalog save. So the numbers move with the game's contents.

## The arrays: type, free list, count

Two arrays were read with the table and start the same way (**Observed**, 604 and 605):

```
u32       type       the component type id the table uses for it
vec<u32>  free       free slots
u32       n          rows, free ones included
n x       row
```

- The **names table** ([entity-names.md](entity-names.md)): type 16 in our editor maps (22 in the played game), 16 free slots in a fresh editor map, 3,264 after six towns were deleted and placed again. A free slot keeps the name its last owner had, so a deleted town's name stays readable.
- The **town array**: its header has one more word in front, and a deleted town's row stays in it, on the free list; the values are in [town-records.md](town-records.md#table-header).
- The free list is found by walking back from n to the longest `vec<u32>` that ends there and holds only distinct slots below n; a shorter one can match by chance (148 and 174 did, before the right 3,264).

## Evidence and tests

- **The table and the town ids (Observed, 605, our Gigantomaniac dry editor map, seed `V7Jv2KYnbU`).** In the fresh save of 11 generated towns the table held 319,657 entries between two copies of that count. The 11 entries with a type-27 pair were at the indexes the building records carry as `town` (all 2,460 records), and their name and record slots gave the names and capacities the editor's Towns export lists for one another. After six towns were deleted and placed again, the 11 live towns were again the type-27 entries, three of them at recycled ids (154,682, 295,811, 296,000), the deleted towns' ids were free, and their buildings still named them.
- **More editor maps (Observed, 604):** the 34-town Giant subarctic map in two pruned stages (31 and 25 towns, with towns renamed in place and two added), an 18-town Gigantomaniac temperate map and a 12-town Gigantomaniac subarctic one. Every town in each map's Towns export was a type-town entry with that name.
- **A played game (Observed, 604, the [Small subarctic game](test-games.md#small-subarctic-game), seven mods):** 63,712 entries; the towns at ids 17,912, 17,913 and 17,914, the ids [town-boundaries.md](town-boundaries.md) had from ticked buildings.
- **Catalog saves (Observed, 2026-11-08):** found in one each of 568 ([6098954](https://mod.io/g/transportfever3/m/autosave-second-1959-12-08)) and 585 ([6204931](https://mod.io/g/transportfever3/m/empty-quarter)), and in 15 of 16 sampled saves of 601 to 605. Not found in [6459692](https://mod.io/g/transportfever3/m/harsewinkel) (604): no trailer with a plausible count. **Open**.
