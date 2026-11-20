# Worked Examples

Two walkthroughs: a warm run (established app) and a cold start (new app). They show what the orchestrator actually does at each stage.

---

## Example 1 — Warm run: `fulfillment-queues` for beyondRx

App-wide design system and starter both already exist. This is the common case.

**Intake (Stage 0)**
- Idea: one-pager describing fulfillment queue views
- Repo: `pharmacy-management-ui`, indexed in Code Explorer
- Staging: beyondRx with SSO
- Slug: `fulfillment-queues`
- Orchestrator reads `references/context-contract.md`, confirms `_design-system/beyondrx/design-system.md` exists → **warm path**

**Stage 1A — freshness check only**
- One `Explore` subagent spot-checks 10 claims (framework version, page background, base font, table row height, button radius, data library version) plus the starter's token files. It returns its table; the orchestrator does any writing.
- All MATCH → reuse as-is. Gate 1A does not fire.
- Cost: 1 subagent instead of recon + 4 extractors + auditor + synthesizer

**Stage 1B — schema migration, then feature research**
- **Step 1B.0:** the app-wide file has no `## Promotion Log` and only a lowercase `Common mistakes to avoid:` prose line. Orchestrator promotes that line to a proper H2 (bullets preserved verbatim), appends an empty Promotion Log table, and adds `Schema version: 1`. Reported at Gate 1.
- Code researcher (`general-purpose`, because it writes) finds `/queue_dashboard` (Pharmacy Queues) is the closest existing page — same table-with-kebab-menu pattern, same tab structure, same Total row. Also finds the Pack Queue DataGrid pattern and the Problem Solve banner. Writes `.pipeline/research/_code-research.md`.
- Browser researcher screenshots the three relevant staging pages to `.pipeline/screenshots/`.
- Research auditor ranks sources, then makes promotion decisions:
  - `palette.shipment.green` — Established (4 occurrences), a token any feature could use → **PROMOTE**
  - `data-grid-styles.ts` — Established (17 importing files) → **PROMOTE**
  - Fulfillment-queue-specific column set → **BRIEF-ONLY** (feature domain)
  - `clickableRowStyles` — Probable (2, both unexported local) → **BRIEF-ONLY, below threshold**
- Synthesizer writes `design-brief.md` at **94 lines** — inspiration, build-it-like-this, feature routes, brief-only patterns. No token tables. (Under the old model this file was 497 lines, most of it a copy.)

**Gate 1** — user reviews the ranked sources, the schema migration, and approves 2 promotions. Orchestrator edits the app-wide file: inserts both patterns tagged `[Promoted from fulfillment-queues, 2026-08-03]`, appends 2 Promotion Log rows, bumps the freshness date. The next prototype for beyondRx inherits both.

**Stage 2 — decomposition**
- Parser: 8 components across 5 pages. Designates `08-mock-data-and-hooks.md` as **contract authority**, owning 6 cross-cutting items (the shipment row interface, `shipmentId: string`, the queue hook signature, and three shared props).
- 8 spec writers in parallel. The authority defines its 6 items explicitly; the other 7 reference them by name and are forbidden from restating them.
- Auditors dispatched in one message: dedicated for the contract authority and the 4 complex specs, one batched auditor for the 3 stubs/fixtures, plus **one cross-spec auditor** reading all 8.
- Cross-spec auditor finds `shipmentId` typed `string` in spec 02 and `number` in spec 04 — a contract violation the per-spec auditors each passed. Resolved in favour of the authority's `string`.
- 2 specs FAIL their own audits → revised → `-v2` audits PASS. Cross-spec re-run: PASS.

**Gate 2** — user answers 3 questions. All latest verdicts PASS.

**Stage 3 — implementation**
- Scaffold: `cp -R _design-system/beyondrx/starter/ prototypes/fulfillment-queues/`, `npm install`, boot confirmed, tsc clean. **No scaffolder subagent, no boot-debug loop.** Theme files, MSW setup, and the app shell arrive pre-validated.
- 8 implementer/validator pairs in parallel. Each implementer gets: spec (pasted), brief (pasted, 94 lines), Visual Identity + Common Mistakes (pasted, ~30 lines), the **contract-authority definitions** (pasted — its spec only names them), and the app-wide path with a proof-of-read requirement.
- One implementer's proof-of-read block reveals it could not find a hover color → stops and flags instead of inventing one. Orchestrator surfaces it as a Gate 1 gap; user approves adding it. This is the failure mode the proof-of-read exists to catch.
- 1 component FAILs validation (used an unapproved hex in a gradient) → retry → PASS

**Stage 4**
- Integrator wires pages and routing
- Smoke: dev server at localhost:3000, `tsc --noEmit` clean
- Fidelity reviewer: **72/100** — header gradient wrong, table cell padding off, env chip missing. Returns 3 `proposed_fixes[]` and one `app_level_lessons` entry: "Do NOT approximate the header gradient — it is a two-stop linear-gradient defined in `header-gradient-border-style.ts:8`, not a flat fill."
- Orchestrator applies all 3 fixes and appends the lesson to the app-wide **Common Mistakes To Avoid** (which now exists, thanks to Step 1B.0)
- Scoped re-score: dimensions 2, 4, 6 in full detail + mandatory holistic re-check + regression sweep → **93/100**, no regressions
- Evals: 7/7 pass (pre-fix). JSONL appended, `tail -1` confirms it landed.
- Trace: independent auditor authors the full trace — context sources, decisions, per-stage summary, gate evidence → 4/4 gates confirmed, 0 discrepancies

**Gate 3** — 93/100, 7/7 evals, 4 auto-fixes reported, 2 promotions and 1 schema migration noted, 1 allowlist gap surfaced.

**Stage 5** — user says "push it" → `prototype/fulfillment-queues` branch.

---

## Example 2 — 🧊 Cold start: first prototype for a new app

Nothing exists for this app. Every cold-start clause fires.

**Stage 0 — intake and prerequisite verification**
- Confirm the new repo is **indexed in Code Explorer** (`get_stats`). If it is not, stop — the entire evidence model depends on it. This is the most common cold-start blocker.
- Confirm a visual reference exists: staging URL + SSO, user screenshots, or Figma. None of the three → halt.
- No `_design-system/<new-app>/` → **cold-start path confirmed**. Announce it: the run will be longer and Gate 1A will fire.

**Stage 1A — full extraction (`references/stage-1a-cold-start.md`)**
- **Recon pass first.** One `Explore` agent maps where styling lives; the orchestrator writes its findings to `.extraction/_recon.md`. Result: Tailwind + shadcn/ui, tokens in `tailwind.config.ts` and `src/styles/tokens.css`, no theme directory. **Nothing like beyondRx** — had the orchestrator assumed `src/theme/*`, the extractors would have found nothing.
- 4 extractors dispatched as `general-purpose` (they write to `.extraction/`), bundled by the *actual* file locations recon found.
- Auditor reads the bundles by path, applies the ≥3 threshold, spot-verifies its 5 highest-impact claims, flags that two competing button implementations exist (a migration in flight).
- Synthesizer writes the app-wide `design-system.md`, including an empty `## Promotion Log` and a `Schema version: 1` line — so no migration is needed on later runs. Its **Common Mistakes To Avoid** is **generated from this app's own evidence** — e.g. "Do NOT use the legacy `Button` in `src/components/ui/button-old.tsx` — the current convention is the shadcn `Button` (`src/components/ui/button.tsx:12`, 41 importing files)." No MUI or Next.js App Router advice appears, because none applies here.

**Gate 1A fires** — user resolves the Probable patterns, picks a winner for the button migration, and confirms the generated mistakes list matches their understanding.

**Stage 1B** — Step 1B.0 finds the schema already current (the cold synthesizer wrote it), so no migration. Research proceeds normally.

**Stage 3 — cold scaffold**
- No starter → full scaffolder subagent. Builds Vite + React Router (per this app's recon, not beyondRx's Next.js), Tailwind config with verbatim token values, shadcn components, the app shell, and the URL-param utility.
- Implementer/validator pairs run as normal.

**Stage 4** — as the warm example. Fidelity lands at 91 after one fix pass.

**After Gate 3 — starter promotion**
- Fidelity 91 ≥ 90 and no starter exists → promote
- Copy framework config, package.json + lockfile, token files, font loading, mock-API setup, app shell, state utility into `_design-system/<new-app>/starter/`. Exclude all feature code, `tasks/`, `.pipeline/`, `design-brief.md`.
- Verify in isolation: copy to temp, `npm install && npm run dev`, `tsc --noEmit` — boots clean with no feature code
- Write `STARTER.md`: source feature, date, fidelity 91 at promotion, schema version, contents
- Report at Gate 3: "Starter template created for `<new-app>` — future prototypes skip the scaffold stage."

**Net:** the cold run costs roughly what a full run cost before. Every subsequent prototype for that app is materially cheaper, and the app-wide file plus the starter keep improving as promotions and fidelity lessons accumulate.
