# Gaps: vehicles and costs

Format of an entry: see [README.md](README.md).

## Stored vehicle state

- **Where a vehicle's speed is kept** (604) Not in the model instance; ship windows read 26 and 35 km/h in one save. Home: [vehicles.md](../vehicles.md). Needs: game window (a speed reading) plus existing saves.
- **Where the vehicle condition (maintenance state) is kept** (604) Condition steps change the running cost ([running-costs.md](../running-costs.md)) but the value itself is not found. Needs: new save pair: send one Very Bad ship to a depot, save paused before and after, diff.
- **When a parked ship's model instance is dropped** (604, one game) One ship had an instance 24,600 units after parking and none 148,600 later; another model type (`dunara_castle`) never had one. Home: [vehicles.md](../vehicles.md). Needs: new saves at short intervals after parking, on two ship models.
- **A vehicle's income, last year and running cost** (604) The windows show a per-vehicle yearly income and running cost; searches for the figures as u32, i64 and f64 found only chance hits. They may sit in the `items*` lists as a per-vehicle list. Home: [entity-stats.md](../entity-stats.md). Needs: existing saves (match against a window figure).
- **Where a ship's load instant is, and what the window's percentage is** (604, one game) Home: [spoilage.md](../spoilage.md#a-loads-age-and-the-windows-percentage). Needs: game window.
- **The nine bytes between instance records and the other bytes of an instance** (604) Home: [vehicles.md](../vehicles.md), [models.md](../models.md). Needs: existing saves.

## Running costs and upkeep

- **What adds to a depot's or maintenance building's accumulated cost, and where it is stored** (604) The window figure equals the next batch's vehicle-maintenance booking exactly (it is not a smooth ramp), but the figure was not found as a number in the save (a search as doubles gave chance hits). Home: [running-costs.md](../running-costs.md). Needs: new save pair around a batch, with the window figure read.
- **Batch bookings that do not match** (604) Two ships in one game missed the by-position rule; the remaining per-batch variations (several values around -1,262 to -1,682 against -1,752, and -2,403 to -2,764 against -3,004) are probably time spent in some state. Home: [finances.md](../finances.md), [running-costs.md](../running-costs.md). Needs: game window (the ship's own window).
- **A depot booked as two halves** (604) One depot booked -30,347 as Road and -30,346 as Tram; whether a depot serving both carriers is always split like this, and the category value of the depot booking, are unread. Home: [finances.md](../finances.md), [running-costs.md](../running-costs.md#a-road-depots-upkeep-against-its-window-604). Needs: existing saves.
- **Whether a depot takes the cost table's multiplier on top** (604) Home: [inflation.md](../inflation.md), [running-costs.md](../running-costs.md). Needs: new save at a year where the table steps.
- **How a cargo station's module swap is counted** (604) One module per side of the lane is implied by the sums but not shown. Home: [running-costs.md](../running-costs.md). Needs: existing saves.
- **Where a parked ship's 5% rate is kept** (604) The model instance and the journal rows carry nothing of it. Home: [running-costs.md](../running-costs.md). Needs: new save pair, one ship parked.
- **The constant 3.3 left over in the upkeep factor** (604) The date probably explains it. Home: [inflation.md](../inflation.md). Needs: new save, same game at another date, or two games differing in one setting.
- **The 50% against 150% Infrastructure Upkeep setting in play** (604) Whether it acts on existing buildings or only on new ones. Home: [settings.md](../settings.md#open). Needs: new save with the same road built under each setting.

## Prices

- **What sets a vehicle's booked price and sale price** (604) Two prices for the same cart 0.015% apart (60,903 and 60,912); sale prices that differ a little between vehicles of one model, which fits age or condition. Home: [finances.md](../finances.md). Needs: game window (vehicle windows next to the sale bookings).
