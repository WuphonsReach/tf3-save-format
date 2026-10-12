# Entity model

Whether the stream is a dump of the game's runtime tables, which are keyed by entity id. **Open**, 604. This note holds the evidence for and against and the test that would settle it; the facts it points to live in their own notes.

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

## A second table follows the parcel table (604, Observed, one game)

Directly after the last parcel record there is another `u32` count, then records of a different shape. The parcel table was read in 111 saves of the [Small subarctic game](test-games.md#small-subarctic-game), from the first save to the last of the parcel tests:

- **The count equals the parcel count** in 93 saves, while the parcel table grew from 2,543 to 5,522. In the last 14 saves, where the parcel table is 7,061 to 7,327, it is 62 higher (7,061 gives 7,123 and 7,327 gives 7,389), and the extra 62 does not change.
- **The records are not parcel records.** They hold small integers, a float and, in some, one extra number in the range of the parcel ids (about 19,000 to 40,000 in the late saves). The layout is not worked out.
- **No array of entity ids stands beside the parcel table.** The words just before its count are the tail of the name table and a few zeros; the count of the second table follows the last parcel record at once.
- **Four saves between the two groups have no parcel table the parser accepts** (the four before the first 62-higher save). Why is not known.

So the stream keeps per-parcel data in two tables of equal length, written one after the other. That fits one table per component, but a parcel's own entity id is in neither (see [parcels.md](parcels.md#parcel-ids-and-the-building-records)), so the tables are addressed by position. Whether position is the link between them is not tested.

## Open

Whether the stream is, for the entity part, one table per component type written one after another, with the free list beside them, or a record per object. Id-keyed tables and free lists also occur in engines that are not entity-component systems, so none of the above decides it.

Test, started with the section above: take a component the API names (`Parcel` is the nearest, its table is known) and check whether the table is a contiguous run of rows sorted or ordered by entity id with no per-row type tag. Then look for a second component with the same shape (signal objects, vehicles, nodes), and for the table order against the order of the API's records. Two components laid out alike would make the per-component reading likely; none would point to a record per object.
