# Exemplar: Comprehensive Mode

Calibration reference for the `acceptance-testing-generator` skill. Annotated excerpts, not a
complete document.

**These are illustrative.** They are modeled on Galen Phase 1 requirements (CC-02, CC-04, CC-05,
DI-05) to show altitude, phrasing, and traceability. Do not copy content from here into a generated
document. Copy the form.

**Audience:** Engineering and Design. This is the build contract, the expansion of a high-level
stakeholder-facing PRD into behavior an engineer can implement against and a QA engineer can verify.

---

## Column set

Six columns. Nothing else.

```
| Test # | Req ID | Area/Theme | Requires Design | Validation and Behavior | Pass/Fail Note |
```

Environment is near-constant across a document, so it is stated once in Purpose rather than repeating
on every row. Comprehensive mode has no Execution section and no ownership table: engineering runs
these.

```markdown
## Purpose

... Tests run in Staging. Tests tagged `[UAT]` also run in UAT; tests tagged `[Prod]` run in
Production as part of release readiness.
```

Requires Design is Yes when Design must decide or produce something for the test to pass (layout,
copy, labels, states, visual treatment), otherwise No.

Only environment tags apply in Comprehensive mode. The executor tags (`[Design]`, `[Clinical]`,
`[Eng]`) exist to override a UAT section's ownership row, and Comprehensive has no ownership table,
so using one here fails eval E1.

---

## Calibrated excerpts

| Test # | Req ID | Area/Theme | Requires Design | Validation and Behavior | Pass/Fail Note |
| --- | --- | --- | --- | --- | --- |
| **Task Queue & Routing** | | | | | |
| 1 | CC-02 | **Completeness Check - Trigger Events** | No | **Given** a patient with an incomplete chart<br>**When** an intake, a check-in, and a renewal are each submitted<br>**Then** the completeness check runs on each. All three triggers verified independently. | |
| 2 | CC-02 | **Task Hold - Incomplete Chart** | No | **Given** a submission whose chart has an open gap<br>**When** the completeness check runs<br>**Then** no provider task is created and the submission stays held until the chart is confirmed complete. | |
| 3 | CC-02 | **Task Hold - Release on Completion** | No | **Given** a held submission with an open gap<br>**When** the gap closes<br>**Then** the task is created and appears in the provider queue. Verified once per trigger type. | |
| 4 | CC-02 | **Task Hold - Never Held** | No | **Given** an open chart gap on the submission<br>**When** an escalation, an urgent case, or a sync visit awaiting scheduling is submitted<br>**Then** the task is not held and reaches a provider without delay. Each of the three verified. | |
| 5 | CC-02 | **Decoupling - Async Visit Steps** | No | **Given** a submission in visit-submission processing<br>**When** DoseSpot registration or identity verification is delayed or fails<br>**Then** the completeness check is neither blocked nor delayed, and a delay in the check does not block those steps. Both directions verified. | |
| 6 | CC-02 | **Re-check - New Gap From Message** | No | **Given** a submission whose chart passed the completeness check<br>**When** a patient message arrives<br>**Then** a message carrying chart-relevant information triggers a re-check, and a message carrying none follows today's behavior. Both cases verified. | |
| **Chart Write-Back & Data Integrity** | | | | | |
| 12 | CC-04 | **Write-Back - Destination Parity** | No | **Given** a chart-completing answer from the patient<br>**When** it is written back<br>**Then** it lands in the same destination the equivalent intake answer lands in today. Verified for a weight value and a condition entry. | |
| 13 | CC-04 | **Write-Back - Attribution and Date** | No | **Given** a value written back to the chart<br>**Then** it carries its source and its capture date, and the provider view shows both. | |
| 14 | CC-04 | **Write-Back - Free Text Normalization** | No | **Given** an ambiguous or free-text patient reply<br>**When** it is written back<br>**Then** it is normalized to structured data first, and the raw reply is not written to a structured field. | |
| 15 | CC-04 | **Write-Back - Structured Control Not Bypassed** | No | **Given** a patient reply containing a misspelled condition name<br>**When** the reply is written back<br>**Then** the drug interaction engine receives the normalized value, not the unrecognized raw string. | |
| 16 | CC-04 | **Center Pane - Question and Answer Visible** | Yes | **Given** a chart-completing answer on the record<br>**When** the provider opens the task<br>**Then** the center pane shows the exact question asked and the exact answer given, presented the way intake answers are presented today. | |
| 17 | CC-04 | **Check-In - Changes Since Last Visit** | Yes | **Given** a patient with a previous visit on file<br>**When** the provider opens a check-in or subsequent visit<br>**Then** the provider view identifies which values changed since the previous visit. | |
| **Chart & Center Pane Display** | | | | | |
| 22 | CC-05 | **Center Pane - Required Elements** `[UAT]` | Yes | **Given** a chart holding every element the requirements name<br>**When** the provider opens the task<br>**Then** the center pane surfaces each: allergies, contraindications, current medications, blood pressure, compliance check, and relevant intake or check-in answers. Each verified present. | |
| 23 | CC-05 | **Center Pane - No Data Change** | No | **Given** a value in its system of record<br>**When** the center pane renders it<br>**Then** the displayed value matches the source, unaltered, unmoved and not re-derived. | |
| 24 | CC-05 | **Center Pane - Missing Element Handling** | Yes | **Given** a named element with no value in the chart<br>**When** the pane renders<br>**Then** it shows the specified empty treatment rather than omitting the row or showing a blank. | |
| **Instrumentation & Analytics** | | | | | |
| 31 | DI-05 | **Miss Detection - Provider Ask Captured** | No | **Given** a task the completeness check cleared<br>**When** the provider asks the patient for additional information<br>**Then** the ask is detected and recorded. | |
| 32 | DI-05 | **Miss Detection - Preventable Only** | No | **Given** two provider asks, one for information the codified definition requires and one reflecting clinical judgment outside it<br>**Then** the first counts toward the miss rate and the second does not. Both cases verified. | |
| 33 | DI-05 | **Miss Rate - Reporting** | No | **Given** recorded misses across a reporting period<br>**When** the miss rate is reported<br>**Then** it is reported at the grain the requirements specify, with the reason breakdown they specify. | |
| **UI Design Verification** | | | | | |
| 47 | CC-05 | **Design - Center Pane Layout** `[UAT]` | Yes | **Given** the approved mocks<br>**When** the center pane renders<br>**Then** layout, element ordering, and visual hierarchy match them. **Verified by: Design ([reviewer name])** | |
| 48 | CC-05 | **Design - Provenance Indicators** `[UAT]` | Yes | **Given** chart data from more than one source<br>**When** the pane renders<br>**Then** the indicator system distinguishing sources matches the approved mocks, severity treatment included. **Verified by: Design ([reviewer name])** | |
| **Launch Gate Readiness** | | | | | |
| 51 | CC-02 | **Feature Flag - Enable and Disable** `[Prod]` | No | **Given** the release in production<br>**When** the flag is enabled and then disabled<br>**Then** enabling activates the completeness check and the new pane, and disabling returns today's behavior with no residual held tasks and no data loss. | |
| 52 | CC-02 | **Rollback - Executed** `[Prod]` | No | **Given** the release in production with held tasks outstanding<br>**When** the release is rolled back<br>**Then** held tasks are released to providers rather than stranded. Verified by execution, not by the existence of a plan. | |
| 53 | DI-05 | **Monitoring - Alarm Wired** `[Prod]` | No | **Given** the named guardrail alarm configured<br>**When** a threshold breach is deliberately induced<br>**Then** the alarm fires and the alert reaches the on-call destination the requirements specify. | |

---

## Why these are calibrated correctly

### Traceability is explicit
Every row carries its requirement ID. When the PRD changes, the affected tests are found by grep
rather than by rereading. Care requirements ship with IDs, so there is no excuse for a test that
does not cite one.

### The table carries only what varies
Six columns. Environment sits in Purpose because it is the same on almost every row, and the three
rows that differ carry a `[UAT]` tag. Requires Design tells Design which tests need its input. Width goes to the Validation cell, which is the
column doing the work.

### Every validation is Given / When / Then
Each clause is bolded and sits on its own line, separated by `<br>` inside the cell. The split is not
decoration: it forces the precondition into the open, which is what an executor has to set up before
they can run anything. Where there is no distinct trigger, When folds into Given rather than being
invented (tests 13, 24 and 32 do this). An `*Example:*` is appended only where a source supplies a
real one, and the pass condition never depends on its values.

### Consolidation follows the requirement, not the permutation
Test 4 covers three exclusions (escalations, urgent, sync-pending) in one row because the
requirement states them as one rule with three instances. Test 1 covers three triggers in one row
for the same reason. Compare with splitting them into six tests, which adds rows without adding
coverage.

Test 32 keeps two cases in one row because the requirement's meaning lives in the contrast:
preventable counts, judgment does not. Splitting them loses the point of the test.

### Each validation is binary
"No provider task is created" is observable. "Task holding works correctly" is not. Every cell names
a condition an executor can confirm or deny without interpretation.

### No invented thresholds
Test 5 says "does not block or delay" rather than naming a millisecond budget, because the source
states no budget. Test 33 says "at the grain the requirements specify" rather than inventing a grain.
Where a threshold is genuinely needed and absent, flag it in the Potential requirement gaps working list.

### Source terminology is preserved
"Completeness check", "held", "codified definition", "center pane". Not "chart validator", "queued",
"clinical rules", "summary card". A renamed term breaks the trace back to the requirement and
creates ambiguity for the engineer implementing it.

### Guardrail mechanism, never model quality
Test 15 checks that the interaction engine receives a normalized value. It does not check whether
the engine's output is clinically correct. That distinction is the line between acceptance testing
and eval measurement.

### Non-goals get no tests
Tests trace only to the PRD's requirements and metrics. A clinically weighty exclusion, like no AI on
the Phase 1 pane, is tested only when the PRD states it as a requirement. Otherwise it goes in the
Potential requirement gaps working list as a candidate PRD open question.

### Design tests name their verifier
A design-fidelity test that no named person owns does not get executed. The reviewer's name comes
from intake or a placeholder, never a guess.

---

## Altitude and structure failures to avoid

| Anti-pattern | Why it fails |
| --- | --- |
| Adding an Environment column | It belongs in Purpose. On a row it repeats the same value dozens of times |
| `\| 15 \| CC-05 \| **Center Pane - Allergies Field** \| The pane displays allergies \|` followed by five more rows, one per element | Six rows where one belongs. The requirement names the elements as one list. Test 22 is the correct form |
| `\| 20 \| CC-04 \| **Write-Back** \| Write-back works as specified \|` | Not binary, restates the requirement instead of testing it, and is not Given/When/Then |
| A Validation cell of unbroken prose, however specific | Not the format. The executor has to reverse-engineer the setup out of a paragraph |
| `**Given** the system is working **When** the user uses it **Then** it works` | The shape with none of its value. Each clause must name something an executor can set up, do, or observe |
| An `*Example:*` whose values come from the prototype | Fixture data as a criterion. Fails eval D2 |
| `\| 25 \| CC-02 \| **Performance** \| The check completes in under 500ms \|` | The source states no budget. Invented threshold. Use "within acceptable time" |
| `\| 30 \| CDS-01 \| **Quality** \| Generated questions are clinically appropriate \|` | Eval measurement, not acceptance testing. Out of scope |
| `\| 35 \| CC-04 \| **Write-Back - Weight** \| Patient reply "182 lbs" writes 182 to the weight field \|` | Asserts a prototype fixture value. Test the normalization behavior, not the sample datum |
| A row with an empty Req ID or Requires Design cell | Fails eval E1. Every Comprehensive test traces to a requirement; detail beyond the PRD is listed in the Tests beyond the requirements working list |
