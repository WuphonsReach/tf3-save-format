# Statistics lists: the yearly bars

How the bars in the warehouse, station, line and industry windows are made from the lists of [statistics-lists.md](statistics-lists.md): a bar is the change of a list over one period of 1,461,000 clock units, not over a calendar year. Checked on 604 in the [Small subarctic game](test-games.md#small-subarctic-game) and in one catalog save (catalog save [6417707](https://mod.io/g/transportfever3/m/333151) for the first rule).

## In short

- **A bar is the last list total in a period minus the last total before it, for `itemsUnloaded` (incoming) and `itemsLoaded` (outgoing) (Observed, every window tried).** Industry windows use `itemsProduced`, `itemsDestroyed` and `itemsConsumed` the same way; line windows use `itemsTransported`.
- **The periods are 1,461,000 clock units (365.25 stored days), at multiples of 1,461,000, and do not follow the date (Observed).** Stopping the date or running the calendar at 0.25x changed nothing; the axis labels keep reading 1/1/1900 and a later bar's tooltip carries the date of its period start.
- **A bar appears with the first list entry in its period, not at the boundary (Observed, one chart).** It excludes any entry newer than the save's clock, so a ship still unloading at the pause shows one entry fewer than the stock does (Observed, one ship, two saves).
- **A list starts with a 0 total at a time of its own (probably its creation), and the first time of one list was the u64 maximum as a start marker (Observed).**
- **Open:** which of two groups with equal `itemsUnloaded` totals is the station and which the warehouse, and why one cart line loaded 2 more fish per period than the warehouse list says.

## Yearly bars

The incoming bar for a year is the last total in that year minus the last total before it, taken from `itemsUnloaded`, and the outgoing bar the same from `itemsLoaded`. An `itemsUnloaded19` list of the test warehouse gave, from 1985 to 2000: 120, 120, 117, 120, 120, 90, 120, 150, 90, 150, 90, 120, 120, 120, 120, 90. The window's tooltips read the same, except 135 for 1991 and 135 for 1992 where the list gave 120 and 150. The outgoing bars for 1996 and 1997 (102 and 150) matched the list of loaded totals too.

- The 15 that moved is one entry (+15) at clock time 134,411,600, which is 0.9 day after the start of 1 January 1992 read as plain calendar days from 1 January 1900, and the day table of [calendar.md](calendar.md#the-day-table) puts it on 1 January 1992 too. The window counted it in 1991. The bars are periods of 1,461,000 clock units, not calendar years ([below](#the-yearly-bars-are-periods-of-1461000-units-604)): 92 x 1,461,000 is 134,412,000, 400 units after the entry, so it falls in period 91, the 1991 bar. **Observed**.
- The 2000 bar read 60 in the saves with the ship not yet unloaded and with 17 of 30 unloaded, and 90 once all 30 were in. The list already held 2,754 (77 for the year) in the middle save, so the bar lagged the list by the unloading in progress. Observed once.
- The station window's unloaded bars equalled the warehouse's incoming bars. Two groups 30 KB apart carry the same `itemsUnloaded` and `itemsUnloaded19` totals, which would explain it; only the one that also has `itemsLoaded19` gave the stock. Which of the two is the station and which the warehouse is **Open**.
- A station window's Loaded and Unloaded bars are the same differences per 1,461,000-unit period, taken from the station's `itemsLoaded<c>` and `itemsUnloaded<c>`. In the [Small subarctic game](test-games.md#small-subarctic-game) (604, April 1919) the window of the station by the cement warehouse showed the five newest pairs as about 48 and 90, 126 and 96, 72 and 96, 126 and 90, 50 and 84, newest first. Two groups with the same `itemsLoaded15` and `itemsUnloaded15` totals gave exactly those figures, the newest pair being the period still open. **Observed**, bars read by eye.

## Evidence and tests

### A small new game: one fish line, three windows (604)

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

### The yearly bars are periods of 1,461,000 units (604)

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
