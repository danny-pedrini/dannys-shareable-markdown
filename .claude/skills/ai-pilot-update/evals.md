# Evals: ai-pilot-update

Each gate's grader grades that gate's evals (`references/qa-briefs.md`) and writes Pass or Fail with evidence into its report. The trace author grades the evals whose Gate says "trace author", at Step 7. It also grades O-2 on the trace it writes when a stopped run resumes.

Step 6 collects every result into `eval-results.md`, and Step 7 adds the trace author's. The trace records them all. Code evals name the script that measures them; the grader runs it and reads its output. Judge evals are the grader's own reading of the files.

Examples come from Round 1 and the published Week 1 tab. They illustrate a failure; they are not rules.

## Active evals

| ID | Name | Gate | Check | Added |
| --- | --- | --- | --- | --- |
| G1-1 | Every fact cites a source read this run | 1 | Code | 2026-11-05 |
| G1-2 | Theme counts recompute from the round files | 1 | Code | 2026-11-05 |
| G1-3 | Audit-only drafts kept separate in the ledger | 1 | Judge | 2026-11-05 |
| G1-4a | Quotes verbatim | 1 | Judge | 2026-11-05 |
| G1-4b | Attribution conflicts marked in the ledger | 1 | Judge | 2026-11-05 |
| G1-5a | Every run-set judge read whole, with SHAs | 1 | Judge | 2026-11-05 |
| G1-5b | Each covered verdict cites the passage that implements it | 1 | Judge | 2026-11-05 |
| G1-5c | Every overlay and the spec that wires it read whole, with SHAs | 1 | Judge | 2026-11-11 |
| G1-6a | Every ticket read live this run | 1 | Code | 2026-11-05 |
| G1-6b | Ticket-dependent counts recomputed | 1 | Code | 2026-11-05 |
| G1-7a | Ramp gates and dates match the feature file | 1 | Code | 2026-11-05 |
| G1-7b | Every challenge has Danny's ruling before drafting | 1 | Judge | 2026-11-05 |
| G1-8 | Interviewee counts at or above the floor | 1 | Judge | 2026-11-05 |
| G1-9 | Adapter read first-hand | 1 | Judge | 2026-11-05 |
| G1-10 | Derived facts recompute | 1 | Code | 2026-11-05 |
| G1-11 | Prior-update facts cite this run's read of the prior tab | 1 | Judge | 2026-11-05 |
| G1-12 | Every unresolved comment captured | 1 | Judge | 2026-11-05 |
| G1-13 | Each failure mode in exactly one theme | 1 | Code | 2026-11-05 |
| G1-14 | Every new round's tickets reach a theme row | 1 | Judge | 2026-11-06 |
| G2-1 | Every number traces to its fact; no superseded figure | 2 | Code + Judge | 2026-11-05 |
| G2-2 | No session artifacts or banned links | 2 | Code | 2026-11-05 |
| G2-3 | Writing hard searches pass | 2 | Code | 2026-11-05 |
| G2-4 | Dependent numbers agree across sections | 2 | Judge | 2026-11-05 |
| G2-5 | Every eval gap has a fix row | 2 | Code | 2026-11-05 |
| G2-6 | Each covered theme names its judge | 2 | Code | 2026-11-05 |
| G2-7 | Owners linked; one eval owner above the table | 2 | Code | 2026-11-05 |
| G2-8 | Sections present and in order | 2 | Code | 2026-11-05 |
| G2-9 | Challenged gates and claims not stated as settled | 2 | Judge | 2026-11-05 |
| G2-10 | Danny's edits survive | 2 | Code | 2026-11-05 |
| G2-11 | Clarity over punchiness | 2 | Judge | 2026-11-05 |
| G2-12 | Bullets at 4 sentences or fewer | 2 | Code | 2026-11-05 |
| G2-13 | No 3-clause sentences | 2 | Code + Judge | 2026-11-05 |
| G2-14 | Unpublished metric values stay out | 2 | Code | 2026-11-05 |
| G2-15 | Audit findings labeled in the draft | 2 | Code | 2026-11-05 |
| G2-16 | Reviewer findings applied without Danny are defect fixes | 2 (trace author) | Judge | 2026-11-05 |
| G3-1 | Tab text matches the draft | 3 | Code | 2026-11-05 |
| G3-2 | Every table has set column widths | 3 | Judge | 2026-11-05 |
| G3-3 | No header word breaks mid-word | 3 | Judge | 2026-11-05 |
| G3-4 | Tab links match the draft | 3 | Code | 2026-11-05 |
| G3-5 | Writes go only to the new tab | 3 | Judge | 2026-11-05 |
| G3-6 | Every link opens | 3 | Code | 2026-11-05 |
| O-1 | Run log complete at each gate | All | Code | 2026-11-05 |
| O-2 | Stop rule honored | All (trace author) | Judge | 2026-11-05 |
| O-3 | Round outputs untouched | 7 (script) | Code | 2026-11-05 |
| GS-1 | Theme assignments accepted unchanged | 1 (trace author) | Judge | 2026-11-05 |
| GS-2 | Eval-coverage verdicts accepted unchanged | 1 (trace author) | Judge | 2026-11-05 |
| GS-3 | Render accepted unchanged | 3 (trace author) | Judge | 2026-11-05 |

## Definitions

### G1-1: Every fact cites a source read this run
**Pass:** `check_facts.py` exits 0. **Fail:** any problem it prints.
**Example:** the precedent acceptance rate came from Danny because the Looker tiles didn't return it. The ledger records it as his ruling, not as a Looker read.

### G1-2: Theme counts recompute from the round files
**Pass:** a fresh `theme_counts.py` run on `themes-working.md` gives the same `theme-counts.json`, and every `computed` fact matches it. The run passes a `--round` for every round in scope at Step 0, whatever its sources, and a `--prior-round` for every `rounds[]` entry with `first_update` set. **Fail:** any difference, or a round left off either list.
**Example:** Re-asking for known facts is 9 drafts from all 4 raters.

### G1-3: Audit-only drafts kept separate in the ledger
**Pass:** every theme with `audit_only` above 0 has two facts, counted drafts and found on review. **Fail:** one fact holds a summed count.
**Example:** Pricing was 5 counted drafts plus 7 found on review; most of its drafts were audit-found.

### G1-4a: Quotes verbatim
**Pass:** every `interview-claims.md` quote is a character-for-character substring of its source at the named location, after normalizing whitespace and quote marks. The grader opens each source. **Fail:** any mismatch.

### G1-4b: Attribution conflicts marked in the ledger
**Pass:** every quote whose speaker differs between the session notes and a synthesis is marked `CONFLICT` in `interview-claims.md`; at Gate 2, `check_doc.py` keeps marked quotes out of the draft. **Fail:** an unmarked conflict.
**Example:** in Round 1, one quote was credited to different speakers in the two sources, so it was dropped.

### G1-5a: Every run-set judge read whole, with SHAs
**Pass:** for every judge in the run set, `sources.md` has every file under `prompts/` (every phase) and every `.py` file holding prompt text or pass/fail rules, each with a blob SHA, read OK this run. **Fail:** any judge or file missing.
**Example:** at one point only 5 of 10 judges had been read first-hand. Rx guideline adherence has two phases, `analyze_v1.md` and `adherence_v1.md`.

### G1-5b: Each covered verdict cites the passage that implements it
**Pass:** every Yes and Partly verdict in `eval-coverage.md` quotes a rule, and the grader finds that rule in the cited file at its SHA. A claim about judge inputs cites the adapter or `evals.context_confirmed`. **Fail:** any verdict without a confirmed passage.
**Example:** completeness's `prompts/v1.md` is an 11-line header; its rule is the `verdict` field description in `models.py`. A subagent claimed judges see only one medication doc; the adapter showed that was wrong.

### G1-5c: Every overlay and the spec that wires it read whole, with SHAs
**Pass:** the files in `evals.overlays.dir` at the recorded commit (the grader lists the folder itself) and the file at `evals.overlays.spec` are each in `sources.md` with a blob SHA, read OK this run; the `eval-coverage.md` footer counts overlay files ("12 of 12 overlay files"); and no Yes or Partly verdict cites only a base judge when an overlay exists for that judge. **Fail:** any overlay file or the spec missing, a footer count that doesn't match the folder, or a verdict that ignores an overlay.
**Example:** in Week 2 the first Step 3 pass graded only the base judges and missed `hdef/eval/overlays/` and `hdef/spec.yaml`. Five of six verdicts changed once they were read.

### G1-6a: Every ticket read live this run
**Pass:** every key the doc counts or links is in `tickets.json` with a `read_at` in this run (`check_facts.py`). **Fail:** any key missing or stale.

### G1-6b: Ticket-dependent counts recomputed
**Pass:** `theme_counts.py --tickets tickets.json` output matches every ticket fact, after `ticket_rulings`. The rerun passes a `--filed-round` for every filed round not passed as `--round`. Every key has its live status category (To Do, In Progress or Done), so closed tickets drop out. **Fail:** any difference.
**Example:** after Danny dropped one P1 and relabeled one ticket, 33 became 32: 14 P1, 11 safety and 21 efficiency. The clinical-judgment cell in the published tab still says 11; the count is 10.

### G1-7a: Ramp gates and dates match the feature file
**Pass:** every ramp fact is a `ruling` from `feature.json` `ramp`, and `check_facts.py` confirms each date matches. Where the launch brief differs, a fact records the brief's value too. **Fail:** a ramp fact from the brief alone, or a mismatch.
**Example:** "1% of patients on Nov 10, one day later than the launch brief."

### G1-7b: Every challenge has Danny's ruling before drafting
**Pass:** every `comments.md` row with a Challenges entry has a Ruling other than `open`, or Danny said at Gate 1 to leave it open, before Step 4's first event. **Fail:** a challenge with no ruling or recorded choice to leave it open.

### G1-8: Interviewee counts at or above the floor
**Pass:** each theme's interviewee fact is at or above `interviewee_floor`. **Fail:** any below.
**Example:** session rows gave Pricing 0; the syntheses gave 3 of 5.

### G1-9: Adapter read first-hand
**Pass:** `sources.md` lists the adapter path with its blob SHA, read OK this run, and every `eval-coverage.md` claim about what judges see cites that path or `feature.json` `evals.context_confirmed`. **Fail:** the adapter wasn't read, or a judge-input claim cites a subagent or nothing.
**Example:** a subagent claimed judges see only one medication doc; the adapter showed that was wrong.

### G1-10: Derived facts recompute
**Pass:** `check_facts.py` prints no problem for a derived fact, and the grader recomputes every `formula (manual)` row from its input facts. **Fail:** any derived Value differs from its formula.
**Example:** after 30% became 20%, the "every 10 points below 30%" line went stale.

### G1-11: Prior-update facts cite this run's read of the prior tab
**Pass:** every fact about the prior update, including each "Since last update" value, cites the `sources.md` row for this run's Docs read of the prior tab. **Fail:** any cites a local file or the prior update's `facts.md`.
**Example:** Danny edited the Week 1 tab by hand after the local draft was written, so the tab, not the file, is what readers saw.

### G1-12: Every unresolved comment captured
**Pass:** `comments.md` has a row for every unresolved comment that this run's `list_comments` read returned. **Fail:** any missing.
**Example:** an unresolved comment thread on the Week 1 tab asked whether the ramp bar means never ramping without lower handle time.

### G1-13: Each failure mode in exactly one theme
**Pass:** `theme_counts.py` on `themes-working.md` exits 0. It exits 3 when a failure mode has no theme and isn't in the "Not in a theme" table. It exits 2 when one sits in two themes, or in a theme and in "Not in a theme". **Fail:** any other exit.
**Example:** Round 1 mapped 46 failure modes to 6 themes.

### G1-14: Every new round's tickets reach a theme row
**Pass:** every round in scope at Step 0 is in `theme-counts.json` `rounds`, so the filed keys of its themed failure modes reach their theme's Tickets cell. **Fail:** a new round passed only as `--filed-round`, whose keys reach the doc-wide total alone.
**Example:** run only on thumbs-down rounds, the edits round's QCARE-297, QCARE-298 and QCARE-299 would reach no theme row.

### G2-1: Every number traces to its fact; no superseded figure
**Pass:** `check_doc.py` prints no `numbers` or `superseded` problem. The grader confirms each number matches the fact for its place in the doc, not only some fact. **Fail:** any problem, or a correct number in the wrong place.
**Example:** the superseded sizing figures are $1.9M, $1.22M and 30%.

### G2-2: No session artifacts or banned links
**Pass:** no `artifacts` problem from `check_doc.py`. **Fail:** any.
**Example:** Danny removed the session-notes and recording links from the Week 1 tab.

### G2-3: Writing hard searches pass
**Pass:** no `writing` problem from `check_doc.py`. **Fail:** any.

### G2-4: Dependent numbers agree across sections
**Pass:** each count that appears in more than one place (TL;DR, pilot table, theme table, priority table, appendix) has one value. **Fail:** any two places disagree.
**Example:** after 30% became 20%, the "every 10 points below 30%" line went stale.

### G2-5: Every eval gap has a fix row
**Pass:** every Gap has a `Fix row` label that is a row of the eval table, and every Partly has one or `none: <reason>` (`check_doc.py` eval gaps). One row may close more than one theme. **Fail:** any missing.
**Example:** a draft said the eval changes "close each gap" when one gap had no row. "Pricing and instruction clarity" is one row for two themes.

### G2-6: Each covered theme names its judge
**Pass:** each theme row's evals cell starts with the verdict and, for Yes and Partly, names every judge in `eval-coverage.md` (`check_doc.py` themes). **Fail:** any missing.
**Example:** the Week 1 tab shows "Partly" alone because it predates this ruling. It would fail.

### G2-7: Owners linked; one eval owner above the table
**Pass:** no `owners` problem from `check_doc.py`. **Fail:** any.

### G2-8: Sections present and in order
**Pass:** no `structure` problem from `check_doc.py`. **Fail:** any.

### G2-9: Challenged gates and claims not stated as settled
**Pass:** each open challenge in `comments.md` appears in the doc as under discussion, or follows Danny's ruling. **Fail:** the doc restates a challenged gate as settled.
**Example:** an unresolved comment thread on the Week 1 tab asked whether the ramp bar means never ramping without lower handle time.

### G2-10: Danny's edits survive
**Pass:** `check_doc.py --danny <snapshot>:<base>` prints no `danny` problem for any snapshot. **Fail:** any line Danny wrote is gone.
**Example:** after each of Danny's "I was making manual edits" messages, both sets of edits had to be re-read and confirmed.

### G2-11: Clarity over punchiness
**Pass:** the grader finds no sentence clipped so short it drops what readers need (an actor, a number, or the reason). **Fail:** any, quoted.
**Example:** "make it more concise" turned into empty, clipped copy.

### G2-12: Bullets at 4 sentences or fewer
**Pass:** `check_doc.py` prints no `length` problem on the final `update.md`, run after the last fix. **Fail:** any.
**Example:** the Week 1 draft had bullets over 4 sentences.

### G2-13: No 3-clause sentences
**Pass:** the grader reads every REVIEW line `check_doc.py` prints and finds no sentence with 3 or more clauses. **Fail:** any, quoted.
**Example:** a trim in the Week 1 draft introduced a 3-clause sentence.

### G2-14: Unpublished metric values stay out
**Pass:** no `metrics` problem from `check_doc.py`. **Fail:** any.
**Example:** Danny ruled that the doc reports which metrics have data, not their values, until he says the values are ready.

### G2-15: Audit findings labeled in the draft
**Pass:** `check_doc.py` prints no `themes` problem, so every theme with audit-only drafts shows both numbers in its row. **Fail:** any. G1-3 checks the ledger; this checks the draft.
**Example:** Pricing's row shows 5 drafts flagged and 7 found on review, never 12.

### G2-16: Reviewer findings applied without Danny are defect fixes
**Pass:** each reviewer or grader finding the orchestrator applied on its own fixes a wrong number, a broken reference or a contradiction with a source. Every other finding is on the list that went to Danny. The trace author compares the reports with `run-log.md` and `STATUS.md`. **Fail:** an addition applied without Danny's go.
**Example:** AGENTS.md: fix defects; bring additions to Danny row by row.

### G3-1: Tab text matches the draft
**Pass:** `compare_tab.py` reports no missing text unit. **Fail:** any.

### G3-2: Every table has set column widths
**Pass:** `build-log.md` has a `set_table_column_width` call for every column of every table. **Fail:** any column without one.
**Example:** Drive's import gave equal-width columns, and the 7-column table ran 8 pages.

### G3-3: No header word breaks mid-word
**Pass:** the grader finds no header cell breaking a word across lines. **Fail:** any, named by page and table.

### G3-4: Tab links match the draft
**Pass:** `compare_tab.py` reports no missing link. **Fail:** any.
**Example:** every appendix row links its Jira ticket.

### G3-5: Writes go only to the new tab
**Pass:** every Docs write in `build-log.md` targets the new tab's ID, and no call touches the doc's title, sharing or comments. **Fail:** any write that targets something else.
**Example:** the Week 1 build edited through the Docs connector and never recreated the doc, so its link stayed the same.

### G3-6: Every link opens
**Pass:** the last `check_doc.py` run prints no `links` problem, so every non-mailto link was opened this run. `compare_tab.py` reports no missing link. **Fail:** any.

### O-1: Run log complete at each gate
**Pass:** `log_check.py` exits 0 before each gate and before Step 7. **Fail:** any non-zero exit.

### O-2: Stop rule honored
**Pass:** `run-log.md` has a Step 1 event for every check Step 1 lists before Step 2 starts. Every failure that persists after its retry, and after the second connector where one exists, ends the run with a `stop` event. **Fail:** any event after an unrecovered failure. The trace author grades it at Step 7, and on the trace it writes when a stopped run resumes.
**Example:** the Looker dashboard tiles didn't return the precedent acceptance rate.

### O-3: Round outputs untouched
**Pass:** at Step 7, `shasum -a 256 -c round-hashes.txt` exits 0. **Fail:** any file differs or is missing. A change by another process fails too, since the run's facts may be stale.
**Example:** the skill consumes `provider-draft-failure-modes` outputs and never redoes them.

## Graduation signals

These measure Danny's changes at a gate, not output quality. A Fail isn't a defect; it resets the count toward graduation in the SKILL.md `<human_in_the_loop>` table (3 consecutive Passes). The trace author grades them at Step 7 from `STATUS.md` and the gate files.

### GS-1: Theme assignments accepted unchanged
**Pass:** Danny changed no proposed theme assignment at Gate 1 and added, split or merged no theme. **Fail:** any change.

### GS-2: Eval-coverage verdicts accepted unchanged
**Pass:** Danny changed no eval-coverage verdict at Gate 1. **Fail:** any change.

### GS-3: Render accepted unchanged
**Pass:** Danny requested no layout fix at Gate 3. **Fail:** any request.

## Version history

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-11-05 | Seeded from handoff section 9 and Danny's answers. The design-time evals advisor's splits and fixes applied: G1-4, G1-5, G1-6 and G1-7 split; G2-1 checks superseded figures; G2-5 rule for Partly and shared rows; G2-10 detection; G3-2 measured from the build log. |
| 1.1 | 2026-11-05 | Danny adopted the advisor's 14 proposed evals (G1-9 to G1-13, G2-12 to G2-16, G3-5, G3-6, O-2, O-3) and 3 graduation signals (GS-1 to GS-3). He kept G2-4 and G2-11 and cut the image half of G3-2. G1-6b checks open tickets only. |
| 1.2 | 2026-11-05 | O-2 is also graded on a stopped run's resume trace. G1-6b names the three status categories and reruns with `--filed-round` for older filed rounds. |
| 1.3 | 2026-11-06 | Theme counts cover every source: G1-2 checks every new round is a `--round` and every prior round a `--prior-round`, and G1-3 and G2-15 name counted drafts. Danny adopted G1-14. |
