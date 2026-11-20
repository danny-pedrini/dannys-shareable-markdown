# Token-efficiency plan: dashboard-requirements

## 1. Answer

Eight changes would cut a future create run by about **$10.12**, from a measured $65.39 (15%), without dropping a check or moving judgment off its model. In the 21 Sep 2026 through 2 Nov 2026 window the same changes would have saved **$10.12**, because the window holds one measured create run. The 29 Oct revise run has no Claude Code transcript, so its saving is unknown.

One change carries more than half the money: offering Danny a `/compact` right after the Gate 2 snapshot is written ($5.60 per run). It needs his call, because it touches the chat-memory risk v1.4 was built to guard. The other seven are skill-text and script changes worth $4.52 combined.

The earlier pass misread this skill. Session `6410cf4e` ($13.03) is not a separate run, and its orchestrator never wrote a document. It is the first branch of the same Provider Pay create run that `0ce68782` continues (corrections in section 2).

> **Source:** Claude Code logs for sessions `6410cf4e`, `0ce68782`, `62e199c0`, `69239f47`; window 21 Sep 2026 through 2 Nov 2026 (Eastern); per-request dollars from `message.usage` per unique request ID at the brief's fitted rates, checked against `cost-state`. Savings derivations are in section 3.

## 2. Measured baseline

### Attributed and segmented dollars

| Session | Class | Dollars | What it is |
| --- | --- | --- | --- |
| `6410cf4e` | Attributed (single skill) | $13.03 logged | Create run, first branch: Steps 0 through 3, P-phase QA rounds 1 and 2, a round 3 that two agents returned nothing for |
| `0ce68782` | Segmented, run | $52.00 logged-equivalent | Same create run, second branch: replanned Step 3, then Steps 4 through 10 |
| `0ce68782` | Segmented, maintenance | $10.12 computed | Post-run skill edits from parent turn 142 onward |
| `62e199c0` | Segmented, maintenance | $0.49 computed | Parent turns 22 through 24 of a PRD-template rewire session |
| `69239f47` | Segmented, maintenance | $3.77 computed | Parent turns 3 through 29 of the v1.4 edit session |

The full create run cost **$65.03 logged-equivalent** ($13.03 plus $62.12, less the $10.12 maintenance segment). Computed per request it is $65.39, a 0.6% gap. Maintenance segments are reported but excluded from every per-run figure below.

**Segmentation rule.** A parent turn belongs to this skill from its load signal (the `/dashboard-requirements` slash record, or a parent Read of its `SKILL.md`) until another skill's parent load signal. A subagent belongs when its `.meta.json` description names one of this skill's steps.

`0ce68782` has only this skill's parent signals. Its one other signal is evals-advisor's `Skill` call inside the Step 10 subagent "Evals-advisor post-run review: dashboard-requirements", which is this skill's Step 10.5 offer. The `69239f47` and `62e199c0` subagents ("QA the v1.4 skill edits", "QA the skill rewire plan") name skill edits, not steps, so they are excluded.

**Cost checks.** `0ce68782` shares 24 parent request IDs ($4.60) with `6410cf4e`; it resumed from that branch's turn 24. Its own computed cost is $62.14 against $62.12 logged. `6410cf4e` computes to $13.39 against $13.03 logged (2.8%), the gap sitting in Sonnet 5 on one fork subagent. Haiku 5.5 rates were not in the brief, so I scaled them to the `cost-state` fit [Assumption: Haiku 5.5 at one quarter of the first-guess rates (needs validation)].

**Baseline numbers that were wrong.**

| Earlier claim | Correction |
| --- | --- |
| `6410cf4e` parent $10.68 on Opus 5.5; "the orchestrator writes the document" | That branch stopped at Step 3. No document was written in it. The run was on v1.2, where a draft subagent wrote the document in `0ce68782` ($1.80). $4.60 of the $10.68 is the prefix both branches share |
| `0ce68782` mixed, $0 attributed | It is mixed only through this skill's own Step 10.5 subagent. $52.00 of it is this skill's run |
| Merging the three groups saves "launches only" | It saves $0.81 per create run (change 4) |
| 29 subagent calls in the single-skill session | I count 34 unique request IDs across its 11 transcripts, 26 without the fork. I could not reconcile the 29 |

The "7 agents, $1.71" Structure and Fidelity figure checks out: 7 launches, one returned nothing, $1.71. Mechanical also ran in that branch (3 launches, $0.02 logged).

> **Source:** same logs and window; request-ID overlap between `6410cf4e` and `0ce68782`; load signals from parent `Skill` calls, slash records and `Read` of `SKILL.md`; subagent `.meta.json` descriptions.

### Step cost map (create run, both branches)

| Step | Parent $ | Subagents with calls | Subagent $ | Setup share of subagent $ |
| --- | --- | --- | --- | --- |
| Steps 0 and 1: intake, context load | $2.61 | 0 | $0.00 | n/a |
| Step 2: questions, intake gate | $1.98 | 0 | $0.00 | n/a |
| Step 3: plan, P QA, Gate 1 (both branches) | $10.83 | 12 | $3.36 | 51% |
| Step 4: inventory, I QA | $6.14 | 6 | $3.55 | 63% |
| Step 5: selection, Gate 2 | $0.75 | 0 | $0.00 | n/a |
| Step 6: draft (draft subagent, retired in v1.4) | $0.61 | 1 | $1.80 | 9% |
| Step 7: D QA, 3 rounds | $3.95 | 15 | $5.16 | 45% |
| Step 8: reviewers, Gates 3 and 4 | $3.36 | 4 | $4.10 | 29% |
| Step 9: revision, R QA, 3 rounds | $5.75 | 16 | $5.62 | 45% |
| Step 10: log, trace | $1.52 | 1 | $2.34 | 0% |
| Step 10.5: evals-advisor offer | $1.15 | 1 | $0.81 | 0% |
| **Total** | **$38.65** | **56** | **$26.74** | |

The parent is 59% of the run. Its $38.65 is $16.38 cache reads, $16.81 cache writes and $5.48 output. Three full cache rewrites after Danny's gaps of more than an hour cost $10.29 of it. Step 3 is the most expensive step because the first branch ran P rounds 1 and 2, then Danny rewound and the second branch replanned and ran round 3.

Setup follows the brief's rule (calls before the first tool that is not Read, Grep, Glob or ToolSearch). Read-only judges such as Definitions and Structure never call another tool, so the rule books their whole cost as setup. Their real fixed cost is the first call's input: $0.07 per cold Sonnet 5 agent.

Future runs follow v1.4, which retires the $1.80 draft subagent and has the parent re-read the drafting list and every input at Step 6. That likely makes a v1.4 create run cost more than this one [Assumption: a 155k-token Step 6 re-read carried over 80 later turns adds $3.72 (needs validation)]. The savings below do not depend on that difference.

> **Source:** same logs; parent turns assigned to steps by the Agent launches, Writes and Edits they contain (Step 3 starts at the `plan.md` write, Step 5 at `gate-2.md`, Step 10 at the invocation-log edit); subagents assigned to the parent turn that launched them.

### Context anatomy

**Parent at its peak turn (turn 141, about 792k tokens):**

| Layer | Tokens (approx.) | Where it enters |
| --- | --- | --- |
| Base: system prompt, tools, memory, slash-loaded skill text | 73k | Turn 1 |
| Always-load references | 89k | Turns 5 and 6 (24k skill references, 65k repo files and exemplars) |
| Source payloads | 100k, plus 94k at turn 23 | Turns 7 through 13 (local inputs, Slack, Google Slides, two Docs); turn 23 content was not inspected |
| Accumulated turns | 436k | QA results, edits, the orchestrator's own output, Danny's queued messages |

**Typical QA subagent (Definitions, D round 2, about 78k at peak):** base 38.7k, of which about 12k is a prefix shared with siblings and 26.7k is written fresh per agent. Brief under 1k.

References: `evals.md` about 10.9k, taxonomy about 3k. Payloads: document about 8k, gate-2 about 2.6k, intake transcript about 2.9k. Two calls; output up to 29k tokens, most of it thinking.

**Loaded every run, used only sometimes.**
- Parent: `evals.md` (12k). The orchestrator builds briefs from the phase map in `SKILL.md`; observed briefs pass the `evals.md` path, and subagents read the definitions.
- Parent: `references/exemplars.md`, both gold exemplars and `danny-voice-exemplar.md` (about 25k together). Only Step 6 uses them, and Step 6 re-reads them from disk under v1.4. Revise mode never drafts.
- Subagents: the full `evals.md` on every QA open, when each group needs only its slice.

> **Source:** same logs; per-turn context is input plus cache read plus cache write tokens; layer sizes from context deltas at the turns named; file sizes from tool-result character counts divided by 3.5, so every token figure here is an estimate.

### Deep-dive checks

**Duplicate and oversized reads.** Subagents opened `evals.md` 26 times ($0.86) and the document 34 times ($0.90). They also opened the PRD 11 times ($0.32), the discovery synthesis 7 times ($0.31) and `gate-1.md` 20 times ($0.26). Document and input reads are each agent's own job; only `evals.md` loads in full where a slice is used (change 2), and merging removes 12 document opens (change 4).

The run made no Jira, Confluence or Figma calls. Three reviewers re-fetched 5 Google sources the parent had read at Step 1 (about 40k tokens, $0.21).

**Cache behavior.** The Opus parent writes 1-hour cache, so 5-minute expiry never hits it; its cost is the three rewrites after gaps of more than an hour ($10.29). Subagents write 5-minute cache. Siblings share only about 12k tokens of prefix, so 46 of the 56 run subagents paid a fresh first-call write of about 26.7k tokens ($0.07 each on Sonnet 5). D rounds 12 minutes apart rewrote that base each round; R rounds 1 and 2, 4 minutes apart, hit cache.

**Fan-out and loop shape.** `SKILL.md` line 89 spawns every judgment group plus Mechanical per round, line 92 respawns the full set on any fail, and line 93 caps a phase at three rounds. Line 130 sets three lenses, line 153 runs reviewers in parallel, and line 195 sets one subagent per group; `references/subagent-briefs.md` lines 83 and 128 repeat the per-group and per-phase rule. Across the six traces, a group passed one round and failed the next three times: 29 Sep D Fidelity (rounds 1 and 2), 28 Oct D Presentation (rounds 2 and 3), 28 Oct R Structure (rounds 1 and 2). At eval level that happened 17 times, so the full re-run stays.

**Parent-thread growth.**

| Step | Parent turns | Context at first turn | Context at last turn |
| --- | --- | --- | --- |
| Steps 0 and 1 | 13 | 73k | 270k |
| Step 2 | 11 | 271k | 385k |
| Step 3 (second branch) | 14 | 377k | 423k |
| Step 4 | 14 | 424k | 485k |
| Step 5 | 5 | 488k | 498k |
| Step 6 | 4 | 499k | 507k |
| Step 7 | 23 | 509k | 589k |
| Step 8 | 14 | 591k | 682k |
| Step 9 | 29 | 683k | 766k |
| Step 10 and offer | 14 | 768k | 793k |

QA, lens and reviewer results are already short: 48 results total 54.6k characters, median 1.1k. The weight is Step 1 inputs and MCP payloads plus the turn-23 addition, about 194k carried through every later turn. After Gate 2 the disk holds what drafting needs, so a compacted or fresh context is cheaper from there (change 1).

**Model mix.**

| Role | Model | Run $ |
| --- | --- | --- |
| Orchestrator (parent) | Opus 5.5 | $38.65 |
| QA judgment groups, inventory lenses, draft subagent, trace author, evals-advisor | Sonnet 5 (default) | $21.76 |
| Mechanical QA | Haiku 5.5 | $0.26 logged |
| Reviewers (data-analytics-eng, pm-exec, care-ops-exec) | Opus 5.5 | $3.71 |
| Fork agent spawned by a Fidelity agent | Sonnet 5 | $0.99 |

Only Mechanical is a candidate to move, and change 8 moves it to a script rather than another model. Judgment, reviewer personas and the document writer stay where they are.

**Tool surface.** Every QA, lens and trace subagent is `general-purpose` and inherits every tool, while they use Read, Grep, Glob and Bash (plus Write for the trace author). The tool block is about 5.6k tokens [Assumption: equal to the Explore versus general-purpose first-call gap (needs validation)]. See change 5.

**Output verbosity.** Not applicable to QA, lens and reviewer agents, whose returns are already short. Two places still pay for full text: the trace author copies ledger and QA rounds into the trace (change 6), and the orchestrator retypes each QA report into a file (change 7).

**Script replacement.** The skill has no `scripts/` folder today. Four deterministic scripts would give identical output: eval slices (change 2), trace skeleton (change 6), verbatim report saving (change 7) and Mechanical checks (change 8).

> **Source:** same logs; read counts from Read tool results in `0ce68782` subagent transcripts; read dollars as tokens written once at the 5-minute rate plus re-reads on later calls; first-call context medians across every subagent transcript in the project logs; group sequences from each trace's `qa_rounds` mapped through `<eval_phase_map>`.

## 3. Changes, ranked by dollars per future run

Per-run figures are standalone. Combined, with overlaps removed, they total $10.12: change 1 already removes most of change 2's and change 6's post-Gate-2 parent share, and change 4 shrinks change 5's agent count. No change saves launches without a dollar figure, so there is no launch-only tail.

### Change 1: offer `/compact` after the Gate 2 snapshot ($5.60 per run)

**Touches.** `SKILL.md` Step 5 (lines 134 through 139) and Step 6 (lines 141 through 144); `references/drafting-rules.md` read list (lines 7 through 18).

**Change.** After `gate-2.md` is written, the orchestrator tells Danny that everything Steps 6 through 10 need is on disk and offers a `/compact` before drafting. After compaction it re-reads `SKILL.md` and `references/subagent-briefs.md`, then runs Step 6's disk re-read unchanged. Danny can decline, and the run proceeds as today.

**Saving.** The parent held 488k tokens at Gate 2 and read it back on each of the 88 turns that followed. Compaction would drop about 388k of that [Assumption: post-compaction context is 73k base, a 15k summary and 12k of re-read skill files (needs validation)]. 388k × 88 turns × $0.20 per million = $6.83. Less one compaction call ($0.40) and a fresh 1-hour write of the 100k remainder ($0.80): **$5.60**.

**Guarding evals.** E36, E19, E12 and E34, the checks that catch a document following memory over files. E36 caught missing markers in the 4 Nov R round 1. E19 failed in the 29 Sep D round 2 and R rounds 1 and 2.

E12 failed in the 29 Sep R round 1. E36 is clause-level since v1.3, after it passed three D rounds on row presence alone.

**Validation.** Rebuild the 28 Oct gate files from that trace's `gate_evidence` (the run folder no longer exists). Run Steps 6 and 7 twice, with and without compaction. Pass bar: the compacted run's D round 1 fails no more evals than the uncompacted run, and E36, E19 and E12 pass in its final D round.

**Risk.** Highest of the set. v1.4 moved drafting into the orchestrator because a fresh context dropped two approved clauses. The guard is that drafting-rules already treats disk as the authority, and the gate snapshots and intake transcript are meant to hold every run rule. Any decision Danny made in chat but never got into a gate file is lost.

### Change 2: give QA agents eval slices and drop `evals.md` from the parent ($1.44 per run)

**Touches.** `SKILL.md` always-load row (line 51) and `<qa_loop_protocol>` step 1 (line 89); `references/subagent-briefs.md` §4 line 107 and §5 line 144; new `scripts/eval-slice.py`.

**Change.** A script prints the verbatim `evals.md` sections for a phase and group, using the `<eval_phase_map>` in `SKILL.md`. The orchestrator writes `<run>/evals-<phase>-<group>.md` and passes that path in each brief. The orchestrator no longer loads `evals.md` at Step 1; it runs the slice script for one eval ID when a fix needs the definition. The trace author and the evals-advisor subagent keep the full file.

**Saving.** Subagents opened `evals.md` 26 times at about 10.9k tokens each, for $0.86. Slices average about 2.5k [Assumption: a group's slice is 23% of the file (needs validation)], saving $0.66. In the parent, 12.2k tokens rode 161 turns ($0.39), cost $0.10 to write and $0.29 across three gap rewrites: $0.78.

**Guarding evals.** Every judgment and code eval depends on the brief carrying the right definitions. The report-completeness check (`<qa_loop_protocol>` step 2) catches a missing eval. It fired in the 28 Oct R round 3, which re-ran Fidelity for E36 alone. Proposed **E41 (code, every phase):** each slice lists exactly the phase map's IDs for its group, and each section is byte-identical to `evals.md`.

**Validation.** Generate slices for all four phases and five groups. Compare IDs against the phase map and diff each section against `evals.md`. Then replay one D round on the committed one-pager. Pass bar: E41 passes, and each group's verdicts match a full-file run.

**Risk.** Low. A judge loses the suite design rules at the top of `evals.md`, so the slice must include them.

### Change 3: load drafting-only files at Step 6, not Step 1 ($1.16 per run)

**Touches.** `SKILL.md` always-load rows (lines 47, 53, 56 and 57) and line 59; `references/drafting-rules.md` read list (lines 7 through 18).

**Change.** Move `references/exemplars.md`, both gold exemplars and `danny-voice-exemplar.md` from the Step 1 list to the Step 6 list. Add the voice exemplar to `drafting-rules.md`, which does not list it today. In revise mode, load `exemplars.md` only for the sync-from-upstream variant, whose step 5 proposes lessons for it.

**Saving.** About 24.9k tokens rode 72 parent turns before Step 6 ($0.36), cost $0.20 to write, and were rewritten in three gaps of more than an hour before Step 6 ($0.60): **$1.16**. Revise runs save more, since they never draft [Assumption: revise runs carry these files on every turn (needs validation)].

**Guarding evals.** E23, E26, E27, E35 and E37 check shape and length, and E22 checks writing patterns. The 28 Oct D round 1 caught five of them failing (E23, E26, E27, E35, E37).

**Validation.** Replay Steps 0 through 6 from the 28 Oct inputs with the new load order. Pass bar: D round 1 fails no more shape evals than the 28 Oct run did, and Steps 2 through 5 ask the same questions and recommend the same cuts.

**Risk.** Low. Steps 2 through 5 do not cite the exemplars.

### Change 4: one judgment agent for Definitions, Structure and Presentation per D and R round ($0.81 per run)

**Touches.** `SKILL.md` `<input_routing>` (lines 68 through 71), `<qa_loop_protocol>` steps 1 and 2 (lines 89 and 90), `<eval_phase_map>` line 195; `references/subagent-briefs.md` §4 (lines 81 through 123).

**Change.** In D and R, one subagent checks E13 through E16, E18, E38, E24, E25, E27, E40 and E37. It receives the union of the three groups' references, including the taxonomy calibration lists for Presentation, because E37 grades against them. Fidelity stays its own agent, and P keeps Structure alone for E04. The completeness check also rejects any report row without quoted evidence, including rows such as "All others Pass".

**Saving.** The 28 Oct run ran these three groups as 18 D and R agents (plus Structure once in P, for the 19 the earlier pass counted). Merging removes 12. Removed first-call input, base re-reads and duplicate document reads come to $1.16.

The merged agent adds one call over a larger context and carries Definitions' references, $0.35. Net **$0.81**.

**Guarding evals.** The eleven merged evals. They caught real failures: 28 Oct D round 1 (E15, E16, E25, E27, E37) and 4 Nov R (E13, E15, E18, E25, E40). Proposed **E42 (code, every QA round):** each report has one row per assigned eval, each with a non-empty Evidence cell.

**Validation.** Replay the committed one-pager through one D round three times each way: three groups, then one merged agent. Pass bar: the merged agent flags every eval the separate agents flagged in two of three runs, and E42 passes on every merged report.

**Risk.** Medium. The 5 Nov revise run used one agent for every group, and its reports listed passes only as "All others Pass" with no evidence. E15, E18, E25 and E27 already flip on unchanged text, so variance may rise. Presentation was routed the document alone, so merging gives it references it did not have (see open questions).

### Change 5: a tool-restricted QA agent type ($0.60 per run)

**Touches.** `references/subagent-briefs.md` lines 3, 19, 83, 128 and 164; new `.claude/agents/dashboard-qa.md` with `tools: Read, Grep, Glob, Bash` and an explicit Sonnet 5 model (Haiku for Mechanical), so nothing inherits the Opus parent.

**Change.** QA, lens and trace subagents spawn as this type instead of `general-purpose`. The trace author also gets Write, scoped by its brief to the trace file.

**Saving.** Opus Explore agents, which carry fewer tools, start at a median of 34.2k tokens, against 39.8k for Opus `general-purpose` agents. [Assumption: the 5.6k gap is tool definitions and carries over to Sonnet 5 (needs validation)]. Do not use 5.6k until the provider-draft-failure-modes change 1 test launch measures the drop, and use that measurement here. At $0.014 per cold first call plus re-reads, across 42 Sonnet agents with 10 cache-hit first calls: **$0.60**, or $0.45 after change 4.

**Guarding evals.** No eval guards tool use today; the brief rules do. Proposed **E44 (code, every QA round):** every QA, lens and trace subagent's `.meta.json` names the `dashboard-qa` type, and none has `spawnDepth` above 1. Two traces show the gap: v1.3 added the no-file rule after a QA subagent wrote scratch files. In the 27 Oct P round 2, a Fidelity agent spawned its own fork agent ($0.99). Removing Write, Edit and Agent enforces both rules.

**Validation.** Run one P round with the new type on the 28 Oct plan rebuilt from the trace. Pass bar: first-call context drops by at least 4k tokens, verdicts match, and no agent errors on a missing tool.

**Risk.** Low. An agent that `model: inherit` would move QA to Opus and raise cost, so the model line is required.

### Change 6: a trace skeleton script ($0.40 per run)

**Touches.** `references/subagent-briefs.md` §6 (lines 162 through 195); new `scripts/trace-skeleton.py`.

**Change.** Before the trace author runs, a script fills `tool_calls` from the ledger, `qa_rounds` and `eval_results` from `qa-reports/`, and runs E21's Logic on the ledger. The trace author verifies those fields against the files and writes the judgment fields: gate evidence, metric deltas, decisions and observations.

**Saving.** Those three fields are 54% of the 28 Oct trace JSON. The trace author's output cost $0.68. [Assumption: output tokens scale with field share (needs validation)] About $0.37, plus fewer report reads: **$0.40**.

**Guarding evals.** E21 and the trace author's gate-evidence audit. The 5 Nov trace caught E21 failing on a ledger that carried `"op":"read"` instead of `write: false`.

**Validation.** Run the script on the 28 Oct ledger and reports if Danny has them, or on a fresh run's folder. Pass bar: its fields match the trace author's hand-built fields exactly.

**Risk.** Low, if the trace author still checks the skeleton against the files rather than trusting it.

### Change 7: save QA reports verbatim with a script ($0.29 per run)

**Touches.** `SKILL.md` `<qa_loop_protocol>` step 1 (line 89); new `scripts/save-qa-report.py`.

**Change.** The orchestrator passes the subagent ID from the Agent result to a script. The script copies that subagent's final message from its transcript into `<run>/qa-reports/`. Today the orchestrator retypes each report with Write, as Opus output. Where no transcript exists (Cursor runs), it falls back to Write.

**Saving.** 23 report writes, about 9k Opus output tokens ($0.18), which then rode the remaining turns ($0.11): **$0.29**, or about $0.20 after change 1.

**Guarding evals.** No eval checks report fidelity. The 4 Nov trace records saved reports as "lightly condensed, not verbatim", and the 5 Nov trace found an orchestrator note appended to one. Proposed **E43 (trace author):** each saved report matches its subagent's final message.

**Validation.** On the next run, save each report both ways and diff them. Pass bar: the script copy matches the subagent message exactly.

**Risk.** Low. The transcript path layout is a Claude Code detail and can change.

### Change 8: run the Mechanical checks as a script ($0.27 per run)

**Touches.** `references/subagent-briefs.md` §5 (lines 126 through 158); `SKILL.md` `<eval_phase_map>` line 195; new `scripts/mechanical-checks.py`.

**Change.** One script runs every Code eval's Logic block for the phase and prints the same report table. It prints `Fail (ambiguous)` with the group to route to whenever a block does not resolve. The orchestrator runs it in the same turn it launches the judgment agents.

**Saving.** The ten Haiku agents cost $0.26 logged in the run. Running the script in an existing turn adds no parent turn: **$0.27** computed.

**Guarding evals.** All Code evals stay: E01, E02, E03, E07, E08, E17, E21, E22, E23, E26, E28 through E33, E35 and E39. Mechanical failures that runs caught: 28 Oct D rounds 1 and 2 (E23, E26, E35), 28 Oct R round 1 (E26), and 5 Nov (E21, E23, E26). One check regressed between rounds (E26, 29 Sep D rounds 1 and 2), so the check must keep running every round.

**Validation.** Run the script on the committed Provider Pay one-pager and the Provider Drafts Confluence exemplar. Pass bar: verdicts match each trace's final `eval_results` for every Code eval, and Danny reviews any divergence.

**Risk.** Medium for E22 and E26, whose tag exceptions and sentence splitting carry interpretation. Haiku's judgment on edge cases is replaced by fixed rules, which is the point but may shift verdicts.

> **Source:** same logs and window; savings computed per request at the fitted rates; trace evidence from `.claude/skills/dashboard-requirements/observability/traces/` (runs of 29 Sep, 30 Sep, 28 Oct, 29 Oct, 4 Nov, 5 Nov 2026) and `observability/invocation-log.jsonl` (the 4 Nov E36 failure); line numbers from the committed skill files.

## 4. What not to cut

- **Fidelity as its own agent.** It holds the clause-level guard: E36 passed three D rounds while two approved clauses were missing until v1.3, and E19 regressed from pass to fail in the 29 Sep D round 2.
- **The full re-run on every fix round.** The six traces show 17 cases of an eval passing one round and failing the next (Definitions 6, Structure 5, Fidelity 3, Mechanical 2, Presentation 1).
- **The orchestrator writing the document on Opus 5.5.** The 28 Oct draft subagent dropped the O1 and A17 clauses that reviewers then restored at Step 8.
- **Step 6's disk re-read.** It is the guard that makes change 1 safe, and the drafting rules depend on it.
- **Reviewer personas on Opus 5.5 ($3.71 in the run).** The care-ops reviewer caught the A13 slice contradiction no D eval read, which is why E40 exists.
- **Three inventory lenses.** E09 failed all three I rounds in the 29 Sep run; breadth is what the lenses buy.
- **Up to three QA rounds per phase.** E15 and E18 flipped Fail, Pass, Fail on unchanged text in the 4 Nov run, so a single round would miss persistent issues.
- **Fidelity reopening the inputs every round.** E12 and E34 judge against the sources themselves, and only the document changes between rounds.

> **Source:** trace `qa_rounds` and `observations` in the six runs named in section 3; `evals.md` E19, E36 and E40 history; `references/design-record.md` §12.

## 5. Open questions for Danny

1. Will you run `/compact` at Gate 2 when the skill offers it? Change 1 is $5.60 of the $10.12. [Assumption: the skill cannot trigger compaction itself (needs validation)]
2. Did you rewind at P round 3 on 27 Oct because E04 kept failing on your recorded reviewer decision? That branch cost $8.43 logged-equivalent. v1.3 fixed E04, so I counted no saving for it.
3. Decision: Presentation receives the taxonomy calibration lists, because E37 grades against them. Change 4 keeps the three-way merge, and E42 still requires evidence on every row.
4. Decision: evals-advisor change E also edits `SKILL.md` line 172, so this skill waits for that subagent. Its $0.06 is counted in the evals-advisor plan, not here.
5. Step 8 launched a fourth reviewer, "general-purpose QA review" ($0.39), that the selection rules do not name. Was that intended?
6. Where did the 29 Oct revise run execute? It has no Claude Code transcript, so I could not measure revise mode.
7. Reviewers re-fetched 5 Google sources over MCP ($0.21). Those calls never reach `mcp-ledger.jsonl`, so E21 cannot audit them. Should reviewers get saved local copies, or should their calls be logged?
8. The 28 Oct run folder lived in the session scratchpad and is gone. Can a copy of a run folder be kept for replays? Every validation plan above needs one.

**Could not measure:** the 29 Oct revise run (no Claude Code transcript; likely Cursor); turn 23's 94k-token addition in the parent, which I did not open, under the privacy rule.
