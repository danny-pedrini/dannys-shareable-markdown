# Template: two_column

Side-by-side comparison. Use whenever the structure is "X vs Y", "before vs after", "shipped vs slipped", "option A vs option B".

## When to use
- Compare two states, options, audiences, time periods
- Show tradeoffs (option A pros vs option B pros)
- Cleaner than a bullets slide for genuinely paired content

## Outline schema
```json
{
  "template": "two_column",
  "title": "Q2 delivery",
  "left_header": "Shipped",
  "left_bullets": ["Helix Phase 1", "Patient 360 v1", "Schema versioning"],
  "right_header": "Slipped",
  "right_bullets": ["MedMatch rewrite (June)", "Idempotency keys RFC (July)"]
}
```

## Content rules
- `title`: sentence case, frames the comparison ("Q2 delivery", not "Shipped vs slipped")
- `left_header` / `right_header`: 1-2 words each, parallel structure ("Shipped" / "Slipped", not "Shipped" / "Things that didn't ship")
- Bullets: max 5 per column. Parallel structure across columns (same level of specificity).
- Don't use for 3+ options — that's a different layout (consider repeated bullets slides instead).

## Visual spec (auto-applied)
- White background
- Title top-left, 36 pt Bold ink
- Two columns, equal width, 30 pt gap
- Column headers at 22 pt Bold sage accent (`#0097A7`)
- Bullets at 16 pt with `• ` prefix
- Confidentiality footer auto-added

## Common mistakes
- Asymmetric columns (5 bullets on left, 1 on right) — fix the balance or use a different template
- Non-parallel headers ("What we built" / "Roadblocks") — make them grammatically symmetric ("Built" / "Blocked")
- Forcing a comparison that isn't really paired — if the right column is "and some other stuff", use a bullets slide
