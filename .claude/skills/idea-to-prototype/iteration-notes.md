# idea-to-prototype — Iteration Notes

**If this skill misbehaves:**
1. Which stage (0–5) failed?
2. Subagent prompt issue or orchestration issue?
3. Prompt → refine the relevant template in the matching `references/` file
4. Orchestration → adjust gate logic in SKILL.md
5. Was the subagent's proof-of-read block present and accurate? A missing one means context discipline broke
6. Check `.pipeline/reviews/_fidelity-review.md` for specific failures

**Current version:** 5.1 | **Architecture:** SKILL.md (405 lines) + `references/` (7 files, prompt templates loaded per stage)

## Version History

### 5.1 (2026-08-03) — Model tiering + Stage 2 cross-spec restructure

Two changes, both from the reverted-pending-evaluation set, re-introduced with explicit approval and better-informed designs. The difference from the first attempt: this round had **real run telemetry** to design against. Both logged production runs used 52 subagents and scored 97 and 100 fidelity; only one recorded a duration — 17,700s (4.9 hours). The other logged `duration_s: null`, so treat 4.9 hours as a single data point, not an average.

**1. Model tiering — tier by verifiability, not perceived difficulty.**

A cheaper model is safe only where a wrong answer surfaces deterministically. Applied to exactly three agents:

| Agent | Model | Why safe |
|---|---|---|
| Stage 1A freshness check | `sonnet` | Diffs 8–12 known claims against a baseline; every citation is grep-verifiable |
| Stage 2 question synthesizer | `haiku` | Pure consolidation — originates no judgment |
| Stage 4.7 trace author | `sonnet` | Structured inspection against a fixed schema + JSONL cross-check |

Explicit do-not-tier list, with reasoning, in SKILL.md's `<model_tiering>`. Implementers and validators are named specifically: their checklists are ~70% mechanical and the evals double-cover the grep-able items, which makes tiering tempting — but "the evals will catch it" is the reasoning that produced the v3.1 regression. 🧊 Cold start inherits the session model everywhere; there is no baseline to diff against, and the scaffolder's output is inherited by every future run.

**Honest scope correction:** the original analysis estimated this at "roughly a third of agents." That was wrong — it was written before enumerating where the agents actually are. Of ~52 agents, ~43 are per-component writing and adversarial review, which is exactly what must not be tiered. Tiering reaches 3 agents, ~5% of run cost. It is free correctness hygiene, not the lever that makes a run cheap.

**2. Stage 2 restructured around its actual failure mode.**

Telemetry showed both runs failed Stage 2 identically, and not on per-spec quality:
- `non-rx-combo-pack`: all 8 specs FAILED round-1 audit on **cross-spec seam conflicts** — 18 resolutions, 4 fix editors, 4 re-audit verifiers to reach 8/8 PASS
- `non-rx-bulk-pack`: 3 rounds of fix-loops on **contract drift across parallel writers**, resolved by declaring spec 01 the single contract authority

Parallel writers each produce a locally-correct spec and collectively produce an inconsistent set; isolated per-spec auditors structurally cannot see it. The expensive part was never the audit — it was the multi-round fix-loop afterward. Stage 2 now attacks this twice:

- **Preventively (Step 2.1):** the parser designates a **contract authority** — one spec owning the canonical definition of every cross-cutting type, prop, and shared interface, with an explicit ownership table. Every other spec references those definitions and must not restate them. This is the `non-rx-bulk-pack` fix applied up front instead of after three rounds.
- **Detectively (Step 2.3):** a dedicated **cross-spec auditor** reads all specs in parallel with the per-spec auditors, hunting only seam conflicts — contract violations, type disagreements, naming drift, duplicated responsibility, seam gaps, state-simulation divergence.

Per-spec auditing is risk-batched to pay for it: dedicated auditors for the contract authority and for complex specs (≥8 AC, ≥150 lines, page-level, or with Required Additions), one batched auditor for stubs and fixtures. Measured spec size varies tenfold (28–387 lines). Per-spec checklist grew to 9 items (added contract compliance).

Gate 2 now requires a cross-spec PASS in addition to every per-spec PASS. One cross-spec re-run is allowed, then escalate — repeated seam failures mean the decomposition is wrong, not the specs. Eval G4 extended to check the cross-spec verdict and to take the highest audit version per spec as authoritative. Gate 2 trace evidence gains `cross_spec_audit_pass` and `contract_authority`.

**Framing note:** the original analysis pitched auditor batching as a token cut. The telemetry reframes it as a correctness restructure that happens to be cheaper — the cross-spec pass is the point, and batching funds it.

**Defects found by the post-5.1 `/audit` and fixed:**

| Defect | Impact | Fix |
|---|---|---|
| Implementers and validators never received the contract-authority definitions | **Producer-consumer break.** Non-authority specs reference shared types by name only, so an implementer had no source to resolve the real shape from — it would have had to infer or invent it, which is the drift the mechanism exists to prevent, moved downstream | Contract definitions pasted into both the implementer and validator prompts; new validator check 7b; added to `context-contract.md`'s always-PASTE list |
| Cross-spec auditor sent a PATH with no proof-of-read | Violated v5.1's own hard constraint, in the one new dispatch that most needs to distinguish a real contract violation from two specs correctly sharing an app-wide type | Proof-of-read added, targeting `## Type Interfaces` |
| Eval G4 matched only the `-v2` revision suffix | Real artifacts use **two** conventions — `-v2` (non-rx-combo-pack) and `-r2`/`-r3` (non-rx-bulk-pack). G4 would have taken a superseded round-1 FAIL as authoritative and produced a false Fail against bulk-pack | G4 now globs `NN-spec-audit*.md`, extracts any trailing integer, takes the highest, and falls back to mtime on ties. Pre-v5.1 prototypes with no cross-spec audit are noted, not failed |
| SKILL.md still listed model tiering and risk-batched auditors as "reverted, pending evaluation" | Self-contradiction against the 5.1 entry directly above it — same defect class as a prior round | Replaced with a status table; narrowed trace author marked reverted *permanently*, with the reason |
| No app-wide vs. contract-authority type ownership rule | The same type could legitimately be claimed by both layers | Scope boundary added to Step 2.1 plus a hard constraint: a type has exactly one home |
| Gate 2's cross-spec requirement lived only in workflow prose | Its sibling rule (no Stage 3 before Gate 2) is a hard constraint; this wasn't | Folded into the existing hard constraint |
| `HOW-IT-WORKS.md` header still said Version 5.0; `examples.md` still described 8 writers → 8 independent auditors | Stale docs | Both updated |
| "~4.9 hours per run" attributed to both runs | Only one run recorded a duration; the other logged `duration_s: null` | Restated as a single data point |


### 5.0 (2026-08-03) — Efficiency without quality loss

**Motivation:** runs took hours and burned very large token volumes. Analysis found the cost was in plumbing, not in the quality machinery — chiefly ~36 full-file pastes of a 500–1,216-line design system per run, emitted as orchestrator *output* tokens.

**The constraint that shaped every change:** v3.1's context-dilution regression (see 4.0 below). Cost reduction had to avoid reducing what each subagent actually reasons from. The resolution is the **context contract**: paste *framing*, path *lookups*, always require a proof-of-read. Deliberately conservative — the aggressive variant (path everything, ~300-line SKILL.md) was considered and rejected as too close to what broke v3.1.

**1. Design system referenced and incrementally updated, not copied.**
- App-wide `_design-system/<app>/design-system.md` is the single source of truth. Each prototype gets `design-brief.md` — feature-local only, ~60–150 lines. Previously each prototype held a full copy: measured 117–1,216 lines against an app-wide 655, i.e. ~655 duplicated lines across 7 prototypes.
- New **promotion protocol** (Stage 1B): Established (≥3), non-feature-specific findings graduate into the app-wide file at Gate 1, tagged and recorded in a Promotion Log. Guards: user approval required, citation re-verified by the auditor, never silently overwrite, never promote below threshold.
- This fixes a real leak. `data-grid-styles.ts` (Established, 17 importing files) and `DialogContext` (Established, 215 call sites) were both filed `[Feature-specific]` in `non-rx-combo-pack`'s copy — app-wide facts stranded in a per-feature file, re-discovered from scratch by later runs.
- Allowlist is now the **union** of the two files. `evals.md` G1/G2/G5/G6 updated, with a documented pre-v5.0 fallback so the 7 existing prototype copies and the 2 legacy `design-brief.md` prototypes stay evaluable.

**2. Context contract (`references/context-contract.md`).** Framing (spec, brief, Visual Identity, Tech Stack, Common Mistakes, requirement excerpts, review reports being responded to) is pasted in full. Lookup (token tables, typography/spacing scales, component inventory, type interfaces, data/forms detail, routes) is pathed with a **mandatory proof-of-read**: the subagent must quote specific values + citations before producing its deliverable. Output missing that block is re-dispatched, not accepted. Escape hatch: a failed lookup escalates that section to PASTE on retry; recurring escalations mean the boundary is wrong and the contract gets fixed.

**3. Progressive disclosure.** Prompt templates moved to `references/` (7 files), loaded per stage. SKILL.md went 1,243 → 367 lines and retains every hard constraint, gate, failure mode, and control-flow decision. Subagents receive byte-identical prompts; only the orchestrator's simultaneous load changes. New HIGH failure mode: **improvised subagent prompt** — the mechanism by which v3.1 degraded, and it fails silently (binary evals still pass while the prototype looks wrong).

**4. Starter template.** `_design-system/<app>/starter/` — a runnable scaffold promoted from the first run to score ≥90 fidelity. Warm runs `cp -R` instead of spawning a scaffolder and debugging a boot loop; the app shell arrives with proven fidelity rather than being re-rolled. Freshness check covers starter token files; drift is patched in the starter so every future run benefits.

**Supporting changes retained:**
- **Scoped fidelity re-score** — failed dimensions in detail, plus a *mandatory* holistic re-check and regression sweep. The holistic check is never scoped away; a fix can break a dimension that previously passed.
- **JSONL write verification** — `tail -1` after every append. A silently failed append leaves no record of the run and no signal that anything went wrong, so the write is confirmed rather than assumed.
- **`cold_start` and `promotions`** log/trace fields, supporting the two-file model.

**Reverted 2026-08-03 — pending separate evaluation.** Five changes were folded in as "supporting" without explicit approval and have been pulled back out at the user's direction, to be assessed individually:

| Reverted | Restored behavior |
|---|---|
| Risk-batched spec auditors | One dedicated auditor per spec, all parallel, each independent of its writer. Cross-spec consistency report removed. |
| Express / Full lane routing | No lanes. Every run uses the full decomposition path. `lane` removed from the JSONL schema; parser no longer emits a Complexity Assessment. |
| Model tiering | No tier guidance anywhere. Subagent type (`Explore` vs. `general-purpose`) is still specified — that is a capability requirement, not a cost optimization. |
| Screenshot caching | Browser researcher navigates and screenshots to `.pipeline/screenshots/` per run. No shared cache, no TTL, no 3-page cap, no image-age reporting. |
| Narrowed trace author | Full v4.2 trace schema restored: `context_sources`, `decisions`, `per_stage_summary`, `tool_calls`, `input_summary`, `output_summary`, `observations`, plus the new `discrepancies`. `observability/README.md` legacy markings reverted. |

Two of the original cold-start clauses went with these reverts, since the mechanisms they constrained no longer exist: "full model tier for cold extractors/scaffolder" (tiering removed) and "express lane forbidden on cold start" (lanes removed). The substantive cold-start clauses — recon pass, starter promotion gate, prerequisite verification — are unaffected.

**Defects found by `/audit` and fixed (2026-08-03):**

| Defect | Impact | Fix |
|---|---|---|
| `Explore` subagents instructed to write files (Stage 1A extractors, Stage 1B code researcher) | **Would break every run.** `Explore` has no Write/Edit tool, so the file silently never appears and the next stage finds no input. Introduced *by* the optimization — extractors previously returned findings inline. | Both switched to `general-purpose`. New hard constraint + failure-mode row. Recon pass and freshness check stay `Explore` and now explicitly return findings for the orchestrator to write. |
| PATH dispatches missing the mandatory proof-of-read (Stage 4 integrator + fidelity reviewer, Stage 1B brief synthesizer) | Violated v5.0's own hard constraint, in the files where token compliance matters most — the exact guard that makes path-ification safe | Proof-of-read added to all three |
| Live app-wide file lacks `## Common Mistakes To Avoid` and `## Promotion Log` | Promotion protocol and paste-sections target sections that don't exist; first run fails or silently no-ops | New **Step 1B.0 schema migration check**, run before any Stage 1B dispatch. Patches structure only, never content. |
| Eval allowlist keyed on the `design-brief.md` filename | `fulfillment-queues-v3` and `-v4` already have files by that name with a different schema — they'd be misrouted into the v5.0 union path | Detection now keys on the source-of-truth pointer line, not the filename |
| Backward-compat fallback assumed pre-v5.0 files are self-contained | `package-weight-capture-solution-a/design-system.md` is a 117-line pointer with no token tables — evaluating it alone would make G1 flag every legitimate production color as invented | Fallback now tests for a color-token table and unions pointer files with the app-wide file. Empty allowlist fails loudly instead of passing silently. |
| Miscounts | "8 prototypes" (actual: 7) and "497–1,216 lines" (actual: 117–1,216), repeated across three files | Corrected |

**🧊 Cold-start clauses** (new-app support hardened):
- **Step 1A.0 recon pass** — maps where styling actually lives before extractors run. Extractor bundling is by file locality, which requires knowing the layout; assuming a `src/theme/` directory is a cold-start failure. A Tailwind + shadcn app has nothing in common with beyondRx's MUI theme dir.
- **Starter promotion gated on fidelity ≥90.**
- Step 0.2 verifies cold-start prerequisites. Code Explorer indexing is the common blocker.

**Portability fixes:**
- **"Common Mistakes To Avoid" is now generated per app** from that app's own evidence. It previously hardcoded beyondRx-specific advice ("Do NOT use MUI Typography variants", "Do NOT use Vite/React Router if production uses Next.js App Router") inside the synthesizer's output schema, unlabeled as example — actively misleading on a non-MUI or non-Next app, and implementers are instructed to read that section first. It now also accumulates: the fidelity reviewer returns `app_level_lessons` that get appended after each run.
- **Skill description generalized** — it named only beyondRx and Pharmacy Dashboard, which drives skill matching and could prevent the skill triggering for a new app.

**Not yet done (deferred from the same analysis):** extractor consolidation on warm re-extraction paths, and the remaining screenshot/image-token reductions. Both were lower value than the four above.

### 4.5 (2026-06-09) — Simplified QA-fix pattern

Removed trivial/structural classification and user gates from the orchestrator's fix handling. Pattern is now: QA subagent reports → orchestrator fixes ALL → orchestrator reports to user. Applied to both Step 4.3 (fidelity reviewer) and Step 4.5 (eval runner).

### 4.4 (2026-06-09) — Fidelity reviewer refactored to pure reporter

Stripped Edit tool access and "LIMITED CORRECTION AUTHORITY" from the fidelity reviewer subagent. Reviewer now returns `proposed_fixes[]` with exact old_string/new_string pairs. Orchestrator applies all fixes. Separation of concerns: auditor reports, orchestrator fixes.

### 4.3 (2026-06-02) — Evals + cross-pollination refinements

Added automatic eval runner (Step 4.5) with 7 code-based evals: no invented colors or fonts (G1), correct framework (G2), all states implemented (G3), spec audit verdicts (G4), no reinvented components (G5), data layer match (G6), all active evals scored (G7 — meta-eval cross-pollinated from feature-impact-sizing). Evidence threshold (originally G5) removed — already enforced by Stage 1A Auditor at Gate 1. Eval results feed into JSONL log (compact) and traces (full detail). Renumbered observability steps to 4.6–4.7.

Added fidelity reviewer correction authority (Step 4.3): the fidelity reviewer could apply targeted fixes within a defined correction scope. *Superseded by v4.4 — reviewer is now a pure reporter; orchestrator applies all fixes.*

Additional v4.3 changes:
- **Weighted anchor scoring rubric** — replaced vague "Score: 0-100" with 8-point weighted rubric (15/15/15/15/10/10/10/10), 3-level anchors (0/half/full), +/-5 holistic adjustment
- **Visual reference mandatory** — Stage 0 hard gate requires Chrome DevTools screenshots, user-provided screenshots, or Figma screenshots. Pipeline halts if none available. Stage 4.3 caps score at 75 if screenshots disappear mid-run
- **G1 expanded to include fonts** — "No invented colors" → "No invented colors or fonts" with font-family scanning in the allowlist check. Single bulletproof check replaces scattered implicit checks
- **Framework check consolidated** — G2 eval is the single authoritative framework check. Validator check 12 clarified to cover file organization only
- **Evals + observability moved before Gate 3** — Steps 4.5-4.7 now run before the user sees the prototype. If the user closes the session after Gate 3, all observability is already on disk
- **Evals capture pre-fix state** — eval results logged to traces reflect what originally happened, not the post-fix state. Orchestrator attempts fixes and reports both eval failures and corrections at Gate 3

### 4.2 (2026-06-01) — Full observability with independent trace authorship

Added Post-Pipeline Observability section (Steps 4.5–4.6, later renumbered to 4.6–4.7 in v4.3):
- **JSONL invocation log** — append-only, one entry per run. Skill-specific fields: `stages_completed`, `fidelity_score`, `fidelity_iterations`, `subagent_count`.
- **JSON traces** — per-run, authored by an independent audit subagent (orchestrator never writes traces). Includes `context_sources`, `decisions`, `per_stage_summary`, and `gate_evidence` for all 4 mandatory gates (scope, design system, specs, fidelity).
- **Mid-run failure handling** — JSONL stub on failure, trace subagent still runs to document partial artifacts.

Schema in `observability/README.md`. Independent authorship chosen because the orchestrator has cognitive momentum and would confirm its own gate compliance uncritically.

### 4.1 (2026-06-01) — Two-tier design system + feature-specific research

Split Stage 1 into two operations:
- **Stage 1A (app-wide, create once):** Full extraction pipeline runs on first prototype for an app, writes to `prototypes/_design-system/<app>/design-system.md`. Subsequent runs freshness-check and reuse — eliminates cross-run variance from re-extraction.
- **Stage 1B (feature-specific, every run):** Code researcher + browser researcher discover which existing pages/components are most relevant to the feature being built. Research auditor validates relevance, verifies new tokens (≥3 threshold), resolves conflicts between new findings and app-wide base (higher occurrence count wins). Merged into prototype's local design-system.md with "Feature-Specific Inspiration" section.

Downstream: spec writers reference inspiration sources; validators check inspiration alignment (new item 3, 12-point checklist); failure modes added for irrelevant inspiration and unresolved token conflicts. Fidelity threshold remains at 90.

### 4.0 (2026-06-01) — Architecture revert + targeted fixes

**What happened:** v3.1 (44 files, 265KB, 56 eval criteria, 12 subagent prompts) produced worse prototypes than v1 (1 file, 43KB) despite passing all binary evals. The `fulfillment-queues-v4` prototype had hallucinated header gradients, wrong font, wrong framework, sparser tokens, and simplified mock layer — all of which passed v3's criteria because the evals checked existence, not correctness.

**Root causes identified:**
1. **Context dilution** — 44 files meant each subagent saw ~1/12th of the context v1's agents saw
2. **Process > product** — tokens spent on eval compliance, observability, escalation handling instead of design judgment
3. **Binary evals can't capture holistic fidelity** — "is there a gradient?" ≠ "is it the right gradient?"

**Fix:** Reverted to v1's single-file architecture. Added 7 targeted improvements:
1. Chrome DevTools MCP for staging screenshots + visual comparison
2. Visual Identity section in design-system.md (3-sentence gestalt + 5 structural patterns)
3. Explicit font fallback guidance (Sofia Pro → Plus Jakarta Sans; later updated to Noto Sans, then IBM Plex Sans per production transition)
4. URL-param state simulation (?loading, ?error, ?empty)
5. Fidelity scoring (0-100) with iteration loop (max 2 passes, ≥90 threshold)
6. Explicit framework matching (prototype must use same framework as production)
7. "Never invent visual elements" as top-level hard constraint

### Prior versions (1.1–3.1)

Key milestones:
- **1.1** (2026-05-04): Original PRD-to-prototype. Added data layer, form library, TypeScript interface extraction.
- **2.0–2.5** (2026-05-21): Added requirements traceability, functional QA, architectural decomposition into 44 files.
- **3.0** (2026-05-26): Full redesign with runtime extraction, 12 subagent prompts, 49 eval criteria.
- **3.1** (2026-05-28): Added fidelity auditor, composition notes, design brief. 56 eval criteria total.

### Lesson learned

The v1→v3 trajectory was a classic over-engineering arc: each version added process to catch failures from the previous version, but the process itself became the bottleneck. Binary eval frameworks work for functional correctness but fail for visual fidelity, which is a continuous, holistic judgment.

The fix was not "better evals" — it was "less process, more context per agent, one holistic reviewer with iteration authority."
