# Extraction briefs

Index of the Step 2a and 2b briefs, for the orchestrator. Each role has its own file under `references/extraction/`, and each brief is routed alone, so the blind re-extractor and second opinion never see the extractor's rules. `{code}` is a batch code from `round.json` `batches[].code`. Every agent below applies `rules-core.md` and never sees another batch's files (SKILL.md hard constraint: one batch per agent). Rules shared by more than one role live in `rules-core.md`, never in two brief files.

| Role | Step | Brief |
| --- | --- | --- |
| Extractor | 2a | `extraction/extractor.md` |
| Blind re-extractor | 2b | `extraction/blind-re-extractor.md` |
| Adjudicator | 2b | `extraction/adjudicator.md` |
| Rule-correction recheck | 2b | `extraction/rule-recheck.md` |
| Input-issue second opinion | 2b | `extraction/second-opinion.md` |

## Orchestrator actions, not briefs

These run as scripts or orchestrator steps between the agents above. No subagent brief covers them:

- **`mechanical_check.py`** (after every batch's 2b agents finish): enforces the coverage rules in `ledger-schema.md` section 2 against `ratings.md`, the export and every ledger. A FAIL names the failing rows and respawns that batch's extractor or adjudicator (max 2 respawns, per the QA loop protocol).
- **`phrase_scan.py`** (after all ledgers are final): a mechanical, cross-batch scan of every draft's text for repeated sentences and 6-word runs. It writes `ledger/qa/phrase-scan.md` with repeat counts by action type and trace IDs. The orchestrator checks its output against any "comments about many messages" rows any extractor logged (`extraction/extractor.md`, rule 8).
