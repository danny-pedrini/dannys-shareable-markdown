"""Round bookkeeping for prd-generator QA: the artifact checksum, E45 and E46.

    python3 .claude/skills/prd-generator/scripts/qa_round.py start  --run <run> --phase <P|D|R|H0|H1|H2> --round <n> --artifact <path>
    python3 .claude/skills/prd-generator/scripts/qa_round.py verify --run <run> --phase <P|D|R|H0|H1|H2> --round <n> --artifact <path>

start   records the artifact's sha256 in <run>/qa-reports/<phase>-round-<n>-checksum.txt and prints
        the report path each group must write.
verify  E45 Report Coverage: each report lists exactly the eval IDs <eval_phase_map> assigns its group.
        E46 QA Artifact Integrity: one report per launched group, a row per assigned eval, and an
        unchanged artifact checksum across the round.
        Writes <run>/qa-reports/<phase>-round-<n>-round-check.md. Exits 2 when the checksum changed,
        1 on any other Fail, 0 when both pass.
"""
import argparse
import os
import re
import sys

import _common as c


def report_path(run, phase, rnd, slug):
    return os.path.join(run, "qa-reports", "%s-round-%d-%s.md" % (phase, rnd, slug))


def checksum_path(run, phase, rnd):
    return os.path.join(run, "qa-reports", "%s-round-%d-checksum.txt" % (phase, rnd))


def groups(phase):
    return {k: v for k, v in c.assigned(phase).items() if k != "round-check"}


def start(a):
    os.makedirs(os.path.join(a.run, "qa-reports"), exist_ok=True)
    with open(checksum_path(a.run, a.phase, a.round), "w", encoding="utf-8") as f:
        f.write("%s  %s\n" % (c.sha256(a.artifact), os.path.abspath(a.artifact)))
    for slug, keys in groups(a.phase).items():
        print("%s: %s -> %s" % (slug, ", ".join(keys), report_path(a.run, a.phase, a.round, slug)))
    return 0


def verify(a):
    e45, e46 = [], []
    expected = groups(a.phase)
    for slug, keys in expected.items():
        path = report_path(a.run, a.phase, a.round, slug)
        if not os.path.exists(path):
            e46.append("no report from %s at %s" % (slug, os.path.basename(path)))
            continue
        got = [r[0] for r in c.parse_report(path)]
        missing = [k for k in keys if k not in got]
        extra = [k for k in got if k not in keys]
        dup = sorted({k for k in got if got.count(k) > 1})
        if missing:
            e46.append("%s has no row for %s" % (slug, ", ".join(missing)))
        if missing or extra or dup:
            e45.append("%s lists %s; assigned %s" % (slug, ", ".join(got) or "nothing", ", ".join(keys)))
    folder = os.path.join(a.run, "qa-reports")
    pat = re.compile(r"^%s-round-%d-(.+)\.md$" % (re.escape(a.phase), a.round))
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        m = pat.match(name)
        if m and m.group(1) not in expected and m.group(1) != "round-check":
            e46.append("unexpected report %s" % name)
    changed = False
    cpath = checksum_path(a.run, a.phase, a.round)
    if not os.path.exists(cpath):
        e46.append("no checksum recorded; run `qa_round.py start` before the round")
    else:
        before = c.read(cpath).split()[0]
        after = c.sha256(a.artifact)
        if before != after:
            changed = True
            e46.append("artifact checksum changed during the round (%s to %s)" % (before[:12], after[:12]))
    rows = [("E45", "Fail" if e45 else "Pass", "; ".join(e45) or "Every report lists exactly its assigned eval IDs"),
            ("E46", "Fail" if e46 else "Pass", "; ".join(e46) or "One report per group, a row per eval, artifact unchanged")]
    passed = sum(1 for r in rows if r[1] == "Pass")
    verdict = "**QA Results (Round check): phase %s, round %d, 2 checked, %d passed, %d failed**" % (a.phase, a.round, passed, 2 - passed)
    body = [verdict, "", "| Eval | Result | Evidence |", "|---|---|---|"] + ["| %s | %s | %s |" % (e, r, ev.replace("|", "\\|")) for e, r, ev in rows]
    with open(report_path(a.run, a.phase, a.round, "round-check"), "w", encoding="utf-8") as f:
        f.write("\n".join(body) + "\n")
    print(verdict)
    for e, r, ev in rows:
        if r != "Pass":
            print("| %s | %s | %s |" % (e, r, ev))
    if changed:
        return 2
    return 1 if passed < 2 else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["start", "verify"])
    ap.add_argument("--run", required=True)
    ap.add_argument("--phase", required=True, choices=list(c.PHASES) + list(c.HANDOFF_POINTS))
    ap.add_argument("--round", required=True, type=int)
    ap.add_argument("--artifact", required=True)
    a = ap.parse_args()
    return start(a) if a.command == "start" else verify(a)


if __name__ == "__main__":
    sys.exit(main())
