# AI Product Sense: Question Bank

> **Source:** [AI Product Sense: Your Complete Guide](ai-product-sense-complete-guide.md), Aakash Gupta and Miqdad Jaffer, *Product Growth* (Oct 16, 2025), plus the eight diagram images saved in this folder. Care/Galen notes draw on the Quality of Care charter and metric priority in `AGENTS.md`, and on the [EMR Team Primer](../../../Project-Galen/Galen-Primer-Danny-Start-Here.md) ([Director of Product], Aug 2026).
> **Created:** Nov 2, 2026

Use this file when scoping a new AI product. Work top to bottom, or jump to the framework that matches the decision in front of you.

**Legend**

- Unmarked questions come from the article or its diagrams, either stated or directly implied.
- `[+]` marks a follow-up question that goes past the article's text.
- **Care/Galen** notes flag where a framework bites hardest for clinical AI. They are prompts to answer, not findings.

**Concepts with one home.** These concepts recur across frameworks. Their questions live in one place, and other sections link back.

- Quality Envelope: [Principle 1](#principle-1-probabilistic-fit-not-feature-fit)
- Context Ledger: [Principle 4](#principle-4-context-is-capital)
- Spark, Shape and Seal: [Principle 5](#principle-5-the-latency-envelope)
- SUQS metrics: [Principle 10](#principle-10-the-suqs-metric-set)

**Source notes**

- The article calls the cascade "five-stage" but lists six stages. This bank uses all six.
- The article uses the "Human-in-the-Loop Ladder" name for two different lists: Principle 6's four rungs and Pattern 3's 4 M's. The system design diagram puts both under its own Pattern 4.
- Principle 1 puts the "delight zone" at P95. Ritual 3 calls P80 the delight level. This bank follows Principle 1.
- The GTM diagram's fourth moat type appears here as "Compounding data." The label was renamed to stay inside the workspace plain-word list.

## Contents

1. [Foundations](#1-foundations)
2. [The AI Product Sense lifecycle](#2-the-ai-product-sense-lifecycle)
3. [REALM: the five lenses and 10 principles](#3-realm-the-five-lenses-and-10-principles)
4. [SPLIT feedback loop](#4-split-feedback-loop)
5. [System design](#5-system-design)
6. [Go-to-market](#6-go-to-market)
7. [Rituals, reframed for a specific product](#7-rituals-reframed-for-a-specific-product)

---

## 1. Foundations

### Product sense: Sid Arora's flow

- What is the overall goal, and have we written it down before discussing solutions?
- Did we work through user discovery, problem discovery and solution discovery in order, or did we start from a solution?
- Are we prioritizing the users, problems and solutions with the highest impact on the overall goal?
- How will we measure success and collect feedback once it ships?

The AI version of this flow has its own section: [the AI Product Sense lifecycle](#2-the-ai-product-sense-lifecycle).

### Product sense levers: Shreyas Doshi

The article and its diagram name these levers and sub-levers but pose no questions about them. Every question here is an extension.

#### Motivation theory

- [+] What motivates the user to do this job today?
- [+] Where is the friction, and does the AI remove it or add new friction (review, correction, waiting)?
- [+] What does satisfaction look like at the end of the task?
- [+] What nudge gets the user to try the AI path the first time?

#### Cognitive empathy

- [+] Metacognition: Which of our own beliefs about the user or the model are untested?
- [+] Intellectual flexibility: What evidence would change our mind about the chosen solution?
- [+] Simulation: Have we walked through the task as the user, start to finish, including a bad output?
- [+] Which user interviews have we run, and what did users say about trust?

#### Creativity: strategic thinking

- [+] Positioning: How is this positioned against the way the user does the job today?
- [+] Segmentation: Which segment benefits first, and which segment is hurt most by errors?
- [+] Differentiation: What sets this apart beyond the model, which competitors can also buy?
- [+] Core of product strategy: How does this tie to the core product strategy?

#### Creativity: creative execution

- [+] Creative mindset: Did we generate more than one solution shape (assistant, draft, automation, no AI) before picking?
- [+] Team rituals: Which rituals keep idea generation going after launch, such as demos and failure reviews?
- [+] Product creativity techniques: Which technique did we use to widen the option set, and who joined?

#### Domain expertise

- [+] Who on the team has deep domain expertise, and do they review outputs?
- [+] Which domain rules must the model never break? (Feeds [Tolerance of Wrongness](#principle-1-probabilistic-fit-not-feature-fit).)

#### Communication

- [+] Product taste: Would we be proud to show a typical output, not only the best one?
- [+] Product artifacts: Do the vision, strategy and proposal docs state the Quality Envelope and the economics?
- [+] Influence: Who must agree before this ships, and what evidence do they need?
- [+] Interviewing and getting interviewed: Can we explain this product's AI tradeoffs clearly from either side of an interview table?

### Product sense, formally defined

- Do we know what to build, for whom, and why?
- Which patterns from past launches apply here, across user needs, market dynamics and execution tradeoffs?

### AI Product Sense: the fit test

The article defines AI Product Sense as "the fit between need, model behavior, and the economic envelope that lets that behavior repeatedly deliver value under uncertainty."

- Need: Is the user need real, and does it matter enough to solve?
- Model behavior: Does the model's behavior across real inputs meet that need, not only in a demo?
- Economic envelope: Can we afford that behavior at real volume?
- Repeatability: Does it deliver value every time, under uncertainty, or only on good days?
- [+] Which part of the fit is weakest today, and what would it take to fix it?
- [+] Does this problem need AI at all, or would a deterministic rule do the job?

> **Care/Galen:** Does the need rank on quality of care first, then patient experience, then cost, per the charter's metric order?

### The Apollo lessons

- Have we planned for outputs that differ every time, not only for the demo path?
- Have we modeled costs as variable, growing with usage?
- Could the feature hurt users outside our product, the way Apollo's email writer hurt spam ratings and inbox health?
- Context engineering: Is the model getting the right context for the task?
- Model economics: Are we using the right model for what the outcome is worth?
- Feedback loop: How does user feedback reach the team and change the product?
- [+] A demanding executive loving the demo proved nothing at Apollo. What evidence beyond the demo do we have?

### The checkbox trap

- Are we judging the feature with checkbox questions ("Does it generate text?") or by how it behaves across real inputs?
- How do we shape the experience around unpredictability so users feel it as stable and trustworthy?

### Signs that product sense is strong

- Will users forgive occasional imperfections because the experience still feels coherent?
- Do costs stay under control as usage grows?
- Has the product earned the right to scale?
- Is trust compounding over time?
- [+] Which metric would show trust compounding, and what is its baseline?

---

## 2. The AI Product Sense lifecycle

The adapted Sid diagram runs from "a vague and ambiguous AI opportunity" to "onto the next thing." Its side note says to prioritize the options with the greatest impact on product success. Learn and Iterate loops back to AI Validation. Questions here check that each stage is done; deeper questions live in the linked sections.

### User discovery

- What is the user job to be done?
- Who are all the users in the workflow, including people who review, approve or receive the output?
- Which one or two users are we prioritizing, and why them?
- [+] Who is affected by the output but never touches the product?

> **Care/Galen:** Does the user map include providers, the patients who receive the output, and the Care Ops reviewers, and which one or two come first?

### Problem discovery

- What are the major problems of the priority users?
- Which problems are we solving, and which are we deliberately leaving alone?
- [+] Is the problem frequent and painful enough to justify outputs that vary?

### Solution discovery

- Which solutions did we brainstorm?
- Which solution has the highest ROI?
- [+] Did the brainstorm include a non-AI option? See [the fit test](#ai-product-sense-the-fit-test).
- [+] Does the ROI estimate include serving cost and the cost of errors?

### AI validation

- Have we defined the Quality Envelope, with P50, P80 and P95 targets plus Tolerance of Wrongness? See [Principle 1](#principle-1-probabilistic-fit-not-feature-fit).
- Have we validated economics as cost per successful outcome at scale? See [Principle 7](#principle-7-economics-before-elegance).
- [+] Which validation result would make us stop?

### Build and deploy

- Have we designed the system architecture as a cascade (Detect, Retrieve, Draft, Verify)? See [Pattern 1](#pattern-1-cascades-and-caches-not-monoliths).
- Have we built and deployed the solution?
- [+] What gate sits between the first build and a broad deploy?

### Learn and iterate

- Is the SPLIT loop running every week? See [SPLIT](#4-split-feedback-loop).
- Are we measuring SUQS? See [Principle 10](#principle-10-the-suqs-metric-set).
- When learning changes the Quality Envelope, do we loop back to AI validation?
- [+] Which signal tells us to move onto the next thing instead of investing further?

---

## 3. REALM: the five lenses and 10 principles

The article says a product built without one of these lenses "is blind." Each lens opens with its guiding questions from the article text and from the REALM diagram.

### Reality of the user

**Guiding questions**

- Are we building for the world as it actually is, or as we wish it to be?
- What is the actual job the user is trying to get done?
- What are the user's goals, constraints, emotions and expectations?
- What is the user's behavior telling us, as opposed to what we think they want?
- Which of our assumptions about user needs or model behavior have we not tested?

#### Principle 1: Probabilistic Fit, Not Feature Fit

This is the home of the Quality Envelope.

- How does the product behave across a distribution of real inputs, not one or two demos?
- Can the experience absorb the variance without breaking trust?

**Quality Envelope**

- P50: What experience should half of users consistently get?
- P80: What noticeably strong experience should most users feel when the system works well?
- P95: What rare, remarkable output would make people tell a friend?
- [+] Which input set do we use to measure each percentile?
- [+] Who signs off on the envelope?

**Tolerance of Wrongness**

- Which errors can the product survive?
- Which errors can it absolutely not survive?
- [+] Is the list of unacceptable errors written down and testable?
- [+] How often does each unacceptable error occur today?

**UX as the shock absorber**

- How do we design the experience so misses don't feel like betrayals?
- Where should we surface confidence levels?
- Which quick correction flows exist?
- Which fallback modes exist?

> **Care/Galen:** Which clinical errors sit outside tolerance (wrong dose, missed drug interaction, wrong patient), and has clinical leadership signed that list?

#### Principle 2: Design for Variance

- Are we designing around variance on purpose, or hoping it goes away?
- Where can variance become a feature instead of a bug?
- [+] Where must variance be suppressed entirely?

**Preview-Then-Prove**

- Where can we show a fast preview, then verify key claims in the background before the user commits?
- [+] What happens if background verification fails after the user has seen the preview?

**Confidence-Forward**

- Does the confidence signal change the user's decision? If not, why show it?
- [+] Is the confidence signal calibrated, so that "80% confident" is right about 80% of the time?

**Correct-Without-Penalty**

- Can the user refine, fix or tighten an output in one click, without redoing everything?
- [+] Do corrections feed evals and context? See [SPLIT Sense](#sense-observe-reality-not-assumptions).

**Recover-With-Humility**

- When the model fails, does the product say so plainly?
- Which graceful fallback do we offer?
- Does any part of the product project fake certainty?

#### Principle 3: The Data Nutrition Label

- Where did this information come from?
- How current is it?
- What does the system know it doesn't know?
- Is uncertainty legible without technical detail?
- Can users see the boundaries of what the product can do?
- [+] Where does the label live in the UI, and is it visible at the moment of decision?

> **Care/Galen:** Can a provider tell AI-captured data from clinician-entered data at a glance, at the moment of the treatment decision?

### Elasticity of the model

**Guiding questions**

- How does the product behave when conditions stretch, scale or shift?
- How does the model behave when we stretch it?
- What are its failure signatures?
- How much variance can it handle before it collapses?
- Do we know what happens at the edges of its competence?
- Which edge cases and unexpected inputs have we tested, and which have we only imagined?

#### Principle 4: Context Is Capital

This is the home of the Context Ledger.

- Are we managing context like a budget?

**Context Ledger: assets**

- Which context makes the model smarter for this task: user profile, task-specific examples, structured data, domain constraints, retrieved docs or active session state?
- What do the user's intent, history, environment and previous actions add?

**Context Ledger: debits**

- What does each piece of context cost in tokens and serialization time?
- What is each piece's staleness risk?
- What privacy risk and legal exposure does each piece carry?

**Context Ledger: profit**

- How much does each piece reduce variance, measured as fewer errors or corrections?
- [+] Have we measured profit by removing one piece at a time and comparing results?

**Minimal Golden Context**

- What is the smallest set of context that reliably moves the needle for this task?
- What are we including only because we can?

**Adaptive Context Accrual**

- When does the user's task or the model's confidence call for more context?
- [+] What triggers the extra retrieval, and what does it add to latency?

**Context Freshness SLAs**

- How often must each piece of context be updated, re-validated or thrown away?
- Where would stale context be worse than no context?
- [+] Who owns each SLA, and what alert fires when one is missed?

> **Care/Galen:** Which chart data goes stale fastest (medications, vitals, labs), and which freshness rule applies before a recommendation uses it?

#### Principle 5: The Latency Envelope

This is the home of Spark, Shape and Seal.

- How does latency feel for this task, given user expectations, task urgency and interaction design?
- [+] Is this a task where users accept a wait (creative ideation) or expect an instant response (a web form)?

**Spark (0.3–0.7s, per the article)**

- What is the first signal that the system is alive and making progress?
- Is that signal meaningful: an outline, a header, a partial preview or a skeleton with hints?

**Shape (1–2.5s, per the article)**

- What first useful structure can the user react to, edit or steer?

**Seal (7s or less, per the article)**

- When does the final output, or a clear path to a completed action, land?
- Are confidence, verification and actionability all in place at Seal?
- [+] What happens when Seal runs past 7 seconds?
- [+] Do we measure Spark, Shape and Seal at P50 and P95, not only as averages?

#### Principle 6: Agent Choreography, Not Agent Hype

- [+] Does this need an agent at all, or would one well-scoped model call do?

**Task, Edge and Guard**

- Task: What are the atomic steps, and can each be executed and evaluated cleanly?
- Edge: Where does action become risky, such as sending email, deleting data or making payments?
- Guard: Which policy, check or human approval is required to cross each edge?
- [+] Which edges are irreversible?

**Human-in-the-loop ladder**

- Suggest: Can the agent propose a sequence with reasons?
- Simulate: Can it run in a sandbox and show diffs?
- Supervise: Can it act with micro-approvals?
- Safeguarded Autonomy: Can it act within strict guardrails and escalate outside them?
- Which rung are we on today, and what evidence earns the next rung?
- [+] What evidence would move us back down a rung?

The [4 M's](#the-4-ms-the-user-side-ladder) are a second ladder covering how users shape the system.

> **Care/Galen:** If providers make every treatment decision and the CDS only recommends, which rung fits each action, and which actions should never climb past Supervise?

### Affordability envelope

**Guiding questions**

- Can the economics of the product support the value it delivers?
- How much does one successful outcome cost in latency, tokens, infrastructure and human supervision?
- Can our economics support the volume we dream of?
- What does one action cost in the demo versus at real production traffic?

#### Principle 7: Economics Before Elegance

**Cost structure**

- What does it cost to acquire context?
- What does it cost to generate outputs?
- What does it cost to verify accuracy?
- What is the error tax when things go wrong?
- The article's test: a $47 cost per user action against $12 revenue per user is a science project, not a product. What are our two numbers?

**Cost disciplines**

- Cost per outcome: Are we tracking cost per outcome, not cost per call?
- Cost escape valves: Where can the system degrade to a cheaper approach without destroying the experience?
- Economic ceiling: What is the most we can spend per user action and keep healthy unit economics?
- Did we set the economic ceiling before building, as a design constraint from day one?
- Value velocity: How quickly do users reach an outcome they'd pay for, relative to what we spend?
- [+] Who owns the cost model, and how often is it refreshed with real usage?
- [+] For internal tools with no revenue per user, what goes on the value side (time saved, quality gained)?

> **Care/Galen:** Does the economic ceiling hold without trading away quality of care or patient experience, which the charter ranks above cost?

### Liability and trust

**Guiding questions**

- What happens when things go wrong, and how do we protect trust?
- What is the cost of getting it wrong?
- Which invisible trust thresholds must the product earn before users let it act for them?
- Where are the edges that require guardrails?
- [+] If trust breaks, what is the recovery plan?

#### Principle 8: Evals as a Product

- Are evals a living system, or a one-time QA checklist?
- Who checks the evals every week, and do they ask "How is it failing?"
- Does quality hold at real serving costs, not only in an expensive test setup?
- Are the errors acceptable or catastrophic? We measure wrongness, not accuracy.
- How will we catch drift and quiet degradation from one month to the next?
- [+] Does the golden dataset cover the tails of the distribution, not only the happy path?
- [+] Which failure modes block a release?
- [+] Who owns the eval rubric?

> **Care/Galen:** Taking the article's triage example (a spelling error is survivable, a misclassified severity is not), does our rubric score clinical correctness and webside manner together, and does each catastrophic error block release?

#### Principle 9: The UMD Contract (User–Model–Data)

- User: Which intent, goals, context and approval power does the user hold?
- Model: Which reasoning limits, confidence signals and refusal behaviors does the model state?
- Data: Which structure, provenance and freshness does the data provide?
- Is the contract written down and explicit?
- When something goes wrong, can users tell which actor failed, or will they blame the wrong one?
- [+] Where does the UI show who contributed what: user input, model output or data source?

> **Care/Galen:** When a recommendation is wrong because the chart was wrong, will the provider blame the model, the data or themselves?

### Market motion

**Guiding questions**

- Why can't someone copy this in three months?
- How does our AI advantage translate into something that compounds?
- Does it give us distribution advantages, data moats or workflow lock-in, or is it just a clever feature?
- Which moment in the user's workflow do we own? See [Strategic Moats](#gtm-concept-5-strategic-moats).

#### Principle 10: The SUQS Metric Set

This is the home of SUQS.

- Are we relying on shallow metrics like clicks or NPS instead of SUQS?

**Speed**

- What is Time to First Value (Spark)?
- What is Time to Seal?

**Usefulness**

- What is the edit distance between the output and what the user keeps?
- What is the replay rate?
- What is the task completion velocity?

**Quality**

- What is the acceptance rate?
- What is the verified success rate?

**Safety**

- What is the intervention rate?
- How many risk breaches did we prevent?

**Compounding**

- Does better Speed lead users to try more tasks?
- Does better Quality earn the user's trust on harder problems?
- Does each Safety win build permission for more autonomy?
- [+] Which SUQS metric is primary for this product, and which serve as guardrails?
- [+] Which baseline do we have for each metric before launch?

> **Care/Galen:** How does SUQS map to the Clinical Quality Score guardrail, and does the metric hierarchy keep quality of care first?

---

## 4. SPLIT feedback loop

SPLIT stands for Sense, Probe, Learn, Integrate and Track. The article frames it as a weekly rhythm.

### Why the loop exists: four drift sources

- Model drift: How will we notice the model changing?
- User behavior: How will we notice users changing as they learn what the system can and can't do?
- Cost structure: How will we notice costs shifting as we optimize?
- Trust dynamics: How will we notice trust evolving with usage?

### Sense: observe reality, not assumptions

- Who watches real user sessions each week?
- Do we capture structured corrections?
- Do we log model uncertainty?
- Do we record SUQS metrics? See [Principle 10](#principle-10-the-suqs-metric-set).
- Is the review focused on failures?

> **Care/Galen:** Can the Care Ops QA labeling program, with its structured conversation reviews and defect tracking, serve as the Sense step for Galen?

### Probe: run micro-experiments

- Which specific hypothesis are we testing this week?
- Which one precise lever are we pulling?
- How do we isolate cause and effect?
- Are we staying surgical, or shipping 10 features at once?

### Learn: codify findings

- Did we document the experiment?
- Which metrics moved?
- How do the results map to the Quality Envelope? See [Principle 1](#principle-1-probabilistic-fit-not-feature-fit).
- Can someone else repeat the experiment?
- Where does the institutional knowledge live?

### Integrate: bake learning into the product

- What moves to production?
- Which defaults change?
- Which guardrails change?
- Which context ledgers change? See [Principle 4](#principle-4-context-is-capital).
- What failed, and did we kill it fast?

### Track: measure the compound effect

- Are SUQS metrics reviewed every week?
- What is the cost per successful outcome this week?
- How has the error distribution shifted?
- How has the latency profile changed?
- What do trust engagement signals show?
- [+] Who owns the weekly SPLIT review, and where are results published?

### Anti-patterns

#### The Wizard Trap

- Is the demo handcrafted for the happy path?
- Have we sensed and tracked the tail ends of the distribution?

#### Feature Fog

- Are we layering knobs and toggles on top of variance instead of reducing the variance?
- Are we handing users the burden of managing model behavior we should have absorbed?

#### Data Drizzle

- When outputs degrade, is our first move to dump more context into the prompt?
- Did we check the [Context Ledger](#principle-4-context-is-capital) before adding context?

#### Latency Debt

- How have Spark, Shape and Seal moved since launch? See [Principle 5](#principle-5-the-latency-envelope).
- Which added verification or retrieval steps slowed the experience, and were they worth it?
- [+] Do we have a latency budget that every new step must fit inside?

---

## 5. System design

The article's claim is that in AI "the system IS the product." Architecture choices show up directly in user experience.

### Pattern 1: Cascades and Caches, Not Monoliths

- Does every request go straight to the biggest, most expensive model? If so, why?
- Is every interaction one shot, with one prompt trying to do everything?
- Does the cascade give us predictable curves for cost and latency, with stable quality?

**Detect**

- Which lightweight classifier decides what kind of request this is: factual, creative, structured or unsafe?
- Does detection run in milliseconds?

**Retrieve**

- Which structured data, domain context or past interactions do we look up before calling a model?
- How does retrieval set boundaries on the model's creativity and reduce hallucinations?

**Draft**

- Which fast, lower-cost model produces the first structure?
- Does the user see the draft, or only the system?

**Verify**

- Which targeted checks run on the draft: fact checks, schema validation or narrow verifications?

**Uplevel**

- When exactly do we call the stronger, more expensive model?
- Is premium spend concentrated only on the sections where it matters?

**Cache**

- What can we reuse: chunks, embeddings or structured retrieval results?
- [+] When does a cached result become unsafe to reuse?

> **Care/Galen:** When a model tier fails, does MedMatch, today's system of record, act as the degradation floor?

### Pattern 2: The Ten Cost Levers

- Prompt Compaction: Which redundant tokens can we cut?
- Retrieval Scoping: Are we giving the model exactly what matters instead of the world?
- Cache Keys: Can we reuse outputs when inputs are identical or similar within a tolerance, and what is that tolerance?
- Speculative Decoding: Can we start rendering while verifying, to save perceived time?
- Multi-pass Pruning: Do we generate once and then prune or fix, instead of regenerating endlessly?
- Re-rankers over Re-generators: Can we generate fewer options and rerank them instead of calling multiple models?
- Post-edit Rules: Which stylistic cleanups can code handle instead of the model?
- Tiered Model Routing: Do cheap models handle the easy 80% and expensive models the hard 20%, and what is our actual split?
- Batch Verifications: Can we group fact checks or safety checks into fewer calls?
- Confidence Threshold Early Exits: Where can processing stop once the system is confident enough?
- When should the PM ask engineering to pull each lever?
- The article claims the levers together cut cost per outcome by 50–70%. Does that hold for our product?
- [+] Which levers have we pulled, and what did each one save?
- [+] Which levers put quality at risk (early exits, loose cache tolerance), and do they have eval coverage before we pull them?

### Pattern 3: Guardrail Grammar

- Are our guardrails clear, testable, binary statements, or vague rules in a wiki?
- Can each guardrail be enforced at runtime?
- Fact fence: Must every numerical claim link to a verified source ID?
- Policy fence: Does every irreversible external action, such as an email or a payment, require rung-3 approval?
- [+] Which ladder defines rung 3 for us? It is Supervise on the [Principle 6 ladder](#principle-6-agent-choreography-not-agent-hype) and Molding on the 4 M's; the article doesn't say which it means.
- Tone fence: What is the brand lexicon, and what happens when an output is flagged?
- Safety fence: What is the domain scope, and does the system refuse and escalate outside it?
- Do the guardrails live inside the cascade rather than outside it?
- [+] How do we test each fence, and what is its false-positive rate?

> **Care/Galen:** What does the safety fence look like for scope of practice, and which requests escalate to a provider instead of being refused?

### The 4 M's: the user-side ladder

The article labels this list as the Human-in-the-Loop Ladder too. The [Principle 6 ladder](#principle-6-agent-choreography-not-agent-hype) governs how much the agent acts. This one governs how users shape it.

- Marking: Can users flag, correct or annotate errors?
- Mentoring: Can users define rules or preferences the system learns?
- Molding: Can users upload examples or data that shape the model's behavior?
- Mandating: Can users set non-negotiable constraints the system must obey?
- How does each rung earn more trust through structure?
- [+] When a user-set rule conflicts with a system guardrail, which one wins?

### Pattern 4: System Design Is Product Sense

- Do we understand the system well enough to make product calls?
- When we ask for "faster," do we know which cascade layer to optimize?
- When we ask for more features, do we know the cost surface they land on?
- Do we understand the guardrails, the cascade and the context window well enough to design trust, speed and quality?
- [+] Can the PM sketch the architecture on a whiteboard without help?

---

## 6. Go-to-market

- Is the PM co-owning GTM with product marketing, or handing it off?
- Does the GTM message match how the product actually behaves, not how we wish it would?

### GTM Concept 1: Two-Sided Aha

- User aha: When does a single interaction save the user time or make the task safer?
- Buyer aha: When does the budget owner see clear ROI, trust and defensibility?
- The article's example pairs a 30-minute task shrinking to 4 minutes (user) with a 60% drop in cost per outcome and no new headcount (buyer). What are our two numbers?
- Are we designing both moments on purpose?

> **Care/Galen:** If the user aha belongs to the provider and the buyer aha to Care Ops leadership and Finance, what does each need to see?

### GTM Concept 2: Golden Path Onboarding

- What happens in the user's first 7 minutes?
- One core task: Which single task does onboarding focus on?
- Minimal Golden Context: What is the least context needed for a good first result? See [Principle 4](#principle-4-context-is-capital).
- Spark under 0.7s: Does the first signal appear that fast?
- P80 within 5 minutes: Does the user get a P80 result in that window?
- Trust signal: What is the one visible trust signal (a verified claim, a guardrail or a confident correction)?
- Shareable artifact: What can the user show someone at the end, such as a doc, a clip or a diff?
- Is the wow moment real, not staged?

### GTM Concept 3: Sell the Feeling, Not the Feature

- Does our message describe the relief, or the technology?
- Can we state the outcome in concrete terms: the time saved, the result and whether it is ready to use?
- Have we cut vague slogans like "Powered by AI" and "intelligent workflows"?
- [+] Can SUQS data back every claim in the message?

### GTM Concept 4: Trust-Led Distribution

- What sentence would one user say to a peer: "I actually let this thing do X without checking"?
- Which trust architecture makes that sentence true?
- [+] Through which peer networks does trust pass in this user group?

> **Care/Galen:** What would a provider need to see before telling a peer they send the AI draft without rewriting it?

### GTM Concept 5: Strategic Moats

- Which workflow moment do we own, and why can't someone else take it?
- Would removing the product break how the user gets their job done?
- Is our answer "our model is better"? If so, we don't have a moat.
- Is our pitch "AI-powered X," or "the only ones you trust to do Z automatically"?
- Workflow Embedding: How deeply is the product integrated into the core workflow?
- Trust Leap: Which automation rights have we earned?
- Distribution Asymmetry: Does the product get better with usage, so our distribution advantages snowball over time?
- Compounding data: Do the data and context we gather with each use give us an advantage competitors can't buy?

### GTM Concept 6: From Demo to Default

- When will users stop thinking "I'm using this AI tool" and think "this is how I do my job"?
- Has the system disappeared into their daily flow?
- Have users stopped noticing it because they trust it?
- [+] Which metric tells us we have reached default status?

---

## 7. Rituals, reframed for a specific product

The article's four rituals build a PM's skill over time. Here they become questions for a specific product.

### Ritual 1: Competitor teardown

- Which AI products solve a similar job, and have we used them the way a normal user would?
- Where do their responses feel inconsistent or uncertain?
- How long do their Spark, Shape and Seal take?
- Which cascade architecture can we infer underneath?
- Where do they pull in context, and where do guardrails quietly step in?
- When do we feel comfortable letting them act alone, and when does that comfort evaporate?

### Ritual 2: REALM pre-mortem

Run these before launch. The guiding questions for each lens live in [REALM](#3-realm-the-five-lenses-and-10-principles).

- Reality: Have we misunderstood the actual user need?
- Elasticity: Will model behavior collapse at scale?
- Affordability: Are the economics unsustainable?
- Liability: Could we lose trust we can't rebuild?
- Market: Is there no compounding advantage?
- [+] Which similar AI launches flopped, and which lens failed for each?

### Ritual 3: Prototype spike

- Can we build a weekend prototype before committing a team?
- Does the prototype include a basic agent with real decision points?
- How do guardrails change the experience once we add them?
- What is the prototype's Quality Envelope: acceptable at P50, delightful at the top, and which errors would destroy trust? See [Principle 1](#principle-1-probabilistic-fit-not-feature-fit).
- What do the prototype's SUQS numbers look like?
- What changes when we vary context length or prompt structure?

### Ritual 4: Learn from people living it

- Whose postmortems and product reviews should we study first?
- Which product reviews where AI features are discussed can we attend?
- Who at the frontier has shipped something similar, and can we talk to them?
- Which AI PM communities share war stories relevant to this problem?

### The final test: trust

- Between the system and the user: Do users trust it enough to let it act?
- Between the economics and reality: Do costs hold at real traffic?
- Between promise and delivery: Does the product do what we say it does?
- Does this product make probabilistic intelligence feel dependable?
