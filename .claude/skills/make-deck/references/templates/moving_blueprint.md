# Template: moving_blueprint

Section divider with navigation context. Shows every section of the deck as a horizontal pill strip, with the current section highlighted in sage. Replaces the plain `section_divider` for decks of 12+ slides where the audience needs to remember the structure.

## When to use
- ALWAYS for decks ≥12 slides — replace every `section_divider` with a `moving_blueprint`
- Long technical walkthroughs where the audience easily loses the thread
- Decks built from spines B (recommendation) or D (pre-mortem) where structure carries meaning

## When NOT to use
- Decks ≤11 slides (use `section_divider`; the spine is short enough to hold mentally)
- Decks with only 2 sections (the strip looks weird with 2 pills)

## Outline schema
```json
{
  "template": "moving_blueprint",
  "sections": [
    "Where we are",
    "What changed",
    "What's next",
    "What's at risk"
  ],
  "current_index": 0,
  "subtitle": "Migration health, capacity, risk posture"
}
```

`current_index` is zero-based. The first section is `current_index: 0`.

## Content rules
- `sections` MUST match the agenda slide's `sections` word-for-word (audience pattern-matching)
- `current_index` increments by 1 each time the blueprint appears
- `subtitle` is optional — one line previewing what's in the section
- 3-6 sections (validator caps at 6)

## Visual spec (auto-applied)
- Beige (`#EEE2D6`) full background
- Horizontal strip at top with one pill per section
- Current pill: sage accent (`#0097A7`) fill, white bold text
- Other pills: white fill, ink text (small section number above section name)
- Big current-section title centered below the strip, 30 pt Bold ink
- Subtitle below title if provided, 14 pt ink
- NO footer (intentional — it's navigation, not content)

## Common mistakes
- Mismatched `sections` between agenda and blueprint — keep them identical
- Forgetting to increment `current_index` — every blueprint should have a different index
- Using the same blueprint slide twice — that's a copy-paste mistake; each section gets its own with its own `current_index`
- Wrong number of sections — must match agenda count
- Empty `current_index` field — validator catches but it's a frequent typo
