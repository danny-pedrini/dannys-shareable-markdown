# Feature Impact Sizing — How It Works

This skill takes a feature idea and produces a defensible dollar-impact
estimate with three scenarios (Low / Base / High) as an interactive
Google Sheet — the sole deliverable. Stakeholders flex assumptions
directly in the sheet and scenarios recalculate live.

---

## The Flow at a Glance

```
  YOU                     CLAUDE                         EXTERNAL
  ───                     ──────                         ────────

  "Size the impact of
   feature X on metric Y"
         │
         ▼
  ┌──────────────┐
  │  1. INTAKE   │  What's the feature?
  │              │  Which metric? (labor, shipping, quality...)
  │  You answer  │  What cost type? (labor only, materials, etc.)
  │  questions   │  Which process step(s)?
  │              │  Scope constraints?
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  1.5  SME    │  "Do you have internal data I
  │  ASSUMPTIONS │   should bake into the model?"
  │              │
  │  You share   │  Time studies, vendor claims,
  │  what you    │  ops estimates, constraints,
  │  know        │  counter-evidence
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  2. PROBLEM  │  Is the problem clear?
  │  FRAMING     │  Who is affected?
  │              │  HOW does it improve the metric?
  │  Pushes back │
  │  if vague    │  (Won't invest research time
  └──────┬───────┘   on a fuzzy problem)
         │
         ▼
  ┌──────────────┐
  │  2.5 RESEARCH│  Claude recommends:
  │  GATE        │  SKIP (you have strong internal data)
  │              │  RUN  (need external benchmarks)
  │  YOU DECIDE  │
  │              │  Saves 15-30 min when you
  │              │  already have the signal
  └──────┬───────┘
         │
         ├── if RUN ──────────────────┐
         │                            │
         │   These run AT THE SAME    │
         │   TIME to save wait time   │
         │                            │
         ▼                            ▼
  ┌──────────────┐         ┌──────────────┐
  │  3. RESEARCH │         │  4. SCALE    │
  │              │         │     DATA     │
  │  Searches    │         │              │   ┌─────────────┐
  │  for external│         │  Reads live  │──▶│ Google      │
  │  benchmarks  │         │  Hims data   │   │ Sheets      │
  │  & case      │         │  from 3      │   │             │
  │  studies     │         │  spreadsheets│   │ • TPH Track. │
  │              │         │              │   │ • Win Calc   │
  │  Returns:    │         │  Returns:    │   │ • Project    │
  │  numbers     │         │  volumes,    │   │   Entitle.   │
  │  with exact  │         │  TPH, labor  │   └─────────────┘
  │  quotes      │         │  dollars, OT │
  └──────┬───────┘         └──────┬───────┘
         │                        │
         └────────┬───────────────┘
                  │         (if SKIP, only
                  │          Scale Data runs)
                  ▼
  ┌──────────────────────────────────────┐
  │  5. TIER SOURCES + EXTRACT BENCHMARKS│
  │                                      │
  │  A = McKinsey, Gartner (best)        │
  │  B = trade pubs (good)               │
  │  C = blogs, marketing (weak)         │
  │                                      │
  │  Then: build proposed scenarios      │
  │  using decision tree logic           │
  └──────────────┬───────────────────────┘
                 │
                 │  These run AT THE SAME TIME
                 │
                 ├─────────────────────────┐
                 ▼                         ▼
  ┌──────────────────┐       ┌──────────────────┐
  │  5.5  QUALITY    │       │  6-PREP          │
  │  GATE            │       │                  │
  │                  │       │  Formats the     │
  │  10 automated    │       │  review tables   │
  │  checks:         │       │  for you         │
  │                  │       │                  │
  │  Quotes real?    │       └────────┬─────────┘
  │  Data fresh?     │                │
  │  Physically      │                │
  │  possible?       │                │
  │  Savings <       │                │
  │  total cost?     │                │
  │  Sources         │                │
  │  credible?       │                │
  │  SME & bench     │                │
  │  aligned?        │                │
  │  No double       │                │
  │  counting?       │                │
  │  ...and more     │                │
  │                  │                │
  │  Returns:        │                │
  │  PASS / WARN /   │                │
  │  FAIL per check  │                │
  └────────┬─────────┘                │
           │                          │
           └──────────┬───────────────┘
                      │
                      ▼
  ┌───────────────────────────────────────────┐
  │                                           │
  │  6. HUMAN REVIEW GATE                     │
  │                                           │
  │  Claude shows you EVERYTHING before       │
  │  calculating anything:                    │
  │                                           │
  │  • Quality gate results (if issues)       │
  │  • SME assumptions you provided           │
  │  • Benchmarks found (with grades)         │
  │  • Hims scale data being used             │
  │  • Proposed Low / Base / High scenarios   │
  │  • Addressable base reconciliation        │
  │                                           │
  │  ─────────────────────────────────────    │
  │  "Want to adjust any values before        │
  │   I run the calculations?"                │
  │  ─────────────────────────────────────    │
  │                                           │
  │  YOU DECIDE. Adjust, approve, or abort.   │
  │                                           │
  └───────────────────┬───────────────────────┘
                      │
                      ▼
  ┌──────────────────┐
  │  7. CALCULATE    │    ┌────────────────────┐
  │                  │───▶│ sizing_            │
  │  All math runs   │    │ calculator.py      │
  │  through a       │    │                    │
  │  Python script,  │◀───│ Deterministic —    │
  │  NOT the LLM     │    │ same input always  │
  │                  │    │ gives same output   │
  │  Built-in sanity │    │                    │
  │  checks verify   │    │ Catches arithmetic │
  │  the inputs too  │    │ errors before they │
  │                  │    │ reach the sheet    │
  └────────┬─────────┘    └────────────────────┘
           │
           ▼
  ┌──────────────────┐    ┌────────────────────┐
  │  8. BUILD SHEET  │───▶│  Interactive       │
  │                  │    │  Google Sheet      │
  │  The SOLE        │    │                    │
  │  deliverable —   │    │  6 tabs:           │
  │  no separate     │    │  README (15 rows   │
  │  markdown report │    │   — narrative +    │
  │                  │    │   live formulas)   │
  │  Builds all tabs,│    │  Assumptions       │
  │  formulas, and   │    │  Scenarios         │
  │  narrative on    │◀───│  TPH Variance      │
  │  the README tab  │    │  Benchmarks        │
  │                  │    │  SME Inputs        │
  │  Verified by     │    │                    │
  │  evals S13-S22   │    │  Yellow cells =    │
  │                  │    │  edit these        │
  └────────┬─────────┘    └────────────────────┘
           │
           ▼
  ┌──────────────────┐
  │  8.5 CROSS-TAB   │  An independent reviewer
  │  COHERENCE QA    │  checks CROSS-TAB
  │                  │  consistency:
  │  Step-level evals│
  │  (S13-S22) already • README vs Scenarios
  │  caught formulas │  • Source counts match
  │  + structure +   │  • Validation vs risks
  │  tag issues.     │  • SME inputs reflected
  │  This catches    │    in model factors
  │  what passes     │  • Mechanism vs factors
  │  individually    │
  │  but contradicts │  Orchestrator applies ALL
  │  across tabs     │  fixes via MCP
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────────────────────────────┐
  │  10-11. BEHIND THE SCENES                │
  │  (runs automatically — you don't         │
  │   need to do anything)                   │
  │                                          │
  │  10. Evals — grades the output against   │
  │      quality criteria (G1-G11, S1-S30)   │
  │                                          │
  │  11. Trace + Log — an independent        │
  │      auditor verifies process gates,     │
  │      writes the trace file AND the       │
  │      invocation log entry                │
  │      (not self-reported)                 │
  └────────┬─────────────────────────────────┘
           │
           ▼

  ┌─────────────────────────────┐
  │  DELIVERABLES               │
  │                             │
  │  1. Google Sheet model      │
  │     (sole deliverable —     │
  │      README tab has the     │
  │      full narrative)        │
  │                             │
  │  2. Confidence rating       │
  │     HIGH / MEDIUM / LOW     │
  │     (on README tab)         │
  │                             │
  │  3. Validation path         │
  │     (on README tab)         │
  │                             │
  │  4. Calculator artifacts    │
  │     (JSON inputs/outputs    │
  │      for audit trail)       │
  └─────────────────────────────┘
```

---

## Key Design Principles

**You stay in control.** Claude never calculates without showing you
the inputs first (Phase 6). You can adjust any assumption, override
any scenario, or abort entirely.

**Research is optional.** If you already have strong internal data
(time studies, pilot results), Claude recommends skipping the 15-30
minute research pipeline. You decide at Phase 2.5.

**No LLM math.** Every calculation runs through a deterministic Python
script. Same inputs always produce the same outputs. The script also
runs its own sanity checks on the inputs — catching arithmetic errors
before they reach the sheet.

**Every number is cited.** Benchmarks include exact quotes from the
source. SME assumptions are tagged with who said what. Scale data
shows which spreadsheet tab it came from.

**Three scenarios, not one.** Low / Base / High with explicit
assumptions for each. Stakeholders can see what drives the range
and flex it in the Google Sheet.

**Independent QA.** After building the sheet, a separate reviewer
checks cross-tab coherence — catching contradictions between tabs
that pass individually. The author can't grade their own work.

**Addressable base is explicit.** For labor cost sizings, the TPH
Variance tab shows exactly what's in the addressable base and what's
excluded — no more conflating the $4 variable cost with the $10+
fully loaded cost.

**Confidence is explicit.** The output tells you how much to trust it:
- **HIGH** — use for prioritization decisions
- **MEDIUM** — run a focused validation first (time study, pilot)
- **LOW** — do not use for prioritization; run discovery first

---

## Architecture

```
SKILL.md                      ← Orchestrator: phases, constraints, workflow
references/
  data-sources.md             ← Spreadsheet IDs, ranges, physical limits
  subagent-contracts.md       ← Subagent contracts, 10-check quality gate
  scenario-logic.md           ← Decision tree, tier-weighting, confidence
  sheet-builder.md            ← Google Sheet formulas, formatting, verification
evals.md                      ← Quality criteria (G1-G11 end-of-run, S1-S30 step-level)
observability/
  invocation-log.jsonl        ← Run history (one line per sizing)
  traces/                     ← Independent audit trails per run
scripts/
  sizing_calculator.py        ← Deterministic math engine + sanity checks
  source_tierer.py            ← A/B/C source classification
```
