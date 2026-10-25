# Finances tab and the money journal

How the company window's Finances tab (Earnings Details and Summary) lines up with the money journal. The journal's layout, its category enums and how to find it are in [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md) and are not repeated here. Here only the link to what the game shows is covered. How upkeep and vehicle running costs are booked is in [running-costs.md](running-costs.md). How long a game was played, read from the journal's periods: [play-length.md](play-length.md).

Checked on 604, one game: catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) saved again with the game paused (calendar speed 0.50x, no mods, no loan taken at the time). 585 and 601 were not looked at.

## In short

Versions: 604 throughout (one catalog save and one new game); 585 and 601 were not looked at.

- **The money journal is what the game's windows read (Confirmed).** Setting the balance with the editor added one `OTHER` booking, and the Finances tab, the Overview chart and the bottom bar all followed with no other copy changed. The journal's bookings sum to the balance, which equals the header money (Confirmed, [Finding the journal](#finding-the-journal)).
- **A tab column is one period of 1,461,000 clock units (Confirmed)** and its Earnings is the sum of every booking except type `LOAN`. The bottom bar's Earnings is the current period's sum, not a running total (Observed, one save).
- **Each tab row is the sum of the bookings in a few category bytes (Confirmed for the rows in [the table](#rows-against-the-booking-categories)).** Depots count under Infrastructure and warehouses have their own Investments row (Observed, one build). The tab's split of upkeep into roads and buildings has no field in the booking (Open).
- **Old bookings are merged, so booking counts do not measure activity (Observed).** Beyond about a year before the save they are summed by month, much older ones by year. Where the cutoffs sit is Open.
- **A sale is a positive booking in the vehicle acquisition category, one per vehicle (Observed).** The tab's vehicle row shows the net. Detail in [vehicle-sale-bookings.md](vehicle-sale-bookings.md).
- **Income is booked as one booking per carrier, all at one time per delivery (Observed).** A line's window balance is its income minus its vehicles' running costs only. How a delivery's pay is split between carriers or lines is Open; players report a split by crow-flies distance per line ([leads](#leads-on-the-split-between-lines)).
- **The carrier byte reads ROAD 0, RAIL 1, TRAM 2, OTHER 3, AIR 4, WATER 5 (Observed, 605).** That is the order of the `Carrier` record in the game's type definitions (`api/tealdef/api/type.d.tl`) and the one FORMAT.md gives, and it fits the starting capital's `OTHER`. On one played game the tram row (2) was passenger-only and the water row (5) moved most when a mod was removed. Not checked on a save with one known kind of vehicle.
- **Income is booked per carrier, so a diff of the sums per (type, construction, maintenance, carrier) between two saves of one game gives a stretch's income and costs (Observed, 605).** Merged old bookings keep their sums. In one game, per clock month, income was $6.89M with a mod's ticket billing and $5.61M without it, with equal running costs.
- **The pay of a delivered unit is scaled by `OnCalcTicketPrice` answers before it is shared along the chain (Observed, 605).** See [the ticket price event](#the-ticket-price-event).
- **A new game starts with no bookings** (the catalog save started with a +4,000,000 booking, so this varies; Observed). Anything built or sold while the game is paused is booked at the paused tick (Observed, two sessions).
- **Not found:** a field for the tab's roads/buildings split, the cause of small price differences for one model, and whether the line-balance rule holds with several lines per carrier.

## Finding the journal

- **Confirmed**: the journal in this save has 25,570 bookings, and their amounts sum to the balance, which equals the header money. That matches FORMAT.md, and the 21-byte booking (`i64` time, `i64` amount, five `u8` categories) read as described there.
- Find it by trying each u32 count `n` with the header money sitting `n * 21 + 4` bytes before the balance's end: the sum of the amounts must equal the balance. The header money also appears as an i64 in a second place in the stream, so check the sum.
- The first booking is time 0 with +4,000,000, the starting capital. Here its type byte is 0 (`LOAN`), with construction `OTHER`, maintenance `OTHER`, other 0 and carrier `OTHER`. FORMAT.md says the starting capital is booked with type `OTHER`, so the type may differ between versions or settings. **Observed**, one save.
- The `time` field is the game clock of [calendar.md](calendar.md): the game's own milliseconds, 4000 per game day at calendar speed 1.00x. It is not milliseconds of real time. **Observed**: the last booking sat at 383,513,600, and the newest timestamps in the Lua states of the same save were 383,512,800 to 383,515,000.
- Bookings are in time order. The journal is not the same data as the long run of balance samples ([below](#the-balance-history-run)).

## Periods

- **Confirmed**: each column of the Earnings Details table is one period of 1,461,000 clock units (365.25 stored days), and the period boundaries are multiples of 1,461,000. For this save the four columns were the bookings with `time` from 378,399,000, 379,860,000, 381,321,000 and 382,782,000 (multiples 259 to 262), the last one still open.
- At calendar speed 0.50x one period shows as six months, which is why the columns read like half years. At another speed the span in game dates would differ. The statistics bars keep the same 1,461,000-unit periods at 0.25x and with the date stopped ([statistics-bars.md](statistics-bars.md#the-yearly-bars-are-periods-of-1461000-units-604)); this tab's columns were not read at another speed. **Open**.
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
- **Old bookings are merged by month** (604, the new game below, save `1246` at clock 5,997,000). Before 4,560,000 the journal holds four infrastructure bookings per 121,750 units, one per carrier, each the sum of what two 60,000-unit batches booked (a warehouse is -4,106 a month, two are -8,212). 121,750 is a twelfth of the 1,461,000-unit year. The first batch kept in full is at 4,560,000, so bookings more than one year (1,461,000 units) older than the save are merged. Later in the same game, 13 truck purchases booked separately at 62,722,000 were still apart in a save at clock 63,198,000 and had become one booking (-4,791,163) at 62,701,250, which is 515 x 121,750, in a save at 64,397,200. **Observed** in these saves: where exactly the cutoff sits (a year before the clock, or a fixed count) is **Open**.
- **Much older bookings are merged by year.** In saves of the same game at clock 58.6 to 63.2 million (1917 and 1918, calendar at 0.25x) the old vehicle purchase bookings sit at multiples of 1,461,000 (39,447,000, 40,908,000, 42,369,000), the start of the 1,461,000-unit period they fall in, one per category and period: the 42,369,000 booking of -2,249,317 is the net of the seven trucks bought and seven carts (`horsewagon_1850_v2` and `horsewagon_1850_usa_v2`) sold at 43,361,200 ([vehicle-sale-bookings.md](vehicle-sale-bookings.md#selling-a-vehicle-is-a-positive-booking-in-the-purchase-category-604)). So merging goes on past the monthly step. Where the yearly step begins was not read. **Observed**, one game.

## The balance history run

**Observed** on 604, catalog save 6428935 (account 3,382,382,812 in the game) loaded, paused at once and saved again. In the stream, far in front of the Lua states, there is a long run of i64 values that each sit within a few percent of the one before and read as a balance history. Three of them, 12 entries apart, equalled the Bank Account row for the last three finished periods on the Finances tab (3,302,688,957, 3,330,544,108, 3,363,416,724). The tab shows six-month periods, so that is about two entries a month. The last entry of the run was 3,382,379,554, which is the header money of the original save and not the re-save's, so the history is sampled and the live balance is not appended to it. It is not the money journal that FORMAT.md describes: that is a separate run of 21-byte bookings ([above](#finding-the-journal)). Find it by searching for one of the period-end figures as 8 little-endian bytes. **Observed**, one save.

## The ticket price event

**Observed** on 605, one game, by a game script that subscribed to it. The game script event `OnCalcTicketPrice` comes once per delivered unit at the delivery tick, before the pay. Its items name the vehicle (which holds the unit itself), the line (the last leg's), `simEntity`, the stock list, `basePrice` (the unit's pay before the pay scale) and `distance` (nil). A subscriber answers `{[i] = m}` for each item and the engine multiplies all the answers. The base game answers this way for the company level (`company/company_growth.script.tl`) and for subsidies (`subventions/deliver_cargo/deliver_cargo.script.tl`, both in `game_mechanics.zip`; see [inflation.md](inflation.md#the-income-multiplier)).

The multiplier scales the unit's **whole** pay, and the pay is then shared along the chain: answers of 0.5, 0 and 2 halved, zeroed and doubled every line of a two-leg chain. So the chain split below happens after the multiplier. This does not tell what the split is. A vehicle window's income chart showed one bar per trip-like period, three of about $3.0M on a grain train, then two reduced ones while a mod answered below 1, then $3.0M again. Source: the Best Before mod's `docs/findings.md` and `docs/future/line-billing.md`, with run tables.

## Leads on the split between lines

Players on the Transport Fever subreddit (October 2026 thread on a loss-making city distribution line) say a good is paid for only once it reaches its final consumer, and then every line that carried it gets a share. Their guesses at the share, none read from a save (all **Open**):

- **Straight-line distance per line.** The pay is divided in proportion to how far each line moved the good as the crow flies. A line whose leg runs sideways to the overall route moves it almost nowhere and earns almost nothing (one player's reading).
- **The projection of each leg onto the base line (our reading of the above).** Draw one line from the source to the final consumer; each line's share is how far its leg's displacement reaches along that line, as a part of the base distance. A sideways leg scores near zero, though its own straight-line length is large, and a backwards leg would score negative or zero. Legs chained from source to consumer have projections that sum to the base distance, so the shares need no scaling. The source may be the producer or the first station.
- **Time on each vehicle**, or **distance driven on each vehicle** along the path.

What a test needs: a delivery that crosses two lines with a known, different crow-flies length and path length for each leg, and a journal read before and after. A third case needs a leg that carries the good away from the consumer (a detour via a station behind the source): its income shows whether the share goes negative, stops at zero or follows length. The 82% water share in [the first delivery](finances-tests.md#loan-payments-and-income-over-ten-minutes) is the one measured split so far; checking it against the two legs' straight-line, path and time lengths would separate the guesses. The journal has no line field, so read the split from the line windows' income, with one line per carrier.

## Evidence and tests

The dated tests are in [finances-tests.md](finances-tests.md): [a new game's journal](finances-tests.md#a-new-games-journal), [a first build-out, row by row](finances-tests.md#a-first-build-out-row-by-row), [loan payments and income over ten minutes](finances-tests.md#loan-payments-and-income-over-ten-minutes), [the bottom bar's Earnings](finances-tests.md#the-bottom-bars-earnings-is-the-current-periods) and [a new game's first batch of bookings while paused](finances-tests.md#a-new-games-first-batch-of-bookings-while-paused).
