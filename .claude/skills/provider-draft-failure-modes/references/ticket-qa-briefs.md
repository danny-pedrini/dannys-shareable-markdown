# Ticket QA briefs

Ready-to-fill subagent briefs for Step 3 and Step 4. Fill every `{placeholder}` with the round's real paths before spawning. Every QA output uses the same four-column table: **Type \| Finding \| Evidence \| Recommendation**, where Type is `DEFECT`, `QUESTION` or `ADDITION` (memory `ticket-filing-plan-qa-write-qa`; the adoption rule for findings is in root `CLAUDE.md` "How to work with Danny"). A QA agent reports; it does not fix. The orchestrator fixes defects, implements sound additions with a change log, and brings questions and Danny's-ruling conflicts to the product owner.

Sections 8 to 10 hold full brief templates (drafters, anonymizer, format checker), and section 11 maps each role to its template. Copy a template to `<round>/briefs/3-<role>.md` with its placeholders filled, then give the subagent that path. Sections 1 to 7 describe the other roles in the shorter Inputs, Task, Output form.

## 1. Ticket plan QA

**Inputs:** `{ticket-plan.md}`, `{failure-modes.md}`, `{cluster_defs.py}`, `{watch-list-prior.md}`, `{dedup-verdicts.md}`, `{priority-rubric.md}`, `{ticket-spec.md}`, `{clinical-rules.md}`, `{STATUS.md}` (its "Gate 2 answers").

**Checks:**
- **Coverage.** Every New and every Regression failure mode whose filing call is `file` appears in exactly one `ticket-plan.md` row (a ticket, a comment, or a merge target). The call comes from `failure-modes.md`, or from a Gate 2 answer that moved it to file. No failure mode is planned twice, and none of the re-eval or covered-by-open-ticket failure modes appears as a new ticket.
- **Held items.** Every held failure mode is in the plan's "Not planned" section (the ledger update follows Step 4), plus an evidence-comment row where the plan gives one. A held failure mode planned as a new ticket is a DEFECT, unless consolidation lifted it over the floor or Danny moved it at Gate 2.
- **Decision items.** Every decision item Danny left open at Gate 2 (a `DECISIONS` entry in `cluster_defs.py` with no Gate 2 answer) appears in exactly one row: a `[Product Discovery]` Task per `priority-rubric.md`, or a comment on the existing ticket that already tracks the question.
- **Consolidation calls.** Every merge in the plan passes the merge test in `ticket-spec.md` ("Consolidation rule"): one shared fix location and one expected behavior that covers every absorbed row. Flag a merge that doesn't, and flag a merge candidate the plan missed.
- **Priority basis.** Each row's recommended priority follows the `priority-rubric.md` section 0 table, from the Gate 2 severity class and the band its counts give. Check the class against the worst credible instance its rationale names. Check the counts against `failure-modes.md`, recomputed for a consolidated ticket so each draft and provider counts once. Check the order within each level against section 2, step 6.
- **Dedup basis.** Each row's dedup status matches `dedup-verdicts.md`'s final verdict for that failure mode. A row claiming "New" when dedup found a covering ticket is a DEFECT.
- **Format.** Title pattern and length (`ticket-spec.md`), "needs clinical confirmation" set wherever the expected behavior is uncodified or the evidence is mechanical-only, no unsupported related-key citations.

**Output file:** `qa-step3-plan.md`. Table: Type \| Finding \| Evidence \| Recommendation. Add a short "Checks that passed" paragraph naming what was verified clean, and a one-paragraph summary.

**Returns:** path, defect count, question count.

## 2. Blind clinical scorer

**Agent type:** `clinical-quality-exec-reviewer`.

**Inputs:** `{ticket-drafts-blind.md}` and the full `{priority-rubric.md}`. `scripts/make_blind.py` builds the blind file. It strips the recommended priority, rationale, dedup status and working-ref lines so scoring is genuinely blind, and keeps each ticket's Counts line. No other file; do not let this agent see `ticket-plan.md` or `dedup-verdicts.md`.

**Task:** score every ticket P0, P1 or P2 with the rubric. Take the severity class from the worst credible instance in the evidence and the band from the Counts line; the section 0 table gives the level. A one-off below severe safety scores at its recurring level when the product owner moved it to file. Give a one-line reason per ticket.

**Output file:** `blind-scores-clinical-quality.md`. Table: Ticket \| Title (short) \| Your priority \| Rationale (one line). A longer clinical note column is fine to add, but the one-line Rationale is the minimum the approval table needs.

**Returns:** path, score counts by priority, count that disagree with the plan's recommended priority (the agent won't know the recommended priority, so the orchestrator computes this after the fact).

## 3. Blind provider scorer

**Agent type:** `telehealth-provider-reviewer`.

**Inputs:** the same `{ticket-drafts-blind.md}` and `{priority-rubric.md}`. Run in parallel with the clinical scorer, never sequentially (two scorers reading the same blind file independently is the point).

**Task and output:** identical to the blind clinical scorer above, writing `blind-scores-provider.md` in the same format.

**Returns:** same as above.

## 4. Format checker

The brief template is section 10. This section keeps the rules the checker follows and what the orchestrator runs first.

**Inputs:** `{ticket-drafts.md}` or the per-batch `ticket-drafts-<code>.md` files, `{ticket-comments.md}`, `{round.json}`, `{export/*.md}` (grep by trace ID only, never load a batch file whole; an `Earlier round:` bullet's trace is in the `export/*.md` of a `prior_rounds` round), `{clinical-rules.md}`, `{ledger/*.md}`, `{dedup-qa-*.md}`, `{ticket-plan.md}`, `{ratings.md}`.

**Scripted checks, run by the orchestrator before this agent and on every fix round.** Do not redo them. `check_tickets.py --tickets` checks the title pattern, session artifacts (FM, T, C, D or ledger row IDs, CR rule IDs, round-folder file names), the writing hard searches and body length. `--traces` checks that every `tr-` ID is `tr-` plus exactly 10 hex characters and a real prefix of a trace in `export/*.md` (an `Earlier round:` bullet: in a `prior_rounds` export). `--threads` checks the Draft and thread section when `round.json` `scope.draft_and_thread` is true: one subheading per Evidence trace, no "Also:" trace expanded, and no section on a session-only ticket. `--conflict` checks that no filed failure mode is a conflict flag while the scope is off.

**Checks:** the eleven checks are listed once, in the section 10 template (names, titles, evidence accuracy and form, counts and labels, live Jira keys with a full read of every comment target, comment content, writing, rulings, placement, session-only evidence). Edit them there; this section holds no second copy.

**Output file:** `qa-step3-format.md` (a fix round writes `qa-step3-format-round-2.md`). A Failures table in Type \| Finding \| Evidence \| Recommendation; write "No failures found" if clean. Add a PASS/FAIL counts table by check and the list of traces checked. Add a "Jira keys verified" table, `Key | Method | Result`, with one row per Jira key in the drafts and comments. Method is `full read` or `scope cell (<dedup-qa file>)`; E29 parses it, and E33 requires `full read` for every comment target.

**Returns:** path, failure counts by Type.

## 5. Anonymizer

The brief template is section 9.

**Inputs:** `{thread-blocks/<code>.md}` (raw blocks from `scripts/make_thread_blocks.py`), one file per agent. The orchestrator fills `<code>` with one `round.json` `batches[]` code, or `EARLIER` when `thread-blocks/EARLIER.md` exists (blocks for `Earlier round:` bullets), and spawns one anonymizer per file. Never give one agent two files, and never spawn a second agent for a file that already has one, except to retry one that failed.

**Task:** replace the names of patients, providers, staff and family members with placeholders (`[PATIENT_NAME]`, `[PROVIDER_NAME]`, `[STAFF_NAME]`, `[FAMILY_NAME]`, or the model's own existing tokens such as `{{provider_intro}}`). Keep everything else exactly as written: weights, dates, doses, locations, medication names, every URL. This is judgment, not regex: watch for a name folded into a quoted sentence, an unusual spelling, or a nickname a simple pattern would miss.

**Output:** the anonymized blocks (consumed next by `scripts/add_threads.py`), and separately, the full list of every name replaced written to the session scratchpad (the template writes one file per code, `names/<code>.txt`, one name per line; an older single `names-replaced.txt` also works). **Never write this list to the round folder or the repo.** E12 reads both forms from the scratchpad only, and a committed copy would defeat its own purpose.

**Returns:** path to the anonymized blocks, count of names replaced.

## 6. Filing agents

**Inputs:** `{bodies/*.md}` and `{index.json}` (title, priority, labels, parent) for the agent's disjoint slice of the approved list, `{round.json}` for `jira.project`, `jira.issue_type`, `jira.epic` and `jira.labels`.

**Task:** `createJiraIssue` per ticket: project `{jira.project}`, issue type `{jira.issue_type}`, parent via `additional_fields: {"parent": {"key": "<jira.epic>"}}`, priority by name (for example "P1 - Feature Blocker"), labels from the ticket's own `index.json` entry (`{jira.labels}` plus its one `safety` or `efficiency` label, v1.2), markdown body from the body file. **Never assign the ticket to anyone.**

**On any create failure:** stop that list immediately. Before retrying, run a JQL check (`project = {jira.project} AND summary ~ "<title fragment>"`) for a partial create. A create can succeed server-side even when the response times out. Only retry once that check comes back clean, and never retry a create without it.

**On an Amend (v1.5):** read every field you change, before and after, with `getJiraIssue` `view: full` or the issue changelog. The compact view drops `resolution` even when you request it by field key. A transition can also set or clear `resolution`, so record resolution old and new on every status change.

**Output file:** `filing-ledger-<x>.md` (one per agent, on a disjoint list). Columns (`round-folder-layout.md` section 4; what E7, E8, E9 parse): Draft \| Key \| Title \| Priority \| Parent \| Labels \| Verified by.

**Returns:** path, keys filed, any draft that stopped and why.

## 7. Filing QA

**Inputs:** `{filing-ledger-*.md}`, `{comment-ledger.md}` (after comments post), `{ticket-review.md}` ("Your call" lines), `{index.json}`, `{bodies/*.md}`, `{round.json}`, and after the ledger update `{failure-modes.md}`, `{cluster_defs.py}`, `{the evidence ledger}` and `{evidence-ledger.md}`.

**Checks, per key:**
- `getJiraIssue`; on a timeout, fall back to JQL `key = X` for that key alone and record which method verified it.
- Type matches `jira.issue_type`, parent matches `jira.epic`, priority matches the approved card in `ticket-review.md`, labels match `jira.labels` plus the one `safety` or `efficiency` label on the draft record's Labels line (v1.2), title matches the draft record exactly.
- Body not truncated: the last heading in the body file (`## Parent`) is present in Jira's returned description.
- No real name anywhere in the returned description, including the Draft and thread section.
- Each comment in `comment-ledger.md` exists on its target ticket (comment ID resolves).
- **Ledger update (once the ledger writer has run).** Run `ledger_tool.py check`. For every failure mode in `failure-modes.md` section 1 that is not an input issue, a decision item, dropped or merged, confirm the ledger has a row whose Note carries `<round slug>/<FM id>`, that its Ticket matches the key in `STATUS` (or `unticketed` for a `hold` call), that its Status follows `evidence-ledger.md` section 3, and that each counted ledger row's trace appears in an Evidence row for it. Every filed or commented key has a ledger row. Report each miss as a DEFECT.
- On an Amend (v1.5): read each changed key with `view: full` or its changelog, using the changelog for old values. Confirm the ledger's old and new values for every field the change touched, including any `resolution` a transition set or cleared. On a timeout, retry `getJiraIssue` instead of the JQL fallback.

**Epic-wide duplicate check (run once, not per key):** JQL `parent = {jira.epic} AND created >= <run date>`. Write the mandatory line (`round-folder-layout.md` section 4; what E9 parses): `Epic query: <n> issues, <d> duplicate summaries`.

**Output file:** `qa-step4.md`. A Failures table in Type \| Finding \| Evidence \| Recommendation (write "No failures found" if clean), the `Epic query:` line, and a PASS-counts table by check (matching Round 3's structure: filed once, type/parent/priority/labels, description not truncated, no real names, each comment exists). Then merge all `filing-ledger-*.md` files into the single canonical `filing-ledger.md` in the same seven-column format.

**Returns:** path, pass/fail counts, the `Epic query:` line.

## 8. Ticket drafter and comment drafter: rules both templates follow

- **One drafter per ticket, one for all comments.** Each ticket drafter writes `<round>/ticket-drafts-<code>.md`, where `<code>` is the `round.json` batch code of the ticket's title trace. When two tickets' title traces share a batch, the second drafter names its file for any other batch code with no ticket yet; the code is only a file name, and `make_blind.py`, `make_thread_blocks.py` and `add_threads.py` ignore it. A batch with no ticket needs no file: `make_blind.py` skips it. The comment drafter writes `<round>/ticket-comments.md`.
- **The orchestrator fills placeholders and writes the filled copy to `<round>/briefs/3-drafter-ticket.md` or `3-drafter-comments.md`.** Round-specific rulings go in a short notes file the brief names through `{round_notes}` (a path, never pasted text), so the template stays general.
- **Labels, epic, project, issue type and source links come from `round.json`.** The brief never hard-codes a round name, a label or a Jira key.
- **A drafter that finds the evidence contradicts the plan** writes the rubric's level and says so in one line under the record. It does not follow the plan silently.
- **Two lessons are binding.** A comment's claim about a target ticket rests on a full live read and quotes its words verbatim. A bullet backed by an edit uses the Edit form, never the Rating form.

### Ticket drafter template (copy to `briefs/3-drafter-ticket.md`)

````markdown
# Step 3 ticket drafter (one ticket)

You draft ONE Jira ticket body. Round folder: `{round}` (`<round>`). Skill folder: `{skill}` (`<skill>`). Repo root: `{repo}` (`<repo>`). Your ticket, failure mode, output code, ledger rows and counts come from your prompt as `{ticket}`, `{fm}`, `{code}`, `{rows}`, `{counts}`. Round notes for this ticket: `{round_notes}` (a path, or "none"). Tickets are read outside this folder by AI Eng, Clinical and Care Ops people. Do not launch subagents. Read every ticket, commit or file yourself.

## Read
1. `<skill>/references/ticket-spec.md`, all of it.
2. `<repo>/CLAUDE.md` section "Writing" and `<repo>/forbidden-writing-patterns.md`. Both bind everything you write yourself. Quoted reviewer text and quoted draft sentences are exempt.
3. `<skill>/references/priority-rubric.md` (section 0 first) and `<skill>/references/rules-core.md`.
4. `<round>/ticket-plan.md`: your ticket's row in the tickets table, its row in the evidence table, its "Related keys" line, and the section that lists the plan's open choices.
5. `<round>/failure-modes.md`: only the block for `{fm}` (grep `### FM-nn:`; never load the file whole). `<round>/dedup-verdicts.md`: the row for `{fm}`. `<round>/dedup/g*.md`: grep for `{fm}` and read its block plus the blocks for the Jira keys your ticket may cite. Never load a dedup file whole.
6. `<round>/clinical-rules.md` (grep for the rules your Expected behavior needs, using the rule IDs in the `{fm}` block, and read each rule's Source column; never cite the rule ID). `<round>/snippets.md` (grep only). `<round>/round.json`. `<round>/STATUS.md`: grep "Gate 2 answers" and the decisions that touch your ticket's topic.
7. The evidence. Your ledger rows are `{rows}`. The prefix letters name the batch: `<code>-<nnn>` lives in `<round>/ledger/<code>.md`. Grep each row ID in its ledger file and take only that row; never load a ledger whole. For each cited trace, grep its first 10 hex characters in `<round>/export/*.md` (grep `Trace tr-<10 hex>`, print about 40 lines after it) and read only that record: the provider draft, the message the provider sent, and the rating note. Quote exactly from there. A trace from an earlier round is in the `export/*.md` of a folder listed in `round.json` `prior_rounds`.
8. Jira (read only): the dedup files already hold each related ticket's final scope. Write the Related and Out of scope lines from those scope cells. Call `mcp__claude_ai_Atlassian__getJiraIssue` (cloud ID from `round.json` `jira.cloud_id`, one key per call) only when your sentence says more than the scope cell does. If a Jira read fails, stop and report the key and the error; never fill the gap from memory.

## Rules that bind this round
- Never write a real name. Never put an FM, T, C, D, ledger-row, CR or rule ID, a round-folder file name, "Danny" or "the product owner" in the ticket. State a ruling as a plain fact with no attribution.
- Evidence redaction is Regime A (`rules-core.md` section 6): replace patient names, ages, weights, BMI, labs, dates and locations inside quotes with `[redacted]`. Medication names, doses, units and reviewer handles stay. Never quote patient-message text in Evidence; paraphrase what the patient asked in one generic clause. A script adds the full thread afterward.
- Reviewer handles come from the ledger Reviewer column. Where the column says `unresolved`, write "A provider".
- Conflict flags are out of scope while `round.json` `scope.conflict_flags_in_scope` is false. Never ask a draft to flag a provider decision.
- Describe behavior, not prompt wording. Never ask for shorter text; a length ticket removes repeats and over-applied protocols first.
- A ticket that touches a ruled topic states the ruling from `clinical-rules.md` and `STATUS.md` as a plain fact. A topic the product owner has not ruled on holds under every reading of the open question (`ticket-spec.md`, "Held topics"). Write no dollar amount unless a ruling gives one.
- Providers are "YouHealth providers" only where you must name them; never "Hims & Hers provider".
- Voice: tight, direct, active. Paragraphs of 4 sentences or fewer. Sentences average under 20 words and none over 35. No three-clause sentences, no em dashes, no numeric ranges and no vague quantities. Run the plain-word and filler searches from CLAUDE.md on your own prose before you finish.

## What to write
One draft record in the exact format of `ticket-spec.md` "Draft record format":
- Header `### {ticket}. <title>`: the title EXACTLY as in `ticket-plan.md` (under 110 characters). If you find a better worst-instance trace, swap it in the title and in your return note; do not change the words.
- Working lines, in this order:
  - `Source failure mode (working ref, not for Jira): {fm}`
  - `Dedup status:` from the plan
  - `Issue type:` from `round.json` `jira.issue_type`
  - `Labels:` from `round.json` `jira.labels`, then the plan's `safety` or `efficiency` label
  - `Recommended priority:` the plan's level, written with its Jira name, such as `P1 - Feature Blocker`
  - `Rationale:` the plan's two sentences; if the evidence contradicts the level, write the rubric's level and explain in one line under the record
  - `Counts: {counts}`
  - `Needs clinical confirmation:` from the plan, with its reason
- Body sections, in this order and exactly: `## Problem`, `## Layer`, `## Evidence`, `## Expected behavior`, `## Eval check`, `## Out of scope`, `## Related`, `## Source`, `## Parent`. Do NOT write `## Draft and thread`: a script inserts it after Evidence.
- Problem: up to 3 short paragraphs. What the draft does wrong, then what happens to the patient if a provider sends it unedited.
- Layer: one line.
- Evidence: open with the `round.json` `evidence_opener`. One bullet per counted trace, up to 8 traces, in the spec's forms. **Provider edits use the Edit form** ("<handle> edited the draft before sending: <what changed>. Note: "<short quote>" Draft: "<offending sentence>"), never the Rating form. A trace with a thumbs-down and an edit gets one bullet giving each. Medium-confidence supporting rows use the Edit form with "(supporting)" after the handle and list only if the counted drafts number fewer than 8. A counted draft from an earlier round uses the `Earlier round:` form with its ID, round name and date (`ticket-spec.md` "Evidence"). More than 8 counted drafts: list 8 (keep the worst instance and the title trace) and add `Also: tr-…` with the rest as IDs only. Use the `tr-` plus 10 hex form everywhere. Every trace must come from your ledger rows.
- Expected behavior: testable bullets, each with its source: a link from the spec's "Clinical source links" (name the Docebo section heading), "Reviewer rule (<handle>), needs clinical confirmation" for an uncodified reviewer rule, or a plainly stated ruling. Tag "needs clinical confirmation" only on a clinical question.
- Eval check: name each Evidence trace as a golden case with a one-line pass or fail, plus any deterministic check that fits.
- Out of scope and Related: only keys that appear in your plan row, `dedup-verdicts.md` or the dedup files, each with one line saying how it differs. Add any adjacent keys the plan row lists under "Related keys".
- Source: `round.json` `source_links` with each "what" line (list a link once when the ratings link and the export link are the same sheet), plus the clinical links your Expected behavior used.
- Parent: `<jira.site>/browse/<jira.epic>` from `round.json`.

## Ticket-specific notes
Read `{round_notes}` if it is a path. It holds only this ticket's rulings and carve-outs, each already in the plan or `STATUS.md`.

## Output
Write `<round>/ticket-drafts-{code}.md`: a one-line `# Ticket drafts: {code}` header, then your record. Write in chunks (one Write, then appends). Do not edit any other file. From `<round>`, run `python3 -I <skill>/scripts/check_tickets.py --tickets ticket-drafts-{code}.md` and fix every hit in your own prose. `--traces` runs later.

## Return
ONLY: the path, ticket count, the `check_tickets.py` result line, and up to 3 one-line notes (a swapped title trace, a level that contradicts the rubric, an open question for the orchestrator).
````

### Comment drafter template (copy to `briefs/3-drafter-comments.md`)

````markdown
# Step 3 comment drafter

You draft the Jira comments listed in `ticket-plan.md`. Round folder: `{round}` (`<round>`). Skill folder: `{skill}` (`<skill>`). Repo root: `{repo}` (`<repo>`). Comments are read outside this folder by AI Eng, Clinical and Care Ops people, and they post as written. Your comments, their targets and purposes: `{comments}` (the C-n rows of the plan's comments section). Round notes: `{round_notes}` (a path, or "none"). Do not launch subagents. Read every ticket, commit or file yourself.

## Read
1. `<skill>/references/ticket-spec.md`: "Hard rules", "Evidence" (the bullet forms), "Comment format and purposes", "Rulings stated plainly" and "Draft record format" (the `### C-<n>` block).
2. `<repo>/CLAUDE.md` section "Writing" and `<repo>/forbidden-writing-patterns.md`. Both bind everything you write yourself, and the active-voice rule for sendable copy applies. Quoted reviewer text and quoted draft sentences are exempt.
3. `<skill>/references/rules-core.md` sections 1, 6 and 7.
4. `<round>/ticket-plan.md`: the comments section (targets, purposes, any split lists) and the section that lists the plan's open choices.
5. `<round>/failure-modes.md`: only the blocks for the failure modes your comments cite (grep `### FM-nn:`; never load the file whole). `<round>/dedup-verdicts.md` rows for those. `<round>/dedup/g*.md`: grep for each and read its block.
6. `<round>/generation-provenance.md`: grep for a target's timing row when a comment states a merge or deploy time (commit links come from there).
7. Evidence ledger rows for each comment's traces (the plan lists them). Each row's letters name its ledger file. Grep each row ID and take only that row. For each cited trace, grep `Trace tr-<10 hex>` in `<round>/export/*.md` (about 40 lines after) and read only that record, so quotes and draft sentences are exact.
8. **Jira, read in full before you write anything about a ticket:** every comment target and every other key a comment names. Call `mcp__claude_ai_Atlassian__getJiraIssue` with the cloud ID from `round.json`, one key per call, and read the description, every comment and the Development field. Never write a claim about a ticket from the plan, a scope cell or memory. If a read fails, stop and report the key and the error.

## Rules that bind this round
- No real names. No FM, T, C, D, ledger-row, CR or rule IDs, no round-folder file names, no "Danny" or "the product owner". State a ruling as a plain fact.
- **A claim about a target ticket rests on your live read.** When a comment says what a ticket asks for, allows or conflicts with, quote its exact words. If the live ticket differs from the plan's description of it (its status, its scope, what it asks), write the comment to match the ticket and say so in your return note. Do not soften a conflict you cannot quote.
- Trace IDs use `tr-` plus 10 hex characters, taken from the ledger rows. Evidence redaction is Regime A (`rules-core.md` section 6): redact patient names, ages, weights, BMI, labs, dates and locations in quotes as `[redacted]`; never quote patient-message text.
- Reviewer handles come from the ledger Reviewer column. `unresolved` becomes "A provider".
- **Provider edits use the Edit form of the spec, never the Rating form.** A counted draft from an earlier round uses the `Earlier round:` form.
- Conflict flags are out of scope while `round.json` `scope.conflict_flags_in_scope` is false.
- Never call anything a regression. A comment that follows a fix merged near generation time is a re-eval request only.
- Each comment is 1 short paragraph, an evidence list in the spec's bullet form (none for an eval-process comment), one Source line, and a closing ask. The Source line links the sheet from `round.json` `source_links`, with its "what" text.
- A comment that points to a ticket not yet filed uses the marker `[T-n key]`; the orchestrator fills it at filing.
- Voice: tight, direct, active. Sentences under about 20 words, none over 35. No em dashes, no numeric ranges, no vague quantities, no three-clause sentences. Run the plain-word and filler searches on your own prose.

## Purposes
The plan names each comment's purpose; `ticket-spec.md` "Comment format and purposes" defines the three. Write each by its purpose:
- **Add evidence.** The traces, each in its form; ask that they join the ticket's golden cases.
- **Ask the re-eval to confirm a fix merged around generation time.** State the merge and production deploy times with commit links from `generation-provenance.md`. List the drafts in the groups the plan gives (drafted after the deploy, and before it, with supporting rows marked "(supporting)"). Ask the next re-eval to run all of them as golden cases and state pass or fail for each. First read the target's live status; if it is not what the plan says, write to the live state and tell the orchestrator.
- **Eval-process.** No trace evidence. State the current rules plainly, quote only the target's exact conflicting words from your live read, say no edit is requested, and point to the new ticket with the `[T-n key]` marker where the plan says to.

## Output
Write `<round>/ticket-comments.md`: a `# Ticket comments` header, then the records in the exact `### C-<n>. Comment on <key> (<ticket summary>)` format of the spec, each with `- Source failure mode (working ref): <FM>` and `- Purpose:` lines, separated by `---`. Use each ticket's live summary in the header. Write in chunks (one Write, then appends). Do not edit any other file. From `<round>`, run `python3 -I <skill>/scripts/check_tickets.py --writing ticket-comments.md` and `python3 -I <skill>/scripts/check_tickets.py --traces ticket-comments.md`, and fix every hit in your own prose.

## Return
ONLY: the path, the comment count, both script result lines, and up to 4 one-line notes (a ticket whose live state differs from the plan, a count that disagrees with the failure-mode block, a quote you could not find, an open question).
````

## 9. Anonymizer template (copy to `briefs/3-anonymizer.md`)

Fill `{code}` with one `round.json` batch code, or `EARLIER`. `{round}` is the round folder. `{scratch}` is the session scratchpad folder, outside the repo.

````markdown
# Step 3 anonymizer (one thread-blocks file)

Your file code is `{code}`. Do not launch subagents. Read every file yourself.

## Task
Round folder: `{round}`. Open `thread-blocks/{code}.md` (raw blocks; read the whole file, it is small). Replace the names of patients, providers, staff and family members with placeholders: `[PATIENT_NAME]`, `[PROVIDER_NAME]`, `[STAFF_NAME]`, `[FAMILY_NAME]`. Leave the model's own tokens alone (`[Patient]`, `{{provider_intro}}`, `{{provider_greeting}}`, any `[...]` placeholder and similar).

Keep everything else exactly as written: weights, dates, doses, locations, medication names, pharmacy names, brand names, app and company names, every URL, punctuation and line breaks. This is judgment, not regex. Watch for a name folded into a quoted sentence, a nickname, a lowercase name, an unusual spelling, a name inside a signature or sign-off, and a name that appears in a patient message or in a provider's earlier message. A medication or brand that looks like a name (Wegovy, Zepbound, Ozempic) is not a name. A word like "Care Team" is not a name.

## Output
1. Overwrite `thread-blocks/{code}.md` with the anonymized text, same structure and headings, using one Write call.
2. Write every name you replaced, one per line, to `{scratch}/names/{code}.txt`. If you replaced none, write an empty file. NEVER write a replaced name anywhere in the round folder, the repo, or your return message.
3. Re-read the file you wrote and confirm no replaced name remains in it, in any spelling or case.

## Return
ONLY: the path of the anonymized file and the count of names replaced (a number, never a name).
````

## 10. Format checker template (copy to `briefs/3-format-checker.md`)

Fill the counts and paths. A fix round uses the same template and writes `qa-step3-format-round-<n>.md`. Section 4 covers what the orchestrator runs first and the output; this template is the single list of checks.

````markdown
# Step 3 format checker

You check {n_tickets} ticket drafts and {n_comments} comments before a product owner reviews them. You report; you never edit a draft. Do not launch subagents. Read every ticket, commit or file yourself.

Round folder: `{round}` (`<round>`). Skill folder: `{skill}` (`<skill>`). Repo root: `{repo}` (`<repo>`).

## Inputs
- `<round>/ticket-drafts.md`, section "## 4. Full ticket drafts" (the tickets with their Draft and thread sections; skim the thread blocks for names only, do not read them line by line). `<round>/ticket-comments.md`.
- `<skill>/references/ticket-spec.md`, `<skill>/references/rules-core.md`, `<round>/round.json`, `<round>/clinical-rules.md`, `<round>/ledger/*.md` and `<round>/ratings.md` (grep only), `<round>/dedup-qa-*.md` (the "Tickets read" tables), `<round>/ticket-plan.md` (titles, the Related-key lists, the section of open choices).
- `<round>/export/*.md`: grep by trace ID only (`Trace tr-<10 hex>`, about 40 lines after). Never load an export file whole. An `Earlier round:` bullet's trace is in the `export/*.md` of a folder in `round.json` `prior_rounds`.
- `<repo>/CLAUDE.md` section "Writing" and `<repo>/forbidden-writing-patterns.md`.

## Already run by script; do not redo
`check_tickets.py --tickets`, `--traces`, `--threads` and `--conflict` all pass on these files: title pattern, session-artifact regex, banned words, trace-ID form (an `Earlier round:` ID against the prior rounds' exports) and thread-section shape.

## Checks
1. **Names.** No real patient, provider, staff or family name outside a placeholder anywhere in the tickets (Draft and thread sections included) or the comments. Medication, pharmacy and street names are not personal names. Flag anything you are unsure about as a QUESTION.
2. **Title judgment.** The action types in each title match the evidence; each title is under about 110 characters; the title trace is one the Evidence bullets cite.
3. **Evidence accuracy (sample).** For each ticket, take the worst-instance trace plus one more. Grep it in `<round>/export/`. Confirm the quoted draft sentence is verbatim from the Provider draft (after `[redacted]` substitutions) and that any quoted reviewer note is verbatim. For each comment, do the same for one trace. List the traces you checked.
4. **Evidence form.** Provider edits use the Edit form. A bullet backed by an edit never uses the Rating form unless that handle also rated the trace (grep `ratings.md`). Thumbs-down evidence uses the Rating form. An earlier round's trace uses the `Earlier round:` form. No patient-message text is quoted in Evidence. Redaction covers patient names, ages, weights, BMI, labs, dates and locations inside quotes. Report each miss.
5. **Counts and labels.** Each ticket's Counts line, Evidence list and Eval check agree on the number of traces. A ticket with more than 8 counted traces lists 8 and an `Also:` line. The Labels line carries `round.json` `jira.labels` plus `safety` or `efficiency`, as in `ticket-plan.md`.
6. **Live Jira keys.** For every Jira key in any draft or comment (Related, Out of scope, comment targets): confirm the key resolves and that its current scope supports the characterization. For a key with a row in a `dedup-qa-*.md` "Tickets read" table, first read only its `updated` field with `mcp__claude_ai_Atlassian__getJiraIssue` (cloud ID from `round.json`). If `updated` predates that row's Read UTC and the draft's characterization stays inside the row's final-scope cell, use that cell. Otherwise read the key in full, one key per call. **For every comment target, read the ticket in full** (description, every comment, Development field) and check that every claim a comment makes about its text is accurate and every quoted phrase is verbatim. Check any comment the orchestrator rewrote after a live read hardest.
7. **Comment content.** A merge or deploy time a comment states matches `<round>/generation-provenance.md` (grep the commit). A `[T-n key]` marker is intentional; it is not a defect. Comments assign no one and ask no one to do a task that sits outside the ticket's own eval.
8. **Writing checklist, judgment rows.** The CLAUDE.md structural checks (lead with the answer, one idea per sentence, no paragraph over 4 sentences, no vague counts) and the manual rows of `forbidden-writing-patterns.md` (exactly-three lists and similar). Quoted reviewer and draft text is exempt. The comments are sendable copy: ownership sentences name the actor.
9. **Rulings.** No ticket or comment names a person as the source of a ruling, cites "Danny" or "the product owner", or states a dollar amount a ruling does not give. No ticket asks a draft to flag a provider decision while `round.json` `scope.conflict_flags_in_scope` is false.
10. **Placement.** Tickets cite session artifacts nowhere: no FM, T, C, D, ledger-row, CR or rule IDs in text a reader sees.
11. **Session-only evidence.** A session-only ticket (title ends `(session YYYY-MM-DD)`) has no trace. Every session bullet in its Evidence matches a statement dated that day in the feedback-session source files named in `round.json` `sources[]` (kind `interviews`; legacy rounds: `extra_sources`), and no participant is named. Skip this check when no ticket is session-only.

## Output
Write `<round>/qa-step3-format.md`: a Failures table with columns Type | Finding | Evidence | Recommendation (Type is DEFECT, QUESTION or ADDITION; write "No failures found" if clean), a PASS/FAIL count table by check, the list of traces you checked in check 3, and a "Jira keys verified" table with columns Key | Method | Result (Method is `full read` or `scope cell (<dedup-qa file>)`; every comment target is `full read`; one row per Jira key in the drafts and comments).

## Return
ONLY: the path, and the failure counts by Type.
````

## 11. Where each brief runs

| Role | Section | Output |
| --- | --- | --- |
| Ticket drafter (one per ticket) | 8 | `ticket-drafts-<code>.md` |
| Comment drafter | 8 | `ticket-comments.md` |
| Anonymizer (one per thread-blocks file) | 9 | `thread-blocks/<code>.md`, scratchpad `names/<code>.txt` |
| Format checker | 10 | `qa-step3-format.md` |
