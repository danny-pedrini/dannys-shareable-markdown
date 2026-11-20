"""Gate checkpoint for run-log.md. Run before presenting any gate, before Step 6 and on every resume.

Run from the round folder:  python3 -I <skill>/scripts/log_check.py

Exits non-zero (and the orchestrator stops until fixed) when:
  1. run-log.md is missing or has no event lines;
  2. a line does not parse as `<UTC ts> | <step> | <event> | <fields>` with a known event type;
  3. the log is behind the work: a working file in the round folder (STATUS.md, qa-*.md, ledger and
     filing files, ticket and comment files, cluster_defs.py) is newer than the last logged event
     by more than 20 minutes. Log the missing events (or a `note` event saying what is not
     recorded and why), then rerun.
Prints warnings (exit 0) for: a gate_presented with no gate_answered, a step_start with no step_end
for a step other than the latest, and the count of subagent and qa_round events.
"""
import datetime
import glob
import os
import re
import sys

EVENTS = {"step_start", "step_end", "mcp_error", "stop", "retry_ok", "gate_presented",
          "gate_answered", "subagent", "qa_round", "note"}
LINE = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) \| ([^|]+?) \| (\w+) \|(.*)$")
SLACK_MIN = 20
WATCH = ["STATUS.md", "qa-*.md", "ledger/*.md", "ledger/qa/*.md", "filing-ledger*.md", "comment-ledger.md",
         "ticket-drafts.md", "ticket-comments.md", "ticket-plan.md", "cluster_defs.py", "report_defs.py",
         "dedup-verdicts.md", "bodies/index.json"]


def main():
    if not os.path.exists("run-log.md"):
        print("FAIL: run-log.md is missing. Create it with log_event.py (a `note` event saying what is "
              "not recorded, then the events you can source from files), then rerun.")
        return 1
    events, bad = [], []
    for n, l in enumerate(open("run-log.md").read().split("\n"), 1):
        if not l.strip() or l.startswith("#"):
            continue
        m = LINE.match(l)
        if not m or m.group(3) not in EVENTS:
            bad.append((n, l[:100]))
            continue
        events.append((datetime.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc),
                       m.group(2).strip(), m.group(3), m.group(4)))
    if not events:
        print("FAIL: run-log.md has no event lines.")
        return 1
    rc = 0
    for n, l in bad:
        print(f"FAIL: run-log.md line {n} does not parse: {l}")
        rc = 1
    last = max(e[0] for e in events)
    newest, newest_f = None, None
    for pat in WATCH:
        for f in glob.glob(pat):
            t = datetime.datetime.fromtimestamp(os.path.getmtime(f), datetime.timezone.utc)
            if newest is None or t > newest:
                newest, newest_f = t, f
    if newest and (newest - last) > datetime.timedelta(minutes=SLACK_MIN):
        gap = int((newest - last).total_seconds() // 60)
        print(f"FAIL: the log is behind the work: {newest_f} changed {gap} minutes after the last logged event "
              f"({last:%Y-%m-%dT%H:%M:%SZ}). Log what happened since, then rerun.")
        rc = 1
    presented = {}
    for ts, step, ev, f in events:
        g = re.search(r"gate=([^;]+)", f)
        if ev == "gate_presented" and g:
            presented[g.group(1).strip()] = True
        if ev == "gate_answered" and g:
            presented.pop(g.group(1).strip(), None)
    for g in presented:
        print(f"WARN: {g} was presented and has no gate_answered yet (expected if it is the gate now waiting).")
    started, ended = {}, set()
    for ts, step, ev, f in events:
        if ev == "step_start":
            started[step] = ts
        if ev == "step_end":
            ended.add(step)
    latest = max(started, key=started.get) if started else None
    for s in started:
        if s not in ended and s != latest:
            print(f"WARN: step '{s}' has a step_start and no step_end.")
    print(f"run-log.md: {len(events)} events; last {last:%Y-%m-%dT%H:%M:%SZ}; "
          f"{sum(1 for e in events if e[2] == 'subagent')} subagent, {sum(1 for e in events if e[2] == 'qa_round')} qa_round")
    print("PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
