#!/usr/bin/env python3
"""Structural lint for a skill folder, run before the Phase 4 grader.

agent-architect runs this on a built or edited skill before it spawns the QA
grader (SKILL.md Phase 4, Structural Lint). The orchestrator records the output
unchanged. The grader still runs every check; its brief does not mention lint.

Checks:
  L1 frontmatter: SKILL.md starts with YAML frontmatter that has name and description
  L2 labeled sections: every XML-style section tag opens and closes, and the
     file has at least one labeled section (XML tag or ## heading)
  L3 when-not-to-use: every "## Tool: <name>" block has a "When NOT to Use" line
  L4 stop message: every "## Tool: <name>" block has a stop or failure line
  L5 subagent type: every Agent tool spawn in SKILL.md or references/*.md states
     a subagent type within the next 8 lines

Usage:
  python3 lint_skill.py <skill-folder>

Exit codes: 0 all checks pass, 1 any check fails, 2 usage or input error.
"""

import json
import os
import re
import sys

TAG_RE = re.compile(r"^<(/?)([a-z][a-z0-9_]*)>\s*$")
TOOL_RE = re.compile(r"^#{2,4}\s+Tool:\s*(.+)$")
SPAWN_RE = re.compile(r"(Use the Agent tool|use the Agent tool|spawn(s)? (a|an|one) [\w\- ]*subagent)", re.I)
TYPE_RE = re.compile(r"(subagent[_ ]type|agent type|Subagent type)", re.I)
STOP_RE = re.compile(r"(stop|Stopped\.|On Failure|If it fails|Failure Handling)", re.I)
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read().split("\n")


def check_frontmatter(lines):
    if not lines or lines[0].strip() != "---":
        return False, "no frontmatter block at line 1"
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return False, "frontmatter block not closed"
    keys = {l.split(":", 1)[0].strip() for l in lines[1:end] if ":" in l}
    missing = [k for k in ("name", "description") if k not in keys]
    return not missing, f"missing: {missing}" if missing else ""


def check_sections(lines):
    stack, errors, in_fence, headings = [], [], False, 0
    for n, line in enumerate(lines, 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("## "):
            headings += 1
        m = TAG_RE.match(line.strip())
        if not m:
            continue
        closing, tag = m.group(1) == "/", m.group(2)
        if not closing:
            stack.append((tag, n))
        elif stack and stack[-1][0] == tag:
            stack.pop()
        else:
            errors.append(f"line {n}: </{tag}> without matching open tag")
    errors += [f"line {n}: <{tag}> never closed" for tag, n in stack]
    labeled = headings > 0 or any(TAG_RE.match(l.strip()) for l in lines)
    if not labeled:
        errors.append("no labeled sections")
    return not errors, "; ".join(errors)


def tool_blocks(lines):
    blocks, current = [], None
    for n, line in enumerate(lines, 1):
        m = TOOL_RE.match(line)
        if m:
            current = {"tool": m.group(1).strip(), "line": n, "body": []}
            blocks.append(current)
        elif current is not None:
            if re.match(r"^#{1,4}\s", line) or line.strip().startswith("</"):
                current = None
            else:
                current["body"].append(line)
    return blocks


def check_tools(lines):
    blocks = tool_blocks(lines)
    no_when_not = [f"{b['tool']} (line {b['line']})" for b in blocks
                   if not any("When NOT to Use" in l for l in b["body"])]
    no_stop = [f"{b['tool']} (line {b['line']})" for b in blocks
               if not any(STOP_RE.search(l) for l in b["body"])]
    note = f"{len(blocks)} tool block(s)"
    return (not no_when_not, f"missing in: {no_when_not}" if no_when_not else note), \
           (not no_stop, f"missing in: {no_stop}" if no_stop else note)


def check_spawns(files):
    missing, count = [], 0
    for path in files:
        lines = read(path)
        for n, line in enumerate(lines, 1):
            if not SPAWN_RE.search(line):
                continue
            count += 1
            window = lines[n - 1:n + 8]
            if not any(TYPE_RE.search(l) for l in window):
                missing.append(f"{os.path.basename(path)}:{n}")
    return not missing, f"no type stated at: {missing}" if missing else f"{count} spawn(s)"


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "usage: lint_skill.py <skill-folder>"}))
        return 2
    folder = sys.argv[1]
    skill = os.path.join(folder, "SKILL.md")
    if not os.path.isfile(skill):
        print(json.dumps({"error": f"SKILL.md not found in {folder}"}))
        return 2

    lines = read(skill)
    ref_dir = os.path.join(folder, "references")
    refs = sorted(os.path.join(ref_dir, f) for f in os.listdir(ref_dir) if f.endswith(".md")) \
        if os.path.isdir(ref_dir) else []

    results = []

    def add(check_id, name, outcome):
        ok, detail = outcome
        results.append({"id": check_id, "check": name, "result": "PASS" if ok else "FAIL", "detail": detail})

    add("L1", "frontmatter name and description", check_frontmatter(lines))
    add("L2", "labeled sections open and close", check_sections(lines))
    when_not, stop = check_tools(lines)
    add("L3", "When NOT to Use per tool", when_not)
    add("L4", "stop message per tool", stop)
    add("L5", "subagent type per spawn", check_spawns([skill] + refs))

    failed = [r for r in results if r["result"] == "FAIL"]
    print(json.dumps({"skill": folder, "checks": results, "failed": len(failed)}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
