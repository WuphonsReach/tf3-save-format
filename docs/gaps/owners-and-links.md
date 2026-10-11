# Gaps: owners and links

Questions of the form "which record belongs to which thing". Format of an entry: see [README.md](README.md).

## Statistics groups

- **Which station, stop, ship or warehouse a group belongs to** (604) The `items*` lists sit in groups, and an industry's id was found on a keyed copy of its Transported lists (three industries in catalog save 6425796, matched by unique totals). For stations, stops and warehouses no owner id has been found, and what puts a stop's lists into a group is unknown. Home: [statistics-lists.md](../statistics-lists.md#groups). Needs: existing saves (ground truth for 6425796: a warehouse's stock of 1,500 plastic, four cotton farms told apart by shipment, a train's two stops told apart by its 210-unit loads); a pair of groups 30 KB apart in a second game carry the same totals, and only one of them holds the Loaded list that gives the stock.
  - Tried: looking for the id in the slot next to a name; lists of sorted ids (they are timestamp arrays); the `happiness_*` keys as owners (they are rated entities, not owners).
  - Leads not yet followed: the bytes above a group; the `__module_` id list in a warehouse record ([cargo-and-warehouses.md](cargo-and-warehouses.md)); whether record order and group order follow entity id; whether per-vehicle and per-line figures sit in the same lists.
- **What the key 0 against 0x1000000, and the large module keys, encode** (604) Two key styles on groups are unexplained. Home: [statistics-lists.md](../statistics-lists.md#groups). Needs: existing saves.
- **Why one industry id also keys the receiving side** (604, one game) The weaving mill's id keys a wool copy that directly follows the supplying farm's group and another wool copy elsewhere, so a key marks the receiving side as well. Home: [statistics-lists.md](../statistics-lists.md#groups). Needs: existing saves.
- **Destination-group keys** (604, one game) Three keys on the fish chain's destination groups moved while trucks were stuck, and which consumer they are is unknown. Home: [statistics-lists.md](../statistics-lists.md), [fish-chain.md](../fish-chain.md). Needs: existing saves, or a new save that follows one building.
- **Which edge group is which road segment** (604, one game) Edge totals stall where vehicles queue, but no edge is tied to a place. Home: [fish-chain.md](../fish-chain.md). Suggested test: new save with one vehicle stopped at a known place, then see which edge total stalls.

## Lines, stops and vehicles

- **A line's stops and vehicles from the save** (604) Line id and name appear only in `line_warning` entries; a line's vehicles can be read while they carry cargo (cargo-unit records of line id and vehicle id). A line that is empty and has no warning (the clothes train of 6425796) cannot be found, and its 60-second stop records lack the cargo vector. Home: [line-ids.md](../line-ids.md). Needs: new save with that train loaded, or a unit id read from the game.
- **A vehicle's own line assignment and route position** (604) Not found in model instances; a byte diff of saves is too noisy to see it. Home: [vehicles.md](../vehicles.md), [lines.md](../lines.md#the-next-stop-a-depot-order-and-a-second-list). Needs: entity ids of the vehicles first (from notification mappings), then a new save in which one vehicle is moved to another line, saved paused before and after.
- **A stop record's own entity id** (604) The record carries the three stop times and the cargo vector but no id has been found in or next to it. Home: [line-ids.md](../line-ids.md). Needs: existing saves.
- **Which fields of the stop record are which** (604) The 37 floats that read 1.0 in every record; the load list shown as "fish 100%"; the departure choice; which of two default-ticked flag bytes is which; the four bytes that follow the three floats on a ship port stop (a count of something that changed from 1 to 2 while stops were edited). A per-cargo byte vector at the end of the record is described in the line note and a 37-float run in the stop-record note; whether they are the same region has not been checked. Home: [lines.md](../lines.md#the-stop-configuration-record), [line-ids.md](../line-ids.md). Needs: new save with a stop set to a distinctive load percentage (the window's 100% is the only value seen).
- **Why a new line's records differ in length** (604, one game) The stop records of two new lines ran 232 and 245 bytes apart. Home: [lines.md](../lines.md#a-new-line-and-its-vehicles). Needs: existing saves.
- **Where a stop's waiting-passenger count is kept** (604) Home: [lines.md](../lines.md#trip-plans-line-stops-and-vehicle-or-a-building-604). Needs: new save with a window number read before saving.
- **The second per-vehicle list** (604) A list of `[u32 1 to 4][u64 clock][u64 vehicle]` covering some vehicles only (26 in one save). What it schedules is unknown. Home: [lines.md](../lines.md#the-next-stop-a-depot-order-and-a-second-list). Needs: existing saves.

## People and trip records

- **Where a person's own record is** (604) Home, work, shop, route and happiness are not found; the only link to a building list is the home block of six consecutive slots per household. Home: [lines.md](../lines.md#which-person-a-record-belongs-to), [entity-names.md](../entity-names.md). Suggested tests: new save with one name in a household block renamed and one from the other block of the same building, to see which homes change; a Locate-follow save against a same-clock save with the camera far away, to see whether any coordinates differ (the save may not store the camera).
- **What owns a record of the trip array** (604) The building ids of its no-line records are not the town building record ids. Home: [lines.md](../lines.md#records-without-a-line). Needs: existing saves.
- **What a record in a vehicle's trip list counts** (604, one game) A record stays after its person has left, until it is rewritten; what creates and removes records (423 before one save) and why the window's 16 differs from the array's 20 are unexplained. Home: [lines.md](../lines.md#trip-plans-line-stops-and-vehicle-or-a-building-604). Needs: existing saves.

## Vehicle and entity names

- **Entity id to model instance slot** (604, Observed in one game) Names and ids run in opposite directions inside one purchase batch, and the id is the name slot plus a constant within a batch; no rule links an entity id to its instance. Home: [entity-names.md](../entity-names.md), [vehicles.md](../vehicles.md). Needs: existing saves.
- **The id rule for later entities** (599 to 604) The company and first towns take id = base + slot; later entities do not. Home: [entity-names.md](../entity-names.md). Needs: existing saves.
- **What follows the name table** (two saves) About 8 zero bytes and a u32 near 171,000. Home: [entity-names.md](../entity-names.md). Needs: existing saves.
- **The table of resource paths** (604) Numbers per cargo and vehicle model that are not the model ids. Home: [entity-names.md](../entity-names.md), [models.md](../models.md). Needs: existing saves.
