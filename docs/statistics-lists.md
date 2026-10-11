# Statistics lists: the running totals behind stocks and charts

Where the game keeps the running totals behind the warehouse window's stock levels and its yearly incoming and outgoing bars. Checked on 604 in one game: catalog save [6417707](https://mod.io/g/transportfever3/m/333151) and later manual saves of it, compared with screenshots of the game's windows. Labels are **Observed** (matched in every save tried, not changed in the game) unless marked.

A stock is not stored as a number. The save keeps, per cargo, a list of running totals of what was unloaded and what was loaded, and the stock is their difference. The yearly bars are differences of the same totals at year boundaries. Earlier searches for the plain figures are in [entity-stats.md](entity-stats.md). What the lists say about industries (output stocks, destroyed cargo, industries created in play) is in [industries.md](industries.md), and the spoiled counts in [spoilage.md](spoilage.md).

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

**Observed** on 604, a new Small subarctic game of a few minutes, in two saves (`1131` at clock 569,800 and `1147` at 632,200, both paused, see [calendar.md](calendar.md)). The streams were 67 MB, so a scan with the pattern above took a second and the fields sat 6.2 to 6.4 MB into the stream. With only fish moving, every figure in three windows could be matched to a field of cargo id 6 (fish, [cargo-ids.md](cargo-ids.md)):

| Window | Figure | Field and values |
|---|---|---|
| Warehouse, stock | 21 then 18 | `itemsUnloaded6` minus `itemsLoaded6`: 29 - 8 in `1131`, 30 - 12 in `1147` |
| Warehouse, Incoming and Outgoing bars | 18 and 8, then 30 and 12 | the same two fields, with the exception in the first bullet below |
| Fishing Grounds, Cargo Flow | Produced 18, Destroyed 6 | `itemsProduced6` ending at 18 (steps 12, 15, 18) and `itemsDestroyed6` ending at 6 |
| Line windows, Transported Last Year | 8 (carts), 40 (ships) | an `itemsTransported6` list ending at 8 (steps 4, 8) and one ending at 40 (steps 30, 40); in `1147` the second ended at 50 and the first at 8 |

- **The bars leave out the newest entry.** In `1131` the warehouse's unloaded list ended at 29 with its last time equal to the save's clock (569,800), but the window's Incoming bar showed 18, the value of the entry before. In `1147` the last unloaded entry (30, at 570,600) was well before the save's clock and the bar showed 30. The loaded list agreed with the bar in both (8 and 12). So the bar is the total up to the last entry that is older than the save's clock, while the stock uses every entry. A ship was unloading at the dock when `1131` was paused, which fits an entry made at that very tick. **Observed**, one ship, two saves. This replaces the unexplained 21 against 18 - 8 in [running-costs.md](running-costs.md#upkeep-and-running-costs-are-booked-in-batches-604).
- **Lists grow by one entry per event time.** The fish loaded at the Fishing Grounds read times 121,749, 243,400 and 352,600 with totals 0, 30 and 40 in `1131`, and the same three plus (630,200, 50) in `1147`. Lists in these two saves held 2 to 9 entries. Each list starts with a total of 0 at a time of its own (121,749, 365,249, 486,999 and so on, not the game start), which looks like the time the list was created; the later entries are totals at the times fish were handled. **Observed**.
- **The Fishing Grounds' output stock and its destroyed fish** follow from the same lists, see [industries.md](industries.md#first-readings-saves-1131-and-1147).
- **A time of 18,446,744,073,709,551,615** (u64 maximum) was the first time of the `itemsDestroyed6` list of the fishing industry: a start marker with the total 0, followed by (111,800, 6).

## The yearly bars are periods of 1,461,000 units (604)

**Observed** on 604, the same new game at clock 3,785,800, with the bars of eight windows read by eye and the lists differenced at the period boundaries 1,461,000 and 2,922,000 (the third bar runs to the clock of the save). All three bars of every window matched, so a bar is the change of a list over one period, as [Yearly bars](#yearly-bars) says, and the calendar date label under it ("1/1/1900" three times) does not move when the date is stopped.

| Window | Bars read (periods 1, 2, 3) | Field and its periods |
|---|---|---|
| Todmorden Warehouse, Incoming and Outgoing | about 90, 175, 105 and 68, 100, 64 | `itemsUnloaded6` and `itemsLoaded6` (fish): 90, 175, 105 and 68, 100, 64, totals 370 and 232; the stock read 138, which is 370 - 232 |
| Todmorden Port, Loaded and Unloaded | about 20, 50, 30 and 90, 175, 105 | a fish `itemsLoaded6` with 20, 50, 30 and the same unloaded list as the warehouse |
| Todmorden Station (a road stop), Loaded | about 68, 102, 66 | a fish `itemsLoaded6` of 68, 102, 66 (the warehouse's outgoing list had 68, 100, 64: the cart line loaded 2 more fish per period than the warehouse list says, which is **Open**) |
| Todmorden Fishing Grounds, Produced | about 45, 61, 38 | `itemsProduced6`: 45, 61, 38 |
| Bromsgrove Quarry, Produced and Destroyed | about 70, 74, 56 and 70, 34, 24 | `itemsProduced24` and `itemsDestroyed24` with those values (24 is stone, see [cargo-ids.md](cargo-ids.md)) |
| Bromsgrove Quarry North, Produced | about 35, 65, 40 | `itemsProduced24`: 35, 65, 40; no destroyed list |
| Bromsgrove Cement Plant, Consumed and Produced | 36, 28 and 18, 14 (none in period 1) | `itemsConsumed24` 0, 36, 28 and `itemsProduced15` 0, 18, 14 |
| Bromsgrove Warehouse (cement), Incoming and Outgoing | 18, 4 and 16 | `itemsUnloaded15` 0, 18, 4 and `itemsLoaded15` 0, 16, 0; stock 6 = 22 - 16 |

- The industry rows of the table also give the output stocks and the stone destroyed at a full quarry, see [industries.md](industries.md#three-periods-clock-3785800).
- **The bars keep to clock periods when the calendar runs (604, `1707`, 0.25x, Feb 9, 1900 on screen).** The town stop's unloaded list differenced at multiples of 1,461,000 gave 105, 60, 84 and 24 for the last four periods (the last one open), the same four bars the player's chart showed, with three axis labels still reading 1/1/1900. The calendar was started at about clock 17,248,000, so the boundary at 17,532,000 (the start of the 13th period) falls in mid-January, not on a date boundary. So the year bars do not follow the date. A save at clock 19,008,600 (`1709`, 21 April 1900 on screen, 15,600 units past the 13th boundary at 18,993,000, which lies in the last hours of 20 April) showed the 13th bars final (the stop 104 and the warehouse 104 in and 104 out, up from 96, 96 and 96 in `1708`) and no bar for the 14th period yet: a bar appears with the first list entry in its period, not at the boundary. **Observed**, one chart.

## A fish chain read end to end: windows, groups, a truck queue (604)

**Observed** on 604 in the Small 1 : 3 subarctic game of [lines.md](lines.md#trip-plans-line-stops-and-vehicle-or-a-building-604), in three paused saves a few minutes apart (clock about 14.9 million, 15.1 million and 15.6 million), with the player's screenshots of every window in the fish chain taken just before each save. The chain is three fishing industries, each with a ship line to one port, a warehouse by the port, and a road line of horse carts (capacity 4) from a stop at the warehouse to a stop in town. Groups are found as in [Finding a warehouse's stock](#finding-a-warehouses-stock), with figures matched to the windows. One game, so every label is **Observed**.

### Every window matched a group

| Window | Group (cargo id 6) |
|---|---|
| Warehouse | stock 496 = unloaded 1,536 minus loaded 1,040; incoming and outgoing bars equal the period differences of the two lists |
| Port | an unloaded list of 1,589 with a loaded list of 796 that stops growing at clock 11,271,000; its unloaded bars were read off the chart and match period for period |
| Warehouse stop on the road line | one loaded list of 1,045 |
| Town stop on the road line | one unloaded list of 1,024 and a loaded list of 132 that also stops at 11,271,000 |
| Fishing industries | produced 841, 748 and 463 with stocks 178, 98 and 22 |

- The industry stock rule held for the three fishing industries ([industries.md](industries.md#later-readings-the-fish-chain-before-and-after-the-trucks)).
- **A stop's loaded list can lead an industry's by one load.** The stop lists read 967 and 670 where the industries read 957 and 650, which fits a ship still loading at the pause (a load is 10 or 20 fish). The warehouse's loaded list and the road line's warehouse-stop list have the same 121 time stamps and differ at only three early entries (2, 2 and 1 fish more at the stop).

### What reaches the warehouse and what does not

- **Where an unloading ship puts its cargo (player's observation, not tested here).** The player reports that a ship unloading at the port puts the cargo into the warehouse first, and only when that cannot take it does the ship hand cargo straight to buildings in range of the port. That fits the warehouse reading 445 to 456 of 500 while Ships 8 and 1 unloaded into it, spoiled fish included, with the stock below its cap. It would predict that once the warehouse is at 500 the port's unloaded figure stops matching the warehouse's incoming figure and the difference reaches the buildings' lists. A check: keep the warehouse full for one unloading and compare the port's Unloaded bar, the warehouse's Incoming bar and the consumers' `itemsUnloaded` lists before and after.
- The port's and the warehouse's unloaded lists have the same 111 time stamps, so one ship unloading is one entry in each. At 25 of them the port counted more than the warehouse (53 fish in all, 1 to 6 per entry).
- **13 of those 25 came with a full warehouse**: the stock before the unloading was 482 to 500 and ended at 500 to 509 (the lists stamp a load a little after the fish leave, so the end can pass 500). The warehouse takes what fits and the rest goes elsewhere, which agrees with the player's account that the warehouse comes first and buildings in range of the port take the overflow.
- **The other 12 came with room** (stocks of 160 to 481 before, 24 fish in all). So some fish leave the port's unloading without entering the warehouse even when it has space. Why (a building taking fish first, or an offset between the two lists' stamps) is **Open**.
- **Where the surplus lands was not found.** No building's `itemsUnloaded6` list has an entry at any of the 25 time stamps, and 40 building groups share stamps with the road line's deliveries. A third path, a truck loading straight from a ship, would show as stop loaded above warehouse outgoing; that gap is 5 fish, early, and none later.
- **The fish a ship line carries equal the fish at four destinations.** The ship lines' `itemsTransported6` totals (700, 362 and 152) add to 1,214, and four small groups with `itemsAtDestination6`, each keyed with a 5-digit number, add to the same: 1,024, 155, 22 and 13. The 1,024 is the town stop's unloaded total and its group's key (25,505 here) is probably that stop. What the other three keys are was not found. After 490,000 more units the two sums still agreed (1,247 and 1,247) while the shares moved, so the split is by destination, not by which ship line carried the fish.
- **Small groups with `itemsTransported6` and `itemsLost6` break an industry's losses down by key.** One industry's `itemsLost6` total of 149 equals the sum of the lost totals of seven such groups (15, 31, 21, 36, 11, 23 and 12). The keys are 5-digit numbers; whether they are consumer buildings was not checked.
- **A group keyed like a line that holds one `itemsTransported6` list** matched each ship line's transported total (key 9,640 held 700, 30,784 held 362, 29,601 held 152). The keys were not tied to line names: the lines' name slots (1,293, 1,847 and 1,853) have no arithmetic relation to them, and the two bus lines' ids from [lines.md](lines.md) had no such group.

### A stuck vehicle: the totals along the route show the queue

The player stopped one cart for a while and saved (`1659`). Counts of fish in the lists, before and after:

| Point | Before | After |
|---|---|---|
| Warehouse loaded, and the stop beside it | 1,052 and 1,057 | 1,060 and 1,065 |
| `itemsAtEdge*_c6` groups upstream (five of them) | 1,044 to 1,052 | 1,048 and 1,060 |
| The town stop's unloaded total and its `itemsAtStop1_c6` | 1,036 and 1,040 | 1,040 and 1,040 (last time unchanged) |
| One `itemsAtEdge0_c6` group at the town end | 1,040 | 1,040 (last time unchanged) |

- **Each `itemsAtEdge<d>_c<cargo>` list is a running total of that cargo passing one point of a line's route** (`d` is 0 or 1, probably the direction). The groups hold one list each, with keys 0 or 16,777,216, and sit apart from each other. The upstream ones equal what the warehouse has loaded (1,060), the downstream one equals what the town stop has received (1,040).
- **The difference between neighbours is fish in transit.** 1,060 - 1,040 = 20 fish, five carts of 4, and the screenshot showed five carts at 4 of 4 in the queue. So a queue shows up as a step in the edge totals: the segment between the last edge still at the old value and the first at the new one is where the fish wait, and the size of the step is how many.
- Which edge group is which road segment was not worked out. The lists give totals and a last time, no position.
- **Spoilage while queued is in the vehicles, not in the lists.** Three of the queued carts showed 4, 4 and 3 spoiled of 4 aboard, with an age bar of 0 or 1%, and two showed none (one with a 3% bar). The `itemsAtStopUnsatisfied1_c6` list did not change ([spoilage.md](spoilage.md#the-15-spoiled-fish-a-candidate-group-and-the-warehouse-keeps-them)).

### Releasing the stuck cart: the queue drains (604)

**Observed** in the same game, saves `1700` to `1702` (the cart released at `1700`, one cart at the town stop trying to unload at `1701`, `1702` made a few minutes later at 4x speed), compared with `1659`.

- **`1700` equals `1659` in every list read**: same fish totals, same last time (15,665,400 is the latest list time in both). The release changed nothing until time passed.
- **The queue shrinks from the downstream end, to the normal baseline.** Fish totals at the town stop and the downstream edges: 1,040 (`1700`), 1,049 and 1,052 (`1701`), 1,076 (`1702`). The upstream edges and the warehouse's loaded total stayed at 1,060 in `1701` and rose to 1,092 in `1702`. So the step between them fell from 20 fish (five carts) to 16 (four) while the warehouse kept loading: the queue drains slower than the warehouse refills it. The step does not go to zero on a working route: with nothing stuck (`1657`) the town stop had 1,024 and the warehouse had loaded 1,040, so about 16 fish (four carts) were always on the road. Read a queue as the step growing past that baseline (20 in `1659`), not as the step itself.
- **In `1701` the stop's arrivals led its unloaded total by what a cart still held.** The stop's `itemsAtStop1_c6` read 1,052 and its unloaded total 1,049, and the cart the player was watching held 3 of 4 (its window showed 3 spoiled) and was trying to unload. In `1702` the two were equal (1,076). That is the same offset as a ship still unloading ([above](#a-small-new-game-one-fish-line-three-windows-604)), and it fits the player's reading that spoiled fish can sit aboard a cart at a stop. Not tested which fish were refused.
- An "unsatisfied" list appeared at the town stop as the aged carts arrived; it and what became of the spoiled fish are in [spoilage.md](spoilage.md#unsatisfied-counts-at-the-stops-604).
- **Later saves, the baseline holds** (`1705` and `1706`, clock 17.27 and 17.72 million). The warehouse's loaded total minus the town stop's unloaded total was 16 (1,146 against 1,130) and 15 (1,176 against 1,161), about the pre-jam 16, so the route had settled at four carts in transit. The upstream edge totals read 1,144 and 1,176 at the two saves, one to three loads above the downstream edge ones (1,132 and 1,164), the spread of the carts along the road.
- **The first bar of the 14th period carries a different date label (`1710`, clock 19,268,600, 7 May 1900 on screen).** Once the first fish moved after the boundary (20 in and 20 out at the warehouse, 20 unloaded at the stop), the bars appeared and the warehouse's tooltip read "Outgoing: 20 (4/1900)". Every earlier bar's tooltip reads "(1/1/1900)" and the three axis labels still read 1/1/1900. The 14th period began on 20 April, so the label is the calendar date of the bar's period start, in a month and year form, and the old bars say 1 January 1900 because the day table had no other day then. **Observed**, one chart.

### The same chain after seven trucks replaced the carts: drained stocks, a second stop (604)

**Observed** on 604 in the same game, in two autosaves made after the player bought seven `benz1912_box` trucks for the road line (the purchase is in [models.md](models.md) and [finances.md](finances.md)): clock 45,001,200 (9 April 1914 on screen) and 46,198,800 (30 June 1915). The calendar ran at 2,000 clock units a day through the first stretch and at 16,000 in the last, so figures are given per clock unit. The production, loaded and unloaded lists keep every entry, so one late save gives the whole time series; the stop arrival lists do not (below). One game, so every label is **Observed**.

- **A truck line moves about 2.5 times what the cart line did.** The line's `itemsTransported6` list grew in steps of 4 to 16 with carts (32 to 40 fish per 365,000 units in the last year before the purchase) and in steps of 12, 24, 36 and 60 (27 and 33 once each) with the trucks (96 to 108 per 365,000). The buy window showed a capacity of 12 for the model, and every arrival at the first road stop is an entry of exactly 12; a step of 36 is three trucks stamped together. Arrivals come 30,000 to 50,000 units apart, which fits seven trucks on a cycle of about 250,000.
- **The warehouse stock fell once the trucks could take more than arrived.** Unloaded minus loaded read 500 (within 12) from 36.5 million to 43.1 million, 483 at 43.8 million, 380 at 45.0 million and 245 at 46.2 million, about 22 fewer per 200,000 units. The trucks loaded about 65 per 200,000 against about 39 arriving. At that rate the stock reaches zero about 2.2 million units after the second save; after that loads can only match arrivals. That is a projection, not read from a later save.
- **`itemsAtStop<n>_c6` is numbered by position on the line, one entry per vehicle arrival.** The truck line's group holds `itemsAtStop1_c6` (first road stop) and `itemsAtStop2_c6` (second road stop), with matching `itemsAtStopUnsatisfied<n>_c6` lists. Stop 1 entries are 12 each. A stop 2 entry is what a truck still held when it reached the second stop, so it is what the first stop did not take. The stop 2 list begins at clock 44,698,432 with an entry of 0 and its first fish are at 44,719,600. From then to 45.0 million nine trucks brought 108 fish to the first stop and 68 reached the second, so the first stop took about 40. From 45.0 million to 46.2 million, 31 trucks brought 372 and 323 reached the second stop: the first stop took about 13%, and the recent stop 2 entries are 11 or 12. Before 44.7 million the first stop took all 12 every time. This agrees with the player's reading that the first stop's demand has been met and the rest goes on; the lists show the split, not the reason.
- **The first stop's unloaded total plus the second stop's arrivals equals its arrivals, to about two loads.** At 46.2 million the first stop had 3,864 arrivals and 3,447 unloaded (417 apart) with 391 arrivals at the second stop; at 45.0 million the figures were 3,492, 3,401 and 68. The remainder (26 and 23) is the size of a couple of loads in transit. The unloaded list of the first stop is the one the sections above call the town stop's; its latest period bar read 35 against 272 in the one before (the period was 62% over).
- **The stop arrival lists keep only a recent window.** The first entry of `itemsAtStop1_c6` is a carried total (3,060 at 43,507,000 in the first save, 3,396 at 44,713,000 in the second, about 40 entries each), the older entries having been folded into it. The industries' and warehouse's lists show no such trimming (hundreds of entries from the first minutes). How the window is chosen (an entry count of about 40 here, about 280 for the `itemsAtDestination6` list of the same line) was not established.
- The fishing industries ran dry once the trucks took their output as fast as it appeared ([industries.md](industries.md#later-readings-the-fish-chain-before-and-after-the-trucks)), and spoiled arrivals stopped ([spoilage.md](spoilage.md#after-trucks-replaced-the-carts-604)).
- **The port still counts more than the warehouse takes, with room in the warehouse.** The port's unloaded total minus the warehouse's was 287 at 43,435,000, 307 at 45.0 million and 325 at 46.2 million, while the warehouse stood at 500, 380 and 245. Another 38 fish left the port's unloading without entering the warehouse when it was not full, which extends the 12 early cases [above](#what-reaches-the-warehouse-and-what-does-not). Where they land is still **Open**.
