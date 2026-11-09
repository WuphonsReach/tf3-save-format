# Industry records: the construction record, deleted industries and stacked copies

Each industry has a construction record in the save. This note gives its layout, the test that tells an industry deleted in the map editor from a live one (the record and the industry's model instances stay), and the older copies of a record an editor rebuild can leave at one spot. What an industry produces and stocks is in [industries.md](industries.md); the free-id list the test uses is in [town-leftovers.md](town-leftovers.md#the-free-id-list-marks-most-dead-towns).

## In short

- **Each industry has a construction record: its `.con` path, its params, its transform, an `i64` and seven lists of entity ids (Observed, 568 to 605).** In eight played catalog saves and three editor saves the records matched the industries' main model instances one for one, at the same position (one save had one instance more).
- **An industry deleted in the map editor keeps its construction record and all its model instances, but every entity id its record lists goes into the free-id list (Observed, 605, four industries in one editor map over three saves).** No live industry had any of its ids free, and the records left that way were exactly the ones missing from the game's Towns / Industries export. Catalog editor maps (601 to 605) show the same pattern: 30 of 263 hold such records, 286 in all. `industry_counts.py`, `industry_compass.py` and the summary leave these industries out.
- **Some editor maps hold several records at one industry's spot, each with its own main instance (Observed, 601 to 605, three catalog maps in detail).** One record is live; the others have their first ids free and share the rest with it, so they look like older copies left each time the industry lost a field. The tools still count each copy (**Open:** whether the game sees one industry).
- **Played saves mostly pass the test; 9 of 311 hold such records, most with no main instance left (Observed, 604 and 605).** One save's free-id list holds nearly its whole road network, and there the test wrongly marks every industry deleted (no guard yet).
- **Open:** whether a deleted industry's record and instances ever leave the save (a load and re-save, or a slot needed again), whether industries that close in play leave their record (27 played records without an instance suggest so), what the `i64` is, and what most of the listed ids are (the first list holds a node of the industry's road).

## The construction record

**Observed**, 568 to 605: read in detail in three editor saves of one map (605) and eight played catalog saves (568, 585, 601, 604, 605), and read without a failure in 436 editor maps (309 catalog maps, 601 to 605, and 127 of ours). The other constructions have records of the same start ([warehouses.md](warehouses.md#the-construction-record), [construction-scripts.md](construction-scripts.md)).

```
str        path       industries/<key>/<key>.con
table      params     a Lua table body (u32 pair count, then the pairs; docs/lua-values.md)
f32 x 16   transform  floats 3, 7 and 11 are 0, float 15 is 1; x, y, z in floats 12 to 14
i64        ?          0 in the editor saves, other values in played ones
vec<u32>   x 6        entity ids
vec<u32>              entity ids
```

- **Finding it.** Search for `industries/` paths that end in `.con` and have their own length as a `u32` before them, then read the rest. The path is stored without the `::/` the Towns export writes. `read_industry_constructions` in [industry_compass.py](../tools/industry_compass.py) does this.
- **The params** seen: `seed`, `sizeFactor`, `year`, `productionLevel` or `inputEnabled`, `modules` (a farm's or forest's fields and buildings), and in some records `boostFactor`, `industrySize`, `upgrade`, `constructOpt56` and `constructOpt78`.
- **The transform's translation is where the industry stands:** the main model instance (`<key>_sm.mdl`, [models.md](models.md)) sat at the same x and y, and the Towns export's `position` is the same point, rounded.
- **The id lists** (the three editor saves). In every land industry the first, second, fourth and fifth lists held one id each and the third and sixth none; the first is an end node of the industry's own road (21 of 21 live records in one save). The oil platform had no road node: its first two lists were empty and its fourth held two ids. The seventh list starts with the fifth list's id and then the fourth's, and is longer: two more than the record's `modules` in most editor records. What the other ids are is **Open**.

## Deleted industries

**Observed**, 605, one Gigantomaniac dry editor map ([test-games.md](test-games.md#giga-dry-editor-map-wr26b)), four industries deleted in the editor and read in three saves; the same pattern in catalog editor maps (601 to 605) whose deletes we did not see.

- **What stays.** The construction record, unchanged byte for byte, and every model instance the industry had: 69 for a farm, 34 for a forest, the main model among them. They stayed through three manual saves and about an hour of editing. The names table keeps the industry's two name entries too ([entity-name-edits.md](entity-name-edits.md#new-and-deleted-industries-605)).
- **What goes.** Every entity id the record lists joins the free-id list ([town-leftovers.md](town-leftovers.md#the-free-id-list-marks-most-dead-towns)). The industry's road leaves the edge table with a later road edit, as other deleted roads do ([editor-saves-tests.md](editor-saves-tests.md#a-delete-reaches-the-edge-table-with-the-next-new-road)).
- **The test.** An industry is deleted when its record lists ids and all of them are in the free-id list. In each save this left exactly the industries of the game's Towns / Industries export (22 of 24, then 22 of 26). `industry_compass.dead_industries` applies it, and `industry_counts.py` drops one main instance within 1 m of each deleted record. A save without a readable free-id list has nothing dropped.
- **Other editor maps.** Of the 263 catalog maps with industry records, 30 held records whose ids were all free (286 of 16,526 records). In four, every industry record was such a record, and in the one checked (mod.io 6440150, 54 records) all 147 industry road edges had both end nodes free too, with no live industry road left: the author had deleted every industry. None of these records shared its spot with a live one. Of our own editor maps only this series had any.
- **Played games (604 and 605).** Of 311 played catalog saves with industry records (568 to 605), 9 held records whose ids were all free, 49 of 20,528 records. 27 of them had no main instance left at their spot: the industry was gone and only its record stayed, which would fit a closure in play (not checked; **Open**). These do not change the count. The other 22 still had their main instance, and the count now leaves them out: 15 in one odd save (below), 7 in three others (mod.io 6423816, 6435288, 6448903), where whether they are editor deletes carried into play is **Open**.
- **A free-id list that does not fit (604, one save).** In mod.io 6443471 (604, start year 2020, dated 1 January 2026, `isMapEditor` false but money 0, counter 0 and no vehicles, as in an editor save; 189 mods) the list `read_free_ids` finds holds 1,585 of the 1,621 road nodes, every town road among them, so either it is not the free-id list or the save is unusual. The test marks all 15 industries there as deleted, and the count reads 0 where 15 stand. The tools have no guard for this yet.
- Whether the record and instances ever leave (after a load and re-save, or when the game needs the slots) is **Open**.

## Stacked records at one spot

**Observed**, 601 to 605, catalog editor maps: 30 of 263 hold a record with some, not all, of its ids free.

- **Copies beside a live record.** In three maps read in detail (mod.io 6417518, 6421079, 6440345) such records stood at the spot of one live record of the same industry, up to eight of them (farms mostly). In all 25 the ids of the first two lists (the first is the road node) were free, and every id not free was one the live record also lists. Each copy had a main instance of its own at the spot, so 6417518 has 68 main instances on 52 industry spots. They look like the older records of an industry rebuilt in the editor.
- **One field fewer each time.** In 6417518 the copies differ from the live record only in their `modules`, all `field.module`. A farm at (-5394, 19262) has a live record with 12 fields and eight copies with 13 to 20, one of each; the 20-field copy alone has `i64` 0 and no `upgrade` key, so it looks like the farm as placed. A second farm has a live record with 8 fields and copies with 9 to 14, and a forest one with 4 and a copy with 7. Only 27 farm pieces stood within 300 m of the first farm, so the copies keep their main instance but few other pieces.
- **What the ids say.** An industry's fields come and go: a road, track or building laid across a field removes it, and depending on how the industry is coded the field can grow back (the user, in play; see also [editor-saves.md](editor-saves.md)). In 6417518 only losses show: a copy's free ids are its two road-node ids and the ids of the fields it has beyond the live record, and the live record lists no field the copies lack. Each copy has road-node ids of its own, so each loss came with a new road node. So each loss of a field seems to have written a new record and left the old one, with its main instance. Whether regrown fields do the same is **Open**. The `i64` is 194800 in every record there but the oldest, so it does not date the copies, and the records' order in the file is not their age.
- **Played saves differ (604 and 605).** 13 of 311 played catalog saves hold records with some ids free. In two read (mod.io 6432410, 6445442) these came in pairs at one spot with the same `i64`: one record with the fields and one with no `modules` and 4 to 6 ids, without a second main instance. What the second record is is **Open**.
- **The count.** `industry_counts.py` counts each copy's main instance, as before. Whether the game shows one industry there is **Open**; the Towns / Industries export of such a map would settle it.
- **Lone records with some ids free** (no live record at the spot; 6437064, 6437799) are counted as live. What they are is **Open**.

## Evidence and tests

### Deleted industries in the Giga dry editor map (605)

The [Giga dry editor map](test-games.md#giga-dry-editor-map-wr26b), its three manual saves `1336`, `1359` and `1439` (what changed in each is listed there). A farm at (2240, 23208) and a forest at (7020, 21688) were deleted before `1336`, and the farms at (4332, -1220) and (5652, 13308) between `1359` and `1439`. The game's view of them came from its Towns / Industries export after each save, the editor's Industries count (22 in `1359`) and the Main Connections log, which named 22 industries and none of the four.

| Save | Records | Ids all free | Main instances | Export |
|---|---|---|---|---|
| `1336` | 24 | the farm and forest deleted first | 24 | empty (below) |
| `1359` | 24 | the same two | 24 | 22 |
| `1439` | 26 | all four | 26 | 22 |

- The live records and the export's industries matched one for one by key and position in `1359` and `1439`. No live record had any id free, and each deleted one had all of its ids free: 9 or 8 per record.
- The two farms deleted between `1359` and `1439` show the change: in `1359` none of their ids were free; in `1439` all were. Their records were byte for byte the same in both saves, and every record was the same in `1336` and `1359`.
- The deleted industries' model instances stayed in all three saves: 69 within 400 m of each farm and 34 of the forest, the same counts each time. Their slots moved only because instances were added before them.
- Their `ind_*` road edges (3 each in `1336`) went as other roads were edited: 0 and 2 were left of the first two in `1359`, and 2 and 0 of the other two in `1439`. In `1336` the first farm's three edges and one of the forest's already had an end node in the free-id list.
- `industry_counts.py` gave 24, 24 and 26 before the test and 22, 22 and 22 with it. `mine-summary` gives the same.
- **The `1336` export listed no industries,** though the save had the 22 live ones and the export was made straight after saving. The records did not change between `1336` and `1359`, so the save does not show why. **Open.**
- Eight played catalog saves had no record failing the test, and their main instances all stood on a record (one save had one main instance more than records): mod.io 6105772 (568), 6204931 (585), 6444225 (601), 6437663, 6433459, 6448530 (604), 6495445 and 6495910 (605).
