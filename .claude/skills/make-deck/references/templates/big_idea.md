# Template: big_idea

A single bold statement, large type, centered. Used for the "one thing to remember" moment of a deck. Pure storytelling: less words, more impact. The visual is the message.

## When to use
- The headline takeaway of the deck (often appears mid-deck or as the close)
- A bold claim or prediction the deck is built around
- A reframe moment ("This is not a tech problem; it's an ops problem")
- The decision you're asking for, stated plainly

## When NOT to use
- Anything that needs supporting points (use bullets or three_card)
- Customer quotes (use pull_quote)
- A number-driven headline (use key_stat)

## Outline schema
```json
{
  "template": "big_idea",
  "statement": "Migration is 83% done. The last 17% is the entire risk surface.",
  "attribution": null
}
```

`attribution` is optional — use it when the statement is a thought, observation, or position attributed to someone with explicit sourcing.

## Content rules
- ≤15 words (validator-enforced; the whole point is less words)
- 6 words or fewer → renders at 44 pt (maximum impact)
- 7-10 words → 36 pt
- 11-15 words → 28 pt
- One sentence, no semicolons, no parenthetical asides
- Sentence case ("Migration is 83% done", not "Migration Is 83% Done")
- Attribution only if you have explicit source for the quote/claim. Per your CLAUDE.md (or your operator profile), never invent attribution.

## Visual spec (auto-applied)
- White background, no footer (intentional clean)
- Statement centered horizontally and vertically
- Sage accent (`#0097A7`) Bold, large type
- Optional attribution below in small ink type, prefixed with "— "

## Common mistakes
- Writing 20-30 words and trying to make the font smaller — cut the statement, don't shrink it
- Using `big_idea` for a topic title — that's a `section_divider`. `big_idea` is for a CLAIM or POSITION, not a topic
- Two consecutive big_idea slides — pick one and cut the other
- Attribution for a position the user holds themselves — drop the attribution; it reads as artificial
