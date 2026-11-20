---
name: make-deck
description: Build native Google Slides decks programmatically with hims & hers brand styling (Poppins font, sage/beige palette, confidentiality footer, BLANK layouts) and built-in storytelling discipline (agenda + moving blueprint + less-words-is-better content rules). Use this skill any time the user asks for a deck, slides, slide deck, presentation, or pitch deck, OR pastes a doc/PRD/briefing/Confluence link and wants a slide version, OR says "make a deck", "build slides for X", "deck this", "turn this into slides", "/make-deck", or "/deck". Use this skill even when the user doesn't explicitly say "Google Slides" — if the deliverable is a slide deck, this is the right tool. Workflow is outline-first with a story-arc spine (cover → exec_summary → agenda → sectioned content with moving_blueprint between → action close) and a mandatory QA pass: every deck is rendered as thumbnails and a dedicated sub-agent grades every slide against the rubric in references/qa-rubric.md before the URL is shared. Supports modifiers like "/make-deck short" (≤8 slides), "/make-deck for cpo" (audience-tuned), and "/make-deck in folder <url>" (Drive destination). 15 templates in the catalog: cover, exec_summary, agenda, moving_blueprint, section_divider, flow_steps, three_card, comparison_2x2, key_stat, metric_grid, big_idea, pull_quote, two_column, do_dont, bullets. Picks visual templates over bullets by default; bullets is treated as a last resort. Storytelling principles, template catalog, and per-template references all live in references/. Builds via scripts/build_deck.py CLI; QAs via scripts/render_thumbnails.py plus a dispatched QA sub-agent. Saves outline + deck URL to outputs/YYYY-MM-DD-<slug>.json so prior decks are referenceable. Do NOT invoke if the user wants a .pptx file (use python-pptx), wants to edit an existing deck (not yet supported), or wants a written one-pager / PRD / doc.
---

# make-deck

Build native Google Slides decks, branded to hims & hers, from any PM source material. Outline-first workflow keeps Claude from building the wrong deck before you can correct course.

## Why this skill exists, briefly

A typical PM deck request goes from "make me a deck about X" to a finished file in four places things go wrong: (1) Claude guesses at structure without asking, (2) the deck has no story arc — it's a list of slides instead of an argument with a shape, (3) Claude writes content that doesn't match your voice, (4) the deck looks generic instead of branded. This skill solves all four: outline-first prevents structure drift, the storytelling spine (agenda + moving blueprint + visual variety + less-words-is-better) forces a coherent arc, embedded style rules enforce voice, and the bundled CLI applies hims & hers palette/typography automatically.

## Storytelling first (mandatory read before outlining)

**Read `references/storytelling-principles.md` in full before designing any outline.** The principles there are the difference between a deck that's a list of facts and a deck that's an argument with a shape.

**Then read `references/storytelling-masters.md`** for the deeper canon (Apple/Jobs, Airbnb, Pixar, Duarte, Reynolds, Tufte, Minto, Anderson) and the specific moves not yet hard-enforced by the validator. Especially: SCQA in exec_summary cards, tension framing on the cover, the one STAR moment requirement, action titles for exec audiences.

The eight core principles from `storytelling-principles.md`:

1. **Lead with the answer** — exec_summary lands at slide 2, not the end
2. **Tell them where you're going** — `agenda` slide at position 3 of every 8+ slide deck
3. **Anchor every section to the spine** — `moving_blueprint` replaces section_divider for decks ≥12 slides
4. **One idea per slide** — if you can't say the takeaway in 5 words, the slide is doing too much
5. **Less words is better** — every word on a slide is a word the speaker can't add
6. **Visuals support the story, they don't tell it** — annotations, not paragraphs
7. **Pace with visual variety** — never 3+ consecutive bullets slides
8. **End on action, not recap** — last slide is forward motion (decision, ask, next 30 days)

Pick a story-arc spine during outline phase. Four spines in `storytelling-principles.md`: A) status update, B) recommendation, C) deep dive, D) pre-mortem. State which spine you're using at the top of the proposed outline.

## Template repository

15 templates in the catalog. **Always reach for a visual template before bullets.** Read `references/template-catalog.md` for the full index, decision flow, and default mix targets. Read `references/templates/<name>.md` for any template you're about to use.

## When to invoke

**Trigger when the user:**
- Says "make a deck", "build slides", "build a deck", "deck this", "turn this into slides", "draft a deck", "/make-deck", "/deck"
- Pastes a PRD, briefing, Confluence page, Google Doc, or Slack thread and asks for a slide version
- References a meeting/review and asks for slides to take into it ("I need slides for tomorrow's manager 1:1")
- Says any synonym for "presentation" (pitch deck, slide deck, slides, deck, presentation, exec deck)

**Trigger even when not explicitly asked**, if the deliverable described is clearly a slide deck.

**Do NOT trigger when:**
- The user wants a .pptx file — use python-pptx instead
- The user wants to edit an existing deck — this skill only creates new decks (v1)
- The user wants a one-pager, status update, PRD, or written doc — those have their own skills
- The user wants to read or summarize an existing deck — that's a Drive MCP read, not this skill

## Modifiers

Parse modifiers from the user's invocation. If multiple appear, apply all.

| Modifier | Effect |
|---|---|
| `short` | Cap outline at 8 slides; bias toward bullets + exec_summary, skip section dividers |
| `medium` | 8–15 slides (the default) |
| `long` | 15+ slides; insert section_dividers every 4–6 content slides |
| `for <person/group>` | **Read the matching file in `references/audiences/` before outlining.** Configs exist for `cpo`, `vp-eng`, `svp-eng`, `cmo`, `skip-level`, `pm-peer`. Each defines framing, content cuts, tone, slide-level defaults, questions to preempt, and antipatterns specific to that audience. If no file matches, fall back to the generic guidance below: "for cpo" → customer-impact framing, confidence levels on dates. "for vp-eng" or "for svp-eng" → capacity + dependency framing. "for cmo" → clinical-safety framing. "for skip-level" → no PHD context assumed. |
| `in folder <url-or-name>` | Drop into specified Drive folder. If URL, extract ID after `/folders/`. If name, resolve via Drive MCP `search_files`. |
| `use [doc/briefing/PRD]` | Treat that as source material; read via Drive MCP / Atlassian MCP before drafting outline |

## Core workflow (always outline-first)

### 1. Gather inputs
Ask only for what's missing. One concise message.
- **Source content** (can be one OR multiple; the skill composes across sources): paste, file path, Google Doc URL (`mcp__google-workspace__get_doc_content` for Docs; `mcp__google-workspace__get_drive_file_content` for other Drive files), Confluence URL (Atlassian MCP `getConfluencePage`), Slack permalink (Slack MCP `slack_read_thread`), Jira issue (Atlassian MCP `getJiraIssue`), Looker chart (use `scripts/looker_to_image.py` to convert), or "use [the briefing/PRD/notes I just made]". For multi-source: list each source explicitly in the outline phase and which slides it'll inform. If sources conflict, surface to user before building.
- **Audience**: defaults to "internal team" if not specified. If user names a person/group with a config at `references/audiences/<name>.md`, read that file before outlining. Otherwise use modifier table guidance.
- **Length target**: short / medium (default) / long
- **Drive folder**: paste URL or name, or default to "My Drive root"
- **Deck title**: infer from source if obvious; otherwise ask

### 2. Propose outline (NEVER skip this)

**First, output a one-line story spine** using Adams/Pixar's six-beat structure ("Once upon a time... Every day... One day... Because of that... Because of that... Until finally..."). If the spine doesn't write cleanly in 6 sentences, the deck has no story and the outline needs more source material. This is the cheapest upstream quality gate (per `references/storytelling-masters.md` Part 4).

**Then output the slide list** as a numbered list, one row per slide:
- Slide # + template type (`cover` / `exec_summary` / `section_divider` / `bullets` / `two_column` / `do_dont` / etc.)
- Slide title
- One-line content summary

**Then write the outline JSON to `/tmp/outline-<slug>.json`** so the user can either approve verbally OR edit the file directly for surgical changes (faster than verbal back-and-forth for complex outlines). Tell the user both options: "Approve in chat, or edit /tmp/outline-<slug>.json directly and tell me to rebuild."

**Why outline-first**: Building 12 slides with the wrong structure wastes ~30 seconds of API calls and forces the user to ask for a rebuild. Outlining first costs 5 seconds and lets the user redirect with one comment ("swap slide 4 for a do/don't"). The cost asymmetry makes outline-first always correct.

Example outline output:
```
Proposed outline (medium, for cpo):

1. cover            "PHD migration status" / "Q2 checkpoint for cpo, May 13 2026"
2. exec_summary     "Executive summary" / lead: 83% complete, blocker is MedMatch /
                    cards: Migration health, Capacity, Risk posture
3. section_divider  "Where we are"
4. bullets          "Milestones in flight" / 3 bullets, named-owner pattern
5. two_column       "Q2 delivery" / Shipped vs Slipped
6. section_divider  "What's next"
7. bullets          "Next 30 days" / 4 bullets with confidence levels
8. do_dont          "How to read this deck" (omitted for short)

Approve, or tell me what to swap.
```

Wait for explicit approval. **Never build the deck before the user says "go" or equivalent.**

### 3. Build via the bundled CLI

The skill ships a CLI at `scripts/build_deck.py` that takes a JSON outline and creates the deck. Do not write inline Python every time — it's already written and bundled.

**Step 1**: Write the approved outline to a temp JSON file.

**Step 2**: Run the CLI.

```bash
python3 ~/.claude/skills/make-deck/scripts/build_deck.py /tmp/outline.json
```

The CLI prints diagnostics to stderr (slide count, template mix, state path) and the deck URL to stdout (last line). The CLI also:
- Validates the outline against template schemas (catches missing fields, oversize bullet lists, max-3-cards rule)
- Creates the deck and applies hims & hers styling per template
- Saves `outline + URL + slide_count + template_mix` to `~/.claude/skills/make-deck/outputs/YYYY-MM-DD-<slug>.json`

**Outline JSON shape** (see per-template references for exact required fields):
```json
{
  "title": "Deck title",
  "parent_folder_id": null,
  "slides": [
    {"template": "cover", "title": "...", "subtitle": "..."},
    {"template": "exec_summary", "title": "...", "lead": "...",
     "principles_header": "Launch principles", "cards": ["...", "...", "..."]},
    {"template": "agenda", "title": "Agenda",
     "sections": ["Section 1", "Section 2", "Section 3", "Section 4"]},
    {"template": "moving_blueprint",
     "sections": ["Section 1", "Section 2", "Section 3", "Section 4"],
     "current_index": 0, "subtitle": "Optional preview line"},
    {"template": "section_divider", "title": "...", "subtitle": "..."},
    {"template": "flow_steps", "title": "...", "lead": "...",
     "steps": ["Step 1 phrase", "Step 2 phrase", "Step 3 phrase"]},
    {"template": "three_card", "title": "...", "lead": "...",
     "cards": [{"header": "Service name", "body": "1-2 sentence description"}]},
    {"template": "comparison_2x2", "title": "...",
     "x_left": "Low effort", "x_right": "High effort",
     "y_bottom": "Low impact", "y_top": "High impact",
     "quadrants": [
       {"header": "Quick wins", "body": "..."},
       {"header": "Major bets", "body": "..."},
       {"header": "Fill-ins", "body": "..."},
       {"header": "Money pits", "body": "..."}
     ]},
    {"template": "key_stat", "stat": "5", "label": "Kafka listeners",
     "caption": "Optional context"},
    {"template": "metric_grid", "title": "...",
     "metrics": [{"value": "83%", "label": "of records migrated"}]},
    {"template": "big_idea",
     "statement": "Migration is 83% done. The last 17% is the risk surface.",
     "attribution": null},
    {"template": "pull_quote",
     "quote": "I shouldn't have to click three times to see a patient's last visit.",
     "author": "Care provider", "role": "Internal interview, May 2026"},
    {"template": "two_column", "title": "...",
     "left_header": "...", "left_bullets": ["..."],
     "right_header": "...", "right_bullets": ["..."]},
    {"template": "do_dont", "title": "...", "dos": ["..."], "donts": ["..."]},
    {"template": "bullets", "title": "...", "lead": "...", "bullets": ["...", "..."]}
  ]
}
```

**Speaker notes**: every slide accepts an optional `notes` string field. Use it when the deck is for a high-stakes meeting (manager 1:1, exec review) — speaker notes carry the things you say but don't put on the slide. Example: `{"template": "bullets", "title": "...", "bullets": [...], "notes": "Mention the MedMatch dep here; don't put it on the slide."}`. Notes flow through every template via the `notes` kwarg.

### 4. QA pass (MANDATORY before sharing the URL)

The build step prints a URL, but **don't surface it yet**. The skill has shipped broken decks (content off-canvas, overlap, wrong template) often enough that a dedicated QA pass is now non-optional.

**Step 4a: render thumbnails.**

```bash
python3 ~/.claude/skills/make-deck/scripts/render_thumbnails.py <presentation_id>
```

This drops `slide-01.png` through `slide-NN.png` into `/tmp/slides-eval/`.

**Step 4b: dispatch the QA sub-agent.**

Spawn a dedicated agent via the `Agent` tool with `subagent_type: "general-purpose"`. The agent reads each thumbnail, grades it against `references/qa-rubric.md`, and returns a structured verdict. Do NOT inspect thumbnails yourself in the main thread — the sub-agent isolates this work and keeps your context clean.

Prompt template for the QA agent (fill in `<...>`):

```
You are a Slides QA agent for the make-deck skill. Read the QA rubric at
~/.claude/skills/make-deck/references/qa-rubric.md in full.
Then grade each slide thumbnail listed below against that rubric.

Thumbnails to grade (slide order matches deck order):
  /tmp/slides-eval/slide-01.png
  /tmp/slides-eval/slide-02.png
  ... [list all N paths]

Deck outline for context (template assignments per slide):
<paste the outline JSON the main thread used to build the deck>

For each thumbnail:
1. Read the PNG (Read tool supports images)
2. Compare against the rubric
3. Assign PASS, WARN, or FAIL
4. For non-PASS, give one-line issue and one-line fix

After grading every slide, output the overall verdict per the rubric
(SHIP, SHIP_WITH_WARNINGS, FIX_REQUIRED, or REBUILD) plus a 2-sentence
plain-English summary.

Return only the structured grade output. No preamble.
```

**Step 4c: act on the verdict.**

| Verdict | Action |
|---|---|
| `SHIP` | Proceed to Step 5 and share the URL. |
| `SHIP_WITH_WARNINGS` | Share the URL, but lead with the warnings up front. Offer to fix any the user cares about. |
| `FIX_REQUIRED` | Do NOT share the URL. Surface the FAILs and the agent's suggested fixes. Propose specific outline edits, get user approval, rebuild, then re-run Step 4. |
| `REBUILD` | A layout-level skill bug (e.g., >30% slides FAIL the same way). Flag to user as a skill issue, do not silently retry. |

### 5. Return URL and follow-ups (only after QA passes)

Before sharing the URL, run **Hard verification searches** from `forbidden-writing-patterns.md` and `.claude/skills/make-deck/references/hims-hers-style-guide.md`. Read **Watch for** Pattern #2 only; short headline fragments are OK on slides. Rewrite hard hits and scan again.

Always include:
1. The deck URL (from CLI stdout)
2. One-line summary: `"8 slides: 1 cover + 1 exec_summary + 2 section_dividers + 4 content"`
3. QA verdict: `"QA: SHIP"` or `"QA: SHIP_WITH_WARNINGS (2 warnings on slides 4, 7)"`
4. State path: `"Outline saved to outputs/2026-05-13-phd-migration-status.json"`
5. Flag any content you guessed at: `"Slide 2 cards are placeholders — give me the real three priorities and I'll regenerate"`
6. One forward nudge: `"Want me to swap slide 5 for a do/don't?"`

## Template reference

Each template has a dedicated reference file. Read the relevant file when you're about to write that slide's outline, not before.

**Read `references/template-catalog.md` for the full index, decision flow, and word-count budgets.** The 15 templates at a glance:

| Template | When to use |
|---|---|
| `cover` | Slide 1, always |
| `exec_summary` | Slide 2 of exec-facing decks (McKinsey answer-first pattern) |
| `agenda` | Slide 3 of every 8+ slide deck; numbered 3-6 section names |
| `moving_blueprint` | Replaces section_divider for decks ≥12 slides; section pills + current name |
| `section_divider` | Between sections in 8-11 slide decks; final slide for "Next up" |
| `flow_steps` | 3-5 sequential steps with numbered circles. Replaces bullets for sequences. |
| `three_card` | 2-4 parallel items each with a short header + 1-2 sentence body |
| `comparison_2x2` | 2x2 matrix with axes and labeled quadrants. Strategic categorization. |
| `key_stat` | Single number that IS the headline. Big sage numeral + label + caption. |
| `metric_grid` | 2-6 related numbers together. KPI dashboard slide. |
| `big_idea` | One bold statement, large type. The "one thing to remember" moment. ≤15 words. |
| `pull_quote` | Customer/exec quote with attribution. Verbatim source only. ≤30 words. |
| `two_column` | Compare exactly 2 things (before/after, shipped/slipped, option A/B) |
| `do_dont` | Behavior contract: DO card vs DON'T card |
| `bullets` | Last-resort content slide; default away from this |

**Always reach for visual templates first.** Bullets slides are functional but uniform; a deck of 8 bullets-only slides reads as a wall of text. The decision flow in `references/template-catalog.md` should drive every slide choice — if `bullets` appears in your outline >2 times, audit each one to find a `flow_steps`, `three_card`, `comparison_2x2`, `key_stat`, or `metric_grid` it could become instead.

For full style spec (palette, typography, footer rules), read `references/hims-hers-style-guide.md`.

## Style rules when authoring slide content

These are non-negotiable. They come from your CLAUDE.md (operator profile at `~/.claude/CLAUDE.md`) hard linguistic rules:

- **Sentence case** for slide titles ("Migration health", not "Migration Health")
- **No em dashes** anywhere. Use commas, periods, parentheses, or split sentences.
- **No throat-clearing** ("It's worth noting", "Importantly", "As mentioned above")
- **No padded adjectives** ("significant", "key", "important") unless removing them changes meaning
- **Numbers need unit + source + date** — "83% migrated, per DX project tracker, May 2026"
- **Attribute to role, not name**, unless the source explicitly names the person. "e-team" not "skip-level execs", "leadership" not specific names.
- **One sentence per bullet**, two max
- **Bullets max 6 per slide** (CLI enforces this; outline validation will fail with >6)
- **Cards max 3** per exec_summary (McKinsey rule of three; CLI enforces)

## Drive folder ID extraction

Given `(internal link)`, the folder ID is the segment after `/folders/`.

Given just a folder name, use Drive MCP `search_files` with:
```
title = 'FolderName' and mimeType = 'application/vnd.google-apps.folder'
```

Pass the resolved ID as `parent_folder_id` in the outline JSON.

## Stateful outputs

Every build writes `outputs/YYYY-MM-DD-<slug>.json` containing the full outline, deck URL, slide count, and template mix. Use these for:
- **"What did I build last time?"** → list `outputs/` and grep
- **"Rebuild that deck but with X"** → read the prior outline, modify, rerun the CLI
- **"Show me a deck like the one I made for cpo"** → search outputs by slug and audience

Old outputs accumulate. They're small (~1 KB each); no rotation policy needed in v1.

## Failure modes & recovery

| Symptom | Cause | Fix |
|---|---|---|
| `FileNotFoundError: slides-oauth.json missing` | OAuth client JSON not at `~/.config/gcloud/slides-oauth.json` | User downloads desktop-app OAuth JSON from GCP Console and saves to that path |
| Browser opens but consent fails | User not added as Test User on OAuth consent screen | GCP Console → APIs & Services → OAuth consent screen → Audience → Test users → add user's Gmail |
| `HttpError 403: insufficientScopes` | Scopes changed since last token | Delete `~/.config/gcloud/slides-token.json` and re-run; OAuth flow re-runs once |
| Deck created but Poppins shows as default | Poppins not enabled in user's Slides account | One-time: open deck → any text → font dropdown → "More fonts" → search "Poppins" → OK |
| CLI exits with "Outline validation failed: slides[N].bullets has 8 items; max is 6" | Style rule enforced | Split bullets across two slides, or cut to the 6 most important |
| CLI exits with "slides[N].cards has 4 items; max is 3" | exec_summary max-3 rule | Pick the 3 strongest, drop the 4th |
| Outline approved but a slide came back wrong | Outline mismatch or content drifted from source | Delete the slide manually in Slides UI; do not try to re-run the whole deck — call the relevant `hh_*` method directly from a one-off Python snippet |
| QA agent returns FIX_REQUIRED | One or more slides FAIL the rubric (off-canvas, overlap, missing footer, wrong template) | Surface the FAILs and suggested fixes to user; propose specific outline edits; rebuild; re-run Step 4 QA. Never share the URL with FAILs unresolved. |
| QA agent returns REBUILD | >30% of slides FAIL the same way — skill-level layout bug, not content | Flag to user as a maintainer issue ("layout template is broken, want me to investigate?"). Do not silently retry; the layout fix has to land first. |
| QA agent returns SHIP_WITH_WARNINGS | WARNs but no FAILs (cramped layout, Title Case, padded adjective, etc.) | Share the URL with the warnings listed up front. Ask the user which (if any) they want fixed. |

## Out of scope (v1, will fail loudly if attempted)

- Editing existing decks (no `update_*` methods on `SlidesClient`)
- Image slides with brand photography (image-by-URL works; no asset library)
- Framework table (Template C in style guide; deferred)
- Launch overview grid (Template F; deferred)
- Charts / data viz (use Looker screenshot → image URL until v2)
- Speaker notes
- Theme master swaps (we override per-slide via shape placement, which is the spec-recommended approach)

If the user asks for any of the above, build what's possible with available templates, then flag the gap explicitly in the follow-up message.

## Quick reference: full toolchain

```bash
SCRIPTS=~/.claude/skills/make-deck/scripts

# Health check before a high-stakes deck (run once at session start):
python3 $SCRIPTS/doctor.py
# (verifies OAuth, token, Slides API ping, Drive write, Poppins, outputs dir)

# Build:
python3 $SCRIPTS/build_deck.py /tmp/outline.json
# (returns deck URL on stdout; saves state to outputs/YYYY-MM-DD-<slug>.json)

# Render thumbnails for vision QA:
python3 $SCRIPTS/render_thumbnails.py <presentation_id>
# (writes /tmp/slides-eval/slide-NN.png for each slide)

# Programmatic pre-QA (fast deterministic checks before vision QA):
python3 $SCRIPTS/pre_qa_check.py <presentation_id>
# (catches em-dashes, bullet overflow, missing footer, off-canvas before tokens)

# Vision QA: spawn an Agent tool sub-agent with the prompt in Step 4b.

# Edit an existing deck (no full rebuild needed):
python3 $SCRIPTS/edit_deck.py /tmp/edit-plan.json
# (delete/reorder/replace_text/add_notes/replace_image ops)

# Looker chart → image URL for outline JSON:
python3 $SCRIPTS/looker_to_image.py <look-id-or-url> [--sample]
# (renders + uploads to Drive, returns drive.google.com/uc URL)

# List or clone prior decks:
python3 $SCRIPTS/list_decks.py [--audience NAME] [--search TEXT]
python3 $SCRIPTS/clone_deck.py <slug> [--new-title "..."]
# (clone writes /tmp/cloned-outline.json; user inspects and reruns build_deck.py)
```

CLI options for build_deck.py:
- `--no-save-state` — skip writing to `outputs/` (rare; use for test runs)
- pass `-` as the outline path to read JSON from stdin

## Editing existing decks

When the user has a deck and wants to change it (rather than rebuild from scratch), use `edit_deck.py` instead of rebuilding. Saves time and preserves the user's manual tweaks.

Edit-plan JSON schema:
```json
{
  "presentation_id": "1ABC...",
  "edits": [
    {"op": "delete_slide", "slide_index": 3},
    {"op": "reorder", "from": 5, "to": 2},
    {"op": "replace_text", "slide_index": 1, "find": "May 12", "replace": "May 13"},
    {"op": "add_notes", "slide_index": 4, "text": "...", "append": true},
    {"op": "replace_image", "slide_index": 7, "image_index": 1, "url": "https://..."}
  ]
}
```

All `slide_index` and `image_index` values are 1-indexed. The CLI validates the plan before any API call.

Use `SlidesClient.get_deck_outline(pid)` to read the existing deck's slide list (with text previews and layout hints) so you can target the right slide indices.

## Evals

`evals/evals.json` defines 3 realistic test prompts for the skill (exec status, complex strategic, short tactical). Run any of them manually in a fresh Claude Code session with `make-deck` loaded to validate the skill end-to-end. See `evals/README.md` for grading methodology.

## File index

| Where | What |
|---|---|
| `SKILL.md` | This file |
| `references/storytelling-principles.md` | Eight core principles + 4 story-arc spines |
| `references/storytelling-masters.md` | Research synthesis (Apple/Airbnb/Pixar/Duarte/Reynolds/Tufte/Minto/Anderson) — deeper patterns the validator does not yet enforce |
| `references/template-catalog.md` | Decision flow for picking templates |
| `references/templates/<name>.md` | Per-template content rules |
| `references/qa-rubric.md` | Vision QA grading rubric |
| `references/hims-hers-style-guide.md` | Brand palette/typography spec |
| `references/audiences/<name>.md` | Per-audience role templates (cpo, vp-eng, svp-eng, cmo, skip-level, pm-peer). Copy + customize. |
| `scripts/slides_client.py` | Core client (build + edit methods) |
| `scripts/build_deck.py` | Outline → deck CLI |
| `scripts/edit_deck.py` | Edit-plan → existing deck CLI |
| `scripts/render_thumbnails.py` | Deck → PNGs for vision QA |
| `scripts/pre_qa_check.py` | Fast deterministic pre-QA |
| `scripts/doctor.py` | Health check |
| `scripts/list_decks.py` | Index of prior runs |
| `scripts/clone_deck.py` | Dupe a prior outline |
| `scripts/looker_to_image.py` | Looker chart → Drive-hosted image URL |
| `outputs/` | One JSON per built deck (outline + URL + slide_count + template_mix) |
| `evals/evals.json` | Test prompts for skill verification |
