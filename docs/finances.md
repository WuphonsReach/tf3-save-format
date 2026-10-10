# Finances tab and the money journal

How the company window's Finances tab (Earnings Details and Summary) lines up with the money journal. The journal's layout, its category enums and how to find it are in [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md) and are not repeated here. Here only the link to what the game shows is covered.

Checked on 604, one game: catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) saved again with the game paused (calendar speed 0.50x, no mods, no loan taken at the time). 585 and 601 were not looked at.

## Finding the journal

- **Confirmed**: the journal in this save has 25,570 bookings, and their amounts sum to the balance, which equals the header money. That matches FORMAT.md, and the 21-byte booking (`i64` time, `i64` amount, five `u8` categories) read as described there.
- Find it by trying each u32 count `n` with the header money sitting `n * 21 + 4` bytes before the balance's end: the sum of the amounts must equal the balance. The header money also appears as an i64 in a second place in the stream, so check the sum.
- The first booking is time 0 with +4,000,000, the starting capital. Here its type byte is 0 (`LOAN`), with construction `OTHER`, maintenance `OTHER`, other 0 and carrier `OTHER`. FORMAT.md says the starting capital is booked with type `OTHER`, so the type may differ between versions or settings. **Observed**, one save.
- The `time` field is the game clock of [calendar.md](calendar.md): the game's own milliseconds, 4000 per game day at calendar speed 1.00x. It is not milliseconds of real time. **Observed**: the last booking sat at 383,513,600, and the newest timestamps in the Lua states of the same save were 383,512,800 to 383,515,000.
- Bookings are in time order. The journal is not the same data as the long run of balance samples ([below](#the-balance-history-run)).

## Periods

- **Confirmed**: each column of the Earnings Details table is one period of 1,461,000 clock units (365.25 stored days), and the period boundaries are multiples of 1,461,000. For this save the four columns were the bookings with `time` from 378,399,000, 379,860,000, 381,321,000 and 382,782,000 (multiples 259 to 262), the last one still open.
- At calendar speed 0.50x one period shows as six months, which is why the columns read like half years. At another speed the span in game dates would differ. Not tested. **Open**.
- The Earnings figure of a period is the sum of every booking except type `LOAN`. In all four periods the sum matched the tab to the dollar (24,828,167, 27,855,151, 32,872,616 and 18,966,088). The Bank Account row is the balance at the end of the period.

## Rows against the booking categories

**Confirmed** for every row of the period 5/89 to 10/89, where each tab figure equalled the sum of the bookings in the listed categories:

| Tab row | Bookings |
|---|---|
| Road, Revenue | `INCOME` with carrier ROAD and TRAM together |
| Road, Running Costs Vehicles | `MAINTENANCE` / `VEHICLE`, carrier ROAD + TRAM |
| Road, Maintenance Vehicles | `MAINTENANCE` / `VEHICLE_MAINTENANCE`, carrier ROAD + TRAM |
| Road, Upkeep Roads + Upkeep Buildings | `MAINTENANCE` / `INFRASTRUCTURE`, carrier ROAD + TRAM (the two rows added up) |
| Rail and Water, Revenue, Running Costs Vehicles, Maintenance Vehicles | the same three categories, with carrier RAIL or WATER |
| Rail, Upkeep Tracks + Upkeep Buildings | `MAINTENANCE` / `INFRASTRUCTURE`, carrier RAIL (the two rows added up) |
| General, Upkeep Warehouses | `MAINTENANCE` / `INFRASTRUCTURE`, carrier OTHER |
| Investments, Roads | `CONSTRUCTION` / `STREET` |
| Investments, Tracks | `CONSTRUCTION` / `TRACK` (none in this period) |
| Investments, Infrastructure | `CONSTRUCTION` / `STATION` and `CONSTRUCTION` / `OTHER` together (the latter was positive, +45,362) |
| Investments, Vehicles | `ACQUISITION` |
| Loan Interest, Loan Transactions | `INTEREST` and `LOAN`. The journal holds 55 of each overall, none in the four periods shown, so these rows read $0 and the match is trivial |

- Trams are counted under Road, so the tab has no Tram row. Air was empty (no AIR bookings).
- The tab splits the infrastructure upkeep into roads and buildings (or tracks and buildings). The booking has no field that does that, so the split is not in the five category bytes. Only the sum was checked. **Open**.
- The bookings in an old period are far fewer than in a recent one: about 220 in each of the two earliest periods above against about 10,000 in each of the last two. Older bookings seem to be merged. **Observed**, so do not use the booking count as a measure of activity.

## A new game's journal

**Observed** on 604, one new game (Small 1 : 3 subarctic, Normal difficulty, seven mods, paused at 1900-01-01) saved four times:

- A new game starts with header money 0 and **no bookings**: no starting capital is booked, unlike the catalog save above. The journal is then an empty list with balance 0, and the stream holds over a thousand zero-balance journal-shaped runs, so the search for a journal by balance ([above](#finding-the-journal)) finds many and the tf3-save-editor CLI calls money read-only.
- After a loan was taken, the journal held one booking, type `LOAN`, amount +18,000,000, and the header money was 18,000,000. The search then found exactly one journal.
- Placing the free Boathouse asset (price "Free" in the build menu) changed neither the journal nor the header money.
- Placing the depot-type Boathouse (price $80,000 in the build menu) added one booking of -81,857, construction type "depots (Water)". The extra 1,857 over the menu price is the cost of the terrain work done for the foundation (reported by the player). The header money fell to 17,918,143, the sum of the two bookings.
- Setting the balance with the editor's `money --set` adds one `OTHER` booking for the difference and rewrites the header money. **Confirmed** on 604, one save: the edited save loaded and the bottom bar's Account read the new balance (2,511,188,193). The Finances tab showed the figures below, so the journal is what the windows read, and no other copy of the balance had to be changed:

  | Window | Shown | Source |
  |---|---|---|
  | Earnings Details, Other | 2,493,270,050 | the added `OTHER` booking |
  | Earnings Details, Investments | -81,857 | the depot booking |
  | Summary, Earnings (also the bottom bar) | 2,493,188,193 | those two, the loan booking left out |
  | Loan Transactions, Debt | 18,000,000 and -18,000,000 | the `LOAN` booking and the loan itself |
  | Bank Account, Account | 2,511,188,193 | the sum of all three bookings |

  The Overview chart "Revenue" bar read 2,493,270,050 (the `OTHER` booking counts as revenue) and "Debt + Cash" 2,493,188,193, the balance less the 18,000,000 debt. Header money was not checked in the game.

### A first build-out, row by row

**Observed** on 604, the same game after buying two small ports, two ship depots, a road depot, a specialised fish warehouse, a truck stop, three road vehicles and four ships, and building a short road (calendar paused at 1 January 1900, so every booking carries the same time, 1000). The journal grew from 3 to 20 bookings (editor labels in quotes), and every figure on the company window's Finances tab matched the bookings in its category to the dollar:

| Tab row | Value | Bookings |
|---|---|---|
| Investments, Roads | -66,002 | "Construction - streets (Road)": 30,000 + 30,000 + 6,002 |
| Investments, Infrastructure | -2,183,875 | "stations" (Water 144,973 and 145,484; Road 74,664) and "depots" (Water 81,857, 838,203 and 700,522; Road 198,172) |
| Investments, Warehouses | -305,973 | one "Construction - warehouses" booking |
| Investments, Vehicles | -1,206,864 | "Vehicle purchase": 3 x 60,912 (Road) and 4 x 256,032 (Water) |
| Investments | -3,762,714 | the four rows above |
| Summary, Earnings | 2,489,507,336 | all bookings except `LOAN`: the +2,493,270,050 `OTHER` booking less Investments |
| Account | 2,507,507,336 | Earnings plus the 18,000,000 loan |

- Depots count under Infrastructure on the tab, not under a row of their own. The existing table above lists only `STATION` and `OTHER` for that row, so the depot booking's category value was not read from the bytes here. **Open**.
- Investments, Warehouses is a row the table above lacks. It held one booking (305,973), for the one warehouse the player bought, a specialised fish warehouse (so the row is not limited to the general warehouse). **Observed**, one build.
- The header money after saving (2,507,507,336) equalled the Account figure.

### Running costs, upkeep, loan payments and income over ten minutes

**Observed** on 604, the same game after about 570 seconds of play (the header's clock at 569,800, the date still 1 January 1900 with the date stopped, see [calendar.md](calendar.md)): the journal held 210 bookings. The loan of 18,000,000 and the first build-out were still in it, then:

- **Upkeep comes in a batch every 60,000 clock units.** There were 9 batches (at 60,000 to 540,000), each of 20 bookings: 11 `MAINTENANCE` / `INFRASTRUCTURE` (5 road, 5 water, 1 carrier `OTHER` for the warehouse), 2 vehicle maintenance (one road, one water) and 7 vehicle running costs (one per vehicle). The period is in clock units, not days: the date did not move while these were booked. The sums per batch ran from -23,886 to -25,158.
- **A batch is a fraction of a year.** The warehouse's window showed $50,000/Year, and its booking per batch (carrier `OTHER`) was -2,053. A year is 1,461,000 units ([above](#periods)), so 24.35 batches make a year, and 24.35 x 2,053 = 49,990, within rounding of the window. **Observed**, one warehouse. The same window showed 21 fish in stock with 18 incoming and 8 outgoing in its chart, which do not add up (18 - 8 = 10); the chart bars may count something else than the stock does. **Open**.
- **Per-booking values.** Infrastructure and vehicle maintenance repeated exactly in every batch (for example a water depot -4,106, road vehicles -315 in total, water vehicles -1,755). Running costs varied between batches: a ship booked -1,752 in most, -1,472, -1,402 or -1,262 in some, and a horse cart -284 to -417. The bookings carry no vehicle or line id (the five category bytes are all there is), but within a batch they come in vehicle order: summed over the nine batches, the fourth water running-cost booking came to 15,138, which is exactly Ship 4's last-year running costs in its window (the first three summed to 15,278, 14,998 and 14,508). **Observed**, one ship, but a match to the dollar. So a vehicle's yearly running costs can be rebuilt from the journal by its place in the batch. Why one batch's cost for a vehicle differs from another's is **Open** (a vehicle not moving for part of the period is a guess).
- **Loan payments.** First at 122,800, then every 121,800 units (the loan was booked at 1,000, so the first fell 121,800 after it): four so far, each a `LOAN` booking of -214,286 plus an `INTEREST` booking of -19,286. 214,286 is 18,000,000 / 84. The interest stayed 19,286 on all four, so it did not fall as the principal was repaid, at least over four payments.
- **Income arrives as one booking per carrier, at one time.** Two bookings at 552,000: Income (Road) +4,554 and Income (Water) +20,771. 552,000 is not a batch time (540,000 and 600,000 are). The booking has no cargo, line or town field. The road line's window showed income 4,554 and the ship line's 20,771, exactly the two bookings.
- **Line windows against the journal.** Line 1 (three horse carts) showed income 4,554, running costs 9,792, balance -5,238; Line 2 (four ships) showed 20,771, 59,922 and -39,151. 9,792 and 59,922 are the sums of all road and all water vehicle-running-cost bookings. So a line's balance is income minus vehicle running costs only, with vehicle maintenance and infrastructure upkeep left out. With one line per carrier this is a match by carrier. Whether it holds with several lines per carrier is untested. **Observed**, one save.
- **One delivery paid both lines.** In this game the player saw no income until the fish had left the cart at the town, and then both lines showed income, although the ships' leg ends at a warehouse. The journal fits that: one pair of income bookings, one per carrier, at one time, so a single delivery was paid out split between the road and the water carrier. The journal cannot say whether the payment came at unloading or when the cart departed, or how the split is worked out (82% water here). **Observed**, one delivery.
- Vehicle age in the line window (9m 28s) is the time since purchase in clock units read as seconds: 569,800 - 1,000 units is 568.8 s. **Observed**.
- The header money (2,506,375,464) equalled the journal balance, which equals the previous balance less these bookings.

## The balance history run

**Observed** on 604, catalog save 6428935 (account 3,382,382,812 in the game) loaded, paused at once and saved again. In the stream, far in front of the Lua states, there is a long run of i64 values that each sit within a few percent of the one before and read as a balance history. Three of them, 12 entries apart, equalled the Bank Account row for the last three finished periods on the Finances tab (3,302,688,957, 3,330,544,108, 3,363,416,724). The tab shows six-month periods, so that is about two entries a month. The last entry of the run was 3,382,379,554, which is the header money of the original save and not the re-save's, so the history is sampled and the live balance is not appended to it. It is not the money journal that FORMAT.md describes: that is a separate run of 21-byte bookings ([above](#finding-the-journal)). Find it by searching for one of the period-end figures as 8 little-endian bytes. **Observed**, one save.