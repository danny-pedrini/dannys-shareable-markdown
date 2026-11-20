# Feature Brief template

A feature brief is a one-pager on something we're planning to build, explore further, or solution on. It says what the idea is, why it's worth doing, what could go wrong, what else we could do, and what we still need to learn, so the people reading it can make the next decision. It does not size appetite or list no-gos.

The `feature-brief-writer` skill fills in this template on every run. The Feature X brief is one good example, written for one purpose (a feasibility check with Legal, Clinical, and Care Ops). `.claude/skills/feature-brief-writer/references/exemplar-fast-prescribe.md` shows its sections done well. Copy its moves, not its purpose.

## Purpose and readers

Every brief has one purpose, and the purpose decides what each section emphasizes. Danny picks it at Gate 1. Common ones:

| Purpose | The ask | Who reads it | What gets the most weight |
|---|---|---|---|
| Feasibility check | Can we do the most impactful version? | The functions that can say no (often Legal, Clinical, Care Ops) | Risks, the fallbacks, and kill questions per function |
| Discovery | Is this worth pursuing, and what do we need to learn first? | Product, design, eng, data, and research partners | The problem, the evidence so far, and the open questions |
| Solutioning | Here is the problem and a starting direction. Help shape it. | Design and eng partners | Today's experience, the direction, and the options |
| Build proposal | We want to build this. Agree, or tell us what's missing. | Leadership and the teams that would build it | Why now, the outcome it moves, and the risks |

A brief can mix these. Name the one that matters most.

The brief should also carry an insight: something the sources show together that none of them says alone, or the honest "so what" behind the evidence. A brief that only restates its sources isn't done.

## Canonical header sequence

`.claude/skills/feature-brief-writer/scripts/mechanical_check.py` reads this block. Each line is one header, in order. `<X>` is the feature name. Every line must appear exactly once, in this order. No other H1 or H2 may appear, and the only H3s are the Appendix sub-sections.

```
# Feature Brief: <X>
## Summary
## What is <X>?
## Why would we do <X>?
## What could go wrong?
## What are our other options?
## What are our most critical discovery questions?
## Appendix
```

The options header may add a clause that fits the purpose, such as "What are our other options if this isn't legally feasible?" or "What are our other options if the data doesn't support this?" It must start with "What are our other options" and end with "?". Danny picks the wording at Gate 1.

Appendix sub-sections are H3s lettered in order from A with no gaps: `### A. <title>`, `### B. <title>`, and so on. Danny approves the list of titles at Gate 1, and the script checks the brief against that list. Pick only what the feature has material for, and title each one for what it shows. Common choices:

- Flow (today's and the new one)
- Current state (screenshots of today's patient or provider experience)
- Mock or prototype of the new experience
- Tiers or rules (for example, a confidence ladder)
- Options, mocked
- Data behind a key number

Every in-text pointer like "(see Appendix A)" must point to a sub-section that exists. A brief with no supporting material has an Appendix with one sub-section, such as "A. Sources."

## Byline

The line right after the H1 is `<Name> | <Mon D, YYYY>`, for example `Danny Pedrini | Nov 16, 2026`. Use the run date unless Danny gives another.

## Section by section

### Summary (two paragraphs)

Paragraph 1 makes the case: why this matters, what we propose or want to explore, and the outcome it moves (quality of care, patient experience, or cost). Order the sentences for the reader. Lead with whatever makes them care first, which is often the strongest sourced fact (a model result, a measured gap, a complaint rate) and sometimes the problem itself. Never open with a bare description of the feature that gives no reason to care.

Paragraph 2 says why the brief exists: its purpose, who it's for, and what you need from them. Fit it to the purpose picked at Gate 1. For a feasibility check, the Feature X line works well:

> The purpose of this feature brief is to validate the feasibility of the concept with <functions> stakeholders before investing resources to further define and build the solution. In the event this most impactful version of the feature is not feasible, we propose less risky, though less impactful, alternatives.

For discovery, it names what we'd need to learn before committing. For solutioning, it invites the readers to shape the direction. For a build proposal, it asks for the go-ahead and names what's needed.

Source: SVPG, [Assessing Product Opportunities](https://www.svpg.com/assessing-product-opportunities/). An opportunity assessment exists to get a clear next decision, and it asks what the alternatives are.

### What is <X>?

1. **"Today, …"** One paragraph on what the patient or provider experiences now, in their words where possible (quote real copy). When there is no "today" (a brand-new capability), say what people do instead. Source: Intercom, [Job Stories](https://www.intercom.com/blog/using-job-stories-design-features-ui-ux/), and the "Today, customers…" opening of Amazon's [PR/FAQ](https://www.workingbackwards.com/concepts/working-backwards-pr-faq-process).
2. **"With <X>, …"** One or two paragraphs walking one specific case through the new flow, step by step. For a discovery or solutioning brief, walk through the direction you'd start from and say plainly what isn't decided. Define any new term in plain words the first time (for example, "a pre-prescription (a prescription written before any provider review)"). Source: Shape Up, [Write the Pitch](https://basecamp.com/shapeup/1.5-chapter-06), on telling one concrete story instead of describing the solution in the abstract.
3. Say what stays the same.
4. End with a pointer to the Appendix, for example "(see Appendix A)," when the Appendix has a flow or mock.

### Why would we do <X>?

A checkbox list. Each claim is a bold checkbox bullet; each piece of support is a nested italic checkbox bullet carrying a sourced number.

```
- [ ] **<Claim in one sentence.>** <One or two sentences of plain explanation, with a link.>
  - [ ] *<Supporting point.>* <The number, its source link, and any caveat (for example, "the data is correlational").>
```

- Each claim names the outcome it moves (quality of care, patient experience, cost).
- Every number has a source link in the same bullet (FM1).
- A number nobody has yet is a placeholder in code format: `` `[TBD: <owner> to <what>]` ``. Never estimate it.
- Say plainly when a number is an upper bound, a proxy, or correlational.

Source: Lenny Rachitsky's 1-pager template (Google Doc `1541V32QgSwyCFWxtiMIThn-6n-2s7fVWztEWVa970uo`), whose "Why" and success-measure sections this mirrors.

### What could go wrong?

Two to four bold checkbox risks. Each one says what goes wrong and, where a source has it, how often.

Source: SVPG, [The Four Big Risks](https://www.svpg.com/four-big-risks/) (value, usability, feasibility, viability), and the rabbit holes section of Shape Up's [Write the Pitch](https://basecamp.com/shapeup/1.5-chapter-06). Cover the risks the brief's readers will raise first. Do not list every risk.

### What are our other options?

One paragraph. Name each option in bold (for example **Fallback A** and **Fallback B**, or **Option A** and **Option B**), say in one sentence what it does, and say what it gives up or gains compared with the main proposal. For a feasibility check, the options are less risky, less impactful versions. For other purposes, they can be different approaches to the same problem, a smaller first step, or doing nothing, with what that costs. They are never unrelated ideas.

Source: Working Backwards [PR/FAQ](https://www.workingbackwards.com/concepts/working-backwards-pr-faq-process), on truth-seeking: a good FAQ shows that several options were considered.

### What are our most critical discovery questions?

Grouped by the people who can answer them, usually by function. Each group header is bold and names the owners in parentheses. Each question is a `- [ ]` checkbox.

```
**<Function> (<Name>, <Name>)**

- [ ] <Question this group has to answer before the next decision.>
```

- Owners come from Danny at Gate 1 or from `Stakeholder Management/stakeholder-directory.md`. Never guess a name (FM1). When nobody owns a question yet, write `` `[TBD: owner]` `` in the group header.
- Each question can be answered with yes, no, a number, or a specific finding. Lead each group with the question whose answer would most change or kill the idea.
- When the brief has options, ask the group most likely to say no what it thinks of them.

Source: SVPG, [The Four Big Risks](https://www.svpg.com/four-big-risks/), which assigns each risk to the function that owns it, and the internal FAQ half of the [PR/FAQ](https://www.workingbackwards.com/concepts/working-backwards-pr-faq-process).

### Appendix

A `---` rule, then `## Appendix`. Each sub-section opens with one plain sentence saying what the reader is looking at. These formats worked well in the Feature X brief; use them when they fit.

| Sub-section type | Content | Format |
|---|---|---|
| Tiers or rules | Each tier (for example, by model confidence), what happens at it, and the value it delivers | A code block |
| Flow | The end-to-end flow, one actor per row (PATIENT, EMR, MODEL, SYSTEM, PROVIDER), with branches back to "Today's experience" | A code block |
| Current state | Screenshots of today's experience with captions, plus an example of the message or screen the feature would change | Images and quoted text |
| Options, mocked | A code-block mock labeled "(dummy sample, not copy we'd actually use)", or a prototype screenshot | Code block or image |
| Mock or prototype | The new view, labeled "Presented to give a visualization, not for copy or design approval." | A code block or image |

Use the two disclaimers verbatim on any mock. Source: Shape Up's fat-marker sketches in [Write the Pitch](https://basecamp.com/shapeup/1.5-chapter-06), which keep mocks rough on purpose so readers react to the idea, not the pixels.

Screenshots are relative image links (`![caption](<slug>-assets/<file>.png)`). At Step 5 the skill copies each one from the run folder into `<slug>-assets/` next to the brief, so the links work during QA.
