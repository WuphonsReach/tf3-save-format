"""Print the industry chains of a Transport Fever 3 install: recipes, boosters, climates, cargo classes,
placement by climate and town cargo by climate.

Usage: industry_chains.py [--content DIR] [--json] [--out DIR]

Reads the install at run time and writes nothing into it. DIR for --content is the install's
`base/content` folder; without it the usual Steam library locations are tried. The output
goes to stdout, or with --out into `DIR/industry-chains.md` (and `.json` with --json). No
install path is printed.

Reads only text files: `industries/<name>.zip` (`<name>/<name>.con.lua`),
`economy.zip` (`economy/<climate>.eco.lua`, `economy/placementparamsutil.lua`) and `cargos/<name>.zip` (`<name>/<name>.cargo.lua`).
Nothing from the install is bundled here. See docs/industry-chains.md.

The files are Lua tables, read here with brace matching and a few regular expressions, not a
Lua interpreter. Anything that does not parse is reported as a warning on stderr, so a mod's
or a later build's changed layout shows up rather than being skipped.
"""
import argparse
import glob
import json
import os
import re
import sys
import zipfile

CLIMATES = ("temperate", "dry", "tropic", "subarctic")
_STEAM_ROOTS = ("~/.steam/steam", "~/.local/share/Steam", "~/snap/steam/common/.local/share/Steam",
                "~/.var/app/com.valvesoftware.Steam/.local/share/Steam")
_GAME = "steamapps/common/Transport Fever 3/base/content"


def find_content():
    for root in _STEAM_ROOTS:
        p = os.path.join(os.path.expanduser(root), _GAME)
        if os.path.isdir(p):
            return p
    return None


def warn(msg):
    print("warning: " + msg, file=sys.stderr)


def strip_comments(text):
    return re.sub(r"--[^\n]*", "", text)


def block(text, key, start=0):
    """The `{...}` after `key` (brace matched), or None."""
    i = text.find(key, start)
    if i < 0:
        return None
    j = text.find("{", i)
    if j < 0:
        return None
    depth = 0
    for k in range(j, len(text)):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return text[j:k + 1]
    return None


def children(tbl):
    """The top-level `{...}` items inside a table body."""
    body = tbl[1:-1]
    out, depth, start = [], 0, None
    for k, c in enumerate(body):
        if c == "{":
            if depth == 0:
                start = k
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                out.append(body[start:k + 1])
    return out


def number(expr):
    """A number or a product such as `22.8125 * 4`."""
    v = 1.0
    for part in expr.split("*"):
        v *= float(part)
    return int(v) if v == int(v) else v


def cargo_name(path):
    m = re.search(r"::/cargos/(\w+)/", path)
    return m.group(1) if m else path


def read_industries(content):
    inds = {}
    for p in sorted(glob.glob(os.path.join(content, "industries", "*.zip"))):
        z = zipfile.ZipFile(p)
        for n in z.namelist():
            if not n.endswith(".con.lua"):
                continue
            t = strip_comments(z.read(n).decode(errors="replace"))
            if "stockListConfig" not in t:
                continue
            name = n.split("/")[0]
            stocks = [(k, cargo_name(c)) for k, c in
                      re.findall(r'type\s*=\s*"(INPUT_STOCK|OUTPUT_STOCK)"\s*,\s*cargoType\s*=\s*"([^"]+)"', t)]
            rules_t = block(t, "rules")
            if rules_t is None:
                warn(f"{name}: no rules block")
                continue
            ins = [c for k, c in stocks if k == "INPUT_STOCK"]
            rules = []
            for r in children(rules_t):
                inp = block(r, "input")
                amounts = [int(x) for x in re.findall(r"-?\d+", children(inp)[0])] if inp and children(inp) else []
                req = block(r, "requiredInput")
                required = [int(x) for x in re.findall(r"\d+", req)] if req else []
                out_t = block(r, "output")
                outs = {cargo_name(k): number(v) for k, v in
                        re.findall(r'\[\s*"([^"]+)"\s*\]\s*=\s*([\d.*\s]+?)\s*[,}]', out_t or "")}
                cap = re.search(r"capacity\s*=\s*([\d.]+(?:\s*\*\s*[\d.]+)*)", re.sub(r"\binput\s*=\s*\{.*?\}\s*,", "", r, flags=re.S))
                if len(amounts) > len(ins):
                    warn(f"{name}: rule has {len(amounts)} input amounts for {len(ins)} input stocks")
                rules.append(dict(
                    takes={ins[i]: a for i, a in enumerate(amounts) if i < len(ins) and a},
                    required=[ins[i - 1] for i in required if 0 < i <= len(ins)],
                    gives=outs,
                    booster=bool(re.search(r"booster\s*=\s*true", r)),
                    cycle=number(cap.group(1)) if cap else None))
            cats = sorted(set(re.findall(r'"(\w+)\.eco"', block(t, "categoryList") or "")))
            inds[name] = dict(climates=cats, stocks=stocks, rules=rules)
    return inds


def read_cargos(content):
    out = {}
    for p in sorted(glob.glob(os.path.join(content, "cargos", "*.zip"))):
        z = zipfile.ZipFile(p)
        for n in z.namelist():
            if not n.endswith(".cargo.lua"):
                continue
            t = strip_comments(z.read(n).decode(errors="replace"))
            m = re.search(r"cargoClasses\s*=\s*\{([^}]*)\}", t)
            if not m:
                continue
            classes = re.findall(r'"(\w+)"', m.group(1))
            out[n.split("/")[0]] = dict(
                classes=classes,
                climates=sorted(set(re.findall(r'"(\w+)\.eco"', block(t, "categoryList") or ""))))
    return out


def named_children(tbl):
    """(key, `{...}` body) pairs of the `key = {...}` items at the top level of a table body."""
    body = tbl[1:-1]
    out, depth, i = [], 0, 0
    while i < len(body):
        c = body[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif depth == 0:
            m = re.match(r"(\w+)\s*=\s*\{", body[i:])
            if m:
                start = i + m.end() - 1
                d = 0
                for k in range(start, len(body)):
                    d += (body[k] == "{") - (body[k] == "}")
                    if d == 0:
                        out.append((m.group(1), body[start:k + 1]))
                        i = k
                        break
        i += 1
    return out


def words(body, key):
    """The quoted words of a `key = { "a", "b" }` list inside body, or []."""
    t = block(body, key + " =")
    return re.findall(r'"(\w+)"', t) if t else []


def read_placement(content):
    """The shared tables of `economy/placementparamsutil.lua`: placement params per industry
    and the cargo categories (the cargo a town can demand are those with a land use)."""
    z = zipfile.ZipFile(os.path.join(content, "economy.zip"))
    try:
        t = strip_comments(z.read("economy/placementparamsutil.lua").decode(errors="replace"))
    except KeyError:
        warn("economy/placementparamsutil.lua missing")
        return {}, {}
    inds, cats = {}, {}
    for fn, out in (("getAllParams", inds), ("getCargoCategories", cats)):
        top = block(t, "placementparamsutil." + fn)  # the first table after the name is the returned one
        if not top:
            warn(f"{fn} not found in placementparamsutil.lua")
            continue
        for name, body in named_children(top):
            d = {}
            for k in ("buildOrder", "initWeight", "tier", "townConsumptionFactor"):
                m = re.search(r"\b" + k + r"\s*=\s*([\d.]+)", body)
                if m:
                    d[k] = number(m.group(1))
            d["tags"] = words(body, "tags")
            d["requires"] = words(body, "requiredIndustryTags")
            d["land_uses"] = words(body, "landUses")
            out[name] = d
    return inds, cats


def read_economies(content):
    z = zipfile.ZipFile(os.path.join(content, "economy.zip"))
    eco = {}
    for c in CLIMATES + ("all",):
        try:
            t = strip_comments(z.read(f"economy/{c}.eco.lua").decode(errors="replace"))
        except KeyError:
            warn(f"economy/{c}.eco.lua missing")
            continue
        removed = sorted(re.findall(r"placementParams\.(\w+)\s*=\s*nil", t))
        weights = {a: int(b) for a, b in re.findall(r"placementParams\.(\w+)\.initWeight\s*=\s*(\d+)", t)}
        ranks = {}
        rt = block(t, "companyRankRequiredIndustries")
        for rank, body in re.findall(r"\[(\d+)\]\s*=\s*(\{[^}]*\})", rt or ""):
            ranks[int(rank)] = sorted(re.findall(r"(\w+)\s*=\s*[\d.]+", body))
        cats_removed = sorted(re.findall(r"cargoCategories\.(\w+)\s*=\s*(?:nil|nin)\b", t))
        requires = {a: re.findall(r'"(\w+)"', b)
                    for a, b in re.findall(r"placementParams\.(\w+)\.requiredIndustryTags\s*=\s*(\{[^}]*\})", t)}
        cat_requires = {a: re.findall(r'"(\w+)"', b)
                        for a, b in re.findall(r"cargoCategories\.(\w+)\.requiredIndustryTags\s*=\s*(\{[^}]*\})", t)}
        build_order = {a: int(b) for a, b in re.findall(r"placementParams\.(\w+)\.buildOrder\s*=\s*(\d+)", t)}
        fb = block(t, "industryPlacementFallbacks")
        fallbacks = dict(re.findall(r'(\w+)\s*=\s*"(\w+)"', fb)) if fb else {}
        eco[c] = dict(removed=removed, init_weight=weights, rank_industries=ranks,
                      categories_removed=cats_removed, requires=requires, category_requires=cat_requires,
                      build_order=build_order, fallbacks=fallbacks)
    return eco


def check(inds, cargos, eco):
    """Warn where the industry files and the economy files disagree about availability."""
    for c in CLIMATES:
        if c not in eco:
            continue
        for name, d in inds.items():
            listed = c in d["climates"]
            removed = name in eco[c]["removed"]
            if listed == removed:
                warn(f"{name} in {c}: industry file says {'present' if listed else 'absent'}, "
                     f"economy file says {'removed' if removed else 'kept'}")


def check_categories(cargos, cats, eco):
    """Warn where an economy's removed cargo categories differ from the cargo files' climates."""
    for c in CLIMATES:
        if c not in eco:
            continue
        for name in cats:
            if name not in cargos:
                continue
            listed = c in cargos[name]["climates"]
            removed = name in eco[c]["categories_removed"]
            if listed == removed:
                warn(f"cargo {name} in {c}: cargo file says {'present' if listed else 'absent'}, "
                     f"economy file says {'category removed' if removed else 'category kept'}")


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out


def amounts(d):
    return ", ".join(f"{v} {k}" for k, v in d.items())


def markdown(inds, cargos, eco, place, cats):
    lines = ["# Industry chains", ""]
    prod, extr = [], []
    for name, d in sorted(inds.items()):
        main = [r for r in d["rules"] if not r["booster"]]
        boost = [r for r in d["rules"] if r["booster"]]
        if main and not any(r["takes"] for r in main):
            b = "; ".join(amounts(r["takes"]) for r in boost)
            extr.append([name, amounts(main[0]["gives"]), b])
        else:
            takes = []
            for r in main:
                s = amounts(r["takes"])
                if r["required"]:
                    s += f" (requires {', '.join(r['required'])})"
                takes.append(s)
            prod.append([name, " / ".join(takes), "; ".join(dict.fromkeys(amounts(r["gives"]) for r in main))])
    lines += ["## Recipes", ""] + table(["Industry", "Takes", "Gives"], prod) + [""]
    lines += ["## Extractive industries", ""] + table(["Industry", "Gives", "Booster (per cycle)"], extr) + [""]
    lines += ["## Climates", ""] + table(["Industry"] + list(CLIMATES), [
        [n] + ["x" if c in d["climates"] else "" for c in CLIMATES] for n, d in sorted(inds.items())]) + [""]
    lines += ["## Cargo", ""] + table(["Cargo", "Classes"] + list(CLIMATES), [
        [n, ", ".join(d["classes"])] + ["x" if c in d["climates"] else "" for c in CLIMATES]
        for n, d in sorted(cargos.items())]) + [""]
    if place:
        lines += ["## Placement by climate", ""]
        head = ["Industry", "Kind", "Order", "Tier", "Weight", "Needs nearby"] + list(CLIMATES)
        rows = []
        for n, d in sorted(place.items(), key=lambda kv: (kv[1].get("buildOrder", 0), kv[0])):
            main = [r for r in inds.get(n, {}).get("rules", []) if not r["booster"]]
            kind = "extractive" if main and not any(r["takes"] for r in main) else "processing"
            row = [n, kind, str(d.get("buildOrder", "")), str(d.get("tier", "")), str(d.get("initWeight", "")),
                   ", ".join(d["requires"])]
            for c in CLIMATES:
                e = eco.get(c)
                if not e:
                    row.append("")
                elif n in e["removed"]:
                    row.append("")
                else:
                    extra = []
                    if n in e["init_weight"]:
                        extra.append(f"weight {e['init_weight'][n]}")
                    if n in e["requires"]:
                        extra.append("needs " + ", ".join(e["requires"][n]))
                    if n in e["build_order"]:
                        extra.append(f"order {e['build_order'][n]}")
                    row.append("x" + (" (" + "; ".join(extra) + ")" if extra else ""))
            rows.append(row)
        lines += table(head, rows) + [""]
    if cats:
        lines += ["## Town cargo by climate", ""]
        head = ["Cargo", "District", "Tier", "Factor"] + list(CLIMATES)
        rows = []
        for n, d in sorted(cats.items(), key=lambda kv: (kv[1].get("tier", 9), kv[1]["land_uses"], kv[0])):
            if not d["land_uses"]:
                continue
            row = [n, ", ".join(u.lower() for u in d["land_uses"]), str(d.get("tier", "")),
                   str(d.get("townConsumptionFactor", ""))]
            row += ["x" if c in eco and n not in eco[c]["categories_removed"] else "" for c in CLIMATES]
            rows.append(row)
        lines += table(head, rows) + [""]
        other = {c: [n for n in e["categories_removed"] if n in cats and not cats[n]["land_uses"]]
                 for c, e in eco.items() if c in CLIMATES}
        lines += ["## Other cargo categories an economy removes", ""] + table(
            ["Economy", "Removed (no district)"], [[c, ", ".join(v)] for c, v in other.items()]) + [""]
    ranks = sorted({r for e in eco.values() for r in e["rank_industries"]})
    rows = []
    for r in ranks:
        cells = []
        for c in CLIMATES + ("all",):
            cells.append(", ".join(eco.get(c, {}).get("rank_industries", {}).get(r, [])))
        rows.append([str(r)] + cells)
    lines += ["## Industries by rank", ""] + table(["Rank"] + list(CLIMATES) + ["all"], rows) + [""]
    w = [[c, ", ".join(f"{k} {v}" for k, v in e["init_weight"].items())] for c, e in eco.items() if e["init_weight"]]
    if w:
        lines += ["## initWeight set by the economy", ""] + table(["Economy", "Industry weight"], w) + [""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--content", help="the install's base/content folder")
    ap.add_argument("--json", action="store_true", help="print JSON instead of Markdown")
    ap.add_argument("--out", help="write industry-chains.md (and .json with --json) into this directory")
    a = ap.parse_args()
    content = a.content or find_content()
    if not content or not os.path.isdir(content):
        sys.exit("base/content not found; pass --content DIR")
    inds, cargos, eco = read_industries(content), read_cargos(content), read_economies(content)
    place, cats = read_placement(content)
    if not inds:
        sys.exit("no industries read; is --content the base/content folder?")
    check(inds, cargos, eco)
    check_categories(cargos, cats, eco)
    data = dict(industries=inds, cargos=cargos, economies=eco, placement=place, cargo_categories=cats)
    md = markdown(inds, cargos, eco, place, cats)
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "industry-chains.md"), "w") as f:
            f.write(md + "\n")
        if a.json:
            with open(os.path.join(a.out, "industry-chains.json"), "w") as f:
                json.dump(data, f, indent=1)
    elif a.json:
        json.dump(data, sys.stdout, indent=1)
        print()
    else:
        print(md)


if __name__ == "__main__":
    main()
