# Skill efficiency recommendations (Claude Code)

Four skill changes would have saved $12.26 in this window without dropping a check or moving judgment off its current model. Four more save launches but have no attributed dollars. The ranked list is first; the per-skill detail and the method follow.

Push back on the premise: skill text is not where most of the money goes. Subagents carried a fixed base context that cost $204.03 in the window, and long parent threads made every turn expensive (see "Outside the ranking").

> **Source:** Claude Code logs in `~/.claude/projects/-Users-dpedrini-Projects-dannys-pm-workspace-care`. Window: sessions whose first record falls 21 Sep 2026 through 2 Nov 2026, Eastern time. Cost per session: `totalCostUSD` on its last `cost-state` record. Window total: $734.58 across 76 distinct sessions. Method below.

## Ranked changes

| Rank | Skill | Change | Saving in window |
| --- | --- | --- | --- |
| 1 | provider-draft-failure-modes | QA agents read the first reader's saved full read of each Jira ticket instead of reopening it | $7.19 |
| 2 | prd-generator | Merge the Scope and Content QA groups into one judgment subagent per round | $2.66 |
| 3 | evals-advisor | One batched QA subagent at the end of the run instead of one per edit | $1.74 |
| 4 | todo-manager | Run the update in one fresh subagent when the parent thread is long | $0.67 |
| 5 | bug-ticket | Narrow the trigger so filing agents in another skill's run do not load it | Launches only |
| 6 | dashboard-requirements | Merge the Structure, Presentation and Definitions QA groups into one judgment subagent per round | Launches only |
| 7 | agent-architect | Make "batch graders that read the same inputs" and "reuse the first grader's saved reads" the default QA pattern | Launches only |
| 8 | acceptance-testing-generator | Batch requirement documents into fewer subagents, keeping Eval Gate 2 per document | Launches only |

Total with dollars: **$12.26**, which is 2.2% of the $569.82 attributed to these eight skills.

> **Source:** each row's estimate is derived in its skill section below, from the same logs and window.

## Method

> **Source:** same logs and window. Method:
> - **Window dating.** First record's timestamp, converted to Eastern time. Under UTC dating, session `e70f0f05` (2 Nov 21:52 ET) falls out of the window. That would cut provider-draft-failure-modes to $0.36 and the window total to $672.90.
> - **Use signals.** A session uses a skill when it has a `Skill` tool call (parent or subagent), a `<command-name>/skill</command-name>` record in the parent, or a parent `Read` of `.claude/skills/<name>/SKILL.md`. String mentions do not count.
> - **Mixed sessions.** A session with signals for two or more skills is mixed. Its cost goes to no skill.
> - **Copies.** Eight zero-cost transcripts share at least 90% of their API request IDs with another session; seven are copies of `6410cf4e` or `0ce68782`. They are forks, not new spend, and are excluded from session and subagent counts.
> - **Subagent launches.** `Agent` or `Task` tool calls, deduplicated by tool-use ID.
> - **Subagent calls.** Unique API request IDs inside `subagents/*.jsonl`, excluding synthetic error records.
> - **Per-request dollars.** Per-model token rates fitted to every `cost-state` `modelUsage` block (fit residual under $0.002 for Sonnet 5, Sonnet 5.5 and Opus 5.5). Computed session totals land within 5% of logged totals where every transcript exists (`9acfc201`: $11.21 vs $11.22; `e70f0f05`: $173.99 vs $166.69).
> - **Setup cost.** An agent's calls until its first tool call that is not `Read`, `Grep`, `Glob` or `ToolSearch`. Merging agents is credited only with the setup cost of the agents removed, which is a lower bound.

The `Skill` tool fired 19 times in the window (16 in parent threads, 3 inside subagents) and 21 times across all logs. I could not reproduce the 22 in the brief. The `attributionSkill` field tags at most 6% of parent spend in these sessions, so it is not used for cost.

## Measurements for the top 8

Top 8 by attributed dollars among skills in `.claude/skills/`. acceptance-testing-generator and make-deck tie at $0.00; acceptance-testing-generator takes the slot on launches (2 vs 1). Subagent figures cover every session that used the skill, with single-skill sessions only in parentheses.

| Skill | Sessions (single / mixed) | Skill-tool launches | Other signals | Attributed $ | Mixed $ (not attributed) | Subagent launches | Subagent calls | SKILL.md: one subagent per item? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| provider-draft-failure-modes | 3 (3 / 0) | 1 | 2 slash, 1 SKILL.md read | $167.05 | $0.00 | 133 (133) | 2,058 (2,058) | Yes: per batch for extractor, blind re-extractor, adjudicator, second opinion, drafter and anonymizer; per group for dedup |
| bug-ticket | 2 (2 / 0) | 2, both inside subagents | 1 SKILL.md read | $162.60 | $0.00 | 74 (74) | 1,170 (1,170) | No; single-agent skill |
| evals-advisor | 3 (1 / 2) | 3 (1 inside a subagent) | none | $86.92 | $236.05 | 153 (10) | 1,785 (227) | No |
| prd-generator | 6 (2 / 4) | 1 | 2 slash, 4 SKILL.md reads | $72.13 | $370.51 | 262 (51) | 2,598 (392) | No per-item; one subagent per QA group per round, full set respawned each fix round |
| todo-manager | 1 (1 / 0) | 1 | none | $67.83 | $0.00 | 14 (14) | 308 (308) | No |
| dashboard-requirements | 4 (1 / 3), plus 7 copies | 0 | 2 slash, 3 SKILL.md reads | $13.03 | $82.45 | 65 (11) | 452 (29) | No per-item; one subagent per QA group per round, plus three lens subagents |
| agent-architect | 5 (1 / 4) | 4 | 2 SKILL.md reads | $0.26 | $229.53 | 116 (0) | 1,462 (0) | Not for itself; its templates set a fresh grader per fix and inherit every tool |
| acceptance-testing-generator | 3 (0 / 3) | 2 | 1 SKILL.md read | $0.00 | $196.57 | 116 (0) | 982 (0) | Yes: one subagent per requirement document in multi-document UAT mode |

> **Source:** same logs and window; counting rules in Method. Fan-out column from each skill's `SKILL.md` as committed, plus the uncommitted provider-draft-failure-modes edits (they change source loading and the Gate 2 `CALL` dict, not fan-out).

## provider-draft-failure-modes

**Measured cost.** $167.05 across 3 sessions, of which `e70f0f05` is $166.69. That session's subagents cost $146.04: 124 transcripts, 106 of them general-purpose agents on Sonnet 5.

**Waste.** Subagents reopened Jira tickets an earlier subagent had already opened: 47 of 65 tickets, 164 extra agent opens. QA agents made 108 Jira calls on such tickets, all of which existed before the round. The reopens cost $10.79, counting each call and the payload it carried through the rest of that agent's turns. Nine full-read agents handled three tickets or fewer each.

> **Source:** same logs and window; `e70f0f05` subagent transcripts, agents ordered by last write, `getJiraIssue` and `listJiraIssueComments` calls only. The session made no Jira writes, so no reopen was a filing read-back.

**Change.** The dedup agent that makes a call saves its full read (description, every comment, Development field) to `dedup/<key>.md`. The 2d dedup QA, the structure QA and later agents read that file. They reopen Jira only for a key whose file lacks a field or whose verdict they dispute.

**Saving.** $7.19, which is $10.79 less the cost of reading the saved files instead. [Assumption: a saved extract is one-third the tokens of the raw Jira responses (needs validation)] Non-QA agents also reopened tickets ($12.66), but parallel agents may have opened the same ticket at the same moment, so that is not counted.

**Quality kept.** Every dedup call still rests on a full read of the ticket. The dedup QA still checks every verdict against the ticket text.

**Do not cut.** One batch per agent (goal 2 in the skill). The blind re-extractor's independence. The second opinion. The three-round QA loop. Extraction, adjudication and blind scoring stay on Sonnet 5; the clinical and provider reviewers stay on Opus 5.5.

## prd-generator

**Measured cost.** $72.13 across 2 single-skill sessions: `a977e688` ($70.64) and `a23fb079` ($1.49). In `a977e688`, 27 QA judgment agents ran (Fidelity, Scope, Content, three phases, three rounds each). They cost $20.38, of which $7.99 was setup.

> **Source:** same logs and window; `a977e688` subagent transcripts, setup as defined in Method.

**Waste.** Scope and Content each open the same artifact, template and `evals.md` in separate contexts every round. Each judgment agent averaged $0.30 in setup before doing any judging.

**Change.** Run Scope and Content as one judgment subagent per round, with both eval lists. Add the report-completeness step dashboard-requirements already has: confirm the report covers exactly the assigned eval IDs.

**Saving.** $2.66: 9 fewer agents at $0.296 average setup.

**Quality kept.** Every eval still runs every round on the full artifact. Fidelity (hallucination, draft fidelity, source distortion) stays its own agent on its current model.

**Do not cut.** The full re-run on every fix round. The run traces show groups that passed one round and failed the next. Scope did so in draft round 2 and revision round 3 of `a977e688`. Fidelity did so in draft round 2 and revision round 3 of the 21 Oct run. The Opus 5.5 reviewer personas, which cost $9.87 in `a977e688`.

> **Source:** `.claude/skills/prd-generator/observability/traces/` runs dated 21 Oct, 26 Oct and 2 Nov 2026; failing eval IDs per round mapped to groups through the skill's `<eval_phase_map>`.

## evals-advisor

**Measured cost.** $86.92 in one single-skill session, `2c925ce8`. Parent turns on Opus 5.5 cost $39.31. The parent launched 10 agents; their 10 transcripts cost $25.59. The logged Sonnet 5 cost is $47.61, so $22.02 of logged cost has no matching request in any transcript. I could not find its cause.

> **Source:** same logs and window; `2c925ce8` `cost-state` `modelUsage` vs per-request dollars; parent `Agent` tool calls.

**Waste.** Seven separate QA check subagents ran, each loading its own base context. Their setup cost $2.03 of their $7.05 total.

**Change.** After Step 5 adoption, run one QA subagent over `evals.md` and every other file the run changed.

**Saving.** $1.74: 6 fewer agents at $0.29 average setup.

**Quality kept.** Every changed file still gets an independent QA read before delivery.

**Do not cut.** The QA itself. The user-acceptance gate before any write to `evals.md`.

## todo-manager

**Measured cost.** $67.83 in one session, `b1d4f7a7`. Only $30.82 of the computed $66.97 came after the skill loaded; the rest of the session worked on the few-shot exemplar library files. The five turns that did the to-do update ran at about 640,000 tokens of context and cost $0.90.

> **Source:** same logs and window; `b1d4f7a7` requests tagged `attributionSkill: todo-manager`, and cost split at the first `Skill` call.

**Waste.** A small edit paid for the whole parent thread on every turn.

**Change.** When the thread is long, run the to-do operation in one subagent on the session model. It reads the list, makes the edit and returns the changed line.

**Saving.** $0.67. [Assumption: a fresh Opus 5.5 agent does the same five turns for $0.23 (needs validation)]

**Quality kept.** Same skill rules, same file, same model.

**Do not cut.** Reading the list before every operation.

## bug-ticket

**Measured cost.** $162.60 across 2 sessions. `487c6f6b` is $151.39, but $113.66 of it ran before the skill loaded. It was a hand-run failure-mode round from before provider-draft-failure-modes existed. Two of its 71 subagents loaded bug-ticket; together they cost $6.62. `9acfc201` is $11.22.

> **Source:** same logs and window; cost split at the first skill signal, per-subagent dollars.

**Waste.** bug-ticket is an FPSE investigation skill: epic read, PRD search, Figma, code search. The two subagents loaded it for a Galen failure-mode round and used only file tools (Read, Bash, Write, Edit), none of its investigation steps. In the same session, QA agents reopened Jira tickets 155 times at $19.10. That is the provider-draft-failure-modes pattern, and its fix now lives there.

**Change.** Narrow the description to "a PM-reported FPSE bug that needs investigation", and say that filing drafts produced by another skill does not load it.

**Saving.** Launches only. The $19.10 is not counted here: it recurs only if a round runs outside provider-draft-failure-modes.

**Quality kept.** Every step of the skill for real FPSE bugs.

**Do not cut.** The draft-before-file confirmation. The no-fabricated-repro rule.

## dashboard-requirements

**Measured cost.** $13.03 in one single-skill session, `6410cf4e`. Parent turns cost $10.68 on Opus 5.5; the orchestrator writes the document. That session ran only the Structure and Fidelity QA groups (7 agents, $1.71), so there was nothing to merge without touching Fidelity.

> **Source:** same logs and window; `6410cf4e` subagent transcripts. Seven zero-cost copies are excluded (Method).

**Waste.** In mixed session `0ce68782`, Structure, Presentation and Definitions ran as 19 separate agents. That cost is not attributed.

**Change.** Run Structure, Presentation and Definitions as one judgment subagent per round. Keep the existing report-completeness check.

**Saving.** Launches only in attributed sessions.

**Quality kept.** Every eval every round.

**Do not cut.** Fidelity as its own agent. The orchestrator writing the document on its current model. The full re-run on fix rounds.

## agent-architect

**Measured cost.** $0.26 in one single-skill session, `8bf3a6b5`. Four mixed sessions cost $229.53.

> **Source:** same logs and window.

**Waste.** Not measurable here. Its templates are where the cost patterns above start: a fresh grader per fix, `model: opus` for every reviewer with "no exceptions", and no `tools:` field, so every subagent inherits every tool.

**Change.** In Step 2.6 and `references/qa-subagent-pattern.md`, make the default to batch graders that read the same inputs into one subagent. Also make later graders read the first grader's saved source reads instead of reopening sources.

**Saving.** Launches only.

**Quality kept.** Producer and grader stay separate; fresh-context grading stays.

**Do not cut.** The independent grader. Opus for reviewer personas.

## acceptance-testing-generator

**Measured cost.** $0.00 attributed: all 3 sessions are mixed, together $196.57.

> **Source:** same logs and window.

**Waste.** Not measurable. Multi-document UAT mode spawns one subagent per requirement document.

**Change.** Give each subagent two documents when their combined size fits one context, with a section prefix per document.

**Saving.** Launches only.

**Quality kept.** Eval Gate 2 still runs on each document's test table before consolidation.

**Do not cut.** Danny's scope confirmation of the document list. The cross-section dedup in this thread.

## Skills launched 3 or more times outside the top 8

| Skill | Skill-tool launches | Sessions (single / mixed) | Attributed $ | Mixed $ (not attributed) |
| --- | --- | --- | --- | --- |
| google-workspace (Anthropic plugin skill, not in `.claude/skills/`) | 4 | 4 (3 / 1) | $76.19 | $173.93 |

No other skill outside the top 8 reached three launches. google-workspace would rank fourth on dollars; it is excluded from the top 8 because it is not a repo skill.

> **Source:** same logs and window.

## Could not measure

- **Cursor.** Cursor keeps no per-request cost after January 2026, and I could not tie a Cursor chat to a skill. Nothing here infers Cursor use.
- **Unexplained logged cost.** $22.02 of Sonnet 5 cost in `2c925ce8` (evals-advisor) matches no request in its transcripts.
- **No cost-state.** Eight sessions have no `cost-state` record; none shows a skill signal.
- **Mixed-only skills.** make-deck, acceptance-testing-generator and most agent-architect use sit in mixed sessions, so their own cost is unknown.

## Outside the ranking

Every subagent starts with about 45,000 to 50,000 tokens of system prompt, tool definitions and memory files, and rereads it on every turn. [estimate range] Across the 738 subagent transcripts in the window (735 with a priced first call), that fixed base cost $204.03, which is 17% of the $450.09 in computed subagent spend. [Assumption: 75% of the first call's context is a fresh cache write, measured on one sample (needs validation)] Trimming that base helps every skill at once, but it is a settings and memory-file change, not skill text.

Moving general-purpose judgment subagents from Sonnet 5 to Sonnet 5.5 would halve their cache-read rate ($0.20 vs $0.10 per million tokens). That is a model change for clinical judgment, which this brief rules out.

> **Source:** same logs and window; first-call context per subagent transcript; fitted per-model rates.

## QA notes

One independent QA subagent recomputed the window, the top 8 costs and the subagent counts from the logs with its own code. No transcript text was printed.

- **Matched:** window total, distinct sessions, copies, all 19 `Skill` launches, every attributed and mixed dollar figure, every subagent launch count, the top 8 order, and the ranked total.
- **Fixed:** `2c925ce8` has 10 parent `Agent` launches, not 17; the earlier count matched raw lines that included request-shape records. The "7 missing transcripts" explanation is withdrawn.
- **Fixed:** subagent calls for bug-ticket, evals-advisor and dashboard-requirements were 1, 2 and 4 high because synthetic error records were counted.
- **Fixed:** the window has 738 subagent transcripts; 3 have no priced first call and sit outside the base-context figure.
- **Fixed:** an untagged percentage range in Method, and the launch definition now names `Task` as well as `Agent`.
