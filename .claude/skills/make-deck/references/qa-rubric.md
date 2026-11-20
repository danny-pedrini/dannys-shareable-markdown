# make-deck QA rubric

The QA agent reads this file and grades each rendered slide thumbnail against the rubric below. Grades are slide-level (PASS / WARN / FAIL) and roll up to a deck-level verdict (SHIP / SHIP_WITH_WARNINGS / FIX_REQUIRED / REBUILD).

## Why QA exists

The skill kept shipping decks with off-canvas content even after layout "fixes" because the user had to spot the bug visually. The QA pass turns that into an automated gate: render thumbnails → vision-grade every slide → only surface the URL to the user once issues are surfaced or resolved. Building the deck is cheap (~30s); shipping a broken deck wastes the user's attention.

## How to use this rubric (QA agent instructions)

You are a dedicated QA agent. You will receive a list of slide thumbnail paths and the deck's outline JSON. For each thumbnail:

1. Read the PNG using the Read tool
2. Compare what you see against the rubric below
3. Assign one verdict per slide: **PASS**, **WARN**, or **FAIL**
4. For any non-PASS slide, give a one-line specific `issue:` and a one-line concrete `fix:`

After grading every slide, output the overall verdict.

Output format (markdown, no preamble):

```
slide-01: PASS
slide-02: WARN
  issue: lead paragraph wraps to 4 lines, eats card space
  fix: cut "illustrative" from "Follow two illustrative patients"
slide-03: PASS
slide-04: FAIL
  issue: right column "Marcus (patient path" truncated at slide edge
  fix: skill-level layout bug, escalate to maintainer
...
OVERALL: FIX_REQUIRED (1 FAIL, 1 WARN)
SUMMARY: <2-sentence plain-English summary of what's wrong and what to do>
```

## FAIL conditions (block shipping)

A FAIL means the deck is not presentation-ready. Any one of these triggers FAIL:

1. **Off-canvas content** — any text or shape extending past the visible slide edge (right, bottom, top, left). Look for letters or shape edges that touch the rendered image border with text continuing past it.
2. **Empty card or panel** — a card/rect background renders but its child text is missing or empty
3. **Severe overlap** — title text overlapping body text, lead text overlapping a panel header, two shapes covering each other
4. **Missing footer** on a content slide (cover, section_divider, key_stat are exempt; everything else needs the confidentiality footer)
5. **Wrong template applied** — outline said `flow_steps` but you see a bullets slide, etc.
6. **Hard linguistic violation** — visible em dash (—) anywhere on the slide. your CLAUDE.md (or your operator profile) hard-bans em dashes.
7. **Recap closing** — final slide titled "Summary", "Recap", "Conclusion", or "In summary". Decks end on forward motion (action, ask, decision), not a recap. The exec_summary at slide 2 IS the summary. (Per Anderson, TED Talks, 2016, ch. 13; Duarte, Resonate, 2010, ch. 10.)
8. **Throat-clearing cover** — cover subtitle starts with "Overview of...", "We will cover...", "This deck...", "Today's agenda...". The cover sets up tension or makes a promise (per Jobs/Gallo and Chesky/Airbnb); it never describes what the deck is "about."
9. **Visual monotony FAIL** — 4 or more consecutive bullets-only slides. (Was a WARN at 3+; bumped to FAIL at 4+ because that's where recall drops sharply per Medina, Brain Rules, 2008, Rule 10.)
10. **Missing STAR moment** — zero `big_idea`, `key_stat`, or `pull_quote` slides in a deck of 8+ slides. Every deck needs one "Something They'll Always Remember" anchor (Duarte, Resonate, 2010, ch. 7; Gallo on Jobs' "boom" moments, 2009, ch. 13). If 2+ STAR slides exist, WARN — too many anchors dilutes recall.

## WARN conditions (ship is OK, but flag)

A WARN means the slide works but isn't optimal. Surface these so the user can decide:

1. **Cramped layout** — bullets running 3+ lines each, body text touching panel edges, card text wrapping awkwardly mid-word
2. **Title wraps to 3+ lines** — title is too long
3. **Lead paragraph wraps to 4+ lines** — lead is too long, eats body space
4. **Asymmetric cards/columns** — one card has 1 line, another has 4 lines (visual imbalance)
5. **Title Case instead of sentence case** — "Executive Summary" should be "Executive summary"
6. **Padded adjective without meaning** — "significant", "key", "important" used as filler
7. **Naked number** — a stat without unit + source + date when context demands it
8. **Visual monotony** — three or more consecutive bullets-only slides (deck feels like a wall of text)
9. **Footer text wraps to 2 lines** — should fit on one (means margins are wrong)

## PASS criteria

A PASS slide:
- All content within the visible canvas
- No overlapping shapes/text
- Title fits in 1-2 lines
- Footer present on content slides, single line
- Sentence case title
- No em dashes, no padded adjectives, no obvious typos
- Cards/columns visually balanced
- Template renders as expected

## Overall verdict

Compute after all slides graded:

- **SHIP** — Every slide PASS
- **SHIP_WITH_WARNINGS** — Some WARNs, zero FAILs. Surface warnings to user; they decide whether to iterate.
- **FIX_REQUIRED** — One or more FAILs. The deck has broken slides; main thread must propose fixes and rebuild before sharing the URL.
- **REBUILD** — More than 30% of slides FAIL with the same layout-level issue. This signals a skill-level layout bug, not content; escalate to maintainer (in practice: rebuild after a skill fix, not just a content edit).

## What the main thread does with the verdict

| Verdict | Main thread action |
|---|---|
| SHIP | Share URL with user. Brief one-line summary. |
| SHIP_WITH_WARNINGS | Share URL but list warnings up front. Offer to fix any the user cares about. |
| FIX_REQUIRED | Do NOT share the URL yet. Surface the FAILs to user, propose specific outline edits (which slides to rewrite, which content to cut), rebuild, then re-QA. |
| REBUILD | Surface to user as a skill bug ("layout-level issue, want me to investigate the template?"). Do not silently re-attempt. |

## Common edge cases

- **Section dividers don't need footers**. The style guide explicitly omits footers on dividers; a missing footer there is not a FAIL.
- **key_stat doesn't need a title**. The big number IS the headline; an absent title is not a FAIL.
- **key_stat anatomy is intentional, not a bug.** A `key_stat` slide is SUPPOSED to render as: a large sage-accent numeral (the headline number) → bold ink label below it → optional small caption beneath. If you see a big floating "5" or "83%" with a label below and caption beneath, that is the template working as designed. **Do NOT flag it as an "orphan numeral" or "stray label"** — that's a false-positive. The big number IS the slide's headline; the label tells you what it counts. Only flag key_stat slides for actual issues: caption wrapping to 4+ lines, label missing, number off-canvas, etc.
- **Cover slide doesn't need a footer**. Same as section divider — intentionally clean.
- **Agenda slides don't need a body footer** — the numbered list IS the content.
- **moving_blueprint slides don't need footers** — they're navigation, not content.
- **big_idea slides don't need footers** — the single bold statement is intentionally clean.
- **Long technical names that wrap** (e.g., `complete_appointment`, `ClassificationModelOutputPersistence`) get a WARN, not a FAIL, if they wrap mid-name but remain readable. Suggest abbreviation in the fix.
