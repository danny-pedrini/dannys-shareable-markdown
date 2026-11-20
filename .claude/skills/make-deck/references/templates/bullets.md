# Template: bullets

The workhorse content slide. Default choice when you don't have a reason to pick something more structured.

## When to use
- Any content slide that's a list of points
- Default fallback when 2-column or do/don't doesn't fit

## Outline schema
```json
{
  "template": "bullets",
  "title": "Migration milestones in flight",
  "lead": "Two milestones remain; both tracking to June.",
  "bullets": [
    "Milestone 3 ships June 7",
    "Milestone 4 ships June 14",
    "Milestone 5 is blocked"
  ],
  "notes": "Milestone 3 = MedMatch visit-id rewrite, [teammate] owns it, ETA June 7. Milestone 4 = GoFlow event backfill, [teammate] owns it, ETA June 14. Milestone 5 = PHD facade cutover, blocked on RFC approval. Mention the dependency in the room."
}
```

## Content rules (headline bullets, narrative in notes)
- `title`: sentence case, 3-6 words
- `lead`: optional one-line setup. Use when the bullets need a frame.
- **Bullets are HEADLINES, not sentences.** Each bullet is 3-5 words. The detail (names, dates, sources, qualifiers) lives in `notes`, not on the slide. The speaker delivers the narrative; the slide is the backdrop.
- Max 5 bullets per slide. Design target 3-4. Validator caps at 6 but rarely hit it.
- If you can't shorten a bullet to 5 words, you're putting two ideas in one bullet. Split, or push the second idea into notes.
- Bullets cite numbers as: just the number on the slide ("$1M"), full citation in notes ("$1M annual savings per finance modeling, May 2026").

## Voice-vs-slide split (the rule)
For every bullet, ask: "Is this the *headline*, or the *story*?"
- Headline (on slide): "Eligibility filters work"
- Story (in notes): "Eligibility filters are license, treatment scope, role, and capacity. All four enforce correctly today. Verified in emr_service via Code Explorer."

The voice-over carries everything except the headline. The audience reads the slide in 2 seconds and then listens to the speaker. Don't make them read a paragraph while you talk over them.

## Visual spec (auto-applied)
- White background
- Title top-left, 36 pt Bold ink
- Optional lead at 13 pt (narrative line, kept small so bullets dominate)
- **Bullets at 20 pt Bold with `• ` prefix and paragraph spacing** (headline treatment)
- Confidentiality footer auto-added

## Common mistakes
- Sentences instead of headlines (rewrite as 3-5 word phrase, push detail to notes)
- 7+ bullets crammed onto one slide (split, don't shrink)
- Naked numbers on slide without speaker-note citation
- Restating the title in the first bullet
