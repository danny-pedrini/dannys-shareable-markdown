# QA Subagent Pattern for Generated Skills

Reference file used by agent-architect when designing agents/skills that include independent QA via subagents. Contains the reusable pattern: when to include QA, how to brief the subagent, fix scope and boundary (for the orchestrator), and integration steps.

---

## When to Include QA Subagents

During Phase 2 (Design), evaluate whether the agent being built needs a QA subagent:

| Signal | Include QA? | Rationale |
|---|---|---|
| Critical/compliance/patient-facing output | **Yes** | Errors costly; independent check worth the latency |
| >3 failure modes identified in Phase 1 D4 | **Yes** | Too many failure modes for reliable self-check |
| Output consumed by another system (not human) | **Yes** | No human in the loop to catch issues |
| Output modifies external state (creates files, posts messages, updates records) | **Yes** | Hard to reverse; catch before commit |
| Simple skill (Fast Path) | **No** | Mini-eval sufficient |
| Human reviews output before action | **Optional** | Human provides the independent check |

**Always communicate the QA decision to the user:**
> "This agent [will / will not] include a QA subagent step. [Reason]. Want to change this?"

---

## Design Principles

### 1. Full Artifact Access, No Edit Authority

The orchestrating agent writes; the QA subagent grades (agent-architect Step 2.6). The QA subagent reads the output artifact from disk, so it gets the complete content, but it never changes it:

- **Reads:** Full output file(s) via `Read`, plus the sources the output claims to rest on
- **Writes:** Only its own report, plus saved source reads in the first round (below)
- **Cannot:** Edit or rewrite the artifact it grades

**Saved source reads.** The first-round grader saves its full read of each external source to `[run-folder]/source-reads/<source-id>.md`, with the read time on the first line. A fix-round grader reads that file instead of reopening the source. It reopens the source only for a missing field, a disputed verdict, or a saved read older than the artifact's last source fetch. It still re-grades the full artifact. Do not use saved reads for dedup QA, blind re-extraction, second opinions, or any check whose brief requires an independent reread.

### 2. Fix Scope and Boundary

Every QA step in a generated skill defines both, for the orchestrator:

**Fix Scope** (what the orchestrator MAY fix on its own from a QA finding):
- Tied directly to failure modes from Phase 1 D4
- Specific, enumerated categories of edits

**Fix Boundary** (what goes to the user instead):
- Architecture decisions from Phase 2
- User-confirmed requirements from Phase 1
- Overall structure, tone, or voice
- Anything outside the declared failure modes

### 3. Report, Then the Orchestrator Fixes

The QA subagent evaluates every failure mode and reports each failure with its location and a recommended fix. The orchestrator applies the fixes within scope, escalates the rest, then spawns a fresh QA subagent to grade again (max 2 fix rounds). A fresh subagent matters: one that has seen its own earlier findings tends to confirm them.

---

## Prompt Template

Use this when generating the QA subagent step for a skill:

```markdown
### Step [N]: Independent QA

After completing the main output, spawn a QA subagent for independent verification.

Use the Agent tool with:
- **Description:** "QA for [skill-name]"
- **Subagent type:** `local-grader` when this brief names only local files; general-purpose when it names an MCP source (agent-architect Step 2.6)
- **Prompt:**

"You are an independent QA reviewer for a [skill-name] output. Your job is to grade the output against specific failure modes and report. You do not edit the output.

## What to Review

Read the output at `[output-file-path]`.

## Requirements Summary

[Key requirements from Phase 1 or the skill's task definition]

## Failure Modes to Check

For each, determine Pass or Fail:

| # | Failure Mode | Pass Definition | Fail Definition |
|---|---|---|---|
| FM1 | [name] | [what passing looks like] | [what failing looks like] |
| FM2 | [name] | [what passing looks like] | [what failing looks like] |

## Fix Scope (the orchestrator may fix these without asking)

- [Category 1]: [what kinds of edits are allowed]
- [Category 2]: [what kinds of edits are allowed]

## Fix Boundary (these go to the user)

- [Protected element 1]
- [Protected element 2]
- Overall structure, architecture, and voice

## Your Workflow

1. Read the output file completely
2. Evaluate each failure mode → Pass or Fail
3. For each Fail, record the location, what is wrong, the fix you recommend, and whether the fix falls within fix scope
4. Do not edit any file except your report. In round 1, also save each external source you read to `[run-folder]/source-reads/<source-id>.md`, read time on line 1. In later rounds, read those files instead of the source. Reopen the source only when a needed field is missing, a verdict is disputed, or a saved read predates the artifact's last source fetch.
5. Return your report in this exact format:

**QA Results: [N] checked, [X] passed, [Y] failed ([A] within fix scope, [B] escalated)**

| FM | Result | Location | Finding | Recommended fix | In fix scope? |
|---|---|---|---|---|---|
| FM1 | Pass | n/a | n/a | n/a | n/a |
| FM2 | Fail | Line 47 | [what is wrong] | [the edit to make] | Yes |
| FM3 | Fail | Section 2 | [what is wrong] | [why this needs a user decision] | No |

If all failure modes pass, report: 'QA passed — no issues found.'"
```

After the report, the orchestrator:
1. Applies every finding within fix scope with targeted edits.
2. Surfaces escalations to the user: "QA found [N] issue(s) that need your input: [list]. Want me to resolve these?"
3. Spawns a fresh QA subagent to grade the fixed output (max 2 fix rounds). It re-runs every failure mode, including ones that passed. Its brief names the saved source reads from round 1 (Design Principle 1), unless that check requires an independent reread. A finding still open after that goes to the user as unresolved.
4. Summarizes the fixes it made: "QA flagged [N] issue(s); I fixed [list]. Review the output to confirm."

---

## For agent-architect's Own Workflow

When agent-architect builds a prompt (Phase 3), it uses QA in Phase 4:

```
Phase 3: DRAFT → writes prompt to deliverable
  ↓
Phase 4a: Self-Evaluate (binary checklist — quick pass)
  ↓
Phase 4b: QA Subagent (independent check of the drafted prompt)
  - Checks: failure mode coverage, decomposition adherence, constraint specificity,
    example quality, tool spec completeness, token efficiency
  - Reports: missing constraints, example/output-format mismatches,
    missing tool failure handling, each with a recommended fix
  - Escalates: architecture changes, missing requirements, ambiguous user intent
  ↓
Phase 4c: Review QA results
  - Findings within fix scope: apply them yourself
  - Escalations: resolve or ask user
  - After any change → re-run 4b with a fresh subagent (max 2 iterations)
  ↓
Phase 5: DELIVER
```

---

## Deliverables Integration

When QA is included in a generated skill, add this section to the Final Output:

```markdown
## QA

**Type:** Independent subagent
**Trigger:** Automatic after main output
**Corrective:** No. It reports findings; the orchestrator fixes them and re-runs QA with a fresh subagent.
**Failure modes checked:** [N] (listed in skill prompt)

The QA subagent runs after the main output and before evals. It checks each declared failure mode and reports. The orchestrator fixes what falls within fix scope and escalates the rest.
```
