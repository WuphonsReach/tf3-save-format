#!/usr/bin/env python3
"""PreToolUse guard: keep Claude out of Transport Fever 3's native binaries.

Modder-facing files in the install (api/tealdef, base/tealdef, base/mod.json,
vscode-template) stay readable. The executable, the model editor binary and
the bundled shared libraries may not be read, dumped, searched or analysed.
Best effort: a script that walks the install and opens files is not caught.
"""
import json
import re
import sys

INSTALL = re.compile(r"Transport[ _]?Fever[ _]?3|steamapps/common")
# Native binaries shipped in the install, by name.
BINARY = re.compile(
    r"TransportFever3(?![\w ])"      # the game executable (the dir has spaces)
    r"|\bModelEditor\b(?!\.sh)"      # model_editor/ModelEditor
    r"|model_editor/|/extra\b"       # dirs holding only native binaries
    r"|\.so(\.\d+)*\b|\.dll\b|\.exe\b"
)
# Tools whose only use on the install would be inspecting binaries.
TOOLS = re.compile(
    r"(^|[\s;|&(`])(strings|objdump|readelf|nm|gdb|lldb|r2|radare2|rizin|"
    r"ghidra\w*|analyzeHeadless|ida\w*|hexdump|xxd|od|ldd|ltrace|strace|"
    r"bvi|hexedit)(?=\s|$)"
)
GREP = re.compile(r"(^|[\s;|&(`])(e|f)?grep\s([^|;&]*)")
RG_BINARY = re.compile(r"(^|[\s;|&(`])rg\b[^|;&]*\s(-\w*a\b|--text|-uuu|--binary)")

REASON = (
    "Blocked by .claude/hooks/tf3-no-binaries.py: the Transport Fever 3 "
    "executable and bundled native libraries are off limits (no reading, "
    "strings, hex dumps, disassembly or binary greps). Modder-facing files "
    "(api/tealdef, base/tealdef, base/mod.json, vscode-template) are fine; "
    "for grep in the install use -I."
)


def check_bash(cmd):
    if not INSTALL.search(cmd):
        return None
    if BINARY.search(cmd):
        return "names a native binary in the TF3 install"
    if TOOLS.search(cmd):
        return "runs a binary-inspection tool on the TF3 install"
    if RG_BINARY.search(cmd):
        return "asks rg to search binary files in the TF3 install"
    for m in GREP.finditer(cmd):
        args = m.group(3)
        if not re.search(r"(\s|^)-\w*I|--binary-files=without-match", " " + args):
            return "greps the TF3 install without -I (would scan the executable)"
    return None


def check_path(path):
    if path and INSTALL.search(path) and BINARY.search(path):
        return "reads a native binary in the TF3 install"
    return None


def main():
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    inp = data.get("tool_input") or {}
    if tool == "Bash":
        why = check_bash(inp.get("command", ""))
    elif tool in ("Read", "Grep", "Glob"):
        why = check_path(inp.get("file_path") or inp.get("path") or "")
        if not why and tool == "Glob":
            why = check_path(inp.get("pattern", ""))
    else:
        why = None
    if why:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"{REASON} ({why})",
        }}))


if __name__ == "__main__":
    main()
