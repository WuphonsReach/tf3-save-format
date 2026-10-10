"""Print the industry chains of a Transport Fever 3 install: recipes, boosters, climates, cargo classes.

Usage: industry_chains.py [--content DIR] [--json] [--out DIR]

Reads the install at run time and writes nothing into it. DIR for --content is the install's
`base/content` folder; without it the usual Steam library locations are tried. The output
goes to stdout, or with --out into `DIR/industry-chains.md` (and `.json` with --json). No
install path is printed.

Reads only text files: `industries/<name>.zip` (`<name>/<name>.con.lua`),
`economy.zip` (`economy/<climate>.eco.lua`) and `cargos/<name>.zip` (`<name>/<name>.cargo.lua`).
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
        eco[c] = dict(removed=removed, init_weight=weights, rank_industries=ranks)
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


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out


def amounts(d):
    return ", ".join(f"{v} {k}" for k, v in d.items())


def markdown(inds, cargos, eco):
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
    if not inds:
        sys.exit("no industries read; is --content the base/content folder?")
    check(inds, cargos, eco)
    data = dict(industries=inds, cargos=cargos, economies=eco)
    md = markdown(inds, cargos, eco)
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
