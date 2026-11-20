# Data Sources Reference

Reference document for feature-impact-sizing skill. Loaded by the orchestrator during Phase 4 (scale data collection) and passed to the Quality Gate Validator for reasonableness checks.

---

## Staleness Check

Each data source has a `verified` date below. **If the verified date is >30 days old**, read the first 5 rows of each tab to confirm structure matches the documented layout before extracting data. If structure has changed (columns shifted, tabs renamed, rows inserted), stop and alert the user — extracting from wrong ranges produces silent bad data.

---

## Canonical Source Rules

| Data | Canonical Source | Why | Do NOT Use |
|---|---|---|---|
| **Annual shipment volume** | D&F_Summary col P (Data Source 1) | Full FY (actuals + forecast), Finance-owned, includes site-level breakdown | TPH Tracker volume columns — those are cumulative YTD actuals, not annual projections |
| **TPH rates** (tasks/hr by role/step) | TPH Tracker D&F TPH (Data Source 3) | Actual weekly performance, site-level | Win Calculator (fallback only for pharmacy step-level UPH) |
| **Labor hours & dollars** (reg/OT/HSV) | TPH Tracker D&F TPH (Data Source 3) | Actual by role and site | — |
| **Shipping cost** | Trans_Summary col P (Data Source 1) | Full FY, includes all carriers and sites | — |
| **Variable cost per fill** | TPH Tracker row 89/175 (Data Source 3) | Direct efficiency metric, weekly granularity | — |

**Critical:** TPH Tracker volume rows (D&F TPH!A8:BB13 for OH, A94:BB99 for AZ) are **cumulative YTD sums** — they only reflect weeks with actuals. Never use these as annual figures. Always pull annual volume from D&F_Summary col P.

---

## Data Source 1: Project Entitlement (Shipping & Fulfillment Costs/Volumes)

- **Spreadsheet ID:** `1YSaPS7Y0sb94tYuga-7mHsfpwT4XXljw35bd_xao9XA`
- **Verified:** 2026-05-29

### Tab: Trans_Summary (Shipping)

| Metric Category | Range | Key Rows |
|---|---|---|
| `shipping_cost` | `Trans_Summary!A1:P40` | Row 4: Total Shipments, Row 16: Shipping Cost, Row 28: Cost Per Package. Column P = FY total. |
| `turnaround` | `Trans_Summary!A1:P12` | Volume context (pairs with user-provided turnaround baseline) |

### Tab: D&F_Summary (Fulfillment)

| Metric Category | Range | Key Rows |
|---|---|---|
| `fulfillment_cost` | `D&F_Summary!A1:P30` | Row 5: Total Shipments, Row 14: Variable Cost, Row 23: Variable Cost Per Unit. Last column = FY total. |
| `labor_cost` | `D&F_Summary!A1:P12` | Volume context (pairs with Win Calculator or TPH Tracker labor data) |
| `quality` | `D&F_Summary!A1:P12` | Volume context (pairs with user-provided quality baseline) |

### Extraction Notes

- Columns D–O = Jan '26 through Dec '26
- Last data column (P or similar) = FY total — **use this for annual figures**
- Rows 2–3 contain headers: `ACT` = actuals, `FCST` = forecast — note which months are actual vs. forecast
- Trans_Summary includes 3PL sites (Strive, Red Rock, Anazao, Curexa) and Labs — filter to relevant scope
- D&F_Summary includes internal sites (OH1, AZ1/2, AZ3) and 3PLs — filter to relevant scope
- If the feature is scoped to specific sites, use site-specific rows, not totals

---

## Data Source 2: Win Calculator (UPH & Labor Rates by Process Step)

- **Spreadsheet ID:** `1AchxjWSX7ZjpGFoYdfixRqXjeHkYhbVI125XzWWeR60`
- **Verified:** 2026-05-29

### Tab: Sheet1 (UPH and Rates)

| What to Read | Range | Key Data |
|---|---|---|
| UPH by process step | `Sheet1!A2:G5` | Row 2: column headers. Row 3: Avg Tasks/Hour (UPH). Row 5: Hourly Rate. |

### Tab: References

| What to Read | Range | Key Data |
|---|---|---|
| Source URL | `References!A1:A5` | Looker report URL used to source UPH data |

### Data Layout

```
         | Data Entry | DUR    | PV1    | Manual Dispense | PV2    | Pack
UPH      | 120        | 224    | 291    | 54              | 125.4  | 34
Hrs/Shift| 10         | 10     | 10     | 10              | 10     | 10
Rate     | $36.00     | $99.78 | $99.78 | $36.00          | $99.78 | $28.00
```

*Quick reference only. Read live via MCP — do not rely on the table above if the sheet may have changed.*

### When to Use Win Calculator

- **Fallback source for pharmacy step-level UPH only** (`Data Entry`, `DUR`, `PV1`, `Manual Dispense`, `PV2`) — TPH Tracker aggregates pharmacy by role (Pharmacist/Tech), not by step, so Win Calculator is the only per-step UPH source. Default to TPH Tracker for aggregate pharmacy labor; only fall back to Win Calc when per-step decomposition is required.
- **Fallback / cross-check for Pack only** — TPH Tracker `D&F TPH` has actual weekly Pack TPH (FY avg ~30.5 vs Win Calculator's 34). Always prefer TPH Tracker.
- Use the user-specified process step(s) from intake to select the relevant columns
- Combine with D&F_Summary volume data to compute annual labor cost baseline

### Labor Cost Baseline Formula

Computed by `sizing_calculator.py`, NOT the LLM.

**The formula depends on what you're sizing:**

```
For all labor cost initiatives (TPH improvement, step elimination, automation):
  Annual SAVINGS = hours_saved × fully_loaded_hourly_rate
  where fully_loaded_hourly_rate = base wage + employer taxes + benefits (~$10/hr for pack FTE)

For total labor cost baseline (context only):
  Annual labor cost = regular_dollars + OT_dollars + HSV_dollars
  (Read each directly from TPH Tracker — do NOT derive from UPH × rate)
```

**Rate guidance:** Always use the **fully loaded hourly rate** ($10/hr for pack FTE per [teammate] Q-011) when valuing saved worked hours. The fully loaded rate includes base wage + employer taxes + benefits — all of which are genuinely saved when a worked hour is eliminated. OT premiums and HSV (holiday/sick/vacation) are structural costs that don't decrease when tasks get faster — but they are NOT included in the $28 fully loaded per-worked-hour rate.

[teammate] (FP&A) confirmed in the May 27 2026 Finance discovery session:
- **TPH uses ONLY worked hours** — it excludes OT, HSV, benefits, and taxes
- **Variable cost per fill (~$4) includes everything** — worked + OT + HSV + benefits/taxes
- The $28 fully loaded rate is the cost **per worked hour** for an FTE — it captures the employer's full cost of that hour (base + taxes + benefits)
- OT and HSV are separate structural costs outside the $28 — they don't shrink when tasks get faster

**Use the fully loaded rate ($10/hr for pack FTE, $23.50 for temp) when computing labor savings from saved worked hours.**

---

## Metric Mechanics (from Finance Discovery — 2026-05-27)

*Source: `Product Strategy & Roadmap/Impact Sizing/2026-05-27-Cost-Calculations-Education-Finance-Discovery.md` — [teammate] (FP&A) walkthrough of WBR data structure with PM team.*

### Variable Cost Per Fill Decomposition

```
Variable Cost Per Fill (~$4)
├── Productivity Component (TPH)
│   ├── Shipments ÷ Worked Hours
│   └── ★ SOFTWARE INITIATIVES AFFECT THIS ★
│
└── Wage Component
    ├── Base wage rates (by role)
    ├── Overtime ($)
    ├── HSV — Holiday / Sick / Vacation ($)
    ├── Estimated taxes & benefits
    └── Workforce composition (FTE vs. temp)
        ← OPS PLANNING LEVER (not product)

Fully Loaded Cost Per Fill (~$10-12)
├── Variable Cost Per Fill (~$4)  ← ABOVE
├── Salaried labor
├── Quality headcount
├── PPE, hot shots, supplies
└── Other fixed costs
    ← OUTSIDE PRODUCT TEAM INFLUENCE
```

**Key implication for sizing:** When sizing software initiatives, the addressable base is the **productivity component** of variable cost per fill (~$4), NOT the fully loaded cost (~$10-12). The fully loaded cost includes items that don't respond to throughput changes.

### Shipment-Based Numerator Distortion

All productivity metrics — pharmacy AND fulfillment — use **shipments (distinct tracking numbers)** as the numerator. NOT PV2 completions, fills, or dispenses. One manual adjustment: oral weight loss × 2.3 vials/shipment.

**Critical distortion:** Because shipments are the numerator for ALL roles, a downstream disruption (pack downtime, HighJump outage) retroactively depresses upstream productivity rates even when upstream was productive. Conversely, fixing a downstream bottleneck makes ALL upstream TPH rates appear to improve — even if those steps didn't get faster.

**What this means for sizing:**
- A pack initiative that increases shipments/hour also appears to improve pharmacist TPH — this is an **artifact**, not real savings
- Do NOT count the apparent improvement in other steps' TPH as additional savings — that's double-counting
- When investigating a week with poor productivity, always check if a downstream disruption caused the drop
- The Quality Gate Validator's Check 9b (double-counting) explicitly screens for this

### HSV: Additive to Cost, Not Throughput

- **TPH** = Shipments ÷ **Worked Hours only**
- **Variable Cost Per Fill** = Total Wage Cost (worked + OT + HSV + benefits) ÷ Shipments
- A spike in HSV increases cost per fill WITHOUT reducing TPH
- Software initiatives affect TPH → they save worked hours → they reduce the worked-hours portion of VCPF
- They do NOT reduce OT or HSV

**For scenario construction:** When building the labor cost factor for the calculator, use `fully_loaded_rate × hours_saved` ($10/hr for pack FTE per [teammate] Q-011). OT and HSV are structural costs outside the fully loaded per-worked-hour rate — they don't change when tasks get faster.

### [teammate]'s Reference Values

Use these as sanity-check ranges (sourced from the FP&A session):

| Metric | Expected Range | Source |
|---|---|---|
| Variable cost per fill (hourly labor only) | $3.50-$5.00 | [teammate], FP&A `[Q-009]` |
| Fully loaded cost per fill | $10-$12 | [Director of Pharmacy & Fulfillment Product] `[Q-010]` |
| Pack associate fully loaded wage | ~$10/hr | [teammate] `[Q-011]` |
| Temp associate wage | ~$8.70/hr | [teammate] `[Q-011]` |
| Pharmacist rate | ~$36.92/hr | Win Calculator |
| Tech rate | ~$13/hr | Win Calculator |

### Compounding: Batch Release Timing Lag

For compounding initiatives, the numerator (tablets) only counts when the batch is **released from QA review** — NOT when produced. Labor is recorded in the production week. A batch produced in week N but released in week N+2 inflates N+2's productivity and deflates N's.

**For sizing compounding initiatives:** Use **rolling 30-day or month-to-date** windows, not weekly snapshots. If the Findings Validator (Check 3: Data Freshness) flags compounding baselines built from weekly data, this timing lag — not thin data — is likely the cause.

### Finance Contact Routing

| Domain | Contact |
|---|---|
| Transportation, shipping, quality, compounding, DNF cost | **[teammate]** (FP&A) |
| R&D, International, Supply Chain | [teammate] ([VP, Operations Finance]'s team) |
| CapEx | [VP of Engineering] |
| Provider / CS | [teammate] ([VP, Operations Finance]'s team) |
| Product / packaging | [teammate] / [teammate] |

---

## Data Source 3: TPH Tracker (Actual Weekly TPH, Labor Hours, Labor Dollars, OT)

- **Spreadsheet ID:** `1wm3QRGVOQedS4dDceebV9A3NlXeMjd00js6rkm6rU6U`
- **Verified:** 2026-05-29

Tracks actual operational performance at **weekly** granularity by site. Provides actual TPH (tasks per hour), labor hours, labor dollars (regular + OT + HSV), and variable cost per fill — all broken down by role and fulfillment sub-function. **For labor cost sizing, this is the primary baseline source when data is available for the affected step.**

### Structure

The `D&F TPH` tab has parallel sections for **OH** (starts row 5) and **AZ** (starts row 91), each containing the same block layout. Weekly columns B–BB (week 1–52, Jan–Dec 2026). Last column = FY total (for hours/dollars) or FY average (for TPH).

### OH Section — Key Ranges

| What to Read | Range | Row Labels | Key Data |
|---|---|---|---|
| Volume by product type | `D&F TPH!A8:BB13` | Volume, Non-WL, Oral, GLP-1, Novo Pen, Novo Pills | **⚠️ YTD cumulative only** — last col sums actuals-to-date, NOT a full-year projection. For annual volume, use D&F_Summary col P. |
| Pharmacy hours by role | `D&F TPH!A15:BB20` | Pharmacy Hours (Work), Pharmacist, Pharmacy Tech, Pharmacist Support, Pharmacy Tech Support, Pharmacy Tech Temp | FY total in last col. |
| Pharmacy TPH by role | `D&F TPH!A22:BB26` | Pharmacy (TPH), Pharmacist (TPH), Pharmacy Tech (TPH), Pharmacist Support (TPH), Pharmacy Tech Support (TPH) | **FY average** in last col. Pharmacy (TPH) FY avg: 28.8. Pharmacist (TPH) FY avg: 71.1. |
| Fulfillment hours by sub-function | `D&F TPH!A28:BB33` | Fulfillment Hours (Work), Fulfillment - Pack, Fulfillment - Lead, Fulfillment - Inventory Control, Fulfillment - Support, Fulfillment Temp Hours | FY total in last col. Pack hours FY: 70,247. |
| Fulfillment TPH by sub-function | `D&F TPH!A35:BB39` | Fulfillment (TPH), Pack (TPH), Lead (TPH), Inventory Control (TPH), Support (TPH) | **FY average** in last col. Pack (TPH) FY avg: **30.5** (vs Win Calculator's 34). |
| Pharmacy regular dollars | `D&F TPH!A41:BB46` | Pharmacist Reg Dollars (total), Pharmacist, Pharmacy Tech, Pharmacist Support, Pharmacy Tech Support, Pharmacy Tech Temp | FY total in last col. Pharmacist Reg FY: $1,100,797. |
| Fulfillment regular dollars | `D&F TPH!A48:BB53` | Fulfillment Reg Dollars (total), Pack, Lead, Inventory Control, Support, Temp | FY total in last col. Fulfillment Reg FY: $798,876. Pack Reg FY: $475,744. |
| Pharmacy OT dollars | `D&F TPH!A55:BB59` | Pharmacist OT Dollars (total), Pharmacist, Pharmacy Tech, Pharmacist Support, Pharmacy Tech Support | FY total in last col. Pharmacist OT FY: $43,069. |
| Fulfillment OT dollars | `D&F TPH!A62:BB66` | Fulfillment OT Dollars (total), Pack, Lead, Inventory Control, Support | FY total in last col. Fulfillment OT FY: $12,320. |
| Pharmacy HSV dollars | `D&F TPH!A69:BB73` | Pharmacist HSV Dollars (total), Pharmacist, Pharmacy Tech, Pharmacist Support, Pharmacy Tech Support | FY total in last col. Pharmacist HSV FY: $136,698. |
| Fulfillment HSV dollars | `D&F TPH!A76:BB80` | Fulfillment HSV Dollars (total), Pack, Lead, Inventory Control, Support | FY total in last col. Fulfillment HSV FY: $108,791. |
| Total pay breakdown | `D&F TPH!A83:BB87` | Total Pay, Pay (base), Taxes, Benefits | FY total in last col. OH Total Pay FY: $3,481,574. |
| Variable cost per fill | `D&F TPH!A89:BB89` | OH Variable Cost per Fill | $/fill. FY average: $4.39. |

### AZ Section

Starts at row 91 ("Arizona"). Same block layout as OH, offset by 86 rows (e.g., AZ Volume = row 94, AZ Pharmacy Hours = row 101, etc.). **⚠️ AZ volume row is also YTD cumulative — use D&F_Summary for annual volume.**

### Auxiliary Tabs

| What to Read | Tab | Range | Key Data |
|---|---|---|---|
| OT dollars by site and role | `Dollars` | `Dollars!A4:CC13` (OH), `Dollars!A15:CC24` (AZ) | OT spend: Pharmacist, Compounding, Tech, Fulfillment, Fixed. Includes % OT row. |
| OT hours by site and role | `Hours` | `Hours!A4:AB13` (OH), `Hours!A15:AB24` (AZ) | OT hours by same role breakdown. |
| Site summary | `Site Summary` | `Site Summary!A5:BB20` | Mirrors D&F TPH structure at site level. Includes Reg Dollars by department. |
| D&F labor model (monthly) | `D&F Model` | `D&F Model!A3:Z20` | Monthly hours by fulfillment sub-function. Sick/vacation rates by department. |

### Extraction Notes

- Weeks with `-` or blank values are future/unfilled — use only weeks with actuals for trend analysis
- OT and HSV are separate from regular dollars — when computing total labor cost, sum regular + OT + HSV for completeness
- The variable cost per fill (row 89 for OH, ~row 175 for AZ) is the most direct single metric for fulfillment efficiency — it already factors in volume, hours, and pay
- When a feature affects a specific fulfillment sub-function (e.g., Pack), use that sub-function's TPH and dollars, not the aggregate Fulfillment row

### When to Use TPH Tracker

- **Always read for fulfillment `labor_cost`** — provides actual TPH, actual hours, and actual dollars for Pack, Lead, IC, Support
- **Always read for OT-related features** — `Dollars` and `Hours` tabs show OT spend that could be reduced
- **Always read for variable cost per fill** — direct efficiency metric, more useful than derived calculations
- **Use for trend analysis** — weekly granularity reveals whether TPH is improving or degrading, which informs scenario assumptions
- **Volume: context and product mix ONLY** — product-level breakdown (GLP-1, Novo, Oral) supports product-scoped sizing, but **never use TPH Tracker volume sums as annual figures**. Always pull annual volume from D&F_Summary col P (see Canonical Source Rules above).

---

## Looker MCP Discovery Protocol (Nice-to-have #9)

When a metric requires Looker data (typically `turnaround`, `quality`, or new-vs-refill volume splits), **do NOT guess the LookML model name** — `get_explores` returns 404 for guesses, wasting tool calls and time.

**Correct sequence:**

1. **Identify the dashboard first.** Use `get_dashboards` with a title pattern (e.g., `"Arizona Order Vision*"`). Capture the dashboard ID.
2. **Pull the dashboard explore name.** From the dashboard metadata, find the explore reference (e.g., `order_lifecycle`).
3. **Pull the model from a tile.** Use `run_dashboard` with the dashboard ID; the first tile's `model` field is the LookML model name (e.g., `order_processing_success`).
4. **Now call `get_explores` and `get_dimensions`** with the known model name to discover available fields.

**Known dashboards for common Hims sizings:**

| Topic | Dashboard | ID | Explore |
|---|---|---|---|
| New vs refill order mix | Arizona Order Vision 2.0 | 4872 | `order_lifecycle` |
| New order trajectory | New Order Vision By Level 2 | 5053 | `order_lifecycle` |
| Order lifecycle summary | Order Lifecycle - Summary | 3689 | `order_lifecycle` |
| Dispatch-to-deliver timing | Order Lifecycle - Dispatch to Deliver | 4462 | `order_lifecycle` |

**If the dashboard ID isn't documented above**, search the workspace `Product Context/Foundational Discovery/Reporting/Existing Outbound Fulfillment Report Audit.md` for "looker" + the topic — dashboard IDs are listed there with their explore names.

**Cost discipline:** Burning 10+ tool calls guessing model names is wasteful. Always start with `get_dashboards` and walk back from a known dashboard.

---

## Rule of Thumb (Must-Fix #6)

**TPH Tracker is the default labor cost source.** Win Calculator is for pharmacy step-level decomposition only (because TPH Tracker doesn't break pharmacy out per step). For any fulfillment labor question, default to TPH Tracker.

---

## Multi-Pool Extraction Protocol (Must-Fix #5)

When `metric_category == labor_cost`, **always pull all three labor pools' weekly TPH series upfront**, not just the one tied to the specific feature mechanism. This prevents the "extrapolate Pack variance to whole pool" hack and surfaces differential addressability across pools (Pack typically has highest variance, AZ Pharmacy often has lowest).

**Required pulls for labor_cost:**

| Pool | OH (rows ~22-26) | AZ (rows ~108-112) | Why |
|---|---|---|---|
| Pack | Pack (TPH) row | Pack (TPH) row | Direct beneficiary of WIP signals / dashboards |
| Pharmacy aggregate | Pharmacy (TPH) row | Pharmacy (TPH) row | Upstream visibility benefit; needed for full labor pool sizing |
| Fulfillment aggregate | Fulfillment (TPH) row | Fulfillment (TPH) row | Non-Pack fulfillment roles (Lead, IC, Support) — also affected by visibility |

**For each pool × site:** compute Mean, Max, and `gap = (Max - Mean) / Mean`.

**For variance-closure model:** weighted average by pool labor share. See `scenario-logic.md` "Model Pattern: Variance-Closure" for the math.

---

## Data Source Priority

When multiple sources provide overlapping data, follow this priority:

| Data Point | Primary Source | Fallback | Why |
|---|---|---|---|
| Pack TPH / UPH | TPH Tracker `D&F TPH` (actual weekly, FY avg 30.5) | Win Calculator (static 34) | Actuals > static estimates. Win Calculator may be stale. |
| Fulfillment labor dollars | TPH Tracker `D&F TPH` (actual Reg + OT + HSV) | Derived from UPH × rate (Win Calculator) | Direct observation > derived. Captures OT and HSV that derivation misses. |
| Pharmacy step-level UPH | Win Calculator `Sheet1` | — | TPH Tracker aggregates pharmacy by role, not by step. Win Calculator is the only per-step source. |
| OT spend | TPH Tracker `Dollars` tab | — | Only source with weekly OT breakdown by role. |
| Shipping cost / volume | Project Entitlement `Trans_Summary` | — | TPH Tracker does not cover shipping. |
| Fulfillment cost / volume (financial plan) | Project Entitlement `D&F_Summary` | — | Use for budget-level figures and 3PL data. TPH Tracker covers internal sites only. |
| Variable cost per fill | TPH Tracker `D&F TPH` row 89 (OH) | Project Entitlement `D&F_Summary` | TPH Tracker is weekly actual; Project Entitlement is monthly forecast. |

**When sources conflict:** Surface the delta. Example: "Win Calculator shows Pack UPH of 34, but TPH Tracker actuals show FY avg of 30.5 — a 10% gap. Using TPH Tracker actuals as the baseline. `[Assumption: Pack TPH = 30.5 — sourced from TPH Tracker FY26 actuals]`"

---

## Physical Limits Reference Table

Used by the Quality Gate Validator (Check 5: physical plausibility) and the parent thread for sanity checks. WARN triggers at 80% of the ceiling; FAIL triggers at or above the ceiling.

| Metric Category | Process Step / Lever | Metric | Ceiling (FAIL at or above) | Source / Rationale |
|---|---|---|---|---|
| `labor_cost` | Pack | Pack TPH | 55 tasks/hr | FY26 avg is 30.5 (TPH Tracker). 55 = ~80% improvement — no known warehouse achieves this without full automation. |
| `labor_cost` | Data Entry | Data Entry UPH | 250 tasks/hr | Win Calculator baseline: 120. 250 = ~2× improvement — implies near-full automation. |
| `labor_cost` | DUR | DUR UPH | 450 tasks/hr | Win Calculator baseline: 224. 450 = ~2× improvement. |
| `labor_cost` | PV1 | PV1 UPH | 550 tasks/hr | Win Calculator baseline: 291. 550 = ~90% improvement. |
| `labor_cost` | Manual Dispense | Manual Dispense UPH | 120 tasks/hr | Win Calculator baseline: 54. 120 = ~2.2× improvement. |
| `labor_cost` | PV2 | PV2 UPH | 250 tasks/hr | Win Calculator baseline: 125.4. 250 = ~2× improvement. |
| `labor_cost` | Any | Improvement % | 60% | No single initiative has historically delivered >50% labor reduction at Hims scale. |
| `shipping_cost` | Any | Cost reduction % | 40% | Carrier optimization at scale rarely exceeds 30%. 40% is extreme upper bound. |
| `fulfillment_cost` | Any | Variable cost reduction % | 50% | Variable cost includes labor + materials — 50% reduction implies near-full automation. |
| `quality` | Any | Error reduction % | 95% | Errors cannot be reduced to zero. 95% reduction = 20× improvement — implies near-perfect automation. |
| `turnaround` | Any | Cycle time reduction % | 70% | Cycle time has hard physical floors (mixing, cooling, curing for compounding; transit for shipping). |
| Any | Any | Adoption rate | 100% | Practical adoption ceiling. 100% is theoretically possible but should WARN at 95% — 3PLs, edge cases, and exceptions always exist. |

**If the feature targets a step/metric not in this table:** The validator should WARN (not FAIL) and note: "No physical limit defined for [step/metric]. Plausibility check is based on general reasonableness only."

**Staleness rule:** These ceilings are based on FY26 baselines. If baselines shift materially (e.g., automation deployed), update this table. The TPH Tracker actuals are the authoritative source for current baselines.

---

## MCP Call Format

All sheet reads use the `google-workspace` MCP server:

```
Tool: read_sheet_values
Server: google-workspace
Arguments: {
  "spreadsheet_id": "[ID from sections above]",
  "user_google_email": "you@example.com",
  "range_name": "[tab]![range]"
}
```

**If MCP is unavailable:** Block. Tell the user: "Cannot reach the Google Workspace MCP. Check the MCP connection and retry."
