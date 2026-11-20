# Storytelling principles for make-deck

Decks fail when they're built as a list of facts instead of an argument with a shape. This file is the philosophy the skill enforces. Read it before designing any outline.

## Core principles

### 1. Lead with the answer (pyramid principle)
The exec_summary lives at slide 2, not the end. Audiences decide whether to lean in or check out in the first 30 seconds; if the conclusion is buried, they check out. Every deck >5 slides MUST have an exec_summary directly after the cover.

### 2. Tell the audience where you're taking them (agenda)
Every deck of 8+ slides MUST have an `agenda` slide at position 3 (after cover and exec_summary). Without it, the audience is guessing where you're going for the entire deck — that cognitive load makes them stop listening.

The agenda lists 3-6 sections (not every slide). It primes pattern-matching: when the audience hits section 2, they think "ah, here's the design part" rather than "wait, where are we?"

### 3. Anchor every section to the spine (moving blueprint)
For decks of 12+ slides, replace every section_divider with a `moving_blueprint`. This shows the full deck structure with the current section highlighted, so the audience always knows "I'm in section 2 of 4."

A moving blueprint is more than navigation; it's a reminder of the story arc. The audience holds the shape of the argument in their head, which is how they remember it later.

### 4. One idea per slide
The biggest density mistake: cramming three points onto one bullets slide because they're related. Related is not the same as belongs-together. If a slide has 5 bullets, it has 5 ideas, and the audience remembers zero. Split into 5 slides with one idea each, or pick the 1 idea that matters and cut the rest.

Practical heuristic: if you can't say the slide's takeaway in 5 words while pointing at the screen, the slide is doing too much.

### 5. Less words is better (the voice-over rule)
Every word on a slide is a word the speaker can't add. Slides are not handouts; they're a backdrop for the presenter's voice. The slide carries the **headline**; the speaker carries the **story**; the speaker notes carry the **detail the speaker needs to remember**.

For every line you'd put on a slide, ask: "Is this the headline, or the story?"
- Headline (on slide, 3-5 words): "Eligibility filters work"
- Story (spoken aloud): "License, treatment scope, role, and capacity all enforce correctly today, no change proposed."
- Detail (in speaker notes): "Verified in emr_service via Code Explorer. the eng leader's prior question on this was answered in the March review; don't relitigate."

Hard limits (the CLI validators enforce most of these):
- Cover subtitle: ≤8 words
- Exec summary lead: ≤25 words (one sentence)
- Exec summary cards: ≤6 words each (headline phrases, not full sentences)
- **Bullets: ≤5 words each (headline style), ≤4 bullets per slide (validator caps at 6 but 4 is the design target). If you can't get under 5 words, you have two ideas; split or push to notes.**
- Flow steps: ≤6 words per step
- Big idea slide: ≤15 words total
- Pull quote: ≤30 words

If content exceeds these, the slide has too much. Cut, don't shrink the font. Move the cut content to speaker notes; that's what notes exist for.

### 6. Visuals support the story; they don't tell it
A chart on a slide is not a story; the speaker's narration about the chart is the story. The chart's job is to make the speaker's claim visible at a glance, not to be a self-contained explanation.

This means:
- Charts get one annotation that calls out the takeaway ("Q2 spike →") instead of being unannotated
- Comparison_2x2 slides have 1-2 sentence quadrant labels, not paragraphs
- Pull quotes show the customer's words; the speaker explains why they matter
- Diagrams have minimal labels; the speaker fills in the connections

If a deck reads cleanly without a speaker, it's a memo, not a deck. Send it as a doc.

### 7. Pace with visual variety
A deck of 12 bullets slides is a wall of text even if each slide is perfect. The eye and the brain need variety to stay engaged. Default template mix for any deck >8 slides:

- ≥1 cover
- ≥1 exec_summary
- ≥1 agenda (decks >8 slides) or moving_blueprint (decks >12 slides)
- ≤3 consecutive bullets slides anywhere
- ≥1 of {flow_steps, three_card, comparison_2x2, key_stat, metric_grid, big_idea, pull_quote} per 4 content slides
- ≥1 section_divider or moving_blueprint per major section

The QA agent checks for visual monotony and WARNs on 3+ consecutive bullets-only slides.

### 7b. Build to one STAR moment (per deck)
Duarte's "Something They'll Always Remember" (Resonate, 2010, ch. 7). Apple keynotes call this the "boom" (Gallo, 2009, ch. 13). Every deck of 8+ slides MUST have exactly one anchor slide: a `big_idea`, `key_stat`, or `pull_quote`. The QA rubric FAILs decks with zero STAR slides and WARNs decks with 2+ (dilutes recall).

For status decks: the STAR is often the headline metric (`key_stat` with the one number that matters). For recommendation decks: the STAR is the `big_idea` with the recommendation. For deep-dives: the STAR is a `pull_quote` from a customer or expert.

### 7c. Action titles for exec audiences
Mayer (Multimedia Learning, 2001) and McKinsey's "action title" pattern: the slide title carries the takeaway as a full sentence ("Migration is 83% complete; one blocker remains"), not a topic label ("Migration status"). When the modifier is `for cpo`, `for vp-eng`, `for svp-eng`, or `for skip-level`, default to action titles. Slide bullets/cards then prove the title's claim.

### 8. End on an action, not a recap
The last content slide before close should be a `do_dont`, a `big_idea`, or a forward-looking `bullets` slide titled "Next 30 days" or "What we need from you" — not a "Summary" recap. The exec_summary at slide 2 IS the summary; a closing recap is redundant and wastes the last attention moment.

The exception: if the deck is read async (no presenter), a closing recap is justified. Otherwise the close is forward-motion.

## Story arc structure

Every deck >5 slides should follow one of these spines. Pick during outline phase:

### Spine A: Update / status (most common for PM decks)
1. Cover
2. Exec summary (TL;DR + 3 principles or themes)
3. Agenda
4. Section 1: Where we are (where this lands today; data, milestones)
5. Section 2: What changed (what shifted since last update)
6. Section 3: What's next (next 30/60/90 days)
7. Section 4: What's at risk (blockers, asks)
8. Close: ask / decision needed

### Spine B: Recommendation / pitch
1. Cover
2. Exec summary (the ask up front)
3. Agenda
4. Section 1: Context (the problem, why now)
5. Section 2: Options considered (2-4 options as comparison_2x2 or three_card)
6. Section 3: Our recommendation (the pick + why)
7. Section 4: How we'd execute (flow_steps)
8. Close: decision, what we need from the audience

### Spine C: Deep dive / education (technical decks, briefings)
1. Cover
2. Exec summary (the headline insight)
3. Agenda
4. Section 1: The map (architecture, players, what connects to what)
5. Section 2: Flow A end-to-end (flow_steps)
6. Section 3: Flow B end-to-end (flow_steps)
7. Section 4: Edge cases or gotchas (do_dont, comparison_2x2)
8. Close: how to talk about this with eng / next read

### Spine D: Pre-mortem / risk briefing
1. Cover
2. Exec summary (the risk + likelihood)
3. Agenda
4. Section 1: What we know (current state)
5. Section 2: What we don't know yet (open questions)
6. Section 3: Scenarios (comparison_2x2 of likelihood vs impact)
7. Section 4: Mitigations (do_dont or flow_steps)
8. Close: decision needed today vs later

## When to break a principle

These principles are defaults, not laws. Break them when the audience or content demands it. But the break is a decision you make, not an accident. If you skip the agenda, it's because the deck is <5 slides and the audience already knows the topic. If you do 6 bullets on one slide, it's because they're a checklist not bullet points.

The skill enforces hard rules (em dashes, footer on content slides, 6-bullet cap, 3-card cap). These principles are soft guidance the QA agent uses to WARN on density and pacing.
