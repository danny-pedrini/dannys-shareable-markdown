# Ticket spec

Every drafting agent follows this file exactly. Values come from `round.json` (epic, project, labels, action names, evidence opener, source links) per `round-folder-layout.md`. Tickets and comments are read by AI Eng, Clinical and Care Ops people outside this folder.

> **Source:** Round 1.5 `ticket-spec.md` (approved) and Round 3 `ticket-spec-r3.md` (overrides), generalized. Writing rules: repo `CLAUDE.md` "Writing" section and `forbidden-writing-patterns.md`, both mandatory and not repeated here.

## Hard rules

1. **No session artifacts in ticket text.** Never write FM, N, D, T, C or EP IDs, ledger row IDs (`PI-001`, `A12`), CR rule IDs, or file names from the round folder. Cite drafts by trace ID only.
2. **Trace IDs.** In the title, use `tr-` plus the first 10 hex characters. In the body, use the same 10-character form. The full 32-character form appears only in the cluster report (`cluster-report-spec.md`). Every trace in the evidence must come from the ledgers (`ledger-schema.md`) or from the failure mode's spread drafts (`clustering-and-dedup.md` section 2a).
3. **No PHI.** Quote reviewer comments and the offending AI-draft sentence only, with patient names, ages, weights, BMI, BP, labs, dates and locations replaced by `[redacted]`. Never quote patient-message text in the Evidence bullets; paraphrase what the patient asked in one generic clause. This redaction rule does not apply to the "Draft and thread" section below, which carries full text by design.
4. **Describe behavior, not implementation.** Say what the draft must do, not how to change the prompt.
5. **Cite sources with links a reader can open** (list in "Clinical source links" below). For a reviewer-stated rule with no written source, write "Reviewer rule (\<handle\>), needs clinical confirmation."
6. **Writing rules** (repo `CLAUDE.md`, `forbidden-writing-patterns.md`), all mandatory. Quoted reviewer text and quoted draft sentences are exempt from the banned-word and numeric-range checks; everything the drafting agent writes itself is not.
7. **No conflict-flag tickets while the scope is off.** See "Scope switches" below.
8. **Placeholders filled by the EMR or provider are inputs.** Never ask a draft to fill one; see `clustering-and-dedup.md` for the classification rule.

## Title pattern

`<action>: <expected behavior in plain words> (tr-xxxxxxxxxx)`

**Session-only tickets (v1.1).** A ticket whose evidence is only feedback-session or interview feedback, with no trace, ends with the session date instead: `(session 2026-10-29)`, or `(sessions 2026-10-29, 2026-11-02)` when more than one session raised it. Use the trace form whenever any trace supports the failure mode. `check_tickets.py` accepts both.

- `<action>` comes from `round.json` `batches[].action` for this round (Round 3 example: `prescribe_visit`, `increase_dose`, `decrease_dose`, `repeat_step`, `send_message`, `refer_visit`; Round 1.5 used `prescribe_initial`, `repeat_step`, `titrate_up`, `titrate_down`, `refer`, `send_message`).
- When one ticket spans action types, join them with slashes, for example `repeat_step/titrate_up/titrate_down:`. When it spans every action type the round uses, write `all actions:`.
- Pick the trace that best shows the worst instance.
- Keep titles under about 110 characters. Treat this as a hard ceiling to check before drafting, not a guideline to catch at QA: Round 3's plan QA found 7 of 46 titles over length and had to send them back.
- Round 3 examples: "send_message: answer the question that was asked, don't switch the plan"; "titrate_down: give a reason when the decrease goes against an increase request."

## Body sections, in order

```
## Problem
## Layer
## Evidence
## Draft and thread
## Expected behavior
## Eval check
## Out of scope
## Related
## Source
## Parent
```

### Problem

1 to 3 short paragraphs: what the draft does wrong, and what happens to the patient if a provider sends it unedited.

For a **Regression**, open with "Regression of \<epic-project\>-xxxx (Done \<date\>)," and say what is still happening.

### Layer

One line: draft copy / shared template text / chart or context input / provider-action conflict the draft should flag.

### Evidence

Open with `round.json` `evidence_opener` (Round 3 example: "Round 3 provider review (ratings Oct 15 to 19, 2026). Drafts from run popular-shad-845, generated on or before Oct 14, 2026."). Add the `evidence_opener` of each source the bullets cite, when that source has its own (`round-folder-layout.md` section 1).

One bullet per trace, in the form for its evidence:

- Rating: `tr-xxxxxxxxxx` (\<action\>). \<Reviewer handle\> (\<GOOD|BAD\>): "\<short verbatim quote, redacted\>". Draft: "\<offending sentence, redacted\>".
- Edit: `tr-xxxxxxxxxx` (\<action\>). \<Provider handle\> edited the draft before sending: \<what the provider changed, one line\>. Note: "\<short verbatim note, redacted\>" (omit when there is none). Draft: "\<offending sentence, redacted\>".
- Eval: `tr-xxxxxxxxxx` (\<action\>). Eval judge \<judge name\> failed the draft: "\<short judge reason, redacted\>". Draft: "\<offending sentence, redacted\>".
- Slack: `tr-xxxxxxxxxx` (\<action\>). \<Provider handle\> reported it on Slack: "\<short verbatim quote, redacted\>". Draft: "\<offending sentence, redacted\>".

- Earlier round: `tr-xxxxxxxxxx` (\<action\>), \<round name\>, \<month day, year\>. Then the wording of the Edit, Rating, Eval or Slack form from the handle on. Use it for a draft from a round listed in `round.json` `prior_rounds` that the failure mode's counts include (for example through the evidence ledger). The ID must be in that round's `export/*.md`, and the bullet must start with the words `Earlier round:` so `check_tickets.py --traces` looks there. A trace from this round never takes the label. Each Earlier-round trace gets a thread block like any other Evidence trace.

A trace with more than one kind of evidence gets one bullet that gives each in turn. An edit is provider evidence, so write it in the Edit form, never in the Rating form: the Rating form needs a thumbs-down or labeling rating by that handle on that trace (`ratings.md`). A provider who only edited the draft gets the Edit form. Medium- and low-confidence diff-only edits are supporting evidence only (`priority-rubric.md` section 2). Use the Edit form for them, and add "(supporting)" after the handle.

Spread drafts (identical defective text found by the phrase scan) go on one line after the bullets, as IDs only: `Same text in: tr-…, tr-…`. The line is not a bullet: its traces get no thread block and don't count toward the 8 below.

List every draft that supports the failure mode. For more than 8, list 8 and add "Also: tr-…, tr-…" with the rest, as IDs only.

**Session evidence (v1.1).** When interview or feedback-session statements back the failure mode, add one bullet per session after the trace bullets: `session 2026-10-29. <n> pilot provider(s): "<short verbatim quote, redacted>".` Never name a participant. A session-only ticket opens Evidence with `round.json` `evidence_opener_session` (falling back to `evidence_opener`) and has no "Draft and thread" section, because it cites no trace. The Source section links the feedback-sessions notes from `round.json` `source_links`.

### Draft and thread

Present when `round.json` `scope.draft_and_thread` is true (default true; memory `provider-draft-tickets-include-thread`), except on a session-only ticket, which cites no trace.

- **Holds:** the messages shown to the model before each draft, then the full draft, for every trace named in the Evidence bullet list above, including an `Earlier round:` trace (built from that round's export). "Also:" traces stay as IDs only and get no thread block.
- **Built from** the batch's raw thread blocks, then an anonymization pass (brief in `ticket-qa-briefs.md`), then inserted into the ticket.
- **Anonymize names only:** patient, provider, staff and family names become placeholders (`[PATIENT_NAME]`, `[PROVIDER_NAME]`, or the model's own tokens like `{{provider_intro}}`). Keep weights, dates, doses, locations and every other detail exactly as written. This supersedes any earlier "never copy patient-message text" rule for this section only; the Evidence section above still redacts.
- **Format:** one subheading per trace, `#### \`tr-xxxxxxxxxx\` (\<action\>)`, then "**Messages before the draft**" (blockquoted, labeled *Patient* or *Provider / care team*, most recent last) and "**Draft**" (blockquoted, full text).
- **Length discipline:** the whole ticket body must stay under Jira's 32,000-character limit. If every Evidence trace's thread block would push it over, move the least essential Evidence traces to "Also:" (IDs only) until it fits. Never truncate a thread block itself, and never drop the Draft and thread section to make room.

### Expected behavior

Bullets, testable, each with its source: a link (see "Clinical source links"), a "Reviewer rule (\<handle\>), needs clinical confirmation" tag, or a plainly stated ruling with no attribution (see "Rulings" below). Only tag "needs clinical confirmation" on a clinical question; a plain writing or formatting rule never carries it.

### Eval check

How the re-eval proves the fix. Name the Evidence traces as golden cases and state pass or fail for each in one line. Add any judge or deterministic check that fits, such as "no draft contains the string X."

### Out of scope

Carve-outs, and sibling tickets by key.

### Related

Jira keys with one line each: the prior ticket this regresses, open siblings, Won't Do context. Before filing, re-verify any characterization of a related ticket's scope against its current description; do not trust a summary line alone.

### Source

`round.json` `source_links` (ratings link: "reviewer verdicts and comments, by trace ID"; export link: "the drafts and the messages before them, by trace ID"), plus the clinical source list below as the ticket's expected-behavior bullets need them.

### Parent

`<jira.site>/browse/<jira.epic>` from `round.json`.

## Draft record format (what the drafting agent writes to its output file, not the ticket itself)

For each ticket:

```
### T-<n>. <title>
- Source failure mode (working ref, not for Jira): <FM ID>
- Dedup status: <New | New (<part> part) | Regression of <key>>
- Issue type: <round.json jira.issue_type>
- Labels: <round.json jira.labels>, <safety | efficiency> (v1.2: every ticket carries one; see priority-rubric.md section 0)
- Recommended priority: <P0 - Unbreak NOW | P1 - Feature Blocker | P2 - Non-Blocker>
- Approved priority: <added after Gate 3 from Danny's call; omit before>
- Rationale: <exactly two sentences: the first names the severity class and the worst instance; the second names the band with its counts and the level the rubric's section 0 table gives>
- Counts: <n> counted drafts, <n> counted instances, <n> providers; band <one-off | recurring | common | none>; sources <kinds>
- Needs clinical confirmation: <yes | no>. Say yes when the expected behavior is uncodified.
- Merged from: <other working refs absorbed into this ticket, or omit the line if none>

<ticket body exactly as it would be filed>
```

For each **comment on an existing ticket**:

```
### C-<n>. Comment on <key> (<ticket summary>)
- Source failure mode (working ref): <FM ID>
- Purpose: <add evidence | ask the re-eval to confirm a fix merged around generation time | eval-process>

<comment body: 1 short paragraph plus an evidence list in the same bullet format as Evidence, the Source link, and a closing ask>
```

## Comment format and purposes

Three purposes, named on the "Purpose" line above:

1. **Add evidence.** The ticket's scope already covers this round's finding. Add the new traces as more cases, in the Evidence bullet format, with a closing ask such as "Please add this trace as a golden case for the fix." A held one-off can get this comment where it helps (`priority-rubric.md` section 0); the comment says the issue was seen once this round.
2. **Ask the re-eval to confirm a fix merged around generation time.** The matched ticket closed Done at or near this round's generation window, so this round cannot confirm whether the fix reached production before the drafts were generated (`clustering-and-dedup.md` deploy check). Ask that the next re-eval include the named trace(s) as golden case(s) and state pass or fail. **Never call this a regression.** A regression needs its own new ticket per the spec above, filed only when the deploy check shows the fix was in production before the generation bound and the behavior still happened.
3. **Eval-process.** A comment about eval mechanics rather than a specific new trace. Use only when neither purpose above fits.

**Claims about the target ticket.** Read the target in full from Jira (description, every comment, Development field) before writing any sentence about what it says. Quote its exact words when a comment says the ticket asks for, allows or conflicts with something. Never describe a target from the plan, the dedup scope cell or memory: a comment that misstates what a ticket says gets posted and misleads the people who maintain that ticket. The format checker reads every comment target in full (its live-Jira-keys check) and E33 fails a target it did not.

## Rulings stated plainly

A product owner's own ruling (recorded as a CR rule in `clinical-rules.md`) is stated as the expected behavior directly, with no attribution and no link. Per repo `CLAUDE.md`: never cite the product owner or their own docs as a source in anything someone else reads, including a document they authored (for example the Few-Shot Exemplar Library). Clinical sources keep their links.

## Clinical source links

Verify each link is still current before using it; a round can move a doc or a snippet ticket.

- Ratings and export links: `round.json` `source_links`.
- WL Clinical Guidelines (Docebo; quote the section heading): https://himsandhers.docebosaas.com/learn/courses/927/weight-loss-clinical-guidelines/lessons/2229:938/weight-loss-clinical-guidelines
- Rx guideline questions sheet: (internal link)
- Message content and eval requirements (PRD): (internal link)
- Voice and Style Guide: (internal link)
- Few-Shot Exemplar Library: (internal link)
- EMR acceptance criteria: (internal link)
- Approved snippets: `round.json` `snippets_ticket` (Round 3 example: QCARE-31, formerly MLENG-5035)
- Jira epic: `<jira.site>/browse/<jira.epic>`

To map a CR rule to its source document, read the rule's Source column in `clinical-rules.md` and its alias legend:

- PRD, dimension and Tier refs: the PRD link.
- PERSONA and voice refs: the Voice and Style Guide.
- EXv2: the Exemplar Library.
- AC and EMRREQ: the EMR acceptance criteria.
- SNIP: the approved snippets ticket.
- DOCEBO: Docebo, with the section heading.
- Q#: the Rx guideline questions sheet, with the Q number.

## Scope switches

- **Conflict flags.** When `round.json` `scope.conflict_flags_in_scope` is false, never ask a draft to flag a provider decision that conflicts with a protocol; log it in `input-issues.md` instead. When true, follow `priority-rubric.md` section 3's conflict-flag row: one ticket per conflict type.
- **Draft and thread.** When `round.json` `scope.draft_and_thread` is false, omit the section entirely; do not leave an empty heading.
- **Held topics.** A ticket that touches a topic the product owner has not ruled on (`clustering-and-dedup.md` section 3) must hold under every reading of the open question. Never ask a draft to add or remove text on that topic unless the ticket plan row says so. Round 1 edits pass example: the price question.

## Priority

Apply `priority-rubric.md`. The severity class comes from the worst credible instance if sent unedited, and the band from the counted instances. The section 0 table turns the two into the level.

The recommended level and rationale come from `ticket-plan.md` after plan QA. A drafting agent that finds the evidence contradicts the planned level writes the level the rubric gives and explains why in one line under the draft record; it does not silently follow the plan.

## Consolidation rule (merge before review)

Apply after the per-failure-mode ticket plan, before Step 3 ticket review: failure modes that share one fix location and one expected behavior covering every row become one ticket spanning the action types involved. List every absorbed failure mode on the "Merged from" line of the draft record.

Round 3 example: after reviewing 46 cards, Danny asked to consolidate redundant tickets, taking 46 down to 37: the three sign-off tickets (T-15, T-22, T-30), goal weight (T-14, T-23), snippet integration (T-21, T-36), Customer Support routing (T-31, T-40), and the same-instruction-twice pair (T-25, T-44).

## Review card format (`ticket-review.md`)

Group every ticket by frequency band (`priority-rubric.md` section 2). Explain in one paragraph why there are N tickets (the clustering rule makes one ticket per wrong behavior per action type, so a repeated pattern becomes one ticket per message type):

| Band | Meaning |
| --- | --- |
| Common | 5+ counted drafts from 2+ providers |
| Recurring | 2+ counted instances |
| One-off | 1 counted instance, filed because it's severe safety or because the product owner moved it to file at Gate 2. A moved one-off scores at its recurring level. |
| None | No counted instance. Severe safety goes to the product owner at Gate 2. Below severe safety, it holds. |

**Summary table columns:** Ticket \| Band \| Issue (short) \| Recommended \| Clinical blind \| Provider blind \| Counted drafts \| Providers \| Sources \| Raised by \| Reviewers raising it \| Rated those drafts \| Mechanical spread. Within a band, order by recommended priority, then counted drafts.

**Each card:**

```
### <Ticket>. <title> (<trace>)

- **Band <band>:** <counted drafts>, <counted instances>, <providers>; sources <kinds>. Say "one provider" when that's true.
- **What's wrong:** <one or two sentences>
- **Expected:** <one line>
- **Raised by:** <names>. **Reviewers who rated those drafts:** <names> (<n>).
- **Drafts:** <trace list>
- **Priority:** recommended <P>; clinical-quality blind <P>; provider blind <P>. Needs clinical confirmation: <yes/no (why)>.
- **Why that priority:** <one or two sentences>
- **Related tickets:** <keys>
- **Evidence:**
  - <trace>, <reviewer> (<verdict>): "<quote>"
- **Your call:** <mandatory line, below>
```

**"Your call" line (mandatory, `round-folder-layout.md` section 4; this is what E8 parses):**

```
Your call: keep <P0|P1|P2>
```
or
```
Your call: drop (<reason>)
```

followed by the product owner's words verbatim on the next line. Round 3 predates this exact format and recorded "Your call: Issue? Yes. Priority: P1." instead; new rounds use the mandatory two-line format above.

## Approval table format (`ticket-drafts.md`)

Mandatory columns, in this order (`round-folder-layout.md` section 4; this is what E5 parses): Draft \| Title \| Recommended \| Clinical blind \| Provider blind \| Disagreement \| Rationale. Disagreement is `yes` or empty. Rows with `yes` come first, then rows sort by recommended priority (P0 first), then by counted drafts (most first). From v1.2, add a `Label` column after Rationale (`safety` or `efficiency`, pre-filled from `priority-rubric.md` section 0) so Danny can flip it at Gate 3.

From v2.0, add `Band` and `Counted drafts` after Label. Append optional columns after these if useful (Round 3 example: Merged from, Needs clinical confirmation).

The file has four sections, with these exact headings, because `add_threads.py`, `check_tickets.py`, `build_review_sheet.py` and `build_cluster_analysis.py` find them by text:

1. `## 1. Approval table`: the table above.
2. `## 2. Not filed`: a table with columns Ticket \| Why, for anything dropped or merged. The Why cell starts with exactly `Merged into T-<n>` for a merge or `Dropped (<reason>)` for a drop; `build_cluster_analysis.py` parses both. Write the heading even when the table is empty.
3. `## 3. Comments`: a pointer to the full comment file ("Full text in `ticket-comments.md`: C-1 \<key\>, C-2 \<key\>, …").
4. `## 4. Full ticket drafts`: the full ticket drafts in the draft record format above. `add_threads.py` exits non-zero without this heading.
