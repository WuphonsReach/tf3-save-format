"""Find facts that more than one note in docs/ mentions, or every mention of one term.

Usage: find_dupes.py [REPO_ROOT] [--note NOTE] [--top N] [--max-notes N] [--exclude NOTE ...]
                         [--kind code|number] [--keep-saves]
       find_dupes.py [REPO_ROOT] --where TERM
       find_dupes.py [REPO_ROOT] --prose [--note NOTE] [--top N]
       find_dupes.py [REPO_ROOT] --since REV [--top N]

Read only, no saves. A fact has one home note and the others link to it, so a term that turns up
in several notes is where drift starts. The terms compared are the inline code spans (field names,
keys, resource paths; a plain lowercase word such as `true` or `name` is skipped) and the numbers
of four or more digits (entity ids, clock values, counts; bare years are skipped, commas are
ignored so `60,000` equals `60000`). Code fences and link targets are not scanned. A code span
that is a test save's name (`1438`, `1220-more-lines`) is left out unless --keep-saves: notes cite
the same saves for different facts.

The default report has three parts: the terms found in 2 to --max-notes notes (default 6; a term
in more is a glossary word like `u32`), most notes first; the pairs of notes that share the most
terms; and the pairs that share terms but do not link to each other. `--note docs/NOTE.md` keeps
only what involves that note: run it after changing a note to see which others to check.
`--where TERM` lists every line mentioning TERM (case-insensitive, commas ignored in numbers) with
its note, line number and nearest heading, so a reader opens those sections and not whole notes.
docs/versions.md (dated counts) is left out of the default report; `--exclude` adds more.
`--kind code` or `--kind number` compares only one kind (code spans are the less noisy; numbers
include entity ids that two tests happened to show).

`--prose` compares wording instead: pairs of lines in different notes that share at least four
runs of eight words (link targets and table rows ignored), most runs first. It finds a paragraph
stated twice, which the term report cannot tell from a pointer.

`--since REV` compares docs/ now (the working tree) with docs/ at git revision REV. A note that
did not exist at REV is counted with the note it took the most terms from (its parent), so a
split's own pointers do not count as spread. It prints the shared code terms before and after,
the terms now in more notes than before, and the links that may be stale: a sentence that links
to a note and names a code term that note has lost since REV (the fact moved, the link did not).

How to read it:
  - A shared term is a lead, not a defect. A link, a pointer sentence or a one-line reminder
    shares terms with the home note and is how the notes are meant to refer to each other. Open
    the lines (`--where`) and check whether the fact itself, not just its name, is stated twice.
  - A split raises the count. Moving a section to a new note leaves pointers and the terms they
    name in both places, so do not push the count down as if it were a score.
  - The pair list shows where two notes lean on each other; it is a hint for merging or moving a
    section, never proof. An unlinked pair is a stronger hint: two notes on the same thing that
    do not know about each other.
  - It compares identifiers, not wording, except with --prose. A claim that went stale in prose
    ("names are not in the save" after the cargo list was found) is only found by grepping the
    phrase.
Exit status is always 0. tools/lint_docs.py runs these checks on one change and fails on errors.
"""
import argparse
import io
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from collections import defaultdict
from contextlib import contextmanager
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_links import _EXTERNAL, _INLINE_CODE, _LINK, md_files  # noqa: E402
from facts_index import link_graph, read_note  # noqa: E402

_CODE_SPAN = re.compile(r"`([^`\n]+)`")
_NUMBER = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d{4,})(?![\w]|\.\d)")
_LINK_TARGET = re.compile(r"\]\([^)]*\)")
_PLAIN_WORD = re.compile(r"\.?[a-z]+")  # `true`, `level`, `name`: too common to say anything
_SAVE_NAME = re.compile(r"\d{4}(?:-[\w-]+)?")  # `1438`, `1220-more-lines`: a test save's name
_SENTENCE = re.compile(r"(?<=[.;])\s+")
_WORD = re.compile(r"[a-z0-9]+")
RUN = 8  # words in one run for --prose
DEFAULT_EXCLUDE = ("docs/versions.md",)


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


def is_save_name(term):
    return bool(_SAVE_NAME.fullmatch(term))


def heading_at(sections, line):
    title = ""
    for _, t, start in sections:
        if start > line:
            break
        title = t
    return title


def doc_notes(root, exclude=DEFAULT_EXCLUDE):
    return [f for f in md_files(root)
            if f.startswith("docs/") and f != "docs/README.md" and f not in exclude]


def collect(root, kind=None, exclude=DEFAULT_EXCLUDE, keep_saves=False):
    """Return {(kind, term): {note: [line numbers]}} over the notes in docs/."""
    seen = defaultdict(lambda: defaultdict(list))
    for f in doc_notes(root, exclude):
        lines, _, _ = read_note(os.path.join(root, f))
        for n, text, in_fence in lines:
            if in_fence:
                continue
            for key in terms_of(text):
                if kind and key[0] != kind:
                    continue
                if not keep_saves and key[0] == "code" and is_save_name(key[1]):
                    continue
                seen[key][f].append(n)
    return seen


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


def prose_pairs(root, exclude=DEFAULT_EXCLUDE, min_runs=4, only=None):
    """Return line pairs in different notes sharing at least min_runs runs of RUN words.

    Each item is (runs, (note, line), (note, line), one shared run), most runs first. `only`, a
    set of (note, line), keeps the pairs with at least one of those lines.
    """
    runs = defaultdict(set)
    for f in doc_notes(root, exclude):
        lines, _, _ = read_note(os.path.join(root, f))
        for n, text, in_fence in lines:
            if in_fence or text.lstrip().startswith("|"):
                continue
            words = _WORD.findall(_LINK_TARGET.sub("]", text).lower())
            for i in range(len(words) - RUN + 1):
                runs[" ".join(words[i:i + RUN])].add((f, n))
    count, sample = defaultdict(int), {}
    for run, places in runs.items():
        if len(places) > 6:  # boilerplate such as a licence line
            continue
        for a, b in combinations(sorted(places), 2):
            if a[0] != b[0] and (only is None or a in only or b in only):
                count[(a, b)] += 1
                sample.setdefault((a, b), run)
    return sorted(((c, a, b, sample[(a, b)]) for (a, b), c in count.items() if c >= min_runs),
                  key=lambda x: (-x[0], x[1], x[2]))


def unlinked_pairs(root, shared):
    """Return {(note, note): [terms]} for the pairs sharing terms with no link either way."""
    graph = link_graph(root, md_files(root))
    out = defaultdict(list)
    for (_, term), per_note in shared.items():
        for a, b in combinations(sorted(per_note), 2):
            if b not in graph.get(a, ()) and a not in graph.get(b, ()):
                out[(a, b)].append(term)
    return out


@contextmanager
def snapshot(root, rev):
    """Yield a temporary folder holding docs/ as it was at git revision rev."""
    data = subprocess.run(["git", "-C", root, "archive", rev, "docs"],
                          capture_output=True, check=True).stdout
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(fileobj=io.BytesIO(data)) as tar:
            try:
                tar.extractall(tmp, filter="data")
            except TypeError:  # Python before 3.12
                tar.extractall(tmp)
        yield tmp


def note_terms(seen):
    """Return {note: set of code terms} from a collect() result."""
    out = defaultdict(set)
    for (_, term), per_note in seen.items():
        for f in per_note:
            out[f].add(term)
    return out


def compare(old_root, new_root, max_notes=6):
    """Compare the code terms of docs/ at old_root and new_root.

    Returns a dict: `left` {note: terms it lost}, `parents` {new note: note it took most terms
    from}, `before` and `after` (shared code terms, new notes counted with their parents),
    `spread` [(term, old notes, new notes)] for terms in more notes than before, and `stale`
    [(note, line, link target, terms)] from stale_links().
    """
    old = collect(old_root, kind="code")
    new = collect(new_root, kind="code")
    old_t, new_t = note_terms(old), note_terms(new)
    left = {f: old_t[f] - new_t[f] for f in old_t if f in new_t and old_t[f] - new_t[f]}
    parents = {}
    for f in new_t:
        if f not in old_t and any(new_t[f] & t for t in left.values()):
            parents[f] = max(old_t, key=lambda g: (len(new_t[f] & old_t[g]), g))
    lost_by = defaultdict(set)
    for g, terms in left.items():
        for t in terms:
            lost_by[t].add(g)

    def fold(f, term):  # a moved term counts where it was; anything else with the main parent
        if f not in parents:
            return f
        return min(lost_by[term]) if lost_by[term] else parents[f]

    folded = {k: {fold(f, k[1]) for f in v} for k, v in new.items()}
    old_n = {k: set(v) for k, v in old.items()}
    spread = sorted(((k[1], sorted(old_n.get(k, ())), sorted(v)) for k, v in folded.items()
                     if 2 <= len(v) <= max_notes and len(v) > len(old_n.get(k, ()))),
                    key=lambda x: (-len(x[2]), x[0]))
    glossary = {k[1] for k, v in new.items() if len(v) > max_notes}
    return {
        "left": left, "parents": parents,
        "before": sum(1 for v in old_n.values() if 2 <= len(v) <= max_notes),
        "after": sum(1 for v in folded.values() if 2 <= len(v) <= max_notes),
        "spread": spread,
        "stale": stale_links(new_root, {f: t - glossary for f, t in left.items()}),
    }


def stale_links(root, left):
    """Return (note, line, target, terms) for a sentence that links to a note in `left` and names
    one of the terms that note lost."""
    out = []
    for f in md_files(root):
        if not f.startswith("docs/"):
            continue
        lines, _, _ = read_note(os.path.join(root, f))
        for n, text, in_fence in lines:
            if in_fence:
                continue
            for sentence in _SENTENCE.split(text):
                names = {t for k, t in terms_of(sentence) if k == "code"}
                if not names:
                    continue
                for target in _LINK.findall(_INLINE_CODE.sub("", sentence)):
                    ref = target.partition("#")[0]
                    if _EXTERNAL.match(target) or not ref:
                        continue
                    dest = os.path.normpath(os.path.join(os.path.dirname(f), ref))
                    if dest != f and names & left.get(dest, set()):
                        out.append((f, n, target, sorted(names & left[dest])))
    return out


def short(notes):
    return ", ".join(os.path.basename(f)[:-3] for f in notes)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root", nargs="?", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    ap.add_argument("--note")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--max-notes", type=int, default=6)
    ap.add_argument("--exclude", nargs="*", default=list(DEFAULT_EXCLUDE))
    ap.add_argument("--kind", choices=["code", "number"], help="compare only code spans or only numbers")
    ap.add_argument("--keep-saves", action="store_true", help="count test save names as terms")
    ap.add_argument("--where")
    ap.add_argument("--prose", action="store_true", help="compare wording, not terms")
    ap.add_argument("--since", metavar="REV", help="compare with docs/ at a git revision")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.where:
        where(root, args.where)
        return 0

    if args.prose:
        pairs = prose_pairs(root, args.exclude)
        if args.note:
            pairs = [p for p in pairs if args.note in (p[1][0], p[2][0])]
        print(f"{len(pairs)} line pair(s) sharing {4}+ runs of {RUN} words; first {min(args.top, len(pairs))}:")
        for c, a, b, run in pairs[:args.top]:
            print(f"  {c:3d}  {a[0]}:{a[1]}  {b[0]}:{b[1]}  \"{run}\"")
        return 0

    if args.since:
        with snapshot(root, args.since) as old:
            r = compare(old, root, args.max_notes)
        for f, p in sorted(r["parents"].items()):
            print(f"new note {f} counted with {p}")
        print(f"shared code terms: {r['before']} at {args.since}, {r['after']} now (new notes with parents)")
        print(f"\n{len(r['spread'])} term(s) in more notes than before; first {min(args.top, len(r['spread']))}:")
        for term, was, now in r["spread"][:args.top]:
            print(f"  {term!r:40} [{short(was)}] -> [{short(now)}]")
        print(f"\n{len(r['stale'])} link(s) naming a term the target note lost:")
        for f, n, target, names in r["stale"]:
            print(f"  {f}:{n} -> {target}: {', '.join(names)}")
        return 0

    seen = collect(root, args.kind, args.exclude, args.keep_saves)
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

    unlinked = unlinked_pairs(root, shared)
    print("\nnote pairs sharing terms with no link either way:")
    for (a, b), terms in sorted(unlinked.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:12]:
        print(f"  {len(terms):4d}  {a}  {b}  {', '.join(terms[:3])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
