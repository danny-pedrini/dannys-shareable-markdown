#!/usr/bin/env python3
"""Save a QA subagent's report verbatim from its Claude Code transcript, then check it.

Save mode copies the subagent's final message to --out byte for byte, appends a
line to <run>/qa-reports/manifest.jsonl (agent ID, path, sha256, agent type,
spawn depth), and runs E42 on the saved report. It also keeps the round's E42
verdict in <phase>-round-<n>-report-check.md, counting -rerun reports toward
their original. Exit 3 means no transcript exists (Cursor runs): save the report
with Write, then run --check on it.

Usage:
  save-qa-report.py --run RUN --agent-id ID --out FILE --phase D --group merged
  save-qa-report.py --run RUN --agent-id ID --out FILE --ids E36    # single-eval re-run
  save-qa-report.py --run RUN --agent-id ID --role lens              # log only, no report
  save-qa-report.py --check FILE --phase D --group Fidelity          # E42 on a saved file
  save-qa-report.py --verify --run RUN                               # E43, for the trace author
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c  # noqa: E402

REPORT_NAME = re.compile(r"^([PIDR])-round-(\d+)-(.+)\.md$")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def e42(text, expected):
    """One row per assigned eval, no other rows, each with non-empty Result and Evidence cells.

    Returns (covered, uncovered, problems): assigned IDs with one complete row, assigned IDs
    without one, and every problem found, including the uncovered IDs.
    """
    problems, seen, complete = [], {}, set()
    for first, result, evidence in c.report_rows(text):
        eid = first.split()[0] if first else ""
        if not (eid.startswith("E") and eid[1:].isdigit()):
            problems.append(f"row not tied to one eval ID: '{first}'")
            continue
        seen[eid] = seen.get(eid, 0) + 1
        if not evidence.strip():
            problems.append(f"{eid} has an empty Evidence cell")
        elif not result.strip():
            problems.append(f"{eid} has an empty Result cell")
        else:
            complete.add(eid)
    for eid, n in seen.items():
        if eid not in expected:
            problems.append(f"{eid} reported but not assigned")
        elif n > 1:
            problems.append(f"{eid} reported {n} times")
    covered = [e for e in expected if e in complete and seen.get(e) == 1]
    uncovered = [e for e in expected if e not in covered]
    problems += [f"{e} missing" for e in uncovered if e not in seen]
    return covered, uncovered, problems


def print_e42(path, expected, problems):
    if problems:
        print(f"E42 Fail: {path}: " + "; ".join(problems))
        return 1
    print(f"E42 Pass: {path}: {len(expected)} of {len(expected)} assigned evals, each with evidence")
    return 0


def record_round(path, expected, covered, uncovered, problems):
    """Keep one E42 row per round in <phase>-round-<n>-report-check.md.

    The round passes when every assigned eval of every subagent has one complete row,
    in the original report or its -rerun report, and no report has a stray or repeated row.
    """
    m = REPORT_NAME.match(Path(path).name)
    if not m or m.group(3) == "report-check":
        return
    phase, rnd, sub = m.group(1), m.group(2), m.group(3)
    folder = Path(path).parent
    side = folder / f"{phase}-round-{rnd}-report-check.json"
    data = json.loads(side.read_text(encoding="utf-8")) if side.exists() else {}
    data[sub] = {"expected": expected, "covered": covered, "uncovered": uncovered, "problems": problems}
    side.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    issues, checked = [], 0
    for name, d in data.items():
        issues += [f"{name}: {p}" for p in d["problems"] if "not assigned" in p]
        if "rerun" in name:
            continue
        checked += 1
        got = set(d["covered"])
        for other, od in data.items():
            if other.startswith(name) and "rerun" in other:
                got |= set(od["covered"])
        issues += [f"{name}: {e} has no complete row" for e in d["expected"] if e not in got]
    result = "Fail" if issues else "Pass"
    evidence = "; ".join(issues) if issues else f"{checked} reports, every assigned eval has one row with evidence"
    evidence = evidence.replace("|", "\\|")
    (folder / f"{phase}-round-{rnd}-report-check.md").write_text(
        f"**QA Results (Report check): {phase}, 1 checked, {int(not issues)} passed, {int(bool(issues))} failed**\n\n"
        f"| Eval | Result | Evidence |\n|---|---|---|\n| E42 | {result} | {evidence} |\n",
        encoding="utf-8",
    )


def expected_ids(a):
    if a.ids:
        return [i.strip() for i in a.ids.split(",") if i.strip()]
    if a.phase and a.group:
        return c.assigned_ids(a.phase, a.group, a.final)
    return None


def manifest_path(run):
    d = Path(run) / "qa-reports"
    d.mkdir(parents=True, exist_ok=True)
    return d / "manifest.jsonl"


def append_manifest(run, entry):
    with open(manifest_path(run), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def verify(run):
    """E43: every saved report still matches its subagent's final message."""
    mpath = Path(run) / "qa-reports" / "manifest.jsonl"
    if not mpath.exists():
        print("E43 Pass: no manifest; reports were saved with Write on a host without transcripts")
        return 0
    problems, checked = [], 0
    for line in mpath.read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        if not entry.get("path"):
            continue
        checked += 1
        saved = Path(entry["path"])
        transcript = c.find_transcript(entry["agent_id"])
        if transcript is None:
            problems.append(f"{saved.name}: transcript for {entry['agent_id']} not found")
            continue
        message = c.final_message(transcript)
        if not saved.exists():
            problems.append(f"{saved.name}: saved file missing")
        elif saved.read_text(encoding="utf-8") != message:
            problems.append(f"{saved.name}: differs from the final message of {entry['agent_id']}")
    if problems:
        print("E43 Fail: " + "; ".join(problems))
        return 1
    print(f"E43 Pass: {checked} saved reports match their subagents' final messages")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", help="Run folder")
    ap.add_argument("--agent-id", help="agentId from the Agent tool result")
    ap.add_argument("--out", help="Report path, <run>/qa-reports/<phase>-round-<n>-<subagent>.md")
    ap.add_argument("--phase", choices=c.PHASES)
    ap.add_argument("--group", help="Fidelity, Structure (P), merged (D, R)")
    ap.add_argument("--final", action="store_true", help="Final QA phase of the run")
    ap.add_argument("--ids", help="Comma-separated eval IDs, for a single-eval re-run")
    ap.add_argument("--role", default="qa", choices=("qa", "lens", "trace"))
    ap.add_argument("--check", help="Run E42 on an already saved report")
    ap.add_argument("--verify", action="store_true", help="Run E43 over the manifest")
    a = ap.parse_args()

    if a.verify:
        if not a.run:
            ap.error("--verify needs --run")
        sys.exit(verify(a.run))

    if a.check:
        expected = expected_ids(a)
        if expected is None:
            ap.error("--check needs --phase and --group, or --ids")
        text = Path(a.check).read_text(encoding="utf-8")
        covered, uncovered, problems = e42(text, expected)
        record_round(a.check, expected, covered, uncovered, problems)
        sys.exit(print_e42(a.check, expected, problems))

    if not (a.run and a.agent_id):
        ap.error("save mode needs --run and --agent-id")
    transcript = c.find_transcript(a.agent_id)
    if transcript is None:
        print(f"No transcript for agent {a.agent_id}. Save the report with Write, then run --check.")
        sys.exit(3)
    meta = c.read_meta(transcript)
    entry = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent_id": a.agent_id.removeprefix("agent-"),
        "role": a.role,
        "agent_type": meta.get("agentType"),
        "spawn_depth": meta.get("spawnDepth"),
        "transcript": str(transcript),
        "path": None,
    }

    if not a.out:
        append_manifest(a.run, entry)
        print(f"Logged {a.role} agent {entry['agent_id']} ({entry['agent_type']}, depth {entry['spawn_depth']})")
        return

    message = c.final_message(transcript)
    if message is None:
        print(f"Agent {a.agent_id} has no final text message. Treat it as a subagent that returned nothing.")
        sys.exit(4)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(message, encoding="utf-8")
    entry["path"] = str(out)
    entry["sha256"] = sha(message)
    append_manifest(a.run, entry)
    print(f"Saved {out} ({len(message)} chars) from agent {entry['agent_id']}")

    expected = expected_ids(a)
    if expected is not None:
        covered, uncovered, problems = e42(message, expected)
        record_round(out, expected, covered, uncovered, problems)
        sys.exit(print_e42(out, expected, problems))


if __name__ == "__main__":
    main()
