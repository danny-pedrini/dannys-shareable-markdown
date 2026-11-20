# Evals: curriculum-sweep

## Active Evals

| ID | Name | Type | Check | Added | Last Result |
|----|------|------|-------|-------|-------------|
| G1 | Link coverage | Generalization | Code | 2026-07-24 | P 2026-11-20 (vacuous: 0 explore links; the only link reclassified to skip) |
| G2 | Grounded summaries | Generalization | Judge | 2026-07-24 | P 2026-11-20 (vacuous: no entries added, judge not run) |
| G3 | Marker-link integrity | Generalization | Code | 2026-07-24 | P 2026-11-20 (vacuous: no entry lines added) |
| G4 | Reciprocal cross-references | Generalization | Code | 2026-07-24 | P 2026-11-20 (vacuous: no ↔ added) |
| G5 | No duplicate entries | Generalization | Code | 2026-07-24 | P 2026-11-20 (0 entries added, 0 dupes) |
| G6 | Categorization defensibility | Generalization | Judge | 2026-07-24 | P 2026-11-20 (vacuous: no entries added, judge not run) |
| G7 | State integrity | Generalization | Code | 2026-07-24 | P 2026-11-20 (1/1 ID traced, skip_reason present) |

## Definitions

### G1: Link coverage

**Pass:** Every URL in this run's manifest with `disposition_planned: "explore"` appears (unwrapped form) in the curriculum file OR in a Flags & Housekeeping flag/skip note.
**Fail:** Any such manifest URL absent from both.
**Check type:** Code-based

**Implementation:**

```check
Type: comparison
Source field: run manifest (observability/manifests/<run>-manifest.json), link entries with link-level "planned": "explore"
Target field: AI-Learning/Curriculum/AI-Learning-Curriculum.md (full file including Flags section)
Logic: for each manifest URL, grep -F the curriculum for the unwrapped URL (strip urldefense wrapper, decode &amp;). Any URL with zero hits = Fail. Report the missing URLs.
```

**Source:** Design-time evals-advisor (FM1, CRITICAL)
**Added:** 2026-07-24
**Notes:** Only runnable if the manifest was written (SKILL.md Step 3 mandates it). Missing manifest = automatic Fail.

### G2: Grounded summaries

**Pass:** For 2 randomly sampled entries added this run, re-fetching the source confirms every specific claim (figures, quotes, attributions, feature names).
**Fail:** Any sampled entry contains a claim the fetched source does not support.
**Check type:** LLM judge

**Implementation:**

```judge
Criterion: Does the fetched source content support every specific claim in this curriculum entry?
Pass definition: All figures, quotes, attributions, and named features in the entry appear in or are directly supported by the source (or its search-recovered mirror).
Fail definition: Any specific claim is absent from, or contradicted by, the source. Vague paraphrase is acceptable; invented specifics are not.
Examples: [add from real runs — do not fabricate]
```

**Source:** Design-time evals-advisor (FM2, CRITICAL)
**Added:** 2026-07-24
**Notes:** Sampled (2 entries/run) for cost; QA Step 6 FM2 provides an independent second sample. If the source is now unreachable, sample a different entry rather than failing. The judge runs as a subagent WITH web access and must re-fetch the sampled URLs — never grade from entry text alone.

### G3: Marker-link integrity

**Pass:** Among lines ADDED this run (git diff): every line containing 🔗 or 📺 contains `](http`; every youtube.com/youtu.be URL sits on a line whose entry marker is 📺 (or carries an inline 📺 for combined entries); no 📌 line contains an http URL except the "Related:"-framed exception; every added 🔗/📺/📌 entry line ends with `*(added YYYY-MM-DD)*` matching the run date.
**Fail:** Any violation on an added line.
**Check type:** Code-based

**Implementation:**

```check
Type: pattern
Source field: lines added this run — diff of the current curriculum file against the Step 1 baseline snapshot (never live git; auto-sync commits absorb mid-run edits)
Target field: same
Logic: (a) grep added lines for 🔗|📺 lacking "](http" → Fail. (b) grep added lines for youtube.com|youtu.be where the line has no 📺 → Fail. (c) grep added 📌 lines containing http:// or https:// and NOT containing "Related" → Fail. (d) grep added entry lines (starting `- 🔗|📺|📌`) not ending with `*(added YYYY-MM-DD)*` where the date equals the run date → Fail.
```

**Source:** Design-time evals-advisor (FM3a, MEDIUM)
**Added:** 2026-07-24

### G4: Reciprocal cross-references

**Pass:** Every `↔ §N` marker on lines added this run points to a section N that contains corresponding content for the same item (an entry, cross-listed entry, or "(primary listing)" pointer).
**Fail:** Any dangling ↔ pointer.
**Check type:** Code-based

**Implementation:**

```check
Type: structural
Source field: baseline-snapshot diff, added lines containing "↔ §"
Target field: the referenced sections in the curriculum file
Logic: for each added "↔ §N" marker, extract the entry's key URL or title; grep section N's content for that URL/title. Zero hits = Fail. Also verify cited section number matches the section's actual title.
```

**Source:** Design-time evals-advisor (FM3b, MEDIUM)
**Added:** 2026-07-24

### G5: No duplicate entries

**Pass:** No URL newly added as a full entry already existed as a full entry in the pre-run file (cross-listings marked ↔ or "(primary listing)" exempt).
**Fail:** A URL gains a second standalone full entry.
**Check type:** Code-based

**Implementation:**

```check
Type: absence
Source field: URLs on added full-entry lines (baseline-snapshot diff)
Target field: the Step 1 baseline snapshot of the curriculum file
Logic: for each newly added full-entry URL, grep the baseline snapshot. If present AND the new line carries no ↔/primary-listing marker → Fail.
```

**Source:** Design-time evals-advisor (FM4, MEDIUM)
**Added:** 2026-07-24

### G6: Categorization defensibility

**Pass:** Every entry added this run sits in a section whose stated theme matches the entry's content; any new category created this run contains ≥2 entries that fit no pre-existing category.
**Fail:** An entry plainly belongs to a different existing section, or a new category's scope duplicates an existing one.
**Check type:** LLM judge

**Implementation:**

```judge
Criterion: Is each new entry in the most defensible section of the current file, and is any new category genuinely necessary?
Pass definition: A reader familiar with the file's section intros would place each entry where it is (or accept the ↔ cross-listing as covering the ambiguity). New categories cover content no existing section's intro encompasses.
Fail definition: An entry's content matches a different section's intro distinctly better and no cross-listing bridges it, or a new category overlaps an existing section's scope.
Examples: [add from real runs — do not fabricate]
```

**Source:** Design-time evals-advisor (FM5, MEDIUM)
**Added:** 2026-07-24
**Notes:** Supporting evidence for the "new category creation" Graduate decision point — the authoritative graduation metric is USER ACCEPTANCE (3 consecutive accepted categories, tracked in state.json `new_category_streak` per SKILL.md Step 10). A G6 pass does not by itself advance the streak.

### G7: State integrity

**Pass:** Every thread ID appended to state.json this run (diff vs. the Step 1 baseline snapshot of state.json) traces to ≥1 of: a manifest link present in the curriculum, a documented skip in Flags, or a flag entry.
**Fail:** Any thread ID marked processed with no curriculum/skip/flag trace.
**Check type:** Code-based

**Implementation:**

```check
Type: comparison
Source field: thread IDs added to state.json this run (diff vs. the baseline snapshot of state.json)
Target field: run manifest + curriculum file (Flags section for skips)
Logic: for each new state ID, find it in the manifest; verify its disposition is consistent (explore → its links resolve per G1; skip → skip_reason present). Any ID absent from the manifest, or with disposition "integrated" but no curriculum trace → Fail.
```

**Source:** Design-time evals-advisor (FM6, HIGH)
**Added:** 2026-07-24
