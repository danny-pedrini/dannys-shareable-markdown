# Trace schema

Observability is Full with independent trace authorship (`agent-architect/references/observability-templates.md` section 5). The orchestrator writes `run-log.md` live and one invocation-log line. A fresh subagent authors the trace from the files on disk.

## 1. `run-log.md` (in the update folder, written live)

Write lines only with `scripts/log_event.py`. Check the log with `scripts/log_check.py` before every gate and before Step 7. A resumed run appends; never truncate or rewrite the log.

```
<UTC ts> | <step> | <event type> | <key=value; key=value>
```

| Event type | Fields | Feeds |
| --- | --- | --- |
| `step_start` | none | `steps[]` |
| `step_end` | `outcome=success\|partial\|failure\|stopped` | `steps[]` |
| `mcp_error` | `server; tool; resource; error; recovered=false` | `mcp_errors[]` |
| `retry_ok` | `server; tool; resource` (`server` is the connector that worked) | flips every `mcp_error` for that resource to recovered, including the first connector's |
| `stop` | `reason` (tool, resource and error, or the missing link) | `stops[]` |
| `gate_presented` | `gate; summary` | `gates[]` |
| `gate_answered` | `gate; summary` (Danny's ruling, in his words where short) | `gates[]` |
| `subagent` | `role; output; ok` | `subagents[]` |
| `qa_round` | `gate; round; fails; defects; fixed; additions` | `qa_rounds[]` |
| `check` | `script; result=pass\|fail; detail` | `checks[]` |
| `note` | `text` (a resume, a gap, a Danny edit snapshot) | none |

Every `mcp_error` is followed, before the step's next event, by a `retry_ok`, a `stop`, or the second connector's `mcp_error` for the same resource. A `stop` ends the turn: the orchestrator reports it to Danny and waits.

## 2. Trace JSON

Path: `.claude/skills/ai-pilot-update/observability/traces/YYYY-MM-DD_HHMM_<feature-slug>.json`. The trace author writes it at Step 6.3, updates the same file at Step 7.3, or writes it at the next resume after a stopped run.

```json
{
  "ts": "2026-11-10T14:02:00Z",
  "skill": "ai-pilot-update",
  "version": "1.1",
  "feature": "AI-Drafted Messages",
  "update_date": "2026-11-10",
  "mode": "run",
  "outcome": "success",
  "duration_s": 0,
  "input_summary": "<rounds in scope, tickets, changes, in one line>",
  "output_summary": "<what was built and where, in one line>",
  "context_sources": [{"type": "google_doc", "id": "<doc id>", "purpose": "prior tab and comments"}],
  "steps": [{"step": "Step 1", "started": "...", "finished": "...", "outcome": "success"}],
  "gates": [{"gate": "Gate 1", "presented": "...", "answered": "...", "summary": "..."}],
  "mcp_errors": [],
  "stops": [],
  "subagents": [{"role": "gate1-grader", "output": "qa-gate1-r1.md", "ok": true}],
  "qa_rounds": [{"gate": "Gate 1", "round": 1, "fails": 2, "defects": 2, "fixed": 2, "additions": 1}],
  "checks": [{"script": "check_facts.py", "result": "pass"}],
  "counts": {"sources_read": 0, "facts": 0, "tickets": 0, "themes": 0, "judges_read": 0, "doc_writes": 0, "pages_rendered": 0, "danny_edit_snapshots": 0},
  "eval_results": [{"eval_id": "G1-1", "name": "Every fact cites a source read this run", "result": "Pass", "detail": null}],
  "gate_evidence": {
    "preflight": {"evidence_found": true, "detail": "..."},
    "gate_1": {"evidence_found": true, "detail": "..."},
    "gate_2": {"evidence_found": true, "detail": "..."},
    "gate_3": {"evidence_found": true, "detail": "..."}
  },
  "decisions": [{"decision": "theme_split", "rationale": "...", "phase": "Gate 1"}],
  "observations": "...",
  "independently_authored": true
}
```

`eval_results` holds every gate's results from `eval-results.md`. At Step 7.3 the trace author adds its own verdicts for the evals `evals.md` assigns to it, and the orchestrator copies those into `eval-results.md` unchanged.

`counts` come from the files, recounted by the trace author: `sources.md` rows, `facts.md` rows, `tickets.json` keys, `themes-working.md` themes, judges read in `eval-coverage.md`, `build-log.md` writes, rendered pages, and `update-danny-<n>.md` files.

## 3. Gate evidence criteria (for the trace author)

| Gate | `evidence_found` is true when |
| --- | --- |
| `preflight` | `run-log.md` shows a Step 1 `step_end` with `outcome=success`, and `sources.md` has a row for every resource Step 1 lists, each OK |
| `gate_1` | `qa-gate1-r<k>.md` and `qa-gate1-post-r<k>.md` exist with no unaddressed Fail, `check_facts.py` passed after the last fix, and a `gate_answered` line for Gate 1 precedes Step 4's first event |
| `gate_2` | `qa-gate2-r<k>.md`, `review-ai-eng.md` and `review-pm-exec.md` exist; `check_doc.py` passed after the last fix; a `gate_answered` line for Gate 2 precedes Step 5's first event |
| `gate_3` | `readback.json` exists, `compare_tab.py` passed, `qa-gate3-r<k>.md` exists, and a `gate_answered` line for Gate 3 precedes Step 7's first event |

Add `detail` for every gate, naming the files inspected. Ambiguous evidence is `false`, with the reason.

## 4. Invocation log

The orchestrator appends one line to `observability/invocation-log.jsonl` at Step 6.3, and updates its outcome and `eval_results` at Step 7.3. The line follows the base schema: `ts`, `skill`, `input_summary`, `duration_s`, `outcome`, `notes` (feature, update date and mode), `version`, and `eval_results` in the compact form `{"id": "G1-1", "r": "P"}`.

## 5. Failure stub

A run that stops still ends with a `stop` line or a `step_end` with `outcome=partial` or `failure`. At the next resume, spawn the trace author on whatever the folder holds before continuing. That trace's `outcome` is `partial` or `failure`, which is correct. The trace author grades O-2 on it.
