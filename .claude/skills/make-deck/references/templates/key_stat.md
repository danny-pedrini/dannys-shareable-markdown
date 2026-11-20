# Template: key_stat

Single big number that IS the headline. Used to give a deck a moment of visual punch. One per deck is usually right; two if the deck is long and the numbers are dramatic.

## When to use
- A number is the most important thing to remember ("83% migrated")
- A count makes the architecture concrete ("5 Kafka listeners")
- A scale figure that grounds the story ("207k Strive customers need re-Rx")
- A timer or deadline ("June 7, ETA")

## When NOT to use
- Multiple related numbers (use a bullets slide or two_column)
- Numbers that need lots of context (the caption gets too long, becomes a bullets slide)
- Numbers without a "so what" (don't put a stat slide if the audience won't immediately know why it matters)

## Outline schema
```json
{
  "template": "key_stat",
  "stat": "5",
  "label": "Kafka listeners in emr_service",
  "caption": "Topic emr.messages.processed_messages drives task creation and downstream routing. The five listeners handle different concerns.",
  "title": "Optional small title above the stat"
}
```

`title` is the one optional field, and is often omitted because the stat IS the title.

## Content rules
- `stat`: 1-6 characters max ("5", "83%", "207k", "$0.9M", "June"). The number stays huge; long strings shrink awkwardly.
- `label`: 2-6 words explaining what the number counts. "Kafka listeners", "of patients migrated", "Strive customers needing re-Rx by July 17"
- `caption`: optional 1-2 sentence context that anchors the "so what". 14 pt, small.
- `title`: optional small title at top. Use when the number isn't self-evident.

## Visual spec (auto-applied)
- White background
- Stat: massive (120 pt) Bold sage-accent (`#0097A7`), centered
- Label: 24 pt Bold ink, centered, below stat
- Caption: 14 pt regular ink, centered, below label
- Confidentiality footer auto-added

## Common mistakes
- Stat too long ("207,000" instead of "207k") — abbreviate
- Label that's a full sentence — cut to the noun phrase
- Caption that's longer than 2 sentences — split into a bullets slide and let the stat stand alone
- Using two key_stat slides back to back — visual fatigue; interleave with other templates
