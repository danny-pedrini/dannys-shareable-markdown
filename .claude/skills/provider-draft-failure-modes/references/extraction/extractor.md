# Extractor brief (Step 2a)

`{code}` is a batch code from `round.json` `batches[].code`. Apply `rules-core.md` and never read another batch's files (SKILL.md hard constraint: one batch per agent).

**Inputs:** `export/{code}.md` (with its sent messages and judge verdicts when the round has edits or evals sources), the `ratings.md` rows for `{code}`, `round.json` `sources[]`, the `file` of any `interviews` or `slack` source whose rows go in this batch, `plan.md`, `clinical-rules.md` (every section), `snippets.md`, `generation-provenance.md` (for the conflict-flag check), `rules-core.md`, `ledger-schema.md`. Do not open a `docebo-*.md` full copy. That copy stays in the round folder for later reference. The rule recheck reads it. Read the Docebo delta only when rule 11 applies.

**Task.** Work in this order:

1. Write rows for every piece of provider and eval evidence in the batch, per `ledger-schema.md` and its section 2a conventions for each source kind. That means every rating row, every corrective change between a draft and the message the provider sent, every failed judge verdict and every Slack report. Eval verdicts need no separate brief: this task and rule 16 cover them.
2. Classify each issue `draft-controlled` or `input-issue` under `rules-core.md` section 1. Name the input and the correct-input rewrite whenever unsure. Classify an input issue only when a provider, an eval judge or a Slack report raises it. Do not search a draft for input issues no source raised.

**Extraction rules** (generalized from Round 3's extractor brief; apply every round):

1. **What the model wrote.** Apply `rules-core.md` section 2 item 1. If a reviewer quotes text not present in the draft block, classify it `input-issue` (owner: EMR, deterministic text) and say the quote was not found in the draft.
2. **The explanation or reasoning block is not patient-facing.** `rules-core.md` section 2 item 2. Never log a defect in it directly; use it to understand what the model believed about its inputs.
3. **The action-detail line is the input.** `rules-core.md` section 2 item 3.
4. **Missed conflict flags.** Apply `rules-core.md` section 4 in full: read the generating prompts, record the Conflict-flag basis for every row that raises this question, and classify per the two-step rule regardless of whether this round files conflict-flag tickets.
5. **Placeholders.** Apply `rules-core.md` section 3. Check `existing-tickets.md` for a standing catalog-gap ticket before calling a leftover token input-issue on scope grounds.
6. **Danny's rulings.** If a reviewer asks for something a ruling memory or a `CR-R<n>` entry in `clinical-rules.md` makes situational or contradicts, still write the row. Classify it on its merits, and start its Expected-behavior cell with `contradicted by CR-R<n>:` (or the ruling memory's name). Clustering maps these to "not a failure mode" and shows Danny; it never drops them silently.
7. **Clinical answers.** Same handling when a reviewer's rule conflicts with a clinical answer in `clinical-rules.md`. Start the Expected-behavior cell with `contradicted by CR-<id>:` and quote the winning rule (`rules-core.md` section 7). Never cite a superseded row as expected behavior or as a contradiction. E39 checks this.
8. **Comments about many messages.** When a reviewer complains about repetition across messages ("this sign-off on every message"), write the row on the trace where it was said, and quote the repeated phrase exactly. The cross-type phrase scan (an orchestrator action) measures how far it spreads; do not try to check other batches yourself.
9. **Redaction in draft quotes.** Apply `rules-core.md` section 6, Regime A, to every quote in the ledger. Never copy text from the "messages before the draft" block; paraphrase in one generic clause instead.
10. **Chart not visible.** A reviewer statement about the chart counts as evidence under the proof rule even when the export doesn't show the chart field. A chart the export doesn't show never makes a row an input issue by itself. Apply `rules-core.md` section 1, "Chart facts the model saw."
11. **Guideline changes.** Check the round's Docebo-delta file (`round.json` points to it, or it is named in `plan.md`) for any clinical-guideline change since the prior round's generation bound. Tag a row `possible guideline change after generation` only if it depends on a rule that changed in that window.
12. **Large files.** Write the ledger in chunks: one Write call for the header and the first rows, then Edits or heredoc appends with a unique delimiter. Never leave a blank line inside the table, because it silently drops the rows after it. Return only the file path and counts.

Rules 13, 14, 15 and 17 are in `rules-core.md` section 8, because the blind re-extractor applies them too. Apply them here as well.

16. **Evals: a judge verdict is a claim to check.** Check it against the draft and visible thread like a reviewer comment. When they contradict the judge, still write the row, and start its Expected-behavior cell with `contradicted by the draft:` and one clause. Never write a row for a passing verdict.

**Output:** `ledger/{code}.md`.

**Returns:** path, row count by provenance and by Evidence basis, draft count, and counts of `input-issue`, `not counted:` and held-topic rows.

**Stop conditions:** a trace any source names has no export record: write it to `export-gaps.md`, do not guess. A record with a note but no generated draft gets a row from the note that says no draft was generated. A source read fails: stop per `rules-core.md` section 7 (MCP no-inference).
