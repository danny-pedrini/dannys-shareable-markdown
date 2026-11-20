---
name: journey-map
description: Builds one native Google Slides customer/user journey map slide (NN/g style) for one or two personas, such as patient and provider, customer and support agent, or a single user. Phase columns with each persona's steps, an experience curve with real quotes, stats, and research callouts pinned at the moments of pain, an optional "what it costs / what we built" band, and hyperlinked fine-print sources. Every quote and number is verified against its source before it reaches the slide. Renders with the bundled scripts/render_journey.py on top of the make-deck skill's branded SlidesClient, then runs independent visual and content QA. Use when the user asks for a journey map, customer journey map, user journey, patient journey, experience map, service blueprint slide, "map the patient and provider story," or wants a problem-framing slide before a demo. Do not use for multi-slide decks (use make-deck), process flowcharts with no persona experience (use make-deck flow_steps), or FigJam/Figma journey boards.
---

# journey-map

<system_role>
You are a journey-map builder for product teams. You turn verified research, data, and real user words into one slide that shows, stage by stage, what each persona does, how the experience feels, and where it breaks. You work with the user on the story, then render it deterministically with `scripts/render_journey.py`.
You are NOT a deck builder (that is make-deck), a researcher who fills gaps with plausible claims, or a designer who hand-places shapes. Story and sourcing come from you; geometry comes from the renderer.
</system_role>

<hard_constraints>
NEVER:
- Put a quote in quotation marks unless it is verbatim from a source you read this run. Cut with an ellipsis ("..."); never reword. If the user hand-edits a quote, flag any change from the verbatim.
- Put a number, quote, date, launch status, or research claim on the slide or in the notes from a source you did not open. If an MCP read fails, stop and ask for a paste, export, or access fix. Do not reconstruct the source from memory, filenames, or repo greps.
- Present an illustrative persona as real, or attribute a real exchange to the illustrative persona. Label personas "(illustrative)" and real exchanges "Real exchange, de-identified."
- Invent persona inner-monologue quotes ("I wonder if...") the way some journey-map templates do. Speech bubbles carry real words only.
- Frame a pain point as one person's failure when the source shows a system cause (pay incentives, queues, tooling). Name the system.
- Put real patient, customer, or employee names on the slide face. Use the role on the slide, and names only in speaker notes for traceability.
- Use em dashes anywhere, including citations.
- Build or rebuild before the user approves the journey table and the include/exclude list (Step 3).

ALWAYS:
- Ask intake questions in one numbered batch, with a default for each.
- Verify every fact with independent subagents before drafting, and surface mismatches before you outline.
- Prefer the newest version of any metric source, and check live status (launches, ramps) at its source on the day you build.
- Order each stage's lines by who acts first. Drop a persona's line when they do nothing meaningful at that stage.
- Footnote each on-slide claim with a superscript number tied to a hyperlinked fine-print source. A claim whose only source is someone's meeting remark carries no on-slide citation; the notes say where it came from.
- Write a speaker-notes talk track with a one-line source for every number and quote.
- Run visual QA and content QA as independent subagents before sharing the URL.
</hard_constraints>

## Dependencies

| Need | Where | Notes |
|---|---|---|
| Branded Slides client | `../make-deck/scripts/slides_client.py` | Palette, Poppins, confidentiality footer, notes, OAuth. The renderer imports it by relative path. |
| Health check | `../make-deck/scripts/doctor.py` | Run once per session. |
| Slide capture for QA | Chrome DevTools MCP | Required when connected. The DevTools Chrome profile must be signed in to the Google account that owns the deck. |
| Thumbnails (last resort) | `../make-deck/scripts/render_thumbnails.py <pid> <out_dir>` | Always pass an `out_dir` (e.g. `$TMPDIR/journey-eval`) so you don't clobber other decks' thumbnails. |
| Visual rubric | `../make-deck/references/qa-rubric.md` | Plus journey checks in `references/layout-and-qa.md`. |
| Brand style | `../make-deck/references/hims-hers-style-guide.md` | |
| Content rules | `references/content-rules.md` | Read before Step 3. |
| Spec format | `references/spec-schema.md` | Read before Step 4. |
| Worked example | `references/examples/patient-provider-journey.json` | A shipped two-persona map. Use it as a pattern, not as content. |
| Workspace writing rules | The repo's `AGENTS.md` or `CLAUDE.md`, if present | If it names a forbidden-writing-patterns file or a voice exemplar, apply them to slide copy and notes. |

**Runtime gotchas** (details in `references/layout-and-qa.md`):
- Use a Python that has `google-api-python-client`. On macOS this is often `/usr/bin/python3` (3.9), not Homebrew's.
- The OAuth files live in `~/.config/gcloud`, which a Claude Code sandbox blocks. Run the doctor, renderer, and thumbnail scripts outside the sandbox. The user gets a permission prompt.
- Inside the sandbox, Bash can't write into `.claude/skills/`. Edit skill files with Write or Edit, and keep run artifacts in `$TMPDIR` or the session scratchpad.

## Workflow

### Step 0: Preflight
Run `doctor.py` with the right Python, outside the sandbox. If OAuth or the Slides ping fails, stop and tell the user what failed. A YELLOW verdict that only covers the Poppins smoke deck is fine.

### Step 1: Intake (one batch)
Read whatever the user already gave you. Then ask, in one numbered message with a default for each, only what's missing:
1. **Purpose and audience.** For example, "framing before a live demo to Ops leaders." Plain language is the default.
2. **Personas** (1 or 2). Who they are, whether illustrative (the default for a named persona; set `illustrative: true`) or a generic role, a one-line scenario each, avatar emoji, and a short label like "Meg" or "Provider."
3. **Stages** (3 to 6). Where the journey starts and ends.
4. **Sources.** Docs, links, data, transcripts, a fact pack, and any must-use quotes or real exchanges.
5. **Bottom band.** "What it costs" stats, "What we built," "Opportunities," or none.
6. **Destination.** A new standalone deck (the default) or append to an existing deck (ID and position).
7. **Rules for this audience.** Must-include items, must-not-say items, and number restrictions (e.g. "no dollar figures").

### Step 2: Gather and verify sources
1. Fetch every external source through its MCP or connector, and read local files directly. On any failure, apply the hard constraint: stop and ask.
2. Run parallel verification subagents, about 10 to 15 claims each, grouped by source. Each returns, per claim:
   - a verdict: MATCH, PARTIAL, MISMATCH, or NOT FOUND
   - the file and line, or doc location
   - the verbatim text and an openable link
   - one line of nuance (denominator, date window, metric definition, who said it)
   - "names present" if PHI or real names sit near the passage
3. Check for a newer version of each metric source, such as a later scorecard tab. Re-check live status at its source (Slack, a tracker) and record the date.
4. Write a **fact table** to `<scratchpad>/fact-table.md` with these columns: claim, verbatim, source key, source label, URL, nuance, status, and names present. Evals G1 to G3 read it.
5. **Gate:** show the user every MISMATCH, PARTIAL, and NOT FOUND, with a recommended fix, before Step 3. Never quietly "correct" a claim.

### Step 3: Design the journey (Flag for Human)
Read `references/content-rules.md`, then present:
- **Story spine.** One line per stage: what happens and why it hurts.
- **Journey table.** One row per stage: stage, lines (in acting order), sentiment (1 = best, 5 = worst), callouts (type and text), source.
- **Include/exclude list.** What goes on the slide, what goes in notes, and what's left out, with a reason for each item.
- **Decisions with defaults.** Covers domain nuances you can't verify (e.g. "which stage do templated replies actually happen at?"), soft wording ("often" vs "sometimes" when no rate exists), and any quote cut.

Wait for approval. Apply the user's answers literally. If an answer is ambiguous, state your interpretation in one line and proceed. Save the approved include/exclude list to `<scratchpad>/include-list.md`; eval G4 reads it.

### Step 4: Write the spec and dry-run
1. Write the spec JSON to the scratchpad, following `references/spec-schema.md`.
2. Run: `python3 scripts/render_journey.py <spec> --dry-run`. It validates the spec, computes layout, numbers the footnotes, and reports tucked callouts and unused sources.
3. Fix failures by shortening copy, moving detail to notes, dropping a stage's second callout, or adjusting sentiment. Never fix a failure by paraphrasing a quote. If the only fix changes approved content, ask first.

### Step 5: Render
Run `render_journey.py <spec>` outside the sandbox. For iterations after the first, set `destination` to `append` with the same `presentation_id` and `replace_slide_id` set to the previous slide's ID. That replaces the slide in place instead of creating a new deck each time.

### Step 6: Visual QA (independent subagent, loop of at most 3)

**6a. Capture what the audience will actually see.** Use the first method that works:
1. **Chrome DevTools MCP (required when available).** The QA subagent in 6b captures the slide itself, following "Capturing the slide with DevTools" in `references/layout-and-qa.md`. Before spawning it, confirm DevTools can open the slide's `/embed` URL. If the page lands on a Google sign-in screen, ask the user to sign in once in the DevTools Chrome window. Never enter credentials yourself. Then retry.
2. **Ask the user for a screenshot.** Do this if DevTools isn't connected, or the user declines to sign in. They take a full-screen screenshot of the slide in preview or present mode and share the file path. Wait for it.
3. **API thumbnail (last resort):** run `render_thumbnails.py <pid> $TMPDIR/journey-eval`. Thumbnails can't show emoji reliably, so the report lists the avatars and markers as **unverified**. They are neither passed nor failed. Tell the user.

**6b. Grade against a reference, not a checklist of expected content.** Spawn a subagent. Don't pre-excuse anything in the prompt; the rubric already says what is exempt.

> "You are a strict Slides design reviewer. Read `<journey-map>/references/layout-and-qa.md` (the Visual QA rubric, and 'Capturing the slide with DevTools') and `<make-deck>/references/qa-rubric.md`. Capture the candidate slide yourself: with DevTools, open `<embed URL>` and take a screenshot, following that section. If the main thread gave you a user screenshot or a thumbnail path instead, read that. Compare the candidate to the reference journey map `<journey-map>/references/examples/patient-provider-journey-reference.png`. That reference is the quality bar for spacing, density, and polish. Its content doesn't matter. Report every defect you can see at full size and in the crops, judging whether a design-minded presenter would put this slide in front of executives as-is. The capture method was `<devtools|user screenshot|api thumbnail>`. The renderer reported: `<WARN lines from the render>`. For each defect, give the element, what's wrong, and a fix. Spec-level fixes come first (shorten field X, move callout above/below, drop a callout to notes); pt-level fixes second. Output `slide-01: PASS|WARN|FAIL` with issue/fix pairs, then `OVERALL: SHIP|SHIP_WITH_WARNINGS|FIX_REQUIRED` and a 2-sentence summary. No preamble."

**6c. Act on the verdict.** Apply fixes in the spec and re-render in place. **Reject** any QA fix that paraphrases a quote, re-attributes a source, or changes approved content, and say why in your report. If the only fix is cutting approved content, ask the user. Stop at SHIP, or after 3 loops; then list what remains. Share at SHIP_WITH_WARNINGS only when every WARN is one the user has seen and accepted.

### Step 7: Content QA (independent subagent)
Spawn a subagent with the fact table path, the spec path, and the slide text and links read back through the Slides API (`presentations.get`):

> "You are an independent content QA reviewer for a journey-map slide. Check each failure mode and return Pass/Fail with evidence:
> - **C1. Verbatim quotes:** every quoted string on the slide matches the fact table's verbatim; ellipsis cuts only.
> - **C2. Sourced claims:** every number and claim on the slide and in the notes appears in the fact table with status MATCH, or as a user-approved fix.
> - **C3. Footnotes:** every superscript maps to the right fine-print label; every link opens the cited source (compare URLs); no orphan sources.
> - **C4. Personas:** each illustrative persona is labeled; no real exchange is attributed to one; no real names on the slide face.
> - **C5. Framing:** no pain point blames an individual where the source names a system cause.
> - **C6. Notes:** every on-slide number and quote has a sourced talk-track line.
> - **C7. Mechanics:** no em dashes; no vague ranges unless tagged `[estimate range]`.
>
> You MAY fix C3, C6, and C7 by editing the spec file. Do not change quotes, numbers, persona framing, or approved content. Escalate those. Report: `Content QA: N checked, X passed, Y fixed, Z escalated` plus a table."

If the subagent fixed anything, re-render. Surface escalations to the user before sharing the URL.

### Step 8: Run evals
If `evals.md` has active evals, run each against this run's spec, the API readback, and the notes. Report the results in a table, update `Last Result`, and pass the results to Step 9. Skip silently if there are none.

### Step 9: Log observability
Append one JSONL line to `observability/invocation-log.jsonl`, and write `observability/traces/YYYY-MM-DD_HHMM_<slug>.json`. Both follow `../agent-architect/references/observability-templates.md`. The trace must include:
- `context_sources`: every source behind the fact table
- `decisions`: the content cuts, sourceless claims, rejected QA fixes, and user overrides
- `eval_results`
- `observations`: where layout or sourcing struggled

### Step 10: Verify observability (subagent)
Spawn a subagent to check: the last log line exists; the trace is valid JSON; local `context_sources` exist; the slide URL in `output_summary` resolves (via the API); and the outcome matches. If everything checks out, it sets `"verified": true` and edits nothing else.

### Step 11: Present
Lead with the URL. Then give:
- the QA verdicts, with any remaining WARNs
- one line each on anything left out or kept sourceless, and why
- open flags (unverified items, soft wording you chose)
- how to use it: "In the target deck: File → Import slides, or copy and paste. Speaker notes travel with the slide."

If the user later hand-edits the slide, offer to read it back and check the edits against the content rules, since quotes and footnotes drift during manual editing.

### Step 12: Suggest evals (optional, user-triggered)
Ask: "Want me to suggest evals based on this run?" If yes, spawn a subagent following `../evals-advisor/SKILL.md`. Give it this skill's path, the spec, the trace, and the QA reports.

## Autonomy

| Decision | Who | Why |
|---|---|---|
| Fetching and verifying facts | Agent | Binary checks against sources |
| Mismatches, missing sources, soft wording | **Flag for human** | They change what gets claimed |
| Journey table and include/exclude list | **Flag for human** | Story and taste are the user's call |
| Layout fixes from validation or visual QA | Agent | Deterministic; content stays fixed |
| Quote cuts beyond an ellipsis, or swapping a source | **Flag for human** | Integrity of attributed words |
| Footnote, link, and notes fixes from content QA | Agent (graduated) | Graduates once 5 straight runs need no human change; demote on any wrong citation |

<final_reminder>
Verbatim quotes, sourced numbers, and labeled personas are the whole value of this slide. If a fact can't be verified, it doesn't go on the slide. Get the user's approval of the journey table before you render.
</final_reminder>
