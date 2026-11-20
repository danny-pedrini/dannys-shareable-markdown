# Evals: dashboard-requirements

## Active Evals

Phases: **P** plan (Step 3), **I** inventory (Step 4), **D** draft (Step 7), **R** revision (Step 9; re-runs every D eval as a regression gate). E21 runs in the final QA phase of the run against the MCP ledger. Groups name the QA subagent that checks the eval: Fidelity, Definitions, Structure, Presentation (judgment, full tier) or Mechanical (code, run by `scripts/mechanical-checks.py`). In D and R, one merged subagent checks the Definitions, Structure, and Presentation evals. Report check evals run in `scripts/save-qa-report.py` as each report is saved. Trace author evals run in the Step 10 trace author.

| ID | Name | Phase Checked | Group | Type | Check | Added | Last Result |
|----|------|---------------|-------|------|-------|-------|-------------|
| E01 | Plan Section Coverage | P | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E02 | Plan No Build-Spec Terms | P | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E03 | Plan Mandatory Reviewer Presence | P | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E04 | Plan Conditional Reviewer Fit | P | Structure | Generalization | Judge | 2026-09-10 | not run |
| E05 | Plan Fidelity to Intake | P | Fidelity | Generalization | Judge | 2026-09-10 | not run |
| E06 | Plan Metric Provenance | P | Fidelity | Generalization | Judge | 2026-09-10 | not run |
| E07 | Inventory Candidate Field Completeness | I | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E08 | Inventory Provenance Tag Format | I | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E09 | Inventory Completeness vs Source | I | Fidelity | Generalization | Judge | 2026-09-10 | not run |
| E10 | Inventory Provenance Validity | I | Fidelity | Generalization | Judge | 2026-09-10 | not run |
| E11 | Inventory Deduplication | I | Fidelity | Generalization | Judge | 2026-09-10 | not run |
| E12 | Invented Number | D, R | Fidelity | Generalization | Judge | 2026-09-10 | not run |
| E13 | Bounded Denominator | D, R | Definitions | Generalization | Judge | 2026-09-10 | not run |
| E14 | Non-Tautological Ratio | D, R | Definitions | Generalization | Judge | 2026-09-10 | not run |
| E15 | Grain Correctness | D, R | Definitions | Generalization | Judge | 2026-09-10 | not run |
| E16 | Tier Placement | D, R | Definitions | Generalization | Judge | 2026-09-10 | not run |
| E17 | Build-Spec Leakage | D, R | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E18 | Coefficient Conflation | D, R | Definitions | Generalization | Judge | 2026-09-10 | not run |
| E19 | Unapproved Adoption | D, R | Fidelity | Generalization | Judge | 2026-09-10 | not run |
| E20 | Surgical Revision | R | Fidelity | Generalization | Judge | 2026-09-10 | not run |
| E21 | External Write Audit | D or R (final phase) | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E22 | Writing-Pattern Violation | D, R | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E23 | Required-Section Presence and Order | D, R | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E24 | Unjustified Extra Section | D, R | Structure | Generalization | Judge | 2026-09-10 | not run |
| E25 | Cross-Section Redundancy | D, R | Structure | Generalization | Judge | 2026-09-10 | not run |
| E26 | Over-Long Prose | D, R | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E27 | Prose Carrying Tabular Content | D, R | Structure | Generalization | Judge | 2026-09-10 | not run |
| E28 | Guardrail Alarm Line Presence | D, R | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E29 | Baseline and Target Column Placement | D, R | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E30 | Summary Metric Count Consistency | D, R | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E31 | ID Sequencing | D, R | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E32 | Cross-Reference Validity | D, R | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E33 | Dangling Ownership | D, R | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E34 | Fabricated Name | D, R | Fidelity | Generalization | Judge | 2026-09-10 | not run |
| E35 | Summary Field Bloat | D, R | Mechanical | Generalization | Code | 2026-09-10 | not run |
| E36 | Dropped Approval | D, R | Fidelity | Generalization | Judge | 2026-09-10 | not run |
| E37 | Under-Table Note Justification | D, R | Presentation | Generalization | Judge | 2026-09-10 | not run |
| E38 | Complement Split Across Rows | D, R | Definitions | Generalization | Judge | 2026-09-29 | not run |
| E39 | Intake Transcript Question Text | P | Mechanical | Generalization | Code | 2026-09-29 | not run |
| E40 | Slice-Rule Contradiction | D, R | Structure | Generalization | Judge | 2026-10-28 | not run |
| E41 | Eval Slice Fidelity | P, I, D, R | Mechanical | Generalization | Code | 2026-11-06 | not run |
| E42 | Report Evidence Completeness | P, I, D, R | Report check | Generalization | Code | 2026-11-06 | not run |
| E43 | Verbatim Report Save | Step 10 | Trace author | Generalization | Code | 2026-11-06 | not run |
| E44 | QA Agent Type and Depth | P, I, D, R | Mechanical | Generalization | Code | 2026-11-06 | not run |

**Suite design rules:** one eval = one failure mode (one remediation action type on one inspection target). A single row may co-fail two evals that test orthogonal properties (a denominator that is both unbounded, E13, and tautological, E14). Examples in each definition are calibration anchors, not additional criteria. Examples marked "none yet" are filled from real runs, never invented. Ambiguous verdicts are reported as `Fail (ambiguous)` and are rubric feedback: when the same eval logs ambiguity across runs, tighten its definitions here. A recorded intake answer or gate decision in the run under test outranks any eval's calibration example or default rule; a judge that sees one never fails the artifact for following it.

**Source for the suite:** evals-advisor, design-time mode, 2026-09-10, against the design's failure modes FM01 to FM23. Splits applied at adoption: FM02 into E13 and E14, FM11 into E23 and E24, FM13 into E26 and E27, FM16 into E30, E31, E32.

**Post-run update, 2026-09-29 (evals-advisor, Provider Drafts run compared against Danny's Confluence edit):** E38 added. E17's pattern tightened after it missed event field lists written in prose. E12, E16, and E35 realigned with prompt fixes to the citation rule, the tier model, and the Summary fields. Second pass the same day: E21's verb match made whole-word, E26 and E37 aligned on bold-lead counting, and E39 added for transcripts saved without question text.

**Post-run update, 2026-10-28 (evals-advisor, December Provider Pay Model run; Danny adopted these changes):** E36 now compares clauses inside kept rows, not just IDs and tiers. E04 and E16 honor recorded owner decisions, and the suite rule above makes that general. E23's Logic normalizes the title placeholder. E25 and E27 get their first calibration examples. E40 added for guardrails that imply a slice §3 excludes. Not adopted: an unset-parameter-to-§5 eval. Held for a second occurrence: source-term redefinition at cutover, and targets that rely on a driver the metric's construction excludes.

**Token-efficiency update, 2026-11-06 (plan at `AI-Learning/Claude-Code-and-Skills/Token-Spend/skill-plans/dashboard-requirements.md`):** E41 to E44 added. They guard four changes: eval slices in place of the full file, one merged judgment subagent in D and R, reports saved by script, and a tool-restricted QA agent type. Mechanical checks now run as a script; every Code eval and its Logic block is unchanged.

## Definitions

### E01: Plan Section Coverage

**Pass:** The plan names every canonical template section at least once.
**Fail:** Any canonical section name is absent from the plan.
**Check type:** Code

```check
Type: presence
Source field: references/template.md canonical header sequence (single-build set; add B and C when the plan declares multi-build)
Target field: plan.md in the run folder
Logic: For each canonical section label (Summary, Stakeholders, Informed, Build, rollout, and arm assignment, Exposure and population, Business outcomes, Hero metrics, Reconciling metrics, Driver metrics, Guardrail metrics, Slices, Next steps for ADS, Open questions, Change log), grep -i the plan file for the label. FAIL if any label has zero matches.
```

**Source:** Design-phase failure mode FM11a, early check
**Added:** 2026-09-10

---

### E02: Plan No Build-Spec Terms

**Pass:** The plan contains no SQL, LookML, or tile-layout content.
**Fail:** Any build-spec pattern appears.
**Check type:** Code

```check
Type: absence
Source field: N/A
Target field: plan.md, excluding any line that contains "not a Looker build spec" or "What this is not"
Logic: grep -nE '```(sql|lookml)|^\s*(SELECT|WITH)\b.*\bFROM\b|^\s*(dimension|measure|explore|view):\s' plan.md. Any match = FAIL.
```

**Source:** FM05, early check
**Added:** 2026-09-10

---

### E03: Plan Mandatory Reviewer Presence

**Pass:** The plan's reviewer set names `data-analytics-eng-reviewer` and `pm-exec-reviewer`, each with rationale text on the same line or bullet.
**Fail:** Either mandatory reviewer is missing or named without rationale.
**Check type:** Code

```check
Type: presence
Source field: SKILL.md Step 8 selection rules
Target field: plan.md reviewer section
Logic: grep -n 'data-analytics-eng-reviewer' and grep -n 'pm-exec-reviewer'. For each hit, strip the agent name and any list marker; FAIL if the remainder is whitespace only. FAIL if either grep returns nothing.
```

**Source:** Intake decision Q28
**Added:** 2026-09-10

---

### E04: Plan Conditional Reviewer Fit

**Pass:** Each conditional reviewer is present if and only if its trigger holds: clinical-quality-exec when a guardrail is a patient-safety or care-quality signal; care-ops-exec when any metric touches handle time, skips, task routing, or provider pay (decisions-per-hour tiers); frontend-eng when the build changes what a provider or patient sees. A presence or absence that Danny decided explicitly, recorded in the plan with its intake or gate source, also passes.
**Fail:** A conditional reviewer is present without its trigger, or a trigger holds and the reviewer is absent, and no recorded decision by Danny explains it.
**Check type:** LLM judge

```judge
Criterion: Does the plan's conditional reviewer selection match the trigger rules given what the build does, per the PRD and the plan, or a decision Danny recorded?
Pass definition: Every conditional reviewer's presence or absence is consistent with whether its trigger condition holds for this build, or the plan records Danny's explicit decision on it with its intake or gate source, confirmed in the intake transcript.
Fail definition: At least one conditional reviewer is included without its trigger, or omitted while its trigger holds, with no recorded decision by Danny.
Examples: Pass, from the December Provider Pay Model run: Danny omitted clinical-quality-exec and frontend-eng although both triggers held (intake: "Don't need the clinical quality exec. Don't need the front end eng either"), and the plan recorded it. The original wording failed all three P rounds on that decision.
```

**Source:** Intake decision Q28
**Added:** 2026-09-10
**Revised:** 2026-10-28. Recorded owner decisions pass.

---

### E05: Plan Fidelity to Intake

**Pass:** Every decision the plan states (build summary, exposure rules, candidate heroes, outcome chain, exclusions) traces to an intake answer, the PRD, or another logged input.
**Fail:** The plan states a decision that contradicts or is absent from the intake transcript and inputs.
**Check type:** LLM judge

```judge
Criterion: Does every substantive claim in the plan trace to the intake transcript or a logged input?
Pass definition: Each plan statement matches, or is a reasonable synthesis of, intake answers and read inputs.
Fail definition: At least one plan statement contradicts an intake answer or introduces a decision no input supports.
Examples: none yet
```

**Source:** FM07, early check
**Added:** 2026-09-10

---

### E06: Plan Metric Provenance

**Pass:** Every candidate metric named in the plan has a stated source: PRD, sizing, or an intake answer.
**Fail:** A candidate metric appears in the plan with no source.
**Check type:** LLM judge

```judge
Criterion: Does every metric candidate in the plan carry a provenance the inputs support?
Pass definition: Each named candidate ties to the PRD, the sizing sheet, or an intake answer.
Fail definition: At least one candidate appears with no source Danny or the inputs provided.
Examples: none yet
```

**Source:** FM01, early check
**Added:** 2026-09-10

---

### E07: Inventory Candidate Field Completeness

**Pass:** Every inventory row has non-empty Proposed tier, Definition sketch, Grain, Window, Good, and Provenance cells.
**Fail:** Any row has an empty required cell.
**Check type:** Code

```check
Type: presence
Source field: N/A
Target field: <Build>-Metrics-Inventory.md table rows
Logic: For each row starting with "| <digit>", split on "|", trim cells. Columns 3 (tier), 4 (definition sketch), 5 (grain), 6 (window), 7 (good), 8 (provenance) must be non-empty. FAIL on any empty cell; quote the row number.
```

**Source:** Step 4 output contract
**Added:** 2026-09-10

---

### E08: Inventory Provenance Tag Format

**Pass:** Every Provenance cell starts with one of: PRD, sizing, inventory file, comment, synthesis, prototype, explicit recommendation.
**Fail:** A Provenance cell starts with anything else.
**Check type:** Code

```check
Type: pattern
Source field: allowed provenance set (FM23)
Target field: inventory Provenance column
Logic: For each row, extract the Provenance cell; match case-insensitive ^(PRD|sizing|inventory file|comment|synthesis|prototype|explicit recommendation)\b. FAIL on no match; quote the cell.
```

**Source:** FM23, format precursor
**Added:** 2026-09-10

---

### E09: Inventory Completeness vs Source

**Pass:** Every PRD success metric, PRD launch-gate metric, and sizing-sheet driver has at least one inventory candidate.
**Fail:** Any of those has no candidate anywhere in the inventory.
**Check type:** LLM judge

```judge
Criterion: Cross-checking the PRD's success metrics, launch gates, and the sizing sheet's named drivers against the inventory, does every item have a candidate?
Pass definition: Every PRD success metric, launch-gate metric, and sizing driver is addressed by at least one inventory row.
Fail definition: At least one is missing; name it.
Examples: none yet
```

**Source:** FM22
**Added:** 2026-09-10

---

### E10: Inventory Provenance Validity

**Pass:** Every candidate's provenance names a source that actually contains or supports the candidate.
**Fail:** A provenance tag names a source that does not contain or support the candidate.
**Check type:** LLM judge

```judge
Criterion: For each candidate, does the source its Provenance names actually contain or support it?
Pass definition: Spot-checking every candidate against its cited source, the candidate or a clear basis for it is present there.
Fail definition: At least one candidate is misattributed or fabricated; name it and the cited source.
Examples: none yet
```

**Source:** FM23
**Added:** 2026-09-10

---

### E11: Inventory Deduplication

**Pass:** No two inventory rows describe the same numerator-and-denominator concept.
**Fail:** Two or more rows are the same metric under different wording.
**Check type:** LLM judge

```judge
Criterion: After the three-lens merge, does the inventory contain duplicate candidates?
Pass definition: Every row is a distinct metric concept; rows differing only in slice were collapsed.
Fail definition: At least two rows describe the same underlying metric; name both.
Examples: none yet
```

**Source:** Step 4 merge contract
**Added:** 2026-09-10

---

### E12: Invented Number

**Pass:** Every rate, count, dollar figure, sample size, ramp percentage, duration, and conversion factor in the document traces to an input or an intake answer, or is tagged `[TBD: owner]`.
**Fail:** Any such figure has no traceable source and no tag.
**Check type:** LLM judge

```judge
Criterion: Does every numeric figure in the document trace to a source in the inputs or the intake transcript?
Pass definition: Each figure matches a value in the PRD, sizing sheet, intake answers, or another logged input, or is tagged [TBD: named owner]. Judge traceability against the inputs and run folder; the document itself cites only openable sources as links (metric-taxonomy.md § Citations), so a figure from an intake answer needs no inline citation.
Fail definition: At least one figure appears with no traceable source and no tag; quote it.
Examples: none yet
```

**Source:** FM01
**Added:** 2026-09-10
**Revised:** 2026-09-29. Dropped the inline-source requirement, which pushed intake and gate numbers into the document.

---

### E13: Bounded Denominator

**Pass:** Every metric's denominator is bounded to a named population, either the §2 eligible population or a tighter set named in the cell.
**Fail:** A denominator has no named bound.
**Check type:** LLM judge

```judge
Criterion: Is every denominator scoped to a specific, named population?
Pass definition: Each Definition cell names the population its denominator rests on, or the cell is a formula over other IDs.
Fail definition: At least one denominator is unbounded ("all tasks", "members") with no population named in the cell or in §2; quote it.
Examples: Pass: "all clinician tasks, fleet-wide across all categories and brands". Fail: "÷ all tasks".
```

**Source:** FM02a
**Added:** 2026-09-10

---

### E14: Non-Tautological Ratio

**Pass:** No numerator-and-denominator pair is defined so the ratio is fixed by construction.
**Fail:** A ratio is constant or near-constant by definition.
**Check type:** LLM judge

```judge
Criterion: Can each ratio's numerator vary independently of the denominator's construction?
Pass definition: For every ratio, the numerator is a genuine subset whose size the build or the population can change.
Fail definition: At least one ratio is fixed by its own definition (the numerator restates the denominator's filter); quote it.
Examples: Fail, from the Galen run: an app-reachable share whose numerator and denominator were both already filtered to app submitters, fixed before the gross-eligible population was defined.
```

**Source:** FM02b
**Added:** 2026-09-10

---

### E15: Grain Correctness

**Pass:** Every metric's Grain names a unit that instantiates for both numerator and denominator.
**Fail:** A Grain names a unit that never instantiates for one side of the ratio.
**Check type:** LLM judge

```judge
Criterion: Can the stated Grain be counted for this metric as defined?
Pass definition: The Grain unit exists as a row or event for both sides of the ratio.
Fail definition: The Grain unit never instantiates for one side; the standing example is task grain for a prevented task.
Examples: Fail, from the Galen run: a deflection rate first written at task grain; a prevented task has no row, so the grain is the submission.
```

**Source:** FM03
**Added:** 2026-09-10

---

### E16: Tier Placement

**Pass:** Every metric sits in the tier its role fits, per `references/metric-taxonomy.md`.
**Fail:** A metric's role, as its own definition and notes describe it, does not match its tier.
**Check type:** LLM judge

```judge
Criterion: Does each metric's tier match its function per the taxonomy tests?
Pass definition: Business outcomes are lagging company outcomes in dollars or retention. Hero metrics are the leading indicators that decide success and gate the ramp; reconciling metrics compute or reconcile a hero; drivers explain movement; guardrails bound harm. Each row's placement matches. A second role named in an under-table note is not a misplacement. A tier that gate-2 or an intake answer set explicitly is not a misplacement, even where the example below placed a similar metric elsewhere.
Fail definition: At least one row's described role belongs to a different tier, and no gate-2 entry or intake answer set that tier; name the row and the tier it belongs in.
Examples: Fail, from the Provider Drafts run: retention (expose-to-cancel) placed as a hero; Danny moved it to Business outcomes because only CIS and AHT gate the ramp. Pass, from the December Provider Pay Model run: provider retention (A10) as a guardrail, because Danny set that tier at intake ("These are both guardrails"); a D-round judge flagged it as ambiguous on the Provider Drafts example.
```

**Source:** FM04
**Added:** 2026-09-10
**Revised:** 2026-09-29. Business outcomes widened to retention; hero defined as ramp-gating. 2026-10-28: recorded tier decisions pass; the Definitions group now receives gate-2 and the intake transcript.

---

### E17: Build-Spec Leakage

**Pass:** The document contains no SQL, LookML, event or field schema, tile layout, Looker explore content, or client event field list written in prose.
**Fail:** Any such content appears outside the "What this is not" boilerplate.
**Check type:** Code

```check
Type: absence
Source field: N/A
Target field: full document, excluding the Summary line that begins "**What this is not:**" and the bullets under it, up to the next bold label
Logic: grep -niE '```(sql|lookml)|^\s*(SELECT|WITH)\b.*\bFROM\b|^\s*(dimension|measure|explore|view):\s|\bLookML\b|Looker explore|tile layout|event_name|\bschema\b|client events?\b|\bevents?\b[^.|]*\bcarr(y|ies|ying)\b' on every line except the excluded lines. Any match = FAIL; quote it.
Examples: Fail, from the Provider Drafts run: "needs cleared and re-retrieve client events carrying draft, action, and surface" (an event field list in prose). It passed the original pattern. Storage requirements are not matched: Danny's approved page keeps one ("the opening and the deterministic block must be stored separately").
```

**Source:** FM05
**Added:** 2026-09-10
**Revised:** 2026-09-29. Pattern extended to client event field lists written in prose.

---

### E18: Coefficient Conflation

**Pass:** Every sourced coefficient or named quantity is kept distinct and attributed to the metric it actually corresponds to.
**Fail:** Two distinct sourced quantities are merged into one, or a metric cites the coefficient for a different quantity.
**Check type:** LLM judge

```judge
Criterion: Are look-alike coefficients from the sizing model kept distinct and correctly mapped?
Pass definition: Each reconciling reference names the coefficient that matches the metric's own definition; two different coefficients are never blended or swapped.
Fail definition: A metric cites a coefficient that measures a different quantity, or two coefficients are treated as one; quote it.
Examples: Fail, from the Galen run: app-submit share cited as evidence about the App Engagement coefficient when it maps to the Visit Modality coefficient.
```

**Source:** FM06
**Added:** 2026-09-10

---

### E19: Unapproved Adoption

**Pass:** Every metric, definition change, and structural choice in the document maps to the gate-2 approved list, the gate-1 plan, or a gate-3 finding Danny adopted.
**Fail:** The document contains a metric, definition, or change no gate approved.
**Check type:** LLM judge

```judge
Criterion: Does the document contain only what the gate snapshots approved?
Pass definition: Every metric ID and every material definition or structural choice traces to gate-1.md, gate-2.md, or an adopted row in gate-3.md.
Fail definition: At least one metric, definition, or change has no approving gate; quote it.
Examples: none yet
```

**Source:** FM07
**Added:** 2026-09-10

---

### E20: Surgical Revision

**Pass:** Every line that differs between the pre-revision copy and the current document maps to an item on the gate-4 touch list, or is the change-log row and Last updated cell.
**Fail:** Any changed line is outside the touch list.
**Check type:** LLM judge

```judge
Criterion: Diffing pre-revision-<n>.md against the document, does every change fall within the approved touch list?
Pass definition: Each added, removed, or altered line maps to a gate-4 item, the new change-log row, the Last updated cell, or a summary count update the touch list implies.
Fail definition: At least one changed line has no touch-list item; quote it.
Examples: none yet
```

**Source:** FM08
**Added:** 2026-09-10

---

### E21: External Write Audit

**Pass:** Every ledger line has `"write":false`, and no ledger tool name carries a write-capable verb as a word.
**Fail:** Any ledger line has `write: true`, lacks the field, or names a write-capable tool.
**Check type:** Code

```check
Type: absence
Source field: N/A
Target field: <run>/mcp-ledger.jsonl
Logic: jq -c 'select(.write != false)' mcp-ledger.jsonl must return nothing. Then run: jq -r '.tool' mcp-ledger.jsonl | sed 's/.*__//' | sed -E 's/([a-z0-9])([A-Z])/\1_\2/g' | tr 'A-Z' 'a-z' | grep -vE '^(get|list|read|search|fetch|query|find|describe)_' | grep -E '(^|_)(create|update|comment|send|post|append|delete|write|set|modify|edit|transition|upload|add|reply|share|trash|move|copy|schedule|destructive|make|insert|replace|duplicate|label|mark|forward|push|merge|deploy)(_|$)'. It must return nothing. The pipeline strips any server prefix, splits camelCase and snake_case into words, exempts names that open with a read verb, and matches whole words only. Any output = FAIL; quote the output and its ledger line.
Examples: Pass (a false-positive Fail under the original substring pattern), from the Provider Drafts run: list_spreadsheet_comments matched "comment". Fail under this pipeline: slack_send_message, addOrEditJiraIssueComment, executeWrite, make_dashboard.
```

**Source:** FM09. Runs in the final QA phase of the run, after the last MCP call.
**Added:** 2026-09-10
**Revised:** 2026-09-29. Substring match replaced with a whole-word match that exempts read-verb names.

---

### E22: Writing-Pattern Violation

**Pass:** Zero matches on every hard verification search in `forbidden-writing-patterns.md` and on the plain-word and filler bans in AGENTS.md.
**Fail:** Any search returns an untagged match.
**Check type:** Code

```check
Type: pattern
Source field: forbidden-writing-patterns.md § Hard verification searches; AGENTS.md § Writing, Mechanical
Target field: full document
Logic: Run each row: grep -c for the em dash character U+2014 (must be 0); grep -n "That's not"; grep -nE 'less a .* more a'; grep -nE "And that matters|That's the part everyone misses|Which is exactly the point"; grep -nE "It's the .* of"; grep -nE "^(Here's the thing|Let me be clear|The truth is|To be clear|I'll be honest)"; grep -nE '\b[0-9]+\s*(to|-)\s*[0-9]+\b', excluding matches inside `[Assumption: ...]` or `[estimate range]` tags, ISO dates matching `[0-9]{4}-[0-9]{2}-[0-9]{2}`, M/D/YY or M/D/YYYY dates matching `[0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4}`, and PRD section references matching `§[0-9]+(\.[0-9]+)?`; grep -niE '\b(several|a few|some time)\b' excluding matches inside `[Assumption: ...]` or `[estimate range]` tags; in the final paragraph and final three bullets grep -niE 'In short|At the end of the day|To summarize|In conclusion|Bottom line:'; grep -niE '\b(utilize|leverage|facilitate|in order to|prior to|subsequently|delve|landscape|ecosystem)\b'; grep -niE "It's worth noting|It's important to|Needless to say|At this point in time|moving forward|going forward". Any hit not covered by an explicit tag exception = FAIL; quote it.
```

**Source:** FM10
**Added:** 2026-09-10

---

### E23: Required-Section Presence and Order

**Pass:** The document's canonical headers appear exactly once each, in the template's order, with the template's wording. B and C blocks appear only in multi-build documents.
**Fail:** A canonical header is missing, duplicated, reworded, or out of order, or a multi-build block appears in a single-build document.
**Check type:** Code

```check
Type: structural
Source field: references/template.md canonical header sequence
Target field: all lines matching ^#{1,3}\s in document order
Logic: Extract headers. Normalize "## A. <anything>" to "## A. [Build]" and "## B. <anything>" to "## B. [Second build]". Normalize the title: take the text after "## A. " as the build name, and replace that build name in the "# " title line with "[Build]". Determine multi-build by presence of a "## B." header. Build the expected list from the template (omit B and C blocks when single-build). Filter actual headers to those that appear in the expected list (extra headers are E24's concern). The filtered sequence must equal the expected list exactly. FAIL on any missing, duplicate, reordered, or reworded header; quote the diff.
```

**Source:** FM11a
**Added:** 2026-09-10
**Revised:** 2026-10-28. Title normalization added; the December Provider Pay Model run logged Fail (ambiguous) on a correctly filled title in D rounds 1 and 2.

---

### E24: Unjustified Extra Section

**Pass:** Every header outside the canonical set was named in the gate-1 plan with a one-line reason, and does not duplicate a canonical section's content.
**Fail:** An extra header exists with no plan entry, or restates what a canonical section already carries.
**Check type:** LLM judge

```judge
Criterion: For each header not in the canonical set, does gate-1.md name it with a reason, and does its content stand apart from the canonical sections?
Pass definition: Every extra header has a gate-1 entry and distinct content.
Fail definition: At least one extra header lacks a gate-1 entry or duplicates canonical content; name it.
Examples: none yet
```

**Source:** FM11b
**Added:** 2026-09-10

---

### E25: Cross-Section Redundancy

**Pass:** Every fact, rationale, and definition is stated in full exactly once; other mentions cross-reference by ID or section.
**Fail:** The same fact, rationale, or definition is stated in full, even reworded, in two or more places.
**Check type:** LLM judge

```judge
Criterion: Is each distinct fact, rationale, or definition stated in full only once, with every other mention a short cross-reference?
Pass definition: No pair of locations carries the same content in full.
Fail definition: At least one pair does; quote both.
Examples: Fail, from the December Provider Pay Model run: §1 said "O1 reruns old rules on the same work, so concurrent changes cancel out of it" and the O1 note said "O1's counterfactual reruns old-model rules on the same period's completed work"; fixed by making §1 read "Its same-period counterfactual (see the O1 note) cancels concurrent changes out of it." Pass, same run: O1's Target cell "$1.2M a year, modeled (sizing in Summary)" points to the Summary's full sizing sentence. A short pointer such as "(see §5)" is a cross-reference, not a restatement.
```

**Source:** FM12
**Added:** 2026-09-10
**Revised:** 2026-10-28. First calibration examples; the same unchanged text passed and then failed across two R rounds.

---

### E26: Over-Long Prose

**Pass:** No prose paragraph exceeds four sentences and no sentence exceeds 35 words.
**Fail:** Any paragraph or sentence exceeds its limit.
**Check type:** Code

```check
Type: structural
Source field: N/A
Target field: prose blocks: consecutive non-blank lines not starting with |, #, >, or a list marker, including under-table notes
Logic: For each prose block, split into sentences on [.!?] followed by a space or end of line, treating "e.g.", "i.e.", "vs.", "§", decimals, and "M/D/YY" dates as non-terminal. A bold lead that ends in a period counts as one sentence; a bold label that ends in a colon ("**Not sliced:**") opens the first sentence and does not count on its own, though its words count toward that sentence's 35. FAIL if any block has more than 4 sentences. For each sentence, count whitespace-separated tokens; FAIL if more than 35. Quote the offending block or sentence and its count.
```

**Source:** FM13a
**Added:** 2026-09-10
**Revised:** 2026-09-29. Bold-lead counting stated; in the Provider Drafts run E26 and E37 disagreed on it.

---

### E27: Prose Carrying Tabular Content

**Pass:** No prose paragraph carries content the template places in a table: metric definitions, stakeholder lists, open questions, slices, workstream assignments, change history.
**Fail:** A prose paragraph substitutes for, or restates, a table row's fields.
**Check type:** LLM judge

```judge
Criterion: Does any prose block carry what the template puts in a table?
Pass definition: Prose is limited to leads, the §1 rationale paragraphs, the §2 state-progression paragraph, "Not sliced", and under-table notes that add reasoning rather than fields.
Fail definition: At least one prose block lists metrics, people, questions, or slices that belong in a table, or restates a row's Definition, Grain, Window, or Good; quote it.
Examples: Fail, from the December Provider Pay Model run: the A13 note opened "A13 carries two reads in one row: the Nov 30 dry run and every payday after GA," which repeated the Definition cell. Pass, same run: the note "Workforce Management's other gaming signals are referenced, not rebuilt" names six signals as an exclusion, with no Grain, Window, or Good fields, so it adds reasoning rather than carrying a table's content.
```

**Source:** FM13b
**Added:** 2026-09-10
**Revised:** 2026-10-28. First calibration examples.

---

### E28: Guardrail Alarm Line Presence

**Pass:** Every row under a Guardrail metrics or Shared guardrails header has "alarm" in its Good cell.
**Fail:** Any guardrail row's Good cell lacks an alarm clause.
**Check type:** Code

```check
Type: presence
Source field: intake decision Q22
Target field: the last non-empty cell of every row matching ^\|\s*[ABC][0-9]+\s*\| that lies under a "### Guardrail metrics" or "## C. Shared guardrails" header and before the next ## or ### header
Logic: For each such row, extract the last cell; grep -i 'alarm'. FAIL if absent; quote the row ID.
```

**Source:** FM14. Note: v2 rows A17 to A20 and B6 to B8 fail this check; they predate the rule (see references/exemplars.md).
**Added:** 2026-09-10

---

### E29: Baseline and Target Column Placement

**Pass:** The Business outcomes table and every Hero metrics table have the eight-cell header; every Reconciling, Driver, Guardrail, and Shared guardrails table has the six-cell header.
**Fail:** Any table's header deviates.
**Check type:** Code

```check
Type: structural
Source field: references/template.md column specifications
Target field: the first row starting with | after each of: "## O.", "### Hero metrics", "### Reconciling metrics", "### Driver metrics", "### Guardrail metrics", "## C. Shared guardrails"
Logic: Split the header row on |, trim cells, drop empties. Under "## O." and "### Hero metrics" the sequence must be exactly: #, Metric, Definition (numerator / denominator), Grain, Window, Baseline, Target, Good. Under the other four: #, Metric, Definition (numerator / denominator), Grain, Window, Good. FAIL on any deviation; quote the header.
```

**Source:** FM15
**Added:** 2026-09-10

---

### E30: Summary Metric Count Consistency

**Pass:** The numeral before "metrics across" in the Summary equals the count of metric-ID rows in the document.
**Fail:** The two numbers differ.
**Check type:** Code

```check
Type: comparison
Source field: Summary, "What ADS should build" line
Target field: all rows matching ^\|\s*[OABC][0-9]+\s*\|
Logic: grep -oE '[0-9]+ metrics across' on the Summary line; take the integer. Count rows matching the ID pattern across the document. FAIL if they differ; report both numbers. FAIL if the Summary carries the count as a word rather than a numeral.
```

**Source:** FM16a
**Added:** 2026-09-10

---

### E31: ID Sequencing

**Pass:** Within each prefix letter, IDs run 1 to N with no gaps or repeats, in document order.
**Fail:** Any prefix skips, repeats, or is out of order.
**Check type:** Code

```check
Type: pattern
Source field: N/A
Target field: all rows matching ^\|\s*([OABC])([0-9]+)\s*\|
Logic: Group the captured numbers by prefix in document order. For each prefix, the sequence must equal 1, 2, ..., N where N is the group's row count. FAIL on any gap, repeat, or reorder; quote the prefix and the sequence found.
```

**Source:** FM16b
**Added:** 2026-09-10

---

### E32: Cross-Reference Validity

**Pass:** Every metric-ID token referenced in prose, Definition cells, Next steps, Open questions, or the Change log resolves to a row, or is explicitly marked as a former ID.
**Fail:** Any referenced ID has no row and no "former" marker.
**Check type:** Code

```check
Type: comparison
Source field: valid-ID set from the E31 row scan
Target field: all text outside the ID column
Logic: Build the valid set from rows. Scan all text for tokens matching \b[OABC][0-9]+\b that are not themselves a row's ID cell. Expand ranges written "X through Y" or "X to Y" with the same prefix. Skip tokens preceded by the word "former". FAIL if any token is not in the valid set; quote it and its line.
```

**Source:** FM16c. v2's 2026-09-02 change-log row cites "C3", which no longer exists; this check catches it.
**Added:** 2026-09-10

---

### E33: Dangling Ownership

**Pass:** Every TBD is written as `[TBD: name-or-role]` with content after the colon; no unfilled `[owner]` remains; every Open questions row has a non-empty Owner cell.
**Fail:** A bare TBD, an unfilled placeholder, or an empty Owner cell.
**Check type:** Code

```check
Type: pattern
Source field: intake decisions Q22 and Q24
Target field: full document; Open questions table
Logic: grep -n 'TBD'; each hit must match \[TBD:\s*[^\]\s][^\]]*\]. grep -n '\[owner\]' must return nothing. For each row under "## 5. Open questions", the second cell must be non-empty. Any violation = FAIL; quote it.
```

**Source:** FM17
**Added:** 2026-09-10

---

### E34: Fabricated Name

**Pass:** Every person named in Stakeholders, Informed, an Owner cell, or Next steps appears in `Stakeholder Management/stakeholder-directory.md`, an input, or the intake transcript.
**Fail:** Any named person appears in none of those.
**Check type:** LLM judge

```judge
Criterion: Is every named person traceable to the stakeholder directory, an input, or an intake answer?
Pass definition: Every name resolves to one of the three sources.
Fail definition: At least one name resolves to none; quote it.
Examples: none yet
```

**Source:** FM18
**Added:** 2026-09-10

---

### E35: Summary Field Bloat

**Pass:** Every non-blank line under Summary, before Stakeholders, starts with one of the seven allowed bold labels or is a bullet under **What this is not:**. The five required labels are present in order, and each field stays within its sentence budget.
**Fail:** An unlabeled or non-allowed line, a missing required label, wrong order, or a field over budget.
**Check type:** Code

```check
Type: structural
Source field: references/template.md Summary field table
Target field: lines between "## Summary" and "### Stakeholders"
Logic: Every non-blank line must begin with one of: **What ADS should build:**, **Primary outcome and sizing:**, **Hard dependency:**, **Launch date:**, **Links:**, **What this is not:**, **Scope notes:**, except lines beginning "- " that follow **What this is not:** before the next bold label. Labels that appear must follow that order. Required: What ADS should build, Primary outcome and sizing, Launch date, Links, What this is not. Hard dependency and Scope notes are optional. Sentence counts (split on [.!?] followed by a space or end of line, treating "e.g.", "i.e.", "vs.", "§", decimals, and dates as non-terminal, per E26's splitting rule): What ADS should build 1, Primary outcome and sizing 2, Hard dependency 1, Launch date 1, Scope notes 2. Any violation = FAIL; quote the line.
```

**Source:** FM19
**Added:** 2026-09-10
**Revised:** 2026-09-29. Hard dependency made optional and bullets allowed under What this is not, per Danny's edit.

---

### E36: Dropped Approval

**Pass:** Every metric and instruction Danny approved at any gate is present in the document, and every clause of each approved definition sketch appears in that metric's row or its under-table note.
**Fail:** An approved metric or instruction is absent, or a kept row drops a clause from its approved definition sketch with no gate change that removed it.
**Check type:** LLM judge

```judge
Criterion: Cross-checking gate-1.md through gate-4.md against the document, is every approved item represented, down to the clauses of each approved definition sketch?
Pass definition: Every approved metric ID appears as a row with the approved tier. For every row, each clause of its gate-2 definition sketch (as amended by adopted gate-3 findings and gate-4 items) appears in the row or its under-table note; wording and order may change, meaning may not be dropped. Every adopted gate-3 finding and every gate-4 touch-list item is applied.
Fail definition: At least one approved item is missing or applied differently from the approval, or a kept row is missing a clause from its approved sketch; name the row and quote the missing clause. In phase D only gate-1 and gate-2 apply; in phase R all four apply.
Examples: Fail, from the December Provider Pay Model run: gate-2's O1 sketch carried "(old-model decisions per payable hour sets the counterfactual tier)" and A17's carried "Fast-side threshold not set." The draft dropped both. E36 passed three D rounds on row presence alone, and reviewers caught the drops at Step 8.
```

**Source:** FM20
**Added:** 2026-09-10
**Revised:** 2026-10-28. Clause-level comparison inside kept rows.

---

### E37: Under-Table Note Justification

**Pass:** Every under-table note explains a choice a careful, informed reader would question, and adds reasoning its row does not carry.
**Fail:** A note explains the obvious or restates its row.
**Check type:** LLM judge

```judge
Criterion: Does each under-table note earn its place per the calibration examples in references/metric-taxonomy.md?
Pass definition: The note addresses a nonstandard grain, an exclusion, an inverse or paired metric, an interpretation limit, or a build-twice risk, and its content is not already in the row.
Fail definition: The note explains a standard choice or restates the row's cells; quote it.
Scope: judge content only. Sentence and word counts belong to E26; never fail a note on length.
Examples: see the earned and not-earned lists in references/metric-taxonomy.md
```

**Source:** FM21
**Added:** 2026-09-10
**Revised:** 2026-09-29. Length removed from scope; in the Provider Drafts run this judge failed notes on a sentence count that E26 passed.

---

### E38: Complement Split Across Rows

**Pass:** No metric row is the complement of another row; each complement pair is one row, with the inverse named in its Definition cell.
**Fail:** Two rows share a denominator and their values sum to 100% by construction, or any cell or note states that one row plus another equals 100%.
**Check type:** LLM judge

```judge
Criterion: Does any metric row exist only as the complement of another row over the same denominator?
Pass definition: For every pair of rows sharing a denominator, their numerators do not partition it, so the pair does not sum to 100% by construction. Complements appear as a clause in one row's Definition cell.
Fail definition: At least one pair of rows sums to 100% by construction, or the document states that it does; quote both rows.
Examples: Fail, from the Provider Drafts run: drafts-shown rate (A6) and BAU trigger rate (A11) shared the draft-resolution denominator, and A11's Definition cell said "A6 plus A11 equals 100%." Danny cut A6 and made drafts-shown rate a clause in the BAU row.
```

**Source:** evals-advisor post-run, 2026-09-29. Generalization failure: metric-taxonomy.md already states "A metric and its complement are one row... Never two rows," and the run produced two rows anyway, passing every D and R round.
**Added:** 2026-09-29

---

### E39: Intake Transcript Question Text

**Pass:** Every question block in the intake transcript carries the full question text and an answer.
**Fail:** Any block has an answer without its question text, or a question without an answer.
**Check type:** Code

```check
Type: structural
Source field: N/A
Target field: <run>/intake-transcript.md
Logic: awk '/^### Q[0-9]+/{if(h&&!(q==1&&a==1))print h;h=$0;q=a=0} /^\*\*Question:\*\* +[^ ]/{q++} /^\*\*Answer:\*\* +[^ ]/{a++} END{if(h&&!(q==1&&a==1))print h;if(!h)print "NO BLOCKS"}' intake-transcript.md must return nothing. Each block needs exactly one Question line and one Answer line. Any output = FAIL; quote the headings it prints.
Examples: Fail, from the Provider Drafts run: the transcript saved Danny's answers without the question text, and E05 failed at phase P.
```

**Source:** evals-advisor post-run, 2026-09-29. Generalization failure: SKILL.md Step 2 already said to save questions and answers verbatim. The block format was added the same day so a code check can verify it.
**Added:** 2026-09-29

---

### E40: Slice-Rule Contradiction

**Pass:** No metric row, Good cell, or under-table note implies a cut that §3's "Not sliced" paragraph excludes, unless §3 states a scoped exception for it.
**Fail:** A row, alarm, or note implies an excluded cut, and §3 states no exception.
**Check type:** LLM judge

```judge
Criterion: Does anything in the metric tables or notes require a cut that §3 says the dashboard does not make?
Pass definition: Every per-unit read implied by a Definition, Good cell, or note (for example a list of individual providers, a single brand, or one state) is either a §3 slice or covered by a scoped exception written in §3.
Fail definition: At least one row or note implies a cut §3 excludes, with no scoped exception; quote the row or note and the §3 exclusion.
Examples: Fail, from the December Provider Pay Model run: A13's alarm fired "if any provider's counts differ after a payday" while §3 read "Not sliced: ... Individual provider." Fixed with a scoped §3 exception: A13's alarm lists the mismatched providers, visible only to three named roles.
```

**Source:** evals-advisor post-run, 2026-10-28. A care-ops reviewer caught the contradiction at Step 8; no D eval read §3 against the guardrails.
**Added:** 2026-10-28

---

### E41: Eval Slice Fidelity

**Pass:** Every eval slice the phase's judgment subagents receive lists exactly the IDs the phase map assigns them, and each eval section in it is byte-identical to evals.md.
**Fail:** A slice is missing, lists a different ID set, or carries a section that differs from evals.md.
**Check type:** Code

```check
Type: comparison
Source field: SKILL.md <eval_phase_map>; evals.md definitions and suite design rules
Target field: <run>/evals-<phase>-<group>.md for every judgment subagent the phase spawns
Logic: For each judgment subagent active this phase (Fidelity; Structure in P; the merged subagent in D and R), the slice file must exist. Its "IDs:" line must equal the phase map's IDs for that subagent, in map order. Each listed eval's section, from its "### E" heading to the line before the next "---", must appear verbatim in the slice and in evals.md. The file must equal a fresh scripts/eval-slice.py output, which also carries the suite design rules. Any miss = FAIL; name the file and the eval.
```

**Source:** Token-efficiency plan, change 2. QA subagents read a slice of this file, not the whole file.
**Added:** 2026-11-06

---

### E42: Report Evidence Completeness

**Pass:** Each QA judgment report has exactly one row per eval assigned to its subagent this phase, and every row has a non-empty Result cell and Evidence cell.
**Fail:** An assigned eval has no row, an eval appears twice or unassigned, a row is not tied to one eval ID, or a Result or Evidence cell is empty.
**Check type:** Code

```check
Type: structural
Source field: SKILL.md <eval_phase_map>, or the single eval ID of a re-run
Target field: each saved report in <run>/qa-reports/
Logic: scripts/save-qa-report.py runs this as it saves each report, or with --check on a report saved with Write. For each table row after the header, the first cell must start with one eval ID. The set of IDs must equal the subagent's assignment, each exactly once. FAIL on any missing, repeated, unassigned, or non-ID row (for example "All others Pass"), or any empty Result or Evidence cell; name the report and the row. A FAIL counts as a report that returned nothing for the affected evals, per <qa_loop_protocol> step 2.
Examples: Fail, from the 5 Nov 2026 revise run: one agent checked every group and listed its passes as a single "All others Pass" row with no evidence.
```

**Source:** Token-efficiency plan, change 4. One merged subagent now checks eleven evals, so a summary row could hide a skipped eval.
**Added:** 2026-11-06

---

### E43: Verbatim Report Save

**Pass:** Every QA report saved in the run folder matches its subagent's final message byte for byte. A run on a host with no subagent transcripts passes with that stated.
**Fail:** A saved report differs from its subagent's final message, its file is missing, or its transcript is missing.
**Check type:** Code

```check
Type: comparison
Source field: each subagent's Claude Code transcript, located by the agent ID in <run>/qa-reports/manifest.jsonl
Target field: the report file each manifest line names
Logic: The trace author runs python3 scripts/save-qa-report.py --verify --run <run>. For each manifest line with a path, the script reads the last assistant message's text blocks from the transcript and compares them with the saved file. Any difference, missing file, or missing transcript = FAIL; quote the script output. No manifest = Pass, noting that reports were saved with Write.
```

**Source:** Token-efficiency plan, change 7. The 4 Nov 2026 trace recorded saved reports as condensed rather than verbatim, and the 5 Nov 2026 trace found an orchestrator note appended to one.
**Added:** 2026-11-06

---

### E44: QA Agent Type and Depth

**Pass:** Every QA, lens, and trace subagent ran as the `dashboard-qa` agent type, and no subagent in the run ran above spawn depth 1. A run on a host with no subagent transcripts passes with that stated.
**Fail:** A logged subagent ran as another type, or any subagent spawned during the run has a spawn depth above 1.
**Check type:** Code

```check
Type: presence
Source field: each subagent's .meta.json beside its transcript
Target field: <run>/qa-reports/manifest.jsonl
Logic: For each manifest line, agent_type must equal "dashboard-qa" and spawn_depth must be 1 or less. Then, in every subagents folder the manifest names, each .meta.json written since one hour before the first manifest line must have spawnDepth 1 or less. Any violation = FAIL; quote the agent ID and the value. No manifest = Pass, noting that the host keeps no transcripts.
Examples: Fail, from the 27 Oct 2026 P round 2: a Fidelity subagent spawned its own fork agent.
```

**Source:** Token-efficiency plan, change 5. v1.3 banned QA file creation after a QA subagent wrote scratch files. The tool-restricted type removes Write, Edit, and the Agent tool, so a fork is no longer possible.
**Added:** 2026-11-06
