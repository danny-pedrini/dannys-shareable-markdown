# Adjudicator brief (Step 2b)

`{code}` is a batch code from `round.json` `batches[].code`. Apply `rules-core.md` and never read another batch's files (SKILL.md hard constraint: one batch per agent).

**Inputs:** `ledger/{code}.md`, `ledger/qa/{code}-blind.md`, `export/{code}.md`, `plan.md`, `clinical-rules.md`, `rules-core.md`, `ledger-schema.md`.

**Do not launch subagents.** Read every file yourself, and run any spot-check as a step of this task.

**Task.** Diff the ledger against the blind file, with `export/{code}.md` as ground truth:

1. Match each blind atomic issue to a ledger row (same trace, same Rating ref, same atomic issue). A blind issue with no match is a miss.
2. Add every miss to the ledger, noted `added in 2b`.
3. Split any ledger row that merges more than one atomic issue (one row per atomic issue, per `ledger-schema.md`), noted `corrected in 2b`.
4. Spot-check every rule or snippet citation in the ledger for scope (does the cited rule apply to this action type and trigger?). Fix an out-of-scope citation, noted `corrected in 2b`.
5. Where the blind file and ledger genuinely disagree on classification (draft-controlled vs. input-issue) and the disagreement is a real judgment call, leave the ledger as written but log it for the second opinion (`second-opinion.md`). Where one side is plainly wrong under `rules-core.md` (not a judgment call), fix it and note why.
6. Check redaction (`rules-core.md` section 6, Regime A) and the proof rule (`rules-core.md` section 5) on every row touched; fix silently if needed.
7. Check that Provenance and Evidence basis follow `ledger-schema.md` section 2a for each row's source kind, and that Classification holds `-` on rows with nothing wrong. Fix any row that breaks this, noted `corrected in 2b`.
8. Check that every `draft-controlled` row's Expected-behavior cell has an `Issue type:` phrase, placed as `ledger-schema.md` says. Add a missing one. Where two rows describe one behavior with different phrases, harmonize the wording.
9. When the batch has edits, check the blind file's `Not counted` table against the ledger, and add any missing row. A ledger `not counted:` row that really corrects a defect gets reclassified as a corrective row, and logged.
10. Compare held-topic tags (`rules-core.md` section 8, extraction rule 17) with the blind file, and add any tag the ledger lacks. A held-topic row the extractor resolved against a rule goes back to its plain classification, keeping the tag.

**Output:** `ledger/qa/{code}-adjudication.md`, a table (Blind ID(s) | Ledger Row ID(s) | What differed | Resolution | Edit made), a "Classification disagreements for second opinion" section (one entry per genuine judgment call, both sides' reasoning stated), and a Counts section (blind issues matched, differences found, rows added, rows corrected, rows reclassified, disagreements logged, redaction check result, proof-rule check result, held-topic tag check result, Classification values normalized).

**Returns:** path, rows added.

**Stop conditions:** blind file missing: retry the blind re-extractor once, then stop.
