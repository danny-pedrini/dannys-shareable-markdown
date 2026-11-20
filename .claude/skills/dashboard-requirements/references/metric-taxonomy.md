# Metric taxonomy and definition conventions

How every row in a dashboard requirements document is classified and written. Used by the inventory lens subagents, the orchestrator at Step 6, and the Definitions QA group.

## Tiers

| Tier | Definition | Test |
|---|---|---|
| **Business outcome** | A lagging company outcome the hero metrics are expected to move: dollars (cost savings) or retention | Is it dollars or retention, and does it lag a hero metric? If not, it is not a business outcome |
| **Hero** | A leading indicator that determines the build's success and gates the ramp, assuming no guardrail is broken | Would you hold or advance the ramp on this number? |
| **Reconciling** | A building block used to calculate a hero metric or to reconcile it to the sizing model or to the number leadership already reads | Does it explain where the hero number comes from, rather than why it moved? |
| **Driver** | A lever investigated to explain over- or under-performance in a hero metric | If this moved, would you expect the hero to move, and would you act on it? |
| **Guardrail** | A quality, safety, or experience signal the build could degrade | Would a regression here make you pause the ramp even if the hero looked good? |

A metric sits in exactly one tier. When a candidate fits two, place it by the question the reader asks first: "did it work" (hero), "where did the number come from" (reconciling), "why did it move" (driver), "did it hurt anything" (guardrail). When a metric also plays a second role, keep one row in its primary tier and name the second role in an under-table note. Example from Provider Drafts: per-judge pass rates are reconciling for CIS and also a guardrail condition on it.

## The Definition cell

Every Definition cell states numerator over denominator, or a formula over other IDs, plus the population and the slice.

- **Population** is named, and it is either the §2 eligible population or a tighter set named in the cell ("net-eligible initial-intake submissions only").
- **Slice** names the arm comparison when one exists ("by member arm").
- **Formulas** reference IDs: "Payable hours saved, deflection (A7) × blended provider rate."
- **Constants** carry their source inline as a link: "× 2.38 minutes (AHT per messaging task, [ADS sizing SOT](url))."
- **Existing metrics** are referenced, not redefined: "References the existing Care Ops stranded-visit metric; do not redefine."

Denominator rules, checked by E13 and E14:

1. The denominator is a bounded, named population. "All tasks" fails; "all clinician tasks, fleet-wide across all categories and brands" passes.
2. The numerator is a genuine subset that can vary independently of the denominator's construction. A ratio fixed by definition is a tautology and is rewritten or cut.
3. A rate that compares arms states the comparison ("difference in creation rate, by member arm") rather than implying it.

## Grain

The unit one row of the underlying data represents. It must be a unit that instantiates for both numerator and denominator (E15).

| Grain | Use when |
|---|---|
| Member, Patient, Subscriber, Provider | The metric counts people |
| Visit / submission | The metric is asked once per visit; also the correct grain for anything prevented, because a prevented task never becomes a row |
| Task | The metric counts task rows that exist |
| Ask, Message, Write, Answer, Section instance | Per-event metrics on the patient or provider interaction |
| Hour, Portfolio | Aggregates: payable hours, dollars |

The standing example: a task-deflection rate cannot be task grain because the deflected task has no row. Its grain is the submission, and the question per submission is binary.

## Window

| Window | Use when |
|---|---|
| Per event (per task, per ask, per write) | The metric is computed at event time and aggregated later |
| Weekly | Guardrails that need a fast read |
| Monthly, plus MoM change | Hero and reconciling metrics |
| Monthly, plus cumulative | Dollars and hours |
| p50 and p90 | Latencies and elapsed times |
| N days post event | Outcomes with a defined observation window; name N |
| Survey cadence | VoC |

"However this is measured by [team] today" is acceptable when the metric already exists and the document must not redefine it.

## Good

`↑`, `↓`, `Hold`, or `Hold or ↑`. Guardrails append the alarm clause in the one approved form (see `template.md`). A metric whose direction depends on context gets `Hold` with an under-table note, not a blank cell.

## Baseline and Target

Present on Hero and Business outcomes only. A baseline is a sourced measured value with a dated, linked source (§ Citations). A target is a sourced commitment (PRD, sizing scenario, leadership decision) with a linked source. Anything else is `[TBD: owner]`.

The skill never derives a target from a sizing coefficient on its own; that derivation is a recommendation for the selection gate, not a cell value. At the selection gate, the orchestrator asks Danny whether each sizing coefficient is a target or a reconciliation value only, and records the answer. Never label a coefficient "not a target" without that answer. Example from Provider Drafts: Danny made the sizing model's 30% AHT reduction the AHT hero's target.

## IDs

- `O` for business outcomes, `A` for the first build, `B` for the second, `C` for shared guardrails.
- Numbers run continuously within a letter across all four tiers, top to bottom.
- IDs never change after the first approved draft. A moved metric keeps a note in the change log ("former C3, now A20"). A cut metric leaves a gap only if the document has been shared; before sharing, renumber.

## Placeholders

| Situation | Write |
|---|---|
| Unknown number, name, date, or threshold | `[TBD: named owner]` |
| Guardrail without a sourced threshold | `*(alarm threshold: [owner])*` |
| Conversion factor Finance must set | `[conversion factor: owner to confirm]` |
| Ramp steps not yet decided | `[TBD: Eng]` |
| Launch date with no cited program status | `[confirm with TPM]` |
| Source that MCP could not read | `[Source unreadable: paste, export, or fix MCP access]` plus the link or ID |

A bare `TBD`, an unfilled `[owner]`, or an invented value is a failure (E33, E12).

## Under-table notes

A note earns its place when it explains a definitional choice a careful, informed reader would push back on, and it adds reasoning the row does not carry. Four sentences maximum, counting a bold lead that ends in a period as one, directly under the table it explains.

Earned, from the Galen Phase 1 run:

- "A1's grain is visit or submission, not task." Explains why a deflection rate cannot be task grain.
- "B6 can falsify full chart review but cannot confirm it." Tells the reader how to interpret a high value.
- "A11 decomposes into three mutually exclusive outcomes." Explains why a blended reply rate hides which failure mode is moving.
- "A9 and A17 are the same failure at two grains." Prevents ADS from building two metrics that disagree about one event.
- "Do not build A16, A17, B3, and B4 twice." Separates runtime eval scores from production signals.

Not earned, from the same run:

- A footnote on conversion-rate methodology under Submit-to-Subscribe. Danny cut it; the definition cell already named the population and the owner of the measurement.
- Any note that restates the Definition, Grain, Window, or Good cell in prose.
- A note whose lead repeats its row before reaching its point. From the December Provider Pay Model run: "A10 reads retention two ways: most efficient and highest CQS" repeated the Definition cell, and "The retention window and cutoffs are [TBD: [Clinical Ops lead]]" repeated the Window cell. Only the clause on why blending the two cohorts hides which providers leave was earned. Lead with that reasoning instead: "A10 keeps two cohorts instead of one."
- Any note explaining a standard choice (a monthly window, a fleet-wide denominator that the cell already names).

## Recurring patterns

| Pattern | Rule |
|---|---|
| Derived metric | Dollar business outcomes and payable hours are formulas over other IDs. Write the formula; do not restate the inputs' definitions. |
| Inverse metric | A metric and its complement are one row, with the inverse named in the Definition cell. Never two rows. Provider Drafts: drafts-shown rate was 100% minus BAU trigger rate, so it became a clause in the BAU row (E38). |
| Subset metric | A metric that is one category, or a sum of categories, of another metric's distribution over the same denominator is a clause in that row. Provider Drafts: Danny redefined discard rate as the manual plus snippet share of the input-type distribution. |
| Input-only number | A number that exists only as an input to another metric's formula is not a row; name it inside that formula. Provider Drafts: messaging tasks per patient mainly fed the cost formula's volume term, and Danny cut it. |
| Same failure, two grains | Allowed when each grain answers a different question. State it in one note and require one window for both. |
| Runtime eval against production signal | Both may exist for the same concern. The note says they will not match and why. |
| Existing metric | Reference it and its owner; do not redefine. |
| Slice against metric | A dimension every metric can be cut by is a slice (§3). A new numerator or denominator is a metric. |
| Sizing coefficient | A coefficient from the sizing model is a reconciliation target, not a metric, unless the document defines a measured metric that reconciles to it. Say which metric reconciles to which coefficient. |
| Look-alike coefficients | Two sourced coefficients with similar names (visit modality, app engagement) are kept distinct; the reconciling note names which one the metric maps to (E18). |

## Citations

The document is for ADS and stakeholders, not an audit trail, so cite only sources a reader can open, as markdown links: the PRD, the sizing sheet, Looker dashboards, Confluence pages, Google Docs, Jira tickets. Never cite intake question numbers, gate or reviewer row numbers, touch-list items, synthesis finding or question numbers, acceptance test numbers, unlinked ticket IDs, or "(Danny Pedrini, Gate 3)". State a decision Danny made as the document's position, without attribution. Provenance for every fact lives in the run folder and the trace.

## What is not a metric

Instrumentation requirements, event names, alarm routing, dashboard tile layout, and experiment power calculations. These belong to Eng, ADS, or the launch plan, and the document says so in "What this is not."
