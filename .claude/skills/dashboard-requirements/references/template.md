# Template: dashboard requirements document

The fixed shape of every document this skill produces. Section order is locked and checked mechanically (E23). Column headers are locked (E29). The Summary field set is locked (E35). Read this before drafting, before any QA pass, and before any revision.

Base case is one build. The multi-build extension is at the end.

## Canonical header sequence

Machine-readable list for E23. Substitute the real build name for `[Build]`. Lines marked multi-build appear only when the document covers two or more builds.

```
# [Build]: Experimentation & Dashboard Requirements
## Summary
### Stakeholders
### Informed
## 1. Build, rollout, and arm assignment
## 2. Exposure and population
## O. Business outcomes
## A. [Build]
### Hero metrics
### Reconciling metrics
### Driver metrics
### Guardrail metrics
## B. [Second build]            multi-build only, with the same four ### tiers
## C. Shared guardrails         multi-build only
## 3. Slices
## 4. Next steps for ADS
## 5. Open questions
## 6. Change log
```

**Ad hoc sections.** Allowed only when the approved plan (gate-1 snapshot) names the section and gives a one-line reason. An ad hoc section sits directly after the canonical section it extends. E23 ignores headers outside the canonical set when checking order; E24 checks that each extra header is justified.

## Skeleton with rules

### Top matter

```
# [Build]: Experimentation & Dashboard Requirements

> **Source:** The Google Doc [Title](url), [author], is the upstream working copy. This local file matches it as of M/D/YY.
```

The source block appears only when an upstream document exists. When the local file has moved past the upstream copy, the second sentence becomes: "This local file is ahead of it as of M/D/YY: [one clause per divergence]."

```
| Doc status       | DRAFT                                              |
| ---------------- | -------------------------------------------------- |
| **Last updated** | M/D/YY                                             |
| **PM lead**      | [Name](mailto:email)                               |
| **ADS leads**    | [Name](mailto:email), [Name](mailto:email)         |
```

Doc status values: DRAFT, IN REVIEW, FINAL. The skill writes DRAFT; Danny changes it by hand.

### Summary

Seven allowed bold labels, in this order. Five are required; Hard dependency and Scope notes are optional. No other labels, no unlabeled paragraphs (E35).

| Label | Budget | Content |
|---|---|---|
| **What ADS should build:** | 1 sentence | The question the dashboard answers, ending with "N metrics across business outcomes, hero, reconciling, driver, and guardrail tiers." Use a numeral for N. |
| **Primary outcome and sizing:** | 2 sentences | Each hero metric as the leading indicator of the business outcome it drives, then the sourced sizing estimate with an inline link. `[TBD: owner]` when no sizing exists. |
| **Hard dependency:** | 1 sentence, optional | Only when a single dependency blocks the whole dashboard, usually arm assignment. When there are many, omit the field rather than list a subset. |
| **Launch date:** | 1 sentence | Date plus program status with its as-of date when a status source exists; otherwise date plus `[confirm with TPM]`. Launch dates are owned by TPMs, never stated as fixed. |
| **Links:** | 1 line | PRD, sizing, and other inputs, pipe-separated markdown links. |
| **What this is not:** | boilerplate bullets | See below. |
| **Scope notes:** | 2 sentences, optional | Only when intake surfaces something a reader must know before the tables, such as a lever measured but not committed. |

Boilerplate for **What this is not:**, one bullet per line under the label:

```
**What this is not:**

- Not a Looker build spec, so no SQL, LookML, event schemas, or tile layout.
- Not a launch plan, so eng owners and dates live elsewhere.
- Instrumentation requirements are Eng's.
- The test plan, including experiment power and sample size, is ADS's.
- Out of scope: [named builds, phases, or topics].
```

Replace the bracket with the real exclusions from intake or delete the last bullet.

### Stakeholders and Informed

```
### Stakeholders

| [Function]       | [Name](mailto:email), [Name](mailto:email) |
| ---------------- | ------------------------------------------ |
| [Function]       | [Name](mailto:email)                       |

### Informed

| Engineering | [Name](mailto:email) |
| ----------- | -------------------- |
| Product     | [Name](mailto:email) |
| Design      | [Name](mailto:email) |
```

Stakeholders are people who review or sign off. Informed are people who receive the document. Every name comes from the stakeholder directory, an input, or an intake answer (E34). A known function with no known person gets `[TBD: role]`.

### 1. Build, rollout, and arm assignment

One-line lead: "[Build] is [one clause on what it does], randomized on [unit]." Then the table, one row per build.

```
| Build | What it does | Rollout | Arm assignment |
| ----- | ------------ | ------- | -------------- |
```

Arm assignment cell carries: the unit (member, provider, visit, or none), the control share, the ramp steps or `[TBD: Eng]`, and how the arm is recorded. Prose after the table is limited to the choices a careful reader would question: why this unit, why this ramp speed, known biases. Each paragraph opens with a bold lead and runs four sentences at most.

### 2. Exposure and population

Conditional paragraph first: the state progression the metrics depend on, written as a chain in one line, followed by one or two sentences on where the build triggers and where exposure is assigned. Include it only when the metrics distinguish states a reader could conflate, such as member against subscriber. Omit it otherwise.

Then the definitions table.

```
| Field                    | Definition |
| ------------------------ | ---------- |
| **Eligible**             | The population every metric's denominator rests on unless a row says otherwise |
| **Exclusions**           | Test and internal accounts, plus build-specific carve-outs with PRD IDs |
| **Exposure / Control**   | The assignment unit, the unexposed arm at each ramp step, and which child objects (visits, tasks, asks) inherit the arm |
| **Launch scope**         | What ships first and what expands the denominator later |
```

Add build-specific rows when a metric depends on them (nested experiments, gross against net eligibility). Each row is one definition. Every denominator in the metric tables must name a population defined here or in its own cell (E13).

### O. Business outcomes

Lead sentence: "Where all cost savings are reported." When retention is a business outcome, the lead reads "Where all cost savings and retention are reported." Add the booked, committed, pipeline split sentence when the PRD requires the split.

```
| #  | Metric | Definition (numerator / denominator) | Grain     | Window                   | Baseline | Target | Good |
| -- | ------ | ------------------------------------ | --------- | ------------------------ | -------- | ------ | ---- |
| O1 |        |                                      | Portfolio | Monthly, plus cumulative |          |        | ↑    |
```

Dollars or retention only: lagging company outcomes the hero metrics are expected to move. Dollar definitions reference other metric IDs as formulas, for example "Payable hours saved, deflection (A7) × blended provider rate." Conversion factors that Finance must set appear inline as `[conversion factor: owner to confirm]`.

### A. [Build]

Four tiers, each with its fixed one-line lead and its table. IDs run A1 upward continuously across all four tiers.

| Tier | Fixed lead sentence | Columns |
|---|---|---|
| Hero metrics | "How we determine the success of [Build], assuming no guardrails broken." | # \| Metric \| Definition (numerator / denominator) \| Grain \| Window \| Baseline \| Target \| Good |
| Reconciling metrics | "Making visible the building blocks used to calculate or contextualize the hero metrics." | # \| Metric \| Definition (numerator / denominator) \| Grain \| Window \| Good |
| Driver metrics | "The levers we investigate to understand over- or under-performance in the hero metrics." | same six |
| Guardrail metrics | "How we ensure [Build] does not degrade quality of care or patient experience." | same six; every Good cell carries an alarm clause |

**Baseline and Target** appear on Hero and Business outcomes only (E29). Each cell is a sourced value with a linked source (taxonomy § Citations), or `[TBD: owner]`. Never invented. Illustrative row with synthetic values, not to be copied:

```
| A1 | **Messaging task deflection rate** | Difference in messaging-task creation rate, eligible initial-intake submissions only, by member arm | Visit / submission | Monthly, plus MoM change | 14.2% ([ADS baseline pull, 8/15/26](url)) | [TBD: Danny Pedrini with ADS] | ↑ |
```

**Alarm clause** on every guardrail row, one form only, in the Good cell: `↓ *(alarm if >20%; PRD §5.2)*` when a sourced threshold exists, or `↓ *(alarm threshold: [owner])*` when it does not (E28). The direction symbol may be ↑, ↓, or Hold.

**Under-table notes.** Bold-led paragraphs under a table, four sentences maximum including the bold lead (E26), only for a definitional choice a careful reader would question. Rules and calibration examples are in `metric-taxonomy.md`.

### 3. Slices

```
| Slice | Why it matters |
| ----- | -------------- |
```

Always present: Time period (users define their own baseline). Each experiment arm as its own row. Then one paragraph opening "**Not sliced:**" naming each excluded dimension with its reason.

### 4. Next steps for ADS

One sentence on how ADS splits the work, then this standard sentence: "ADS defines the metrics with proper data sources, flags instrumentation gaps to Eng, and works with Product to prioritize metrics that will be available at launch (and the prioritization of those that will come later)." Then the table. The split is illustrative and ADS finalizes it.

```
| Workstream | Metrics | Owner |
| ---------- | ------- | ----- |
```

Metrics cells list IDs or ranges ("A10 through A12"). Every ID must exist as a row (E32).

### 5. Open questions

```
| Question | Owner | Blocks |
| -------- | ----- | ------ |
```

Owner is a named person or a named team via a named person. Blocks names metric IDs or section numbers. No row without an owner (E33).

### 6. Change log

```
| Date       | Change | Requester |
| ---------- | ------ | --------- |
| YYYY-MM-DD | Initial version | Danny Pedrini |
```

A revision row records only what a reader needs: metrics added, cut, re-tiered, or redefined, and the new metric count when it changed. Never record gate numbers, reviewer finding counts, or touch-list items. Danny may decline the row for a round. Every metric ID cited in a change-log row must exist in the current document, or be written as "former C3, now A20" (E32).

## Multi-build extension

When two or more builds ship together and randomize separately: §1 gets one row per build; each build gets its own lettered section with the four tiers; §C Shared guardrails holds only metrics that both builds move, sliced by every arm; §3 gets one slice row per arm; the Summary's hard-dependency sentence, when present, names every randomization. Metric IDs use A for the first build, B for the second, C for shared.
