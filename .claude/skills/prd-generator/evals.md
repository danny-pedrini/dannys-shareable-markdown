# Evals: prd-generator

## Active Evals

Phases: P is plan QA (Step 4), D is draft QA (Step 6), R is revision QA (Step 8). H0, H1, and H2 are the handoff checks after the intake gate, Gate 1, and Gate 2 (SKILL.md `<handoff_protocol>`). Groups and phases per SKILL.md `<eval_phase_map>`.

| ID | Name | Phase Checked | Type | Check | Added | Last Result |
|----|------|---------------|------|-------|-------|-------------|
| E01 | Plan Dropped Inputs | P | Generalization | Judge | 2026-06-25 | None yet (v3.0) |
| E02 | Hallucination | P, D, R | Generalization | Judge | 2026-06-25 | None yet (v3.0) |
| E03 | Goals Are Outcomes | P | Generalization | Judge | 2026-06-25 | None yet (v3.0) |
| E04 | Scope Misplacement | P, D, R | Generalization | Judge | 2026-06-25 | None yet (v3.0) |
| E05 | Phantom Alternatives | P | Generalization | Code | 2026-06-25 | None yet (v3.0) |
| E09 | Eng Encroachment | P, D, R | Generalization | Judge | 2026-06-25 | None yet (v3.0) |
| E10 | Draft Fidelity | D, R | Generalization | Judge | 2026-06-25 | None yet (v3.0) |
| E11 | Content Duplication | P, D, R | Generalization | Judge | 2026-06-25 | None yet (v3.0) |
| E13 | TL;DR Bloat | D, R | Generalization | Code | 2026-06-25 | None yet (v3.0) |
| E14 | Metadata Bloat | D, R | Generalization | Code | 2026-06-25 | None yet (v3.0) |
| E15 | Mermaid Usage | D, R | Generalization | Code | 2026-06-25 | None yet (v3.0) |
| E18 | Unopenable Source | D, R | Generalization | Code | 2026-06-25 | None yet (v3.0) |
| E21 | Source Mechanism Distortion | P, D, R | Generalization | Judge | 2026-06-26 | None yet (v3.0) |
| E22 | Goal Redundancy & Constraint Masking | P | Generalization | Judge | 2026-08-04 | None yet (v3.0) |
| E23 | Risk Materiality | P, D, R | Generalization | Judge | 2026-08-04 | None yet (v3.0) |
| E24 | Dependency Validity | P, D, R | Generalization | Judge | 2026-08-04 | None yet (v3.0) |
| E26 | Orphaned Design-Decision Belief | P, D, R | Generalization | Judge | 2026-08-04 | None yet (v3.0) |
| E28 | Section Presence and Order | D, R | Generalization | Code | 2026-10-13 | None yet (v3.0) |
| E29 | Unfilled Template Residue | D, R | Generalization | Code | 2026-10-13 | None yet (v3.0) |
| E30 | Metric Baseline and Target | D, R | Generalization | Code | 2026-10-13 | None yet (v3.0) |
| E31 | AI Launch Elements | P, D, R | Generalization | Judge | 2026-10-13 | None yet (v3.0) |
| E32 | Problem Section Form | D, R | Generalization | Code | 2026-10-13 | None yet (v3.0) |
| E33 | AC Format Leakage | D, R | Generalization | Code | 2026-10-13 | None yet (v3.0) |
| E34 | Testable Detail Leakage | P, D, R | Generalization | Judge | 2026-10-13 | None yet (v3.0) |
| E35 | Embedded Sub-Document | P, D, R | Generalization | Judge | 2026-10-13 | None yet (v3.0) |
| E36 | Story ID Integrity | D, R | Generalization | Code | 2026-10-13 | None yet (v3.0) |
| E37 | Undefined Acronym | D, R | Generalization | Code | 2026-10-13 | None yet (v3.0) |
| E38 | Writing-Pattern Violation | D, R | Generalization | Code | 2026-10-13 | None yet (v3.0) |
| E39 | Surgical Revision | R | Generalization | Judge | 2026-10-13 | None yet (v3.0) |
| E40 | Unapproved Adoption | R | Generalization | Judge | 2026-10-13 | None yet (v3.0) |
| E41 | Undefined Internal Label | P, D, R | Generalization | Judge | 2026-10-27 | None yet (v3.2) |
| E42 | Process as Story | P, D, R | Generalization | Judge | 2026-10-27 | None yet (v3.2) |
| E43 | Requirement Coverage | P, D, R | Generalization | Judge | 2026-10-27 | None yet (v3.4) |
| E44 | Gate Snapshot Completeness | H0, H1, H2 | Generalization | Judge | 2026-11-06 | None yet (v3.8) |
| E45 | Report Coverage | P, D, R, H0, H1, H2 | Generalization | Code | 2026-11-06 | None yet (v3.8) |
| E46 | QA Artifact Integrity | P, D, R, H0, H1, H2 | Generalization | Code | 2026-11-06 | None yet (v3.8) |
| E47 | First-Read Clarity | P, D, R | Generalization | Judge | 2026-11-18 | None yet (v3.9) |

**Suite design rules:** one eval = one failure mode (one remediation action type on one inspection target). A single artifact statement may legitimately co-fail two evals that test orthogonal properties (e.g., a goal that is both activity-phrased [E03] and a restatement of another goal [E22]). Examples in each definition are calibration anchors, not additional criteria. Examples use Care scenarios; they are illustrative, not facts about any real launch.

**Template rule coverage:** every rule in the `Templates/PRD-Template.md` usage block maps to at least one eval.

| Template rule | Enforced by |
| --- | --- |
| 1. One PRD per launch | E35 (future phase in detail) |
| 2. Cold-reader altitude, no word cap | E34 (testable detail kept out), E47 (plain on first read); no length check |
| 3. What and why vs. the acceptance criteria doc | E33, E34, E43 |
| 4. Say each fact once | E11 |
| 5. Omit empty sections | E29 |
| 6. Link, don't embed | E35 |
| 7. Baseline and numeric target | E30 |
| 8. AI launch elements | E31 |
| 9. No engineering implementation detail | E09 |
| 10. Story ID format | E36 |
| 11. Cold-reader test | E37 (acronyms), E41 (internal labels), E28 (Today column) |
| 12. Openable sources | E18 |
| 13. Writing checklist | E38, plus the draft brief (full CLAUDE.md checklist) |
| 14. Mechanisms as sources state them | E21 |
| 15. Stories are product behavior | E42 |
| Problem section guidance (POV form, evidence links) | E32 |

## Definitions

### E01: Plan Dropped Inputs

**Pass:** Every constraint, requirement, and contextual detail from the inputs and intake answers appears in the plan's PRD content or on the acceptance criteria hand-off list (`<run>/acceptance-criteria-handoff.md`).
**Fail:** Any input or intake constraint, requirement, or contextual detail is absent from both.
**Check type:** LLM judge

```judge
Criterion: Does the plan carry every constraint, requirement, and contextual detail from Danny's inputs and intake answers, in its PRD content or on its acceptance criteria hand-off list?
Pass definition: Every distinct piece of information from the inputs (canvases, notes, files, threads) and the intake transcript is represented in the plan's PRD sections or on the hand-off list. Nothing was dropped.
Fail definition: At least one constraint, requirement, metric, persona detail, or contextual fact from the inputs or intake is missing from both the PRD content and the hand-off list.
Note: a detail correctly placed on the hand-off list instead of the PRD is a Pass here. Whether a detail that IS in the PRD content belongs on the hand-off list instead is E34's check.
```

**Examples:**
- Pass: The intake excluded Maryland patients from the pilot; the plan's Out of scope carries it with the reason.
- Pass: The prototype shows a feedback modal that blocks submit without a reason; the plan puts that rule on the hand-off list, not in the story table.
- Fail: The inputs named Hims Weight Loss as the next phase; no plan section and no hand-off item mentions it.

**Source:** Design-phase failure mode analysis; retargeted 2026-10-13 from the spec to the plan, with the hand-off list counted as coverage (the v3.0 PRD deliberately excludes testable detail)
**Added:** 2026-06-25 (retargeted 2026-10-13)

---

### E02: Hallucination

**Pass:** Every requirement, metric, number, stakeholder name, and technical detail in the artifact is traceable to the inputs, intake answers, or the stakeholder directory (names only).
**Fail:** The artifact contains any requirement, metric, threshold, name, or technical detail not present in those sources.
**Check type:** LLM judge

```judge
Criterion: Is every factual claim in the artifact traceable to the inputs, the intake transcript, or (for names) the stakeholder directory?
Pass definition: All requirements, metrics, thresholds, stakeholder names, persona details, and technical specifics can be traced to a specific input, intake answer, or directory entry. Unknowns are written as [TBD: needs data] or [TBD: owner].
Fail definition: At least one requirement, metric, threshold, name, or technical detail appears in the artifact but cannot be found in any input, intake answer, or (for names) the directory. It was fabricated.
Note: a mechanism that does appear in a source but is elaborated past it or swapped for a different one is E21's check. This eval covers claims with no basis in any source.
```

**Examples:**
- Pass: Every number in the metrics table (the task deflection baseline, the 30% reply-rate baseline) appears in the sizing doc or the intake.
- Fail: The plan sets a "90% draft acceptance" target that no input or intake answer states.
- Fail: Doc status names a design lead who appears in no input, no intake answer, and not in the stakeholder directory.

**Source:** Design-phase failure mode analysis; 2026-10-13 added the stakeholder directory as the ground truth for names
**Added:** 2026-06-25

---

### E03: Goals Are Outcomes

**Pass:** Each goal states an outcome that explains why the work matters, aligned with the problem section and mapped to a metric. Together, the goals cover every part of the user and business problems the launch can address.
**Fail:** A goal describes an activity, output, or feature rather than an outcome, or is disconnected from the problem section, or maps to no metric, or a part of the problem the launch addresses has no goal.
**Check type:** LLM judge

```judge
Criterion: Does every goal represent the fundamental "why" behind the work: an outcome aligned with the problem section and the metrics table?
Pass definition: Each goal states an outcome that explains why the work matters. Goals align with the user and business problems, and each maps to at least one metric in the table. They are not activity descriptions ("build X", "implement Y") or feature lists. Together, they cover every part of the user and business problems that this launch's stories address.
Fail definition: One or more goals describe activities, outputs, or features rather than outcomes. Or a goal is disconnected from the problem section, or doesn't map to any metric. Or a part of the problem the launch addresses has no goal, so the goals are narrower than the work.
Note: whether goals overlap each other or mask delivery constraints is E22's check, not this one.
```

**Examples:**
- Pass: "Cut provider time spent asking patients for missing chart information," tied to the task deflection metric.
- Fail: "Build an Ivy chart-completion flow," an activity, not an outcome.
- Fail: The business problem names savings, paying for all tasks, and a quality incentive; the stories cover tasks, day boundaries, and controlled substances pay; the only pay goal is "providers get paid for every task."

**Source:** Design-phase failure mode analysis; coverage added 2026-10-27 (Danny: goals should comprehensively address the parts of the problems this PRD can address)
**Added:** 2026-06-25 (narrowed 2026-08-04: goal overlap and constraint masking moved to E22; examples moved to Care 2026-10-13; coverage added 2026-10-27)

---

### E04: Scope Misplacement

**Pass:** Every scope item (Non-goal, Out of scope item, Risk, Dependency, Open question) sits in the section that matches its nature per the cross-section ownership contract.
**Fail:** An item sits in a section that doesn't match its nature, e.g., a belief listed as a Non-goal, or an undecided call written as a Risk as if settled.
**Check type:** LLM judge

```judge
Criterion: Is each scope item placed in the correct section per the cross-section ownership contract?
Pass definition: Non-goals are outcomes we are not pursuing. Out of scope items are work excluded from this launch, with a why. Risks are things that could go wrong, including load-bearing assumptions written as risks. Dependencies are things this PRD needs from someone else to launch. Open questions are genuinely undecided items that fit no other category. Every item's nature matches its section.
Fail definition: An item is placed in a section that doesn't match its nature, e.g., excluded work listed as a Non-goal, a belief listed under Non-goals, an undecided product call presented as a Risk or as settled, or Danny's own open call listed as a Dependency.
Note: this eval checks placement only. An item appearing in TWO sections is E11. A Dependencies row's owner or blocking validity is E24. A Risks row's triviality is E23. A missing Risks row is E26. A story that is really a process is E42. Do not fail those defects here.
```

**Examples:**
- Pass: "An autonomous AI doctor" sits in Non-goals (an outcome we are not pursuing); "Hims Weight Loss" sits in Out of scope with "lands in Q4."
- Fail: "Legal hasn't decided the message cap" listed under Risks; it is undecided and belongs in Open questions.

**Source:** Design-phase failure mode analysis; retargeted 2026-10-13 to the v3.0 buckets (Assumptions became Risks)
**Added:** 2026-06-25 (narrowed 2026-08-04; retargeted 2026-10-13)

---

### E05: Phantom Alternatives

**Pass:** `### Alternatives considered` is present only if 2 or more real options were debated in the inputs or intake. If only one approach was discussed, the section is omitted.
**Fail:** The section exists when only one approach was considered, or it contains fabricated alternatives.
**Check type:** Code

```check
Type: absence
Source field: Inputs and intake transcript, count distinct solution approaches discussed
Target field: "### Alternatives considered" in the artifact
Logic: If the inputs and intake transcript contain discussion of only one approach (no "option A vs B" debate, no tradeoff comparison), the artifact must NOT contain "### Alternatives considered". Grep for that header; if present when only 1 option was discussed, FAIL.
```

**Examples:**
- Pass: The intake debated extending the existing recommendation card against building a new one; the table shows exactly those two.
- Fail: Only one approach was discussed, but the plan adds an Alternatives considered table with an invented "manual review" option.

**Source:** Design-phase failure mode analysis; template states "Only when 2 or more options were actually debated"; grep target moved to the Appendix subsection 2026-10-13
**Added:** 2026-06-25 (retargeted 2026-10-13)

---

### E09: Eng Encroachment

**Pass:** The whole PRD contains only product-level language: what the system should do, not how it is built.
**Fail:** Any section contains implementation details: API paths, database tables or columns, algorithm choices, framework references, or architecture decisions.
**Check type:** LLM judge

```judge
Criterion: Is the PRD free of technical implementation details in every section?
Pass definition: The PRD describes observable behavior and outcomes. No API paths, database schemas, algorithm names, framework references, field or identifier choices, or architecture decisions appear anywhere, including user stories, rollout, risks, and dependencies.
Fail definition: Any section mentions specific API endpoints, database tables or columns, algorithm choices, framework-specific patterns, or architectural decisions. The PRD has no technical section that exempts them.
Note: a dependency on another team's system may name that system ("needs the CDS draft output") without describing how it is built. Testable behavioral detail that is not implementation (edge cases, states, data capture) is E34's check.
```

**Examples:**
- Pass: "A revealed draft always names the provider who opened the chart."
- Fail: "The CDS writes drafts to the provider_drafts table and the EMR fetches them from /recommendations."

**Source:** Design-phase failure mode analysis; inspection target widened to the whole PRD 2026-10-13 (v3.0 has no Technical Considerations or RBAC section)
**Added:** 2026-06-25 (retargeted 2026-10-13)

---

### E10: Draft Fidelity

**Pass:** The draft contains every detail from the approved gate-1 plan's PRD content, with no detail dropped, altered, or added.
**Fail:** Any gate-1 detail is absent from the draft, or altered (a target changed, a story softened, items combined or split differently), or new content appears that the plan does not have.
**Check type:** LLM judge

```judge
Criterion: Does the draft faithfully reproduce every detail from the gate-1 plan's PRD content without drops, alterations, or additions?
Pass definition: Every user story, metric, target, goal, scope item, risk, dependency, and open question in the gate-1 plan appears in the draft with identical meaning. Structure may differ (prose to table) but substance is preserved. The plan's working lists (reviewer set, hand-off list, flags) correctly do not appear.
Fail definition: At least one gate-1 detail is missing from the draft, or altered: a target changed, a story softened or strengthened, items combined differently, or content added that the plan doesn't have.
```

**Examples:**
- Pass: All 9 user stories from gate-1 appear with unchanged priorities, and every metric target matches.
- Fail: Gate-1's "patient-ask false-positive rate under 2%" became "keep false positives low," and MSG-07 is missing.

**Source:** Design-phase failure mode analysis; ground truth moved from the perfected spec to the gate-1 snapshot 2026-10-13
**Added:** 2026-06-25 (retargeted 2026-10-13)

---

### E11: Content Duplication

**Pass:** Every fact, story, behavior, item, or concept is stated in exactly one location. Other locations that need it cite it instead of restating it.
**Fail:** The same underlying fact, story, behavior, item, or concept appears in two or more locations, even if reworded.
**Check type:** LLM judge

```judge
Criterion: Is every fact, story, behavior, item, or concept stated in exactly one location, with cross-references used elsewhere instead of restatement?
Pass definition: Each distinct piece of information appears once: in a story, a scope section, a table row, or prose. Other locations that reference it use cross-references (e.g., "per MSG-05", "see Out of scope"). Brief context-setting mentions are acceptable (e.g., naming a metric in the TL;DR that the metrics table defines).
Fail definition: The same underlying fact, behavior, item, or concept appears in two or more locations, even when reworded or scoped to different sections. Covers: two stories describing the same behavior; the rollout restating a story; the same exclusion in Non-goals and Out of scope; the same metric defined in Goals and the metrics table; the user problem restated after the POV sentence.
```

**Examples:**
- Pass: The Maryland exclusion is stated once in Out of scope; a Risks row cites "see Out of scope."
- Fail: MSG-05's pre-generated drafts are described in the story and restated, reworded, in the rollout's Fallback line.
- Fail: The Hims Weight Loss phase appears in Non-goals and again in Out of scope.

**Source:** Design-phase failure mode analysis; broadened 2026-08-04 to absorb E19; examples moved to Care 2026-10-13
**Added:** 2026-06-25 (broadened 2026-08-04)

---

### E13: TL;DR Bloat

**Pass:** The TL;DR section is one paragraph of at most 5 sentences, with no bullets, sub-headers, or multi-paragraph content.
**Fail:** The TL;DR contains more than one paragraph, more than 5 sentences, bullet points, or sub-headers.
**Check type:** Code

```check
Type: structural
Source field: None
Target field: Content between "## TL;DR" and the next "## " header
Logic: Extract the content between "## TL;DR" and the next "## " header. Trim whitespace. Check: (1) no double newline (multiple paragraphs), (2) no lines starting with "- ", "* ", or a numbered list marker (bullets), (3) no lines starting with "### " (sub-headers), (4) count sentences by splitting on terminal punctuation (".", "!", "?") followed by a space or end of text, ignoring periods inside numbers, abbreviations (e.g., "e.g.", "U.S."), and decimals; FAIL if the count exceeds 5, (5) for each sentence, count em dash characters (U+2014) and semicolons combined; FAIL if any single sentence has 2 or more, since that is a run-on stitching multiple ideas together to stay under the sentence cap. FAIL if any check trips.
Note: an em dash also fails E38. That co-failure is legitimate (E38 is the writing-pattern ban; this check catches stitched run-ons).
```

**Examples:**
- Pass: One 5-sentence paragraph covering how it works today, the change's impact on cost and on quality, what we're building, and this launch's expected impact, with one idea per sentence.
- Fail: A TL;DR with a bullet list of features, or a single paragraph running 7 sentences.
- Fail: A 4-sentence TL;DR where one sentence stitches the current workflow, its cost, and the fix together with two semicolons.

**Source:** Template states "5 sentences max"; sentence-count check added 2026-08-04; run-on check added 2026-08-05; header renamed to "## TL;DR" 2026-10-13; cap raised from 4 to 5 on 2026-10-26 at Danny's request
**Added:** 2026-06-25 (logic extended 2026-08-04, 2026-08-05; retargeted 2026-10-13; cap raised 2026-10-26)

---

### E14: Metadata Bloat

**Pass:** The Doc status and Related docs tables contain only the fields the template defines, plus any field Danny added at intake.
**Fail:** Either table contains a field the template doesn't define and Danny didn't request.
**Check type:** Code

```check
Type: comparison
Source field: Template metadata fields from Templates/PRD-Template.md
Target field: Bold field names in the artifact's Doc status table and Related docs table
Logic: Extract all bold field names from both tables. Allowed Doc status fields: Status, PM, Tech lead, Design lead, Clinical lead, Last updated. Allowed Related docs fields: Background docs, Sizing, Acceptance criteria, Prototype, Mocks, Dashboard requirements, Eval bar. Any field not in the allowed set is a FAIL unless the intake transcript shows Danny requested it. An empty link cell is not a failure (Related docs rows stay as slots); Clinical lead and Eval bar may be absent when the launch is not clinical or not AI.
```

**Examples:**
- Pass: Doc status has the template fields; Related docs keeps all six standard rows, three with links and three empty.
- Fail: Doc status adds "Version" and "Target release" rows the template doesn't define and Danny didn't request.

**Source:** Template defines the canonical metadata fields; allowed set replaced with the v3.0 Doc status and Related docs fields 2026-10-13; Related docs set replaced with Danny's standard rows 2026-10-27
**Added:** 2026-06-25 (retargeted 2026-10-13)

---

### E15: Mermaid Usage

**Pass:** The document contains zero Mermaid diagram blocks.
**Fail:** The document contains one or more ```` ```mermaid ```` code blocks.
**Check type:** Code

```check
Type: absence
Source field: None
Target field: Full document content
Logic: Grep for "```mermaid" (case-insensitive). If found, FAIL. ASCII diagrams are the only acceptable diagram format.
```

**Examples:**
- Pass: No Mermaid blocks anywhere; the Surface table carries screenshots.
- Fail: A Mermaid flowchart of the draft-reveal flow appears under What are we building?

**Source:** Design-phase constraint: ASCII preferred over Mermaid for Confluence compatibility
**Added:** 2026-06-25

---

### E18: Unopenable Source

**Pass:** Every link points to a hosted URL a reader can open, and no claim is cited to a session artifact.
**Fail:** The document links a local filesystem path, or cites a session artifact (intake question numbers, gate rows, reviewer rows or finding numbers, unlinked ticket IDs).
**Check type:** Code

```check
Type: absence
Source field: None
Target field: All markdown links and citation text in the document
Logic: (1) Extract all markdown link targets and bare URLs. FAIL if any target starts with "/Users/", "./", or "../", or contains no "://" (a relative path). In-document anchors (e.g., "#whats-still-open") are acceptable. (2) Grep the text outside link targets for session-artifact citations: "intake" followed by "Q", "question", or "#" and a number; "Gate 1", "Gate 2", "Gate 3", or "gate-" followed by a number; "reviewer row", "finding #", or "finding" followed by a number; and ticket-shaped IDs matching \b[A-Z]{2,}-\d{3,}\b that are not inside a link's text or target. FAIL on any match. Story IDs (two-digit numbers such as MSG-04) do not match the ticket pattern.
```

**Examples:**
- Pass: Every link is a Confluence, Google Docs, Figma, or Looker URL; the ticket MLENG-5032 appears only as the text of a link to it.
- Fail: Related docs links `prototypes/galen-drafts/` (a local path).
- Fail: A Risks row says "per intake Q7" and an Open questions row cites "DX-26283" with no link.

**Source:** Design-phase failure mode analysis (PRDs are published to Confluence); renamed and extended 2026-10-13 to cover template rule 12 and CLAUDE.md's ban on citing session artifacts
**Added:** 2026-06-25 (extended 2026-10-13)

---

### E21: Source Mechanism Distortion

**Pass:** Every mechanism the artifact states matches the mechanism the inputs or intake describe: no unconfirmed elaboration, and no substitution while shortening.
**Fail:** The artifact elaborates a mechanism beyond what the inputs and intake confirm, or restates a mechanism as a different one.
**Check type:** LLM judge

```judge
Criterion: Does every mechanism the artifact states (an incentive, a cause and effect, a system behavior, a trigger) match the mechanism the inputs or intake describe?
Pass definition: For each story, rollout rule, problem statement, risk, or hand-off item that explains how something works, the mechanism matches the inputs. Any detail beyond the inputs (e.g., turning "drafts invalidate on new info" into a specific trigger list) has Danny's explicit confirmation in the intake transcript. Shortened mechanisms keep the same cause and effect.
Fail definition: The artifact adds mechanism detail (triggers, timing, cascade rules, multi-surface behavior) that goes beyond the inputs and is not confirmed in the intake, OR it restates a source mechanism as a different one, such as naming a behavior or cause the source doesn't describe.
Note: E02 covers facts with no basis in any source. E21 covers a mechanism that does appear in a source but is elaborated past it or swapped for a different one. Phase P judges the plan; phases D and R judge the PRD.
```

**Examples:**
- Pass: The input said "drafts invalidate on a new patient message"; the intake asked for the full trigger list; the story and hand-off list match Danny's answer.
- Fail: An input mentioned "a nudge for non-responders" once; the plan elaborated it into a 15-minute push schedule with suppression rules no one confirmed.
- Fail: The input says providers slow down late in the month to add payable hours at a high tier; the PRD says the model "rewards holding visits open."

**Source:** Post-run observation (a canvas's one-line mention was elaborated into an unintended user story); retargeted from the spec to the plan 2026-10-13; extended to D and R and to substituted mechanisms 2026-10-27, driven by the ownership-contract rule "State mechanisms as the inputs state them"
**Added:** 2026-06-26 (retargeted 2026-10-13, extended 2026-10-27)

---

### E22: Goal Redundancy & Constraint Masking

**Pass:** Every goal is a distinct outcome. No goal restates another, and no goal is a delivery constraint dressed up as an outcome.
**Fail:** Two or more goals restate the same outcome in different words, or a goal states a delivery constraint (technology choice, timeline commitment, build vs. buy).
**Check type:** LLM judge

```judge
Criterion: Is every goal actually a distinct outcome: not a restatement of another goal, and not a delivery constraint?
Pass definition: For every pair of goals, they express meaningfully different outcomes. No goal states a technology choice, timeline commitment, build-vs-buy position, or similar delivery constraint. Constraints like that belong in Out of scope, Risks, or Alternatives considered, not Goals.
Fail definition: Two or more goals restate the same idea in different words. Or a goal is phrased as a constraint on how the work is delivered rather than why it matters.
Note: whether a goal is outcome-shaped at all is E03's check. A single goal may fail both.
Note: this eval's two conditions are one failure mode: an entry that shouldn't be in the Goals list, with one remediation (remove or relocate it) and one inspection target (the Goals list).
```

**Examples:**
- Pass: One goal targets provider messaging cost; another targets patient reply speed.
- Fail: "Reduce messaging handle time" and "Make providers faster at messaging" listed separately, plus "Ship on the Care Coach drafting infrastructure" as a third.

**Source:** Split from E03 2026-08-04; examples moved to Care 2026-10-13
**Added:** 2026-08-04

---

### E23: Risk Materiality

**Pass:** Every Risks row is material and specific: if it happened, a story, metric, or rollout decision would change, and the risk or the belief behind it is disputed by a stakeholder in the inputs, or genuinely uncertain for this launch.
**Fail:** A Risks row is generic boilerplate, trivial, or an ordinary fact that changes nothing.
**Check type:** LLM judge

```judge
Criterion: Is every row in the Risks table both material and specific to this launch?
Pass definition: For each row: (1) if the risk materialized, or the belief behind it proved false, at least one story, metric, or rollout decision would change, AND (2) it is specific to this launch and disputed by a stakeholder in the inputs, or genuinely uncertain. Not a generic risk any launch could list with no mechanism. Each row has a mitigation and an owner.
Fail definition: At least one row is trivial (nothing changes if it happens), generic boilerplate with no launch-specific mechanism ("adoption could be low"), an unremarkable fact that belongs as inline rationale, a staffing or capacity concern, or an unconfirmed claim that belongs in intake as a question.
Note: a material belief that SHOULD be a Risks row but isn't is E26's check. Both share this materiality bar.
```

**Examples:**
- Pass: "Patients don't answer the chart questions (reply rate is about 30% today); mitigation: ask at submission and fill from existing data first; owner: Ivy PM."
- Fail: "Providers may need time to learn the new UI," with no mechanism and nothing in the PRD that changes if it's true.
- Fail: "The Dec 1 date rests on an engineering manager's read of team capacity." Capacity belongs in the program plan.

**Source:** Split from E04 2026-08-04 as Assumption Load-Bearing; materiality bar added 2026-08-14; renamed and retargeted to the Risks table 2026-10-13 (the v3.0 template writes load-bearing assumptions as risks)
**Added:** 2026-08-04 (retargeted 2026-10-13)

---

### E24: Dependency Validity

**Pass:** Every Dependencies row has an owner outside Danny, is committed to by another PRD, initiative, or owning team, and genuinely blocks or gates this launch.
**Fail:** A Dependencies row is Danny's own undecided call, blocks nothing, or has no other body of work or owning team committed to delivering it.
**Check type:** LLM judge

```judge
Criterion: Does every Dependencies row represent something this launch genuinely needs from someone else: not Danny's own undecided call, and not work this PRD should claim as its own story?
Pass definition: Each row names an owner other than Danny, points to another PRD, initiative, or owning team that has committed to deliver it (status or timeline, even if unscheduled), and describes work or a decision the launch waits on. A Care Ops workstream (pay model, training, a sign-off) passes when a named team owns it and the launch waits on it, even with no separate initiative.
Fail definition: At least one row has Danny as its effective owner (an Open question), is a non-blocking FYI, OR no other PRD, initiative, or owning team has committed to deliver it. The test is not "which team's engineers would build this"; it is "has another body of work or team already committed." If not, it belongs in this PRD's own stories.
Note: a Care Ops workstream owned by a named team that the launch waits on is never a Fail for lacking a separate initiative. The owning team's commitment is enough.
```

**Examples:**
- Pass: "Ivy pre-Rx enablement (Owner: Ivy team): the chart-completion asks need the Ask tab before Rx. Blocks launch: Yes."
- Pass: "Clinical and Legal sign the action-to-snippet mapping (Owner: Clinical). Blocks launch: Yes." A named team owns it and the launch waits.
- Fail: "Decide the per-patient message cap," owned by Danny. That is an Open question.
- Fail: "Build the draft-not-available state (Owner: EMR engineering)" with no other initiative committed to it. It is this PRD's own story.

**Source:** Split from E04 2026-08-04; Fail condition broadened 2026-08-06; Care Ops workstream rule added 2026-10-13 (Danny's decision)
**Added:** 2026-08-04 (amended 2026-10-13)

---

### E26: Orphaned Design-Decision Belief

**Pass:** Every design decision that rests on a material belief (disputed by a stakeholder in the inputs, or one that would change a story, metric, or rollout decision if false) has that belief as its own Risks row. Ordinary facts behind a rationale stay inline.
**Fail:** A decision's rationale (an Out of scope exclusion, a Non-goal, a story choice) rests on a material belief that never appears in the Risks table.
**Check type:** LLM judge

```judge
Criterion: Does every design decision that rests on a MATERIAL belief have that belief stated as its own Risks row?
Pass definition: For each rationale attached to a design decision elsewhere (Out of scope rows, Non-goals, story choices, rollout choices), any belief it depends on that clears the materiality bar appears as a Risks row. Ordinary facts behind a rationale (a UI convention, a well-known process fact) are correctly left inline. That is a Pass, not a gap.
Fail definition: At least one decision's rationale rests on a belief that clears the materiality bar but exists only inline, never as a Risks row.
Note: the quality of rows already in the Risks table is E23's check. Both share the same materiality bar, so a belief this eval would promote must survive E23 once promoted. Do not flag every unstated premise.
```

**Examples:**
- Pass: Out of scope: "Non-app patients, see Risks (half of submits happen on web, so the launch addresses about half the opportunity)." The belief has its own Risks row.
- Pass: A story states inline that "Prescribe and Refer drawers already auto-populate a snippet today," with no Risks row. It is an ordinary product fact.
- Fail: Out of scope excludes non-app patients "because most patients use the app," a contested belief that never appears in Risks.

**Source:** Split from E04 2026-08-04; materiality bar added 2026-08-14; promotion target moved to the Risks table 2026-10-13
**Added:** 2026-08-04 (retargeted 2026-10-13)

---

### E28: Section Presence and Order

**Pass:** Every required section is present, in template order, with the template's required table columns. Optional sections may be absent.
**Fail:** A required section is missing, sections are out of order, a header is renamed, or a required table column is missing or renamed.
**Check type:** Code

```check
Type: structural
Source field: Header and column list from Templates/PRD-Template.md
Target field: All "## " and "### " headers and the header rows of the story, metrics, rollout, risks, dependencies, and open questions tables
Logic: (1) Required "## " headers, in this order: Approvals, TL;DR, What problem are we solving?, How will we know it worked?, What are we building?, How does it roll out?, What could go wrong?. Optional, but in template position when present: What are we not doing? (after How will we know it worked?), What do we need from others?, What's still open?, Appendix, Revision markers, then Change log (last; present only once the PRD is shared). Required "### " under How will we know it worked?: Goals, then Metrics. Required "### " under What are we building?: User stories. Optional "### ": Non-goals, Out of scope, Alternatives considered. "#### " headers that group stories under User stories are allowed. FAIL on a missing required header, a renamed header, or any header out of order. (2) Required columns: story table `ID · P | User story | Today | What good looks like`; metrics `Type | Metric | Baseline | Target | Source`; rollout `Stage | Audience | Exit criteria`; risks `Risk | Mitigation | Owner`; dependencies `Dependency | Owner | What we need | Blocks launch?`; open questions `# | Question | Why it matters | Owner | Needed by`. FAIL on a missing or renamed column in any table that is present.
```

**Examples:**
- Pass: All required sections in order; Dependencies omitted because there are none.
- Fail: The story table drops the Today column.
- Fail: "What could go wrong?" appears before "How does it roll out?"

**Source:** Template structure; template rule 11 (the Today column carries current state for cold readers)
**Added:** 2026-10-13

---

### E29: Unfilled Template Residue

**Pass:** No template scaffolding survives: no placeholders, no "N/A," no HTML comments, no usage block, no empty sections.
**Fail:** Any template scaffolding or empty section survives in the PRD.
**Check type:** Code

```check
Type: absence
Source field: Templates/PRD-Template.md placeholder conventions
Target field: Full document
Logic: FAIL on any of: (1) an angle-bracket placeholder matching <[A-Za-z][^>]*> outside code spans and link targets; (2) "@Name"; (3) the unfilled choice strings "Draft / In review / Approved" or "Yes / No"; (4) the whole word "N/A"; (5) "<!--"; (6) "Template usage"; (7) a "## " or "### " header followed directly by a header of the same or higher level, or by the end of the document, with no content between. A header followed directly by its own lower-level subsection (e.g., "## What are we not doing?" then "### Non-goals") is not empty; the template lays sections out that way. [TBD: ...] and [Assumption: ...] tags are not residue.
```

**Examples:**
- Pass: Every cell is filled or the row is omitted; unknowns read [TBD: needs data].
- Fail: Related docs still shows "| **Mocks** | <Link> |" instead of an empty link cell.
- Fail: "### Out of scope" sits empty above "## What are we building?".

**Source:** Template rule 5 and the usage block's "delete this block and every HTML comment before publishing". Check 7 narrowed 2026-10-26: it failed the template's own section layout in all three Provider Pay revision rounds
**Added:** 2026-10-13 (check 7 narrowed 2026-10-26)

---

### E30: Metric Baseline and Target

**Pass:** Every metrics row has a baseline and a numeric target, or [TBD: needs data] in place of an unknown. A metric that has never been measured may read "None (new metric)" as its baseline.
**Fail:** A metrics row has an empty baseline or target, or a directional target with no number.
**Check type:** Code

```check
Type: pattern
Source field: None
Target field: Baseline and Target cells of the table under "## How will we know it worked?"
Logic: For each data row: the Baseline cell must contain a digit, "[TBD: needs data]", or "None (new metric)" for a metric that has never been measured; the Target cell must contain a digit or "[TBD: needs data]". FAIL if either cell is empty, or if the Target cell has no digit and contains any of "up", "down", "hold", "improve", "maintain", "no regression", "increase", "decrease" (whole words, case-insensitive) without a TBD tag.
```

**Examples:**
- Pass: Guardrail target "no drop below the 92% baseline."
- Fail: Primary target "down"; guardrail target "hold or improve; no regression."

**Source:** Template rule 7; the Galen PRD's metrics table used directional targets (see `references/exemplars.md`)
**Added:** 2026-10-13

---

### E31: AI Launch Elements

**Pass:** For an AI launch, the PRD states all four required elements. For a non-AI launch, the eval passes automatically.
**Fail:** An AI launch is missing one or more of the four elements.
**Check type:** LLM judge

```judge
Criterion: If this is an AI launch (per the Step 0 answer, or the PRD describes AI-generated output reaching providers or patients), does the PRD state all four elements template rule 8 requires?
Pass definition: Not an AI launch; or the PRD has (1) a Guardrail row for clinical quality in the metrics table, (2) rollout stages with exit criteria, (3) a clear statement of who makes the final clinical decision (e.g., "the provider reviews and sends every draft; nothing auto-sends"), and (4) a Fallback line stating what the user sees when there is no AI output.
Fail definition: An AI launch is missing at least one of the four, or states one so vaguely a reader can't tell who decides or what happens without AI output.
Note: whether the guardrail row has a baseline and numeric target is E30's check. Whether the rollout section exists at all is E28's.
```

**Examples:**
- Pass: The metrics table has "Guardrail | Clinical Quality Score"; rollout runs Back data, Shadow, Phased ramp, GA with exit criteria; MSG-01 says the provider explicitly sends every draft; Fallback reads "today's composer, with snippets and typing."
- Fail: An AI drafting launch with no Fallback line and no statement of who sends the message.

**Source:** Template rule 8
**Added:** 2026-10-13

---

### E32: Problem Section Form

**Pass:** The user problem is one POV sentence with evidence. The business problem has evidence. A Feature impact line states the sized impact, and its figure matches the sized-impact source.
**Fail:** The POV form is missing, a problem has no evidence link or Assumption tag, the Feature impact line is missing or has no figure, or its figure doesn't match the sized impact (for example, it states the baseline instead).
**Check type:** Code

```check
Type: pattern and comparison
Source field: Intake transcript (answer to question C1, the sized impact); in revise mode with no C1 answer, the pre-revision copy and the touch list
Target field: Content under "## What problem are we solving?"
Logic: (1) A line starting "**User problem:**" contains "needs a way to" and "because". (2) Between "**User problem:**" and "**Business problem:**" there is at least one markdown link with "://" in its target or an "[Assumption:" tag. (3) A line starting "**Business problem:**" exists, and between it and the next "## " header there is at least one markdown link with "://" in its target or an "[Assumption:" tag. (4) A line starting "**Feature impact:**" follows the Business problem line and contains a digit or "[TBD: needs data]". (5) The figure in the Feature impact line (e.g., "$1.3M") appears in the intake transcript's answer to question C1. In revise mode with no C1 answer, it must match the pre-revision copy's Feature impact figure or a touch-list item that sets it. If no source is routed, report Fail (ambiguous). FAIL if any check trips.
```

**Examples:**
- Pass: "**User problem:** A Weight Loss provider needs a way to act on a complete chart because about two thirds of messaging time goes to collecting information we could gather up front." Then "Evidence:" with a link to the ADS analysis.
- Pass: "**Feature impact:** The change is sized at about $1.3M a year in savings," and the C1 answer gives $1.3M a year.
- Fail: "**Business problem:** Messaging is expensive." No number, no link, and no Feature impact line.
- Fail: "**Feature impact:** $28.8M paid to providers last year." That is the baseline spend; C1 gives $1.3M in savings.

**Source:** Template guidance for the problem section (Danny's decision: one User problem line carrying the POV statement, with evidence for both problems); Feature impact line and sized-impact match added 2026-10-27 (Danny: the quantified impact must be clear, visible, and the right number)
**Added:** 2026-10-13 (retargeted 2026-10-27)

---

### E33: AC Format Leakage

**Pass:** No acceptance-test formatting appears, and every "What good looks like" cell is at most 2 sentences.
**Fail:** Given/When/Then formatting appears anywhere, or a "What good looks like" cell exceeds 2 sentences.
**Check type:** Code

```check
Type: pattern
Source field: None
Target field: Full document; the "What good looks like" column of the story table
Logic: (1) Grep for "**Given**", "**When**", "**Then**", or a line or cell containing the words Given, When, and Then in that order (case-sensitive, whole words). FAIL on any match. (2) For each story row, count sentences in the "What good looks like" cell (same sentence rule as E13). FAIL if any cell exceeds 2. Ignore a trailing revision-marker note (text starting with ➕, 🔄, or ~~) when counting sentences.
Note: testable detail written as ordinary prose (edge cases, states, data capture) is E34's check. Whole embedded documents are E35's.
```

**Examples:**
- Pass: "What good looks like: The provider sees the draft the moment they click into the compose bar. Nothing appears before they act."
- Fail: A cell reading "Given a task with drafts, When the provider clicks, Then the draft appears."

**Source:** Template rule 3; replaces E12 (v2.2's requirement-format check)
**Added:** 2026-10-13

---

### E34: Testable Detail Leakage

**Pass:** The PRD stays at the outcome level. Edge cases, state matrices, data-capture specs, and per-field rules live on the acceptance criteria hand-off list, not in the PRD.
**Fail:** The PRD carries testable, behavior-level detail that belongs in the acceptance criteria doc.
**Check type:** LLM judge

```judge
Criterion: Is every story, rollout row, and section written at the outcome level, with acceptance-criteria-level detail left out?
Pass definition: Stories say what the user gets and why. No section lists edge cases, enumerates UI states, specifies what each record stores, defines per-field validation, or walks through step-by-step interaction rules. In the plan (phase P), such detail sits on the hand-off list.
Fail definition: Any section carries detail a QA engineer would test line by line: edge-case lists, state tables, data-capture field lists, error-handling rules, or multi-step interaction specs.
Note: Given/When/Then formatting and the 2-sentence cap are E33's checks. A whole sub-document embedded in a section (an eval rubric, a sizing model) is E35's. Implementation detail (APIs, schemas) is E09's.
```

**Examples:**
- Pass: "MSG-10 · P1: Every draft shows why it says what it says, and the provider can flag a wrong one."
- Fail: A story listing the four feedback modal states, the required reason field, the stored record's fields, and the cancel behavior.

**Source:** Template rule 3; the Galen PRD put acceptance criteria inside story cells (see `references/exemplars.md`)
**Added:** 2026-10-13

---

### E35: Embedded Sub-Document

**Pass:** Supporting material lives in its own doc, linked from Related docs. Future phases appear as one Out of scope line.
**Fail:** A section embeds a sizing model, an eval rubric, a sub-team's requirements, a dashboard spec, or a future phase in detail.
**Check type:** LLM judge

```judge
Criterion: Does the PRD link supporting documents instead of embedding them, and keep future phases to one line?
Pass definition: Sizing appears as an aggregate number with a link. Eval bars, sub-team requirements, and dashboard specs are links in Related docs. Future phases appear only as Out of scope lines saying where the work lands.
Fail definition: Any section reproduces a sizing calculation, an eval dimension table or rubric, another team's detailed requirements, a dashboard metric spec, or a future phase's stories or design.
Note: behavior-level detail for this launch is E34's check. Duplication of a fact within the PRD is E11's.
```

**Examples:**
- Pass: "Business problem: about $1.8M annualized in Weight Loss messaging cost." Then a link to the sizing doc.
- Fail: A seven-dimension eval rubric with a worked example sits under What are we building?
- Fail: Phase 2's recommendation stories appear in full below this launch's stories.

**Source:** Template rules 1 and 6; the Galen PRD embedded the Ivy requirements, eval dimensions, and Cost & P&L detail (see `references/exemplars.md`)
**Added:** 2026-10-13

---

### E36: Story ID Integrity

**Pass:** Every story ID is a prefix plus a number, unique, with a valid priority. In phase R, no existing ID is renumbered or reused.
**Fail:** An ID is malformed or duplicated, a priority is invalid, or a revision renumbered or reused an ID.
**Check type:** Code

```check
Type: pattern and comparison
Source field: In phase R, the pre-revision copy and the touch list
Target field: The ID · P column of the story table
Logic: (1) Each cell matches ^[A-Z]{2,6}-\d{2,}[a-z]? · P[012]$ (the "·" is the middle dot U+00B7). FAIL on any mismatch. (2) FAIL if any ID repeats. (3) Phase R only: every ID in the pre-revision copy is still present unless the touch list removes it; FAIL if one is missing. FAIL if an ID the touch list removed reappears on a different story. FAIL if a new ID takes a number lower than the highest existing number in its prefix.
```

**Examples:**
- Pass: "MSG-04 · P0" through "MSG-11 · P1," unique; a revision appends MSG-12.
- Fail: "msg4 · High."
- Fail: A revision renumbers MSG-08 to MSG-07 after MSG-07 was cut.

**Source:** Template rule 10; the acceptance criteria doc's Req ID column cites story IDs, so they must stay stable. Revision markers belong at the end of the changed cell, never in the ID · P cell
**Added:** 2026-10-13

---

### E37: Undefined Acronym

**Pass:** Every acronym is defined at its first use.
**Fail:** An acronym appears with no definition at its first use.
**Check type:** Code

```check
Type: pattern and comparison
Source field: None
Target field: Full document, excluding the H1 title line, code spans, link targets, and the ID · P column
Logic: Extract tokens matching \b[A-Z][A-Z0-9&]{1,}\b (2 or more capitals, e.g., EMR, CDS, S2S). Exclude story ID prefixes, P0, P1, P2, the TBD inside `[TBD: ...]` tags, and the allowlist PRD, TL, DR, AI, GA, ID, PM (the regex splits "TL;DR" into TL and DR, so both are listed). For each remaining token, PASS if its first occurrence is immediately preceded or followed by a parenthetical expansion ("Clinical Decision Support (CDS)" or "CDS (Clinical Decision Support)"). FAIL on any token that is not.
```

**Examples:**
- Pass: "Treatment Plan Authority (TPA)" at first use.
- Fail: "S2S lift" in the TL;DR with no expansion.

**Source:** Template rule 11 (cold-reader test). Glossary option removed 2026-10-26 (Danny: no one reads it)
**Added:** 2026-10-13 (retargeted 2026-10-26)

---

### E38: Writing-Pattern Violation

**Pass:** Every hard verification search in `forbidden-writing-patterns.md` and the CLAUDE.md plain-word and filler searches return zero matches.
**Fail:** Any search returns a match.
**Check type:** Code

```check
Type: absence
Source field: forbidden-writing-patterns.md (Hard verification searches) and CLAUDE.md (Plain words, Filler)
Target field: Full document
Logic: Run every row of the Hard verification searches table exactly as specified, including the em dash search, the numeric range regex, and the vague-quantity phrases, with that file's tag exceptions. Then search for the CLAUDE.md plain-word list (utilize, leverage, facilitate, in order to, prior to, subsequently, delve, landscape, ecosystem) and filler list (It's worth noting, It's important to, Needless to say, At this point in time, moving forward, going forward). FAIL on any match. Exclude from the numeric range regex: ISO dates matching [0-9]{4}-[0-9]{2}-[0-9]{2}, M/D/YY and M/D/YYYY dates, story IDs such as MSG-04 (which do not match it), and any match inside a link target or bare URL (for example, a Figma `node-id=1929-6382`).
Note: row 7 (exactly-three parallel lists) is a manual read. The Fidelity judge checks it in phases D and R and reports it as `E38 (row 7)`; `scripts/mechanical_check.py` runs every other row. Either verdict failing fails E38.
```

**Examples:**
- Pass: Zero matches across every search.
- Fail: "We'll ramp over 2 to 4 weeks" (untagged range) and an em dash in the TL;DR.
- Pass: A Figma link whose URL holds `node-id=1929-6382`; the match sits inside a link target.

**Source:** CLAUDE.md pre-delivery checklist; template rule 13
**Added:** 2026-10-13 | **Updated:** 2026-11-02 (URL exclusion; the AI-Recommended Next Actions run failed every round on a Figma node ID)

---

### E39: Surgical Revision

**Pass:** In phase R, the only differences between the pre-revision copy and the revised PRD are the touch-list items and the consequential updates the skill requires (Last updated, and once the PRD is shared, revision markers and one change-log row).
**Fail:** The revision changed anything outside the touch list.
**Check type:** LLM judge

```judge
Criterion: Did the revision change only what the approved touch list names?
Pass definition: Every difference between the pre-revision copy and the revised PRD traces to a touch-list item, an entry in `<run>/touch-list-amendments.md`, an entry in `<run>/outside-edits.md` that Danny chose to keep, the Last updated cell, or, once the PRD is shared, one change-log row. Passages outside the touch list are unchanged word for word. A revision-marker note appended to a changed requirement is part of that touch-list item's change, not a separate deviation.
Fail definition: At least one passage outside the touch list was reworded, reordered, added, or removed.
Note: whether an adopted change was approved at all is E40's check.
```

**Examples:**
- Pass: The touch list fixed MSG-07's priority; only that cell, Last updated, and the change log changed.
- Fail: Fixing MSG-07 also reworded the TL;DR and two Risks rows.

**Source:** Ported from dashboard-requirements (Surgical Revision); CLAUDE.md "Edit surgically"
**Added:** 2026-10-13

---

### E40: Unapproved Adoption

**Pass:** Every reviewer-sourced change in the revised PRD traces to a gate-2 adoption, and every Addition adopted was adopted by Danny by row.
**Fail:** A reviewer finding was applied without a gate-2 adoption, or an Addition was applied under delegated (Defect-only) adoption.
**Check type:** LLM judge

```judge
Criterion: Was every reviewer-sourced change approved at Gate 2, with Additions adopted only by Danny by row?
Pass definition: Each change that traces to a reviewer finding matches a row in gate-2.md marked adopted. Any Addition row applied shows Danny's per-row adoption, not delegated adoption.
Fail definition: A reviewer finding appears in the revised PRD with no gate-2 adoption, or an Addition was applied under delegated adoption, which covers Defect rows only.
Note: whether the revision stayed within the touch list is E39's check.
```

**Examples:**
- Pass: Gate-2 shows Danny adopted finding 3 (a Defect) and finding 7 (an Addition, by row); both appear, nothing else.
- Fail: Danny said "accept the slam dunks," and a new Risks row from a reviewer (an Addition) appears.

**Source:** Ported from dashboard-requirements (Unapproved Adoption); CLAUDE.md "Reviewer findings are candidates, not edits"
**Added:** 2026-10-13

---

### E41: Undefined Internal Label

**Pass:** Every internal label a non-technical cold reader wouldn't know (a phase, program, initiative, team shorthand, or internal nickname) is defined in plain language at its first use.
**Fail:** An internal label appears with no plain-language definition at its first use.
**Check type:** LLM judge

```judge
Criterion: Can a non-technical stakeholder with no context understand every internal label the first time it appears?
Pass definition: Each internal label (a phase name, program or initiative name, team shorthand, or internal nickname) is defined in plain language where it first appears, or is self-explanatory from its own words. Later uses may rely on that first definition.
Fail definition: At least one internal label appears with no plain-language definition at its first use and is not self-explanatory, so a cold reader would have to ask what it means.
Note: all-caps acronyms are E37's check. Common business words and the template's own section names are not internal labels.
```

**Examples:**
- Pass: "The 2027 plan has three phases: crawl (a purpose-built pay application), walk (dynamic pay priced by supply and demand), and run (full pay visibility for providers)."
- Fail: Out of scope says "landing in the 2027 crawl phase," and crawl is defined nowhere in the PRD.

**Source:** Template rule 11 (cold-reader test), extended to internal labels 2026-10-27 (Danny: the Provider Pay PRD used crawl, walk, and run with no context)
**Added:** 2026-10-27

---

### E42: Process as Story

**Pass:** Every user story's What good looks like is met by something the build team ships in the product.
**Fail:** A story is met by a team process, a notice between teams, a reporting commitment, or another team's deliverable rather than shipped product behavior.
**Check type:** LLM judge

```judge
Criterion: Is every user story a piece of product behavior the build team ships?
Pass definition: For each story, the outcome in What good looks like is delivered by product or software the build team ships: a screen, a data change, a system behavior.
Fail definition: At least one story's outcome is delivered by a process (a change notice, a sign-off, a training, a meeting), a reporting commitment, or another team's work. That item belongs in Dependencies, in Out of scope, or out of the PRD.
Note: placement of non-story items (Non-goals, Out of scope, Risks, Dependencies, Open questions) is E04. Whether a Dependencies row is valid is E24. Implementation detail is E09.
```

**Examples:**
- Pass: "The widget shows the period's signed sync visit count."
- Fail: "DPE gets notice before any EMR change that could affect pay ships."
- Fail: "The agreed metrics and guardrails reach the analytics reporting layer, per a companion dashboard requirements doc."

**Source:** Template rule 15; ownership-contract rule "Stories are product behavior" (Danny, 2026-10-27: PIN-04 and PIN-05 in the Provider Pay PRD read as process, not software)
**Added:** 2026-10-27

---

### E43: Requirement Coverage

**Pass:** Every in-scope surface, outcome, and decision a stakeholder would want a say in, from the inputs and intake, has a requirement: a story, rollout stage, fallback, or metric.
**Fail:** An in-scope outcome or stakeholder-level decision in the inputs has no requirement, and it is not listed as out of scope or as an open question.
**Check type:** LLM judge

```judge
Criterion: Is the PRD comprehensive at the requirement level?
Pass definition: Each in-scope surface, user-facing outcome, data commitment to another team, and decision a stakeholder would want a say in (a product choice with user, incentive, clinical, or trust consequences) that the inputs or intake describe appears in a story, rollout stage, the fallback, or a metric. Requirements may stay high level.
Fail definition: At least one such item appears in the inputs, sits in scope, and reached no requirement. It may sit only on the acceptance criteria hand-off list, or nowhere. It is not listed as out of scope or as an open question.
Note: E01 checks that the plan dropped no input at all, and the hand-off list counts as coverage there. E43 checks that requirement-level items reached a requirement, not only the hand-off list. Detail that only elaborates how an existing requirement works belongs on the hand-off list and passes. E03 checks that the goals cover the problem; E43 checks the requirements. E04 checks where a scope item sits; E43 checks that a requirement exists at all.
```

**Examples:**
- Pass: The inputs describe how a failed refresh should behave; the PRD's story says the widget shows when it last refreshed, and the failure behavior sits on the hand-off list as detail of that story.
- Fail: The inputs decide the widget shows no countdown to the next pay tier, a choice with incentive consequences, and it appears only on the hand-off list.

**Source:** Danny, 2026-10-27: the PRD is comprehensive and high level; a decision a stakeholder would want a say in belongs in the PRD, and how an agreed requirement works belongs in the acceptance criteria doc
**Added:** 2026-10-27

---

### E44: Gate Snapshot Completeness

**Pass:** The snapshot for a handoff point carries every decision, modification, and answer in Danny's messages for that point.
**Fail:** Danny's messages hold a modification, decision, or answer the snapshot is missing or has altered.
**Check type:** LLM judge

```judge
Criterion: Could a fresh session resume from this snapshot alone and act on everything Danny said at this point?
Pass definition: Every modification, decision, approval condition, and answer in `<run>/danny-<point>.md` appears in the snapshot with the same meaning. At H0 the snapshot is the intake transcript; at H1 it is gate-1.md (in revise mode, gate-3.md and gate-1.md when written); at H2 it is gate-2.md, with each row's decision and who made it.
Fail definition: At least one item in Danny's messages is missing from the snapshot, or the snapshot changes its meaning: a softened modification, a dropped condition, a decision attributed to the wrong person, or a delegated adoption recorded as a per-row one.
Note: whether a later draft or revision honors the snapshot is E10's, E39's, or E40's check. This eval checks only that the snapshot holds what Danny said.
```

**Examples:**
- Pass: Danny approved Gate 1 with "make MSG-06 a P1 and drop the Shadow stage"; gate-1.md shows MSG-06 at P1 and no Shadow stage.
- Fail: Danny said "adopt 2 and 5, defer 7"; gate-2.md records finding 7 as declined.
- Fail: Danny's intake answer named a $0.4M sized impact; the intake transcript records the answer as "see sizing doc."

**Source:** `AI-Learning/Claude-Code-and-Skills/Token-Spend/skill-plans/prd-generator.md` change 1: a fresh session resumes from the snapshot, so a modification left out of it is lost
**Added:** 2026-11-06

---

### E45: Report Coverage

**Pass:** Each QA report in a round lists exactly the eval IDs `<eval_phase_map>` assigns its group for that phase, once each.
**Fail:** A report is missing an assigned eval, lists an eval its group was not assigned, or lists one twice.
**Check type:** Code

```check
Type: comparison
Source field: SKILL.md <eval_phase_map> (Group and phase columns)
Target field: The Eval column of every <run>/qa-reports/<phase>-round-<n>-<group>.md for the round
Logic: `scripts/qa_round.py verify` parses each report's table rows and compares the Eval column with the group's assigned list (Fidelity in phases D and R also owns `E38 (row 7)`). FAIL on any missing, extra, or repeated ID.
```

**Examples:**
- Pass: The phase D Scope-Content report lists E04, E23, E24, E26, E42, E09, E11, E31, E34, E35, E41, and E47, once each.
- Fail: The phase P Scope-Content report has no E22 row.

**Source:** `AI-Learning/Claude-Code-and-Skills/Token-Spend/skill-plans/prd-generator.md` change 3: judges read per-group brief files, so a dropped eval would not surface on its own
**Added:** 2026-11-06

---

### E46: QA Artifact Integrity

**Pass:** Every launched group wrote one report with a row per assigned eval, and the artifact's checksum is unchanged across the round.
**Fail:** A group's report is missing, a report has no row for an assigned eval, an unexpected report appears, or the artifact changed during the round.
**Check type:** Code

```check
Type: comparison
Source field: <run>/qa-reports/<phase>-round-<n>-checksum.txt, written by `scripts/qa_round.py start` before the round
Target field: The artifact under test and every report file for the round
Logic: `scripts/qa_round.py verify` checks (1) a report exists for every group the phase map assigns this phase, (2) each report has a row for every assigned eval, (3) no other report file for this phase and round exists, and (4) the artifact's sha256 equals the recorded one. FAIL if any check trips. A checksum change exits 2, and the orchestrator stops and tells Danny.
```

**Examples:**
- Pass: Fidelity, Scope-Content, and Mechanical reports all exist for D round 2, and the PRD's checksum matches the one recorded before the round.
- Fail: The PRD's checksum changed between `start` and `verify`, so a QA agent edited it.

**Source:** `AI-Learning/Claude-Code-and-Skills/Token-Spend/skill-plans/prd-generator.md` change 6: QA agents now write their own report files, so nothing else guards report integrity
**Added:** 2026-11-06

---

### E47: First-Read Clarity

**Pass:** A non-technical cold reader understands every prose sentence on one read.
**Fail:** At least one sentence needs a second read, a jump to another section, or knowledge the PRD never gave, to make sense.
**Check type:** LLM judge

```judge
Criterion: Could a non-technical stakeholder with no context understand every prose sentence and table cell sentence on the first read?
Pass definition: Each sentence uses full grammar and plain words, and says what happens and to whom. Labels the reader was given earlier may be reused.
Fail definition: At least one sentence fails on first read for any of these reasons: (1) shorthand the reader was never given, such as a stage or section name used as a verb ("passed Back data") or a coined phrase ("clears its bar," "gets the Fallback"); (2) an abstract stand-in for a plain statement ("our regulatory posture"); (3) stacked qualifiers or negations the reader has to untangle; (4) it names a thing without saying what happens ("Keeps the LLM to the rationale, which narrows what Legal reviews"); (5) it only makes sense after following a "(see X)" pointer, when one plain clause would have done. Quote each failing sentence and name its reason.
Note: undefined acronyms are E37's check, and undefined internal labels at first use are E41's. A point repeated in two sections is E11's. Required tags (`[TBD: ...]`, `[Assumption: ...]`) and template field names are not failures. Judge only clarity, not whether the content belongs in the PRD.
```

**Examples:**
- Pass: "A recommendation only shows when the model has already proven accurate for that action on past visits and is confident about this patient."
- Fail: "The action type has passed Back data, and the model's confidence on this task clears that type's threshold." A rollout stage name is used as a verb, and the reader has to work out what passing it means.
- Fail: "It shows no confidence score, and neither its fixed nor its AI-written text says the system 'recommends' or presents the action as the default." The stacked negation takes two reads.

**Source:** Danny, 2026-11-18: the AI-Recommended Next Actions PRD packed its content into dense, jargon-heavy sentences; his Feature X brief is the target. Patterns in `forbidden-writing-patterns.md`, Compression slop
**Added:** 2026-11-18

---

## Retired Evals

| ID | Name | Retired | Absorbed Into | Rationale |
|----|------|---------|---------------|-----------|
| E19 | Cross-Requirement Duplication | 2026-08-04 | E11 | E19's scope (duplication across requirements, appendix, and prose) was a subset of E11's failure mode; running both tripled judge load on one defect and produced correlated verdicts |
| E06 | Missing Edge Cases | 2026-10-13 | None (acceptance criteria doc) | Edge cases live in the acceptance criteria doc; the v3.0 PRD has no Edge Cases section |
| E07 | Edge Case Confusion | 2026-10-13 | None (acceptance criteria doc) | No Edge Cases section exists to confuse with requirements |
| E08 | Bad RBAC Naming | 2026-10-13 | None | The Care template has no RBAC section; RBAC naming was a pharmacy convention |
| E12 | Prose-Heavy Reqs | 2026-10-13 | E33 | No R-###.# requirement bullets in v3.0; E33 checks the story table's 2-sentence cap and Given/When/Then leakage |
| E16 | Prototype Visual Missing | 2026-10-13 | None | No Prototype section; the Figma or prototype link lives in Related docs, and screenshots in the optional Surface table |
| E17 | Redundant ASCII | 2026-10-13 | None | No Prototype section, so no ASCII-versus-URL redundancy to check |
| E20 | Prototype UX Gap | 2026-10-13 | None (acceptance criteria doc) | UI-interaction coverage belongs to the acceptance criteria doc, whose generator inspects the prototype |
| E25 | Prototype Section Verbosity | 2026-10-13 | None | No Prototype section to pad |
| E27 | Body Length | 2026-10-26 | None | Danny removed the word cap: the 2,400-word limit truncated the Provider Pay PRD until parts no longer made sense. Altitude is set by template rule 2 and reviewed at the gates, not counted |
