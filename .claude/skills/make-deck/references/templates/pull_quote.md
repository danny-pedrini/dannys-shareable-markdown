# Template: pull_quote

Customer, stakeholder, or executive quote with attribution. The customer voice landing on the slide carries more weight than the speaker paraphrasing it.

## When to use
- User research findings (a quote from an interview)
- Customer feedback (NPS verbatim, support transcript)
- Executive direction ("a skip-level exec said in last week's e-team: ...")
- Provider/clinician quote in a Care deck
- Anywhere the source's own words have more impact than your summary

## When NOT to use
- Made-up quotes or composite quotes — per your CLAUDE.md (or your operator profile), attribution must be verifiable
- Statistics or claims you'd rather narrate (use `big_idea` or `bullets`)
- Long monologues (≤30 words; longer is body text, not a slide)

## Outline schema
```json
{
  "template": "pull_quote",
  "quote": "I shouldn't have to click three times to see a patient's last visit.",
  "author": "Care provider",
  "role": "Internal interview, May 2026"
}
```

`role` is optional but recommended — it gives the audience context for why this quote matters.

## Content rules
- ≤30 words (validator-enforced)
- The quote is verbatim from a verifiable source. Per the skill's rule: never put a name on a quote unless that exact name appears in the citation.
- Use a role descriptor instead of a name if you don't have explicit attribution permission ("Care provider", "Sr PM", "WL customer in onboarding")
- Keep the quote in the source's voice — don't sanitize for grammar if the verbatim is rougher
- Single quote per slide. If you have three customer quotes, use three pull_quote slides (paced between other content).

## Visual spec (auto-applied)
- Sage tint (`#F5FAF6`) background
- Large opening quote mark "“" in sage accent at top, centered
- Quote body centered, 18-22 pt ink (size depends on word count)
- Attribution at bottom: "— Author, Role" in sage accent, 14 pt Bold
- Confidentiality footer

## Common mistakes
- Inventing or paraphrasing quotes — never do this. If you don't have a real quote, use `big_idea` for your own framing instead.
- Long quotes (40+ words) — cut to the core sentence. The speaker can read the rest aloud.
- Attribution to a specific person without source — if the source is "the team", attribute to "the team", not a name.
- Two pull_quotes back-to-back — break them up with other templates.
