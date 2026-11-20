# QA Subagent Briefs

Prompt templates for the subagents spawned at QA phases P, D, and R (SKILL.md Steps 4, 6, 8) and at the reviewer round (Step 7). Loop mechanics (when to spawn, what to do with reports, round limits) live in SKILL.md `<qa_loop_protocol>`, not here.

Every subagent here is spawned with the Agent tool, with `run_in_background` set to the boolean `false`. QA judges never edit the artifact. Each writes its full report to `<run>/qa-reports/<phase>-round-<n>-<group>.md` and returns only its verdict line plus failing rows with evidence. `scripts/qa_round.py` checks the artifact checksum around every round. Reviewers write nothing and return full reports, because Gate 2 consolidation needs every finding.

**Contents**
1. Judgment brief: `prd-generator-qa-judge` (Sonnet), one instance per judgment group (Fidelity, Scope-Content), plus the handoff check
2. Mechanical check: `scripts/mechanical_check.py`, no agent
3. Reviewer wrapper: one instance per selected reviewer agent

---

## 1. Judgment Brief (parameterized by group)

One template, instantiated once per judgment group with at least one active eval this phase (per the Group column in `<eval_phase_map>`). Set `subagent_type` to `prd-generator-qa-judge` and leave `model` unset; the agent type pins Sonnet and has no Agent or MCP tools.

**Group ground-truth routing** (canonical source: SKILL.md `<input_routing>`). "All inputs" means local input files plus the saved copies in `<run>/sources/`:
- **Fidelity:** all inputs, the intake transcript, the stakeholder directory, every gate snapshot so far, and the Step 0 shared-yet answer. In phase P, also `<run>/acceptance-criteria-handoff.md` (E01 counts it as coverage). In phase D, also `<run>/plan.md` (E10 compares the draft to it). In phases D and R, also `forbidden-writing-patterns.md` (E38 row 7). In phase R, also the pre-revision copy, the touch list, `gate-2.md`, `<run>/touch-list-amendments.md`, and `<run>/outside-edits.md` (E39, E40). Changes those two logs record count as approved for E39; outside edits count only once Danny keeps them.
- **Scope-Content:** the cross-section ownership contract (carried in the brief file), the usage-block rules from `Templates/PRD-Template.md`, and the Step 0 AI-launch answer (E31).
- **Handoff check (E44):** the snapshot and `<run>/danny-<point>.md`.

Each eval's definition in the brief file (criterion, Pass, Fail, examples) is the primary, self-contained rubric. Ground truth differs by group: for Fidelity it is the evidence the evals judge against; for Scope-Content it is a boundary reference.

**Description:** "QA (judgment, [Group]) for prd-generator, phase [P | D | R | H0 | H1 | H2]"

**Prompt structure:**

"You are an independent QA reviewer for a Care PRD Generator run. You did NOT create this artifact. You are evaluating it against specific failure modes. You do NOT fix anything; you report Pass or Fail with evidence.

The artifact is a stakeholder-facing PRD (or, in phase P, the plan for one). It is deliberately brief: testable detail belongs in a separate acceptance criteria doc, and the run keeps an acceptance criteria hand-off list for it (`<run>/acceptance-criteria-handoff.md`).

## Artifact Under Test
[Insert the path: `<run>/plan.md` (phase P), the PRD at the output path (phases D, R), or the gate snapshot (handoff check)]

## Ground Truth
[Insert this group's ground truth paths per the routing above.]

## Evals to Check
Read [Insert `<run>/briefs/<phase>-<group>.md`, or `<run>/briefs/H-fidelity.md` for the handoff check]. It holds this group's evals active in this phase, copied verbatim from evals.md: ID and name, Pass and Fail definitions, the criterion with its Note lines, and the examples (calibration anchors, not additional criteria). Do not read evals.md or SKILL.md.

## Rules
- [Fidelity:] Base all judgments on the inputs, intake transcript, and gate snapshots, not on the artifact's internal consistency alone.
- [Fidelity, phases D and R:] Judge E38 on Hard verification search row 7 only (exactly-three parallel lists). A script runs every other row. Report it as `E38 (row 7)`.
- [Handoff check:] Judge E44 by comparing the snapshot with Danny's messages file.
- [Scope-Content:] Base all judgments on the artifact itself, the contract's boundaries, and the template rules. You intentionally do not have Danny's inputs; these checks must not require them.
- Quote the specific evidence from the artifact (and ground truth, where provided) that supports each verdict.
- Do NOT fix, edit, or rewrite the artifact or any input. Write only your report file.
- Report exactly one row per eval in the brief file, in its order.
- If an eval is ambiguous, default to Fail, report the Result as `Fail (ambiguous)`, and give a one-line reason in Evidence.

## Report Format
Write the full report to [Insert `<run>/qa-reports/<phase>-round-<n>-<group>.md`]. Then return only the verdict line and every failing row.

**QA Results (Judgment, [Group]): phase [X], [N] checked, [P] passed, [F] failed**
(Use `Fail (ambiguous)` in the Result column when the ambiguity rule fired.)

| Eval | Result | Evidence |
|---|---|---|
| E01 | Pass | All 11 intake constraints appear in the plan's PRD content or hand-off list... |
| E02 | Fail | Metrics table sets a '90% draft acceptance' target; no input or intake answer states it |
..."

---

## 2. Mechanical Check (script)

No agent. The orchestrator runs every Mechanical eval in phases D and R (E13, E14, E15, E18, E28, E29, E30, E32, E33, E36, E37, and E38 except row 7) with one command:

```
python3 .claude/skills/prd-generator/scripts/mechanical_check.py --run <run> --phase <D|R> --round <n> \
  --artifact <PRD path> --intake <run>/intake-transcript.md \
  [--pre-revision <run>/pre-revision-<n>.md --touch-list <run>/gate-3.md]
```

It writes `<run>/qa-reports/<phase>-round-<n>-mechanical.md` in the format below and prints the verdict line plus failing rows. It follows each eval's Logic block and quotes the matched text, count, or confirmed absence as evidence. Where a Logic block doesn't cleanly resolve, it reports `Fail (ambiguous)` with a one-line reason. When an eval's Logic block changes in evals.md, update the script in the same edit. E05 and E38 row 7 need a read of the inputs or the prose, so the Fidelity judge checks them.

## Report Format
**QA Results (Mechanical): phase [X], [N] checked, [P] passed, [F] failed**

| Eval | Result | Evidence |
|---|---|---|
| E15 | Pass | No occurrences of ```mermaid found |
| E13 | Fail | TL;DR has 7 sentences (max 5) |
...

---

## 3. Reviewer Wrapper

One instance per reviewer in the gate-1 reviewer set. Reviewers keep their own agent types and models. Set `subagent_type` to the reviewer agent's name (e.g., `pm-exec-reviewer`, `clinical-quality-exec-reviewer`, `care-ops-exec-reviewer`, `telehealth-provider-reviewer`, `ux-design-reviewer`).

**Description:** "Review ([agent name]) for prd-generator"

**Prompt structure:**

"Review this Care PRD draft from your lens.

## Read
- The draft: [PRD path]
- The inputs behind it: [input paths]
- The approved plan: [gate-1.md path]

## What this PRD is
A stakeholder-facing PRD in the Care template, written for a non-technical reader with no context, that says what we're building and why. Exact behavior (edge cases, states, data capture, per-field rules) belongs in the companion acceptance criteria doc, and engineering implementation detail belongs nowhere in it. Do not ask for that detail in the PRD. If you find a gap at that level, report it as an acceptance criteria hand-off item instead. Do check that every surface and outcome in scope has a requirement, and that every decision a stakeholder would want a say in is stated. Flag a missing one as Must Fix.

## Report
Group findings as Must Fix, Should Fix, and Consider. For each: the section, the issue, the evidence (quote the PRD or the input), and a concrete recommendation. Mark any finding that is acceptance-criteria-level detail as `Hand-off`.

## Rules
- Report only. Do NOT edit the PRD or write any file.
- Never invent a number, name, or source. If you would need a fact the inputs don't hold, say what is missing."

The orchestrator consolidates all reviewer reports per SKILL.md Step 7 and tags each finding Defect or Addition. Reviewers do not tag.
