# Design record: `dashboard-requirements` skill

Built with agent-architect (Full Process) on 2026-09-10. This is the Phase 1 (Discover) and Phase 2 (Design) record, kept for iteration: when the template, gates, or eval suite change, start here. The orchestrator does not load this file at runtime.

Gold exemplar: `Project-Galen/Phase-1/Galen-Phase-1-Metrics-One-Pager-ADS-v2.md` (v2)
Negative exemplar: banned-sections list in `references/exemplars.md` (v1 file deleted; shapes retained there)
Sibling skill whose conventions this follows: `.claude/skills/prd-generator/SKILL.md`

---

## 0. Decisions from intake (Danny, 2026-09-10)

44 questions asked in one batch in chat, all answered.

| # | Topic | Decision |
|---|---|---|
| 1 | Scope | Care Product initiatives, ADS audience |
| 2 | Modes | Create and Revise, chosen at intake |
| 3 | Plan gate | Skill owns Plan, approve, Execute. Full evals, subagent review, and traces for each key step |
| 4 | Name | `dashboard-requirements` |
| 5 | Builds | One build is the base case; multi-build is an extension |
| 6 | Min inputs | PRD or one-pager naming the build, plus ADS leads. Danny will usually have more |
| 7 | Optional inputs | Sizing sheet, metrics inventory, dashboard best-practices reference, discovery syntheses, prototype code or Figma, prior review comments, upstream Google Doc |
| 8 | Inventory | Skill builds an exhaustive metrics inventory as an intermediate artifact, with QA subagent review, saved next to the output. Whittling happens at a later gate |
| 9 | MCP scope | All MCP sources in scope, read-only. Confluence, Google Docs, Sheets, Slack, GitHub are the common ones |
| 10 | MCP failure | Stop, per AGENTS.md |
| 11 | Doc comments | Read them, surface as candidates at the selection gate with provenance, never auto-adopt |
| 12 | Table columns | Six columns locked: #, Metric, Definition (numerator / denominator), Grain, Window, Good. Section-prefixed IDs |
| 13 | Sections | Every section from Business outcomes down is always included. Replace "Two builds, two randomizations" with an upfront section covering what the feature does, how it rolls out, and how and at what level the experiment arm is assigned. Streamline the Summary; v2's summary has ad hoc text |
| 14 | Count | No ceiling; flag above 35 at the selection gate and propose cuts |
| 15 | Tiers | Hero, Reconciling, Driver, Guardrail, Business outcomes definitions locked as proposed |
| 16 | Notes | Under-table note only when a definition makes a choice a careful reader would question |
| 17 | Stakeholders | Stakeholders and Informed tables with mailto links from the stakeholder directory. Never invent a name; `[TBD: role]` |
| 18 | Source block | Required whenever an upstream doc exists |
| 19 | Doc status | DRAFT, Last updated, PM lead, ADS leads. Locked |
| 20 | v1 sections | Generally not included. May be added ad hoc when a need arises. No detailed inclusion rules |
| 21 | Baseline/target | Hero metrics and Business outcomes only |
| 22 | Alarm lines | Every guardrail has one |
| 23 | Failure modes | Proposed list accepted. Add: not adhering to the specified sections, redundancy across sections, long paragraphs or walls of text. Use prd-generator's failure modes as inspiration |
| 24 | Numbers | Tag `[TBD: named owner]`, never invent, never a bare TBD |
| 25 | Revision | Show the touch list before writing |
| 26 | Questions | One big batch in chat, never AskUserQuestion |
| 27 | Selection gate | Candidates with tier, definition sketch, provenance; Danny approves before drafting |
| 28 | Reviewers | data-analytics-eng and pm-exec always; clinical-quality-exec when a guardrail is clinical; care-ops-exec when provider workflow or pay is touched. Add FE eng or Design for user-behavior metrics |
| 29 | Findings | Present consolidated Must Fix / Should Fix / Consider; apply nothing until Danny decides |
| 30 | Rounds | One revision pass, QA subagent, re-present. Two rounds, then flag persistent issues |
| 31 | Slack draft | No |
| 32 | Change log | One consolidated row per review round, requester is Danny |
| 33 | Eval granularity | Per-step |
| 34 | Code evals | Proposed list plus whatever the new failure modes suggest |
| 35 | Judge evals | Same |
| 36 | Tiers | Mechanical on haiku, judgment on full tier |
| 37 | Traces | Independent trace authorship |
| 38 | Gate evidence | Plan approved, metric list approved, reviewers spawned, reviewer decisions captured, QA passed, change log updated |
| 39 | Queryable | Metrics added, cut, or changed; MCPs and tools called; other context used |
| 40 | HITL | As proposed, no graduation plan; Danny automates further when he sees fit |
| 41 | Layout | `.claude/skills/dashboard-requirements/` with SKILL.md, references/, evals.md, observability/ |
| 42 | Exemplars | v2 gold; v1 for banned sections only |
| 43 | Iteration support | Yes |
| 44 | Always-load refs | forbidden-writing-patterns, voice exemplar, stakeholder directory, glossary. Anything else in the workspace loads when relevant, no special call-outs |

Plan-approval defaults, all accepted by Danny: section numbering 1, 2, O, A, (B, C), 3, 4, 5, 6; `frontend-eng-reviewer` for the user-behavior lens; three inventory lenses; reviewers opt-in in Revise mode; v2's state-progression prose kept as a conditional paragraph in §2; alarm format is v2's italic form, one form only.

---

## 1. Pre-flight

| Question | Answer | Result |
|---|---|---|
| One job in ten words? | "Produce ADS dashboard requirements docs" hides intake, planning, inventory, selection, drafting, review orchestration, revision | Full Process |
| Tools? | Read, Write, Edit, Glob, Grep, Agent, plus five MCP servers read-only | Full Process |
| Easy to catch mistakes? | No. A wrong denominator or invented number reaches ADS and costs a build cycle | Full Process |

QA subagents: included. Per Danny (Q3) and because the skill has more than three failure modes and writes files.

---

## 2. Discovery summary (4D canvas)

### D1 Demand

**Primary job:** Produce, or surgically revise, a dashboard requirements document for ADS that specifies every metric a Care Product build's dashboard needs, in the v2 shape, through gated steps Danny approves.

**Scope boundary.** Does not write SQL, LookML, event schemas, or tile layouts. Does not design the experiment or the launch plan. Does not write to Google Docs, Confluence, Slack, Jira, or any external system. Does not decide the metric list; Danny does at the selection gate.

**Input.** Create mode: a PRD or one-pager (Confluence, Google Doc, or local), ADS leads, output path, plus optional inputs (Q7). Revise mode: existing doc path, Danny's change instructions (the authority), optional review comments or threads.

**Output.** Markdown doc at the user-specified path. Intermediate metrics inventory saved next to it. Plan and touch lists in the scratchpad. Trace and log in the skill's observability folder.

**Success.** Danny approves at each gate without re-explaining the template. Every metric has a scoped numerator and denominator, a grain that can be counted, a window, a direction, and a tier. ADS can start defining each metric to build spec without a clarifying meeting. All adopted evals pass or carry a flagged persistent issue.

### D2 Data (context requirements)

| Data needed | Source | Availability | Sensitivity | Layer |
|---|---|---|---|---|
| Build description, requirements, PRD success metrics | PRD via Confluence MCP or local file | Always (required) | Internal | Domain |
| Sizing model: coefficients, dollar estimates, drivers | Google Sheet via MCP | Sometimes | Internal | Domain |
| Existing metrics inventory | Local file or none | Sometimes | Internal | Domain |
| Dashboard best-practices reference | Local file | Sometimes | Internal | Rules |
| Discovery syntheses, meeting notes | Local files | Sometimes | Internal | Domain |
| Prototype UI or Figma | GitHub MCP, local `prototypes/`, Figma MCP | Sometimes | Internal | Domain |
| Review comments and threads | Google Doc comments MCP, Slack MCP | Sometimes | Internal | Domain |
| Upstream Google Doc (working copy) | Google Docs MCP | Sometimes | Internal | Environment |
| Stakeholder names and emails | `Stakeholder Management/stakeholder-directory.md` | Always | Internal | Domain |
| Domain vocabulary | `Company-Context/Hims-Hers-Business-Terminology-Glossary.md` | Always | Internal | Domain |
| Writing rules | `forbidden-writing-patterns.md`, `danny-voice-exemplar.md` | Always | Internal | Rules |
| Template, taxonomy, question bank, briefs | Skill `references/` | Always | Internal | Rules |
| Gold exemplar | v2 doc | Always | Internal | Rules |
| Danny's intake answers | Conversation | Always after Step 2 | Internal | Intent |
| Existing doc (Revise mode) | Local file | Always in that mode | Internal | Domain |

### D3 Discovery (runtime strategy and tools)

| Data | Strategy | Tool | Failure fallback |
|---|---|---|---|
| PRD | Direct input path or Confluence ID; Read or Atlassian MCP | `Read`, `mcp__claude_ai_Atlassian__getConfluencePage` | MCP failure: stop per AGENTS.md; ask for paste, export, or access fix |
| Sizing sheet | Sheets MCP | `mcp__google-workspace__read_sheet_values`, `get_spreadsheet_info` | Stop per AGENTS.md if the user pointed at it; if not provided, business outcomes carry `[TBD: owner]` |
| Upstream doc and comments | Docs MCP | `get_doc_as_markdown`, `list_document_comments` | Stop per AGENTS.md |
| Slack threads | Slack MCP | `slack_read_thread`, `slack_read_channel` | Stop per AGENTS.md |
| Prototype code | GitHub MCP or local | `mcp__github__get_file_contents`, `Read`, `Glob` | Note gap; user-behavior metrics flagged as unverified against UI |
| Figma | Figma MCP | `get_design_context`, `get_screenshot` | Note gap |
| Repo references | Read | `Read`, `Glob`, `Grep` | Missing always-load file: stop and tell Danny |
| Subagents | Agent tool | `Agent` with `subagent_type` for reviewers, `general-purpose` for inventory, draft, QA, trace | Subagent failure: retry once, then stop and tell Danny |
| Output | Write, Edit | `Write` (create), `Edit` (revise and fixes) | Present in chat if write fails |

**Minimum toolset:** Read, Glob, Grep, Write, Edit, Agent, Bash (for mechanical evals: grep, wc). MCP tools as the inputs require.
**Dependencies:** Step 1 context load must succeed before Step 2 questions. Plan approval before inventory. Selection approval before draft.
**Parallelization:** Inventory lens subagents run in parallel. Reviewer subagents run in parallel. QA judgment groups plus the mechanical subagent run in parallel within a round.
**Write policy:** MCP is read-only in this skill. No tool that creates, updates, comments, or sends may be called.

### D4 Defense

**Pre-checks.** Mode known. PRD readable. ADS leads known or `[TBD]` accepted by Danny. Output path known. Revise mode: existing doc read in full; change instructions captured verbatim.

**Post-checks.** Per-phase evals (Section 6). Independent QA subagents at each phase. Independent trace authorship confirms gate evidence.

**Fallbacks.** MCP failure: stop. Missing sizing: `[TBD: named owner]` in business outcomes. Missing stakeholder: `[TBD: role]`. Missing threshold for a guardrail alarm: `alarm threshold: [owner]`. Unknown baseline or target: `[TBD: owner]`. Subagent failure: retry once, then stop and tell Danny.

**Failure modes.** One remediation type on one inspection target each.

| ID | Failure mode | Severity | Detectable by | Eval |
|---|---|---|---|---|
| FM01 | Invented number: a rate, count, dollar figure, sample size, ramp percentage, duration, or conversion factor with no source in inputs or intake answers | Critical | Judge | E06, E12 |
| FM02a | Unbounded denominator: denominator not bounded to a named population | Critical | Judge | E13 |
| FM02b | Tautological ratio: numerator and denominator defined so the ratio is fixed by construction | Critical | Judge | E14 |
| FM03 | Wrong grain: grain names a unit that cannot be counted for that metric, such as task grain for a prevented task | Critical | Judge | E15 |
| FM04 | Tier misplacement: metric placed in a tier its role does not fit per the taxonomy | High | Judge | E16 |
| FM05 | Build-spec leakage: SQL, LookML, event or field schemas, tile layout, or Looker explore names | High | Code | E02, E17 |
| FM06 | Coefficient conflation: two distinct sourced definitions merged or swapped, such as visit modality and app engagement | High | Judge | E18 |
| FM07 | Unapproved adoption: a metric, definition change, or reviewer suggestion present in the draft that Danny did not approve at a gate | Critical | Judge | E05, E19 |
| FM08 | Non-surgical revision: Revise mode or post-review edits touch content outside the approved touch list | Critical | Judge | E20 |
| FM09 | External write: any MCP call that creates, updates, comments, or sends | Critical | Code (ledger audit) | E21 |
| FM10 | Writing-pattern violation: em dash, forbidden word, filler phrase, vague range, banned opener or closer | Medium | Code | E22 |
| FM11a | Required section missing, duplicated, reworded, or out of template order | High | Code | E01, E23 |
| FM11b | Extra section present without a stated need | High | Judge | E24 |
| FM12 | Cross-section redundancy: the same fact, rationale, or definition stated in full in more than one place | Medium | Judge | E25 |
| FM13a | Over-long prose: a paragraph over four sentences or a sentence over 35 words | Medium | Code | E26 |
| FM13b | Prose carrying what the template puts in a table | Medium | Judge | E27 |
| FM14 | Guardrail without alarm line: a guardrail row whose Good cell lacks a sourced threshold or `alarm threshold: [owner]` | High | Code | E28 |
| FM15 | Baseline and target misplacement: Baseline and Target present outside Hero and Business outcomes, or absent there | Medium | Code | E29 |
| FM16a | Summary metric count differs from table row count | Medium | Code | E30 |
| FM16b | IDs not sequential within a section prefix | Medium | Code | E31 |
| FM16c | A referenced metric ID does not exist as a row | Medium | Code | E32 |
| FM17 | Dangling ownership: an open question without an owner, a bare TBD, or an alarm placeholder without an owner | Medium | Code | E33 |
| FM18 | Fabricated name: a person in Stakeholders, Informed, Owner, or Next steps not present in the stakeholder directory, the inputs, or intake answers | Critical | Judge | E34 |
| FM19 | Summary bloat: summary contains fields beyond the template's fixed set, or any field exceeds its sentence budget | Medium | Code | E35 |
| FM20 | Dropped approval: a metric or instruction Danny approved at a gate is absent from the draft or the revision | Critical | Judge | E36 |
| FM21 | Under-table note that does not earn its place: a note explaining something no careful reader would question, or restating the table | Low | Judge | E37 |
| FM22 | Inventory gap: a PRD success metric, launch-gate metric, or sizing driver with no candidate in the inventory | High | Judge | E09 |
| FM23 | Inventory fabrication: a candidate whose provenance is not one of PRD, sizing, inventory file, comment, synthesis, prototype, or explicit recommendation | High | Judge | E08, E10 |

**Complexity assessment.** Distinct responsibilities: 9 (intake, context load, clarifying questions, plan, inventory, selection, draft, review orchestration, revision), plus QA, evals, and trace. Critical: inventory completeness, definitional correctness, approval fidelity, surgical revision. Task type: agentic, gated. Pattern: sequential pipeline with human gates, fan-out for inventory and reviewers, iterative refinement for QA loops. Autonomous loop: no.

---

## 3. Decomposition decision

Superseded in part by §12 (v1.4): the orchestrator now writes the document; the draft subagent is retired.

**Responsibilities:** 9 > 3, so decompose. Critical responsibilities compete for attention (drafting versus definitional correctness versus approval fidelity), and they need different expertise (analytics engineering, product judgment, prose).

**Decision:** Orchestrator plus subagents, following prd-generator. The orchestrator holds the conversation, asks questions, runs gates, merges, fixes, and never self-evaluates. Subagents generate, review, and audit.

| Component | Type | Handles |
|---|---|---|
| Orchestrator (SKILL.md) | LLM, conversation owner | Steps 0 to 3, gates, merge, fixes during QA loops, revision application |
| Inventory lens subagents (3, parallel) | LLM, `general-purpose` | Exhaustive candidate generation, one lens each |
| Draft subagent | LLM, `general-purpose` | Writes the doc from the approved list |
| QA judgment subagents (per group) | LLM, `general-purpose`, full tier | Judge evals per phase |
| QA mechanical subagent | LLM, `general-purpose`, haiku | Code evals per phase, executed with grep and wc |
| Reviewer subagents | Existing `.claude/agents/*-reviewer` | Must Fix / Should Fix / Consider |
| Trace author subagent | LLM, `general-purpose` | Independent trace authorship with gate evidence |

Rationale for a draft subagent rather than the orchestrator drafting: fresh attention on the write against a strict template, and the orchestrator stays the editor. This is the prd-generator pattern and it is what kept v1's 27-page problem from recurring in v2.

Rationale for three inventory lenses rather than one subagent: Danny wants the inventory exhaustive (Q8). Three lenses with different framings surface more candidates than one pass, and the QA subagent dedups.

---

## 4. Architecture

### 4.1 Pattern

Sequential pipeline with four human gates, fan-out at inventory and review, QA loops after plan, inventory, draft, and revision. Two modes share Steps 0, 1, 9, 10.

### 4.2 Workflow (Create mode)

```
Step 0  Intake and mode          ask in chat if invocation lacks: mode, build, PRD location, ADS leads, output path, optional inputs
Step 1  Load context             always-load refs, skill refs, all inputs (MCP or local); record every source; MCP failure = stop
Step 2  Clarifying questions     one batch in chat from the question bank, filtered to what inputs do not answer; defaults stated;
                                 never the AskUserQuestion tool (Q26)
        Intake gate              coverage table over question-bank sections; follow-ups only for failing rows
Step 3  Plan                     run folder; sections, build summary, exposure definitions, candidate heroes, outcome chain,
                                 reviewer set, exclusions. P-phase QA. GATE 1: Danny approves
Step 4  Inventory (fan-out)      3 lens subagents in parallel; orchestrator merges and dedups; I-phase QA loop;
                                 save <Build>-Metrics-Inventory.md next to output
Step 5  Selection                present by tier with keep/cut recommendation and provenance; flag >35.
                                 GATE 2: Danny approves list. Record adds, cuts, re-tiers
Step 6  Draft (subagent)         approved list + intake transcript + plan + template + taxonomy + exemplar + inputs; Write
Step 7  Draft QA loop            D-phase evals, qa_loop_protocol (max 3 rounds)
Step 8  Reviewer round           reviewers in parallel; consolidate one table, Severity = Must Fix / Should Fix / Consider
                                 GATE 3: Danny decides per item
Step 9  Revision                 touch list, GATE 4: Danny approves; Edit only; change-log row; R-phase QA loop
                                 (fidelity, surgical, full D regression); up to 2 fix rounds, then flag persistent issues
Step 10 Compile, log, trace,     compile each eval's final-round verdict from the QA loops (no re-run); JSONL entry;
        deliver                  independent trace authorship subagent; present
```

Step numbers are identity labels shared by both modes, not positions. Revise mode lists them in its own execution order.

**Run artifacts (scratchpad, `dashboard-requirements/<slug>/`).** At every gate the orchestrator writes the approved artifact to `gate-N.md`: the approved plan, the approved metric ID list with definition sketches, the reviewer decisions per finding, the approved touch list. QA and trace subagents read these files, never chat history. The orchestrator also appends every MCP call to `mcp-ledger.jsonl` as it is made: server, tool, resource ID, purpose, `write: false`. The trace author audits the ledger.

### 4.3 Workflow (Revise mode)

Execution order; step labels are the Create-mode identities.

```
Step 0  Intake                   existing doc path, change instructions verbatim (the authority), optional comments or threads
Step 1  Load context             the doc in full, always-load refs, skill refs, any pointed-to sources
Step 2  Clarifying questions     only where instructions are ambiguous; one batch
Step 3  Change plan              each instruction mapped to touched sections and lines; comments listed as candidates, not changes
                                 GATE: Danny approves the touch list
Step 9  Apply                    Edit only; change-log row; R-phase QA loop (fidelity, surgical, full D regression)
Step 8  Reviewer round (opt-in)  only if Danny asks
Step 10 Compile, log, trace, deliver
```

### 4.4 QA loop protocol (shared)

Same as prd-generator. Spawn all of the phase's judgment groups plus the mechanical subagent in parallel. All pass: proceed. Any fail: orchestrator applies targeted fixes, respawns the full set. Max 3 rounds per phase. Persistent issue flagged as verbatim or mutated. Run-level ceiling: at 3 unresolved issues, pause and ask Danny.

### 4.5 Human-in-the-loop classification

| Decision point | Classification | Rationale |
|---|---|---|
| Reading inputs, recording sources | Agent autonomous | Deterministic; trace audits it |
| Choosing which question-bank questions to ask | Agent autonomous | Coverage gate catches gaps |
| Plan content | Flag for human (Gate 1) | Shapes everything downstream |
| Inventory generation and merge | Agent autonomous | QA subagent checks completeness and provenance |
| Metric list, tiers, cuts | Flag for human (Gate 2) | Product judgment; Danny's call |
| Definition wording inside the approved list | Agent autonomous | Evals check denominator, grain, window |
| Under-table notes | Flag for human at Gate 3 review | Danny cut most of them in the Galen run; no graduation plan per Q40 |
| Stakeholder and owner names | Agent autonomous from directory and inputs; `[TBD: role]` otherwise | Never invented |
| Reviewer set selection | Agent autonomous with stated rationale | Rules are explicit (Q28) |
| Reviewer finding adoption | Flag for human (Gate 3) | Q29 |
| Revision touch list | Flag for human (Gate 4) | Q25 |
| Change-log row | Agent autonomous | Template-driven |
| Persistent QA issue after 2 fix rounds | Flag for human | Q30 |

No Graduate items (Q40).

### 4.6 Reviewer set

| Reviewer agent | When | Why |
|---|---|---|
| `data-analytics-eng-reviewer` | Always | Denominators, grain, instrumentation readiness, experiment design |
| `pm-exec-reviewer` | Always | Metric quality, business case, narrative, decision-readiness |
| `clinical-quality-exec-reviewer` | Any guardrail is a patient-safety or care-quality signal | CQS, patient harm, sign-off |
| `care-ops-exec-reviewer` | Any metric touches handle time, skips, task routing, or provider pay (decisions-per-hour tiers) | Handle time, workforce, pay operationalization |
| `frontend-eng-reviewer` | Build changes what a provider or patient sees | Telemetry: which user behaviors are measurable in Amplitude. Chosen over ux-design-reviewer because its lane includes telemetry and observability |

Reviewers receive the draft, the PRD, and the approved metric list. They report; they never edit. The orchestrator consolidates into one table: Finding | Reviewer(s) | Severity (Must Fix, Should Fix, or Consider) | Affects (metric IDs or sections) | Recommendation. Duplicates merged with every reviewer attributed. Danny decides per row: adopt, decline, or defer to open questions.

### 4.7 Context architecture (six layers)

| Layer | Content | Structure | Fallback |
|---|---|---|---|
| Intent | Mode, build, output path, Danny's intake answers and gate decisions | Conversation, recorded verbatim to the run folder for subagents | Ask |
| User | Danny's voice exemplar, writing rules | Always-load files | Stop if missing |
| Domain | PRD, sizing, syntheses, prototype, comments, glossary, stakeholder directory | MCP reads and local files, each logged as a context source | Stop on MCP failure; `[TBD]` on optional |
| Rules | Template, taxonomy, question bank, subagent briefs, evals.md, AGENTS.md MCP rule | Skill references | Stop if missing |
| Environment | Existing doc (Revise), upstream Google Doc state, run folder | Read at Step 1 | Note absence in source block |
| Exposition | The doc | Template | n/a |

### 4.8 Attention strategy

SKILL.md leads with role and the ten-step workflow. Hard constraints repeat the five critical failure modes (FM01, FM07, FM08, FM09, FM20) and ban the AskUserQuestion tool for any question asked of Danny (Q26), matching prd-generator. Final reminder restates: never invent a number, never adopt without a gate, never edit outside the touch list, never write to an external system. Detail lives in references; SKILL.md landed at 274 lines.

---

## 5. Output template

Implemented in `template.md`. Section order: top matter, Summary (seven fixed labels), Stakeholders, Informed, 1 Build rollout and arm assignment, 2 Exposure and population (conditional state-progression paragraph plus definitions table), O Business outcomes (eight columns), A [Build] with four tiers (Hero eight columns; Reconciling, Driver, Guardrail six), B and C multi-build only, 3 Slices, 4 Next steps for ADS, 5 Open questions, 6 Change log.

Baseline and Target cells: sourced value with inline source, or `[TBD: owner]`. Never invented (Q21, Q24). v2 has no Baseline or Target column anywhere, so template.md carries one illustrative row, marked synthetic. Alarm line format in Good, one form only: `↓ *(alarm if >20%; PRD §X)*` with a sourced threshold, or `↓ *(alarm threshold: [owner])*` without one (Q22). v2's guardrail rows without alarm text (A17 to A20, B6 to B8) predate this rule; exemplars.md says so.

---

## 6. Evals (per-step, four phases)

Phases: **P** plan, **I** inventory, **D** draft, **R** revision. R re-runs all D evals as a regression gate and adds E20 surgical and E36 widened to all gates. Evals-advisor ran in design-time mode on 2026-09-10 and proposed 35 evals; adopted as 37 after splitting FM02 (E13, E14) and FM13 (E26, E27). E21 audits the MCP ledger in the final QA phase. Suite: 17 Code on haiku, 20 Judge on the full tier, grouped Fidelity, Definitions, Structure, Presentation.

Evals-advisor flagged three detectability limits, all accepted: FM07 and FM20 need gate snapshots on disk (added, 4.2); FM09 is only as good as the ledger, which the orchestrator self-reports; FM12 redundancy detection degrades on very large docs, and a similarity pre-pass is a future improvement, not v1.

---

## 7. Observability

Full with independent trace authorship (Q37). Log written by the orchestrator; trace written only by the trace author subagent from artifacts on disk, with `gate_evidence` (approved ID lists and touch lists embedded), `metric_deltas`, `qa_rounds`, `reviewers`, every ledger line, and `independently_authored: true`. Schema in `trace-schema.md`.

---

## 8. Skill file layout

```
.claude/skills/dashboard-requirements/
├── SKILL.md
├── evals.md
├── references/
│   ├── template.md
│   ├── metric-taxonomy.md
│   ├── intake-question-bank.md
│   ├── subagent-briefs.md
│   ├── drafting-rules.md   (v1.4)
│   ├── trace-schema.md
│   ├── exemplars.md
│   └── design-record.md   (this file)
└── observability/
    ├── README.md
    ├── invocation-log.jsonl
    └── traces/
```

---

## 9. Plan QA record (2026-09-10)

Plan QA subagent: 15 checks, 8 passed, 7 failed. All 7 fixed before build: reviewer-findings schema unified on Severity = Must Fix, Should Fix, Consider; FM02, FM11, FM13, FM16 split into one remediation each; §2.1 state-progression prose restored as conditional; AskUserQuestion ban added; column header text fixed to the locked form; step numbers declared identity labels; Step 10 compiles final-round verdicts rather than re-running. The two MCP tool names it flagged as lacking workspace precedent, `list_document_comments` and `get_file_contents`, were verified present in the live tool catalog.

Evals-advisor prompt-fix suggestions, all adopted: exemplars.md disclaims v2's alarm-less guardrail rows and missing Baseline/Target columns; template.md carries a synthetic Baseline/Target row; one alarm format; reviewer trigger examples in the briefs; gate snapshots on disk; FM16 split; note calibration examples in the taxonomy.

## 10. Skill QA record (2026-09-10)

Mechanical self-check on all files: zero em dashes after replacing the "not run" placeholder glyph in evals.md, zero forbidden words, one vague quantifier fixed in exemplars.md.

Independent skill QA subagent: 10 checks, 6 passed, 2 fixed in place, 3 escalated. Fixed: E22's vague-range exclusions given concrete regex patterns for ISO dates, M/D/YY dates, and PRD section references; E35's sentence counter given E26's non-terminal exceptions. Escalations, all resolved by the orchestrator as design implementation: "dashboard best-practices reference" added to the optional inputs list and the when-relevant context line; two fallbacks added (missing always-load file stops the run; a failed subagent is retried once, then the step stops); care-ops-exec trigger unified across SKILL.md, subagent-briefs.md, and E04 as "handle time, skips, task routing, or provider pay (decisions-per-hour tiers)".

Known limits at v1.0: no run has executed yet, so every eval's Last Result is "not run" and every judge eval's examples are "none yet". The first real run should be followed by the post-run evals-advisor offer at Step 10.

## 11. Patch record (2026-09-29, v1.1 and v1.2)

Source: Danny's Confluence edit of the Provider Drafts run (page 3480027223), sorted by evals-advisor in post-run mode. Intake question bank changes are left to Danny.

| Intake decision | Superseded by |
|---|---|
| 15 Tiers | Business outcomes are dollars or retention; heroes are the leading indicators that gate the ramp; a second role goes in a note |
| 29 Findings | Findings tagged Defect or Addition; delegated adoption covers Defects only. A deferral reaches Open questions only past the Step 9.1 bar, so "defer to open questions" in §4 is superseded |
| 32 Change log | A row only for reader-relevant changes; Danny may decline it |
| 42 Exemplars | Provider Drafts Confluence snapshot added as a second gold exemplar |

Template changes: the title adds "Experimentation &", and Hard dependency is optional. "What this is not" becomes bullets with the ADS test-plan line; launch date may carry program status; §2 merges Control and Exposure inheritance; §4 gains a standard sentence. New rules: taxonomy § Citations; complement, subset, and input-only patterns; the Gate 2 target question; the Step 9.1 open-questions bar; and the Revise-mode sync from upstream.

Evals: E38 added (generalization: the taxonomy already banned complement pairs as two rows). E17's pattern extended (generalization: event field lists passed as prose). E12, E16, and E35 realigned with the prompt fixes. A mechanical internal-reference eval was deferred: the citation rule was unstated, so this is a specification fix first, and an eval follows only if leakage recurs.

v1.2, same day: E21's verb match made whole-word with read-verb names exempt. E26 counts a period-ended bold lead as a sentence, and E37 no longer judges length. The intake transcript gets a block format, and E39 checks it. The first sync from upstream ran on the Provider Drafts document.

## 12. Patch record (2026-10-29, v1.4)

**Decision.** The orchestrator writes the document at Step 6. The draft subagent is retired, and its rules moved to `references/drafting-rules.md`, which Step 6 re-reads from disk with the gate files, template, taxonomy, and exemplars. Subagents still build the inventory lenses, run QA, review, and author the trace. QA independence is unchanged: the orchestrator writes, and QA subagents judge.

**Evidence, December Provider Pay Model run (trace `observability/traces/2026-10-28_1300_provider-pay-emr-december.json`).**

| Finding | Source |
|---|---|
| Gate-2 carried O1's "(old-model decisions per payable hour sets the counterfactual tier)" and A17's "Fast-side threshold not set." The draft dropped both. Reviewers caught them at Step 8, and gate-4 items T8 and T18 restored them | Trace `metric_deltas`; E36 example in `evals.md` |
| Run-specific rules had to be hand-written into the draft brief, among them the $1.2M target correction, open items stay open, the two eligible populations, and the confounds. Anything left out was lost | Danny, 2026-10-28. The brief is not on disk |
| Draft QA round 1 failed 8 evals: E15, E16, E23, E25, E26, E27, E35, E37. E16 and E23 were rubric gaps v1.3 fixed, which leaves 6 | Trace `qa_rounds.D` |

**Inventory considered and kept with subagents.** Danny first moved the inventory to the orchestrator too, then reversed it. The inventory is a breadth task before any approval exists, so it has no approved clauses to drop.

The context the lenses need is on disk (intake transcript, gate-1). The 10/28 inventory passed I-phase round 1 with 62 candidates. Three parallel lenses avoid one author anchoring across lenses. The orchestrator still merges.

**Superseded.** §2 D3 Subagents row (draft no longer a `general-purpose` subagent); §3 Draft subagent row and its rationale paragraph; §4.2 Step 6 "(subagent)".

**New risk and guard.** By Step 6 the orchestrator's context is long, and chat memory can override a file (a superseded number, a dropped clause). Guard: Step 6 re-reads its files from disk and treats them as the authority. E36 compares clauses inside kept rows (v1.3), so a drop is caught either way.

**Trade-off accepted.** §3's reason for a draft subagent was fresh attention on a strict template, which kept v1's 27-page shape from recurring. That is given up. Guard: Step 6 re-reads the template and both gold exemplars, and E23, E26, E27, and E35 still check shape and length.

**Baseline for the next run.** Draft QA round 1: 6 failures. Approved clauses restored at Step 8: 2.

## 13. Patch record (2026-11-06, v1.5)

**Decision.** Token-efficiency changes from `AI-Reference-Materials/Claude-Code-and-Skills/Token-Spend/skill-plans/dashboard-requirements.md` §3. Every check still runs, and every fix round still re-runs the full set. Fidelity stays its own subagent. The orchestrator still writes the document, and reviewers stay on their own types and models.

| Change | Where |
|---|---|
| Offer `/compact` after the Gate 2 snapshot; Danny may decline | SKILL.md Step 5.5, Step 6.0; `drafting-rules.md` |
| Drafting-only files and the voice exemplar load at Step 6, not Step 1 | SKILL.md `<context_sources>`; `drafting-rules.md` |
| QA subagents read eval slices; the orchestrator no longer loads `evals.md` (E41) | `scripts/eval-slice.py`; `<qa_loop_protocol>` step 1 |
| One merged judgment subagent in D and R, given the union of the three groups' references (E42) | `<input_routing>`; briefs §4 |
| `dashboard-qa` agent type for QA, lens, and trace subagents (E44) | `.claude/agents/dashboard-qa.md`; briefs |
| Trace skeleton script; the trace author writes through its merge step | `scripts/trace-skeleton.py`; briefs §6 |
| Reports saved verbatim from transcripts (E43) | `scripts/save-qa-report.py` |
| Mechanical checks as a script | `scripts/mechanical-checks.py`; briefs §5 |

**Superseded.** §0 row 36 (Mechanical on haiku); §2 D3 Subagents row (`general-purpose` for inventory, QA, and trace) and its parallelization note; §3 `general-purpose` type on the lens, QA, and trace rows, and the QA mechanical subagent row; §4.4's mechanical subagent.

**New risk and guard.** A compacted context loses any chat decision missing from the gate files. Guard: Step 5.5 checks the gate files before offering, and E36, E19, and E12 still run in D. The merged subagent may raise verdict variance on E15, E18, E25, and E27. Guard: E42 requires quoted evidence on every row.

**Deviation from the plan.** The plan gives the trace author Write. One agent type cannot grant Write to the trace author alone, so `dashboard-qa` has no Write, and `scripts/trace-skeleton.py merge` writes the trace.
