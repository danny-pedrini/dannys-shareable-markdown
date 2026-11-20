# Domain Roadmap Generator — Evals

Binary pass/fail criteria run automatically during QA (Step 7, Gate 3) on every invocation.

## Adopted Evals

| ID | Eval | Pass Criteria | Added |
|---|---|---|---|
| 1 | `initiative_data_matches_source` | Every initiative name, impact figure, and eng estimate in the document matches the Google Sheet source exactly | 2026-06-08 |
| 2 | `delivery_forecast_math_correct` | Delivery month for each initiative is consistent with the stated capacity assumptions and sequencing | 2026-06-08 |
| 3 | `h2_savings_sum_correct` | H2 savings goal = sum of annual impact for initiatives with 2026 delivery dates | 2026-06-08 |
| 4 | `north_star_math_correct` | Per-shipment target = H2 savings goal / annual shipment volume | 2026-06-08 |
| 5 | `no_fabricated_numbers` | Every metric in the goals table traces to a named data source | 2026-06-08 |
| 6 | `losses_header_present` | "Losses" header exists in Section 5 even when empty | 2026-06-08 |
| 7 | `below_line_has_descriptions` | Every appendix item has both a Description and a Current Status | 2026-06-08 |
| 8 | `no_post_hj_mvp_rationale` | No below-the-line item uses "post-HighJump MVP enhancement" as its rationale | 2026-06-08 |
| 9 | `delivery_forecast_script_ran` | The Python delivery forecast script (`delivery_forecast.py`) executed successfully and produced valid JSON output with a `schedule` array and `capacity_by_month` object | 2026-06-09 |

## Proposed (Not Yet Adopted)

_None yet. Run `/evals-advisor` after a skill invocation to get suggestions._
