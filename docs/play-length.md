# How long a game was played, from the money journal

A measure for ranking mined saves by how much they were played: the number of periods in which the player built, bought, paid upkeep or earned. The journal layout is in [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md) and its periods, merging of old bookings and booking categories in [finances.md](finances.md). The script is `tools/journal.py`; `tools/mine_saves.py` writes the result into each summary's `journal` block and `index.csv`.

## In short

- **Count periods, not bookings (Observed, 568 to 604, 588 mined saves).** Old bookings merge by month and year but keep their period, so the span from the first to the last play booking (`play_periods`) and the number of periods with income (`income_periods`) measure how long a game was played.
- **Play is a booking of type `CONSTRUCTION`, `ACQUISITION`, `MAINTENANCE`, `INCOME` or `SUBSIDY`;** the starting capital and loan are left out. An editor map can have play bookings, so `income_periods` above 0 is the better sign vehicles ran.
- **The journal is found by its place** after the edge-addon name table; two 568 saves were not found.
- **Open.** Where an editor map's bookings come from.

## How it is measured

Checked on 568 to 604 on the 588 mined catalog saves and maps. The unit is the period of 1,461,000 clock units ([finances.md](finances.md#periods)).

- **Observed** (568 to 604): the journal is found by its place, after the edge-addon name table, whatever the header money is (0 in most editor maps). Save format 568 has no such table; there the balance bytes (header money, non-zero in those saves) are searched and the 21-byte bookings walked back until the stored count matches. Two 568 saves (catalog 6105556 and 6105772) were not found this way: one has money 0, and in the other the header money matched no balance that fits its bookings. Every other 604, 601 and 599 save had a journal, as did the rest of the 568 saves read (the 5 editor maps of the mined set were not re-read here). **Observed**.
- **Play is a booking of type `CONSTRUCTION`, `ACQUISITION`, `MAINTENANCE`, `INCOME` or `SUBSIDY`.** The starting capital and loan bookings are left out. **Observed**: a save no one built in has a journal with 0 bookings (a 604 game at its start date with no income, and a converted map with a clock past 6 million both read 0).
- **Count periods, not bookings.** Old bookings are merged by month and then by year ([finances.md](finances.md#rows-against-the-booking-categories)) but keep their period, so the span from the period of the first play booking to the period of the last (`play_periods`, both counted) and the number of periods with income (`income_periods`) hold where the booking count does not. A game's oldest bookings sit at time 0 or at a period start, so a span is read to whole periods. **Observed**.
- **An editor map can have play bookings.** 262 of the 305 editor maps hold 1 or more periods of construction bookings and 13 hold 10 or more (the longest 15), some with income: the journal of a map comes from the game it was made from or from the editor's own building. So `income_periods` above 0 is the better sign that vehicles ran. **Observed**; where the editor bookings come from is **Open**.
- **The journal and the achievements counter can disagree.** One 604 map (catalog [6429778](https://mod.io/g/transportfever3/m/simplon), not an editor map, 1925 date) has `totalIncome` 33.9 million in the achievements state and an empty journal; in the other 572 saves that have both, income above 0 in one means above 0 in the other. **Observed**, one save; the journal was probably cleared when the map was made.

## Evidence and tests

Ranking, deepest first, on the 588: 402 periods (catalog [6429195](https://mod.io/g/transportfever3/m/hometown-of-overseas-chineseli-shui-city1)), 263 ([6428935](https://mod.io/g/transportfever3/m/emerald-shores3), the game of finances.md), 248 and 193. 66 non-editor saves read 0 periods.
