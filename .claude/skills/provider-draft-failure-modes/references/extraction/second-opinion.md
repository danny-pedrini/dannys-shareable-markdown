# Input-issue second opinion brief (Step 2b)

`{code}` is a batch code from `round.json` `batches[].code`. Never read another batch's files (SKILL.md hard constraint: one batch per agent).

Runs on every row marked `input-issue`, and every row carrying an ambiguous tag (`rules-core.md` section 5). The orchestrator builds the target list with `make_second_opinion_input.py {code}`, which strips the extractor's own classification before handing it to this agent.

**Inputs:** `ledger/qa/{code}-second-opinion-targets.md`, `export/{code}.md`, `rules-core.md` (sections 1–3 only: the input-issue rule, the platform-text rule, the placeholder rule). **Does not see** `ledger/{code}.md`, the extractor's classification or the extractor's brief.

**Task, part A: classify.** For each target row, independently classify `draft-controlled`, `input-issue`, or `mixed`, from the export and `rules-core.md` alone. Name the input and owner when the call is `input-issue`, and give one sentence of reasoning and a confidence (`high`/`medium`/`low`).

**Output A:** `ledger/qa/{code}-input-second-opinion.md`, a table (Row ID | Your classification | Input named and owner | One-sentence reason | Confidence), and Counts (draft-controlled, input-issue, mixed, total).

**Task, part B: recommend, after the diff exists.** The orchestrator runs `compare_second_opinion.py {code}` against this output and the ledger, which writes the raw disagreement table to `ledger/qa/{code}-second-opinion-diff.md` (columns: Row ID, Trace, Atomic issue, Ledger says, Ledger input named, Second opinion says, Second-opinion input named, Second-opinion reason, Confidence). In the same turn part A returns, the orchestrator sends that file's path back to this same agent as a message. If this agent has already finished, the orchestrator spawns a fresh Recommend agent (or uses the adjudicator) with part B of this brief, as before. Part B never goes to the rule-recheck agent. The script ends every disagreement row with a `Recommendation` cell reading `Recommendation: TBD`. Edit that cell in place, replacing `TBD`, so the cell reads:

```
Recommendation: <ledger|second opinion> (<one line why>)
```

This is the exact format `round-folder-layout.md` section 4 and eval E3 require. Do not skip a disagreement row, and do not recommend a side without a one-line reason tied to `rules-core.md`.

**Returns:** path, disagreement count (part A); path, rows recommended (part B).

**Stop conditions:** targets file missing: retry once, then stop.
