# Exemplars

## Gold exemplar

`Project-Galen/Phase-1/Galen-Phase-1-Metrics-One-Pager-ADS-v2.md` (v2, 2026-09-07 state, 33 metrics, two builds).

Read it in full before drafting. It is a multi-build document, so its §1 is heavier than the base case needs.

### Imitate

- Table density. Every metric is one row; prose exists only to defend a choice.
- Definition cells that name the population and the arm: "Difference in messaging-task creation rate, net-eligible initial-intake submissions only, by member arm."
- Grain reasoning made explicit where it is non-obvious (A1 note).
- Reconciling tier that ties the hero back to the sizing model (A5 reconciles to the Visit Modality coefficient) and to the number leadership already reads (A4).
- Decomposition notes that explain why a split matters (A11).
- "Same failure at two grains" and "do not build twice" notes that stop ADS from building disagreeing metrics.
- Exposure definitions table (§2.2) with gross against net eligibility and exclusion IDs from the PRD.
- Open questions with a named owner and a Blocks column citing IDs.
- Change log rows that name what moved and the new count.
- The "What this is not" sentence.

### Do not imitate

These predate rules Danny locked on 2026-09-10 or are defects the evals now catch.

| v2 element | Why not | Rule |
|---|---|---|
| Guardrail rows A17 through A20 and B6 through B8 carry no alarm text | Every guardrail now carries an alarm clause | E28 |
| No Baseline or Target column anywhere | Hero and Business outcomes now carry both | E29 |
| Change log 2026-09-02 row cites "C3 untouched visits"; the current document has no C3, the metric is A20 | Cross-references must resolve | E32 |
| Summary sentence lists "business-outcomes, the hero product outcomes, supporting drivers, and guardrail metrics", omitting reconciling | Summary sentence uses the fixed tier list | E35 |
| "Document summary and metadata" carries ad hoc paragraphs (Additional value levers, Ramp go and no-go) | Summary uses the seven fixed labels; extras go to Scope notes, two sentences maximum | E35 |
| Section numbering 1, 2, O, A, B, C, 4, 5, 6, 7 with no 3 | Canonical sequence is 1, 2, O, A, (B, C), 3, 4, 5, 6 | E23 |
| "## 1. Two builds, two randomizations" | Base case is one build; the section is "Build, rollout, and arm assignment" | E23 |
| Reviewer- and comment-derived metrics added to the document before Danny approved them, then partially cut | Every metric enters through the selection gate | E19 |

## Second gold exemplar: Provider Drafts (Confluence)

`references/exemplar-provider-drafts-confluence.md` (2026-09-29 snapshot, 18 metrics, one build). Danny's published edit of this skill's Provider Drafts run. Where it and the Phase 1 v2 exemplar differ, this one reflects the newer rules.

### Imitate

- Every citation is a link a reader can open. No intake, gate, or finding numbers.
- The Summary pairs each hero with the lagging business outcome it drives.
- Owners assigned by team in bold on the CIS computation bullets, instead of open questions.
- Three open questions, each blocking a named metric.
- Accepted limitations stated plainly: "we will live with the directionality."

### What Danny changed from the skill's output

| Skill output | Danny's edit | Rule now |
|---|---|---|
| More than 40 citations to intake questions, gate rows, synthesis findings, and tickets | None; links to the PRD, judges doc, Looker, Legal request, and pay plan instead | Taxonomy § Citations |
| 21 open-question rows, most from the reviewer round | 3 rows | SKILL.md Step 9.1 bar |
| Reviewer-derived minimum-count note and named responders in alarm cells | Note removed; two alarm cells keep a short minimum-count clause | Defect or Addition tagging at Gate 3 |
| Drafts-shown rate as its own row, the complement of BAU trigger rate | A clause in the BAU row | Taxonomy Inverse metric row; E38 |
| Discard rate as its own row over revealed drafts | Redefined as manual plus snippet share, a clause in the distribution row | Taxonomy Subset metric row |
| Messaging tasks per patient as its own row, only an input to the cost formula | Cut | Taxonomy Input-only row |
| Retention as a hero metric | O2, a business outcome; only CIS and AHT gate the ramp | Taxonomy tiers; E16 |
| Sizing coefficient labeled "a 30% AHT reduction from Q4 2026 (not a target)" | A2 Target: 30% | Gate 2 target question |
| Client event field lists in Definition and open-question cells | Removed; ADS flags instrumentation gaps to Eng. A8 kept one storage clause | E17 pattern; §4 standard sentence |
| Required Hard dependency field naming three records | Removed; too many dependencies to name only three | Hard dependency optional |
| Change-log row listing gate rows and finding counts | No row | Template change-log rule |

### Do not imitate

| Snapshot element | Why not |
|---|---|
| A6 Grain "Hour" on a cost per completed task | Grain should be Task (E15) |

## Lessons from Danny's edits: December Provider Pay sync

`project-galen/Provider-Pay/Analytics/Provider-Pay-EMR-December-Metrics-One-Pager-ADS.md`, synced from Danny's Confluence edit on 2026-11-03. Not a gold exemplar; these two lessons only.

- In sentences, write "metric A1," not a bare "A1," so readers outside ADS can follow. ID and Blocks columns keep the bare ID.
- When a document first moves to Confluence, the change log restarts at one "Initial version" row.

## Negative exemplar

v1 (2026-08-25, 25 metrics) was deleted after ADS-v2 became the ask. The banned shapes below are the residual teaching material; do not regenerate them by default.

### Sections that are not generated by default

Danny removed all of these to get from v1 to v2. Any one may return as an ad hoc section when the approved plan names it with a one-line reason.

- "What ships if arm assignment is not ready" (v1 §2.3)
- "What can and cannot be claimed" (v1 §2.4)
- "What the dashboard is for at each ramp step" (v1 §2.5)
- "Where this departs from the PRD" (v1 §3.7)
- "Views" (v1 §5)
- A glossary
- "Decisions that shaped what is absent"
- Traps or caveats as their own section; the surviving ones became under-table notes
- Static baseline and target columns on every tier; now Hero and Business outcomes only
- Alarm lines and targets the PM had not set; now sourced or owner-tagged

### What v1 got wrong

It ran to roughly 27 pages. Metrics were split across two tables per tier. Rationale lived in walls of text rather than one note per questionable choice. Metrics entered because a reviewer or a comment suggested them, not because Danny selected them. The evals for section adherence, prose length, redundancy, and unapproved adoption exist because of v1.
