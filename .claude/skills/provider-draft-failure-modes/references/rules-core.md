# Core rules

Every extractor, blind re-extractor, adjudicator, second-opinion, rule-recheck, dedup and QA agent applies these exactly as written. The orchestrator routes this file to every judgment agent (see SKILL.md `<input_routing>`). Do not retype these rules into `plan.md` or any brief; point to this file by name.

## 1. The input-issue rule

Never file a bug for a problem the draft does not control. An **input issue** is a defect that would remain even if the model had written a perfect message from the inputs it was given.

**Examples of inputs (not draft-controlled):**
- **The provider's decision:** the action type (refer vs. hold vs. increase), whether to act now, or the referral decision itself.
- **Action details the provider or EMR supplied:** the medication, dose, strength, supply length, pharmacy, or any value the EMR fills into a placeholder.
- **Chart, intake or catalog data that is missing or wrong at the source:** a medication list entered wrong, a price or product the catalog doesn't carry, or a fact no field records. Stale or conflicting chart facts are not on this list (see "Chart facts the model saw" below).
- **Deterministic text the model doesn't write:** a platform-injected snippet block, and EMR-injected greetings or sign-offs.
- **Eval artifacts:** mislabeled mined actions, and what the labeling tool displayed.

**A draft-controlled failure** is anything the model wrote or left out:
- wording and tone
- a fact asserted beyond the inputs
- misreading or misstating a correct input
- missing required content
- not answering the patient
- relying on a chart fact the rest of the context shows is out of date or contradicted

**Test to apply:** "If the model had written a perfect message from the inputs shown, would this defect remain?" Yes → input issue. No → draft-controlled.

**Chart facts the model saw.** A perfect message reads the chart, the intake and the thread together. Relying on a fact the rest of that context makes wrong is draft-controlled, even when the fact came from the chart:
- **A stale fact.** The dates in context show it no longer holds. Examples: a compounded medication whose last shipment is past its shelf life, a weight logged months ago, or an old questionnaire answer given as the current reason.
- **A conflict.** Two chart fields disagree, or the chart and the thread do. Examples: a recorded highest weight that doesn't fit a recorded gastric bypass, or a status the thread shows already resolved.
- **A question that ignores the conflict.** The draft asks the patient to confirm the doubtful value instead of asking the question that resolves it.

The expected behavior is to notice and act: account for the time gap, or ask the question that resolves the conflict. A chart value is an input issue only when it is wrong at the source and nothing else in the context shows it. The export does not show the chart, so never assume the model lacked a fact a reviewer says the chart holds. When the model may not have received that fact, the row stays draft-controlled and the ticket's Layer line reads "chart or context input" (`ticket-spec.md`).

**Mixed cases.** File only the draft-controlled part. Example (Round 3): the EMR supplied the wrong dose, but the draft also invented a reason for the dose. File the invented reason, not the dose. Write two ledger rows, one of each classification, from one reviewer comment when it holds two issues.

**Name the input.** Whenever a row is classified `input-issue`, or the classifier is unsure, name:
1. the specific input believed wrong (the field, value or decision),
2. who owns it: one of the four owners below,
3. one sentence on what the draft would have written given the correct input.

Never leave an `input-issue` row without this. `build_cluster.py` fails the round if any does.

**Input-issue owners** (`cluster_defs.INPUT_OWNERS` keys; every entry must land in exactly one):
- Provider decision (for Clinical Quality)
- EMR (action details, fields, workflow)
- Chart or catalog data
- Eval dataset or tool

Every input issue goes to `input-issues.md`, grouped by owner. Never drop one, even when it duplicates another row's input. Danny reviews that list with Clinical Quality; it is not a ticket list.

Classify a row as an input issue only when a provider, an eval judge or a Slack report raises it. A provider source is a comment, an edit or a labeling reason. Do not search a draft for input issues no source raised.

## 2. The platform-text rule (who authors what)

Only text the model actually produced is eligible to be draft-controlled.

1. **What the model wrote.** The draft block in `export/<code>.md` is the model's output. Everything in it is draft-controlled, including a sentence the prompt tells the model to reproduce verbatim. The fix for that is a prompt edit, not a dismissal. The only text that is an input, not draft-controlled, is text the platform adds outside the model's output: greeting and patient-name tokens filled after generation, a deterministic snippet block the model does not write, and an EMR's own greeting or sign-off. If a reviewer quotes text that is not in the draft block, classify it `input-issue` (owner: EMR, deterministic text) and say the quote was not found in the draft.
2. **An "Explanation" or reasoning block the model emits is not patient-facing.** Use it only to see what the model believed about its inputs (for example, that it misread a dose). Never log a defect against the explanation itself.
3. **The action-detail line (medication, dose, action type) is the input the provider or EMR supplied.** A draft that misstates or mishandles a correct action-detail value is draft-controlled. A wrong value in the line itself is an input (owner: provider decision, or EMR).

## 3. The placeholder rule

A leftover `[INSERT ...]` or similar token is classified by **who the generating prompt tells to author its content**:
- If the prompt tells the model to write the content itself, a leftover token is draft-controlled, and the rubric's harm-if-sent test applies to it (see `priority-rubric.md`).
- If the prompt tells the model to leave the token for the provider or EMR to fill, a leftover token is an input issue (owner: chart or catalog data), logged, not filed.

Within that, check scope before naming the input: the token is draft-controlled when a protocol or thread row supported the missing content, and an input issue when no protocol row covers the case (Round 3 example: QCARE-62 recorded that the interim-guidance table had no row for several real cases, so some leftover tokens were a catalog-data gap, not a drafting defect). Name which applies in the row.

## 4. The missed-conflict-flag rule

A provider's decision conflicts with a protocol, and the draft does not flag it.

**Step 1 always runs, regardless of scope.** Read the generating prompts at the generating commit (GitHub) and record, per prompt file, whether it instructs the model to flag a provider-decision-versus-protocol conflict. This check decides draft-controlled vs. input issue, and it runs every round no matter what `round.json` `scope.conflict_flags_in_scope` says:
- If the prompts instruct flagging, a missed flag is **draft-controlled**.
- If they don't, a missed flag is an **input issue** (the decision itself is always an input; log the conflict).

Record the basis in the ledger's Conflict-flag basis column: `prompt instructs flagging (<file>:<lines> @ <commit>)` or `prompt does not instruct flagging (<files read> @ <commit>)`.

**Step 2, the scope switch, only applies after step 1 calls a row draft-controlled.** `round.json` `scope.conflict_flags_in_scope`:
- `true`: file the draft-controlled missed flag as a ticket.
- `false` (the default; Danny ruled flagging out of scope on 2026-10-21): log it in `input-issues.md` with the conflict noted. Do not file it.

Never ask a draft to flag a provider decision while the scope is off: not in a ticket's expected behavior, not in a comment, not in a prompt-edit recommendation. `check_tickets.py --conflict` and E21 enforce this at the ticket level.

## 5. The proof rule

A row is evidence only when a provider backs it or a failed eval judge does. Provider evidence is a comment, an edit, a labeling reason or a Slack report. A BAD verdict with no recorded reason is ignored. It is not filed and it is not evidence.

**Evidence is not the same as a counted instance.** Which rows count toward the filing floor and the frequency band is the allow-list in `priority-rubric.md` section 2. Phrase-scan identical text counts only once a counted source shows the text is a defect.

**Eval failures get a provider comment's checks.** Classify each one `draft-controlled` or `input-issue` under section 1. When a ruling, a clinical answer, or the draft and thread themselves contradict the judge, set the row aside the same way as a contradicted reviewer rule (`extraction/extractor.md`, extraction rules 6, 7 and 16).

**Provenance tags**, one per observation: `reviewer-stated`, `reviewer-edit-on-good` (a thumbs-up that still asked for a change), `thumbs-only` (a rating with no text; it satisfies the coverage check and is never evidence on its own), `provider-edit` (a change only the provider's edit shows), `eval-judge` (a failed judge verdict), `input-issue`, `slack`. A round from before v3.0 may also carry `inferred`. Scripts read that tag as not counted and never rewrite the row.

**Ambiguous tags.** Any error tag whose reason text can plausibly point at an input rather than the draft's own wording must get a second opinion. Never classify a row by the tag name alone. Round 3 examples: `expected_flag_for` and `dosage_medication_mismatch` (a reviewer's reason can blame a provider's prescription update rather than the draft). Treat any new tag the same way if its reason text names a provider decision, an EMR field, or chart data as the suspected cause. Check `ratings.md` for new tags each round; the error-tag taxonomy in `ledger-schema.md` is "as of the last round," not fixed.

## 6. PHI and names: two regimes

**Regime A: ledgers and every other repo working file** (`ledger/*.md`, `export/*.md`, `plan.md`, `clinical-rules.md`, `failure-modes.md`, `input-issues.md`, `dedup/*.md`, `dedup-verdicts.md`, and all QA files). Redact in quotes: replace patient names, ages, weights, lab values, dates and locations with `[redacted]`. Never copy patient-message text; if a quote contains it, replace that span with `[patient text omitted]`, or paraphrase in one generic clause with no identifiers. Medication names, doses, units, pharmacy names (for example GiftHealth) and reviewer handles are not PHI and stay as written.

**Regime B: thread blocks and ticket "Draft and thread" sections** (`thread-blocks/<code>.md` and the Draft-and-thread section of every filed ticket body). These carry the **full draft and the full prior messages**, for every trace in the ticket's evidence list, with names anonymized only: patient, provider, staff and family names become placeholders. Weights, dates, doses and every other detail stay as written. This is Danny's standing instruction (memory `provider-draft-tickets-include-thread`, 2026-10-21) and it **supersedes** the Regime A "never copy patient-message text" rule for exactly these two file types. Run the anonymization pass as judgment, not regex, and keep each ticket body under Jira's 32,000-character limit.

**State both regimes plainly whenever PHI handling comes up.** Do not imply one blanket redaction rule covers the whole round.

The list of replaced names (`names/<code>.txt`, or an older `names-replaced.txt`) lives in the session scratchpad only. It never goes into the round folder, a commit, or any file this skill writes to the repo (`round-folder-layout.md` section 2).

## 7. Other ground rules

- **Tickets and comments are read outside this session.** Cite the ratings sheet, trace IDs and openable source links. Never cite ledger row IDs, failure-mode numbers, rule IDs (`CR-*`), decision-item IDs, or Danny himself. State a ruling as a plain fact ("the GiftHealth paragraph applies to a new prescription only"), not as "per Danny's ruling."
- **Subagents return paths and counts, not content.** They write large files in chunks: one Write call, then Edits or appends, because a single huge write fails at the output-token limit.
- **Parallel agents touching one file use targeted Edits only.** Never let two agents each rewrite the same file whole.
- **MCP no-inference stop rule.** If a live source read fails (auth error, not found, empty result, timeout, or any partial failure), stop immediately. Do not infer, reconstruct, or summarize the missing source from a reviewer's quote, a prior round's file, or "probably about X" reasoning. Report the server, tool, resource ID and error, and ask for a fix, a paste, or an export.
- **Never reconstruct a draft from a reviewer's quote.** If the export is missing or incomplete for a trace, the row goes to `export-gaps.md`, not the ledger.
- **Danny's ruling memories override older docs.** In this order of recency where they conflict: `galen-exemplar-beat-rulings-v4`, `galen-patient-facing-language-rules`, `galen-no-repeated-lines-in-exemplars`. Do not flag a ruling these memories make situational as a missing beat (example: Increase drafts do not need to state the minimum time on dose).
- **The Docebo row wins a conflict on clinical content.** When two rows in `clinical-rules.md` conflict, the Docebo row wins over a row from a template, a PRD, an exemplar, or another doc. The winning row is a section 14 row, or a row in the newest Docebo delta when the round has one. Cite that row. Never cite a row whose Status contains `superseded by` as expected behavior or as a contradiction. Danny's ruling memories keep their current precedence over older docs. [Assumption: rulings still sit above Docebo (needs validation)] E39 checks that a ledger does not cite a superseded row.
- **Assign nothing to anyone in Jira.** Leave the assignee field empty on every filed ticket and comment, regardless of who is named in a decision item or a flag-for-Danny note.
- **Route new AI Eng questions to the person named in `round.json` or `STATUS.md` Gotchas** ([AI Eng lead] as of 2026-10-21; [AI engineer] left the team 2026-10-16 and gets nothing new assigned or asked).

## 8. Extraction rules 13, 14, 15 and 17

The extractor and the blind re-extractor both apply these. They keep their extraction-rule numbers, so a reference to "extraction rule 17" means the rule below.

**Rule 13. Edits: what a corrective change is.** A wrong fact, a wrong clinical call, a missed patient question or fact, a re-ask, or a section the case did not need. Read a heavy rewrite at content level, not word level. Add a row for every claim the provider's note makes that the edit doesn't show.

**Rule 14. Edits: changes that fix nothing still get a row.** This covers a sign-off, an intro the note doesn't ask to change, and counseling the provider added without fixing a draft defect. Each gets a `not counted:` row (`ledger-schema.md` section 1, Atomic issue). Never drop one silently.

**Rule 15. Edits: correcting a supplied value is an input issue.** An edit that corrects an EMR-supplied or chart value is an input issue when the value is wrong at the source and nothing in the context shows it; name the input. An edit that corrects a stale or contradicted chart fact is draft-controlled (section 1, "Chart facts the model saw"). If the draft could still have handled the case better, write a second row for the draft-controlled part.

**Rule 17. Held topics.** When `plan.md` holds a topic for the product owner, start the Atomic issue of every row touching it with `[<topic>]` (Round 1 edits pass example: `[price]`). Record the row fully and classify it on its merits. Never resolve it against a rule; Gate 2 shows it to the product owner.
