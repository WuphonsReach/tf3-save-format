#!/usr/bin/env python3
"""List the model instances of a TF3 save: vehicles, people and animals with their positions.

Usage:
  model_instances.py SAVE.sav [--near X,Y,R] [--prefix PATH] [--stream]

Prints one line per instance: its slot (the instance's place among the instances of the chosen
model paths, in stream order), the model path, the position (x, y, z in metres) and the facing (the first row of the
transform: the direction the model points along x and y). `--near X,Y,R` keeps the instances
within R metres of the point, `--prefix` picks the model paths that start with it (default `vehicle/`;
`characters/` for people, `animal/`, or empty for everything). Only reads: no save is written.

A model instance is the record of docs/models.md: a model id, then a 4 x 4 `f32` transform with
floats 3, 7 and 11 equal to 0 and float 15 equal to 1. The scan looks for that pattern after the
model table, so it can also hit a stray match in other data; the model id has to be inside the
table. It reads the whole stream (about 20 s for a 700 MB stream). A vehicle's own entity id and
its name (`Train 18`) are not next to its instance (docs/entity-names.md), so the output names a
vehicle by model and slot. The slot changes when instances come and go, so it is only good within
one save.
"""
import argparse
import math
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tf3save import decompress  # noqa: E402

_INSTANCE = re.compile(rb"(....)(.{12}\x00\x00\x00\x00.{12}\x00\x00\x00\x00.{12}\x00\x00\x00\x00)"
                       rb"(.{12})\x00\x00\x80\x3f", re.S)


def read_model_table(data):
    """(model paths by id, offset just after the table). The table is the first thing after the
    header (docs/models.md): a u32 count, then per model a `str` source mod, a `str` path and a
    u32 id equal to its index. Found by the first `animal/` path, as the base game's table
    sorts them first."""
    first = data.find(b"animal/")
    if first < 0:
        raise ValueError("no model table found")
    for start in range(max(0, first - 2000), first):
        n = struct.unpack_from("<I", data, start)[0]
        if not 100 < n < 100000:
            continue
        p, paths = start + 4, []
        try:
            for k in range(n):
                length = struct.unpack_from("<I", data, p)[0]
                p += 4 + length
                length = struct.unpack_from("<I", data, p)[0]
                path = data[p + 4:p + 4 + length].decode()
                p += 4 + length
                if struct.unpack_from("<I", data, p)[0] != k:
                    break
                p += 4
                paths.append(path)
            else:
                return paths, p
        except (struct.error, UnicodeDecodeError, MemoryError):
            continue
    raise ValueError("no model table found")


def read_instances(data, prefixes=("vehicle/",), table=None):
    """The model instances whose model path starts with one of `prefixes`, as dicts: `slot` (index
    among the instances of those prefixes, in stream order), `model` (path), `x`, `y`, `z`
    (the translation), `fx`, `fy` (the first row of the transform: the facing) and `offset`.
    Pass `table=read_model_table(data)` to reuse a table already read."""
    paths, end = table or read_model_table(data)
    wanted = {i for i, p in enumerate(paths) if p.startswith(tuple(prefixes))}
    out = []
    for m in _INSTANCE.finditer(data, end):
        mid = struct.unpack("<I", m.group(1))[0]
        if mid not in wanted:
            continue
        x, y, z = struct.unpack("<3f", m.group(3))
        fx, fy = struct.unpack_from("<2f", m.group(2))
        if not all(math.isfinite(v) for v in (x, y, z, fx, fy)):
            continue
        out.append({"slot": len(out), "model": paths[mid], "x": x, "y": y, "z": z,
                    "fx": fx, "fy": fy, "offset": m.start()})
    return out


def short_model(path):
    """`vehicle/truck/benz1912/benz1912_box.mdl` -> `benz1912_box`."""
    return os.path.splitext(path.rsplit("/", 1)[-1])[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("save")
    ap.add_argument("--near", help="X,Y,R")
    ap.add_argument("--prefix", default="vehicle/", help="model path prefix (empty: all)")
    ap.add_argument("--stream", action="store_true")
    args = ap.parse_args()
    raw = open(args.save, "rb").read()
    data = raw if args.stream else decompress(raw)
    near = tuple(float(v) for v in args.near.split(",")) if args.near else None
    for i in read_instances(data, (args.prefix,)):
        if near and math.hypot(i["x"] - near[0], i["y"] - near[1]) > near[2]:
            continue
        print("slot %-6d %-40s x %9.1f y %9.1f z %5.1f  facing %6.2f %6.2f"
              % (i["slot"], short_model(i["model"]), i["x"], i["y"], i["z"], i["fx"], i["fy"]))


if __name__ == "__main__":
    main()
