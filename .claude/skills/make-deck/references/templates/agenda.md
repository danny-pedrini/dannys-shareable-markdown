# Template: agenda

The "table of contents" slide. Tells the audience the shape of the argument they're about to hear. Goes at slide 3 (after cover and exec_summary) of every deck with 8+ slides.

## When to use
- ALWAYS for decks ≥8 slides
- Slide 3 specifically (cover → exec_summary → agenda → content)
- 3-6 sections — the validator rejects fewer than 3 (not useful) or more than 6 (too many to remember)

## When NOT to use
- Decks ≤7 slides (audience can hold the shape in their head)
- Decks read async (a written deck has navigation other ways)

## Outline schema
```json
{
  "template": "agenda",
  "title": "Agenda",
  "sections": [
    "Where we are",
    "What changed",
    "What's next",
    "What's at risk"
  ]
}
```

`title` defaults to "Agenda" if omitted.

## Content rules
- Sections are 2-4 word labels, sentence case ("Where we are", not "Where We Are" or "An overview of the current state of the project")
- Sections should match the section_divider or moving_blueprint titles that appear later in the deck — same word-for-word, so the audience can pattern-match
- Don't list every slide title — list the section headings
- Parallel structure: all sections noun phrases OR all questions, not mixed

## Visual spec (auto-applied)
- White background
- "Agenda" title at top-left, 22 pt Bold ink
- Numbered list, 01–06, left-aligned
- Numbers in sage accent (`#0097A7`), 24 pt Bold
- Section names in ink, 18 pt Bold
- Thin gray divider line between rows
- Confidentiality footer

## Common mistakes
- 8+ sections (the validator rejects). If you have 8 sections, the deck is two decks.
- Section names that are sentences ("First we'll cover the current state of the migration") — cut to "Current state"
- Mismatched between agenda and actual section titles ("Where we are" in agenda becomes "Migration health" later — pick one and use it twice)
- Putting agenda at slide 1 or slide 2 — it goes at slide 3 after the cover and exec_summary
