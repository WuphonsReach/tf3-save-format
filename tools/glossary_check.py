#!/usr/bin/env python3
"""Point out places where a note says a player's word or an on-screen label and should say the key.

Usage: glossary_check.py [REPO_ROOT] [PATH ...] [--summary] [--ambiguous] [--include-quoted]
       glossary_check.py [REPO_ROOT] --since REV [PATH ...]
       glossary_check.py [REPO_ROOT] --stdin

Read only, no saves. The word lists come from the tables in docs/glossary.md, so the glossary is
the one place to fix: a row's "Players say" cell gives words that should be the row's key, and
where the "Label" cell differs from the key (Canned Food against tinned_food) the label is
checked too. A key written with spaces ("tinned food") counts as the key. Skipped as not prose:
fenced code, a capitalised word in mid-sentence (a proper name such as a line's name or a quoted label), inline code spans, link targets, URLs, and text in double quotes (the notes quote
the screen's own wording; --include-quoted checks those too). A label is only checked when the
row has one plain key: rows keyed by `small_*` or a string id would flag the repo's own
"road stop" and "port". Also skipped: a word inside a longer key or label that the glossary
names ("metal" in "sheet metal", "steel" in "steel mill", "stop" in "road stop"), and a word
whose own key is in code font within 60 characters ("the two `modular_terminal` cargo stations").

PATH defaults to docs/*.md and tools/*.md. docs/glossary.md is never checked (it lists the words).
`--since REV` checks only the lines added since git revision REV, so a change can be checked
before it is committed. `--stdin` checks text from standard input, for example a commit message:
    git log -1 --format=%B | python3 -I tools/glossary_check.py --stdin

A word the glossary marks "(ambiguous)", and the bold words in its "Ambiguous words" list, are
skipped unless --ambiguous: they may be right. `--word W` (repeatable) checks only those words,
for example `--ambiguous --word dock --word coach`. A hit is a lead, not a defect (a quoted player's
word, a cargo class such as "bulk", a word used in its plain sense). Open the line and judge.
Exit status is 0 unless the glossary cannot be read.
"""
import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

GLOSSARY = "docs/glossary.md"


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def plain_key(cell):
    """The key when the cell is exactly one plain lowercase key in backticks, else None."""
    m = re.fullmatch(r"`([a-z][a-z0-9_]*)`", cell)
    return m.group(1) if m else None


def norm(s):
    return re.sub(r"[\s_]+", " ", s.strip().lower())


def parse_glossary(text):
    """Return a list of entries {word, key, kind, ambiguous, note}."""
    entries = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and set(lines[i + 1].replace("|", "").strip()) <= set("-: "):
            head = [h.lower() for h in cells(lines[i])]
            j = i + 2
            rows = []
            while j < len(lines) and lines[j].startswith("|"):
                rows.append(cells(lines[j]))
                j += 1
            say = next((k for k, h in enumerate(head) if "say" in h or "write" in h and k > 0), None)
            say = head.index("players say") if "players say" in head else say
            lab = head.index("label") if "label" in head else None
            for r in rows:
                if len(r) != len(head) or say is None:
                    continue
                key_cell = r[0].replace("`", "")
                simple = plain_key(r[0])
                for word in r[say].split(","):
                    word = word.strip()
                    amb = "ambiguous" in word
                    word = re.sub(r"\s*\(.*?\)", "", word).strip()
                    if word and norm(word) != norm(simple or key_cell):
                        entries.append(dict(word=word, key=key_cell, kind="alias", ambiguous=amb))
                if lab is not None and simple and norm(r[lab]) != norm(simple):
                    entries.append(dict(word=r[lab], key=key_cell, kind="label", ambiguous=False))
            i = j
        else:
            i += 1
    # the "Ambiguous words" list: "- **a, b**: ..." (bold words)
    for ln in lines:
        m = re.match(r"- \*\*(.+?)\*\*: (.*)", ln)
        if m:
            for word in m.group(1).split(","):
                entries.append(dict(word=word.strip(), key=re.sub(r"[`*]", "", m.group(2))[:80], kind="ambiguous", ambiguous=True))
    # one entry per word: the first listed (a table row) wins over a later one
    seen, out = set(), []
    for e in entries:
        k = norm(e["word"])
        if k in seen:
            continue
        seen.add(k)
        out.append(e)
    return out


def known_names(text):
    """Regexes for the multi-word keys and labels the glossary names (`sheet_metal`, Road Stop)."""
    names = {norm(k) for k in re.findall(r"`([a-z][a-z0-9_]*)`", text)}
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("|") and i + 1 < len(lines) and set(lines[i + 1].replace("|", "").strip()) <= set("-: "):
            head = [h.lower() for h in cells(ln)]
            if "label" in head:
                lab = head.index("label")
                for row in lines[i + 2:]:
                    if not row.startswith("|"):
                        break
                    r = cells(row)
                    if len(r) == len(head):
                        names |= {norm(w) for w in re.split(r",| or ", r[lab]) if w.strip()}
    names = sorted((n for n in names if " " in n), key=len, reverse=True)
    return [re.compile(r"(?<!\w)" + re.escape(n).replace(r"\ ", r"[\s_-]+") + r"(?:s|es)?(?!\w)", re.I) for n in names]


def key_patterns(key):
    """Code-span regexes for the identifiers in an entry's key cell (`small_*` matches `small_old`)."""
    ids = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9_*]*", key) if "_" in w or w.islower()]
    return [re.compile("`" + re.escape(w).replace(r"\*", "[a-z0-9_]*") + "`") for w in ids if len(w) > 2]


def prose_of(line, quoted):
    """Blank out what is not prose: code spans, link targets, URLs, and (unless asked) quotes."""
    line = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line)
    line = re.sub(r"\]\([^)]*\)", lambda m: "]" + " " * (len(m.group(0)) - 1), line)
    line = re.sub(r"https?://\S+", lambda m: " " * len(m.group(0)), line)
    if not quoted:
        line = re.sub(r"[\"“][^\"“”]{1,80}[\"”]", lambda m: " " * len(m.group(0)), line)
    return line


def compile_entries(entries):
    out = []
    for e in entries:
        words = re.escape(norm(e["word"])).replace(r"\ ", r"[\s_-]+")
        rx = re.compile(r"(?<![\w/])" + words + r"(?:s|es)?(?![\w/])", re.I)
        out.append((rx, e, key_patterns(e["key"])))
    return out


def scan_lines(numbered, compiled, include_amb, quoted, names=()):
    """numbered: iterable of (lineno, text). Yields (lineno, matched text, entry, text)."""
    fence = False
    for no, text in numbered:
        if text.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        prose = prose_of(text, quoted)
        spans = [m.span() for nx in names for m in nx.finditer(prose)]
        for rx, e, keys in compiled:
            if e["ambiguous"] and not include_amb:
                continue
            for m in rx.finditer(prose):
                if m.group(0)[0].isupper() and not re.search(r"(^|[.!?:|]\s|\|\s|^[-*>\s]*(\*\*)?)$", prose[:m.start()]):
                    continue  # a capital mid-sentence is a proper name or a quoted label
                s, t = m.span()
                if any(a <= s and t <= b and b - a > t - s for a, b in spans):
                    continue  # part of a longer key or label ("sheet metal")
                near = text[max(0, s - 60): t + 60]
                if any(k.search(near) for k in keys):
                    continue  # its key is written beside it
                yield no, m.group(0), e, text


def added_lines(root, rev, paths):
    """(path, lineno, text) for lines added since REV in the working tree."""
    out = subprocess.run(["git", "-C", str(root), "diff", "-U0", rev, "--", *paths],
                         capture_output=True, text=True, check=True).stdout
    path, no = None, 0
    for ln in out.splitlines():
        if ln.startswith("+++ "):
            path = ln[6:] if ln.startswith("+++ b/") else None
        elif ln.startswith("@@"):
            m = re.search(r"\+(\d+)", ln)
            no = int(m.group(1)) if m else 0
        elif ln.startswith("+") and not ln.startswith("+++") and path:
            yield path, no, ln[1:]
            no += 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("args", nargs="*", help="optional REPO_ROOT (a directory) then PATHs")
    ap.add_argument("--since", metavar="REV")
    ap.add_argument("--stdin", action="store_true")
    ap.add_argument("--summary", action="store_true", help="only the count per word")
    ap.add_argument("--ambiguous", action="store_true", help="also report the ambiguous words")
    ap.add_argument("--include-quoted", action="store_true")
    ap.add_argument("--word", action="append", metavar="W", help="check only this word (repeatable)")
    a = ap.parse_args()

    root = Path(".")
    rest = list(a.args)
    if rest and (Path(rest[0]) / GLOSSARY).is_file():
        root = Path(rest.pop(0))
    try:
        gtext = (root / GLOSSARY).read_text(encoding="utf-8")
    except OSError as e:
        sys.exit(f"cannot read {GLOSSARY}: {e.strerror}")
    entries = parse_glossary(gtext)
    if a.word:
        want = {norm(w) for w in a.word}
        entries = [e for e in entries if norm(e["word"]) in want]
    compiled = compile_entries(entries)
    names = known_names(gtext)

    hits = []  # (where, lineno, matched, entry, text)
    if a.stdin:
        numbered = enumerate(sys.stdin.read().splitlines(), 1)
        hits = [("stdin", no, m, e, t) for no, m, e, t in scan_lines(numbered, compiled, a.ambiguous, a.include_quoted, names)]
    else:
        paths = rest or ["docs", "tools"]
        if a.since:
            by_file = {}
            for p, no, t in added_lines(root, a.since, paths):
                if p.endswith(".md") and p != GLOSSARY:
                    by_file.setdefault(p, []).append((no, t))
            for p, nl in by_file.items():
                hits += [(p, no, m, e, t) for no, m, e, t in scan_lines(nl, compiled, a.ambiguous, a.include_quoted, names)]
        else:
            files = []
            for p in paths:
                pp = root / p
                files += sorted(pp.glob("*.md")) if pp.is_dir() else [pp]
            for f in files:
                rel = str(f.relative_to(root)) if f.is_absolute() or root != Path(".") else str(f)
                rel = rel.removeprefix("./")
                if rel == GLOSSARY:
                    continue
                text = f.read_text(encoding="utf-8").splitlines()
                hits += [(rel, no, m, e, t) for no, m, e, t in scan_lines(enumerate(text, 1), compiled, a.ambiguous, a.include_quoted, names)]

    if not a.summary:
        for where, no, m, e, t in hits:
            if e["kind"] == "ambiguous":
                advice = f"ambiguous, check context ({e['key']})"
            elif e["kind"] == "label":
                advice = f"label, key is {e['key']}"
            else:
                advice = f"write {e['key']}"
            ctx = t.strip()
            i = ctx.lower().find(m.lower())
            ctx = ("..." if i > 40 else "") + ctx[max(0, i - 40): i + len(m) + 40] + ("..." if len(ctx) > i + len(m) + 40 else "")
            print(f"{where}:{no}: '{m}' -> {advice} | {ctx}")
    count = Counter((e["word"], e["key"], e["kind"]) for _, _, _, e, _ in hits)
    print(f"\n{len(hits)} lead(s), {len(count)} word(s)")
    for (word, key, kind), n in count.most_common():
        print(f"  {n:4d}  {word} ({kind}) -> {key}")


if __name__ == "__main__":
    main()
