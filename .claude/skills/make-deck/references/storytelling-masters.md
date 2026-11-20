# Storytelling masters: research synthesis for make-deck

Research synthesis distilling the canonical works on presentation storytelling and visual design (Jobs/Gallo, Pixar, Airbnb/Chesky, Duarte, Reynolds, Tufte, Minto/McKinsey, Anderson/TED, Medina) into specific, actionable changes for the make-deck skill.

This file complements `references/storytelling-principles.md`. That file holds the skill's existing eight principles. This file holds the upstream research those principles came from, the deeper patterns the skill does not yet enforce, and the file-by-file changes needed to close the gap.

---

## Executive summary (takeaways that should land in the skill)

1. **Frame every deck around tension, not topic.** Duarte's "what is vs. what could be" oscillation (Resonate, 2010, ch. 4) and Pixar's "story spine" (Coats, 22 Rules, Rule 4) both demand the deck open by establishing a gap. Action: rewrite `cover.md` and `exec_summary.md` to require a tension, not just a title.
2. **Every section transition is a re-statement of the gap, not navigation.** Duarte's sparkline (Resonate, p. 30) treats section breaks as oscillations between "what is" and "what could be." Action: extend `moving_blueprint.md` and `section_divider.md` to require a subtitle that re-states the gap, not just the section name.
3. **Build to one "STAR moment."** Duarte's Something They'll Always Remember (Resonate, ch. 7). Apple keynotes call this the "boom" (Gallo, Presentation Secrets of Steve Jobs, ch. 13). Action: require one `big_idea`, `key_stat`, or `pull_quote` slide flagged as the STAR moment per deck, and gate QA on its presence.
4. **Answer-first, then SCQA.** Minto's Pyramid Principle (Minto, 1987, ch. 2) and McKinsey's SCQA frame (Situation, Complication, Question, Answer) say the exec_summary must lead with the answer, then justify with three supporting points. The skill already does answer-first; the gap is forcing three (not 1 or 4) supporting points and labeling them as Situation/Complication/Resolution. Action: rewrite `exec_summary.md` to require exactly 3 cards mapped to S-C-R, with the lead carrying the answer.
5. **Cut the slide count in half, every time.** Reynolds (Presentation Zen, 2008, ch. 3) and Kawasaki (10/20/30 rule, blog 2005) both argue most decks have 2x the slides they need. Action: add a QA WARN when slide count exceeds (audience size + audience expertise + question complexity), and bias `short` modifier as default for exec audiences.
6. **One idea per slide is a working-memory law, not a style preference.** Miller's 7±2 (Psychological Review, 1956) and Sweller's cognitive load theory (Cognitive Science, 1988) explain why a 5-bullet slide produces zero recall. Action: harden the bullets-cap from 6 (current validator) to 4 in the design target, and have QA WARN on 5-6 bullet slides even though they pass the validator.
7. **Charts get a "so what" annotation; data alone is not a story.** Tufte (Visual Display of Quantitative Information, 1983, ch. 5) on data-ink ratio; Few (Show Me the Numbers, 2004, ch. 1) on the analyst's obligation to interpret. Action: add a metric_grid rule that every grid needs a one-line "so what" caption, and QA FAILs a metric_grid with no lead.
8. **End on the ask, not the recap.** Anderson (TED Talks, 2016, ch. 13) and Duarte (Resonate, ch. 10) both close on a "new bliss," a vision of the after-state. The skill already mandates this. The gap is QA: it does not currently check for it. Action: add a QA FAIL for any final slide titled "Summary", "Recap", or "Conclusion".
9. **Visual variety is a memory law, not a design preference.** Medina (Brain Rules, 2008, Rule 10: Vision trumps all other senses) shows pictorial recall at 65% after 3 days vs. 10% for text. The skill already mandates visual variety. The gap is the rubric does not penalize 3+ consecutive bullets at the FAIL level. Action: upgrade the bullets-monotony check from WARN to FAIL when 4+ consecutive bullets-only slides appear.
10. **Title is the headline; bullets are the proof.** Mayer (Multimedia Learning, 2001) and McKinsey's "action title" pattern (Pyramid Principle in practice) say the slide title carries the takeaway as a full sentence ("Migration is 83% complete"), not a topic label ("Migration status"). Action: add an "action title" mode for exec audiences (`for cpo`, `for vp-eng`, `for svp-eng`, `for skip-level`) where the title is the takeaway sentence and bullets/cards prove it.
11. **Three is the magic number.** Gallo (Presentation Secrets of Steve Jobs, 2009, ch. 7) on Jobs' rule of three; Duarte on three-act structure; the cards-max-3 rule in exec_summary already encodes this. The gap is `three_card` allows 4 cards. Action: drop `three_card` cap from 4 to 3 to enforce the rule of three universally.
12. **The cover slide sets the contract for the next 20 minutes.** Chesky's Airbnb deck (2009, slide 1) and Jobs' "Today, Apple reinvents the phone" (Macworld 2007, opening 30 seconds, transcribed in Gallo ch. 1) both make a promise the deck must keep. Action: rewrite `cover.md` so the subtitle is a promise or tension, not a date stamp.

---

## Part 1: The five master frameworks

### A. Apple / Steve Jobs (via Carmine Gallo)

Source: Carmine Gallo, *The Presentation Secrets of Steve Jobs*, McGraw-Hill, 2009. Reverse-engineered from Macworld, WWDC, and special-event keynotes 1998 to 2010.

**The Jobs structure (Gallo, ch. 1 to 17):**

1. **Headline first** (ch. 4). Every announcement has a one-line headline that fits in a Twitter post. "Today, Apple reinvents the phone" (Macworld, Jan 9 2007, opening keynote). "1000 songs in your pocket" (iPod launch, Oct 23 2001).
2. **Rule of three** (ch. 7). Three products in the iPhone reveal ("a widescreen iPod, a phone, an internet communicator"). Three reasons to buy. Three features per release. Never two, never four. Three is the smallest pattern the brain perceives as a set (Gallo p. 80, citing cognitive psychology).
3. **An antagonist** (ch. 9). Every Jobs keynote has a villain: IBM (1984), Microsoft (Macworld 1997), Flash (2010), the BlackBerry keyboard (2007). The villain creates tension the product resolves.
4. **One core message per keynote** (ch. 5). The iPhone keynote is about reinventing the phone. The iPad keynote is about a third device between phone and laptop. Never two themes.
5. **Boom moments** (ch. 13). One "holy shit" moment per keynote: the original iPhone pinch-to-zoom demo (Macworld 2007), the MacBook Air sliding out of a manila envelope (Macworld 2008). The boom is rehearsed and choreographed; it is not improvised.
6. **Magic words** (ch. 14). Gallo's analysis of Jobs' word frequency: "incredible", "amazing", "boom", "gorgeous". Short, concrete, sensory. Not "innovative" or "industry-leading" or "robust".
7. **Visuals carry the message** (ch. 8). Average Jobs slide has 7 words. Many have zero words and one image. The slide never repeats what Jobs is saying; it shows what he is saying.

**When to use**: any deck where the goal is conviction, not information transfer. Product launches, recommendations, pitches.

**Example move for make-deck**: cover.md subtitle should be the headline (the one-line takeaway), not a date stamp. Today's cover.md shows "Q2 checkpoint for cpo, May 13 2026"; a Jobs cover would show "Migration is 83% done; the last 17% is the entire risk surface."

### B. Airbnb / Brian Chesky

Source: The original Airbnb pitch deck, 2008 to 2009, widely re-published (e.g., Sequoia archive; Reid Hoffman's *Masters of Scale* podcast, ep. "Brian Chesky", Oct 2017). Chesky's storyboarding method described in *The Airbnb Story* (Leigh Gallagher, 2017, ch. 4).

**The Airbnb 10-slide template (sequence as published, slide titles verbatim from the 2009 deck):**

1. Cover. "AirBed&Breakfast" + tagline "Book rooms with locals, rather than hotels."
2. **Problem**. Three pain points, bullets.
3. **Solution**. Three benefits, bullets.
4. **Market validation**. Couchsurfing.com 660,000 users, craigslist 17,000 listings (cite dates from 2009 deck).
5. **Market size**. Top-down TAM math, three numbers.
6. **Product**. Three screenshots of the funnel.
7. **Business model**. The unit economics, one line.
8. **Market adoption**. Go-to-market, three channels.
9. **Competition**. 2x2 matrix.
10. **Team / why us / ask**. Closing slide.

**Storyboarding from Disney (Chesky on Masters of Scale, Oct 2017):** Chesky and Joe Gebbia hired Pixar animator [teammate] in 2013 to storyboard the Airbnb host and guest experience as a frame-by-frame narrative. The output became "Snow White" (host story) and "Mickey Mouse" (guest story), the canonical artifacts used by Airbnb product and design teams. The principle: design the narrative arc of the user's experience before designing any feature.

**When to use**: any pitch or recommendation deck where the audience is being asked for a decision (investment, headcount, capacity).

**Example move for make-deck**: spine B (recommendation) should mirror the Airbnb sequence: problem, solution, validation, market, product, model, adoption, competition, team/ask. The skill's current spine B is closer but does not have an explicit validation or competition slot.

### C. Disney / Pixar storytelling

Source: Emma Coats, Pixar story artist, *22 Rules of Storytelling*, originally a Twitter thread May to June 2011, widely re-published. The "story spine" credited to Kenn Adams, *How to Improvise a Full-Length Play* (2007), adopted by Pixar.

**The story spine (Adams, 2007; Pixar Rule 4):**

> "Once upon a time there was ___. Every day, ___. One day ___. Because of that, ___. Because of that, ___. Until finally ___."

This six-beat structure is the underlying form of every Pixar feature (Toy Story, Up, Finding Nemo, Inside Out), confirmed by Coats and by Pixar's *The Art of Storytelling* internal training, public excerpts.

**Coats' 22 Rules, the load-bearing ones for decks:**

- Rule 2: "You gotta keep in mind what's interesting to you as an audience, not what's fun to do as a writer." Write for the reader, not for the author.
- Rule 4: the story spine (above).
- Rule 6: "What is your character good at, comfortable with? Throw the polar opposite at them. Challenge them. How do they deal?" Introduce a complication, do not just present a state.
- Rule 9: "When you're stuck, make a list of what WOULDN'T happen next. Lots of times the material to get you unstuck will show up." Useful for outline brainstorming, not for the deliverable itself.
- Rule 14: "Why must you tell THIS story? What's the belief burning within you that your story feeds off of? That's the heart of it." Every deck needs a stake, a reason the speaker is the right person to give it.

**The "What If" framework (Pixar)**: every story starts with a "what if" question. Toy Story: "What if toys had feelings?" Inside Out: "What if emotions had emotions?" For a PM deck: "What if the migration finishes on time but the last 17% breaks production?" The question sets up the tension.

**When to use**: every deck has a story spine even if the audience is internal. Skipping the spine is what makes a deck feel like a list of slides.

**Example move for make-deck**: the outline phase should produce a one-line story spine ("Once upon a time PHD lived in 17 places. Every day, queries took 5 seconds. One day, we started consolidating. Because of that, 83% are now in one place. Because of that, the last 17% are the only remaining risk. Until finally, MedMatch's visit-id rewrite ships in June.") before any slide is designed.

### D. Nancy Duarte (Resonate, Slide:ology)

Sources: Nancy Duarte, *Resonate*, Wiley, 2010; *Slide:ology*, O'Reilly, 2008; *DataStory*, Ideapress, 2019.

**The sparkline (Resonate, ch. 2, pp. 30 to 40):**

A presentation oscillates between "what is" (the current state) and "what could be" (the future state) at every section break. The full sparkline:

1. Beginning: establish "what is."
2. Middle: oscillate (every section is a new "what is to what could be" gap).
3. End: arrive at the "new bliss," the after-state the audience can choose.

Duarte analyzed Martin Luther King's *I Have a Dream* (Resonate, ch. 8) and Steve Jobs' iPhone keynote (ch. 9) against the sparkline. Both fit.

**STAR moments (Resonate, ch. 7, pp. 168 to 183):**

"Something They'll Always Remember." Five flavors:

1. **Memorable dramatization**. A physical demo (Jobs sliding the MacBook Air out of the envelope).
2. **Repeatable sound bites**. A phrase the audience repeats afterwards ("It just works").
3. **Evocative visuals**. One image that lodges (Al Gore's hockey-stick climate chart, *An Inconvenient Truth*).
4. **Emotive storytelling**. A personal anecdote that anchors the abstract.
5. **Shocking statistics**. One number that breaks the audience's mental model.

Duarte: every presentation should have exactly one STAR moment. Two competes; zero forgets.

**"What is" vs. "What could be" oscillation (Resonate, ch. 4):**

Each section of the deck oscillates between the gap and the resolution. The "gap" creates tension; the audience leans in to find out how it closes.

**Slide:ology principles (2008, ch. 1 to 3):**

- "Treat your audience as king" (ch. 1). Write for them, not for the speaker.
- Visual story over bullets (ch. 3). Bullets are for handouts, slides are for visual support.
- One message per slide (ch. 4).
- Six-by-six rule: max 6 bullets, max 6 words each. Better: fewer. (ch. 5)

**When to use**: any deck longer than 10 slides where the audience risks losing the spine.

**Example move for make-deck**: between every section transition, the `moving_blueprint` should carry a subtitle that names the gap ("Where we are: 83% done. Where we want to be: 100% by July 17."). The skill's current moving_blueprint.md allows a subtitle but does not require gap-framing.

### E. McKinsey / BCG / Bain (via Barbara Minto)

Sources: Barbara Minto, *The Minto Pyramid Principle*, Minto International, 1987 (rev. 2009); Gene Zelazny, *Say It with Charts*, McGraw-Hill, 1985 (rev. 2001); Ethan Rasiel, *The McKinsey Way*, McGraw-Hill, 1999.

**The Pyramid Principle (Minto, 1987, chs. 1 to 3):**

1. **Start with the answer.** Begin every doc, slide, paragraph with the conclusion. Justification follows.
2. **Group ideas into three levels.** Top: the answer. Middle: 2 to 4 supporting arguments. Bottom: data backing each argument.
3. **MECE the supporting arguments.** Mutually Exclusive, Collectively Exhaustive. No overlap, no gaps.
4. **Order arguments by importance or logic.** Strongest first when the audience is skeptical; chronological when the audience needs to follow a sequence.

**SCQA framework (Minto, 1987, ch. 4):** the introduction pattern:

- **Situation**: the stable backdrop the audience already accepts.
- **Complication**: the change or tension that forces a decision.
- **Question**: the implicit question raised by the complication.
- **Answer**: the recommendation that resolves the question.

SCQA is the structure of every McKinsey one-pager and the first slide of every McKinsey deck.

**Action titles (Zelazny, 1985; Rasiel, 1999):**

The slide title is the conclusion of the slide stated as a full sentence. Not "Migration progress" but "Migration is on track to finish July 17 but blocked on MedMatch." The body of the slide proves the title. A consultant reading only the titles of a deck should get the entire argument.

**Ghost decks (Rasiel, 1999, ch. 9):**

Build the entire deck as a sequence of slide titles BEFORE designing any slide content. If the titles tell the story end-to-end, the deck will work. If the titles don't, no amount of design rescues it. This is the consulting industry's equivalent of make-deck's outline-first phase.

**When to use**: every exec-facing deck. The skill's existing storytelling-principles.md already cites "answer-first" but does not yet enforce SCQA or action titles.

**Example move for make-deck**: when the modifier `for cpo`, `for vp-eng`, `for svp-eng`, or `for skip-level` is set, switch slide titles to action-title mode (full-sentence conclusions) and require the exec_summary lead to follow SCQA.

---

## Part 2: Cross-cutting principles where the masters agree

### Universal law 1: Lead with the answer

- **Source**: Minto, 1987, ch. 2; Gallo on Jobs, 2009, ch. 4 (headline first); Anderson, TED Talks, 2016, ch. 1 (the through-line); Duarte, Resonate, 2010, ch. 5 (clear premise).
- **Cognitive basis**: working memory limit, Miller, *The magical number seven, plus or minus two*, Psychological Review 63(2), 1956. Audiences can hold 4±1 chunks of information, per Cowan, *The magical number 4 in short-term memory*, Behavioral and Brain Sciences 24(1), 2001. If the conclusion arrives at slide 12 of 12, the audience has forgotten the setup.
- **Implication**: the conclusion lives at slide 2 (exec_summary), not the end.

### Universal law 2: One idea per slide

- **Source**: Reynolds, Presentation Zen, 2008, ch. 4 (signal-to-noise); Duarte, Slide:ology, 2008, ch. 4; Tufte, Beautiful Evidence, 2006, ch. 5; Jobs via Gallo, 2009, ch. 5 (one core message).
- **Cognitive basis**: Sweller, *Cognitive load theory*, Cognitive Science 12(2), 1988. Working memory cannot process two streams simultaneously; a slide with two ideas forces the audience to choose which to ignore.
- **Implication**: if the takeaway cannot be stated in 5 words, the slide is two slides.

### Universal law 3: Less is more (signal over noise)

- **Source**: Reynolds, Presentation Zen, 2008, ch. 3 (kanso, the Zen concept of simplicity); Tufte, Visual Display of Quantitative Information, 1983, ch. 4 (data-ink ratio); Kawasaki, "10/20/30 rule", blog, Dec 30 2005.
- **Cognitive basis**: Lavie, *Distracted and confused?*, Trends in Cognitive Sciences 9(2), 2005. Every irrelevant element on a slide competes for limited attention.
- **Implication**: cut every word, line, and pixel that does not advance the takeaway. The default move is delete, not add.

### Universal law 4: Story beats data

- **Source**: Duarte, Resonate, 2010, ch. 1 (the resonance of narrative); Coats, Pixar 22 Rules, Rule 2; Anderson, TED Talks, 2016, ch. 4 (the narrative arc); Heath & Heath, *Made to Stick*, Random House, 2007, ch. 5 (emotional > rational).
- **Cognitive basis**: Green & Brock, *The role of transportation in the persuasiveness of public narratives*, Journal of Personality and Social Psychology 79(5), 2000. Narrative transportation produces higher recall than fact lists (Stanford Graduate School of Business, Aaker, *Persuasion and the Role of Vivid Case Histories*, 2014 lecture, cited in *Telling Stories that Stick*).
- **Implication**: every deck has a protagonist (the patient, the provider, the operator), a complication (the gap), and a resolution (the recommendation). Without the spine, data alone does not persuade.

### Universal law 5: Pace with visual variety

- **Source**: Medina, *Brain Rules*, Pear Press, 2008, Rule 10 (vision trumps all other senses); Reynolds, Presentation Zen, 2008, ch. 5 (visual contrast); Duarte, Slide:ology, 2008, ch. 6 (visual hierarchy).
- **Cognitive basis**: Paivio, *Dual-coding theory*, Canadian Journal of Psychology 45(3), 1991. Visual + verbal encoding produces ~2x recall vs. verbal alone. Medina, 2008: pictorial recall at 65% after 3 days, text at 10%.
- **Implication**: a deck of uniform bullets slides has the recall profile of an unillustrated memo. Visual templates are not decoration; they are recall scaffolding.

### Universal law 6: Three is the rule

- **Source**: Gallo on Jobs, 2009, ch. 7; Atkinson, *Beyond Bullet Points*, Microsoft Press, 2007, ch. 3; Minto, 1987 (3-deep pyramid layering); Aristotle, *Rhetoric*, Book III, ca. 350 BCE (the three-part appeal: ethos, pathos, logos).
- **Cognitive basis**: three is the smallest set that establishes a pattern. Two is a pair; four is a list. Three feels complete without feeling exhaustive.
- **Implication**: three options, three reasons, three priorities, three sections of the agenda, three cards in the exec_summary.

### Universal law 7: End on forward motion

- **Source**: Anderson, TED Talks, 2016, ch. 13 (the close); Duarte, Resonate, 2010, ch. 10 (new bliss); Heath & Heath, Made to Stick, 2007, ch. 6 (call to action).
- **Cognitive basis**: peak-end rule, Kahneman, *Evaluation by moments*, Choices, Values, and Frames, 2000. The audience remembers the peak emotional moment and the ending. A flat recap as the close depresses the entire deck's recall.
- **Implication**: the last slide is a decision, an ask, or a forward-looking commitment, not a summary.

---

## Part 3: Where the masters disagree

The masters agree on the universal laws above. They diverge on questions of degree and audience. These tensions are productive: knowing when to lean each way is the skill the make-deck rubric should encode.

### Tension 1: Data density (Tufte/McKinsey vs. Reynolds/Jobs)

- **Tufte position**: maximize data-ink ratio. A single small-multiples chart can carry 200+ data points (Tufte, Visual Display, 1983, ch. 6). Information density is a virtue when the audience is analytical.
- **McKinsey position**: dense but structured. Action title + supporting data table + footnotes. The slide is also a leave-behind document, not just a screen.
- **Reynolds/Jobs position**: minimum data-ink. One number, one chart, one image per slide. The slide is a backdrop for the speaker, never a leave-behind.
- **When to lean Tufte/McKinsey**: technical audience, async or hybrid consumption, audience expects to study the deck after the meeting. Care eng leadership reading async.
- **When to lean Reynolds/Jobs**: live exec presentation, decision-forcing, time-constrained. the CPO, e-team, your VP Eng live.
- **Implication for make-deck**: the modifier `async` or `for eng` should bias toward denser metric_grid and two_column slides. Live exec mode should bias toward key_stat, big_idea, pull_quote.

### Tension 2: Emotion (Disney/Pixar) vs. rationality (Tufte/McKinsey)

- **Pixar position**: every story is fundamentally emotional. Without the gut, the head does not commit (Coats Rule 14: "what's the belief burning within you").
- **Tufte position**: emotional manipulation in data presentation is a form of chartjunk. The data is the argument; emotion adds noise (Tufte, Visual Display, 1983, ch. 5 on the duck and chartjunk).
- **When to lean Pixar**: pitches, vision documents, customer-impact framing. WL Membership business case to e-team.
- **When to lean Tufte**: performance reviews, dashboards, post-mortems. Migration tracker, OKR check-ins.
- **Implication for make-deck**: spine B (recommendation) and spine C (deep dive) should differ in emotional weight. Spine B should include one pull_quote or big_idea. Spine C should not have pull_quotes; it should have flow_steps and metric_grids.

### Tension 3: Number of slides (Kawasaki 10 vs. McKinsey 30+)

- **Kawasaki position**: 10/20/30 rule. 10 slides, 20 minutes, 30-point font minimum (Kawasaki blog, Dec 30 2005).
- **McKinsey position**: a board deck can be 40 slides because each slide is also a stand-alone analysis page.
- **When to lean Kawasaki**: live presentations to non-experts, pitch contexts, time-bounded meetings.
- **When to lean McKinsey**: written deliverables, study-and-decide audiences, formal business reviews.
- **Implication for make-deck**: the `short` modifier (≤8 slides) is the Kawasaki end; `long` (15+) is the McKinsey end. The skill should pick `short` by default for any exec-facing audience modifier and `long` for any internal-team or technical audience modifier.

### Tension 4: Bullets allowed or banned

- **Reynolds position**: bullets are a default that should be the exception. Presentation Zen, 2008, ch. 4: "If you have bullet points, you do not need slides; print them."
- **Atkinson position** (Beyond Bullet Points, 2007): replace bullets with the cinematic flow of one image + one sentence per slide.
- **McKinsey position**: bullets are fine if they are MECE and the title is an action title that interprets them.
- **Implication for make-deck**: bullets is correctly tagged as last-resort. The skill's design target of ≤2 bullets slides per deck is the right default. Action titles (Universal law 1 + McKinsey) salvage bullets slides that the outline could not visualize.

---

## Part 4: Specific moves to bake into make-deck

Each move below maps to a concrete file change. The skill already covers many of these; this section flags only the gaps.

### 4.1 Cover slide should set up a tension, not a topic

**File**: `references/templates/cover.md`

**Current state**: subtitle is "audience + date pattern" ("Q2 checkpoint for cpo, May 13 2026").

**Recommended change**: add a second valid subtitle pattern, "the headline as tension." Examples:

- "Migration is 83% done; the last 17% is the entire risk surface."
- "WL Membership launched in March. Now the retention question."
- "Peptides launch in 90 days. Five Rx. Three states. One open compliance question."

The skill should pick between "audience + date" (low-stakes status decks) and "headline as tension" (recommendation, pitch, decision-forcing decks) based on the spine selected during outline.

**Citation**: Jobs/Gallo ch. 4 (headline first); Duarte Resonate ch. 4 (what is vs. what could be).

### 4.2 Exec summary should map to SCQA

**File**: `references/templates/exec_summary.md`

**Current state**: lead (one sentence with the answer) + 3 cards (verb-led phrases).

**Recommended change**: the three cards should map to Situation, Complication, Resolution by default. Example:

- Lead: "PHD migration is 83% complete; remaining 17% is blocked on MedMatch."
- Card 1 (Situation): "83% migrated"
- Card 2 (Complication): "MedMatch unmigrated"
- Card 3 (Resolution): "June rewrite unblocks"

This is the existing schema, used differently. The change is the guidance in `exec_summary.md`, not the schema.

**Citation**: Minto, 1987, ch. 4 (SCQA).

### 4.3 Every section transition should re-state the gap

**File**: `references/templates/moving_blueprint.md`, `references/templates/section_divider.md`

**Current state**: subtitle is optional; usually a preview line.

**Recommended change**: make subtitle required for `moving_blueprint`, and the subtitle should name the gap addressed in the upcoming section. Examples:

- Section "Where we are" subtitle: "83% of records in one place. 17% still in legacy stores."
- Section "What's at risk" subtitle: "Three known blockers. Two we can fix this quarter. One escalates."

**Citation**: Duarte Resonate ch. 2 (sparkline oscillation).

### 4.4 Every deck has one STAR moment

**File**: new section in `references/storytelling-principles.md`; QA check in `references/qa-rubric.md`.

**Current state**: skill does not enforce a single anchor moment.

**Recommended change**: during outline phase, flag one slide as the STAR moment (must be `big_idea`, `key_stat`, or `pull_quote`). QA WARN if no STAR moment is flagged; QA WARN if two are flagged. This forces the presenter to pick the one thing the audience will always remember.

**Citation**: Duarte Resonate, 2010, ch. 7.

### 4.5 Action titles for exec audiences

**File**: `references/storytelling-principles.md` (new section); affects all content templates.

**Current state**: titles are topic labels ("Migration health", "Q2 delivery", "Next 30 days").

**Recommended change**: when audience modifier is `for cpo`, `for vp-eng`, `for svp-eng`, `for skip-level`, or `for cmo`, switch title style to action title (full-sentence conclusion). Examples:

- Topic: "Migration health" to Action: "Migration is on track; one blocker."
- Topic: "Q2 delivery" to Action: "We shipped 8 of 10 Q2 milestones."
- Topic: "Next 30 days" to Action: "We deliver MedMatch by June 14."

Storytelling-principles.md should add: "Default to topic titles for internal-team decks; switch to action titles for exec audiences."

**Citation**: Zelazny, 1985 (action titles); Rasiel, 1999, ch. 9 (ghost decks built from action titles); Atkinson, 2007 (Beyond Bullet Points: title is the headline).

### 4.6 Story spine in the outline phase

**File**: `SKILL.md` step 2 (Propose outline).

**Current state**: outline is a numbered list of slide types and titles.

**Recommended change**: before listing slides, output a one-line story spine using Adams/Pixar's six-beat structure: "Once upon a time ___. Every day ___. One day ___. Because of that ___. Because of that ___. Until finally ___."

If the spine doesn't write cleanly, the deck doesn't have a story and the outline shouldn't proceed. This is a cheap upstream check that catches confused decks.

**Citation**: Adams, 2007 (story spine); Coats, 2011 (Rule 4); Chesky on Masters of Scale, 2017 (storyboarding from Pixar).

### 4.7 Bullets cap of 4 (design), 6 (validator)

**File**: `references/storytelling-principles.md` and `references/templates/bullets.md`.

**Current state**: validator caps at 6; design target is 4 (already stated).

**Recommended change**: make the QA rubric WARN on 5 or 6 bullets, not just on 6. The design target should be enforced at QA time so that even technically-valid bullets slides get flagged for trimming.

**Citation**: Miller, 1956 (7±2); Cowan, 2001 (4±1); Duarte Slide:ology ch. 5 (six-by-six rule).

### 4.8 Metric grid requires "so what" caption

**File**: `references/templates/metric_grid.md`.

**Current state**: lead paragraph is optional.

**Recommended change**: make `lead` required for metric_grid. The lead carries the one-line interpretation ("we're behind on intake, ahead on activation"). Without it, the slide is naked data, and naked data does not persuade.

**Citation**: Few, *Show Me the Numbers*, Analytics Press, 2004, ch. 1; Tufte, Visual Display, 1983, ch. 5 (the analyst's obligation to interpret).

### 4.9 Three-card cap, not four

**File**: `references/templates/three_card.md` (per catalog allows 4); `scripts/build_deck.py` validator.

**Current state**: three_card validator caps at 4 cards.

**Recommended change**: drop the cap from 4 to 3. The rule of three is universal across Jobs, Minto, Duarte. The exception (4 cards) creates a slide that the audience cannot pattern-match. If 4 items are genuinely necessary, use `comparison_2x2` (which is also four, but with axes that create meaning).

**Citation**: Gallo, 2009, ch. 7; Minto, 1987, ch. 3 (pyramid layering).

### 4.10 Cover slide carries a promise

**File**: `references/templates/cover.md`.

**Current state**: subtitle is "audience + date pattern."

**Recommended change**: the cover subtitle should be either (a) a promise about what the audience will get from this deck or (b) the headline tension. Today's pattern ("Q2 checkpoint for cpo, May 13 2026") is neither. Examples of promises:

- "What we'll cover: status, risk, the ask."
- "20 minutes, three decisions."
- "Where the migration stands and what we need."

**Citation**: Jobs at Macworld 2007, opening 30 seconds (transcript in Gallo, 2009, ch. 1: "Today we're introducing three revolutionary products"); Chesky's Airbnb deck slide 1 (2009): "Book rooms with locals, rather than hotels." Both make a promise the deck delivers on.

---

## Part 5: Anti-patterns to add to the QA rubric

Each anti-pattern below maps to a check in `references/qa-rubric.md`. These are failure modes the masters explicitly name.

### 5.1 Chartjunk (FAIL when severe, WARN otherwise)

- **Definition**: visual decoration that does not encode data (Tufte, Visual Display, 1983, ch. 5). 3D effects, gradient fills, drop shadows on chart bars, excessive gridlines.
- **Check**: metric_grid slide with decorative graphics that do not carry data.
- **Map to rubric**: add to WARN list, "decorative chart elements not encoding data."

### 5.2 Throat-clearing opener (FAIL)

- **Definition**: opening slide content that introduces the speaker, the agenda, the methodology, before the audience knows what they're being told (Anderson, TED Talks, 2016, ch. 3 on the through-line).
- **Check**: cover slide subtitle containing phrases like "Overview of...", "Introduction to...", "We will cover...".
- **Map to rubric**: add to FAIL list (matches your CLAUDE.md (or your operator profile) "No throat-clearing" hard rule).

### 5.3 Conclusion slide that recaps (FAIL)

- **Definition**: final slide titled "Summary", "Recap", "Conclusion", "Wrap-up", or any close that re-states what was already said (Duarte Resonate ch. 10; Anderson TED Talks ch. 13).
- **Check**: last slide before deck close, title contains recap-language.
- **Map to rubric**: add to FAIL list. The exec_summary at slide 2 IS the summary; a closing recap wastes the peak-end attention moment (Kahneman, 2000, peak-end rule).

### 5.4 Naked numbers (WARN; FAIL if claim is consequential)

- **Definition**: numbers without unit, source, or date (your CLAUDE.md (or your operator profile) hard rule).
- **Check**: any metric_grid or key_stat slide where the lead or caption does not anchor the source and date.
- **Map to rubric**: already partially in QA rubric WARN list. Upgrade to FAIL when the number drives a decision (recommendation deck, board deck).

### 5.5 Three-or-more consecutive bullets slides (FAIL)

- **Definition**: visual monotony that erases the recall benefit of visual variety (Medina, 2008, Rule 10; Reynolds, 2008, ch. 5).
- **Check**: scan slide sequence for 3+ consecutive `bullets` template slides.
- **Map to rubric**: currently a WARN; upgrade to FAIL at 4+ consecutive. Three is borderline; four is a structural problem.

### 5.6 Slide with two ideas (WARN)

- **Definition**: a slide where the takeaway cannot be stated in 5 words (Duarte Slide:ology ch. 4; Reynolds ch. 4).
- **Check**: hard to automate, but proxy: bullets slide with bullets covering more than one topic; two_column with mismatched left/right framing; three_card where one card is at a different level of abstraction.
- **Map to rubric**: add to WARN list as "slide carries 2+ ideas; consider splitting."

### 5.7 No STAR moment in the deck (WARN)

- **Definition**: no `big_idea`, `key_stat`, or `pull_quote` slide flagged as the anchor (Duarte Resonate ch. 7).
- **Check**: count of `big_idea` + `key_stat` + `pull_quote` slides. Zero in a deck >8 slides is a WARN.
- **Map to rubric**: add to WARN list.

### 5.8 Two STAR moments competing (WARN)

- **Definition**: more than one anchor slide, which dilutes recall (Duarte Resonate ch. 7).
- **Check**: 2+ `big_idea` slides in a deck <15 slides; 2+ consecutive STAR templates (big_idea then key_stat then pull_quote in a row).
- **Map to rubric**: add to WARN list.

### 5.9 Topic title instead of action title for exec audiences (WARN)

- **Definition**: when the audience modifier is exec-facing, slide titles should be conclusions, not labels (Zelazny, 1985; Rasiel, 1999).
- **Check**: outline carries an audience modifier of `for cpo`/`for vp-eng`/`for svp-eng`/`for skip-level`/`for cmo`, and content slide titles are noun phrases instead of full sentences.
- **Map to rubric**: add to WARN list, "exec audience modifier set; consider action titles."

### 5.10 Cover slide is a topic, not a promise or tension (WARN)

- **Definition**: cover subtitle that is purely informational (date stamp, project name) without a promise of what the audience will get or the tension the deck addresses.
- **Check**: cover slide subtitle pattern. If only "<audience>, <date>", and the deck is recommendation/pitch spine (B), flag.
- **Map to rubric**: add to WARN list, "cover sets up topic, not tension."

---

## Part 6: Citation index

All sources cited above, organized by master.

### Apple / Jobs / Gallo

- Gallo, Carmine. *The Presentation Secrets of Steve Jobs: How to Be Insanely Great in Front of Any Audience*. McGraw-Hill, 2009. Chapters 1, 4, 5, 7, 8, 9, 13, 14.
- Jobs, Steve. Macworld Keynote, January 9, 2007 (iPhone introduction). Transcript widely re-published; key segments quoted in Gallo, 2009, ch. 1.
- Kawasaki, Guy. "The 10/20/30 Rule of PowerPoint." Guy Kawasaki blog, December 30, 2005. URL: guykawasaki.com/the_102030_rule.

### Airbnb / Chesky

- The original Airbnb pitch deck, "AirBed&Breakfast", 2009. Widely re-published; canonical scan in Reid Hoffman's Sequoia archive and via Pitch Deck Examples (pitchdeckexamples.com).
- Hoffman, Reid. "Brian Chesky: Handcrafted." *Masters of Scale* podcast, episode 1, October 11, 2017.
- Gallagher, Leigh. *The Airbnb Story: How Three Ordinary Guys Disrupted an Industry, Made Billions, and Created Plenty of Controversy*. Houghton Mifflin Harcourt, 2017. Chapter 4 on storyboarding.

### Disney / Pixar

- Coats, Emma. "22 Rules of Storytelling." Originally Twitter, May to June 2011, @lawnrocket. Re-published Pixar Touch blog, June 2011; archived widely.
- Adams, Kenn. *How to Improvise a Full-Length Play: The Art of Spontaneous Theater*. Allworth Press, 2007. Source of the story spine framework.
- Internal Pixar storytelling training, *The Art of Storytelling*, public excerpts via Khan Academy "Pixar in a Box" series.

### Nancy Duarte

- Duarte, Nancy. *Resonate: Present Visual Stories that Transform Audiences*. Wiley, 2010. Chapters 1, 2, 4, 5, 7, 8, 9, 10. Sparkline pp. 30 to 40; STAR moments pp. 168 to 183.
- Duarte, Nancy. *Slide:ology: The Art and Science of Creating Great Presentations*. O'Reilly, 2008. Chapters 1, 3, 4, 5, 6.
- Duarte, Nancy. *DataStory: Explain Data and Inspire Action Through Story*. Ideapress Publishing, 2019.

### Garr Reynolds

- Reynolds, Garr. *Presentation Zen: Simple Ideas on Presentation Design and Delivery*. New Riders, 2008 (2nd ed. 2011). Chapters 3 (kanso/simplicity), 4 (signal-to-noise), 5 (visual contrast).

### Edward Tufte

- Tufte, Edward. *The Visual Display of Quantitative Information*. Graphics Press, 1983 (2nd ed. 2001). Chapters 4 (data-ink ratio), 5 (chartjunk), 6 (small multiples).
- Tufte, Edward. *Beautiful Evidence*. Graphics Press, 2006. Chapter 5 on the relationship of evidence to argument.
- Few, Stephen. *Show Me the Numbers: Designing Tables and Graphs to Enlighten*. Analytics Press, 2004 (2nd ed. 2012). Chapter 1 on the analyst's obligation.

### McKinsey / BCG / Bain

- Minto, Barbara. *The Minto Pyramid Principle: Logic in Writing, Thinking, and Problem Solving*. Minto International, 1987 (revised editions through 2009). Chapters 1, 2, 3, 4.
- Zelazny, Gene. *Say It with Charts: The Executive's Guide to Visual Communication*. McGraw-Hill, 1985 (4th ed. 2001).
- Rasiel, Ethan. *The McKinsey Way: Using the Techniques of the World's Top Strategic Consultants to Help You and Your Business*. McGraw-Hill, 1999. Chapter 9 on ghost decks.

### TED / Anderson

- Anderson, Chris. *TED Talks: The Official TED Guide to Public Speaking*. Houghton Mifflin Harcourt, 2016. Chapters 1 (the through-line), 3 (openers), 4 (narrative arc), 13 (closing).

### Beyond Bullet Points / Mayer

- Atkinson, Cliff. *Beyond Bullet Points: Using Microsoft PowerPoint to Create Presentations that Inform, Motivate, and Inspire*. Microsoft Press, 2007 (4th ed. 2018). Chapter 3 on the headline/title-as-conclusion pattern.
- Mayer, Richard E. *Multimedia Learning*. Cambridge University Press, 2001. Chapter on the multimedia principle and split-attention effect (basis for one-idea-per-slide).

### Cognitive science basis

- Miller, George A. "The Magical Number Seven, Plus or Minus Two: Some Limits on Our Capacity for Processing Information." *Psychological Review* 63(2), 1956, pp. 81 to 97.
- Cowan, Nelson. "The Magical Number 4 in Short-Term Memory: A Reconsideration of Mental Storage Capacity." *Behavioral and Brain Sciences* 24(1), 2001, pp. 87 to 114.
- Sweller, John. "Cognitive Load During Problem Solving: Effects on Learning." *Cognitive Science* 12(2), 1988, pp. 257 to 285.
- Paivio, Allan. "Dual Coding Theory: Retrospect and Current Status." *Canadian Journal of Psychology* 45(3), 1991, pp. 255 to 287.
- Kahneman, Daniel, and Amos Tversky (eds.). *Choices, Values, and Frames*. Cambridge University Press, 2000. Chapter on peak-end rule.
- Green, Melanie C., and Timothy C. Brock. "The Role of Transportation in the Persuasiveness of Public Narratives." *Journal of Personality and Social Psychology* 79(5), 2000, pp. 701 to 721.
- Lavie, Nilli. "Distracted and Confused?: Selective Attention under Load." *Trends in Cognitive Sciences* 9(2), 2005, pp. 75 to 82.
- Medina, John. *Brain Rules: 12 Principles for Surviving and Thriving at Work, Home, and School*. Pear Press, 2008. Rule 10 (vision trumps all other senses).
- Heath, Chip, and Dan Heath. *Made to Stick: Why Some Ideas Survive and Others Die*. Random House, 2007. Chapters 5 (emotional), 6 (story).
- Aaker, Jennifer. "Persuasion and the Role of Vivid Case Histories." Stanford Graduate School of Business, recorded lecture, 2014. Source of the "stories are more memorable than facts" claim, often re-cited.

### Other

- Aristotle. *Rhetoric*. Book III, ca. 350 BCE. The three-part appeal (ethos, pathos, logos), origin of the rule of three.
