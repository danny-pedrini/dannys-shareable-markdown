# Template: exec_summary

The TL;DR slide. Lands at slide 2 of every exec-facing deck. McKinsey/BCG default: answer-first, before any setup.

## When to use
- Slide 2 of any deck going to skip-level execs, the CPO, your VP Eng, the SVP Eng, or the CMO
- Skip for purely internal team decks <5 slides

## Outline schema
```json
{
  "template": "exec_summary",
  "title": "Executive summary",
  "lead": "PHD migration is 83% complete; remaining 17% is blocked on MedMatch visit-id rewrite ([teammate], ETA June).",
  "principles_header": "Launch principles",
  "cards": ["Expand access", "Drive growth", "Reduce friction"]
}
```

## Content rules
- `title`: usually literally "Executive summary"; sometimes "TL;DR" or "Top line"
- `lead`: ONE sentence with the answer. Numbers need unit + source + date.
- `principles_header`: 2-4 words ("Launch principles", "Three priorities", "What we owe you")
- `cards`: exactly 1-3 short, verb-led phrases (max 3). Each card is one principle or one priority. Cards render as bold sage `#0097A7` text on white inside a sage-tint panel.

## Visual spec (auto-applied)
- White background
- Title at top-left, 36 pt Bold, `#1C1C1C`
- Lead paragraph directly under title, 18 pt
- Sage tint (`#F5FAF6`) panel spanning width
- Principles header centered inside panel, 24 pt Bold sage accent (`#0097A7`)
- 1-3 white rounded-rect cards inside panel, 200 pt tall, equal width
- Confidentiality footer auto-added

## Common mistakes
- 4+ cards (max is 3 — McKinsey rule of three)
- Cards as full sentences instead of verb-led phrases ("We are going to expand access" → "Expand access")
- Lead paragraph >2 sentences (one is plenty)
- Vague leads ("Migration is progressing well") — needs the number and the blocker
