# Observability Templates for Claude Code Skills

Reference file used by agent-architect when generating observability scaffolding for new skills. Contains canonical schemas for invocation logs, JSON trace files, the observability README, and verification subagent instructions.

Observability tracks what happened and why. It records eval results as run metadata (pass/fail counts in the log, per-eval detail in traces) but does not define or execute evals — that responsibility lives in `evals.md` and the eval runner step. Full observability includes external verification via a subagent that confirms log and trace accuracy after each run.

---

## Decision Logic

At the end of the delivery phase, default to **Full** observability. Present it as the recommended default and ask only whether the user wants to opt down:

> "I'll include **Full observability** (invocation log + JSON traces per run + external verification). This is strongly recommended — traces are the foundation for eval-driven improvement. Want to opt down?
> - **Light** → Invocation log only. Enough to spot trends without per-run detail.
> - **None** → Skip observability entirely."

---

## Directory Structure

When observability is enabled for a skill, create this structure:

```
.claude/skills/<skill-name>/
├── SKILL.md
├── references/
└── observability/
    ├── README.md               # Schema docs + how to use
    ├── invocation-log.jsonl    # Append-only, one entry per run
    └── traces/                 # One JSON file per run (queryable with jq)
```

**Light observability** includes only `README.md` + `invocation-log.jsonl`.
**Full observability** includes all three items, `scripts/verify_observability.py` and the verification subagent.

---

## 1. Invocation Log Schema (JSONL)

One JSON object per line, appended after each skill run. Never overwrite — append only.

```json
{"ts":"2026-05-29T14:30:00Z","skill":"prd-generator","input_summary":"Generate PRD from pack queue one-pager","duration_s":180,"tool_calls":12,"tokens_est":45000,"outcome":"success","notes":"","version":"1.0","eval_results":[{"id":"G1","r":"P"},{"id":"G2","r":"P"},{"id":"G3","r":"F"}]}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ts` | ISO 8601 string | Yes | When the run started |
| `skill` | string | Yes | Skill name (matches SKILL.md frontmatter `name:`) |
| `input_summary` | string | Yes | One-line description of what was provided (not the full input) |
| `duration_s` | integer | No | Approximate wall-clock seconds from start to finish |
| `tool_calls` | integer | No | Total tool invocations during the run |
| `tokens_est` | integer | No | Estimated total tokens (input + output). Rough estimate is fine |
| `outcome` | enum | Yes | `"success"` / `"partial"` / `"failure"` |
| `notes` | string | No | Brief note on anything notable about this run |
| `version` | string | Yes | Skill version (from Version History if using iteration support, otherwise `"1.0"`) |
| `eval_results` | array | No | Per-eval results for this run. Omit entirely if no evals configured. Each entry: `{"id":"G1","r":"P"}` where `r` is `"P"` (Pass) or `"F"` (Fail). Compact format — full detail (failure explanations) lives in traces only |

### eval_results Compact Format

The JSONL log uses a compact format to keep lines short while enabling per-eval trend queries:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Eval ID from `evals.md` (e.g., `G1`, `G2`) |
| `r` | enum | `"P"` (Pass) or `"F"` (Fail) |

Full eval detail (failure explanations, eval names) lives in the trace file's `eval_results` array. The JSONL log is the trend layer — use it for "which evals are failing over time?" queries. Open the trace when you need the *why*.

### Querying Eval Trends from the Invocation Log

```bash
# All runs where G1 failed
jq 'select(.eval_results[]? | select(.id == "G1" and .r == "F"))' invocation-log.jsonl

# Failure rate per eval ID
jq -s '[.[].eval_results[]?] | group_by(.id) | map({id: .[0].id, total: length, failed: [.[] | select(.r == "F")] | length})' invocation-log.jsonl

# Runs with any eval failure
jq 'select(.eval_results[]? | select(.r == "F")) | {ts, skill, eval_results}' invocation-log.jsonl
```

### Outcome Definitions

| Value | When to Use |
|-------|-------------|
| `success` | Skill completed its job; output met expectations |
| `partial` | Skill completed but output needed significant manual edits or missed some requirements |
| `failure` | Skill could not complete its job (tool failure, wrong output, abandoned) |

---

## 2. Trace File Schema (JSON)

One JSON file per run, saved to `observability/traces/`. Naming convention: `YYYY-MM-DD_HHMM_<short-slug>.json`

Example filename: `2026-05-29_1430_pack-queue-prd.json`

```json
{
  "ts": "2026-05-29T14:30:00Z",
  "skill": "prd-generator",
  "version": "1.0",
  "duration_s": 180,
  "outcome": "success",
  "input_summary": "Generated PRD from pack queue one-pager. User provided one-pager path and target folder.",
  "context_sources": [
    {"type": "local", "path": "Templates/PRD-Template.md", "purpose": "PRD template"},
    {"type": "local", "path": "Product Strategy/one-pagers/pack-queue.md", "purpose": "Source one-pager"},
    {"type": "local", "path": "Product Strategy/PRDs/carrier-selection-prd.md", "purpose": "Example PRD for style reference"}
  ],
  "output_summary": "Wrote PRD to Product Strategy/PRDs/pack-queue-prd.md. 12 sections, 8 user stories, 3 success metrics with baselines.",
  "tool_calls": [
    {"tool": "Read", "target": "Templates/PRD-Template.md", "purpose": "Load PRD template", "ok": true},
    {"tool": "Read", "target": "Product Strategy/one-pagers/pack-queue.md", "purpose": "Load source one-pager", "ok": true},
    {"tool": "Glob", "target": "Product Strategy/PRDs/*.md", "purpose": "Find example PRDs", "ok": true},
    {"tool": "Write", "target": "Product Strategy/PRDs/pack-queue-prd.md", "purpose": "Write final PRD", "ok": true}
  ],
  "decisions": [
    {"decision": "skip_ui_section", "rationale": "No Figma mock provided — UI section would be speculative.", "phase": "3"},
    {"decision": "flag_baselines_as_tbd", "rationale": "One-pager lacked metric baselines for 2 of 3 success metrics. Flagged rather than fabricated.", "phase": "5"}
  ],
  "eval_results": [
    {"eval_id": "G1", "name": "Source dependency coverage", "result": "Pass", "detail": null},
    {"eval_id": "G2", "name": "Metric baseline presence", "result": "Fail", "detail": "SLA metric missing baseline value"}
  ],
  "observations": "PRD had no Figma mock — skipped UI section. One-pager was sparse on metrics; had to flag 2 of 3 baselines as TBD.",
  "verified": true
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ts` | ISO 8601 string | Yes | When the run started |
| `skill` | string | Yes | Skill name |
| `version` | string | Yes | Skill version |
| `duration_s` | integer | No | Approximate wall-clock seconds |
| `model_type` | string | No | Skill-specific classification tag for the run's model or pattern (e.g., `"direct_fte_elimination"`, `"percentage_of_cost_pool"`). Useful when a skill supports multiple model types and you want to correlate model type with eval outcomes or duration |
| `outcome` | enum | Yes | `"success"` / `"partial"` / `"failure"` |
| `input_summary` | string | Yes | One paragraph describing what was provided (not the full input) |
| `context_sources` | array | Yes | Local files, Google Sheets, URLs, or other sources used as context during the run |
| `context_sources[].type` | string | Yes | Source type: `"local"`, `"google_sheet"`, `"url"`, `"google_doc"` |
| `context_sources[].path` | string | Conditional | File path (for `local` type). Relative to workspace root |
| `context_sources[].id` | string | Conditional | Resource ID (for `google_sheet`, `google_doc` types) |
| `context_sources[].url` | string | Conditional | URL (for `url` type) |
| `context_sources[].purpose` | string | Yes | Why this source was used (one phrase) |
| `output_summary` | string | Yes | 2-3 sentences describing what was produced, including file paths |
| `tool_calls` | array | Yes | Notable tool calls only — skip routine reference reads unless they failed |
| `tool_calls[].tool` | string | Yes | Tool name (e.g., `Read`, `Write`, `Bash`) |
| `tool_calls[].target` | string | Yes | What was read/written/executed |
| `tool_calls[].purpose` | string | Yes | Why this tool call was made (one phrase) |
| `tool_calls[].ok` | boolean | Yes | Whether the call succeeded |
| `decisions` | array | No | Key decisions made during the run — choices that shaped the output beyond default behavior |
| `decisions[].decision` | string | Yes | Short slug for the decision (e.g., `"skip_research"`, `"remove_factor"`) |
| `decisions[].rationale` | string | Yes | Why this decision was made |
| `decisions[].phase` | string | No | Which skill phase the decision occurred in |
| `eval_results` | array | No | Omit entirely if no evals configured. Per-eval Pass/Fail detail |
| `eval_results[].eval_id` | string | Yes | Eval ID from `evals.md` (e.g., `G1`) |
| `eval_results[].name` | string | Yes | Eval name |
| `eval_results[].result` | enum | Yes | `"Pass"` / `"Fail"` |
| `eval_results[].detail` | string | No | Brief explanation for failures; `null` for passes |
| `observations` | string | Yes | Surprises, edge cases, where the skill struggled — most valuable field for refinement |
| `verified` | boolean | No | Set to `true` by verification subagent if all checks pass. Absent or `false` if not verified |

### Querying Traces

JSON traces are queryable with `jq`. Common queries:

```bash
# All failed runs
jq 'select(.outcome == "failure")' traces/*.json

# Runs where a specific eval failed
jq 'select(.eval_results[]? | select(.result == "Fail" and .eval_id == "G1"))' traces/*.json

# Average duration across successful runs
jq -s '[.[] | select(.outcome == "success") | .duration_s] | add / length' traces/*.json

# Runs with unverified observability
jq 'select(.verified != true) | {ts, skill, outcome}' traces/*.json
```

Include only notable tool calls — skip routine reads of skill references unless they failed.

---

## 3. Observability README Template

Placed at `observability/README.md` inside each skill.

```markdown
# Observability: [skill-name]

This directory tracks invocation history and run traces for the [skill-name] skill.

## Files

| File | Purpose | Format | Updated |
|------|---------|--------|---------|
| `invocation-log.jsonl` | Append-only log of every run | JSONL (one object per line) | After each run |
| `traces/` | Detailed trace per run | JSON (one file per run) | After each run (Full only) |

## How It Works

1. The skill auto-appends to these files as its final step
2. A verification subagent confirms log + trace accuracy (Full only)
3. If the skill fails before reaching the logging step, the parent thread writes a failure stub

## Querying

Both the invocation log and traces are queryable with `jq`:

\`\`\`bash
# Eval trend from invocation log (single file, fast)
jq 'select(.eval_results[]? | select(.id == "G1" and .r == "F"))' invocation-log.jsonl

# Failure detail from traces (per-file, when you need the why)
jq 'select(.eval_results[]? | select(.result == "Fail"))' traces/*.json

# Failed runs
jq 'select(.outcome == "failure")' traces/*.json
\`\`\`

## Periodic Review (recommended: every 10 runs or monthly)

1. Scan `invocation-log.jsonl` for patterns — rising `partial`/`failure` rates, increasing duration, recurring eval failures
2. For eval trends: `jq -s '[.[].eval_results[]?] | group_by(.id) | map({id: .[0].id, total: length, failed: [.[] | select(.r == "F")] | length})' invocation-log.jsonl`
3. Read traces for any `partial` or `failure` runs to understand what went wrong
4. Check for unverified runs: `jq 'select(.verified != true)' traces/*.json`
5. Use findings to refine the skill prompt (add constraints, examples, or instructions)

## Schema Reference

See `agent-architect/references/observability-templates.md` for field definitions and format specifications.
```

---

## 4. Self-Logging Steps (Added to Generated Skills)

When observability is enabled, agent-architect adds these as the final steps in the generated skill's workflow.

### For Full Observability

```markdown
### Step [N]: Log Observability

After completing the task, record this run:

1. **Append to invocation log** — Add one JSONL entry to `observability/invocation-log.jsonl`:
   - `ts`: ISO 8601 timestamp of when the run started
   - `skill`: this skill's name
   - `input_summary`: one-line description of what was provided
   - `duration_s`: approximate seconds from start to finish
   - `tool_calls`: count of tool invocations this run
   - `tokens_est`: estimated total tokens — rough estimate is fine (optional)
   - `outcome`: "success" / "partial" / "failure"
   - `notes`: anything notable (leave empty if clean run)
   - `version`: current skill version
   - `eval_results`: per-eval results array using compact format: `[{"id":"G1","r":"P"},{"id":"G2","r":"F"}]` where `r` is `"P"` (Pass) or `"F"` (Fail). Omit entirely if no evals configured

2. **Write trace file** — Create `observability/traces/YYYY-MM-DD_HHMM_<short-slug>.json` following the JSON trace schema in `references/observability-templates.md`. Include all required fields: ts, skill, version, outcome, input_summary, context_sources, output_summary, tool_calls (with purpose field), observations. Include decisions (key choices that shaped the output), and eval_results if evals are configured.

### Step [N+1]: Verify Observability

After logging, run the mechanical checks as a script, then spawn a verification subagent for the judgment check.

1. **Run the script:**
   `python3 [skill-path]/scripts/verify_observability.py --skill-dir [skill-path] --trace [trace-path] --output [output-path]`
   It checks that the log entry exists, `outcome` matches the output on disk, `ts` is within the last 10 minutes, the trace is valid JSON, local `context_sources` paths exist, `output_summary` paths exist, every `tool_calls` entry has a `purpose`, and the trace and log outcomes match. Record its output unchanged; it is the verdict on those checks (agent-architect Step 2.6). If it exits non-zero, surface the failed checks and do not spawn the subagent.
2. **Spawn the verification subagent** only after the script exits 0. Use the Agent tool with:
- **Description:** "Verify observability for [skill-name]"
- **Subagent type:** `local-grader`
- **Prompt:**
  "Verify the judgment part of the observability data for the most recent run of [skill-name]. A script already passed the mechanical checks.

  1. Read the trace file at `[trace-path]` and the output at `[output-path]`.
  2. Confirm the `decisions` array captures the non-default choices made during the run (if any were made). Base this on the output and its notes, not on what the trace claims.
  3. If it does, rewrite the trace file with `\"verified\": true` and no other change.
  4. Report: 'Verified.' or the specific discrepancy found.

  Only modify the trace `verified` field. No other edits."

If the script or the verification subagent reports a discrepancy, surface it to the user: "Observability verification found an issue: [discrepancy]. Want me to fix the log entry?" After a fix, re-run the script and then a fresh verification subagent.

**Script setup:** copy `agent-architect/references/verify_observability.py` into the generated skill's `scripts/` folder.

**Mid-run failure safety:** If the skill fails before reaching this logging step, the parent thread (which invoked the skill) should write a minimal JSONL stub:
```json
{"ts":"...","skill":"...","input_summary":"...","outcome":"failure","notes":"Skill failed before logging step — stub written by parent thread","version":"..."}
```
```

### For Light Observability

```markdown
### Step [N]: Log Invocation

After completing the task, append one JSONL entry to `observability/invocation-log.jsonl`:
- `ts`: current ISO 8601 timestamp
- `skill`: this skill's name
- `input_summary`: one-line description of what was provided
- `outcome`: "success" / "partial" / "failure"
- `version`: current skill version
- `eval_results`: per-eval results array using compact format (omit if no evals configured)
```

Light observability does not include trace files or verification.

---

## 5. Independent Trace Authorship (for Skills with Mandatory Process Gates)

**When to use:** The skill has mandatory human review gates, external tool invocations that must be verified (e.g., a calculator script), or process steps where self-reporting bias is a concern. In standard Full observability, the parent thread writes both the JSONL log and the trace — it grades its own homework. Independent trace authorship fixes this by having the subagent *author* the trace (not just verify it).

**How it works:**

| Step | Who | What |
|------|-----|------|
| Log invocation | Parent thread | Appends JSONL entry (compact, low-stakes — just metadata + eval results) |
| Author trace | Independent subagent | Reads artifacts on disk, audits gate evidence, writes the full trace file |

The parent thread **never writes the trace file**. The subagent starts cold — it didn't execute the skill, has no cognitive momentum, and bases all findings on artifact evidence.

**Gate evidence schema extension:** When a skill has mandatory process gates, the trace file includes a `gate_evidence` object alongside the standard fields:

```json
{
  "ts": "...",
  "skill": "...",
  "version": "...",
  "outcome": "...",
  "input_summary": "...",
  "output_summary": "...",
  "tool_calls": ["..."],
  "eval_results": [{"eval_id": "G1", "name": "...", "result": "Pass", "detail": null}],
  "gate_evidence": {
    "<gate_name>": {
      "evidence_found": true,
      "detail": "What the auditor observed in the artifacts"
    }
  },
  "observations": "Auditor's independent assessment",
  "independently_authored": true
}
```

Each gate gets a key in `gate_evidence` with at minimum `evidence_found` (boolean) and `detail` (string). Skills define additional gate-specific fields based on what can be inspected (e.g., `artifact_exists`, `structure_valid`, `report_consistent`).

**Querying gate evidence across runs:**

```bash
# Runs where any gate lacked evidence
jq 'select(.gate_evidence | to_entries[] | .value.evidence_found == false)' traces/*.json

# Research gate decisions over time
jq '{ts, decision: .gate_evidence.research_gate.decision}' traces/*.json

# All independently authored traces (vs. parent-authored legacy traces)
jq 'select(.independently_authored == true)' traces/*.json
```

**Relationship to evals:** Gate-related evals (run in the eval step) check artifacts directly and produce Pass/Fail. The trace subagent independently checks the same artifacts and records findings in `gate_evidence`. If the eval and the trace disagree, that's a signal to investigate. The eval is the authoritative result; the trace provides independent corroboration.

**Subagent prompt template for independent trace authorship:**

```markdown
### Step [N+1]: Independent Trace Authorship

After logging the invocation, spawn an independent subagent to author the trace file.

Use the Agent tool with:
- **Description:** "Author trace for [skill-name]"
- **Subagent type:** `local-grader` when this brief names only local files; general-purpose when it names an MCP source (agent-architect Step 2.6)
- **Prompt:**

"You are an independent auditor for a [skill-name] run. Your job is to examine artifacts on disk and author the run's trace file. You did NOT execute this skill — you are inspecting evidence after the fact.

## What to Examine

1. **Output:** `[output-file-path]`
2. **Artifacts:** `[artifact-dir]`
3. **Invocation log (last entry):** `[skill-dir]/observability/invocation-log.jsonl`
4. **Eval definitions:** `[skill-dir]/evals.md`

## Context Sources Audit

Reconstruct which files and external resources were used as context during this run. For each source, record:
- `type`: `local`, `google_sheet`, `url`, `google_doc`
- `path`/`id`/`url`: the resource identifier
- `purpose`: why it was used (one phrase)

Verify that local file paths exist on disk. For external resources, record the ID or URL as-is.

## Decisions Audit

Identify key decisions made during the run that shaped the output beyond default behavior. For each:
- `decision`: short slug (e.g., `skip_research`, `remove_factor`)
- `rationale`: why this decision was made
- `phase`: which skill phase it occurred in (if applicable)

Look for evidence of decisions in: the output report (skip notes, assumption rationale), the JSONL entry notes, and the artifact structure (e.g., missing sections that would normally be present).

## Gate Evidence Audit

For each mandatory gate, independently determine whether artifact-level evidence exists:

[List each gate with specific inspection criteria — what files to check, what structure to verify, what report sections to inspect]

## Write the Trace File

Create `[skill-dir]/observability/traces/YYYY-MM-DD_HHMM_<slug>.json` following the trace schema with `context_sources`, `decisions`, and `gate_evidence` fields.

## Rules
- Base ALL findings on what you observe in the files — not on what the JSONL entry claims
- If an artifact is missing, record that — do not infer what it would have contained
- If gate evidence is ambiguous, set evidence_found: false and explain in detail
- Verify local `context_sources` paths exist — flag any that don't
- You MUST NOT modify any file except the trace file you are creating
- Report: 'Trace authored. Context sources: [N]. Decisions: [N]. Gate evidence: [N/M] gates confirmed, [issues if any].'"
```

---

## Deliverables Integration

When observability is enabled, add this section to the skill's Final Output:

```markdown
## Observability

**Level:** Full | Full + Independent Authorship | Light
**Log:** `observability/invocation-log.jsonl`
**Traces:** `observability/traces/` (Full only, JSON format — queryable with `jq`)
**Trace authorship:** [Parent-written with subagent verification | Independently authored by audit subagent]
**Gate evidence:** [Yes — traces include gate_evidence section | N/A — no mandatory gates]

The skill auto-logs after each run. Review periodically (every ~10 runs) to spot trends.
```
