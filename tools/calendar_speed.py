#!/usr/bin/env python3
"""Print the calendar speed, play speed and current day stored in a TF3 .sav.

Usage: calendar_speed.py SAVE.sav [...]

Only reads. The field is the game's `millisPerDay` (4000 at 1.00x); the day table follows it; see
docs/script-states.md for the pattern it is found by. Importable through
tf3save.find_game_speed(stream) and find_day_table(stream).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tf3save import calendar_speed_label, date_of_day, decompress, find_day_table, find_game_speed  # noqa: E402


label = calendar_speed_label  # kept for scripts that import it


def main():
    for path in sys.argv[1:]:
        print("==", os.path.basename(path))
        try:
            with open(path, "rb") as f:
                data = decompress(f.read())
            g = find_game_speed(data)
            table = find_day_table(data)
        except Exception as e:  # report and carry on with the next save
            print("  FAILED:", e)
            continue
        if g is None:
            print("  field not found (or found more than once)")
            continue
        name = label(g["millis_per_day"]) or "not a slider step"
        print(f"  millisPerDay {g['millis_per_day']} ({name})  play speed {g['play_speed']}"
              f"{' (paused)' if g['play_speed'] == 0 else ''}  t1 {g['t1']}  offset {g['offset']}")
        if table:
            tick, day = table[-1]
            print(f"  day table: {len(table)} entries, current day {date_of_day(day)} began at tick {tick},"
                  f" {g['t1'] - tick} ticks ago")


if __name__ == "__main__":
    main()
