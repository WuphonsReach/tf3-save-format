"""Outline the notes in docs/: size, sections, links in and out.

Usage: facts_index.py [REPO_ROOT] [--max-words N] [--outline NOTE]

Read only, no saves. The default view is one row per note in docs/ (words, sections, links to it
from other notes, links from it to other notes), biggest first, with a mark on every note over
--max-words (default 3500) as a candidate for splitting. `--outline docs/NOTE.md` prints that
note's headings with line numbers and the words under each, so a reader can open one section
instead of the whole note. Links in code fences and inline code are not counted. Exit status is
always 0; the marks are advice.

Use it before reading notes to find where a fact probably lives and which notes have grown too
big (a note over the limit was the usual reason a whole-corpus consistency pass was needed), and
before a split to see what links to the note. Split a note when it is flagged, not after it has
become unmanageable. A note with no links from other notes (the "no note links to" line) is
reachable only through docs/README.md; that is a hint, not an error.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_links import _EXTERNAL, _FENCE, _HEADING, _INLINE_CODE, _LINK, md_files  # noqa: E402


def read_note(path):
    """Return (lines, sections, links) of one Markdown file.

    lines: list of (line number, text, in_fence). sections: list of (level, title, first line).
    links: list of (line number, target) for links outside code.
    """
    lines, sections, links, in_fence = [], [], [], False
    with open(path, encoding="utf-8") as f:
        for n, text in enumerate(f, 1):
            text = text.rstrip("\n")
            if _FENCE.match(text):
                in_fence = not in_fence
                lines.append((n, text, True))
                continue
            lines.append((n, text, in_fence))
            if in_fence:
                continue
            m = _HEADING.match(text)
            if m:
                sections.append((len(m.group(1)), m.group(2), n))
            links += [(n, t) for t in _LINK.findall(_INLINE_CODE.sub("", text))]
    return lines, sections, links


def doc_notes(root):
    return [f for f in md_files(root) if f.startswith("docs/") and f != "docs/README.md"]


def words(lines):
    return sum(len(t.split()) for _, t, _ in lines)


def link_graph(root, files):
    """Return {note: set of notes it links to} over all given Markdown files."""
    out = {}
    for f in files:
        _, _, links = read_note(os.path.join(root, f))
        dests = set()
        for _, target in links:
            if _EXTERNAL.match(target):
                continue
            ref = target.partition("#")[0]
            if ref:
                dests.add(os.path.normpath(os.path.join(os.path.dirname(f), ref)))
        out[f] = dests
    return out


def outline(root, note):
    lines, sections, _ = read_note(os.path.join(root, note))
    total = words(lines)
    print(f"{note}: {total} words, {len(sections)} headings")
    for i, (level, title, start) in enumerate(sections):
        end = sections[i + 1][2] if i + 1 < len(sections) else len(lines) + 1
        w = words(lines[start:end - 1])
        print(f"{start:5d} {w:5d}w {'  ' * (level - 1)}{title}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root", nargs="?", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    ap.add_argument("--max-words", type=int, default=3500)
    ap.add_argument("--outline", metavar="NOTE")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.outline:
        outline(root, args.outline)
        return 0

    files = md_files(root)
    notes = doc_notes(root)
    graph = link_graph(root, files)
    rows = []
    for f in notes:
        lines, sections, _ = read_note(os.path.join(root, f))
        inbound = sum(1 for g, dests in graph.items() if g not in (f, "docs/README.md") and f in dests)
        outbound = len({d for d in graph[f] if d in notes and d != f})
        rows.append((words(lines), f, len(sections), inbound, outbound))
    rows.sort(reverse=True)

    print(f"{'words':>6} {'heads':>5} {'in':>3} {'out':>3}  note")
    for w, f, heads, inb, outb in rows:
        flag = "  <- over --max-words, consider a split" if w > args.max_words else ""
        print(f"{w:6d} {heads:5d} {inb:3d} {outb:3d}  {f}{flag}")
    total = sum(r[0] for r in rows)
    print(f"{len(rows)} notes, {total} words (about {total * 3 // 2} tokens)")
    orphans = [f for _, f, _, inb, _ in rows if inb == 0]
    if orphans:
        print("no note links to: " + ", ".join(orphans))
    return 0


if __name__ == "__main__":
    sys.exit(main())
