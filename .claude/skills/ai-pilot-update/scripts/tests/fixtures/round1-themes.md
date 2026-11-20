# Themes: AI-Drafted Messages

Version: 1

> **Source:** Round 1 mapping in [Pilot-Update-Skill-Handoff.md](../../Pilot-Update-Skill-Handoff.md) section 4 (6 themes over 46 failure modes). Theme labels and "What goes wrong" text from the published Week 1 tab of AI-Drafted Messages: Pilot Week 1 Update, read via Drive on 2026-11-05. Danny approved the mapping on 2026-11-03.

Format and rules: `.claude/skills/ai-pilot-update/references/feature-file-schema.md` section 2. The `Failure modes` cell lists `round-slug: FM-NN, ...` and separates rounds with `;`. `theme_counts.py` reads this file; edit it only through a Gate 1 ruling, and bump the version when you do.

## Themes

| # | Theme | What goes wrong | Failure modes |
| --- | --- | --- | --- |
| 1 | Re-asking for known facts | Asks for blood pressure, or why a medication is taken, when the chart or thread already has the answer | pilot-1: FM-01, FM-16, FM-43, FM-47 |
| 2 | Length, repetition and buried asks | Repeats advice already sent, counsels on every minor side effect, and puts the provider's question below the education | pilot-1: FM-11, FM-12, FM-25, FM-32 |
| 3 | Pricing | A price placeholder for every option before the patient picks one, a price fact the draft can't verify, or pricier options first | pilot-1: FM-02, FM-07, FM-08, FM-09, FM-10, FM-26, FM-49 |
| 4 | Clinical judgment | Misapplies a guideline: eligibility, interim dosing, drug interactions, or re-offering a drug that caused side effects | pilot-1: FM-05, FM-06, FM-19, FM-21, FM-22, FM-23, FM-24, FM-28, FM-31, FM-35, FM-36, FM-38, FM-40, FM-42, FM-48 |
| 5 | Medication status | Continues or changes a dose without confirming the patient received or started it, or misses skipped doses | pilot-1: FM-15, FM-17, FM-18, FM-20, FM-29, FM-37, FM-44, FM-46 |
| 6 | Unclear instructions | A dosing sentence that doesn't name the drug, two target doses in one sentence, or ambiguous shipment dates | pilot-1: FM-03, FM-04, FM-27, FM-30, FM-34, FM-39, FM-41, FM-45 |

## Not in a theme

| Round | Failure mode | Reason | Ruled by |
| --- | --- | --- | --- |

## Version log

| Version | Date | Change | Ruled by |
| --- | --- | --- | --- |
| 1 | 2026-11-03 | Round 1 (pilot-1): 6 themes over 46 failure modes | Danny, Week 1 update |
