# Audience: skip-level exec (CEO / COO / CFO / e-team)

> Template. Copy this to `<name>.md` and edit the four sections marked with EDIT.

## Role

EDIT: Their title, role in the company, what part of the business they own, what they typically pay attention to.

Example: "CEO at Acme. Reads three or four decks a week. Has zero context on your specific workstream. Pattern-matches against business impact and strategic fit; will glance at slide 2 and decide whether to keep reading."

## What they care about

1. Business impact in plain language: revenue, retention, cost-to-serve, customer outcomes.
2. Strategic fit. How does this connect to the top-three priorities they've stated this year?
3. Where this work is now (one sentence) and where it needs to go (one sentence).
4. What you need from them, by when.
5. The shortest path through the deck. They will not read 15 slides.

## Default framing

Lead with the business outcome in plain English. No jargon, no acronyms without translation. Assume they have zero context on your workstream and will skim.

Default spine: **A (status update)** for ongoing work, **B (recommendation)** when proposing a new bet. Always **short or medium length** (avoid long; they won't read past slide 8).

Exec summary lens (3 cards):
- Card 1: business outcome ("Patients in WL Membership now see X; retention +N pp")
- Card 2: strategic fit ("Connects to membership-economics priority")
- Card 3: the ask ("Decision on Y by Z")

## Content cuts

- **Include**: the business outcome, the metric vs target, the one-line ask, the strategic-fit sentence.
- **Cut**: implementation detail, eng terminology, team-specific context, history older than 60 days, anything that requires prior-deck knowledge.
- **Translate**: every acronym on first mention. "PHD (Patient Health Data)", "TPA (Titration Protocol Adjustment)", etc. Use full names on first mention even when they look long.

## Tone adjustments

Plain English. Short sentences. Confident but not promotional. Lead with the answer; reasons follow only if asked. State numbers with context (vs target, vs last quarter, vs competitor).

Avoid: any acronym not defined on the slide it appears on. Any reference to a prior deck or a prior decision. Any tech-stack name.

## Slide-level defaults

| Slide type | Default behavior |
|---|---|
| cover | Subtitle is the headline business outcome ("Migration delivers $X cost-to-serve savings; complete by July") |
| exec_summary | Lead is the business-outcome sentence. Cards: outcome / strategic fit / ask. |
| key_stat | Strong choice for skip-level. Lead with the number that decides. |
| section_divider | Plain English only. "Where we are" / "What changed" / "What's next" / "The ask" |
| close slide | Forward-looking, one-line ask. "Need your read on X by Y" or "Decision needed on Z by W" |

## Things they will ask

1. What's the dollar impact (or customer-outcome impact)?
2. How does this connect to [strategic priority]?
3. What's the date, and what's the confidence?
4. What do you need from me?
5. Who else has weighed in?

## Things to NEVER do for this audience

- Use any acronym you wouldn't say in a public earnings call without translating.
- Lead with implementation detail. They've stopped reading.
- Show a 15-slide deck. Cut to 6-8 maximum.
- Reference a prior deck without summarizing the prior conclusion in one line.
- Bury the ask. Put it on the close slide in a single sentence.

## When this is the wrong audience config

- If the audience has full context on your workstream (your manager, eng partner), use a more specific template.
- If the deck is technical (architecture, scope), the eng templates are better even if the eng leader is "skip-level" because they have the technical context.
- If it's a clinical-safety review, use `_template-cmo.md`.
