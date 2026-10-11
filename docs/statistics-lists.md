# Statistics lists: the running totals behind stocks and charts

Where the game keeps the running totals behind the warehouse window's stock levels and its yearly incoming and outgoing bars. Checked on 604 in one game: catalog save [6417707](https://mod.io/g/transportfever3/m/333151) and later manual saves of it, compared with screenshots of the game's windows. Labels are **Observed** (matched in every save tried, not changed in the game) unless marked.

A stock is not stored as a number. The save keeps, per cargo, a list of running totals of what was unloaded and what was loaded, and the stock is their difference. The yearly bars are differences of the same totals at year boundaries. Earlier searches for the plain figures are in [entity-stats.md](entity-stats.md). What the lists say about industries (output stocks, destroyed cargo, industries created in play) is in [industries.md](industries.md), and the spoiled counts in [spoilage.md](spoilage.md). Two whole cargo chains read with these lists (fish from three industries to a town, stone and cement from a quarry to a town) are in [fish-chain.md](fish-chain.md) and [cement-chain.md](cement-chain.md).

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
- Which entity an `items` group belongs to was **not found**. The structure above a group has no readable owner id, and the group after a run of `happiness_*` groups did not name one. To tie a group to a warehouse, match the stock figures (below) to the warehouse window.

## Stock = unloaded minus loaded

For each cargo `c` in an object's group, `last value of itemsUnloaded<c>` minus `last value of itemsLoaded<c>` equals the stock the warehouse window shows for that cargo. A warehouse group has one such pair per module slot.

- A test warehouse with one liquid slot, in three saves: the ship's cargo (id 19 here) read unloaded 2,737, 2,754, 2,767 and loaded 2,737 throughout, so the difference was 0, 17 and 30, which was what the window showed (warehouse empty and ship loaded; ship half unloaded; ship unloaded).
- A flatbed warehouse with steel 411 and sheet metal 420 in the window: a group with ids 10 and 11 and differences 411 and 420. Read by the window's order that makes steel 10 and sheet metal 11, but the save's cargo list has sheet metal at 10 and steel at 11, and which is right is **Open** ([cargo-ids.md](cargo-ids.md#the-id-is-the-position-in-the-cargo-list)).
- A six-slot warehouse with meat 1, cement 11, clothes 40, tinned food 2 and furniture 52 and a sixth slot with 11: a group with ids 7, 15, 27, 28, 31 and 1 and exactly those differences. The ids agree with the table in [cargo-ids.md](cargo-ids.md).
- The 15-module warehouse of [warehouses.md](warehouses.md): in two saves the group held 15 cargo ids and the differences matched all eight levels read from the window in the first save (460, 208, 108, 83, 60, 34, 15, 8) and the four that the second save left unchanged (208, 8, 49 and 15) plus the grain and stone levels read there (473 and 362).

- **A second game** ([6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1), temperate, 1937, 604; a paused re-save compared with all 23 rows of the Warehouses tab). All 15 rows with something stored had a group whose stock fit: Stored 114, 284 and 13 were rows whose only icon was fish, each a single list of id 6, and 36 was id 6 as well; 84 and 1,017 were id 9 (vegetables; the rows' icon was a green gem), 995 was one list (id 2, dyes), 551 was dyes 2, logs 12 and plastic 29 (491, 12 and 48), 2,120 was fuel 20 (488), planks 13 (132) and plastic 29 (1,500), 520 was sand 5 (20) plus glass 32 (500), and the three rows of 500 each had one list (fertilizer 3, plastic 29 and fabric 26). Names are from the save's cargo list ([cargo-ids.md](cargo-ids.md#the-id-is-the-position-in-the-cargo-list)); the purple-cube goods icon sat on 29, plastic. Where several lists gave one total (8, 20 and 500) the row was not pinned to one group. **Observed**, one game.
- **A group may have an `itemsUnloaded<c>` list and no `itemsLoaded<c>`.** Cargo that was never taken out of the warehouse has no loaded list, and the stock is then the last unloaded total. In the second game the 500 of glass and the 1,017 of id 9 were such lists. Treat a missing loaded list as 0 when taking differences (**Observed**; the first game's test cases all had both).
- **A cargo's stock can pass one module's 500.** The row with 1,017 was a 3-module warehouse (capacity 1,500, 68%) and its group had that single cargo id. So the stock is not held per module; whether several modules were set to the same cargo is **Open**.

Differences are not stocks in every group: in one save about a third of the groups with both lists (143 of 395) had a negative difference somewhere. The rule was checked on warehouses only, so a group is picked by matching window values, not by list names alone.

## Yearly bars

The incoming bar for a year is the last total in that year minus the last total before it, taken from `itemsUnloaded`, and the outgoing bar the same from `itemsLoaded`. An `itemsUnloaded19` list of the test warehouse gave, from 1985 to 2000: 120, 120, 117, 120, 120, 90, 120, 150, 90, 150, 90, 120, 120, 120, 120, 90. The window's tooltips read the same, except 135 for 1991 and 135 for 1992 where the list gave 120 and 150. The outgoing bars for 1996 and 1997 (102 and 150) matched the list of loaded totals too.

- The 15 that moved is one entry (+15) at clock time 134,411,600, which is 0.9 day after the start of 1 January 1992 read as plain calendar days from 1 January 1900, and the day table of [calendar.md](calendar.md#the-day-table) puts it on 1 January 1992 too. The window counted it in 1991. The bars are periods of 1,461,000 clock units, not calendar years ([below](#the-yearly-bars-are-periods-of-1461000-units-604)): 92 x 1,461,000 is 134,412,000, 400 units after the entry, so it falls in period 91, the 1991 bar. **Observed**.
- The 2000 bar read 60 in the saves with the ship not yet unloaded and with 17 of 30 unloaded, and 90 once all 30 were in. The list already held 2,754 (77 for the year) in the middle save, so the bar lagged the list by the unloading in progress. Observed once.
- The station window's unloaded bars equalled the warehouse's incoming bars. Two groups 30 KB apart carry the same `itemsUnloaded` and `itemsUnloaded19` totals, which would explain it; only the one that also has `itemsLoaded19` gave the stock. Which of the two is the station and which the warehouse is **Open**.
- A station window's Loaded and Unloaded bars are the same differences per 1,461,000-unit period, taken from the station's `itemsLoaded<c>` and `itemsUnloaded<c>`. In the [Small subarctic game](test-games.md#small-subarctic-game) (604, April 1919) the window of the station by the cement warehouse showed the five newest pairs as about 48 and 90, 126 and 96, 72 and 96, 126 and 90, 50 and 84, newest first. Two groups with the same `itemsLoaded15` and `itemsUnloaded15` totals gave exactly those figures, the newest pair being the period still open. **Observed**, bars read by eye.

## How entries are added

- A new delivery adds one entry, with the time of its last unloading step. While a ship is still unloading, that last entry is rewritten in place (the count stayed 103 while the total went from 2,754 to 2,767 and the time from 28 to 29 October).
- Counts are limited: the longest lists had about 1,200 entries, and a list's count fell between two saves (159 to 158) while its total rose, so old entries are dropped. The totals keep their meaning because they are cumulative.
- Time values are game clock units. 17 April 2000 was 146,524,000, 2000-01-01 was 146,096,000 and 28 October 2000 was about 147,300,000, on a game at 1.00x.

## Finding a warehouse's stock

1. Decompress the stream ([container.md](container.md)) and scan for fields with the pattern above, then chain them into groups (`u32 key`, `u32 n`, `n` fields).
2. For each group take the cargo ids that have `itemsUnloaded<c>` (and `itemsLoaded<c>` where it exists, else 0), and compute the differences.
3. Pick the group whose differences equal the figures in the warehouse window. With 15 slots this is unique; with one or two slots it needs a second save with other figures.

A scan of one 940 MB stream took about one minute in Python.

## A small new game: one fish line, three windows (604)

**Observed** on 604, the [Small subarctic game](test-games.md#small-subarctic-game) a few minutes in, in two saves (`1131` at clock 569,800 and `1147` at 632,200, both paused, see [calendar.md](calendar.md)). The streams were 67 MB, so a scan with the pattern above took a second and the fields sat 6.2 to 6.4 MB into the stream. With only fish moving, every figure in three windows could be matched to a field of cargo id 6 (fish, [cargo-ids.md](cargo-ids.md)):

| Window | Figure | Field and values |
|---|---|---|
| Warehouse, stock | 21 then 18 | `itemsUnloaded6` minus `itemsLoaded6`: 29 - 8 in `1131`, 30 - 12 in `1147` |
| Warehouse, Incoming and Outgoing bars | 18 and 8, then 30 and 12 | the same two fields, with the exception in the first bullet below |
| Fishing Grounds, Cargo Flow | Produced 18, Destroyed 6 | `itemsProduced6` ending at 18 (steps 12, 15, 18) and `itemsDestroyed6` ending at 6 |
| Line windows, Transported Last Year | 8 (`horsewagon_1850_v2` carts), 40 (ships) | an `itemsTransported6` list ending at 8 (steps 4, 8) and one ending at 40 (steps 30, 40); in `1147` the second ended at 50 and the first at 8 |

- **The bars leave out the newest entry.** In `1131` the warehouse's unloaded list ended at 29 with its last time equal to the save's clock (569,800), but the window's Incoming bar showed 18, the value of the entry before. In `1147` the last unloaded entry (30, at 570,600) was well before the save's clock and the bar showed 30. The loaded list agreed with the bar in both (8 and 12). So the bar is the total up to the last entry that is older than the save's clock, while the stock uses every entry. A ship was unloading at the port when `1131` was paused, which fits an entry made at that very tick. **Observed**, one ship, two saves. This replaces the unexplained 21 against 18 - 8 in [running-costs.md](running-costs.md#upkeep-and-running-costs-are-booked-in-batches-604).
- **Lists grow by one entry per event time.** The fish loaded at the Fishing Grounds read times 121,749, 243,400 and 352,600 with totals 0, 30 and 40 in `1131`, and the same three plus (630,200, 50) in `1147`. Lists in these two saves held 2 to 9 entries. Each list starts with a total of 0 at a time of its own (121,749, 365,249, 486,999 and so on, not the game start), which looks like the time the list was created; the later entries are totals at the times fish were handled. **Observed**.
- **The Fishing Grounds' output stock and its destroyed fish** follow from the same lists, see [industries.md](industries.md#first-readings-saves-1131-and-1147).
- **A time of 18,446,744,073,709,551,615** (u64 maximum) was the first time of the `itemsDestroyed6` list of the fishing industry: a start marker with the total 0, followed by (111,800, 6).

## The yearly bars are periods of 1,461,000 units (604)

**Observed** on 604, the same new game at clock 3,785,800, with the bars of eight windows read by eye and the lists differenced at the period boundaries 1,461,000 and 2,922,000 (the third bar runs to the clock of the save). All three bars of every window matched, so a bar is the change of a list over one period, as [Yearly bars](#yearly-bars) says, and the calendar date label under it ("1/1/1900" three times) does not move when the date is stopped.

| Window | Bars read (periods 1, 2, 3) | Field and its periods |
|---|---|---|
| Todmorden Warehouse, Incoming and Outgoing | about 90, 175, 105 and 68, 100, 64 | `itemsUnloaded6` and `itemsLoaded6` (fish): 90, 175, 105 and 68, 100, 64, totals 370 and 232; the stock read 138, which is 370 - 232 |
| Todmorden Port, Loaded and Unloaded | about 20, 50, 30 and 90, 175, 105 | a fish `itemsLoaded6` with 20, 50, 30 and the same unloaded list as the warehouse |
| Todmorden Station (a road stop), Loaded | about 68, 102, 66 | a fish `itemsLoaded6` of 68, 102, 66 (the warehouse's outgoing list had 68, 100, 64: the cart line (`horsewagon_1850_v2` and `horsewagon_1850_usa_v2`) loaded 2 more fish per period than the warehouse list says, which is **Open**) |
| Todmorden Fishing Grounds, Produced | about 45, 61, 38 | `itemsProduced6`: 45, 61, 38 |
| Bromsgrove Quarry, Produced and Destroyed | about 70, 74, 56 and 70, 34, 24 | `itemsProduced24` and `itemsDestroyed24` with those values (24 is stone, see [cargo-ids.md](cargo-ids.md)) |
| Bromsgrove Quarry North, Produced | about 35, 65, 40 | `itemsProduced24`: 35, 65, 40; no destroyed list |
| Bromsgrove Cement Plant, Consumed and Produced | 36, 28 and 18, 14 (none in period 1) | `itemsConsumed24` 0, 36, 28 and `itemsProduced15` 0, 18, 14 |
| Bromsgrove Warehouse (cement), Incoming and Outgoing | 18, 4 and 16 | `itemsUnloaded15` 0, 18, 4 and `itemsLoaded15` 0, 16, 0; stock 6 = 22 - 16 |

- The industry rows of the table also give the output stocks and the stone destroyed at a full quarry, see [industries.md](industries.md#three-periods-clock-3785800).
- **The bars keep to clock periods when the calendar runs (604, `1707`, 0.25x, Feb 9, 1900 on screen).** The town stop's unloaded list differenced at multiples of 1,461,000 gave 105, 60, 84 and 24 for the last four periods (the last one open), the same four bars the player's chart showed, with three axis labels still reading 1/1/1900. The calendar was started at about clock 17,248,000, so the boundary at 17,532,000 (the start of the 13th period) falls in mid-January, not on a date boundary. So the year bars do not follow the date. A save at clock 19,008,600 (`1709`, 21 April 1900 on screen, 15,600 units past the 13th boundary at 18,993,000, which lies in the last hours of 20 April) showed the 13th bars final (the stop 104 and the warehouse 104 in and 104 out, up from 96, 96 and 96 in `1708`) and no bar for the 14th period yet: a bar appears with the first list entry in its period, not at the boundary. **Observed**, one chart.
