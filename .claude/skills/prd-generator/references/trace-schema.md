# Trace Schema

Formats for the run folder, the invocation log line, and the per-run trace written in SKILL.md Step 9.

## Run folder

`<session scratchpad>/prd-generator/YYYY-MM-DD_<slug>/`

| File | Written at |
| --- | --- |
| `intake-transcript.md` | Step 2 (each question's full text plus Danny's verbatim answer) |
| `prototype-captures.md` | Step 1, when a prototype or Figma link is provided |
| `sources/<slug>.md` | Step 1, one per MCP-read input, content as returned |
| `briefs/plan-<A, B, or C>.md`, `briefs/<P, D, or R>-<group>.md`, `briefs/H-fidelity.md` | Step 1, by `scripts/extract_briefs.py` |
| `plan-A.md`, `plan-B.md`, `plan-C.md`, `plan.md` | Step 3 |
| `acceptance-criteria-handoff.md` | Step 3 (appended in Step 7); passed to acceptance-testing-generator in Step 9 |
| `qa-reports/<phase>-round-<n>-<group>.md` | Every QA round, phases P, D, R, and every handoff check round (H0, H1, H2). Judges write their own; `scripts/mechanical_check.py` writes `mechanical`; `scripts/qa_round.py` writes `round-check` and `checksum.txt` |
| `gate-1.md`, `gate-2.md`, `gate-3.md` | At each gate, before proceeding |
| `danny-<point>.md`, `STATUS.md` | Each handoff point (H0, H1, H2): Danny's messages verbatim, then the resume file |
| `trace-compiled.json` | Step 9, by `scripts/compile_trace.py` |
| `pre-revision-<n>.md` | Step 8, before applying the touch list |
| `touch-list-amendments.md` | Step 8, each phase R fix and each cross-reference fix after a deletion |
| `outside-edits.md` | Step 8, when Edit reports the PRD changed on disk; records Danny's keep or revert call per change |

## Invocation log line

One line appended to `.claude/skills/prd-generator/observability/invocation-log.jsonl` per run, with Edit (never Bash). One `eval_results` entry per eval, holding its run-final verdict; per-phase history lives in the trace.

```json
{"ts":"...","skill":"prd-generator","version":"3.0","mode":"create","input_summary":"...","outcome":"success","eval_results":[{"id":"E01","r":"P"}],"notes":"..."}
```

## Trace

Written to `.claude/skills/prd-generator/observability/traces/YYYY-MM-DD_HHMM_<slug>.json`.

```json
{
  "ts": "ISO 8601",
  "skill": "prd-generator",
  "version": "3.0",
  "mode": "create | revise",
  "outcome": "success | partial | failure",
  "input_summary": "One-line description of inputs",
  "context_sources": [{"type": "local | confluence | gdoc | slack | figma | prototype", "path": "...", "purpose": "...", "saved_copy": "<run>/sources/<slug>.md | null", "fetched_at": "ISO 8601 | null"}],
  "output_summary": "PRD path, story count",
  "tool_calls": [{"tool": "...", "target": "...", "purpose": "...", "ok": true}],
  "decisions": [{"decision": "...", "rationale": "...", "step": "..."}],
  "gates": [{"gate": 1, "approved": true, "snapshot": "<run>/gate-1.md", "modifications": "Danny's changes, summarized"}],
  "reviewers": {
    "selected": [{"agent": "pm-exec-reviewer", "reason": "always"}],
    "findings": 0,
    "adopted": {"defect": 0, "addition": 0},
    "declined": 0,
    "deferred": 0,
    "handoff_items": 0
  },
  "eval_results": [{"eval_id": "E01", "name": "...", "phase": "P", "result": "Pass", "detail": null}],
  "qa_loops": {
    "intake":   {"attempts": 1, "rounds": [[]]},
    "plan":     {"attempts": 1, "rounds": [[]], "persistent": []},
    "draft":    {"attempts": 2, "rounds": [["E13", "E34"], []], "persistent": []},
    "revision": {"attempts": 1, "rounds": [[]], "persistent": []},
    "handoff":  {"H0": {"attempts": 1, "rounds": [[]], "persistent": []}}
  },
  "companion_docs": {"offered": ["acceptance-testing-generator"], "accepted": [], "evals_doc_reminder": false},
  "observations": "Surprises, edge cases, struggles"
}
```

## Field notes

- **Compiled fields:** `eval_results`, `qa_loops` (except `intake`), and the log line's `eval_results` come from `<run>/trace-compiled.json`. Copy them unchanged. The parent writes every other field.

- **`eval_results`:** one entry per eval per phase it was active in, holding that phase's final-round verdict. A multi-phase eval like E02 appears up to three times (P, D, R), so `eval_results` can never silently disagree with `qa_loops.rounds`. A verdict from the default-to-Fail-on-ambiguity rule carries `"detail": "ambiguous: <one-line reason>"`.
- **`qa_loops.<phase>.rounds`:** one array per QA round, listing the eval IDs that failed that round (empty array = clean round). `attempts` = `rounds.length`, at most 3 per phase. `persistent` holds the phase's unresolved issues: evals failing in the final round and an earlier round, plus evals failing for the first time in the final round.
- **`qa_loops.intake`:** produced by `<intake_gate>`, not `<qa_loop_protocol>`. `rounds` lists failed row letters (A through L) per round. No `persistent` key and no round cap.
- **`qa_loops.handoff`:** one entry per handoff point (H0, H1, H2) whose E44 check ran. E44's `eval_results` entries carry the point as their `phase`.
- **Omit phases that did not run.** Revise mode usually has no `plan` or `draft` phase.
- **`gates`:** one entry per gate passed. In revise mode, Gate 1 appears only when the change plan went beyond the instructions.
- **v2.2 traces** (runs before 2026-10-13) use `qa_loops` keys `interview`, `spec`, `draft`, `polish` and v2.2 eval IDs. Do not migrate them.
