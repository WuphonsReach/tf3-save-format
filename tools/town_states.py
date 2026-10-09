"""Print the per-town rating state of a save (the `townStates` table of the town script).

Usage: town_states.py SAVE.sav [...]

Read only. See docs/town-states.md and docs/lua-values.md. Editor saves have an empty table.

The value reader follows tf3-save-editor (crates/lib/src/lua.rs,
https://github.com/TBK/tf3-save-editor), Copyright (c) 2026 TBK, MIT OR Apache-2.0.
See THIRD_PARTY_NOTICES.md.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tf3save import decompress  # noqa: E402

# Script-state values: u32 tag, then 0 nil, 1 bool (u8), 2 number (f64), 3 string (u32 length +
# bytes), 4 table (u8 flag: 0 is a nil table with nothing after it, 1 is followed by a u32 pair
# count and the key and value pairs). The same encoding tf3-save-editor reads in `lua.rs`.
_KEY = struct.pack("<II", 3, 10) + b"townStates"


class _Reader:
    def __init__(self, data, pos):
        self.d, self.p = data, pos

    def take(self, fmt):
        v = struct.unpack_from(fmt, self.d, self.p)[0]
        self.p += struct.calcsize(fmt)
        return v

    def value(self):
        tag = self.take("<I")
        if tag == 0:
            return None
        if tag == 1:
            return bool(self.take("<B"))
        if tag == 2:
            return self.take("<d")
        if tag == 3:
            n = self.take("<I")
            s = self.d[self.p:self.p + n].decode("latin1")
            self.p += n
            return s
        if tag == 4:
            if not self.take("<B"):
                return None
            out = {}
            for _ in range(self.take("<I")):
                k = self.value()
                out[k] = self.value()
            return out
        raise ValueError(f"unknown tag {tag} at {self.p}")


def town_states(data):
    """The `townStates` table as a dict (index -> state dict), or None if the save has none."""
    pos = data.find(_KEY)
    while pos != -1:
        try:
            r = _Reader(data, pos + 8 + 10)
            table = r.value()
            if isinstance(table, dict) and all(isinstance(v, dict) for v in table.values()):
                return table
        except (ValueError, struct.error, UnicodeDecodeError):
            pass
        pos = data.find(_KEY, pos + 1)
    return None


def describe(path):
    states = town_states(decompress(open(path, "rb").read()))
    if states is None:
        print("  no townStates table found")
        return
    print(f"  {len(states)} town states")
    for idx, t in states.items():
        ef = t.get("eventFactors", {})
        ratings = {k: round(v["value"], 3) for k, v in t.get("cachedRatings", {}).items()}
        penalties = {k: round(v, 5) for k, v in ef.get("reasonToPenalty", {}).items() if v}
        entity = t.get("townEntity", {}).get("entity")
        print(f"  #{int(idx)} entity {int(entity) if entity is not None else '?'}"
              f"  authority {t.get('authorityScore', float('nan')):.3f}  score {ef.get('score', float('nan')):.4f}"
              f"  ratings {ratings}  penalties {penalties}")


def main():
    for path in sys.argv[1:]:
        print("==", path)
        try:
            describe(path)
        except Exception as e:  # report and carry on with the next save
            print("  FAILED:", e)


if __name__ == "__main__":
    main()
