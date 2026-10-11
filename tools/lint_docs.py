"""Check one change to docs/ before it is committed: errors that block it, leads to read.

Usage: lint_docs.py [REPO_ROOT] [--since REV] [--max-words N] [--max-section-words N] [--top N]

Read only, no saves. Compares the working tree with git revision REV (default HEAD, so the
uncommitted change; pass an older commit to check a series of commits) and reports on what
changed, not on the whole of docs/. It runs the other scripts' checks and prints one line each.

Errors (exit status 1):
  - anything check_links.py reports (dead links and anchors, notes or scripts missing from an
    index), over the whole repo
  - a note that crossed --max-words (default 3500) in this change, or a new note over it
  - a section whose own text crossed --max-section-words (default 1500), or a new one over it (a
    section moved whole from another note keeps its old size and is only a warning if it grew)
  - a sentence that links to a note and names a code term that note lost in this change: the
    fact moved and the link did not (find_dupes.py --since)

Warnings (shown, exit status still 0; open the named lines, then decide):
  - a note or section already over its limit that grew
  - a changed line sharing six or more runs of eight words with a line in another note: the same
    paragraph in two places (find_dupes.py --prose, which lists from four)
  - a code term now in more notes than at REV, a split's new note counted with the note it came
    from (find_dupes.py --since)
  - a changed note sharing two or more code terms with a note it does not link to and that does
    not link to it

The warnings are leads, not defects; see "How to read it" in find_dupes.py. `--where TERM` of
find_dupes.py lists a term's lines. The last line is the count of each.
"""
import argparse
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_links import find_problems  # noqa: E402
from facts_index import read_note, section_words, words  # noqa: E402
from find_dupes import collect, compare, doc_notes, prose_pairs, snapshot, unlinked_pairs  # noqa: E402

_HUNK = re.compile(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@")


def changed_lines(root, rev):
    """Return {note: set of line numbers added or changed since rev}, untracked notes whole."""
    out = {}
    diff = subprocess.run(["git", "-C", root, "diff", "-U0", "--no-color", "--no-ext-diff", rev, "--", "docs"],
                          capture_output=True, text=True, check=True).stdout
    note = None
    for line in diff.split("\n"):
        if line.startswith("+++ "):
            note = line[6:] if line.startswith("+++ b/") and line.endswith(".md") else None
        elif note and (m := _HUNK.match(line)):
            start, count = int(m.group(1)), int(m.group(2) or 1)
            out.setdefault(note, set()).update(range(start, start + count))
    untracked = subprocess.run(["git", "-C", root, "ls-files", "--others", "--exclude-standard", "docs"],
                               capture_output=True, text=True, check=True).stdout.split()
    for note in untracked:
        if note.endswith(".md"):
            with open(os.path.join(root, note), encoding="utf-8") as f:
                out[note] = set(range(1, sum(1 for _ in f) + 1))
    return {k: v for k, v in out.items() if k != "docs/README.md" and v}


def sizes(root, note):
    """Return (words, {section title: (first line, words)}) of a note, or None if it is missing."""
    path = os.path.join(root, note)
    if not os.path.exists(path):
        return None
    lines, sections, _ = read_note(path)
    return words(lines), {t: (s, w) for _, t, s, w in section_words(lines, sections)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root", nargs="?", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    ap.add_argument("--since", default="HEAD", metavar="REV")
    ap.add_argument("--max-words", type=int, default=3500)
    ap.add_argument("--max-section-words", type=int, default=1500)
    ap.add_argument("--top", type=int, default=15, help="warnings shown per kind")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    errors, warnings = [], []

    _, problems = find_problems(root)
    errors += problems
    changed = changed_lines(root, args.since)

    with snapshot(root, args.since) as old:
        moved = {}  # section title -> words anywhere at REV, so a section moved whole is not new
        for note in doc_notes(old, ()):
            for title, (_, w) in sizes(old, note)[1].items():
                moved[title] = max(w, moved.get(title, 0))
        for note in sorted(changed):
            now, then = sizes(root, note), sizes(old, note)
            if now is None:
                continue
            was = then[0] if then else 0
            if now[0] > args.max_words and now[0] > was:
                (warnings if was > args.max_words else errors).append(
                    f"{note}: {now[0]} words ({f'was {was}' if was else 'new'}), limit {args.max_words}: split it")
            old_sections = then[1] if then else {}
            for title, (start, w) in now[1].items():
                prev = old_sections[title][1] if title in old_sections else moved.get(title, 0)
                if w > args.max_section_words and w > prev:
                    (warnings if prev > args.max_section_words else errors).append(
                        f"{note}:{start}: section \"{title}\" {w} words ({f'was {prev}' if prev else 'new'}), "
                        f"limit {args.max_section_words}")
        r = compare(old, root)

    for f, n, target, names in r["stale"]:
        errors.append(f"{f}:{n}: links {target} for {', '.join(names)}, no longer in that note")

    only = {(f, n) for f, lines in changed.items() for n in lines}
    shown = 0
    for c, a, b, run in prose_pairs(root, min_runs=6, only=only):
        warnings.append(f"{a[0]}:{a[1]} and {b[0]}:{b[1]}: {c} runs of wording in common (\"{run}\")")
        shown += 1
        if shown == args.top:
            break
    for term, was, now in r["spread"][:args.top]:
        warnings.append(f"`{term}` now in {len(now)} notes (was {len(was)}): {', '.join(now)}")
    shared = {k: v for k, v in collect(root, kind="code").items() if 2 <= len(v) <= 6}
    unlinked = [(a, b, t) for (a, b), t in unlinked_pairs(root, shared).items() if (a in changed or b in changed) and len(t) > 1]
    for a, b, terms in sorted(unlinked, key=lambda x: (-len(x[2]), x[0], x[1]))[:args.top]:
        warnings.append(f"{a} and {b} share {', '.join(terms[:3])} and do not link each other")

    for kind, items in (("error", errors), ("warning", warnings)):
        for item in items:
            print(f"{kind}: {item}")
    for f, p in sorted(r["parents"].items()):
        print(f"note: new note {f} counted with {p}")
    print(f"{len(changed)} changed note(s) since {args.since}: {len(errors)} error(s), {len(warnings)} warning(s); "
          f"shared code terms {r['before']} -> {r['after']}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
