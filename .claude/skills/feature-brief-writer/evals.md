# Evals: feature-brief-writer

Per-output evals. Step 6 runs every one of them on every QA round; Step 7 records the final round's verdicts here and in the trace. Graders read only the definitions they are assigned (`references/grader-briefs.md`).

## Active Evals

| ID | Name | Type | Check | Covers | Grader | Added | Last Result |
|----|------|------|-------|--------|--------|-------|-------------|
| G1 | Template conformance | Generalization | Code | FM3 | `scripts/mechanical_check.py` | 2026-11-18 | Pass, 2026-11-18 |
| G2 | Hard writing searches | Generalization | Code | FM4 (mechanical) | `scripts/mechanical_check.py` | 2026-11-18 | Pass, 2026-11-18 |
| G3 | Every claim sourced | Generalization | Judge | FM1 | Fidelity judge | 2026-11-18 | Pass, 2026-11-18 |
| G4 | Reader-first order | Generalization | Judge | FM2 | Fidelity judge | 2026-11-18 | Pass, 2026-11-18 |
| G5 | Plain, uncompressed writing | Generalization | Judge | FM4 (judgment) | Writing judge | 2026-11-18 | Fail, 2026-11-18 |
| G6 | Stop discipline | Generalization | Code | FM5 | `scripts/mechanical_check.py` | 2026-11-18 | Fail, 2026-11-18 |
| G7 | Gate 1 fidelity | Generalization | Judge | Gate 1 | Fidelity judge | 2026-11-18 | Pass, 2026-11-18 |

## Definitions

### G1: Template conformance

**Pass:** The brief's headers match the canonical header sequence in `Templates/Feature-Brief-Template.md` exactly, the Appendix H3s match the list in `gate-1.md`, the byline follows the H1, and no template placeholder is left.
**Fail:** Any header added, dropped, renamed, repeated, or out of order; an Appendix sub-section not on the Gate 1 list; a missing byline; or a leftover placeholder.
**Check type:** Code-based

```check
Type: structural
Source field: Templates/Feature-Brief-Template.md "Canonical header sequence" block; gate-1.md "Options header:" and "Appendix:" lines
Target field: every H1, H2, and H3 in the brief, outside fenced code
Logic: (1) Substitute the feature name for <X> into the canonical H1/H2 list, and replace the line starting "## What are our other options" with "## " plus the Gate 1 Options header, which must start with "What are our other options" and end with "?"; the brief's H1 and H2 headers, bold markers stripped and curly quotes normalized, must equal that list in order. (2) The H3 headers must all sit under "## Appendix" and equal the Gate 1 Appendix list in order, lettered A, B, C with no gap. (3) The first non-blank line after the H1 matches "<Name> | <Mon D, YYYY>". (4) No "<X>", "<Name>", "<Function>", "<title>", or other "<word>" placeholder outside code. (5) Every "Appendix <Letter>" pointer in the body names a letter on the Gate 1 list.
```

**Source:** Phase 1 D4, FM3 (Danny, Nov 18, 2026: "Must never: go outside the brief template")
**Added:** 2026-11-18

### G2: Hard writing searches

**Pass:** Zero hits on every row of "Hard verification searches" in `forbidden-writing-patterns.md` except row 7, on the AGENTS.md plain-word and filler bans, and on session-artifact citations.
**Fail:** Any hit.
**Check type:** Code-based

```check
Type: absence
Source field: forbidden-writing-patterns.md "Hard verification searches" rows 0, 1, 3, 4, 5, 6, 8, 8b, 9; AGENTS.md plain-word and filler lists
Target field: the brief, with fenced code, `>` blockquote lines (verbatim quoted copy), and link targets removed
Logic: Run each search as its row states (row 8 is exempt when the sentence carries "[Assumption:" or "[estimate range]"; row 8b only when it carries "[Assumption:"; row 9 runs on the final paragraph and last 3 bullets). Also search for the plain-word bans (utilize, leverage, facilitate, in order to, prior to, subsequently, delve, landscape, ecosystem), the filler bans (It's worth noting, It's important to, Needless to say, At this point in time, moving forward, going forward), and session-artifact citations ("ledger L<n>", "L<n>" in parentheses, "Gate 1", "gate-1", "intake Q<n>", "round <n>"). Any hit fails. If the forbidden-patterns file has a row the script does not implement, report Fail (ambiguous).
```

**Source:** Phase 1 D4, FM4; AGENTS.md pre-delivery checklist
**Added:** 2026-11-18

### G3: Every claim sourced

**Pass:** Every number, quote, name, date, and link in the brief traces to a ledger row whose saved copy says the same thing, and every claim from a doc, sheet, Slack thread, or deck carries a link a reader can open.
**Fail:** Any claim with no ledger row, a ledger row whose saved copy says something different (a changed number, a widened scope, a quote reworded), a named person not in the inputs, Gate 1, or `Stakeholder Management/stakeholder-directory.md`, or a sourced claim with no openable link.
**Check type:** LLM judge

```judge
Criterion: Does every factual claim in the brief match a ledger row and that row's saved copy, with an openable link where the source is a doc or thread?
Pass definition: Each number, quote, name, date, and link maps to a ledger row; the saved copy at its locator supports the claim as worded; doc and thread claims link to the source. Ledger rows marked `none (Danny)`, `local: <path>`, or `code: <repo>/<path>` need no link in the brief. `[TBD: <owner> to <what>]` placeholders pass.
Fail definition: One or more claims are missing from the ledger, differ from the saved copy, name an unsourced person, or lack the link. Quote the claim and the saved copy side by side.
Examples: Add from real runs. Do not invent.
```

**Source:** Phase 1 D4, FM1
**Added:** 2026-11-18

### G4: Reader-first order

**Pass:** The Summary's first paragraph tells the reader why the idea matters before or alongside what it is, and the second paragraph states the brief's purpose and ask as approved in `gate-1.md`; "What is <X>?" shows today's experience (or what people do instead) before the new one; and every claim in "Why would we do <X>?" carries its support or an owned `[TBD: ...]` inside its bullet.
**Fail:** The Summary opens with a bare description of the feature that gives no reason to care, the purpose paragraph is missing or asks for something other than the Gate 1 ask, "What is" describes the new flow before today's experience, or a "Why" claim has no support or owned TBD in its bullet.
**Check type:** LLM judge

```judge
Criterion: Does the brief tell its readers why to care and what it needs from them before asking them to absorb the solution?
Pass definition: Summary paragraph 1 gives the reason to care no later than its second sentence; paragraph 2 names the Gate 1 purpose and ask; "Today," (or what people do instead) precedes "With <X>,"; every Why claim has support or an owned TBD in the same bullet. Opening with evidence, the problem, or "We propose X because Y" can all pass.
Fail definition: Any of those four is broken. Quote the first sentence of the offending section.
Examples: Pass: "A teammate has built a model that predicts the provider's treatment decision with high accuracy on a large share of initial visits." followed by "We propose a variant of AI-Recommended Next Actions called Feature X." Fail: a Summary whose first two sentences only describe what the feature does.
```

**Source:** Phase 1 D4, FM2; generalized Nov 18, 2026 (Danny: evidence-first is one way to lead, not the rule)
**Added:** 2026-11-18

### G5: Plain, uncompressed writing

**Pass:** No compression slop (C1 to C6 in `forbidden-writing-patterns.md`), no forced triplet (row 7), no AI slop from the Watch-for list, and the AGENTS.md structural checks pass: one idea per sentence, no paragraph over 4 sentences, no sentence over 35 words unless splitting hurts clarity, the draft stops on its strongest line, and a cold reader understands every sentence on one read.
**Fail:** Any instance of C1 to C6, a row 7 triplet, AI slop, or a broken structural check.
**Check type:** LLM judge

```judge
Criterion: Would one of the brief's readers (gate-1.md, "Purpose and readers") who has never seen this feature understand every sentence on one read, with no compressed shorthand?
Pass definition: Zero instances of C1 to C6, row 7, or Watch-for AI slop, and every AGENTS.md structural check passes.
Fail definition: Name the pattern ID, quote the sentence, and give a plain rewrite in the voice of danny-voice-exemplar.md lines 19 to 48.
Examples: The C1 to C6 bad and fix pairs in forbidden-writing-patterns.md, and danny-voice-exemplar.md lines 49 to 92 (the AI draft) as the fail case.
```

**Source:** Phase 1 D4, FM4; Danny, Nov 18, 2026, on compressed shorthand in AI drafts
**Added:** 2026-11-18

### G6: Stop discipline

**Pass:** Every failed MCP call in `mcp-calls.jsonl` is followed directly by one retry of the same tool and resource that succeeded, `preflight.md` has no `Failed` row, and every row in `link-check.md` is `OK` for the current round.
**Fail:** A failed call with no retry, a second retry, a different tool or resource used after a failure, a failed retry followed by more calls, a `Failed` preflight row, or a `Failed` link row.
**Check type:** Code-based

```check
Type: structural
Source field: <run>/mcp-calls.jsonl, <run>/preflight.md, <run>/link-check.md
Target field: the same files
Logic: Read mcp-calls.jsonl in order. For each line with ok=false and step not "8": the next line must have retry_of equal to its n, the same tool and resource, and ok=true. No line may have retry_of pointing at a line that is itself a retry. Any line with step "8" is ignored (Confluence push failures are reported, not stopped on). preflight.md and link-check.md: every Result cell equals "OK". link-check.md "Round:" equals the current QA round. Missing files fail.
```

**Source:** Phase 1 D4, FM5 (Danny: "If any MCP the run needs fails in a session, stop all work and report what failed")
**Added:** 2026-11-18

### G7: Gate 1 fidelity

**Pass:** The brief's purpose and ask, insight, opening, proposal, options, question owners, options header, and Appendix list are the ones in `gate-1.md`, including every change Danny made there.
**Fail:** The brief serves a different purpose or ask, drops the approved insight, opens differently, words the proposal so its scope changes, adds, drops, or swaps an option, names an owner not in `gate-1.md`, or drops one of Danny's Gate 1 changes.
**Check type:** LLM judge

```judge
Criterion: Does the brief carry every Gate 1 decision as approved?
Pass definition: Each decision in gate-1.md appears in the brief with the same meaning, and every item under "Danny's changes, verbatim" is reflected.
Fail definition: Name the decision, quote gate-1.md and the brief side by side, and say what changed.
Examples: Add from real runs. Do not invent.
```

**Source:** Phase 2 design, Gate 1 (Danny approves the framing before drafting)
**Added:** 2026-11-18
