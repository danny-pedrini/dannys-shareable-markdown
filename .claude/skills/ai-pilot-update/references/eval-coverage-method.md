# Eval-coverage method (Step 3)

Grade each theme against the eval judges as they exist in code, read first-hand this run. This step gets its own pass because it is where Round 1 went wrong twice: a verdict graded from a partial read, and a subagent's wrong claim about what judges see.

## 1. What to read, every run

All paths come from `feature.json` `evals`. Read on GitHub at `evals.ref`; record the commit SHA once (the directory listing returns it) and each file's blob SHA in `sources.md`. Never reuse a prior update's grading or `eval-coverage.md`, even when SHAs match.

1. **The run set.** Read `evals.run_set_source` (the launch brief) for the judges the Evals team runs. Then read `evals.catalog` and compare: a judge in the catalog but not the run set, or the reverse, goes to Gate 1. *Example (Round 1): no `writing_quality` judge existed in the catalog yet.*
2. **Every judge in the run set, whole.** List the judge's folder (`evals.judge_dir`). Read every file under `prompts/` (all phases) and every `.py` file that holds prompt text or pass/fail rules, including `models.py`, `spec.py` and `general.py`. *Example (Round 1): completeness's `prompts/v1.md` is an 11-line header; its rule is the `verdict` field description in `models.py`. Rx guideline adherence has two phases, `analyze_v1.md` and `adherence_v1.md`, framed for "a PRESCRIPTION APPROVAL message".*
3. **The adapter** (`evals.adapter`): what each judge receives (thread, chart snapshot, documents). Facts about judge inputs come from this file or from `evals.context_confirmed`, never from a subagent, reviewer or summary doc.
4. **The unit tests** (`evals.unit_tests`): which past cases they check. They catch only the cases they were written for.
5. **The overlays** (`evals.overlays`): rules added on top of a base judge for this feature's drafts. Read every overlay file whole, plus the spec that wires overlays to judges and to the pre-launch and weekly profiles, and grade each theme against the judge plus its overlay. *Example (Week 2): the first pass graded only the base judges, missed 12 files in `hdef/eval/overlays/` and `hdef/spec.yaml`, and five of six verdicts changed once they were read.*

Count the judges and overlays read first-hand and write both under the `eval-coverage.md` table ("10 of 10 judges, 12 of 12 overlay files"). Fewer than all is a stop: report which files failed to load.

Read every judge file whole yourself; never grade from extracts or cited ranges. If the judge files plus the other Step 2 reads won't fit in one context, stop before grading and ask Danny how to split the work.

## 2. How to grade a theme

For each theme in `themes-working.md`:

- Read the theme's failure-mode descriptions in each round's `failure-modes.md`.
- For each judge, find the passage that would fail a draft showing this failure, in the prompt or the output schema. Quote it verbatim in `Rule quoted`.
- `Yes`: a judge's rule fails the theme's failures as providers described them.
- `Partly`: a rule fails some of the theme's failures, or only on some action types. Say which part it misses. Check framing too: a judge written for one action type (for example, prescription approval) only partly covers drafts of another.
- `Gap`: no run-set judge's rule fails it. If unit tests cover specific past cases, the doc says "Gap (unit tests only)".
- Note judges that push the other way (a rule that rewards the failure), with the quote. *Example (Round 1): semantic coverage treats added content as "never a semantic-coverage failure", which works against cutting length.*
- Name the judge or judges behind every `Yes` and `Partly`, as the doc will write them.

## 3. Connect every gap to a fix

- Every `Gap` gets a row in the doc's eval-changes table. Write the row's exact label in `Fix row`.
- A `Partly` gets a row or `none: <reason>`; the doc states the reason.
- The eval owner (`evals.owner`) is named once, with a mailto link, in the paragraph above the eval-changes table.
- Never write that the changes "close each gap" unless every gap has a row.

## 4. What reviewers may and may not change

A reviewer or grader claim about what a judge checks or sees is adopted only when a file read this run confirms it. Open the file, quote the passage, then fix. A claim with no confirming passage goes to Danny as a question, never into the doc.

## 5. Gate 1 presentation

Show Danny every verdict that changed from the prior update, and every verdict whose judge files changed SHA since the prior update. For the first update of a feature, show every verdict.
