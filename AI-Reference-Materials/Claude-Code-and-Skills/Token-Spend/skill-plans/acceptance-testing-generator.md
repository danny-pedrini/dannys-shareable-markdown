# Token-efficiency plan: acceptance-testing-generator

## 1. Answer

Five changes would save **$3.64 per future run** and **$10.93 over the window (21 Sep 2026 through 2 Nov 2026)**, which is 43% of the $25.29 this skill's three measured runs cost. No check is removed and no judgment changes model. One more change saves launches only.

Most of the money is not in the skill's own steps. Both measured sessions started the skill after a long prd-generator thread, so every Opus parent turn re-read 345,000 to 718,000 tokens of unrelated history [estimate range]. Starting the run in a fresh session with a handoff file is worth $7.60 of the $10.93.

> **Source:** Claude Code logs in `~/.claude/projects/-Users-dpedrini-Projects-dannys-pm-workspace-care`, sessions `93a3e520`, `cf5250a3`, `62e199c0`. Window and session dating as in `AI-Best-Practices/Token-Spend/skill-efficiency-recommendations.md` (Method). Per-request dollars from `message.usage` per unique `requestId` at the brief's fitted rates. Savings derivations are in section 3.

## 2. Measured baseline

### Attributed and segmented dollars

Attributed dollars stay at **$0.00**: all three sessions are mixed, and their totals ($86.02, $97.25, $13.30) sum to the $196.57 the earlier pass reported. Segmentation finds **$29.40** spent inside this skill's segments, of which **$25.29** went to three real runs.

| Segment | Session | Boundary (UTC) | Parent $ | Subagents | Subagent $ | Total $ |
| --- | --- | --- | --- | --- | --- | --- |
| R1: new Comprehensive doc, 21 Oct | `93a3e520` | From the `Skill` call at 18:05:35.977 to session end | 9.05 | 6 | 3.29 | 12.34 |
| R2: surgical revision, 27 Oct | `cf5250a3` | From the `Skill` call at 10:40:06.466 until 11:13:56 | 3.06 | 2 | 1.14 | 4.20 |
| R3: full-pass revision, 27 Oct | `cf5250a3` | 11:13:56 until 12:09:42 | 4.72 | 6 | 4.03 | 8.75 |
| Skill maintenance (not a run) | `cf5250a3` | From 12:09:42 until the prd-generator `SKILL.md` Read at 13:11:26.614 | 2.53 | 1 | 0.91 | 3.44 |
| Reference read (not a run) | `62e199c0` | From the `SKILL.md` Read at 23:33:42.036 to session end | 0.67 | 0 | 0.00 | 0.67 |

**Segmentation rule.** A parent turn belongs to this skill when its timestamp falls between this skill's load signal and the next skill's load signal. A subagent belongs to the segment that contains its parent `Agent` tool call. Nested subagents (spawn depth 2) belong to the segment that contains their first request; all 16 nested transcripts in these sessions fall outside this skill's segments.

- **`93a3e520`.** prd-generator owns 10:52:29 (slash command) up to 18:05:35.977. Its last launch, "QA three post-delivery PRD fixes" at 17:59:16, stays with prd-generator. This skill owns 18:05:35.977 onward.
- **`cf5250a3`.** prd-generator owns everything before 10:40:06.466 (its last launch is at 10:39:14) and everything from 13:11:26.614 on. Eleven later launches go to prd-generator under this rule, including "QA AC skill v1.1 implementation" ($0.94), whose description names this skill. I did not count them here.
- **`62e199c0`.** agent-architect's segment ends at 23:33:42.036. The parent read this skill's `SKILL.md` (1,828 characters returned) and then edited only prd-generator files. That is a reference read, not a run, so it is excluded from per-run figures.

The R2/R3 split at 11:13:56 and the maintenance split at 12:09:42 are mine. They follow the two invocation-log lines for 27 Oct and the first Bash call that reads skill passages to edit.

Computed totals land within 5% of `cost-state` (`93a3e520` +1.5%, `cf5250a3` +1.6%, `62e199c0` minus 0.2%). The brief gives no Haiku rate, so the one Haiku agent in R3 is priced at $0.00; logged Haiku spend for all of `cf5250a3` was $0.16.

> **Source:** same logs and window. Load signals per the earlier pass's Method (`Skill` call, slash-command record, parent `Read` of a `SKILL.md`). Segmentation as stated above; synthetic error records excluded; fork copies (shared request IDs) all sit outside these segments.

### Baseline numbers corrected

- **Subagent launches and calls.** The earlier pass lists 116 launches and 982 calls for this skill. Both reproduce (94 parent launches plus 22 nested; 982 unique request IDs), but they are whole-session counts. Only **15 launches and 104 calls** fall inside this skill's segments, and **13 launches and 97 calls** inside real runs.
- **"Waste: not measurable."** With segmentation, it is: $25.29 across three runs, $8.43 per run on average.
- **The earlier change has no measured use.** It batches UAT multi-document fan-out. Every run in the window was Comprehensive with one requirement document, and so was every trace since 18 Sep 2026.

### Step cost map

R1 is the only window run that executed every step. "Setup" follows the brief: calls before an agent's first tool that is not Read, Grep, Glob or ToolSearch. A read-and-judge agent such as Gate 2 never calls another tool, so its whole run counts as setup.

| R1 step | Parent turns | Parent $ | Subagents | Subagent $ | Setup $ (share) |
| --- | --- | --- | --- | --- | --- |
| Steps 1 and 1b: intake and model interview | 2 | 0.56 | 0 | 0.00 | n/a |
| Steps 2 and 3: references and sources | 3 | 0.64 | 0 | 0.00 | n/a |
| Step 5: inventory and Eval Gate 1 | 4 | 0.95 | 1 | 0.37 | 0.10 (26%) |
| Steps 7 through 9: generate, write, E5, Eval Gate 2 | 7 | 1.94 | 1 | 0.41 | 0.41 (100%) |
| Step 10: QA | 4 | 0.91 | 1 | 0.47 | 0.19 (41%) |
| Step 11: evals | 5 | 1.12 | 0 | 0.00 | n/a |
| Step 12: log | 3 | 0.66 | 0 | 0.00 | n/a |
| Step 13: trace (3 launches) | 10 | 2.06 | 3 | 2.03 | 0.29 (14%) |
| Step 14: present | 1 | 0.20 | 0 | 0.00 | n/a |
| **Total** | **39** | **9.05** | **6** | **3.29** | **0.99 (30%)** |

| R3 step | Parent turns | Parent $ | Subagents | Subagent $ | Setup $ (share) |
| --- | --- | --- | --- | --- | --- |
| Step 5: inventory and Eval Gate 1 | 5 | 0.64 | 1 | 0.37 | 0.12 (33%) |
| Steps 7 through 9: revise and Eval Gate 2 | 3 | 0.38 | 1 | 0.46 | 0.10 (21%) |
| Step 10: QA round 1 | 6 | 0.77 | 1 | 0.64 | 0.18 (29%) |
| QA round 2 plus the eval suite, in one subagent | 6 | 0.83 | 1 | 1.59 | 0.33 (21%) |
| Fixes after Danny's ruling, Step 12 log | 9 | 1.29 | 0 | 0.00 | n/a |
| Step 13 trace and the Haiku `evals.md` update | 2 | 0.31 | 2 | 0.97 | 0.00 (0%) |
| Steps 11 and 14: finish and present | 4 | 0.50 | 0 | 0.00 | n/a |

R2 skipped Steps 5, 11 and 13 by design (logged `partial`). It ran a plan QA and a post-edit QA ($1.14, 58% setup); its 22 parent turns cost $3.06, and 12 of them ($1.42) went to logging and presenting.

> **Source:** same logs and window. Step boundaries are parent timestamps at each step's first tool call (for example, R1 Step 10 starts at 19:27:52 UTC). Subagents are mapped to steps by launch time.

### Context anatomy

| Layer | Typical subagent (first call to peak) | Parent at peak (R1, 918,281 tokens) |
| --- | --- | --- |
| Base: system prompt and tool definitions | About 11,900 tokens, cache-read from the shared prefix | Inside the session's 73,593-token first request |
| Base: memory files and the brief | About 36,000 tokens, written fresh on the first call (75% of the first context) | Same first request |
| Unrelated thread history | None | **718,000 tokens** of prd-generator work |
| Skill text | Not loaded, except R3's eval runner (`SKILL.md`, 52,204 characters) | 17,495 tokens (`SKILL.md` load) |
| References | `qa-subagent.md` (14,214 chars), `evals.md` (46,688 chars), `observability-templates.md` (25,039 chars) | Template, categories and Comprehensive exemplar: 15,264 tokens; `qa-subagent.md` plus an evals listing: 7,307 tokens |
| Source payloads | PRD (20,353 to 25,845 chars) [estimate range], AC document (31,656 to 33,663 chars) [estimate range], inventory, addendum; R3's eval runner also read three supporting docs (119,321 chars) | PRD: 7,020 tokens |
| Accumulated turns | Peaks: Gate 1 81,753; Gate 2 84,207; QA 103,435; auditor 135,979; R3 eval runner 217,008 | About 79,000 tokens (the written document, gate results, Bash output) |

**Loaded every run, used only sometimes.** Conditional loading already works: `source-ingestion.md`, `prototype-analysis-subagent.md` and `exemplar-uat.md` never loaded in these Comprehensive runs. The every-run waste is narrower. `SKILL.md` lines 421 through 446 and 449 through 493 (UAT-only rules, 5,926 characters) load on every Comprehensive run. Auditors load all of `evals.md` and `observability-templates.md` but use only the gate sections.

> **Source:** same logs and window. Token figures are `input + cache_read + cache_creation` per request, or deltas between consecutive requests. Character counts are tool-result sizes. Read results measured 2.1 characters per token (median of 24 single-read deltas).

### Deep-dive findings

**Duplicate and oversized reads.** No MCP payloads appear: every source in these runs was a local file. Within R1, the PRD was opened by 6 agents ($0.20), the AC document by 5 ($0.28) and `evals.md` in full by 2 auditors ($0.17). Within R3, `evals.md` was opened by 3 agents ($0.28) and the PRD by 5 ($0.25). Re-reads of the document and PRD are the independent checks themselves, so they stay.

The avoidable reads are rule files opened in full and the R1 auditor reruns (changes 2 and 4).

**Cache behavior.** The Opus parent writes 1-hour cache, so pauses of up to 42.7 minutes (R1, between 18:33 and 19:15 UTC) stayed warm. A pause over an hour at 791,533 tokens would rewrite $6.33 of context; fresh-context runs cut that exposure to about $0.59.

Sonnet 5 subagents write 5-minute cache. Each wrote about 36,000 tokens fresh on its first call, and 4 of the 15 segment agents wrote their whole first context fresh because no sibling had run in the past 5 minutes. That fixed base ($0.09 per agent) is harness and memory-file cost, not skill text, so it is not ranked here.

**Fan-out and loop shape.** Eval Gate 1 is one agent (`SKILL.md` lines 343 through 359). Gate 2 is one agent per draft (lines 495 through 509), or one per document in UAT fan-out (lines 459 through 466). QA re-runs in full after escalations, two iterations at most (`SKILL.md` lines 566 through 572; `references/qa-subagent.md` lines 166 through 172). The trace auditor is one agent (lines 607 through 648).

Traces show checks that pass one QA round and fail the next: A3 and C4 in the 27 Oct 2026 full pass, B3 in the 4 Nov 2026 revision, C3 in the 5 Nov 2026 revision. Full re-runs must stay.

**Parent-thread growth.** R1's parent grew from 809,028 tokens at the first skill turn to 918,281 at the last: 109,253 tokens over 39 turns. R2 and R3 started at 437,060 tokens and reached 545,093 over 57 turns. The orchestrator also holds `qa-subagent.md` (to build the QA brief) and 10,704 characters of eval definitions read through Bash. A fresh thread would be cheaper on every turn (change 1).

**Model mix.**

| Role | Model |
| --- | --- |
| Parent: interview, generation, Step 11 judge evals (including G1 quote fidelity), Step 12 log | Opus 5.5 |
| Eval Gates 1 and 2, QA, trace auditor, plan QA | Sonnet 5 (general-purpose default) |
| `evals.md` Last Result update (R3) | Haiku |

R3 ran its judge evals inside a Sonnet 5 subagent, while `SKILL.md` Step 11 puts them in the parent. I propose no model moves. The mechanical work (code evals, the Last Result column, the log line) moves to a script, not to a cheaper model.

**Tool surface.** All 15 segment subagents are general-purpose and inherit every tool. Each used at most four tool types (Read, Bash, Write, Edit). Tool definitions sit inside the 11,900-token cached prefix, so they cost at most $0.0024 per call, $0.23 across the 97 run calls even if the whole prefix were tools. Not applicable as a dollar change.

**Output verbosity.** Returns to the parent run from 900 to 8,996 characters of text [estimate range], so verbosity is not material. The larger outputs are hidden reasoning (Gate 2's final call: 20,999 output tokens, $0.21) and the auditors' trace JSON. Two of those JSON writes were rejected (change 2). Not applicable beyond change 2.

**Script replacement.** The 19 code or code-prefilter evals in `evals.md` (A1, A2, A3, B2, B4, C1, E1, E2, E3, E5, F1, F2, F3, plus the code halves of A5, B3, E4, G1, G2, G3) are written as grep logic but are run by a model each time. The skill has no `scripts/` folder.

R1's parent spent 5 Opus turns on Step 11 and R3's eval runner made 15 Bash-only calls ($1.09). The Last Result update took a Haiku agent 25 Edits. Change 3 covers these.

> **Source:** same logs and window; traces in `.claude/skills/acceptance-testing-generator/observability/traces/` and `observability/invocation-log.jsonl` for round outcomes.

## 3. Changes, ranked by dollars per future run

Savings are sequential: each change is computed after the ones above it. Per-run figures divide the window figure by the three measured runs.

### Change 1: start the run in a fresh context when the thread is long ($2.53 per run, $7.60 in window)

**Touches:** `SKILL.md` lines 204 through 237 (Step 1 intake), adding a check before question 1.

**Change.** Before intake, the skill checks whether the current thread is long or carries another skill's work. If it does, the skill writes a handoff file to the session scratchpad: known intake answers, inferred model-interview defaults, decisions from the session that bear on the feature, and source paths. It then asks Danny to open a fresh session and invoke the skill with that path. Steps 1 and 1b still run in full in the new session, so the handoff only pre-fills defaults.

**Saving.** Each parent turn in the run re-read the pre-skill history at $0.20 per million tokens: 718,000 tokens in R1 (791,533 at load, less the 73,593-token session base) and 345,000 in `cf5250a3`. That is $5.60 in R1 (39 turns) and $3.94 across R2 and R3 (57 turns).

Fresh-session overhead is $0.59 (rewriting the 73,593-token base at $8 per million) plus the handoff turns in the old thread: $0.46 in R1 and $0.30 in `cf5250a3`. [Assumption: the handoff takes 2 parent turns and 3,000 output tokens (needs validation)] Net: $4.55 plus $3.05, or $7.60. Break-even is a thread of about 240,000 tokens at the measured average of 32 turns per run.

**Guarding evals.** G4, B5, B1, G1 and G2 in `evals.md`, QA check C4, and the `model_confirmed` and `traceability` gates. Traces show they catch the failure a lost thread could cause. C4 and G4 failed in the 27 Oct 2026 full pass on an unstated period split, and B5 failed in the 4 Nov and 5 Nov 2026 revisions. The 25 Sep 2026 auditor found five in-scope IDs untraced that A1 had passed.

No eval checks the handoff itself. **Proposed eval H1:** every decision the handoff lists appears in the model section, a cited requirement, or the Step 14 gap list.

**Validation plan.** Replay R3: the PRD and AC document as of the 27 Oct 2026 auto-sync commit, plus the three supporting documents, in a fresh session with a handoff written from `cf5250a3`. R1 cannot be replayed as-is, because its addendum file no longer exists. Compare Step 11 eval results and gate evidence with R3's log line and trace. Pass bar: every eval and gate that passed in R3 passes, C4 and G4 still fail on the same unstated split before the fix, and parent dollars fall by at least $2.00.

**Risk.** Danny pays one extra session start. Context that never reached a file (a verbal ruling, a Slack aside) can drop. The model interview is the backstop, and H1 makes the drop visible.

### Change 2: the auditor writes its trace to the scratchpad; the parent copies it ($0.59 per run, $1.77 in window)

**Touches:** `SKILL.md` lines 607 through 648 (Step 13 brief, the `Write` instruction at lines 642 and 643) and `<tool_access>` lines 182 through 199.

**Change.** The auditor writes the trace to `<session scratchpad>/acceptance-testing-generator/<slug>/trace.json` and returns the path plus a SHA-256 hash. The parent copies it into `observability/traces/` with `Write` and confirms the hash. The auditor still authors every field; the parent only moves bytes.

**Saving.** In R1 the first two auditors' `Write` calls into `.claude/skills/` were rejected at the permission prompt. Danny then messaged and the parent relaunched; the third auditor's write succeeded. The two lost auditors cost $1.36.

They added 7 parent turns, which cost $1.42 at R1's real context and $0.41 after change 1. Window: $1.36 plus $0.41. [Assumption: the two rejections were permission friction, not Danny vetoing the trace content (needs validation)]

**Guarding evals.** The seven process gates the auditor audits (`evals.md` lines 778 through 791) and `independently_authored`. Auditors have caught real defects: `traceability` false on 25 Sep and 5 Nov 2026, `intake_confirmed` false on both 28 Sep 2026 runs. **Proposed gate `trace_integrity`:** the committed trace's hash equals the hash the auditor reported.

**Validation plan.** Replay R1 Step 13 only, with the 21 Oct 2026 AC document and PRD from git. Pass bar: one auditor launch, zero permission prompts, hashes match, and 6 of 6 gates with evidence as in the 21 Oct 2026 trace.

**Risk.** A parent that edits the file in transit would break independence. The hash check catches that.

### Change 3: `scripts/code_evals.py` runs the code evals and formats the log line ($0.35 per run, $1.05 in window)

**Touches:** `SKILL.md` lines 575 through 586 (Step 11) and 590 through 605 (Step 12); `evals.md` lines 37 through 66 (Active Evals table) as the script's ID list. New file `scripts/code_evals.py`.

**Change.** The script reads the document, the working-sections file, the Step 5 inventory and the requirement source. It runs every code eval and code prefilter listed under script replacement, and prints one compact table plus the judge candidates. It also prints the new Last Result column and the JSONL log line.

The parent pastes both in with one `Edit` each, since Bash writes inside `.claude/skills/` are denied. Judge evals stay in the parent on Opus, reading only the script's candidates.

**Saving.** R1 Step 11 took 5 parent turns ($0.40 after change 1); 2 turns would do it, saving $0.24. [Assumption: script output cuts Step 11 to 2 parent turns (needs validation)] R1 Step 12 drops one of 3 turns, saving $0.08.

R3's eval runner spent $1.09 on 15 Bash-only calls. [Assumption: the script replaces 10 of those 15 calls (needs validation)] That is $0.73. The Haiku agent is also removed; with no Haiku rate, it is not counted.

**Guarding evals.** The code evals themselves, with current catches: A3 failed in the 27 Oct 2026 full pass; R1's Step 11 caught an F1 range and a G3 misquote that QA passed (21 Oct 2026 log line); F3 was introduced and fixed on 5 Nov 2026. A2 and A3 recorded "Skipped, inventory not retained" on 4 Nov and 5 Nov 2026, and the script makes that skip visible rather than silent. **Proposed eval H2:** the script's report lists every active code eval ID exactly once.

**Validation plan.** Run the script, without the skill, on the 21 Oct and 27 Oct 2026 AC documents from git with their inventories. Then run it on the 5 Nov 2026 document with its pre-revision snapshot. Pass bar: the same P, F or S as the logged `eval_results` for every code eval, and every hit the model reported also appears in the script's output.

**Risk.** A grep can drift from the prose definition in `evals.md`. H2 plus the parity replay guard that, and any definition edit must update the script in the same change.

### Change 4: scoped reads of rule files and the QA brief by path ($0.15 per run, $0.45 in window)

**Touches:** `SKILL.md` lines 615 and 616 and 642 and 643 (auditor brief), line 568 (QA spawn), and `references/qa-subagent.md` lines 10 through 38.

**Change.** The auditor brief names `evals.md` lines 751 through 791 (the A1 relationship and the process gates) and `observability-templates.md` sections 2 and 5 (lines 95 through 190 and 319 through 428), not whole files. The parent passes `qa-subagent.md` by path with the bracketed fields filled, and does not read the file itself. Eval or QA briefs do not ask the agent to read `SKILL.md`. Requirement sources and the AC document stay full reads for every judge.

**Saving.** Full `evals.md` reads by the R1 first auditor and the R3 auditor: $0.16. Unused template sections: $0.04. `SKILL.md` in R3's eval runner (24,859 tokens carried over 18 calls): $0.15. The R1 parent's `qa-subagent.md` read and its 9,923-character inlined brief: $0.10.

Each is tokens times the Sonnet write rate plus $0.20 per million for every later call.

**Guarding evals.** All seven process gates, the 21 QA failure modes, and the Step 11 judge evals. R1's third auditor read `evals.md` with a 40-line limit and still produced 6 of 6 gates with evidence (21 Oct 2026 trace). The auditor's full re-read of the source is what caught the 18 Sep 2026 misquote (`evals.md` lines 570 through 572), so source reads are not scoped.

**Validation plan.** Replay R3's QA round 2 and Step 13 against the skill version of 27 Oct 2026 from git, with the scoped briefs. Pass bar: QA reproduces the A3, C4 and G4 failures, and the auditor's gate results match the 27 Oct 2026 trace.

**Risk.** A line range drifts when `evals.md` is edited. Point to headings, with line numbers as a hint.

### Change 5: move UAT-only rules into `references/uat-mode.md` ($0.02 per run, $0.06 in window)

**Touches:** `SKILL.md` lines 421 through 446 and 449 through 493 (5,926 characters); a one-line pointer stays in `<modes>` and Step 7.

**Change.** UAT runs read the new reference at Step 2, beside `exemplar-uat.md`. Comprehensive runs do not load it.

**Saving.** 5,926 characters at the measured 3.05 characters per token for `SKILL.md` is 1,943 tokens. Each load pays the 1-hour write ($8 per million) plus $0.20 per million on each later turn. Two loads in the window (R2 and R3 shared one) come to $0.06.

**Guarding evals.** E1, E3, F2 and C2 on UAT output. No UAT run falls in the window, so no trace shows them catching this. **Proposed eval H3:** a UAT run's trace `context_sources` includes `references/uat-mode.md`.

**Validation plan.** Replay the 30 Aug 2026 UAT run (Galen Phase 1 Complete the Chart). Pass bar: E1, E3 and F2 pass, and the section list matches the 30 Aug 2026 output.

**Risk.** A UAT run that skips the reference loses its altitude rules. H3 catches that.

### Change 6: two requirement documents per UAT fan-out subagent (launches only)

**Touches:** `SKILL.md` lines 449 through 493 (or `references/uat-mode.md` after change 5).

**Change.** As the earlier pass proposed, pair documents whose combined size fits one context, with a section prefix each. Eval Gate 2 still runs on each document's test table before consolidation.

**Saving.** Launches only: one base context ($0.09 first write) per pair. No run in the window used this path.

**Guarding evals.** F2 (prefix collision), A4 (duplicates), C2 (altitude) and Eval Gate 2 per document.

**Validation plan.** Defer until a multi-document UAT input exists, then run it once batched and once unbatched. Pass bar: identical F2, A4 and C2 results, and Gate 2 findings per document match.

**Risk.** Two documents in one context can bleed terminology across sections (B3).

## 4. What not to cut

- **Danny's scope confirmation of the document list** (`SKILL.md` lines 454 and 455). It is held fixed, and it sets the in-scope ID set that A1 and `traceability` grade against.
- **The Step 1b model interview.** R1 spent $0.56 on it. The 18 Sep 2026 run built six criteria on a misread prototype control, which is why G4 exists.
- **Eval Gate 1.** It found six missing degraded paths on 21 Oct 2026 and seven inventory defects on 18 Sep 2026 (invocation log). It costs $0.37.
- **Eval Gate 2 on each test table.** It failed three tests on 21 Oct 2026, two on 27 Oct 2026 and 14 on 18 Sep 2026.
- **The full QA re-run each round.** A3 and C4 passed round 1 and failed round 2 on 27 Oct 2026; B3 on 4 Nov 2026 and C3 on 5 Nov 2026 did the same.
- **Step 11 evals after QA.** On 21 Oct 2026 QA passed all 19 checks and Step 11 still caught F1 and G3 defects.
- **The independent trace auditor and its full source re-read.** It overruled A1 on 25 Sep 2026 and 5 Nov 2026, and caught the 18 Sep 2026 misquote.
- **The cross-section dedup in the orchestrating thread.** It is held fixed, and A4 depends on it.
- **Opus in the parent and Sonnet 5 in the gates, QA and auditor.** Generation, quote fidelity (G1) and clinical judgment stay on their current models.

## 5. Open questions for Danny

1. Will you start an AC run in a fresh session from a handoff file after a PRD session? If not, the alternative is one fresh Opus subagent that runs Steps 2 through 13. It cannot pause for a mid-run ruling like the A3 one on 27 Oct 2026, though.
2. On 21 Oct 2026, did you reject the first two trace writes on purpose, or was it permission-prompt friction? Change 2's saving depends on the answer.
3. Would you rather add a permission rule for `.claude/skills/*/observability/traces/` in settings than have the parent copy the file? That is a settings change, so it is your call.
4. Step 11 judge evals ran on Opus in R1 and on Sonnet 5 inside a subagent in R3. Which is intended? This plan assumes the parent on Opus, per `SKILL.md` Step 11.
5. Five traces have no Claude Code session: 25 Sep, 28 Sep (two runs), 4 Nov and 5 Nov 2026. The November traces cite Cursor agent-store paths. [Assumption: the September runs were also in Cursor (needs validation)] Cursor keeps no per-request cost, so these runs are unmeasured. Should the per-run figure count them?
6. Decision: evals-advisor change E also edits `SKILL.md` lines 679 and 680, so this skill waits for that subagent. Its $0.06 is counted in the evals-advisor plan, not here.
