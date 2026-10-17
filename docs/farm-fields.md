# Farm fields

What a crop farm's fields are in a save, how many it has, and what the number beside the production bar in the farm's panel counts. Read from three crop farms of one save and from the game's `farm.con.lua` (`industries/farm.zip` in `base/content`).

## In short

- **The panel's number is the farm's count of field records (Observed, 604, one game, three farms: 7, 10 and 13).** In the save each farm holds a `modules` table with one entry per field, and the table held 7, 10 and 13 entries for the three farms whose panels read 7, 10 and 13. A field counts once whatever its size: the 10-field farm has four of the biggest plots, and counting by area would give far more than 10.
- **A farm has up to 20 field slots, numbered 1 to 20 (Confirmed from the game file, Observed in the save).** The file lists them by size: slots 1 to 4 are 120 by 120 m, 5 to 9 are 60 by 60, 10 to 14 are 60 by 120 and 15 to 20 are 120 by 60. In the save the `modules` table is keyed by slot. A farm seems to keep only the slots the game could place (not tested), so the 13-field farm in the test had no slot 1, 3 or 4 and the 7-field one had slots 1, 3, 9, 13, 15, 19 and 20.
- **Output scales with the count (Observed, three farms).** The file gives the farm's rule 24 grain and 16 vegetables and `industrialCapacity` 20. The panel showed 12 grain and 8 vegetables at 10 fields, 8 and 6 at 7, and 16 and 10 at 13: the count over 20 times the rule, rounded (1.2 grain and 0.8 vegetables per field).
- **Open.** What the two larger numbers under the icons (59 and 39 at 10 fields, 37 and 28 at 7, 73 and 45 at 13) count: they sit near 4 to 5 times the per-cycle figure and were not tied to a field in the save. Whether the livestock farm, forest and clay pit work the same way (the stream holds the same record shape for them) was not checked. What the panel line "Industry is expanded to its full potential" tests (it showed at 13 fields, not at 7 or 10) is not known.

## How the fields are stored

Each field is a Lua table in the farm's `modules` table. It starts with the string `::/industries/farm/field.module` (`livestock_farm/`, `forest/` and `clay_pit/` have their own) and a `variant` key. In the 30 records read `variant` was 0; the number that tells fields apart is the table key before each record, a number from 1 to 20. Find a farm's fields by that string: the records of one farm follow each other, and the table's count sits just before the first (a `u32` after the `modules` key's table tag).

The earlier note on a road removing a field ([editor-saves.md](editor-saves-tests.md#a-running-clock-a-tree-a-farm-and-a-rock)) called these numbers variants; they are the slot keys.

## Evidence and tests

- **604, one Large flat game, one save (27 December 1913), screenshots of the three farms taken in the game.** Field records by farm: 13 (slots 2, 5, 6, 7, 8, 10, 12, 13, 14, 15, 17, 18, 20), 10 (1, 2, 3, 4, 8, 11, 12, 14, 18, 20) and 7 (1, 3, 9, 13, 15, 19, 20). The slot sizes match the pictures: the 7-field farm showed two big plots, three wide, one tall and one small; the 13-field farm showed one big plot. Counting the plots on the 7-field and 13-field pictures gave 7 and 13. The 10-field picture was not counted to 10: plots that touch run together in the outline, so a count by eye there is a guess, and the slot list (four big plots) is the better check. The three counts are all different, so the farm a group belongs to follows from the number; the slot sizes check it independently.
