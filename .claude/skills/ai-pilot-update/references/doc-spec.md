# Doc spec

The structure of the published Week 1 update, written generally. The prior tab is the default structure for the next one: `feature.json` `doc.sections` lists its H2 headings.

A section tied to one round (*Example (Round 1): Appendix B, the edits pass*) comes to Step 0 when that round isn't new. Danny rules to carry it forward (rebuilt from sources he names and read this run), link it (heading and link only) or drop it. A dropped section's heading leaves `doc.sections`, and the ruling goes in `rulings[]`.

**Readers:** `feature.json` `readers`. Engineering leaders are the most demanding: show a data-driven, methodical path to the feature's product and business outcomes.

## Writing rules

- Clarity over punchiness. Tables and data wherever they fit.
- Every number, date and status comes from `facts.md`. Every quote comes from `interview-claims.md`, verbatim.
- No session artifacts: no failure-mode, ticket-draft, gate, row, trace, fact or source IDs, reviewer handles or working-file names. Readers can't open them.
- Quotes carry provider name and date. No links to session notes or recordings (`feature.json` `banned_link_patterns`).
- Slack facts link the specific message's permalink. Other facts link the doc, page, sheet or ticket they came from, read this run.
- Name owners with mailto links. Never cite Danny or his docs as a source; state his rulings plainly.
- Never edit Danny's text unasked. Flag his typos and contradictions at Gate 2; he fixes or rules.
- No bullet or paragraph over 4 sentences. No sentence with 3 or more comma-separated clauses. Run the full workspace writing checklist (AGENTS.md, `forbidden-writing-patterns.md`).
- Write the prose in the voice of `danny-voice-exemplar.md`, starting with the Feature X doc exemplar.

## Header

- H1: `feature.json` `doc.h1_format` (*Example (Round 1): "AI-Drafted Messages: Pilot Week 1 Update"*).
- Byline paragraph: `<Mon D, YYYY> | <author>`.

## TL;DR

Five bullets, each with a bold lead sentence:

1. Provider sentiment, with the main tension (*Example (Round 1): providers see real value but are slower today than with snippets*).
2. Feedback volume by source (for example thumbs-downs, edits, evals and interviews), then ticket counts: open tickets by priority, safety and efficiency split.
3. The fixes that would help providers most.
4. Model or ramp news, with the next ramp date.
5. The bar for the next ramp step after that.

**Since last update** (every update after the first): a short block under the TL;DR listing what changed (data-methods section 3). Write each change as this run's value with the prior one in parentheses, for example `Open tickets: <now> (<prior> at the last update)`, so `check_doc.py` reads only this run's count.

## 1. Where the <stage> stands

A two-column key-value table with no header row and a shaded key column. In `update.md`, its header line is empty (`| | |`). Rows: providers live, feedback volume (counted drafts by source, window, raters), interviews, bug tickets (open count, link to the epic), and the stage's primary metric (*Example (Round 1): "Measured handle time: None yet"*).

## 2. What the feedback says

- One sentence on ranking: by consistency across providers and sources; severity and frequency come through ticket priority; a draft can fall under more than one theme.
- The theme table, columns from `feature.json` `doc.theme_table`: `#`, Theme, What goes wrong, Drafts flagged, Providers interviewed who raised it, Tickets, Caught by evals today.
  - Drafts flagged: counted drafts across all sources, then "plus N more found on review" when audit-only drafts exist. Add the split by source where it helps (data-methods section 1).
  - Tickets: open counted total, then the P0 and P1 split in parentheses.
  - Caught by evals today: the `eval-coverage.md` verdict, then the judge or judges that cover it, per Danny's ruling. Format: "Partly: doctor relationship"; "Gap (unit tests only)". *Example (Round 1): the Week 1 tab shows the verdict alone, because it predates the ruling.*
- A link to the round's full cluster analysis (`round.json` `report.google_doc_url`).
- The lessons (data-methods section 2), each a bold lead sentence plus the numbers.
- **Where our evals fall short:** one paragraph naming the run set and where it is listed. Then one bullet per Gap or Partly theme, grouping themes the same judges miss, quoting the judge rules that matter. End with what readers should watch instead until judges exist.

## 3. What the interviews added

Bold-led paragraphs for each corroborated finding, each followed by its supporting quotes in italics with name and date. Include what providers like. Every finding names how many providers said it.

## 4. Bug tickets

- The priority scale table (Priority, Definition, Count) from `feature.json` `priority_scale` and `theme-counts.json` tickets. Counts are open tickets from every filed round plus those filed outside a round (data-methods section 5).
- The P0 tickets in plain words.
- The efficiency issues raised to P1, as a numbered list.
- Open tickets filed outside a round, each on its own line with a link.
- Evidence added to existing tickets, as a count from `comment-ledger.md`.
- A pointer to Appendix A.

## 5. What we're changing

- **Model:** the change and its reasons, each reason a bold-led bullet with numbers. Each Slack fact ends with the speaker and date in parentheses, linked to the message's permalink (*Example (Round 1): "([AI Eng lead], Oct 28)"*).
- **Content changes:** table (Change, Status, Ask); each Change cell links its page; each Ask names an owner with mailto.
- **Eval considerations:** one paragraph naming the eval owner once with mailto, then a table (Gap, What closes it). One row per distinct `Fix row` label in `eval-coverage.md`; one row may close more than one theme's gap (*Example (Round 1): "Pricing and instruction clarity"*).

## 6. Ramp plan

- The next step and date, compared with the launch brief.
- Each gate as a numbered item: bold gate name, then its status this run. Metric status carries an "as of" time and the instrumentation owner.
- The pilot-alongside ruling and why.
- The bar for later steps, as bullets.
- The business case: the current sizing figure with its link, the precedent, and any derived sensitivity.
- Open challenges stay visibly open.

## Appendix A: P0 and P1 tickets

Table of open P0 and P1 tickets (Priority, Label, The draft should...). Each third cell is the ticket's plain-words title, linked to Jira. Then a line pointing to the P2s on the epic and the launch-blockers dashboard.

## Round appendices

A round appendix holds source-specific detail the theme table can't show, such as edit depth (data-methods section 1). Its counts are already in the theme table, so it never adds to them. It opens with a Source paragraph that a reader can follow: the sheet and tab, the window, the raters with counts, and the read date. Then "What stands out" bullets, the classification method, and its tables. Never include patient names, and never include or link a per-draft log: each row is PHI about one patient's message.

A round appendix carried forward by link keeps its heading and holds only the link to the prior tab's appendix (data-methods section 1).

## Google Docs layout targets (checked at Gate 3)

- Every table has fixed column widths that fit the page; no default equal widths. A narrow column for counts, a wide one for text.
- Header rows bold and shaded; no header cell wraps mid-word.
- Wide tables (6 or more columns) in 9-point text.
- Nested bullets nest; numbered lists restart where the markdown restarts them.
- Links land on the cell or phrase the markdown links.
