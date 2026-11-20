# Audience: your VP Engineering / primary eng partner

> Template. Copy this to `<name>.md` and edit the four sections marked with EDIT.

## Role

EDIT: Their title, scope of teams under them, what they own (capacity, scope, rollout), reporting line.

Example: "VP Eng at Acme. Reports to SVP Eng (or CTO). Owns capacity and scope across N teams. Their feasibility calls are load-bearing; when they weigh in, the recommendation adjusts."

## What they care about

1. Feasibility, grounded in real team capacity (not best-case).
2. Scope realism. What's in, what's out, why.
3. Phased rollouts with explicit gates between phases.
4. Dependency clarity. Which teams, which systems, what order.
5. No over-promising. They have seen PMs commit eng to dates eng never agreed to.

## Default framing

Open with the eng problem statement, then proposed phasing.

Default spine: **B (recommendation)** when proposing scope. **C (deep dive)** for architecture walkthroughs.

Exec summary lens (3 cards):
- Card 1: scope statement ("Pilot ships X only, leaves Y untouched")
- Card 2: phasing ("Phase 0 → 1 → 2 → 3, gated at each")
- Card 3: capacity ask ("Eng-weeks pending sizing")

Acceptance criteria should be concrete enough that an EM can hand the slide to a tech lead and get a sized ticket back.

## Content cuts

- **Include**: scope boundaries, phase gates, capacity ask in eng-weeks or sprints, named dependencies, rollout plan, AC.
- **Cut**: customer-experience storytelling as the main argument, growth framing, anything that smells like a pitch deck.
- **Translate**: nothing. Full context assumed on your stack, your team structure, your prior reviews.

## Tone adjustments

PM-to-senior-eng-leader. Concrete and bounded. Use eng-week ranges with low / high ends. Label estimates as PM-generated and flagged for eng validation when not yet sized. Use "we propose" not "we will" when scope is not yet confirmed.

Avoid: promotional language ("game-changing"). Vague risks ("tight timeline"). Date commitments without phase gates.

## Slide-level defaults

| Slide type | Default behavior |
|---|---|
| cover | Subtitle is "Eng scope review with <name>, <date>" |
| exec_summary | Lead is the scope statement. Cards: scope / phasing / capacity ask. |
| metric_grid | Default: eng-weeks low / high, team count, dependency count. Real numbers only. |
| flow_steps | Default to phased rollout (Phase 0 / Phase 1 / Phase 2) with the gate between each. |
| section_divider | "Scope" / "Phasing" / "Dependencies" / "Risks and asks" |
| close slide | Default ask: capacity commitment or phase-gate decision. "Need your call on Phase 1 scope by <date>." |

## Things they will ask

1. Where did the eng-week range come from, and who sized it?
2. What's in Phase 1, what's in Phase 2, and what's out entirely?
3. Which teams are on the critical path, and have they agreed?
4. What's the rollback plan if Phase 1 misses?
5. What does this displace on the existing roadmap?

## Things to NEVER do for this audience

- Present scope without capacity reality. If the team is full, say so on the slide.
- Show a single date with no phase gates behind it.
- Bury cross-team dependencies in a footnote.
- Claim eng agreement when it hasn't been confirmed. Mark as "proposed" until the EM signs off.
- Use customer-impact framing as the load-bearing argument. Lead with the eng problem.

## When this is the wrong audience config

- If the deck is for the SVP Eng review, use `_template-svp-engineering.md`. Same eng frame, different altitude (throughput + risk vs capacity + feasibility).
- If the deck is for your manager / CPO, use `_template-cpo.md`. Customer framing wins there.
- If it's a clinical-safety review, use `_template-cmo.md`; eng is a feasibility reviewer, not the sign-off.
