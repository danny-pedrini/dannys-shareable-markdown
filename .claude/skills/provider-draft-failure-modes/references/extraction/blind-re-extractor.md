# Blind re-extractor brief (Step 2b)

`{code}` is a batch code from `round.json` `batches[].code`. Apply `rules-core.md` and never read another batch's files (SKILL.md hard constraint: one batch per agent).

**Inputs:** `export/{code}.md`, the `ratings.md` rows for `{code}`, the batch's Slack `file` if any, and `rules-core.md`, including its section 8 (extraction rules 13, 14, 15 and 17). **Does not see** `ledger/{code}.md`, `plan.md`, `clinical-rules.md` or the extractor's brief. This keeps it blind to the extractor's conclusions and to clinical-rule citations, so it catches raw reviewer issues independently. When `plan.md` holds a topic, the orchestrator names it in this brief, and the agent tags it as extraction rule 17 says.

**Task.** Re-extract every provider and eval issue in the batch, using only the export and the input-issue rule (`rules-core.md` section 1). That covers reviewer-stated and reviewer-edit-on-good issues from the rating rows, every corrective change between a draft and the message the provider sent, every failed judge verdict and every Slack report. Extraction rules 13, 14 and 15 define a corrective change. Classify each as `draft-controlled` or `input-issue`, naming the input when unsure, in the same style as `ledger-schema.md`'s columns (Trace ID, Rating ref, Provenance, Verbatim reviewer quote, Offending draft sentence, Atomic issue, Classification, Input named). Add a Source column: `rating`, `edit`, `note`, `edit and note`, `eval` or `slack`.

**Output:** `ledger/qa/{code}-blind.md`, one row per atomic issue found. When the batch has edits, add a second table, `Not counted` (`Trace ID | Type (sign-off, intro, added counseling) | One clause`). End with a one-line count of rating rows with text, edited drafts, failed verdicts and atomic issues extracted.

**Returns:** path, issue count.

**Stop conditions:** export file missing or unreadable: stop and report.
