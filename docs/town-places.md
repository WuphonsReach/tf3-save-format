# Town places

How to read each town's name and put it on the map from the save alone, with no industry names, labels or street clusters. The structure it rests on is the [entity table](entity-table.md). The reader is `tools/town_places.py`. Labels are as in [README.md](README.md).

## In short

- **The tie is stored (Observed, 604 and 605, seven games, every town).** A town's entry in the entity table holds its name slot and its town record row. The building records carry the same entry's index as their `town`, and list their parcels, whose rows in the parcel table hold their corners in map metres. So: name ← town entity → buildings → parcels → place.
- **The point is the mean of the town's parcel centres (Observed).** It was 12 to 128 m from the position in the editor's Towns export, over 130 town readings in eight editor saves of four maps. That position is the midpoint of the town's first street; no record found here marks that street (**Open**).
- **Deleted and stale towns drop out (Observed).** A deleted town's entity is free, so its buildings and leftover roads name a dead id. Its name stays in a free slot of the names table and is not read. A town renamed in place keeps its id and slot.
- **It replaces the slot-run reading for towns.** `tf3save.town_names` reads the run after the company ([entity-names.md](entity-names.md#town-names-604)). That run is empty in editor maps, and in played games it can run past the towns: 16 names for 3 towns in catalog save [6433459](https://mod.io/g/transportfever3/m/5000), one too many in four sampled saves. The entity table gave the towns' own count in all of them.
- **Where it fails (Open).** A town with no building gets a name but no point. In 568 and 585 the building record pattern finds nothing, so no towns are read. One 604 catalog save of 16 had no entity table found.

## The chain

1. **Names.** Read the entity names table and its free list ([entity-table.md](entity-table.md#the-arrays-type-free-list-count)). The type id in front of the free list is the name type.
2. **Entities.** Find and read the entity table ([entity-table.md](entity-table.md#layout)).
3. **Buildings.** List the building records by pattern ([town-buildings.md](town-buildings.md#the-record-and-how-to-list-it)). Their `town` values that are live entities with a name pair are towns.
4. **The town type.** It is the type all those entities share, apart from the name type, that the fewest entities carry (11 in a map of 11 towns, against 7,181 and 205,867 for the other two shared types). Every entity with that type is a town, built on or not. Its slot is the town record's row ([town-records.md](town-records.md)), so the record's capacities and cargo go with the name.
5. **Parcels.** A building's parcel ids are entities with one pair; its type is the parcel type and its slot, with the top bit masked, the parcel's row in the parcel table ([parcels.md](parcels.md)). The centre of a parcel's first face (the street-side cell) is its point.
6. **The town's point** is the mean of its buildings' parcel points. `town_places.py` prints it with the largest distance from it to a parcel (220 to 740 m in these saves), and `--export towns-export.lua` adds the distance to the export's position for the same name.

## What the point is and is not

- The editor's export gives a town's position as the midpoint of an 88 m `town_old_small` edge (all 11 towns of a fresh generated editor map, within 0.04 m). Later edits can split that edge; the point then lies on a shorter piece.
- **Nothing found marks that edge (Observed, two saves).** It is not first in the edge table, not the edge with the lowest or highest node ids, not the edge of the town's first parcel row (60 to 250 m off), and not the edge whose midpoint is nearest the street nodes' mean (right for 9 and 7 towns of 11 in two saves, 60 to 140 m off for the rest). The town entry's other two types (0 and 10 in [entity-table.md](entity-table.md#component-types-seen)) were not followed to a position, and no `f32` or `f64` pair of the export's position is in the stream.
- So the parcel mean is a label point, not the game's centre. The mean of the town's street nodes (17 to 75 m from the export in one map) is about as good, but needs the streets tied to the town first, which the parcels give (each parcel names its street edge).

## Evidence and tests

All 2026-11-08.

- **Gigantomaniac dry editor map (Observed, 605, seed `V7Jv2KYnbU`, our own):** a fresh save with 11 generated towns, one after renaming them (same ids and slots, new names), one after six were deleted and placed again (11 live towns, three at recycled ids, six dead ids still named by 457 buildings), and one after industries and main roads. The three exported stages matched their exports by name, record capacities and cargo, at 22 to 76 m; the renamed stage (no export) kept every id and slot under the new names.
- **Giant subarctic editor map (Observed, 604, ours, the map of [town-leftovers.md](town-leftovers.md)):** two pruned stages, 31 and 25 towns. All named as in their exports, the four renamed in place included (same id, new name), and the two towns added by hand at fresh ids and late name slots (145 and 574); 27 to 103 m.
- **Gigantomaniac temperate (18 towns) and Gigantomaniac subarctic (11 and 12 towns) editor maps (Observed, 604, ours):** all named as in the exports, 12 to 128 m.
- **A played game (Observed, 604, the [Small subarctic game](test-games.md#small-subarctic-game)):** the three towns at the ids [town-boundaries.md](town-boundaries.md) gives, with their names; no export to measure against.
- **Catalog saves (Observed, 568 to 605):** 15 of 16 sampled saves of 601 to 605 gave every town a name and a point once zero-face parcels were allowed ([parcels.md](parcels.md#the-parcel-table-604)); the `town_names` run agreed where it was not one name long. A hand-built catalog map with 16 towns at scattered name slots read the same way. In one save each of 568 and 585 the entity table was found but no building record, so no town. The one save without an entity table is in [entity-table.md](entity-table.md#evidence-and-tests).
- **Not yet checked:** the four towns whose centres were measured on screen ([town-centre.md](town-centre.md)), and a town with no buildings.
