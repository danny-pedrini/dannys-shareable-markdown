# Stage 1B — Feature Research, Promotion, and the Design Brief

**Runs on every prototype**, cold start or warm. Produces `prototypes/<feature>/design-brief.md` and, at Gate 1, updates the app-wide `design-system.md` in place.

Read `context-contract.md` first if you have not this run.

---

## What this stage does differently now

Earlier versions copied the entire app-wide design system into each prototype and interleaved feature findings. That produced ~655 duplicated lines per prototype and stranded genuinely app-wide discoveries inside feature files — `data-grid-styles.ts` (17 importing files) and `DialogContext` (215 call sites) both sat in a per-feature copy and were re-discovered by later runs.

The model now:

1. **Research** the feature against the existing app (unchanged).
2. **Promote** Established findings *into* the app-wide file — it gets richer every run.
3. **Write a small brief** with only what is genuinely feature-specific.

Consequence: later prototypes for the same app start from more, and research gets cheaper over time rather than repeating.

---

## Step 1B.0: App-wide schema migration check (do this FIRST, every run)

The v5.0 promotion protocol and the downstream paste-sections depend on the app-wide file having sections that **pre-v5.0 files do not have**. Verify and patch before dispatching anything.

Check `prototypes/_design-system/<app>/design-system.md` for each of these. The orchestrator patches any that are missing — no subagent needed, these are structural additions, not content changes:

| Required section | If missing |
|---|---|
| `## Common Mistakes To Avoid` (H2) | Pre-v5.0 files may have a lowercase prose line like `Common mistakes to avoid:` inside Visual Identity. **Promote it to a proper H2 section**, preserving its existing bullets verbatim. If nothing equivalent exists, create the H2 with the note: `*No app-level traps recorded yet — populated from fidelity-review `app_level_lessons` as runs accumulate.*` |
| `## Promotion Log` (H2, at end of file) | Create it with the table header: `\| Date \| From feature \| What was promoted \| Evidence \|` and the note `*Feature findings graduated into this file. Appended at Gate 1 of each run.*` |
| `*Schema version: N*` in the header block | Add `*Schema version: 1*` |
| `*Last freshness check: [date]*` in the header block | Add it with the date of the most recent verification, or today if the freshness check just passed |

**Do not invent content while migrating.** Preserve every existing value verbatim. This step only adds structure so later steps have somewhere to write; it never changes a token, citation, or claim.

Report the migration at Gate 1 under a "Schema migration" line so the user knows the shared file's structure changed.

**Known state as of the v5.x rollout:** the live `prototypes/_design-system/beyondrx/design-system.md` has neither `## Common Mistakes To Avoid` (it has a lowercase prose line at ~line 35) nor `## Promotion Log`, and carries no schema-version line. It **will** need this migration on its first v5.x run.

---

## Step 1B.1: Feature research (parallel)

Dispatch these in a SINGLE message.

**Subagent types:** both use **`general-purpose`** — each writes its findings to disk, and `Explore` cannot use Write or Edit.

### Code researcher (`general-purpose`)

```
You are researching which existing pages and components in <repo-name> are most relevant
to building a prototype for: "<feature description from idea source>".

Read for context (path — consult as needed, do not summarize back):
  prototypes/_design-system/<app>/design-system.md

Before you begin, quote from that file: the framework line from Tech Stack, and one
structural pattern from Visual Identity. If you cannot, stop and report the failure.

Your job:
1. Find pages/screens functionally similar to the feature being built (building a queue
   view → find existing queue/table/list pages).
2. For each relevant page: URL route, key components, layout pattern, data-fetching
   approach, and how it handles loading / empty / error.
3. For each relevant component: file path, props interface, which tokens it uses,
   patterns worth replicating.
4. Rank by relevance — closest match first.
5. For every pattern you report, give an occurrence count across the codebase. This
   determines promotion eligibility downstream, so count carefully: how many files
   import or use this pattern?

Write to: prototypes/<feature>/.pipeline/research/_code-research.md

Format:

## Most Relevant Pages
| Rank | Page | Route | Why Relevant | Key Components | Source |
|---|---|---|---|---|---|

For each top-3 page:
### [Page Name]
- **Route:**
- **Layout pattern:** [+ citation]
- **Components used:** [list with paths]
- **Tokens/styles used:** [specific token names — cite each]
- **State handling:** [loading/empty/error approach]
- **Data fetching:** [hook name, query key, response shape]
- **What to replicate:**
- **What NOT to replicate:** [page-specific things that would not apply]

## Most Relevant Components
[Same detail for components appearing across multiple pages]

## Patterns Not In The App-Wide Design System
| Pattern | Value/Shape | Occurrence count | Citations | Why the feature needs it |
|---|---|---|---|---|
[This table feeds the promotion decision. Be precise about counts.]

Report back: the file written, the #1 ranked page, and the count of new patterns found.
```

### Browser researcher (`general-purpose`, only if Chrome DevTools available)

```
You are visually researching the staging app to find design-inspiration pages for a
prototype of: "<feature description>".

Using Chrome DevTools MCP:
1. Navigate to pages likely similar to the feature being built
2. Screenshot each relevant page
3. For each page: note the visual layout, table structure, button placement, header
   treatment, spacing rhythm, and any patterns the prototype should match
4. Save screenshots to prototypes/<feature>/.pipeline/screenshots/ with descriptive names

Write findings to: prototypes/<feature>/.pipeline/research/_browser-research.md
Report back: pages visited, screenshots taken, and per page a brief description of what
visual patterns are relevant to the prototype.
```

---

## Step 1B.2: Research auditor + promotion decision

Spawn one auditor (`general-purpose`):

```
You are auditing feature-specific design research for <feature>, and deciding which
findings graduate into the app-wide design system.

Read:
- App-wide design system: prototypes/_design-system/<app>/design-system.md
- Code research: prototypes/<feature>/.pipeline/research/_code-research.md
- Browser research (if present): prototypes/<feature>/.pipeline/research/_browser-research.md

Confirm you read all three: name each file and one fact from it. If a file is missing,
say so explicitly and continue with what exists.

Your job:

1. **Relevance check.** Are the identified pages/components actually relevant to this
   feature? Flag anything that looks like a stretch.

2. **Promotion decision — this is the important one.** For each entry in the code
   researcher's "Patterns Not In The App-Wide Design System" table, classify:

   | Classification | Criterion | Destination |
   |---|---|---|
   | **PROMOTE** | Established (>=3 occurrences) AND not feature-specific in nature — a token, base component, reusable style object, shared type, or data/form pattern any feature could use | App-wide design-system.md |
   | **BRIEF-ONLY** | Established but genuinely specific to this feature's domain (e.g. a column set that only makes sense for this screen) | design-brief.md |
   | **BRIEF-ONLY (below threshold)** | Probable (2) or Single instance (1), regardless of nature | design-brief.md, tagged with status |
   | **REJECT** | Citation missing, vague, or unverifiable | Neither — flag as unverified |

   Verify the citation for every PROMOTE candidate by re-reading the cited file:line
   yourself. A promotion writes into the shared file every future prototype inherits —
   an unverified promotion is worse than a missed one. Downgrade to BRIEF-ONLY if the
   citation does not hold.

   Test for "not feature-specific": would a *different* feature for this app plausibly
   use this? 17 files importing a grid style = yes. A dialog for combining non-Rx
   packages = no.

3. **Conflict resolution.** If a finding conflicts with an existing app-wide value,
   determine which has more consistent evidence across the codebase. Higher occurrence
   count wins. Never silently overwrite an app-wide value — every conflict goes to the
   user at Gate 1 with both values and your recommendation.

4. **Inspiration summary.** Ranked "build it like this" references — the specific pages
   and components the prototype should use as visual anchors.

Write to: prototypes/<feature>/.pipeline/research/_research-audit.md

Format:

## Inspiration Sources (Ranked)
| Rank | Source | Route | Why | Key Patterns To Copy | Screenshot |
|---|---|---|---|---|---|

## Promotion Manifest (app-wide additions — requires Gate 1 approval)
| Pattern | Value/Shape | Occurrences | Citations | Citation verified? | Target section |
|---|---|---|---|---|---|

## Brief-Only Findings
| Pattern | Value | Status | Why not promoted |
|---|---|---|---|

## Conflicts Requiring User Decision
| Pattern | App-Wide Value | Research Value | Occurrence counts | Recommendation |
|---|---|---|---|---|

## Rejected (Unverifiable)
## Relevance Concerns

Report back: promote count, brief-only count, conflict count, rejected count.
```

---

## Step 1B.3: Write the design brief

Spawn one synthesizer (`general-purpose`). This is a **small** file — if it exceeds ~150 lines, content is leaking in that belongs app-wide or nowhere.

```
You are writing the feature-local design brief for <feature>.

Read: prototypes/<feature>/.pipeline/research/_research-audit.md
Path for reference (do NOT copy content from it): prototypes/_design-system/<app>/design-system.md

PROOF OF READ — before writing, confirm from the app-wide file: its exact `Schema version`
line, and the names of two sections whose content you must therefore NOT duplicate into the
brief. If you cannot find the Schema version line, report it — the app-wide file may need
migration (see Step 1B.0).

Write to: prototypes/<feature>/design-brief.md

CRITICAL: This file must NOT duplicate the app-wide design system. No color tables, no
typography scales, no spacing scales, no component inventory, no shared type interfaces.
Those live in the app-wide file and downstream agents read them there by path. Duplicating
them is the specific failure this file was created to eliminate.

Include ONLY feature-specific content:

# Design Brief — <feature>
*Feature-local additions to the app-wide design system.*
*App-wide source of truth: `prototypes/_design-system/<app>/design-system.md` — READ IT
for all tokens, typography, spacing, components, data-layer patterns, and shared types.*
*The permitted-value allowlist is the UNION of that file and this one.*
*Created [date] | App-wide schema version: [N]*

## Feature Summary
[2-3 sentences: what is being built and for whom.]

## Feature-Specific Inspiration
### Ranked Inspiration Sources
| Rank | Source Page/Component | Route | Why | Screenshot |
|---|---|---|---|---|

### Build It Like This
[Per top-3 source: concrete instructions on what to copy — layout, structure, state
handling, interaction patterns — with file:line citations. This is the primary framing
content for implementers. Be specific: "same MUI Table with custom Cell wrappers as
src/app/queue_dashboard/components/pharmacy-queues-table.tsx:34-88, not a DataGrid."]

### Do NOT Replicate
[Page-specific things from the inspiration sources that would be wrong here.]

## Feature-Local Patterns
[Only BRIEF-ONLY findings from the audit. Each with value, status
(Established/Probable/Single), citation, and why it did not promote. These are permitted
in THIS prototype only.]

## Feature Routes
| Route | Page | Notes |
|---|---|---|

## Feature-Local Type Interfaces
[Only interfaces specific to this feature. Shared domain types live app-wide — cite them
by name and point at the app-wide file.]

## Conflicts Resolved At Gate 1
| Pattern | Chosen Value | Rejected Value | Rationale | Decided by |
|---|---|---|---|---|

## Screenshots
| File | Page | Captured | Fresh or cached |
|---|---|---|---|

## Open Items
[Anything still unresolved.]

Report back: line count of the file written, and confirmation that no app-wide token
tables were copied into it.
```

---

## 🛑 Gate 1: User reviews the brief and approves promotions

Present to the user:

- Path to `design-brief.md` and its line count
- **Ranked inspiration sources** with screenshots — this is the substance of the gate; the user is confirming "yes, build it like that page"
- **Promotion manifest** — what will be written into the shared app-wide file, with evidence. Flag that these persist beyond this prototype.
- **Conflicts** — both values, occurrence counts, your recommendation. User decides.
- Screenshot freshness — anything reused from cache and how old
- Batched open questions

### Applying promotions (after approval only)

Once the user approves, the orchestrator edits `prototypes/_design-system/<app>/design-system.md` directly:

1. Insert each approved pattern into its target section, tagged `[Promoted from <feature>, YYYY-MM-DD]`.
2. Append a row per promotion to the **Promotion Log** table at the bottom of the file.
3. If a conflict was resolved in favor of the research value, update the app-wide value and record the old value in the Promotion Log row.
4. Bump `Last freshness check` to today — the promoted claims were just verified against production.
5. If a fidelity review later reveals a systematic error, append the lesson to the app-wide **Common Mistakes To Avoid** section (see `stage-4-fidelity-observability.md`).

**Guards:**

- Never promote without user approval at this gate.
- Never promote an unverified citation.
- Never promote below the ≥3 threshold.
- Never silently overwrite — every changed app-wide value gets a Promotion Log row with the prior value.
- Do not promote from a *failed* run. If the pipeline aborts before Gate 3, promotions made at Gate 1 stand only if their citations were verified; note the incomplete run in the log.
