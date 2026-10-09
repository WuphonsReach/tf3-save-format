# Finances tab and the money journal

How the company window's Finances tab (Earnings Details and Summary) lines up with the money journal. The journal's layout, its category enums and how to find it are in [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md) and are not repeated here. Here only the link to what the game shows is covered.

Checked on 604, one game: catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) saved again with the game paused (calendar speed 0.50x, no mods, no loan taken at the time). 585 and 601 were not looked at.

## Finding the journal

- **Confirmed**: the journal in this save has 25,570 bookings, and their amounts sum to the balance, which equals the header money. That matches FORMAT.md, and the 21-byte booking (`i64` time, `i64` amount, five `u8` categories) read as described there.
- Find it by trying each u32 count `n` with the header money sitting `n * 21 + 4` bytes before the balance's end: the sum of the amounts must equal the balance. The header money also appears as an i64 in a second place in the stream, so check the sum.
- The first booking is time 0 with +4,000,000, the starting capital. Here its type byte is 0 (`LOAN`), with construction `OTHER`, maintenance `OTHER`, other 0 and carrier `OTHER`. FORMAT.md says the starting capital is booked with type `OTHER`, so the type may differ between versions or settings. **Observed**, one save.
- The `time` field is the game clock of [calendar.md](calendar.md): the game's own milliseconds, 4000 per game day at calendar speed 1.00x. It is not milliseconds of real time. **Observed**: the last booking sat at 383,513,600, and the newest timestamps in the Lua states of the same save were 383,512,800 to 383,515,000.
- Bookings are in time order. The journal is not the same data as the long run of balance samples described in [header.md](header.md).

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
