# Content rules for journey maps

Read before designing the journey (Step 3). These rules come from shipped maps and the edits presenters made to them by hand. Each rule names the failure it prevents.

## The shape of a good map

- **Five stages is the sweet spot.** Use 3 to 6. Name each stage for what happens ("Chart review"), not for an emotion.
- **One idea per callout, and about one callout per stage.** A second callout fits only when the stage carries two different kinds of evidence (a voice quote plus a research finding) *and* the curve is flat enough there to leave room on both sides. Where the curve dives through a stage, choose the stronger callout and put the other in the notes. The renderer enforces this. (Presenters cut extra quotes and stats by hand when a map was overstuffed.)
- **Put the pain where it happens.** If a reply is templated at check-in, the evidence goes in the check-in column, not in a generic "messaging is bad" stage.
- **Follow the persona.** The curve tracks the primary persona's experience: 1 = best, 5 = worst. Set sentiment from the evidence, not for drama. The worst point should sit where the strongest evidence is.
- **End on the bridge.** If the slide sets up a demo or proposal, the bottom band's right side ("What we built", "Opportunities") names what addresses the pain in one line per item. The slide doesn't recap.
- **Title:** When the slide is inserted into a larger deck, use a plain label ("Example patient journey"). The argument ("What we gain in efficiency, we often lose in patient experience") goes in the talk track, unless the user wants it as the title.

## Personas

- Label any made-up persona "(illustrative)" in their name line, and say so in the first line of the notes.
- The scenario line states what the persona wants, in their terms ("Wants a decision while she's motivated, from a provider who reads what she wrote"). It may be framing, but it must be consistent with the evidence.
- For the second persona, the description states the forces on them: incentive, workload, tools ("Paid per completed treatment decision, working a queue, with a snippet two clicks away"). This keeps the system visible and stops the map from blaming the person.
- Avatars are single-codepoint emoji (👩, 🧑, 🩺, 🎧, 💻). Joined and skin-tone emoji break apart in Slides; see `layout-and-qa.md`.

## Stage lines

- **Order the lines by who acts first in that stage.** At "Info request," the provider asks, then the patient answers. At "Submit," only the patient acts, so drop the provider line.
- Use plain verbs at present-tense: "Asks Meg questions to complete her chart, one of which she already answered."
- **Ask the user about domain mechanics you can't verify.** In a real build, the first draft put "sends a snippet" at the info-request stage. The domain owner corrected it: snippets mostly happen at decision (fine) and check-in (bad). Behaviors like these are ask-first.
- **Without a measured rate, prefer soft frequency words.** If no source measures a behavior ("asks for info already in the chart"), write "sometimes," or describe one instance ("one of which she already answered"), and give the closest measured proxy in the notes. If the measured rate is small, don't call the behavior "often."

## Quotes

- They must be verbatim from a source you read this run. Shorten only with "..." at a natural cut.
- Watch for hand edits that drift. A presenter rewrote "I still don't even know at this point, what's their BMI" as "I'm scrolling, scrolling… I still can't even find their BMI…" and relabeled a feedback session as a "shadowing session." Both changes made the quote and its attribution untrue. Flag drift like this; don't adopt it.
- Attribute by role and context ("Clinical educator," "Escalation clinician"). The full name, credentials, and date go in the notes.
- **Real exchanges** (a customer message and the reply) go in an `exchange` callout. Give each bubble a bold speaker label ("Patient:", "Provider:"), use alternating bubble styles, and caption it "Real exchange, de-identified." The source must already be de-identified. Never show message IDs.
- Don't invent persona thought bubbles. If you have no real quote for a stage, use a stat or research callout, or nothing.

## Numbers and research

- Every on-slide number needs a footnoted, hyperlinked source in the fine print. The notes add the unit, the date window, the denominator, and any caveat (for example, "judge is directional," "unweighted average across six actions").
- **Use the newest version of a metric source.** A later scorecard tab or a re-sized model replaces the older figure. When versions disagree, show the user both and ask.
- **Derived numbers:** if the slide shows an average or roll-up that isn't printed in the source, recompute it from the source table, and state the method in the notes. (Example: 56%, 66%, and 65% were unweighted means across six action rows.)
- **No vague ranges** ("2 to 3 hours") unless the source gives a range. If it does, tag it `[estimate range]` in the notes.
- **External research can carry a systemic point** (e.g. information overload drives clinician errors and burnout). Requirements:
  - The citation has a working link.
  - The claim is phrased as a paraphrase, not in quote marks, unless it's verbatim.
  - The paraphrase stays within what the source supports.
  - Before using it, confirm the paper exists and actually says this.
- **Respect audience number rules.** If the user says "no dollar figures," none go on the slide. Notes may carry a one-line "if asked about dollars" answer, with its source.

## Sources and fine print

- Each source gets a short label ("Pre-Rx funnel monitoring," "Clinical educator session, Sep 2026," "Budd 2023") and an openable URL. The renderer numbers footnotes in order of first appearance and drops any source that's never cited.
- **Sourceless claims:** when the only source is a colleague's remark in a meeting, leave it uncited on the slide and in the notes. Citing a person by name as the source reads oddly to an audience. Say so in the include/exclude list.
- Recording links (Fathom, Zoom) may need access. Mention this when you present.
- **After any hand edit, check for orphans:** a superscript with no source, or a source whose callout was deleted.

## Speaker notes

- The notes are a talk track, one block per stage, in the order you'll present.
- **First line:** the persona caveat, and what the curve means ("up is good, down is bad").
- **Each block:** what to say, the fuller verbatim quote, the caveats, then `Source:` lines with author or owner and date.
- **Read-aloud cues** go where they're needed ("Read it aloud and pause after the provider line").
- **The last line is the transition** to whatever comes next ("let me show you what we built").
- Names are allowed in notes for traceability. PHI and message IDs are never allowed.

## Writing mechanics (slide face and notes)

- No em dashes. Use a comma, colon, period, or parentheses.
- Use plain language for operations audiences, and define jargon once in the notes.
- Use sentence case.
- Emphasis goes on the number or the one word that matters (`**~44%**`, `**not**`), not whole sentences.
- If the workspace has a forbidden-writing-patterns file or a voice guide, run its hard searches on all copy before content QA.
