"""Check the relative links in the repo's Markdown files.

Usage: check_links.py [REPO_ROOT]

Read only. Looks at every tracked `.md` file (falls back to walking the folder outside a git
checkout) and reports:
  - a relative link whose target file or folder does not exist
  - a `#anchor` that matches no heading in the target file (GitHub's slug rules)
  - a note in docs/ that docs/README.md does not link to
  - a script or schema file in tools/ that tools/README.md does not mention

Web links (http, https, mailto) are not fetched. Links inside code fences and inline code are
skipped. Exit status is 1 when anything is reported, 0 otherwise.
"""
import os
import re
import subprocess
import sys

_FENCE = re.compile(r"^\s*(```|~~~)")
_INLINE_CODE = re.compile(r"`[^`]*`")
_LINK = re.compile(r"(?<!!)\[(?:[^\]]|\[[^\]]*\])*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_REF_DEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s+(\S+)")
_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
_EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.I)


def md_files(root):
    try:
        out = subprocess.run(
            ["git", "-C", root, "ls-files", "--cached", "--others",
             "--exclude-standard", "*.md"],
            capture_output=True, text=True, check=True,
        ).stdout.split("\n")
        return sorted(f for f in out if f)
    except (OSError, subprocess.CalledProcessError):
        found = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "local"]
            for name in filenames:
                if name.endswith(".md"):
                    found.append(os.path.relpath(os.path.join(dirpath, name), root))
        return sorted(found)


def slug(heading):
    """GitHub's anchor for a heading: strip markup, lowercase, drop punctuation, spaces to '-'."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = text.replace("`", "").replace("*", "")
    text = re.sub(r"<[^>]+>", "", text).lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def scan(path):
    """Return (link targets with line numbers, heading anchors) of one Markdown file."""
    links, anchors, seen = [], set(), {}
    in_fence = False
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if _FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = _HEADING.match(line)
            if m:
                s = slug(m.group(2))
                k = seen.get(s, 0)
                seen[s] = k + 1
                anchors.add(s if k == 0 else f"{s}-{k}")
            bare = _INLINE_CODE.sub("", line)
            links += [(n, t) for t in _LINK.findall(bare)]
            m = _REF_DEF.match(bare)
            if m:
                links.append((n, m.group(1)))
    return links, anchors


def find_problems(root):
    """Return (Markdown files checked, list of problem lines) for the repo at root."""
    files = md_files(root)
    scanned = {f: scan(os.path.join(root, f)) for f in files}
    problems = []
    linked_from_docs_readme = set()

    for f, (links, _) in list(scanned.items()):
        for n, target in links:
            if _EXTERNAL.match(target):
                continue
            ref, _, frag = target.partition("#")
            dest = os.path.normpath(os.path.join(os.path.dirname(f), ref)) if ref else f
            if f == "docs/README.md":
                linked_from_docs_readme.add(dest)
            full = os.path.join(root, dest)
            if not os.path.exists(full):
                problems.append(f"{f}:{n}: missing target {target}")
            elif frag and dest.endswith(".md"):
                if dest not in scanned:
                    scanned[dest] = scan(full)
                if frag.lower() not in scanned[dest][1]:
                    problems.append(f"{f}:{n}: no heading for #{frag} in {dest}")

    for f in files:
        if f.startswith("docs/") and f != "docs/README.md" and f not in linked_from_docs_readme:
            problems.append(f"{f}: not linked from docs/README.md")

    tools_readme = os.path.join(root, "tools", "README.md")
    if os.path.exists(tools_readme):
        with open(tools_readme, encoding="utf-8") as fh:
            text = fh.read()
        for name in sorted(os.listdir(os.path.join(root, "tools"))):
            if name.endswith(".py") and name not in text:
                problems.append(f"tools/{name}: not mentioned in tools/README.md")
        schema_dir = os.path.join(root, "tools", "schema")
        if os.path.isdir(schema_dir) and "schema/" not in text:
            problems.append("tools/schema/: not mentioned in tools/README.md")
    return files, problems


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else
                           os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    files, problems = find_problems(root)
    for p in problems:
        print(p)
    print(f"{len(files)} Markdown files checked, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
