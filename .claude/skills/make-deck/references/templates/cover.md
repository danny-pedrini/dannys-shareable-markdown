# Template: cover

The opening slide of every deck. Sets the visual identity and frames audience expectations.

## When to use
- Always slide 1
- Never anywhere else

## Outline schema
```json
{
  "template": "cover",
  "title": "PHD migration status",
  "subtitle": "Q2 checkpoint for cpo, May 13 2026"
}
```

## Content rules
- `title`: ≤7 words, sentence case, no period
- `subtitle`: audience + date pattern is strongest ("Q2 checkpoint for cpo, May 13 2026"). Optional.
- No bullets, no body copy. The cover is identity, not content.

## Visual spec (auto-applied)
- Dark ink (`#1C1C1C`) background
- White Poppins Bold title at 44 pt, top-left at 40/180 pt
- Beige (`#EEE2D6`) subtitle at 22 pt
- "hims & hers" wordmark bottom-right (placeholder until brand asset wired in v2)

## Common mistakes
- Putting a TL;DR on the cover (that's slide 2's exec_summary)
- Long titles ("Status update on the patient health data migration project for the executive team") — cut to 4-7 words
- Title case ("Migration Status") — use sentence case ("Migration status")
