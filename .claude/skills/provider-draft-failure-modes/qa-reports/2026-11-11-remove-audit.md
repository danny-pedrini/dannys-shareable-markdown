# QA: remove the draft audit (v3.0)

No defects. One addition, held for Danny.

Checked against `Project-Galen/Phase-3/Discovery/Provider-Pilot-Week-2/PLAN-remove-audit.md` and the six answers in the Version history row. Local files only. The grader did not edit anything.

## Defects

None.

## Addition

`.claude/skills/ai-pilot-update/scripts/theme_counts.py` still writes an Audit-only drafts column. Left unchanged. This change-set does not cover that skill.

## Checks

1. Pass. New-round instructions no longer tell an extractor to audit every draft, write Evidence basis `inferred`, write Reviewer `audit`, or run CHECK 3. See `references/extraction/extractor.md` and `references/ledger-schema.md`.
2. Pass. `scripts/counting.py` still treats a legacy `inferred` row as not counted. `scripts/ledger_tool.py` aliases the old rubric phrase and does not rewrite the ledger.
3. Pass. CHECK 6 to 9 still match E2. Coverage rules in `references/ledger-schema.md` are 1 to 6.
4. Pass. An input issue is classified only when a provider, an eval judge, or Slack raises it (`references/rules-core.md` section 1, extractor Task 2).
5. Pass. Extractors skip the verbatim Docebo section. The rule recheck reads it (`SKILL.md` input routing, `references/extraction/rule-recheck.md`).
6. Pass. E38 fails a v3.0 round that writes those checklist values, and Week 2 stays not measurable (`scripts/run_evals.py`).
7. Pass. Removing the unused `traces` assignment is dead-code cleanup. Checks 1, 2, and 4 to 9 do not use it.
8. Pass. A severe-safety failure mode with zero counted instances goes to the product owner when the round has not already stored a call (`scripts/build_cluster.py` `filing_call`).

> **Source:** QA pass 2026-11-11, local read of the skill files named above.
