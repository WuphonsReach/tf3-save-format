# Finances tab and the money journal: tests

The dated tests behind [finances.md](finances.md): what the Finances tab, the company window and the bottom bar showed against the money journal in one new game and one catalog save, save by save. The conclusions are in "In short" there. All on 604.

## What the tests showed

- **The journal is what the windows read (Confirmed, one save).** Setting the balance with the editor added one `OTHER` booking, and every window followed.
- **A new game starts with no bookings (Observed)**; a loan is the first booking. Building while paused books at the paused tick (Observed, two sessions).
- **Every tab row of a first build-out matched its bookings to the dollar (Observed).** Loan payments run on a fixed schedule; income is one booking per carrier per delivery.
- **The bottom bar's Earnings is the current period's sum (Observed).**
- **Open:** the depot booking's category value, why one cart model has two prices 0.015% apart, whether a depot for two carriers is always split in two, and how a delivery's pay is split.

## A new game's journal

**Observed** on 604, the [Small subarctic game](test-games.md#small-subarctic-game) when new (paused at 1900-01-01), saved four times:

- A new game starts with header money 0 and **no bookings**: no starting capital is booked, unlike the catalog save in [finances.md](finances.md). The journal is then an empty list with balance 0, and the stream holds over a thousand zero-balance journal-shaped runs, so the search for a journal by balance ([Finding the journal](finances.md#finding-the-journal)) finds many and the tf3-save-editor CLI calls money read-only.
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

**Observed** on 604, the same game after buying two small ports, two ship depots, a road depot, a specialised fish warehouse, a road stop (`small_*`), three road vehicles and four ships, and building a short road (calendar paused at 1 January 1900, so every booking carries the same time, 1000). The journal grew from 3 to 20 bookings (editor labels in quotes), and every figure on the company window's Finances tab matched the bookings in its category to the dollar:

| Tab row | Value | Bookings |
|---|---|---|
| Investments, Roads | -66,002 | "Construction - streets (Road)": 30,000 + 30,000 + 6,002 |
| Investments, Infrastructure | -2,183,875 | "stations" (Water 144,973 and 145,484; Road 74,664) and "depots" (Water 81,857, 838,203 and 700,522; Road 198,172) |
| Investments, Warehouses | -305,973 | one "Construction - warehouses" booking |
| Investments, Vehicles | -1,206,864 | "Vehicle purchase": 3 x 60,912 (Road) and 4 x 256,032 (Water) |
| Investments | -3,762,714 | the four rows above |
| Summary, Earnings | 2,489,507,336 | all bookings except `LOAN`: the +2,493,270,050 `OTHER` booking less Investments |
| Account | 2,507,507,336 | Earnings plus the 18,000,000 loan |

- Depots count under Infrastructure on the tab, not under a row of their own. [The table of rows against categories](finances.md#rows-against-the-booking-categories) lists only `STATION` and `OTHER` for that row, so the depot booking's category value was not read from the bytes here. **Open**.
- Investments, Warehouses is a row [that table](finances.md#rows-against-the-booking-categories) lacks. It held one booking (305,973), for the one warehouse the player bought, a specialised fish warehouse (so the row is not limited to the general warehouse). **Observed**, one build.
- The header money after saving (2,507,507,336) equalled the Account figure.

### Loan payments and income over ten minutes

**Observed** on 604, the same game after about 570 seconds of play (the header's clock at 569,800, the date still 1 January 1900 with the date stopped, see [calendar.md](calendar.md)): the journal held 210 bookings. The loan of 18,000,000 and the first build-out were still in it. The upkeep and running-cost batches of the same journal are in [running-costs.md](running-costs.md#upkeep-and-running-costs-are-booked-in-batches-604). Then:

- **Loan payments.** First at 122,800, then every 121,800 units (the loan was booked at 1,000, so the first fell 121,800 after it): five by the next save (the fifth at 610,000, as predicted), each a `LOAN` booking of -214,286 plus an `INTEREST` booking of -19,286. 214,286 is 18,000,000 / 84. The interest stayed 19,286 on all four, so it did not fall as the principal was repaid, at least over four payments.
- **Income arrives as one booking per carrier, at one time.** Two bookings at 552,000: Income (Road) +4,554 and Income (Water) +20,771. 552,000 is not a batch time (540,000 and 600,000 are). The booking has no cargo, line or town field. The road line's window showed income 4,554 and the ship line's 20,771, exactly the two bookings.
- **Line windows against the journal.** Line 1 (three `horsewagon_1850_v2` carts) showed income 4,554, running costs 9,792, balance -5,238; Line 2 (four ships) showed 20,771, 59,922 and -39,151. 9,792 and 59,922 are the sums of all road and all water vehicle-running-cost bookings. So a line's balance is income minus vehicle running costs only, with vehicle maintenance and infrastructure upkeep left out. With one line per carrier this is a match by carrier. Whether it holds with several lines per carrier is untested. **Observed**, one save.
- **One delivery paid both lines.** In this game the player saw no income until the fish had left the cart at the town, and then both lines showed income, although the ships' leg ends at a warehouse. The journal fits that: one pair of income bookings, one per carrier, at one time, so a single delivery was paid out split between the road and the water carrier. The journal cannot say whether the payment came at unloading or when the cart departed, or how the split is worked out (82% water here). **Observed**, one delivery.
- Vehicle age in the line window (9m 28s) is the time since purchase in clock units read as seconds: 569,800 - 1,000 units is 568.8 s. **Observed**.
- The header money (2,506,375,464) equalled the journal balance, which equals the previous balance less these bookings.

### The bottom bar's Earnings is the current period's

**Observed** on 604, the same game at clock 2,246,600 (journal 1,718 bookings, balance 2,495,976,310, the same figure as the Account on the bottom bar). The bar's Earnings read -4,938,203 although the all-time sum of bookings other than `LOAN` was 2,481,833,458. The sum of those bookings from 1,461,000 (the start of the period the clock is in, see [Periods](finances.md#periods)) was exactly -4,938,203. So the bar shows the current period, and in the first game of this series (clock below 1,461,000) it showed what looked like a total. The bar's cargo figure (124) was `cargoDeliveredCount` and its passenger figure (0) `passengerTransportedCount` ([script-states.md](script-states.md#counters-and-achievements)). 18 loan payments (3,857,148 in all) had been made, so the loan sum stood at 14,142,852.

### A new game's first batch of bookings while paused

**Observed** on 604, the same game a quarter of an hour of play later (save at clock 1,121,000, the calendar stopped, 477 bookings, money 2,503,056,661). The player added vehicles to the fish lines, bought the first buses and trucks, built a line from a `quarry` to the `cement_plant` and took a subsidy:

- **Everything done while paused is booked at the paused tick.** 40 bookings share the time 1,095,400: 5 depots, 5 stations, a warehouse, 5 pieces of street, 25 vehicle purchases and the subsidy payment. The game had been paused with the clock at 1,095,400 while the player built, so building is allowed while paused and the booking time is the clock, not the order. The first build-out ([A first build-out, row by row](#a-first-build-out-row-by-row)) was booked in the same way at time 1,000. **Observed**, two paused sessions.
- **Vehicle purchases are one booking each**, in groups of equal price: 4 x 60,903 (the `horsewagon_1850_usa_v2` carts added at 887,400), then at 1,095,400 5 x 60,912 (five more of that model), 4 x 57,138 (four `horse_cart_small`), and 16 x 96,918, all `Road`, and two ships, 585,194 at 1,021,800 and 438,891 at 1,035,400 (`Water`). The two different prices for the same cart (60,903 and 60,912) are 0.015% apart. Why they differ is **Open**. The later maintenance batches show the effect of each purchase: the 900,000 batch had 11 running-cost bookings (7 + 4 carts) and the 1,080,000 batch 13 (+ 2 ships), one per vehicle as in [the earlier batches](running-costs.md#upkeep-and-running-costs-are-booked-in-batches-604).
- **A depot for two carriers is booked as two bookings.** One depot cost -30,347 as `Road` and -30,346 as `Tram` at the same tick, the two halves of 60,693. The `Tram` booking is the only one in the game. **Observed**, one depot. Whether a depot that serves both carriers is always split like this is **Open**.
- **A subsidy accepted adds a `Subsidy` booking** at the acceptance tick, +2,610,000 here, see [subsidies.md](subsidies.md#a-new-game-an-offer-its-expiry-and-an-accepted-subsidy-604). Its category is its own, not `Income`.
- **The loan payment kept its schedule**: at 975,400 and 1,097,200 (121,800 apart), -214,286 and -19,286 each.
- **Income keeps coming as one pair of bookings per delivery** (Road and Water at one time), now at 635,400, 719,400 (three bookings), 825,200, 915,800, 1,013,200 and 1,099,000, each pair about 24,500 to 25,100 in total.
