# Feedback log: feature-brief-writer

Record each issue Danny or a run surfaces, then the fix. Bump the version in `SKILL.md` `<iteration>` when a fix changes the skill.

## Feedback Log

<!-- Copy this block for each issue. Newest first. -->

### Issue #[N]
**Date:** [Date]
**Reported by:** [Who noticed the issue]
**Input:** [What was provided to the skill]
**Expected:** [What should have happened]
**Actual:** [What actually happened]
**Root Cause:** [Why it failed, and which section of SKILL.md, the template, or evals.md should have prevented it]
**Fix:** [What was changed]
**Status:** 🔴 Open | 🟡 In Progress | 🟢 Fixed | ⚪ Won't Fix

## Performance Tracking

Pulled from `observability/invocation-log.jsonl` at each periodic review. No extra logging.

| Metric | How to measure | Target |
|---|---|---|
| First-round pass rate | Runs where every eval passed in round 1, over all runs | Rising over time |
| Adoption | Briefs Danny approved at Gate 2 without rewriting a section | Every run |
| Recurring failures | Eval IDs that fail in more than one run | Falling over time |
