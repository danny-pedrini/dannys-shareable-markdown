# Feature Impact Sizing — Loop Architecture Diagram

> Last updated: 2026-06-17 | 45 active checks across 6 eval gates

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    FEATURE IMPACT SIZING LOOP                              ║
║                    Google Sheet = sole deliverable                          ║
║                    45 active checks across 6 eval gates                    ║
╚══════════════════════════════════════════════════════════════════════════════╝


┌──────────────────────────────────────────────────────────────────────────────┐
│  TRIGGER: "Size the impact of feature X on metric Y"                        │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
═══════════════════════════════════════════════════════════════  HUMAN GATES
                               │
┌──────────────────────────────▼───────────────────────────────────────────────┐
│  1. INTAKE                                                       [HUMAN]    │
│                                                                             │
│  • Collect feature description (≥2 sentences)                    BLOCKING   │
│  • Map primary metric (labor/shipping/fulfillment/quality/turnaround)       │
│  • Identify cost type (labor_only, materials_only, shipping_only, etc.)     │
│  • Identify affected process steps (for labor_cost)                         │
│  • Derive ARTIFACT_DIR: Impact Sizings/_artifacts/<feature-slug>/           │
│  • Get scope constraints (sites, products, time horizon)                    │
│                                                                             │
│  OUTPUTS: Structured intake record, ARTIFACT_DIR path                       │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────────────┐
│  1.5 SME ASSUMPTIONS                                             [HUMAN]    │
│                                                                             │
│  • Ask PM for: time studies, vendor claims, ops estimates, constraints,     │
│    counter-evidence                                                         │
│  • Capture each: value, source, confidence (HIGH/MED/LOW),                 │
│    applies_to (improvement_pct, adoption_rate, baseline_override, etc.)     │
│                                                                             │
│  OUTPUTS: SME assumptions array (or empty array if none)                    │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────────────┐
│  2. PROBLEM FRAMING                                                         │
│                                                                             │
│  • Verify: problem statement exists, target identified, mechanism clear     │
│  • Push back if vague: "How does [feature] improve [metric]?"              │
│                                                                             │
│  OUTPUTS: Validated mechanism description                                   │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────────────┐
│  2.5 RESEARCH GATE                                                          │
│                                                                             │
│  • Assess: SME confidence, feature novelty, benchmark availability          │
│  • Recommend SKIP (strong SME data) or RUN (need benchmarks)               │
│  • Wait for user confirmation                                               │
│                                                                             │
│  OUTPUTS: Decision — SKIP or RUN                                            │
│  If SKIP: Phases 3, 5.1-5.4 bypassed.                                      │
│           S1,S2,S5,S6,S24,S25,S26,S28 skipped.                             │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
═══════════════════════════════════════════════════════════════  SELF-CORRECTION
                               │                                   LOOP BEGINS
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
┌────────────────────────────┐  ┌────────────────────────────┐
│  3. RESEARCH    (parallel) │  │  4. SCALE DATA  (parallel) │
│                            │  │                            │
│  • Generate 5-8 queries    │  │  • Pre-flight MCP check    │
│  • Run research pipeline   │  │  • Read live sheet data:   │
│    (15-30 min)             │  │    TPH Tracker, Win Calc,  │
│                            │  │    Project Entitlement     │
│  ┌──────────────────────┐  │  │  • Pull ALL labor pools    │
│  │ TIMEOUT (>45 min):   │  │  │  • Compute per-pool labor  │
│  │ Human gate — 4 opts: │  │  │    cost and variance gap   │
│  │ 1. Retry fewer queries│  │  │                            │
│  │ 2. Proceed SME-only  │  │  │  OUTPUT: Structured JSON   │
│  │ 3. Wait longer       │  │  │  {metric_category,         │
│  │ 4. Abort             │  │  │   volumes, baselines,      │
│  │ DO NOT auto-proceed  │  │  │   labor_data, conflicts[]} │
│  └──────────────────────┘  │  │                            │
│                            │  │                            │
│  OUTPUT: JSON benchmarks   │  │                            │
│  [{source_title, url,      │  │                            │
│    improvement_value,      │  │                            │
│    exact_quote, ...}]      │  │                            │
└─────────────┬──────────────┘  └─────────────┬──────────────┘
              │                               │
              ▼                               ▼
╔═════════════════════════════╗  ╔═════════════════════════════╗
║  EVAL GATE 1 (4 evals)     ║  ║  EVAL GATE 2 (4 evals)     ║
║                             ║  ║                             ║
║  S1:  Schema validity       ║  ║  S3:  Schema + completeness ║
║  • Valid JSON? Non-null     ║  ║  • metric_category match?   ║
║    fields?                  ║  ║  • volumes > 0? baselines?  ║
║                             ║  ║  • site sums ≈ annual total?║
║  S2:  Quote-value alignment ║  ║                             ║
║  • improvement_value in     ║  ║  S4:  Range reasonableness  ║
║    exact_quote?             ║  ║  • TPH 10-55?              ║
║                             ║  ║  • Volume/site 2M-8M?      ║
║  S24: Quote-in-chunk        ║  ║  • Pack rate $25-$32?       ║
║  • exact_quote in research  ║  ║                             ║
║    pipeline chunk file?     ║  ║  S23: Canonical source      ║
║  • Catches fabrication      ║  ║  • Right source per metric? ║
║                             ║  ║  • Volume from D&F_Summary  ║
║  S28: Query quality         ║  ║    NOT TPH Tracker YTD?     ║
║  • Metric-specific terms    ║  ║                             ║
║    present in each query?   ║  ║  S27: MCP read completeness ║
║  • Feature name present?    ║  ║  • Row/col count matches    ║
║                             ║  ║    data-sources.md ranges?  ║
║                             ║  ║  • Catches silent truncation║
╚════════════╤════════════════╝  ╚════════════╤════════════════╝
             │                                │
             └────────────────┬───────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────────────────┐
│  5. SOURCE TIERING + BENCHMARK EXTRACTION                                    │
│                                                                              │
│  • 5.1: source_tierer.py → A/B/C tier per source                           │
│  • 5.2: Extract benchmarks (8 fields + optional conversion_note)            │
│  • 5.3: Save → $ARTIFACT_DIR/extracted_benchmarks.json                      │
│  • 5.4: Validate + save drops → extraction_drops.json                       │
│                                                                              │
│  OUTPUTS: extracted_benchmarks.json + extraction_drops.json                  │
└─────────────────────────────┬────────────────────────────────────────────────┘
                              │
╔═════════════════════════════╧════════════════════════════════════════════════╗
║  EVAL GATE 3 (4 evals)                                                      ║
║                                                                             ║
║  S5:  Completeness + traceability                                           ║
║  • All 8 fields populated? URLs in VERIFIED_URLS.md? Tiers valid?          ║
║                                                                             ║
║  S6:  Value-in-quote accuracy                                               ║
║  • improvement_value in exact_quote? Catches orchestrator drift             ║
║                                                                             ║
║  S25: Extraction coverage                                                   ║
║  • extracted + dropped ≥ Research Agent output count?                       ║
║  • Catches silently dropped benchmarks                                      ║
║                                                                             ║
║  S26: Improvement type consistency                                          ║
║  • All benchmarks same type (%, $, time)? If mixed, conversion_note?       ║
║  • Prevents nonsense in tier-weighted averaging                             ║
╚═════════════════════════════╤════════════════════════════════════════════════╝
                              │
                 ┌────────────┴────────────────┐
                 │                             │
                 ▼                             ▼
┌────────────────────────────┐  ┌──────────────────────────────┐
│  5.5 QUALITY GATE          │  │  6-PREP                      │
│       (parallel)           │  │       (parallel)             │
│                            │  │                              │
│  10 structured checks:     │  │  Format 4 review tables      │
│  1. Quote accuracy         │  │  for Human Review Gate       │
│  2. Scale data reasonable  │  │                              │
│  3. Data freshness         │  │                              │
│  4. Conflict verification  │  │                              │
│  5. Physical plausibility  │  │                              │
│  6. Addressable base       │  │                              │
│  7. Source quality + indep │  │                              │
│  8. SME-benchmark align    │  │                              │
│  9. Scenario consistency   │  │                              │
│     (9b overlaps QG10 —    │  │                              │
│      intentional, see      │  │                              │
│      subagent-contracts)   │  │                              │
│  10. Factor redundancy     │  │                              │
│                            │  │                              │
│  OUTPUT: JSON {checks[10], │  │  OUTPUT: Formatted markdown  │
│   summary: {pass, warn,    │  │  tables for Phase 6          │
│   fail, blocking}}         │  │                              │
└─────────────┬──────────────┘  └──────────────┬───────────────┘
              │                                │
              ▼                                │
╔═════════════════════════════╗                 │
║  EVAL GATE 4 (2 evals)     ║                 │
║                             ║                 │
║  S7: QG output integrity    ║                 │
║  • 10 checks, counts sum,   ║                 │
║    blocking flag correct    ║                 │
║                             ║                 │
║  S8: Zero blocking failures ║                 │
║  • On FAIL: fix scenario    ║                 │
║    → re-run QG → re-eval    ║                 │
╚════════════╤════════════════╝                 │
             │                                 │
             └─────────────────┬───────────────┘
                               │
═══════════════════════════════════════════════════════════════  HUMAN GATE
                               │
┌──────────────────────────────▼───────────────────────────────────────────────┐
│  6. HUMAN REVIEW GATE                                            [HUMAN]    │
│                                                                             │
│  • Present: QG audit, SME assumptions, benchmarks, scale data, scenarios   │
│  • Ask: "Want to adjust any values before I run the calculations?"          │
│  • Wait for confirmation. Incorporate adjustments.                          │
│                                                                             │
│  OUTPUTS: User-confirmed scenario assumptions                               │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
═══════════════════════════════════════════════════════════════  SELF-CORRECTION
                               │                                   CONTINUES
┌──────────────────────────────▼───────────────────────────────────────────────┐
│  7.1 CONSTRUCT CALCULATOR INPUT                                              │
│                                                                              │
│  • Pick model pattern: variance-closure, improvement×adoption, or unit-cost  │
│  • Run 4-step factor redundancy check                                        │
│  • Build factors[] array + derivations + per_unit_divisor                    │
│  • Save → $ARTIFACT_DIR/sizing_input.json                                    │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
╔══════════════════════════════╧═══════════════════════════════════════════════╗
║  EVAL GATE 5 (2 evals)                                                      ║
║                                                                             ║
║  S9:  Calculator input schema                                               ║
║  • JSON structure, Low<Base<High, derivations present                      ║
║  • per_unit_divisor > 0 and within 2M-15M for shipment metrics             ║
║                                                                             ║
║  S10: Factor independence — no double-counting              [LLM JUDGE]     ║
║  • Variable factor redundant with constant's derivation?                    ║
║  • Blocks calculator from running on inflated inputs                        ║
╚══════════════════════════════╤═══════════════════════════════════════════════╝
                               │
┌──────────────────────────────▼───────────────────────────────────────────────┐
│  7.2 RUN CALCULATOR                                                          │
│                                                                              │
│  • sizing_calculator.py — ALL math here, LLM never does arithmetic          │
│  • 7.3 Verify: 3 scenarios, sanity_checks[] PASS, steps complete            │
│                                                                              │
│  OUTPUT: $ARTIFACT_DIR/sizing_output.json                                    │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────────────┐
│  8. BUILD GOOGLE SHEET (sole deliverable)                                    │
│                                                                              │
│  Per sheet-builder.md:                                                       │
│                                                                              │
│  8.1: Create spreadsheet                                                     │
│  8.2: Create tabs: README, Assumptions, Scenarios, TPH Variance             │
│       (labor_cost only), Benchmarks, SME Inputs (always)                    │
│  8.3: Populate all tabs:                                                     │
│       ┌─────────────────────────────────────────────────────────────────┐    │
│       │  README tab (15 rows — the complete narrative)                  │    │
│       │                                                                 │    │
│       │  Rows 1-5:   Metadata (Feature, Date, PM, Metric, Confidence) │    │
│       │  Rows 6-8:   LIVE FORMULAS (Base, Range, Per-Unit)            │    │
│       │  Row 9:      How to Use                                        │    │
│       │  Row 10:     Source Quality (N sources, tier breakdown)        │    │
│       │  Row 11:     Problem Context + impact mechanism               │    │
│       │  Row 12:     Key Assumptions & Risks ([Assumption:] tags)     │    │
│       │  Row 13:     Validation Recommendation                         │    │
│       │  Row 14:     Confidence Rationale                              │    │
│       │  Row 15:     Next Step                                         │    │
│       └─────────────────────────────────────────────────────────────────┘    │
│       Assumptions — 1 row per factor, constants col D, variables C/D/E      │
│       Scenarios — ALL live formulas referencing Assumptions                  │
│       TPH Variance — weekly TPH + variance gap + labor buildup              │
│       Benchmarks — evidence table (7 columns) or skip note                  │
│       SME Inputs — evidence table (7 columns) or "No SME inputs" row       │
│  8.4: Format (yellow highlighting, bold headers, currency/%)                │
│  8.5: Verify (Scenarios Base matches calculator)                            │
│  8.6: Generate shareable link                                                │
│                                                                              │
│  LOCAL CONTEXT DUMP → $ARTIFACT_DIR/sizing_context.json                     │
│  (README narrative, source quality, SME inputs, benchmarks, rationales,     │
│   spreadsheet URL — keeps directory self-contained)                         │
│                                                                              │
│  OUTPUTS: Google Sheet + URL + sizing_context.json                           │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
╔══════════════════════════════╧═══════════════════════════════════════════════╗
║  EVAL GATE 6 (12 evals — highest-count gate)                                ║
║                                                                             ║
║  S13: Attribution tags                                                      ║
║       [Assumption:] in README row 12? [SME:] in Assumptions col G?         ║
║       (non-empty check owned by S21, not S13)                              ║
║                                                                             ║
║  S14: Scenarios cells are formulas (not static)                             ║
║                                                                             ║
║  S15: Formula column references correct                     ◄── HIGHEST     ║
║       Constants→col D, Variables→C/D/E for L/B/H               STAKES      ║
║                                                                             ║
║  S16: Scenarios Base matches calculator (dynamic row finding)               ║
║       Searches col A for "Annual Impact" — not hardcoded to row 2          ║
║                                                                             ║
║  S17: Factor row order matches sizing_input.json                            ║
║                                                                             ║
║  S18: Editable cells have yellow highlighting                               ║
║       (MCP feasibility TBD — may be manual check on first run)             ║
║                                                                             ║
║  S19: Tab structure matches spec (incl. conditional TPH Variance)          ║
║                                                                             ║
║  S20: Constants have blank Low/High columns                                 ║
║                                                                             ║
║  S21: README 15 labels + non-empty + B6/B7/B8 formulas + accuracy          ║
║       Owns all README structural checks (S13 owns attribution only)        ║
║                                                                             ║
║  S22: All 3 scenarios computed, ordered, match calc (dynamic row)          ║
║                                                                             ║
║  S29: Benchmarks + SME Inputs tab column structure (7 headers each)        ║
║                                                                             ║
║  S30: Shareable link generated (valid URL in sizing_context.json)          ║
╚══════════════════════════════╤═══════════════════════════════════════════════╝
                               │
                               │  ⚠️ PROCESS CONSTRAINT: Do NOT modify the
                               │  sheet between Phase 8 eval gate passing
                               │  and Phase 8.5 reading the sheet.
                               │
┌──────────────────────────────▼───────────────────────────────────────────────┐
│  8.5 CROSS-TAB COHERENCE QA (8 checks)                                      │
│                                                                              │
│  Independent subagent reads the sheet as a whole via MCP:                    │
│                                                                              │
│  C1: README ↔ Scenarios                                                     │
│      Headline $, range, per-unit all consistent?                            │
│                                                                              │
│  C2: README Sources ↔ Benchmarks tab                                        │
│      Source count + tier breakdown match actual rows?                        │
│                                                                              │
│  C3: README Validation ↔ README Risks                                       │
│      Recommendation doesn't contradict stated assumptions?                  │
│                                                                              │
│  C4: SME Inputs tab ↔ Assumptions tab                                       │
│      Every SME input reflected in corresponding factor?                     │
│                                                                              │
│  C5: README Mechanism ↔ Assumptions factor names                            │
│      Mechanism description structurally aligned with factors?               │
│                                                                              │
│  C6: README Confidence ↔ Benchmarks + Scenarios                            │
│      Confidence level matches source quality + scenario spread rules?       │
│                                                                              │
│  C7: Assumptions factor count ↔ Scenarios formula factor count              │
│      Every factor row referenced in the multiplication chain?               │
│      Catches silently dropped factors — HIGHEST RISK coherence gap          │
│                                                                              │
│  C8: TPH Variance addressable labor ↔ Assumptions constant (labor only)    │
│      Buildup total matches the model input within 1%?                       │
│                                                                              │
│  Orchestrator applies fixes via MCP modify_sheet_values                      │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
═══════════════════════════════════════════════════════════════  END-OF-RUN
                               │
┌──────────────────────────────▼───────────────────────────────────────────────┐
│  10. END-OF-RUN EVALS (9 active G-evals — safety net)                        │
│                                                                              │
│  G1:  No LLM math — sizing_output.json exists + sheet numbers match calc    │
│  G2:  No fabricated benchmarks — Benchmarks tab quotes contain values       │
│  G4:  Correct addressable base — TPH Variance tab has labor buildup         │
│  G6:  Research gate evidence — Benchmarks tab has data or skip text         │
│  G7:  SME elicitation evidence — SME Inputs tab has data or "none" row      │
│  G8:  Human review gate evidence — Assumptions tab has L/B/H factors        │
│  G10: All evals scored — must run LAST (9 G + 28 S in trace)               │
│       (skips conditional S-evals if no research)                            │
│  G11: Impact mechanism validated — README row 11 matches factors [LLM judge]│
│  G12: sizing_context.json exists + complete — local backup enforcement      │
│                                                                              │
│  RETIRED: G3 (→S19), G5 (→S22), G9 (tautological)                          │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────────────┐
│  11. INDEPENDENT TRACE + LOG                                                 │
│                                                                              │
│  ONE independent subagent — single trust boundary                            │
│                                                                              │
│  EXAMINES (independently, not trusting orchestrator):                        │
│  • Google Sheet via MCP (tabs, README, Scenarios, Benchmarks, SME)          │
│  • $ARTIFACT_DIR/ (sizing_input, sizing_output, sizing_context,             │
│    extracted_benchmarks, extraction_drops)                                   │
│  • evals.md (definitions for corroboration)                                 │
│                                                                              │
│  AUDITS:                                                                     │
│  • Context Sources — which files/sheets/URLs were used                      │
│  • Decisions — research gate, factor inclusion/exclusion, SME anchoring     │
│  • Step Evals — validates orchestrator's step_evals_log                     │
│  • Gate Evidence — independently verifies 4 process gates                   │
│                                                                              │
│  WRITES:                                                                     │
│  1. observability/traces/YYYY-MM-DD_HHMM_<slug>.json  (full trace)         │
│  2. observability/invocation-log.jsonl                  (compact index)     │
│                                                                              │
│  "The AI that does the work never judges its own work"                       │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  📦 DELIVER                                                                  │
│                                                                              │
│  📊 Interactive Model: [Impact Sizing — Feature — Date]                      │
│     Stakeholders edit yellow cells on Assumptions tab to flex scenarios.     │
│                                                                              │
│  Local artifacts ($ARTIFACT_DIR):                                            │
│  ├── sizing_input.json          calculator input (factors + derivations)    │
│  ├── sizing_output.json         calculator output (3 scenarios + steps)     │
│  ├── sizing_context.json        sheet narrative backup (README 11-15,       │
│  │                               source quality, SME, benchmarks,           │
│  │                               factor rationales, sheet URL)              │
│  ├── extracted_benchmarks.json  research evidence (if research ran)         │
│  └── extraction_drops.json      dropped benchmarks with reasons             │
│                                                                              │
│  observability/traces/          independent audit trail per run              │
│  observability/invocation-log   queryable run index (jq)                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## What Happens at Each Eval Gate

```
ORCHESTRATOR completes Phase N
        │
        ▼
EVAL SUBAGENT (independent) spawned with:
  • Expected eval IDs for this phase
  • Artifact paths to read
  • Eval definitions from evals.md
        │
  For each eval: execute check logic → Pass or Fail
        │
  COMPLETENESS META-CHECK: "Did I score every expected eval?"
        │
  Returns: {phase, results[], all_expected_scored, summary}
        │
   ALL PASS? ─── YES ──→ Record in step_evals_log → Phase N+1
        │
        NO
        │
ORCHESTRATOR self-corrects using eval failure detail
        │
EVAL SUBAGENT re-runs FAILING evals only + meta-check
        │
   ALL PASS? ─── YES ──→ Record (with correction) → Phase N+1
        │
        NO → FLAG TO USER (max 1 self-correction attempt)
```

---

## Eval Gate Summary

| Gate | After     | Evals              | What They Catch                     |
|------|-----------|---------------------|-------------------------------------|
| 1    | Research  | S1,S2,S24,S28  (4)  | Schema, fabrication, quote authenticity, query quality |
| 2    | Scale Data| S3,S4,S23,S27  (4)  | Schema, ranges, canonical sources, MCP truncation |
| 3    | Extraction| S5,S6,S25,S26  (4)  | Completeness, drift, coverage, type mix |
| 4    | QG        | S7,S8          (2)  | QG format, blocking failures |
| 5    | Calc Input| S9,S10         (2)  | JSON schema, divisor validity, factor double-counting |
| 6    | Sheet     | S13-S22,S29,S30 (12)| README narrative, formulas, column refs, accuracy, tabs, labels, headers, shareable link |
|      | QA (8.5)  | C1-C8          (8)  | Cross-tab: README↔Scenarios, sources↔benchmarks, factor count parity, buildup↔constant |
|      | End-run   | G1,G2,G4,G6-G8,G10-G12 (9) | Safety net: LLM math, fabrication, gate evidence, context backup, mechanism validation |

**Step-level:** 28 active S-evals across 6 gates
**Coherence:** 8 C-checks (independent subagent)
**End-of-run:** 9 active G-evals (safety net)
**Total:** 45 active checks

---

## Eval Ownership (MECE)

Clear ownership boundaries — no eval checks the same thing at the same phase:

| Concern | Authority | Phase | Backup |
|---------|-----------|-------|--------|
| Quote authenticity (in chunk) | S24 | 3 | — |
| Quote-value alignment (research) | S2 | 3 | S6 (Phase 5), G2 (Phase 10) |
| Query quality | S28 | 3 | — |
| Scale data schema | S3 | 4 | — |
| Scale data ranges | S4 | 4 | QG Check 2 (Phase 5.5) |
| Canonical sources | S23 | 4 | — |
| MCP read completeness | S27 | 4 | — |
| Extraction completeness | S5 | 5 | — |
| Extraction value accuracy | S6 | 5 | G2 (Phase 10) |
| Extraction coverage | S25 | 5 | — |
| Improvement type consistency | S26 | 5 | — |
| QG output integrity | S7 | 5.5 | — |
| Scenario blocking failures | S8 | 5.5 | — |
| Calculator input schema | S9 | 7.1 | — |
| Factor independence | S10 | 7.1 | QG Check 10 (Phase 5.5) |
| README attribution tags | S13 | 8 | — |
| Scenarios are formulas | S14 | 8 | — |
| Formula column refs correct | S15 | 8 | — |
| Base matches calculator | S16 | 8 | S22 (all 3), G1 (Phase 10) |
| Factor row order | S17 | 8 | — |
| Yellow highlighting | S18 | 8 | — (manual if MCP unavailable) |
| Tab structure | S19 | 8 | — |
| Constants blank L/H | S20 | 8 | — |
| README labels + formulas + accuracy | S21 | 8 | C1 (Phase 8.5) |
| All 3 scenarios match calc | S22 | 8 | G1 (Phase 10) |
| Tab column headers | S29 | 8 | — |
| Shareable link | S30 | 8 | G12 (Phase 10) |
| Cross-tab coherence (8 checks) | C1-C8 | 8.5 | — |
| No LLM math | G1 | 10 | S16/S22 (Phase 8) |
| No fabricated benchmarks | G2 | 10 | S2 (Phase 3), S6 (Phase 5) |
| Addressable base | G4 | 10 | — |
| Research gate evidence | G6 | 10 | — |
| SME elicitation evidence | G7 | 10 | — |
| Review gate evidence | G8 | 10 | — |
| All evals scored (runs LAST) | G10 | 10 | — |
| Impact mechanism | G11 | 10 | — |
| sizing_context.json backup | G12 | 10 | S30 (Phase 8) |

---

## Outer Loop (Human-Owned)

```
After delivery, the PM:

1. Reviews the trace file
   • step_evals[]: which phases self-corrected? On what?
   • gate_evidence{}: all 4 process gates confirmed?
   • eval_results[]: any G-eval failures?

2. Queries the invocation log for patterns
   jq '[.step_evals[]? | select(.attempt_2 != null)]
       | map({phase, eval_id, correction})' traces/*.json

3. Runs /evals-advisor when warranted

4. Manually updates evals.md

The system fixes its own mechanical errors.
The PM decides what "good" looks like.
```

---

## Local Artifact Structure

```
Impact Sizings/
  _artifacts/
    <feature-slug>/
      sizing_input.json        ← calculator input (factors + derivations)
      sizing_output.json       ← calculator output (3 scenarios + steps)
      sizing_context.json      ← sheet narrative backup (README 11-15,
      │                           source quality, SME inputs, benchmarks,
      │                           factor rationales, spreadsheet URL)
      extracted_benchmarks.json← research evidence (if research ran)
      extraction_drops.json    ← dropped benchmarks with reasons

observability/
  invocation-log.jsonl         ← one line per run (jq-queryable index)
  traces/
    YYYY-MM-DD_HHMM_<slug>.json ← full independent audit trail per run
```

Directory is self-contained: if the Google Sheet is deleted, sizing_context.json preserves all narrative + evidence context.

---

## Legend

| Symbol | Meaning |
|--------|---------|
| `[HUMAN]` | Human gate — PM provides input or confirms |
| `[LLM JUDGE]` | Eval requires reasoning, not just code checks |
| `╔═══════════╗ EVAL GATE` | Self-correction checkpoint: independent subagent + completeness meta-check. PASS → proceed, FAIL → fix → re-eval, still FAIL → flag |
| Phase 8.5 | Cross-tab coherence QA (C1-C8, independent subagent) |
| G-series | End-of-run safety net (9 active, 3 retired) |
| Phase 11 | Independent trace + log (single subagent, single trust boundary) |
| INNER LOOP | Automated: catch → correct → re-verify (within a run) |
| OUTER LOOP | Human-owned: review traces → curate evals (across runs) |

## Core Rules

1. **"The AI that does the work never judges its own work."**
2. **ALL math goes through sizing_calculator.py.**
3. **The Google Sheet is the sole deliverable.**
4. **The local directory is self-contained (sizing_context.json backup).**
5. **Pipeline timeout = human gate, not silent fallback.**
