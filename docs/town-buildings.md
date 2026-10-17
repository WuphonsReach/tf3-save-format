# Town buildings

The record of every building in a town (houses, shops, workplaces): its level, parcels, height, build time, owning town and the "Historic Preservation" flag, and how the records change in play. The parcels it names are in [parcels.md](parcels.md). The town's own record (capacities and cargo) is in [town-records.md](town-records.md). Checked on 604 in one game, the [Small subarctic game](test-games.md#small-subarctic-game), against the player's screenshots of the building windows.


## In short

All 604, one game (the Small subarctic game), checked against the player's screenshots of building windows.

- **Every building has one record of `41 + 4n` bytes (n = its parcels, 1 to 4), listed by a find-by-pattern scan, not by offset (Confirmed, two ticked buildings among 569 records).** It holds two entity ids, `level`, an id, a flag byte, the parcel ids, `depth`, `height`, the owning `town` and `timeBuilt`. The layout is in [The record and how to list it](#the-record-and-how-to-list-it).
- **The flag byte is "Historic Preservation" (`blockedDevelopment`, Confirmed from the API and from a one-byte diff).** Ticking a building sets that byte 0 to 1 and nothing else in the record changes; unticking reverses it. The preview of a demolition adds a "Historic Buildings Will Be Removed" line for ticked ones and the same cost and reputation figure (Observed, one stretch).
- **The `level` in the record is the number the window shows (Observed, restaurant and store).** A level 2 commercial building holds 4 fish and 2 tinned food and 16 customers, a level 1 building half of that. A level can go down and up again within minutes, and houses change level too (Observed).
- **The second id (`b`) is 0xffffffff for a building without a stock (a house) and equal to the first id for a stocked one (Observed, 1900 game); the first id is not a stable key,** so follow a building by its parcels. Whether a house gets a stock later in a game was not tested.
- **`timeBuilt` is a clock value, 0, or all ones (Observed);** what all ones means that 0 does not is Open.
- **The `town` field is the owning town (Confirmed, two buildings),** but the records hold no position, and the buildings a player ticks along one street do not sit together in the table or share a `town` value (Open why).
- **Open:** what `a`, `b` and `d` point to, what the three small entries near the end of the stream record when a flag changes, and whether the actual demolition costs or loses more with the flag on.

## The building record and "Historic Preservation" (604)

**Observed** on 604 in the Small subarctic game, saves `1427` (clock 11,239,800), `1428` and `1429` (both 11,324,600), with the player's screenshots of a commercial building in the catchment of the port.

### The record and how to list it

- **The window.** A commercial building's window showed a first row of its level (1), the supply of each cargo it takes (fish 100% or 83%, tinned food 0%) and the year (1900), then "Input Stocks" (fish 2 of 2, tinned food 0 of 1), "Customers" (6 of 6, then 5 of 6 at the later look) and a "Historic Preservation" checkbox, whose tooltip reads that it keeps the building's appearance but it can still level up. The player ticked it between `1427` and `1428`.
- **What the game's API says it is.** The `TownBuilding` component (`api/engine.d.tl`) holds `personCapacity`, `stockList` and `construction` (entities), `level` (1 to 4), `parcels` (entities), `depth` (1 to 4), `height`, `town` (entity), `timeBuilt` (clock) and `blockedDevelopment` (boolean, "block town developer from changing this building"). The command that the checkbox runs, `makeTownBuildingSetBlockedDevelopmentCmd` (`api/cmd.d.tl`), sets that boolean, and the game's own comment calls such a building "Historic". So the flag is `blockedDevelopment`, and the building's customers and stocks sit in the entities it points to (the stock records: [building-stocks.md](building-stocks.md)).
- **Confirmed on 604 (one game, two buildings): the flag is one byte in the building's record, and the records can be listed.** Saves `1428` (the 5 of 6 building ticked, clock 11,324,600) and `1429` (the 8 of 8 building also ticked, same clock 11,324,600, paused throughout) differed in 124 places, and one of them was a single byte going 0 to 1 inside the record below. `1427` had no record with the byte set, `1428` one and `1429` two, so the byte is the "Historic Preservation" tick (`blockedDevelopment`). The player's count agrees: only two buildings on the map had been ticked by `1429`, and the scan finds exactly two set bytes among 569 records.

```
u32  a            an entity id
u32  b            the same id again, or 0xffffffff
u32  level        1 to 4 by the API; 1 and 2 only in this game
u32  d            an entity id (often a - 1)
u8   blockedDevelopment   0 or 1
vec<u32> parcels  u32 n (1 to 4 here), then n entity ids
u32  depth        1 to 4
f32  height       metres
u32  town         the town's entity id
u64  timeBuilt    a clock value, see calendar.md
```

- **The records follow each other with nothing between them.** A record is 41 + 4n bytes, and the distances between consecutive flag bytes were 45, 49, 53 and 57 (n = 1 to 4) for nearly all of 569 records. The order differs from the API's list (the flag sits straight after `level` and one entity, before the parcels). The scan took a `level` byte, an entity, a flag byte of 0 or 1 and a count of 1 to 16, then checked depth, height, a town id and a build time; a find-by-pattern, not by offset.
- **What the 569 were.** Three towns (entity ids 17,912, 17,913 and 17,914, with 181, 82 and 306 records), every building of the game, not only commercial ones. `1427` held 566 records and `1428` 569: the three buildings built in the 91st month. The two ticked buildings are both in town 17,914: the 5 of 6 one has height 23.3 and `timeBuilt` 9,936,000, the 8 of 8 one (the larger) height 25.7 and `timeBuilt` 7,440,000. Build times run from 0 to 11,304,000, and several buildings share one value (5,017,600 for example), so they come in batches. What `a`, `b` and `d` point to was not followed.
- **`timeBuilt` is a clock value, 0, or all ones (Observed, 604, one game).** The first save of the [Small subarctic game](test-games.md#small-subarctic-game) (1 January 1900) held 410 records: 327 with 0, 83 with all 64 bits set, none with a clock value. By 1 April 1920 there were 1,329: 1,170 with a clock value, 144 with 0, 15 with all ones. Of the 83 all-ones records, 74 kept their parcel ids and 59 of those had a clock value by then (a rebuild in place writes a new time); of the 327 zeros, 145 did and 38 lost their parcel set. A level change leaves the value alone (21 zeros went from level 1 to 2). The all-ones records are the larger buildings of the start (2 to 4 parcels wide, mostly depth 4, 19.9 m high on average against 15.3 m); what all ones means that 0 does not is **Open**. A scan that wanted a plausible clock value skips them, so the 569 above may be short.

### The town field and the town boundaries

The `town` field of a building record is the owning town (Confirmed, 604, two buildings), and the boundary between two towns on the map fits the line equidistant from their first crossings (Observed, three games). The evidence, the screenshots and the open questions are in [town-boundaries.md](town-boundaries.md).

The ticks made in the map editor, a building's position and what the record's `town` value is are in [editor-map-buildings.md](editor-map-buildings.md).

## Evidence and tests

The dated tests are in [town-buildings-tests.md](town-buildings-tests.md): [ticking buildings, save by save](town-buildings-tests.md#ticking-buildings-save-by-save), [what the flag does in the game](town-buildings-tests.md#what-the-flag-does-in-the-game) and [building records change level during play](town-buildings-tests.md#building-records-change-level-during-play-and-a-records-first-id-is-not-its-identity-604).
