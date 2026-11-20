# Audience: your SVP Engineering / skip-level eng leader

> Template. Copy this to `<name>.md` and edit the four sections marked with EDIT.

## Role

EDIT: Their title, the VP Engs who report to them, what they read for, where their pushback typically lands.

Example: "SVP Eng at Acme. Manages VP Engs across the org. Reads decks looking for throughput, dependency risk, and whether the org is solving the right problem. Their pushback is a priority signal."

## What they care about

1. Dependencies with explicit contingency. What if X slips, what's Plan B.
2. Risks framed with consequence and mitigation, not just "risk: tight timeline".
3. Scope realism at the program level (across teams, across quarters).
4. Throughput. Is the team shipping, or is the team busy.
5. "Show me the metric, not the activity." Outcome numbers, not status colors.

## Default framing

Open with the outcome metric and where it stands today.

Default spine: **A (status update)** for program reviews. **D (pre-mortem)** when surfacing risk.

Exec summary lens (3 cards):
- Card 1: outcome metric ("Migration is 83% complete; target was 90% by May")
- Card 2: throughput ("Cycle time down 22% QoQ")
- Card 3: top risk with mitigation ("Plan B for context summary slip = minimal version from existing data")

Every section should answer "what did this move?" not "what did this do?"

## Content cuts

- **Include**: outcome metrics with baseline + target, dependency map with named owners, risks with consequence + mitigation, throughput indicators (ship count, cycle time, rework rate).
- **Cut**: implementation-level detail, slide real estate on activity ("we held 4 design reviews"), promotional framing.
- **Translate**: nothing. Full context assumed.

## Tone adjustments

Senior-to-senior. Tight, conservative, no padding. Lead with the conservative end of any range. State the metric and where it stands; do not editorialize. When surfacing their prior pushback, name it directly: "You flagged X in April; here's where it lands now."

## Slide-level defaults

| Slide type | Default behavior |
|---|---|
| cover | Subtitle is "Program review with <name>, <date>" |
| exec_summary | Lead is the outcome metric vs target in one sentence. Cards: outcome / throughput / top risk. |
| metric_grid | Default: outcome vs target, cycle time, dependency-on-time rate. Real numbers with source and date. |
| comparison_2x2 | Default axes: likelihood × impact for risk register, or scope × capacity for program load. |
| section_divider | "Outcome" / "Throughput" / "Dependencies" / "Risks and mitigations" |
| close slide | Default ask: contingency decision or dependency unblock. "Need your call on contingency for X by <date>." |

## Things they will ask

1. What's the metric, and what's it vs target?
2. If the critical dependency slips, what's Plan B?
3. What's the consequence of this risk landing, in customer or revenue terms?
4. Why is this team still on this; what does the throughput say?
5. What did we ship vs what did we work on?

## Things to NEVER do for this audience

- Show activity as a win. "RFC approved" is not a win; "X shipped, Y customers now see Z" is a win.
- Present a risk without a consequence and a mitigation.
- Hide a slipped dependency behind a green status color.
- Use best-case dates. Lead with the conservative end of the range.
- Skip the metric because it isn't yet flattering. State it with context.

## When this is the wrong audience config

- If this is for your direct VP Eng review first, use `_template-vp-engineering.md`. Same eng frame, lower altitude (capacity vs throughput).
- If the deck is for your manager / CPO, use `_template-cpo.md`. They want customer framing.
- If the audience is the e-team broadly, use `_template-skip-level-exec.md`; the SVP has more context than the CEO/COO/CFO do.
