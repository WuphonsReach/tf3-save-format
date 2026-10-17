# Entity model

Whether the stream is a dump of the game's runtime tables, which are keyed by entity id. **Open**, 604. This note holds the evidence for and against and the test that would settle it; the facts it points to live in their own notes.

## In short

- **Question (Open, 604).** Is the stream, for the entity part, a dump of the game's component tables keyed by entity id (with a free list beside them), or a record per object? Nothing found decides it.
- **For the component reading (Observed).** The game's API declares `Parcel`, `TransportVehicle` and `EmissionGrid` records; a crash log named a component lookup on entity 0; things refer to each other by entity id; a free-id list sits near the end; edge, junction and strip tables keep rows for freed ids; no table of live entities exists.
- **A per-building list apart from the building records (Observed, one game, 111 saves).** After the parcel table a count and a run of 8-word units follow, one per building, linked to the building record by its first id. That fits data split by component and is not how a record-per-object layout looks.
- **The test that would settle it** is in the Open section: find a second component laid out like the parcel table.

## What the game's own files say (604, Observed)

- The game's API definitions (`engine.d.tl` in `api/tealdef/api/`) declare record types such as `EmissionGrid`, `TransportVehicle` and `Parcel`, each with a `new` constructor. [parcels.md](parcels.md) already ties the stored parcel table to the `Parcel` record.
- The game's crash log from a Buy Vehicles crash named a native lookup that asked for the `TransportVehicle` component of entity 0 (component type index 65) and failed, because entity 0 carried only `EmissionGrid`. The wording is that of an entity-component-system: an entity is a bare id, and each kind of data is a component attached to it. The index also says there are dozens of component types. One log, one crash; the saved game did not hold the bug (the crash save loaded and the same purchase worked).

## What the stream looks like from that side (604, Observed)

Each point is a result in its home note, not a new finding:

- Things refer to each other by entity id: parcels, edges, nodes, signals ([parcels.md](parcels.md), [signals.md](signals.md), [road-network.md](road-network.md)).
- A list of free entity ids sits near the end of the stream and is used from the front ([town-leftovers.md](town-leftovers.md#the-free-id-list-marks-most-dead-towns)).
- The edge, junction and strip tables keep rows for ids that are on the free list, so a delete does not clear every table ([town-leftovers.md](town-leftovers.md)).
- A new signal is thin: its id is in the edge record and in few other places, and one id occurs in about ten places in all ([signals.md](signals.md)).
- No table of live entities was found ([town-leftovers.md](town-leftovers.md#no-other-table-holds-the-live-ids)). A dump of per-component tables would not need one.

## Open

Whether the stream is, for the entity part, one table per component type written one after another, with the free list beside them, or a record per object. Id-keyed tables and free lists also occur in engines that are not entity-component systems, so none of the above decides it.

Test, started with the section above: take a component the API names (`Parcel` is the nearest, its table is known) and check whether the table is a contiguous run of rows sorted or ordered by entity id with no per-row type tag. Then look for a second component with the same shape (signal objects, vehicles, nodes), and for the table order against the order of the API's records. Two components laid out alike would make the per-component reading likely; none would point to a record per object.


## Evidence and tests

### A count and a per-building run follow the parcel table (604, Observed, one game)

Directly after the last parcel record there is a `u32` that equals the parcel count, then a run of 8-word units, one for each town building. The parcel table was read in 111 saves of the [Small subarctic game](test-games.md#small-subarctic-game), from the first save to the last of the parcel tests:

- **The count equals the parcel count** in 93 saves, while the parcel table grew from 2,543 to 5,522. In the last 14 saves, where the parcel table is 7,061 to 7,327, it is 62 higher (7,061 gives 7,123 and 7,327 gives 7,389), and the extra 62 does not change.
- **The run is not that long.** In four saves the run was 422, 501, 1,023 and 1,418 units against 2,543, 3,128, 5,522 and 7,327 parcels, so it follows the number of buildings, not the count in front of it. What the count counts is **Open**.
- **A unit is 8 `u32` words** and ends in the float 1.0 (`3f 80 00 00`): `w0 w1 size 1 id w5 0 1.0f`. The `id` is the first id (`a`) of a building record ([town-buildings.md](town-buildings.md#the-record-and-how-to-list-it)) for 1,329 of the 1,330 such units in the late save, and the units run in the order of the records (1,049 of 1,329 steps go to the next record; the rest are small moves). So the units are per-building data kept apart from the building records.
- **Fields.** `w0` is 0 or 1 (78 ones), `w1` is 0, 1 or 2, `size` takes 15 values from 1 to 64 (3 and 1 the most common), the word before the id is always 1, `w5` is 2 (14 times 3) and the word before the float always 0. `w0` and `w1` are not the record's flag byte or its town. `size` is not the record's depth or its parcel count. `w5` is not the record's level (3 occurs only on level 2 records). `w1` (0, 1, 2) is not the zone either: against the construction path of [town-buildings.md](building-construction-paths.md#the-zone-and-footprint-from-the-construction-path-604) it was spread over all three values for each zone (`res` 154, 33 and 36 in the first save), nor the variant number or the footprint. What `w0`, `w1` and `size` hold is **Open**.
- **Other units.** 88 units in the late save are a different shape, `2 20 0 0 2.0f 2 0 1`, with no id and no pattern in which building they stand beside (**Open**). One unit with the same shape as the building units carries an id (40,918) no building record has.
- **After the run** a different structure starts, with a short list of small numbers and a long run of one repeated town entity id.
- **No array of entity ids stands beside the parcel table.** The words just before its count are the tail of the name table and a few zeros.
- **Four saves between the two groups have no parcel table the parser accepts** (the four before the first 62-higher save). Why is not known.

This does not show a table of equal length per parcel, which an earlier reading of the equal counts suggested. The stream does keep a per-building list apart from the building records, linked by the building's first id, which is not how a record-per-object layout would look but fits data split by component. A parcel's own entity id is in neither table (see [parcels.md](parcels.md#parcel-ids-and-the-building-records)).
