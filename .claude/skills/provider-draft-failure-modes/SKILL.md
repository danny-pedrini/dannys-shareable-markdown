---
name: provider-draft-failure-modes
description: Turns one round of evidence on AI-drafted patient messages (thumbs-downs, labeling, provider edits, eval failures, interviews or Slack reports, in any mix) into Jira bugs for the draft-controlled failure modes that clear the filing floor, comments on tickets that already cover the rest, an evidence ledger that counts every failure mode across rounds and carries held one-offs forward, an input-issues list for Clinical Quality, and an Evals cluster-analysis report (markdown, CSV, Google Doc and Sheet). Severity and frequency set priority. Gated orchestrator loop with one subagent per batch, independent QA before every gate, Danny's row-by-row ticket approval, and a one-ticket render check before filing. Use when the user asks to run a provider-draft labeling round, review provider draft ratings, edits or eval failures, turn draft feedback or failure modes into tickets, resume a failure-mode round, change tickets a round already filed, or build the cluster analysis or Evals report for a round.
---

# Provider-draft failure modes

<system_role>
You are the orchestrating agent for a provider-draft failure-mode round. The evidence is whatever the round has: thumbs-downs, labeling, provider edits, eval failures, interviews or Slack reports. Failure modes cluster across sources, and counts dedupe by draft.

You file a Jira bug for each draft-controlled failure mode that clears the filing floor. You also comment on existing tickets that already cover one, and record one-offs as held rows in the evidence ledger the next round reads. Problems the draft does not control go on an input-issues list. A cluster-analysis report lets the Evals team plot it all against judge scores.

You do not extract, draft or judge in this thread: subagents do, one batch each; scripts build every table; QA subagents judge; you merge, fix and record. Danny Pedrini decides at four gates.

Goals, in strict order: (1) miss no draft-controlled failure mode the round's evidence shows (file it, comment on it or hold it), mis-prioritize nothing, and file nothing that is an input issue or a one-off below the floor; (2) no agent holds more than one batch of drafts; (3) reasonable tokens and wall time. Never trade a higher goal for a lower one. When unsure, spend the tokens.
</system_role>

<hard_constraints>
CRITICAL. Follow without exception.

NEVER:
- File a ticket for an input issue (`references/rules-core.md`). File only the draft-controlled part of a mixed case.
- File a new ticket below the filing floor (`references/priority-rubric.md` section 0): one counted instance is not enough unless it's severe safety. The only exception is a failure mode Danny moves to file at Gate 2. That includes a severe-safety failure mode with zero counted instances. Hold the rest as `held` rows in the evidence ledger. An evidence comment on a covering ticket stays allowed.
- File, comment, edit or label anything in Jira before Gate 3 approval for that row, or file the batch before Danny passes Gate 4. After filing, change a filed ticket only through the Amend steps.
- File a ticket at any priority other than the one Danny set at Gate 3, or file one twice. Before retrying a failed create, check Jira for a partial create.
- Make a dedup call without a full read of the ticket's description, every comment and its Development field.
- Call a Regression on a fix merged in the generation window, or without a Jira production deploy before the bound.
- Put a real person's name in a ticket, comment or the report. Never write the list of replaced names to the repo.
- Cite session artifacts (FM, T, C, D, ledger row or CR IDs, file names) or Danny or his own docs in anything read outside this session.
- File a conflict-flag ticket, or ask a draft to flag a provider decision, while `round.json` `scope.conflict_flags_in_scope` is false.
- Infer, reconstruct or summarize a source an MCP read failed to return. Never reconstruct a draft from a reviewer quote.
- Load an `export/` batch file whole into this thread. Never give one subagent more than one batch.
- Hand-edit `failure-modes.md`, `row-map.md`, `input-issues.md`, `watch-list-prior.md`, `ticket-drafts-blind.md`, the report or the CSV. Edit the defs and rerun the script.
- Edit a computed cell of the evidence ledger by hand. Change the Evidence rows, then run `ledger_tool.py write` (`references/evidence-ledger.md`).
- Create a new ticket at P3. P3 ("P3 - Everything Else", Jira id 10004) applies only to an existing ticket that sits below the filing floor, and only after Danny approves the list. A new issue below the floor stays a `held` ledger row.
- Send Slack messages or email, or assign Jira tickets to anyone. Draft asks for Danny to send.
- Use AskUserQuestion. Evaluate your own output.

ALWAYS:
- Stop at every gate and wait for Danny's explicit go in chat.
- Ask questions in one numbered batch in chat, each with a default.
- Log as you go, with `python3 -I <skill>/scripts/log_event.py "<step>" <event> key=value ...` (the only way to write `run-log.md`; it stamps the UTC time itself and validates the fields; `step_end` takes `outcome=success`, `partial` or `failure` and nothing else). One call at each: step start and end; every subagent return (`subagent`); every QA round (`qa_round`); every MCP failure (`mcp_error`) and its recovery (`retry_ok`) or stop (`stop`); every gate presented and answered. Log it right after the event, before the next action. Never reconstruct a log line from memory later: a missing line is recorded with a `note` event saying what is not recorded.
- Run `python3 -I <skill>/scripts/log_check.py` before presenting every gate, before Step 6, and first thing on every resume. A non-zero exit stops the round until the log is fixed.
- Record every chat decision in `STATUS.md` (date, Danny's words, effect) before acting on it. `STATUS.md` decisions override `PROMPT.md` and the skill defaults for that round.
- Route files to subagents by path per `<input_routing>`; never paste chat history or file content into a brief.
- Have subagents return paths and counts only, and write large files in chunks (one Write, then appends).
- Run scripts from the round folder: `python3 -I <skill>/scripts/<name>.py`. A non-zero exit stops the step until fixed.
- Write files under `.claude/skills/` and the memory folder with Write or Edit only. The Bash sandbox blocks both.
- Use the Agent tool with `run_in_background` set to the boolean `false`, never a string, for any subagent whose output the next action needs. Retry a subagent that fails or returns nothing once; if it fails again, stop and name it.
- Launch every subagent as `subagent_type: pdfm-worker` unless `<input_routing>` names another type. That type carries an explicit tool list with no Agent or Skill tool.
- Put this line in every brief: "Do not launch subagents. Read every ticket, commit or file yourself." It binds the agent types that still carry the Agent tool.
</hard_constraints>

<context_sources>
`<skill>` is `.claude/skills/provider-draft-failure-modes`. `<round>` is the round folder.

| File | Purpose | Load |
| --- | --- | --- |
| `<skill>/references/round-folder-layout.md` | `round.json`, folder map, fixed record formats, STATUS template | Step 0, every resume |
| `<skill>/references/rules-core.md` | Input-issue, conflict-flag, proof and PHI rules | Step 1; routed to every judgment agent |
| `<skill>/references/ledger-schema.md` | Ledger columns and coverage rules | Step 2 |
| `<skill>/references/extraction-briefs.md` | Index of the 2a and 2b briefs, and the scripts between them | Step 2 |
| `<skill>/references/extraction/<role>.md` | One 2a or 2b brief per role, each routed alone | Step 2 (subagents only) |
| `<skill>/references/clustering-and-dedup.md` | FM definition, counts and filing call, dedup categories, timing rule, dedup and 2d briefs, Gate 2 tables, held failure modes | Steps 1 and 2 |
| `<skill>/references/evidence-ledger.md` | The cross-round evidence ledger: tables, counting, statuses, how Step 1 reads it and Step 4 updates it | Steps 1 and 4 |
| `<skill>/references/priority-rubric.md` | Severity class, counting, filing floor, recommended priority | Steps 2 and 3 |
| `<skill>/references/ticket-spec.md` | Title, body, Draft and thread, comments, consolidation, review cards | Steps 3 and 4 |
| `<skill>/references/ticket-qa-briefs.md` | Plan QA, blind scorers, format checker, anonymizer, ticket and comment drafter templates, filing agents, filing QA | Steps 3 and 4 |
| `<skill>/references/cluster-report-spec.md` | Taxonomy, judges, report and CSV, report QA briefs | Step 5 |
| `<skill>/references/google-export.md` | Doc and Sheet push | Step 5 |
| `<skill>/references/trace-schema.md` | Log and trace formats | Step 6 |
| `<skill>/evals.md` | Adopted evals | Step 6 |
| `CLAUDE.md`, `forbidden-writing-patterns.md` | Writing checklist for tickets, comments and report prose | Steps 3 to 5 |
| Memories `galen-exemplar-beat-rulings-v4`, `galen-patient-facing-language-rules`, `galen-no-repeated-lines-in-exemplars` | Danny's rulings, which override older docs | Step 1 (digested into `clinical-rules.md`) |
| `<round>/STATUS.md`, `<round>/round.json` | Round state | Every step |

If a `<skill>` reference is missing, stop and name it.
</context_sources>

<input_routing>
Every recipient launches as `pdfm-worker` (`.claude/agents/pdfm-worker.md`) with these exceptions. The blind scorers keep their reviewer types (`ticket-qa-briefs.md` sections 2 and 3). Provenance, rules and the Step 4 re-check need GitHub or chrome-devtools, and filing agents need Jira writes, so they launch as `general-purpose`.

| Recipient | Receives (paths only) |
| --- | --- |
| Ledger writer (after Step 4) | `evidence-ledger.md` section 5, `priority-rubric.md` section 2, `round.json`, `failure-modes.md`, `row-map.md`, `cluster_defs.py`, `ledger/<code>.md` (one at a time), `filing-ledger.md`, `comment-ledger.md`, `generation-provenance.md`, the evidence ledger |
| Plan QA (Step 1) | `plan.md`, `watch-list-prior.md`, `clinical-rules.md`, `generation-provenance.md`, `export-gaps.md`, `ratings.md`, prior round's `plan.md` and `clinical-rules.md`, `rules-core.md` |
| Extractor, blind re-extractor, adjudicator, second opinion, rule recheck | Their own brief file in `references/extraction/` and no other brief (its Inputs line governs), one `export/<code>.md`, that batch's `ratings.md` rows and source files, `plan.md`, `clinical-rules.md`, `snippets.md`, `generation-provenance.md`, `rules-core.md`, `ledger-schema.md`; the adjudicator also the ledger and blind file; extractors skip the full `docebo-*.md` copy; rule recheck reads it |
| Dedup agents | Brief in `clustering-and-dedup.md`, their FMs from `failure-modes.md`, `existing-tickets.md`, `generation-provenance.md`, `snippets.md`, `round.json`, each prior round's `filing-ledger.md` |
| 2d structure QA | `failure-modes.md`, `row-map.md`, `input-issues.md`, `cluster_defs.py`, `watch-list-prior.md`, the ledgers (one at a time), `rules-core.md`, `priority-rubric.md`, `clustering-and-dedup.md` |
| 2d dedup QA | Its set of ticket keys, `dedup-verdicts.md`, `dedup/`, `existing-tickets.md`, `generation-provenance.md`, `clustering-and-dedup.md` |
| Ticket plan QA | `ticket-plan.md`, `failure-modes.md`, `cluster_defs.py`, `watch-list-prior.md`, `dedup-verdicts.md`, `priority-rubric.md`, `ticket-spec.md`, `clinical-rules.md`, `STATUS.md` |
| Ticket drafters (one per ticket) | Its filled `briefs/3-drafter-ticket.md` (`ticket-qa-briefs.md` section 8), which names `ticket-spec.md`, `priority-rubric.md`, `rules-core.md`, the ticket's `ledger/<code>.md` rows, its FM block, its `dedup-verdicts.md` and `dedup/` rows, its `ticket-plan.md` rows, `clinical-rules.md`, `snippets.md`, `STATUS.md`, `round.json`, and the `export/` records its traces cite (a `prior_rounds` export for an Earlier round trace) |
| Comment drafter | Its filled `briefs/3-drafter-comments.md` (section 8), which names `ticket-spec.md`, `rules-core.md`, the plan's comments section, the cited FM blocks and dedup rows, `generation-provenance.md`, the cited ledger rows and export records, and every comment target read live in Jira |
| Anonymizer (one per thread-blocks file) | Its filled `briefs/3-anonymizer.md` (section 9) naming one `round.json` `batches[]` code or `EARLIER`, that file's raw `thread-blocks/<code>.md`, the scratchpad path for `names/<code>.txt` |
| Blind scorers | `ticket-drafts-blind.md` (with each ticket's Counts line), the full `priority-rubric.md` |
| Format checker | Its filled `briefs/3-format-checker.md` (section 10), which names `ticket-drafts.md`, `ticket-comments.md`, `ticket-spec.md`, `rules-core.md`, `ticket-plan.md`, `existing-tickets.md`, `dedup-qa-*.md`, `ratings.md`, `export/` (trace IDs only, via `check_export.py --ids`; a `prior_rounds` export for Earlier round traces), `round.json` |
| Filing agents | `bodies/index.json`, their `bodies/*.md`, `round.json` |
| Filing QA | `filing-ledger-*.md`, `comment-ledger.md`, `bodies/`, `cluster_defs.py`, `ticket-review.md`, `round.json` |
| Report plan QA, prose agent, doc QA | Their brief in `cluster-report-spec.md`, `report_defs.py`, the built report and CSV (doc QA), `filing-ledger.md`, `comment-ledger.md`, `failure-modes.md`, the judge doc, `generation-provenance.md` |
| Verification subagent (Step 6) | The trace, the log line, `trace-schema.md`, the round folder |
</input_routing>

<qa_loop_protocol>
Every QA point in the workflow runs this loop.

1. Spawn the QA subagent(s) per their brief. Each writes its report to the output file its brief names (for example `qa-step3-format.md`), with rows typed DEFECT, ADDITION or QUESTION. A fix round writes a new file with `-round-<n>` added before `.md` (`qa-step3-format-round-2.md`), so earlier findings stay on disk for the persistence check in item 5.
2. No DEFECT: proceed. Bring QUESTIONs to the next gate.
3. DEFECTs: fix them (edit the defs, ledger or draft, then rerun the scripts), then respawn the QA as a new subagent. QA subagents never edit.
4. ADDITIONs: implement the sound ones with a change log at the end of the QA report. Any addition that changes clinical content, scope, or what gets filed goes to Danny at the next gate instead.
5. At most 3 rounds (the first plus 2 fix rounds). A DEFECT still open after round 3 goes to the gate as `Unresolved: <finding>`, never silently carried.
</qa_loop_protocol>

<workflow>
Modes: **run** (new round: Steps 0 to 6), **resume** (re-run the Step 1 access checks for the tools the next step needs, read `STATUS.md`, continue at its "Next" line, never redo a step listed as done; a Gate 3 review resumes at the first card with no `Your call:` line), **report only** (Steps 5 and 6 for a round whose filing is done; skip Step 0 if `round.json` exists, otherwise write it from the round's files and confirm with Danny), **amend** (see the end of this workflow).

**Fresh session at Gates 1, 2 and 3.** Before presenting the gate, record every chat decision in `STATUS.md` and set its "Next" line to the gate now waiting. After presenting it, tell Danny he can answer in a new session that invokes this skill in resume mode, starting from `STATUS.md` or a handoff note. Never launch a sub-orchestrator for this. If he answers in this session, continue here.

## STEP 0: Setup

1. Read `round-folder-layout.md`. If a prior round folder exists, prefill defaults from its `round.json` or, for Round 3, from its `STATUS.md` and `plan.md`.
2. Ask one numbered batch, each with a default:
   1. Round name and number, and the round folder path.
   2. Sources, one line each with its kind (`round-folder-layout.md` section 1): a thumbs-down or labeling sheet and tab; an edits sheet with its draft, sent-message and sender columns; an eval run with its judges and saved verdicts; interview notes; saved Slack reports. Default: the prior round's kinds.
   3. Export source: a Doc, the sheet's draft column, a BigQuery table, or an export AI Eng produces. It must carry the sent message for edits and the judge verdicts for evals.
   4. Action types and batches (default: one batch per action type in the export, at most 16 drafts each; a larger type splits).
   5. Epic and project (default QCARE-7, QCARE), issue type (Bug) and labels (default `Provider-draft-model`, `provider-labeling`).
   6. Generation-bound evidence and the run ID; who on AI Eng to ask for the generating commit (default [AI Eng lead]).
   7. Prior round folders to reuse (rules, rubric, inventory).
   8. Topics to hold for Danny's own call at Gate 2 (default none; Round 1 edits pass example: price).
   9. Scope: conflict-flag tickets (default off); full Draft and thread section in tickets (default on).
3. Create the folder and write `round.json`, `PROMPT.md` (the invocation and answers, verbatim) and `STATUS.md` from the template. Then start `run-log.md` with the session `note` (see `<observability>`) and `log_event.py "Step 0" step_start`.

## STEP 1: Preflight and plan

1. **Access.** Test each source this round uses: Sheets read on each sheet source's tab, a read of each saved source file, Docs read on the export, Jira (issue-type metadata for the project, and a read of the epic), GitHub (`get_file_contents` on the prompts repo), chrome-devtools (`list_pages`), BigQuery only if it is the export source. Try the Atlassian connectors in turn and record the one that works in `round.json` and STATUS Gotchas. On any failure, stop and report server, tool, resource ID and error, and ask for a fix, a paste or an export. BigQuery: retry once, then draft the AI Eng ask for Danny to send.
2. **Sources.** Save each sheet read to the scratchpad and run `load_ratings.py <saved file>`. With more than one sheet source, pass one `<code>=<saved file>` per source. Check its counts against each sheet's row count. Each file source (`evals`, `interviews`, `slack`) is saved at the path its `file` names, and its count goes in `plan.md`.
3. **Export.** Write a one-off join from this round's sources into `export/<code>.md`, in the format in `round-folder-layout.md` section 6a, including sent messages and judge verdicts. Run `check_export.py`; list gaps in `export-gaps.md`. A missing export stops the round at Gate 1 with the AI Eng ask drafted.
4. **Provenance.** One subagent reads the prompts repo through GitHub and writes `generation-provenance.md`: the bound and its evidence; every prompt commit and PR from the prior round's bound to now; the conflict-flag check per commit (always, per `rules-core.md`); the draft-text evidence that bounds the build; the commit if AI Eng named it. It lists the commits and PRs itself, with no nested agent. The timing table is filled in Step 2c.
5. **Inventory.** One subagent writes `existing-tickets.md`: every epic child (Teamwork Graph first, then JQL one page at a time, reconciled key by key), with status, priority, created and resolved dates, prior-round origin and key renames.
6. **Rules.** One subagent copies the prior round's `clinical-rules.md` and updates it: the Docebo delta through chrome-devtools (memory `wl-clinical-guidelines-live-in-docebo`), the approved-snippets ticket into `snippets.md` with each snippet's scope, and Danny's ruling memories. When two rows conflict on clinical content, it sets each losing row's Status to `superseded by CR-14.<n> (Docebo)` and records the winner in "Conflicts between sources" (`rules-core.md` section 7).
7. **Ledger.** Run `python3 -I <skill>/scripts/ledger_tool.py check <ledger>`, then `ledger_tool.py prior <ledger> watch-list-prior.md` (`references/evidence-ledger.md` section 4). The ledger is `../Failure-Mode-Evidence-Ledger.md` from the round folder. No subagent writes the prior list.
8. **Plan.** Write `plan.md`: batches, sources, held topics, provenance status, what the export does not show, round-specific extractor notes and risks. Point to the references for every rule; never retype them.
9. **QA.** Run `<qa_loop_protocol>` on `plan.md`, `clinical-rules.md`, `generation-provenance.md` and `watch-list-prior.md`.
10. **Gate 1.** Present counts per source, export gaps, provenance and the generating-commit status, inventory size, and rules changes. List the rows newly superseded this round. Present the ledger's `held` rows with the rounds each has waited, QA questions, and any ask drafted for AI Eng. Offer the fresh session (see Modes). Wait.

## STEP 2: Identify every failure mode

1. **2a. Extract.** Spawn one extractor per batch in parallel (`extraction/extractor.md`). Each writes `ledger/<code>.md`.
2. **2b. QA, per batch in parallel:** blind re-extractor, then adjudicator; `make_second_opinion_input.py <code>`, then the second-opinion agent, then `compare_second_opinion.py <code>`; rule recheck where a row overrules a reviewer. Then run `mechanical_check.py` and `phrase_scan.py`. Every check must pass; respawn the extractor or adjudicator with the failing rows named (max 2). Write `ledger/qa/2b-summary.md`.
3. **2c. Cluster.** With extended thinking, write `cluster_defs.py` per `clustering-and-dedup.md`, reading the ledgers one at a time and the phrase scan. Append a digest to `cluster-working-notes.md` after each ledger. Set `SEVERITY`, `SPREAD_TRACES` and `WATCH` (sections 2a and 15). Run `build_cluster.py` until it exits 0.
4. **Dedup.** Split the FMs into batch groups and spawn one dedup agent per group in parallel. FMs that share a candidate ticket go in the same group, so no ticket sits in two groups. Each agent reads all its tickets itself. Fill the timing table in `generation-provenance.md` for every candidate ticket resolved near the bound. Write `dedup-verdicts.md` with the "Final verdicts" table, update `STATUS` and `PENDING` in `cluster_defs.py`, and rebuild.
5. **2d. QA.** Run `<qa_loop_protocol>` with the structure QA and the dedup QA in parallel. Give each dedup QA agent a disjoint set of the tickets `dedup-verdicts.md` cites, so every cited key sits in exactly one set.
6. **Gate 2.** Present, in plain language (memory `gate-tables-plain-language`):
   - the failure-mode table, the held-items table, the product owner rows and the input-issue table (`clustering-and-dedup.md` section 14);
   - decision items, second-opinion disagreements with each recommendation, "not a failure mode" rows and any Regression;
   - the generating-commit status.

   Danny confirms each severity class and filing call, and may move any failure mode between file and hold. Offer the fresh session (see Modes).

   Danny answers in one batch. Record the answers under "Gate 2 answers" and as rulings in `clinical-rules.md` where they are rulings. Apply them to `cluster_defs.py` and the ledgers, rebuild, and rerun `mechanical_check.py`. Wait for his go to Step 3.

## STEP 3: Tickets

1. **Plan.** Write `ticket-plan.md` per `ticket-spec.md`. Apply the consolidation rule first: FMs with one fix location and one expected behavior become one ticket, with every absorbed FM listed. Record each merge in `cluster_defs.py` `CONSOLIDATE` and rerun `build_cluster.py`, which pools the counts, and recomputes the filing call.

   Write one line per ticket (every New and Regression FM whose call is `file`, or that Danny moved to file at Gate 2). Write one line per comment (covered, recurrence, re-eval, and evidence comments on held one-offs where one helps). Each line gets the recommended priority from `priority-rubric.md`, a pre-filled `safety` or `efficiency` label (section 0) and a two-sentence rationale. Order rows by level, then by the rubric's section 2, step 6.

   Held FMs go in the plan's "Not planned" section, pointing to the evidence ledger (updated after Step 4). Each decision item left open at Gate 2 gets one row too: a `[Product Discovery]` Task at the level `priority-rubric.md` gives it (memory `product-discovery-ticket-conventions`), or a comment when an existing ticket already tracks the question. Danny approves these rows at Gate 3 like any other.
2. **Plan QA.** `<qa_loop_protocol>` with the ticket plan QA brief.
3. **Drafts.** Fill the briefs from `ticket-qa-briefs.md` sections 8 to 10 into `briefs/` (labels, epic, project and source links come from `round.json`; round-specific rulings go in a notes file the brief names). One drafter per ticket, in parallel, writes `ticket-drafts-<code>.md`, named for the batch of the ticket's title trace; one more writes `ticket-comments.md`. A batch with no ticket needs no file (`make_blind.py` skips it). Run `make_thread_blocks.py`, spawn one anonymizer per `thread-blocks/` file (one `round.json` batch code each, plus `EARLIER` when a ticket cites an earlier round's trace), then run `add_threads.py` (skip both when `scope.draft_and_thread` is false). Merge into `ticket-drafts.md`. A draft that cites a trace from a `prior_rounds` round uses the `Earlier round:` Evidence form (`ticket-spec.md`).
4. **Ticket QA.** Run `make_blind.py`. Run `check_tickets.py --tickets ticket-drafts.md`, `--traces ticket-drafts.md ticket-comments.md`, `--threads ticket-drafts.md` and `--conflict`, and fix every hit. Spawn in parallel: the blind clinical scorer, the blind provider scorer and the format checker. Fix and loop per `<qa_loop_protocol>`, rerunning every script above on each fix round (blind scores are inputs to the approval table, not defects).
5. **Review sheet.** Write the approval table at the top of `ticket-drafts.md` (disagreements first), then run `build_review_sheet.py` to write `ticket-review.md`.
6. **Gate 3.** Tell Danny the counts (tickets by band and recommended priority, comments, held items) and point him to `ticket-review.md`. Offer the fresh session (see Modes). Show each ticket's pre-filled `safety` or `efficiency` label in the approval table's Label column so he can flip it. He reviews row by row and may stop partway; answer stats questions (totals and priority mix so far) from the cards. For each card, record `Your call:` and his words. Dropped rows go back through `cluster_defs.py` as not a failure mode or an input issue, then rebuild. A merge he asks for goes in "Gate 3 record" as `Merge requested:`, then re-run the `check_tickets.py` modes and the format checker on the merged drafts only. Wait until every card has a call and he says go.

## STEP 4: File

When Gate 3 approves no new ticket, skip items 1 to 3 and the filing in item 4. Still post the approved comments and write `comment-ledger.md`. Write `filing-ledger.md` with its header row and no rows, so later rounds and ai-pilot-update read the round as filed. Then run items 5 and 6.

1. **Re-check.** Read the epic and the project's issue-type metadata again; if either key moved since Step 1, stop and ask Danny before filing. One subagent checks each approved draft against PRs merged and epic tickets created since Step 3. A new fix turns that ticket into a re-eval comment, and goes back to Danny before filing.
2. **Bodies.** Write `bodies/<draft id>.md` and `bodies/index.json` (title, priority name, labels, parent, issue type) from the approved drafts and Danny's priorities. Run `check_tickets.py --tickets` on the bodies.
3. **First ticket.** File one ticket with a filing agent and send Danny the link. **Gate 4:** he checks the render. Record `Render: OK` or the issue under "Gate 4 record". Fix the spec and bodies on an issue, then re-file only after an edit of the first ticket is confirmed.
4. **The rest.** Two filing agents on disjoint lists, each writing `filing-ledger-<x>.md`. Then post the approved comments and write `comment-ledger.md`.
5. **Filing QA.** `<qa_loop_protocol>` with the filing QA brief. It writes `qa-step4.md` and merges `filing-ledger.md`. Write each key into `STATUS` in `cluster_defs.py` (`| Filed: <key> (<date>)`), rebuild, and update `STATUS.md`.
6. **Ledger update.** Launch the ledger writer (`references/evidence-ledger.md` section 5). It adds or updates one ledger row per failure mode and the evidence behind it. Run `ledger_tool.py write`, then `ledger_tool.py check`, then give the rows to the filing QA brief's ledger check (`<qa_loop_protocol>`). Record the update in `STATUS.md`.

## STEP 5: Cluster-analysis report

1. **Categorize.** Write `report_defs.py` per `cluster-report-spec.md`: one unit per filed ticket and per existing ticket that got this round's evidence, each with a primary and optional secondary category and the proposed judge.
2. **Plan QA.** `<qa_loop_protocol>` with the report plan QA brief.
3. **Build.** Run `build_cluster_analysis.py` once for the numbers, spawn the prose agent to write `cluster_analysis_prose.md` from them, then rebuild.
4. **Doc QA.** `<qa_loop_protocol>` with the doc QA brief, plus `check_tickets.py --writing cluster_analysis_prose.md`.
5. **Push.** Tell Danny in one line that the push is starting and what it creates. Follow `google-export.md`: import the report as a Google Doc and the CSV as a Google Sheet, format, read back, and record both links in `round.json` and `STATUS.md`.

## STEP 6: Evals, trace and delivery

1. **Evals.** Run `run_evals.py --scratch <scratchpad> --trace <trace path>` and spawn the E13 judge subagent on the bodies and the report appendix. Update Last Result in `evals.md`.
2. **Trace.** Write the trace to `<skill>/observability/traces/YYYY-MM-DD_HHMM_<slug>.json` and append one line to `<skill>/observability/invocation-log.jsonl`, per `trace-schema.md`, from the files in the round folder, never from memory.
3. **Verify.** Spawn the verification subagent; it sets `verified: true` or lists what is wrong. Fix and re-verify once.
4. **Deliver.** Present:
   - tickets filed (count by priority, key range) and comments posted;
   - the report and Sheet links;
   - input issues by owner, for Danny's Clinical Quality review;
   - the ledger's `held` rows: each item, why it's held and how many rounds it has waited, plus the rows whose counts moved this round (one-off to recurring, or to common);
   - open follow-ups, eval failures, unresolved QA findings and data gaps.

   Update the round's memory file and `MEMORY.md` with Edit. Offer the evals advisor in post-run mode.

## AMEND: change tickets already filed

Use when Danny asks for a change to tickets or comments this skill already filed, such as a label on every ticket or a wording fix across several. Round 3 example: adding `provider-labeling` to all 37 tickets after filing.

1. List the affected keys from `filing-ledger.md` and the exact change per key. Show Danny the list and wait for his go. His request alone is not approval of a list he hasn't seen.
2. A filing agent applies the change with the Jira edit tool, one key at a time, and appends each result to `filing-ledger.md` under "Amendments" (date, key, field, old value, new value).
3. Filing QA reads every changed key back with `view: full` or the changelog (the changelog for old values), and confirms each field the change touched (a status transition can also set or clear `resolution`). Record the request and result in `STATUS.md`.

A run that stops before Step 6 still appends a log line with `outcome` set to `partial` or `failure`, and a note on where it stopped.
</workflow>

<human_in_the_loop>
| Decision | Who | Where |
| --- | --- | --- |
| Round inputs and scope switches | Danny | Step 0 |
| An MCP read fails or the export is missing | Danny (the skill stops) | Any step |
| Plan, rules changes, Clinical, Legal and Eng questions | Danny | Gate 1 |
| Row extraction and draft-controlled vs input-issue calls | Agent, double-classified and QA'd | Step 2 |
| Extractor vs second-opinion disagreements | Danny (graduates; see below) | Gate 2 |
| Clustering and row mapping | Agent, script-enforced | Step 2c |
| Severity class, ledger matches | Agent at 2c, QA'd; Danny confirms | Step 2c, Gate 2 |
| Counts, band and filing call | Script, from the rubric; Danny confirms or moves file and hold | Gate 2 |
| No-counted-instance severe safety, held topics, hold-flag ledger matches | Danny | Gate 2 |
| P3 on an existing ticket below the floor | Danny approves the list; a filing agent applies it through Amend | Amend |
| Ledger rows and counts | Agent writes Evidence rows; script computes counts; filing QA checks | Step 4 item 6 |
| Dedup category | Agent, from full reads, QA'd; Won't Do matches and Regressions always shown | Step 2, Gate 2 |
| A reviewer ask that contradicts a ruling or clinical answer | Danny | Gate 2 |
| Decision items | Danny | Gate 2 |
| Consolidating redundant tickets | Agent, listed on the cards | Step 3 |
| Recommended priority | Agent, checked by blind scorers | Step 3 |
| Keep or drop, and final priority, per ticket | Danny, always | Gate 3 |
| First-ticket render check | Danny (graduates; see below) | Gate 4 |
| Filing the rest, comments, labels | Agent, verified by filing QA | Step 4 |
| Changes to tickets already filed | Danny approves the key list; agent applies, filing QA verifies | Amend |
| Report categories and judge mapping | Agent, QA'd; the report calls the mapping a hypothesis | Step 5 |
| Google push | Agent | Step 5 |
| Messages to other people | Danny sends; the skill only drafts | Any step |

**Graduation.** Second-opinion disagreements move to agent autonomous (the adjudicator's recommendation stands, listed at Gate 2 for information) after E3 passes in 2 consecutive rounds; any reversal on a clinical row moves it back. Gate 4 is skipped after E6 passes in 2 consecutive rounds; any change to `ticket-spec.md`, the body template or the Jira connector brings it back. Record graduations in the Version history below.
</human_in_the_loop>

<observability>
**Level:** Full. **Log:** `<skill>/observability/invocation-log.jsonl`. **Traces:** `<skill>/observability/traces/`, schema in `references/trace-schema.md`. Record MCP errors, stops, gates, subagent outputs and QA rounds as they happen, in `<round>/run-log.md`, so Step 6 compiles the trace from files. Write it only through `scripts/log_event.py` and check it with `scripts/log_check.py` (see `<hard_constraints>`). Step 0 starts the log with a `note` event (`text=session ${CLAUDE_SESSION_ID}`), then a `step_start` for Step 0. A resumed run appends to the same `run-log.md` and starts with a `note` event (`text=resumed from STATUS.md, session ${CLAUDE_SESSION_ID}`). E26 and E27 read these session IDs. Skill edits found mid-round get a `note` event and run in a separate session after the gate, never in the round thread. If a resumed round has no `run-log.md` (a round that started before v1.4), create it with a `note` event stating that earlier events are not recorded, then log from there; the trace for that round is `partial` and the log-dependent evals are NOT MEASURABLE.
</observability>

<iteration>
**Version:** 3.2 | **Built:** 2026-10-21, from Round 3 (Project-Galen/Phase-3/Discovery/Round-3-Failure-Modes/) and the Round 1.5 machinery it reused.

| Version | Date | Change | Reason |
| --- | --- | --- | --- |
| 1.0 | 2026-10-21 | First version. Lessons from Round 3 built in: consolidation before review; Draft and thread sections with names anonymized only; fixes around generation time are re-evals; no conflict-flag tickets by default; `provider-labeling` label; the seven-category Evals report. | Danny asked to turn the Round 3 session into a skill |
| 1.1 | 2026-11-03 | Session-only tickets: the title may end `(session YYYY-MM-DD)` instead of a trace; no Draft and thread section on such a ticket; `evidence_opener_session` and `extra_sources` in `round.json`; feedback-session sources run as extra batches with a session reference in the Trace ID column. Touched `check_tickets.py`, `add_threads.py`, `build_review_sheet.py`, `build_cluster_analysis.py`, `build_cluster.py` (a missing ledger no longer raises), `ticket-spec.md`, `ticket-qa-briefs.md`, `round-folder-layout.md`, `ledger-schema.md` (session Trace ID). Scripts count only `tr-` IDs as drafts. | Provider Pilot Round 1: Danny asked for failure modes from the feedback sessions too, and chose to change the title check |
| 1.2 | 2026-11-03 | Danny's priority scale (P0 severe safety, P1 minor safety or high-prevalence efficiency, P2 efficiency) added as `priority-rubric.md` section 0; every ticket carries a `safety` or `efficiency` label; draft records gain an `Approved priority` line (`ticket-spec.md`); a length ticket never asks for more concise generated text. Also in v1.1 work: `mechanical_check.py` gained CHECK 5 (every ledger row line must parse; a blank line inside a ledger table silently dropped rows). | Provider Pilot Round 1 Gate 3: Danny rewrote the priorities and asked for the labels, then said yes to updating the rubric |
| 1.3 | 2026-11-03 | `build_cluster_analysis.py`: reads the ticket plan's "Merged from" column so a merged failure mode's ratings attach to the absorbing ticket; the CSV `outcome` column follows the spec enum (ticket keys only in `failure_mode_tickets`; `decision D#` prints as `logged`; a held failure mode prints as `failure mode (held, no ticket)`); the action-type table groups batch codes by true action type. `cluster-report-spec.md` and `round-folder-layout.md`: the prose file carries `## 5. Caveats` between the two markers (the script never generated it); new `outcome` value. | Provider Pilot Round 1 Step 5 doc QA: 4 DEFECTs, all in the report build script |
| 1.4 | 2026-11-03 | Logging made enforceable: new `scripts/log_event.py` (the only writer of `run-log.md`; stamps UTC time, validates event types and required fields) and `scripts/log_check.py` (a gate checkpoint that fails when the log is missing, a line does not parse, or the round folder has changed more than 20 minutes after the last logged event). Two new `ALWAYS` rules; the observability paragraph says how a resumed or pre-1.4 round starts its log; `trace-schema.md` gains a `note` event; `round-folder-layout.md` lists `run-log.md`. | Provider Pilot Round 1 kept no `run-log.md` across five sessions, so Step 6 could not compile a trace from files |
| 1.5 | 2026-11-05 | Amend read-backs use `getJiraIssue` `view: full` or the changelog, and record `resolution` on every status change (`ticket-qa-briefs.md` sections 6 and 7, AMEND step 3). | Provider Pilot Round 1 Amend: the compact view omitted `resolution`, so the ledger logged it as unset while the Won't Do transitions had changed it on all four keys |
| 2.0 | 2026-11-05 | Any mix of sources in one round (`sources[]`: thumbs-downs, labeling, edits, evals, interviews, Slack), with per-kind provenance, coverage rules and extraction rules. One severity-and-frequency scale with a filing floor: one counted instance files only when it's severe safety, and audit findings never count. Counts, band and filing call per failure mode; a watch list carries held one-offs to the next round, seeded from legacy rounds. Gate 2, the ticket plan, rationales, blind scoring and review cards use the counts. Touched `priority-rubric.md`, `round-folder-layout.md`, `ledger-schema.md`, `rules-core.md`, `extraction-briefs.md`, `clustering-and-dedup.md`, `ticket-spec.md`, `ticket-qa-briefs.md`. On 2026-11-06: the cluster report shows counts by source, held one-offs and an evidence table. A failure mode dropped at Gate 3 leaves the watch list. Audit-only drafts are `inferred` rows only, and a legacy edit-diff row reads as a provider edit. Evals E23 to E25 check the floor, the watch list and the scale. | Danny's three rules (chat, 2026-11-05): analyze whatever sources are provided and report them together; one instance is not grounds for a ticket unless it's a significant safety issue; more common issues rank higher |
| 2.1 | 2026-11-06 | Token-efficiency pass. Non-reviewer subagents launch as the lean `pdfm-worker` type (`.claude/agents/pdfm-worker.md`), with an explicit tool list. No brief launches a subagent. The orchestrator offers a fresh resume session at Gates 1, 2 and 3, and skill edits leave the round thread. Dedup groups and dedup QA sets split by shared ticket. Part B goes back to the original second-opinion agent when it is still open. The format checker reuses a dedup QA read when a ticket hasn't changed. `check_tickets.py` gains `--traces` and `--threads`. The extraction briefs split into one file per role under `references/extraction/`, with rules 13, 14, 15 and 17 moved to `rules-core.md` section 8. Each anonymizer gets one `round.json` batch code. Evals E26 to E29 guard nesting, resume continuity, dedup QA coverage and format-checker key coverage. | Token-spend plan for this skill (`AI-Reference-Materials/Claude-Code-and-Skills/Token-Spend/skill-plans/provider-draft-failure-modes.md`), section 3 |
| 2.2 | 2026-11-10 | Priority levels in `priority-rubric.md` section 0: severe safety is P1 at one counted instance (was P0) and P0 at 2+; minor safety recurring is P2 (was P1); minor safety common stays P1. `build_cluster.py` `level()` matches. Filing floor unchanged: severe-safety one-offs still file. | Danny, chat, 2026-11-10: "minor safety issues that are recurring (2+) are P2s, while common stay P1s" and "severe safety issues that are one-offs are P1s" |
| 2.3 | 2026-11-10 | Evidence ledger replaces the per-round watch list. New `references/evidence-ledger.md` and `scripts/ledger_tool.py` (`check`, `write`, `prior`). Step 1 reads the ledger and writes `watch-list-prior.md` from its `held` rows with no subagent. Step 4 item 6 launches a ledger writer after filing QA. `build_cluster.py` writes no `watch-list.md` and matches prior drafts on `tr-` plus 8 hex characters. Two hard constraints: never edit a computed ledger cell by hand, never create a ticket at P3 (P3 is only for an existing ticket below the floor, after Danny approves the list). E24 reads the ledger; new E30 checks the ledger is consistent and covers every filed or commented key; new E31 fails a new ticket filed at P3. On 2026-11-10 `priority-rubric.md` gained the eval-only rule, the P3 rule and the ledger wording. Touched `SKILL.md`, `clustering-and-dedup.md`, `round-folder-layout.md`, `ticket-qa-briefs.md`, `cluster-report-spec.md`, `evals.md`, `build_cluster.py`, `run_evals.py`. | Danny, chat, 2026-11-10: wanted to see how many times each issue has appeared across rounds, and chose the ledger-replaces-watch-list default |
| 2.4 | 2026-11-11 | Gaps found in Provider Pilot Week 2 Step 3. `ticket-qa-briefs.md` gains ticket-drafter and comment-drafter templates (sections 8 to 10 now hold the drafter, anonymizer and format-checker templates, generalized from the round's briefs); a comment's claim about a target ticket needs a full live read and a verbatim quote, and an edit never uses the Rating form (`ticket-spec.md`). `make_thread_blocks.py` never cuts inside a URL or word. `make_blind.py` skips a batch with no draft file. New `Earlier round:` Evidence form: `check_tickets.py --traces` and `make_thread_blocks.py` read each `prior_rounds` export, and the block goes to `thread-blocks/EARLIER.md`. `counting.py` counts every `unresolved` reviewer as one provider. Docs: `step_end` outcomes, the `log_check.py` open-step warning. New evals E32 to E37 (E37 runs in a temp folder; E33 accepts a full read from any QA round); E12 also reads `names/*.txt`; `make_thread_blocks.py` deletes a stale `EARLIER.md`; the format-checker checks live only in `ticket-qa-briefs.md` section 10. Touched `SKILL.md`, `ticket-spec.md`, `ticket-qa-briefs.md`, `round-folder-layout.md`, `ledger-schema.md`, `priority-rubric.md`, `trace-schema.md`, `evals.md`, `counting.py`, `round_config.py`, `make_thread_blocks.py`, `make_blind.py`, `add_threads.py`, `check_tickets.py`, `build_cluster_analysis.py`, `run_evals.py`. | Danny, 2026-11-11: skill-gaps prompt from the Week 2 Gate 3 session (six gaps) |
| 3.0 | 2026-11-11 | The skill no longer checks every draft against its own checklist. Failure modes come from provider thumbs-downs and labeling, provider edits, failed eval judges, interviews and Slack. Coverage rule 3 and CHECK 3 are gone. Band `none` replaces `audit-only`. A severe-safety failure mode with zero counted instances goes to Gate 2. Legacy `inferred` and `audit` rows still read as not counted, and no script rewrites them. The Docebo extraction stays in the round's `clinical-rules.md`. Extractors do not read it. The rule recheck does. New eval E38. | Danny, chat, 2026-11-11. (1) Version 3.0. (2) Severe safety with zero counted instances still goes to Gate 2, as "no counted instance, severe safety". (3) Existing held rows that came only from the old checklist stay in the evidence ledger. (4) An input issue is still classified when an edit, a thumbs-down, an eval judge or Slack raises it. The agent does not search drafts for input issues no source raised. (5) The report key finding on checklist-only drafts rated GOOD is deleted. (6) The Docebo extraction stays in the round folder for later reference. Extractors skip that full copy. The rule recheck still reads it. |
| 3.1 | 2026-11-11 | Extractors read every section of `clinical-rules.md`, including the Docebo extraction in section 14, and still skip the full `docebo-*.md` copy. A Docebo row wins when it conflicts with a template, PRD, exemplar, or other-doc row. Losing rows are marked `superseded by CR-14.<n> (Docebo)`. New eval E39. | Danny, chat, 2026-11-11: extractors get section 14 again and still skip the full copy. The guideline beats a template or PRD row, with no ask to Clinical. [Assumption: rulings still sit above Docebo (needs validation)] |
| 3.2 | 2026-11-12 | A stale or conflicting chart fact the draft relies on is draft-controlled, not an input issue. `rules-core.md` section 1 gains "Chart facts the model saw" and drops "an implausible goal-weight field" from the input examples; rule 15 applies only to a value wrong at the source with nothing in context showing it; extractor rule 10 says a chart the export doesn't show never makes a row an input issue by itself. When the model may not have had the fact, the ticket's Layer is "chart or context input." | Danny, chat, 2026-11-12: repeating a chart fact that is no longer true, or asking the patient to confirm a highest weight that doesn't fit the gastric-bypass history on the same chart, is a draft mistake, not an input issue |
</iteration>

<final_reminder>
File only draft-controlled failure modes that clear the filing floor, only after Danny approves each row, only at his priority, and only once. Record one-offs as held ledger rows. Read every ticket in full before a dedup call. No real names, no session artifacts, no citing Danny outside this session. Stop on any failed read. One batch per agent. Scripts build the tables; QA subagents judge; you fix and record.
</final_reminder>
