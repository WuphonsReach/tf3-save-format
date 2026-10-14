# Building stocks

A town's cargo is stored twice. The town record ([town-records.md](town-records.md)) holds the picks the town asks for. Each existing building has stock records of its own with the cargo it actually takes. Changing the first does not change the second. Checked on 604, editor saves (an 18-town giant map of ours and its re-saves), catalog save [6430076](https://mod.io/g/transportfever3/m/gigantomanisch-fjpjcl8aod-start-bearbeitet) (day 1 of 1900) and one played save.

## The symptom

**Observed**, one editor map. Its town records were patched in place (tier 1 and `vehicles` picks moved to tier 0 cargo; ids and weights only, same stream length). In the editor, the Editor tab and the Towns export showed the new picks. The Towns table (supply, demand, coverage columns) and a commercial building's window still showed the old cargo (an input stock of `tinned_food`, 0 of 1). Scanning the patched save and the autosaves written after loading it found the new ids in the record and no leftover old-cargo `(u32 id, f32 weight)` pair anywhere else. The `town_cargo` and `town` script states are empty in editor saves, so the old picks are not kept in a town-level table.

The save before the patch and the patched one had the same number of building stock records for every cargo, which is the same finding without the editor: **Confirmed** on 604 (one map), the record patch did not touch the stocks.

## What the API says

`api/tealdef/api/cmd.d.tl` has `makeTownUpdateCargoNeedsCmd(entity, cargoNeeds, updateTownBuildings)`: the town's per-district needs (residential, commercial, industrial) are replaced, and the third argument says whether all buildings are updated at once. The `Stock` and `StockList` records are in `api/tealdef/api/engine.d.tl`. A stock holds `cargoType`, `capacity` and `loadSpeedModifier` among others, and a stock list also holds rules with a `consumptionFactor`. The Editor tab behaves like that command with the flag set (**Observed**: after a pick is changed there, the building windows show the new cargo).

## The stock record

**Observed** on 604 in four saves. Find it by pattern (the stock lists sit together in one run of entity data, about 30% into a 400 MB stream here; do not use an offset):

```
00 00 00 00   u32 0
00 00 80 3f   f32 1.0       (probably loadSpeedModifier)
01 00 00 00   u32 1
<id u32>      cargo id, a position in the save's own cargo list (cargo-ids.md)
00 00 00 00
<cap u32>     capacity
00 00 00 00
```

- **Two matches per building.** Matches alternate: a constant 37-byte block whose id and capacity read 1 and 1 (the same bytes in all 600 of the giant map and all 2,446 of 6430076; what it is is **Open**), then the building's cargo block 37 bytes later, and the next building's constant block 82 bytes after that. The cargo blocks are therefore 119 bytes apart, back to back. The giant map had 600 and 599 of them, one contiguous run; 6430076 had 2,446 cargo blocks.
- **Inside the cargo block** (offsets from the start of the pattern) the id sits at +12, the capacity at +20, and the capacity is repeated as a byte at +73 (equal in all 599, 2,446 and 1,386 cargo blocks of the three saves that were checked; the played save's other matches are not all buildings). Bytes that vary between records are only +12, +20, +73 and a float at +77 to +80; everything else in the 82 bytes was the same in every record of the giant map and 6430076.
- **Capacity** was 1 or 2 in 575 of 599 giant-map blocks, 3 or 4 in 24. The building window showed stock 0 of 1 with 3 customers and 0 of 2 with 6 customers, so capacity follows the building's size, but where the customer count is stored was not found (**Open**).
- **The float at +77** was 1.2 in 507 of 599 giant-map blocks and in all 2,446 of 6430076. The rest were 0.6 (87), 0.3 (3) and 0.9 (2). It is 1.2 in every record whose cargo is tier 0 (`fish`, `meat`, `vegetables`, `planks`, `fuel`, `bricks`); `clothes` had 49 at 1.2 and 64 at 0.6 and `vehicles` 10 at 0.6 and 3 at 0.3. It is not a function of the cargo alone: the nine `vehicles` blocks of one town held 0.6 six times and 0.3 three times. Probably a consumption factor scaled by something per building; **Open**.
- **Buildings and stock lists.** The building record's `b` field ([town-buildings.md](town-buildings.md#the-record-and-how-to-list-it)) is a stock list entity or 0xffffffff. The same map had 566 building records with `b` set (found by the pattern there; the scan may miss some) against 599 cargo blocks, so the counts are close but not reconciled (**Open**). The stock record holds no entity id in its 82 bytes, so a stock record is not tied to its building by an id; its town is found by run and count ([below](#which-blocks-belong-to-which-town-604)).

## Changing one town in the Editor tab

**Observed**, one town of 15 buildings. Save A was the map re-saved unchanged; save B had only that town's commercial pick changed in its Editor tab (to `meat`). Both streams have the same count of matches (1,199), and comparing them in stream order gives exactly 15 differing blocks: 6 commercial (`tinned_food` to `meat`) and 9 industrial (`vehicles` to `planks`), which is the town's 15 stock-bearing buildings. In those blocks the id (+12) changed in all 15, the capacity and its copy (+20, +73) went from 1 to 2 in 11 and the float went to 1.2 in 10 (from 0.6 in 7 and 0.3 in 3).

The town's record in A already named `vegetables` (commercial) and `planks` (industrial), the values the record patch had written, while its buildings carried `tinned_food` and `vehicles`. In B the record's commercial pick was `meat` and its industrial pick unchanged, yet the industrial buildings also changed, from `vehicles` to `planks`. So the command brought every building of the town into line with the town's whole need list, not only the pick that was edited (**Observed**, one town), and a record that was patched without it stays out of line.

## Which blocks belong to which town (604)

**Observed**, an 18-town giant temperate editor map and four re-saves, each changing the cargo of one or a few towns in their Editor tabs (the 1900 start, 599 cargo blocks, 1,173 building records found by the pattern in [town-buildings.md](town-buildings.md#the-record-and-how-to-list-it)).

- **A town's blocks sit together.** The save after a single-town edit differed from the one before in one unbroken run of cargo blocks (counted in block order, starting at 0): 93 in a row for the large town (52 commercial and 41 industrial blocks changed, no unchanged block inside), and 19 in a row for a small one (13 and 6). A third town, whose commercial pick only was edited, showed 59 changed blocks spread over a run of 95, with its unchanged industrial blocks between them. An edit of two towns at once gave one run of 95 and one split run (below), and an edit of 10 towns at once gave a dozen runs of 2 to 46.
- **A run is as long as the town's count of records with `b` equal to `a`.** Counting the building records by their `town` field, the town with 93 such records, the one with 95 and the one with 19 are the three whose edits gave runs of 93, 95 and 19. So `b` equal to `a` marks a building with a cargo block, and the town field in the building record names the same town as the run (**Observed**, three towns). In all, 600 records had `b` equal to `a` and the stream held 599 cargo blocks and 600 constant blocks; the missing block was not found.
- **That holds for every zone.** Reading each record's zone from its construction path ([building-construction-paths.md](building-construction-paths.md)), `b` equal to `a` was set on 247 of 573 residential, 190 of 329 commercial and 163 of 271 industrial records, so a house can have a block and a shop or factory can lack one. What decides it is **Open**.
- **A town can be in more than one run.** The nine `vehicles` blocks of one town were one block in front of the 19-block run of another town and eight behind it, with that town's 19 blocks in between. The runs follow when the buildings were made, not the town as a whole, so a town that was grown in two steps has two.
- **A deleted building keeps its block.** After the player bulldozed one industrial plot (3 by 4 parcels, see [parcels.md](parcels.md#deleting-a-building-604)), all 599 cargo blocks (the 82 bytes of each) and every field of all 1,173 building records were unchanged, so a run probably counts the buildings the town ever had, not only those standing (**Observed**, 604, one deletion; the inference is not tested).
- **The order inside a run is not found.** Sorting a town's records by the first id `a`, the second id `b`, `d`, the position in the record table, `timeBuilt`, the first or last parcel or the height gave neither the zone pattern nor the capacity pattern of the blocks (the 93 blocks of the large town against its 93 records, a Pearson correlation under 0.3 for the capacity against parcels, depth, level and height under every order). The record table itself is in `timeBuilt` order and alternates between towns, so the block order is not the table order. A block can therefore be tied to its town, but not yet to its building.

## Method pitfalls

Do not diff a manual editor save against another by offset. A manual editor save re-serialises a large entity region (about 62 MB to 326 MB into the stream here) with shifting offsets, though only one town changed: A and B differ in length by 27,185 bytes. Two autosaves from one session differ by 440 bytes at equal length. Count `(id, capacity)` pairs over the whole stream and pair the matches in stream order.

## Open

- What the constant block is, what the float measures and where a building's customer count is kept.
- The order of the blocks inside a town's run, the reason a record has `b` equal to `a` or not, and the 600th block (see above).
- **Observed** (604, play in the map editor and a game, not checked in a save): changing a town's cargo in its Editor tab changed all of that town's existing buildings, which agrees with the save diff in [Changing one town in the Editor tab](#changing-one-town-in-the-editor-tab). Buildings built afterwards followed the town's picks to an extent not known, and no building asked for a cargo that was not on the town's label. A town's label grows as it levels up ([cargo-ids.md](cargo-ids.md#how-the-game-adds-cargo-to-a-town); a record with a second commercial cargo is in [town-records.md](town-records.md)).
- Still **Open**: the exact rule for new buildings, whether picking the cargo the record already holds triggers the building update, whether the game repairs a building that disagrees with its town on load or on a level change, and how stock capacity follows level and cargo weight: not tested in a save.
- Residential buildings: no pick was changed, so none were looked at.
- The Towns table's per-town demand figure was not rebuilt from the stocks.
