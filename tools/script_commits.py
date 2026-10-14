#!/usr/bin/env python3
"""Which git commit last changed a script, or any module it imports from this folder.

Used by mine_summary.py and mine_saves.py to tell a change that needs the summaries rebuilt (mine_summary.py,
save_header.py, tf3save.py) from one that needs the maps redrawn (terrain_map.py and what it imports), by asking
for the commit of one script's import closure. `tools_commit()` is the whole folder's.

Usage: script_commits.py [SCRIPT]       (prints the closure's files and its commit; no argument: the folder's commit)

Standard library only. A commit is "-dirty" if a file in the set has uncommitted changes, and None outside a git
checkout. The imports are found by parsing the script (an `import` or `from ... import` anywhere in it, a
lazy one inside a function included) and keeping the names that are a .py file here.
"""
import ast
import os
import subprocess
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))


def _commit(files):
    """Short hash of the last commit that changed any of files (names in TOOLS_DIR), "-dirty" if one has changes."""
    try:
        git = ["git", "-C", TOOLS_DIR]
        h = subprocess.run(git + ["log", "-1", "--format=%h", "--"] + files, capture_output=True, text=True, check=True)
        st = subprocess.run(git + ["status", "--porcelain", "--"] + files, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return (h.stdout.strip() or None) and h.stdout.strip() + ("-dirty" if st.stdout.strip() else "")


def tools_commit():
    """Short hash of the last commit that changed a tools/*.py, "-dirty" if one has changes, or None."""
    return _commit(["*.py"])


def closure(entry):
    """The script and every module of this folder it imports, directly or through another, as sorted file names."""
    seen, todo = set(), [entry]
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        tree = ast.parse(open(os.path.join(TOOLS_DIR, name), encoding="utf-8").read())
        for node in ast.walk(tree):
            mods = ([a.name for a in node.names] if isinstance(node, ast.Import)
                    else [node.module] if isinstance(node, ast.ImportFrom) and node.module and not node.level
                    else [])
            for m in mods:
                f = m.split(".")[0] + ".py"
                if os.path.isfile(os.path.join(TOOLS_DIR, f)):
                    todo.append(f)
    return sorted(seen)


def closure_commit(entry):
    """tools_commit() for just the script `entry` (a file name in this folder) and what it imports."""
    return _commit(closure(entry))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(" ".join(closure(sys.argv[1])))
        print(closure_commit(sys.argv[1]))
    else:
        print(tools_commit())
