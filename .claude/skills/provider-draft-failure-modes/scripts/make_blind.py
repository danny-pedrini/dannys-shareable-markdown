"""Build ticket-drafts-blind.md for the Step 3 blind scorers.

Keeps each ticket's working number, title, Counts line and filed body. Drops the working-ref
lines (source failure mode, dedup status, issue type, labels, recommended priority, rationale,
clinical-confirmation flag) and any planner note that names a priority, so a blind scorer sees
only what a reader outside this session would see, plus the counts the rubric's band needs.

Reads every `ticket-drafts-<code>.md` in the round folder for a batch code in round.json
(per-batch files, in batch order). A batch with no file is skipped and counted in the summary
line: most batches never get a ticket, so a missing file is normal, never an error (v2.4). A
stub file (a header line and no `### T-` record) is also fine. Exits 1 only when no ticket was
found in any file.
Run from the round folder:  python3 -I <skill>/scripts/make_blind.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.getcwd()
sys.path.insert(0, HERE)
import round_config as RC  # noqa: E402

cfg = RC.load(os.path.join(ROOT, "round.json"))
FILES = [f"ticket-drafts-{b}.md" for b in RC.batch_codes(cfg)]
DROP = re.compile(r'^- (Source failure mode|Dedup status|Issue type|Labels|Recommended priority|Rationale|Needs clinical confirmation|Priority note|Planned)\b', re.I)
out = ["# Ticket drafts for blind scoring",
       "",
       "Score each ticket with `priority-rubric.md`: the severity class of its worst credible instance, "
       "then the band its Counts line gives. Recommended priorities have been removed.",
       ""]
n = 0
read_files, skipped = 0, 0
for f in FILES:
    if not os.path.exists(f):
        skipped += 1
        continue
    read_files += 1
    in_ticket = False
    for line in open(f).read().split("\n"):
        if line.startswith("### T-"):
            in_ticket = True
            n += 1
            out += ["", line]
            continue
        if not in_ticket or DROP.match(line):
            continue
        out.append(line)
open("ticket-drafts-blind.md", "w").write("\n".join(out) + "\n")
leaks = [l for l in out if re.search(r'Recommended priority|Rationale:|P0 - |P1 - |P2 - |\bP[012]\b', l)]
print(f"tickets: {n}; draft files read: {read_files}; batches with no draft file: {skipped}; "
      f"possible priority leaks: {len(leaks)}")
for l in leaks[:10]:
    print("  ", l[:120])
if n == 0:
    print("make_blind.py: no ticket found in any ticket-drafts-<code>.md; nothing to score", file=sys.stderr)
    sys.exit(1)
