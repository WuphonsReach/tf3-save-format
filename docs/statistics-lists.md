# Statistics lists: warehouse stock and yearly bars

Where the game keeps the running totals behind the warehouse window's stock levels and its yearly incoming and outgoing bars. Checked on 604 in one game: catalog save [6417707](https://mod.io/g/transportfever3/m/333151) and later manual saves of it, compared with screenshots of the game's windows. Labels are **Observed** (matched in every save tried, not changed in the game) unless marked.

A stock is not stored as a number. The save keeps, per cargo, a list of running totals of what was unloaded and what was loaded, and the stock is their difference. The yearly bars are differences of the same totals at year boundaries. Earlier searches for the plain figures are in [entity-stats.md](entity-stats.md).

## A field

A named list of (time, running total) pairs, stored as two parallel vectors:

| Part | Encoding |
|---|---|
| name | `str`, 3 to 48 characters of `A-Z a-z 0-9 _` |
| times | `vec<u64>`, ascending, in the game clock unit of [script-states.md](script-states.md) (1/4,000 of a game day) |
| totals | `vec<u64>`, same length as `times`, rising (cumulative) |
| end | one zero byte |

Names found by scanning for the pattern `u32 length` + `items` + letters: `itemsLoaded`, `itemsUnloaded`, `itemsLost`, `itemsTransported`, `itemsProduced`, `itemsConsumed`, `itemsDestroyed`, `itemsAtDestination`, `itemsAtDestinationUnsatisfied`, `itemsAtEdge0_c<cargo>`, `itemsAtStop1_c<cargo>` and similar. A number at the end (`itemsUnloaded19`) is a cargo id ([cargo-ids.md](cargo-ids.md)); without one the list counts all cargos. A stream had about 420,000 such fields. Other statistics have the same shape: `happiness_station`, `happiness_vehicle`, `happiness_residential`, `traffic_congestion` and others (not read further).

## Groups

Fields come in groups, back to back: `u32 key`, `u32 n`, then `n` fields. About 150,000 groups with `items` fields were found in a 940 MB stream.

- The groups with `itemsLoaded`, `itemsUnloaded`, `itemsLost`, `itemsConsumed` and `itemsProduced` lists (per cargo) have key `0` or `16777216` (`0x1000000`). The warehouse groups read had either. What separates the two keys was not found.
- A group keyed with one of the first town ids (58,493 to 58,508 in the game read, see [entity-names.md](entity-names.md)) holds `itemsAtEdge` and `itemsAtEdgeUnsatisfied` lists and repeats many times: it looks like a per-town entry inside a larger structure.
- `happiness_station` and `happiness_vehicle` groups are keyed with ids of 5 to 6 digits (for example 268,963) and sit directly before some `items` groups.
- Which entity an `items` group belongs to was **not found**. The structure above a group has no readable owner id, and the group after a run of `happiness_*` groups did not name one. To tie a group to a warehouse, match the stock figures (below) to the warehouse window.

## Stock = unloaded minus loaded

For each cargo `c` in an object's group, `last value of itemsUnloaded<c>` minus `last value of itemsLoaded<c>` equals the stock the warehouse window shows for that cargo. A warehouse group has one such pair per module slot.

- A test warehouse with one liquid slot, in three saves: the ship's cargo (id 19 here) read unloaded 2,737, 2,754, 2,767 and loaded 2,737 throughout, so the difference was 0, 17 and 30, which was what the window showed (warehouse empty and ship loaded; ship half unloaded; ship unloaded).
- A flatbed warehouse with steel 411 and sheet metal 420 in the window: a group with ids 10 and 11 and differences 411 and 420. So steel is 10 and sheet metal is 11 in this game.
- A six-slot warehouse with meat 1, cement 11, clothes 40, tinned food 2 and furniture 52 and a sixth slot with 11: a group with ids 7, 15, 27, 28, 31 and 1 and exactly those differences. The ids agree with the table in [cargo-ids.md](cargo-ids.md).
- The 15-module warehouse of [warehouses.md](warehouses.md): in two saves the group held 15 cargo ids and the differences matched all eight levels read from the window in the first save (460, 208, 108, 83, 60, 34, 15, 8) and the four that the second save left unchanged (208, 8, 49 and 15) plus the grain and stone levels read there (473 and 362).

- **A second game** ([6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1), temperate, 1937, 604; a paused re-save compared with all 23 rows of the Warehouses tab). All 15 rows with something stored had a group whose stock fit: Stored 114, 284 and 13 were rows whose only icon was fish, each a single list of id 6, and 36 was id 6 as well; 84 and 1,017 were id 9 (vegetables in the table; the rows' icon was a green gem), 995 was one list (id 2), 551 was ids 2, 12 and 29 (491, 12 and 48), 2,120 was fuel 20 (488), planks 13 (132) and id 29 (1,500), 520 was id 5 (20) plus glass 32 (500), and the three rows of 500 each had one list (ids 3, 29 and 26). Where several lists gave one total (8, 20 and 500) the row was not pinned to one group. **Observed**, one game. Ids 20, 13 and 32 agree with [cargo-ids.md](cargo-ids.md); the same row put the purple-cube cargo (a goods icon) at 29.
- **A group may have an `itemsUnloaded<c>` list and no `itemsLoaded<c>`.** Cargo that was never taken out of the warehouse has no loaded list, and the stock is then the last unloaded total. In the second game the 500 of glass and the 1,017 of id 9 were such lists. Treat a missing loaded list as 0 when taking differences (**Observed**; the first game's test cases all had both).
- **A cargo's stock can pass one module's 500.** The row with 1,017 was a 3-module warehouse (capacity 1,500, 68%) and its group had that single cargo id. So the stock is not held per module; whether several modules were set to the same cargo is **Open**.

Differences are not stocks in every group: in one save about a third of the groups with both lists (143 of 395) had a negative difference somewhere. The rule was checked on warehouses only, so a group is picked by matching window values, not by list names alone.

## Yearly bars

The incoming bar for a year is the last total in that year minus the last total before it, taken from `itemsUnloaded`, and the outgoing bar the same from `itemsLoaded`. An `itemsUnloaded19` list of the test warehouse gave, from 1985 to 2000: 120, 120, 117, 120, 120, 90, 120, 150, 90, 150, 90, 120, 120, 120, 120, 90. The window's tooltips read the same, except 135 for 1991 and 135 for 1992 where the list gave 120 and 150. The outgoing bars for 1996 and 1997 (102 and 150) matched the list of loaded totals too.

- The 15 that moved is one entry (+15) at clock time 134,411,600, which is 0.9 day after the start of 1 January 1992 read as plain calendar days from 1 January 1900. The window counted it in 1991. Moving every year boundary 3,700 to 9,600 units (0.9 to 2.4 days) after the plain calendar start fits all 15 bars; the plain start fits 14. So the game's year for a clock time is not exactly the calendar day count. The day table of [script-states.md](script-states.md#the-day-table) puts that entry on 1 January 1992 too (plain 4000 ticks per day in that game), so the bars are not binned by that table's day alone. Whether the offset comes from the calendar speed setting (all saves here were at 1.00x) or a fixed offset is **Open**.
- The 2000 bar read 60 in the saves with the ship not yet unloaded and with 17 of 30 unloaded, and 90 once all 30 were in. The list already held 2,754 (77 for the year) in the middle save, so the bar lagged the list by the unloading in progress. Observed once.
- The station window's unloaded bars equalled the warehouse's incoming bars. Two groups 30 KB apart carry the same `itemsUnloaded` and `itemsUnloaded19` totals, which would explain it; only the one that also has `itemsLoaded19` gave the stock. Which of the two is the station and which the warehouse is **Open**.

## How entries are added

- A new delivery adds one entry, with the time of its last unloading step. While a ship is still unloading, that last entry is rewritten in place (the count stayed 103 while the total went from 2,754 to 2,767 and the time from 28 to 29 October).
- Counts are limited: the longest lists had about 1,200 entries, and a list's count fell between two saves (159 to 158) while its total rose, so old entries are dropped. The totals keep their meaning because they are cumulative.
- Time values are game clock units. 17 April 2000 was 146,524,000, 2000-01-01 was 146,096,000 and 28 October 2000 was about 147,300,000, on a game at 1.00x.

## Finding a warehouse's stock

1. Decompress the stream ([container.md](container.md)) and scan for fields with the pattern above, then chain them into groups (`u32 key`, `u32 n`, `n` fields).
2. For each group take the cargo ids that have `itemsUnloaded<c>` (and `itemsLoaded<c>` where it exists, else 0), and compute the differences.
3. Pick the group whose differences equal the figures in the warehouse window. With 15 slots this is unique; with one or two slots it needs a second save with other figures.

A scan of one 940 MB stream took about one minute in Python.
