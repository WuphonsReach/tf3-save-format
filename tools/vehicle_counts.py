#!/usr/bin/env python3
"""Count the vehicles of a TF3 save by carrier, power and load.

Usage: vehicle_counts.py SAVE.sav [--game DIR] [--models]      (prints the counts as JSON)

A vehicle is one model instance whose model path starts with `vehicle/` (docs/models.md); a train or tram is
one instance per unit, locomotives, power cars, middle cars and wagons each. The model path says the folder
(`bus`, `truck`, `tram`, `train`, `waggon`, `ship`, `plane`, `helicopter`, `zeppelin`, `car`). For a base-game
model the install's model file (`base/content/vehicle/<folder>/<name>.zip`, text metadata only, read at run time,
nothing stored) says more: its `transportVehicle.carrier` (ROAD, TRAM, RAIL, WATER, AIR), whether its
`landVehicle.engines` list has an engine, and which cargo classes its compartments take
(docs/vehicle-classes.md). Without the install, or for a mod's model, the folder alone gives the carrier
and the power and load are "unknown" (a `waggon` is taken as unpowered).

Result keys: `from_install` (true when at least one model was read from the install), one key per carrier that has
vehicles (`road`, `tram`, `rail`, `water`, `air`), each a dict of `power` (powered, unpowered, unknown) to
`load` (passenger, cargo, mixed, none, unknown) to count, `helicopters` under `air`, `ambient` (the town traffic:
`car` models, and anything under `vehicle/` that is not a carrier, such as zeppelins), and `models_unread` (how
many distinct models had no metadata). `--models` adds `models`, the count per model path.

Importable: `count_vehicles(data, game_dir=None)` takes the decompressed stream. Reads a save and the install,
writes nothing.
"""
import argparse
import collections
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_instances import read_instances, read_model_table  # noqa: E402
from tf3save import decompress  # noqa: E402

GAME_DIRS = ("~/.steam/steam", "~/.local/share/Steam", "~/snap/steam/common/.local/share/Steam",
             "~/.var/app/com.valvesoftware.Steam/.local/share/Steam")
# The game's own carrier names, and the folder under `vehicle/` that stands in for one without the install.
CARRIERS = {"ROAD": "road", "TRAM": "tram", "RAIL": "rail", "WATER": "water", "AIR": "air"}
FOLDER_CARRIER = {"bus": "road", "truck": "road", "tram": "tram", "train": "rail", "waggon": "rail",
                  "ship": "water", "plane": "air", "helicopter": "air"}


def find_vehicle_dir(game_dir=None):
    """The install's `base/content/vehicle` folder (from `game_dir`, the install folder, or the usual
    Steam places), or None."""
    roots = [os.path.expanduser(game_dir)] if game_dir else \
        [os.path.join(os.path.expanduser(d), "steamapps", "common", "Transport Fever 3") for d in GAME_DIRS]
    for root in roots:
        path = os.path.join(root, "base", "content", "vehicle")
        if os.path.isdir(path):
            return path
    return None


def _block(text, key, start=0):
    """The text between the braces of `key = {` at or after `start`, or None."""
    m = re.compile(r"\b%s = \{" % key).search(text, start)
    if not m:
        return None
    depth, i = 1, m.end()
    while depth and i < len(text):
        depth += (text[i] == "{") - (text[i] == "}")
        i += 1
    return text[m.end():i - 1]


def read_model_info(vdir, path):
    """{carrier, powered, load} for a base-game model from its model file's metadata, or None where the
    install has no such file. `powered` is None where the file gives no land vehicle (ships and aircraft:
    they carry their own engines); `load` is passenger, cargo, mixed or none."""
    parts = path.split("/")
    if vdir is None or len(parts) < 4 or parts[0] != "vehicle":
        return None
    zpath = os.path.join(vdir, parts[1], parts[2] + ".zip")
    if not os.path.isfile(zpath):
        return None
    try:
        with zipfile.ZipFile(zpath) as z:
            text = z.read("/".join(parts[2:])).decode("utf-8", "replace")
    except (KeyError, zipfile.BadZipFile):
        return None
    meta = text[text.find("metadata = {"):]
    tv = _block(meta, "transportVehicle")
    carrier = re.search(r'carrier = "(\w+)"', tv or "")
    if not carrier:
        return None
    land = _block(meta, "landVehicle")
    powered = None
    if land is not None:
        engines = _block(land, "engines")
        powered = bool(engines and engines.strip())
    classes = set()
    for group in re.findall(r"cargoClassesIncluded = \{([^}]*)\}", tv):
        classes.update(re.findall(r'"(\w+)"', group))
    passengers, cargo = "PASSENGERS" in classes, bool(classes - {"PASSENGERS"})
    return {"carrier": CARRIERS.get(carrier.group(1), carrier.group(1).lower()), "powered": powered,
            "load": "mixed" if passengers and cargo else "passenger" if passengers else "cargo" if cargo else "none"}


def count_vehicles(data, game_dir=None, with_models=False):
    table = read_model_table(data)
    vdir = find_vehicle_dir(game_dir)
    per_model = collections.Counter(i["model"] for i in read_instances(data, ("vehicle/",), table))
    out = {"from_install": False}
    ambient = collections.Counter()
    unread = 0
    for path, n in per_model.items():
        folder = path.split("/")[1] if path.count("/") >= 1 else ""
        info = read_model_info(vdir, path)
        if info:
            out["from_install"] = True
        elif folder in FOLDER_CARRIER:
            unread += 1
            info = {"carrier": FOLDER_CARRIER[folder], "powered": False if folder == "waggon" else None, "load": "unknown"}
        else:
            ambient["car" if folder == "car" else "other"] += n
            continue
        if info["powered"] is None:
            power = "powered" if info["carrier"] in ("water", "air") else "unknown"
        else:
            power = "powered" if info["powered"] else "unpowered"
        node = out.setdefault(info["carrier"], {}).setdefault(power, collections.Counter())
        node[info["load"]] += n
        if folder == "helicopter":
            out["air"]["helicopters"] = out["air"].get("helicopters", 0) + n
    out["ambient"] = dict(ambient)
    out["models_unread"] = unread
    if with_models:
        out["models"] = {p: n for p, n in sorted(per_model.items()) if p.split("/")[1] != "car"}
    return out


# index.csv columns (mine_summary.py): units per carrier; `cargo` counts units whose load is cargo or mixed.
INDEX_NAMES = ["veh_road", "veh_tram", "veh_tram_cargo", "veh_rail", "veh_rail_unpowered", "veh_water", "veh_air",
               "veh_air_cargo"]


def index_values(counts):
    """The INDEX_NAMES values for a `count_vehicles` result (empty strings where there is none)."""
    if not counts:
        return [""] * len(INDEX_NAMES)

    def total(carrier, power=None, loads=None):
        return sum(n for p, by_load in (counts.get(carrier) or {}).items() if p != "helicopters"
                   and power in (None, p) for load, n in by_load.items() if loads is None or load in loads)
    return [total("road"), total("tram"), total("tram", loads=("cargo", "mixed")), total("rail"),
            total("rail", "unpowered"), total("water"), total("air"), total("air", loads=("cargo", "mixed"))]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("save")
    ap.add_argument("--game", help="the install folder (default: the usual Steam places)")
    ap.add_argument("--models", action="store_true", help="also give the count per model path")
    args = ap.parse_args()
    data = decompress(open(args.save, "rb").read())
    json.dump(count_vehicles(data, args.game, args.models), sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
