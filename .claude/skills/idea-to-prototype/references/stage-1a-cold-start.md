# Stage 1A — App-Wide Design System (Cold Start)

**🧊 THIS IS THE COLD-START PATH. It runs when `prototypes/_design-system/<app>/design-system.md` does not exist — i.e. the first prototype ever built for an app.**

Because it runs rarely, it is the least-exercised path in the skill. Do not improvise it. Execute the steps below in order.

**Output:** `prototypes/_design-system/<app>/design-system.md` — the single source of truth defined in `context-contract.md`.

**Subagent types in this file:** the recon pass and the freshness check use `Explore` (read-only, they return findings). The extractors, auditor, and synthesizer use `general-purpose` because they **write to disk** — `Explore` cannot use Write or Edit.

**Model tier in this file:** every agent inherits the session model. This is the 🧊 cold-start exception in SKILL.md's `<model_tiering>` — extraction is novel discovery with no baseline to diff against, and the synthesizer's output becomes the root of every downstream allowlist. The only exception is the freshness check at the end of this file, which is not part of cold start.

---

## Step 1A.0: Recon pass (do this FIRST — do not skip on a new app)

You do not yet know how this app organizes styling. Never assume it looks like a previously-prototyped app. Dispatch **one** `Explore` subagent (read-only — it returns its file map; you write it to disk):

```
You are mapping where visual styling lives in the codebase <repo-name>. You are NOT
extracting values yet — you are locating the files a later pass will read exhaustively.

Determine:
1. Styling approach: MUI sx / styled-components / Emotion / CSS Modules / Tailwind /
   vanilla CSS / a design-tokens package / some mix. Cite evidence for each you find.
2. Where design tokens live. Look for: a theme directory, tailwind.config.*, a tokens
   or design-system package, *.css custom properties, styled-components ThemeProvider.
   Give exact paths.
3. Whether tokens are centralized or scattered. If scattered, name the 3-5 directories
   with the highest density of styling values.
4. Component library: a UI kit (MUI, Chakra, Radix, shadcn), custom in-house components,
   or both. Where do base components (Button, Input, Select) live?
5. Framework and router: read package.json. Next.js App Router / Next.js Pages / Vite +
   React Router / Remix / other. Quote the exact dependency versions.
6. Data-fetching library and form library from package.json + one usage example each.
7. Icon library.

Return a markdown file map:

## Styling Approach
[Approach + evidence citations]

## Token Locations
| What | Path | Centralized? |
|---|---|---|

## Component Library
[Kit + base component locations]

## Framework / Router / Data / Forms / Icons
| Concern | Choice | Version | Evidence (file:line) |
|---|---|---|---|

## Highest-Density Styling Directories
[Ranked list of 3-5 paths, for the exhaustive extraction pass]

## Anomalies
[Multiple competing approaches, dead theme files, migration in progress]

DO NOT write to disk. Return findings as your response.
```

**Why this exists:** the extractor bundling in Step 1A.1 is organized by *file locality*. That only works if you know which files hold the tokens. On a previously-prototyped app you already know; on a new app you must discover it first. Skipping this and assuming a `src/theme/` directory is a cold-start failure mode.

---

## Step 1A.1: Dispatch extractors (parallel, bundled by file locality)

Write the recon output to `prototypes/_design-system/<app>/.extraction/_recon.md` yourself (the recon agent is `Explore` and returns findings rather than writing them), then dispatch these **four** subagents in a SINGLE message using **`general-purpose`** — they write their findings to disk, which `Explore` cannot do. Bundles are organized by *where values live*, not by concept — one agent owning one location searches it completely, rather than five agents each partially scanning the same files.

| # | Subagent | Scope | Reads |
|---|---|---|---|
| 1 | **Token extractor** | Colors, typography, spacing, icon sizes, motion/transitions — **all five** from the token locations recon identified | The token files/dirs from recon |
| 2 | **Off-token sweeper** | Styling values used *outside* the token files: inline hex, one-off `sx` values, hardcoded px, ad-hoc font-families. Its job is occurrence counting and anomaly detection | The high-density dirs from recon, excluding token files |
| 3 | **Component & pattern extractor** | Base components + reusable style objects. Props/variants, file locations, visual description. Also note components that DON'T exist | Component library paths from recon |
| 4 | **Data / forms / types extractor** | Data-fetching library + canonical query/mutation patterns, form library + validation, shared domain TypeScript interfaces captured verbatim | Feature dirs + shared type dirs |

Add a fifth only if the user supplied a Figma link:

| 5 | **Figma extractor** | Tokens via `get_design_context`, screenshots via `get_screenshot` | Figma `fileKey` + `nodeId` |

### Extractor prompt template

```
You are extracting [SCOPE] from <repo-name> to inform a design-matching prototype.

Recon findings (where things live): <paste prototypes/_design-system/<app>/.extraction/_recon.md>
Your assigned locations: <paste the specific paths for this bundle>
User-provided files: <list paths in .pipeline/inputs/>

Your job: find EVERY distinct [SCOPE] value/pattern in your assigned locations. Your
bundle is scoped so you can be exhaustive — do not sample, do not stop at the first
few. For each finding, cite file:line.

Quality bar:
- Report an evidence count per pattern (how many distinct occurrences you observed)
- Do NOT speculate or fill gaps with conventions you "expect" — report only what you cite
- Single-occurrence patterns go in a separate section, not the main list
- Capture exact values verbatim. Do not round, normalize, or tidy. "#F9F9F5" not "off-white"

Write your findings to: prototypes/_design-system/<app>/.extraction/<bundle-name>.md

Format:

## [Scope] Findings

### [Pattern/Token Name]
- **Value:** [exact, verbatim]
- **Evidence count:** [N occurrences]
- **Source locations:** path/to/file.tsx:42-48, path/to/other.tsx:103-110, ...
- **Observed usage:** [brief]

## Single-Instance Findings (Below Threshold)
[Same format]

## Notes / Anomalies
[Inconsistencies, deprecated-looking code, competing patterns, migrations in flight]

Report back only: the file you wrote, a count of patterns found per category, and any
anomaly you think the auditor must not miss.
```

Note the change from earlier versions: extractors **write to disk** and report a summary. The auditor reads the files by path. This keeps a 10k-token findings dump out of the orchestrator's context in both directions — and it is why these must be `general-purpose`, not `Explore`.

---

## Step 1A.2: Auditor (sequential, after extractors finish)

Spawn **one** auditor (`general-purpose`):

```
You are the design-system auditor for <app>. Your stance is adversarial — default to
skeptical, demand citations.

Read all extractor findings:
- prototypes/_design-system/<app>/.extraction/*.md
- Recon map: prototypes/_design-system/<app>/.extraction/_recon.md

Before you begin, confirm you read every file: list the filenames and the pattern count
in each. If any expected bundle is missing, say so and stop.

Your job:
1. Evidence threshold: "Established" = >=3 distinct source locations. "Probable" = 2.
   "Single instance" = 1. Apply this strictly — an extractor claiming a pattern is
   common without 3 citations does not clear the bar.
2. Cross-check the off-token sweeper against the token extractor. Where a raw value is
   used inline that duplicates a named token, flag it — this reveals which tokens are
   real conventions vs. aspirational.
3. Detect contradictions across bundles (including Figma vs. code disagreements).
4. Flag dead code, deprecated patterns, one-off experiments.
5. Identify GAPS: what would a prototype likely need that no extractor found?
6. Spot-verify: pick the 5 highest-impact claims and re-read the cited file:line yourself
   to confirm the citation is real and says what the extractor claimed.

Write to: prototypes/_design-system/<app>/.extraction/_audit.md

Format:

## Established Patterns (Use Freely)
[>=3 occurrences. Name, exact value, evidence count, top 3 citations.]

## Probable Patterns (Flag for User Confirmation)
## Single Instances (Do Not Use Without Approval)
## Token vs. Inline Conflicts
## Contradictions Detected
## Gaps (Likely Needed But Not Found)
## Spot-Verification Results
[The 5 claims you re-checked and whether each held up]
## Open Questions for User

Do NOT rubber-stamp. "Insufficient evidence" beats guessing.
Report back: counts per category + any failed spot-verification.
```

---

## Step 1A.3: Synthesizer

Spawn one synthesizer (`general-purpose`):

```
You are writing the app-wide design system for <app>. This is the SINGLE SOURCE OF TRUTH
for every prototype targeting this app — it will be read by every future run and updated
incrementally rather than regenerated. Write it to last.

Read: prototypes/_design-system/<app>/.extraction/_audit.md
Also read (for anything the audit references): the extraction bundle files in the same dir.

Before writing anything, confirm your reads: state the count of Established patterns the
audit lists, and quote one exact token value with its citation. If the audit file is
missing or empty, STOP and report that — do not synthesize from assumption.

Write to: prototypes/_design-system/<app>/design-system.md

Schema:

# Design System — <app>
*Single source of truth. Created [date]. Read by every prototype targeting this app.*
*Last freshness check: [date] | Schema version: 1*

## Tech Stack
- Framework: [exact, from package.json — this determines the prototype's framework]
- Styling: [approach from recon]
- Component library: [kit + custom wrappers]
- Icon library:
- Data layer: [library + version + mock approach]
- Form library:
- Evidence: [<=3 bullet citations]

## Visual Identity
[3 sentences on what the app looks and feels like. Concrete and sensory — colors,
density, shape language, chrome. This gives implementers the gestalt before tokens.]

Key structural patterns (cite each):
1. [Header treatment — path]
2. [Page layout wrapper — path]
3. [Table/data display conventions incl. row height — path]
4. [Button shape language — path]
5. [Any dominant grid/list pattern — path]

## Common Mistakes To Avoid
[DERIVE THESE FROM THIS APP'S ACTUAL CONVENTIONS. Do not copy them from another app.
Each entry must name a real, citable convention of THIS codebase that a prototype could
plausibly get wrong. Seed from: the auditor's "Token vs. Inline Conflicts" section, the
"Contradictions" section, and any anomaly where the obvious guess would be wrong.
Format each as: "Do NOT <mistake> — <this app's actual convention> (<citation>)".
Later runs append to this section from fidelity-review findings.]

## Font Handling
Production font: [name]
Availability: [licensed / Google Fonts / self-hosted]
Prototype fallback: [exact fallback + how it loads]
[If the production font is unavailable, name the specific fallback. Never allow a
generic sans-serif substitution.]

## Color Tokens
| Token | Value | Status | Usage | Source |
|---|---|---|---|---|
[Preserve the app's own nesting/grouping structure exactly as production names it.]

## Typography
[Scale with exact fontSize / fontWeight / lineHeight / letterSpacing per token.
Document the app's application mechanism explicitly — e.g. sx spread vs. variants.]

## Spacing Scale
## Reusable Style Objects
[Complete code, verbatim, with citations]
## Components
| Component | Status | Variants | Location | Notes |
|---|---|---|---|---|
## Data Layer
[Library, canonical query pattern with snippet + citation, mock fetcher shape,
loading/error conventions]
## Forms
## Type Interfaces (Reuse As-Is)
| Interface | Source | Notes |
|---|---|---|
## Routes
## Open Items Requiring User Decision

## Promotion Log
*Feature findings graduated into this file. Appended at Gate 1 of each run.*
| Date | From feature | What was promoted | Evidence |
|---|---|---|---|

---

Rules:
- Every value verbatim from the audit. Do not round or normalize.
- Every Established entry carries its citation.
- Mark Probable and Single-instance entries with their status — do not silently promote.
- Populate "Common Mistakes To Avoid" from THIS app's evidence only. An empty section
  with a note is correct if the audit surfaced no such traps; fabricated entries are not.
```

---

## 🛑 Gate 1A: User reviews the app-wide design system

**First run for an app only.** Present:

- Path to the file
- Established / Probable / Single-instance counts
- Contradictions and how they were resolved
- Gaps the auditor flagged
- Failed spot-verifications, if any
- The generated "Common Mistakes To Avoid" list — confirm these match the user's understanding of the app
- Batched open questions

Wait for resolution. Update the file. Re-confirm before Stage 1B.

On subsequent runs where the freshness check passes, this gate does not fire.

---

## Freshness check (warm path — not cold start)

When `design-system.md` already exists, do **not** run this file. Dispatch one `Explore` subagent with **`model: claude-5-5-sonnet`** (read-only — it returns its table, it does not write). Tiering is safe here and only here in this file: the check diffs against a known baseline and every citation it returns is grep-verifiable.

```
Spot-check these design-system claims against current production code in <repo-name>.
For each, report MATCH or DIVERGED with the current value and citation.

<paste 8-12 highest-impact claims: framework version, primary background, primary text
color, header treatment, base font, table row height, primary button radius, data
library version>

Also confirm the starter template's token files still match:
compare prototypes/_design-system/<app>/starter/src/theme/* against production.

Return a table: Claim | Expected | Actual | MATCH/DIVERGED | Citation
```

- All MATCH → reuse as-is, proceed to Stage 1B.
- Any DIVERGED → surface the drift to the user with both values. Ask: patch the specific tokens, or re-run full extraction? Patch is almost always right; full re-extraction reintroduces the cross-run variance this cache exists to prevent.
- Starter token drift → patch the starter too, so the fix benefits every future run.
