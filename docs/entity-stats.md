# Stocks and yearly figures: not found as plain numbers

What was looked for in the entity data and not found. Checked on 604, catalog save [6417707](https://mod.io/g/transportfever3/m/333151) (paused on 17 April 2000, **A**) and a later manual save of the same game, still paused when screenshots of the game were taken (**B**). All labels are **Open**: a failed search shows how the values are not stored, not where they are.

Numbers read from the game's windows, then searched for in the decompressed stream:

| Value shown | Where | Searched as |
|---|---|---|
| A vehicle's and a line's income for a year (for example 15,767,238 and 24,549,162) and last-year totals | Vehicle and line windows, Balance chart tooltips | i64, f64 and f32 of the shown number, also scaled by 100, 1,000, 0.01 and 0.001; f64 anywhere in the shown number to the next whole number. The scaled searches for 0.01 and 0.001 gave a few i64 hits on 5 and 6 digit numbers (6 to 280 each) that were not examined and are probably chance |
| A construction site's input stocks (0, 56, 116 and 97 against capacities 150, 150, 300 and 150) | Landmark construction site window | The four values with their capacities close together, as u16, u32, f32 and f64, in A and B |
| A warehouse's ten stock levels (477, 16, 64, 30, 12, 53, 49, 392, 12 and 106, each of 500) | Warehouse window | The values close together as u16, u32, i64, f32 and f64, scaled by 10, 100, 256 and 1,000, and as the exact sequence in window order and reverse with up to four zero entries between |
| A warehouse's yearly incoming and outgoing (2,640 for 1998, 2,861 and 2,722) | Statistics chart tooltips | Together as u32, i64, f32 and f64. The one hit was a long sorted run of increasing integers, a false positive |

- The Lua tables of the script states did hold the figures that sit in them, for example the construction progress per cargo in [landmarks.md](landmarks.md) and the subsidy amounts in [script-states.md](script-states.md). So the figures not found are most likely in the binary entity data, in a form these searches did not cover: yearly figures may be kept in finer buckets (the shown number a sum), and stocks may be in a packed or per-entity layout.
- Searching for small numbers or for entity ids gives many false hits: ids and counters are dense in long sorted lists and in repeating `(tag, value)` runs near the end of the stream. A search needs a rare value (a large money figure) or several values that must agree.
- A warehouse is built from modules, one per cargo slot, see [warehouses.md](warehouses.md). So stocks may be kept per module rather than per warehouse, which a search for ten values close together would miss. A search per module (one stock, one capacity) was not tried.
- Not tried: a before and after pair of saves with one stock changed by a known amount, and a save of a map with one warehouse and nothing else, which would make the entity's data easy to isolate.
