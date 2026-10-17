# Vehicle sale and purchase bookings

How buying and selling vehicles shows in the money journal: a sale is a positive booking, the booked price of a purchase can differ from the buy window's, and sale prices differ per model. The journal and the Finances tab rows are in [finances.md](finances.md). Checked on 604 in one game, the [Small subarctic game](test-games.md#small-subarctic-game).

## In short

- **A sale is a positive booking in the vehicle's own acquisition category, one booking per vehicle (Observed, 604).** The tab's "Investments, Vehicles" row therefore shows the net of purchases and sales. These were the first positive bookings of that kind in a journal of 5,955.
- **Sale prices differ by model, and a little by vehicle (Observed).** Two at about 48.3 thousand and five at 46,838 in 1912; per model +2,712, +1,210 and +593 in 1917 to 1918. A dependence on age or condition is Open (not tested against the vehicle windows).
- **A purchase's booked price can differ from the buy window's (Observed).** Equal in 1912, $35 below it in 1917 to 1918; carts and ships also booked at two slightly different prices in the first months. What sets it is Open.
- **Read a sale's time from the journal, not from a screenshot (Observed):** with the game running, the booking came about two game days after the confirm dialog's screenshot.

## Evidence and tests

### Selling a vehicle is a positive booking in the purchase category (604)

**Observed** on 604, one game (the Small subarctic game, saves `1958` and `1959`, paused at clock 43,361,200, 1 January 1912 plus ten days). The player sold seven old horse carts (`horsewagon_1850_v2` and `horsewagon_1850_usa_v2`) and bought seven `benz1912_box` trucks at the Todmorden road depot ("Buy 7 Vehicles for $2,580,102", $368,586 each in the buy window).

- The journal gained 14 bookings, all at the paused clock and with the same five category bytes as the purchases (3, 6, 2, 0, 0, the `ACQUISITION` / road bookings of the vehicle purchases in [finances.md](finances.md#a-new-games-first-batch-of-bookings-while-paused)). Seven were -368,586, the buy button's per-vehicle price. Seven were **positive**: +48,309, +48,286 and five of +46,838. Their sum, 330,785, is what separates the 2,580,102 bought from the fall of 2,249,317 in the account (2,500,026,265 to 2,497,776,948).
- So the game books a sale as money in, in the vehicles' own acquisition category, one booking per vehicle, not as a negative purchase. The Finances tab's "Investments, Vehicles" row therefore shows the net. These were the first positive bookings of that kind in the whole journal (5,955 bookings). The sale prices differ a little between vehicles (two at about 48.3 thousand, five at 46,838), which fits a value that depends on age or condition (**Open**: not tested against the vehicle windows).
- Buying and selling in one go shows in the header counts too, see [header.md](header.md#counts-the-load-dialog-shows).
- **Later purchases and sales in the same game (clock 58.4 to 62.7 million, 1917 and 1918)** kept the pattern: one booking per vehicle, same category bytes, sales positive.
  - **The booked price was $35 below the buy window's.** Three batches of the same model, 7, 14 and 13 Benz 3-Ton Bulk, were bought with the window showing $368,586 each (7 for $2,580,102, 13 for $4,791,618), and each vehicle was booked at -368,551 (at 58,426,800, 61,148,400 and 62,722,000). In 1912 the same window price had been booked in full. Prices of one model also differed slightly in the first months of the game (carts at 60,903 and 60,912, ships at 438,891 and 438,912). What sets the booked price is **Open**.
  - **Sale prices are per model.** Nine horse carts of two models sold for +2,712 each (four of one model) and +1,210 each (five of the other): 4 x 2,712 + 2 x 1,210 = +13,268 at 58,811,600, the change in the bottom bar's Earnings across the sale (-187,412 to -174,144, paused), and 3 x 1,210 later. Sixteen old trucks of one model sold for +593 each, in batches of 7 and 9.
  - **Read a sale's time from the journal, not from a screenshot.** Twice, with the game running, the booking came about two game days after the player's screenshot of the confirm dialog. At 0.25x and play speed 4 a game day is about 4 real seconds, so that is the few seconds before the button was clicked, not a delay in the game.
