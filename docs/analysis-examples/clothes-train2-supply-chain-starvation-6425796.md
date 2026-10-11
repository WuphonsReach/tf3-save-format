# Worked example: a train with nothing to carry

Not a format note. The goal of this folder is to test whether the repo has the information and the tooling to support an analysis of a player's question, and to record where it does not. This first example asks "where are the bottlenecks on this line?". It shows how the [statistics lists](../statistics-lists.md) were used to answer a player's question, "where are the bottlenecks on this line?", and what the answer rested on. Each step names the note that holds the underlying fact. Checked on 604, one game: catalog save [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1) (temperate, no mods, clock 94,328,800, shown date 18 February 1937). Cargo ids are the base game's ([cargo-ids.md](../cargo-ids.md)): `wool` 25, `fabric` 26, `dyes` 2, `clothes` 27.

## Does the repo support this? (first verdict)

| Need | In the repo | Status |
|---|---|---|
| Cargo ids for the save, recipes, which industry makes what | `tf3save.cargo_list`, [cargo-ids.md](../cargo-ids.md), [industry-chains.md](../industry-chains.md) | Supported |
| Clock, calendar speed, date of a clock value | `tools/calendar_speed.py`, [calendar.md](../calendar.md) | Supported |
| Read the `items*` lists, group them, difference per period to the save's clock | [statistics-lists.md](../statistics-lists.md) and `tools/items_lists.py` (`--cargo`, `--table`, `--entries`) | Supported since the tool was promoted from private and throwaway scripts; before that this was a gap. Its figures matched the earlier hand-made table on this save |
| Say which group belongs to which stop, industry or line | none; matched by equal totals and per-period figures | **Gap** (**Open** in [statistics-lists.md](../statistics-lists.md#groups)) |
| Say which vehicles run a line, and where they are | none; [vehicles.md](../vehicles.md) ties vehicles to depots and slots only | **Gap** (**Open**) |
| Say why a stage stopped (road or track cut, vehicles sold or stuck) | the `vehicle2problem` table is documented, but keyed by vehicle | **Gap**: not decidable from the save as read so far |
| Line stops and the stops' cargo configuration | [lines.md](../lines.md) documents the stop record and trip plans | Not tried here; it could tie a line to its stops and so to groups |

Verdict: the notes were enough to explain what happened and when. They were not enough to say which line, which vehicles or why. The list reading, the one step that had no public tool, is now `tools/items_lists.py`. Add to the table when another example is tried.

## The question and the starting figures

The Lines tab showed a rail line with Load 0, Utilization 0%, capacity 210 and Frequency 27 min 23 s. Frequency and Rate are explained in [lines.md](../lines.md#the-lines-windows-frequency-rate-and-load-columns-604). Load 0 says the line is empty now, not why.

## Method

1. **Find the stages.** The chain is `livestock_farm` (`wool`), `weaving_mill` (`fabric`), `textile_factory` (`fabric` and `dyes` into `clothes`), then a warehouse. The recipes are in [industry-chains.md](../industry-chains.md).
2. **Difference every list per period.** Take each stage's `items*` totals at multiples of 1,461,000 clock units, from period 1 to the save's clock (here period 65), and print every period, trailing zeros included. `tools/items_lists.py` does this. A reader that stops at a fixed number of periods, or drops trailing zeros, shows an old game wrongly and hides exactly the stages that stopped (**Confirmed**: an earlier private reader capped at 39 periods gave wrong figures here). See [statistics-lists.md](../statistics-lists.md#the-yearly-bars-are-periods-of-1461000-units-604).
3. **Read each list's last entry time, not only its total.** A stage that stopped has a last entry long before the save's clock.
4. **Identify the line by its figures.** The loading stop's `itemsLoaded` showed loads of 210, the line's capacity. Its total (1,938) equalled the total unloaded at the warehouse stop. Each load was unloaded about 660,000 units later. A match like this is **Observed**; the line-to-vehicle link itself is **Open** ([vehicles.md](../vehicles.md)).
5. **Use clock units, not dates.** This save's calendar had been stopped since clock 76,984,000 ([calendar.md](../calendar.md#the-day-table)), so every event after it has the same shown date.

## What the lists said (604, Observed)

| Stage | Last entry in the clock | Periods before the save |
|---|---|---|
| Clothes loaded at the line's loading stop | 83,108,800 | about 7.7 |
| `clothes` produced | 82,364,800 | about 8.2 |
| `fabric` delivered to the `textile_factory` | 82,343,600 | about 8.2 |
| `wool` delivered to the `weaving_mill` | 82,063,800 | about 8.4 |
| `dyes` delivered to the `textile_factory` | 94,083,400 | still arriving |
| `wool` produced at the farms | 94,261,200 | still produced |

- **The line is starved, not slow.** The `textile_factory` had no input after the `weaving_mill` stopped, and the mill had no wool. Dyes kept arriving, and the factory had taken in about 300 more than it used, so dyes were not the limit.
- **The farms' wool is not collected.** Their `itemsLost` lists grew by about what they produced in each of the last periods (for one farm 57 to 116 lost against 96 to 104 produced). Whether that is spoilage, a full output or something else is **Open** ([spoilage.md](../spoilage.md#the-itemslost-lists)).
- **Why wool stopped is not in the lists.** A cut road or track, a removed line, sold vehicles and a blocked train look the same here. The save holds 58 vehicles in `vehicle2problem` ([notifications.md](../notifications.md#bookkeeping-tables)), but that table is keyed by vehicle and the vehicle-to-line link is **Open**.

## When the line did limit the chain

In periods 51 and 52 the factory's trucks brought 366 and 270 `clothes` to the station while the line loaded 210 in each period, so about 216 were left waiting. In the next three periods the factory's `itemsLost27` grew by 107, 75 and 37, which is 219 (**Observed**: the figures agree, nothing was tested). After period 53 the factory made only 70 to 90 a period, under half of what the line could move (a loop took 1.25 to 1.56 million units, one load of 210 a period), so the line's size stopped mattering.

An earlier gap is also visible: in periods 36 to 44 the factory's lost list grew by about as much as it produced, while the line had no loads (its first loads were in periods 25 to 27 and it resumed in period 45). Something else carried the cargo, or nothing did (**Open**).

## What the method cannot give

- Which vehicle or line owns a group. Groups are matched by figures ([statistics-lists.md](../statistics-lists.md#groups)).
- Why a stage stopped. The lists show that it did and when.
- A date for any event once the calendar is stopped; use the clock.
