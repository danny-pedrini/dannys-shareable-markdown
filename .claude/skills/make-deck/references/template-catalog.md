# Template catalog (master index)

The skill's full repository of slide templates. Pick from this list during outline phase; reach for visual templates BEFORE bullets.

## Decision flow: "what template do I use?"

```
Is this slide 1?                                              → cover
Is this slide 2 (or anywhere "the answer up front" lives)?    → exec_summary
Is this slide 3 of an 8+ slide deck?                          → agenda
Is this a section break?
  - Deck >12 slides?                                          → moving_blueprint
  - Otherwise                                                 → section_divider
Does the content advance through time / steps (3-5 items)?    → flow_steps
Is the content a comparison between exactly two things?       → two_column
Is it a behavior/policy contract (DO vs DON'T)?               → do_dont
Is the content 2-4 parallel items with names + descriptions?  → three_card
Is the content a 2x2 matrix (axes + 4 quadrants)?             → comparison_2x2
Is a single number THE headline?                              → key_stat
Are 2-6 related numbers the headline?                         → metric_grid
Is one sentence the entire point of the slide?                → big_idea
Is the content a customer/stakeholder quote?                  → pull_quote
None of the above and content is 2-6 short points?            → bullets (last resort)
```

If you reach `bullets` for more than 2 slides in a row, the deck is too uniform. Audit whether one of those slides is actually a `flow_steps`, `three_card`, or `comparison_2x2` in disguise.

## All templates at a glance

| Template | Position in deck | Content shape | Density | Reference |
|---|---|---|---|---|
| `cover` | Slide 1 | Title + subtitle | Sparse | `references/templates/cover.md` |
| `exec_summary` | Slide 2 | Lead + 3 verb-phrase cards | Medium | `references/templates/exec_summary.md` |
| `agenda` | Slide 3 (decks 8+ slides) | 3-6 section names, numbered | Sparse | `references/templates/agenda.md` |
| `moving_blueprint` | Between sections (decks 12+ slides) | Section pills + current name | Sparse | `references/templates/moving_blueprint.md` |
| `section_divider` | Between sections (decks 8-12) | Title + optional subtitle on beige | Sparse | `references/templates/section_divider.md` |
| `flow_steps` | Process / sequence slides | 3-5 numbered horizontal steps | Sparse | `references/templates/flow_steps.md` |
| `two_column` | Compare 2 things | Two parallel columns, bullets | Medium | `references/templates/two_column.md` |
| `do_dont` | Behavior contract | DO / DON'T cards | Medium | `references/templates/do_dont.md` |
| `three_card` | 2-4 parallel items | Header + body per card | Medium | `references/templates/three_card.md` |
| `comparison_2x2` | 2x2 matrix | Axes + 4 quadrants | Medium | `references/templates/comparison_2x2.md` |
| `key_stat` | Single headline number | Big number + label + caption | Sparse | `references/templates/key_stat.md` |
| `metric_grid` | 2-6 related numbers | Grid of mini-stats | Medium | `references/templates/metric_grid.md` |
| `big_idea` | The one thing | Single bold statement | Very sparse | `references/templates/big_idea.md` |
| `pull_quote` | Customer/exec quote | Quote + attribution | Sparse | `references/templates/pull_quote.md` |
| `bullets` | Last-resort content | Title + bullets list | Heavy | `references/templates/bullets.md` |

## Default template mix targets

For a typical PM deck of 10-15 slides, aim for this distribution:

| Template | Slides |
|---|---|
| cover | 1 |
| exec_summary | 1 |
| agenda | 1 |
| moving_blueprint or section_divider | 2-4 (one per section) |
| Visual content (`flow_steps`, `three_card`, `key_stat`, `metric_grid`, `comparison_2x2`, `big_idea`, `pull_quote`) | 4-7 |
| Comparison (`two_column`, `do_dont`) | 0-2 |
| `bullets` | ≤2 |

If your deck has more than 2 bullets slides, the outline phase failed. Go back and ask which of those bullets slides is actually a sequence (flow_steps), a comparison (two_column), parallel items (three_card), or a metric (key_stat / metric_grid).

## Templates that take NO title

These templates carry their headline in a different field, so `title` is optional in the outline:

- `key_stat` → headline is `stat` + `label`
- `big_idea` → headline is `statement`
- `pull_quote` → headline is `quote`
- `moving_blueprint` → headline is the current section name (auto-pulled from `sections[current_index]`)
- `agenda` → defaults to "Agenda" if `title` not provided

## Word-count budgets (hard limits, validator-enforced)

The CLI rejects outlines that exceed these caps:

| Field | Max |
|---|---|
| `exec_summary.cards[]` | 3 cards total |
| `bullets.bullets[]` | 6 bullets total |
| `flow_steps.steps[]` | 5 steps total |
| `three_card.cards[]` | 4 cards total |
| `agenda.sections[]` | 6 sections total (min 3) |
| `moving_blueprint.sections[]` | 6 sections total |
| `big_idea.statement` | 15 words |
| `pull_quote.quote` | 30 words |
| `metric_grid.metrics[]` | 6 metrics total (min 2) |
| `comparison_2x2.quadrants[]` | exactly 4 |

When in doubt, fewer items is better. The skill's storytelling principle is **less words is better** (see `references/storytelling-principles.md`).
