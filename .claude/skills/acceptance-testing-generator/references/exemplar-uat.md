# Exemplar: UAT Mode

Calibration reference for the `acceptance-testing-generator` skill. Annotated excerpts, not a
complete document.

**These are illustrative.** They are modeled on Galen Phase 1 requirements to show altitude,
structure, and how execution detail is expressed. Do not copy content. Copy the form.

> **Superseded in four places, after the first real run was reviewed.** The illustrative sections below
> still show (1) a per-section ownership table, (2) a design-verification test in every section,
> (3) `Environment: UAT`, and (4) a published document containing every section. All four changed:
> ownership is now one document-level pair; design tests appear only where a section has a real design
> surface; the environment default is **Staging**, because Care has no dedicated UAT environment, which
> also makes the `[Staging]` tag shown below redundant; and roughly half the sections are now working or
> omitted. `<section_routing>` and Step 7 in SKILL.md are authoritative wherever they disagree with what
> follows.
>
> The **altitude** calibration is what this file is actually for, and it still holds exactly. Read the
> test tables for how a UAT scenario is scoped and worded. Read SKILL.md for structure and ownership.

**Audience:** Providers, Clinical Ops, Care Ops. A person who does not read code executes these and
signs off. Every test must be runnable by someone who has the training material and nothing else.

**Assumes:** engineering has already completed integration testing. This document does not repeat
field-level validation.

---

## Column set

Four columns. Nothing else.

```
| Test # | Area/Theme | Validation and Behavior | Pass/Fail Note |
```

Environment and ownership are near-constant across a document, so putting them on every row spends
width to repeat the same value. They live in the Execution section instead, with short bracket tags
marking the handful of rows that differ.

---

## The Execution section

This is what replaces the three columns. It goes near the top, before Scope.

```markdown
## Execution

**Environment:** UAT, except tests tagged `[Prod]`, which run in Production after go-live.

**Ownership**

| Section | Setup By | Executed By |
| --- | --- | --- |
| CTC (Complete the Chart, patient side) | Ivy Team | Care Ops QA |
| CHT (Provider chart experience) | Eng | Provider |
| E2E (Cross-cluster) | Ivy Team | Provider |

- **Setup By** creates the test conditions.
- **Executed By** runs the test and signs off.

**Exception tags**

| Tag | Meaning |
| --- | --- |
| `[Prod]` | Runs in Production after go-live |
| `[Staging]` | Also worth running earlier, in Staging |
| `[Design]` | Executed by Design |
| `[Clinical]` | Executed by Clinical Ops |
| `[Eng]` | Executed by Engineering |
```

Nine tagged rows across the 26 below. Five of those nine are the design, rollback, and smoke rows
that every section carries by construction, and those always differ from the section default. Only
four are discretionary. Everything else inherits.

---

## Section 1: Complete the Chart, patient side (CTC)

**Requirements:** CC-02, CC-03, IVY-02, IVY-03, IVY-05
**What it does:** checks a chart for gaps at submission, asks the patient for what is missing, and
holds the provider task until the chart is ready.

| Test # | Area/Theme | Validation and Behavior | Pass/Fail Note |
| --- | --- | --- | --- |
| CTC-01 | **Gap Detected, Chart Completed** | Submit an intake with a known gap. The patient receives the questions as one sequence, not trickled over time. Answer them. Each answer persists as it is given. The chart closes the gap and the provider task appears. (CC-02, CC-03, IVY-02) | |
| CTC-02 | **Complete Chart, No Ask** | Submit an intake with no gap. The patient receives no questions and the provider task is created without delay. (CC-02) | |
| CTC-03 | **Pre-Fill From Existing Data** | Submit for an existing patient whose prior records cover part of the gap. Only the residual is asked. Pre-filled values are shown to the patient for confirmation rather than re-entry, and write back with their source and date. (IVY-03) | |
| CTC-04 | **Stale Data Reopens the Gap** | Submit for a patient whose relevant value is older than its freshness window. The value is treated as a gap and asked. A value inside its window is treated as complete. Both cases in one run. (IVY-03) | |
| CTC-05 | **Patient Does Not Respond** | Submit with a gap and do not answer. The patient receives the specified nudges and no more. The task stays held rather than escalating to a provider. The task releases if the patient later re-engages. (CC-03) | |
| CTC-06 | **No Consent Falls Back** | Submit for a patient who has not consented to AI outreach. No questions are sent and the task proceeds to a provider the way it does today. (CC-03) | |
| CTC-07 | **Ambiguous Answer Clarified** | Answer a question with an implausible or misspelled value. The patient is asked to confirm or correct before anything is saved. After the specified number of attempts, the reply is accepted as free text and surfaced to the provider rather than looping. (IVY-02) | |
| CTC-08 | **Provider Message Takes Over** | With questions still pending, send a provider message to the patient. The remaining questions are not sent and the thread hands to the provider. Subsequent patient replies reach the provider directly. (IVY-02) | |
| CTC-09 | **Patient Sees One Action Item** | With a gap open, the app surfaces the action item directing the patient to answer, and it opens to the next question. Once the chart is complete, the surface shows the provider-review state instead. (IVY-05) | |
| CTC-10 | **Escalation Never Held** `[Clinical]` | Submit an escalation and an urgent case, each with an open gap. Both reach a provider without being held. (CC-02) | |
| CTC-11 | **Chart Record Disclaimer** `[Clinical]` | When data is saved to the patient record, the specified disclaimer surface appears and opens to the legal text. (IVY-02) | |
| CTC-12 | **UI Design** `[Design]` `[Staging]` | Patient-facing surfaces match the approved mocks. **Verified by: Design ([reviewer name])** | |
| CTC-13 | **Production Smoke** `[Prod]` | After go-live at the first cohort: submit a live intake with a gap, confirm the patient is asked, the answer writes back, and the task releases. Confirm the guardrail dashboard reflects the run. | |

---

## Section 2: Provider chart experience (CHT)

**Requirements:** CC-04, CC-05, DI-05
**What it does:** presents the completed chart in one view so the provider reaches a treatment
decision without hunting.

| Test # | Area/Theme | Validation and Behavior | Pass/Fail Note |
| --- | --- | --- | --- |
| CHT-01 | **Decision In One View** | Open a task whose chart was completed. Every element the requirements name is visible in the center pane without navigating away. Reach a treatment decision using only that view. (CC-05) | |
| CHT-02 | **Patient Answers Visible and Attributed** | The question asked and the answer given are both visible, with the source and date shown. The provider does not re-ask what was already collected. (CC-04) | |
| CHT-03 | **Carried-Forward vs Newly Collected** | For a patient with pre-filled data, the provider can tell which values were carried forward and which were newly collected. (IVY-03, CC-04) | |
| CHT-04 | **Check-In Shows What Changed** | On a check-in, the provider can identify which values changed since the previous visit. (CC-04) | |
| CHT-05 | **Missing Element Is Legible** | For a chart where a named element has no value, the pane makes the absence clear rather than showing a blank the provider might misread as normal. (CC-05) | |
| CHT-06 | **Interaction Checking Intact** `[Clinical]` | For a patient whose chart was completed through the new path, the existing interaction and safety checks behave as they do today. A value collected through the new path is checked, not skipped. (CC-04) | |
| CHT-07 | **Preventable Miss Recorded** `[Clinical]` | A provider asks the patient for information the codified definition covers. The miss is recorded. A provider asks something the definition does not cover. It is not recorded. (DI-05) | |
| CHT-08 | **UI Design** `[Design]` `[Staging]` | Center pane layout and the provenance indicator system match the approved mocks. **Verified by: Design ([reviewer name])** | |
| CHT-09 | **Rollback Executed** `[Eng]` `[Staging]` | Disable the feature. Providers see today's chart experience with no residual state and no data loss. Re-enable and confirm the new pane returns. | |
| CHT-10 | **Production Smoke** `[Prod]` | After go-live: a provider opens a live completed-chart task, confirms the pane renders in one view, and reaches a decision. Confirm the clinical quality guardrail shows no regression. | |

---

## Cross-cluster scenarios

Tests the seams between sections, not a repeat of either.

| Test # | Area/Theme | Validation and Behavior | Pass/Fail Note |
| --- | --- | --- | --- |
| E2E-01 | **Full Lifecycle** | Patient submits intake with a gap, is asked, answers, chart completes, task releases, provider opens the task and reaches a treatment decision from the center pane. One continuous run with one patient. | |
| E2E-02 | **Non-Response Recovery** | Patient submits with a gap and does not answer through all nudges. Task stays held. Patient re-engages days later and answers. Task releases and the provider sees the answers with their capture dates. | |
| E2E-03 | **Handoff Mid-Conversation** | Patient submits with a gap and is asked. Provider messages the patient before the chart completes. Remaining questions stop. Provider and patient exchange directly. Provider reaches a decision using the partial chart plus the exchange. | |

---

## Why these are calibrated correctly

### Scenario altitude, not field altitude
CTC-01 covers submission, question delivery, sequencing, persistence, gap closure, and task release
in one row. In Comprehensive mode those are six tests. Here they are one journey, because the person
executing cares whether the flow works, not which field wrote first.

### Contrast pairs stay together
CTC-04 tests stale and fresh in one row. CHT-07 tests preventable and not-preventable in one row.
The requirement's meaning lives in the contrast, and separating them makes each half look arbitrary.

### The table stays narrow
Four columns means the Validation cell gets the width it needs. A UAT test is a paragraph of
scenario, and three near-constant columns squeezing it is the wrong trade.

### Tags mark real exceptions only
Nine tagged rows out of 26, and five of those are structural: every section ends with a design row,
and most carry a rollback or smoke row. Those always differ from the section default, so they do not
count toward density. That leaves four discretionary tags, all `[Clinical]`, on the rows where
clinical judgment is the thing being validated.

Judge density on the non-structural rows only. In CHT that is 2 of 7, well under a third. Counting the
structural rows would make every well-formed section look over-tagged, which is a measurement error
rather than a real signal.

### Section ownership reflects who can create the condition
Ivy Team drives anything requiring a real patient-side conversation. Eng seeds charts for tests that
start at the provider surface. Assigning this per section rather than per row is honest: it is a
property of the section's subject matter, not of individual tests.

### Rollback is executed, not documented
CHT-09 requires disabling the feature and observing the result. "A rollback plan exists" is not a test.

### Each section carries design and go-live coverage
Every section ends with a design-fidelity test and a production smoke test. Both are routinely
skipped and both are routinely regretted.

---

## Altitude and structure failures to avoid

| Anti-pattern | Why it fails |
| --- | --- |
| Adding an Environment, Setup By, or Executed By column | Those belong in the Execution section. On a row they repeat the same value dozens of times |
| `\| CTC-14 \| **Disclaimer Copy** \| The modal reads "Your medical record has been updated" \|` | Exact copy verification. Integration testing covered it. Belongs in Comprehensive mode |
| `\| CTC-15 \| **Modal Close, X** \|` plus `CTC-16 Close Button` plus `CTC-17 Backdrop` | Three rows for one behavior. Fold into the parent test |
| `\| CHT-12 \| **Event Schema** \| The event contains patient_id, gap_type, timestamp \|` | Event schema validation. Not something a provider can execute |
| `\| CTC-18 \| **Ask Quality** \| Questions are relevant and non-redundant \|` | Eval measurement, and not binary. Out of scope |
| A section with 26 tests | Consolidate. Sections run 10 to 15 tests. `[estimate range]` If a section genuinely needs more, it is probably two sections |
| No `[Prod]` tag anywhere | The document never validates go-live |
| A tag with no legend entry, or a legend entry no row uses | Both fail eval E1 |
| A `[Staging]` tag when the environment is already Staging | A tag that restates the default is noise. Fails E1 |
| `\| CTC-19 \| **Scope - No New Intake Questions** \|` | A non-goal. Non-goals get no tests; Scope points to the PRD's out-of-scope section |
| A design-verification test in a section with no design surface | Produces a contrived row. Write design tests only where there is something to look at |
| `\| WRB-08 \| **Stub Is Versioned** \| The EMR records which stub version it rendered \|` | An engineering-internal interface. No Care Ops or provider executor can run it. Name the requirement in Scope as verified elsewhere |
| A published coverage table, dedup notes, or prerequisites section | Working sections. They belong in the chat summary, not the artifact |
