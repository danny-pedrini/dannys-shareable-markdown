# Forbidden writing patterns

Check every draft against this list before delivery. **Hard verification searches** must PASS (zero matches unless noted). **Watch for** items require a read and rewrite when obvious; they are not automatic FAIL on grep alone.

> **Source:** Ruben Hassid, LinkedIn post on AI writing tells (Aug 2026). Adapted for Danny's workspace.

## Patterns

| #   | Pattern                                      | Bad                                                                                      | Fix                                                                                               |
| --- | -------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| 0   | Em dash                                      | "Hi all — quick intro" / "Phase 1 — Complete the Chart"                                  | Use a period, colon, comma, or parentheses: "Hi all. Quick intro" / "Phase 1: Complete the Chart" |
| 1   | "That's not X. That's Y."                    | "That's not compliance. That's stalling."                                                | Say the second half only: "They're stalling."                                                     |
| 2   | AI slop fragments (watch for)                | "Fast. Simple." / "No fluff. Just answers." (adjective/adverb pairs with no verb)       | Merge into one sentence, or use intentional punch with a verb ("Three phases. One CDS engine.")     |
| 3   | Metaphor with no action                      | "Less a hammer, more a scalpel."                                                         | Say what to do instead.                                                                           |
| 4   | Self-applause                                | "And that matters." / "That's the part everyone misses." / "Which is exactly the point." | Delete. You lose nothing.                                                                         |
| 5   | Analogy to something the reader may not know | "It's the Excel of AI agents."                                                           | Explain directly, or drop the analogy.                                                            |
| 6   | Throat-clearing openers                      | "Here's the thing." / "Let me be clear." / "The truth is."                               | Start one sentence later.                                                                         |
| 7   | Always exactly three items                   | "Faster, cheaper, smarter."                                                              | Use however many fit: two, four, five. Never force a triplet.                                     |
| 8   | Vague ranges                                 | "5 to 10 minutes."                                                                       | One number ("7 minutes") or admit you do not know.                                                |
| 9   | Ending recap                                 | "In short..." / "At the end of the day..."                                               | Stop on the strongest line. Do not repeat the whole post.                                         |

**Pattern #2 is not a violation** when short headline pairs in Slack or decks carry substance (e.g., a deck title and subtitle, or "Three phases." followed by "One CDS engine.").

## Also avoid (deck copy)

- Padded adjectives with no information ("significant," "key," "important") when deck copy applies. See `.claude/skills/make-deck/references/hims-hers-style-guide.md`.

## Hard verification searches

Run these against the draft text before delivery. **PASS = zero matches** for each search, unless the row says otherwise.

| #   | Search                                                                                     | How to run                                                                                                                                |
| --- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 0   | Em dash character `—`                                                                      | Search the full draft for `—`                                                                                                             |
| 1   | `That's not`                                                                               | Case-sensitive phrase search                                                                                                              |
| 3   | `less a` + `more a` (same sentence)                                                        | Phrase search; rewrite if both appear as a contrast metaphor                                                                              |
| 4   | `And that matters` / `That's the part everyone misses` / `Which is exactly the point`      | Phrase search (any match = FAIL)                                                                                                          |
| 5   | `It's the .* of`                                                                           | Regex or read for "X of Y" product analogies; rewrite to direct explanation                                                               |
| 6   | `Here's the thing` / `Let me be clear` / `The truth is` / `To be clear` / `I'll be honest` | Phrase search at sentence start                                                                                                           |
| 7   | Exactly-three parallel lists                                                               | Read: no comma-separated triplet of single adjectives/nouns used as the whole argument (e.g., "Faster, cheaper, smarter."). Manual check. |
| 8   | `\d+\s*(to|-)\s*\d+`                                                                       | Regex for numeric ranges like "5 to 10" or "5-10"; FAIL unless tagged `[Assumption: X (needs validation)]` or `[estimate range]`          |
| 8b  | `several` / `a few` / `some time`                                                          | Phrase search for vague quantity/time; FAIL unless tagged `[Assumption: X (needs validation)]` or replaced with one number                |
| 9   | `In short` / `At the end of the day` / `To summarize` / `In conclusion` / `Bottom line:`   | Phrase search in the final paragraph or final 3 bullets                                                                                   |

After any FAIL, rewrite the hit and rerun **all** hard search rows from the top.

## Watch for (judgment, not automatic FAIL)

| #   | Pattern | When to rewrite |
| --- | ------- | --------------- |
| 2   | AI slop fragments | Consecutive sentences that are both under 4 words AND neither contains a verb. Rewrite when it reads like AI marketing cadence. Do not flag intentional deck/Slack punch (see Pattern #2 note above). |

## Compression slop (watch for)

These patterns show up when a draft holds too many points and gets squeezed to fit. The fix is usually to cut a point or explain it in plain words, not to reword the dense sentence. Read every draft for them. They are judgment calls, not grep checks.

> **Source:** Danny Pedrini, Nov 18, 2026, comparing his Feature X brief with AI drafts. Bad examples are from `Quality-of-Care/Phase-2/PRD-AI-Recommended-Next-Actions-v2.md` and `Quality-of-Care/Feature-X/Feature-X-One-Pager.md`.

| #   | Pattern | Bad | Fix |
| --- | ------- | --- | --- |
| C1  | Shorthand the reader was never given | "The action type has passed Back data, and the model's confidence on this task clears that type's threshold." | "A recommendation only shows when the model has already proven accurate for that action on past visits and is confident about this patient." |
| C2  | Abstract stand-in for a plain statement | "If it is not, we walk down to the most impactful compromise Legal allows." / "what it does to our regulatory posture" | "In the event this most impactful version of the feature is not feasible, we propose less risky, though less impactful, alternatives." / "whether it changes the product's regulatory status" |
| C3  | Pointer instead of explanation | "(see Dependency 1)," "(see Vision)," "(open question 6)" scattered through the body. The PRD has 20 "(see" pointers; Danny's brief has 5. | Say the one fact the reader needs right there. Keep a pointer only when the other section holds more than a sentence the reader needs. |
| C4  | Stacked qualifiers | "Neither its fixed nor its AI-written text says the system 'recommends' or presents the action as the default." | "Nothing on the card says the system 'recommends' the action or treats it as the default." |
| C5  | Names a thing without saying what happens | "Keeps the LLM to the rationale, which narrows what Legal reviews and what the rationale rubric covers." | "If the headline is fixed text, only the rationale is AI-written, so Legal and the rubric only have to cover that part." |
| C6  | The same point made more than once | The PRD says it will test the 30% time savings assumption before build in the TL;DR, the Feature impact line, and the pre-build study. | Say it once where the reader needs it. A TL;DR may preview it; the body says it once. |

## Living document

Add a row when Danny catches a new pattern. This file is the living ban list.
