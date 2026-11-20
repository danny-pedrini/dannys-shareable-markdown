# Scenario Construction Logic

Reference document for feature-impact-sizing skill. Loaded by the orchestrator during Phase 6 (scenario construction) and Phase 8 (confidence assignment).

---

## Scenario Assumption Decision Tree

For each variable factor in the model, walk this tree in order. The first matching condition wins.

```
For each variable factor:

  IF a HIGH-confidence SME assumption applies to this factor:
    → Base   = SME value
    → Low    = SME value × 0.7 (sensitivity floor; or use SME-stated lower bound if given)
    → High   = SME value × 1.3 (sensitivity ceiling; or use SME-stated upper bound if given)
    → Rationale: "Base anchored to internal data ([SME source]); benchmarks corroborate at X–Y%."
    → External benchmarks become sanity checks only.

  ELSE IF a MEDIUM-confidence SME assumption applies (typically a stated range, e.g., "10–15%"):
    → Base   = tier-weighted benchmark average, CLAMPED to the SME range
    → Low    = MAX(SME range lower bound, conservative benchmark)
    → High   = MIN(SME range upper bound, top-tier benchmark)
    → Rationale: "Benchmark-anchored within SME-stated range ([SME source])."

  ELSE IF only a LOW-confidence SME assumption (vendor claim, gut feel) applies:
    → Base   = tier-weighted benchmark average (ignore the SME claim)
    → Low    = 50% of Base, or most conservative credible benchmark
    → High   = upper bound from top-tier source, CAPPED at 50% of vendor-claimed value
    → Rationale: "Benchmark-anchored; vendor/gut claim included as sensitivity case only."

  ELSE (no SME input for this factor):
    → Base   = tier-weighted benchmark average (A=3× weight, B=2×, C=1×; exclude LOW applicability)
    → Low    = ~50% of Base, or most conservative credible benchmark
    → High   = upper bound from highest-tier source, assuming full adoption
    → Rationale: "External benchmark-anchored; no internal SME input available."
```

---

## SME Confidence → Scenario Treatment

Confidence is assigned during intake (Phase 1.5). It drives scenario construction as follows:

| SME Confidence | Definition | What It Triggers in Scenario Construction |
|---|---|---|
| **HIGH** (measured internal data) | Time study, pilot result, A/B test, Datadog/Looker data from Hims operations | Anchors Base directly; benchmarks become sanity checks. Low/High = ±30% of SME value (or SME-stated bounds). |
| **MEDIUM** (credible SME estimate) | Informed range from a named SME (ops lead, engineer, pharmacist) — typically expressed as a range | Clamps benchmark-anchored Base to the SME range. Low/High bounded by SME range endpoints. |
| **LOW** (vendor claim or gut feel) | Vendor demo claim, RFP number, or unsubstantiated estimate with no data backing | Caps High at 50% of claimed value; otherwise ignored. Base driven by benchmarks only. |

---

## Tier-Weighted Benchmark Averaging

When computing the benchmark-anchored Base value, weight by source quality tier:

| Tier | Weight | Examples |
|---|---|---|
| A | 3× | McKinsey, Gartner, Forrester, peer-reviewed, government data |
| B | 2× | Supply Chain Dive, trade associations, reputable vendor research with data |
| C | 1× | Blog posts, vendor marketing, unrecognized domains |

**Exclusion rule:** Drop any benchmark rated **LOW applicability** before averaging — they distort more than they inform.

**Formula:**

```
tier_weighted_avg = Σ(weight_i × improvement_value_i) / Σ(weight_i)

where weight_i = 3 if tier A, 2 if tier B, 1 if tier C
and only benchmarks with MEDIUM or HIGH applicability are included
```

**Worked example:**

| # | Source | Tier | Improvement | Applicability | Weight |
|---|---|---|---|---|---|
| 1 | McKinsey report | A | 15% | HIGH | 3 |
| 2 | Supply Chain Dive | B | 12% | HIGH | 2 |
| 3 | Vendor white paper | C | 20% | MEDIUM | 1 |
| 4 | Industry blog | C | 25% | LOW | excluded |
| 5 | MHI benchmark | B | 10% | MEDIUM | 2 |

```
tier_weighted_avg = (3×0.15 + 2×0.12 + 1×0.20 + 2×0.10) / (3 + 2 + 1 + 2)
                  = (0.45 + 0.24 + 0.20 + 0.20) / 8
                  = 1.09 / 8
                  = 0.136 → 13.6%
```

Benchmark #4 excluded (LOW applicability). Result: Base = 13.6%.

---

## Scenario Construction Rules

**Always apply these when building the proposed scenario assumptions table:**

1. **Adoption rate treatment** — Apply the same decision tree to adoption rate as to improvement percentage. Respect any SME-stated constraints (e.g., "3PLs won't adopt" → cap adoption at internal-sites-only percentage).

2. **Rationale documentation** — Every variable factor's rationale MUST cite which decision tree path was taken: `HIGH SME`, `MEDIUM SME`, `LOW SME`, or `No SME`. Include the specific source (e.g., "[SME: [Ops Program director] — time study Q1 2026]" or "Tier-weighted avg of 3 A/B benchmarks").

3. **Ambiguous conflicts** — If an SME assumption and benchmark range genuinely conflict and the decision tree resolution feels forced, surface both to the user in the Human Review Gate. Don't silently pick one. Present: "SME says X, benchmarks say Y — which should anchor the model?"

4. **Low < Base < High** — Every variable factor must satisfy this ordering. If the decision tree produces an inversion (rare — usually means the SME range and benchmark range barely overlap), flag it and ask the user to resolve.

5. **Override documentation** — If the user adjusts a scenario value during the Human Review Gate, tag it: `[Override: User set [factor] [scenario] to [value] — rationale: "..."]`. Overrides persist into the sheet's Assumptions tab Source/Rationale column.

---

## Model Pattern: Variance-Closure (for visibility / signal features with internal performance data)

**When to use this pattern instead of the generic `improvement_pct × realization_rate` model:**

| Trigger | Why |
|---|---|
| `metric_category == labor_cost` | Variance closure only makes sense for labor productivity (not materials, shipping, etc.) |
| Hims has internal multi-period TPH / UPH performance data (e.g., TPH Tracker) | The variance gap is a *measured* number, not a benchmark estimate |
| Feature mechanism = "make underperformance visible" or "close best-vs-mean gap" (dashboards, WIP signals, monitoring, alerting) | The closure mechanism is the dashboard surfacing variance the operator can act on |

If all three triggers fire, **prefer variance-closure over the heuristic `improvement_pct × realization_rate` framing.** It's better-anchored, more defensible to stakeholders, and avoids the "realization_rate is a fudge factor" problem.

**Variance-closure factor structure:**

```json
{
  "factors": [
    {
      "name": "annual_addressable_labor_cost",
      "is_constant": true,
      "value": 40000000,
      "unit": "$",
      "derivation": { "method": "sum", "components": [...] }
    },
    {
      "name": "weighted_variance_gap",
      "is_constant": true,
      "value": 0.1881,
      "unit": "%",
      "source": "Pool-weighted best-vs-mean TPH gap from TPH Tracker, 20 wks FY26 YTD",
      "derivation": {
        "method": "formula",
        "formula": "pool_pharm_share * pharm_gap + pool_ff_share * ff_gap",
        "compute": "pool_pharm_share * pharm_gap + pool_ff_share * ff_gap",
        "inputs": {
          "pool_pharm_share": 0.670,
          "pharm_gap": 0.1748,
          "pool_ff_share": 0.330,
          "ff_gap": 0.2151
        }
      }
    },
    {
      "name": "variance_closure_pct",
      "is_constant": false,
      "low": 0.30,
      "base": 0.50,
      "high": 0.70,
      "unit": "%",
      "rationale": "Share of variance gap closed by the feature. Calibrated against SME anchors: [Ops Program director] 10% effective uplift ÷ 18.81% gap ≈ 53% closure (Base); [Director of Pharmacy & Fulfillment Product] 15% ÷ 18.81% ≈ 80% (above High)."
    }
  ]
}
```

**Computing the variance gap (instructions for the orchestrator in Phase 6):**

1. From the TPH Tracker (or equivalent), pull multi-week series for each relevant labor pool (Pack, Pharmacy aggregate, Fulfillment aggregate, etc.).
2. For each pool × site combination, compute: `gap = (max_tph - mean_tph) / mean_tph`.
3. Compute labor-share weights per pool: `pool_labor = volume / mean_tph × blended_rate`.
4. Within-pool weighted gap: `pool_gap = Σ (site_labor_share × site_gap)`.
5. Cross-pool weighted gap: `overall_gap = Σ (pool_labor_share × pool_gap)`.
6. This `overall_gap` becomes the `weighted_variance_gap` constant in the JSON.

**Calibrating variance_closure_pct against SME anchors:**

If an SME provides a "throughput uplift" estimate (e.g., [Ops Program director]'s "10% conservative"), translate it to an implied closure percentage:

```
implied_closure = sme_uplift_pct / variance_gap
```

Example: [Ops Program director] says 10% throughput uplift; variance_gap = 18.81% → implied_closure = 53%. Set Base ≈ 50%. [Director of Pharmacy & Fulfillment Product] says 15% → implied_closure = 80%. Set High ≈ 70-75%.

**Why this is better than `improvement_pct × realization_rate`:**

| Issue with old pattern | How variance-closure fixes it |
|---|---|
| `improvement_pct` was a benchmark estimate from outside Hims | `variance_gap` is *measured* in Hims data |
| `realization_rate` was a heuristic discount with no anchor | `variance_closure_pct` is a clear mechanistic question ("what % of observed variance does this feature close?") |
| Stakeholder pushback: "where did 75% come from?" | Stakeholder defense: "[Ops Program director]'s 10% anchor implies 53% closure → Base 50%; [Director of Pharmacy & Fulfillment Product]'s 15% implies 80% → High 70%" |
| Single uniform value applied to entire labor pool | Per-pool gaps computed and weighted; differential addressability surfaced |

**Known limitation:** Closure % is applied uniformly across the pool. In reality, it varies by sub-queue (Pack benefits most from WIP signals; upstream pharmacy steps benefit less). Document this in Assumptions & Risks section. A per-sub-queue model is the next-rung-up rigor if the project scope warrants it.

---

## Confidence Level Assignment

Assigned during synthesis (Phase 8) based on source quality and scenario spread.

| Confidence | Source Threshold | Uncertainty Range | Use For |
|---|---|---|---|
| **HIGH** | ≥2 A-tier sources corroborating | <20% spread (High/Low ratio <1.5×) | Roadmap prioritization decisions. Monitor actuals post-launch. |
| **MEDIUM** | 1 A-tier or ≥2 B-tier sources | 20-50% spread | Directional prioritization. Run a focused validation before committing eng resources. |
| **LOW** | No A/B-tier sources, or all benchmarks LOW applicability | >50% spread | Do NOT use for prioritization. Run structured discovery first. |

**Uncertainty range calculation:**

```
uncertainty_range = (high_result - low_result) / base_result × 100
```

If `uncertainty_range` > 50%, confidence cannot exceed MEDIUM regardless of source quality. If > 100%, confidence is forced to LOW.

**Confidence overrides:**
- Research pipeline timed out → cap at LOW (no benchmarks to validate against)
- All SME inputs are LOW confidence and no benchmarks → cap at LOW
- User overrode any FAIL quality gate check → cap at MEDIUM (structural concern acknowledged but unresolved)

### Validation Path by Confidence Level

For each validation recommendation, include all four fields:

| Confidence | Recommendation Template |
|---|---|
| **HIGH** | **Action:** Monitor actuals post-launch (Looker dashboard, weekly TPH review). **Effort:** Low. **Timeline:** Ongoing after launch. **What it reduces:** Confirms model accuracy; enables recalibration for future sizings. |
| **MEDIUM** | **Action:** [Specific validation — time study, vendor demo, limited pilot, or process observation]. **Effort:** [Low/Medium]. **Timeline:** [1-4 weeks]. **What it reduces:** [Which specific assumption or uncertainty it addresses]. |
| **LOW** | **Action:** [Structured discovery — process observation, time study, or A/B test to establish internal baselines]. **Effort:** [Medium/High]. **Timeline:** [2-6 weeks]. **What it reduces:** [Which foundational assumption is missing]. |

For MEDIUM and LOW, the specific action must name the assumption it validates — not a generic "do more research."
