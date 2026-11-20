# Subagent briefs

Prompt-construction templates for every subagent the orchestrator spawns. Loop mechanics live in SKILL.md `<qa_loop_protocol>`; this file holds the prompts. Use the Agent tool with `run_in_background: false`, passed as a boolean. QA, lens, and trace subagents spawn as `subagent_type: dashboard-qa` (`.claude/agents/dashboard-qa.md`: Read, Grep, Glob, and Bash, on Sonnet). Reviewers spawn as their own types. Do not pass `model`.

Contents:
1. Inventory lens subagents (three, parallel)
2. Draft subagent (retired in v1.4)
3. Reviewer wrapper and consolidation format
4. QA judgment brief (parameterized by group)
5. Mechanical checks (a script since v1.5)
6. Trace author brief

Every brief receives file paths, not chat history. The gate snapshots in the run folder are the record of what Danny approved.

---

## 1. Inventory lens subagents

Spawn three in parallel, `subagent_type: dashboard-qa`. After each returns, log it with `python3 scripts/save-qa-report.py --run <run> --agent-id <agentId> --role lens`, so E44 can check its type. Each receives: every input file path (PRD, sizing, syntheses, inventory, prototype, comments), the intake transcript path, the gate-1 plan path, and `references/metric-taxonomy.md`.

**Description:** "Inventory lens [A|B|C] for dashboard-requirements: [Build]"

**Shared prompt body:**

"You are building one lens of an exhaustive metrics inventory for a dashboard requirements document. Your job is breadth: surface every metric that could plausibly belong, so a human can whittle the list later. Do not filter for importance. Do filter for measurability and provenance.

Read, in this order: `references/metric-taxonomy.md`, the gate-1 plan at [path], the intake transcript at [path], then every input at [paths].

For every candidate, output one table row with these columns:
`Candidate | Proposed tier | Definition sketch (numerator / denominator) | Grain | Window | Good | Provenance | Measurability note`

Rules:
- Provenance starts with one of: PRD, sizing, inventory file, comment, synthesis, prototype, explicit recommendation. Then the locator (PRD ID, sheet tab, comment author, file). A recommendation with no source says `explicit recommendation: [one-line reason]`.
- Never invent a number. Definition sketches name populations and arms, not values.
- Never restate a metric that another team already publishes; reference it with its owner.
- Mark a candidate `not measurable at launch` in the note when the data does not exist yet, and say what would make it measurable.
- One row per distinct numerator-and-denominator concept. If two candidates differ only in slice, they are one row.

Your lens:"

**Lens A, Outcomes and reconciling:** "Business outcomes in dollars or retention, and the payable hours that reconcile them; the hero metrics the PRD names; every building block that computes or reconciles a hero; every sizing coefficient and the measured metric that would reconcile to it; the number leadership already reads for this problem."

**Lens B, Drivers and guardrails:** "Patient-side, provider-side, and system-side levers that would explain hero movement; every clinical quality, patient experience, and provider experience signal the build could degrade; latency and reliability signals; retention and cancellation signals; anything the PRD lists as a launch gate."

**Lens C, User behavior and instrumentation:** "What providers and patients do on the new surface: opens, expansions, scrolls, skips, overrides, corrections, time in view. Check the prototype or Figma for what actually exists; do not propose a behavior the UI cannot produce. Note for each whether it lives in Amplitude or the warehouse. Include eval-instrument health where an AI component is scored at runtime."

**Return format:** the table, then a short list of candidates you considered and rejected as unmeasurable or duplicative, with one reason each.

**Merge (orchestrator).** Union the three tables. Collapse rows with the same numerator-and-denominator concept into one, keeping the union of provenance and the fuller definition sketch. Add a `Lens` column recording A, B, C, or a combination. Number rows sequentially. Write to `<OutputDir>/<Build>-Metrics-Inventory.md` with a header stating build, date, sources read, and candidate count. Then run the I-phase QA loop.

---

## 2. Draft subagent

Retired in v1.4. The orchestrator writes the document itself at Step 6; the rules are in `drafting-rules.md`.

---

## 3. Reviewer wrapper and consolidation

Spawn every selected reviewer in parallel using its own `subagent_type` (`data-analytics-eng-reviewer`, `pm-exec-reviewer`, `clinical-quality-exec-reviewer`, `care-ops-exec-reviewer`, `frontend-eng-reviewer`). Each receives the draft path, the PRD path, and the gate-2 snapshot path.

**Selection rules.** Always: data-analytics-eng and pm-exec. Clinical-quality-exec when any guardrail is a patient-safety or care-quality signal (Clinical Quality Score, preventable miss, referral rate, eval pass rate). Care-ops-exec when any metric touches handle time, skips, task routing, or provider pay (decisions-per-hour tiers). Frontend-eng when the build changes what a provider or patient sees, so user-behavior metrics are possible. Record the selection and rationale in the plan (E03, E04).

**Description:** "[reviewer] review of dashboard requirements: [Build]"

**Prompt wrapper:**

"Review the dashboard requirements document at [draft path] for ADS. Context: the PRD at [path]; the approved metric list at [gate-2 path], which the PM has already blessed, so do not propose removing metrics from it without a specific defect. Return Must Fix / Should Fix / Consider per your agent definition. For each finding name the metric IDs or section it affects and give one implementable recommendation. Do not edit any file."

**Consolidation (orchestrator).** One table, deduplicated, every contributing reviewer attributed:

`# | Finding | Reviewer(s) | Severity | Type | Affects | Recommendation`

Severity is Must Fix, Should Fix, or Consider; when reviewers disagree, record the higher severity and note the disagreement. Type is Defect (a wrong denominator, grain, or reference, or a contradiction with a source) or Addition (a new row, rule, note, alarm mechanic, open question, or instrumentation ask).

Present the table in chat. Danny answers per row: adopt, decline, or defer. A delegated adoption covers Defect rows only; Addition rows stay declined unless Danny adopts them by row. Record the answers to `gate-3.md` with the same numbering and who decided each row.

---

## 4. QA judgment brief (parameterized by group)

One instance per judgment subagent the phase spawns, per the phase map in SKILL.md: Fidelity in every phase, Structure in P, and in D and R one merged subagent for every Definitions, Structure, and Presentation eval. `subagent_type: dashboard-qa`.

**Ground truth routing:**

| Group | Receives beyond the artifact |
|---|---|
| Fidelity | Every input path, the intake transcript, and every gate snapshot written so far. For E20 also the pre-revision copy the orchestrator saved to the run folder. |
| Structure (P) | `references/template.md` and the intake transcript, for E04's recorded reviewer decisions |
| Merged (D and R) | `references/metric-taxonomy.md`, including the earned and not-earned calibration lists E37 grades against; `references/template.md`; `gate-1.md`, for E24; `gate-2.md` and the intake transcript, for E16's recorded tier decisions |

Every group also receives its eval slice, `<run>/evals-<phase>-<group>.md`, written by `scripts/eval-slice.py`. The scripts name the groups `Fidelity`, `Structure`, and `merged`.

**Description:** "QA (judgment: [Fidelity | Structure | Merged]) for dashboard-requirements, [Phase]"

**Prompt:**

"You are an independent QA reviewer for a dashboard-requirements run. You did not create this artifact. You evaluate it against specific failure modes and report Pass or Fail with quoted evidence. You fix nothing.

## Artifact under test
[Path: the plan (P), the inventory (I), or the document (D, R)]

## Ground truth
[Per the routing table]

## Evals to check
Read [path to `<run>/evals-<phase>-<group>.md`]. It holds the suite design rules and the full definition of every eval you check this phase, with any recorded examples. Do not read `evals.md`.

## Rules
- [Fidelity] Base every judgment on the inputs and gate snapshots, never on the artifact's internal consistency alone.
- [Structure, Merged] Base every judgment on the artifact and the references you were given. You intentionally do not have the inputs.
- A decision Danny recorded in the intake transcript or a gate snapshot outranks an eval's calibration example or default rule. Never fail the artifact for following one.
- Report a verdict for every eval in the slice, and no others.
- Quote the exact text that supports each verdict. Every row needs its own quoted evidence, Pass rows included. Never collapse rows into a summary row such as "All others Pass".
- If an eval is ambiguous on this artifact, report `Fail (ambiguous)` with a one-line reason.
- Do not edit, fix, or rewrite anything. Create, edit, or delete no file anywhere, including scratch scripts; return the report as text only.

## Report format
Return the report as your final message, with nothing after the table.

**QA Results (Judgment: [Group]): [Phase], [N] checked, [X] passed, [Y] failed**

| Eval | Result | Evidence |
|---|---|---|"

---

## 5. Mechanical checks

A script since v1.5; no subagent. In the same turn the orchestrator launches the judgment subagents, it runs:

`python3 scripts/mechanical-checks.py --phase <phase> --artifact <path> --run <run> --out <run>/qa-reports/<phase>-round-<n>-mechanical.md`

Add `--final` in the run's final QA phase, which adds E21 against the ledger. The script runs every Mechanical eval active in the phase, implementing each evals.md Logic block, and prints the report in this format:

**QA Results (Mechanical): [Phase], [N] checked, [X] passed, [Y] failed**

| Eval | Result | Evidence |
|---|---|---|

When a Logic block does not resolve on the artifact, the script reports `Fail (ambiguous)` and names the judgment subagent to route it to. It also reports `Fail (ambiguous)` when an evals.md Logic block no longer matches the hash it was written against. Update the check and its hash in the same edit as the Logic block.

---

## 6. Trace author brief

Spawned once at Step 10 after the JSONL entry is written and `scripts/trace-skeleton.py build` has written `<run>/trace-skeleton.json`. `subagent_type: dashboard-qa`. It has no Write tool; the skeleton script's merge step writes the trace. Receives: the output path, the inventory path, the run folder path (gate snapshots, intake transcript, plan, ledger, pre-revision copy, trace skeleton), `evals.md`, `references/trace-schema.md`, the invocation log path, and the compiled QA reports the orchestrator saved to `<run>/qa-reports/`. After it returns, log it with `python3 scripts/save-qa-report.py --run <run> --agent-id <agentId> --role trace`. If the script reports a type other than `dashboard-qa`, say so in the delivery.

**Description:** "Author trace for dashboard-requirements: [Build]"

**Prompt:**

"You are an independent auditor for a dashboard-requirements run. You did not execute the skill. You examine artifacts on disk and author the run's trace file. Base every finding on what the files show, not on what the invocation log claims.

## Examine
1. Output document: [path]. Inventory: [path].
2. Run folder: [path]. Contains intake-transcript.md, plan.md, gate-1.md through gate-4.md as applicable, mcp-ledger.jsonl, pre-revision copies, qa-reports/, trace-skeleton.json.
3. Last line of the invocation log: [path].
4. Eval definitions: `evals.md`. Trace schema: `references/trace-schema.md`.

## Audit
- **Context sources:** list every file and MCP resource used, from the ledger and the plan. Verify local paths exist.
- **Tool calls:** the skeleton's `tool_calls` holds every ledger entry, and its `_e21` holds E21's Logic result on the ledger. Check both against the ledger. Flag any entry with `write` not false or a tool name that carries a write verb. Put notable Write, Edit, and Agent calls in `tool_calls_extra`.
- **Gate evidence:** for each gate, confirm the snapshot exists, is non-empty, and matches the document (approved IDs appear as rows; declined findings are absent; touch-list items are the only changed lines against the pre-revision copy). Record `evidence_found`, the snapshot path, and detail. Embed the approved ID list and the touch list.
- **Metric deltas:** from gate-2 (inventory to approved list) and gate-3 and gate-4 (revision), list added, cut, retiered, and changed IDs with one-line reasons.
- **QA rounds:** the skeleton's `qa_rounds` holds rounds run, failed eval IDs per round, and persistent flags per phase. Check them against qa-reports/.
- **Reviewers:** per reviewer, counts of Must Fix, Should Fix, Consider, and adopt, decline, defer.
- **Eval results:** the skeleton's `eval_results` holds each eval's final-round verdict per phase. Check them against qa-reports/.
- **Report saves (E43):** run `python3 [skill-dir]/scripts/save-qa-report.py --verify --run [run folder]`. Record its verdict as an E43 entry in `eval_results_extra`, phase `"trace"`.
- **Decisions:** non-default choices visible in the plan, the intake transcript, or the document (ad hoc sections, omitted optional paragraphs, TBDs written instead of values).

## Write
Pipe the judgment fields as one JSON object to `python3 [skill-dir]/scripts/trace-skeleton.py merge --skeleton [run folder]/trace-skeleton.json --out [run folder]/trace.json`. The object carries ts, version, mode, outcome, input_summary, context_sources, output_summary, gate_evidence, metric_deltas, reviewers, decisions, observations, and the two `_extra` lists. The script adds the skeleton fields and `independently_authored: true`. If a skeleton field is wrong, include the corrected field in the object and explain the correction in observations.

## Rules
- If an artifact is missing, record that. Do not infer its contents.
- If gate evidence is ambiguous, set `evidence_found: false` and explain.
- Modify no file other than the trace the merge step writes. Run no other command that writes.
- Report: 'Trace authored. Context sources: N. Gate evidence: N of M confirmed. Metric deltas: N. Flags: [list or none].'"
