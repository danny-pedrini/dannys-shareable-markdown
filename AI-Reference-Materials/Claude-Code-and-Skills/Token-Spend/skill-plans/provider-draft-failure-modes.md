# provider-draft-failure-modes: token-efficiency plan

## 1. Answer

Nine changes would cut **$44.47 per future run**, and the same over the window, since the window held one run.

That net removes $0.86 counted in both change 1 and changes 6 and 10 [Assumption: that is the tool-list share of those five agents (needs validation)], and it drops change 9. The $17.49 lean worker type is untested and should be validated first. Without it the total is $27.84.

The top three:

| Rank | Change | Per future run | Window |
| --- | --- | --- | --- |
| 1 | Lean worker agent type with an explicit tool list for every non-reviewer subagent | $17.49 [Assumption: an explicit `tools:` list removes about 29,400 tokens of skill, agent and deferred-tool listings per agent (needs validation)] | $17.49 |
| 2 | No nested subagents: dedup, dedup QA, provenance and adjudicator agents do their own reads | $13.81 | $13.81 |
| 3 | Fresh orchestrator session at Gates 1, 2 and 3, resuming from `STATUS.md` | $8.82 | $8.82 |

These figures cover Steps 0 through 3 only. Steps 4, 5 and 6 of this round ran in sessions `ad11bf5f` and `bed14ed4`, which start after 2 Nov 2026 and were not measured.

I do not recommend the earlier report's top change as written. Having the dedup QA read the dedup agent's saved extract would remove the QA's independent reread, which `clustering-and-dedup.md` section 13 requires ("Do not trust the write-up"). Its $7.19 saving also rested on a reopen cost I could not reproduce (section 2).

## 2. Measured baseline

**Attributed dollars.** $167.05 across 3 single-skill sessions: `e70f0f05` $166.69 (logged), `4fcb4562` $0.36 (two parent requests, no subagents), `64a86f6e` $0.00 (no requests). No session using this skill was mixed, so there are no segmented dollars from another skill's sessions.

**Split inside `e70f0f05`.** The session also edited the skill itself (v1.1 and v1.2). Rule: subagents whose `.meta.json` description names a skill change, plus parent turns that contain an Edit or Write under `.claude/skills/`. That segment is $6.05: 3 QA subagents at $5.08 and 14 parent turns at $0.97. The round's own work is $159.91 of the $165.96 computed.

> **Source:** Claude Code logs, `~/.claude/projects/-Users-dpedrini-Projects-dannys-pm-workspace-care`, window 21 Sep 2026 through 2 Nov 2026 by first-record Eastern time. Per-request dollars from `message.usage` per unique `requestId` at the brief's fitted rates. Scratch scripts in `$TMPDIR/skillplan-pdfm/`.

**Baseline numbers I found wrong.**

| Earlier figure | Corrected | Why |
| --- | --- | --- |
| Subagents $146.04; session computed $173.99 (4.4% over logged) | Subagents $138.01; session computed $165.96 (0.4% under the logged $166.69) | 16 fork transcripts copy their parent agent's opening requests. 51 request IDs appear in more than one transcript and were counted twice. |
| 133 subagent launches | 124 agents: 104 launched by the parent, 20 nested inside subagents | Fork transcripts repeat their parent's Agent calls, which inflates a raw count. |
| QA reopens of Jira tickets cost $10.79; non-QA reopens $12.66 | QA agents $3.83 (108 calls); QA forks $2.28 (66 calls); dedup agents $1.08 (26); dedup forks $2.88 (45). All reopens $10.07; all 332 Jira calls $15.74 | Priced as the issuing turn's share plus the payload carried through the agent's later turns, with payload tokens measured from context growth (median 2.47 characters per token over 1,063 tool results). |
| "Nine full-read agents with three tickets or fewer" | 16 fork agents were each named for three tickets or fewer. 6 of them read 10 or more distinct tickets | A fork inherits the parent's whole brief and redoes its task. |

The counts the earlier pass gave for Jira did reproduce: 65 distinct tickets, 47 opened by more than one agent, 164 extra agent opens, 108 QA reopen calls. The model rates also reproduce `cost-state` per model to the cent.

**Step cost map (`e70f0f05`).** Setup means calls before the first tool that is not Read, Grep, Glob or ToolSearch.

| Step | Parent $ | Subagents | Subagent $ | Setup $ (share) |
| --- | --- | --- | --- | --- |
| 0 and 1: setup, preflight, plan QA (parent includes v1.1 skill edits) | $4.44 | 6 (1 nested) | $17.16 | $1.77 (10%) |
| 2a extract | $6.09 for 2a and 2b together | 11 | $17.61 | $3.43 (19%) |
| 2b blind re-extract | (above) | 10 | $7.32 | $2.15 (29%) |
| 2b adjudicate | (above) | 11 (1 nested) | $10.63 | $2.89 (27%) |
| 2b second opinion, parts A and B, targeted reruns | (above) | 22 | $10.93 | $5.96 (55%) |
| 2b rule recheck | (above) | 6 | $3.58 | $1.00 (28%) |
| 2c cluster | $0.50 | 1 | $5.01 | $0.29 (6%) |
| Dedup | $4.66 for dedup, 2d and Gate 2 | 7 plus 11 nested | $19.27 | $3.31 (17%) |
| 2d structure QA | (above) | 2 | $5.13 | $0.40 (8%) |
| 2d dedup QA | (above) | 5 plus 7 nested | $9.44 | $2.66 (28%) |
| 3 plan and plan QA | $4.59 for Step 3 | 3 | $5.17 | $0.81 (16%) |
| 3 drafts | (above) | 9 | $14.03 | $3.03 (22%) |
| 3 anonymize | (above) | 7 | $1.33 | $1.09 (82%) |
| 3 blind scorers (Opus 5.5) | (above) | 2 | $1.91 | $1.74 (91%) |
| 3 format checker | (above) | 1 | $4.41 | $0.26 (6%) |
| Gate 3 review and v1.2 skill edits | $7.67 | 0 | $0 | n/a |
| Skill-change QA (maintenance) | (in rows above) | 3 | $5.08 | $0.51 (10%) |
| **Total** | **$27.95** | **124** | **$138.01** | |

Steps 4, 5, 6 and AMEND: not applicable in this window (not run in `e70f0f05`).

> **Source:** same logs and window; parent turns split by timestamp at the first subagent launch of each step; subagents mapped to steps by `.meta.json` description.

**Context anatomy.**

| Part | Typical subagent (2a extractor, batch SB; peak 259,142 tokens) | Parent at peak turn (848,346 tokens) |
| --- | --- | --- |
| Base context | 48,714 tokens on the first call: 12,235 cached shared prefix, 36,479 fresh write | 64,837 tokens on the first call |
| Inside the base | Tool definitions for 9 tools ~8,000; deferred-tool list ~12,300; skill listing ~8,400; agent listing ~5,400; CLAUDE.md and AGENTS.md ~4,800; MCP instructions ~3,300; sandbox ~2,400; memory ~2,100 [Assumption: 4.1 characters per token, fitted so the parts sum to the measured first call (needs validation)] | Same listings plus 15 parent tools |
| Skill text loaded | Brief (median 324 characters) plus `extraction-briefs.md`, `rules-core.md`, `ledger-schema.md`: ~12,300 tokens | `SKILL.md` via the Skill tool and `round-folder-layout.md`: ~23,500 tokens (`extraction-briefs.md` and `rules-core.md` came in through Bash, counted below) |
| Source payloads | `clinical-rules.md` ~66,400 tokens (the largest single read); `export/SB.md` ~20,400; provenance, plan, Bash output and its own trace file ~27,400 | Bash output ~149,600 tokens; agent returns ~45,600; MCP reads ~11,100 |
| Accumulated turns | The rest, ~84,000 tokens, mostly 68,384 output tokens of ledger writing | The rest, ~538,000 tokens: 104 briefs, edits, heredocs, QA report reads and 379,739 output tokens |

Reference files that load on every run but serve only part of their readers:

- `extraction-briefs.md`: 54 agents read all five briefs and use one.
- `ledger-schema.md`: part B "Recommend" agents read it but need only the Recommendation format.
- `rules-core.md`: second-opinion agents may use only sections 1, 2 and 3 but load all of it.
- `clinical-rules.md` section 14: a 64,221-character Docebo copy that also exists as the dated Docebo file in the round folder.

> **Source:** same logs; first-call usage and `api-request-shape` and `attachment` records of agent `a6b2e51`; parent `api-request-shape`; tool-result sizes; token counts from context growth.

## 3. Changes, ranked by dollars per future run

Change 9 is rejected and saves $0. It keeps its number so the other references still point at the same sections.

### 1. Lean worker agent type ($17.49, assumption-heavy)

**Touches.** `SKILL.md` line 47 (Agent tool rule), the `<input_routing>` table at lines 74 through 92, and a new agent definition such as `.claude/agents/pdfm-worker.md`, which sits outside the skill folder and needs Danny's approval.

**Change.** Every non-reviewer subagent launches as one worker type with an explicit `tools:` list: Read, Write, Edit, Bash, Grep and Glob, plus Atlassian read tools for dedup, dedup QA, inventory and the format checker. It carries no Agent or Skill tool, so it can't fork. The two Opus 5.5 reviewers keep their own types and models.

**Saving.** 102 top-level non-reviewer agents made 1,801 requests. At 29,400 fewer tokens each, that is one first-call write at $2.50/M plus 1,700 cache reads at $0.20/M, which comes to $17.49. The 29,400 figure is the skill listing, agent listing, deferred-tool list and MCP instructions measured in agent `a6b2e51`. The two custom reviewer agents still received every listing, so a custom type alone does not remove them; only the `tools:` list might.

This $17.49 includes the four Recommend agents change 6 removes and the duplicate anonymizer change 10 removes, $0.86. The Answer total counts those agents once. The same test launch is the measurement for the tool-list figures in the prd-generator, dashboard-requirements and agent-architect plans.

**Guarding evals.** E1 and E2 (coverage), E11 (full reads), E12 and E13 (names). No trace shows these evals catching anything yet: the traces folder is empty and every eval reads "not run". Propose **E23, No nested subagents**: FAIL if any subagent `.meta.json` for the run's session IDs has `spawnDepth` above 1.

**Validation.** First, spawn one worker of the new type with an empty brief and read its first-call context. Proceed only if it drops by at least 20,000 tokens. Then replay Step 2b for batches SB and FA from a scratch copy of the Provider Pilot Round 1 folder. Pass bar: `mechanical_check.py` exits 0, and the adjudicated ledger covers every atomic issue in the saved one, matched by trace and issue type.

**Risk.** The saving may be near zero if the harness injects the listings regardless of `tools:`. A missing tool would stall an agent; the retry-once rule at line 47 catches that.

### 2. No nested subagents ($13.81)

**Touches.** `SKILL.md` lines 37 through 47 (ALWAYS block), line 127 (provenance), line 140 (dedup); `clustering-and-dedup.md` section 9 (lines 107 through 127) and section 13 (lines 177 through 189); `extraction-briefs.md` section 3 (lines 54 through 75).

**Change.** Add one rule to every brief: "Do not launch subagents. Read every ticket, commit or file yourself." Dedup agents spawned 11 nested agents and dedup QA 3 spawned 6. Provenance spawned a GitHub lister, adjudicator SD spawned an ad hoc check, and one fork spawned a further QA agent. A fork named for one ticket read up to 13 distinct tickets, and one fork was a "no-op placeholder" costing $0.58.

**Saving.** The 20 nested agents cost $17.33. Subtract what the parent agents would spend instead.

That is $1.31 for the Jira reads on the tickets each fork was named for, and $1.21 to keep the two ad hoc checks as in-agent steps. Commit listing in the provenance agent adds $1.00 [Assumption: in-agent commit listing costs $1.00 (needs validation)]. Net: $13.81.

**Guarding evals.** E11 and E10 (dedup), E17 (timing). Proposed E23 above.

**Validation.** Replay the Step 2 dedup on the saved `cluster_defs.py` and `existing-tickets.md` in a scratch copy. Pass bar: the "Final verdicts" categories match the saved `dedup-verdicts.md` for every ticket whose Jira `updated` time predates 3 Nov 2026; E10, E11, E17 and E23 pass.

**Risk.** A dedup group's own context grows when it reads all its tickets. The longest group (G7, 36 Jira calls) peaked at 316,400 tokens without nesting, so this stays inside one context.

### 3. Fresh orchestrator session at each gate ($8.82)

**Touches.** `SKILL.md` line 105 (modes), line 133 (Gate 1), lines 142 through 149 (Gate 2), line 162 (Gate 3), and line 234 (observability).

**Change.** After presenting each gate, the orchestrator tells Danny to answer in a new session that runs resume mode. Resume already rereads `STATUS.md` and continues at its "Next" line. Skill edits found mid-round go to a separate session, not the round thread.

**Saving.** The parent started at 64,837 tokens, peaked at 848,346 and cost $27.95 on Sonnet 5.5. I replayed every parent request with the context reset at the first turn after 13:20, 15:40 and 16:45 UTC on 3 Nov 2026 (Gate 1 answer, Step 3 start, Gate 3 table).

Each reset pays a fresh 1-hour write of the resume base. With a 150,000-token resume base, the parent costs $19.13 [Assumption: resume base of 150,000 tokens (needs validation)]. The reset also shrinks the 835,452-token cache rewrite after the 60-minute gap at Gate 3, which cost $3.34.

**Guarding evals.** E3 and E8 read `STATUS.md` decisions, and `log_check.py` runs on every resume. Propose **E24, Resume continuity**: every session after the first starts with a `note` event "resumed from STATUS.md", and every Gate 2 and Gate 3 decision in `STATUS.md` has a matching `gate_answered` event.

**Validation.** From a scratch copy of the round, start a fresh session at Step 3 using the saved Gate 2 state. Pass bar: the regenerated `ticket-plan.md` has the same ticket set, merges and recommended priorities as the saved one, and E24 passes.

**Risk.** A chat decision that never reached `STATUS.md` is lost. The hard constraint at line 42 already requires recording first; E24 makes a miss visible.

### 4. Script the format checker's mechanical checks ($1.25)

**Touches.** `ticket-qa-briefs.md` section 4 (lines 44 through 60); `scripts/check_tickets.py` docstring (lines 1 through 26) and `main` (lines 214 through 237).

**Change.** `check_tickets.py --tickets` already checks the title pattern, session artifacts, writing rules and body length. Add a `--traces` mode (every `tr-` prefix resolves in `export/*.md`) and a `--threads` mode (one Draft and thread subheading per Evidence trace). The checker brief then keeps only the judgment checks: names, and whether each live Jira key supports its characterization.

**Saving.** The checker cost $4.41, of which $1.91 was Jira. Its other $2.50 went to 38 Bash calls and 17 Reads, mostly greps for the same patterns. Half of that is $1.25 [Assumption: half the non-Jira spend is mechanical rechecking (needs validation)].

**Guarding evals.** E14, E20 and E21 run the same script at Step 6.

**Validation.** Run the new modes on the saved `ticket-drafts.md`. Pass bar: they flag both DEFECTs recorded in `qa-step3-format.md` that fall under these checks, or show those checks were judgment ones the brief keeps.

**Risk.** Low; scripts are deterministic and stop the step on a non-zero exit.

### 5. Group dedup and dedup QA by shared ticket ($1.18)

**Touches.** `SKILL.md` line 140; `clustering-and-dedup.md` line 109 (dedup split) and line 179 (QA ranges).

**Change.** The orchestrator puts FMs that share a candidate ticket in the same dedup group, and gives each dedup QA agent a disjoint set of tickets rather than FM numbers. Every dedup call still rests on its own agent's full read, and every QA still rereads every cited ticket from scratch.

**Saving.** Top-level dedup agents reopened tickets another group had read 12 times ($0.51). Dedup QA agents did so 20 times ($0.67).

**Guarding evals.** E11 (every dedup call has a `Read:` line). Propose **E25, Dedup QA reread coverage**: every key in `dedup-verdicts.md` appears in a "Tickets read" table in some `dedup-qa-*.md`. This also protects against the earlier report's change.

**Validation.** Rebuild the grouping from the saved `cluster_defs.py` with a script and count candidate tickets per group. Pass bar: no ticket in more than one dedup group or QA range, and E11 and E25 pass on a dedup replay.

**Risk.** Groups become uneven; a group with one heavily shared ticket may hold more FMs.

### 6. Message the original second-opinion agent for part B ($1.00)

**Touches.** `extraction-briefs.md` section 4 (lines 77 through 89) and section 5, part B (lines 100 through 109).

**Change.** Part B goes back to the original second-opinion agent. Message it in the same turn it returns. The rule recheck stays a separate agent, because it has already read the Docebo source. If the second-opinion agent has already finished, keep today's fresh Recommend agent.

**Saving.** Four batches (SB, SE, FA, FB) ran both. The four Recommend agents' setup was $1.00. That saving holds only if a same-turn message costs less than a fresh agent. [Assumption: a same-turn resume costs less than $1.00 of setup (needs validation)]

**Guarding evals.** E3 parses the `Recommendation:` cells.

**Validation.** For batches SB and FA, message the original second-opinion agent with the saved diff and overrule rows, and run the rule recheck separately. Pass bar: every `Recommendation:` cell picks the same side as the saved file, the rule-recheck verdicts match, and the recommendation does not come from the rule-recheck agent.

**Risk.** Messaging a finished background agent can re-write its whole context. The message goes out in the same turn, and a finished agent keeps the fresh Recommend path.

### 7. Format checker reuses verified reads when a ticket hasn't changed ($0.85)

**Touches.** `ticket-qa-briefs.md` section 4, "Live Jira keys" bullet (line 52).

**Change.** For a key that a dedup QA agent read in full this round, the checker first reads only its `updated` field. If `updated` predates the QA's `Read:` time, it uses that QA's final-scope line. It does a full read when the draft's characterization goes beyond that scope line, when the scope line is missing, when `updated` is newer, or when no QA read the key.

**Saving.** 31 of the checker's 37 keys were read in full during dedup. Its Jira payload carry was $1.16; 31 of 37 keys at one-eighth payload saves $0.85 [Assumption: a one-field read is one-eighth the payload (needs validation)]. Keys whose draft goes past the scope line pay a full read, so $0.85 is a ceiling. [Assumption: most of the 31 keys stay inside the scope line (needs validation)]

**Guarding evals.** None today. Propose **E26, Format checker key coverage**: every Jira key in `ticket-drafts.md` and `ticket-comments.md` is listed in `qa-step3-format.md` with how it was verified.

**Validation.** On the saved drafts, compare the checker's verdict per key under both methods. Pass bar: identical verdicts on every key.

**Risk.** It trusts the dedup QA's scope line, which is itself an independent reread.

### 8. Split `extraction-briefs.md` per role ($0.76)

**Touches.** `extraction-briefs.md` lines 1 through 118; `SKILL.md` line 58 and line 79.

**Change.** One file per role (extractor, blind re-extractor, adjudicator, rule recheck, second opinion), each brief routed alone. The blind re-extractor and second opinion then never see the extractor's rules, which strengthens their independence.

**Saving.** Whole-file reads cost $1.08 across 54 agents; 70% of that is $0.76 [Assumption: each role uses 30% of the file (needs validation)].

**Guarding evals.** E2, plus the adjudicator's Counts section.

**Validation.** Replay 2a and 2b for batches SB and FA. Pass bar: `mechanical_check.py` exits 0; the blind file's miss count is not lower than the saved `SB-adjudication.md` and `FA-adjudication.md` counts.

**Risk.** A shared rule edited in one file and not another; keep shared rules in `rules-core.md`.

### 9. Epic inventory stays on Sonnet 5 (rejected, $0)

**Touches.** `SKILL.md` line 128.

**Change.** Rejected. Step 1.5 records prior-round origin and key renames, which is matching work, not a field list. It stays on Sonnet 5 with extraction and adjudication.

**Saving.** $0. The earlier $0.62 ($4.10 on Sonnet 5, repriced to $3.48) is not counted.

**Guarding evals.** Not applicable. No change.

**Validation.** Not applicable.

**Risk.** Not applicable. A model move here could miss a renamed key.

### 10. Name one batch per anonymizer from `round.json` ($0.17)

**Touches.** `SKILL.md` line 159; `ticket-qa-briefs.md` section 5 (lines 62 through 70).

**Change.** The orchestrator fills each anonymizer brief from `round.json` `batches[]`, one code each. In this run one agent took ID and RV together, then RV ran again, which also broke goal 2.

**Saving.** The duplicate RV agent cost $0.17.

**Guarding evals.** E12 and E13.

**Validation.** Check the run log for one `subagent` event per batch code at the anonymizer step.

**Risk.** None.

### 11. Keep skill maintenance out of the round session (launches only)

**Touches.** `SKILL.md` lines 233 through 235.

**Change.** Skill edits found mid-round get logged as a `note` and run in a separate session after the gate. In this run, v1.1 and v1.2 edits ran at 239,197 and 815,450 tokens of parent context. The dollars overlap with change 3, so none are claimed here.

## 4. What not to cut

- **One batch per agent.** Goal 2 in `SKILL.md`; the only overlap in this run (change 10) broke it.
- **The blind re-extractor's independence.** Adjudicators added rows the extractors missed (the `added in 2b` notes in `ledger/qa/*-adjudication.md`); change 8 strengthens it.
- **The second opinion.** E3 is the graduation signal and needs the disagreements it produces.
- **The three-round QA loop.** 2d structure QA round 2 found one incomplete round-1 fix and one defect a round-1 fix introduced (`qa-2d-structure-round-2.md`). Step 1 QA fell from 6 DEFECTs to 3, with a rename only partly fixed (`qa-step1-round-2.md`).
- **The dedup QA's independent reread.** `clustering-and-dedup.md` section 13 forbids trusting the write-up; E25 would guard it.
- **Sonnet 5 for extraction, adjudication and blind scoring.** Held fixed by the brief; these are clinical judgment calls.
- **Sonnet 5 for the epic inventory.** Step 1.5 records prior-round origin and key renames (`SKILL.md` line 128), so change 9 is rejected.
- **Opus 5.5 for the clinical and provider scorers.** Held fixed; they cost $1.91, 91% of it setup that only a persona change could cut.
- **Full reads before a dedup call.** E11 and the hard constraint at `SKILL.md` line 26.

## 5. Open questions for Danny

1. Is `clinical-rules.md` section 14 (the Docebo copy, 64,221 characters) a duplicate of sections 1 through 6 for extraction purposes? Routing it only to the rule recheck would save $1.14 per run, but extractors audit dosing against it, so I left it out of the ranking.
2. Nine large-context subagents (extractors, blind re-extractors, the 2c writer, the ticket-plan writer and a drafter) rewrote their whole context in under 3 minutes, at $4.70. The cause is unknown [Assumption: the harness clears old tool results and the prefix changes (needs validation)]. Do you want that investigated as a harness question?
3. Decision: briefs pass `run_in_background` as a boolean false. The $9.00 in notification turns stays uncounted until a run shows those turns drop. Whether the harness still forces background launches after a real boolean is an open harness question.
4. Do you approve an agent definition outside the skill folder (change 1)? If not, change 2 still works through brief text alone.
5. Should Steps 4, 5 and 6 (sessions `ad11bf5f` at $32.13 and `bed14ed4` at $155.50, both after the window) get the same pass? They were not measured here.
