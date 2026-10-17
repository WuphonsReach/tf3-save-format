# Statistics lists: the running totals behind stocks and charts

Where the game keeps the running totals behind the warehouse window's stock levels and its yearly incoming and outgoing bars. Checked on 604 in one game: catalog save [6417707](https://mod.io/g/transportfever3/m/333151) and later manual saves of it, compared with screenshots of the game's windows. Labels are **Observed** (matched in every save tried, not changed in the game) unless marked.

A stock is not stored as a number. The save keeps, per cargo, a list of running totals of what was unloaded and what was loaded, and the stock is their difference. The yearly bars are differences of the same totals at period boundaries ([statistics-bars.md](statistics-bars.md)). Earlier searches for the plain figures are in [entity-stats.md](entity-stats.md). What the lists say about industries (output stocks, destroyed cargo, industries created in play) is in [industries.md](industries.md), and the spoiled counts in [spoilage.md](spoilage.md). Two whole cargo chains read with these lists (fish from three industries to a town, stone and cement from a quarry to a town) are in [fish-chain.md](fish-chain.md) and [cement-chain.md](cement-chain.md).

## In short

- **A stock is not stored as a number; it is the last `itemsUnloaded<c>` total minus the last `itemsLoaded<c>` total of the warehouse's group (Observed, matched against windows in two games and a 15-module warehouse).** A missing loaded list counts as 0. A group is picked by matching window values, since differences are negative somewhere in about a third of the groups that have both lists.
- **A statistics field is a named list of (time, running total) pairs: a `str` name, a `vec<u64>` of times, a `vec<u64>` of totals and a zero byte (Observed).** A trailing number in the name is a cargo id; none means all cargos.
- **Fields come in groups: `u32 key`, `u32 n`, then `n` fields (Observed).** Industry-side groups have key `0` or `16777216`; a group with an entity id as key can be a keyed copy of an industry's `Transported` lists, which ties an industry to an id (Observed, one game). A group can be the sum of the two stops of one station.
- **Which entity owns a group without such a keyed copy (stops, stations, warehouses) was not found (Open),** and neither was what separates the keys `0` and `16777216`.
- **A new delivery adds one entry, and a ship still unloading rewrites the last entry in place (Observed).** The longest lists held about 1,200 entries and old entries are dropped.
- **The delivered-cargo counters match the lists exactly in two games and to 99.2% in the long one; passengers fall short in all three (Open).**
- The bars of the windows are made from the same lists: [statistics-bars.md](statistics-bars.md).


## A field

A named list of (time, running total) pairs, stored as two parallel vectors:

| Part | Encoding |
|---|---|
| name | `str`, 3 to 48 characters of `A-Z a-z 0-9 _` |
| times | `vec<u64>`, ascending, in the game clock of [calendar.md](calendar.md) (the game's milliseconds, 4,000 a day at 1.00x) |
| totals | `vec<u64>`, same length as `times`, rising (cumulative) |
| end | one zero byte |

Names found by scanning for the pattern `u32 length` + `items` + letters: `itemsLoaded`, `itemsUnloaded`, `itemsLost`, `itemsTransported`, `itemsProduced`, `itemsConsumed`, `itemsDestroyed`, `itemsAtDestination`, `itemsAtDestinationUnsatisfied`, `itemsAtEdge0_c<cargo>`, `itemsAtStop1_c<cargo>` and similar. A number at the end (`itemsUnloaded19`) is a cargo id ([cargo-ids.md](cargo-ids.md)); without one the list counts all cargos. A stream had about 420,000 such fields. Other statistics have the same shape: `happiness_station`, `happiness_vehicle`, `happiness_residential`, `traffic_congestion` and others (not read further).

## Groups

Fields come in groups, back to back: `u32 key`, `u32 n`, then `n` fields. About 150,000 groups with `items` fields were found in a 940 MB stream.

- The groups with `itemsLoaded`, `itemsUnloaded`, `itemsLost`, `itemsConsumed` and `itemsProduced` lists (per cargo) have key `0` or `16777216` (`0x1000000`). The warehouse groups read had either. What separates the two keys was not found.
- A group keyed with one of the first town ids (58,493 to 58,508 in the game read, see [entity-names.md](entity-names.md)) holds `itemsAtEdge` and `itemsAtEdgeUnsatisfied` lists and repeats many times: it looks like a per-town entry inside a larger structure.
- `happiness_station` and `happiness_vehicle` groups are keyed with ids of 5 to 6 digits (for example 268,963) and sit directly before some `items` groups.
- **A group can be the sum of two other groups (604, Observed, one game, [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1)).** One group's `itemsUnloaded` total (9,575) was exactly the sum of two other groups' (2,438 and 7,137), and its per-cargo totals added the same way (wool 4,152 and dyes 2,985 on one side, clothes 1,938 and fabric 500 on the other). The two were the two stops of one station: cargo arrives at one stop and leaves from the other. The `itemsLoaded` totals did not add exactly (9,075 against 9,304; the 229 left out were a wool and a clothes list). Test it when a station has several stops: look for a group whose totals are the sum of two others. What puts a stop's lists in a group is **Open**. The worked reading is in [analysis-examples/clothes-train2-supply-chain-starvation-6425796.md](analysis-examples/clothes-train2-supply-chain-starvation-6425796.md).
- **An industry's id sits on a keyed copy of its `Transported` lists (604, Observed, [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1)).** The industry's own group (key `0` or `16777216`, with `itemsProduced`, `itemsConsumed` and so on) names no id. A group whose key is an entity id and whose only lists are `itemsTransported<c>` and `itemsTransported` (or `itemsAtDestination<c>`) holds the same final total as one in the industry's group, in fewer entries (10 against 39, 21 against 146, 29 against 151, 33 against 200). Three industries tied this way: the chemical plant is 161,263 (Transported dyes 2,052 and plastic 2,104 both equal, a third list of 16,853 equals its Unloaded total); Westbury Cotton Farm #1 is 237,445 (wool 1,195, unique among the four farms); the weaving mill feeding the textile factory is 179,707 (fabric 3,504). The cargo-unit records of [line-ids.md](line-ids.md) carry the same id as the cargo's origin (237,445 on Wool1's records, 161,263 on the dyes and plastic lines), which confirms the farm one independently of the totals. The id 179,707 also keys a 1,195 wool copy that directly follows the farm #1 group and a 2,925 wool one elsewhere, which add to the mill's 4,120 wool unloaded, so a key also marks the receiving side (why, and which list is whose, is **Open**). Match by a total that is unique in the save; two industries with equal totals cannot be told apart.
- Which entity a group *without* such a keyed copy belongs to (stops, stations, warehouses) was **not found**. For those, the structure above a group has no readable owner id, and the group after a run of `happiness_*` groups did not name one. To tie a group to a warehouse, match the stock figures (below) to the warehouse window.

## Stock = unloaded minus loaded

For each cargo `c` in an object's group, `last value of itemsUnloaded<c>` minus `last value of itemsLoaded<c>` equals the stock the warehouse window shows for that cargo. A warehouse group has one such pair per module slot.

- **A group may have an `itemsUnloaded<c>` list and no `itemsLoaded<c>`.** Cargo that was never taken out of the warehouse has no loaded list, and the stock is then the last unloaded total. In the second game the 500 of glass and the 1,017 of id 9 were such lists. Treat a missing loaded list as 0 when taking differences (**Observed**; the first game's test cases all had both).
- **A cargo's stock can pass one module's 500.** The row with 1,017 was a 3-module warehouse (capacity 1,500, 68%) and its group had that single cargo id. So the stock is not held per module; whether several modules were set to the same cargo is **Open**.

Differences are not stocks in every group: in one save about a third of the groups with both lists (143 of 395) had a negative difference somewhere. The rule was checked on warehouses only, so a group is picked by matching window values, not by list names alone.

## How entries are added

- A new delivery adds one entry, with the time of its last unloading step. While a ship is still unloading, that last entry is rewritten in place (the count stayed 103 while the total went from 2,754 to 2,767 and the time from 28 to 29 October).
- Counts are limited: the longest lists had about 1,200 entries, and a list's count fell between two saves (159 to 158) while its total rose, so old entries are dropped. The totals keep their meaning because they are cumulative.
- Time values are game clock units. 17 April 2000 was 146,524,000, 2000-01-01 was 146,096,000 and 28 October 2000 was about 147,300,000, on a game at 1.00x.

## Finding a warehouse's stock

1. Decompress the stream ([container.md](container.md)) and scan for fields with the pattern above, then chain them into groups (`u32 key`, `u32 n`, `n` fields).
2. For each group take the cargo ids that have `itemsUnloaded<c>` (and `itemsLoaded<c>` where it exists, else 0), and compute the differences.
3. Pick the group whose differences equal the figures in the warehouse window. With 15 slots this is unique; with one or two slots it needs a second save with other figures.

A scan of one 940 MB stream took about one minute in Python.

## Evidence and tests

### Stock tests: warehouses matched to their windows

- A test warehouse with one liquid slot, in three saves: the ship's cargo (id 19 here) read unloaded 2,737, 2,754, 2,767 and loaded 2,737 throughout, so the difference was 0, 17 and 30, which was what the window showed (warehouse empty and ship loaded; ship half unloaded; ship unloaded).
- A flatbed warehouse with steel 411 and sheet metal 420 in the window: a group with ids 10 and 11 and differences 411 and 420. Read by the window's order that makes steel 10 and sheet metal 11, but the save's cargo list has sheet metal at 10 and steel at 11, and which is right is **Open** ([cargo-ids.md](cargo-ids.md#the-id-is-the-position-in-the-cargo-list)).
- A six-slot warehouse with meat 1, cement 11, clothes 40, tinned food 2 and furniture 52 and a sixth slot with 11: a group with ids 7, 15, 27, 28, 31 and 1 and exactly those differences. The ids agree with the table in [cargo-ids.md](cargo-ids.md).
- The 15-module warehouse of [warehouses.md](warehouses.md): in two saves the group held 15 cargo ids and the differences matched all eight levels read from the window in the first save (460, 208, 108, 83, 60, 34, 15, 8) and the four that the second save left unchanged (208, 8, 49 and 15) plus the grain and stone levels read there (473 and 362).

- **A second game** ([6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1), temperate, 1937, 604; a paused re-save compared with all 23 rows of the Warehouses tab). All 15 rows with something stored had a group whose stock fit: Stored 114, 284 and 13 were rows whose only icon was fish, each a single list of id 6, and 36 was id 6 as well; 84 and 1,017 were id 9 (vegetables; the rows' icon was a green gem), 995 was one list (id 2, dyes), 551 was dyes 2, logs 12 and plastic 29 (491, 12 and 48), 2,120 was fuel 20 (488), planks 13 (132) and plastic 29 (1,500), 520 was sand 5 (20) plus glass 32 (500), and the three rows of 500 each had one list (fertilizer 3, plastic 29 and fabric 26). Names are from the save's cargo list ([cargo-ids.md](cargo-ids.md#the-id-is-the-position-in-the-cargo-list)); the purple-cube goods icon sat on 29, plastic. Where several lists gave one total (8, 20 and 500) the row was not pinned to one group. **Observed**, one game.

### Delivered totals against the lists (604)

**Observed** on 604, three games. The two delivered totals ([script-states.md](script-states.md#counters-and-achievements)) can be set against the lists. For cargo, add the last totals of the per-cargo `itemsAtDestination<c>` lists (cargo id above 0) in groups that also hold the plain `itemsAtDestination` aggregate, the industry-keyed copies described under Groups. For people, add the last totals of every `itemsAtDestination` list for cargo id 0 (passengers).

| Game | Cargo delivered | Cargo lists | People delivered | Passenger lists |
|---|---|---|---|---|
| catalog save [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1), autosave of 18 Feb 1937 | 192,474 | 190,872 | 283,102 | 275,045 |
| temperate game from 1900, 20,480 x 40,960 m | 10,562 | 10,562 | 64,281 | 63,382 |
| [Small subarctic game](test-games.md#small-subarctic-game), 1 April 1920 | 16,774 | 16,774 | 41,640 | 41,353 |

The cargo lists add up to the counter exactly in the two smaller games and to 99.2% in the long one. The passenger lists fall short in all three (97.2% to 99.3%). **Open:** the counters or the lists may lag behind each other, an industry or stop that was deleted may take its lists with it, or there is something not understood yet; none of these was tested. The grouping rule is a construction of this note: a stricter one, groups keyed by an industry id only, gave 187,332 for the long game's cargo.
