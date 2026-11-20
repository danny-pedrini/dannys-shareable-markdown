# Evals: feature-impact-sizing

## Verification Model

Evals use a **three-layer verification** approach:

1. **Step-Level Evals (S-series):** Run mid-pipeline after each critical phase. The orchestrator validates output against S-eval criteria. On FAIL, the self-correction protocol fires: fix → re-validate → escalate to user if still failing. These are the **first line of defense** — catching errors before they propagate downstream.
2. **End-of-Run Evals (G-series, Phase 10):** Check final artifacts — sheet tabs, `sizing_output.json`, file structure. Produces Pass/Fail per eval. These are the **safety net** — catching anything step-level evals missed, especially drift introduced during sheet construction.
3. **Independent Trace (Phase 11):** A separate subagent audits artifacts on disk and records findings in the trace file's `gate_evidence` and `step_evals` sections. Provides independent corroboration — if Phase 10 and Phase 11 disagree, that's a signal to investigate.

Gate-related evals (G1, G6–G8) check artifacts in Phase 10 and are independently corroborated by the trace subagent in Phase 11. The trace's `gate_evidence` section is queryable for trend analysis across runs.

Step-level eval results are recorded in the trace's `step_evals` array, including self-correction attempts and outcomes.

## Active Evals

| ID | Name | Type | Check | Added | Last Result |
|----|------|------|-------|-------|-------------|
| G1 | No LLM math | Generalization | Code | 2026-06-01 | Pass (2026-06-02) |
| G2 | No fabricated benchmarks | Generalization | Code | 2026-06-01 | Pass (2026-06-02) |
| ~~G3~~ | ~~Complete report structure~~ | ~~Retired~~ | — | 2026-06-01 | Retired (2026-06-16) — redundant with S19 (tab structure) in sheet-only architecture |
| G4 | Correct addressable base | Generalization | Code | 2026-06-01 | Pass (2026-06-02) |
| ~~G5~~ | ~~Scenario ordering and transparency~~ | ~~Retired~~ | — | 2026-06-01 | Retired (2026-06-16) — redundant with S22 (scenario ordering + match) in sheet-only architecture |
| G6 | Research gate question asked | Generalization | Code | 2026-06-01 | Pass (2026-06-02) |
| G7 | SME assumption elicitation occurred | Generalization | Code | 2026-06-01 | Pass (2026-06-02) |
| G8 | Human review gate evidence | Generalization | Code | 2026-06-01 | Pass (2026-06-02) |
| ~~G9~~ | ~~Phase 9 Google Sheet built~~ | ~~Retired~~ | — | 2026-06-01 | Retired (2026-06-16) — tautological in sheet-only architecture; S19 covers tab structure |
| G10 | All active evals scored | Generalization | Code | 2026-06-01 | N/A (2026-06-02) |
| G11 | Impact mechanism validated | Generalization | LLM judge | 2026-06-03 | Pass (2026-06-04) |
| G12 | sizing_context.json exists and complete | Generalization | Code | 2026-06-17 | — |

## Step-Level Evals

Step-level evals run mid-pipeline after each critical phase. On FAIL, the self-correction protocol fires before escalating to the user. Results are recorded in the trace's `step_evals` array.

| ID | Phase | Name | Type | Check | Added | Last Result |
|----|-------|------|------|-------|-------|-------------|
| S1 | 3 | Research output schema validity | Generalization | Code | 2026-06-15 | — |
| S2 | 3 | Research quote-value alignment | Generalization | Code | 2026-06-15 | — |
| S3 | 4 | Scale data schema and completeness | Generalization | Code | 2026-06-15 | — |
| S4 | 4 | Scale data range reasonableness | Generalization | Code | 2026-06-15 | — |
| S5 | 5 | Extraction completeness and traceability | Generalization | Code | 2026-06-15 | — |
| S6 | 5 | Extraction accuracy — value-in-quote | Generalization | Code | 2026-06-15 | — |
| S7 | 5.5 | Quality Gate Validator output integrity | Generalization | Code | 2026-06-15 | — |
| S8 | 5.5 | Quality Gate — zero blocking failures | Generalization | Code | 2026-06-15 | — |
| S9 | 7.1 | Calculator input schema validity | Generalization | Code | 2026-06-15 | — |
| S10 | 7.1 | Factor independence (no double-counting) | Generalization | LLM judge | 2026-06-15 | — |
| ~~S11~~ | ~~8~~ | ~~Report structural completeness~~ | ~~Retired~~ | — | 2026-06-15 | Retired (2026-06-16) — report eliminated; S19 covers sheet tab structure, S21 covers README rows |
| ~~S12~~ | ~~8~~ | ~~Report-calculator number consistency~~ | ~~Retired~~ | — | 2026-06-15 | Retired (2026-06-16) — report eliminated; S16 + S22 cover sheet-calculator number consistency |
| S13 | 8 | Assumption and SME attribution tags | Generalization | Code | 2026-06-15 | — |
| S14 | 8 | Scenarios cells are formulas (not static) | Generalization | Code | 2026-06-15 | — |
| S15 | 8 | Scenarios formula column references correct | Generalization | Code | 2026-06-15 | — |
| S16 | 8 | Scenarios Base matches calculator output | Generalization | Code | 2026-06-15 | — |
| S17 | 8 | Factor row order matches sizing_input.json | Generalization | Code | 2026-06-15 | — |
| S18 | 8 | Editable cells have yellow highlighting | Generalization | Code | 2026-06-15 | — |
| S19 | 8 | Tab structure matches specification | Generalization | Code | 2026-06-15 | — |
| S20 | 8 | Constants have blank Low/High columns | Generalization | Code | 2026-06-15 | — |
| S21 | 8 | README labels + B6/B7/B8 accuracy | Generalization | Code | 2026-06-15 | — |
| S22 | 8 | All 3 scenarios computed, ordered, match calc | Generalization | Code | 2026-06-15 | — |
| S23 | 4 | Canonical source compliance | Generalization | Code | 2026-06-16 | — |
| S24 | 3 | Quote-in-chunk verification | Generalization | Code | 2026-06-16 | — |
| S25 | 5 | Extraction coverage (benchmark count reconciliation) | Generalization | Code | 2026-06-16 | — |
| S26 | 5 | Improvement type consistency | Generalization | Code | 2026-06-16 | — |
| S27 | 4 | MCP read completeness (row/column count) | Generalization | Code | 2026-06-17 | — |
| S28 | 3 | Research query quality | Generalization | Code | 2026-06-17 | — |
| S29 | 8 | Benchmarks/SME tab column structure | Generalization | Code | 2026-06-17 | — |
| S30 | 8 | Shareable link generated | Generalization | Code | 2026-06-17 | — |

## Definitions

### G1: No LLM math

**Pass:** (a) `sizing_output.json` exists and has the calculator's structural signature (`sanity_checks[]`, `calculation_steps`, three scenario keys), AND (b) every dollar figure, percentage, and per-unit value in the sheet's README tab rows 6-8 and Scenarios tab matches a value in `sizing_output.json` or an explicitly cited raw data source.
**Fail:** `sizing_output.json` is missing or lacks the calculator's structure (evidence the calculator wasn't used), OR any numerical value in the sheet cannot be traced to the calculator output or a cited source.
**Check type:** Code-based (comparison + structural)

```check
Type: comparison
Source field: sizing_output.json — check structure AND extract all values from scenarios[].result, scenarios[].per_unit_result, scenarios[].factors_used[].value
Target field: Sheet README tab rows 6-8 (Base Case Annual Impact, Range, Per-Shipment Impact) + Scenarios tab all data cells — extract all dollar-formatted numbers and percentages via MCP read_sheet_values
Logic:
  (0) Structural check: Verify sizing_output.json exists at the expected artifact path. Verify it contains: a top-level object with keys for three scenarios (low/base/high), each scenario has result, per_unit_result, factors_used, and calculation_steps fields, and a top-level sanity_checks[] array. If any structural element is missing = Fail (calculator wasn't used or output is fabricated).
  (1) Parse sizing_output.json and build a set of all numeric values (results, per-unit results, factor values) across all three scenarios. Normalize formats: strip $, commas, expand M/K suffixes (e.g., $0.9M → 2500000).
  (2) Read sheet cells via MCP: read_sheet_values on README!B6:B8 and Scenarios!B2:D[last]. Extract all numeric values with the same normalization. Exclude non-metric references.
  (3) For each sheet number, check if it exists in the calculator output set (within 0.5% tolerance for rounding) OR is immediately preceded by a source citation (e.g., "Trans_Summary", "D&F TPH", "TPH Tracker", "Win Calculator", or a research source title).
  (4) Any sheet number not in either set = Fail.
```

**Source:** Derived from NEVER constraint #1 ("Perform ANY math in the LLM — all calculations go through sizing_calculator.py")
**Added:** 2026-06-01 | **Updated:** 2026-06-16 (reworked for sheet-only architecture)
**Notes:** Converted from LLM judge to code check. Step (0) verifies the calculator was used (structural signature); steps (1-4) verify sheet numbers match its output. The Phase 11 trace subagent independently corroborates this finding in `gate_evidence.calculator_used`. Most common trigger is unit conversions (e.g., annual → per-fill) that seem "too simple" for the calculator.

---

### G2: No fabricated benchmarks

**Pass:** Every row in the Benchmarks tab has a non-empty `Exact Quote` cell that contains the claimed improvement value (as substring or semantic equivalent). All URLs match entries in the research pipeline's `VERIFIED_URLS.md`.
**Fail:** Any benchmark row has an empty `Exact Quote`, or the claimed improvement value does not appear in the quoted text, or the URL is not in `VERIFIED_URLS.md`.
**Check type:** Code-based

```check
Type: presence
Source field: Benchmarks tab in the sheet — each row's "Exact Quote" column (via MCP read_sheet_values)
Target field: Same row's "Improvement" column value
Logic: Read Benchmarks tab via MCP read_sheet_values. For each data row, verify that the Exact Quote cell is non-empty AND contains the numeric improvement value (allowing for format variation: "12%" matches "12 percent" or "12%"). Flag any row where the quote is empty or doesn't contain the claimed number.
```

**Source:** Derived from NEVER constraints #2 ("Cite a benchmark number that isn't directly quoted from a research chunk") and #12 ("Fabricate improvement percentages, dollar figures, or benchmark data")
**Added:** 2026-06-01 | **Updated:** 2026-06-16 (reworked for sheet-only architecture)
**Notes:** The Quality Gate Validator (Phase 5.5) Check 1 also covers this, but that runs on raw inputs. This eval catches drift introduced during sheet construction (Phase 8).

---

### G3: Complete report structure

**Pass:** The report contains all required sections with non-empty content: TL;DR, Problem Context, Benchmarks (with source quality summary), Hims Scale Data, Scenario Analysis (Assumptions table + Impact Summary + Calculation Detail for all 3 scenarios), Assumptions & Risks, Reducing Uncertainty (with confidence level + validation recommendation), Appendix: Sources.
**Fail:** Any required section is missing or contains only a header with no content.
**Check type:** Code-based

```check
Type: structural
Source field: N/A
Target field: Output report — markdown headers
Logic:
  (1) Parse the report for ## headers.
  (2) Verify each required section exists: "TL;DR", "Problem Context", "Benchmarks", "Hims Scale Data", "Scenario Analysis", "Assumptions & Risks" (or "Assumptions and Risks"), "Reducing Uncertainty", "Appendix: Sources" (or "Appendix").
  (3) For each section, verify it contains at least one non-empty line of content (not just a header followed by another header or EOF).
  (4) Within "Scenario Analysis", verify sub-sections exist: "Assumptions" (with a markdown table), "Impact Summary" (with a markdown table), and three "Calculation Detail" blocks (Low, Base, High — each with a code fence containing calculation steps).
  (5) Within "Benchmarks", verify a "Source Quality" line exists.
  (6) If an SME-Sourced Assumptions section exists, verify it either has a populated table OR an explicit "No SME inputs" statement.
  (7) Any missing section or empty section = Fail.
```

**Source:** Derived from the Phase 8 output report template structure
**Added:** 2026-06-01
**Notes:** Functionally identical to step-level eval S11, which runs at Phase 8 before QA. If S11 passed at Phase 8, G3 should auto-pass unless Phase 8.5 coherence fixes inadvertently broke structure — a regression G3 would catch. The most common failure mode is a missing "Reducing Uncertainty" section or an SME section with neither content nor an explicit "none" statement.

---

### G4: Correct addressable base

**Pass:** When `cost_type == labor_only` AND the model uses a percentage-of-cost-pool pattern: the sheet's TPH Variance tab contains a Labor Base Buildup section showing `addressable_labor + non_labor_variable = total_variable_cost`. When the model uses a direct FTE-elimination or cycle-time-reduction pattern: the buildup is replaced with a one-line note explaining the model type.
**Fail:** A percentage-of-cost-pool model is missing the Labor Base Buildup in the TPH Variance tab, OR a direct model has a buildup table (unnecessary), OR the buildup math doesn't add up.
**Check type:** Code-based

```check
Type: structural + arithmetic
Source field: sizing_input.json — factors[].name (check for "addressable" or "annual_*_cost" pattern)
Target field: Sheet TPH Variance tab — Labor Base Buildup section (via MCP read_sheet_values)
Logic:
  (1) Read sizing_input.json. Check if any factor name contains "addressable" or matches "annual_*_cost" pattern — this indicates a percentage-of-cost-pool model.
  (2) If percentage-of-cost-pool pattern detected: read TPH Variance tab via MCP read_sheet_values. Verify it contains a "Labor Base Buildup" section with rows that sum to a total. Check that the total matches the D&F_Summary Variable Cost figure (within 5%).
  (3) If no percentage-of-cost-pool pattern (e.g., direct FTE elimination, cycle-time reduction): verify the TPH Variance tab does NOT have a buildup section, or has a one-line note explaining the model type (e.g., "Direct headcount model" or "Cycle-time-reduction model").
  (4) If the model pattern is ambiguous, WARN (not FAIL).
```

**Source:** Derived from Must-Fix #4 (cost type classification) and the Phase 8 reconciliation template
**Added:** 2026-06-01 | **Updated:** 2026-06-16 (reworked for sheet-only architecture)
**Notes:** The reconciliation requirement was added after the Building Health Dashboard sizing conflated $18M Variable Cost with $13M productive labor. This eval prevents that class of error from recurring. The Labor Base Buildup now lives in the TPH Variance tab instead of a markdown report section.

---

### G5: Scenario ordering and transparency

**Pass:** (a) For every variable factor in the Assumptions table, Low < Base < High values are in ascending order. (b) All three Calculation Detail sections (Low, Base, High) are present and contain the full factor multiplication chain.
**Fail:** Any variable factor has Low ≥ Base or Base ≥ High (inverted ordering), OR any Calculation Detail section is missing or truncated.
**Check type:** Code-based

```check
Type: comparison + structural
Source field: Output report — Assumptions table, Calculation Detail sections
Target field: N/A (self-consistency check)
Logic:
  (1) Parse the Assumptions table. For each row where Type = "variable" (or the row has distinct Low/Base/High values): extract Low (col C), Base (col D), High (col E) as numbers.
  (2) Verify Low < Base < High for each variable factor. If any inversion = Fail.
  (3) Verify three Calculation Detail sections exist (one for each scenario: Low, Base, High).
  (4) Each Calculation Detail section must contain a code fence with at least one line showing factor multiplication (the "Formula:" line from sizing_calculator.py output).
  (5) Verify the final result in each Calculation Detail matches the corresponding value in the Impact Summary table (within 0.5% tolerance).
```

**Source:** Derived from scenario construction rule #4 ("Low < Base < High — Every variable factor must satisfy this ordering")
**Added:** 2026-06-01
**Notes:** Inversions are rare but catastrophic — they make the Low scenario look better than High, which confuses every stakeholder who reads the report. The transparency check (Calculation Detail completeness) ensures the "show your work" principle is maintained.

---

### G6: Research gate question asked

**Pass:** The sheet's Benchmarks tab contains either: (a) at least one data row with research sources (indicating research was run), OR (b) explicit text indicating research was skipped (e.g., "External research skipped", "research skipped per gate decision").
**Fail:** The Benchmarks tab is empty with no explanation, OR contains benchmarks but with no indication that the research gate decision was made.
**Check type:** Code-based

```check
Type: presence
Source field: Sheet Benchmarks tab (via MCP read_sheet_values)
Target field: N/A
Logic:
  (1) Read the Benchmarks tab via MCP read_sheet_values.
  (2) Check if it contains at least one data row (row 2+) with non-empty cells (indicating research was run) = Pass.
  (3) OR check if any cell contains text matching patterns like "research skipped", "External research skipped", "gate decision", "no external research" (indicating explicit skip) = Pass.
  (4) If neither populated data rows nor skip language is found = Fail.
```

**Source:** Derived from Phase 2.5 ALWAYS constraint ("Present a research gate recommendation")
**Added:** 2026-06-01 | **Updated:** 2026-06-16 (reworked for sheet-only architecture)
**Notes:** This is a gate evidence check — the Phase 11 trace subagent independently corroborates it in `gate_evidence.research_gate`. The eval doesn't check WHETHER research should have been run (that's a judgment call) — only that the gate decision was explicitly made and documented.

---

### G7: SME assumption elicitation occurred

**Pass:** The sheet's SME Inputs tab exists and contains either: (a) at least one data row with SME input data, OR (b) a "No SME inputs provided" row (the tab is always created — this row indicates the gate was reached but no inputs were given).
**Fail:** The SME Inputs tab does not exist, OR the tab exists but is empty (no data rows and no "No SME inputs" placeholder).
**Check type:** Code-based

```check
Type: presence
Source field: Sheet SME Inputs tab (via MCP read_sheet_values)
Target field: N/A
Logic:
  (1) Verify the SME Inputs tab exists via get_spreadsheet_info. Tab missing = Fail.
  (2) Read the SME Inputs tab via MCP read_sheet_values.
  (3) Check if it contains at least one data row (row 2+) with non-empty cells = Pass (SME inputs were captured).
  (4) OR check if any cell contains text matching "No SME inputs", "no SME inputs provided", "none provided" = Pass (gate was reached, no inputs given).
  (5) If the tab exists but has only a header row with no data and no placeholder text = Fail.
```

**Source:** Derived from Phase 1.5 ALWAYS constraint ("Ask the user explicitly for SME-sourced assumptions")
**Added:** 2026-06-01 | **Updated:** 2026-06-16 (reworked for sheet-only architecture)
**Notes:** This is a gate evidence check — the Phase 11 trace subagent independently corroborates it in `gate_evidence.sme_elicitation`. Like G6, this checks that the step happened, not that the right decision was made. The SME Inputs tab is now always created — if no SME inputs were provided, it has a "No SME inputs provided" row.

---

### G8: Human review gate evidence

**Pass:** The sheet's Assumptions tab exists and has columns for Variable/Factor, Low, Base, High (and optionally Source/Rationale), with at least one data row.
**Fail:** No Assumptions tab exists, OR the tab has no data rows, OR it's missing the Low/Base/High columns.
**Check type:** Code-based

```check
Type: structural
Source field: Sheet Assumptions tab (via MCP read_sheet_values)
Target field: N/A
Logic:
  (1) Verify the Assumptions tab exists via get_spreadsheet_info. Tab missing = Fail.
  (2) Read the Assumptions tab header row via MCP read_sheet_values on Assumptions!A1:G1.
  (3) Verify the header row contains "Variable" (or "Factor"), "Low", "Base", "High" columns.
  (4) Read Assumptions!A2:A[last] to verify at least one data row exists.
  (5) If any of (1-4) fail = Fail.
```

**Source:** Derived from Phase 6 MANDATORY constraint ("Do NOT skip. Do NOT proceed to calculation without user confirmation.")
**Added:** 2026-06-01 | **Updated:** 2026-06-16 (reworked for sheet-only architecture)
**Notes:** This is a gate evidence check — the Phase 11 trace subagent independently corroborates it in `gate_evidence.review_gate`. The Assumptions tab IS the artifact that proves the review gate was presented. Without it, there's no evidence the user confirmed before calculation.

---

### G9: Phase 9 Google Sheet built

**Pass:** The report's TL;DR section contains a Google Sheets URL (indicating the interactive model was built). The URL points to a valid spreadsheet.
**Fail:** No Google Sheets URL appears in the report's TL;DR section, or the URL is malformed.
**Check type:** Code-based (presence check)

```check
Type: presence
Source field: Output report — TL;DR section
Target field: N/A
Logic:
  (1) Find the "TL;DR" section in the report.
  (2) Search for a URL matching pattern "(internal link)".
  (3) If found = Pass. If not found = Fail.
```

**Source:** Derived from Phase 9 instruction ("Include the sheet URL in the report's TL;DR section")
**Added:** 2026-06-01 | **Updated:** 2026-06-15 (Phase 9 now mandatory — changed from "offer" to "built")
**Notes:** Previously an LLM judge checking whether the skill offered to build the sheet. Now a code-based check verifying the sheet was actually built and linked, since Phase 9 is mandatory.

---

### G10: All active evals scored

**Pass:** The trace file's `eval_results` array contains one entry for every eval ID in the Active Evals table (G-series), AND the trace file's `step_evals` array contains one entry for every eval ID in the Step-Level Evals table (S-series), at the time of the run.
**Fail:** Any G-series eval ID is missing from `eval_results`, or any S-series eval ID is missing from `step_evals`.
**Check type:** Code-based (comparison)

```check
Type: comparison
Source field: evals.md — Active Evals table ID column (G-series) + Step-Level Evals table ID column (S-series)
Target field: Trace file (observability/traces/*.json) — eval_results[].eval_id (G-series) + step_evals[].eval_id (S-series)
Logic:
  (1) Parse evals.md Active Evals table and extract the set of all non-retired G-series IDs (expected: {G1, G2, G4, G6, G7, G8, G10, G11, G12}).
  (2) Parse evals.md Step-Level Evals table and extract the set of all S-series IDs (e.g., {S1, S2, ..., S13}).
  (3) Parse the most recent trace file's eval_results array and extract all eval_id values → g_scored.
  (4) Parse the most recent trace file's step_evals array and extract all eval_id values → s_scored.
  (5) Compute g_missing = g_series_ids - g_scored. Compute s_missing = s_series_ids - s_scored.
  (6) Exception: If research was skipped (Phase 2.5 → SKIP), S1, S2, S5, S6, S24, S25, S26, and S28 are expected to be absent — exclude them from s_missing.
  (7) If the trace file has no step_evals array (pre-wiring runs), skip the S-series check entirely — S-series checking is gated on the trace schema update that adds step_evals support.
  (8) If g_missing is empty AND s_missing is empty = Pass. Otherwise = Fail. Report which specific IDs were not scored.
```

**Source:** Observed failure in Auto-Divert + Auto-Stage run (2026-06-01) — G6, G7, G8 existed in evals.md but were not scored in the trace's eval_results. Phase 10 should run ALL active evals.
**Added:** 2026-06-01 | **Updated:** 2026-06-15 (expanded to cover S-series step-level evals)
**Notes:** This is a meta-eval — it checks the eval runner itself. **Must run last within Phase 10** — if it runs before other G-evals complete, it will false-fail on the not-yet-scored evals. The most common failure mode is adding new evals to evals.md mid-session and the eval runner only scoring the subset it saw at load time. The S-series exception for skipped research prevents false failures when Phases 3 and 5 are conditionally bypassed.

---

### G11: Impact mechanism validated

**Pass:** The sheet's README tab row 11 (Problem Context) correctly describes the mechanism by which the feature improves the metric. The described mechanism is factually accurate (e.g., correctly identifies which steps are automated vs. still manual), AND the calculator factors are consistent with that mechanism (e.g., if the mechanism says "removes labeling time," the factors include a labeling-time-savings variable, not a headcount-elimination variable).
**Fail:** The Problem Context in README row 11 misattributes what the feature automates or changes (e.g., claims it automates packing when it automates post-pack steps), OR the calculator factors don't match the described mechanism (e.g., mechanism describes cycle-time savings but factors model FTE elimination), OR the mechanism was corrected mid-run by the user rather than validated proactively by the skill.
**Check type:** LLM judge (requires understanding whether the described mechanism matches how the feature actually works — factual/reasoning check that code cannot assess)

```judge
Criterion: Does the sheet's README tab row 11 (Problem Context) correctly and accurately describe HOW the feature improves the metric? Is the mechanism factually accurate, and are the calculator factors consistent with that mechanism?
Pass: The Problem Context accurately describes which steps are automated vs. manual, the causal chain from feature to metric improvement is sound, and the calculator factors (names, units, structure) align with what the mechanism describes.
Fail: The Problem Context misattributes what the feature automates (e.g., claims it replaces a human step that is still manual), OR the calculator factors don't match the described mechanism (structural inconsistency), OR the mechanism required user correction during the run (indicating the skill didn't validate proactively per Phase 2).
```

**Source:** Observed in Slam-Line Automation run (2026-06-02) — the skill initially framed SLAM as automating packing itself. The user had to request a web search to validate; research confirmed SLAM automates post-pack steps (scan, label, apply, manifest), not packing. The skill corrected course but only after user intervention. Phase 2 clearly requires mechanism validation before proceeding.
**Added:** 2026-06-03 | **Updated:** 2026-06-16 (reworked for sheet-only architecture)
**Notes:** This is inherently a judgment call. Code can verify structural consistency (do factor names match mechanism keywords?) but cannot assess factual correctness. An LLM judge with access to the research chunks and the sheet's README can assess whether the mechanism described aligns with what the benchmarks describe. The "corrected mid-run by user" criterion is assessable from conversation context but not from artifacts alone — trace the conversation for user messages like "I thought a human still..." or mechanism-correction patterns.

---

## Step-Level Eval Definitions

Step-level evals (S-series) run mid-pipeline as part of the self-correction loop. After each critical phase produces output, the orchestrator validates against the relevant S-evals. On FAIL: self-correct → re-validate → escalate if still failing (max 1 correction attempt per phase).

**Conditional evals:** S1, S2, S5, S6, S24, S25, S26, and S28 only run when research is conducted (Phase 2.5 → RUN). When research is skipped, these evals are skipped and excluded from the G10 completeness check.

---

### S1: Research output schema validity

**Phase:** 3 (Research)
**Pass:** Research Agent output is a valid JSON array where every item has non-null `source_title` (string), `url` (string), `improvement_value` (number), and `exact_quote` (string). OR output is `{"benchmarks": [], "pipeline_error": "..."}` (valid error format).
**Fail:** Output is not valid JSON, or any item is missing a required field, or field types are wrong (e.g., `improvement_value` is a string instead of number).
**Check type:** Code-based (schema validation)

```check
Type: structural
Source field: Research Agent output (JSON)
Target field: N/A (self-consistency check)
Logic:
  (1) Parse output as JSON. If parse fails = Fail.
  (2) If output is an object with "benchmarks" key (empty array) and "pipeline_error" key = Pass (valid error format).
  (3) If output is an array, for each item verify: source_title (string, non-null), url (string, non-null), improvement_value (number, non-null), exact_quote (string, non-null). Any violation = Fail.
  (4) Empty array [] with no pipeline_error = Pass (no benchmarks found, but format is valid).
```

**Source:** Derived from subagent-contracts.md Research Agent output validation
**Added:** 2026-06-15
**Self-correction:** On FAIL, re-prompt Research Agent with: "Output failed schema validation: [specific error]. Return the corrected JSON array."

---

### S2: Research quote-value alignment

**Phase:** 3 (Research)
**Pass:** For every benchmark item in the Research Agent output, the `improvement_value` (as number or formatted string) appears as a substring or semantic equivalent within `exact_quote`.
**Fail:** Any item's `improvement_value` does not appear in its `exact_quote` in any recognizable format.
**Check type:** Code-based (substring match with format normalization)

```check
Type: presence
Source field: Research Agent output — each item's improvement_value
Target field: Same item's exact_quote
Logic:
  (1) For each benchmark item, extract improvement_value (e.g., 0.12).
  (2) Generate normalized format variants: "12%", "12 percent", "12%", "0.12", "12 per cent". For absolute values: "$X", "X dollars", "$X.XX". For time: "X minutes", "X hours", "X seconds".
  (3) Check if ANY variant appears as a substring in exact_quote (case-insensitive).
  (4) If no variant found in the quote = Fail for that item. Report: "Benchmark from [source_title]: claimed [improvement_value] not found in quote."
  (5) Overall: all items pass = Pass. Any item fails = Fail.
```

**Source:** Derived from NEVER constraint #2 ("Cite a benchmark number that isn't directly quoted from a research chunk") — applied at the point of origin (Phase 3) rather than end-of-run
**Added:** 2026-06-15
**Self-correction:** On FAIL, re-prompt Research Agent with: "Benchmark #N from [source_title] claims [value] but the exact_quote doesn't contain it. Re-extract the correct quote containing that number, or drop the benchmark if the number isn't in the source."
**Notes:** This is the step-level precursor to G2. Catching fabrication here prevents it from polluting scenarios downstream. If S2 passes but G2 later fails, the drift was introduced during orchestrator extraction (Phase 5) or sheet construction (Phase 8) — a different failure mode.

---

### S3: Scale data schema and completeness

**Phase:** 4 (Scale Data)
**Pass:** Scale Data Agent output matches the schema in subagent-contracts.md: `metric_category` matches the requested category, `volumes.annual_total` is non-null and > 0, `baselines.primary_metric` is non-null, and `conflicts` is an array (even if empty).
**Fail:** `metric_category` mismatch, null or zero `volumes.annual_total`, null `baselines.primary_metric`, or `conflicts` field missing.
**Check type:** Code-based (schema + null check)

```check
Type: structural
Source field: Scale Data Agent output (JSON)
Target field: Requested metric_category from Phase 1 intake
Logic:
  (1) Parse output as JSON. If parse fails = Fail.
  (2) Verify output.metric_category matches the requested metric_category (exact string match). Mismatch = Fail.
  (3) Verify output.volumes.annual_total is non-null and > 0. Null or ≤ 0 = Fail.
  (4) Verify output.baselines.primary_metric is non-null (has at least value and unit). Null = Fail.
  (5) Verify output.conflicts exists and is an array (empty array is valid). Missing = Fail.
  (6) If metric_category == "labor_cost": verify output.labor_data is non-null. Null = Fail.
  (7) If output.volumes.by_site exists and has ≥2 entries: verify sum(by_site values) is within 5% of output.volumes.annual_total. Divergence > 5% = Fail ("Site-level volumes don't sum to annual total — possible cross-source inconsistency").
```

**Source:** Derived from subagent-contracts.md Scale Data Agent output validation
**Added:** 2026-06-15
**Self-correction:** On FAIL, re-prompt Scale Data Agent with the specific failure and the raw sheet data again: "Output failed validation: [specific error]. Re-structure the data with the correct [field]."

---

### S4: Scale data range reasonableness

**Phase:** 4 (Scale Data)
**Pass:** All numeric values in the Scale Data Agent output fall within expected ranges from the Physical Limits Reference Table and QG Check 2 ranges.
**Fail:** Any value is negative, zero when it shouldn't be, or > 5× outside expected range.
**Check type:** Code-based (range validation)

```check
Type: comparison
Source field: Scale Data Agent output — all numeric values in baselines and labor_data
Target field: Expected ranges (hardcoded from data-sources.md Physical Limits Table + QG Check 2)
Logic:
  (1) Extract all numeric values from baselines.primary_metric.value, baselines.by_step[].uph, baselines.by_step[].hourly_rate, labor_data fields, volumes.annual_total, volumes.by_site values.
  (2) For each value, check against the expected range for its type:
      - TPH (any role): 10–55. Pharmacist TPH: 60–90.
      - Variable cost per fill: $3.50–$5.00.
      - Pack associate hourly rate: $25–$32.
      - Pharmacist hourly rate: $90–$110.
      - Annual volume per site: 2M–8M (OH ~5M, AZ ~4M at FY26 scale; below 2M likely partial/weekly read, above 8M likely multi-site total).
  (3) If value is negative or zero (when > 0 expected) = Fail.
  (4) If value is > 5× outside expected range boundary = Fail.
  (5) If value is 1–5× outside = WARN (log but don't fail — may be valid edge case).
  (6) Overall: any Fail-severity violation = Fail. WARN-only = Pass with warnings.
```

**Source:** Derived from QG Check 2 (Scale Data Reasonableness) ranges — applied at Phase 4 before scenario construction to enable earlier self-correction
**Added:** 2026-06-15
**Self-correction:** On FAIL, orchestrator re-reads the specific sheet range that produced the anomalous value. If the re-read returns the same value, it's likely real data — escalate to user: "Scale data value [X] for [metric] is outside expected range. Is this correct?"
**Notes:** Overlaps with QG Check 2 but runs one full phase earlier. Catching bad data here saves a full cycle through scenario construction and QG validation.

---

### S5: Extraction completeness and traceability

**Phase:** 5 (Benchmark Extraction)
**Pass:** Every extracted benchmark in `extracted_benchmarks.json` has all 8 fields populated (non-null, non-empty). Every `url` matches an entry in `VERIFIED_URLS.md`. Every `tier` is one of A/B/C. Every `applicability_to_hims` has a rating (HIGH/MEDIUM/LOW) AND a non-empty explanation string.
**Fail:** Any field is null/empty, any URL not in `VERIFIED_URLS.md`, any tier not A/B/C, or applicability has no explanation.
**Check type:** Code-based (field presence + enum validation + URL cross-reference)

```check
Type: presence + comparison
Source field: $ARTIFACT_DIR/extracted_benchmarks.json — each record's 8 fields
Target field: VERIFIED_URLS.md (for URL cross-reference), enum sets for tier and applicability
Logic:
  (1) Parse extracted_benchmarks.json. If parse fails = Fail.
  (2) For each record, verify 8 required fields are non-null and non-empty: source_title, url, tier, improvement_type, improvement_value, exact_quote, context, applicability_to_hims. Any null/empty = Fail for that record.
  (3) For each record, verify url appears in VERIFIED_URLS.md (substring match against the URL list). Not found = Fail.
  (4) For each record, verify tier ∈ {"A", "B", "C"}. Invalid = Fail.
  (5) For each record, verify applicability_to_hims starts with "HIGH", "MEDIUM", or "LOW" and has additional explanation text after the rating. Rating-only with no explanation = Fail.
  (6) Overall: all records pass = Pass. Any record fails = Fail. Report which records and fields failed.
```

**Source:** Derived from Phase 5.2 extraction requirements + P3 specification fix (artifact output format)
**Added:** 2026-06-15
**Self-correction:** On FAIL, re-extract the failing benchmark(s) with specific feedback: "Benchmark from [source]: [field] is [null/invalid/missing]. Re-extract from the research chunk, or drop if the data isn't available."
**Notes:** Depends on the P3 specification fix that defines the `extracted_benchmarks.json` artifact format. Without the artifact, there's nothing for this eval to check.

---

### S6: Extraction accuracy — value-in-quote

**Phase:** 5 (Benchmark Extraction)
**Pass:** For every extracted benchmark in `extracted_benchmarks.json`, `improvement_value` appears in `exact_quote` (substring match with format normalization).
**Fail:** Any benchmark's value not found in its quote.
**Check type:** Code-based (substring match — identical to S2 implementation)

```check
Type: presence
Source field: $ARTIFACT_DIR/extracted_benchmarks.json — each record's improvement_value
Target field: Same record's exact_quote
Logic: Identical to S2 logic, applied to the orchestrator's extraction output instead of the Research Agent's raw output. See S2 check implementation for the normalization and matching steps.
```

**Source:** Derived from NEVER constraint #2 — applied at the orchestrator's extraction step (Phase 5.2), not just the Research Agent's output (Phase 3)
**Added:** 2026-06-15
**Self-correction:** On FAIL, re-extract the failing benchmark from the original research chunk. If the value genuinely isn't in the quote, drop the benchmark.
**Notes:** Deliberate redundancy with S2. S2 catches the Research Agent; S6 catches the orchestrator's extraction. If S2 passes and S6 fails, the orchestrator introduced drift during extraction — a clear signal for the self-correction loop. This is the step-level precursor to end-of-run G2 (which catches drift introduced during sheet construction in Phase 8).

---

### S7: Quality Gate Validator output integrity

**Phase:** 5.5 (Quality Gate)
**Pass:** QG Validator output has a `checks` array with exactly 10 items. Each item has `result` matching PASS, WARN, or FAIL. `summary.pass_count + summary.warn_count + summary.fail_count == 10`. `summary.blocking` is `true` if and only if any check result is FAIL.
**Fail:** Fewer or more than 10 checks, any missing `result`, counts don't sum to 10, or `blocking` flag contradicts check results.
**Check type:** Code-based (structural + arithmetic)

```check
Type: structural + arithmetic
Source field: Quality Gate Validator output (JSON)
Target field: N/A (self-consistency check)
Logic:
  (1) Parse output as JSON. If parse fails = Fail.
  (2) Verify output.checks is an array with length == 10. Wrong count = Fail.
  (3) For each check in output.checks: verify check.result ∈ {"PASS", "WARN", "FAIL"}. Invalid = Fail.
  (4) Count results: pass_count = count where result == "PASS", warn_count = count where result == "WARN", fail_count = count where result == "FAIL".
  (5) Verify output.summary.pass_count == pass_count, summary.warn_count == warn_count, summary.fail_count == fail_count. Mismatch = Fail.
  (6) Verify pass_count + warn_count + fail_count == 10. Sum ≠ 10 = Fail.
  (7) Compute expected_blocking = (fail_count > 0). Verify output.summary.blocking == expected_blocking. Mismatch = Fail.
```

**Source:** Derived from subagent-contracts.md Quality Gate Validator output validation
**Added:** 2026-06-15
**Self-correction:** On FAIL, re-prompt QG Validator with: "Output failed integrity check: [specific error — e.g., 'only 8 checks returned' or 'summary counts don't add up']. Re-run all 10 checks and return the corrected report."
**Notes:** This checks the validator's *format*, not its *findings*. S8 checks the findings. Both must pass before the orchestrator acts on the QG results.

---

### S8: Quality Gate — zero blocking failures

**Phase:** 5.5 (Quality Gate)
**Pass:** All 10 QG checks return PASS or WARN. `summary.blocking == false`.
**Fail:** Any check returns FAIL (`summary.blocking == true`).
**Check type:** Code-based (field check)

```check
Type: presence
Source field: Quality Gate Validator output — summary.blocking
Target field: N/A
Logic:
  (1) Read output.summary.blocking.
  (2) If false = Pass. If true = Fail.
  (3) On Fail, extract the failing check(s): [check.id, check.name, check.detail, check.suggested_action] for each check where result == "FAIL".
```

**Source:** Derived from Phase 5.5 constraint: "FAIL checks are blocking"
**Added:** 2026-06-15
**Self-correction:** On FAIL, the orchestrator reads the failing check's `suggested_action` and applies the fix:
- Check 5 (Physical plausibility) → reduce High scenario assumption to below ceiling
- Check 6 (Addressable base) → narrow scope or reduce improvement assumptions
- Check 9a (Scenario consistency) → fix Low/Base/High ordering
- Check 9b (Double-counting) → separate overlapping factors
- Check 10 (Factor redundancy) → remove the redundant variable factor
Then re-run the QG Validator. If still FAIL → escalate to user (existing Phase 5.5 behavior).
**Notes:** Not all FAILs are self-correctable. Checks 1 (quote accuracy), 2 (data reasonableness), 3 (data freshness), 4 (conflict verification), 7 (source quality), and 8 (SME-benchmark alignment) typically require user input to resolve. The self-correction loop should only attempt mechanical fixes; ambiguous ones go to the user.

---

### S9: Calculator input schema validity

**Phase:** 7.1 (Calculator Input)
**Pass:** Valid JSON with required top-level fields (`feature_name`, `metric_category`, `factors[]`, `result_label`). Each factor has `name` and `is_constant`. Constant factors have `value` (number). Variable factors have `low`, `base`, `high` (all numbers) with `low < base < high`. Every `labor_cost` constant factor has a `derivation` field with valid `method` (sum or formula). If `per_unit_divisor` exists, it is a positive number within a reasonable range for the metric category.
**Fail:** Missing required field, type mismatch, variable factor with inverted ordering (low ≥ base or base ≥ high), `labor_cost` constant missing derivation, or `per_unit_divisor` is zero/negative/outside expected range.
**Check type:** Code-based (schema + ordering validation)

```check
Type: structural + comparison
Source field: $ARTIFACT_DIR/sizing_input.json
Target field: N/A (self-consistency + schema check)
Logic:
  (1) Parse sizing_input.json. If parse fails = Fail.
  (2) Verify top-level fields exist: feature_name (string), metric_category (string), factors (array, length ≥ 1), result_label (string). Any missing = Fail.
  (3) For each factor in factors[]:
      a. Verify name (string, non-empty) and is_constant (boolean) exist. Missing = Fail.
      b. If is_constant == true: verify value (number) exists. Missing = Fail.
      c. If is_constant == false: verify low, base, high (all numbers) exist. Missing = Fail. Verify low < base < high. Inversion = Fail.
  (4) If metric_category == "labor_cost": for each constant factor, verify derivation field exists with method ∈ {"sum", "formula"}. Missing derivation = Fail.
  (5) If derivation.method == "sum": verify components[] exists with ≥1 item, each having name (string) and value (number).
  (6) If derivation.method == "formula": verify formula (string), compute (string), and inputs (object with ≥1 numeric value) exist.
  (7) If top-level per_unit_divisor field exists:
      a. Verify it is a number > 0. Zero or negative = Fail ("per_unit_divisor is [value] — division by zero or negative").
      b. Verify it falls within a reasonable range for the metric category:
         - Shipment-based (labor_cost, shipping_cost, fulfillment_cost): 2M–15M (Hims FY26 scale)
         - Quality/turnaround: no range constraint (context-dependent)
      c. Value outside range = Fail ("per_unit_divisor [value] outside expected range for [metric_category]").
```

**Source:** Derived from Phase 7.1 input construction rules + NEVER constraint #22 + per_unit_divisor validation gap
**Added:** 2026-06-15
**Self-correction:** On FAIL, fix the specific JSON error (add missing field, correct ordering, add derivation) and re-validate. Most common fixes: adding `derivation` to a constant the orchestrator forgot to derive, and fixing Low/Base/High inversions from copy-paste errors.

---

### S10: Factor independence (no double-counting)

**Phase:** 7.1 (Calculator Input)
**Pass:** Every variable factor in the calculator input represents an independent lever not already captured in any constant factor's `derivation.components` or `derivation.inputs`. No (variable, constant) pair shares a scope, adoption, or volume constraint.
**Fail:** A variable factor (e.g., `adoption_rate`) is conceptually redundant with a component or input in a constant's derivation (e.g., per-leg volume percentages that represent the automatable share).
**Check type:** LLM judge (semantic overlap detection requires understanding what factor names/descriptions *mean* — code can check name-level overlap but cannot assess conceptual redundancy like "is `adoption_rate` redundant with `40% of 79201 totes` in a derivation component?")

```judge
Criterion: Is every variable factor in the calculator input JSON independent of every constant factor's derivation components/inputs?

Pass: Each variable factor represents a distinct lever. No constant factor's derivation.components[].name or derivation.inputs keys contain a scope, adoption, or volume constraint that the variable factor also represents. The variable factor adds a genuinely new dimension to the multiplicative model.

Fail: A variable factor duplicates a constraint already embedded in a constant's derivation — applying it as a separate multiplier double-counts the effect. Examples: (1) a constant built from per-leg volume percentages + a separate adoption_rate variable, (2) a constant scoped to internal sites + a separate site_adoption_rate excluding 3PLs, (3) a constant embedding an "automatable share" + a separate automation_adoption variable.
```

**Source:** Derived from Phase 7.1 Factor Redundancy Check protocol (P2 specification fix) + QG Check 10
**Added:** 2026-06-15
**Self-correction:** On FAIL, remove the redundant variable factor and add a design decision note to the Assumptions tab Source/Rationale column. Re-validate to confirm no remaining redundancy.
**Notes:** Overlaps with QG Check 10 but runs earlier — on the JSON before the calculator executes. QG Check 10 runs on proposed scenarios; S10 runs on constructed input. Catching here prevents the calculator from producing an inflated result that the QG would then flag.

---

### S11: Report structural completeness

**Phase:** 8 (Report Synthesis)
**Pass:** Report contains all required `##` sections with non-empty content: TL;DR, Problem Context, Benchmarks (with Source Quality summary line), Hims Scale Data, Scenario Analysis (with Assumptions table + Impact Summary + Calculation Detail for all 3 scenarios), Assumptions & Risks, Reducing Uncertainty (with confidence level + validation recommendation), Appendix: Sources. If SME-Sourced Assumptions section exists, it has either a populated table or explicit "No SME inputs" statement.
**Fail:** Any required section missing or empty (header followed immediately by another header or EOF).
**Check type:** Code-based (structural — markdown header parsing)

```check
Type: structural
Source field: Output report (markdown)
Target field: N/A
Logic:
  (1) Parse the report for ## headers.
  (2) Verify each required section exists: "TL;DR", "Problem Context", "Benchmarks", "Hims Scale Data", "Scenario Analysis", "Assumptions & Risks" (or "Assumptions and Risks"), "Reducing Uncertainty", "Appendix: Sources" (or "Appendix").
  (3) For each section, verify it contains at least one non-empty line of content (not just a header followed by another header or EOF).
  (4) Within "Scenario Analysis", verify sub-sections exist: "Assumptions" (with a markdown table), "Impact Summary" (with a markdown table), and three "Calculation Detail" blocks (Low, Base, High — each with a code fence containing calculation steps).
  (5) Within "Benchmarks", verify a "Source Quality" line exists.
  (6) If an "SME-Sourced Assumptions" section exists, verify it either has a populated table OR explicit "No SME inputs" text.
  (7) Any missing section or empty section = Fail.
```

**Source:** Derived from Phase 8 output report template structure — identical to G3 implementation, applied at Phase 8 for earlier self-correction
**Added:** 2026-06-15
**Self-correction:** On FAIL, add the missing section(s) using the Phase 8 report template structure. Re-validate to confirm all sections present.
**Notes:** Functionally identical to end-of-run G3. Running at Phase 8 means structural gaps are fixed before Phase 8.5's cross-section coherence check and Phase 10's end-of-run evals.

---

### S12: Report-calculator number consistency

**Phase:** 8 (Report Synthesis)
**Pass:** Every dollar figure, percentage, and per-unit value in the report's TL;DR, Scenario Analysis, and Hims Scale Data sections matches a value in `sizing_output.json` (within 0.5% rounding tolerance) OR is immediately preceded by a cited raw data source.
**Fail:** Any report number not traceable to calculator output or a cited source.
**Check type:** Code-based (comparison)

```check
Type: comparison
Source field: $ARTIFACT_DIR/sizing_output.json — all values from scenarios[].result, scenarios[].per_unit_result, scenarios[].factors_used[].value
Target field: Output report — all dollar-formatted numbers ($X,XXX or $X.XM) and percentages from ## TL;DR, ## Scenario Analysis, and ## Hims Scale Data sections
Logic:
  (1) Parse sizing_output.json and build a set of all numeric values across all three scenarios. Normalize: strip $, commas, expand M/K suffixes.
  (2) Parse the report sections and extract all numeric values with the same normalization. Exclude numbers in section headers, dates, and non-metric references.
  (3) For each report number, check if it exists in the calculator output set (within 0.5% tolerance) OR is immediately preceded by a source citation (e.g., "Trans_Summary", "D&F TPH", "TPH Tracker", "Win Calculator", or a research source title).
  (4) Any report number not in either set = Fail.
```

**Source:** Derived from G1 check steps (1)–(4), applied at Phase 8 for earlier self-correction
**Added:** 2026-06-15
**Self-correction:** On FAIL, identify the mismatched number(s) and replace with the correct value from `sizing_output.json`. Re-validate.
**Notes:** This is the core of G1 (number consistency) without the structural signature check (which G1 retains as end-of-run). Running at Phase 8 catches transcription errors before Phase 8.5 QA, reducing QA findings.

---

### S13: Assumption attribution + README narrative completeness

**Phase:** 8 (Build Sheet)
**Pass:** (a) README tab row 12 (Key Assumptions & Risks) contains at least one `[Assumption: ...]` tag. (b) If SME Inputs tab has data rows (not just the "No SME inputs" placeholder), the Assumptions tab's Source/Rationale column (col G) contains at least one `[SME: ...]` tag.
**Fail:** README row 12 has no `[Assumption:` tags. SME data exists but no `[SME:` tags in Assumptions col G.
**Check type:** Code-based (MCP read + regex presence)

```check
Type: presence
Source field: Sheet README tab rows 11-15 (via read_sheet_values), Assumptions tab col G (via read_sheet_values), SME Inputs tab (via read_sheet_values)
Target field: N/A
Logic:
  (1) Read README!B12. Search for "[Assumption:" substring. Not found = Fail.
  (2) Read SME Inputs tab. If it has data rows (not just header + "No SME inputs" placeholder): read Assumptions!G2:G[last]. Search for "[SME:" substring. Not found = Fail.
  (3) Overall: all checks pass = Pass. Any violation = Fail.
```

**Source:** Derived from ALWAYS constraints + README tab expansion (rows 11-15 are the narrative content that replaced the markdown report)
**Added:** 2026-06-15 | **Updated:** 2026-06-16 (reworked for sheet-only architecture — checks sheet README and Assumptions tab instead of markdown report)
**Self-correction:** On FAIL, populate the empty README cells or add missing tags. For missing `[Assumption:]` tags in row 12: wrap each risk in the tag format. For missing `[SME:]` tags: add to the relevant Assumptions Source/Rationale cells.
**Notes:** This eval focuses on attribution tagging only. README rows 11-15 non-empty checks are owned by S21 (structural + numerical accuracy). The ownership split avoids duplicate self-correction for the same failure.

---

### S14: Scenarios cells are formulas (not static values)

**Phase:** 8 (Build Sheet)
**Pass:** Every data cell on the Scenarios tab (row 2+ in columns B, C, D) contains a formula starting with `=`. Zero cells contain static numeric values.
**Fail:** Any data cell in the Scenarios output area contains a literal number instead of a formula.
**Check type:** Code-based (formula inspection via MCP)

```check
Type: presence
Source field: Scenarios tab — all data cells (row 2+, columns B/C/D)
Target field: N/A
Logic:
  (1) Call read_sheet_values on Scenarios!A1:D30 with include_formulas: true.
  (2) Identify all data rows (row 2+) where column A has a non-empty label.
  (3) For each data cell in columns B, C, D of those rows: check if the formula field starts with "=".
  (4) Any non-empty cell that lacks a formula (contains a literal number) = Fail.
  (5) Exception: Section header rows (e.g., "DISPATCH BREAKDOWN") and blank separator rows are excluded.
```

**Source:** sheet-builder.md 9.3 Rules: "Outputs MUST be live formulas referencing Assumptions. Never paste static numbers."
**Added:** 2026-06-15
**Self-correction:** On FAIL, identify the static cells and rewrite them as formulas referencing the correct Assumptions cells per the row mapping. Re-validate.

---

### S15: Scenarios formula column references correct

**Phase:** 8 (Build Sheet)
**Pass:** In every Scenarios formula, references to constant-factor Assumptions rows use column D regardless of which scenario column the formula is in. References to variable-factor rows use column C in the Low scenario (Scenarios col B), column D in Base (Scenarios col C), column E in High (Scenarios col D).
**Fail:** A constant factor is referenced via column C or E. A variable factor uses the same column across all three scenarios instead of C/D/E.
**Check type:** Code-based (formula parsing via MCP)

```check
Type: comparison
Source field: Scenarios tab formulas (include_formulas: true) + Assumptions tab col A (Type: constant/variable)
Target field: N/A (self-consistency)
Logic:
  (1) Read Assumptions!A1:B[last] to build type map: {row_number: is_constant} for each data row.
  (2) Read Scenarios formulas with include_formulas: true.
  (3) For each formula, parse all cell references matching pattern Assumptions![A-Z][0-9]+.
  (4) For each reference, extract column letter and row number. Look up row in the type map.
  (5) If row is constant and column is C or E = Fail ("Constant factor in row [N] referenced via column [X] instead of D").
  (6) If row is variable: check Scenarios column context. Scenarios col B (Low) must reference Assumptions col C. Scenarios col C (Base) must reference Assumptions col D. Scenarios col D (High) must reference Assumptions col E. Mismatch = Fail.
```

**Source:** sheet-builder.md 9.3 Layout convention: "Constants reference column D in every scenario; variables reference C/D/E for Low/Base/High respectively."
**Added:** 2026-06-15
**Self-correction:** On FAIL, rewrite the offending formulas with correct column references. Re-validate.
**Notes:** This is the highest-stakes sheet eval. Wrong column references produce a sheet that *looks* like it recalculates but silently returns wrong numbers when stakeholders change assumptions — the Base value would update correctly but Low and High would not reflect the flexed input.

---

### S16: Scenarios Base matches calculator output

**Phase:** 8 (Build Sheet)
**Pass:** The computed value in Scenarios Base column (col C, Annual Impact row) matches `sizing_output.json` Base scenario `result` within $1 or 0.1%, whichever is larger.
**Fail:** Divergence exceeds the tolerance.
**Check type:** Code-based (numeric comparison via MCP + JSON)

```check
Type: comparison
Source field: read_sheet_values on Scenarios tab (computed values, NOT formulas)
Target field: sizing_output.json → base scenario → result
Logic:
  (1) Read Scenarios!A1:A20 to find the Annual Impact row (search for cell containing "Annual Impact"). Record its row number → impact_row.
  (2) Read the Base column value at Scenarios!C[impact_row] (without include_formulas — get computed result).
  (3) Read $ARTIFACT_DIR/sizing_output.json, extract scenarios.base.result.
  (4) Parse both as numbers (strip $ and commas).
  (5) Compute delta = abs(sheet_value - calculator_value).
  (6) Compute tolerance = max(1, abs(calculator_value) * 0.001).
  (7) If delta > tolerance = Fail. Report: "Sheet Base: $[X], Calculator Base: $[Y], Delta: $[Z], Tolerance: $[T], Row: [impact_row]."
  (8) If no "Annual Impact" row found in A1:A20 = Fail. Report: "No 'Annual Impact' row found on Scenarios tab."
```

**Source:** sheet-builder.md 8.5 verification step 1
**Added:** 2026-06-15
**Self-correction:** On FAIL, diagnose which factor formula is wrong by comparing each factor's Assumptions value against the calculator input. Fix the formula and re-validate.

---

### S17: Factor row order matches sizing_input.json

**Phase:** 8 (Build Sheet)
**Pass:** Column B (Factor names) on the Assumptions tab, from row 2 onward, lists factors in the exact order they appear in `sizing_input.json` `factors[]`, followed by `per_unit_divisor` (if present in the JSON). No factors missing, no extra factors, no reordering.
**Fail:** Factor order differs from `sizing_input.json`, any factor is missing, any unexpected factor appears, or divisor is interleaved with factors.
**Check type:** Code-based (ordered comparison via MCP + JSON)

```check
Type: comparison
Source field: read_sheet_values on Assumptions!B2:B[last]
Target field: sizing_input.json → factors[].name + per_unit_divisor (if present)
Logic:
  (1) Read Assumptions!B2:B20 to get factor label sequence (stop at first empty cell).
  (2) Read $ARTIFACT_DIR/sizing_input.json. Build expected sequence: [factors[0].name, factors[1].name, ..., "per_unit_divisor" if top-level per_unit_divisor field exists].
  (3) Compare sequences element-by-element. Order mismatch, missing element, or extra element = Fail.
  (4) Specifically check: divisor (if present) comes after ALL factors, never interleaved.
```

**Source:** sheet-builder.md 9.3: "Factors come first in the same order as factors[] in sizing_input.json... per_unit_divisor row goes immediately after the last factor row"
**Added:** 2026-06-15
**Self-correction:** On FAIL, rewrite the Assumptions tab rows in the correct order. This will also require rewriting all Scenarios formulas since row numbers will shift. Re-validate S14–S16 after correction.

---

### S18: Editable cells have yellow highlighting

**Phase:** 8 (Build Sheet)
**Pass:** On the Assumptions tab, every editable cell has yellow background (#FFF59D or equivalent): variable rows columns C, D, E; constant rows column D only. Non-editable cells (constant rows C/E, header row, all Scenarios cells) do NOT have yellow background.
**Fail:** Any editable cell lacks yellow highlighting, or any non-editable cell has yellow highlighting.
**Check type:** Code-based (format inspection)

```check
Type: presence
Source field: Spreadsheet formatting data for Assumptions tab
Target field: N/A
Logic:
  (1) Read Assumptions!A1:A[last] to identify constant vs variable rows.
  (2) For each variable row: check cells C, D, E have yellow background. Missing = Fail.
  (3) For each constant row: check cell D has yellow background. Cells C, E must NOT have yellow. Yellow on C or E = Fail.
  (4) Header row (row 1) must NOT have yellow background.
```

**Source:** sheet-builder.md 9.4: "Yellow background on editable cells in Assumptions"
**Added:** 2026-06-15
**Self-correction:** On FAIL, apply formatting via format_sheet_range to the correct cells. Re-validate.
**Notes:** MCP tool limitation: if `read_sheet_values` cannot return background color data, this eval must be checked manually or deferred. The eval subagent should attempt the check and, if formatting data is unavailable, return `"result": "Skip", "detail": "MCP does not expose background color data — manual check required"`. The orchestrator logs the Skip and does NOT count it as a failure. **First-run action:** test whether the Google Workspace MCP returns formatting data. If consistently unavailable, convert S18 to a manual checklist item in sheet-builder.md rather than burning subagent cycles on a guaranteed Skip.

---

### S19: Tab structure matches specification

**Phase:** 8 (Build Sheet)
**Pass:** The spreadsheet contains the required tabs in order. For `labor_cost`: README, Assumptions, Scenarios, TPH Variance, Benchmarks, SME Inputs (if SME data exists). For other metric categories: README, Assumptions, Scenarios, Benchmarks, SME Inputs (if SME data exists). No unexpected extra tabs.
**Fail:** Missing required tab, extra unexpected tab, wrong tab order, TPH Variance present for non-labor metric, or TPH Variance absent for labor_cost.
**Check type:** Code-based (structural via MCP)

```check
Type: structural
Source field: get_spreadsheet_info → sheet names and order
Target field: Expected tab list based on metric_category and SME data presence
Logic:
  (1) Call get_spreadsheet_info to get tab names in order.
  (2) Determine metric_category from sizing_input.json.
  (3) Build expected tab list:
      - Always: ["README", "Assumptions", "Scenarios"]
      - If metric_category == "labor_cost": append "TPH Variance" (or "TPH Context")
      - Always: append "Benchmarks"
      - If SME data was captured in Phase 1.5: append "SME Inputs"
  (4) Compare actual tab names to expected (case-insensitive, allow minor variants like "TPH Context" for "TPH Variance").
  (5) Missing required tab = Fail. Extra tab (other than auto-created "Sheet1") = Warn. Wrong order = Fail.
  (6) If metric_category != "labor_cost" and a TPH tab exists = Fail.
  (7) If metric_category == "labor_cost" and no TPH tab exists = Fail.
```

**Source:** sheet-builder.md 9.2 required tabs table
**Added:** 2026-06-15
**Self-correction:** On FAIL, create missing tabs or reorder existing ones via MCP. Re-validate.

---

### S20: Constants have blank Low/High columns

**Phase:** 8 (Build Sheet)
**Pass:** For every row on the Assumptions tab where column A = "constant", cells in columns C (Low) and E (High) are empty/blank.
**Fail:** Any constant row has a non-empty value in column C or E.
**Check type:** Code-based (value inspection via MCP)

```check
Type: presence
Source field: read_sheet_values on Assumptions!A1:E[last]
Target field: N/A
Logic:
  (1) Read Assumptions!A1:E[last].
  (2) For each data row (row 2+), read column A.
  (3) If column A == "constant": verify column C is empty/blank AND column E is empty/blank.
  (4) Non-empty value in C or E for a constant row = Fail. Report: "Constant factor [name] in row [N] has non-empty [Low/High] value: [value]."
```

**Source:** sheet-builder.md 9.3 Layout convention: "Constants — single value in Base column (D) only. Low (C) and High (E) cells stay blank."
**Added:** 2026-06-15
**Self-correction:** On FAIL, clear the offending cells. Re-validate.
**Notes:** This failure mode is subtle — a constant with values in Low/High columns would cause Scenarios formulas that correctly reference C/D/E for variables to accidentally pick up the constant's non-Base value, producing wrong Low/High scenario results.

---

### S21: README label-value alignment, formulas, and numerical accuracy

**Phase:** 8 (Build Sheet)
**Pass:** (a) README!A1:A15 contains exactly the 15 canonical labels in order. (b) Each B-column value is non-empty. (c) B6 is a formula starting with `=Scenarios!`. (d) B7 is a formula starting with `=` (live Range, not static string). (e) B8 is a formula starting with `=` (live Per-Shipment, not static). (f) B5 is one of HIGH/MEDIUM/LOW. (g) B3 is "Danny Pedrini". (h) B7 rendered values match `sizing_output.json` low.result and high.result within $1 or 0.1% tolerance. (i) B8 rendered value matches `sizing_output.json` base.per_unit_result within the same tolerance.
**Fail:** Any label missing, misordered, or wrong. Any B value empty. B6, B7, or B8 is static (no formula). B5 is not a valid confidence level. B7 or B8 rendered values don't match calculator output.
**Check type:** Code-based (structural + formula inspection + numeric comparison via MCP)

```check
Type: structural + presence + comparison
Source field: read_sheet_values on README!A1:B15 with include_formulas: true + sizing_output.json
Target field: Canonical label list + calculator values
Logic:
  (1) Read README!A1:B15 with include_formulas: true.
  (2) Define canonical labels: ["Feature", "Generated", "PM", "Metric Category", "Confidence", "Base Case Annual Impact", "Range", "Per-Shipment Impact (Base)", "How to Use", "Sources", "Problem Context", "Key Assumptions & Risks", "Validation Recommendation", "Confidence Rationale", "Next Step"].
  (3) Compare A1:A15 values to canonical labels in order. Mismatch = Fail.
  (4) Verify no B cell is empty. Empty = Fail.
  (5) Verify B6 formula field starts with "=Scenarios!" (live formula, not static). Missing formula = Fail.
  (6) Verify B7 formula field starts with "=" (live formula, not static string). Missing formula = Fail.
  (7) Verify B8 formula field starts with "=" (live formula, not static). Missing formula = Fail.
  (8) Verify B5 value ∈ {"HIGH", "MEDIUM", "LOW"}. Other = Fail.
  (9) Verify B3 == "Danny Pedrini". Other = Fail.
  (10) Read $ARTIFACT_DIR/sizing_output.json. Extract low.result, high.result, base.per_unit_result.
  (11) Parse B7 rendered value — extract the two dollar values from the range. Compare against low.result and high.result. Tolerance: max($1, value * 0.001). Exceeds tolerance = Fail.
  (12) Parse B8 rendered value — extract the dollar value. Compare against base.per_unit_result. Same tolerance. Exceeds tolerance = Fail.
```

**Source:** sheet-builder.md 8.3 README canonical schema + Must-Fix #3 + README B6 spec update
**Added:** 2026-06-15 | **Updated:** 2026-06-16 (expanded from 10 to 15 rows; added B7/B8 numerical accuracy checks)
**Self-correction:** On FAIL, rewrite the full README!A1:B15 block per Must-Fix #3 canonical protocol. If B6 is static, replace with `=Scenarios!C2`. If B7/B8 values are wrong, replace with correct values from sizing_output.json. Re-validate.
**Notes:** S13 checks attribution tags (`[Assumption:]` and `[SME:]`) on rows 11-15 and Assumptions col G. S21 owns all structural checks: 15 canonical labels, non-empty values, formula presence (B6/B7/B8), and numerical accuracy (B7/B8 vs calculator). No overlap — S13 is attribution, S21 is structure.

---

### S22: All 3 scenarios computed, ordered, and match calculator

**Phase:** 8 (Build Sheet)
**Pass:** The computed Annual Impact values on the Scenarios tab satisfy Low (col B) ≤ Base (col C) ≤ High (col D). All three are non-zero. Low and High match `sizing_output.json` low and high scenario results within $1 or 0.1% tolerance.
**Fail:** Values not ordered Low ≤ Base ≤ High, any value is zero/empty, or Low/High diverge from calculator output beyond tolerance.
**Check type:** Code-based (numeric comparison via MCP + JSON)

```check
Type: comparison
Source field: read_sheet_values on Scenarios tab (computed values)
Target field: sizing_output.json → low/base/high scenario results
Logic:
  (1) Read Scenarios!A1:A20 to find the Annual Impact row (search for "Annual Impact"). Record row number → impact_row.
  (2) Read Scenarios!B[impact_row]:D[impact_row] as computed values (without include_formulas).
  (3) Parse as numbers (strip $ and commas). Let low=B, base=C, high=D.
  (4) Verify low <= base <= high. Inversion = Fail.
  (5) Verify none are zero, empty, or NaN. Zero/empty = Fail.
  (6) Read $ARTIFACT_DIR/sizing_output.json, extract low.result, base.result, high.result.
  (7) For each pair (sheet_low vs calc_low, sheet_base vs calc_base, sheet_high vs calc_high):
      Compute delta = abs(sheet - calc). Tolerance = max(1, abs(calc) * 0.001).
      If delta > tolerance = Fail. Report which scenario diverged and by how much.
  (8) If no "Annual Impact" row found = Fail (same as S16 step 8).
```

**Source:** sheet-builder.md 8.5 verification + scenario ordering principle
**Added:** 2026-06-15
**Self-correction:** On FAIL, diagnose which formula is wrong by comparing factor-by-factor. Fix and re-validate.
**Notes:** S16 checks Base only. S22 extends to all three scenarios. Both are needed — S16 is the quick check (catches most issues), S22 is the comprehensive check (catches Low/High-specific formula errors like using column D for a variable factor in the Low scenario).

---

### S23: Canonical source compliance

**Phase:** 4 (Scale Data)
**Pass:** For each baseline and volume metric in the Scale Data Agent output, the `source` field matches the canonical source defined in `references/data-sources.md` Canonical Source Rules for the requested `metric_category`.
**Fail:** Any baseline or volume uses a non-canonical source — e.g., TPH Tracker for annual volume (should be D&F_Summary), or Win Calculator for TPH rates when TPH Tracker data is available (Win Calculator is fallback only for pharmacy step-level UPH).
**Check type:** Code-based (lookup table comparison)

```check
Type: comparison
Source field: Scale Data Agent output — source fields on volumes, baselines, labor_data
Target field: Canonical Source Rules from data-sources.md
Logic:
  (1) Build canonical source lookup by metric_category:
      - Annual shipment volume → "D&F_Summary" (NEVER "TPH Tracker" or "D&F TPH")
      - TPH rates (any) → "TPH Tracker" or "D&F TPH" (primary). "Win Calculator" only acceptable for pharmacy step-level (Data Entry, DUR, PV1, PV2, Manual Dispense)
      - Labor hours & dollars → "TPH Tracker" or "D&F TPH"
      - Shipping cost → "Trans_Summary"
      - Variable cost per fill → "TPH Tracker"
  (2) Read Scale Data Agent output.
  (3) For volumes.source: verify it contains the canonical source name for "annual volume." If it contains "TPH Tracker" or "D&F TPH" = Fail ("TPH Tracker volumes are cumulative YTD, not annual — must use D&F_Summary col P").
  (4) For baselines.primary_metric.source and each baselines.by_step[].source: verify each matches the canonical source for its data type. If metric_category == "labor_cost" and a TPH baseline cites "Win Calculator" for a non-pharmacy-step = Fail ("Win Calculator is fallback only for pharmacy step-level UPH").
  (5) Any non-canonical source = Fail. Report: "[field] uses [actual source] but canonical source is [expected source]."
```

**Source:** Derived from data-sources.md Canonical Source Rules table and SKILL.md Must-Fix #6 (Source Priority)
**Added:** 2026-06-16
**Self-correction:** On FAIL, orchestrator re-reads from the canonical source and re-runs the Scale Data Agent with corrected raw data. If the canonical source is unavailable via MCP, block and tell the user.
**Notes:** The most dangerous failure mode this catches is using TPH Tracker cumulative YTD volume as if it were annual volume — this systematically understates the addressable base, producing an estimate that looks conservative but is actually just wrong. data-sources.md explicitly warns: "TPH Tracker volume rows are cumulative YTD sums — they only reflect weeks with actuals. Never use these as annual figures."

---

### S24: Quote-in-chunk verification

**Phase:** 3 (Research)
**Pass:** For every benchmark in the Research Agent output, the `exact_quote` appears as a substring in at least one research pipeline chunk file. The quote is genuinely from the source material, not fabricated by the LLM.
**Fail:** Any `exact_quote` does not appear in any chunk file — the quote was likely fabricated or heavily paraphrased during extraction.
**Check type:** Code-based (substring search across chunk files)

```check
Type: presence
Source field: Research Agent output — each item's exact_quote
Target field: Research pipeline chunk files (read via Read tool from the pipeline output directory)
Logic:
  (1) Read the Research Agent output. For each benchmark item, extract exact_quote.
  (2) Read INDEX.md from the research pipeline output to identify all chunk file paths.
  (3) Read each chunk file.
  (4) For each exact_quote: search for it as a substring (case-insensitive, whitespace-normalized) across all chunk files.
  (5) If the quote is found in any chunk = Pass for that item.
  (6) If the quote is NOT found in any chunk = Fail for that item. Report: "Quote from [source_title] not found in any research chunk — possible fabrication."
  (7) Whitespace normalization: collapse multiple spaces/newlines to single space before matching (chunks may have formatting differences from the original).
  (8) Overall: all quotes found = Pass. Any quote not found = Fail.
```

**Source:** Addresses the gap between URL verification (VERIFIED_URLS.md confirms URLs are reachable) and content verification (S2 confirms value appears in quote, but neither checks that the quote itself is real)
**Added:** 2026-06-16
**Self-correction:** On FAIL, re-read the chunk files for the failing source. If the chunk exists but the quote is paraphrased: re-extract the verbatim text from the chunk. If no chunk exists for that source: drop the benchmark ("Benchmark from [source] dropped — no supporting chunk found").
**Notes:** This is the deepest authenticity check in the research pipeline. The chain of trust is: URL exists (VERIFIED_URLS.md) → quote exists in chunk (S24) → value exists in quote (S2/S6) → value is used correctly in model (S-evals downstream). S24 plugs the middle link. The most common trigger would be the LLM paraphrasing a chunk passage rather than copying it verbatim — the self-correction should re-extract the exact text.

---

### S25: Extraction coverage (benchmark count reconciliation)

**Phase:** 5 (Benchmark Extraction)
**Pass:** The number of benchmarks in `extracted_benchmarks.json` plus the number of explicitly logged "Benchmark dropped" messages accounts for every benchmark-bearing item in the Research Agent output. No benchmarks were silently dropped.
**Fail:** `extracted_benchmarks.json` has fewer records than the Research Agent output's benchmark items (those with non-null `improvement_value`), and the delta is not explained by logged drop messages.
**Check type:** Code-based (count comparison)

```check
Type: comparison
Source field: Research Agent output (Phase 3) — count of items with non-null improvement_value
Target field: $ARTIFACT_DIR/extracted_benchmarks.json + $ARTIFACT_DIR/extraction_drops.json
Logic:
  (1) Count the Research Agent output items where improvement_value is non-null → research_count.
  (2) Count the records in extracted_benchmarks.json → extracted_count.
  (3) Count the records in extraction_drops.json → dropped_count. If the file doesn't exist = Fail ("extraction_drops.json missing — Phase 5.4 did not write the required drop log").
  (4) Verify: extracted_count + dropped_count >= research_count.
  (5) If extracted_count + dropped_count < research_count = Fail. Report: "Research Agent produced [research_count] benchmarks, but only [extracted_count] were extracted and [dropped_count] were explicitly dropped. [delta] benchmarks silently lost."
  (6) If extracted_count + dropped_count >= research_count = Pass.
```

**Source:** Identified gap — benchmarks silently dropped between Phase 3 output and Phase 5 extraction with no logging or explanation
**Added:** 2026-06-16
**Self-correction:** On FAIL, re-read the Research Agent output and identify which benchmarks are missing from the extraction. For each missing benchmark: either extract it (if it has valid data) or explicitly log why it was dropped (e.g., "no quantified improvement", "duplicate of benchmark #N"). Re-validate.
**Notes:** The most common trigger is the orchestrator extracting a subset of benchmarks during Phase 5.2 because some chunks seemed less relevant — but without logging the exclusion. Silent drops reduce model quality (fewer data points for tier-weighted averaging) with no audit trail explaining why.

---

### S26: Improvement type consistency

**Phase:** 5 (Benchmark Extraction)
**Pass:** All benchmarks in `extracted_benchmarks.json` that will enter the tier-weighted average have the same `improvement_type` (all `percentage`, all `absolute_dollar`, or all `time`). OR if types are mixed, each record includes a `conversion_note` field explaining how the value will be normalized before averaging.
**Fail:** Records have mixed `improvement_type` values with no `conversion_note` field — the tier-weighted averaging formula would combine incompatible units.
**Check type:** Code-based (enum consistency check)

```check
Type: comparison
Source field: $ARTIFACT_DIR/extracted_benchmarks.json — improvement_type field per record
Target field: N/A (self-consistency)
Logic:
  (1) Parse extracted_benchmarks.json.
  (2) Filter to records with applicability_to_hims starting with "HIGH" or "MEDIUM" (these enter the tier-weighted average per scenario-logic.md; LOW-applicability records are excluded).
  (3) Collect the set of distinct improvement_type values from the filtered records.
  (4) If the set has exactly 1 element = Pass (all benchmarks are in the same unit).
  (5) If the set has > 1 element: for each record with a minority type, check if a conversion_note field exists and is non-empty. All minority-type records have conversion_note = Pass. Any missing = Fail.
  (6) Report: "Benchmarks have mixed improvement types: [list]. Records without conversion notes: [list]."
```

**Source:** scenario-logic.md tier-weighted averaging formula assumes all improvement_values are comparable — mixing percentages with absolute dollars produces nonsense math
**Added:** 2026-06-16
**Self-correction:** On FAIL, identify the mixed-type records. If conversion is straightforward (e.g., absolute dollar savings can be divided by the baseline to get a percentage), add a `conversion_note` and a normalized `improvement_value_pct` field. If conversion requires assumptions not in the data, flag to the user: "Benchmarks mix [types] — need a baseline to normalize. Which baseline should I use?"
**Notes:** The tier-weighted formula in scenario-logic.md is `Σ(weight × improvement_value) / Σ(weight)`. This only makes sense when all `improvement_value`s are in the same unit. Mixing 0.12 (12% reduction) with 50000 ($18K savings) would produce a meaningless average. This eval catches the problem at extraction time, before it silently corrupts the scenario construction.

---

### S27: MCP read completeness (row/column count)

**Phase:** 4 (Scale Data)
**Pass:** Each MCP `read_sheet_values` call returned the expected number of rows and columns for its range, as documented in `references/data-sources.md`. No truncation occurred.
**Fail:** Any MCP read returned fewer rows or columns than expected for the specified range — indicating silent truncation of sheet data.
**Check type:** Code-based (count comparison)

```check
Type: comparison
Source field: Scale Data Agent output — raw_sheet_data dimensions per source tab
Target field: Expected dimensions from data-sources.md range specifications
Logic:
  (1) For each raw_sheet_data entry in the Scale Data Agent output, record the number of rows and columns returned.
  (2) Compare against expected dimensions from data-sources.md:
      - D&F_Summary: ≥25 rows, ≥16 columns (P = col 16)
      - Trans_Summary: ≥30 rows, ≥16 columns
      - D&F TPH (OH section): ≥90 rows, ≥52 columns (weekly data)
      - D&F TPH (AZ section): ≥90 rows, ≥52 columns
  (3) If actual rows < expected rows OR actual columns < expected columns = Fail. Report: "[source_tab] returned [actual_rows]x[actual_cols] but expected ≥[expected_rows]x[expected_cols] — possible truncation."
  (4) If all ranges match or exceed expected dimensions = Pass.
```

**Source:** Identified gap — MCP could return truncated data that passes all schema and range checks
**Added:** 2026-06-17
**Self-correction:** On FAIL, re-read the specific range with explicit row/column bounds. If re-read returns the same truncated result, the sheet may have fewer rows than expected — escalate to user: "MCP returned fewer rows than expected for [source]. Is the data source complete?"

---

### S28: Research query quality

**Phase:** 3 (Research)
**Pass:** Each generated search query contains at least one term from the metric-specific query pattern table (SKILL.md Phase 3.1) AND includes the feature name or a recognizable synonym.
**Fail:** Any query lacks a metric-specific term or the feature name — indicating a poorly targeted query that would return irrelevant results.
**Check type:** Code-based (keyword presence)

```check
Type: presence
Source field: Generated search queries (from Phase 3.1 output)
Target field: Metric-specific query pattern terms + feature name
Logic:
  (1) Extract the list of generated queries from Phase 3.1 output.
  (2) Extract the feature name from Phase 1 intake.
  (3) Build metric-specific term sets from Phase 3.1 pattern table:
      - labor_cost: {"labor", "cost", "reduction", "UPH", "FTE", "savings", "workforce", "throughput", "productivity"}
      - shipping_cost: {"shipping", "cost", "carrier", "parcel", "package", "freight", "logistics"}
      - fulfillment_cost: {"fulfillment", "variable cost", "per unit", "DTC", "warehouse"}
      - quality: {"error", "accuracy", "defect", "quality", "rate"}
      - turnaround: {"cycle time", "turnaround", "speed", "throughput", "fulfillment time"}
  (4) For each query: verify it contains ≥1 term from the metric set (case-insensitive substring). Missing = Fail for that query.
  (5) For each query: verify it contains the feature name or a 2+ word substring of it. Missing = Fail for that query.
  (6) Overall: all queries pass = Pass. Any query fails = Fail.
```

**Source:** Identified gap — poorly targeted queries produce irrelevant research that passes all downstream evals
**Added:** 2026-06-17
**Self-correction:** On FAIL, regenerate the failing queries using the Phase 3.1 pattern table explicitly. Re-validate.
**Notes:** Conditional — only runs when research is conducted (Phase 2.5 → RUN). Skipped when research is skipped.

---

### S29: Benchmarks and SME Inputs tab column structure

**Phase:** 8 (Build Sheet)
**Pass:** The Benchmarks tab row 1 contains the expected 7 column headers: #, Source, URL, Tier, Improvement, Exact Quote, Applicability. The SME Inputs tab row 1 contains the expected 7 column headers: #, Assumption, SME Source, Value, Confidence, Applies To, Treatment in Model.
**Fail:** Any header is missing, misspelled, or in the wrong column position.
**Check type:** Code-based (structural via MCP)

```check
Type: structural
Source field: read_sheet_values on Benchmarks!A1:G1 and SME Inputs!A1:G1
Target field: Expected header lists
Logic:
  (1) Read Benchmarks!A1:G1. Verify values match: ["#", "Source", "URL", "Tier", "Improvement", "Exact Quote", "Applicability"] (case-insensitive, allow minor variants like "Source Title" for "Source").
  (2) Read SME Inputs!A1:G1. Verify values match: ["#", "Assumption", "SME Source", "Value", "Confidence", "Applies To", "Treatment in Model"] (case-insensitive).
  (3) Any missing or misordered header = Fail.
```

**Source:** sheet-builder.md 8.3 tab layouts — Benchmarks and SME Inputs tab column definitions
**Added:** 2026-06-17
**Self-correction:** On FAIL, rewrite the header row with the correct values via MCP modify_sheet_values. Re-validate.

---

### S30: Shareable link generated

**Phase:** 8 (Build Sheet)
**Pass:** The `sizing_context.json` file contains a non-empty `spreadsheet_url` field with a valid Google Sheets URL (matching pattern `(internal link)`).
**Fail:** `sizing_context.json` is missing, or `spreadsheet_url` is empty/null/malformed.
**Check type:** Code-based (file read + URL pattern match)

```check
Type: presence
Source field: $ARTIFACT_DIR/sizing_context.json → spreadsheet_url field
Target field: N/A
Logic:
  (1) Read $ARTIFACT_DIR/sizing_context.json. If file doesn't exist = Fail.
  (2) Parse JSON. Extract spreadsheet_url field. If null/empty = Fail.
  (3) Verify spreadsheet_url matches pattern "(internal link)". No match = Fail.
  (4) Pass.
```

**Source:** Identified gap — sheet could be built but never shared, leaving the user with no way to find it
**Added:** 2026-06-17
**Self-correction:** On FAIL, call get_drive_shareable_link on the spreadsheet_id and update sizing_context.json with the URL. Re-validate.

---

### G12: sizing_context.json exists and complete

**Pass:** `$ARTIFACT_DIR/sizing_context.json` exists and contains all required fields: `spreadsheet_id` (non-empty string), `spreadsheet_url` (valid Sheets URL), `readme` object with keys for rows 11-15 (problem_context, key_assumptions_risks, validation_recommendation, confidence_rationale, next_step — all non-empty), `source_quality` (non-empty), `sme_inputs` (array), `benchmarks` (array), `factor_rationales` (array with ≥1 entry).
**Fail:** File missing, any required field null/empty, or readme sub-fields missing.
**Check type:** Code-based (file existence + JSON schema validation)

```check
Type: structural
Source field: $ARTIFACT_DIR/sizing_context.json
Target field: N/A (schema check)
Logic:
  (1) Verify file exists at $ARTIFACT_DIR/sizing_context.json. Missing = Fail.
  (2) Parse JSON. Parse error = Fail.
  (3) Verify spreadsheet_id is non-empty string. Empty = Fail.
  (4) Verify spreadsheet_url matches "(internal link)". No match = Fail.
  (5) Verify readme object exists with keys: problem_context, key_assumptions_risks, validation_recommendation, confidence_rationale, next_step. Each must be non-empty string. Any missing/empty = Fail.
  (6) Verify source_quality is non-empty string. Empty = Fail.
  (7) Verify sme_inputs is an array (empty array is valid — "No SME inputs" case). Missing = Fail.
  (8) Verify benchmarks is an array (empty array is valid — research skipped case). Missing = Fail.
  (9) Verify factor_rationales is an array with ≥1 entry (every sizing has at least one factor). Empty = Fail.
```

**Source:** Identified gap — local context backup could be silently missing, leaving the directory incomplete if the sheet is deleted
**Added:** 2026-06-17
**Self-correction:** On FAIL, re-read the sheet via MCP and reconstruct sizing_context.json from the current sheet state. Re-validate.
**Notes:** This is the only eval that verifies the local backup exists. Without it, the "directory is self-contained" guarantee has no enforcement.
