#!/usr/bin/env python3
"""Mechanical observability checks for a generated skill run.

Template script. agent-architect copies it into a generated skill's scripts/
folder when that skill has Full observability. The orchestrator runs it after
the logging step and records its output unchanged (agent-architect Step 2.6).

It runs the eight mechanical checks from the verification step in
references/observability-templates.md. It does not judge whether `decisions`
captures non-default choices, and it never sets `verified`. A fresh agent does
both after this script exits 0.

Usage:
  python3 verify_observability.py --skill-dir .claude/skills/<skill> \
      --trace .claude/skills/<skill>/observability/traces/<file>.json \
      [--output <path> ...] [--root <workspace-root>] [--max-age-min 10]

Pass --max-age-min 0 to skip the recency check (for replaying old traces).
Pass --all-traces to check every trace in the skill's traces/ folder and
compare each result with its recorded `verified` flag.

Exit codes: 0 all checks pass, 1 any check fails, 2 usage or input error.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys

PATH_RE = re.compile(r"[\w.\-/ ]*/[\w.\-/ ]*\.\w{1,5}")


def parse_ts(value):
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def load_log(log_path):
    entries = []
    with open(log_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                entries.append(None)
    return entries


def resolve(root, path):
    return path if os.path.isabs(path) else os.path.join(root, path)


def check_trace(trace_path, log_entries, root, outputs, max_age_min):
    results = []

    def add(check_id, name, ok, detail=""):
        results.append({"id": check_id, "check": name, "result": "PASS" if ok else "FAIL", "detail": detail})

    # M4: trace file exists and is valid JSON
    trace = None
    if not os.path.isfile(trace_path):
        add("M4", "trace exists and is valid JSON", False, f"missing: {trace_path}")
    else:
        try:
            with open(trace_path, encoding="utf-8") as fh:
                trace = json.load(fh)
            add("M4", "trace exists and is valid JSON", isinstance(trace, dict))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            add("M4", "trace exists and is valid JSON", False, str(exc))
    trace = trace if isinstance(trace, dict) else {}

    # M1: log entry for this run exists (matched on ts and skill)
    entry = None
    for item in reversed(log_entries):
        if isinstance(item, dict) and item.get("ts") == trace.get("ts") and item.get("skill") == trace.get("skill"):
            entry = item
            break
    add("M1", "log entry exists for this run", entry is not None,
        "" if entry else f"no log entry with ts={trace.get('ts')} skill={trace.get('skill')}")

    # M2: outcome matches the output on disk
    out_paths = list(outputs) or PATH_RE.findall(str(trace.get("output_summary", "")))
    out_paths = [p.strip() for p in out_paths if p.strip()]
    outcome = (entry or {}).get("outcome")
    if outcome in ("success", "partial"):
        missing = [p for p in out_paths if not (os.path.isfile(resolve(root, p)) and os.path.getsize(resolve(root, p)) > 0)]
        ok = bool(out_paths) and not missing
        detail = "no output path given or found" if not out_paths else (f"missing or empty: {missing}" if missing else "")
        add("M2", "outcome matches output on disk", ok, detail)
    elif outcome == "failure":
        add("M2", "outcome matches output on disk", True, "failure outcome; no output required")
    else:
        add("M2", "outcome matches output on disk", False, f"outcome not readable: {outcome!r}")

    # M3: log ts is recent
    if max_age_min <= 0:
        add("M3", "log ts is recent", True, "skipped (--max-age-min 0)")
    else:
        ts = parse_ts((entry or {}).get("ts"))
        if ts is None:
            add("M3", "log ts is recent", False, "ts missing or not ISO 8601")
        else:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=dt.timezone.utc)
            age = (dt.datetime.now(dt.timezone.utc) - ts).total_seconds() / 60
            add("M3", "log ts is recent", 0 <= age <= max_age_min, f"age {age:.1f} min")

    # M5: local context_sources exist
    sources = trace.get("context_sources")
    if not isinstance(sources, list):
        add("M5", "local context_sources exist", False, "context_sources missing or not a list")
    else:
        local = [s.get("path") for s in sources if isinstance(s, dict) and s.get("type") == "local"]
        missing = [p for p in local if not p or not os.path.exists(resolve(root, p))]
        add("M5", "local context_sources exist", not missing, f"missing: {missing}" if missing else f"{len(local)} checked")

    # M6: output_summary paths exist on disk
    summary_paths = [p.strip() for p in PATH_RE.findall(str(trace.get("output_summary", ""))) if p.strip()]
    missing = [p for p in summary_paths if not os.path.exists(resolve(root, p))]
    add("M6", "output_summary paths exist", bool(summary_paths) and not missing,
        "no path in output_summary" if not summary_paths else (f"missing: {missing}" if missing else ""))

    # M7: tool_calls non-empty, each entry has purpose
    calls = trace.get("tool_calls")
    ok = isinstance(calls, list) and len(calls) > 0 and all(isinstance(c, dict) and c.get("purpose") for c in calls)
    add("M7", "tool_calls non-empty with purpose", ok, "" if ok else "empty, or an entry lacks purpose")

    # M8: trace outcome matches log outcome
    add("M8", "trace outcome matches log outcome", entry is not None and trace.get("outcome") == outcome,
        f"trace={trace.get('outcome')!r} log={outcome!r}")

    return trace, results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skill-dir", required=True)
    ap.add_argument("--trace")
    ap.add_argument("--all-traces", action="store_true")
    ap.add_argument("--output", action="append", default=[])
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--max-age-min", type=float, default=10)
    args = ap.parse_args()

    log_path = os.path.join(args.skill_dir, "observability", "invocation-log.jsonl")
    if not os.path.isfile(log_path):
        print(json.dumps({"error": f"invocation log not found: {log_path}"}))
        return 2
    if not args.trace and not args.all_traces:
        print(json.dumps({"error": "pass --trace or --all-traces"}))
        return 2

    log_entries = load_log(log_path)

    if args.all_traces:
        trace_dir = os.path.join(args.skill_dir, "observability", "traces")
        report, disagreements = [], 0
        for name in sorted(os.listdir(trace_dir)) if os.path.isdir(trace_dir) else []:
            if not name.endswith(".json"):
                continue
            trace, results = check_trace(os.path.join(trace_dir, name), log_entries, args.root, [], 0)
            passed = all(r["result"] == "PASS" for r in results)
            recorded = trace.get("verified") is True
            if passed != recorded:
                disagreements += 1
            report.append({"trace": name, "mechanical_pass": passed, "recorded_verified": recorded, "checks": results})
        print(json.dumps({"traces": report, "disagreements": disagreements}, indent=2))
        return 1 if disagreements else 0

    _, results = check_trace(args.trace, log_entries, args.root, args.output, args.max_age_min)
    failed = [r for r in results if r["result"] == "FAIL"]
    print(json.dumps({"trace": args.trace, "checks": results, "failed": len(failed)}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
