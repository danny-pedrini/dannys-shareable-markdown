# [PRD] <Feature name>

> **Template usage:** A stakeholder-facing PRD written for a non-technical reader with no context. It says what we're building and why. Exact behavior lives in the companion acceptance criteria doc (`Templates/Acceptance-Testing-Template.md`, built by the `acceptance-testing-generator` skill). Delete this block and every HTML comment before publishing.
>
> **Rules**
>
> 1. One PRD per launch. Program vision lives in a separate strategy doc.
> 2. Write for a non-technical cold reader. Give enough context that someone new to the problem understands what we're building and why. There is no word cap: cut repetition, not context, and leave testable detail to the acceptance criteria doc.
> 3. The PRD is comprehensive and high level. Comprehensive: every outcome the launch delivers has a requirement here (a story, rollout stage, the fallback, or a metric). High level: each states the outcome, not the mechanism, so a non-technical stakeholder can approve it without knowing how it works; link the mocks or prototype once they exist. The acceptance criteria doc is the detailed contract with Engineering and Design, and every test there traces to a requirement here. A decision a stakeholder would want a say in is a requirement and belongs here; how an agreed requirement works belongs there. No Given/When/Then, edge-case lists, or data-capture specs here.
> 4. Say each fact once. Cross-reference it after that.
> 5. Omit empty sections, subsections, and rows, except Related docs rows, which stay as slots with an empty link until the doc exists. No "N/A" placeholders. A new metric with no baseline reads "None (new metric)."
> 6. Link, don't embed. Sizing, the eval bar, sub-team requirements, and dashboards each get their own doc, listed in Related docs.
> 7. Every metric has a baseline and a numeric target. `[TBD: needs data]` is allowed. "Up" and "down" are not targets.
> 8. Every AI launch states a clinical quality guardrail, rollout stages with exit criteria, who makes the final clinical decision, and the fallback when there is no AI output.
> 9. No engineering implementation detail.
> 10. Story IDs are a prefix plus a number (e.g., `MSG-04`). Append new IDs; never renumber or reuse one. Once the PRD has been shared with Engineering and Design, mark changes with the revision markers and log them in the Change log, both at the end of the document. Before then, edit in place.
> 11. Cold-reader test: define each acronym, Care term, and internal label the first time it appears. There is no Glossary. The Today column carries the current state.
> 12. Sources are links a reader can open. No local file paths and no session artifacts (intake question numbers, reviewer rows, unlinked ticket IDs).
> 13. The repo's writing checklist applies: no em dashes, no vague ranges, plain words.
> 14. State mechanisms as the sources state them: plain steps, nothing added, nothing swapped.
> 15. Stories describe product behavior the build team ships. Team processes and other teams' deliverables are Dependencies or out of scope.

**Doc status**

| Field | Value |
| --- | --- |
| **Status** | Draft / In review / Approved |
| **PM** | @Name |
| **Tech lead** | @Name (BE); @Name (FE) |
| **Design lead** | @Name |
| **Clinical lead** | @Name |
| **Last updated** | <Date> |

<!-- Tech lead: one name, or a backend and a frontend lead. Clinical lead: clinical launches only; delete the row otherwise. -->

**Related docs**

<!-- Keep every row as a slot. A doc that doesn't exist yet keeps its row with a blank link cell: no placeholder text. Eval bar: AI launches only. -->

| Doc | Link |
| --- | --- |
| **Background docs** | <Link> |
| **Sizing** | <Link> |
| **Acceptance criteria** | <Link> |
| **Prototype** | <Link> |
| **Mocks** | <Link> |
| **Dashboard requirements** | <Link> |
| **Eval bar** | <Link> |

## Approvals

<!-- Delete rows that don't apply to this launch. -->

| Name | Function | Sign-off + date |
| --- | --- | --- |
| @Name | Product | |
| @Name | Engineering | |
| @Name | Design | |
| @Name | Clinical | |
| @Name | Legal | |
| @Name | Care Ops | |

## TL;DR

<!-- 5 sentences max: how it works today, the change's impact on cost and on quality (from Feature impact), what we're building, and this launch's expected impact. -->

<How it works today.> <Impact on cost and quality.> <What we're building.> <Expected impact of this launch.>

## What problem are we solving?

<!-- Link evidence for every claim that has it. Tag a claim with no evidence `[Assumption: X (needs validation)]`. The user problem sentence is the POV statement; don't restate it elsewhere. The business problem states the baseline (current spend, volume, or rate) and every business motivation. Feature impact is the change the launch or its parent initiative is sized to cause (savings, cost avoided, revenue, or a metric's movement), taken from the sizing doc or the PM's confirmed intake answer. It is never the baseline. Add the Note only when this launch is one team's part of a larger initiative. -->

**User problem:** <Persona> needs a way to <job> because <biggest discovery insight>.
Evidence: <Link>, <Link>

**Business problem:** <The problem, with the baseline it's measured against, and every business motivation.>

**Feature impact:** <The sized impact, with its figure.>

**Note:** <What the larger initiative changes, who drives it, and why it needs this launch.>

Evidence: <Link>, <Link>

## How will we know it worked?

<!-- Goals in priority order, 3 max. Primary is usually cost. Every AI launch carries a clinical quality guardrail. Unknown baseline: `[TBD: needs data]`. -->

### Goals

1. <Outcome, not an activity>

### Metrics

| Type | Metric | Baseline | Target | Source |
| --- | --- | --- | --- | --- |
| **Primary** | <Metric> | <Current value> | <Numeric target> | <Link> |
| **Guardrail** | <Clinical quality metric> | <Current value> | <Numeric target> | <Link> |
| **Leading** | <Metric> | <Current value> | <Numeric target> | <Link> |

## What are we not doing?

### Non-goals

<!-- Outcomes we are not pursuing. One line of why each. Omit this subsection if empty. -->

- **<Non-goal>:** <Why>

### Out of scope

<!-- Work excluded from this launch. One line of why, plus where it lands if it's planned. Omit this subsection if empty. -->

- **<Item>:** <Why>. <Where it lands, if planned.>

## What are we building?

**Hypothesis:** If we <change>, then <metric moves>, because <insight>.

<!-- Optional, for launches that change screens. Attach a screenshot in each Today and With this launch cell. -->

| Surface | Today | With this launch |
| --- | --- | --- |
| <Screen or surface> | <Screenshot and what it does now> | <Screenshot and what changes> |

### User stories

<!-- Pick one short prefix per surface or subsystem, unique within the initiative (Galen uses CC-, REC-, CDS-, MSG-). When stories split into named groups, add a one-line intro explaining the groups and give each its own "####" header and table. "What good looks like" is 2 sentences max; the testable version lives in the acceptance criteria doc. -->

**Priority:** P0 = launch blocker. P1 = targeted for launch, not blocking. P2 = after launch.

| ID · P | User story | Today | What good looks like |
| --- | --- | --- | --- |
| <ID> · P0 | As a <persona>, I want <action>, so that <outcome>. | <How it works today> | <The outcome when this works> |

Detailed acceptance criteria: <Link to the acceptance criteria doc>

## How does it roll out?

<!-- Non-AI launches drop Back data and Shadow. Stage names match the acceptance criteria doc's Launch Phase values. -->

| Stage | Audience | Exit criteria |
| --- | --- | --- |
| **Back data** | None. Runs offline against historical cases. | <Numeric bar> |
| **Shadow** | Live traffic. Outputs are logged, not shown. | <Numeric bar> |
| **Phased ramp** | <Share of users>, with a <share> holdout | <Numeric bar> |
| **GA** | <Full audience> | <Numeric bar> |

**Fallback:** <What the user sees when there is no AI output.>

## What could go wrong?

<!-- Write load-bearing assumptions here as risks. -->

| Risk | Mitigation | Owner |
| --- | --- | --- |
| <Risk> | <Mitigation> | @Name |

## What do we need from others?

<!-- Anything another team must deliver, including Care Ops workstreams such as pay model changes, training, and sign-offs. Put why it matters in What we need. -->

| Dependency | Owner | What we need | Blocks launch? |
| --- | --- | --- | --- |
| <Dependency> | @Name | <What we need and why it matters> | Yes / No |

## What's still open?

| # | Question | Why it matters | Owner | Needed by |
| --- | --- | --- | --- | --- |
| 1 | <Question> | <Why it matters> | @Name | <Date> |

## Appendix

### Alternatives considered

<!-- Only when 2 or more options were actually debated. -->

| Option | Why not chosen |
| --- | --- |
| <Option> | <Reason> |

## Revision markers

Use these once the PRD has been shared with Engineering and Design, so readers see the delta and story IDs stay stable. Before then, edit in place with no markers.

| Marker | Meaning |
| --- | --- |
| ➕ | Requirement added after the initial draft |
| 🔄 | Requirement revised. State what changed. |
| ~~struck~~ | Requirement removed. State why and where it is covered instead. |

**Story IDs:** append new IDs; never renumber or reuse one. The acceptance criteria doc's Req ID column cites them.

## Change log

<!-- Add only once the PRD has been shared with Engineering and Design. Delete before then. -->

| Date | What changed | Where | Why |
| --- | --- | --- | --- |
| <Date> | <What changed> | <Section or story ID> | <Why> |
