# Template: metric_grid

Multiple related numbers in a grid. Use when 2-6 stats together tell a story that no single number tells alone. A KPI dashboard slide.

## When to use
- "Here are the 4 numbers you need to remember"
- A snapshot dashboard at the top of a status update
- Funnel metrics (visits → intakes → orders → activated)
- A milestone scorecard
- Anything where multiple numbers are jointly meaningful

## When NOT to use
- One number is the headline (use `key_stat`)
- 7+ numbers (becomes unreadable — pick the 6 that matter)
- Numbers that need narrative more than display (use bullets)
- A table with rows and columns (use a real spreadsheet, not a Slides table)

## Outline schema
```json
{
  "template": "metric_grid",
  "title": "Q2 migration snapshot",
  "lead": "Headline numbers from the DX tracker, May 13 2026.",
  "metrics": [
    {"value": "83%", "label": "of records migrated"},
    {"value": "17%", "label": "remaining"},
    {"value": "5", "label": "consumers integrated"},
    {"value": "2", "label": "blockers open"}
  ]
}
```

## Content rules
- 2-6 metrics (validator: <2 → use key_stat, >6 → rejected)
- `value`: ≤6 chars max ("83%", "207k", "$0.9M", "5d", "June")
- `label`: 2-6 words, noun phrase ("of records migrated", "consumers integrated")
- All metrics should be at the same level of abstraction (don't mix percentage with raw count with currency unless intentional)
- Numbers should come from a single source/date so the snapshot is coherent
- Per your CLAUDE.md (or your operator profile): numbers need unit + source + date. Lead paragraph or caption is where source+date goes if it doesn't fit in the label.

## Layout (auto-determined by count)
- 2 metrics → 1 row × 2 cols
- 3 metrics → 1 row × 3 cols
- 4 metrics → 2 rows × 2 cols
- 5-6 metrics → 2 rows × 3 cols (5th metric leaves one empty cell, OK)

## Visual spec (auto-applied)
- White background
- Title at top-left, 22 pt Bold ink
- Optional lead at 12 pt
- Each metric in its own sage-tint (`#F5FAF6`) rounded rect
- Big number: 40 pt Bold sage accent (`#0097A7`), centered
- Label below: 11 pt Bold ink, centered
- Confidentiality footer

## Common mistakes
- Numbers without source or date — add a lead paragraph: "Per DX tracker, May 13 2026"
- Mixed units that confuse ("83%" next to "207k" next to "June" — that's three different scales). Either make units explicit or split across slides.
- Vanity metrics ("12,000 page views") next to outcome metrics ("83% migrated"). Pick a level.
- Labels longer than the number is wide — the label should fit on one line below the value
