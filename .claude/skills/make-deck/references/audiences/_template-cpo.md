# Audience: your CPO / VP Product / direct manager

> Template. Copy this to `<name>.md` (e.g. `alex.md`) and edit the four sections marked with EDIT.

## Role

EDIT: Their title, who they report to, scope of influence, decision rights they hold.

Example: "CPO at Acme. Manages all of Product. Sets quarterly priorities. Reads decks between meetings, often on mobile. Decision rights on roadmap, headcount, and exec-narrative framing."

## What they care about

EDIT: 3-5 specific things they ask about every review, ranked. Concrete is better than vague.

Common patterns for this role:
1. Customer impact. "What changed for the customer?"
2. Growth tied to a strategic bet (e.g. a key product line, a partnership).
3. Dates with explicit confidence levels (not "soon", not "Q3").
4. The one-line ask. What do you need from them, by when.
5. How this work compounds (does it set up the next quarter, or is it one-off).

## Default framing

Open with the customer-impact line, then the metric, then the ask.

Default spine: **A (status update)** for ongoing workstreams. **B (recommendation)** when proposing a new bet.

Exec summary lens (3 cards):
- Card 1: customer impact ("Patients in WL Membership now see X")
- Card 2: business metric ("Retention +N pp vs control")
- Card 3: the ask ("Decision needed on Y by Z")

## Content cuts

- **Include**: customer outcome, dollar/metric impact, named owners on dependencies, dates with confidence levels.
- **Cut**: implementation detail, eng acronyms, code-path specifics, history older than 30 days.
- **Translate**: any acronym from another workstream on first mention. They have full context on yours but not adjacent.

## Tone adjustments

PM-to-manager. Direct, no padding, conversational. Confidence levels on every date ("July 17 ± 1 week, blocked on X"). When citing a number, include source + date in speaker notes, not on the slide.

Avoid: pitch-deck language ("game-changing", "transformative"). Vague status ("on track", "going well").

## Slide-level defaults

| Slide type | Default behavior |
|---|---|
| cover | Subtitle is the headline takeaway ("Migration is 83% done; remaining 17% is the risk surface") not a date stamp |
| exec_summary | Lead is the customer-impact sentence. Three cards: outcome / metric / ask. |
| metric_grid | Default metrics: growth, retention, cost-to-serve, NPS. Real numbers with source and date. |
| section_divider | "Where we are" / "What changed" / "What's next" / "What we need" |
| close slide | Forward-looking. Default ask: "Decision needed on X by Y" or "Want your read on Z" |

## Things they will ask

EDIT: 3-5 questions this person asks every time. Build the deck to preempt them.

Common patterns:
1. "What's the customer impact?" → make slide 2 lead with customer outcome
2. "What's the confidence on that date?" → cite confidence on every date
3. "What does this displace on the roadmap?" → name the trade-off
4. "Who's on the critical path?" → name owners on dependencies
5. "How does this connect to [strategic priority]?" → tie back in the exec summary

## Things to NEVER do for this audience

EDIT: Specific antipatterns for this person.

Common patterns:
- Lead with implementation detail. They've stopped reading by slide 4.
- Use a single date without a confidence range. They will probe.
- Bury the ask in the appendix. Put it on the close slide.
- Claim work is "done" when it has shipped to <100% of users. Use "shipped to X cohort" instead.
- Tell them what their feedback should be. Surface options; they pick.

## When this is the wrong audience config

- If the deck is for the SVP Eng or VP Eng, use the eng templates. They want capacity reality, not customer framing.
- If the deck will get forwarded a level up (to the CEO/COO), use `_template-skip-level-exec.md` because the senior audience has less context.
- If it's a clinical-safety review, use `_template-cmo.md`; safety framing is required and customer framing alone won't pass.
