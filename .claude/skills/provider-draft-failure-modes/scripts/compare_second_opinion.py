"""Compare a batch ledger's classifications with its input-issue second opinion.

Writes ledger/qa/<BATCH>-second-opinion-diff.md and prints counts. Every disagreement row ends
with a `Recommendation:` cell (round-folder-layout.md section 4, for E3). Deciding which side is
right needs judgment this script cannot supply deterministically, so the cell is always written
as `Recommendation: TBD`; the adjudicator agent (2b) edits each row to replace TBD with its call
and a one-line reason before 2c clustering or Gate 2 reads the file. Document this in any
per-round format notes that reference this file.
Run from the round folder:  python3 -I <skill>/scripts/compare_second_opinion.py <BATCH>
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mechanical_check import ledger_rows, col  # noqa: E402

if len(sys.argv) != 2:
    print("usage: compare_second_opinion.py <BATCH>", file=sys.stderr)
    sys.exit(1)
b = sys.argv[1]
qa_dir = os.path.join("ledger", "qa")
led = {col(r, "row id"): r for r in (ledger_rows(b) or [])}
so_path = os.path.join(qa_dir, f"{b}-input-second-opinion.md")
targets_path = os.path.join(qa_dir, f"{b}-second-opinion-targets.md")
if not os.path.exists(so_path) or not os.path.exists(targets_path):
    print(f"compare_second_opinion.py: missing {so_path} or {targets_path}", file=sys.stderr)
    sys.exit(1)
so = {}
for l in open(so_path):
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    if len(c) >= 4 and re.fullmatch(rf"{b}-\d{{3}}", c[0]):
        so[c[0]] = c
dis, agree, missing = [], 0, []
tgt = set(re.findall(rf"\| (?:yes|no) \| ({b}-\d{{3}}) \|", open(targets_path).read()))
for rid in sorted(tgt):
    if rid not in so:
        missing.append(rid)
        continue
    a = col(led[rid], "classification").split()[0] if col(led[rid], "classification") else ""
    s = (so[rid][1].strip("`").lower().split() or [""])[0]
    if a == s:
        agree += 1
    else:
        dis.append((rid, a, s, so[rid]))
L = [f"# Second-opinion disagreements, batch {b}", "",
     "Ledger classification (extractor, after 2b adjudication) versus the independent second "
     "opinion. The adjudicator agent fills in each row's Recommendation cell.", "",
     "| Row ID | Trace | Atomic issue (ledger) | Ledger says | Ledger input named | Second opinion says | Second-opinion input named | Second-opinion reason | Confidence | Recommendation |",
     "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for rid, a, s, c in dis:
    r = led[rid]
    L.append(f"| {rid} | {col(r,'trace id')[:13]} | {col(r,'atomic issue')} | {a} | {col(r,'input named')} | {s} | {c[2] if len(c)>2 else ''} | {c[3] if len(c)>3 else ''} | {c[4] if len(c)>4 else ''} | Recommendation: TBD |")
L += ["", f"Counts: {len(tgt)} rows re-classified; {agree} agree; {len(dis)} disagree; {len(missing)} missing from the second opinion{(': ' + ', '.join(missing)) if missing else ''}."]
open(os.path.join(qa_dir, f"{b}-second-opinion-diff.md"), "w").write("\n".join(L) + "\n")
print(f"{b}: {len(tgt)} targets, {agree} agree, {len(dis)} disagree ({', '.join(f'{d[0]} {d[1]}->{d[2]}' for d in dis)}), missing {missing}")
