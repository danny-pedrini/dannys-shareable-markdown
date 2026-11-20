# Template: section_divider

Beige full-bleed slide between major sections. Resets the viewer's attention; signals a topic shift.

## When to use
- Decks >10 slides: insert before each new major section
- Final slide: "Next up" or "Discussion" pattern
- Skip in decks <8 slides; they don't need pacing

## Outline schema
```json
{
  "template": "section_divider",
  "title": "Where we are",
  "subtitle": "Migration health, capacity, risk"
}
```

## Content rules
- `title`: 2-5 words, sentence case, no period. Verb optional.
- `subtitle`: optional one-line preview of what's coming. Skip if obvious from title.
- No bullets, no logos, no footer (intentional — divider slides are visual breaths)

## Visual spec (auto-applied)
- Beige (`#EEE2D6`) full background
- Title centered, 40 pt Bold ink
- Subtitle centered below title, 22 pt Regular ink
- No footer (style guide explicitly omits it on dividers)

## Common mistakes
- Section titles that are full sentences ("Here is where we are in the migration")
- Using as a content slide ("Where we are: 83% done, ETA June, blocker is X") — that belongs on a bullets slide
- Stacking two dividers back-to-back (one section = one divider)
