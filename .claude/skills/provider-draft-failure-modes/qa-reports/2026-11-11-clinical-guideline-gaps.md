# QA: clinical-guideline gaps (v3.1)

No defects. No additions.

Checked against `Project-Galen/Phase-3/Discovery/Provider-Pilot-Week-2/PLAN-clinical-guideline-gaps.md`. Changes 1 and 2 and E39 are in the skill. Change 3 and E40 stay out. Plan section 2 still says pending.

## Defects

None.

## Additions

None.

## Checks

1. Pass. Extractors read every section of `clinical-rules.md` and still skip the full `docebo-*.md` copy (`references/extraction/extractor.md` line 5, `SKILL.md` line 87).
2. Pass. Rule 7 cites the winning row and never cites a superseded row (`extractor.md` line 20).
3. Pass. The rule recheck calls section 14 the Docebo extraction and names `docebo-<date>.md` (`references/extraction/rule-recheck.md` line 7).
4. Pass. A Docebo row wins a clinical-content conflict. Rulings keep their current precedence. The assumption is tagged (`references/rules-core.md` line 106).
5. Pass. The rules subagent marks a losing row `superseded by CR-14.<n> (Docebo)`. Gate 1 lists rows newly superseded this round (`SKILL.md` lines 140 and 144).
6. Pass. Version is 3.1. E39 is NOT MEASURABLE when no Status contains `superseded by` (`evals.md`, `scripts/run_evals.py`).
7. Pass. Week 2 copy: 27 PASS, 7 FAIL (E11, E17, E22, E24, E26, E28, E29), 4 NOT MEASURABLE (E3, E12, E38, E39). The round folder was not edited.
8. Pass. Zero ledger lines cite CR-1.17, CR-1.21, or CR-6.7.
9. Pass. The blind re-extractor stays blind. The adjudicator already reads all of `clinical-rules.md`. Rule 11 is unchanged.

> **Source:** QA pass 2026-11-11, local read of the files named above.
