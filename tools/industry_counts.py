#!/usr/bin/env python3
"""Count the industries of a TF3 save, in total and per kind.

Usage: industry_counts.py SAVE.sav      (prints the counts as JSON)

An industry is one model instance of the kind's main model, `industries/<key>/<key>_sm.mdl` (or, for the sand
excavator, which has none, its `_particles.mdl`; `industry_compass.main_models`). Where that model has no
instance but the key's own `<key>.mdl` has, that one counts (a sand excavator whose `_sm` model is placed only
in the preview block). Its other instances (cranes, sheds, particles) are not counted. A mod's industry that has no such model is missed.

Result: `count`, and `by_key` (industry key to count, keys sorted); null where the save has no readable model
table (the reader raises ValueError).

Importable: `count_industries(data)` takes the decompressed stream. Reads a save, writes nothing.
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from industry_compass import main_models  # noqa: E402
from model_instances import read_instances, read_model_table  # noqa: E402
from tf3save import decompress  # noqa: E402


def count_industries(data):
    try:
        table = read_model_table(data)
    except ValueError:
        return None
    placed = read_instances(data, ("industries/",), table)
    mains = main_models(table[0], {i["model"] for i in placed})
    by_key = collections.Counter(mains[i["model"]] for i in placed if i["model"] in mains)
    return {"count": sum(by_key.values()), "by_key": dict(sorted(by_key.items()))}


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: industry_counts.py SAVE.sav")
    json.dump(count_industries(decompress(open(sys.argv[1], "rb").read())), sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
