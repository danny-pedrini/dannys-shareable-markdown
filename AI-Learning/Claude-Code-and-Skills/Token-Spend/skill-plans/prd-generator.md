# prd-generator: token-efficiency plan

Plan only. Nothing in the skill has changed.

## 1. Answer

The full change set saves about **$16.91 per future create run** (24% of the $69.14 average) and **$2.54 per revise run** (16% of $16.28). Applied to the three runs in the window from 21 Sep 2026 through 2 Nov 2026, it would have saved **$36.35 of $154.56** (24%).

One change carries 43% of the create saving: start each post-gate phase in a fresh parent context ($7.27 per create run). Without the one Fidelity fan-out seen on 21 Oct, the typical create run saves about $13.50.

No change removes a check. The full re-run on every fix round stays, and Fidelity stays its own agent. The Opus 5.5 reviewer personas stay too.

> **Source:** Claude Code transcripts under `~/.claude/projects/` for sessions a977e688, 93a3e520 and cf5250a3, window 21 Sep 2026 through 2 Nov 2026. Each unique requestId is priced at the brief's rates. Savings are computed per change, then combined with the overlaps removed (section 3).

## 2. Measured baseline

### Attributed and segmented dollars

| Session | Kind | Computed $ | Logged $ | Gap | Skill $ | Method |
| --- | --- | --- | --- | --- | --- | --- |
| a977e688 | Create run, 2 Nov | 70.44 | 70.64 | 0.3% | 65.78 run, 4.66 post-run | Attributed (single skill) |
| a23fb079 | Skill maintenance, not a run | 1.49 | n/a | n/a | 1.49 | Attributed |
| 93a3e520 | Create run, 21 Oct | 87.82 | 86.02 | 2.1% | 72.49 | Segmented |
| cf5250a3 | Revise run, 26 Oct | 99.07 | 97.25 | 1.9% | 21.75 segment, 16.28 run | Segmented |
| 6a7d3d70 | SKILL.md read as reference | 173.62 | 173.93 | 0.2% | 1.54 | Segmented |
| 62e199c0 | Skill rewire session | 13.27 | 13.30 | 0.2% | 2.80 | Segmented |

Attributed dollars are **$67.27** for real runs plus maintenance ($65.78 + $1.49). Segmented dollars are **$98.58** ($72.49 + $21.75 + $1.54 + $2.80). Agents launched inside a segment whose description names no skill step are reported apart: $1.28 in 93a3e520, $4.95 in cf5250a3, $1.58 in 62e199c0.

**Segmentation boundaries.** 93a3e520 runs from the `/prd-generator` command record at 10:52:29Z on 21 Oct to the `Skill` call for acceptance-testing-generator at 18:05:35Z. cf5250a3 runs from the `Skill` call for prd-generator at 15:33:19Z on 26 Oct to the `Skill` call for acceptance-testing-generator at 10:40:06Z on 27 Oct. Subagents count when launched inside the segment and their `.meta.json` description names a Plan, Draft, QA phase or Review step. That includes the Fidelity grandchildren in 93a3e520 that name E01 and E21.

The cf5250a3 run itself ended with the last parent turn on 26 Oct, at 18:06:33Z, after the trace write at 17:47:48Z. Its run cost is parent $9.20, QA $5.02 and in-run skill-edit QA $2.06.

From 13:11:26Z on 27 Oct the same session is prd-generator again. The parent read this skill's `SKILL.md`, and the work is skill maintenance, not a revise run. QA priced that span at $53.79, including a $20.66 skill-update agent. It stays out of the run totals above, and acceptance-testing-generator does not count it either.

> **Source:** transcripts above. Segment ends are structural load signals (`Skill` tool calls or slash-command records), never string mentions. Totals were checked against the last `cost-state` record; no gap exceeds 5%.

### Baseline numbers found wrong

| Claim | Corrected value | Why |
| --- | --- | --- |
| 27 judgment agents in a977e688 spent $7.99 on setup | $2.39 under the literal rule | Setup = calls before the first tool that is not Read, Grep, Glob or ToolSearch. Counting text-only judging calls as setup gives $5.55; counting the stopping call gives $8.73. No definition reproduces $7.99. The $20.37 total holds: Fidelity $11.98, Scope $4.13, Content $4.26. |
| Merging Scope and Content saves $2.66 (9 agents × $0.296 setup) | $2.81 standalone, $2.12 after eval extracts | The saving is real but comes from per-agent overhead plus duplicate evals.md reads, not setup alone. |
| $72.13 attributed across two single-skill sessions | $65.78 of real run cost | a23fb079 is maintenance, and a977e688 includes $4.66 of post-run work. |
| 6a7d3d70 sums 12.6% over its logged cost | 0.2% after dedup | 165 request IDs appear in two subagent files (a fork pair), worth $22.27. |
| Revise mode ran four times in nine days | One measurable revise run | The 4 Nov and 5 Nov revise traces name a `Task` tool and match no Claude Code session. [Assumption: they ran in Cursor (needs validation)]. A fourth revise run was not found. |

### Step cost map

Create run a977e688 (Steps 0 through 2 include the 1 Nov pre-run turns):

| Step | Parent $ | Subagents | Subagent $ | Setup $ (share) | Other agents $ |
| --- | --- | --- | --- | --- | --- |
| Steps 0 through 2 | 5.93 | 0 | 0.00 | 0.00 | 1.42 |
| Step 3 Plan | 1.32 | 3 | 4.68 | 1.86 (40%) | 0.00 |
| Step 4 Plan QA | 3.94 | 12 | 7.59 | 1.07 (14%) | 0.00 |
| Step 5 Draft | 0.34 | 1 | 0.82 | 0.00 | 0.00 |
| Step 6 Draft QA | 3.73 | 12 | 5.89 | 0.83 (14%) | 0.00 |
| Step 7 Reviewers | 3.60 | 6 | 9.87 | 0.00 | 0.00 |
| Step 8 Revision QA | 6.27 | 12 | 7.56 | 0.48 (6%) | 0.00 |
| Step 9 Trace | 2.81 | 0 | 0.00 | 0.00 | 0.00 |

Create run 93a3e520 (total $72.50):

| Step | Parent $ | Subagents | Subagent $ | Setup $ (share) | Other agents $ |
| --- | --- | --- | --- | --- | --- |
| Steps 0 through 2 | 5.13 | 0 | 0.00 | 0.00 | 0.74 |
| Step 3 Plan | 1.42 | 3 | 3.62 | 1.25 (35%) | 0.00 |
| Step 4 Plan QA | 7.89 | 12 | 9.13 | 0.94 (10%) | 7.77 Fidelity grandchildren |
| Step 5 Draft | 0.40 | 1 | 2.15 | 0.00 | 0.00 |
| Step 6 Draft QA | 3.90 | 12 | 4.15 | 0.92 (22%) | 0.00 |
| Step 7 Reviewers | 2.69 | 4 | 6.80 | 1.01 (15%) | 0.00 |
| Step 8 Revision QA | 9.80 | 12 | 5.23 | 0.86 (16%) | 0.00 |
| Step 9 Trace | 1.66 | 0 | 0.00 | 0.00 | 0.00 |

Revise run cf5250a3:

| Step | Parent $ | Subagents | Subagent $ | Setup $ (share) | Other agents $ |
| --- | --- | --- | --- | --- | --- |
| Steps 0 through 3 | 2.52 | 0 | 0.00 | 0.00 | 0.00 |
| Step 8 Revision QA | 5.50 | 12 | 5.02 | 0.95 (19%) | 2.06 skill-edit QA |
| Step 9 Trace | 1.18 | 0 | 0.00 | 0.00 | 0.00 |

The parent orchestrator is 42% of create-run spend ($27.94 of $65.78 in a977e688). Cache reads alone are $18.46 of the a977e688 parent's $30.80 session total.

> **Source:** transcripts above. Steps are bounded by the parent's tool calls (first plan launch, gate writes, first QA launch per phase, trace write). Models: Opus 5.5 parent and reviewers, Sonnet 5 plans, draft and judgment QA, Haiku 5.5 mechanical QA ($0.66 in a977e688 at approximated Haiku rates that match the log).

### Context anatomy

| Context | Base (harness) | Skill text | References | Source payloads | Accumulated turns | Peak |
| --- | --- | --- | --- | --- | --- | --- |
| Sonnet judgment QA agent | 48.4k first call: 12.0k cached system prompt plus 36.4k fresh write | Full SKILL.md, 15.8k, read by Scope P agents only | Full evals.md, about 26k, read by every judge; the group needs at most 22% of it | Artifact under test, about 8.6k for a plan; Fidelity adds all inputs | Not measured separately | Fidelity up to 240k; Scope and Content up to 125k |
| Plan agent | Same base | Full SKILL.md, 15.8k | Gold PRD, exemplars, template | All inputs | n/a | Up to 260k |
| Opus parent, a977e688 | About 79k | SKILL.md via the slash command | Always-load files, 46.2k as tool results | Inputs about 30k; Bash reads 62.5k | Subagent reports delivered as messages, about 118k; the parent's own tool inputs and prose, about 175k | About 780k by Step 8 |

Harness attachments across a QA agent's life, in characters: tool list 56k, skill listing 30k, deferred tools 24k, agent listing 21.5k, CLAUDE.md and AGENTS.md 19k, MCP instructions 13k, sandbox 9.8k. The launch prompt is under 3.5k characters, so the orchestrator never inserts the group's evals as `references/qa-subagent-briefs.md` line 39 tells it to.

> **Source:** transcripts above, first-call and peak `usage` per agent. Tokens from characters at 2.54 characters per token for JSON tool results (median of measured pairs) and 2.35 for raw markdown.

## 3. Changes, ranked by dollars per future run

Per-run and window figures below are standalone. The combined total in section 1 removes overlaps: after the fresh-context change, the parent lean-load saves $0.56, QA self-written reports about $0.60 [Assumption: a third of the carry saving survives a fresh parent (needs validation)], and the trace script $0.18.

| Rank | Change | Per create run | Per revise run | Window |
| --- | --- | --- | --- | --- |
| 1 | Fresh parent context after each gate | $7.27 | n/a | $14.54 |
| 2 | QA judges as a fixed-tool agent type | $4.12 | $0.23 | $8.48 |
| 3 | Per-group eval extracts for judges | $1.82 | $0.56 | $4.19 |
| 4 | Merge Scope and Content | $1.79 | $0.51 | $4.08 |
| 5 | Parent loads only what it uses | $1.61 | $0.53 | $3.75 |
| 6 | QA agents write their own report file | $1.24 | $0.33 | $2.80 |
| 7 | Deterministic mechanical-check script | $0.70 | $0.21 | $1.60 |
| 8 | Trace compile script | $0.49 | $0.25 | $1.23 |
| 9 | Plan briefs get extracts, not full SKILL.md | $0.11 | n/a | $0.22 |
| 10 | Save MCP sources once to the run folder (no dollar saving; enables rank 2) | $0 | $0 | $0 |

### 1. Fresh parent context after each gate

**Where:** SKILL.md Step 4 item 3 (line 201), Step 7 item 4 (line 224), the intake gate (lines 76 through 83), and Revise mode (lines 245 through 253).

**Change.** At three points the parent writes a handoff and continues in a fresh context: after the intake gate, after Gate 1 and after Gate 2. The handoff lists the run folder, the gate snapshot and the next step. Either Danny resumes in a new session from the run folder, or the parent launches an Opus sub-orchestrator for the next block. The gate snapshots already hold Danny's decisions verbatim, so the next block reads files, not chat history.

**Saving.** The parent context grows from about 79k to about 780k tokens, and every call rereads it. I repriced each post-gate block from a new 110k base (1-hour write $0.88), keeping 4 parent turns per block. That gives $6.35 for a977e688 and $8.19 for 93a3e520. In 93a3e520 it also removes the $3.42 cache rebuild after the 90-minute Gate 1 wait.

**Guarding evals.** E10 (draft matches gate-1) failed in the 21 Oct draft phase and every 26 Oct revision round. E39 (surgical revision) failed in 21 Oct revision rounds 1 and 3 and every 26 Oct round. E40 (unapproved adoption) never failed in a trace, so there is no evidence it catches a dropped Gate 2 decision. Propose **E44 Gate snapshot completeness**: a judge run before each handoff compares the snapshot with Danny's gate message and fails on any missing modification.

**Validation.** Replay: the a977e688 run folder still holds gate-1.md, gate-2.md, plan.md and every QA report. Run Steps 5 through 6 once from gate-1.md in a fresh session and compare its D-round-1 verdicts with D-round-1 in that folder. Pass bar: E10 and E43 verdicts match, and E44 passes on all three snapshots.

**Risk.** A modification Danny gave in chat but left out of the snapshot is lost. E44 is the guard.

### 2. QA judges as a fixed-tool agent type

**Where:** `references/qa-subagent-briefs.md` judgment brief (lines 14 through 62) and SKILL.md `<qa_loop_protocol>` item 1 (line 88).

**Change.** Add a project agent type for QA judges with tools Read, Grep, Glob and Bash, no Agent tool and no MCP tools. Pin it to Sonnet 5 explicitly, because `inherit` would move judges onto the Opus parent model. Fidelity reads saved source copies (rank 10) instead of calling MCP.

**Saving.** In 93a3e520, Fidelity P spawned grandchildren that cost $7.77; removing them nets $6.89 after $0.44 per round of extra reading. A smaller harness block saves about $0.025 per agent [Assumption: about 6.8k fewer base tokens, measured on two Explore agents on Opus (needs validation)]. Do not use 6.8k until the provider-draft-failure-modes change 1 test launch measures the drop, and use that measurement here. That is $0.68 for 27 judges per create run, or $0.45 after the merge.

**Guarding evals.** E01, E02, E21 and E43. E01 failed in plan rounds 1 and 2 on 21 Oct and 2 Nov, E21 failed in plan round 1 on 21 Oct and round 2 on 2 Nov. That shows Fidelity catches dropped inputs without nested agents in a977e688.

**Validation.** Replay Fidelity P on the 2 Nov plan (pre-revision and plan files in the a977e688 run folder) with the new agent type. Pass bar: E01, E02, E21 and E43 verdicts match P-round-1 in that folder, and each Fail cites the same defect location.

**Risk.** The fan-out was seen once, so the $6.89 may not recur. A tool-poor agent may skip a check it would have delegated; the replay tests that.

### 3. Per-group eval extracts for judges

**Where:** `references/qa-subagent-briefs.md` line 39, and SKILL.md `<eval_phase_map>` (lines 256 through 294).

**Change.** A script writes one brief file per group and phase into the run folder. It holds that group's eval definitions from evals.md and, for Scope, the ownership contract from SKILL.md lines 138 through 150. Judges read that file and nothing else from the skill. This does what line 39 already asks for.

**Saving.** Judges read full evals.md (about 26k tokens) 27 times in a977e688, and Scope P agents read full SKILL.md. Repriced with extract sizes (Fidelity 7.9k, 7.5k and 10.2k characters for P, D and R; Scope 9.5k; Content 9.4k) at the 5-minute write and later-call read rates: $1.95, $1.68 and $0.56.

**Guarding evals.** Every judgment eval. E11 failed in every phase of every create trace, and E04 newly failed in a later round five times. That shows the judges catch these from definitions alone.

**Validation.** First, a script check: every extracted block is byte-identical to its evals.md section. Then replay D round 1 for all three groups on draft-before-D1-fixes.md from the a977e688 run folder. Pass bar: identical Pass or Fail per eval ID versus that folder's D-round-1 reports. Propose **E45 Report coverage** (Code): each report lists exactly the assigned eval IDs.

**Risk.** Low. The definitions are unchanged; judges lose only unrelated text.

### 4. Merge Scope and Content

**Where:** SKILL.md `<eval_phase_map>` group column (lines 268 through 280), `<input_routing>` (lines 69 through 70), and the briefs judgment template.

**Change.** One judge checks the 13 Scope and Content evals per round. Fidelity stays separate.

**Saving.** Removing 9 Content agents per create run removes their overhead and duplicate reads, minus extra template reading for the merged agent. That is $2.12 for a977e688 and $1.45 for 93a3e520 after rank 3, plus $0.022 per launch prompt; standalone it is $2.81 for a977e688.

**Guarding evals.** E04, E23, E24, E26, E42 (Scope) and E09, E11, E31, E34, E35, E41 (Content). Scope regressed from pass to fail four times across traces. Content failed in nearly every round. Both groups therefore produce signal a merged agent must keep.

**Validation.** Replay D round 1 and R round 1 from the a977e688 run folder three times each with the merged agent [Assumption: three replays show verdict variance (needs validation)]. Pass bar: every eval that failed in the original Scope or Content report fails in at least two of three replays, and E45 passes.

**Risk.** Medium. One agent holding 13 rubrics may skim the later ones. Keep the split if any replay misses an original failure.

### 5. Parent loads only what it uses

**Where:** SKILL.md `<context_sources>` (lines 42 through 62) and Step 1 item 1 (line 116).

**Change.** The parent stops loading evals.md, the stakeholder directory, the glossary, the voice exemplar, the acceptance-testing template, exemplars.md and the gold PRD; subagents keep them. trace-schema.md loads at Step 9. The parent opens the directory or glossary only when a fix needs a name or term.

**Saving.** Carry cost of those reads: $1.45 in a977e688, $1.77 in 93a3e520, $0.53 in the revise run. This assumes 10% of runs reopen a file [Assumption: 10% on-demand lookups (needs validation)]. After rank 1 it falls to $0.50 and $0.61.

**Guarding evals.** E02 (names) and E37 and E41 (undefined terms) catch a bad parent fix. E37 failed in a977e688 D round 1 and persisted in both 21 Oct draft and revision phases; E41 persisted on 2 Nov.

**Validation.** Give a fresh Opus context the a977e688 D-round-1 reports plus draft-before-D1-fixes.md, once with and once without these files. Run D round 2 QA on both outputs. Pass bar: no eval fails in the lean version that passes in the full one.

**Risk.** Low. Subagents still receive every file they need.

### 6. QA agents write their own report file

**Where:** `references/qa-subagent-briefs.md` lines 5 and 51 (QA never writes files), and `<qa_loop_protocol>` item 1 (line 88).

**Change.** Each QA agent writes its full report to `<run>/qa-reports/` and returns only the verdict line plus failing rows with evidence. The parent checks the artifact checksum before and after the round, so a QA agent cannot edit the artifact unnoticed.

**Saving.** Reports reach the parent as messages: 118k tokens in a977e688, then the parent re-emits them as Bash or Write calls. Returning 35% of each report [Assumption: failing rows are 35% of report size (needs validation)] and dropping the re-emission saves $1.30, $1.17 and $0.33.

**Guarding evals.** None guards report integrity. Propose **E46 QA artifact integrity** (Code): one report per launched agent, a row per assigned eval, and an unchanged artifact checksum across the round. E45 also applies.

**Validation.** Replay D round 1 from the a977e688 folder with self-writing agents. Pass bar: E45 and E46 pass, and the persistent-versus-mutated classification for round 2 matches the original.

**Risk.** It relaxes a stated rule. Reviewers keep returning full reports, because Gate 2 consolidation needs every finding.

### 7. Deterministic mechanical-check script

**Where:** `references/qa-subagent-briefs.md` mechanical brief (lines 64 through 103) and `<eval_phase_map>` Mechanical rows (lines 281 through 293).

**Change.** A script runs the Code evals E13, E14, E15, E18, E28, E29, E30, E32, E33, E36, E37 and E38 and writes the report. E05 and the manual triplet row of E38 move to the Fidelity judge.

**Saving.** The Haiku agents cost $0.86 in a977e688, $0.53 in 93a3e520 and $0.21 in the revise run, scaled to the logged cost. It also saves 9 launches per create run.

**Guarding evals.** The same Code evals. E38 failed every D and R round on 2 Nov (a Figma node ID false positive), E29 and E37 persisted on 21 Oct, and E29 recurred verbatim on 26 Oct. Those are rubric bugs a script makes visible and repeatable. E05 never failed in a trace, so seed a known phantom alternative into the replay plan.

**Validation.** Run the script on draft-before-D1-fixes.md from the a977e688 folder. Pass bar: verdicts match D-round-1-mechanical.md for every eval, and each `Fail (ambiguous)` goes to Danny.

**Risk.** Low. A script is stricter than a Haiku reading.

### 8. Trace compile script

**Where:** SKILL.md Step 9 items 1 and 2 (lines 237 through 238).

**Change.** A script compiles `eval_results` and `qa_loops` from the qa-reports folder. The parent writes only judgment fields.

**Saving.** Step 9 cost $4.02 in a977e688 at an average 717k context, and the trace JSON is about 16k characters. Removing the compile turns saves about $0.49 per create run [Assumption: half the Step 9 output tokens are compile work (needs validation)], $0.18 after rank 1.

**Guarding evals.** None. E46 covers the report files the script reads.

**Validation.** Run the script on the a977e688 qa-reports folder and diff its output against the 2 Nov trace. Pass bar: identical eval IDs per round and phase.

**Risk.** Low.

### 9. Plan briefs get extracts, not full SKILL.md

**Where:** SKILL.md Step 3 (lines 134 through 196).

**Change.** Each plan brief carries its own section and the ownership contract (lines 138 through 150) as a file. Plan agents stop reading full SKILL.md.

**Saving.** $0.22 in a977e688, where plan agents read SKILL.md; $0 in 93a3e520.

**Guarding evals.** E04, E11 and E42. E11 failed plan round 1 on 2 Nov.

**Validation.** The script check from rank 3: extracted text is byte-identical to SKILL.md.

**Risk.** Low.

### 10. Save MCP sources once to the run folder

**Where:** SKILL.md Step 1 item 2 (line 117).

**Change.** Step 1 writes each Google Doc or Confluence page to `<run>/sources/`. Subagents read those files. 93a3e520 already did this; a977e688 did not and made 16 MCP calls for 2 docs.

**Saving.** About $0 directly. It makes rank 2 possible and keeps every agent on one source version.

**Guarding evals.** E02 and E21. The AGENTS.md MCP no-inference rule still applies at Step 1.

**Validation.** Byte-compare a saved copy with a fresh MCP read of the same doc.

**Risk.** A stale copy if the doc changes mid-run. Record fetch time in the trace.

## 4. What not to cut

| Keep | Reason |
| --- | --- |
| Full re-run on every fix round | Scope regressed from pass to fail four times, Fidelity twice and Mechanical twice across the traces. |
| Fidelity as its own agent | Only Fidelity reads the inputs; E01 failed plan rounds 1 and 2 on 21 Oct and 2 Nov. |
| Opus 5.5 reviewers | They raised 48 findings on 2 Nov and Danny adopted 37 ($9.87). |
| Three plan subagents | Step 3 cost $4.68 and $3.62, and each plan agent already peaks near 260k tokens, so folding them saves little. |
| Sonnet 5 for judgment QA, plans and draft | They make clinical-scope and quote-fidelity calls; E02 and E21 depend on them. |
| Prototype and Figma captures at Step 1 | They feed E43, which failed plan rounds 1 and 2 on 2 Nov. |
| Gate snapshots written verbatim | Rank 1 depends on them as the resume source. |

## 5. Open questions for Danny

1. Rank 1: resume in a new session yourself, or have the parent launch an Opus sub-orchestrator? The first loses nothing but costs you a command per gate.
2. Rank 2: should Fidelity ever spawn its own agents? It happened once, on 21 Oct, for $7.77.
3. Where did the 4 Nov and 5 Nov revise runs run, and was there a fourth? I could not measure them.
4. Decision: the a977e688 run folder is copied to `AI-Best-Practices/Token-Spend/replays/prd-generator/2026-11-02_ai-recommended-next-actions/`, and that path is gitignored. The other two run folders were already gone. Future runs should snapshot the same way.
5. Every phase in every trace hit the 3-round cap except one. E11, E29 and E37 persist across runs, which suggests rubric bugs. Fixing them through evals-advisor would save a round [Assumption: about $2.50 per avoided round (needs validation)] without cutting a check. Want that as a separate plan?
6. In 93a3e520, subagents waited over 5 minutes after Bash calls, costing $2.40 in cache rewrites. Were those permission prompts?
7. Rank 6 lets QA agents write files, which the briefs forbid today. Is that acceptable with the checksum guard?
