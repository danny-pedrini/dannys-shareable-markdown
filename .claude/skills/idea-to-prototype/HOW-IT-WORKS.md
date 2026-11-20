# idea-to-prototype — How It Works

**Version 5.1.** Two things to understand before reading the flow:

**1. The design system is a durable, growing asset — not a per-run artifact.**

```
prototypes/_design-system/<app>/          ← SINGLE SOURCE OF TRUTH, grows every run
├── design-system.md                        all tokens, components, types, data layer
└── starter/                                validated runnable scaffold (≥90 fidelity)

prototypes/<feature>/
└── design-brief.md                       ← ~60-150 lines, FEATURE-LOCAL ONLY
                                            (no token tables — those live app-wide)

ALLOWLIST = design-system.md ∪ design-brief.md
```

Established feature discoveries are **promoted** into the app-wide file at Gate 1, so each run makes the next one cheaper and better.

**2. Context contract: paste framing, path lookups, always prove the read.**

| | Delivery | Examples |
|---|---|---|
| **Framing** — reasoned *from* | Pasted in full | The spec, the brief, Visual Identity, Tech Stack, Common Mistakes, review reports |
| **Lookup** — values looked *up* in | Path + **proof-of-read** | Token tables, typography/spacing scales, component inventory, type interfaces |

Subagent prompt templates live in `references/`, loaded per stage. This is deliberately conservative: v3.1 diluted subagent context across 44 files and produced *worse* prototypes. The proof-of-read requirement (quote specific values + citations before producing the deliverable) is the guard that keeps path-ification from repeating that.

```
                        ┌─────────────────────────────────────────┐
                        │              USER  INPUTS               │
                        │                                         │
                        │  Idea source (required)                 │
                        │  Feature name (required)                │
                        │  Repo name, Figma URL, screenshots,     │
                        │  GitHub repo URL (all optional)         │
                        └────────────────────┬────────────────────┘
                                             │
                                             ▼
╔═══════════════════════════════════════════════════════════════════════════╗
║  STAGE 0 — INTAKE                                                       ║
║                                                                         ║
║  FIRST ACTION: read references/context-contract.md                      ║
║                                                                         ║
║  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────────┐   ║
║  │ Gather inputs │→ │ COLD OR WARM?    │→ │ Bootstrap SSO +          │   ║
║  │ (batched ask) │  │ _design-system/  │  │ Visual reference gate    │   ║
║  └──────────────┘  │ <app>/ exists?   │  │ (MANDATORY — at least    │   ║
║                     │                  │  │ one of: DevTools shots,  │   ║
║                     │ 🧊 NO → verify:  │  │ user screenshots, or     │   ║
║                     │  • repo indexed  │  │ Figma. Halt if none.)   │   ║
║                     │    (get_stats)   │  └────────────┬─────────────┘   ║
║                     │  • visual ref    │               ▼                 ║
║                     │    obtainable    │  ┌──────────────────────────┐   ║
║                     │  Announce longer │  │ Scaffold workspace       │   ║
║                     │  run + Gate 1A   │  │ prototypes/<feature>/    │   ║
║                     └──────────────────┘  │  ├── .pipeline/          │   ║
║                                           │  ├── design-brief.md     │   ║
║                                           │  ├── tasks/              │   ║
║                                           │  └── README.md           │   ║
║                                           └──────────────────────────┘   ║
╚═══════════════════════════════════════════════╤═══════════════════════════╝
                                                │
                                     ┌──────────▼──────────┐
                                     │   GATE 0            │
                                     │   User confirms     │
                                     │   scope & inputs    │
                                     └──────────┬──────────┘
                                                │
╔═══════════════════════════════════════════════▼═══════════════════════════╗
║  STAGE 1A — APP-WIDE DESIGN SYSTEM (create once, reuse)                 ║
║                                                                         ║
║  ┌────────────────────────────────────────────────────────────┐         ║
║  │ prototypes/_design-system/<app>/design-system.md exists?   │         ║
║  └──────┬─────────────────────────────────────────┬───────────┘         ║
║     YES │                                    NO   │                     ║
║         ▼                                         ▼                     ║
║  ┌──────────────────┐              ┌──────────────────────────────────┐ ║
║  │ WARM PATH        │              │ 🧊 COLD START (new app)          │ ║
║  │ Freshness check: │              │ references/stage-1a-cold-start.md│ ║
║  │ 1 Explore agent  │              │                                  │ ║
║  │ spot-checks      │              │ Step 1A.0 RECON PASS (first!)    │ ║
║  │ 8-12 claims +    │              │ Explore agent — returns its map; │ ║
║  │ starter tokens   │              │ orchestrator writes it to disk   │ ║
║  │                  │              │ ┌──────────────────────────────┐ │ ║
║  │                  │              │ │ Where does styling LIVE?     │ │ ║
║  │ All MATCH→reuse  │              │ │ MUI theme dir? Tailwind cfg? │ │ ║
║  │ DIVERGED→ask     │              │ │ CSS modules? tokens pkg?     │ │ ║
║  │  user: patch or  │              │ │ NEVER assume a known app's   │ │ ║
║  │  re-extract      │              │ │ layout                       │ │ ║
║  │ (patch usually)  │              │ └──────────────┬───────────────┘ │ ║
║  │                  │              │                ▼                 │ ║
║  │ Gate 1A does     │              │ 4 EXTRACTORS, bundled by FILE    │ ║
║  │ NOT fire         │              │ LOCALITY (not by concept)        │ ║
║  └──────────────────┘              │ ┌─────┐┌─────┐┌─────┐┌────────┐ │ ║
║                                    │ │Token││Off- ││Comp││Data/   │ │ ║
║                                    │ │files││token││+   ││forms/  │ │ ║
║                                    │ │(all ││sweep││styl││types   │ │ ║
║                                    │ │ 5)  ││+cnt ││objs││        │ │ ║
║                                    │ └──┬──┘└──┬──┘└─┬──┘└───┬────┘ │ ║
║                                    │    └──────┴─────┴───────┘      │ ║
║                                    │         ▼  (write to disk)      │ ║
║                                    │  Auditor (>=3, spot-verifies 5) │ ║
║                                    │         ▼                        │ ║
║                                    │  Synthesizer                     │ ║
║                                    │  • "Common Mistakes To Avoid"    │ ║
║                                    │    GENERATED from THIS app's     │ ║
║                                    │    evidence (portability fix)    │ ║
║                                    │         ▼                        │ ║
║                                    │  🛑 Gate 1A: user review         │ ║
║                                    └──────────────────────────────────┘ ║
║                                                                         ║
║  Shared file: Tech Stack, Visual Identity, Common Mistakes, Font        ║
║  Handling, Color Tokens, Typography, Spacing, Style Objects,            ║
║  Components, Data Layer, Forms, Type Interfaces, Routes, Promotion Log  ║
╚═══════════════════════════════════════════════╤═══════════════════════════╝
                                                │
╔═══════════════════════════════════════════════▼═══════════════════════════╗
║  STAGE 1B — FEATURE-SPECIFIC RESEARCH (every run)                       ║
║                                                                         ║
║  Step 1B.0 SCHEMA MIGRATION CHECK (first, every run)                    ║
║  ┌──────────────────────────────────────────────────────────────────┐   ║
║  │ Pre-v5.0 app-wide files lack sections v5.0 writes to. Patch:     │   ║
║  │  • ## Common Mistakes To Avoid (promote lowercase prose line)    │   ║
║  │  • ## Promotion Log            (create empty table)              │   ║
║  │  • Schema version / freshness  (add if absent)                   │   ║
║  │ Preserve every existing value verbatim. Report at Gate 1.        │   ║
║  └──────────────────────────────────────────────────────────────────┘   ║
║                                                                         ║
║  ┌────────────────────────┐    ┌─────────────────────────────┐          ║
║  │  CODE RESEARCHER       │    │  BROWSER RESEARCHER         │          ║
║  │  (general-purpose —    │    │  (Chrome DevTools)          │          ║
║  │   it WRITES to disk;   │    │  Navigate staging,          │          ║
║  │   Explore cannot)      │    │  screenshot similar pages   │          ║
║  │  "Which existing pages │    │  → .pipeline/screenshots/   │          ║
║  │  & components match?"  │    │                             │          ║
║  │  Reports OCCURRENCE    │    │                             │          ║
║  │  COUNTS — these drive  │    │                             │          ║
║  │  promotion eligibility │    │                             │          ║
║  └───────────┬────────────┘    └──────────────┬──────────────┘          ║
║              └────────────────┬────────────────┘                        ║
║                               ▼                                         ║
║  RESEARCH AUDITOR — classifies every finding:                           ║
║  ┌─────────────────────────────────────────────────────────────────┐   ║
║  │ PROMOTE     │ Established (>=3) + not feature-specific           │   ║
║  │             │ → app-wide design-system.md (citation re-verified) │   ║
║  │ BRIEF-ONLY  │ Established but feature-domain-specific            │   ║
║  │ BRIEF-ONLY  │ Probable (2) or Single (1) — below threshold       │   ║
║  │ REJECT      │ Citation missing/vague/unverifiable                │   ║
║  └─────────────────────────────────────────────────────────────────┘   ║
║                               ▼                                         ║
║  BRIEF SYNTHESIZER → prototypes/<feature>/design-brief.md               ║
║  (~60-150 lines. NO token tables — that duplication is what v5.0        ║
║   removed. Points at the app-wide file as source of truth.)             ║
╚═══════════════════════════════════════════════╤═══════════════════════════╝
                                                │
                                     ┌──────────▼──────────────────┐
                                     │   GATE 1                    │
                                     │   User reviews brief +      │
                                     │   ranked inspiration +      │
                                     │   APPROVES PROMOTIONS       │
                                     │   (they persist beyond      │
                                     │    this prototype)          │
                                     │            ▼                │
                                     │   Orchestrator edits        │
                                     │   app-wide file: tagged     │
                                     │   inserts + Promotion Log   │
                                     └──────────┬──────────────────┘
                                                │
╔═══════════════════════════════════════════════▼═══════════════════════════╗
║  STAGE 2 — IDEA DECOMPOSITION                                           ║
║                                                                         ║
║  Requirements Parser → R# list + traceability matrix                    ║
║                                    │                                    ║
║  Parser also designates the CONTRACT AUTHORITY — one spec owns every    ║
║  cross-cutting type/prop. Others REFERENCE, never redefine. This is     ║
║  the preventive half: both prior runs failed on contract drift.         ║
║                                                                         ║
║  Spec Writers (PARALLEL, one per NEW component — reuse needs no spec)   ║
║  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                   ║
║  │ Spec A   │ │ Spec B   │ │ Spec C   │ │ Spec D   │  ...              ║
║  └─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘                   ║
║        ▼             ▼             ▼             ▼                      ║
║  ALL PARALLEL, all independent of writers:                              ║
║  ┌───────────────────────────┐  ┌──────────────────────────────────┐   ║
║  │ PER-SPEC AUDITORS         │  │ CROSS-SPEC AUDITOR (reads ALL)   │   ║
║  │ dedicated for: contract   │  │ ONLY job: conflicts BETWEEN      │   ║
║  │  authority, >=8 AC,       │  │ specs. Contract violations,      │   ║
║  │  >=150 lines, page-level  │  │ type disagreements, naming       │   ║
║  │ batched for: stubs,       │  │ drift, duplicated responsibility,│   ║
║  │  placeholders, fixtures   │  │ seam gaps.                       │   ║
║  │ 9-pt checklist, PASS/FAIL │  │ This is what caught 8/8 round-1  │   ║
║  │                           │  │ failures in a real run.          │   ║
║  └─────────────┬─────────────┘  └───────────────┬──────────────────┘   ║
║                └────────────────┬────────────────┘                      ║
║        ├── FAIL? → fix at source (authority wins ties) → fresh -v2      ║
║        │          audits + ONE cross-spec re-run, then escalate         ║
║        ▼                                                                ║
║  Question Synthesizer (haiku) → consolidates all open Qs +              ║
║                                 flags contract-addition requests        ║
╚═══════════════════════════════════════════════╤═══════════════════════════╝
                                                │
                                     ┌──────────▼──────────┐
                                     │   GATE 2            │
                                     │   All specs PASS    │
                                     │   before proceeding │
                                     └──────────┬──────────┘
                                                │
╔═══════════════════════════════════════════════▼═══════════════════════════╗
║  STAGE 3 — IMPLEMENTATION                                               ║
║                                                                         ║
║  Step 3.1 SCAFFOLD — two paths                                          ║
║  ┌──────────────────────────────┐  ┌──────────────────────────────────┐ ║
║  │ WARM: starter/ exists        │  │ 🧊 COLD: no starter yet          │ ║
║  │ NO SUBAGENT.                 │  │ Full scaffolder subagent — its   │ ║
║  │  cp -R _design-system/<app>/ │  │ output gets promoted and         │ ║
║  │       starter/ → <feature>/  │  │ inherited forever                │ ║
║  │  npm install && npm run dev  │  │                                  │ ║
║  │  + component stubs, routes   │  │ Builds: framework per recon,     │ ║
║  │  + tsc --noEmit clean        │  │ verbatim token files, font       │ ║
║  │                              │  │ loading, mock API, APP SHELL,    │ ║
║  │ Theme files, MSW, app shell  │  │ URL-param state utility          │ ║
║  │ arrive PRE-VALIDATED (>=90   │  │                                  │ ║
║  │ fidelity when promoted).     │  │ After Gate 3, if fidelity >=90:  │ ║
║  │ No boot-debug loop.          │  │  → PROMOTE to starter/           │ ║
║  │                              │  │  (verify boots in isolation,     │ ║
║  │ Boot fails? Starter drifted: │  │   write STARTER.md, exclude all  │ ║
║  │ fix IN starter, re-copy      │  │   feature code)                  │ ║
║  └──────────────────────────────┘  └──────────────────────────────────┘ ║
║                                    │                                    ║
║  Step 3.2 Implementer / Validator Pairs (MAX PARALLELISM)               ║
║  Each implementer gets: spec + brief + Visual Identity + Common         ║
║  Mistakes PASTED; app-wide design-system.md as PATH + PROOF-OF-READ     ║
║  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         ║
║  │  IMPLEMENTER A  │  │  IMPLEMENTER B  │  │  IMPLEMENTER C  │  ...    ║
║  │  (writes code)  │  │  (writes code)  │  │  (writes code)  │         ║
║  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         ║
║           ▼                    ▼                    ▼                   ║
║  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         ║
║  │  VALIDATOR A    │  │  VALIDATOR B    │  │  VALIDATOR C    │         ║
║  │  (default FAIL) │  │  (default FAIL) │  │  (default FAIL) │         ║
║  │  12-pt checklist│  │  12-pt checklist│  │  12-pt checklist│         ║
║  │  PASS/FAIL      │  │  PASS/FAIL      │  │  PASS/FAIL      │         ║
║  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         ║
║           │                                                             ║
║           ├── FAIL? → fresh implementer + validator (max 2 retries)     ║
║           ▼                                                             ║
║  ALL components must PASS before proceeding                             ║
╚═══════════════════════════════════════════════╤═══════════════════════════╝
                                                │
╔═══════════════════════════════════════════════▼═══════════════════════════╗
║  STAGE 4 — COMPOSITION & FIDELITY                                       ║
║                                                                         ║
║  Integrator → wire pages, routing, mock data, app shell                 ║
║  Smoke Test → npm install, npm run dev, npx tsc --noEmit                ║
║                                    │                                    ║
║  Step 4.3: FIDELITY REVIEWER (pure reporter)                            ║
║  ┌─────────────────────────────────────────────────────────────┐        ║
║  │   Screenshots staging ←→ prototype (Chrome DevTools)        │        ║
║  │   PROOF OF READ on the app-wide file before scoring tokens  │        ║
║  │   8-point weighted anchors + holistic +/-5 adjustment       │        ║
║  │   SCORE: 0━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━100  │        ║
║  │                         target: >=90                        │        ║
║  │                                                             │        ║
║  │   Returns proposed_fixes[] — does NOT edit files            │        ║
║  │   Returns app_level_lessons[] → appended to the app-wide    │        ║
║  │     "Common Mistakes To Avoid" (file learns every run)      │        ║
║  │   Orchestrator applies ALL fixes, reports to user           │        ║
║  └──────────────────────────────┬──────────────────────────────┘        ║
║                    ┌────────────┴────────────┐                          ║
║        fixes made  │                         │ no fixes                 ║
║                    ▼                         │                          ║
║  Step 4.4: FRESH reviewer, SCOPED re-score   │                          ║
║   • failed dimensions in full detail         │                          ║
║   • holistic feel +/-5 ALWAYS (mandatory —   │                          ║
║     a fix can break what already passed)     │                          ║
║   • regression sweep on previously-full dims │                          ║
║            Max 2 total passes → escalate     │                          ║
╚═════════════════════════════════════════╤════╧══════════════════════════╝
                                          │
╔═════════════════════════════════════════▼═══════════════════════════════╗
║  EVALS & OBSERVABILITY  (before user sees prototype, even on failure)  ║
║                                                                        ║
║  Step 4.5: RUN EVALS (7 automated checks)                              ║
║  ┌──────────────────────────────────────────────────────────────┐       ║
║  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐         ║       ║
║  │  │ G1 │ │ G2 │ │ G3 │ │ G4 │ │ G5 │ │ G6 │ │ G7 │         ║       ║
║  │  │No  │ │Frmw│ │All │ │Spec│ │No  │ │Data│ │Meta│         ║       ║
║  │  │inv.│ │mrk │ │stat│ │audt│ │rein│ │layr│ │eval│         ║       ║
║  │  │clrs│ │mtch│ │impl│ │pass│ │comp│ │mtch│ │scrd│         ║       ║
║  │  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘         ║       ║
║  │  Results → update evals.md + pass to Steps 4.6–4.7          │       ║
║  └──────────────────────────────────────────────────────────────┘       ║
║                                    │                                    ║
║  Step 4.6: LOG INVOCATION (orchestrator writes JSONL)                   ║
║  ┌──────────────────────────────────────────────────────────────┐       ║
║  │  1 line → invocation-log.jsonl                               │       ║
║  │  ts, version, stages_completed, fidelity_score,              │       ║
║  │  subagent_count, cold_start, promotions, outcome,            │       ║
║  │  eval_results (compact)                                      │       ║
║  │                                                              │       ║
║  │  THEN `tail -1` TO VERIFY THE WRITE LANDED. A silently       │       ║
║  │  failed append leaves no record and no signal. Report a      │       ║
║  │  miss as a skill defect rather than proceeding.              │       ║
║  └──────────────────────────────────────────────────────────────┘       ║
║                                    │                                    ║
║  Step 4.7: INDEPENDENT TRACE (separate subagent authors trace)          ║
║  ┌──────────────────────────────────────────────────────────────┐       ║
║  │  Inspects artifacts on disk — orchestrator NEVER writes this │       ║
║  │                                                              │       ║
║  │  Gate Evidence:  Gate 0   Gate 1     Gate 2   Gate 3         │       ║
║  │                  Scope    Brief+     Specs    Fidelity       │       ║
║  │                           Promotions  (latest audit per spec)│       ║
║  │                                                              │       ║
║  │  + context_sources + decisions + per_stage_summary           │       ║
║  │  + tool_calls + observations + eval_results (full detail)    │       ║
║  │  + discrepancies vs. the JSONL entry                         │       ║
║  │  + flags a brief that duplicates app-wide token tables       │       ║
║  │                                                              │       ║
║  │  → observability/traces/YYYY-MM-DD_HHMM_<slug>.json          │       ║
║  └──────────────────────────────────────────────────────────────┘       ║
║                                                                        ║
║  MID-RUN FAILURE: skip evals → JSONL stub → still attempt trace        ║
╚═════════════════════════════════════════╤═══════════════════════════════╝
                                          │
                               ┌──────────▼──────────┐
                               │   GATE 3            │
                               │   User reviews      │
                               │   running prototype │
                               │   Fidelity score +  │
                               │   eval results +    │
                               │   trace confirmed   │
                               └──────────┬──────────┘
                                          │
                                          │  User: "push it"
                                          ▼
╔══════════════════════════════════════════════════════════════════════════╗
║  STAGE 5 — REPO PUSH  (explicit user trigger only)                     ║
║                                                                        ║
║  Pre-push prep → Push via GitHub MCP → Verify file landed              ║
║  Branch: prototype/<feature>                                           ║
╚══════════════════════════════════════════════════════════════════════════╝


  ═══════════════════════════════════════════════════════════════════
  KEY DESIGN PRINCIPLES
  ═══════════════════════════════════════════════════════════════════

  CONTEXT CONTRACT      Paste FRAMING (what a subagent reasons from).
                        Path LOOKUPS (what it looks values up in),
                        always with a PROOF-OF-READ. Prompt templates
                        live in references/, loaded per stage — never
                        improvised. v3.1 failed by diluting subagent
                        context across 44 files; this is the guard.

  DESIGN SYSTEM AS      One app-wide design-system.md per app = single
  GROWING ASSET         source of truth, referenced and incrementally
                        updated — never copied, never regenerated.
                        Each prototype adds only a small design-brief.md.
                        Established findings are PROMOTED into the shared
                        file at Gate 1, so every run improves the next.
                        ALLOWLIST = design-system.md ∪ design-brief.md

  STARTER TEMPLATE      First run to score >=90 gets its scaffold frozen
                        as _design-system/<app>/starter/. Later runs
                        cp -R it — inheriting proven fidelity instead of
                        re-rolling the dice on the app shell.

  EVIDENCE >=3          No "Established" pattern without >=3 citations.
                        Also the promotion threshold.

  ADVERSARIAL REVIEW    Builder =/= reviewer. Default verdict: FAIL.
                        One auditor per spec, each independent of the
                        writer. Trace authored by independent subagent.

  HOLISTIC FIDELITY     Weighted anchor scoring (8 items, 0-100) +/-5.
                        Reviewer reports findings with proposed fixes.
                        Orchestrator applies all fixes. Fresh reviewer
                        re-scores. Iterate until >=90. The holistic
                        check is NEVER scoped away.

  RIGHT SUBAGENT TYPE   Explore = read-only (no Write/Edit). Any subagent
                        that writes to disk MUST be general-purpose.
                        Explore agents return findings; the orchestrator
                        writes them.

  TIER BY VERIFIABILITY Cheaper models ONLY where a wrong answer surfaces
                        deterministically: freshness check (sonnet),
                        question synthesizer (haiku), trace author
                        (sonnet). Everything else inherits the session
                        model. Implementers and validators are NEVER
                        tiered — adversarial review is load-bearing.
                        🧊 Cold start inherits everywhere (no baseline).

  NEVER INVENT          If it's not in production code, don't use it.

  EVALS AS GUARD        7 automated checks (G1-G7) run before Gate 3.
                        All code-based, resolved against the union
                        allowlist. Results feed into logs + traces.

  OBSERVABILITY         Every run recorded. JSONL (orchestrator, write
                        verified with tail -1) + full JSON trace
                        (independent subagent, never the orchestrator).

  ═══════════════════════════════════════════════════════════════════
  TOOL CHAIN
  ═══════════════════════════════════════════════════════════════════

  Code Explorer MCP ──── extract tokens/patterns from production code
  Chrome DevTools MCP ── SSO bootstrap, staging screenshots, live comparison
  Figma MCP ──────────── design context + screenshots (user-provided URLs only)
  GitHub MCP ─────────── push to repo (Stage 5 only, on user trigger)
  Agent tool ─────────── spawn Explore + general-purpose subagents
  Read/Write/Edit ────── manage prototype files on disk
  Bash ───────────────── npm install, npm run dev, tsc --noEmit, eval checks
```
