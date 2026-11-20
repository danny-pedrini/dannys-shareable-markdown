# Trace schema and run artifacts

Formats for everything the skill writes outside the document itself: the run folder in the session scratchpad, the invocation log entry, and the per-run trace. The trace is authored by an independent subagent (see `subagent-briefs.md` §6), never by the orchestrator.

## Run folder

Path: `<session scratchpad>/dashboard-requirements/<slug>/` where `<slug>` is `YYYY-MM-DD_<build-slug>`. The session scratchpad path is given in the system prompt.

| File | Written at | Content |
|---|---|---|
| `intake-transcript.md` | Step 2 | Every question asked and Danny's answer, verbatim, numbered. One block per question: a `### Q<n>` heading, a `**Question:**` line with the full question text as asked, and an `**Answer:**` line (E39) |
| `plan.md` | Step 3 | The plan as presented |
| `gate-1.md` | Gate 1 | The approved plan, plus Danny's modifications, verbatim |
| `gate-2.md` | Gate 2 | The approved metric list: ID, name, tier, definition sketch, provenance. Plus a deltas block: added, cut, retiered, changed against the inventory, with reasons |
| `gate-3.md` | Gate 3 | The consolidated findings table with Danny's decision per row: adopt, decline, defer |
| `gate-4.md` | Gate 4 | The approved touch list: item, section, metric IDs, lines, change. Revise mode writes this at its single gate |
| `pre-revision-<n>.md` | Before each Step 9 apply | Byte copy of the document before edits, for E20 |
| `mcp-ledger.jsonl` | Throughout | One line per MCP call, appended as the call is made |
| `qa-reports/<phase>-round-<n>-<subagent>.md` | Each QA round | Every QA subagent report, saved verbatim by `scripts/save-qa-report.py`, plus the mechanical report from `scripts/mechanical-checks.py` |
| `qa-reports/<phase>-round-<n>-report-check.md` | Each QA round | The round's E42 verdict, kept by `scripts/save-qa-report.py` with a `.json` sidecar |
| `qa-reports/manifest.jsonl` | Each saved report and each logged lens or trace subagent | Agent ID, role, agent type, spawn depth, transcript path, saved path, sha256 (E43, E44) |
| `evals-<phase>-<group>.md` | Each QA phase | The eval slice for one judgment subagent, from `scripts/eval-slice.py` (E41) |
| `trace-skeleton.json` | Step 10 | `tool_calls`, `qa_rounds`, `eval_results`, and E21's result, from `scripts/trace-skeleton.py build` |

### Ledger line

```json
{"ts":"2026-09-10T15:02:11Z","server":"claude_ai_Atlassian","tool":"getConfluencePage","resource":"3071574019","purpose":"PRD","ok":true,"write":false}
```

`write` is always `false` in this skill. A ledger line with `write: true` is a critical failure (E21).

## Invocation log entry

Appended by the orchestrator to `observability/invocation-log.jsonl` at Step 10.

```json
{"ts":"2026-09-10T14:30:00Z","skill":"dashboard-requirements","mode":"create","input_summary":"Galen Phase 1 CTC + EMR 2.0 from Confluence PRD, sizing sheet, 4 syntheses","outcome":"success","version":"1.0","eval_results":[{"id":"E01","r":"P"},{"id":"E12","r":"P"},{"id":"E28","r":"F"}],"notes":"E28 persistent: two guardrail owners unknown"}
```

`eval_results` carries one entry per eval with its run-final verdict. Per-phase history lives in the trace.

## Trace file

Path: `observability/traces/YYYY-MM-DD_HHMM_<slug>.json`.

```json
{
  "ts": "2026-09-10T14:30:00Z",
  "skill": "dashboard-requirements",
  "version": "1.0",
  "mode": "create",
  "outcome": "success",
  "input_summary": "One paragraph: build, inputs provided, mode.",
  "context_sources": [
    {"type": "confluence", "id": "3071574019", "purpose": "PRD", "exists": true},
    {"type": "google_sheet", "id": "1S9x9RBi3YDzW1jEpOHzmbZaS0xbCROUKtYqB5ZYeQAQ", "purpose": "Sizing SOT", "exists": true},
    {"type": "local", "path": "Project-Galen/Phase-1/Phase-1-Metrics-Inventory.md", "purpose": "Prior inventory", "exists": true}
  ],
  "output_summary": "Wrote <path>. 33 metrics: 3 outcomes, 2 hero, 5 reconciling, 7 driver, 6 guardrail. Inventory at <path>, 61 candidates.",
  "tool_calls": [
    {"tool": "mcp__claude_ai_Atlassian__getConfluencePage", "target": "3071574019", "purpose": "PRD", "ok": true, "write": false},
    {"tool": "Write", "target": "<output path>", "purpose": "Draft", "ok": true}
  ],
  "gate_evidence": {
    "plan_approved": {"evidence_found": true, "snapshot": "<run>/gate-1.md", "detail": "Plan names 11 sections, 4 reviewers; Danny added one ad hoc section."},
    "metric_list_approved": {"evidence_found": true, "snapshot": "<run>/gate-2.md", "approved_ids": ["O1", "O2", "A1"], "detail": "All 33 approved IDs appear as rows; no extra rows."},
    "reviewers_spawned": {"evidence_found": true, "agents": ["data-analytics-eng-reviewer", "pm-exec-reviewer"], "detail": "Two reports in qa-reports/."},
    "reviewer_decisions_captured": {"evidence_found": true, "snapshot": "<run>/gate-3.md", "adopt": 6, "decline": 3, "defer": 2},
    "touch_list_approved": {"evidence_found": true, "snapshot": "<run>/gate-4.md", "items": ["A4 wording", "§5 new row"], "detail": "Diff against pre-revision-1.md touches only listed lines."},
    "qa_passed": {"P": true, "I": true, "D": true, "R": false, "detail": "R: E28 persistent."},
    "changelog_updated": {"evidence_found": true, "detail": "Row dated 2026-09-10 names the revision and count 33."}
  },
  "metric_deltas": [
    {"gate": "2", "added": [], "cut": ["Candidate 14 (duplicate of A5)"], "retiered": ["A13 driver from guardrail"], "changed": [], "reason": "Danny's selection"},
    {"gate": "3-4", "added": ["A21"], "cut": [], "retiered": [], "changed": ["A4 definition"], "reason": "Adopted findings 2 and 5"}
  ],
  "qa_rounds": {
    "P": {"attempts": 1, "rounds": [[]], "persistent": []},
    "I": {"attempts": 2, "rounds": [["E09"], []], "persistent": []},
    "D": {"attempts": 2, "rounds": [["E22", "E30"], []], "persistent": []},
    "R": {"attempts": 3, "rounds": [["E28"], ["E28"], ["E28"]], "persistent": ["E28"]}
  },
  "reviewers": [
    {"agent": "data-analytics-eng-reviewer", "must_fix": 2, "should_fix": 3, "consider": 1, "adopted": 4, "declined": 1, "deferred": 1}
  ],
  "eval_results": [
    {"eval_id": "E01", "name": "Plan Section Coverage", "phase": "P", "result": "Pass", "detail": null},
    {"eval_id": "E28", "name": "Guardrail Alarm Line Presence", "phase": "R", "result": "Fail", "detail": "A19, A20 lack an alarm owner"}
  ],
  "decisions": [
    {"decision": "state_progression_paragraph_included", "rationale": "Metrics distinguish member from subscriber", "phase": "6"}
  ],
  "observations": "Auditor's independent assessment: surprises, gaps, where the run struggled.",
  "independently_authored": true
}
```

### Field notes

- `context_sources[].type`: `local`, `confluence`, `google_doc`, `google_sheet`, `slack`, `github`, `figma`, `url`. Local entries carry `path`; the rest carry `id` or `url`. `exists` is the auditor's check, local paths only.
- `tool_calls`: every ledger line, plus notable non-MCP calls (Write, Edit on the output, Agent spawns). Routine reads of skill references are omitted unless they failed.
- `gate_evidence`: one key per gate. `evidence_found` is false when the snapshot is missing, empty, or disagrees with the document. Revise mode has `touch_list_approved` and `qa_passed.R` only, plus `plan_approved` when a change plan was presented.
- `metric_deltas`: one entry per gate that changed the list. IDs refer to the final document; a cut candidate is named by its inventory row.
- `qa_rounds.rounds`: one array per round listing failed eval IDs; `attempts` equals its length; maximum 3. `persistent` holds evals failing in the final round and at least one earlier round, plus evals failing for the first time in the final round.
- `eval_results`: one entry per eval per phase it was active in, recording that phase's final-round verdict. Ambiguous verdicts carry `"detail": "ambiguous: <reason>"`.
- `independently_authored`: always true. A trace without it was written by the orchestrator and should be treated as unverified.

## Queries

```bash
# Runs with any gate lacking evidence
jq 'select(.gate_evidence | to_entries[] | .value.evidence_found == false) | {ts, mode}' traces/*.json

# Failure rate per eval across runs
jq -s '[.[].eval_results[]?] | group_by(.id) | map({id: .[0].id, total: length, failed: [.[] | select(.r == "F")] | length})' invocation-log.jsonl

# Any write-capable MCP call ever recorded
jq 'select(.tool_calls[]? | select(.write == true))' traces/*.json

# Metrics cut at selection, across runs
jq '.metric_deltas[] | select(.gate == "2") | .cut' traces/*.json

# Persistent QA issues by phase
jq '{ts, persistent: [.qa_rounds | to_entries[] | select(.value.persistent | length > 0) | {phase: .key, evals: .value.persistent}]}' traces/*.json
```
