#!/usr/bin/env python3
"""Build the mechanical fields of a run's trace, then merge the trace author's fields.

build: the orchestrator runs it before spawning the trace author. It fills
tool_calls from mcp-ledger.jsonl, qa_rounds and eval_results from qa-reports/,
and records E21's Logic result on the ledger under _e21.

merge: the trace author runs it after checking the skeleton against the files.
It reads the judgment fields as one JSON object on stdin, writes the trace with
independently_authored true, and refuses to overwrite an existing trace.
Any key in the stdin object replaces the skeleton's value; the script names each
replaced key so the author can explain it in observations. A key ending in
_extra is appended to the list it names: tool_calls_extra for the run's Write,
Edit, and Agent calls, and eval_results_extra for E43.

Usage:
  trace-skeleton.py build --run RUN [--out RUN/trace-skeleton.json]
  trace-skeleton.py merge --skeleton RUN/trace-skeleton.json --out TRACE.json < fields.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c  # noqa: E402

REPORT_NAME = re.compile(r"^([PIDR])-round-(\d+)-(.+)\.md$")
JUDGMENT_KEYS = (
    "ts", "version", "mode", "outcome", "input_summary", "context_sources", "output_summary",
    "gate_evidence", "metric_deltas", "reviewers", "decisions", "observations",
)
ORDER = (
    "ts", "skill", "version", "mode", "outcome", "input_summary", "context_sources", "output_summary",
    "tool_calls", "gate_evidence", "metric_deltas", "qa_rounds", "reviewers", "eval_results",
    "decisions", "observations", "independently_authored",
)


def tool_calls(run):
    ledger = Path(run) / "mcp-ledger.jsonl"
    calls = []
    if not ledger.exists():
        return calls
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        calls.append({
            "tool": rec.get("tool"),
            "target": rec.get("resource"),
            "purpose": rec.get("purpose"),
            "ok": rec.get("ok"),
            "write": rec.get("write"),
        })
    return calls


def verdicts(run):
    """{phase: {round: {eval_id: (result, evidence)}}} from qa-reports/, re-runs read last."""
    reports = Path(run) / "qa-reports"
    files = []
    for p in reports.glob("*.md") if reports.exists() else []:
        m = REPORT_NAME.match(p.name)
        if m:
            files.append((m.group(1), int(m.group(2)), "rerun" in m.group(3), p.name, p))
    out = {}
    for phase, rnd, _rerun, _name, path in sorted(files):
        table = out.setdefault(phase, {}).setdefault(rnd, {})
        for first, result, evidence in c.report_rows(path.read_text(encoding="utf-8")):
            eid = first.split()[0]
            if re.fullmatch(r"E\d\d", eid):
                table[eid] = (result, evidence)
    return out


def failed(result):
    return result.lower().startswith("fail")


def qa_rounds_and_results(run):
    names = {r["id"]: r["name"] for r in c.phase_map()}
    rounds_out, results = {}, []
    all_verdicts = verdicts(run)
    for phase in c.PHASES:
        by_round = all_verdicts.get(phase)
        if not by_round:
            continue
        ordered = [by_round[n] for n in sorted(by_round)]
        fails = [[e for e, (res, _) in sorted(r.items()) if failed(res)] for r in ordered]
        rounds_out[phase] = {"attempts": len(ordered), "rounds": fails, "persistent": fails[-1]}
        for eid, (res, evidence) in sorted(ordered[-1].items()):
            detail = None
            if "ambiguous" in res.lower():
                detail = f"ambiguous: {evidence}"
            elif failed(res):
                detail = evidence
            results.append({
                "eval_id": eid,
                "name": names.get(eid, ""),
                "phase": phase,
                "result": "Fail" if failed(res) else "Pass",
                "detail": detail,
            })
    return rounds_out, results


def build(a):
    run = Path(a.run)
    rounds, results = qa_rounds_and_results(run)
    e21_result, e21_evidence = c.e21(run / "mcp-ledger.jsonl")
    skeleton = {
        "skill": "dashboard-requirements",
        "tool_calls": tool_calls(run),
        "qa_rounds": rounds,
        "eval_results": results,
        "_e21": {"result": e21_result, "evidence": e21_evidence},
    }
    out = Path(a.out) if a.out else run / "trace-skeleton.json"
    out.write_text(json.dumps(skeleton, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out}: {len(skeleton['tool_calls'])} tool calls, phases {', '.join(rounds) or 'none'}, "
          f"{len(results)} eval results. E21 on the ledger: {e21_result}.")


def merge(a):
    skeleton = json.loads(Path(a.skeleton).read_text(encoding="utf-8"))
    fields = json.load(sys.stdin)
    missing = [k for k in JUDGMENT_KEYS if k not in fields]
    if missing:
        sys.exit("Missing judgment fields: " + ", ".join(missing))
    out = Path(a.out)
    if out.exists():
        sys.exit(f"{out} exists; a trace is written once")
    extras = {k[: -len("_extra")]: fields.pop(k) for k in list(fields) if k.endswith("_extra")}
    replaced = [k for k in fields if k in skeleton and not k.startswith("_")]
    trace = {k: v for k, v in skeleton.items() if not k.startswith("_")}
    trace.update(fields)
    for key, items in extras.items():
        trace[key] = list(trace.get(key, [])) + list(items)
    trace["independently_authored"] = True
    ordered = {k: trace[k] for k in ORDER if k in trace}
    ordered.update({k: v for k, v in trace.items() if k not in ordered})
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Trace written: {out}. Skeleton fields replaced: {', '.join(replaced) or 'none'}. "
          f"Skeleton E21: {skeleton.get('_e21', {}).get('result', 'not run')}.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--run", required=True)
    b.add_argument("--out")
    m = sub.add_parser("merge")
    m.add_argument("--skeleton", required=True)
    m.add_argument("--out", required=True)
    a = ap.parse_args()
    build(a) if a.cmd == "build" else merge(a)


if __name__ == "__main__":
    main()
