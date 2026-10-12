#!/usr/bin/env python3
"""Test the compass words in industry names against where the industries stand, and plot them.

Usage:
  industry_compass.py SAVE.sav OUT.svg [--all-names] [--stream]

The game names a second industry of a kind near a town `<Town> <Kind> North` (or South, East, West)
when it lies in that direction from the town (docs/compass.md). This reads a save's town names, the
street edges (the town centres), the industry model instances and the entity names, finds the
industries with a compass word, and draws each one against its town's centre, x to the right and y
up (the game's own frame). It prints, for every compass name, how many same-kind industries near
the town lie in the sector the word names under the game frame (x east, y north) and under the sun
frame (north is +x, east is -y), so the two can be compared (docs/compass.md).

The save keeps no town position. A town's centre is the mean of the end points of its `town_*`
street edges, taken per connected group (a group is one town). Which group is which town comes from
the industry names: an industry's name starts with a town's name, and each town's count of
industries per kind has to match its group's. An industry's position is the origin of the main
model of its kind (`industries/KEY/KEY_sm.mdl`, or the first `*_particles.mdl` of the folder). The
name table does not say which instance carries which name, so a compass name is tied to an
instance by its sector, and only where exactly one same-kind instance near the town lies there.

Only reads: no save is written. The SVG is drawn with the standard library; a PNG is a screenshot of
it from a browser.
"""
import argparse
import collections
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tf3save as t  # noqa: E402
from model_instances import read_instances, read_model_table  # noqa: E402
from save_header import read_header  # noqa: E402
from street_edges import read_edges  # noqa: E402

# the label the game puts in a name, where it is not the key in title case (docs/glossary.md)
LABELS = {"saw_mill": "Saw Mill", "food_factory": "Canning Factory", "farm": "Crop Farm", "forest": "Logging Camp",
          "sand_excavator": "Sand Dredger", "printing_press": "Printing Factory", "tool_factory": "Tools Factory",
          "bricks_works": "Brickworks", "glass_works": "Glassworks", "oil_platform": "Oil Platform",
          "fishing_grounds": "Fishing Grounds", "cement_plant": "Cement Plant"}
WORDS = {"North": "N", "South": "S", "East": "E", "West": "W"}
# buildings the player places are named the same way (a name of the town and the kind); model -> label in the name
BUILDINGS = {"depots/road/road_maint_station/road_maint_station.mdl": "Maintenance Building",
             "depots/rail/rail_maint_station/rail_maint_station.mdl": "Maintenance Building",
             "depots/water/water_maint_station/water_maint_station.mdl": "Maintenance Building",
             "depots/road/road_depot/road_depot.mdl": "Road Depot",
             "depots/road/tram_depot/tram_depot.mdl": "Tram Depot",
             "depots/rail/rail_depot.mdl": "Rail Depot",
             "depots/water/water_depot.mdl": "Ship Depot",
             "assets/ingo_bootsschuppen/ingo_bootsschuppen.mdl": "Boathouse"}


def label(key):
    return LABELS.get(key) or key.replace("_", " ").title()


# the eight ways to lay east and north on the map's x and y: (swap, a, b) with east = a * (y if swap else x)
# and north = b * (x if swap else y). `game` is x east, y north; `sun` is north +x, east -y (docs/compass.md).
FRAMES = {"game": (False, 1, 1), "sun": (True, -1, 1)}
for _swap in (False, True):
    for _a in (1, -1):
        for _b in (1, -1):
            _name = "east %s%s, north %s%s" % ("+-"[_a < 0], "y" if _swap else "x", "+-"[_b < 0], "x" if _swap else "y")
            if (_swap, _a, _b) not in FRAMES.values():
                FRAMES[_name] = (_swap, _a, _b)


def sector(dx, dy, frame):
    """N, E, S or W of an offset (dx, dy) in map metres under a frame of FRAMES: the axis with the
    larger part decides."""
    swap, a, b = FRAMES[frame]
    east, north = a * (dy if swap else dx), b * (dx if swap else dy)
    return ("E" if east > 0 else "W") if abs(east) >= abs(north) else ("N" if north > 0 else "S")


def main_models(paths):
    """{model path: industry key}: the main model of each industry folder."""
    keys = {p.split("/")[1] for p in paths if p.startswith("industries/") and p.count("/") >= 2}
    found = {}
    for k in sorted(keys):
        sm = "industries/%s/%s_sm.mdl" % (k, k)
        if sm in paths:
            found[sm] = k
            continue
        part = sorted(p for p in paths if p.startswith("industries/%s/" % k) and p.endswith("_particles.mdl"))
        if part:
            found[part[0]] = k
    return found


def town_clusters(edges):
    """One dict per connected group of `town_*` street edges: centre, node count, its edges."""
    use = [e for e in edges if (e["type"] or "").startswith("town_")]
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for e in use:
        parent[find(e["p0"][:2])] = find(e["p1"][:2])
    groups = collections.defaultdict(list)
    for p in list(parent):
        groups[find(p)].append(p)
    out = []
    for root, pts in groups.items():
        out.append({"c": (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)), "n": len(pts),
                    "edges": [(e["p0"][0], e["p0"][1], e["p1"][0], e["p1"][1]) for e in use if find(e["p0"][:2]) == root]})
    out.sort(key=lambda c: -c["n"])
    return out


def read(path, stream=False):
    raw = open(path, "rb").read()
    data = raw if stream else t.decompress(raw)
    names = t.entity_names(data)
    towns = t.town_names(data)
    table = read_model_table(data)
    mains = main_models(table[0])
    inds = [{"kind": label(mains[i["model"]]), "x": i["x"], "y": i["y"]}
            for i in read_instances(data, ("industries/",), table) if i["model"] in mains]
    inds += [{"kind": BUILDINGS[i["model"]], "x": i["x"], "y": i["y"]}
             for i in read_instances(data, tuple(BUILDINGS), table) if i["model"] in BUILDINGS]
    clusters = town_clusters(read_edges(data))
    return data, names, towns, inds, clusters[:len(towns or ())]       # the biggest groups: one per town


def assign(towns, inds, clusters, names):
    """Tie each town to a cluster; give each industry its nearest cluster. Returns {town: cluster index}."""
    for i in inds:
        i["cl"] = min(range(len(clusters)), key=lambda k: math.hypot(i["x"] - clusters[k]["c"][0], i["y"] - clusters[k]["c"][1]))
    keys = sorted({i["kind"] for i in inds})
    per_town = {tw: collections.Counter() for tw in towns}
    for n in set(names):
        for tw in towns:
            if n.startswith(tw + " "):
                rest = re.sub(r"( #\d+| North| South| East| West)$", "", n[len(tw) + 1:])
                for k in keys:
                    if rest == k:
                        per_town[tw][k] += 1
                        break
    def score(tw, k):
        have = collections.Counter(i["kind"] for i in inds if i["cl"] == k)
        return sum(min(c, have[key]) for key, c in per_town[tw].items())
    town_cl, used = {}, set()
    for tw, k in sorted(((tw, k) for tw in towns for k in range(len(clusters))), key=lambda tk: -score(*tk)):
        if tw not in town_cl and k not in used:
            town_cl[tw] = k
            used.add(k)
    return town_cl, per_town


def compass_names(towns, names):
    out = []
    for n in sorted(set(names)):
        for tw in towns:
            m = re.match(r"%s (.+) (North|South|East|West)$" % re.escape(tw), n)
            if m:
                out.append((n, tw, m.group(1), WORDS[m.group(2)]))
    return out


ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")


def icon_symbols():
    """`<symbol>`s for tools/icons/{sunrise,sunset}.svg (64 x 64, drawn in `currentColor`), their clip
    ids made unique so the three can sit in one document. A missing file leaves its icon out."""
    out = {}
    for name in ("sunrise", "sunset"):
        try:
            text = open(os.path.join(ICON_DIR, name + ".svg"), encoding="utf-8").read()
        except OSError:
            continue
        inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", text, flags=re.S).replace('id="sky"', 'id="sky-%s"' % name)
        out[name] = '<symbol id="icon-%s" viewBox="0 0 64 64">%s</symbol>' % (name, inner.replace("url(#sky)", "url(#sky-%s)" % name))
    return out


def svg(panels, title, sun=True):
    far = max([math.hypot(i["dx"], i["dy"]) for p in panels for i in p["cands"]] + [1000.0])
    rng = math.ceil(far * 1.03 / 1000.0) * 1000.0
    cols = 2 if len(panels) <= 4 else 3 if len(panels) <= 9 else 4
    w = 470 if cols < 4 else 430
    rows = -(-len(panels) // cols)
    s = (w / 2 - 34) / rng
    head, strip = 78, 36
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif" font-size="12">'
           % (w * cols, head + (w + strip) * rows), '<rect width="100%" height="100%" fill="#fff"/>',
           '<text x="12" y="22" font-size="15" font-weight="bold">%s</text>' % title.partition(" (")[0],
           '<text x="12" y="38" fill="#555">%s</text>' % title.partition(" (")[2].rstrip(")"),
           '<text x="12" y="54" fill="#555">x right, y up (the game\'s frame); rings every 1 km; shaded = the quarter the compass word names; '
           'dark blue = of that kind, near the town, inside it; hollow = outside</text>']
    if sun:
        out.append('<text x="12" y="70" fill="#555">orange = where the Morning (sunrise) and Evening (sunset) sun stand on the screen (docs/compass.md)</text>')
    symbols = icon_symbols() if sun else {}
    if symbols:
        out.append("<defs>%s</defs>" % "".join(symbols.values()))
    for k, p in enumerate(panels):
        cell_y = head + (k // cols) * (w + strip)
        ox, oy = (k % cols) * w + w / 2, cell_y + strip + w / 2
        inside = [i for i in p["cands"] if i["sec"] == p["word"]]
        d = rng * s * 0.97
        g = ['<g>', '<text x="%.0f" y="%.0f" font-weight="bold" fill="#0f2a6b">%s</text>' % (ox - w / 2 + 8, cell_y + 18, p["name"]),
             '<text x="%.0f" y="%.0f" font-size="11" fill="#555">%d of %d %s near %s lie in the %s quarter</text>'
             % (ox - w / 2 + 8, cell_y + 32, len(inside), len(p["cands"]), p["kind"], p["town"], p["word"]),
             '<rect x="%.0f" y="%.0f" width="%d" height="%d" fill="#fafafa" stroke="#bbb"/>' % (ox - w / 2 + 6, oy - w / 2 + 6, w - 12, w - 12)]
        wedge = {"N": (-d, -d, d, -d), "S": (-d, d, d, d), "E": (d, -d, d, d), "W": (-d, -d, -d, d)}[p["word"]]
        g.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#17398f" fill-opacity="0.08"/>'
                 % (ox, oy, ox + wedge[0], oy + wedge[1], ox + wedge[2], oy + wedge[3]))
        for r in range(1000, int(rng) + 1, 1000):
            g.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#ddd"/>' % (ox, oy, r * s))
            g.append('<text x="%.1f" y="%.1f" fill="#aaa" font-size="10" text-anchor="end">%d km</text>' % (ox - 3, oy - r * s - 2, r // 1000))
        g.append('<path d="M%.1f %.1fL%.1f %.1fM%.1f %.1fL%.1f %.1f" stroke="#ccc" stroke-dasharray="4 4"/>'
                 % (ox - d, oy - d, ox + d, oy + d, ox - d, oy + d, ox + d, oy - d))
        g.append('<path d="M%.1f %.1fH%.1fM%.1f %.1fV%.1f" stroke="#bbb"/>' % (ox - d, oy, ox + d, ox, oy - d, oy + d))
        for lab, lx, ly in (("N", ox, oy - d - 4), ("S", ox, oy + d + 14), ("E", ox + d + 8, oy + 4), ("W", ox - d - 8, oy + 4)):
            g.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-weight="bold" fill="#666">%s</text>' % (lx, ly, lab))
        # the sun's path on the screen (docs/compass.md): Morning towards -y, Evening towards +y
        for nm, (ix, iy), tip in (("sunrise", (ox + 26, oy + d - 8), "Morning sun: -y"),
                                  ("sunset", (ox + 26, oy - d - 5), "Evening sun: +y")):
            if nm in symbols:
                g.append('<use href="#icon-%s" x="%.1f" y="%.1f" width="34" height="34" color="#e07000" fill="currentColor"><title>%s</title></use>'
                         % (nm, ix - 17, iy - 17, tip))
                g.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="11" fill="#b35900">%s</text>'
                         % (ix, iy + 22.5, "rise" if nm == "sunrise" else "set"))
        cx, cy = p["centre"]
        for x0, y0, x1, y1 in p["edges"]:
            g.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#888" stroke-width="1.2"/>'
                     % (ox + (x0 - cx) * s, oy - (y0 - cy) * s, ox + (x1 - cx) * s, oy - (y1 - cy) * s))
        g.append('<path d="M%.1f %.1fH%.1fM%.1f %.1fV%.1f" stroke="#000" stroke-width="2"/>' % (ox - 7, oy, ox + 7, ox, oy - 7, oy + 7))
        g.append('<text x="%.1f" y="%.1f" font-weight="bold">%s</text>' % (ox + 9, oy + 18, p["town"]))
        for i in p["cands"]:
            hit = i["sec"] == p["word"]
            g.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s" stroke="%s" stroke-width="2"/>'
                     % (ox + i["dx"] * s, oy - i["dy"] * s, 7 if hit else 6, "#17398f" if hit else "#fff", "#fff" if hit else "#555"))
            if len(p["cands"]) <= 3:                      # few enough to label without crowding
                x_off = i["dx"] * s
                anchor = "end" if x_off > w / 2 - 90 else "start" if x_off < -w / 2 + 90 else "middle"
                g.append('<text x="%.1f" y="%.1f" text-anchor="%s" fill="%s">%.1f km %s</text>'
                         % (ox + x_off + {"end": -9, "start": 9, "middle": 0}[anchor], oy - i["dy"] * s - 11, anchor,
                            "#0f2a6b" if hit else "#555", math.hypot(i["dx"], i["dy"]) / 1000, i["sec"]))
        g.append('</g>')
        out += g
    out.append('</svg>')
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("save")
    ap.add_argument("out")
    ap.add_argument("--stream", action="store_true", help="the file is a decompressed stream")
    ap.add_argument("--max-panels", type=int, default=6, help="draw at most this many panels, the most telling first "
                    "(default 6): exactly one same-kind candidate in the named quarter, then more candidates near the "
                    "town, then a clearer margin")
    ap.add_argument("--no-sun", action="store_true", help="leave the sunrise and sunset icons off the panels")
    args = ap.parse_args()
    data, names, towns, inds, clusters = read(args.save, args.stream)
    if not towns or not clusters:
        sys.exit("no towns or no town streets found")
    town_cl, per_town = assign(towns, inds, clusters, names)
    print("towns %d, street groups kept %d, industries and depots %d" % (len(towns), len(clusters), len(inds)))
    for tw in towns:
        c = clusters[town_cl[tw]]["c"] if tw in town_cl else None
        print("  %-14s group %s centre %s" % (tw, town_cl.get(tw), "%.0f, %.0f" % c if c else "-"))
    kinds = {i["kind"] for i in inds}
    panels, tally = [], collections.Counter()
    for name, tw, lab, word in compass_names(towns, names):
        if tw not in town_cl or lab not in kinds:
            print("%-34s skipped (town or kind not matched)" % name)
            continue
        c = clusters[town_cl[tw]]
        cands = [i for i in inds if i["kind"] == lab and i["cl"] == town_cl[tw]]
        for i in cands:
            i["dx"], i["dy"] = i["x"] - c["c"][0], i["y"] - c["c"][1]
        res = {}
        for frame in FRAMES:
            n_fit = sum(sector(i["dx"], i["dy"], frame) == word for i in cands)
            res[frame] = n_fit
            tally[(frame, "some")] += n_fit >= 1
            tally[(frame, "one")] += n_fit == 1
        print("%-36s %2d near the town; in the %s sector: game frame %d, sun frame %d"
              % (name, len(cands), word, res["game"], res["sun"]))
        for i in cands:
            i["sec"] = sector(i["dx"], i["dy"], "game")
        panels.append({"name": name, "town": tw, "kind": lab, "word": word, "centre": c["c"], "edges": c["edges"], "cands": cands})
    print("compass names: %d. Names with a candidate in the sector the word names, and with exactly one, per frame:" % len(panels))
    for frame in sorted(FRAMES, key=lambda f: -tally[(f, "some")]):
        print("  %-28s %2d  %2d%s" % (frame, tally[(frame, "some")], tally[(frame, "one")],
                                      "  (game: x east, y north)" if frame == "game" else "  (sun: north +x, east -y)" if frame == "sun" else ""))
    for p in panels:
        inside = [i for i in p["cands"] if i["sec"] == p["word"]]
        margin = max([max(abs(i["dx"]), abs(i["dy"])) / (min(abs(i["dx"]), abs(i["dy"])) or 1.0) for i in inside] or [0])
        p["rank"] = (len(inside) != 1, len(inside), -len(p["cands"]), -margin)
    panels.sort(key=lambda p: p["rank"])
    if len(panels) > args.max_panels:
        print("drawing the %d most telling of %d panels (--max-panels)" % (args.max_panels, len(panels)))
        panels = panels[:args.max_panels]
    if panels:
        hd = read_header(args.save) if not args.stream else {}
        where = ""
        if hd:
            clim = re.search(r"climates/(\w+)/", dict(hd["resources"]).get("climate", "") if not isinstance(hd["resources"], dict) else hd["resources"].get("climate", ""))
            where = " (seed %s, %s, %d x %d m, start year %s)" % (hd["map_seed"], clim.group(1) if clim else "?", hd["map_w_m"], hd["map_h_m"], hd["start_year"])
        open(args.out, "w").write(svg(panels, "Compass-named industries and buildings against their town's centre" + where,
                                           sun=not args.no_sun))
        print("wrote", args.out)
    else:
        print("no compass-named industry found")


if __name__ == "__main__":
    main()
