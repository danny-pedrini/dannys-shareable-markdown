"""Insert a '## Draft and thread' section after '## Evidence' in every ticket in ticket-drafts.md.

Blocks come from thread-blocks/<code>.md (names anonymized). Each ticket gets the blocks for the
traces cited in its Evidence bullets, excluding "Also:" lines. Writes ticket-drafts.md in place
and prints body lengths against Jira's 32,000-character description limit. Batch codes come from
round.json. Skip this script when round.json `scope.draft_and_thread` is false.
Run from the round folder:  python3 -I <skill>/scripts/add_threads.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.getcwd()
sys.path.insert(0, HERE)
import round_config as RC  # noqa: E402

cfg = RC.load(os.path.join(ROOT, "round.json"))
if not RC.draft_and_thread_in_scope(cfg):
    print("add_threads.py: scope.draft_and_thread is false; nothing to do")
    sys.exit(0)

blocks = {}
for b in RC.batch_codes(cfg) + ["EARLIER"]:  # EARLIER holds the blocks for "- Earlier round:" bullets (v2.4)
    path = os.path.join("thread-blocks", f"{b}.md")
    if not os.path.exists(path):
        continue
    txt = open(path).read()
    for part in re.split(r"\n(?=### `tr-)", txt):
        m = re.match(r"### `(tr-[0-9a-fA-F]{10})`", part)
        if m:
            blocks[m.group(1)] = part.strip()

s = open("ticket-drafts.md").read()
if "## 4. Full ticket drafts" not in s:
    print("add_threads.py: 'ticket-drafts.md' has no '## 4. Full ticket drafts' section")
    sys.exit(1)
head, tail = s.split("## 4. Full ticket drafts", 1)
parts = re.split(r"\n(?=### T-\d+\. )", tail)
out, report, missing = [], [], []
for p in parts:
    m = re.match(r"\s*### (T-\d+)\. ", p)
    if not m or "## Draft and thread" in p:
        out.append(p)
        continue
    if "## Evidence" not in p:
        out.append(p)
        continue
    ev = p.split("## Evidence", 1)[1].split("\n## ", 1)[0]
    trs = []
    for line in ev.split("\n"):
        if line.startswith("- ") and not line.lower().startswith("- also"):
            for t in re.findall(r"tr-[0-9a-fA-F]{10}", line):
                if t not in trs:
                    trs.append(t)
    if not trs:
        # A ticket backed only by feedback-session evidence cites no trace, so it has no draft or
        # thread to show. Leave it without the section.
        report.append((m.group(1), 0, len(p[p.index("## Problem"):].rstrip().rstrip("-").rstrip()) if "## Problem" in p else len(p)))
        out.append(p)
        continue
    sec = ["## Draft and thread",
           "The messages shown to the model before each draft, then the full draft. Names are replaced with placeholders."]
    for t in trs:
        if t not in blocks:
            missing.append((m.group(1), t))
            continue
        sec += ["", blocks[t].replace("### `", "#### `", 1)]
    if "\n## Expected behavior" in p:
        idx = p.index("\n## Expected behavior")
        p = p[:idx] + "\n\n" + "\n".join(sec) + "\n" + p[idx:]
    else:
        p = p.rstrip() + "\n\n" + "\n".join(sec) + "\n"
    body = p[p.index("## Problem"):].rstrip().rstrip("-").rstrip() if "## Problem" in p else p
    report.append((m.group(1), len(trs), len(body)))
    out.append(p)
open("ticket-drafts.md", "w").write(head + "## 4. Full ticket drafts" + "\n".join(out))
if missing:
    print("MISSING THREAD BLOCKS:", missing)
for t, n, L in report:
    print(t, n, L, "OVER" if L > 32000 else "")
if missing:
    sys.exit(1)
