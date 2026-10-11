# Finances tab and the money journal

How the company window's Finances tab (Earnings Details and Summary) lines up with the money journal. The journal's layout, its category enums and how to find it are in [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md) and are not repeated here. Here only the link to what the game shows is covered. How upkeep and vehicle running costs are booked is in [running-costs.md](running-costs.md).

Checked on 604, one game: catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) saved again with the game paused (calendar speed 0.50x, no mods, no loan taken at the time). 585 and 601 were not looked at.

## Finding the journal

- **Confirmed**: the journal in this save has 25,570 bookings, and their amounts sum to the balance, which equals the header money. That matches FORMAT.md, and the 21-byte booking (`i64` time, `i64` amount, five `u8` categories) read as described there.
- Find it by trying each u32 count `n` with the header money sitting `n * 21 + 4` bytes before the balance's end: the sum of the amounts must equal the balance. The header money also appears as an i64 in a second place in the stream, so check the sum.
- The first booking is time 0 with +4,000,000, the starting capital. Here its type byte is 0 (`LOAN`), with construction `OTHER`, maintenance `OTHER`, other 0 and carrier `OTHER`. FORMAT.md says the starting capital is booked with type `OTHER`, so the type may differ between versions or settings. **Observed**, one save.
- The `time` field is the game clock of [calendar.md](calendar.md): the game's own milliseconds, 4000 per game day at calendar speed 1.00x. It is not milliseconds of real time. **Observed**: the last booking sat at 383,513,600, and the newest timestamps in the Lua states of the same save were 383,512,800 to 383,515,000.
- Bookings are in time order. The journal is not the same data as the long run of balance samples ([below](#the-balance-history-run)).

## Periods

- **Confirmed**: each column of the Earnings Details table is one period of 1,461,000 clock units (365.25 stored days), and the period boundaries are multiples of 1,461,000. For this save the four columns were the bookings with `time` from 378,399,000, 379,860,000, 381,321,000 and 382,782,000 (multiples 259 to 262), the last one still open.
- At calendar speed 0.50x one period shows as six months, which is why the columns read like half years. At another speed the span in game dates would differ. The statistics bars keep the same 1,461,000-unit periods at 0.25x and with the date stopped ([statistics-lists.md](statistics-lists.md#the-yearly-bars-are-periods-of-1461000-units-604)); this tab's columns were not read at another speed. **Open**.
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
- The bookings in an old period are far fewer than in a recent one: about 220 in each of the two earliest periods above against about 10,000 in each of the last two. Older bookings are merged (next bullet). **Observed**, so do not use the booking count as a measure of activity.
- **Old bookings are merged by month** (604, the new game below, save `1246` at clock 5,997,000). Before 4,560,000 the journal holds four infrastructure bookings per 121,750 units, one per carrier, each the sum of what two 60,000-unit batches booked (a warehouse is -4,106 a month, two are -8,212). 121,750 is a twelfth of the 1,461,000-unit year. The first batch kept in full is at 4,560,000, so bookings more than one year (1,461,000 units) older than the save are merged. **Observed** in this one save: where exactly the cutoff sits (a year before the clock, or a fixed count) is **Open**.
- **Much older bookings are merged by year.** In saves of the same game at clock 58.6 to 63.2 million (1917 and 1918, calendar at 0.25x) the old vehicle purchase bookings sit at multiples of 1,461,000 (39,447,000, 40,908,000, 42,369,000), the start of the 1,461,000-unit period they fall in, one per category and period: the 42,369,000 booking of -2,249,317 is the net of the seven trucks bought and seven carts sold at 43,361,200 ([below](#selling-a-vehicle-is-a-positive-booking-in-the-purchase-category-604)). So merging goes on past the monthly step. Where the yearly step begins was not read. **Observed**, one game.

## A new game's journal

**Observed** on 604, the [Small subarctic game](test-games.md#small-subarctic-game) when new (paused at 1900-01-01), saved four times:

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

### Loan payments and income over ten minutes

**Observed** on 604, the same game after about 570 seconds of play (the header's clock at 569,800, the date still 1 January 1900 with the date stopped, see [calendar.md](calendar.md)): the journal held 210 bookings. The loan of 18,000,000 and the first build-out were still in it. The upkeep and running-cost batches of the same journal are in [running-costs.md](running-costs.md#upkeep-and-running-costs-are-booked-in-batches-604). Then:

- **Loan payments.** First at 122,800, then every 121,800 units (the loan was booked at 1,000, so the first fell 121,800 after it): five by the next save (the fifth at 610,000, as predicted), each a `LOAN` booking of -214,286 plus an `INTEREST` booking of -19,286. 214,286 is 18,000,000 / 84. The interest stayed 19,286 on all four, so it did not fall as the principal was repaid, at least over four payments.
- **Income arrives as one booking per carrier, at one time.** Two bookings at 552,000: Income (Road) +4,554 and Income (Water) +20,771. 552,000 is not a batch time (540,000 and 600,000 are). The booking has no cargo, line or town field. The road line's window showed income 4,554 and the ship line's 20,771, exactly the two bookings.
- **Line windows against the journal.** Line 1 (three horse carts) showed income 4,554, running costs 9,792, balance -5,238; Line 2 (four ships) showed 20,771, 59,922 and -39,151. 9,792 and 59,922 are the sums of all road and all water vehicle-running-cost bookings. So a line's balance is income minus vehicle running costs only, with vehicle maintenance and infrastructure upkeep left out. With one line per carrier this is a match by carrier. Whether it holds with several lines per carrier is untested. **Observed**, one save.
- **One delivery paid both lines.** In this game the player saw no income until the fish had left the cart at the town, and then both lines showed income, although the ships' leg ends at a warehouse. The journal fits that: one pair of income bookings, one per carrier, at one time, so a single delivery was paid out split between the road and the water carrier. The journal cannot say whether the payment came at unloading or when the cart departed, or how the split is worked out (82% water here). **Observed**, one delivery.
- Vehicle age in the line window (9m 28s) is the time since purchase in clock units read as seconds: 569,800 - 1,000 units is 568.8 s. **Observed**.
- The header money (2,506,375,464) equalled the journal balance, which equals the previous balance less these bookings.

### The bottom bar's Earnings is the current period's

**Observed** on 604, the same game at clock 2,246,600 (journal 1,718 bookings, balance 2,495,976,310, the same figure as the Account on the bottom bar). The bar's Earnings read -4,938,203 although the all-time sum of bookings other than `LOAN` was 2,481,833,458. The sum of those bookings from 1,461,000 (the start of the period the clock is in, see [Periods](#periods)) was exactly -4,938,203. So the bar shows the current period, and in the first game of this series (clock below 1,461,000) it showed what looked like a total. The bar's cargo figure (124) was `cargoDeliveredCount` and its passenger figure (0) `passengerTransportedCount` ([script-states.md](script-states.md#counters-and-achievements)). 18 loan payments (3,857,148 in all) had been made, so the loan sum stood at 14,142,852.

### A new game's first batch of bookings while paused

**Observed** on 604, the same game a quarter of an hour of play later (save at clock 1,121,000, the calendar stopped, 477 bookings, money 2,503,056,661). The player added vehicles to the fish lines, bought the first buses and trucks, built a quarry-to-concrete-plant line and took a subsidy:

- **Everything done while paused is booked at the paused tick.** 40 bookings share the time 1,095,400: 5 depots, 5 stations, a warehouse, 5 pieces of street, 25 vehicle purchases and the subsidy payment. The game had been paused with the clock at 1,095,400 while the player built, so building is allowed while paused and the booking time is the clock, not the order. The first build-out ([above](#a-first-build-out-row-by-row)) was booked in the same way at time 1,000. **Observed**, two paused sessions.
- **Vehicle purchases are one booking each**, in groups of equal price: 4 x 60,903 (the horse carts added at 887,400), then at 1,095,400 5 x 60,912 (carts again), 4 x 57,138, and 16 x 96,918, all `Road`, and two ships, 585,194 at 1,021,800 and 438,891 at 1,035,400 (`Water`). The two different prices for the same cart (60,903 and 60,912) are 0.015% apart. Why they differ is **Open**. The later maintenance batches show the effect of each purchase: the 900,000 batch had 11 running-cost bookings (7 + 4 carts) and the 1,080,000 batch 13 (+ 2 ships), one per vehicle as in [the earlier batches](running-costs.md#upkeep-and-running-costs-are-booked-in-batches-604).
- **A depot for two carriers is booked as two bookings.** One depot cost -30,347 as `Road` and -30,346 as `Tram` at the same tick, the two halves of 60,693. The `Tram` booking is the only one in the game. **Observed**, one depot. Whether a depot that serves both carriers is always split like this is **Open**.
- **A subsidy accepted adds a `Subsidy` booking** at the acceptance tick, +2,610,000 here, see [subsidies.md](subsidies.md#a-new-game-an-offer-its-expiry-and-an-accepted-subsidy-604). Its category is its own, not `Income`.
- **The loan payment kept its schedule**: at 975,400 and 1,097,200 (121,800 apart), -214,286 and -19,286 each.
- **Income keeps coming as one pair of bookings per delivery** (Road and Water at one time), now at 635,400, 719,400 (three bookings), 825,200, 915,800, 1,013,200 and 1,099,000, each pair about 24,500 to 25,100 in total.

### Selling a vehicle is a positive booking in the purchase category (604)

**Observed** on 604, one game (the Small subarctic game, saves `1958` and `1959`, paused at clock 43,361,200, 1 January 1912 plus ten days). The player sold seven old horse carts and bought seven `benz1912_box` trucks at the Todmorden road depot ("Buy 7 Vehicles for $2,580,102", $368,586 each in the buy window).

- The journal gained 14 bookings, all at the paused clock and with the same five category bytes as the purchases (3, 6, 2, 0, 0, the `ACQUISITION` / road bookings of the vehicle purchases above). Seven were -368,586, the buy button's per-vehicle price. Seven were **positive**: +48,309, +48,286 and five of +46,838. Their sum, 330,785, is what separates the 2,580,102 bought from the fall of 2,249,317 in the account (2,500,026,265 to 2,497,776,948).
- So the game books a sale as money in, in the vehicles' own acquisition category, one booking per vehicle, not as a negative purchase. The Finances tab's "Investments, Vehicles" row therefore shows the net. These were the first positive bookings of that kind in the whole journal (5,955 bookings). The sale prices differ a little between vehicles (two at about 48.3 thousand, five at 46,838), which fits a value that depends on age or condition (**Open**: not tested against the vehicle windows).
- Buying and selling in one go shows in the header counts too, see [header.md](header.md#counts-the-load-dialog-shows).
- **Later purchases and sales in the same game (clock 58.4 to 62.7 million, 1917 and 1918)** kept the pattern: one booking per vehicle, same category bytes, sales positive.
  - **The booked price was $35 below the buy window's.** Three batches of the same model, 7, 14 and 13 Benz 3-Ton Bulk, were bought with the window showing $368,586 each (7 for $2,580,102, 13 for $4,791,618), and each vehicle was booked at -368,551 (at 58,426,800, 61,148,400 and 62,722,000). In 1912 the same window price had been booked in full. Prices of one model also differed slightly in the first months of the game (carts at 60,903 and 60,912, ships at 438,891 and 438,912). What sets the booked price is **Open**.
  - **Sale prices are per model.** Nine horse carts of two models sold for +2,712 each (four of one model) and +1,210 each (five of the other): 4 x 2,712 + 2 x 1,210 = +13,268 at 58,811,600, the change in the bottom bar's Earnings across the sale (-187,412 to -174,144, paused), and 3 x 1,210 later. Sixteen old trucks of one model sold for +593 each, in batches of 7 and 9.
  - **With the game running, a sale was booked about two game days after the player's screenshot of the confirm dialog** (twice, at 0.25x and play speed 4), so read a sale's time from the journal, not from the screen.

## The balance history run

**Observed** on 604, catalog save 6428935 (account 3,382,382,812 in the game) loaded, paused at once and saved again. In the stream, far in front of the Lua states, there is a long run of i64 values that each sit within a few percent of the one before and read as a balance history. Three of them, 12 entries apart, equalled the Bank Account row for the last three finished periods on the Finances tab (3,302,688,957, 3,330,544,108, 3,363,416,724). The tab shows six-month periods, so that is about two entries a month. The last entry of the run was 3,382,379,554, which is the header money of the original save and not the re-save's, so the history is sampled and the live balance is not appended to it. It is not the money journal that FORMAT.md describes: that is a separate run of 21-byte bookings ([above](#finding-the-journal)). Find it by searching for one of the period-end figures as 8 little-endian bytes. **Observed**, one save.
