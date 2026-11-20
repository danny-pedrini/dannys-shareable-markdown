# Cluster report spec

Spec for Step 5's Evals cluster-analysis report: a markdown doc plus a companion CSV that let the Evals team plot provider verdicts against judge scores for the same drafts, and see where the judges should have caught each failure mode.

> **Source:** Round 3 `cluster-analysis-plan.md` (as revised after `qa-cluster-plan.md`), `qa-cluster-doc.md`, `cluster_analysis_prose.md`, and the built `Round-3-Failure-Mode-Cluster-Analysis.md` and `round-3-rating-rows.csv`.

## Audience

The Evals and AI Eng teams. They know the judges and the traces; they do not know this round folder's working files. Never cite a session artifact to them (list in "No session artifacts" below).

## Unit of analysis

One row per Jira ticket that carries this round's evidence:

- **Filed this round.** One row per ticket filed in Step 4; a merged ticket counts once, even though it absorbed several failure modes.
- **Existing tickets that got this round's evidence.** One row per ticket that received a comment in Step 4. A ticket can carry two rows when a single comment covers two distinct failure modes on it (Round 3 example: MLENG-5405 carried a repeat-step row and a separate refer-visit row from the same comment).

Show category distributions two ways: filed-only, and filed plus existing-ticket rows together. Leaving the existing-ticket rows out understates the clinical share, since they can hold a meaningful fraction of the core clinical cases (Round 3 example: 4 of 8 core rows, stated as "half," not "most").

A failure mode with no ticket and no comment this round is not a unit row either. It goes in the held-or-dropped list (section 3c): held below the filing floor, sent to the product owner, or dropped at Gate 3.

Not unit rows, but kept in the trace table so the plot reads correctly: input-issue rows, "not a failure mode" rows, and logged rows (for example, chart not visible). A judge should not be expected to fail a draft for these; a BAD verdict on one is not an eval miss.

## Taxonomy

Seven categories, matching `report_defs.CATEGORIES` in `round-folder-layout.md` exactly, in this order. Each row gets one primary category and an optional secondary.

| Category | Definition |
| --- | --- |
| Clinical safety: core | The draft gives, omits or contradicts an instruction that could change what the patient takes, or whether they get timely in-person or urgent care. Examples: a missing stop, taper, hold or transition instruction; a missed escalation; a contradictory dose; a missing restart-dose warning. |
| Clinical safety: edge case | Clinically inaccurate, incomplete or out-of-scope content that wouldn't directly cause harm, or matters only in specific patient context. Examples: a wrong or backwards reason for a decision, a missing option or counseling point, a conditional follow-up stated as unconditional, eligibility criteria revealed, diabetes-care scope confusion. |
| Writing quality | Sentence construction, word choice and jargon, order of information, the same instruction twice in one message, pasted-in blocks and markup. Also covers a call to action that is present but hard to spot because of placement or formatting. The ask itself is stated; only its visibility or phrasing is the problem. |
| Templated repetition | The same sentence or paragraph across most messages of a type, or boilerplate the patient doesn't need: sign-offs, goal weight, the Treatment Plan pointer, the check-in paragraph, the Gifthealth handoff. |
| Conversation handling | Doesn't address the patient's ask or an open item, leads with something other than the request, or leaves no path forward. The ask itself goes unaddressed or gets deprioritized, not just hard to see. |
| Factual fidelity | A non-clinical claim the thread or chart doesn't support (an invented detail, an attributed request), a wrong product name, a re-asked question the chart already answers, or a false assumption in required text. |
| Operational routing | Sends the patient to the wrong team or channel, such as the Care Team instead of Customer Support for billing. Scoped to who owns the next step, not to a paragraph that assumes the wrong context (that is Factual fidelity). |

Category reflects the nature of the worst credible instance if sent unedited, independent of the priority actually filed (see "Caveats" below on why).

## Judge mapping (hypothesis)

This mapping is a hypothesis drawn from the judge definitions in the judge doc at `round.json` `judges_doc`. State it as a hypothesis for the Evals team to confirm or correct, never as a measured result.

| Category | Judge(s) that should catch it |
| --- | --- |
| Clinical safety: core and edge case | `rx_guideline_adherence` (plan contradiction, `decision_signal`), `completeness` (missing protocol content), `drives_results` (an action named for a side effect; note it only checks that an action exists, not that it's the right one) |
| Factual fidelity | `groundedness`, or `doctor_relationship` where the draft ignores facts already in context |
| Conversation handling | `question_answered`, `done_in_one`, `direction` |
| Templated repetition | `doctor_relationship` (template feel), partly |
| Writing quality | No dedicated judge |
| Operational routing | `direction` (who owns the next step) |

Each row in the failure-mode table can name its own judge, which may differ from the category default where the fit is closer (for example, `rx_guideline_adherence (decision_signal)` for a wrong rationale, instead of the category's general listing). Do not force a row onto the category default when a closer judge exists; do not invent a judge not named in the judge doc; where no judge fits, write "none dedicated" or "none confirmed," never leave it blank.

## Fields per failure-mode row

Ticket key and link; title; status (filed this round, or existing ticket with this round's evidence added); approved priority (or "existing ticket"); action types; primary and secondary category; proposed judge; what goes wrong (from the ticket's Problem); expected behavior (from the ticket); evidence counts (drafts, rating rows, distinct reviewers, verdict mix, reviewer-stated versus mechanical-only); counted drafts by source kind (`counting.py`; the Source values in `round-folder-layout.md` section 6a, with `scan` shown as "phrase scan"); mechanical spread where measured (for example, "the same sign-off in 13 of 15 increase drafts"); traces (10-character form, linked to the trace appendix).

## Report sections

In this order: Key findings; How this is built and how to use it (unit of analysis, categories, judge mapping, how to use it for the scatter plot); Distribution by category (overall, by action type, by evidence type); Failure modes (a summary table across every row, then full detail cards grouped by category, then the held-or-dropped list); Trace table (one row per rated or counted draft); Caveats; Trace appendix (one entry per cited trace); Evidence table (one row per evidence item).

The summary table's last column, "Counted drafts by source," holds the same split as each card's source line. A draft two sources back counts under each, so the split can sum past the Drafts column.

### Distribution tables

- **By category:** filed-only count and share, filed-plus-existing count and share, and a Clinical (core + edge case) versus Non-clinical rollup row.
- **By action type:** rows are categories, columns are the round's action types; a row spanning several action types counts once per type.
- **By evidence type:** rows are categories. Columns are "2+ reviewers," "1 reviewer," "eval judge only," "mechanical count only." A legacy edit-diff row credits the trace's rater, so it counts as a reviewer.

### Failure-mode detail card

```
##### [<KEY>](<jira link>): <title>

- **Status:** Filed <date> | Existing ticket, this round's evidence added <date>. **Priority:** <P> | existing ticket.
- **Category:** <primary>. **Judge that should catch it:** <judge(s)>.
- **What goes wrong:** <1 to 3 sentences>
- **Expected:** <1 to 2 sentences, or "Ask on the ticket:" line for a comment unit>
- **Evidence:** <n> draft(s); reviewers <names>; verdicts <mix>; <reviewer-stated|mechanical> <n>. A round built before v3.0 may also show `legacy audit` on a row the old checklist wrote.
- **Counted drafts by source:** <source kind> <n>, … | none.
- **Traces:** [tr-xxxxxxxxxx](#tr-xxxxxxxxxx), …

  - `tr-xxxxxxxxxx` <reviewer> (<verdict>): <quote or paraphrase>
```

### Held or dropped without a ticket (section 3c)

One row per failure mode that got no ticket and no comment this round. Columns: Failure mode (its title, never an FM ID) \| Action types \| Severity class \| Counted drafts \| Providers \| Why. Why is the filing call's reason (for example, "seen once, efficiency"), "for the product owner: <reason>", "dropped by the product owner" (a Gate 3 drop), or "no ticket this round" when no call applies. Every failure mode whose filing call is `hold` becomes a `held` row in the evidence ledger, including one with no 3c row. A failure mode the product owner dropped at Gate 3 never carries.

A held or dropped failure mode that an existing ticket partly claims stays in that ticket's row, so it gets no 3c row. Its other evidence rows still read `failure mode (held, no ticket)` or `failure mode (dropped by the product owner)`.

### Trace table (one row per rated or counted draft)

Columns: Trace ID (full form) \| Action type \| Medication \| Ratings \| GOOD \| BAD \| Reviewers (verdict) \| Failure modes a reviewer or eval judge raised \| Failure modes from mechanical count only \| Other outcomes (input-issue, not a failure mode, logged) \| Judge pass/fail \| Judge notes. A ticket an eval judge raised alone reads `<ticket row label> (eval judge <judge names>)`; the label is the key, plus its row note on an existing ticket with two rows. A draft counted only through phrase-scan spread appears only when the spread backs a ticket, and lists that ticket in the mechanical column. An unrated draft that backs a held or dropped failure mode shows that outcome under Other outcomes. Leave the last two columns empty for the Evals team to fill in.

### Trace appendix (one entry per cited trace)

One `<a id="tr-xxxxxxxxxx"></a>` anchor plus a `### tr-xxxxxxxxxx (<action>)` heading per trace, holding: full trace ID, medication on the action, tickets it supports, the messages before the draft (labeled *Patient* or *Provider / care team*, most recent last), the full draft, and every rating on that draft (reviewer, verdict, redacted comment). An unrated draft says so and points to the failure-mode detail. Names are anonymized; nothing else is changed, matching the filed tickets. Every trace table anchor referenced in the failure-mode cards must resolve to a defined anchor here. Every trace with a reviewer-raised or mechanical-only failure mode needs an entry, except a spread-only draft missing from the ticket's own evidence list.

### Evidence table and CSV

The evidence table has one row per rating, plus one per edit, failed judge verdict, Slack report or session mention that no rating carries. Legacy checklist rows add none. The CSV ships alongside the doc as the join-ready copy of this table. Exact header (Round 3's `round-3-rating-rows.csv` predates `source`):

```
label_id,trace_id,action_type,medication,reviewer,rated_at_utc,verdict,tags,outcome,failure_mode_tickets,categories,judge_pass_fail,judge_notes,source
```

`source` is the row's source kind: `thumbs-downs`, `labeling`, `edits`, `evals`, `interviews` or `slack`, or `ratings` when a rating's sheet isn't recorded and the sheets differ in kind. Only rating rows carry a label ID and a rated time. Every other row carries the ledger's Verdict (`ledger-schema.md` section 1), such as `FAIL` on an eval row.

`trace_id` is the full 32-character form, except that a session row holds its session reference. An eval row's reviewer is `eval`, and its tags name the judge. `failure_mode_tickets` holds the tickets a row maps to, and `categories` their categories.

`outcome` holds the row's other destinations, semicolon-joined, and is blank when the row maps only to tickets. Its values are `coverage only (thumbs-only)`, `coverage only (no issue row)`, `input-issue`, `not a failure mode`, `logged`, `failure mode (held, no ticket)` and `failure mode (dropped by the product owner)`. A round built before v3.0 may still show `coverage only (audit, no issue)` on a legacy row. New rounds do not write it. A held failure mode is a real one deliberately not ticketed this round.

`judge_pass_fail` and `judge_notes` start blank for the Evals team to fill. The in-document evidence table shows a narrower column set for readability (Label ID, Trace ID, Source, Reviewer, Rated (UTC), Verdict, Tags, Outcome); the CSV always carries the full header above. For the verdict scatter plot, filter the CSV to rows with a label ID.

## Key findings to compute

Write these as data-grounded bullets, each recomputed from the built tables, never asserted from memory of the plan:

- **Category distribution, with and without existing-ticket rows.** The clinical share (core + edge case) counted filed-only versus filed-plus-existing.
- **BAD ratings split by destination.** Of all BAD ratings, how many point to a failure mode versus an input the draft doesn't control versus something that is not a failure mode. State the total a judge should not be expected to catch (input-issue plus not-a-failure-mode BAD ratings).
- **Split verdicts.** Of drafts with a reviewer-raised failure mode, how many drew both GOOD and BAD verdicts from different reviewers. Flag that judge correlation should use rating-level rows, not a per-draft majority.
- **Evidence strength distribution.** Rows backed by 2+ reviewers, by exactly 1, by eval judges only, and by mechanical count only.
- **Source differences, when the round has more than one source.** Name what one source surfaced that the others didn't (for example, failure modes seen only in provider edits or only in eval judge failures). Skip this bullet for a one-source round.
- **Held or dropped.** How many failure modes got no ticket and no comment, and why (held below the floor, for the product owner, dropped by the product owner).
- **Likely judge gaps.** Categories with no dedicated judge (Writing quality) or only partial coverage (Templated repetition via `doctor_relationship`), and any specific open clinical decision a judge can't currently resolve (Round 3 example: whether an escalation level is sufficient, not just present).

## Caveats to always include

- **Generating build** (per `generation-provenance.md`): run ID, that the exact commit is unconfirmed, and the earliest PR the draft text proves the build is at or after.
- **Thumbs-only ratings.** State the count and that they carry no written reason.
- **Evidence strength.** Restate the 2+/1/mechanical-only split from the key findings, and that a mechanical spread figure not in a ticket's own evidence list has no appendix entry of its own.
- **How priority was set.** State plainly that the filed priority reflects the failure mode's severity, how often it recurred, and the product owner's row-by-row call at Gate 3. That call can differ from what the rubric scored. A one-off below the filing floor gets no ticket; it sits in the held list. Tell the reader to use category, not priority, as the clinical-severity signal.
- **Reviewer list.** Name every reviewer and flag which one is the Care product reviewer (their own labeling comments are evidence too, not a conflict).
- **Names-only anonymization.** State that messages and drafts appear in full with names replaced by placeholders, and that reviewer comments carry forward any `[redacted]` already in the ratings.

## No session artifacts

Never write an FM, T, C, D or ledger row ID, a CR rule ID, or a file name from the round folder, anywhere in the report, the prose, or the CSV. Ticket keys are the only IDs that appear. Trace IDs appear in full (32 hex characters) in the trace table, appendix and CSV, and as `tr-` plus 10 characters everywhere else.

## Prose agent brief

**Inputs:** the computed tables and counts only (the distribution tables, the key-findings numbers, the caveats list), never the plan or QA files, and never a fresh read of `export/` or the ledgers.

**Task:** write `cluster_analysis_prose.md` with a title, an opening paragraph, the Key findings bullets, and the "How this is built and how to use it" narrative sections, inserting two literal markers: `{{TABLES_A}}` after the narrative sections, where `scripts/build_cluster_analysis.py` splices in sections 2 to 4 (distribution, failure-mode summary, detail and held-or-dropped list, trace table); then a hand-written `## 5. Caveats` section (the script does not generate it); then `{{TABLES_B}}` as the last line, where the script splices in section 6 (trace appendix) and section 7 (evidence table). Every number in the prose must trace to a computed table; never estimate or round from impression.

**Output:** `cluster_analysis_prose.md`.

**Returns:** path, a list of every numeric claim made and the table each traces to.

## Plan QA brief

**Inputs:** the Step 5 category-assignment plan, `failure-modes.md`, `dedup-verdicts.md`, `filing-ledger.md`, `comment-ledger.md`, `ratings.md`, `input-issues.md`, `row-map.md`, the judge doc at `round.json` `judges_doc`.

**Checks:** every filed ticket and every existing-ticket row appears exactly once; category counts foot correctly against the row-by-row table; each row's category matches this spec's taxonomy definitions (not a near-miss reading); each row's judge choice matches the judge doc's actual scope (for example, `drives_results` only checks that an action was named, not whether it was clinically sufficient; don't assign it to a row where the real gap is a wrong-but-present action); headline data facts (thumbs-only count, input-issue count, not-a-failure-mode count, reviewer list, no-P0s-filed fact) check out against `ratings.md` and `row-map.md`; the source list cites every file the plan draws a fact from, including provenance files.

**Output:** `qa-cluster-plan.md`, in the Type \| Finding \| Evidence \| Recommendation format, with a sentence up front naming what was confirmed clean.

## Doc QA brief

**Inputs:** the built report and CSV, the (post-plan-QA) category-assignment plan, `build_cluster_analysis.py`, `cluster_analysis_prose.md`, `export/*.md` (grep by trace ID, never loaded whole).

**Checks:** every row's category, secondary and judge string matches the plan exactly; every count in the Key findings and distribution tables recomputes from the underlying data; every in-page trace anchor resolves and every qualifying trace has an appendix entry; every Jira and judge-source link is well-formed and resolves to the right key; CSV trace IDs are the full 32-character form, apart from session rows; the CSV has one row per evidence-table row; each card's source line matches its summary-table column; no failure mode in 3c also sits in a ticket row; no real person's name anywhere, including inside a quoted comment carried over from a ticket; no session artifacts; the writing checklist (em dash, banned words, filler, vague ranges, paragraph length) passes on the prose sections; spot-check 5 appendix entries against `export/*.md` for action type, medication, messages and draft text.

**Output:** `qa-cluster-doc.md`, same format as the plan QA brief, plus a one-line summary of defect and question counts.
