# Statistics lists: warehouse stock and yearly bars

Where the game keeps the running totals behind the warehouse window's stock levels and its yearly incoming and outgoing bars. Checked on 604 in one game: catalog save [6417707](https://mod.io/g/transportfever3/m/333151) and later manual saves of it, compared with screenshots of the game's windows. Labels are **Observed** (matched in every save tried, not changed in the game) unless marked.

A stock is not stored as a number. The save keeps, per cargo, a list of running totals of what was unloaded and what was loaded, and the stock is their difference. The yearly bars are differences of the same totals at year boundaries. Earlier searches for the plain figures are in [entity-stats.md](entity-stats.md).

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
- A flatbed warehouse with steel 411 and sheet metal 420 in the window: a group with ids 10 and 11 and differences 411 and 420. So steel is 10 and sheet metal is 11 in this game.
- A six-slot warehouse with meat 1, cement 11, clothes 40, tinned food 2 and furniture 52 and a sixth slot with 11: a group with ids 7, 15, 27, 28, 31 and 1 and exactly those differences. The ids agree with the table in [cargo-ids.md](cargo-ids.md).
- The 15-module warehouse of [warehouses.md](warehouses.md): in two saves the group held 15 cargo ids and the differences matched all eight levels read from the window in the first save (460, 208, 108, 83, 60, 34, 15, 8) and the four that the second save left unchanged (208, 8, 49 and 15) plus the grain and stone levels read there (473 and 362).

- **A second game** ([6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1), temperate, 1937, 604; a paused re-save compared with all 23 rows of the Warehouses tab). All 15 rows with something stored had a group whose stock fit: Stored 114, 284 and 13 were rows whose only icon was fish, each a single list of id 6, and 36 was id 6 as well; 84 and 1,017 were id 9 (vegetables in the table; the rows' icon was a green gem), 995 was one list (id 2), 551 was ids 2, 12 and 29 (491, 12 and 48), 2,120 was fuel 20 (488), planks 13 (132) and id 29 (1,500), 520 was id 5 (20) plus glass 32 (500), and the three rows of 500 each had one list (ids 3, 29 and 26). Where several lists gave one total (8, 20 and 500) the row was not pinned to one group. **Observed**, one game. Ids 20, 13 and 32 agree with [cargo-ids.md](cargo-ids.md); the same row put the purple-cube cargo (a goods icon) at 29.
- **A group may have an `itemsUnloaded<c>` list and no `itemsLoaded<c>`.** Cargo that was never taken out of the warehouse has no loaded list, and the stock is then the last unloaded total. In the second game the 500 of glass and the 1,017 of id 9 were such lists. Treat a missing loaded list as 0 when taking differences (**Observed**; the first game's test cases all had both).
- **A cargo's stock can pass one module's 500.** The row with 1,017 was a 3-module warehouse (capacity 1,500, 68%) and its group had that single cargo id. So the stock is not held per module; whether several modules were set to the same cargo is **Open**.

Differences are not stocks in every group: in one save about a third of the groups with both lists (143 of 395) had a negative difference somewhere. The rule was checked on warehouses only, so a group is picked by matching window values, not by list names alone.

## Yearly bars

The incoming bar for a year is the last total in that year minus the last total before it, taken from `itemsUnloaded`, and the outgoing bar the same from `itemsLoaded`. An `itemsUnloaded19` list of the test warehouse gave, from 1985 to 2000: 120, 120, 117, 120, 120, 90, 120, 150, 90, 150, 90, 120, 120, 120, 120, 90. The window's tooltips read the same, except 135 for 1991 and 135 for 1992 where the list gave 120 and 150. The outgoing bars for 1996 and 1997 (102 and 150) matched the list of loaded totals too.

- The 15 that moved is one entry (+15) at clock time 134,411,600, which is 0.9 day after the start of 1 January 1992 read as plain calendar days from 1 January 1900. The window counted it in 1991. Moving every year boundary 3,700 to 9,600 units (0.9 to 2.4 days) after the plain calendar start fits all 15 bars; the plain start fits 14. So the game's year for a clock time is not exactly the calendar day count. The day table of [calendar.md](calendar.md#the-day-table) puts that entry on 1 January 1992 too (plain 4000 ticks per day in that game), so the bars are not binned by that table's day alone. Whether the offset comes from the calendar speed setting (all saves here were at 1.00x) or a fixed offset is **Open**.
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

- **The bars leave out the newest entry.** In `1131` the warehouse's unloaded list ended at 29 with its last time equal to the save's clock (569,800), but the window's Incoming bar showed 18, the value of the entry before. In `1147` the last unloaded entry (30, at 570,600) was well before the save's clock and the bar showed 30. The loaded list agreed with the bar in both (8 and 12). So the bar is the total up to the last entry that is older than the save's clock, while the stock uses every entry. A ship was unloading at the dock when `1131` was paused, which fits an entry made at that very tick. **Observed**, one ship, two saves. This replaces the unexplained 21 against 18 - 8 in [finances.md](finances.md#running-costs-upkeep-loan-payments-and-income-over-ten-minutes).
- **Lists grow by one entry per event time.** The fish loaded at the Fishing Grounds read times 121,749, 243,400 and 352,600 with totals 0, 30 and 40 in `1131`, and the same three plus (630,200, 50) in `1147`. Lists in these two saves held 2 to 9 entries. Each list starts with a total of 0 at a time of its own (121,749, 365,249, 486,999 and so on, not the game start), which looks like the time the list was created; the later entries are totals at the times fish were handled. **Observed**.
- **A time of 18,446,744,073,709,551,615** (u64 maximum) was the first time of the `itemsDestroyed6` list of the fishing industry: a start marker with the total 0, followed by (111,800, 6).
- **The industry's output stock follows from the same lists.** The Fishing Grounds' window showed 272 of 300 fish in `1131` and 262 in `1147`. Starting from 300, adding `itemsProduced6` (18), taking away `itemsDestroyed6` (6) and the fish loaded (`itemsLoaded6`, 40 in `1131` and 50 in `1147`) gives 272 and 262 in both saves. A ship was loading its 10 fish at the platform when `1147` was made, and those 10 had already left the stock. So an industry's stock is not stored as a plain number either: it is worked out from running totals plus a start value, here the output capacity (300). **Observed**, one industry in two saves. Why a start of 300 sits with 6 destroyed fish (the stock was full at the beginning of the game?) is **Open**. The production figure of 39 in the window was not found.
- **When the destroyed fish were destroyed.** The Fishing Grounds' production list read (time, total): (111,800, 6), (223,400, 9), (335,000, 12), (446,800, 15), (558,400, 18), so the first pulse was 6 fish and each later one 3, about 111,600 units apart. Its destroyed list had one entry, (111,800, 6): all of the first pulse and none of the later ones. Ships had loaded 30 fish by the next list entry (243,400), but the lists give the time of an entry, not of each loading, so the stock at each pulse cannot be read. That fits "a full output stock destroys what it cannot hold", and the start value of 300 above is the capacity, but the one event cannot tell this from other readings (a spoil timer, a rule for the first pulse). **Open**. The game's own type files show that stocks of industries and warehouses carry a quality and a spoiled count (`numSpoiled` and `quality` in `CargoUtil.StockConfig`, `base/tealdef/gui/main/cargo_util.d.tl`), and that the engine destroys cargo when a line's stop is set to force-unload at a full input stock (`forceUnload` in `api/tealdef/api/engine.d.tl`). Neither file says what the `itemsDestroyed` total counts. A test: leave an industry's stock full with no ship loading for one cycle and compare the destroyed total with the production pulses.

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

- **Output stocks again follow `start + produced - destroyed - loaded`.** The Fishing Grounds read 38 of 300: 300 + 144 produced - 6 destroyed - 400 loaded. The quarry read 400 of 400: 400 + 200 - 128 - 72. The start value was the output capacity both times, as in the first test above.
- **The quarry fits "a full stock destroys what it cannot hold".** In period 1 nothing was loaded and the stock began full at 400, so all 70 stone produced were destroyed (70 produced, 70 destroyed). In periods 2 and 3, once carts loaded 44 and 28, only 34 of 74 and 24 of 56 were destroyed. The quarry that was not full (North, 140 of 400) destroyed nothing. This is the test proposed above, made by accident, and it fits that reading better than a spoil timer, because the destroyed amount follows the stock being full and not the age of the cargo. **Observed**, two quarries and one fishery, still not a proof: the engine's rule is not in any file the project reads.
- Two other lists in these saves had identical produced and destroyed values (18 at 256 and 378, 12 at 176, with periods [100, 98, 58], [147, 147, 84] and [68, 68, 40]): industries of other cargos that were probably not served (their windows were not looked at), so everything produced was destroyed. They would agree with the same reading. **Observed**.

## A quarry's destroyed stone pulse by pulse, and industries that start empty (604)

**Observed** on 604 in the same new game at clock 5,997,000 (save `1246`), with the windows read in the paused game right after the save.

- **The rule holds again.** The Bromsgrove Quarry read 396 of 400. Its lists end at 353 produced (`itemsProduced24`), 205 destroyed (`itemsDestroyed24`) and 152 loaded (`itemsLoaded24`), and 400 + 353 - 205 - 152 = 396. The Fishing Grounds that had been served read 0 of 300: 300 + 281 produced - 6 destroyed - 575 loaded = 0.
- **Destroyed stone against a stock that caps at 400.** The produced list has one entry per pulse (about 106,000 units apart, 5 to 18 stone each, the size grows with the booster percentage). Replaying the three lists with a stock that starts at 400, drops by what was loaded and is cut at 400 after each pulse gives the stone each pulse should have destroyed. The replay's final stock is 396, the same as the window, and its destroyed total is the same 205. Of the 40 pulses where anything was destroyed or predicted to be, 24 match exactly. They include all 13 of the first period (nothing loaded, stock full, destroyed equals produced) and the pulses where the stock sat at 399 or 400 (4 destroyed of 5 at stock 399). The other 16 differ by 1 to 6 stone and the differences cancel in neighbouring pulses (3 destroyed against 7 predicted, then 3 destroyed against 0 predicted, and so on). The loaded list stamps a total when a cart finishes, and stone leaves the stock when loading starts, so a stamp that lags the removal would move stone between neighbouring pulses. That fits, and it was not tested. **Observed**: this is the best support yet for "destroyed means what did not fit", but it is not proven. A direct test is a save made while a cart is loading at a full quarry.
- **Some industries start with an empty output stock.** Three more fishing industries (named with the suffixes E, S and W) read 114, 93 and 114 of 300 fish, and in each the stock equals its produced total (114, 93, 114) with no destroyed or loaded list at all. That works only if the start value was 0, not the capacity. The quarry "North" of the first test (140 of 400, nothing destroyed) fits the same. The industries that start at their capacity are the ones the map made.

## When an industry's lists begin, and industries that appear in play (604)

**Observed** on 604 in the same new game, reading the `itemsProduced<c>` list of every industry in the 12 manual saves and 7 autosaves of the game (the last at clock 5,997,000).

- **Two kinds of first entry.** The industries the map made have a list that starts with the marker time 18,446,744,073,709,551,615 and total 0, then the first production pulse (the seven lists of the new game, cargo ids 1, 6 (fish), 12, 18 and 24 (stone); the first pulses are at 88,200 to 120,400). The others start with a real time and total 0 and then a pulse a little later. There were 10 of those, plus the cement plant's cement list (below).
- **The creation times are half-year boundaries.** The real start times are 730,499, 1,460,999, 2,191,499, 2,921,999, 3,652,499 (three industries at once), 4,382,999, 5,113,499 and 5,843,999: every multiple of 730,500 minus 1, up to the save's clock. 730,500 is half of the 1,461,000-unit year ([finances.md](finances.md#periods)). So in this game a new industry appeared at each of the first 8 half-year boundaries (10 industries in all), and none between them. The first pulse of the fish industries followed 1 to 120 units after the boundary (1,461,000; 2,191,600; 3,652,600), so the industry exists from the boundary on. The quarry's first pulse came 112,000 units after its boundary (842,400), the first stone pulse of the stone industry created at 5,843,999 came 120,600 after it. The creation check therefore looks to run on a half-year tick, which fits the player's account that new industries appear depending on how the game is going. What decides whether one appears (the check ran 8 times with 10 industries; the chance, if any, was not seen) is **Open**.
- **West, South and East are three of them, in that order.** The fish lists created at 1,460,999, 2,191,499 and 3,652,499 are the fishing industries West, South and East. The stocks alone did not say so (West and East both read 114 fish); the production figures did (West 36, a pulse of 3 fish, and East 71, a pulse of 6), and the spawn notifications in the save settle it ([notifications.md](notifications.md#industry-spawn-notifications-604)). The three were created at 1,461,000, 2,191,500 and 3,652,500 and started with an empty stock, as above. An earlier version of this note had East and West the other way round. The other creation times belong to a quarry (stone, "North"), a quarry West at 5,844,000, an oil platform East at 2,922,000, two crop farms and a coal mine and an iron ore mine (the cargo ids 1, 18, 21 and 22 are not in [cargo-ids.md](cargo-ids.md) yet).
- **The cement plant's list is the exception.** Its `itemsProduced15` list starts at 1,947,999, one tick before 1,948,000 (16 months of 121,750), not on a half-year boundary, with its first pulse at 2,052,400. The plant is one of the map's industries. Its cement list was probably created when stone first reached it (see the next bullet). **Open**.
- **Only producing industries have a list.** The Industries tab of the overview listed 23 industries: 17 primaries (three crop farms, a logging camp, three quarries, a coal mine, an iron ore mine, five fishing grounds, two oil platforms, an oil well) and 6 secondaries (a cement plant, saw mill, canning factory, steel mill, livestock farm, oil refinery). There were 18 `itemsProduced` lists: one per primary and one for the cement plant, the only secondary that had been supplied (the other five showed input 0 and output 0). So the 10 industries created in play are all primaries, and 7 primaries and 6 secondaries made up the map. A secondary's list is created when it is first supplied, which fits the cement plant's list starting at 1,947,999. **Observed**, one game.
- **A new game's lists first appear in the saves when they were created, no earlier.** In the manual saves made in order the first save holding each start time was the first one made after it (730,499 in `1208`, 1,460,999 and 2,191,499 in `1220-more-lines`, 2,921,999 and 3,652,499 in `1236`, the last three in `1246`). Closed industries were not seen to leave their lists behind or vanish; the game was not played through a closure. **Open**.

## Spoiled cargo and `itemsLost` (604)

**Observed** on 604 in the Small 1 : 3 game, save `1401` (clock 10,026,200, paused) with the player's screenshots from the two minutes before it, and `1339` (6,428,600) for comparison. **Open**: where the spoiled count is kept.

- **What the game's windows show.** Ship 8 (a `sydfart` on a fishing line, stuck at the port, 0 km/h) read 15 of 20 fish aboard with a sad-face counter of 15 beside it (presumably the spoiled count, the interface's `numSpoiled`, so all 15 aboard); Ship 4 (a Canadian Trawler unloading at the same terminal) read 3 of 10 fish and no counter. The port had one terminal of type Passenger and Cargo with all three fishing lines on it. A cargo cart on the road line read 4 of 4 and the line 16 of 28, with no counter. The fish in the warehouse read 445 of 500.
- **What the game's files say.** The user interface reads a spoiled count (`countBad`) and an average quality for a vehicle, a line, a stop or a stock from engine calls (`gui/main/cargo_util.tl` in `base/content/gui.zip`, `numSpoiled` and `spoiledCount` in `base/tealdef/gui/main/cargo_util.d.tl`). The fish definition (`cargos/fish/fish.cargo.lua` in `base/content/cargos/fish.zip`) holds a delivery time of 1,125 seconds and decay values that its price function (`constantFn`) does not use. How the engine decides a unit is bad was not read from a script.
- **Not in the stream by name.** The decompressed `1401` stream held no `spoil`, `quality`, `decay` or `countBad` string, and there is no `itemsLost6` list (6 is fish, see [cargo-ids.md](cargo-ids.md)). So spoilage is either per-unit data inside the vehicle and stock records or a number derived from times, and neither was found.
- **`itemsLost0` grew.** In `1339` the list (cargo id 0, a cargo not in the id table) held (4,017,749, 0) and (4,137,800, 3). In `1401` it also held (9,715,200, 5), (9,852,800, 14) and (9,957,000, 17): 14 more lost items, all after the third autosave of the day (clock 9,046,200) and 104,200 to 137,600 units apart. Whether these are the same units as the spoiled fish, or another cargo, was not settled; the cargo id 0 does not fit fish. The list appears in several copies of one group, as the other `items` lists do.
- **The Delivery Time tab.** The company window's "Delivery Time" tab draws one bar per cargo type of the game, "the expected delivery time", with a note that food has a low expected time, that bulk cargo is less time sensitive and that late delivery affects town ratings. Each bar shows its value in a tooltip. **Observed**, one game, with these tooltips read by the player, each equal to the cargo file's `timeToDeliverInSeconds` (in the `cargos/` archives of `base/content`) times 1.5:

| Bar (icon) | Tooltip | File value x 1.5 |
|---|---|---|
| meat | 22 m 30 s | 900 s = 1,350 s |
| fish | 28 m 7 s | 1,125 s = 1,687.5 s |
| grain (ears of wheat) | 32 m 9 s | 1,286 s = 1,929 s |
| fertilizer (leaf sack) | 37 m 30 s | 1,500 s = 2,250 s |
| flask icon, 1,800 s class | 45 m 0 s | 1,800 s = 2,700 s |
| concrete | 56 m 15 s | 2,250 s = 3,375 s |
| drop icon (oil class, 3,000 s) | 1 h 15 m | 3,000 s = 4,500 s |
| stone, and the orange (ore) and light blue-grey bars beside it | 1 h 52 m each | 4,500 s = 6,750 s (1 h 52 m 30 s) |

  The five bars at the 3,000 s class stand at the 1 h 15 m level, as the drop icon's tooltip says. The three tallest bars (the 4,500 s class) are clipped at the 1 h 50 m top of the axis, but their tooltips still give the real value, 1 h 52 m, so the clipping only affects the drawing. The cargo behind a bar is told by its icon and by the number, not by a name: the "concrete" bar has the 2,250 s of the `cement` file, which `sawdust`, `dyes`, `vehicles`, `tools`, `machines`, `glass` and `fuel` share, and the flask is one of the 1,800 s cargos. Where the 1.5 comes from is **Open**: the player's view is that the game difficulty may also change the spoil time, so 1.5 may hold only for this game's settings. The save's `townConfig.sensitivityCargoDelivery` was 4.0 (with the other settings listed in [settings.md](settings.md)), and no test changed any setting. A test would be the same tab read in a game made with another difficulty preset, or with that one slider moved.
- **Specialized and universal warehouses (player's observation, not read from the save).** The player reports that in a specialized warehouse the spoil timer of the cargo stops, and in a universal warehouse it keeps running. Not tested here; the warehouse modules are in [warehouses.md](warehouses.md).
