# Exemplars

What to imitate and what to avoid. Loaded by the orchestrator and routed to the plan and draft subagents.

> **Source:** Project Galen PRD, "'Complete Patient Chart', EMR 2.0 & the Clinical Decision Support (CDS)," PM lead [Director of Product]. Local mirror `Project-Galen/Project-Docs/Requirements/PRD-Project-Galen-Complete-Patient-Chart.md`; Confluence page. Line numbers refer to the local mirror as read on 2026-10-13 and may drift as the page changes.

The Galen PRD is the model the Care template keeps the best ideas from. It is also about 17,900 words in the local mirror, far more than a non-technical cold reader needs. Imitate the patterns below; do not imitate its length or its structure as a whole.

## Imitate

| Pattern | Where in the Galen PRD | How the template uses it |
| --- | --- | --- |
| A "Reader context (how it works today)" column on every user story | Story table header, line 101 | The story table's Today column |
| A change log with a Why column | Change log, line 14 | The Change log section, at the bottom, started once the PRD is shared |
| Launch stages with exit criteria: Back data, Shadow, Phased ramp, GA | Launch readiness, line 711 | How does it roll out? |
| A Type column on metrics (Primary, Guardrail, Leading) | Phase 1 goals & success metrics, line 116 | The metrics table's Type column |
| Care Ops workstreams with owners | Operational requirements, line 720 | Rows in What do we need from others? |
| Prefixed story IDs (CC-, REC-, CDS-, MSG-) with a priority | Story tables, lines 101 and 319 | The `ID · P` column; the acceptance criteria doc cites these IDs |
| A short Non-goals list, one line each | Non-goals, line 72 | What are we not doing? |

## Avoid

| Pattern | Where in the Galen PRD | What the template does instead |
| --- | --- | --- |
| Acceptance criteria inside story cells, with 6 or more criteria per cell | CC-02 (line 104), REC-01 (line 321) | "What good looks like" is 2 sentences max; the detail goes on the acceptance criteria hand-off list (E33, E34) |
| Whole sub-documents embedded in the PRD | Ivy detailed requirements (line 137), eval dimensions (line 246), message-type eval bar (line 364) | Each is its own doc, linked in Related docs (E35) |
| The sizing calculation reproduced in full | Cost & P&L detail, line 603 | One aggregate number in the business problem, with a link to the sizing doc (E35) |
| Three phases at full depth in one PRD | Phases 1, 2, and 3 throughout | One PRD per launch; later phases are one Out of scope line each (E35) |
| The same content in two places | Vision (line 26) and Appendix D (line 766); FAQs (line 30) and Appendix G (line 814) | Say each fact once (E11); no FAQ section |
| Directional metric targets ("down," "up," "hold or improve") | Metrics table, lines 118, 122, and 125 | A baseline and a numeric target, or `[TBD: needs data]` (E30) |
| Open questions scattered in Notes cells | e.g., CC-02's Notes cell, line 104 | One What's still open? table (E04, E11) |

## The companion

`Project-Galen/Phase-3/Requirements/Acceptance-Criteria-AI-Drafted-Messages-EMR-Functionality.md` (Confluence) shows where the detail the PRD leaves out goes. Each test traces to a PRD story ID in its Source column, which is why story IDs must stay stable (E36).

## Lessons from Danny's edits

Added only on Danny's approval. None yet.

## Gold standard

The Provider Pay PRD, per `references/exemplar-gold.md`. Where it and the Galen patterns above disagree, the gold exemplar wins. At the end of a revise run on a PRD Danny has edited by hand and published, the skill offers to repoint `exemplar-gold.md` at that PRD (SKILL.md, Revise mode, item 7).
