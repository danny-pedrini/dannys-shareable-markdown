# Ledger schema

One markdown table per batch, at `ledger/<code>.md`, where `<code>` is a batch code from `round.json` `batches[].code`. One row per atomic issue: a comment holding two issues becomes two rows. Pipe characters inside quoted text become `/`.

## 1. Columns

| Column | Values |
| --- | --- |
| Row ID | `<batch code>-<nnn>`. Working reference only; never cited outside this session (`rules-core.md` section 7). |
| Trace ID | Full ID as it appears in `export/<code>.md` (and in `ratings.md` when rated). A feedback-session batch (an `interviews` source in `round.json` `sources[]`; legacy `extra_sources`) has no trace: it holds `session-<YYYY-MM-DD>` (add `-am` or `-pm` when two sessions share a date). Session rows follow section 2a. Scripts count only IDs that start `tr-` as drafts. |
| Action type | From the export, matches a `round.json` `batches[].action` value |
| Provenance | `reviewer-stated`, `reviewer-edit-on-good`, `thumbs-only`, `provider-edit` (a change only the provider's edit shows), `eval-judge` (a failed judge verdict), `input-issue`, `slack` (`rules-core.md` section 5). A row classified as an input issue carries `input-issue` here. A round from before v3.0 may also carry `inferred` (section 2b). |
| Evidence basis | What proves the issue: `reviewer-stated`, `reviewer-edit-on-good`, `provider-edit`, `provider-edit+note` (an edit the provider's note explains), `eval-judge`, or `slack`. Keeps the proof rule checkable on `input-issue` rows. Blank for `thumbs-only`. Counting reads this column, against the allow-list in `priority-rubric.md` section 2. A legacy row may still hold `inferred`. Scripts read it as not counted. |
| Reviewer | A person's handle from `round.json` `reviewers[]`, or a session handle on an interview row (section 2a). `reviewers[]` lists every provider handle any source names: the rater, the provider who sent an edited message, or the provider who reported on Slack. `eval` for an eval row. A legacy row may still hold `audit` (section 2b). |
| Verdict | `GOOD`, `BAD`, `FAIL` (eval rows), or `n/a` (Slack rows, and edit rows on a trace with no rating). A legacy `audit` row may also hold `n/a`. |
| Rating ref | `<handle> · <YYYY-MM-DD HH:MM>` exactly as in `ratings.md`. Append ` · dup` if `ratings.md` marks it an earlier duplicate. Blank for eval, Slack and diff-only edit rows, and for a legacy `audit` row. |
| Error tag | Reviewer tag verbatim. Eval rows use `judge:<judge name>`, so no counter treats a judge as a reviewer. Thumbs-only, Slack and diff-only edit rows use `none`. A legacy row may still carry an `inferred:` tag (section 2b). |
| Verbatim reviewer quote | Exact text from the tag reason or note, an eval row's judge reason, or a Slack report's text, redacted per `rules-core.md` section 6, Regime A. Blank for thumbs-only and diff-only edit rows, and for a legacy `inferred` row. |
| Offending draft sentence | The draft sentence at fault, redacted per the same regime. `(omission)` for omissions. |
| Atomic issue | One sentence: what went wrong. An edit row says what the provider changed. Thumbs-only rows: `thumbs only, no issue stated`. An edit that fixes no draft defect (a sign-off, an intro the note doesn't ask to change, or counseling the provider added): `no defect; not counted: <sign-off \| intro \| added counseling>: <one clause>`. A legacy row may still read `audited, no issue found` (section 2b). |
| Classification | `draft-controlled` or `input-issue` (`rules-core.md` section 1). A mixed comment becomes two rows, one of each. `-` on a row with nothing wrong. Legacy ledgers also hold `n/a`, an em dash or a blank there. |
| Input named | Required when Classification is `input-issue`, and for any row where the classifier was unsure. Name the input believed wrong, its owner (one of the four in `rules-core.md` section 1), and one sentence on what the draft would have written given the correct input. Blank only for draft-controlled rows with no doubt. |
| Conflict-flag basis | Only for missed-conflict-flag rows: `prompt instructs flagging (<file>:<lines> @ <commit>)` or `prompt does not instruct flagging (<files read> @ <commit>)` (`rules-core.md` section 4). |
| Expected behavior + guidance source | On every `draft-controlled` row, write `Issue type: "<imperative phrase, as a ticket title would read>".` first, after any `contradicted by ...:` clause. Clustering groups rows by fix location and behavior, not by this wording. Then one sentence of expected behavior, then the source: a rule ID from `clinical-rules.md`, `reviewer rule: <handle> on <trace prefix>`, an approved-snippet citation with its scope, or `uncodified, needs clinical confirmation`. State the scope the guidance applies in (action type and trigger); see the scope-of-guidance check in `clustering-and-dedup.md`. |
| Confidence | Diff-only edit rows (Evidence basis `provider-edit`): `high` (the sent message plainly states the corrected fact or drops the sentence), `medium` (the change could be preference, or depends on the thread or chart), `low` (plausible concern). Only `high` diff-only rows count. Blank on other rows. |
| Export ref | The entry number in `export/<code>.md` |

## 2. Coverage rules

Every ledger file must satisfy each rule that applies to its round's sources before Step 2b's mechanical check passes:

1. Every one of the batch's rating rows maps to at least one ledger row through Trace ID plus Rating ref, including repeats.
2. A rating with any reason or note gets at least one `reviewer-stated` or `reviewer-edit-on-good` row (or an `input-issue` row whose Evidence basis is one of those or `provider-edit+note`). A tag with no reason becomes a row whose Atomic issue is `tag only: <tag>; reason not stated`.
3. Every `input-issue` row has Input named filled.
4. **Edits.** Every draft with a recorded sent message that differs from it at content level (platform tokens aside) gets at least one row with Evidence basis `provider-edit` or `provider-edit+note`, `not counted:` rows included.
5. **Evals.** Every failed judge verdict maps to at least one row on its trace with Error tag `judge:<judge name>`.
6. **Slack.** Every saved report that names a trace maps to at least one `slack` row on that trace.

Interview sessions have no per-statement coverage rule. `mechanical_check.py` enforces these rules against `ratings.md`, the export and the batch ledgers. A FAIL loops back to that batch's extractor or adjudicator with the failing rows named (max 2 respawns, per the QA loop protocol in SKILL.md).

### 2a. Row conventions by source kind

- **Ratings** (`thumbs-downs`, `labeling`): the columns as defined above.
- **Edits.** Diff each draft against the message the provider sent at content level: facts, clinical calls, questions asked or answered, and sections. Write one row per atomic corrective change.
  - A change the provider's note explains: Provenance `reviewer-stated`, Evidence basis `provider-edit+note`, the rating's handle in Reviewer, the Rating ref and the quote.
  - A change only the diff shows: Provenance and Evidence basis `provider-edit`, a blank Rating ref, and a Confidence. Reviewer is the sending provider, or the trace's rater when the source's `sender_column` is null. With neither, Reviewer is `unresolved`, and Gate 2 lists the row like an unmatched session handle. Every `unresolved` reviewer counts as one provider, however many rows carry it (v2.4); `sender_n` and `provider_n` handles count as written. An unmatched interview session handle (the Interviews bullet below) is a different case and stays its own provider.
  - A note with no matching edit, or a trace with no sent message: Provenance and Evidence basis `reviewer-stated`.
- **Evals.** One row per failed judge verdict, with Provenance and Evidence basis `eval-judge`, Reviewer `eval`, Verdict `FAIL`, Error tag `judge:<judge name>` and the judge's reason as the quote. A passing verdict gets no row. The row gets the same classification and contradiction checks as a provider comment (`rules-core.md` section 5).
- **Interviews.** Provenance `reviewer-stated`, no Rating ref, and Action type `feedback_session`. Reviewer is the rater's handle when the speaker is a rater; otherwise it's a stable session handle. Session handles are stable across a round's interviews sources, and any source's `providers` map resolves them. A handle mapped to `null` is its own provider, and a handle no map holds is unresolved. In a round with no map (legacy), each handle is its own provider. Gate 2 lists unresolved handles, and each counts as a distinct provider until the product owner matches it.
- **Slack.** Provenance and Evidence basis `slack`, the reporting provider in Reviewer, and the trace the report names.
- **Input issues** of any kind carry Provenance `input-issue` and keep the proof in Evidence basis.

### 2b. Legacy values

Read these as written; never rewrite a legacy ledger.

- **Provider Pilot Round 1 edits pass (2026-11-05).** Diff-only rows carry Provenance `inferred`, Evidence basis `provider-edit` and Reviewer `audit`. They count at Confidence `high` only, credited to the trace's rater. Its `provider-edit+note` rows (71) and `note` rows (10, a note with no matching edit) count as provider evidence. Its input-issue rows kept Provenance `reviewer-stated` or `inferred`.
- **Provider Pilot Round 1 (2026-11-03).** `inferred` rows with a blank Evidence basis are the old checklist findings.
- **Rounds before v3.0.** They carry `inferred` and `audit` rows. Scripts read those rows as not counted and never rewrite them.

## 3. Error-tag taxonomy

The labeling tool's tags as of Round 3: `clinical_inaccuracy`, `ignored_patient_context`, `incomplete_guidance`, `lack_of_verbiage_clarity`, `missing_compliance_content`, `other`, `dosage_medication_mismatch`, `template_personalization_error`, `inappropriate_tone`.

This list is not fixed. Check `ratings.md` each round for tags not in this list and add them here with the round they first appeared. Any tag whose reason text can point at an input, not only the draft's wording, is an ambiguous tag under `rules-core.md` section 5 and needs a second opinion regardless of whether it is on this list.
