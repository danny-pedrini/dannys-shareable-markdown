# Phase 8: BUILD INTERACTIVE MODEL (Google Sheet)

**The Google Sheet is the sole deliverable** — the interactive model stakeholders use to flex assumptions and make decisions. There is no separate markdown report.

Build a Google Sheet that mirrors the model's logic, exposes every assumption as a configurable cell with live formulas, and captures the reasoning narrative (problem context, risks, validation path) on the README tab.

> **All Phase 8 tools are on the `google-workspace` MCP server.** Tool names below are bare; the fully-qualified form is `mcp__google-workspace__<tool>` (e.g., `create_spreadsheet` → `mcp__google-workspace__create_spreadsheet`).

## 8.1: Create the Sheet

Use the `create_spreadsheet` MCP tool to create a new spreadsheet:

```
Tool: create_spreadsheet
Arguments: {
  "user_google_email": "you@example.com",
  "title": "Impact Sizing — [Feature Name] — [YYYY-MM-DD]"
}
```

Capture the returned `spreadsheet_id` and URL. Then add the tabs below using `create_sheet`, and populate each with `modify_sheet_values`.

## 8.2: Required Tabs

The sheet MUST have these tabs in this order. The TPH Variance tab is **required when `metric_category == labor_cost`** (Must-Fix #7); omit otherwise.

| Tab | Purpose | Cells Stakeholders Edit | Required When |
|---|---|---|---|
| `README` | Feature summary, confidence level, how to use the model, source links | None (reference only) | Always |
| `Assumptions` | Every variable factor exposed as Low/Base/High inputs + every baseline as a single input | **All yellow-highlighted cells** | Always |
| `Scenarios` | Low/Base/High results with live formulas referencing `Assumptions` | None — outputs only | Always |
| `TPH Variance` | TPH source data (weekly series for each pool), variance gap calc, **Labor Base Buildup** | None — evidence record | `metric_category == labor_cost` |
| `Benchmarks` | Full benchmark table with sources, tiers, exact quotes, applicability | None — evidence record | Always |
| `SME Inputs` | Every SME assumption captured in Phase 1.5 with source, confidence, treatment. **Always created** — if no SME inputs, include one row: "No SME inputs provided — elicitation occurred, PM had no data." | None — evidence record | Always |

## 8.3: Tab Layouts

**`README` tab** — columns A:B, single canonical schema (15 rows). This tab is the complete narrative for the sizing — it replaces the markdown report.

| Row | A (Label) | B (Value) |
|---|---|---|
| 1 | Feature | [Feature name] |
| 2 | Generated | [YYYY-MM-DD] |
| 3 | PM | Danny Pedrini |
| 4 | Metric Category | [labor_cost / shipping_cost / etc.] |
| 5 | Confidence | [HIGH / MEDIUM / LOW] |
| 6 | Base Case Annual Impact | `=Scenarios!C2` (MUST be a live formula — never paste a static value.) |
| 7 | Range | `=Scenarios!B2` & " – " & `=Scenarios!D2` (live formula referencing Low and High) |
| 8 | Per-Shipment Impact (Base) | `=Scenarios!C3` (live formula if per-unit row exists on Scenarios tab) |
| 9 | How to Use | Edit yellow cells on `Assumptions` tab to flex scenarios. Scenarios tab recalculates live. |
| 10 | Sources | [N] sources ([A] A-tier, [B] B-tier, [C] C-tier). See `Benchmarks` and `SME Inputs` tabs. |
| 11 | Problem Context | [Feature description]. Target metric: [X]. Impact mechanism: [HOW the feature improves the metric — 2-3 sentences max]. |
| 12 | Key Assumptions & Risks | Top 3-5 risks, each tagged [Assumption: X — needs validation]. Use line breaks within the cell to separate items. |
| 13 | Validation Recommendation | [Action]: [specific validation step]. Effort: [Low/Medium/High]. Timeline: [estimate]. What it reduces: [which uncertainty]. |
| 14 | Confidence Rationale | [Why HIGH/MEDIUM/LOW — cite source quality + scenario spread. E.g., "2 A-tier sources, 15% spread → HIGH" or "No A/B-tier, 80% spread → LOW".] |
| 15 | Next Step | [One clear action item — e.g., "Share with [Ops Program director] for SME validation" or "Ready for roadmap prioritization".] |

**🛑 Must-Fix #3 — Canonical README writer protocol (NEVER use partial column-B updates):**

Once the README is created, **all updates MUST rewrite the entire `A1:B15` block in a single `modify_sheet_values` call.** Partial column-B-only updates (e.g., `B7:B9`) are forbidden because they cause label-value misalignment if the row schema ever drifts.

**Why this matters:** During the v2/v3/v4 iterations of the Building Health Dashboard sizing, partial `B7:B9` writes landed under the wrong labels because the original README had been created with fewer rows than expected. The QA agent caught it on a second pass, but only after the misaligned data had already been visible to the user.

**The protocol:**

1. **First write (creation):** Write all 15 rows at `A1:B15` with both labels (column A) and values (column B) together.
2. **Subsequent updates:** Re-write the full `A1:B15` block — preserve column A labels exactly, update column B values. **Never** write to `B<n>:B<m>` alone.
3. **After every README update:** Read back `A1:B15` via `read_sheet_values` and verify each row's label-value pair makes sense (label in A, expected content type in B).
4. **If labels in column A appear to have shifted** (e.g., row 7 should say "Range" but reads "Per-Shipment Impact"), STOP. Rewrite the full `A1:B15` block with the canonical schema. Do not chase the shift downward.

**Example canonical update call:**

```
Tool: modify_sheet_values
Arguments: {
  "spreadsheet_id": "...",
  "range_name": "README!A1:B15",
  "values": [
    ["Feature", "..."],
    ["Generated", "..."],
    ["PM", "Danny Pedrini"],
    ["Metric Category", "..."],
    ["Confidence", "..."],
    ["Base Case Annual Impact", "=Scenarios!C2"],
    ["Range", "..."],
    ["Per-Shipment Impact (Base)", "..."],
    ["How to Use", "Edit yellow cells on Assumptions tab to flex scenarios. Scenarios tab recalculates live."],
    ["Sources", "..."],
    ["Problem Context", "..."],
    ["Key Assumptions & Risks", "..."],
    ["Validation Recommendation", "..."],
    ["Confidence Rationale", "..."],
    ["Next Step", "..."]
  ]
}
```

**Verification after write:**
```
Tool: read_sheet_values
Arguments: {"spreadsheet_id": "...", "range_name": "README!A1:B15"}
```
Confirm row 6 column A reads "Base Case Annual Impact" and column B contains a dollar figure. Confirm rows 11-15 are non-empty (narrative content). Repeat sanity check for each row.

**`Assumptions` tab** — one row per factor (from `sizing_input.json` `factors[]`), then one row for `per_unit_divisor` if it exists. No section-header rows. Use a `Type` column to distinguish constants from variables:

```
Col A    | Col B                | Col C     | Col D     | Col E     | Col F     | Col G
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
Type     | Factor               | Low       | Base      | High      | Unit      | Source / Rationale                                        ← Row 1 (header)
constant | annual_shipping_cost |           | 89186113  |           | $         | Trans_Summary FY26 col P                                  ← Row 2  (factors[0])
variable | improvement_pct      | 0.05      | 0.10      | 0.15      | %         | Tier-weighted bench. avg; SME ([Ops Program director]) caps at 30%   ← Row 3  (factors[1])
variable | adoption_rate        | 0.60      | 0.80      | 0.95      | %         | Low: AZ only. Base: AZ+OH. High: All incl. 3PLs (SME).    ← Row 4  (factors[2])
constant | per_unit_divisor     |           | 11729317  |           | shipments | Trans_Summary FY26 row 4 (used as Per-Unit denominator)   ← Row 5  (divisor)
```

This example matches the Phase 7.1 input JSON, which has **3 factors** (`annual_shipping_cost`, `improvement_pct`, `adoption_rate`) and a separate top-level `per_unit_divisor: 11729317`. The divisor is **not** a factor in the multiplicative model — it's a denominator used only by the Per-Unit formula.

**Layout convention (critical — Scenarios formulas depend on this):**
- **Constants** — single value in the **Base** column (D) only. Low (C) and High (E) cells stay **blank**. `Scenarios` formulas reference column D for constants in all three scenarios.
- **Variables** — separate values in Low (C), Base (D), High (E). `Scenarios` formulas reference C for the Low scenario, D for Base, E for High.
- **Row layout** — Row 1 is the header. Row 2 is the first data row. Factors come first in the same order as `factors[]` in `sizing_input.json` (`row_number = factor_index + 2`). The `per_unit_divisor` row (if any) goes **immediately after the last factor row** — never interleaved with factors.
- **Labels (column B)** must exactly match factor `name` values from the calculator input — this is the join key when wiring formulas. The divisor row uses the literal label `per_unit_divisor`.
- **If a factor was anchored to an SME assumption**, prefix the Source column with `[SME: <name>]`.
- **Per-unit divisor handling:** `sizing_input.json` has a top-level `per_unit_divisor` field (e.g., `total_shipments` for shipping, `annual_volume` for labor, error count for quality). Always add it as a labeled `per_unit_divisor` row immediately after the last factor row, even if its value coincidentally matches a factor. This keeps the row mapping simple and unambiguous: factors are factors, divisor is divisor.

**Before writing any Scenarios formulas:** Build an explicit row mapping by iterating through `factors[]` in `sizing_input.json` in order, then appending the divisor (if present). For each row, record: `name`, `role` (`factor` or `divisor`), `is_constant`, and `row_number`. Output this mapping in a code-fenced block in your response before proceeding to formulas — it's the join key everything downstream depends on. Example matching the JSON above:

```
Row mapping (from sizing_input.json):
  factors[0] annual_shipping_cost  factor   constant  → row 2
  factors[1] improvement_pct       factor   variable  → row 3
  factors[2] adoption_rate         factor   variable  → row 4
  per_unit_divisor (total_shipments) divisor constant → row 5
```

If the input has 2 or 5 factors instead of 3, the mapping shifts and the divisor row moves accordingly. **Never** write formulas without first producing this mapping — guessing row numbers is the most common cause of broken sheets.

**`Scenarios` tab** — outputs computed via formulas referencing the layout above. Example formulas matching the 3-factor + divisor mapping shown immediately above:

```
Col A                       | Col B (Low)                                        | Col C (Base)                                       | Col D (High)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Annual Impact ($)           | =Assumptions!D2 * Assumptions!C3 * Assumptions!C4  | =Assumptions!D2 * Assumptions!D3 * Assumptions!D4  | =Assumptions!D2 * Assumptions!E3 * Assumptions!E4     ← Row 2
Per-Unit Impact ($/ship)    | =B2 / Assumptions!D5                               | =C2 / Assumptions!D5                               | =D2 / Assumptions!D5                                  ← Row 3
% of Baseline               | =B2 / Assumptions!D2                               | =C2 / Assumptions!D2                               | =D2 / Assumptions!D2                                  ← Row 4
```

**Reading the example formulas:**
- `annual_shipping_cost` (factor, constant) is row 2 → reference column **D** (Base) in all three scenarios.
- `improvement_pct` (factor, variable) is row 3 → reference **C3** for Low, **D3** for Base, **E3** for High.
- `adoption_rate` (factor, variable) is row 4 → reference **C4** for Low, **D4** for Base, **E4** for High.
- `per_unit_divisor` (divisor, constant) is row 5 → reference **D5** in the Per-Unit formula only. The divisor is NOT multiplied into Annual Impact.
- `% of Baseline` divides Annual Impact by the baseline cost (row 2) — same denominator across all three scenarios.

**Rules:**
- Outputs MUST be live formulas referencing `Assumptions`. Never paste static numbers.
- Use the exact same multiplicative structure as the `sizing_calculator.py` input — one factor per cell, product across the row.
- Constants reference column D in every scenario; variables reference C/D/E for Low/Base/High respectively.
- When you write formulas via `modify_sheet_values`, pass `valueInputOption: "USER_ENTERED"` so strings starting with `=` are parsed as formulas. With `RAW`, they'd be stored as literal text and nothing would calculate.

**`TPH Variance` tab** — REQUIRED for `labor_cost` features. Three sections:

**Section 1: Weekly TPH source data** (rows 1-26)

| Row | Content |
|---|---|
| 1 | Title: "TPH Variance Source Data" |
| 2 | Source citation (TPH Tracker spreadsheet ID + tab + week range) |
| 4 | Headers: `Week | OH Pack | AZ Pack | OH Pharm | AZ Pharm | OH Ful | AZ Ful` |
| 5-24 | 20 weeks of TPH data (one row per week, 7 columns) |
| 26 | Mean row (formulas: `=AVERAGE(B5:B24)` etc.) |
| 27 | Max row (formulas: `=MAX(B5:B24)` etc.) |
| 28 | Min row |
| 29 | Best-vs-Mean Gap row (formulas: `=(B27-B26)/B26` etc.) |
| 31 | Pool weighted gap (per-pool: Pharmacy gap and Fulfillment gap) |
| 32 | Pool labor share (e.g., "Pharmacy 67% of $X" / "Fulfillment 33%") |
| 33 | OVERALL POOL-WEIGHTED VARIANCE GAP (formula: `=pharm_share*pharm_gap + ff_share*ff_gap`) |

**Section 2: Labor Base Buildup (Must-Fix #7)** — auto-generated when `metric_category == labor_cost`. Stakeholder-facing buildup showing how the addressable labor figure is constructed.

| Row | A | B | C |
|---|---|---|---|
| 38 | (blank) | **LABOR BASE BUILDUP — How we get to $XX.XM addressable** | (blank) |
| 39 | (blank) | **Component** | **Annual $** |
| 40 | (blank) | Productive Pharmacy (DUR + PV1 + PV2 + Data Entry + Manual Dispense) | $8,504,325 |
| 41 | (blank) | Productive Fulfillment (Pack + Lead + Inventory Control + Support) | $4,187,716 |
| 42 | (blank) | **Productive labor subtotal** | **$12,692,040** |
| 43 | (blank) | `'+ OT premium overage`  *(apostrophe prefix to escape `+` formula trap)* | $192,400 |
| 44 | (blank) | `'+ Temp labor (smoothable via better forecasting)` | $540,200 |
| 45 | (blank) | `'+ Structural premium portion` | $1,375,360 |
| 46 | (blank) | **ADDRESSABLE LABOR (model input → Assumptions!D2)** *(yellow background)* | **$14,800,000** |
| 47 | (blank) | (blank) | (blank) |
| 48 | (blank) | **Cross-check vs D&F_Summary Variable Cost** | (blank) |
| 49 | (blank) | Non-labor variable cost (packaging, vials, labels, supplies — NOT addressable) | $3,398,440 |
| 50 | (blank) | **TOTAL D&F INTERNAL VARIABLE COST (D&F_Summary)** | **$18,198,440** |
| 52 | (blank) | "Dashboards + WIP signals affect labor productivity, not materials. The $3.40M non-labor portion would be addressed by different features (e.g., Digital Medication Guides for paper inserts)." | (blank) |

**Why this section is required:** During the Building Health Dashboard sizing, a stakeholder reviewing the sheet asked "why $13M when D&F shows $18M?" — the answer was buried in a wall of text in the Source/Rationale cell. Surfacing it as a structured buildup with a Variable Cost cross-check answers the question in two clicks instead of two paragraphs.

**Formatting rules for this section:**
- Row 38 (title): Bold + light blue background (`#E8F0FE`)
- Row 39 (header): Bold
- Rows 42, 46, 50 (totals): Bold
- Row 46 (Addressable Labor model input): Bold + yellow background (`#FFF59D`) to signal "this is the actual model input"
- Column C: Currency format, right-aligned
- Apostrophe-prefix any cell with leading `+` to escape Sheets' formula parser

**Section 3: Why-it-matters narrative** (rows 53+)

Free-form text. Short paragraph explaining what the dashboard mechanism actually closes (the best-vs-mean gap), plus 2-3 validation needs.

---

**`Benchmarks` tab** — evidence record of all research sources:

| # | Source | URL | Tier | Improvement | Exact Quote | Applicability |

**`SME Inputs` tab** — **always created**. If Phase 1.5 captured assumptions, populate the full table. If not, include a single row: `[1, "No SME inputs provided — elicitation occurred, PM had no data.", "—", "—", "—", "—", "—"]`.

| # | Assumption | SME Source | Value | Confidence | Applies To | Treatment in Model |

## 8.3.1: Source / Rationale Cell Style (Nice-to-have #8)

The `Source / Rationale` column on the Assumptions tab is the first thing a cold reviewer reads. It must be **stakeholder-readable from the start**, not a methodology dump.

**Rules for each Source/Rationale cell:**

1. **Maximum 2 sentences.** If the explanation needs more, put detail on the right tab (TPH Variance, SME Inputs, Benchmarks) and reference it with "See [tab name]."
2. **Answer "what is this number and where did it come from?"** Skip: derivation math, version history breadcrumbs ("v3 refactor", "Replaces v2"), MCP discovery caveats, SME attribution (lives on SME Inputs tab), benchmark cross-references (lives on Benchmarks tab).
3. **Use plain language, not method names.** Good: "Total labor cost across Pharmacy and Fulfillment pools." Bad: "Refactored 2026-05-29 v3: full TPH Tracker actuals across both pools."
4. **End with a tab-pointer when relevant.** "See TPH Variance tab for source data" / "See SME Inputs tab for attribution."

**Good vs. bad examples:**

| Factor | ❌ Bad (methodology dump) | ✅ Good (stakeholder-readable) |
|---|---|---|
| `annual_addressable_labor_cost` | "Refactored 2026-05-29 v3: full TPH Tracker actuals across both pools. Pharmacy $8.50M (OH 4.99M / 28.87 TPH × $59.70 + AZ 3.96M / 18.65 TPH × $59.70). Fulfillment $4.19M (OH 4.99M / 20.26 TPH × $28 + AZ 3.96M / 25.04 TPH × $28; includes Pack + Lead + IC + Support). Pharmacy blended rate $59.70 = Win Calc step-hour-weighted avg of pharmacist $99.78 and tech $36. Replaces v2 hybrid ($11.41M = Win Calc upstream + TPH Pack)." | "Total labor cost across Pharmacy and Fulfillment pools. Hours = FY26 shipment volume ÷ actual mean TPH from TPH Tracker; rates = $22.09/hr blended pharmacy and $10/hr fulfillment. See TPH Variance tab for source data." |
| `weighted_variance_gap` | "v3 pool-weighted: Pharmacy gap 17.48% (OH 20.19% × 44.9% labor + AZ 15.28% × 55.1%) × pool share 67.0% + Fulfillment gap 21.51% (OH 23.89% × 60.9% + AZ 17.81% × 39.1%) × pool share 33.0% = 18.81%. Lower than v2 Pack-only 22.75% — AZ Pharmacy variance is materially tighter (15.28%) which pulls weighted gap down." | "Gap between Hims's best-practice week and the average week, measured in the TPH Tracker over 20 weeks. This is the throughput headroom that real-time dashboards + WIP signals can close. Pharmacy contributes 67%, Fulfillment 33%. See TPH Variance tab." |

**Test before writing:** Read the cell aloud as if you're a stakeholder seeing it for the first time. Does it tell you (a) what the number measures and (b) where it came from, in under 30 seconds? If no, simplify.

---

## 8.4: Apply Formatting

After populating data, use `format_sheet_range` to:
- Bold all header rows
- Yellow background on editable cells in `Assumptions`:
  - **Constants:** only the Base cell (column D) — Low and High are blank by convention
  - **Variables:** Low, Base, and High cells (columns C, D, E)
- Currency format on `$` columns
- Percentage format on `%` columns
- Freeze the header row on every tab

## 8.5: Verify and Return

1. Read back the Base column on `Scenarios` via `read_sheet_values` and confirm the Sheets Base value matches the `sizing_calculator.py` Base result to within **$1 OR 0.1%, whichever is larger**. If divergence exceeds this tolerance, do NOT proceed — diagnose which factor is in the wrong cell or missing. The most common cause is a wrong cell reference in a Scenarios formula (e.g., referencing a constant via column C/E instead of D, or hitting the wrong row because factors were reordered).
2. Generate a shareable link with `get_drive_shareable_link` (commenter access by default — the user can promote to edit if they want stakeholders to flex it).
3. Include the URL prominently in the final deliverable to the user:

```
📊 **Interactive Model:** Impact Sizing — Feature — Date
   Stakeholders can edit the yellow cells on the `Assumptions` tab to flex scenarios.
```

4. The sheet IS the deliverable — there is no separate report to update.

## 8.6: Error Handling

| Error | What to Do |
|---|---|
| `create_spreadsheet` fails | Surface error to the user. Do NOT silently ignore — if the user requested the sheet, they expect it. |
| Scenarios formulas don't match calculator output | Stop. Diagnose the formula. Common cause: wrong cell references or missing factor. Fix before returning sheet to user. |
| User has no Drive write access | Block and tell the user. |
| README rows appear misaligned (label/value mismatch after update) | Do NOT chase the shift with more partial writes. Rewrite the full `A1:B15` block per the canonical schema (Must-Fix #3). Verify rows 11-15 are present and non-empty after rewrite. |
| `modify_sheet_values` cell error: "Formula parse error" on text values starting with `+` | Prefix the value with an apostrophe (`'+8% incremental`) to force literal text — Sheets interprets leading `+` as a formula. |
