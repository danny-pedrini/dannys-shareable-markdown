# Evals: journey-map

Per-output evals, run at Step 8 against: the spec JSON, the fact table, the Slides API readback (text runs, link URLs, notes), and the approved include/exclude list. Each check covers something the renderer's `validate()` can't. The validator already hard-blocks em dashes, length limits, missing fields, and undefined source keys.

## Active Evals

| ID | Name | Type | Check | Added | Last Result |
|----|------|------|-------|-------|-------------|
| G1 | Quote verbatim fidelity | Generalization | Code | 2026-10-15 | — |
| G2 | Claim and footnote traceability | Generalization | Code | 2026-10-15 | — |
| G3 | No real names or IDs on slide face | Generalization | Code | 2026-10-15 | — |
| G4 | No scope drift from approved include list | Generalization | Code | 2026-10-15 | — |
| G5 | Notes talk-track coverage | Generalization | Code | 2026-10-15 | — |
| G6 | System framing, not blame | Generalization | Judge | 2026-10-15 | — |

## Definitions

### G1: Quote verbatim fidelity

**Pass:** Every quoted string on the slide is a contiguous substring of its fact-table verbatim, in order. That covers `quote` callout text and `exchange` turn text. The only allowed change is cutting with "...".
**Fail:** Any quoted string differs from the verbatim by more than an ellipsis cut. A quote or exchange with `source: null` also fails.
**Check type:** Code-based

```check
Type: comparison
Source field: fact table `verbatim` column, keyed by source key
Target field: spec stages[].callouts[].text (type quote) and stages[].callouts[].turns[].text (type exchange), cross-checked against the API readback for the same shapes
Logic: For each quoted string Q with source key S, get V = fact-table verbatim for S. Split Q on "..." and strip the curly quotes the renderer adds. Fail if any part is not a case-sensitive substring of V, or if the parts don't appear in V in order. Fail if a quote or exchange callout has source null.
```

**Source:** evals-advisor design-time proposal (FM1)
**Added:** 2026-10-15
**Notes:** Catches hand edits that drift, e.g. "I still don't even know at this point, what's their BMI" rewritten as "I'm scrolling, scrolling... I still can't even find their BMI".

### G2: Claim and footnote traceability

**Pass:** Every cited source key exists in the fact table with status MATCH, or with an override logged in the trace's `decisions`. The on-slide number or claim matches the fact table. The rendered hyperlink URL for its footnote equals the fact-table URL. Every fine-print source is cited by at least one on-slide superscript.
**Fail:** A cited source is missing, unresolved (PARTIAL, MISMATCH, or NOT FOUND with no override), textually mismatched, linked to the wrong URL, or orphaned.
**Check type:** Code-based

```check
Type: comparison
Source field: fact table columns claim, verbatim, url, status, keyed by source key; trace decisions[]
Target field: spec sources{} joined to every source-bearing item; API readback link URLs on fine-print runs; superscript markers in on-slide text runs
Logic: For each cited key: join to the fact-table row (fail if absent); fail if status != MATCH and there is no decisions override; fail if spec url != fact-table url; fail if the item's numbers (regex \d[\d.,]*%?) don't appear in that row's claim or verbatim. Read back the fine-print runs: superscript N's label must link to the Nth cited source's URL. Fail on any fine-print superscript number that appears nowhere else on the slide.
```

**Source:** evals-advisor design-time proposal (FM2)
**Added:** 2026-10-15
**Notes:** Catches wrong-source mapping and orphans left behind after hand edits, e.g. a ⁷ whose callout was deleted.

### G3: No real names or IDs on slide face

**Pass:** No on-slide text run contains a real name or message or ticket ID that the fact table flagged "names present". Such strings may appear in speaker notes only.
**Fail:** Any flagged name or ID appears outside the notes.
**Check type:** Code-based

```check
Type: absence
Source field: literal strings recorded in fact-table rows flagged "names present"
Target field: API readback text of every on-slide shape (exclude the speaker-notes shape)
Logic: Case-insensitive, word-boundary search for each flagged string across concatenated on-slide text. Fail on any hit.
```

**Source:** evals-advisor design-time proposal (FM3)
**Added:** 2026-10-15

### G4: No scope drift from approved include list

**Pass:** Every stage line, callout, cost stat, and "what we built" line in the spec matches an entry on the Step 3 approved include list.
**Fail:** The spec contains an item with no approved entry.
**Check type:** Code-based

```check
Type: comparison
Source field: approved include list saved at Step 3 (scratchpad `include-list.md`, also logged in trace decisions)
Target field: spec stages[].lines[], stages[].callouts[], bottom_band.left.stats[], bottom_band.right.lines[]
Logic: Flatten the spec into (stage, item type, text) tuples. For each tuple, require an approved entry with the same stage and item type whose text matches, or contains the same quote or number. Fail on any unmatched tuple.
```

**Source:** evals-advisor design-time proposal (FM5)
**Added:** 2026-10-15
**Notes:** Layout fixes may shorten approved text, so match on the quote or number, not the exact wording.

### G5: Notes talk-track coverage

**Pass:** Every number and every quote on the slide face appears in the speaker notes, and the notes block that covers it contains a "Source:" line.
**Fail:** An on-slide number or quote is missing from the notes, or its block has no "Source:" line. A number deliberately left uncited may say where it came from in prose instead.
**Check type:** Code-based

```check
Type: comparison
Source field: number/percent tokens and quoted substrings from the API readback of on-slide text
Target field: spec notes, split into blocks on blank lines
Logic: For each token or quote, find the notes block that contains it (fail if none). Fail if that block has no line starting "Source:", unless the item has source null in the spec.
```

**Source:** evals-advisor design-time proposal (FM7)
**Added:** 2026-10-15

### G6: System framing, not blame

**Pass:** Pain points on the slide and in the notes are framed around the system cause that the evidence names (incentive, queue, tooling, policy).
**Fail:** Any phrase attributes a bad outcome to an individual's effort, competence, or character where the cited evidence names a system cause.
**Check type:** LLM judge

```judge
Criterion: Does any on-slide or notes passage frame a pain point as an individual's personal failing when the fact-table evidence names a system cause?
Pass definition: Pain points read as consequences of the system (pay model, queue, tools, policy), matching the evidence.
Fail definition: A passage blames a role-labeled individual's competence or character where the evidence names a system cause.
Examples: [add Pass/Fail examples from real runs; do not fabricate]
```

**Source:** evals-advisor design-time proposal (FM6)
**Added:** 2026-10-15
