# Rule-correction recheck brief (Step 2b)

`{code}` is a batch code from `round.json` `batches[].code`. Apply `rules-core.md` and never read another batch's files (SKILL.md hard constraint: one batch per agent).

Runs only for rows where the ledger rejects, narrows, or contradicts a reviewer's claim (an "overrule"). It always runs as its own agent. Never fold it into the second opinion's part B; this agent has read the Docebo source, and part B has not.

**Inputs:** `ledger/{code}.md` (the overrule rows only), `clinical-rules.md` (including section 14, the Docebo extraction), the round's `docebo-<date>.md`, `snippets.md`. The full copy stays in the round folder so this recheck, and any later reference, can read it without a live fetch.

**Task.** For each overrule row, read the rule's **source text** directly (the Docebo file or the sheet, never `clinical-rules.md`'s summary alone) and confirm or reverse the ledger's position. Overruling a reviewer can down-rank a real failure mode, so every overrule needs source text behind it, quoted with file and heading.

**Output:** `ledger/qa/{code}-rule-recheck.md`, a table (Row ID | Reviewer claim, short | Ledger position, short | Source text quoted, with file and heading | Verdict: Upheld/Reversed/Unsure | Edit made), and a Summary (rows checked, upheld, reversed, unsure).

**Returns:** path, overrules upheld and reversed.

**Stop conditions:** source file unreadable: stop and report.
