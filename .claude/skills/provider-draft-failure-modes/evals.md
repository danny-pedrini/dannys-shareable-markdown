# Evals: provider-draft-failure-modes

Every eval runs at Step 6 against the final round folder, the Jira state recorded by filing QA, and the run trace. Code evals run as `python3 -I <skill>/scripts/run_evals.py` from the round folder; it prints one `E<n> PASS|FAIL|NOT MEASURABLE <detail>` line per eval (E1 to E39) and exits non-zero on any FAIL. E13 is the only judge eval; the orchestrator spawns it as a subagent.

"Bodies" means `bodies/*.md` (the filed descriptions). "Comments" means the comment bodies in `ticket-comments.md` for comments posted per `comment-ledger.md`. "Report prose" means `cluster_analysis_prose.md`. "Report" means the built report file named in `round.json`.

## Active Evals

| ID | Name | Type | Check | Added | Last Result |
|----|------|------|-------|-------|-------------|
| E1 | Export covers every rated trace | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E2 | Every ledger row maps once | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E3 | Second-opinion graduation signal | Generalization | Code | 2026-10-21 | Not measurable (Pilot Week 2: no Gate 2 answers section in the fixed format) |
| E4 | No merge requests at Gate 3 | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E5 | Priority disagreements flagged | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E6 | Render-check graduation signal | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E7 | No input issue filed | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E8 | Filed only what was approved, at the approved priority | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E9 | Filed once | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E10 | No filing over a covering ticket | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E11 | Every dedup call rests on a full read | Generalization | Code | 2026-10-21 | Fail (Pilot Week 2, 2026-11-11: dedup files carry no `Read:` lines in the fixed format) |
| E12 | Replaced names absent | Generalization | Code | 2026-10-21 | Not measurable (Pilot Week 2: no names file in the scratchpad) |
| E13 | No person name left in thread sections | Generalization | Judge | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11: 0 names in 8 bodies and 50 appendix entries) |
| E14 | No session artifacts | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11, after the draft comments file got QCARE-323 in place of its marker) |
| E15 | Danny and his docs not cited | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E16 | Stopped on every MCP failure | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E17 | No Regression without a pre-bound production deploy | Generalization | Code | 2026-10-21 | Fail (Pilot Week 2, 2026-11-11: two held Regression calls have no timing-table row with a pre-bound production deploy) |
| E18 | Report counts match the data | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E19 | Body length within Jira's limit | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E20 | Writing checklist | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E21 | No conflict-flag ticket while the scope is off | Generalization | Code | 2026-10-21 | Pass (Pilot Week 2, 2026-11-11) |
| E22 | Report categories and judges are valid | Generalization | Code | 2026-10-21 | Fail (Pilot Week 2, 2026-11-11: a comma inside a judge's parenthetical splits it, so "partly)" is not found) |
| E23 | Filing floor | Generalization | Code | 2026-11-06 | Pass (Pilot Week 2, 2026-11-11) |
| E24 | Held one-offs recorded | Generalization | Code | 2026-11-06 | Fail (Pilot Week 2, 2026-11-11: 19 held failure modes covered by an existing ticket sit on that ticket's row, not a `held` row) |
| E25 | Recommendation follows the scale | Generalization | Code | 2026-11-06 | Pass (Pilot Week 2, 2026-11-11) |
| E26 | No nested subagents | Generalization | Code | 2026-11-06 | Fail (Pilot Week 2, 2026-11-11: one local-grader agent in an earlier session has spawn depth 2) |
| E27 | Resume continuity | Generalization | Code | 2026-11-06 | Pass (Pilot Week 2, 2026-11-11) |
| E28 | Dedup QA reread coverage | Generalization | Code | 2026-11-06 | Fail (Pilot Week 2, 2026-11-11: keys cited in the dedup verdicts have no row in a dedup QA "Tickets read" table) |
| E29 | Format checker key coverage | Generalization | Code | 2026-11-06 | Fail (Pilot Week 2, 2026-11-11: two cited keys are missing from "Jira keys verified") |
| E30 | Evidence ledger consistent and complete | Generalization | Code | 2026-11-10 | Pass (Pilot Week 2, 2026-11-11) |
| E31 | No new ticket filed at P3 | Generalization | Code | 2026-11-10 | Pass (Pilot Week 2, 2026-11-11) |
| E32 | Thread blocks never split a URL or a word | Generalization | Code | 2026-11-11 | Pass (Pilot Week 2, 2026-11-11) |
| E33 | Every comment target read in full | Generalization | Code | 2026-11-11 | Pass (Pilot Week 2, 2026-11-11) |
| E34 | Edit evidence never uses the Rating form | Generalization | Code | 2026-11-11 | Pass (Pilot Week 2, 2026-11-11) |
| E35 | Every cited trace resolves and has its thread block | Generalization | Code | 2026-11-11 | Pass (Pilot Week 2, 2026-11-11) |
| E36 | Unresolved reviewers count as one provider | Generalization | Code | 2026-11-11 | Pass (Pilot Week 2, 2026-11-11) |
| E37 | Blind file builds with no draft file for most batches | Generalization | Code | 2026-11-11 | Pass (Pilot Week 2, 2026-11-11) |
| E38 | No new checklist rows | Generalization | Code | 2026-11-11 | Not measurable on a round built before v3.0 |
| E39 | Superseded rules never cited | Generalization | Code | 2026-11-11 | Not measurable (Pilot Week 2, 2026-11-11: no Status contains `superseded by`) |

## Definitions

### E1: Export covers every rated trace

**Pass:** `check_export.py` exits 0: every trace in `ratings.md` has one record in `export/<batch>.md`, and where the sheet carries a draft column, each export draft matches it.
**Fail:** any rated trace without a record, or any draft mismatch.
**Check type:** Code-based

```check
Type: comparison
Source field: trace IDs in ratings.md
Target field: trace headers in export/*.md
Logic: run check_export.py; FAIL on non-zero exit, detail = its first 5 error lines.
```

**Source:** evals advisor, design time (handoff integrity, D4 failure mode 7). **Added:** 2026-10-21

### E2: Every ledger row maps once

**Pass:** `mechanical_check.py` and `build_cluster.py` both exit 0 on the final folder.
**Fail:** an unmapped or double-mapped row, a rating with text and no reviewer row, or an input-issue row with no input named. Per source kind, it also fails on an edited draft with no edit row, a failed judge verdict with no judge row, or a Slack-reported trace with no `slack` row. It fails when an evals or Slack source file isn't found (`mechanical_check.py` CHECK 6 to 9). The detail names each failing check.
**Check type:** Code-based

```check
Type: structural
Source field: ratings.md rows; ledger/*.md rows; the round's edits, evals and Slack sources
Target field: cluster_defs.py destinations
Logic: run both scripts; FAIL on either non-zero exit.
```

**Source:** evals advisor, design time (D4 failure mode 7). **Added:** 2026-10-21

### E3: Second-opinion graduation signal

**Pass:** every Gate 2 answer on a second-opinion disagreement, as recorded in `STATUS.md` under "Gate 2 answers", matches the adjudicator's recommendation for that row.
**Fail:** any answer that reverses the recommendation.
**Check type:** Code-based

```check
Type: comparison
Source field: "Recommendation:" per row in ledger/qa/*-second-opinion-diff.md
Target field: "Gate 2 answers" rows in STATUS.md (format "<row>: <ledger|second opinion|other> (<Danny's words>)")
Logic: FAIL for each row whose answer differs from the recommendation. NOT MEASURABLE if no disagreements existed.
```

**Source:** evals advisor, design time (Graduate item). **Added:** 2026-10-21
**Notes:** passing in 2 consecutive rounds graduates the disagreement decision to agent autonomous (SKILL.md human-in-the-loop table).

### E4: No merge requests at Gate 3

**Pass:** `STATUS.md` "Gate 3 record" lists no merge requested by Danny.
**Fail:** one or more merges requested at Gate 3.
**Check type:** Code-based

```check
Type: presence
Source field: STATUS.md "Gate 3 record" section
Target field: lines starting "Merge requested:"
Logic: FAIL if any such line exists; detail = the count.
```

**Source:** evals advisor, design time (autonomous consolidation step). **Added:** 2026-10-21

### E5: Priority disagreements flagged

**Pass:** in the `ticket-drafts.md` approval table, every row whose clinical or provider blind score differs from the recommended priority has `yes` in the Disagreement column, and all such rows come before the agreed rows.
**Fail:** an unflagged disagreement, or a flagged row below an agreed row.
**Check type:** Code-based

```check
Type: structural
Source field: approval table columns Recommended, Clinical blind, Provider blind, Disagreement
Target field: same table
Logic: parse the table; check flags and ordering.
```

**Source:** evals advisor, design time (autonomous recommendation step). **Added:** 2026-10-21

### E6: Render-check graduation signal

**Pass:** `STATUS.md` "Gate 4 record" says `Render: OK`.
**Fail:** it records a render issue.
**Check type:** Code-based

```check
Type: presence
Source field: STATUS.md "Gate 4 record"
Target field: line "Render: OK" or "Render: issue (<what>)"
Logic: FAIL on "Render: issue". NOT MEASURABLE if Gate 4 was skipped after graduation.
```

**Source:** evals advisor, design time (Graduate item). **Added:** 2026-10-21
**Notes:** passing in 2 consecutive rounds graduates Gate 4.

### E7: No input issue filed

**Pass:** every filed key maps through a `STATUS` entry ending "Filed: <key>" in `cluster_defs.py` to a failure mode with at least one `draft-controlled` row in `row-map.md`.
**Fail:** a filed key maps to an FM whose rows are all `input-issue`, or to no FM.
**Check type:** Code-based

```check
Type: comparison
Source field: keys in filing-ledger.md
Target field: cluster_defs.STATUS, row-map.md Classification column
Logic: for each key, find FMs whose STATUS contains "Filed: <key>"; FAIL if none, or if none of their rows is draft-controlled.
```

**Source:** evals advisor, design time (D4 failure mode 1). **Added:** 2026-10-21

### E8: Filed only what was approved, at the approved priority

**Pass:** every key in `filing-ledger.md` traces to a card in `ticket-review.md` whose call line reads `Your call: keep <P>`, and the priority filing QA read from Jira equals that P.
**Fail:** a filed key with no keep card, a card marked drop, or a priority mismatch.
**Check type:** Code-based

```check
Type: comparison
Source field: ticket-review.md "Your call:" lines (keep P0|P1|P2, or drop (reason))
Target field: filing-ledger.md Draft, Key and Priority columns
Logic: join on draft ID; FAIL per mismatch.
```

**Source:** evals advisor, design time (D4 failure mode 2). **Added:** 2026-10-21

### E9: Filed once

**Pass:** the final epic-wide JQL recorded in `qa-step4.md` returned exactly as many issues created by this run as `filing-ledger.md` has rows, with no two sharing a summary.
**Fail:** a count mismatch or a duplicate summary.
**Check type:** Code-based

```check
Type: comparison
Source field: qa-step4.md line "Epic query: <n> issues, <d> duplicate summaries"
Target field: filing-ledger.md row count
Logic: FAIL if n differs from the row count or d > 0.
```

**Source:** evals advisor, design time (D4 failure mode 2). **Added:** 2026-10-21

### E10: No filing over a covering ticket

**Pass:** every filed FM's final category in `dedup-verdicts.md` is New or Regression.
**Fail:** a filed FM whose category is Covered by open ticket, Recurrence, Done after generation or Won't Do match.
**Check type:** Code-based

```check
Type: comparison
Source field: filed FMs (via cluster_defs.STATUS "Filed:")
Target field: dedup-verdicts.md final-verdict table, Category column
Logic: FAIL per filed FM with another category.
```

**Source:** evals advisor, design time (D4 failure mode 3). **Added:** 2026-10-21
**Notes:** trusts the dedup verdict itself; dedup QA catches a wrong verdict.

### E11: Every dedup call rests on a full read

**Pass:** every Jira key named in `dedup-verdicts.md` has a line in `dedup/*.md` of the form `Read: <key> · description yes · comments <n> · Development <state> · <UTC time>`.
**Fail:** any named key without one.
**Check type:** Code-based

```check
Type: comparison
Source field: Jira keys in dedup-verdicts.md (regex [A-Z]+-\d+)
Target field: "Read:" lines in dedup/*.md
Logic: FAIL per key with no Read line or with "description no".
```

**Source:** evals advisor, design time (D4 failure mode 4). **Added:** 2026-10-21

### E12: Replaced names absent

**Pass:** no entry in the session-scratchpad `names-replaced.txt` or `names/*.txt` appears, case-insensitive and whole word, in bodies, comments, the report or the CSV.
**Fail:** any hit.
**Check type:** Code-based

```check
Type: absence
Source field: <scratchpad>/names-replaced.txt and <scratchpad>/names/*.txt (one name per line; never in the repo)
Target field: bodies/*.md, comment bodies, report, CSV
Logic: whole-word case-insensitive search; FAIL per hit with file and line. NOT MEASURABLE if the scratchpad file is gone (new session); say so.
```

**Source:** evals advisor, design time (D4 failure mode 5). **Added:** 2026-10-21

### E13: No person name left in thread sections

**Pass:** each "Draft and thread" section in the bodies, and each trace entry in the report appendix, names people only by placeholders.
**Fail:** any real first or last name of a patient, provider, staff member or family member remains.
**Check type:** LLM judge

```judge
Criterion: Does this text contain a real person's name rather than a placeholder?
Pass definition: every person is referred to by a placeholder such as [PATIENT_NAME], [PROVIDER_NAME] or {{provider_intro}}, or by role.
Fail definition: any real first or last name of a person remains; quote it.
Examples: add from your own runs; do not fabricate.
```

**Source:** evals advisor, design time (D4 failure mode 5; code only knows names the anonymizer caught). **Added:** 2026-10-21
**Notes:** medication, product and pharmacy names are not person names. Reviewer handles are allowed.

### E14: No session artifacts

**Pass:** bodies, comments and report prose contain no match for `\b(FM|T|C|D)-\d+\b`, `\b(<batch codes from round.json>)-\d{3}\b`, `\bCR-[R\d]`, `cluster_defs`, `ledger/`, or a file name ending `.md` or `.py`.
**Fail:** any match.
**Check type:** Code-based

```check
Type: absence
Source field: round.json batch codes
Target field: bodies, comments, report prose, report
Logic: regex search; FAIL per hit with file and line. Jira keys and trace IDs are allowed.
```

**Source:** evals advisor, design time (D4 failure mode 6). **Added:** 2026-10-21

### E15: Danny and his docs not cited

**Pass:** bodies, comments and the report contain no "Danny", "Pedrini" or link to the Few-Shot Exemplar Library, and never cite the handle `dpedrini` as the source of a rule or decision. The handle may appear wherever reviewers are named.
**Fail:** any of those hits.
**Check type:** Code-based

```check
Type: absence
Source field: none
Target field: bodies, comments, report
Logic: search "Danny|Pedrini|Few-Shot Exemplar Library|3428646928"; and "dpedrini" cited as a source ("per dpedrini", "dpedrini ruled/decided/approved", "dpedrini's ruling/call"). FAIL per hit.
```

**Source:** evals advisor, design time (D4 failure mode 6). **Added:** 2026-10-21

### E16: Stopped on every MCP failure

**Pass:** every `mcp_errors` entry in the run trace is followed by a `stops` entry for the same step before any later step's first event, or by a logged successful retry of the same read.
**Fail:** a step advanced after an unrecovered MCP error.
**Check type:** Code-based

```check
Type: structural
Source field: trace mcp_errors[] (ts, step, server, tool, resource, error, recovered)
Target field: trace stops[] and steps[] timestamps
Logic: for each error with recovered false, FAIL unless a stop for that step precedes the next step's start.
```

**Source:** evals advisor, design time (D4 failure mode 11). **Added:** 2026-10-21

### E17: No Regression without a pre-bound production deploy

**Pass:** every FM whose dedup category is Regression has a row in the `generation-provenance.md` timing table with a production deploy before the bound and a merge before the generation window start in `round.json`.
**Fail:** any Regression missing either.
**Check type:** Code-based

```check
Type: comparison
Source field: dedup-verdicts.md Regression rows
Target field: generation-provenance.md timing table (Key, PR, Merged UTC, Prod deploy UTC, Category)
Logic: FAIL per Regression without a prod deploy before generation_bound_utc or with a merge at or after generation_window_start_utc.
```

**Source:** evals advisor, design time (D4 failure mode 8). **Added:** 2026-10-21

### E18: Report counts match the data

**Pass:** every filed key appears in the report. CSV rows with a label ID equal the `ratings.md` rating rows, and the CSV has one row per evidence-table row (section 7). The trace table lists each trace once, covering every rated trace and every trace with a counted row on a failure mode in `row-map.md`. Spread rows are exempt, since the table lists them only when they back a ticket.
**Fail:** any mismatch. A report with no evidence table, or a `row-map.md` with no Counted column (both built before skill v2.0), skips that part and says so in the detail.
**Check type:** Code-based

```check
Type: comparison
Source field: filing-ledger.md, ratings.md, row-map.md Counted column
Target field: report trace table and evidence table, CSV
Logic: recount from the built files; FAIL per mismatch.
```

**Source:** evals advisor, design time (D4 failure mode 9). **Added:** 2026-10-21

### E19: Body length within Jira's limit

**Pass:** every `bodies/*.md` is under 32,000 characters, and `qa-step4.md` found each body's last heading in Jira.
**Fail:** a body at or over the limit, or a truncated description.
**Check type:** Code-based

```check
Type: structural
Source field: bodies/*.md
Target field: qa-step4.md check "Description not truncated"
Logic: len(text) < 32000 per file; FAIL per file over, and if the truncation check is below 100%.
```

**Source:** evals advisor, design time (D4 failure mode 10). **Added:** 2026-10-21

### E20: Writing checklist

**Pass:** no hit from the hard verification searches in `forbidden-writing-patterns.md`, the plain-word and filler lists in `CLAUDE.md`, or an em dash, in bodies, comments and report prose.
**Fail:** any hit.
**Check type:** Code-based

```check
Type: absence
Source field: forbidden-writing-patterns.md hard searches; CLAUDE.md plain-word and filler lists
Target field: bodies, comments, report prose
Logic: check_tickets.py --writing over those files; FAIL per hit. Quoted draft and reviewer text inside Draft and thread sections and quote marks is exempt.
```

**Source:** evals advisor, design time (D4 failure mode 10). **Added:** 2026-10-21

### E21: No conflict-flag ticket while the scope is off

**Pass:** when `round.json` has `scope.conflict_flags_in_scope` false, no filed FM has `kind="conflict-flag"` in `cluster_defs.py`.
**Fail:** one does.
**Check type:** Code-based

```check
Type: absence
Source field: round.json scope; cluster_defs.FM kind
Target field: filed FMs
Logic: FAIL per filed FM with kind conflict-flag while the scope is off.
```

**Source:** evals advisor, design time (D4 failure mode 12). **Added:** 2026-10-21

### E22: Report categories and judges are valid

**Pass:** every unit in `report_defs.py` has a primary category from the seven in `references/cluster-report-spec.md`, an empty or valid secondary, and judges that each appear in the judge doc named in `round.json`, or "none dedicated" or "none confirmed" (the two values the spec allows when no judge fits).
**Fail:** any other value.
**Check type:** Code-based

```check
Type: pattern
Source field: cluster-report-spec.md category list; judge doc judge names
Target field: report_defs.py units
Logic: FAIL per invalid value.
```

**Source:** evals advisor, design time (autonomous Step 5 categorization). **Added:** 2026-10-21

### E23: Filing floor

**Pass:** every filed Bug has 2+ counted instances, or is severe safety with one, or has a Gate 2 `file` entry in `cluster_defs.CALL`. It reads the severity class, not the filed priority, since Danny can lower a P0 at Gate 3. That entry is Danny's go. A severe-safety failure mode with zero counted instances needs it (`priority-rubric.md` section 0). Decision items are exempt, since the floor doesn't apply to them.
**Fail:** a filed Bug below the floor with no Gate 2 `file` entry.
**Check type:** Code-based

```check
Type: comparison
Source field: filing-ledger.md Draft; ticket-plan.md FM; cluster_defs.CALL
Target field: failure-modes.md section 1 Counted instances and Severity class
Logic: join each filed draft to its plan FM; FAIL per ticket below the floor. NOT MEASURABLE when failure-modes.md has no filing calls (built before skill v2.0).
```

**Source:** Danny's failure-mode rules, 2026-11-05, in `Project-Galen/Phase-3/Launch/Failure-Mode-Rules-Skill-Fix-Handoff.md` (one-offs filed in Round 1). **Added:** 2026-11-06

### E24: Held one-offs recorded

**Pass:** every failure mode whose filing call is `hold` is a `held` row in the evidence ledger, found by the working key `<round slug>/<FM id>` in the row's Note. A failure mode the product owner dropped at Gate 3 is exempt. An evidence comment is optional.
**Fail:** a held failure mode with no `held` ledger row carrying its working key.
**Check type:** Code-based

```check
Type: comparison
Source field: failure-modes.md section 1 Filing call; the Gate 3 drops in ticket-drafts.md
Target field: the evidence ledger's Summary Status and Notes Note
Logic: FAIL per held failure mode with no `held` ledger row whose Note carries its working key. NOT MEASURABLE when failure-modes.md has no filing calls, or the ledger is missing.
```

**Source:** Danny's failure-mode rules, 2026-11-05, in `Project-Galen/Phase-3/Launch/Failure-Mode-Rules-Skill-Fix-Handoff.md`. **Added:** 2026-11-06 **Changed:** 2026-11-10, from `watch-list.md` to the evidence ledger (skill v2.3)

### E25: Recommendation follows the scale

**Pass:** each `ticket-plan.md` recommended priority equals the rubric level `build_cluster.py` gives its failure mode from the severity class and band. Danny's Gate 3 call can still differ, so E25 reads the plan, not the filed priority. Decision items are exempt.
**Fail:** a plan row whose recommendation differs from the scale.
**Check type:** Code-based

```check
Type: comparison
Source field: ticket-plan.md Recommended priority
Target field: failure-modes.md section 1 Level (rubric)
Logic: FAIL per mismatch; the detail lists rows whose failure mode has no level. NOT MEASURABLE when no row has a level.
```

**Source:** Danny's failure-mode rules, 2026-11-05, in `Project-Galen/Phase-3/Launch/Failure-Mode-Rules-Skill-Fix-Handoff.md`. **Added:** 2026-11-06

### E26: No nested subagents

**Pass:** no subagent in any of the run's sessions has `spawnDepth` above 1. The session IDs come from the `note` events in `run-log.md` that name a session.
**Fail:** any subagent `.meta.json` with `spawnDepth` 2 or more.
**Check type:** Code-based

```check
Type: structural
Source field: run-log.md note events with "session <id>"
Target field: ~/.claude/projects/*/<session id>/subagents/*.meta.json spawnDepth
Logic: FAIL per subagent with spawnDepth > 1; detail names the session, file and agent type. NOT MEASURABLE when no note names a session, or no metadata is found for them.
```

**Source:** token-efficiency plan, changes 1 and 2 (`AI-Reference-Materials/Claude-Code-and-Skills/Token-Spend/skill-plans/provider-draft-failure-modes.md`). **Added:** 2026-11-06
**Notes:** the plan proposed this as E23; it is E26 because E23 to E25 were already taken.

### E27: Resume continuity

**Pass:** every session after the first opens with a `note` event that says `resumed from STATUS.md` and names the session. A gate whose `STATUS.md` section ("Gate 2 answers" or "Gate 3 record") holds any line has at least one `gate_answered` event for that gate in `run-log.md`.
**Fail:** a later session whose first note lacks the resume text, or a recorded gate with no `gate_answered` event.
**Check type:** Code-based

```check
Type: comparison
Source field: run-log.md note events with "session <id>"; STATUS.md "Gate 2 answers" and "Gate 3 record"
Target field: run-log.md gate_answered events
Logic: FAIL per later session without the resume text, and per recorded gate with no gate_answered. NOT MEASURABLE when no note names a session.
```

**Source:** token-efficiency plan, change 3. **Added:** 2026-11-06
**Notes:** the plan proposed this as E24. It matches gate answers per gate, not per decision line, because `STATUS.md` decisions carry no event ID.

### E28: Dedup QA reread coverage

**Pass:** every Jira key in `dedup-verdicts.md` has a row in the "Tickets read" table of some `dedup-qa-*.md`.
**Fail:** a cited key no dedup QA agent reread.
**Check type:** Code-based

```check
Type: comparison
Source field: Jira keys in dedup-verdicts.md (session-artifact IDs excluded)
Target field: Key column of every "Tickets read" table in dedup-qa-*.md
Logic: FAIL per key with no row. NOT MEASURABLE when either file is missing.
```

**Source:** token-efficiency plan, change 5; guards the dedup QA's independent reread (`references/clustering-and-dedup.md` section 13). **Added:** 2026-11-06
**Notes:** the plan proposed this as E25.

### E29: Format checker key coverage

**Pass:** every Jira key in `ticket-drafts.md` and `ticket-comments.md` has a row in the "Jira keys verified" table of a `qa-step3-format*.md`, with Method `full read` or `scope cell (<dedup-qa file>)`.
**Fail:** a key with no row, or a row with any other method.
**Check type:** Code-based

```check
Type: comparison
Source field: Jira keys in ticket-drafts.md and ticket-comments.md (session-artifact IDs excluded)
Target field: "Jira keys verified" table, Key and Method columns
Logic: FAIL per missing key or invalid method. NOT MEASURABLE when no such table exists (built before skill v2.1).
```

**Source:** token-efficiency plan, change 7. **Added:** 2026-11-06
**Notes:** the plan proposed this as E26.

### E30: Evidence ledger consistent and complete

**Pass:** `ledger_tool.py check` exits 0 on the evidence ledger, and every ticket key in `filing-ledger.md` (rows `T-n`) and every target in `comment-ledger.md` (rows `C-n`) has a Summary row in the ledger.
**Fail:** a computed cell is stale, an Evidence row is malformed, or a filed or commented key has no ledger row.
**Check type:** Code-based

```check
Type: comparison
Source field: filing-ledger.md Key; comment-ledger.md Target
Target field: the evidence ledger's Summary Ticket column; ledger_tool.py check exit code
Logic: FAIL when check exits non-zero, and per filed or commented key with no ledger row. NOT MEASURABLE when the ledger, filing-ledger.md and comment-ledger.md are all missing.
```

**Source:** Danny, chat, 2026-11-10: one ledger counts every failure mode across rounds. **Added:** 2026-11-10
**Notes:** a round whose ledger update has not run yet fails this eval on purpose; Step 4 item 6 is what clears it.

### E31: No new ticket filed at P3

**Pass:** no row of `filing-ledger.md` (rows `T-n`) has a Priority that starts with P3.
**Fail:** a new ticket filed at P3. P3 is only for an existing ticket below the filing floor, after Danny approves the list (`priority-rubric.md` section 1).
**Check type:** Code-based

```check
Type: comparison
Source field: filing-ledger.md Priority, rows T-n
Target field: none (the value must not start with P3)
Logic: FAIL per filed ticket whose Priority starts with P3. NOT MEASURABLE when filing-ledger.md is missing or has no T-n rows. Amendments (moves of existing tickets to P3) are not T-n rows and are exempt.
```

**Source:** Danny, chat, 2026-11-10: never create a new ticket as P3; P3 only for an existing ticket below the floor. **Added:** 2026-11-10

### E32: Thread blocks never split a URL or a word

**Pass:** in every block of `thread-blocks/*.md`, each URL in the export record's messages and draft sits whole on one line. Also, no two adjacent quote lines of one message or draft join into a single token of the source text (that would be a line ending mid-word or mid-URL).
**Fail:** a URL cut across lines, or a pair of lines whose last and first tokens, joined with no space, form a token the export holds.
**Check type:** Code-based

```check
Type: comparison
Source field: the messages before the draft and the draft in the export record (this round's export/*.md, or a prior_rounds export for an Earlier round: trace)
Target field: the blockquote lines of each block in thread-blocks/*.md
Logic: FAIL per URL not found whole on one block line, and per adjacent quote-line pair whose alphanumeric boundary characters join into a source token. NOT MEASURABLE when thread-blocks/ has no file.
```

**Source:** Provider Pilot Week 2 Step 3: `make_thread_blocks.py` cut 6 URLs and one product name across lines, and the orchestrator rejoined them by hand. **Added:** 2026-11-11
**Notes:** the check reads the anonymized blocks, so a name replaced inside a token is not compared. An eval that passes here says the heuristic and the anonymizer both left every URL and word whole.

### E33: Every comment target read in full

**Pass:** every ticket a comment in `ticket-comments.md` targets (`### C-<n>. Comment on <key>`) has a row with Method `full read` in the format checker's "Jira keys verified" table, in any `qa-step3-format*.md` round.
**Fail:** a comment target with no `full read` row in any round (only `scope cell (...)` rows, or none).
**Check type:** Code-based

```check
Type: comparison
Source field: the key in each "### C-<n>. Comment on <key>" heading of ticket-comments.md
Target field: "Jira keys verified" table, Key and Method columns, in qa-step3-format*.md
Logic: FAIL per target key whose Method does not start with "full read". NOT MEASURABLE when no ticket-comments.md, no qa-step3-format*.md, or no such table.
```

**Source:** Provider Pilot Week 2: two comment drafts misdescribed their target tickets (one said a ticket asked for consent when it never did; one said two golden cases agreed when they contradicted each other), and the format checker's full read of each target caught both. **Added:** 2026-11-11
**Notes:** E29 accepts a scope cell for a key named in a ticket's Related line. A comment makes a claim about the target's own text, so only a full read counts.

### E34: Edit evidence never uses the Rating form

**Pass:** every Evidence bullet in `ticket-drafts.md` and `ticket-comments.md` that uses the Rating form (`tr-... (<action>). <handle> (GOOD|BAD): "..."`) names a handle that left a rating on that trace in `ratings.md`.
**Fail:** a Rating-form bullet whose handle left no rating on the trace (the trace was only edited).
**Check type:** Code-based

```check
Type: comparison
Source field: Rating-form bullets (trace ID, handle) in ticket-drafts.md and ticket-comments.md
Target field: ratings.md rating rows (trace, reviewer handle from the Rating ref)
Logic: FAIL per Rating-form bullet whose (trace, handle) has no rating row. NOT MEASURABLE when ratings.md or both draft files are missing.
```

**Source:** Provider Pilot Week 2 Step 3: one ticket and one comment wrote a provider's edit in the Rating form, and the format checker caught both. **Added:** 2026-11-11

### E35: Every cited trace resolves and has its thread block

**Pass:** `check_tickets.py --traces` passes on `ticket-drafts.md` and `ticket-comments.md` (a trace on an `Earlier round:` bullet is in a `prior_rounds` export; any other trace is in this round's export), and `--threads` passes on `ticket-drafts.md` (one thread subheading per Evidence trace, an Earlier-round trace included).
**Fail:** either script exits non-zero. The detail names the first problems.
**Check type:** Code-based

```check
Type: structural
Source field: tr- IDs in ticket-drafts.md and ticket-comments.md; round.json prior_rounds
Target field: export/*.md and each prior round's export/*.md; the Draft and thread sections
Logic: run check_tickets.py --traces and --threads; FAIL on a non-zero exit. NOT MEASURABLE when ticket-drafts.md is missing.
```

**Source:** Provider Pilot Week 2: a ticket counted a draft from the Provider Pilot Round 1 edits pass, but `--traces` read only this round's export, so its ID stayed out of the ticket. **Added:** 2026-11-11

### E36: Unresolved reviewers count as one provider

**Pass:** in `failure-modes.md`, no Counts line lists an `unresolved:tr-...` handle, and `unresolved` appears at most once per failure mode. Each Summary row's Providers number also equals the length of that failure mode's list. `sender_n` and `provider_n` handles count as written, and an unmatched interview session handle (`unresolved:<handle>`) stays its own provider.
**Fail:** an `unresolved:tr-...` handle, `unresolved` listed twice, or a Providers number that differs from the list.
**Check type:** Code-based

```check
Type: structural
Source field: the "providers:" list in each failure mode's Counts line
Target field: the Providers column of failure-modes.md section 1
Logic: FAIL per failure mode with an unresolved:<id> handle or a count that differs from its list. NOT MEASURABLE when failure-modes.md has no Counts lines.
```

**Source:** Provider Pilot Week 2 Gate 2 (STATUS decision 13e): the scripts gave one ticket 5 providers because each unresolved edit row counted as its own person. **Added:** 2026-11-11
**Notes:** a failure-modes.md built before skill v2.4 fails this eval until `build_cluster.py` reruns.

### E37: Blind file builds with no draft file for most batches

**Pass:** `make_blind.py` exits 0 in a temp folder that holds `round.json` and one `ticket-drafts-<code>.md` with a ticket, so every other batch code has no file.
**Fail:** a non-zero exit.
**Check type:** Code-based

```check
Type: structural
Source field: the first ticket-drafts-<code>.md that holds a ticket
Target field: make_blind.py exit code
Logic: copy round.json and that one file to a temp folder, run make_blind.py there (the round's own ticket-drafts-blind.md is untouched); FAIL on non-zero exit. NOT MEASURABLE when no ticket-drafts-<code>.md holds a ticket.
```

**Source:** Provider Pilot Week 2: `make_blind.py` exited 1 for any batch code without a draft file, and most batches never get a ticket, so the orchestrator wrote 18 empty stub files. **Added:** 2026-11-11

### E38: No new checklist rows

**Pass:** no ledger row has Evidence basis `inferred` or Reviewer `audit`, and no `failure-modes.md` row has band `audit-only`.
**Fail:** a round at v3.0 or later still has one of those.
**Check type:** Code-based

```check
Type: absence
Source field: ledger/*.md Evidence basis and Reviewer; failure-modes.md Band
Target field: none
Logic: FAIL on Evidence basis inferred, Reviewer audit, or band audit-only. NOT MEASURABLE when the ledger still contains the pre-v3.0 phrase "audited, no issue found" or a legacy edits-pass row (Provenance inferred, Evidence basis provider-edit, Reviewer audit).
```

**Source:** Danny, chat, 2026-11-11: failure modes come from provider feedback, edits and eval runs. The skill no longer checks every draft against its own checklist. **Added:** 2026-11-11
**Notes:** Week 2 is the calibration case. Its ledger still holds checklist rows from the round that shipped them, so this eval does not score that folder. A later round that writes one fails.

### E39: Superseded rules never cited

**Pass:** no ledger Expected-behavior cell cites a `CR-` ID whose Status in `clinical-rules.md` contains `superseded by`.
**Fail:** a cell cites one of those IDs.
**Check type:** Code-based

```check
Type: absence
Source field: Expected behavior + guidance source in ledger/*.md
Target field: clinical-rules.md rows whose Status contains `superseded by`
Logic: FAIL when an Expected-behavior cell cites one of those IDs. NOT MEASURABLE when no row has that status, which covers a round built before v3.1.
```

**Source:** Danny, chat, 2026-11-11: extractors read section 14 again, and a Docebo row wins over a template, PRD, exemplar, or other-doc row. **Added:** 2026-11-11
**Notes:** Week 2 is the calibration example. Its open conflicts are CR-1.17 with CR-14.3, CR-1.21 with CR-14.9, and CR-6.7 with CR-14.45. No row has Status `superseded by`, so this eval does not score that folder.
