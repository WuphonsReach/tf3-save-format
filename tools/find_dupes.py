"""Find facts that more than one note in docs/ mentions, or every mention of one term.

Usage: find_dupes.py [REPO_ROOT] [--note NOTE] [--top N] [--max-notes N] [--exclude NOTE ...]
                         [--kind code|number]
       find_dupes.py [REPO_ROOT] --where TERM

Read only, no saves. A fact has one home note and the others link to it, so a term that turns up
in several notes is where drift starts. The terms compared are the inline code spans (field names,
keys, resource paths; a plain lowercase word such as `true` or `name` is skipped) and the numbers
of four or more digits (entity ids, clock values, counts; bare years are skipped, commas are
ignored so `60,000` equals `60000`). Code fences and link targets are not scanned.

The default report has two parts: the terms found in 2 to --max-notes notes (default 6; a term in
more is a glossary word like `u32`), most notes first, and the pairs of notes that share the most
terms. `--note docs/NOTE.md` keeps only what involves that note: run it after changing a note to
see which others to check. `--where TERM` lists every line mentioning TERM (case-insensitive,
commas ignored in numbers) with its note, line number and nearest heading, so a reader opens
those sections and not whole notes. docs/versions.md (dated counts) is left out of the default
report; `--exclude` adds more. `--kind code` or `--kind number` compares only one kind (code
spans are the less noisy; numbers include entity ids that two tests happened to show).

How to read it:
  - A shared term is a lead, not a defect. A link, a pointer sentence or a one-line reminder
    shares terms with the home note and is how the notes are meant to refer to each other. Open
    the lines (`--where`) and check whether the fact itself, not just its name, is stated twice.
  - A split raises the count. Moving a section to a new note leaves pointers and the terms they
    name in both places, so do not push the count down as if it were a score.
  - The pair list shows where two notes lean on each other; it is a hint for merging or moving a
    section, never proof.
  - It compares identifiers, not wording. A claim that went stale in prose ("names are not in the
    save" after the cargo list was found) is only found by grepping the phrase.
Exit status is always 0.
"""
import argparse
import os
import re
import sys
from collections import defaultdict
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_links import _INLINE_CODE, md_files  # noqa: E402
from facts_index import read_note  # noqa: E402

_CODE_SPAN = re.compile(r"`([^`\n]+)`")
_NUMBER = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d{4,})(?![\w]|\.\d)")
_LINK_TARGET = re.compile(r"\]\([^)]*\)")
_PLAIN_WORD = re.compile(r"\.?[a-z]+")  # `true`, `level`, `name`: too common to say anything


def terms_of(text):
    """Return the comparable terms of one line, as (kind, term)."""
    text = _LINK_TARGET.sub("]", text)
    found = []
    for span in _CODE_SPAN.findall(text):
        span = " ".join(span.split())
        if 2 <= len(span) <= 60 and not _PLAIN_WORD.fullmatch(span):
            found.append(("code", span))
    bare = _INLINE_CODE.sub("", text)
    for num in _NUMBER.findall(bare):
        plain = num.replace(",", "")
        if "," not in num and 1800 <= int(plain) <= 2199:
            continue
        found.append(("number", plain))
    return found


def heading_at(sections, line):
    title = ""
    for _, t, start in sections:
        if start > line:
            break
        title = t
    return title


def where(root, term):
    needle = term.lower()
    plain = needle.replace(",", "")
    hits = 0
    for f in md_files(root):
        if not f.startswith("docs/"):
            continue
        lines, sections, _ = read_note(os.path.join(root, f))
        for n, text, in_fence in lines:
            low = text.lower()
            if in_fence or (needle not in low and plain not in low.replace(",", "")):
                continue
            hits += 1
            excerpt = " ".join(text.split())
            if len(excerpt) > 110:
                at = max(0, low.find(needle) - 40) if needle in low else 0
                excerpt = ("..." if at else "") + excerpt[at:at + 110] + "..."
            print(f"{f}:{n} [{heading_at(sections, n)}] {excerpt}")
    print(f"{hits} line(s)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root", nargs="?", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    ap.add_argument("--note")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--max-notes", type=int, default=6)
    ap.add_argument("--exclude", nargs="*", default=["docs/versions.md"])
    ap.add_argument("--kind", choices=["code", "number"], help="compare only code spans or only numbers")
    ap.add_argument("--where")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.where:
        where(root, args.where)
        return 0

    seen = defaultdict(lambda: defaultdict(list))  # (kind, term) -> note -> [line numbers]
    for f in md_files(root):
        if not f.startswith("docs/") or f == "docs/README.md" or f in args.exclude:
            continue
        lines, _, _ = read_note(os.path.join(root, f))
        for n, text, in_fence in lines:
            if not in_fence:
                for key in terms_of(text):
                    if args.kind and key[0] != args.kind:
                        continue
                    seen[key][f].append(n)

    shared = {k: v for k, v in seen.items() if 2 <= len(v) <= args.max_notes}
    if args.note:
        shared = {k: v for k, v in shared.items() if args.note in v}
    ranked = sorted(shared.items(), key=lambda kv: (-len(kv[1]), -sum(map(len, kv[1].values())), kv[0][1]))

    print(f"{len(shared)} term(s) in 2 to {args.max_notes} notes; first {min(args.top, len(ranked))}:")
    for (kind, term), per_note in ranked[:args.top]:
        where_ = ", ".join(f"{os.path.basename(f)[:-3]}:{ns[0]}" + (f"x{len(ns)}" if len(ns) > 1 else "")
                           for f, ns in sorted(per_note.items()))
        print(f"  {term!r:40} {where_}")

    pairs = defaultdict(int)
    for per_note in shared.values():
        for a, b in combinations(sorted(per_note), 2):
            pairs[(a, b)] += 1
    if args.note:
        pairs = {k: v for k, v in pairs.items() if args.note in k}
    print("\nnote pairs sharing the most terms:")
    for (a, b), count in sorted(pairs.items(), key=lambda kv: -kv[1])[:12]:
        print(f"  {count:4d}  {a}  {b}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
