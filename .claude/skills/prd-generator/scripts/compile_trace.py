"""Compile the trace's eval_results and qa_loops from a prd-generator run's qa-reports folder (SKILL.md Step 9).

    python3 .claude/skills/prd-generator/scripts/compile_trace.py --run <run> [--out <path>]

Reads every <phase>-round-<n>-<group>.md report and writes <run>/trace-compiled.json with:
  eval_results      one entry per eval per phase it ran in, holding that phase's final-round verdict
  qa_loops          plan, draft, revision, and handoff: attempts, failed eval IDs per round, persistent
  log_eval_results  the invocation-log list: each eval's verdict from the last phase it ran in
E38 combines the Mechanical row and the Fidelity `E38 (row 7)` row: either Fail fails it.
The parent writes every judgment field (decisions, gates, reviewers, observations, persistent
classification) and qa_loops.intake itself, and copies these fields unchanged.
"""
import argparse
import json
import os
import re
import sys

import _common as c

PHASE_KEYS = {"P": "plan", "D": "draft", "R": "revision"}
REPORT = re.compile(r"^(P|D|R|H[0-2])-round-(\d+)-([a-z-]+)\.md$")
RANK = {"Pass": 0, "Fail (ambiguous)": 1, "Fail": 2}


def collect(folder):
    """{phase: {round: {eval_id: (result, evidence)}}}"""
    data = {}
    for name in sorted(os.listdir(folder)):
        m = REPORT.match(name)
        if not m:
            continue
        phase, rnd = m.group(1), int(m.group(2))
        bucket = data.setdefault(phase, {}).setdefault(rnd, {})
        for key, result, evidence in c.parse_report(os.path.join(folder, name)):
            eid = key.split()[0]
            prior = bucket.get(eid)
            if prior is None or RANK[result] > RANK[prior[0]]:
                bucket[eid] = (result, evidence)
    return data


def loop(rounds):
    order = sorted(rounds)
    failed = [[e for e, (r, _) in sorted(rounds[n].items()) if r != "Pass"] for n in order]
    final = set(failed[-1]) if failed else set()
    earlier = set().union(*failed[:-1]) if len(failed) > 1 else set()
    persistent = sorted(final & earlier) + sorted(final - earlier) if len(failed) > 1 else sorted(final)
    return {"attempts": len(order), "rounds": failed, "persistent": persistent}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    folder = os.path.join(a.run, "qa-reports")
    data = collect(folder)
    names = c.eval_names()

    eval_results, qa_loops, last = [], {}, {}
    for phase in ["P", "D", "R", "H0", "H1", "H2"]:
        if phase not in data:
            continue
        rounds = data[phase]
        final = rounds[max(rounds)]
        for eid in sorted(final, key=lambda e: int(e[1:])):
            result, evidence = final[eid]
            detail = "ambiguous: %s" % evidence if result == "Fail (ambiguous)" else None
            eval_results.append({"eval_id": eid, "name": names.get(eid, ""), "phase": phase,
                                 "result": "Fail" if result.startswith("Fail") else "Pass", "detail": detail})
            last[eid] = {"Pass": "P", "Fail": "F", "Fail (ambiguous)": "F-ambiguous"}[result]
        if phase in PHASE_KEYS:
            qa_loops[PHASE_KEYS[phase]] = loop(rounds)
        else:
            qa_loops.setdefault("handoff", {})[phase] = loop(rounds)

    out = {"eval_results": eval_results, "qa_loops": qa_loops,
           "log_eval_results": [{"id": e, "r": r} for e, r in sorted(last.items(), key=lambda x: int(x[0][1:]))]}
    path = a.out or os.path.join(a.run, "trace-compiled.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("wrote", path, "with", len(eval_results), "eval_results across", ", ".join(qa_loops) or "no phases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
