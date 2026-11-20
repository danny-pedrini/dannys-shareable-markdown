# Evals: acceptance-testing-generator

28 of the 29 evals are **generalization** evals: they check produced output, not prompt clarity. H2 is
the exception: it checks the eval script itself. IDs use
family prefixes (A through H) rather than one sequential run, because the families map to
distinct failure classes and the grouping is what makes a failing run diagnosable. Family letters are
stable keys for the invocation log and traces.

**Granularity:** per-step and per-output. Eval Gates 1 and 2 run mid-workflow on the requirement
inventory and the draft tests. The full suite runs at Step 11 against the finished document.

**Count:** 29 evals. A1 to A5 (5), B1 to B5 (5), C1 to C2 (2), D1 to D2 (2), E1 to E5 (5), F1 to F3 (3),
G1 to G4 (4), H1 to H3 (3).

**Judge cost:** 14 evals call a judge every applicable run. B1, B5, C2, A4, D1, D2, G4 and H1 are pure
judge; A5, B3, E4, G1, G2 and G3 are code-prefiltered then judged. A2 and A3 were downgraded to code
by comparing against the Step 5 inventory instead of re-reading the source. F1 to F3, H2 and H3 are pure code.

**Code checks run in `scripts/code_evals.py`.** The script reads this file's Active Evals table as its
ID list, runs every code eval and code prefilter, and prints the judge candidates. A definition edit
here updates the script in the same change.

**QA overlap:** `references/qa-subagent.md` covers A1 through E5 (19 checks) because those are the ones
with bounded correction scope. F1 to F3, G1 to G4, and H1 to H3 are eval-runner only. F evals are mechanical and
fixing them means renumbering; G evals are source-fidelity and model-fidelity findings, where the fix
is a re-read or a question to Danny, not an edit QA can make unsupervised.

**Conditional evals:** D1 and D2 run only when an implementation source was consulted. A3 runs only
when the requirements declare non-goals or out-of-scope items. F2 runs only on a multi-source run. F3 runs only on a
revision of a document already shared with Design and Eng. A5 runs on every document, because it checks both a missing exclusion section on an AI
feature and a spurious one on a feature without AI behavior. H1 runs only when the run started from a
handoff or STATUS.md. H3 runs only on a UAT run, after the Step 13 trace copy. F1, G1 to G4, and H2
run on every document.
Skipped evals are recorded as skipped (`S`), never as passed.

**The G family exists because a document can pass everything else and still be wrong.** A1 to F3 check
that the document is internally sound, traceable, and well formed. The 2026-09-18 run passed every one
of them that ran and still had to be rebuilt, because its model of the product was wrong and two of
its source attributions said the opposite of what the source said. G1 and G2 check fidelity to sources; G3 checks
the document against itself; G4 checks the document against a model Danny confirmed.

---

## Active Evals

| ID | Name | Type | Check | Added | Last Result |
| --- | --- | --- | --- | --- | --- |
| A1 | Untraced requirement | Generalization | Code | 2026-08-30 | Pass (2026-11-05) |
| A2 | Missing degraded-path coverage | Generalization | Code | 2026-08-30 | Skipped (2026-11-05, Step 5 inventory not retained) |
| A3 | Out-of-scope test | Generalization | Code | 2026-08-30 | Skipped (2026-11-05, Step 5 inventory not retained) |
| A4 | Duplicate coverage | Generalization | Judge | 2026-08-30 | Pass (2026-11-05) |
| A5 | AI-quality scope leak | Generalization | Code + Judge | 2026-08-30 | Pass (2026-11-05) |
| B1 | Invented requirement | Generalization | Judge | 2026-08-30 | Fail (2026-11-05, test 5 "adjustments" and quality-bonus location have no PRD basis; pre-existing) |
| B2 | Invented threshold | Generalization | Code | 2026-08-30 | Pass (2026-11-05) |
| B3 | Terminology drift | Generalization | Code + Judge | 2026-08-30 | Pass (2026-11-05) |
| B4 | Retrieval failure absorbed | Generalization | Code | 2026-08-30 | Pass (2026-11-05) |
| B5 | Unstated stakeholder decision | Generalization | Judge | 2026-10-27 | Fail (2026-11-05, test 5a forbids copy saying counts may be wrong; no PRD requirement or flagged gap) |
| C1 | Non-binary test | Generalization | Code | 2026-08-30 | Pass (2026-11-05) |
| C2 | Wrong altitude for mode | Generalization | Judge | 2026-08-30 | Pass (2026-11-05) |
| D1 | Source precedence violation | Generalization | Judge | 2026-08-30 | Pass (2026-11-05) |
| D2 | Fixture data as requirement | Generalization | Judge | 2026-08-30 | Pass (2026-11-05) |
| E1 | Format drift | Generalization | Code | 2026-08-30 | Pass (2026-11-05) |
| E2 | Test ID integrity | Generalization | Code | 2026-08-30 | Pass (2026-11-05) |
| E3 | Required section absent | Generalization | Code | 2026-08-30 | Pass (2026-11-05) |
| E4 | PHI or real patient data | Generalization | Code + Judge | 2026-08-30 | Pass (2026-11-05) |
| E5 | Writing-pattern violation | Generalization | Code | 2026-08-30 | Pass (2026-11-05) |
| F1 | Broken cross-reference | Generalization | Code | 2026-08-30 | Pass (2026-11-05) |
| F2 | Section prefix collision or drift | Generalization | Code | 2026-08-30 | Skipped (2026-11-05, single-source Comprehensive run) |
| F3 | Revision marker incomplete | Generalization | Code | 2026-08-30 | Pass (2026-11-05, after the Change log named what changed in tests 4, 10, 11, 14, and 17) |
| G1 | Misquoted source | Generalization | Code + Judge | 2026-09-19 | Pass (2026-11-05) |
| G2 | Source directive inverted | Generalization | Code + Judge | 2026-09-19 | Pass (2026-11-05) |
| G3 | Meta-table contradicts its test | Generalization | Code + Judge | 2026-09-19 | Pass (2026-11-05) |
| G4 | Unconfirmed model assumption | Generalization | Judge | 2026-09-19 | Pass (2026-11-05) |
| H1 | Handoff decision dropped | Generalization | Judge | 2026-11-06 | Not yet run |
| H2 | Code eval missing from the script report | Tooling | Code | 2026-11-06 | Not yet run |
| H3 | UAT rules not loaded | Generalization | Code | 2026-11-06 | Not yet run |

---

## Definitions

### A1: Untraced requirement

**Pass:** every in-scope requirement ID is accounted for. Comprehensive: in the Req ID column, or in
the working coverage table as an explicit gap with a reason. UAT: cited by at least one test, or named
in the Scope section as verified outside the document with who verifies it.
**Fail:** any in-scope requirement ID is accounted for in neither place.
**Check type:** Code-based

```check
Type: comparison
Source field: requirement IDs in the source document, filtered to the declared in-scope set
Target field: Comprehensive, the Req ID column plus the coverage traceability table. UAT, the inline
  citations in the Validation column plus the Scope section.
Logic: Extract requirement IDs from the source with a pattern matching the source's own ID scheme
  (e.g. grep -oE '\b(CC|IVY|REC|CDS|MSG|DI)-[0-9]{2}\b' | sort -u), then narrow to the in-scope set.
  Every in-scope ID must appear in the target set. Report any missing ID by name.
Note for BOTH modes: the coverage table is a working section and is NOT in the document. Grade
  against the version the generating thread reported in chat, and, for Comprehensive, against the
  published Req ID column. Never Fail a document of either mode for lacking a coverage table.
```

**Source:** Failure-mode audit of the prior skill, plus Care requirement structure. **Added:** 2026-08-30
**Notes:** the single most consequential eval. Care requirements ship with IDs, so this is fully mechanical.

### A2: Missing degraded-path coverage

**Pass:** every fallback, below-threshold, no-consent, no-response, timeout, service-down, or
"as it does today" path named in the requirements has a test exercising it.
**Fail:** any such path is named in the source with no corresponding test.
**Check type:** Code-based, against the Step 5 inventory

Step 5 produces an inventory with a "Degraded paths named" column, and Eval Gate 1 independently
verifies that column against the source. So the semantic extraction is already done and verified.
This eval compares two structured artifacts rather than paying a judge to re-read the source.

```check
Type: comparison
Source field: the "Degraded paths named" column of the Step 5 requirement inventory
Target field: the output's tests
Logic: For each degraded path listed in the inventory, confirm at least one test exercises it. Match
  on the requirement ID plus a distinguishing keyword from the path description (no consent, no
  response, timeout, service down, below threshold, unconfigured, as it does today, BAU). Report any
  inventory-listed path with no matching test, by requirement ID and path.
Prerequisite: the Step 5 inventory must be retained for this run. If it was not, this eval cannot run
  as code. Record it as skipped and say why rather than silently passing.
```

**Source:** Care-specific. Galen requirements define degraded paths heavily and they are the
most-skipped coverage. Downgraded from Judge to Code after the evals-advisor noted Step 5 already
structures this data. **Added:** 2026-08-30

### A3: Out-of-scope test

**Pass:** no live test traces to a non-goal or out-of-scope item; every test traces to a PRD requirement
(a user story, rollout stage, or the fallback) or a PRD metric. Both modes.
**Fail:** a live test exists whose purpose is confirming a non-goal or out-of-scope item is absent, or a
test cites a non-goal or out-of-scope item as its Req ID.
**Check type:** Code-based, against the Step 5 inventory. **Skipped when** the requirements declare no
non-goals and no out-of-scope items.

```check
Type: comparison
Source field: the "Non-goal or out of scope" column of the Step 5 requirement inventory
Target field: the test table. Comprehensive, the Req ID and Area/Theme cells. UAT, the Area/Theme cell
  and the inline requirement citation.
Logic: Ignore struck rows (~~...~~). FAIL if any live test's Req ID or inline citation reads "Out of
  scope", "Non-goals", or names an inventory non-goal or out-of-scope item instead of a requirement or
  metric. FAIL if any live test's Area/Theme names scope verification or an absence check on an
  inventory item ("Scope - No ..."). Match on keyword overlap rather than one-to-one. A clinically
  weighty exclusion that the PRD also states as a requirement traces to that requirement's ID and
  passes. An in-scope test that encodes a decision the PRD never states is B5, not this eval.
Prerequisite: same as A2. If the inventory was not retained, record as skipped with the reason.
```

**Source:** Prior skill quality check that was missing from the initial failure-mode list. Downgraded
from Judge to Code alongside A2. Retargeted 2026-10-27: Danny ruled scope-verification tests overdone;
acceptance tests map only to the PRD's requirements and metrics. **Added:** 2026-08-30 (retargeted
2026-10-27)

### A4: Duplicate coverage

**Pass:** no two tests validate the same requirement behavior, and permutations of one behavior are consolidated.
**Fail:** two or more tests are near-duplicates, or permutations that the consolidation rules say to merge appear as separate rows.
**Check type:** LLM judge

```judge
Criterion: Is any behavior tested more than once, or split into permutations that should be one test?
Pass definition: Each test validates a distinct behavior. Permutations of a single rule appear in one row.
Fail definition: Name the duplicate or splittable test numbers and the behavior they share.
```

**Source:** Prior skill deduplication rules. **Added:** 2026-08-30

### A5: AI-quality scope leak

**Pass:** no test measures model accuracy, output correctness, eval pass rate, gold-set performance,
or clinical appropriateness of generated output. The AI-scope exclusion (one line in Purpose in
Comprehensive, one bullet under Out of scope in UAT) is present when the feature has AI behavior, and
absent when it does not.
**Fail:** any such test exists, OR the exclusion section is absent on an AI feature, OR the exclusion
section is present on a feature with no AI behavior.
**Check type:** Code-based screen, then LLM judge. **Runs on every document**, because the
spurious-inclusion half applies specifically to non-AI features.

```check
Type: absence
Target field: Validation and Behavior column
Logic: grep -noiE 'pass rate|gold set|clinically appropriate|clinically correct|accuracy|precision|recall|
  judge score|eval score|model quality|correct recommendation' on the output. Any hit inside a test row
  is a candidate. Then judge whether the hit measures the model or describes a mechanism.
  Then confirm the AI-scope exclusion exists (Comprehensive: a Purpose line; UAT: an Out of scope
  bullet) if and only if the Step 5 AI-behavior
  determination was positive. Present on a non-AI feature is a Fail: it is boilerplate that tells a
  stakeholder a gap exists where none does.
```

**Source:** Danny, 2026-08-30. AI output failure analysis and eval measurement are handled separately from acceptance testing. **Added:** 2026-08-30
**Notes:** the distinction is mechanism versus measurement. "The gate blocks below threshold" passes. "The pass rate is at least 90 percent" fails.

### B1: Invented requirement

**Pass:** every test traces to the requirements or to a consulted implementation source. Tests that add
detail beyond the requirements appear in the Tests beyond the requirements working list, with their
origin.
**Fail:** a test asserts behavior with no source basis and is not disclosed.
**Check type:** LLM judge

```judge
Criterion: Does every test trace to a real source, with undisclosed additions flagged?
Pass definition: Each test maps to source content, or is listed in the Tests beyond the requirements working list (working-sections file) with its origin.
Fail definition: A test asserts behavior no source supports and is not disclosed. Name it.
```

**Source:** Prior skill. **Added:** 2026-08-30

### B2: Invented threshold

**Pass:** every number, percentage, duration, latency figure, count, or size used as a pass condition
appears in the source, or is tagged `[Assumption: X (needs validation)]`.
**Fail:** any untagged numeric pass condition absent from the source.
**Check type:** Code-based

```check
Type: comparison
Source field: numeric values in the source
Target field: numeric values in the output's Validation and Behavior column
Logic: Extract numerics with units or percent signs from the output test rows
  (grep -noE '[0-9]+(\.[0-9]+)?\s*(ms|s|sec|second|minute|min|hour|day|%|percent|character|item)'), then
  confirm each appears in the source. Test numbers, requirement IDs, and dates are exempt. Values tagged
  [Assumption: or [estimate range] are exempt.
```

**Source:** Prior skill hard constraint. **Added:** 2026-08-30
**Notes:** performance tests with no stated threshold must read "within acceptable time".

### B3: Terminology drift

**Pass:** tests use the source's own terms for features, statuses, surfaces, and data elements.
**Fail:** a test renames a source term, invents a status value, or substitutes a synonym.
**Check type:** Code-based prefilter, then LLM judge

Building a term list from arbitrary requirements is semantic extraction, not grep. The code half
narrows the candidates; the judge half decides whether each candidate is a real substitution.

```check
Type: presence
Source field: distinctive nouns and status values in the source
Target field: output test rows
Logic (code prefilter): Extract candidate terms from the source: all-caps or snake_case status values
  (grep -oE '\b[A-Z][A-Z_]{3,}\b'), backticked terms, and bolded noun phrases. For each, report
  whether it appears verbatim anywhere in the output. A source term that never appears verbatim is a
  candidate substitution. Also grep the output for the known Care substitution pairs below.
```

```judge
Criterion: Does the output substitute a synonym where the requirements use a specific term?
Pass definition: Every candidate flagged by the prefilter is either absent because that requirement
  is genuinely out of scope, or present verbatim where it refers to that thing.
Fail definition: A test refers to a source concept using a different name. Name the source term, the
  substituted term, and the test number.
Known Care substitution risks: summary card for center pane; chart validator for completeness check;
  queued for held; clinical rules for codified definition; recommendation for next action.
```

**Source:** Prior skill quality check ("column and field names match PRD exactly"), reclassified from
Code to Code plus Judge after the evals-advisor found the term-list step is not mechanizable.
**Added:** 2026-08-30

### B4: Retrieval failure absorbed

**Pass:** every source that failed retrieval is marked with a `[Source unreadable` placeholder plus a
link or resource ID, and no content attributed to it appears in the output.
**Fail:** content appears that no successfully retrieved source could have supplied, or a failed source is unmarked.
**Check type:** Code-based

```check
Type: presence
Target field: whole output document, plus the run's retrieval record
Logic: If the run recorded any retrieval failure, confirm a matching [Source unreadable placeholder
  exists with an adjacent link or ID. Confirm no section cites the failed source as its basis.
  If the run recorded zero failures, this eval passes trivially.
```

**Source:** Danny, 2026-08-30. Hard stop on retrieval failure. **Added:** 2026-08-30

### B5: Unstated stakeholder decision

**Pass:** every test that encodes a decision a stakeholder would want a say in traces to a PRD
requirement that states that decision, or the decision is listed as a candidate requirement (the
Potential requirement gaps working list in the working-sections file, Comprehensive; the Step 14 chat
summary in UAT).
**Fail:** a test encodes such a decision, meaning a product choice with user, incentive, clinical, or
trust consequences, that no PRD requirement states and that is not flagged as a candidate requirement.
**Check type:** LLM judge. Runs on every document.

```judge
Criterion: Does any test introduce a decision a stakeholder would want a say in that the PRD never states?
Pass definition: Each test either elaborates how an agreed PRD requirement works (states, edge cases,
  labels, error handling, accessibility, design fidelity), or encodes a stakeholder-level decision that
  a PRD requirement states, or encodes one that the document flags as a candidate requirement.
Fail definition: At least one test encodes a stakeholder-level decision, such as whether to show a
  number, nudge a behavior, or restrict who sees what, that no PRD requirement states and that is not
  flagged as a candidate requirement.
Note: detail that elaborates how an agreed requirement works passes; this eval targets new decisions,
  not depth. Invented behavior with no source at all is B1. Invented thresholds are B2. A test for an
  out-of-scope item is A3; this eval concerns in-scope decisions the PRD left unstated.
```

**Examples:**
- Pass: a test requires that a failed refresh keeps the last good figures and never shows zeros. It
  is how the PRD's "shows when it last refreshed" requirement works.
- Fail: a test requires no countdown to the next pay tier, a choice with incentive consequences, when
  no PRD requirement says so and the document doesn't flag it.

**Source:** Danny, 2026-10-27: the PRD is comprehensive and high level; a decision a stakeholder would
want a say in belongs in the PRD, and how an agreed requirement works belongs in the acceptance
criteria doc. **Added:** 2026-10-27

### C1: Non-binary test

**Pass:** every validation cell can be answered Pass or Fail by its executor without interpretation.
**Fail:** any cell contains an unqualified judgment.
**Check type:** Code-based

```check
Type: absence
Target field: Validation and Behavior column
Logic: grep -noiE 'works correctly|works as expected|behaves as expected|behaves properly|
  is accurate|is correct|performs well|is intuitive|is user.friendly|is reliable|
  functions correctly|as appropriate|handled properly|displays correctly' on test rows.
  Every hit is a Fail. No exceptions.
```

The phrase list is deliberately narrow so there is no carve-out to judge. Each listed phrase is
unsalvageable on its own terms: a cell containing it is asserting a verdict rather than an observation,
even if it also states a real condition elsewhere. Rewrite the phrase, keep the condition.

Words like "properly", "successfully", and "good" are excluded from the list because they appear
legitimately ("successfully scan the label", "a good-faith reply"). Catching them would require the
same judgment call this eval exists to avoid.

**Source:** Prior skill. **Added:** 2026-08-30

### C2: Wrong altitude for mode

**Pass:** test granularity matches the mode.
**Fail:** Comprehensive contains vague multi-step scenarios where detail was available. UAT contains
single-field display checks, exact copy verification, event schema validation, or single modal close paths.
**Check type:** LLM judge

```judge
Criterion: Does each test's granularity match the declared mode?
Pass definition: Comprehensive tests are specific and field- or state-level. UAT tests are journeys a
  non-technical executor can run end to end.
Fail definition: Name each test whose altitude is wrong and say which mode it belongs to.
```

**Source:** Prior skill altitude calibration. **Added:** 2026-08-30

### D1: Source precedence violation

**Pass:** conflicts resolve according to the precedence declared at intake, and the precedence is
recorded: in the trace and the Step 14 chat summary always, and in UAT also in the document's
precedence sentence. A Comprehensive document publishes no precedence sentence under either precedence.
**Fail:** a conflict resolves against the declared precedence, the precedence is missing from the
trace or the chat summary, a UAT document omits its precedence sentence, or a Comprehensive document
publishes one.
**Check type:** LLM judge. **Skipped when** no implementation source was consulted.

```judge
Criterion: Do tests resolve conflicts according to the precedence this run declared?
Precedence for this run: [requirements win | mocks win]. This must be supplied. If it was not, record
  the eval as skipped rather than assuming requirements-win.
Pass definition, requirements win: every conflict is disclosed in the working discrepancy list (working-sections file) and resolved to the requirement, or to
  the implementation source with an explicit note that the requirements are silent.
Pass definition, mocks win: tests follow the mocks where they differ from the PRD, and the chat
  summary states the precedence and lists the superseded PRD statements (UAT also states it in its
  precedence sentence). The absence of a discrepancy table is CORRECT under this precedence and is not
  a failure.
Fail definition: a test resolves a conflict against the declared precedence, or the precedence is
  never stated where the mode requires it (the chat summary always; UAT also in the document), leaving
  a reader to guess.
```

**Source:** Prior skill ("PRD is source of truth", "flag discrepancies explicitly"). **Added:** 2026-08-30

### D2: Fixture data as requirement

**Pass:** no test asserts a hardcoded prototype sample value.
**Fail:** a test asserts a sample patient name, dose, date, vital, medication name, or message string
that is placeholder data rather than specified behavior.
**Check type:** LLM judge. **Skipped when** no prototype was consulted.

```judge
Criterion: Does any test assert a prototype fixture value?
Pass definition: Tests assert specified behavior. Where an example value appears, it is illustrative
  and the pass condition does not depend on it.
Fail definition: A test's pass condition depends on a value that exists only as prototype sample data.
```

**Source:** New, from adding prototype code as an input. **Added:** 2026-08-30

### E1: Format drift

**Pass:** the column set matches the mode, every row has a value in every required column, and no
category header row is empty of tests.
**Fail:** wrong columns for the mode, a blank required cell, or an empty category header.
**Check type:** Code-based

```check
Type: structural
Target field: the acceptance tests table
Logic: Confirm the header row matches the mode's column set exactly.
  Comprehensive: 6 columns (Test #, Req ID, Area/Theme, Requires Design, Validation and Behavior,
    Pass/Fail Note). For each test row, confirm Req ID is non-empty and Requires Design is Yes or No;
    on category header rows Requires Design is blank.
  UAT: 4 columns (Test #, Area/Theme, Validation and Behavior, Pass/Fail Note).
  Both: Fail if an environment, Setup By, or Executed By column was added. Those belong in the
    environment statement (Purpose in Comprehensive, the Execution section in UAT), not on a row.
  Execution section: in UAT, confirm it exists and states an environment. In Comprehensive, confirm
    the environment is stated exactly once, in Purpose, and that no Execution section exists. For UAT, confirm a document-level
    Setup By drawn from {Eng, Eng/QA, Ivy Team, Care Ops, Clinical} and a document-level Executed By
    drawn from {Provider, Clinical Ops, Care Ops QA, Eng, Design, Care Ops and providers}. A
    per-section pair is allowed but not required, and when present must carry a stated reason.
  Exception tags: every bracket tag in an Area/Theme cell must be one of the closed six
    {[Staging], [UAT], [Prod], [Design], [Clinical], [Eng]}. Fail on a tag outside that set.
    Every tag must be interpretable from the environment statement (Purpose in Comprehensive, the
    Execution section in UAT), by either of two means: a legend table,
    or prose that names what the tag departs from. A legend table is optional, not required. Fail only
    when a tag's meaning appears in neither. If a legend table IS present, Fail on a legend entry no row
    uses, since that is stale scaffolding.
    In Comprehensive mode, also Fail on an executor tag ([Design], [Clinical], [Eng]), since that mode
    has no ownership table for them to override.
  Redundant tags: Fail on any tag that restates the document default. If the environment is Staging, a
    [Staging] tag is noise. If a whole section is declared Eng-executed in prose, an [Eng] tag on its
    rows is noise. The tag vocabulary marks exceptions, not defaults.
  Both: confirm each bold category header row is followed by at least one test row, and that no test
    row has an empty Validation and Behavior cell.
```

**Source:** Prior skill format checks. **Added:** 2026-08-30

### E2: Test ID integrity

**Pass:** IDs are sequential within their scheme and unique. Before the doc is shared, they run with no
gaps. After it is shared, no ID was renumbered or reused.
**Fail:** an unexplained gap, a duplicate ID, or a test renumbered or reused after sharing.
**Check type:** Code-based

```check
Type: pattern
Target field: Test # column
Logic: Extract IDs in order. Confirm uniqueness. Not yet shared (per the intake answer): confirm the
  sequence has no gaps, since removed tests are deleted and the rest renumbered. Shared: allow sub-IDs
  (22a after 22) and struck rows that retain their number, diff against the prior shared version, and
  confirm no existing ID changed meaning or was reused.
```

**Source:** Prior skill E2E criterion, plus Danny's sub-ID convention. Before/after-sharing rule added 2026-10-27 (Danny: delete and renumber while first building; strike once iterating with Design and Eng). **Added:** 2026-08-30

### E3: Required section absent

**Pass:** all sections required for the mode are present with content.
**Fail:** any required section missing or empty.
**Check type:** Code-based

```check
Type: structural
Target field: output section headers
Logic:
  Comprehensive requires: Purpose (with the environment line), "The model these criteria assume",
    Acceptance Tests, test data requirements, test environment prerequisites, sign-off criteria, and
    revision markers.
  Comprehensive must NOT contain: Source blocks, Execution, Scope, a Source precedence section, a
    precedence sentence, a discrepancy table, Tests beyond the requirements, Potential requirement
    gaps, coverage traceability, key success criteria, an appendix, or a "What is it" section. Those
    are working or omitted per <section_routing>; presence is the Fail.
  Both modes: a Change log is required once the intake records the doc as shared, and is a Fail when
    present on a doc not yet shared.
  UAT requires: Purpose, Execution (with a document-level Setup By and Executed By), Scope, a stated
    source precedence, Acceptance Tests, test data requirements, sign-off criteria, revision markers,
    and at least one launch-readiness or production-smoke test per section.
  UAT must NOT contain: coverage traceability, cross-section dedup notes, candidate requirements,
    test environment prerequisites, key success criteria, an appendix, a "What is it" section, or a discrepancy table.
    Those are working or omitted per <section_routing> in SKILL.md. Presence is the Fail.
  UAT design-verification: required only where a section has a real design surface. Absence is not a
    Fail. A design test on a section with no design surface IS a Fail, since that is the contrived row
    the rule exists to prevent.
  Conditional: AI-scope exclusion when the feature has AI behavior. Comprehensive gets one line in
    Purpose plus an ownership sentence; UAT gets one bullet under Out of scope plus an ownership
    sentence.
  Confirm each required header exists and has non-placeholder content beneath it.
```

**Source:** Consolidates four prior skill checks. **Added:** 2026-08-30

### E4: PHI or real patient data

**Pass:** no real or realistic patient identifier anywhere in the output.
**Fail:** an MRN, member ID, date of birth, address, phone number, email, or a full name presented as
a real patient with clinical detail.
**Check type:** Code-based screen, then LLM judge

```check
Type: absence
Target field: whole output document
Logic: grep for identifier patterns: SSN-shaped, phone-shaped, email-shaped, date-of-birth-shaped,
  and long digit strings. Then judge whether any named person paired with clinical detail is presented
  as a real patient rather than a labeled synthetic example.
```

**Source:** Care-specific. This repo is committed to git. **Added:** 2026-08-30
**Notes:** synthetic examples are fine when labeled as such. Test data sections must state that data is synthetic.

### E5: Writing-pattern violation

**Pass:** zero em dashes, zero untagged numeric ranges, zero forbidden words.
**Fail:** any hit.
**Check type:** Code-based

```check
Type: absence
Target field: whole output document
Logic:
  grep -n "—" "$D"                                       # must be empty
  grep -noE '[0-9]+\s*(to|-)\s*[0-9]+' "$D"             # each hit must carry [estimate range] or [Assumption:
  grep -noiE 'utilize|leverage|facilitate|in order to|prior to|subsequently|delve|landscape|ecosystem|It.s worth noting|moving forward|going forward' "$D"
```

**Source:** `forbidden-writing-patterns.md` and AGENTS.md. The prior skill checked none of this. **Added:** 2026-08-30

### F1: Broken cross-reference

**Pass:** every test ID and section name the document cites resolves to something that exists in the
document, and every PRD open question it cites exists in the PRD.
**Fail:** any dangling citation.
**Check type:** Code-based. **Runs on every document.**

Widened 2026-09-19 from multi-source-only. The 2026-09-18 single-source run carried three dangling
references that nothing caught: "the changed-action guard (test 28)" when it was 29, "Test 40 verifies
the block is carried intact" when it was 41, and three coverage rows pointing at a discrepancy table
that had been removed. Prose cross-references are the common case; `PFX-NN` citations are the rare one.

```check
Type: comparison
Source field: IDs and headings defined in the document, plus the open-question numbers in the PRD named in the metadata block
Target field: IDs and section names cited anywhere in the document
Logic: Build three defined sets.
  (a) Test IDs from the Test # column, sub-IDs included.
  (b) Open-question numbers from the PRD's "What's still open?" table.
  (c) Section names from lines matching '^#{2,3} '.
  Then extract citations and diff each against its set.
  Tests:    grep -onE '\b[Tt]ests? [0-9]+[a-z]?(( ?, ?| and )[0-9]+[a-z]?)*'
  PRD open questions: grep -onE 'PRD Open question [0-9]+'
  Sections: grep -onE '(the|in the|see the) "([^"]{3,40})" section'. That is, only a section name
            the document quotes or backticks. Free prose is NOT checked.
  Every cited test ID must be in (a); every cited PRD open question in (b); every quoted section name in (c),
  compared case-folded with the leading article stripped. Report each dangling citation with its line.
Why the section check is narrow: an earlier draft matched any '(the|in the) <words> (section|table)'.
  It fired on ordinary prose ("the coverage table", "the gap analysis table"), which names tables
  inside sections rather than headings, and it missed the real Title Case references. Enforce an
  explicit citation form instead of trying to parse English.
Note: a "to" range is expanded before matching, and also trips E5, which requires ranges written out.
  Both findings are correct: write them as explicit lists ("tests 18, 19, 20, 21"). The
  [estimate range] tag never exempts an ID range; it is for quantities, not identifiers.
```

**Source:** evals-advisor, 2026-08-30. Widened by evals-advisor 2026-09-19 after three misses in one
single-source run. **Added:** 2026-08-30

### G1: Misquoted source

**Pass:** every double-quoted string attributed to a source appears verbatim in that source.
**Fail:** any quoted string is a paraphrase, a truncation that changes its scope, or absent from the
cited source.
**Check type:** Code-based

Distinct from B1 (invented requirement) and B2 (invented threshold): here the requirement is real, the
source is real, and the quotation marks are the lie. The 2026-09-18 run attributed `"Exact user flow
TBD"` to [AI Eng lead]'s roadmap, which says "The exact user flow still needs to be defined." Only the
independent trace auditor caught it, and only because it re-read the source.

```check
Type: comparison
Source field: the cited source file for each row
Target field: double-quoted spans in the output
Logic: Collect double-quoted spans of 4 or more words from the whole document. There is no Source
  column on a test row, so resolve each span's source in this order:
    1. the gap-list, discrepancy or coverage row it sits in (in the document or the working-sections file), which does carry a source cell;
    2. otherwise the row's Req ID, mapped to the PRD named in the metadata block;
    3. otherwise the nearest preceding `> **Source:**` block, where one exists (UAT working copies),
       else the requirement document itself.
  Resolve that to a local file where one exists (repo paths, and the requirement document itself),
  then `grep -F` the span against it, normalizing curly quotes to straight and collapsing whitespace.
  Any span with no verbatim match is a candidate. A span whose source resolves to something that is
  not a local file (Slack, Confluence, Figma, "Product decision") is reported as unverifiable rather
  than failed; list those separately so Danny can spot-check them.
```

```judge
Criterion: Is this quoted span a citation of a source, or copy the document is specifying?
Pass definition: The span is UI copy, a state name, or a string the document is defining rather than
  quoting from somewhere (a placeholder string, a button label, an error message being specified).
  Those carry no source obligation.
Fail definition: The span is presented as words a source said, and it does not appear verbatim in
  that source. Name the row, the span, and the file searched.
Note: the judge only sees spans the code step could not match. A span that matched verbatim never
  reaches it.
```

**Source:** evals-advisor, 2026-09-19, from the EMR-26 fabricated quotation. **Added:** 2026-09-19

### G2: Source directive inverted

**Pass:** where the output says a source directs an inclusion, exclusion, or deferral, the cited source
directs that same thing.
**Fail:** the output attributes a directive to a source that the source contradicts, or that the source
does not state at all.
**Check type:** Code-based prefilter, then LLM judge

The 2026-09-18 run wrote "E3's two drift cases are excluded per the source." The source says "Fold
those in rather than tracking them twice." The document claimed a source's authority for the opposite
of its instruction, which is worse than an unsourced claim because it survives review.

```check
Type: presence
Target field: whole output document
Logic (code prefilter): grep -noiE 'per the source|the source (says|states|asks|requires|directs|excludes|includes|omits)|as the source|source (calls for|leaves)|deliberately (excluded|omitted) per' on the output.
  Each hit, plus the surrounding sentence and whatever source that row resolves to (the same
  resolution order G1 uses: the row's own source cell, else its Req ID through the metadata block's
  PRD, else the nearest preceding `> **Source:**` block where one exists (UAT working copies), else
  the requirement document itself), becomes a judge candidate.
  Zero hits passes trivially.
```

```judge
Criterion: Does the cited source direct what this sentence claims it directs?
Pass definition: The source passage states, or plainly implies, the same inclusion, exclusion, or
  deferral the sentence attributes to it.
Fail definition: The source directs the opposite, directs nothing on the point, or the sentence
  reverses a "fold this in" into an "exclude this" (or the reverse). Name the sentence, the cited
  source, and quote the passage that decides it.
```

**Source:** evals-advisor, 2026-09-19, from the EMR-21 inversion. **Added:** 2026-09-19

### G3: Meta-table contradicts its test

**Pass:** every claim a coverage, gap-list, discrepancy, or test-environment-prerequisite row makes
about a specific test's content matches that test's actual text, whether the row is published or
working.
**Fail:** any of those rows describes a test in terms the test does not contain.
**Check type:** LLM judge, narrowly scoped

The 2026-09-18 run had the coverage table and the gap table both state that test 19 read "within
acceptable time." It did not; QA found the row unfailable and had to rewrite it. The document
misquoted its own row in two places. Separately, a coverage row said EMR-07's "all three residuals are
open" while the discrepancy table said residual 3 was answered.

```check
Type: comparison
Source field: the acceptance tests table
Target field: coverage, gap-list, discrepancy, and prerequisite rows that cite a test number, in the
  document or the working-sections file
Logic (code prefilter): For each meta-row, in the document and in the working-sections file, extract cited test numbers
  (grep -oE '\b[Tt]ests? [0-9]+[a-z]?'). Pair each meta-row with the full text of every test it cites.
  Only those pairs go to the judge, so the judge reads two table rows, never the document.
```

```judge
Criterion: Does the cited test row contain what this meta-row says it contains?
Pass definition: Every claim the meta-row makes about the test's wording, scope, or coverage is borne
  out by the test's own text.
Fail definition: The meta-row quotes wording the test does not use, claims coverage the test does not
  provide, or contradicts another meta-row about the same test. Name both rows and the conflict.
```

**Source:** evals-advisor, 2026-09-19, from the test 19 self-misquote. **Added:** 2026-09-19

### G4: Unconfirmed model assumption

**Pass:** every criterion that depends on how the product works traces to a statement in the document's
"The model these criteria assume" section, which was confirmed at the Step 1b model interview.
**Fail:** a criterion assumes a behavior, a control's purpose, or a state that the model section does
not state.
**Check type:** LLM judge

This is the eval for the failure that produced the 2026-09-18 rework: six criteria built on a
prototype dropdown read as an AI-message-type selector when it was the snippet picker. Every other
eval passed that document. The model section exists so that the premise is written down where a judge,
and Danny, can check it in one place.

```judge
Criterion: Does every criterion rest on a model statement the document actually makes?
Pass definition: For each test, the behavior it assumes (what a control is for, what states exist,
  what is pre-computed, what the fallback is) is stated in "The model these criteria assume", in a
  cited requirement, OR is listed in the Tests beyond the requirements working list with its origin. That last carve-out
  matches B1's: a derived test is legitimate when it is declared, and G4 must not fail what B1 passes.
Fail definition: A test assumes a product behavior that appears nowhere in the model section or the
  requirements and is not disclosed, most often inferred from a prototype control's appearance. Name
  the test, the assumption, and what the model section says instead.
Prerequisite: the model section must exist. If it does not, this eval fails the whole document and the
  `model_confirmed` gate has been skipped.
```

**Source:** evals-advisor, 2026-09-19, from the snippet-picker misreading. **Added:** 2026-09-19

**Relationship to the `model_confirmed` gate.** Same pattern as A1 and `traceability`: two graders,
deliberately. G4 is run by the generating thread at Step 11 against the document it just wrote; the
gate is audited at Step 13 by a subagent that did not write it and does not know what the run
intended. G4 asks whether the criteria match the model section. The gate asks whether the model
section exists and says something real. Do not collapse them. **If they disagree, the gate wins**, for
the same reason A1 defers to `traceability`: a thread that misread the product while generating can
misread it again while checking.

### F2: Section prefix collision or drift

**Pass:** each section prefix is unique to one requirement document and matches the prefix assigned in
Step 7. Every test ID in a section carries that section's prefix.
**Fail:** two sections share a prefix, a section's tests use a prefix other than its assigned one, or
a prefix changed from the prior published document.
**Check type:** Code-based. **Skipped when** the run used a single requirement document.

```check
Type: pattern
Target field: Test # column, grouped by section heading
Logic: For each section, extract the prefix from its test IDs. Confirm one prefix per section, no
  prefix used by two sections, and every ID within a section sharing that section's prefix. On a
  revision run, diff against the prior document and confirm no prefix changed meaning.
```

**Source:** evals-advisor, 2026-08-30. Multi-source orchestration is a whole workflow branch that had
no eval coverage. **Added:** 2026-08-30
**Notes:** a drifted prefix breaks every ticket and comment that referenced the old ID.

### F3: Revision marker incomplete

**Pass:** every test that differs from the prior shared version carries the correct marker with
its required annotation. ➕ for added, 🔄 with a statement of what changed, ~~struck~~ with why and
where it is covered instead.
**Fail:** a changed, added, or removed test has no marker, or a marker appears without its annotation.
**Check type:** Code-based. **Skipped when** the document has not yet been shared with Design and Eng, since no markers are expected before then.

```check
Type: comparison
Source field: the prior shared version
Target field: the revised document
Logic: Diff the two acceptance tests tables by test ID. For each added ID, confirm a ➕ marker. For
  each ID whose Validation text changed, confirm a 🔄 marker and that the row or a nearby note states
  what changed. For each removed or struck ID, confirm ~~strikethrough~~ plus a reason and a pointer
  to where it is now covered. Report each unmarked or unannotated difference.
```

**Source:** evals-advisor, 2026-08-30. E2 checked ID stability but nothing checked that the marker
legend was actually used, which is the one behavior unique to running this skill twice.
**Added:** 2026-08-30

### H1: Handoff decision dropped

**Pass:** every decision the handoff or STATUS.md lists appears in "The model these criteria assume",
in a cited requirement, or in the Step 14 gap list.
**Fail:** a listed decision appears in none of the three.
**Check type:** LLM judge. **Skipped when** the run did not start from a handoff or STATUS.md.

```judge
Criterion: Did every decision the handoff carried reach the run's output?
Pass definition: Each decision listed in the handoff is stated in the model section, is the substance
  of a requirement a test cites, or is raised in the Step 14 gap list.
Fail definition: Name each handoff decision that appears in none of the three, and the handoff line
  it came from.
```

**Source:** token-efficiency plan change 1, 2026-11-06. A fresh session drops context that never
reached a file, and no other eval checks the handoff itself. **Added:** 2026-11-06

### H2: Code eval missing from the script report

**Pass:** the `scripts/code_evals.py` report lists every active eval whose Check is Code, or Code +
Judge, exactly once.
**Fail:** an active code eval ID is missing from the report or listed twice.
**Check type:** Code-based. Runs on every run.

```check
Type: comparison
Source field: IDs in the Active Evals table whose Check column contains "Code"
Target field: the eval IDs in the script's results table
Logic: The script builds the source set from this file and checks its own report against it. An ID
  with no implementation in the script reports as skipped with that reason, never as passed.
```

**Source:** token-efficiency plan change 3, 2026-11-06. A grep can drift from its prose definition,
and a dropped ID would pass silently. **Added:** 2026-11-06

### H3: UAT rules not loaded

**Pass:** a UAT run's trace lists `references/uat-mode.md` in `context_sources`.
**Fail:** a UAT run's trace omits it.
**Check type:** Code-based. **Skipped when** the run is Comprehensive. Runs after the Step 13 trace copy.

```check
Type: presence
Target field: context_sources in the committed trace
Logic: scripts/code_evals.py --mode uat --doc [path] --only H3 --trace [trace]. Pass when any
  context_sources path ends in references/uat-mode.md.
```

**Source:** token-efficiency plan change 5, 2026-11-06. The UAT altitude rules moved out of `SKILL.md`,
so a UAT run that skips the reference loses them. **Added:** 2026-11-06

---

## Relationship between A1 and the `traceability` process gate

Both check requirement coverage, deliberately, with different graders:

| | A1 (eval) | `traceability` (process gate) |
| --- | --- | --- |
| Who runs it | The generating thread, via Bash at Step 11 | The independent audit subagent at Step 13 |
| Reads | The source and the output | The artifacts only, with no knowledge of what the run intended |
| Purpose | Catch the omission before delivery | Confirm the self-report was honest |

This is defense in depth, not redundancy. **If they disagree, the process gate wins.** A1 is
self-graded, and a thread that missed a requirement while generating can miss it again while checking.
A disagreement is itself a finding: surface it to Danny rather than picking the more convenient answer.

---

## Deferred, from the evals-advisor review

Recommended and not implemented. Cost optimizations, not correctness gaps. Revisit once real run data
shows what judge calls actually cost.

| Recommendation | Why deferred |
| --- | --- |
| Add a code prefilter to B1, C2, A4, and D1 to shrink what the judge reads | Each needs a keyword list tuned against real output. Building one from zero runs would be guesswork |
| Downgrade D2 to a string-presence check against the prototype subagent's FIXTURES list | Sound idea. Needs the subagent's inventory retained across the run, the same way A2 and A3 now retain the Step 5 inventory. Worth doing after the first prototype-backed run |

---

## Process gates

Audited by the trace subagent at Step 13, not run as evals. A gate without evidence is surfaced to Danny.
`trace_integrity` is the exception: the parent checks it after copying the trace, since the auditor
cannot check a copy that does not exist yet.

| Gate | Evidence to look for |
| --- | --- |
| `model_confirmed` | A "The model these criteria assume" section exists and states the happy path, the surface states, what is pre-computed versus on demand, and the fallback. Criteria do not assume a model the section omits |
| `intake_confirmed` | Metadata block populated with the mode's fields (Comprehensive: PRD link, status, product, engineering, and design leads; UAT: mode, author, participants). Not unfilled placeholders |
| `retrieval_integrity` | No content lacking a plausible source. Every `[Source unreadable` placeholder carries a link or ID |
| `traceability` | Requirement ID count in the working-sections file's coverage table matches the source. Reported as found versus expected |
| `mode_consistency` | Column set and altitude match the declared mode |
| `writing_patterns` | Step 9 grep checks return clean |
| `numbering_integrity` | Numbering and marker usage match the run's shared answer: no gaps and no markers or Change log before sharing; struck rows, sub-IDs, no reused numbers, and a Change log row after |
| `trace_integrity` | The committed trace's SHA-256 hash equals the hash the auditor reported. Checked by the parent at Step 13 and reported in the Step 14 summary |
