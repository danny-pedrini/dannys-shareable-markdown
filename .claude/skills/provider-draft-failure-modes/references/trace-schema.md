# Trace schema

Observability for this skill is Full: an append-only run log written live in the round folder, one JSON trace per run compiled from it at Step 6, an invocation-log line per run, and a verification subagent. Based on the agent-architect observability templates (`agent-architect/references/observability-templates.md`), extended with the fields this skill's gated, multi-step, multi-subagent pipeline needs.

## 1. `run-log.md` (written live, in the round folder)

SKILL.md has the orchestrator record MCP errors, stops, gates, subagent outputs and QA rounds as they happen, appended to `<round-folder>/run-log.md`. This is the only file written during the run that Step 6 trusts for timing and sequence; everything else in the round folder shows final state, not what happened when. A resumed run appends to the same file; never truncate or rewrite it.

### Line format

One line per event:

```
<UTC ts> | <step> | <event type> | <fields>
```

- `<UTC ts>`: ISO 8601, e.g. `2026-10-21T18:04:00Z`.
- `<step>`: the step and sub-step name as used in `STATUS.md` (e.g. `Step 1`, `Step 2a`, `Step 3`, `Gate 3`).
- `<event type>`: one of `step_start`, `step_end`, `mcp_error`, `stop`, `retry_ok`, `gate_presented`, `gate_answered`, `subagent`, `qa_round`, `note`. Write lines only with `scripts/log_event.py` and check the log with `scripts/log_check.py` (SKILL.md `<hard_constraints>`). `note` (`text=<one line>`) marks a resume or a gap (for example `text=events before 2026-11-03T19:00Z are not recorded`); it feeds no trace array.
- `<fields>`: `key=value` pairs separated by `; `. A value containing `|` or `;` gets wrapped in backticks.

### Event types and fields

| Event type | Fields | Feeds trace array |
| --- | --- | --- |
| `step_start` | (none required beyond step) | `steps[]` (`started`) |
| `step_end` | `outcome=<success\|partial\|failure>` | `steps[]` (`finished`, `outcome`) |
| `mcp_error` | `server=<name>; tool=<name>; resource=<id>; error=<message>; recovered=<true\|false>` | `mcp_errors[]` |
| `retry_ok` | `server=<name>; tool=<name>; resource=<id>` | marks the matching prior `mcp_error` (same step, server, tool, resource) `recovered=true` |
| `stop` | `reason=<one line>` | `stops[]` |
| `gate_presented` | `gate=<name>; summary=<one line of what was shown>` | `gates[]` (`presented`, `summary`) |
| `gate_answered` | `gate=<name>; summary=<one line of what was decided>` | `gates[]` (`answered`), appended to `summary` |
| `subagent` | `role=<name>; batch=<id or ->; output=<path>; ok=<true\|false>` | `subagents[]` |
| `qa_round` | `qa_point=<name>; round=<n>; defects=<n>; fixed=<n>` | `qa_rounds[]` |

Example lines:

```
2026-10-21T17:03:12Z | Step 1 | step_start |
2026-10-21T17:04:05Z | Step 1 | mcp_error | server=atlassian-hh-sse; tool=getJiraIssue; resource=QCARE-125; error=timeout; recovered=false
2026-10-21T17:04:06Z | Step 1 | stop | reason=getJiraIssue timed out on QCARE-125, no fallback attempted yet
2026-10-21T17:06:40Z | Step 1 | retry_ok | server=atlassian-hh-sse; tool=getJiraIssue; resource=QCARE-125
2026-10-21T17:09:00Z | Step 1 | step_end | outcome=success
2026-10-21T17:30:00Z | Step 2a | subagent | role=extractor; batch=PI; output=ledger/PI.md; ok=true
2026-10-21T18:10:00Z | Step 2b | qa_round | qa_point=2b-mechanical; round=1; defects=3; fixed=3
2026-10-21T19:00:00Z | Gate 2 | gate_presented | gate=Gate 2; summary=failure-mode table, input-issue table, decision items D1-D7
2026-10-21T19:22:00Z | Gate 2 | gate_answered | gate=Gate 2; summary=8 disagreements resolved, D1-D7 answered
```

### Compiling `run-log.md` into the trace (Step 6)

- **`steps[]`:** one entry per step name. `started` = timestamp of its first `step_start` line; `finished` = timestamp of its last `step_end` line (null if the run stopped before one was written); `outcome` = the `outcome` field of that last `step_end` line (or `"partial"` if the run ended without one, per the failure-stub rule below).
- **`mcp_errors[]`:** one entry per `mcp_error` line, fields copied directly (`ts`, `step`, `server`, `tool`, `resource`, `error`). `recovered` starts as the line's own value; a later matching `retry_ok` line (same step, server, tool, resource) flips it to `true`.
- **`stops[]`:** one entry per `stop` line (`ts`, `step`, `reason`).
- **`gates[]`:** one entry per gate name, merging its `gate_presented` line (`presented` ts) and `gate_answered` line (`answered` ts, `summary`). A gate with a `presented` entry and no `answered` entry by the end of the log means the run is still waiting at that gate; Step 6 reports it as such rather than compiling a trace for an unfinished run.
- **`subagents[]`:** one entry per `subagent` line, fields copied directly (`role`, `batch`, `output path` from `output`, `ok`).
- **`qa_rounds[]`:** one entry per `qa_round` line, fields copied directly (`qa point` from `qa_point`, `round`, `defects`, `fixed`).

**A step left open at a gate (intended).** A round that pauses at a gate leaves the step it was in with a `step_start` and no `step_end`, because the step is not finished. `log_check.py` prints `WARN: step '<name>' has a step_start and no step_end` for any open step other than the one that started last. When a parent step (for example `Step 3`) has sub-steps logged under their own names (`Step 3 item 3`), the parent is open and not the latest, so the warning fires for it at every gate. The warning exits 0 and does not block the gate. Do not add a `step_end` to silence it: a `step_end` on a step that has not finished would put a false `finished` time in the trace. The verification subagent (section 4, check 1) accepts a `step_start` with no `step_end` for any step open at a gate. Add the `step_end` when the step actually finishes. The failure-stub rule in section 5 is for a different case: a run that ends for good (an unrecoverable error, an abandoned round) gets a `stop` event or a `step_end` with `outcome=partial` or `failure`. A pause at a gate is not an ending.

E16 (`evals.md`) parses `mcp_errors`, `stops` and `steps` directly off this compiled structure: every `mcp_errors` entry with `recovered` false must be followed by a `stops` entry for the same step before the next step's first event (its first `step_start` or `subagent` line), or the eval fails. Keeping `run-log.md` accurate as you go, not reconstructed after the fact, is what makes that check mean something.

## 2. Trace JSON (one file per run, compiled at Step 6)

Written to `.claude/skills/provider-draft-failure-modes/observability/traces/YYYY-MM-DD_HHMM_<round-slug>.json`. Compiled from `run-log.md` (section 1) plus `round.json`, `STATUS.md` and the round folder's final counts; never hand-written mid-run.

```json
{
  "ts": "2026-10-21T17:03:12Z",
  "skill": "provider-draft-failure-modes",
  "version": "1.0",
  "round": "Round 3",
  "mode": "run",
  "duration_s": 68000,
  "outcome": "success",
  "input_summary": "Round 3: 90 drafts, 6 reviewers, ratings sheet + [AI Eng lead]'s export doc, epic QCARE-7.",
  "context_sources": [
    {"type": "google_sheet", "id": "<ratings sheet id>", "purpose": "Reviewer ratings"},
    {"type": "google_doc", "id": "<export doc id>", "purpose": "Drafts and prior messages"}
  ],
  "output_summary": "37 tickets filed (QCARE-183 to QCARE-219), 12 comments posted, cluster report and CSV built and pushed to Google.",
  "steps": [
    {"step": "Step 1", "started": "2026-10-21T17:03:12Z", "finished": "2026-10-21T17:09:00Z", "outcome": "success"}
  ],
  "gates": [
    {"gate": "Gate 2", "presented": "2026-10-21T19:00:00Z", "answered": "2026-10-21T19:22:00Z", "summary": "8 disagreements resolved, D1-D7 answered"}
  ],
  "mcp_errors": [
    {"ts": "2026-10-21T17:04:05Z", "step": "Step 1", "server": "atlassian-hh-sse", "tool": "getJiraIssue", "resource": "QCARE-125", "error": "timeout", "recovered": true}
  ],
  "stops": [
    {"ts": "2026-10-21T17:04:06Z", "step": "Step 1", "reason": "getJiraIssue timed out on QCARE-125, no fallback attempted yet"}
  ],
  "subagents": [
    {"role": "extractor", "batch": "PI", "output path": "ledger/PI.md", "ok": true}
  ],
  "qa_rounds": [
    {"qa point": "2b-mechanical", "round": 1, "defects": 3, "fixed": 3}
  ],
  "counts": {
    "ratings": 192,
    "traces": 90,
    "ledger_rows": 332,
    "failure_modes": 55,
    "input_issues": 37,
    "tickets_planned": 46,
    "tickets_approved": 37,
    "tickets_filed": 37,
    "comments": 12
  },
  "eval_results": [
    {"eval_id": "E9", "name": "Filed once", "result": "Pass", "detail": null}
  ],
  "observations": "Jira connector dropped once mid-Step 1 and reconnected on retry; no other friction.",
  "verified": true
}
```

### Field definitions beyond the agent-architect base schema

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `round` | string | Yes | `round.json` `round` |
| `mode` | enum | Yes | `"run"`, `"resume"`, `"report"` (SKILL.md modes) |
| `steps[]` | array | Yes | `{step, started, finished, outcome}`, compiled per section 1 |
| `gates[]` | array | Yes | `{gate, presented, answered, summary}`, compiled per section 1 |
| `mcp_errors[]` | array | No (omit if none) | `{ts, step, server, tool, resource, error, recovered}` |
| `stops[]` | array | No (omit if none) | `{ts, step, reason}` |
| `subagents[]` | array | Yes | `{role, batch, output path, ok}`, one per subagent spawned |
| `qa_rounds[]` | array | Yes | `{qa point, round, defects, fixed}`, one per QA pass at every gate |
| `counts` | object | Yes | `ratings, traces, ledger_rows, failure_modes, input_issues, tickets_planned, tickets_approved, tickets_filed, comments`, read from the round folder's final state (`ratings.md`, `row-map.md`, `failure-modes.md`, `input-issues.md`, `ticket-plan.md`, `ticket-drafts.md`, `filing-ledger.md`, `comment-ledger.md`) |
| `eval_results[]` | array | No (omit if `evals.md` wasn't run, e.g. a `report`-mode run on a folder still mid-filing) | `{eval_id, name, result, detail}`, one per eval in `evals.md` |

All other fields (`ts`, `skill`, `version`, `duration_s`, `outcome`, `input_summary`, `context_sources`, `output_summary`, `tool_calls`, `decisions`, `observations`, `verified`) follow the base schema in `agent-architect/references/observability-templates.md` section 2 unchanged. `tool_calls` and `decisions` are optional and, for this skill, usually thin: most of what they'd record is already captured more precisely in `subagents[]`, `gates[]` and `STATUS.md`'s "Decisions made in chat" sections, so only include a `tool_calls` entry for a notable one-off (e.g. a BigQuery fallback) and a `decisions` entry for a scope choice not already in a gate summary.

## 3. Invocation log (`observability/invocation-log.jsonl`)

One compact line per run, appended after Step 6, following the base schema in `agent-architect/references/observability-templates.md` section 1 unchanged: `ts`, `skill`, `input_summary`, `duration_s`, `tool_calls`, `tokens_est`, `outcome`, `notes`, `version`, `eval_results` (compact `{"id":"E9","r":"P"}` form). Set `notes` to the round name and mode (e.g. `"Round 3, mode=run"`) so the trend log is readable without opening a trace.

## 4. Verification subagent

After writing the invocation-log line and the trace file, spawn a fresh subagent (never the orchestrator that ran the round) to verify them, following the pattern in `agent-architect/references/observability-templates.md` section 4, with these checks added for this skill:

1. Every `steps[]` entry in the trace has a matching pair of lines in `run-log.md` (or a single `step_start` with no `step_end`, only for a step still open at the gate where the run stopped, including a parent step whose sub-steps have ended).
2. Every `mcp_errors[]` entry with `recovered: true` has a matching `retry_ok` line in `run-log.md`; every one with `recovered: false` has a matching `stops[]` entry for the same step.
3. `counts` matches a fresh count from the round folder's own files (re-run the count, don't trust the trace's arithmetic).
4. `eval_results` in the trace matches the last `run_evals.py` output for this round.

If all checks pass, set `"verified": true` in the trace file. Report the specific discrepancy otherwise; do not silently fix the trace.

## 5. Failure-stub rule

If a run stops early (a gate left unanswered across sessions, an unrecoverable MCP error, an explicit stop), the orchestrator still appends a final `run-log.md` line (`stop` event, or a `step_end` with `outcome=partial` or `outcome=failure`) before ending the turn. At the next Step 6 opportunity (the next resume, or a manual trace-only pass), compile the trace from whatever `run-log.md` holds; do not wait for a clean finish to write observability data. A trace compiled this way has `"outcome": "partial"` or `"failure"` and an empty or short `eval_results[]`, which is expected and correct, not an error to fix.

## 6. `observability/README.md` content

Copy this into `.claude/skills/provider-draft-failure-modes/observability/README.md`.

```markdown
# Observability: provider-draft-failure-modes

This directory tracks invocation history and run traces for the provider-draft-failure-modes skill. Full observability: an invocation log, one JSON trace per run, and a verification subagent.

## Files

| File | Purpose | Format | Updated |
|------|---------|--------|---------|
| `invocation-log.jsonl` | Append-only log of every run | JSONL (one object per line) | After each run |
| `traces/` | Detailed trace per run, compiled from the round folder's `run-log.md` | JSON (one file per run) | After each run |

## How it works

1. During the run, the orchestrator appends one line per event (step start/end, MCP error, stop, retry, gate presented/answered, subagent, QA round) to `<round-folder>/run-log.md`. See `references/trace-schema.md` section 1 for the line format.
2. At Step 6, the orchestrator compiles `run-log.md` plus `round.json` and the round folder's final counts into a trace file here, and appends one line to `invocation-log.jsonl`.
3. A fresh verification subagent checks the trace against `run-log.md` and a fresh recount, then sets `verified: true` or reports the discrepancy.
4. If a run stops before Step 6, the next resume (or a manual trace-only pass) still compiles a trace from whatever `run-log.md` holds, marked `outcome: "partial"` or `"failure"`.

## Querying

\`\`\`bash
# Eval trend from invocation log
jq 'select(.eval_results[]? | select(.id == "E9" and .r == "F"))' invocation-log.jsonl

# Runs where an MCP error was never recovered or stopped properly (should be none; this is also E16)
jq 'select(.mcp_errors[]? | select(.recovered == false))' traces/*.json

# Failed or partial runs
jq 'select(.outcome != "success")' traces/*.json

# Unverified traces
jq 'select(.verified != true)' traces/*.json
\`\`\`

## Periodic review (every 5 rounds)

1. Scan `invocation-log.jsonl` for rising `partial`/`failure` rates or a recurring eval failure.
2. Read the traces for any `partial` or `failure` run and the `stops[]` reasons inside them.
3. Check `gates[]` across recent traces for a gate that keeps taking long between `presented` and `answered`; that is a sign the gate's summary isn't landing, not that the product owner is slow.
4. Feed findings back into `SKILL.md` and these reference files, not into a one-off workaround for the next round.

## Schema reference

See `references/trace-schema.md` for full field definitions, and `agent-architect/references/observability-templates.md` for the base schema this extends.
```
