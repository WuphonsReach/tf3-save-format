#!/usr/bin/env python3
"""Print the calendar speed and play speed stored in a TF3 .sav.

Usage: calendar_speed.py SAVE.sav [...]

Only reads. The field is the game's `millisPerDay` (4000 at 1.00x); see
docs/script-states.md for the pattern it is found by. Importable through
tf3save.find_game_speed(stream).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tf3save import decompress, find_game_speed  # noqa: E402


def label(millis_per_day):
    """Calendar speed as the game shows it, or None for a value that is no slider step."""
    if millis_per_day == 0:
        return "Paused (date stopped)"
    speed = 4000 / millis_per_day
    return f"{speed:g}x" if millis_per_day in (1000, 2000, 4000, 8000, 16000) else None


def main():
    for path in sys.argv[1:]:
        print("==", os.path.basename(path))
        try:
            with open(path, "rb") as f:
                g = find_game_speed(decompress(f.read()))
        except Exception as e:  # report and carry on with the next save
            print("  FAILED:", e)
            continue
        if g is None:
            print("  field not found (or found more than once)")
            continue
        name = label(g["millis_per_day"]) or "not a slider step"
        print(f"  millisPerDay {g['millis_per_day']} ({name})  play speed {g['play_speed']}"
              f"{' (paused)' if g['play_speed'] == 0 else ''}  t1 {g['t1']}  offset {g['offset']}")


if __name__ == "__main__":
    main()
