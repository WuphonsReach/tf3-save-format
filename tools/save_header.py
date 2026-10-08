#!/usr/bin/env python3
"""Read the header of a TF3 .sav. Full on formats 599, 601 and 604; up to the preview on 568 and 585.

Usage: save_header.py SAVE.sav [...]

Only reads; prints one block per save. Importable: read_header(path) returns a dict.
Field meanings are in docs/header.md.

The read order is ported from tf3-save-editor (crates/lib/src/header.rs,
https://github.com/TBK/tf3-save-editor), Copyright (c) 2026 TBK, MIT licence.
See THIRD_PARTY_NOTICES.md. Differences: the preview is read whatever its flag
byte says, and the four u32s after the version and the u32 after the money are
named by what they hold.
"""
import struct
import sys

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tf3save import decompress as _decompress  # noqa: E402


class R:
    def __init__(self, data, pos=0):
        self.d, self.p = data, pos

    def take(self, n):
        if self.p + n > len(self.d):
            raise EOFError(f"need {n} bytes at {self.p}")
        b = self.d[self.p:self.p + n]
        self.p += n
        return b

    def u8(self): return self.take(1)[0]
    def u32(self): return struct.unpack("<I", self.take(4))[0]
    def i32(self): return struct.unpack("<i", self.take(4))[0]
    def i64(self): return struct.unpack("<q", self.take(8))[0]
    def f64(self): return struct.unpack("<d", self.take(8))[0]

    def string(self):
        return self.take(self.u32()).decode("utf-8", "replace")

    def value(self):
        tag = self.u32()
        if tag == 0: return None
        if tag == 1: return bool(self.u8())
        if tag == 2: return self.f64()
        if tag == 3: return self.string()
        if tag == 4: return self.table() if self.u8() else None
        raise ValueError(f"lua tag {tag} at {self.p - 4}")

    def table(self):
        return [(self.value(), self.value()) for _ in range(self.u32())]


def flatten(t, prefix=""):
    out = {}
    for k, v in t:
        key = f"{prefix}{k}"
        if isinstance(v, list):
            out.update(flatten(v, key + "."))
        else:
            out[key] = v
    return out


def read_header(path, data=None):
    """Header fields as a dict. `data` is the decompressed stream if already loaded."""
    if data is None:
        data = _decompress(open(path, "rb").read())
    r = R(data)
    if r.take(4) != b"tf**":
        raise ValueError("not a tf** save")
    h = {"version": r.u32(), "start_year": r.u32(), "map_w_m": r.u32(), "map_h_m": r.u32(), "unknown": r.u32(),
         "money": r.i64(), "counter": r.u32()}
    h["info"] = r.table()
    h["mods"] = []
    for _ in range(r.u32()):
        m = dict(zip(("id", "source", "path", "name", "extra"), [r.string() for _ in range(5)]))
        m["flags"] = r.u32()
        h["mods"].append(m)
    h["has_preview"], w, ht = r.u8(), r.u32(), r.u32()
    h["preview_size"] = (w, ht)
    n = r.u32()
    h["preview_offset"] = r.p
    h["preview_bytes"] = len(r.take(n))
    h["partial"] = None
    try:
        _read_tail(r, h)
    except Exception as e:  # older formats (568, 585) differ from here on; keep what was read
        h["partial"] = f"{type(e).__name__}: {e}"
        h["header_end"] = None
    h["stream_len"] = len(data)
    return h


def _read_tail(r, h):
    h["stats_i64"] = [r.i64() for _ in range(6)]
    h["stats_i32"] = [r.i32() for _ in range(11)]
    h["stats_pairs"] = [(r.u32(), r.u32()) for _ in range(r.u32())]
    h["stats_u32"] = [r.u32(), r.u32()]
    h["stats2_i64"] = [r.i64() for _ in range(9)]
    h["stats2_u32"] = [r.u32(), r.u32()]
    h["labels"] = [(r.string(), r.u32()) for _ in range(r.u32())]
    h["stats3"] = [r.u32(), r.i64(), r.i64(), r.u32()]
    h["config_mods"] = [r.string() for _ in range(r.u32())]
    h["resources"] = [(r.string(), r.string()) for _ in range(r.u32())]
    h["params"] = [(r.string(), r.table()) for _ in range(r.u32())]
    h["mission"], h["kind"] = r.string(), r.string()
    h["flag"], h["value"] = r.u8(), r.u32()
    h["id"] = r.string()
    h["settings"] = flatten(next((t for k, t in h["params"] if k == ""), []))
    h["header_end"] = r.p


def main():
    for path in sys.argv[1:]:
        print("==", path)
        try:
            h = read_header(path)
        except Exception as e:  # report and carry on with the next save
            print("  FAILED:", e)
            continue
        if h["partial"]:
            print("  PARTIAL (tail not parsed):", h["partial"])
        print(f"  version {h['version']}  start year {h['start_year']}  map {h['map_w_m']} x {h['map_h_m']} m"
              f"  unknown {h['unknown']}  money {h['money']}  counter {h['counter']}")
        print(f"  preview: has={h['has_preview']} size={h['preview_size']} bytes={h['preview_bytes']}")
        print(f"  mods: {len(h['mods'])}  resources: {dict(h.get('resources', []))}")
        print(f"  isMapEditor={h.get('settings', {}).get('isMapEditor')} map.size={h.get('settings', {}).get('map.size')} "
              f"header_end={h['header_end']} stream={h['stream_len']}")


if __name__ == "__main__":
    main()
