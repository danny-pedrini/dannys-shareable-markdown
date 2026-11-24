# agent-architect: token-efficiency plan

## 1. Answer

Five changes would save about $1.85 per future agent-architect run, which is 11.5% of the $16.04 mean measured run. Over 21 Sep 2026 through 2 Nov 2026 they would have saved $7.23 of agent-architect's own spend. Separately, the template changes would have saved $17.19 downstream in the skills agent-architect generates, and most of that overlaps the per-skill plans.

- **Own run, per future run:** $1.31 from a pre-flight handoff to a fresh session, $0.39 from a local-only grader agent type, $0.14 from splitting SKILL.md and $0.005 from removing a duplicated template.
- **Own run, window:** $5.23, $1.56, $0.42 and $0.02 for the same four changes.
- **Downstream, window:** $15.05 from the grader agent type and $2.14 from a scripted observability check. Count the $15.05 once across all plans, since every per-skill plan that adds `tools:` fields claims part of it.
- **Without the riskiest change** (the handoff), the own-run saving falls to $0.54 per run.

Two baseline numbers were wrong. Session `8bf3a6b5` ($0.26) carried no skill text, so the attributed skill-text cost is $0.00. Session `6a7d3d70` computes 12.6% above its logged cost until request IDs that fork subagents share are deduplicated; after that it is 0.4% below.

## 2. Measured baseline

> **Source:** Claude Code logs in `~/.claude/projects/-Users-dpedrini-Projects-dannys-pm-workspace-care`. Window: sessions whose first record falls 21 Sep 2026 through 2 Nov 2026, Eastern time (84 sessions, including 8 zero-cost copies). Per-request dollars at the fitted rates in the brief, each request ID priced once per session across the parent and every subagent transcript. Session totals land within 0.6% of `totalCostUSD` on the last `cost-state` record.

### 2.1 Attributed and segmented dollars

| Session | Type | Logged $ | Agent-architect $ (strict segment) | Parent part | Subagent part |
| --- | --- | --- | --- | --- | --- |
| `8bf3a6b5` | Single (attributed) | $0.26 | $0.00 of skill text | $0.26, all base context | none |
| `6a7d3d70` | Mixed, new build (provider-draft-failure-modes) | $173.93 | $32.90 | $1.69 | $31.21, 6 agents |
| `57fea835` | Mixed, new build (journey-map) | $35.28 | $20.27 | $18.04 | $2.23, 4 agents |
| `62e199c0` | Mixed, edit (prd-generator rewire) | $13.30 | $7.73 | $4.74 | $2.99, 2 agents |
| `69239f47` | Mixed, edit (dashboard-requirements v1.4) | $7.02 | $3.26 | $0.83 | $2.43, 2 agents |

Segmented total: **$64.16** across four runs, a mean of $16.04 per run. Attributed total: $0.26.

**Segmentation rule.** Parent requests run from agent-architect's load signal up to the request before the next load signal for a different skill. Signals are a `Skill` call, a slash-command record or a `Read` of a `SKILL.md`. A subagent counts when its `.meta.json` description names an agent-architect step: design QA, skill-reference drafting, script build, replay against the skill, or QA of skill edits. String mentions do not count.

**Why `8bf3a6b5` is not a skill run.** The session has one request. Its response is the `Skill` call, and no later request carried the skill text. The $0.26 is a 65,257-token 1-hour cache write of base context on Sonnet 5.5, plus 269 output tokens. It started 12 seconds before `69239f47`, which ran the same skill.

**Outside the strict segments.** Parent requests 306 through 384 of `6a7d3d70` ($9.73) and requests 3 through 29 of `69239f47` ($3.77) did agent-architect work. Each followed a `Read` of the target skill's `SKILL.md`, which the rule treats as a new load signal. That $13.50 is not counted.

**One request stream, two files.** In `6a7d3d70`, the "Build and test skill scripts" agent and a fork named "QA section 6a edit against scripts" share 162 request IDs. They count once, at $21.39.

### 2.2 Step cost map

Parent dollars are bucketed between subagent launches. For `6a7d3d70` and `69239f47`, the parent column uses the extended range, since the strict range holds no complete step; those dollars are labeled and sit outside the $64.16. Setup means calls before the first tool that is not `Read`, `Grep`, `Glob` or `ToolSearch`.

| Step (SKILL.md lines) | Parent $ | Subagents | Subagent $ | Setup share |
| --- | --- | --- | --- | --- |
| Skill load and pre-flight (lines 51 through 118) | $0.72 in `6a7d3d70` requests 300 and 301 at about 950,000 tokens of context; $0.31 in `69239f47`; $3.25 in `57fea835`, a cold resume after an 18-hour gap | 0 | $0 | not applicable |
| Discover and design (lines 267 through 987) | $3.01 (`6a7d3d70`, extended); $0.68 (`62e199c0`); $1.75 (`69239f47`, extended); `57fea835` design and draft are not separable, $10.11 combined | 3 plan or design QA agents | $3.70 | $0.86 (23%) |
| Draft (lines 988 through 1218) | $5.20 (`6a7d3d70`, extended); $3.81 (`62e199c0`); $2.44 (`69239f47`, extended) | 3 producer agents (`6a7d3d70`) | $26.36 | $0.42 (2%) |
| Evaluate (lines 1219 through 1307) | $3.21 (`6a7d3d70`, extended); $7.94 (`57fea835`) | 8 QA, replay and evals-advisor agents | $8.80 | $1.36 (15%) |
| Deliver, observability, evals (lines 1308 through 1676) | $0.25 (`62e199c0`); $0.41 (`69239f47`, extended) | evals advisor counted under Evaluate | $0 | not applicable |

Across all 14 counted subagents, setup was $2.64 of $38.86 (6.8%). The single largest cost is the script-build agent in `6a7d3d70`: 164 requests, peaking at 618,927 tokens of context, $21.39.

### 2.3 Context anatomy

> **Source:** same logs and window. Character counts from the first-turn attachment and request-shape records. Tokens use 3.2 characters per token, fitted on one sample (`69239f47` plan QA: 155,500 characters against 48,659 tokens). [Assumption: the ratio holds for other agents (needs validation)]

**Typical subagent** (general-purpose, mean of 761 transcripts in all logs; first call 46,412 tokens):

| Component | Characters | About tokens |
| --- | --- | --- |
| Deferred MCP tool listing | 43,789 | 13,700 |
| Skill listing | 33,734 | 10,500 |
| Built-in tool definitions | 31,280 | 9,800 |
| Instructions (`CLAUDE.md`, memory index) | 17,316 | 5,400 |
| Sandbox text | 9,798 | 3,100 |
| System prompt | 2,910 | 900 |
| Brief | 3,727 | 1,200 |
| Skill text loaded | none by `Skill`; three agents read agent-architect SKILL.md slices of 8,992, 1,546 and 1,295 tokens | |
| References loaded | `observability-templates.md` in full by 2 agents at 7,825 tokens each; `qa-subagent-pattern.md` (2,135) and `evals-storage-template.md` (2,023) by 1 agent each | |
| Source payloads and accumulated turns | peaks of 149,037, 210,541, 254,174 and 266,785 tokens for the QA agents in each run | |

**Parent at its peak turn** (`57fea835`, 663,990 tokens):

| Component | About tokens |
| --- | --- |
| Base context (first request of a fresh session, `69239f47`) | 65,068 |
| Prior unrelated thread held at skill load | 340,913 |
| SKILL.md loaded by `Skill` (measured in three sessions: 35,840, 36,044 and 36,336) | 36,044 |
| References read in full (all four) | 13,100 |
| Turns and source payloads accumulated during the run | 208,865 |

**Loaded every time, used only sometimes.** The `Skill` tool injects all 2,154 lines of SKILL.md on every load. These sections serve only one path or one artifact type:

| Section (lines) | About tokens | Used when |
| --- | --- | --- |
| Fast path (120 through 265) | 1,400 | Fast Path runs only; 0 of 4 window runs |
| Post-deployment iteration (1418 through 1597) | 1,700 | Only when the user opts into iteration support |
| Knowledge base: tools reference and external APIs (1677 through 1857) | 4,100 | Only when designing a new tool set |
| Worked example (1869 through 2085) | 3,500 | Rarely; no run shows a need for it |

On a Fast Path run, everything after line 266 except observability and evals (about 28,500 tokens) would go unused. The window has no Fast Path run. Edits need little of the file: `62e199c0` read only lines 829 through 892, about 1,300 tokens. In references, `observability-templates.md` section 5 (lines 318 through 428) applies only to skills with mandatory gates, yet both full reads loaded it.

### 2.4 Duplicate and oversized reads

| Item | Count | Dollars |
| --- | --- | --- |
| Files read by more than one agent-architect subagent in the same run | 4 runs; 330,540 duplicate tokens | $1.89 |
| SKILL.md re-read by the parent after auto-compaction (`6a7d3d70` requests 303 and 304) | 3 slices, about 16,800 tokens | about $0.40 [Assumption: 80 later turns at the Opus 5.5 read rate (needs validation)] |
| `observability-templates.md` read in full when one section was used | 4 reads (2 parent, 2 subagent) | $0.08 for the subagent reads |
| Eval-runner template duplicated across `evals-storage-template.md` lines 93 through 125 and `evals-advisor-step.md` lines 9 through 35 | both files read together in 2 runs | $0.01 |

Most of the $1.89 is graders re-reading the target skill's files and the round folder. Fresh-context grading requires that, so it stays. No MCP payload (Jira, Confluence, Google Docs, Slack, Figma) was read by more than one agent-architect-step agent.

### 2.5 Cache behavior

- **Cold parent rewrites.** `57fea835` request 74 wrote 405,979 tokens ($3.25) after an 18-hour gap. `69239f47` request 16 wrote 173,694 tokens ($1.39) after an overnight gap. Both are 1-hour expiries caused by user pauses, not skill text.
- **Compaction.** `6a7d3d70` loaded the skill into a 968,901-token thread; the next request compacted to 90,342 tokens ($0.62) and dropped the skill text.
- **Subagent 5-minute expiries.** Five agent-architect-step agents rewrote nearly their whole context mid-run: the script builder 3 times, the two reference writers, cross-file QA and the rewire-plan QA. Together that is 1.89 million tokens, or $4.73 at the Sonnet 5 write rate.
- **Sibling prefixes.** Siblings launched together share only about 11,800 tokens of cached prefix (system plus tool definitions); every attachment after that is a fresh write per sibling. Eight of the 14 counted agents launched alone and wrote 100% of their first call fresh; siblings wrote about 75%.

### 2.6 Fan-out and loop shape

- **Fresh grader per fix round, max 2 rounds:** SKILL.md lines 850, 1258 and 1304; `qa-subagent-pattern.md` lines 51 and 117 through 121; autonomous loop at SKILL.md line 612.
- **One grader per judge eval:** `evals-advisor-step.md` line 21 and `evals-storage-template.md` line 108.
- **Verification subagent every run, fresh re-verify after a fix:** `observability-templates.md` lines 268 through 292.
- **Agent-architect's own traces:** not applicable. The skill has no `observability/` folder and no `evals.md`.
- **Downstream regressions:** prd-generator's traces record 24 evals that passed one round and failed the next, across 18 round transitions in 5 traces. Dashboard-requirements and acceptance-testing-generator traces do not record per-round results, so they give no evidence either way.

### 2.7 Parent-thread growth

| Session | Context at skill load | Peak | Mean per turn | Turns |
| --- | --- | --- | --- | --- |
| `6a7d3d70` | 932,565 | 968,901 before compaction, then 409,547 | 388,295 (strict) | 6 strict, 85 extended |
| `57fea835` | 405,981 | 663,990 | 575,888 | 89 |
| `62e199c0` | 238,289 | 358,031 | 301,515 | 27 |
| `69239f47` | 65,068 | 199,050 | 169,683 | 29 |

The largest parent cost is starting agent-architect inside a long, finished thread. In `57fea835`, 340,913 tokens of a finished make-deck thread rode along for 89 turns. In `62e199c0`, the prior thread was the rewire's direct input, so a fresh session would have lost needed context.

In `57fea835`, the parent also read the rendered slide image 3 times and the render script 4 times at about 600,000 tokens of context. A visual-QA subagent already existed for that check.

### 2.8 Model mix

| Role | Model |
| --- | --- |
| Orchestrator (4 mixed sessions) | Opus 5.5 |
| Orchestrator (`8bf3a6b5`) | Sonnet 5.5 |
| Every agent-architect-step subagent (design QA, producers, replay, edit QA, evals advisor) | Sonnet 5, general-purpose default |
| Reviewer personas from Step 2.5a | none launched inside agent-architect segments |

No model change is proposed. Every subagent in these runs does judgment work (design QA, drafting, fidelity replay), not mechanical work.

### 2.9 Tool surface

All 12 reviewer agents in `.claude/agents/` carry `model: opus` and no `tools:` field. Both come from SKILL.md lines 798 through 809. MCP tools are deferred behind `ToolSearch`, so the inherited cost is the deferred-tool listing plus the skill listing: about 77,500 characters, or 24,200 tokens, per agent. `claude-code-guide`, which has a restricted tool list, receives neither listing.

QA graders still need MCP sometimes: 98 of 390 QA-named general-purpose agents called an MCP tool, as did 5 of 33 reviewer launches (all logs).

### 2.10 Output verbosity and script replacement

**Verbosity:** not material. Background launches return a short acknowledgment, and graders write reports to files. The four synchronous QA reports in `62e199c0` were 6,246, 6,884, 8,582 and 6,562 characters, about $0.01 of parent reads each.

**Script replacement:** the verification subagent in `observability-templates.md` lines 276 through 288 runs 9 checks. Eight are mechanical: the log entry exists, its outcome matches the file on disk, the timestamp is recent, the trace is valid JSON, source paths exist, output paths exist, every tool call has a purpose, and the two outcomes match. provider-draft-failure-modes already scripts this kind of check (`scripts/log_check.py`). The Phase 4 checks that test structure could also run as a lint script before the grader: labeled sections, frontmatter, a "When NOT to Use" line per tool, a stop message per tool.

## 3. Changes, ranked by dollars per future run

C4 ranks on its downstream saving ($2.14 in the window); its own-run saving is $0.

### C1. Pre-flight: offer a handoff when the thread holds a finished, different task ($1.31 per run, own)

**Touches:** SKILL.md lines 83 through 97 (Pre-Flight Assessment).

**Change:** Add a fourth pre-flight check. If the thread already holds a finished task that is not this build's input, offer to write a handoff with the existing `handoff` skill and continue in a new session. If the user declines, or the prior work is the build's input, continue in place.

**Saving:** In `57fea835`, a fresh start would carry 335,913 fewer tokens per turn for 88 turns: $5.91 at $0.20 per million. Subtract the handoff turn ($0.16) and the new session's base write ($0.52), for $5.23.

The rule would not fire in the other three runs: `6a7d3d70` auto-compacted, `62e199c0`'s prior work was the input and `69239f47` was already fresh. Window: $5.23; per run: $1.31. [Assumption: a handoff file is 5,000 tokens (needs validation)] [Assumption: future runs resemble the window mix of 1 in 4 runs started in a finished, unrelated thread (needs validation)]

**Guarding evals:** none exist. Propose **AA1** (Judge): the handoff file names every file path, decision and open question the build later used; pass when the replayed build cites nothing that the handoff lacks. No trace evidence exists, since agent-architect has no traces.

**Validation:** Replay the `57fea835` journey-map build from a handoff written at request 74. Compare the "Independent QA of journey-map skill" findings and the generated skill's `evals.md` results with the original. Pass bar: the same FAIL set from the independent QA, no new escalation, AA1 passes, and segment cost drops at least $3.

**Risk:** Lost context, since the prior thread can hold the user's intent in ways a handoff misses. That is why the rule offers and never forces. Duplicates the todo-manager plan's long-thread change; the QA pass may prefer one workspace-level rule.

### C2. Local-only grader agent type with a `tools:` allowlist ($0.39 per run own; $15.05 window downstream)

**Touches:** SKILL.md lines 768 through 769 (Minimum Viable Toolset), lines 846 through 876 (Step 2.6), lines 1292 through 1305 (Phase 4 QA); `qa-subagent-pattern.md` lines 59 through 66 (Agent tool call in the template); `evals-advisor-step.md` line 21; `observability-templates.md` lines 270 through 274. Also one new file, `.claude/agents/local-grader.md` [Assumption: name (needs validation)].

**Change:** Define one agent type for graders and producers that read only local files: `tools: Read, Grep, Glob, Bash, Write`, no `ToolSearch` and no `Skill`, and the same model the general-purpose default uses today. The templates name this type for any grader whose brief lists no MCP source. Graders that check a live source keep general-purpose. Reviewer personas are unchanged.

**Saving:** About 24,200 tokens off each launch: one 5-minute write plus a read on every later turn. For the 12 eligible agents in agent-architect's runs, that is $1.56, or $0.39 per run.

Downstream, sessions touching the five generated skills had 166 eligible QA-named agents worth $16.61; minus agent-architect's own $1.56, that leaves $15.05, about $0.10 per grader launch. All logged skills together: $29.22. [Assumption: an allowlist without `ToolSearch` and `Skill` drops both listings for custom agents, as it does for `claude-code-guide` (needs validation)]. Do not use 24,200 until the provider-draft-failure-modes change 1 test launch measures the drop, and use that measurement here.

evals-advisor change E also edits `references/evals-advisor-step.md` lines 45 through 58, so apply the two edits together.

**Guarding evals:** none in agent-architect. Propose **AA2** (Code): every grader brief that names an MCP source uses general-purpose, and every brief that names only local paths uses the local grader. Downstream, prd-generator **E18** (Unopenable Source) and acceptance-testing-generator **G1** (Misquoted source) would catch a grader that lost a source. No trace shows E18 failing, so its catch is untested.

**Validation:** Rerun the "QA the v1.4 skill edits" brief (`69239f47`) and the "QA the rewired prd-generator skill" brief (`62e199c0`) on the file versions committed at the time, using the new type. Pass bar: identical PASS or FAIL on every check, first-call context at least 20,000 tokens smaller, zero tool-unavailable stops.

**Risk:** A grader that does need MCP would stop under Step 2.5b. That is safe but costs a rerun. Model drift if the type's `model:` alias resolves differently from today's default (open question 2). Duplicates every per-skill plan that adds `tools:` fields; count the downstream dollars once.

### C3. Split SKILL.md into a core plus on-demand references ($0.14 per run, own)

**Touches:** SKILL.md lines 120 through 265, 1418 through 1597, 1677 through 1857 and 1869 through 2085. They move to `references/fast-path.md`, `references/iteration-support.md`, `references/tools-reference.md` and `references/worked-example.md`. Each original spot keeps a one-line pointer.

**Change:** Move the four sections out of the loaded file, about 10,700 tokens. Hard constraints, pre-flight, Steps 2.5a through 2.7, Phase 4 verdict logic, observability and evals stay in the core.

**Saving:** 8,700 net tokens per load. [Assumption: a Full Process run reads back one moved section of 2,000 tokens (needs validation)] That is $0.07 for the 1-hour write on Opus 5.5, plus $0.07 for reads over a mean of 40 later turns in the three runs that loaded through `Skill`. Window: 3 loads, $0.42. A Fast Path run would read `fast-path.md` and skip nothing new; the saving there is unmeasured, since no window run took that path.

**Guarding evals:** propose **AA3** (Code): every line of hard constraints (lines 19 through 49), Step 2.5b and Step 2.6 survives verbatim in the core, and every pointer opens. No trace evidence exists.

**Validation:** Replay the `69239f47` dashboard-requirements v1.4 edit with the split file. Pass bar: the plan QA and edit QA return the same verdicts, the `Skill` load is 27,500 tokens or less, and AA3 passes.

**Risk:** The model skips a moved section it needed, for example the tools reference on a new MCP-heavy build. Each pointer names its trigger, which mitigates this.

### C4. Script the mechanical observability checks (downstream: $2.14 window; own: $0)

**Touches:** `observability-templates.md` lines 268 through 296, plus a new template script, `references/verify_observability.py` [Assumption: name (needs validation)].

**Change:** Generated skills run the script for the eight mechanical checks; per Step 2.6 (SKILL.md line 853), its output counts as the verdict. The judgment check stays with a fresh agent: "decisions captures non-default choices", plus gate evidence under section 5. That agent's brief drops the eight checks.

**Saving:** Five trace-verifier or trace-author agents cost $5.34 in the window. [Assumption: 40% of their turns run the mechanical checks (needs validation)] That gives $2.14. No agent is removed.

**Guarding evals:** propose **AA4** (Code): the script's result matches the recorded `verified` flag on every existing trace. Downstream, acceptance-testing-generator's trace-audit reruns in session `93a3e520` show the current agent catching something, but the cause was not read.

**Validation:** Run the script over every existing trace in the four downstream skills with observability. Pass bar: identical outcome on each mechanical check against the recorded verifications.

**Risk:** Low for mechanical checks. The judgment check must not be dropped. Duplicates provider-draft-failure-modes (which already has `log_check.py`) and any per-skill plan that scripts trace checks.

### C5. Remove the duplicated eval-runner template ($0.005 per run, own)

**Touches:** `evals-storage-template.md` lines 93 through 125.

**Change:** Replace the block with a pointer to `evals-advisor-step.md` Step 1. The two copies differ in one line, the code-check sentence (line 107 versus line 20). Keep the `evals-advisor-step.md` wording, which says the check's result is recorded unchanged.

**Saving:** About 450 tokens in the two runs that read both files, $0.02 over the window.

**Guarding evals:** propose **AA5** (Code): exactly one eval-runner template exists across the references. No trace evidence exists.

**Validation:** Diff the two blocks before the edit. Pass bar: the only difference is the code-check sentence, and the kept copy has the stricter wording.

**Risk:** None found.

### C8. Lint script for the structural Phase 4 checks (no dollar estimate)

**Touches:** SKILL.md lines 1223 through 1240 and 1263 through 1290, plus a new `scripts/lint_skill.py`.

**Change:** The orchestrator runs the script before spawning the grader, as Step 2.6 already allows. Checks: frontmatter fields, labeled sections, a "When NOT to Use" line per tool, a stop message per tool, and a stated `tools:` decision per subagent. The grader still runs every check.

**Saving:** Not estimated. It removes no launch and may shorten grader turns.

**Guarding evals:** propose **AA6** (Code): lint output matches the grader's verdict on the same checks across the four window runs' final skill files.

**Validation:** Run the lint over the four skills edited or built in the window. Pass bar: agreement with each run's last QA verdict on every structural check.

**Risk:** False confidence if the grader starts trusting lint. The grader brief does not mention lint results.

### C6. Batch judge-eval graders that read the same inputs (launches only)

**Touches:** `evals-advisor-step.md` line 21; `evals-storage-template.md` line 108; SKILL.md lines 1292 through 1305.

**Change:** One grader per group of judge evals that share inputs, with a report-completeness check (each report covers exactly its assigned eval IDs). This replaces one grader per eval.

**Saving:** No agent-architect dollars. Downstream, it duplicates prd-generator ($2.66 in the earlier report), dashboard-requirements and evals-advisor ($1.74), which already batch or plan to.

**Guarding evals:** prd-generator **E10** (Draft Fidelity) and **E02** (Hallucination). In the 21 Oct 2026 prd-generator trace, E10 passed draft round 1 and failed round 2, and E02 passed plan round 1 and failed round 2. The batched grader must still run both on every round.

**Validation:** Replay the 21 Oct 2026 prd-generator run with batched graders. Pass bar: the same failing eval IDs in every round.

**Risk:** Attention dilution in a grader with too many evals. Cap each group at the evals that share one input set.

### C7. Fix-round graders reuse the first grader's saved source reads (launches only)

**Touches:** `qa-subagent-pattern.md` lines 28 through 33 and 117 through 121; SKILL.md lines 848 through 851.

**Change:** The first grader saves its full read of each external source to a file. Later fresh graders read that file and reopen a source only for a missing field or a disputed verdict. The fresh grader still re-grades the full artifact.

**Saving:** No agent-architect dollars; no agent-architect-step agent reopened an MCP source. Downstream, the provider-draft-failure-modes plan rejects this pattern for dedup QA (it removes the independent reread `clustering-and-dedup.md` section 13 requires) and could not reproduce the earlier $7.19.

**Guarding evals:** provider-draft-failure-modes dedup QA checks (per its own plan); prd-generator **E21** (Source Mechanism Distortion).

**Validation:** Replay one fix-round grader that reads a verbatim saved copy and one that reopens the source. Pass bar: identical verdicts, and the saved copy is byte-identical to a fresh read. Do not apply to dedup QA.

**Risk:** A stale saved read. The saved file records its read time, and a grader reopens the source when the file predates the artifact's last source fetch.

## 4. What not to cut

- **A fresh grader on every fix round, re-running the full eval set:** prd-generator traces show 24 pass-then-fail regressions across 18 round transitions.
- **Producer and grader separation:** held fixed by the brief, and SKILL.md lines 33 through 35 make it a hard constraint that every generated skill inherits.
- **Reviewer personas on Opus, with full tool access:** held fixed; 5 of 33 reviewer launches read Google Docs through MCP, so a `tools:` allowlist would break them.
- **Graders re-reading the target skill's files:** that is $1.89 of duplicate reads over four runs, but each grader must read the edited files in fresh context.
- **MCP access for source-checking graders:** 98 of 390 QA-named graders called MCP tools; C2 applies only to local-only briefs.
- **Full observability by default:** the prd-generator traces are the only evidence of the regressions above.
- **The judgment half of observability verification:** C4 scripts only the mechanical checks; "decisions" and gate evidence stay with an agent.

## 5. Open questions for Danny

1. Does a custom agent with a `tools:` allowlist (no `ToolSearch`, no `Skill`) drop the deferred-tool and skill listings, as `claude-code-guide` does? One test launch settles C2's $0.10 per grader.
2. Which model would a custom grader's `model:` value resolve to? Today's graders run on Sonnet 5, and C2 must not move them.
3. Is offering a handoff acceptable when you start agent-architect in a long thread? `57fea835` built journey-map the day after the make-deck work it came from.
4. Should edits to existing skills get their own short path? Two of four window runs were edits, and the pre-flight covers only new builds.
5. Five agent-architect-step subagents paid $4.73 in 5-minute cache expiries mid-run. Is a 1-hour subagent cache worth testing at the settings level? That is outside this skill's text.
6. Should `8bf3a6b5` count as a run? It is an aborted start that loaded no skill text.
