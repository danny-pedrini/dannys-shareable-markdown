# evals-advisor: token-efficiency plan

## 1. Answer

Six skill changes would save **$5.38 per future run** and **$16.13 over the 21 Sep 2026 through 2 Nov 2026 window**. One session-level change outside `SKILL.md` would add $10.10 per run and $30.30 in the window, for **$15.48 per run and $46.43 in the window** if Danny adopts it.

The skill itself is cheap. Its own workflow cost $8.30 across its three runs: $5.57 standalone, $1.78 embedded and $0.95 design-time. Most of the $86.92 attributed to it came after the skill finished, in a 13-hour session of follow-on eval authoring.

The $22.02 gap is explained. A background subagent that had already handed back sat idle for about 7 hours. Repeated wake-ups re-wrote its 461,000-token context into the 5-minute cache, and those API requests never logged a response.

Per-run figures average the window's mode mix (one run of each mode) and assume each pattern recurs at its window rate. [Assumption: future runs follow the window's one-in-three rate for each pattern (needs validation)]

## 2. Measured baseline

### Attributed and segmented dollars

| Session | Mode | Rule | Dollars |
| --- | --- | --- | --- |
| `2c925ce8` | Standalone | Attributed (single-skill session) | $86.92 logged |
| `2c925ce8` | Standalone | Skill workflow only: parent turns 0 through 32 | $5.57 |
| `0ce68782` | Embedded (Mode 2) | Segmented, strict rule | $1.96 |
| `0ce68782` | Embedded (Mode 2) | Skill workflow only, plus the Step 5 adoption turn | $1.78 |
| `6a7d3d70` | Design-time (Mode 3) | Segmented, strict rule | $8.41 |
| `6a7d3d70` | Design-time (Mode 3) | Skill workflow only: Skill call through the `evals.md` write | $0.95 |

Window totals: $86.92 attributed, $10.37 segmented under the strict rule, and $8.30 of actual skill workflow.

**Segmentation rule.** Parent turns run from the evals-advisor load signal to the next skill's load signal in the parent. Subagents count only when their `.meta.json` description names an evals-advisor step. In `0ce68782` the load signal is inside subagent `agent-aea50b87`, so the parent segment starts at the turn that launched it (turn 135) and ends at the parent's Read of `dashboard-requirements/SKILL.md` (turn 141). In `6a7d3d70` no later skill loads, so the strict segment runs from turn 313 to the end of the session.

**Skill workflow only.** This tighter cut ends at the skill's own terminal artifact. That is the `evals.md` write in Mode 3, the subagent's handback plus the adoption edit in Mode 2, and the last report draft before the first follow-on subagent in Mode 1. It is reported for comparison, not as attributed spend.

**What the standalone session actually did.** After turn 32, `2c925ce8` stopped being an evals-advisor run. It never read a target skill's `SKILL.md` and never wrote an `evals.md`. Its writes went to Galen Phase 3 eval plans, a persona doc, memory files and a Confluence PRD. Turns 33 through 168 cost $33.75 in the parent, plus $25.59 in subagents and the $22.02 gap.

> **Source:** Claude Code logs in `~/.claude/projects/-Users-dpedrini-Projects-dannys-pm-workspace-care`, sessions `2c925ce8`, `0ce68782`, `6a7d3d70` and their `subagents/`. Window 21 Sep 2026 through 2 Nov 2026, Eastern time. Per-request dollars from `message.usage` per unique `requestId` at the brief's fitted rates; session totals from the last `cost-state` record. Tool targets read structurally from `tool_use` inputs; no message text printed or quoted.

### Check against cost-state

| Session | Computed | Logged | Gap |
| --- | --- | --- | --- |
| `2c925ce8` | $64.91 | $86.92 | 25.3%, explained below |
| `0ce68782` | $66.48 | $62.12 | Computed is 7.0% high because 24 parent request IDs ($4.60, all Opus 5.5) repeat from `6410cf4e`, which this session resumed. Without them Opus 5.5 computes to $40.64, matching the log; Haiku logs $0.24 with no transcript |
| `6a7d3d70` | $172.94 | $173.93 | 0.6% |

The `0ce68782` gap comes from the 24 request IDs it shares with `6410cf4e`; net of them it computes to $61.88 against $62.12 logged. My segment figures use per-request pricing, and none of the shared requests fall in its segments.

In `6a7d3d70`, subagent `agent-adff292a` shares 152 of its 162 request IDs with `agent-a4b5b5c1`. Summing transcripts without deduplication double-counts about $19 there. The table above deduplicates.

> **Source:** same logs and window; `cost-state` `modelUsage` vs per-request dollars deduplicated by `requestId` across parent and subagents.

### Corrections to the earlier pass

- **$22.02 unexplained.** Explained below: unlogged requests from an idle background subagent.
- **"Seven QA check subagents, setup $2.03 of $7.05."** I could not reproduce either figure. The session has eight check agents ($9.03, setup $1.37); the seven QA agents without the final page verify cost $8.59 with $1.25 of setup.
- **$1.74 saving.** Recomputed under the same method: 6 fewer agents at $0.18 average setup is **$1.07**. Those agents checked follow-on change-sets, not evals-advisor output, so it is not a change to this skill (see section 4).
- **$86.92 attributed.** Correct as a session total, but only $5.57 of it ran the skill's workflow.

### The $22.02 gap in `2c925ce8`

Transcripts match cost-state on Sonnet 5 output (527,239 vs 527,351 tokens) and nearly on cache reads (44.08M vs 44.54M). The gap is cache writes: 4,600,807 in transcripts vs 13,370,030 logged. That gap is 8,769,223 tokens, worth $21.92 at $2.50 per million. The read gap of 461,026 tokens adds $0.09.

The missing requests are in subagent `agent-ad5e7479` ("Map marked passages to Confluence nodes"). Its transcript has 112 `api-request` records but only 87 responses. After its last handback at 06:37 UTC on 31 Oct, 24 requests got no response, spaced roughly every 16 minutes until the parent stopped it with `TaskStop` at 13:32 UTC. Each carried about 461,000 tokens of context, idle well past the 5-minute cache.

The arithmetic fits: 19 full re-writes at about 461,500 tokens make 8.77M. One request at 09:14:33 UTC came 3 seconds after a write, and the logged read gap is exactly that context, 461,026 tokens. The remaining 4 unanswered requests were not billed.

The wake-ups were not Danny or the parent: the parent was idle from 06:35 until 13:30 UTC. Four times, an identical 173-character harness message flagged `isMeta` and `turnCompanion` woke the agent. I could not determine why requests got no logged response. [Assumption: stalled streams retried by the client, billed on input (needs validation)]

Counting the logged wake-up turns too, the idle agent cost **$30.30**: $8.28 logged and $22.02 unlogged. Six of the logged turns were full 461,000-token re-writes ($6.92).

> **Source:** `2c925ce8/subagents/agent-ad5e7479e04d3afe8.jsonl`: `api-request` records vs unique `assistant` `requestId`s, `usage` fields, `isMeta`/`turnCompanion` flags and a content hash of the meta message (text not printed). Parent timeline from `2c925ce8` parent `api-request` and `assistant` timestamps.

### Step cost map

Setup follows the brief's rule: calls before the first tool that is not Read, Grep, Glob or ToolSearch. Skill and Bash end setup under that rule, so it reports $0.00 for every step here. The Step 1 rows show the real context-gathering cost.

**Standalone (`2c925ce8`, parent on Opus 5.5)**

| Step | Parent turns | Parent $ | Subagents | Subagent $ | Setup $ |
| --- | --- | --- | --- | --- | --- |
| Load (Skill call) | 0 | $0.52 | 0 | $0.00 | $0.00 |
| Step 1: gather context | 1 through 12 | $1.48 | 0 | $0.00 | $0.00 |
| Steps 2, 3 and 4: analyze, classify, report | 13 through 32 | $3.57 | 0 | $0.00 | $0.00 |
| Step 5: adopt | not run | $0.00 | 0 | $0.00 | $0.00 |
| Follow-on work (not a skill step) | 33 through 168 | $33.75 | 10 | $25.59 logged, $22.02 unlogged | $1.38 |

**Embedded (`0ce68782`, subagent on Sonnet 5, parent on Opus 5.5)**

| Step | Where | Parent $ | Subagents | Subagent $ | Setup $ |
| --- | --- | --- | --- | --- | --- |
| Launch, background wait, receive | Parent turns 135 through 137 | $0.64 | 1 | $0.81 (rows below) | $0.00 |
| Load (Skill call) | Subagent call 1 | | | $0.11 | $0.00 |
| Step 1: gather context | Subagent calls 2 through 10 | | | $0.55 | $0.00 |
| Steps 2, 3 and 4: report | Subagent call 11 | | | $0.14 | $0.00 |
| Step 5: adopt | Parent turn 143 | $0.33 | 0 | $0.00 | $0.00 |

The return to adopt, 3 hours later, began with a $6.40 full re-write of the 792,619-token parent (turn 141). It falls in the dashboard-requirements segment under the strict rule.

**Design-time (`6a7d3d70`, inline in the agent-architect parent on Opus 5.5)**

| Step | Parent turns | Parent $ | Subagents | Subagent $ | Setup $ |
| --- | --- | --- | --- | --- | --- |
| Load, Steps 1, 2 and 3 (design report) | 313 through 315 | $0.57 | 0 | $0.00 | $0.00 |
| Step 4: adopt (read template, write `evals.md`) | 320, 321 | $0.38 | 0 | $0.00 | $0.00 |

Turn 313 also launched agent-architect's own design QA; its $0.22 is counted here in full.

> **Source:** same logs and window; per-turn dollars from `assistant` `usage`; step boundaries from `tool_use` targets (Skill call, Write of scratchpad report files, Write/Edit of `evals.md`).

### Context anatomy

Token counts come from `usage`. Character counts come from the `api-request-shape` and attachment records. The skill text measures 7,399 tokens: the cache write on the turn after the Skill call, less that turn's output.

| Part | Mode 2 subagent at peak (call 11, 153,295 tokens) | Mode 1 parent at end of skill phase (turn 32, 286,866 tokens) |
| --- | --- | --- |
| Base context: system prompt, tool definitions, memory | 39,386 tokens on call 1. Includes 8 tool definitions (31,859 characters) and a 3,223-character brief | 64,387 tokens on turn 0. Includes 15 tool definitions (37,380 characters) and 10,616 characters of system prompt |
| Skill text | 7,399 tokens, plus harness attachments: an agent listing (44,112-character record) and MCP instructions (6,505-character record). Call 2 wrote 18,859 tokens | 7,399 tokens |
| References loaded | None. The skill has no `references/` folder | None in Mode 1. Mode 3 adoption read `agent-architect/references/evals-storage-template.md` and `observability-templates.md` |
| Source payloads | Target `SKILL.md` and `evals.md`: 29,022 tokens. Trace and invocation log: 29,441. Three gates, the consolidated review, a pre-revision copy and 13 QA reports: 29,540 | Read results: 51,617 tokens. Bash results: 35,232. Mixed Bash and Read turns: 21,206 |
| Accumulated turns | 10,474 output tokens before the final report | 107,750 output tokens, including thinking, three report drafts written to scratchpad, and the same reports re-typed in chat |

The Mode 1 parent kept growing after the skill finished: 381,581 tokens at turn 47, 551,501 at turn 99 and 738,641 at turn 168.

**Loads every run, used only sometimes.** No reference files exist. In `SKILL.md`, Mode 3 instructions (lines 345 through 425, 4,038 characters) load in Modes 1 and 2 and go unused. The two worked examples (lines 263 through 320, 2,493 characters) go unused in Mode 3. The inline scaffold (lines 153 through 168) duplicates `agent-architect/references/evals-storage-template.md` and is used only when `evals.md` is missing.

> **Source:** same logs and window; `api-request-shape` `tools` and `system` lengths, `attachment` record types and lengths, `usage` per call. Character counts of `SKILL.md` sections from the committed file.

### Deep-dive findings (brief items 3 through 10)

**3. Duplicate and oversized reads.** The standalone input, the Round 3 cluster analysis, is 326,487 bytes. Its full Read at turn 1 and an 890-line Read at turn 3 both returned too little to be the file; the agent then read it in four chunks. [Assumption: both hit the Read tool's size limit (needs validation)]

In Mode 2 the subagent re-read the target `SKILL.md` and `evals.md` that the parent already held (29,022 tokens), which a fresh context needs. It also read the full 16,546-byte `invocation-log.jsonl` when only the current run's line applies. The skill's own steps made no MCP calls; every Confluence read in `2c925ce8` belongs to follow-on work.

**4. Cache behavior.** Opus 5.5 parents use the 1-hour cache, so idle gaps over an hour forced full re-writes: `2c925ce8` turn 117 ($4.86) and turn 164 ($5.90), and `0ce68782` turn 141 ($6.40).

Sonnet 5 subagents use the 5-minute cache; the idle agent above paid 25 full re-writes. In `2c925ce8`, sibling subagents launched within 5 minutes shared a 12,200-token cached prefix on their first call. The Mode 2 subagent's first call was 100% fresh write (39,384 of 39,386 tokens, $0.10).

**5. Fan-out and loop shape.** Not applicable. `SKILL.md` sets no fan-out, no QA groups and no fix rounds. Mode 2 (lines 333 through 343) and the agent-architect template (`references/evals-advisor-step.md` lines 37 through 61) spawn one subagent.

The skill has no `observability/traces/`, so there is no pass-then-fail history to examine.

**6. Parent-thread growth.** See the context anatomy. The orchestrator held three full report drafts twice each: once as Write input, once as chat text (13,371, 13,189 and 7,057 characters re-typed). The follow-on work carried the whole skill phase (about 219,000 tokens beyond a fresh start) for 136 turns.

**7. Model mix.** Mode 1 and Mode 3 run inline on the session model, Opus 5.5. Mode 2 runs as a general-purpose subagent launched with defaults, on Sonnet 5.

Adoption runs in the parent on Opus 5.5. Haiku appears only in harness side queries ($0.0003 in `2c925ce8`).

This plan moves no role: all of the skill's work is eval-design judgment, and the only mechanical task (checking that `evals.md` is consistent) goes to a script, not a cheaper model.

**8. Tool surface.** The Mode 2 subagent inherited 8 tools and used 3: Skill, Read and Bash. The unused Agent tool definition is 9,048 characters.

The harness also injected the full agent listing into its context (a 44,112-character record), which only matters to an agent that can launch agents. [Assumption: removing the Agent tool also removes the agent listing (needs validation)]

**9. Output verbosity.** Mode 1 re-typed each report in chat after writing it to a scratchpad file. Mode 2 returns the full report (11,382 output tokens, $0.11), which Danny needs to decide adoption; the parent then summarized it in 2,343 tokens rather than echoing it. The scratchpad copies lived under `/private/tmp` and no longer exist, so no report from the window survives outside the transcripts.

**10. Script replacement.** No `scripts/` folder exists. Checking `evals.md` consistency is deterministic: index rows match definition sections, IDs are unique, and each definition has its required fields.

Today that check falls to the QA subagent. Creating the scaffold from the template is also deterministic, but it costs almost nothing as model work.

> **Source:** same logs and window; Read `offset`/`limit` inputs and following-turn cache writes; `cost-state` and per-request `usage`; file sizes from disk.

## 3. Changes, ranked by dollars per future run

### S1. Stop handed-back background subagents (outside `SKILL.md`)

**Touches.** `AGENTS.md`, "Editing files and plans" section, or a hook. Not this skill's text. Danny decides; `.claude/settings.json` stays untouched without his ask.

**Change.** When a background subagent has handed back and no follow-up message is planned, the orchestrator stops it with `TaskStop` before ending its turn. Before a long idle, it runs `ListAgents` and stops anything finished. The parent in `2c925ce8` did exactly this at 13:32 UTC, 7 hours late.

**Saving.** $30.30 in the window, the idle agent's cost after its last handback. Per run: $10.10. [Assumption: an idle background agent recurs in one of three evals-advisor sessions (needs validation)] It is not a skill step, so it is excluded from the skill total.

**Guarding evals.** None exist. Propose **EA-09**: no background subagent records an API request more than 15 minutes after its last handback unless the parent sent it a message after that handback. Code-based, from transcript timestamps.

**Validation.** Replay the timeline of `2c925ce8` under the rule and confirm EA-09 flags `agent-ad5e7479` at its 07:00 UTC request. Pass bar: EA-09 flags it, and no other agent in the three sessions that later received a parent `SendMessage` is flagged.

**Risk.** Stopping an agent that Danny meant to resume loses its context. The rule applies only after handback with no planned follow-up.

### B. Close the run before follow-on work

**Touches.** `SKILL.md` after line 151 (new "Step 6: Close the run"), and Mode 1 lines 324 through 331.

**Change.** After the report, and adoption if any, the skill states that it is done. If Danny continues with work that is not an evals-advisor step, the skill offers to write a handoff with the `handoff` skill and continue in a fresh session. The handoff names the saved report (change C), adopted IDs, pending prompt fixes and any running background agents. The acceptance gate and QA reads are untouched.

**Saving.** $8.53 in the window, from `2c925ce8`. A fresh session would have started the follow-on at about 69,400 tokens (64,387 base plus a 5,000-token handoff) instead of 288,679, saving 219,292 tokens per turn. [Assumption: a 5,000-token handoff carries what the follow-on needed (needs validation)]

That is 134 cached turns at $0.20 per million ($5.88) plus two idle re-writes at $8 per million ($3.51). Less a new base write ($0.56) and a handoff run, that nets $8.53. [Assumption: a handoff run costs $0.30 (needs validation)] Per run: $2.84.

**Guarding evals.** None exist. Propose **EA-06**: when Step 6 fires, the handoff file names the report path, every adopted ID, every unapplied S-item and every running background agent. Code-based presence check. Also **EA-01** (below) to confirm the close step never writes `evals.md`.

**Validation.** Replay `2c925ce8` turn 0 input through turn 32, stop at Step 6, then run the first follow-on task (the writing-quality eval plan) from the handoff. Compare the plan against the version written in the original session. Pass bar: EA-06 and EA-01 pass, the first follow-on turn's context is under 100,000 tokens, and Danny rates the plan as no worse.

**Risk.** Follow-on work can lose conversational nuance that is not on disk. The skill offers the split; Danny can decline.

### C. Save the report to disk so adoption can resume in a fresh session

**Touches.** `SKILL.md` Step 4 (lines 94 through 131), Step 5 (lines 133 through 149), and Mode 2 lines 340 through 343. Also `agent-architect/references/evals-advisor-step.md` lines 50 through 58, which is another skill's file and needs Danny's go-ahead.

**Change.** Step 4 writes the report to `.claude/skills/<target>/observability/evals-advisor/<date>-<mode>.md` (or the run folder if the target has one) before presenting it. Step 5 can then start from that file. If Danny returns after a break, the skill tells him adoption can run in a fresh session that reads the saved report. The user-acceptance gate is unchanged: nothing goes to `evals.md` without his explicit acceptance.

**Saving.** $7.07 in the window, from `0ce68782`. The adoption return re-wrote 792,619 tokens at $8 per million. A fresh session would write about 84,000 (base, saved report, target `evals.md`), saving $5.67.

[Assumption: the saved report is 4,000 tokens and the target `evals.md` 16,000 (needs validation)] The next 10 turns would each carry about 700,000 fewer tokens ($1.40). Per run: $2.36.

**Guarding evals.** **EA-01**: no Write or Edit to any `evals.md` before a user turn that names the IDs to adopt. Code-based, from tool order in the transcript.

**EA-05**: `evals.md` consistency (see change I). **EA-10**: every finding ID in the saved file appears in what Danny saw, and the reverse. Code-based.

**Validation.** Replay the Mode 2 brief from `0ce68782` against `dashboard-requirements` at commit `8eb65fa^`, using the 28 Oct 1300 provider-pay trace in its `observability/traces/`. Then run adoption in a fresh session from the saved file, applying the same accepted items Danny recorded in `dashboard-requirements/evals.md` line 56. Pass bar: EA-01, EA-05 and EA-10 pass, and the resulting `evals.md` diff matches commit `8eb65fa` apart from dates.

**Risk.** A fresh adoption session lacks the run's conversation. The saved report carries the evidence each finding needs, and Danny still accepts item by item.

### D. Show an index in chat instead of re-typing the full report (Mode 1)

**Touches.** `SKILL.md` Step 4 lines 94 through 96, and the adoption prompt at line 135.

**Change.** After saving the report (change C), the chat shows one line per finding (ID, name, Specification or Generalization) and the file path. Danny opens the file to read the evidence.

**Saving.** $0.22 in the window. `2c925ce8` re-typed 33,617 characters, about 11,800 tokens at the measured 2.84 characters per token.

That cost $0.24 in Opus output plus $0.02 of carry through turn 32. An index keeps 15% of it. [Assumption: the index is 15% of the report's length (needs validation)] Per run: $0.07. Carry after turn 32 is counted under change B.

**Guarding evals.** **EA-10**, plus **EA-02**: the saved report has the Step 4 sections, and its "Issues found" count equals the number of S and G items listed. Code-based.

**Validation.** Replay the `2c925ce8` standalone input through Step 4. Pass bar: EA-02 and EA-10 pass, and Danny confirms he can decide adoption from the index plus file. This is a preference call (open question 4).

**Risk.** If Danny prefers reading in chat, this costs him a click per run for $0.07.

### E. Launch the Mode 2 subagent in the foreground

**Touches.** `SKILL.md` Mode 2 lines 333 through 338; `agent-architect/references/evals-advisor-step.md` lines 45 through 58; `dashboard-requirements/SKILL.md` line 172; `acceptance-testing-generator/SKILL.md` lines 679 and 680. The last three belong to other skills.

**Change.** The calling skill waits for the evals-advisor subagent instead of running it in the background. That removes the parent's empty acknowledgment turn.

**Saving.** $0.18 in the window: `0ce68782` turn 136, an empty turn at 783,506 tokens. Per run: $0.06. It scales with the parent's size, which is large by the end of a generated skill's run.

**Guarding evals.** **EA-02** (report complete) and **EA-01**.

**Validation.** Replay the `0ce68782` Mode 2 brief in the foreground. Pass bar: EA-01 and EA-02 pass, and the parent makes one turn between launch and presenting the report.

**Risk.** Danny cannot chat with the parent for the 7.5 minutes the subagent ran.

### F. Read oversized inputs by section, and only the current run's log line

**Touches.** `SKILL.md` Step 1, lines 51 through 58.

**Change.** For a run output too large for one Read, list its headings first (Grep for `^#`) and read by offset, rather than attempting a full read. Read only the current run's line from `invocation-log.jsonl`. Every section is still read; only the failed attempts go away.

**Saving.** $0.08 in the window: the failed 890-line Read turn in `2c925ce8` ($0.06) and the full invocation log in `0ce68782` ($0.02). Per run: $0.03.

**Guarding evals.** **EA-04**: the Read calls on the run output together cover every line of the file. Code-based, from Read offsets and limits against the file's line count. **EA-03**: each S and G item's "Observed" line names a file and section the agent actually read. Code-based.

**Validation.** Replay the `2c925ce8` standalone input. Pass bar: EA-03 and EA-04 pass, the finding list matches the original report's IDs and names, and Step 1 takes one turn fewer.

**Risk.** Section-first reading could skip text between headings. EA-04 catches that.

### G. Give the Mode 2 subagent only the tools it uses

**Touches.** `SKILL.md` Mode 2 lines 333 through 343 and the agent-architect template lines 45 through 58. Needs a new agent definition (for example `.claude/agents/evals-advisor.md`) with `tools: Read, Grep, Glob, Bash, Skill, Edit, Write` and the session's current subagent model.

**Change.** Spawn Mode 2 as that agent type instead of general-purpose. Edit and Write stay for a resumed adoption. Only the Agent tool goes, and with it the agent listing.

**Saving.** $0.05 in the window, from the one Mode 2 run. The cut is about 11,600 tokens: the Agent definition (about 2,600) plus the agent listing (about 9,000). [Assumption: tool JSON runs 3.5 characters per token; the listing is what remains of call 2's write (needs validation)] That is one 5-minute write at $2.50 per million and 10 reads at $0.20 per million. Per run: $0.02.

**Guarding evals.** **EA-02** and **EA-03**. The trace supports the change: `agent-aea50b87` made zero Agent calls.

**Validation.** Replay the `0ce68782` Mode 2 brief with the new agent type. Pass bar: EA-02 and EA-03 pass, the findings match the original's IDs and names, and the first call's context is at least 9,000 tokens smaller.

**Risk.** Low. Mode 2 never launches agents.

### H. Run Modes 1 and 3 in a fresh subagent when the parent is long

**Touches.** `SKILL.md` Mode 1 lines 324 through 331 and Mode 3 lines 345 through 357.

**Change.** When the invoking thread is over 300,000 tokens, run Steps 1 through 4 in one fresh subagent on the session model, not a cheaper one. Its brief lists every issue Danny already flagged in the thread (the skip rule at line 79). The parent keeps the acceptance gate and adoption.

**Saving.** $0.00 in the window and $0.00 per run at the current mix. Neither inline run qualified: `2c925ce8` loaded at 64,387 tokens and `6a7d3d70` at 215,812.

Break-even is near 285,000 tokens. An Opus base write costs about $0.39, and each of 10 turns saves the context above 90,000 tokens at $0.20 per million. [Assumption: 10 turns per run and a 90,000-token subagent context (needs validation)] At 700,000 tokens it would save about $0.83 per run.

**Guarding evals.** Propose **EA-07**: no finding duplicates an issue the brief lists as already flagged by Danny. LLM judge, because matching an issue to a finding needs interpretation. Also **EA-02**, **EA-03**, and for Mode 3 **EA-08**: the Coverage Check table lists every D4 failure mode with an eval ID or a marked gap. Code-based.

**Validation.** Replay the `6a7d3d70` design-time inputs inside a padded 400,000-token thread, both inline and in a subagent. Compare against `provider-draft-failure-modes/evals.md` at commit `a798459`. Pass bar: EA-02, EA-03, EA-07 and EA-08 pass in both, and the subagent run covers the same D4 failure modes as `a798459`.

**Risk.** A subagent loses context the brief does not carry. Keep it conditional.

### I. Add `scripts/check_evals_md.py` (no dollar estimate)

**Touches.** `SKILL.md` Step 5 lines 137 through 149, and a new `scripts/` folder.

**Change.** After an adoption write, run the script. It confirms each index row has a definition section, IDs are unique, and every definition has Pass, Fail, Check type, a `check` or `judge` block, Source and Added. The independent QA subagent still reads every changed file. It gets the script's result instead of counting rows by hand.

**Saving.** No estimate. The QA agent after the `0ce68782` adoption (`agent-abea9df8`, $1.19) made 31 Bash calls, but I cannot tell from tool inputs alone which were structural counting. It saves no launches.

**Guarding evals.** **EA-05**: the script's checks become the eval. The validation below supplies the first test cases.

**Validation.** Run the script on `dashboard-requirements/evals.md` at `8eb65fa^` and `8eb65fa`, and on `provider-draft-failure-modes/evals.md` at `a798459`. Pass bar: no false failures on any of the three, and a deliberately broken copy (one index row deleted) fails.

**Risk.** A rigid parser may reject valid formatting variations. Tune it on the three committed files.

## 4. What not to cut

- **User-acceptance gate before any `evals.md` write** (lines 28 and 133 through 135). Danny's record of the 28 Oct adoption (`dashboard-requirements/evals.md` line 56) lists suggestions not adopted and suggestions held for a second occurrence. The gate filters real output.
- **Independent QA read of every changed file.** In `0ce68782`, the parent edited `evals.md` again at turn 147, after the QA agent launched at turn 145.
- **Per-change-set QA in follow-on work.** The earlier report's evals-advisor change (one batched QA at the end) targets the seven QA agents in `2c925ce8`. Each checked a different change-set, launched between 04:15 and 05:34 UTC, and `AGENTS.md` requires one QA subagent per change-set. `SKILL.md` has no QA step for that change to edit.
- **Mode 2's full Step 1 reads** ($0.55 of $0.81). The 28 Oct post-run eval E40 rests on reviewer evidence (`dashboard-requirements/evals.md` line 791), and the subagent's Step 1 reads included `reviews/consolidated.md`.
- **Mode 2's full report return** ($0.11). Danny decides adoption from it; the parent already summarizes it instead of echoing it.
- **Skill text.** At 7,399 tokens, moving Mode 3 or the examples to references saves under $0.04 per run and adds a Read turn in the mode that needs them.
- **Models.** Mode 1 and Mode 3 stay on the session model, and Mode 2 stays on Sonnet 5. All of it is eval-design judgment, and `2c925ce8` applied it to clinical provider-draft evals.

## 5. Open questions for Danny

1. Was `2c925ce8` an evals-advisor run? `SKILL.md` targets Claude Code skills and their `evals.md`. That session aimed it at Galen product evals and never wrote an `evals.md`.
   If product-eval design is out of scope, $81.35 of the $86.92 should leave this skill's attribution. If it is in scope, should `SKILL.md` say so?
2. Do you know what sends the `turnCompanion` meta message that woke the idle background agent? Should change S1 live in `AGENTS.md`, a hook, or a Claude Code setting?
3. Would you take a fresh-session handoff after an evals-advisor run as the default offer (change B)?
4. Do you want reports in chat or in a file with a chat index (change D)?
5. Is a blocking foreground Mode 2 run acceptable (change E)? It also edits two other skills and the agent-architect template.
6. Where should saved reports live: the target skill's `observability/evals-advisor/`, or the run folder when one exists (change C)?