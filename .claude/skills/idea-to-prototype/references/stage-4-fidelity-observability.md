# Stage 4 — Composition, Fidelity, Evals, Observability

Read `context-contract.md` first if you have not this run.

---

## Step 4.1: Integrator

Spawn one integrator (`general-purpose`):

```
You are composing the prototype into a runnable app.

Design brief: <paste FULL content of design-brief.md>
App Visual Identity: <paste that section from the app-wide design-system.md>
Traceability matrix (pages and component placement): <paste the Pages/Screens table>
Component implementations: <list file paths>

App-wide design system — READ BY PATH:
  prototypes/_design-system/<app>/design-system.md
Consult the Routes section for production route conventions and the Components table for
any base components you wire in directly.

PROOF OF READ — before wiring anything, quote from that file: the production route pattern
you are mirroring (with its citation), and the exact prop signature of one base component
you wire in directly. If you cannot find either, STOP and report which lookup failed.

Your job:
1. Wire components into pages per the traceability matrix.
2. Set up routing matching production conventions from the Routes section.
3. Wire mock data through the component tree.
4. Make interactions work: clicks, navigation, modals, filters, sorting.
5. Home page = the natural entry point implied by the idea source.
6. Verify the app shell (header, nav, layout wrapper) matches production structure exactly.

Do NOT add real API calls or auth. All data is mock.

Run `npm run dev` and confirm no errors. Report: pages built, user flows working, any gaps
or non-functional placeholders (be explicit about these — they go in the Gate 3 caveats).
```

## Step 4.2: Smoke test

Orchestrator, directly via Bash:

1. `npm install` (idempotent)
2. Start `npm run dev` in background; verify it serves
3. Capture the local dev URL
4. `npx tsc --noEmit` — fix any type errors
5. Stop the background server

---

## Step 4.3: Fidelity reviewer (pure reporter — no file edits)

Spawn one fidelity reviewer (`general-purpose`) — this is the single most important review in the pipeline:

```
You are the final visual fidelity reviewer. Your job: determine whether this prototype
looks like the real app — not just whether it uses the right tokens, but whether the
overall composition, hierarchy, and feel are correct.

You are a PURE REPORTER. You score, identify issues, and propose fixes. You do NOT edit
any file. The orchestrator applies fixes.

Design brief (inspiration sources): <paste FULL content of design-brief.md>
App Visual Identity + Common Mistakes: <paste both sections from app-wide design-system.md>
Screenshots: <paths in .pipeline/screenshots/>
Component implementations: <list paths>
Prototype dev URL: <url>

App-wide design system — READ BY PATH for token verification:
  prototypes/_design-system/<app>/design-system.md

PROOF OF READ — before scoring token compliance (audit point 3), quote the exact value +
citation for two tokens the implementation uses. If a value in the code does not appear in
either the app-wide file or the brief, that is an automatic 0 on audit point 3.

**Screenshot requirement:** at least one visual reference MUST exist in
.pipeline/screenshots/. If none exists, cap your score at 75 and flag: "No visual
reference available for comparison — score capped at 75."

If Chrome DevTools MCP is available:
1. Navigate to the prototype dev URL; screenshot each page
2. Navigate to the staging equivalents; screenshot them
3. Compare directly

## Scoring Rubric (weighted anchors)

| # | Audit Point | Weight | 0 (Fail) | Half | Full |
|---|---|---|---|---|---|
| 1 | **Holistic feel** | 15 | Looks generic/foreign | Recognizable but something is off | Belongs in the app naturally |
| 2 | **App shell** | 15 | Missing or wrong (header, logo, nav, env badge) | Present, minor errors | Exact match |
| 3 | **Token compliance** | 15 | Invented values found | All valid, minor misuse (right color, wrong context) | Every value cited to the allowlist |
| 4 | **Composition/layout** | 15 | Different arrangement from production | Same structure, proportions off | Matches production arrangement |
| 5 | **Typography** | 10 | Wrong fonts or scale not used | Right font, wrong application mechanism | Scale applied correctly |
| 6 | **Data display** | 10 | Tables/grids visually wrong | Structure right, details off | Row height, padding, headers match |
| 7 | **Interactive states** | 10 | Missing hover/focus/active | Some present | All present and matching |
| 8 | **Missing elements** | 10 | Major elements absent | Minor elements absent | Nothing missing |

**Holistic adjustment:** after summing, apply +/-5 with a mandatory one-sentence
justification. This is the "forest" check — a prototype can score well per-item and still
feel wrong composed.

**Total:** weighted sum + adjustment, capped at 100.

## Workflow
1. Score each of the 8 points (0, half, or full)
2. Apply the holistic adjustment with justification
3. Write the full breakdown table to: prototypes/<feature>/.pipeline/reviews/_fidelity-review.md
4. For EVERY issue, return a proposed_fixes[] entry with exact old_string/new_string when
   possible, or a description when a text swap is insufficient
5. Identify any issue that represents a REPEATABLE app-level trap — something a future
   prototype for this app would likely also get wrong. Flag these separately; they get
   appended to the app-wide "Common Mistakes To Avoid" section.
6. Do NOT use Edit. Do NOT modify prototype files.

Return format:

**Fidelity: [score]/100 | Proposed fixes: [N]**

proposed_fixes:
- { "file": "src/header.tsx", "line": 12, "issue": "Wrong header gradient hex", "old_string": "#E8D5C4", "new_string": "#F0D9C8" }
- { "file": "src/components/layout.tsx", "issue": "Sidebar should wrap content, not sit adjacent", "description": "Move <Sidebar> to be a parent of <ContentArea>" }

app_level_lessons:
- "Do NOT <mistake> — <the app's actual convention> (<citation>)"
```

**After the reviewer returns**, the orchestrator:

1. **Applies all proposed fixes** via targeted Edit calls. No classification, no user gate.
2. **Appends any `app_level_lessons`** to the app-wide design system's "Common Mistakes To Avoid" section, tagged with the source feature and date. This is how the app-wide file gets smarter each run.
3. **Reports** the score, breakdown, and what was fixed.
4. Proceeds to Step 4.4 if any fix was applied.

---

## Step 4.4: Fidelity confirmation (scoped re-score)

If fixes were applied, spawn a **fresh** reviewer (different invocation — preserves adversarial independence). Scope its work, but never scope away the holistic check:

```
You are re-scoring a prototype after fixes. You did not perform the original review.

Original review: <paste .pipeline/reviews/_fidelity-review.md scoring table + the issue list>
Fixes applied: <list the edits made>
[Plus the same brief / Visual Identity / screenshots / dev URL inputs as the original review]

Take fresh screenshots. Then:

1. **Re-score in full detail** ONLY these dimensions: <list the dimensions that scored
   below full in the original review>.
2. **Re-score item 1 (Holistic feel) and the +/-5 holistic adjustment ALWAYS**, against
   your fresh screenshots. This is mandatory and not optional — it is the check that
   catches a fix breaking composition.
3. **Regression sweep** on the dimensions that previously scored full: you do not need to
   re-derive them in detail, but confirm from your fresh screenshots that none regressed.
   If one did, re-score it in full and say so.

Carry forward unchanged scores for dimensions that were full and did not regress.

Return the same format as the original review, plus a line:
**Regressions detected: [none | list]**
```

Max 2 total passes (original + 1 confirmation). If still below 90, present to the user with the score and the remaining gaps.

---

## Step 4.5: Run evals (before the user sees the prototype)

1. **Read** `.claude/skills/idea-to-prototype/evals.md` for active evals and their check definitions.
2. **Execute** each check via Bash/grep against prototype artifacts. Note that the allowlist for G1/G2/G5/G6 is the **union** of the app-wide `design-system.md` and the prototype's `design-brief.md` — see the eval definitions.
3. **Record pre-fix results.** These are what the trace captures.
4. **Attempt targeted fixes** on failures:
   - G1 (invented color/font) → replace with the nearest allowlist value
   - G2 (wrong framework) → escalate; structural, too risky to auto-fix
   - G3 (missing state) → add the URL-param handling
   - G4 (spec audit FAIL) → escalate; gate violation
   - G5 (reinvented component) → replace with the allowlist import
   - G6 (raw useState for server data) → refactor to the app's query pattern
   - G7 (meta-eval) → find the unscored eval and run it
5. **Update** `Last Result` in `evals.md` with the **pre-fix** result.
6. **Pass pre-fix results forward** to Steps 4.6–4.7:
   - Invocation log: compact — `[{"id":"G1","r":"P"},{"id":"G2","r":"F"}]`
   - Trace: full — `[{"eval_id":"G1","name":"...","result":"Pass","detail":null}]`
   - Evals do not re-run after fixes. The trace records what originally happened; fixes are reported at Gate 3.
7. **Root-cause any failure** as a **specification** issue (tighten a subagent prompt), a **generalization** issue (recurring across runs — check `invocation-log.jsonl`), or an **architectural** issue (pipeline gap). Surface at Gate 3.

Skip silently if `evals.md` has no active evals.

---

## Step 4.6: Log the invocation

**Schema:** `observability/README.md`.

Append one line to `.claude/skills/idea-to-prototype/observability/invocation-log.jsonl`:

```json
{"ts":"<ISO 8601>","skill":"idea-to-prototype","version":"5.1","input_summary":"<feature-slug> for <app> from <input-type>","duration_s":<approx>,"stages_completed":<0-5>,"fidelity_score":<N|null>,"fidelity_iterations":<N>,"subagent_count":<N>,"cold_start":<true|false>,"promotions":<N>,"outcome":"<success|partial|failure>","notes":"","eval_results":[]}
```

**Then verify the write landed:** `tail -1` the file and confirm your entry is present. A silently failed append leaves no record of the run and no signal that anything went wrong. If the tail does not show your entry, report it at Gate 3 as a skill defect rather than moving on.

| Field | Required | Notes |
|---|---|---|
| `ts` | Yes | Run start, ISO 8601 |
| `skill` | Yes | `"idea-to-prototype"` |
| `version` | Yes | From SKILL.md iteration notes |
| `input_summary` | Yes | Feature slug, app, input types |
| `duration_s` | No | Intake → Gate 3 |
| `stages_completed` | Yes | Highest fully completed, 0–5 |
| `fidelity_score` | Yes | Final; `null` if Stage 4 not reached |
| `fidelity_iterations` | No | Review passes |
| `subagent_count` | No | Total Agent invocations |
| `cold_start` | No | `true` if this run created the app-wide design system |
| `promotions` | No | Count promoted into the app-wide file at Gate 1 |
| `outcome` | Yes | `success` / `partial` / `failure` |
| `notes` | No | SSO issues, retries, overrides |
| `eval_results` | No | Compact form |

**Outcome rules:** `success` = running prototype, fidelity ≥90 (or user accepted lower), all gates passed. `partial` = prototype exists but fidelity <90 unaccepted, or user stopped early. `failure` = no running prototype.

---

## Step 4.7: Independent trace authorship

Spawn an independent subagent with **`model: claude-5-5-sonnet`** to author the trace by inspecting artifacts on disk. The orchestrator NEVER writes the trace — only the subagent does. Independent authorship exists because the orchestrator has cognitive momentum from running the pipeline and would confirm its own gate compliance uncritically.

Tiering is safe here because the work is structured inspection against a fixed schema plus a JSONL cross-check — every finding is checkable against disk. Do NOT narrow this agent's *scope* to save cost; the full trace has caught real errors in the orchestrator's self-report, including a wrong `duration_s` and a wrong timezone offset on a prior run.

```
You are an independent auditor for an idea-to-prototype run. You did NOT execute this
skill — you are inspecting evidence on disk after the fact. Your job: examine artifacts,
verify gate compliance, and author the trace file.

## Artifacts to Examine
1. Prototype directory: prototypes/<feature>/
2. Design brief: prototypes/<feature>/design-brief.md
3. App-wide source of truth: prototypes/_design-system/<app>/design-system.md
4. Specs: prototypes/<feature>/tasks/*.md
5. Traceability matrix: prototypes/<feature>/tasks/_traceability.md
6. Review reports: prototypes/<feature>/.pipeline/reviews/
7. Fidelity report: prototypes/<feature>/.pipeline/reviews/_fidelity-review.md
8. Screenshots: prototypes/<feature>/.pipeline/screenshots/
9. Research findings: prototypes/<feature>/.pipeline/research/
10. Invocation log (last entry): .claude/skills/idea-to-prototype/observability/invocation-log.jsonl

## Context Sources Audit

Reconstruct which files and external resources were used as context during this run. For
each, record `type`, `path`/`id`/`url`, and `purpose`.

Source types:
- `local` — files in .pipeline/inputs/, design-brief.md, the app-wide design-system.md,
  specs, review reports
- `code_explorer` — the indexed production repo (infer from the app-wide Tech Stack or the
  JSONL notes)
- `staging_url` — staging pages accessed via Chrome DevTools (check .pipeline/screenshots/
  for evidence of which URLs were visited)
- `figma` — Figma files (check the brief or app-wide file for Figma node references)

**Verification:** for each `local` source, confirm the file actually exists on disk. Flag
any missing paths in `observations`.

## Decisions Audit

Identify key decisions that shaped the output beyond default pipeline behavior. Evidence:
- App-wide design-system.md header/notes (reuse vs. full extraction, font substitution)
- Promotion Log rows (what was promoted this run, and any prior value it replaced)
- .pipeline/reviews/ (retry evidence — multiple audit versions for the same spec)
- Fidelity report (iteration notes, score progression)
- JSONL `notes` field (tool unavailability, user overrides)
- Missing artifacts that would normally be present (no screenshots = Chrome DevTools
  unavailable; no starter = cold-start run)

For each decision: record a short `decision` slug, `rationale`, and `phase` (stage number).

## Gate checks

### Gate 0 — Scope confirmed
- .pipeline/inputs/ exists and holds >=1 file
- Record: input count, file types

### Gate 1 — Design system approved
- design-brief.md exists in the prototype dir
- It contains a "Feature-Specific Inspiration" section (proves Stage 1B ran)
- The app-wide design-system.md exists and contains evidence-threshold annotations
  (search for 'Established', 'Probable', 'Single')
- Record: brief line count, whether the brief duplicates app-wide token tables (grep for
  "## Color Tokens" in the brief — its PRESENCE is a defect under the two-file model,
  report it), promotion-log row count

### Gate 2 — All specs pass
- Count spec files in tasks/ excluding _traceability.md
- Count *-spec-audit*.md files in .pipeline/reviews/
- For each spec, find its LATEST audit (a -v2 supersedes the original) and read the verdict
- Check _cross-spec-audit.md (latest version) exists and read its verdict — Gate 2 requires
  this in addition to the per-spec verdicts
- Check whether _traceability.md has a "## Contract Authority" section and record which spec
  it names
- Record: spec count, audit count, latest-verdict-per-spec, cross-spec verdict, contract
  authority, any FAIL (quote it)

### Gate 3 — Fidelity reviewed
- _fidelity-review.md exists and contains a numeric score
- .pipeline/screenshots/ holds >=1 file
- Record: score, iteration count, screenshot count

## Write the Trace File

Create .claude/skills/idea-to-prototype/observability/traces/YYYY-MM-DD_HHMM_<feature-slug>.json

The trace MUST include ALL of these fields (schema: observability/README.md):
- `ts`, `skill`, `version`, `duration_s`, `outcome` — copy from the JSONL last entry, then
  cross-check against artifact evidence
- `input_summary` — 2-3 sentences: feature, target app, inputs provided, scope
- `context_sources` — array of {type, path/id/url, purpose} from the Context Sources Audit.
  Verify local paths exist
- `output_summary` — 2-3 sentences: what was produced, component count, page count,
  fidelity score, push status
- `decisions` — array of {decision, rationale, phase} from the Decisions Audit. Empty array
  if the pipeline ran on pure defaults
- `stages_completed` — integer 0-5
- `fidelity_score` — integer or null
- `fidelity_iterations` — integer
- `cold_start` — boolean: did this run create the app-wide design system?
- `promotions` — integer: findings promoted into the app-wide file at Gate 1
- `per_stage_summary` — object with keys stage_0 through stage_5, each having `status`
  (complete/skipped/failed/not_reached) and `notes`
- `tool_calls` — array of notable invocations: {tool, target, purpose, ok}. Include
  `purpose` on every entry
- `gate_evidence` — object with keys gate_0_scope, gate_1_design_system, gate_2_specs,
  gate_3_fidelity. Each has `evidence_found` (boolean), `detail` (string), and the
  gate-specific structured fields per observability/README.md
- `eval_results` — array (empty if no evals configured)
- `discrepancies` — array of strings: every place the JSONL disagrees with disk, plus any
  missing expected artifact. Empty array if clean
- `observations` — your independent assessment: surprises, gaps, concerns, what the
  artifacts reveal about the run. Include missing context-source paths and JSONL
  discrepancies here too
- `independently_authored` — always `true`

Rules:
- Base ALL findings on what you observe in the files — not on what the JSONL claims
- If an artifact is missing, record that fact; do not infer what it would have contained
- If gate evidence is ambiguous, set evidence_found: false and explain why in detail
- Verify local context_sources paths exist on disk — flag any that don't
- Cross-check the JSONL's outcome and stages_completed against what you observe. If they
  disagree, flag the specific discrepancy
- For incomplete runs: record what artifacts DO exist. `not_reached` stages have empty
  notes. Partial gate evidence is valuable
- You MUST NOT modify any file except the trace you are creating

Report back: "Trace authored. Context sources: [N]. Decisions: [N]. Gate evidence: [N/4]
gates confirmed. Discrepancies: [N]. [Any concerns.]"
```

**After it returns:**

- All gates confirmed, no discrepancies → proceed
- Discrepancies → surface to the user: "The trace auditor found [detail]. Want me to correct the log entry?"
- `evidence_found: false` on a stage that should have completed → investigate before Stage 5
- Brief contains duplicated app-wide token tables → that is a Stage 1B defect; note it and fix the synthesizer prompt

---

## Mid-run failure handling

If the pipeline fails before Step 4.5:

1. Write a minimal JSONL failure stub:
   ```json
   {"ts":"...","skill":"idea-to-prototype","version":"5.1","input_summary":"<feature-slug> for <app>","stages_completed":<last completed>,"fidelity_score":null,"outcome":"failure","notes":"Failed at Stage N: <reason>"}
   ```
   Then `tail -1` to confirm it landed.
2. Still run Step 4.7. Partial gate evidence beats no record. If the prototype directory does not exist at all, the auditor records that and sets all gates to `evidence_found: false`.
