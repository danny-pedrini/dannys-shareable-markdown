# Drafting rules

Step 6 rules. The orchestrator writes the document itself (v1.4); this file replaces the retired draft subagent brief. Read it and every file below from disk at Step 6, even if you read them earlier in the run. By Step 6 the conversation is long, and these files outrank anything you remember from it.

The gate snapshots and the intake transcript hold this run's rules: Gate 1 modifications, intake decisions, Gate 2 deltas, and target answers. Apply each as written. There is no separate list of run rules. If Danny ran `/compact` after Gate 2, these files are the only record of the run; read every one.

Items 3, 4, and 5 load here for the first time in a create run; Step 1 does not read them.

## Read, in this order

1. `references/template.md`
2. `references/metric-taxonomy.md`
3. `references/exemplars.md`
4. `Project-Galen/Phase-1/Galen-Phase-1-Metrics-One-Pager-ADS-v2.md` and `references/exemplar-provider-drafts-confluence.md`, the gold exemplars
5. `danny-voice-exemplar.md`, for the prose around the template's tables, starting with the Feature X doc exemplar
6. `<run>/gate-2.md`
7. `<run>/gate-1.md`
8. `<run>/intake-transcript.md`
9. `Stakeholder Management/stakeholder-directory.md`
10. `forbidden-writing-patterns.md`
11. Every input

## The job

Danny chose the metrics at Gate 2. Render them in the fixed template with definitions an analytics engineer can build from.

## Rules

- The gate-2 snapshot is the metric list. Add nothing, cut nothing, re-tier nothing. If a definition sketch is too thin to render, write it as far as the sources allow and tag the gap `[TBD: owner]` with the owner the intake transcript names.
- Each kept row carries every clause of its gate-2 definition sketch, including measurability notes and caveats. Rewording is fine; dropping a clause is not.
- Follow the canonical header sequence and column headers exactly. Summary uses only the seven allowed labels.
- Every number traces to an input or intake answer, or is `[TBD: owner]`. Every name comes from the stakeholder directory, an input, or the intake transcript.
- Cite only sources a reader can open, as markdown links (taxonomy § Citations). Never cite intake question numbers, gate or reviewer rows, synthesis finding or question numbers, acceptance test numbers, unlinked ticket IDs, or "(Danny Pedrini, Gate N)". State Danny's decisions as the document's position.
- Every guardrail Good cell carries the alarm clause in the one approved form. Baseline and Target appear on Hero and Business outcomes only.
- Write an under-table note only for a choice a careful reader would question, per the taxonomy's calibration examples. When in doubt, omit the note.
- No paragraph over four sentences. No sentence over 35 words. No em dashes. None of: utilize, leverage, facilitate, in order to, prior to, subsequently, delve, landscape, ecosystem, several, a few.
- No SQL, LookML, event or field schemas, tile layout, or Looker explore names.
- State each fact once. Cross-reference by ID everywhere else.
- Change log: one row, today's date, "Initial version", requester Danny Pedrini.

Write the finished document to the output path with the Write tool.
