# Evals for `make-deck`

## What `evals.json` is

`evals.json` follows the skill-creator evaluation framework. Each entry is a
realistic PM scenario the skill must handle: a prompt, the expected behavior,
and a list of pass/fail assertions a grader checks against the produced deck.

The schema mirrors what `anthropic-skills:skill-creator` consumes when it runs
its automated evaluation subagent pipeline. Today these run **manually** (see
below). Automated runs are v2.

## How to run a single eval manually

1. Start a fresh Claude Code session in the workspace root so no prior state
   leaks in.
2. Paste the eval's `prompt` field verbatim as your first message.
3. Let `make-deck` run end-to-end: outline, build, QA pass, URL.
4. Capture:
   - The final deck URL (`docs.google.com/presentation/d/...`)
   - The QA verdict (`SHIP`, `SHIP_WITH_WARNINGS`, or `BLOCKED`)
   - The path of the saved outline JSON under `outputs/`

## How to grade

Each assertion in `evals.json` is graded as PASS / FAIL / N/A by hand:

- **`deck-url-returned`**: final message must contain a
  `docs.google.com/presentation/d/...` URL.
- **`no-em-dashes`**: open the deck, scan slide titles, bodies, and speaker
  notes for em dashes or double hyphens. One hit equals FAIL.
- **`visual-variety`**: count distinct templates in the outline JSON. At
  least 2 non-`bullets` templates equals PASS.
- **`non-bullets-majority`**: count of non-`bullets` content slides must
  exceed `bullets` slides. Cover, exec_summary, agenda, section_divider, and
  moving_blueprint do not count as content slides for this assertion.
- **`has-agenda`**: slide 3 of the outline uses the `agenda` template.
- **`no-agenda`**: no slide uses the `agenda` template.
- **`tpa-disambiguation`**: on first mention, deck text spells out both
  "Titration Protocol Adjustment" and "Treatment Plan Authority service".
- **`audience-tuning`**: content or speaker notes reference your VP Eng and SVP Eng
  by name, capacity framing, or dependency framing.
- **`ends-with-ask`**: the last content slide is forward-looking (next
  step, decision needed, ask).
- **`state-file-written`**: file exists at
  `~/.claude/skills/make-deck/outputs/YYYY-MM-DD-<slug>.json`.
- **`qa-pass`**: QA verdict from `references/qa-rubric.md` is `SHIP` or
  `SHIP_WITH_WARNINGS`.

After grading, run the QA rubric end-to-end against the rendered thumbnails
(`scripts/render_thumbnails.py <pres_id>`). The rubric in
`references/qa-rubric.md` is the source of truth for the `qa-pass` assertion.

## Recording results

For each manual run, append a row to a local notebook (or a Slack DM to
yourself) with: eval id, date, deck URL, per-assertion PASS/FAIL, and any
qualitative notes. Over time these inform skill iteration.

## Automated runs (v2)

Skill-creator can spawn a subagent pipeline that runs evals automatically and
grades them with an LLM judge. That work is not wired up yet for `make-deck`.
When it is, this README will be updated with the entrypoint command.
