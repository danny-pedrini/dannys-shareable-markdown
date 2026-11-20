"""Append one event to the update folder's run-log.md (the only file the trace author trusts for timing and sequence).

Run from the update folder:
    python3 -I <skill>/scripts/log_event.py <step> <event> [key=value ...]

Examples:
    python3 -I <skill>/scripts/log_event.py "Step 1" step_start
    python3 -I <skill>/scripts/log_event.py "Step 1" mcp_error server=google-docs tool=read_document resource=<doc id> error=timeout recovered=false
    python3 -I <skill>/scripts/log_event.py "Step 1" stop reason="Sheets read of the sizing sheet failed twice"
    python3 -I <skill>/scripts/log_event.py "Gate 1" subagent role=gate1-grader output=qa-gate1-r1.md ok=true
    python3 -I <skill>/scripts/log_event.py "Gate 1" qa_round gate="Gate 1" round=1 fails=2 defects=2 fixed=2 additions=1
    python3 -I <skill>/scripts/log_event.py "Gate 1" gate_presented gate="Gate 1" summary="fact ledger, 3 open comments"

The timestamp is the current UTC time; never pass one. Line format and event types are in
references/trace-schema.md section 1. A value containing | or ; is wrapped in backticks.
Creates run-log.md (with a one-line header) when it does not exist. Exits non-zero on an unknown
event type or a missing required field, and writes nothing.
"""
import datetime
import os
import sys

REQUIRED = {
    "step_start": [],
    "step_end": ["outcome"],
    "mcp_error": ["server", "tool", "resource", "error", "recovered"],
    "retry_ok": ["server", "tool", "resource"],
    "stop": ["reason"],
    "gate_presented": ["gate", "summary"],
    "gate_answered": ["gate", "summary"],
    "subagent": ["role", "output", "ok"],
    "qa_round": ["gate", "round", "fails", "defects", "fixed", "additions"],
    "check": ["script", "result"],
    # A free-text marker (a resume, a reconstructed gap). Ignored when the trace is compiled.
    "note": ["text"],
}
HEADER = "# run-log (one line per event, written by log_event.py; see references/trace-schema.md)\n"


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    step, event, pairs = argv[1], argv[2], argv[3:]
    if event not in REQUIRED:
        print(f"log_event.py: unknown event type '{event}'. Valid: {', '.join(REQUIRED)}", file=sys.stderr)
        return 2
    fields = {}
    for p in pairs:
        if "=" not in p:
            print(f"log_event.py: field '{p}' is not key=value", file=sys.stderr)
            return 2
        k, v = p.split("=", 1)
        fields[k.strip()] = v.strip()
    missing = [k for k in REQUIRED[event] if k not in fields]
    if missing:
        print(f"log_event.py: event '{event}' needs: {', '.join(missing)}", file=sys.stderr)
        return 2
    if event == "step_end" and fields["outcome"] not in ("success", "partial", "failure", "stopped"):
        print("log_event.py: outcome must be success, partial, failure or stopped", file=sys.stderr)
        return 2
    if event == "check" and fields["result"] not in ("pass", "fail"):
        print("log_event.py: result must be pass or fail", file=sys.stderr)
        return 2
    cells = "; ".join(f"{k}={('`' + v + '`') if ('|' in v or ';' in v) else v}" for k, v in fields.items())
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new = not os.path.exists("run-log.md") or os.path.getsize("run-log.md") == 0
    with open("run-log.md", "a") as fh:
        if new:
            fh.write(HEADER)
        fh.write(f"{ts} | {step} | {event} | {cells}".rstrip() + "\n")
    print(f"logged: {ts} | {step} | {event}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
