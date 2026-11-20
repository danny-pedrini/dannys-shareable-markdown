# Audience configurations

Per-audience config files let the skill tune a deck for a specific reader: framing, content cuts, tone, slide-level defaults, and the antipatterns to avoid for that person.

## How they work

When you invoke `/make-deck for <name>` (e.g. `/make-deck for cpo`), the skill reads `references/audiences/<name>.md` before drafting the outline. The config shapes:

- Which story-arc spine to default to
- What goes on the exec summary cards
- Default subtitles, section names, metric choices
- What to drop or compress for this audience
- Questions to preempt
- Antipatterns specific to that person

## Templates shipped (starting points)

Six role-based templates ship with the skill. They are not configs for any specific person; they are patterns you copy and customize.

| File | When it fits |
|---|---|
| `_template-cpo.md` | Your direct manager at the CPO / VP Product / Director level. Cares about customer impact, growth, dates with confidence. |
| `_template-vp-engineering.md` | Primary eng partner. Cares about scope, capacity, phased rollouts, dependencies. |
| `_template-svp-engineering.md` | Skip-level eng leader. Cares about throughput, dependency risk, metric-not-activity. |
| `_template-cmo.md` | Clinical or medical leader. Cares about safety, compliance, clinical quality. |
| `_template-skip-level-exec.md` | E-team / skip-level (CEO, COO, CFO). No context on your workstream. |
| `_template-pm-peer.md` | PM peer. Direct, casual, real numbers. |

## Customizing for your stakeholders

Three-step setup, ~5 min per stakeholder:

1. **Copy the closest template:**
   ```bash
   cd ~/.claude/skills/make-deck/references/audiences
   cp _template-cpo.md alex.md
   ```

2. **Edit four sections:**
   - **Role** (top of file): replace the generic role description with the actual person's title and reporting line
   - **What they care about**: 3-5 specific things this person asks about every time
   - **Things they will ask**: questions to preempt on the deck itself
   - **Things to NEVER do for this audience**: specific antipatterns for this person

3. **Use it:**
   ```
   /make-deck for alex
   ```

Now the skill reads `alex.md` instead of falling back to generic guidance.

## Why this matters

Audience tuning is the difference between a deck that reads as "Claude generated this" and one that reads as "this PM knows my reader." Two examples:

- For a customer-impact-driven manager, slide 2 leads with the customer outcome. For an eng partner, slide 2 leads with the scope statement and phasing.
- For a skip-level exec, every workstream acronym gets translated on first mention. For an eng partner, no translation — full context is assumed.

Per-stakeholder configs encode what you've learned about how each person reads decks, so the skill applies that learning every time without you re-explaining it.

## When NOT to use audience tuning

- One-off internal team standup: skip the modifier, default tone is fine
- Multi-audience deck (e.g. eng + clinical + business in one room): pick the senior-most audience to default to and call out the others in the close slide

## How the skill falls back

If you invoke `/make-deck for <name>` and no matching config file exists, the skill falls back to the generic modifier-table guidance in `SKILL.md`. No error. But you lose all the per-stakeholder polish.

## Where to learn the pattern

The template files themselves are the documentation. Read `_template-cpo.md` first — it's the most fleshed out — then the eng templates which show how the pattern adapts to engineering audiences.
