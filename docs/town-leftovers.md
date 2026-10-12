# Deleted towns' leftover roads

What a deleted town leaves in a save, and the one marker found for it. Background and the first test (a town deleted in the map editor) are in [road-network.md](road-network.md#deleting-the-town). Labels are as in [README.md](README.md). Everything here is **Observed**, 604, one Giant editor map of 25 live towns; no other map was checked.

## What stays after a deletion

- A town deleted by hand keeps its roads in the street-edge table, 30 to 45 nodes each. Drawing country roads over the place did not remove them. A map drawn from the table therefore shows towns the game no longer has.
- A later edit cleared some leftovers and not others: in one save step the roads of two older deleted towns, far from anything drawn, lost 47 edges, while two newer ones kept all of theirs.
- **A load and a save does not clear them.** Three runs agree: the game's autosave of a loaded save, a manual save made after loading it, and a second load and save of that. The edge tables came out identical each time. (The one difference between the first two, three edges, was a livestock farm placed on a dead town's ground between them: its model parts are absent from the earlier saves and present from then on. Its access road (`ind_entrance_old_country` and two `ind_country_old_small` edges) came in and three of the dead town's edges at that spot left, so an industry placed on the ground clears the leftovers under it.)
- What the second load and save did change: the header, a small stretch around the junction table, a large run about two fifths into the stream, and the free-id list at the end, which grew by about 12 KB (the stream by the same).

## The free-id list marks most dead towns

Join the town-type edges into clusters (edges sharing a node), one per town. The map had 33 clusters and 25 towns in the editor's Towns export, so 8 clusters had no live town. The free-id list ([road-network.md](road-network.md#the-other-tables-a-road-edit-touches)) is the long ascending run of `u32` near the end of the stream; a tool finds it as the run with the longest ascending stretch among the four 4-byte alignments of the last megabyte.

| Clusters | Node ids found in the free list |
|---|---|
| 25 matching a live town | 0 of every cluster |
| 5 dead towns | 41 of 42, 34 of 36, 31 of 31, 30 of 33, 21 of 23 |
| a dead town west of a livestock farm | 4 of 29, about what chance gives; 8 of its ids are also nodes of a later country road 20 km away |
| 2 dead towns in the far south, each partly cleaned | 18 of 44, 1 of 2 |

Of the 4,038 nodes in the table, 185 were in the list, about 180 of them in those clusters. The same five clusters showed it in the later save, so the load and save did not change it.

**The exception is probably id reuse.** In this table 14 node ids stand at two places. Eight of them are ids of the unfreed town's nodes, also used by a country road drawn later at the far side of the map. New roads take ids from the free list ([road-network.md](road-network.md#the-other-tables-a-road-edit-touches)), so those eight were freed with the town, taken by the new road, and left the list. That leaves 17 of its 29 ids unaccounted for (a guess: other new entities took them). The other six doubled ids were not checked.

**Check against the player's knowledge.** The player knew each town's place on the road network and which roads they re-drew through the old streets (they delete the grid, then join country roads through it, sometimes trimming an inbound road back first). With the town edges of the five clusters dropped, the country roads left in the circles read as the player described: a dead-end town (1 dead end, no junction), a T-town (1 junction, 3 roads in), and a town with no junction (the unfreed town too, once its edges are dropped as well). A fourth, a through town, also had a junction and two dead ends: two stubs of three edges each, which the player confirmed were deleted roads (below). The sixth circle on the map (a through road, no junction) and the far-south pair were not part of the check.

## It marks single deleted roads too

Taking the list per node, not per town: an edge with an end node in the list is a leftover. In that map 224 of 4,238 edges qualify: 216 in the dead towns, two country edges in the far south, and the two stubs of the through town (3 edges each, a dead end at each tip, each joined to the live road at its other end). Of 2,823 country-road nodes, only 7 were in the list, all in those stubs. No edge of a live town or of a live road qualified. With those edges dropped the through town's circle held one road in and one out and no junction, as the player described it. **Observed**, one map. The unfreed town's edges are not caught by this, for the reason above.

## No flag in the edge record

**Observed**, one map. The edge records of the dead edges do not differ from live ones of the same type. The `u32` after the street type is 0 in all 4,238 records. In the lane block (117 bytes after the tangents), no byte takes a value in the dead edges (188 small-town, 28 extra-small town and 8 country edges; [street types](glossary.md#street-types)) that no live edge of the type has, and no byte is the same in all dead edges and rare among live ones. So the table itself does not say which roads the game still has, and the game must take what it draws from another table: the junction table or the ground polygons ([road-network.md](road-network.md#the-other-tables-a-road-edit-touches)) are the candidates, as both followed a deletion at once. The junction table's records follow the edge table's node order only roughly, and the nodes without a matching record were not the dead ones, so that comparison gave nothing.

## The strip table keeps dead rows too

**Observed**, one map. The road-surface strip table ([road-network.md](road-network.md#the-other-tables-a-road-edit-touches)) is keyed by an edge's own entity id, and nearly all its entries pair with town edges (574 of 1,062 live town edges, one country edge). Of those 575 live-edge entries, none has its id in the free-id list. In the five dead towns, all 120 entries paired with an edge have their id in it (31 of 31, 18 of 18, 32 of 32, 11 of 11, 28 of 28). The unfreed town's edges show 9 of 21, and the two far-south clusters 7 of 24. 82 of the 574 entries that pair with no edge are in the list too. The junction table names 192 listed edge ids among its 1,307.

So the list reads as the entity ids the game no longer has, and the edge table, the strip table and the junction table all keep rows for ids that are gone. That the game draws from the entity set is a **guess**; it fits why no flag sits on any of these rows. A town's edge id and node ids together catch 14 of the unfreed town's 31 edges.

Open: whether a town's nodes enter the list at once on deletion, whether the rest of the unfreed town's ids were taken by other entities, and whether the list can stand in for the Towns export (a map filter needs a rule for towns like the unfreed one).
