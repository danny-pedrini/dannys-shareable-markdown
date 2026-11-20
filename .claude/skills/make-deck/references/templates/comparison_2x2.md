# Template: comparison_2x2

A 2x2 matrix with axes and labeled quadrants. The most common strategic-thinking visualization. Use when content naturally splits across two dimensions.

## When to use
- Effort vs impact (prioritization)
- Likelihood vs severity (risk register)
- Build vs buy by complexity vs criticality
- Now vs later by cost vs value
- Any 2-dimensional categorization where 4 buckets capture the space

## When NOT to use
- 3 dimensions (use multiple slides or a different framework)
- A single ordered list (use bullets or flow_steps)
- A simple "this versus that" (use two_column)
- More than 4 buckets (use a different table layout)

## Outline schema
```json
{
  "template": "comparison_2x2",
  "title": "Q3 initiative prioritization",
  "x_left": "Low effort",
  "x_right": "High effort",
  "y_bottom": "Low impact",
  "y_top": "High impact",
  "quadrants": [
    {"header": "Quick wins", "body": "Patient chart preloader; intake answer prefill"},
    {"header": "Major bets", "body": "PHD full migration; TPA cutover"},
    {"header": "Fill-ins", "body": "Footer date format; cron cleanup"},
    {"header": "Money pits", "body": "Theme master swap; non-Slides exports"}
  ]
}
```

Quadrant order is **TL, TR, BL, BR** (top-left, top-right, bottom-left, bottom-right). The validator enforces exactly 4 entries.

## Content rules
- Axis labels: 1-3 words, parallel structure ("Low effort"/"High effort", not "Low effort"/"Significant work required")
- Quadrant headers: 1-3 words, descriptive of the bucket ("Quick wins", "Major bets")
- Quadrant body: optional 1-2 sentence description or 2-3 examples; ≤15 words per quadrant
- All four quadrants should be filled (an empty quadrant signals a flawed framework — pick different axes)
- Headers should be parallel structure across quadrants

## Visual spec (auto-applied)
- White background
- Title at top-left, 22 pt Bold ink
- Sage-tint (`#F5FAF6`) matrix with white gridlines dividing the 4 cells
- Axis labels outside the matrix in sage accent (`#0097A7`) Bold
- Quadrant headers in ink Bold, 12 pt
- Quadrant body in ink regular, 10 pt
- Confidentiality footer

## Common mistakes
- Axes that aren't actually orthogonal (e.g., "Important" vs "Urgent" works; "Important" vs "Strategic" doesn't because they overlap)
- Empty quadrants — means your axes don't carve the space cleanly; pick different axes
- Quadrant bodies that run 4+ sentences — cut to one sentence or 2-3 examples
- Mixed framing (one quadrant has examples, another has rules) — pick a treatment and apply uniformly
- Backwards axes — convention is "good" in the top-right. "Low impact" should be at the bottom, not the top.
