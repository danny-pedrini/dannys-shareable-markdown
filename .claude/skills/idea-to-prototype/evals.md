# Evals: idea-to-prototype

## The Allowlist (read this before running any eval)

As of skill v5.0 the design system is **two files**, and the permitted-value allowlist is their **union**:

```
ALLOWLIST = prototypes/_design-system/<app>/design-system.md    # app-wide source of truth
          ∪ prototypes/<feature>/design-brief.md                # feature-local additions
```

G1, G2, G5, and G6 all resolve values against this union. Checking only the brief would flag every production token as invented; checking only the app-wide file would flag every approved feature-local pattern.

**Resolving `<app>`:** read the app-wide path from the header of the v5.0 brief (it states the source-of-truth path by schema requirement). If that line is absent, fall back to the single `_design-system/*/` directory whose name matches the target app in the invocation log's `input_summary`.

### Allowlist resolution algorithm

**Do not detect the v5.0 model by filename.** Two prototypes predating v5.0 already have a file named `design-brief.md` with a different schema — [fulfillment-queues-v3](../../../prototypes/fulfillment-queues-v3/design-brief.md) and [fulfillment-queues-v4](../../../prototypes/fulfillment-queues-v4/design-brief.md). Keying on existence alone misroutes them.

Detect by **schema marker**, and never rely on a single file being self-contained:

1. **Is this a v5.0 brief?** A `design-brief.md` qualifies only if it contains the source-of-truth pointer line (matching `App-wide source of truth:` or `_design-system/`). If yes → allowlist = app-wide `design-system.md` **∪** `design-brief.md`.
2. **Otherwise**, collect every candidate that exists: `prototypes/<feature>/design-system.md`, any non-conforming `design-brief.md`, and the app-wide `design-system.md`.
3. **Test each candidate for self-containment** — does it actually contain a color-token table (a `## Color Tokens` heading or ≥10 distinct hex values)? Some pre-v5.0 files are thin pointers, not copies: [package-weight-capture-solution-a/design-system.md](../../../prototypes/package-weight-capture-solution-a/design-system.md) is 117 lines and opens *"Inherits from app-wide beyondRx design system"* — it has Tech Stack and Visual Identity but no token tables.
4. **Union everything that exists.** A pointer-style file unions with the app-wide file it points at. Never evaluate against a pointer file alone — it has no token tables, so G1 would flag every legitimate production color as invented.
5. If no candidate contains a color-token table → **Fail** the eval as a missing prerequisite, and say which files were found and what each lacked. Do not silently pass an empty allowlist.

**Rule of thumb: unioning too much risks a false PASS on one token; unioning too little guarantees false FAILs on dozens.** Prefer the wider union and report which file each matched value came from (G1 step 7).

This keeps all 7 pre-v5.0 prototype copies and the 2 legacy `design-brief.md` prototypes evaluable without modification.

## Verification Model

Evals use a **two-layer verification** approach:

1. **Eval Runner (Step 4.5):** Checks prototype artifacts directly — source files, design-system.md, package.json, specs, reviews. Produces Pass/Fail per eval. These are the authoritative results.
2. **Independent Trace Author (Step 4.7):** A separate subagent independently audits the same artifacts and records findings in the trace file's `gate_evidence` section. This provides independent corroboration — if the eval runner and the trace disagree, that's a signal to investigate.

Gate-related evals (G4) check artifacts in the eval runner (Step 4.5) and are independently corroborated by the trace subagent (Step 4.7). The trace's `gate_evidence` section is queryable for trend analysis across runs.

## Active Evals

| ID | Name | Type | Check | Added | Last Result |
|----|------|------|-------|-------|-------------|
| G1 | No invented colors or fonts | Generalization | Code | 2026-06-01 | Pass (2026-11-14, sh-cross-category-opportunities: 2 colors in SHXO-added lines, `#7a5cff` and `#c5381a`, plus `var(--ai-violet)` and `var(--border-secondary)` from the approved verbatim `ntspin` spinner; all in the union allowlist; only font-family is `inherit`. No src/: scanned lines added to index.html vs the pin) |
| G2 | Correct framework match | Generalization | Code | 2026-06-01 | Pass (2026-11-14, sh-cross-category-opportunities: scoped to matches [product designer]'s file. Tech Stack is vanilla HTML/CSS/JS with no package.json; prototype has no package.json and no script src, link, import, React or jQuery in added lines) |
| G3 | All states implemented | Generalization | Code | 2026-06-01 | Pass (2026-11-14, sh-cross-category-opportunities: `SHXO.parseState(location.search)` reads loading, error, empty; empty omits the tile, loading and error drive composer states; integrator verified each renders) |
| G4 | Spec audit verdicts all pass | Generalization | Code | 2026-06-01 | Pass (2026-11-14, sh-cross-category-opportunities: latest audit per spec is `NN-spec-audit-v6.md`, all 4 PASS; `_cross-spec-audit-v4.md` PASS) |
| G5 | No reinvented base components | Generalization | Code | 2026-06-01 | Pass (2026-11-14, sh-cross-category-opportunities: scoped to matches [product designer]'s file. Added code calls [product designer]'s `tile`, `tbs`, `esc`, `q`, `I` through the hook; redefines none. A local `fact` object constructor inside the SHXO IIFE shares a name with [product designer]'s `fact()` in a different scope and is not a component) |
| G6 | Data layer matches production | Generalization | Code | 2026-06-01 | Pass (2026-11-14, sh-cross-category-opportunities: scoped to matches [product designer]'s file. Mock data is hard-coded JS literals and patient switching uses `dp-patient`, as in the pin; zero fetch, XMLHttpRequest, Math.random, Date.now or new Date in added lines) |
| G7 | All active evals scored | Generalization | Code | 2026-06-02 | Pass (2026-11-14, sh-cross-category-opportunities: 7/7) |

_G5 (Evidence threshold enforced) was removed in v4.3 — this failure mode is caught by the Stage 1A Auditor at Gate 1, before the user approves the design system. Running it again at Stage 4 has near-zero true-positive surface since design-system.md doesn't change after Gate 1._

## Definitions

### G1: No invented colors or fonts

**Pass:** Every color value (hex, rgb, rgba, hsl, hsla) AND every font-family declaration in prototype source files under `prototypes/<feature>/src/` appears in the **allowlist** (see The Allowlist above).
**Fail:** Any color value or font-family in a prototype source file cannot be found in the allowlist.
**Check type:** Code-based (comparison)

**Implementation:**
```check
Type: comparison
Source field: THE ALLOWLIST (union — resolve per "The Allowlist" section at the top of this file):
  - prototypes/_design-system/<app>/design-system.md
  - prototypes/<feature>/design-brief.md
  (resolve per the "Allowlist resolution algorithm" at the top of this file — union all
   existing candidates; never evaluate against a pointer-style file alone)
  Extract all color values (hex #XXX/#XXXXXX/#XXXXXXXX, rgb/rgba, hsl/hsla) AND all font-family values (from Typography, Font Handling, Reusable Style Objects, and any fontFamily references) across ALL allowlist files.
Target field: prototypes/<feature>/src/**/*.tsx, *.ts (excluding node_modules/, .pipeline/) — extract all color values AND font-family declarations
Logic:
  (1) Resolve the allowlist file set. If the app-wide file cannot be resolved and no pre-v5.0 fallback exists = Fail (missing prerequisite).
  (2) Build color allowlist from ALL resolved files combined. Normalize: lowercase, expand 3-digit hex to 6-digit, and strip whitespace inside rgb()/rgba()/hsl() before comparing (whitespace-variant rgba mismatches caused false positives in prior runs). Include standard CSS values that don't need approval: transparent, inherit, currentColor, #000, #fff, #000000, #ffffff, and theme-object references.
  (3) Build font allowlist from ALL resolved files: Font Handling + Typography sections. Include system fallbacks (sans-serif, monospace, inherit).
  (4) Scan prototype source files: grep for hex (#[0-9a-fA-F]{3,8}), rgb/rgba, hsl/hsla AND fontFamily declarations (fontFamily: "...", font-family: "...") in all .tsx/.ts under src/.
  (5) Check membership of each extracted value against the combined allowlists.
  (6) Any unmatched color or font = Fail. Zero unmatched = Pass.
  (7) Report which allowlist file each matched value came from — an approved value found ONLY in design-brief.md that is app-wide in nature (a base token, not feature-specific) indicates a missed promotion at Gate 1. Note it; do not fail for it.
```

**Source:** Derived from failure_modes table ("Invented color/gradient" — CRITICAL, "Font mismatch" — HIGH) and hard constraints. This is the single authoritative check for both color and font fidelity — the Stage 3 Validator item 11 also scans for these but this eval is the bulletproof final verification.
**Added:** 2026-06-01
**Notes:** Colors are the #1 failure mode; fonts are #5. Combined into one eval because the check mechanism is identical (build allowlist from design-system.md, scan source files, flag anything not in the list). Most common color trigger: subagents inventing hover/focus colors. Most common font trigger: using a generic sans-serif instead of the documented fallback.

---

### G2: Correct framework match

**Pass:** The framework dependency in `prototypes/<feature>/package.json` matches the framework documented in the **app-wide** `design-system.md > Tech Stack` section.
**Fail:** The framework in `package.json` does not match, or the Tech Stack section is missing.
**Check type:** Code-based (comparison)

**Implementation:**
```check
Type: comparison
Source field: prototypes/_design-system/<app>/design-system.md — ## Tech Stack > Framework line (extract framework name)
  Tech Stack is app-wide by definition and never lives in design-brief.md. A brief that
  contains a Tech Stack section is a v5.0 schema violation — report it.
  Fallback: if the app-wide file has no Tech Stack section, read it from
  prototypes/<feature>/design-system.md (pre-v5.0 copies and pointer files both carry one)
Target field: prototypes/<feature>/package.json — dependencies + devDependencies keys
Logic:
  (1) Parse the Tech Stack section and extract the framework (e.g., "Next.js 14 with App Router" → "next").
  (2) Parse package.json dependencies and devDependencies.
  (3) If design-system.md says Next.js → "next" must be in dependencies AND "vite" must NOT be in dependencies/devDependencies.
  (4) If design-system.md says Vite → "vite" must be in devDependencies AND "next" must NOT be.
  (5) Mismatch or missing Tech Stack section = Fail.
```

**Source:** Derived from failure_modes table ("Wrong framework" — HIGH) and hard constraint ("Match the existing app's framework")
**Added:** 2026-06-01
**Notes:** A framework mismatch means the entire scaffold is wrong and engineers can't reuse any of it. Trivial to check, catastrophic when wrong, zero false positives. The Stage 1A Synthesizer and Stage 3 Scaffolder should prevent this, but this eval catches it if both miss.

---

### G3: All states implemented

**Pass:** Every page-level component implements URL-param state simulation for at least `loading`, `error`, and `empty` states (via `useSearchParams` or equivalent reading of `?loading=true`, `?error=true`, `?empty=true`).
**Fail:** Any page-level component does not reference at least these three URL param state toggles.
**Check type:** Code-based (presence)

**Implementation:**
```check
Type: presence
Source field: prototypes/<feature>/tasks/_traceability.md — ## Pages / Screens table (extract page component file paths)
Target field: Each page component file listed in the traceability matrix
Logic:
  (1) Parse _traceability.md to identify all page-level components and their file paths.
  (2) For each page component file, verify TWO conditions:
      (a) The file imports useSearchParams (or Next.js equivalent like searchParams prop) — confirms URL-param wiring exists, not just string mentions.
      (b) The file contains conditional JSX branches keyed on each of the three params: searchParams.get('loading'), searchParams.get('error'), searchParams.get('empty') (or equivalent patterns like searchParams.has(), destructured params, or URLSearchParams). The branch must influence rendered output — a variable assignment alone is insufficient.
  (3) Each page must satisfy both conditions for all three state params. A page missing the import OR missing a conditional branch for any param = Fail.
  (4) If _traceability.md is missing or has no Pages table = Fail (prerequisite artifact missing).
```

**Source:** Derived from hard constraint ("NEVER ship a screen with only the happy path — every screen needs default / empty / loading / error / ≥1 edge") and the second prime directive ("State coverage as handoff contract")
**Added:** 2026-06-01
**Notes:** State coverage is one of the two prime directives. Engineers use these URL params to exercise every state without code changes — if they're missing, the prototype fails as a handoff artifact. The Stage 3 Validator item 8 checks this per-component, but this eval verifies page-level coverage across the entire prototype.

---

### G4: Spec audit verdicts all pass

**Pass:** For every spec file in `prototypes/<feature>/tasks/` (excluding `_traceability.md`), a corresponding audit file in `prototypes/<feature>/.pipeline/reviews/` exists whose **latest** version contains "Verdict: PASS" — AND `_cross-spec-audit.md` exists with a final verdict of "Verdict: PASS".
**Fail:** Any spec lacks an audit, any spec's latest audit verdict is "FAIL", or the cross-spec audit is missing or FAIL.
**Check type:** Code-based (structural)

**Implementation:**
```check
Type: structural
Source field: prototypes/<feature>/tasks/*.md (excluding _traceability.md) — list and count spec files
Target field: prototypes/<feature>/.pipeline/reviews/*-spec-audit.md — list, count, and check verdicts
Logic:
  (1) List all .md files in tasks/ excluding _traceability.md. Count = spec_count.
  (2) For each spec NN, glob ALL its audit files: `NN-spec-audit*.md`. Do NOT assume a
      single revision-suffix convention — real runs on disk use at least two:
      `NN-spec-audit-v2.md` (non-rx-combo-pack) and `NN-spec-audit-r2.md` /
      `NN-spec-audit-r3.md` (non-rx-bulk-pack). Matching only one convention silently
      takes a superseded round-1 FAIL as authoritative and produces a false Fail.
  (3) Determine the AUTHORITATIVE audit per spec: extract any trailing integer from the
      suffix (v2→2, r3→3, no suffix→1) and take the highest. If two files tie, take the
      most recently modified. Record which file you treated as authoritative.
  (4) If any spec has no matching audit file at all = Fail (missing audit).
  (5) If any spec's authoritative verdict is "FAIL" = Fail. A round-1 FAIL superseded by a
      later PASS is the expected fix-loop shape, not a gate violation.
  (6) Cross-spec audit: glob `_cross-spec-audit*.md` and apply the same
      highest-revision rule. Missing = Fail. Authoritative verdict "FAIL" = Fail. This is
      the check covering the failure mode both prior production runs actually hit.
      Pre-v5.1 prototypes have no cross-spec audit — for those, skip step (6) and note it
      rather than failing, since the mechanism did not exist when they were built.
  (7) All specs PASS on their authoritative audit AND cross-spec PASS (or legitimately
      absent per step 6) = Pass.
```

**Source:** Derived from failure_modes table ("Premature implementation" — HIGH) and Gate 2 enforcement ("Implementation cannot start until every spec has a PASS verdict")
**Added:** 2026-06-01
**Notes:** Gate 2 is foundational — if specs don't all pass audit, every downstream artifact (implementation, composition, fidelity) is built on shaky ground. The trace subagent independently corroborates this in `gate_evidence.gate_2_specs`. If this eval and the trace disagree, investigate.

---

### G5: No reinvented base components

**Pass:** No prototype source file defines a new component (via `export function`, `export const`, or `export default function`) with the same name as a component listed as available in the **allowlist's** Components tables.
**Fail:** Any prototype source file exports a component whose name matches an available allowlist component.
**Check type:** Code-based (absence)

**Implementation:**
```check
Type: absence
Source field: THE ALLOWLIST — ## Components tables from BOTH:
  - prototypes/_design-system/<app>/design-system.md  (base components)
  - prototypes/<feature>/design-brief.md              (feature-local component patterns, if any)
  (pre-v5.0 fallback: prototypes/<feature>/design-system.md alone)
  Extract component names with Established status.
Target field: prototypes/<feature>/src/**/*.tsx — component export definitions
Logic:
  (1) Parse the Components table(s) across all allowlist files. Extract all component names with Established status (e.g., Button, Input, Select, Dialog, Table, Chip, Badge).
  (2) In prototype source files, grep for patterns: "export function <Name>", "export const <Name>", "export default function <Name>" where <Name> matches a component from step (1).
  (3) Exclude files that are clearly re-exporting or thin-wrapping the library component (file imports the component from the design system path and re-exports with minor prop defaults).
  (4) Any non-wrapper match = Fail. The prototype should import these from the existing library, not redefine them.
```

**Source:** Derived from failure_modes table ("Reinvented base component" — HIGH) and hard constraint ("Reuse the existing app's base components by their exact prop interfaces — do NOT reinvent base components the existing UI library already provides")
**Added:** 2026-06-01
**Notes:** Reinvented base components mean engineers must throw away the prototype's version and rewire to the real library. The Stage 3 Validator item 4 checks for raw HTML elements (`<button>`, `<input>`), but this eval catches the subtler case where a component with the right name is defined locally instead of imported.

---

### G6: Data layer matches production

**Pass:** Prototype component files use the data-fetching library documented in the **app-wide** `design-system.md > Data Layer` (e.g., `useQuery` from TanStack Query) for mock data. No `useState` holds data typed as an API response interface from either allowlist file's Type Interfaces.
**Fail:** Any prototype component file uses `useState` to hold mock data matching an API response interface, OR the documented data-fetching library has zero imports across prototype source files.
**Check type:** Code-based (absence)

**Implementation:**
```check
Type: absence
Source field:
  - Library: prototypes/_design-system/<app>/design-system.md — ## Data Layer (app-wide by definition)
  - Interfaces: ## Type Interfaces from BOTH the app-wide design-system.md AND
    prototypes/<feature>/design-brief.md (## Feature-Local Type Interfaces)
  (pre-v5.0 fallback: prototypes/<feature>/design-system.md alone)
Target field: prototypes/<feature>/src/**/*.tsx — useState calls and data-fetching library imports
Logic:
  (1) Extract the data-fetching library name from the app-wide Data Layer section (e.g., "TanStack Query" → useQuery).
  (2) Extract all TypeScript interface names from the Type Interfaces tables across BOTH allowlist files (these represent API response shapes).
  (3) Grep prototype source files for useState calls. For each, check if the type parameter or initial value references any interface name from step (2). Match patterns: useState<InterfaceName>, useState(mockData as InterfaceName), or useState with a variable whose type is an API response interface.
  (4) If any useState holds data typed as an API response interface = Fail.
  (5) Additionally: if the Data Layer section specifies a library but zero imports of that library (e.g., useQuery, useMutation) exist across prototype source files = Fail.
```

**Source:** Derived from failure_modes table ("Raw useState for server-fetched data" — HIGH) and hard constraint ("Match the existing app's data layer — do NOT substitute raw React state for data that would be server-fetched in production")
**Added:** 2026-06-01
**Notes:** The whole point of matching the production data layer is that engineers can swap mock fetchers for real API calls with zero component changes. Raw useState breaks this contract entirely. The Stage 3 Validator item 5 catches this per-component, but this eval verifies the pattern holds across the entire prototype.

---

### G7: All active evals scored

**Pass:** The eval runner (Step 4.5) produced a result (Pass or Fail) for every eval ID listed in the Active Evals table above. The count of scored evals equals the count of active evals.
**Fail:** Any active eval ID is missing from the eval results, or the scored count is less than the active count.
**Check type:** Code-based (structural)

**Implementation:**
```check
Type: structural
Source field: .claude/skills/idea-to-prototype/evals.md — Active Evals table (extract all eval IDs: G1, G2, ... GN)
Target field: The eval_results array produced by Step 4.5 this run
Logic:
  (1) Parse the Active Evals table. Extract all IDs from the ID column. Count = active_count.
  (2) Count the eval_results entries produced by this run = scored_count.
  (3) If scored_count < active_count = Fail. List which eval IDs were not scored.
  (4) If scored_count == active_count and every active ID appears in results = Pass.
```

**Source:** Cross-pollinated from feature-impact-sizing G10. Catches the failure mode where an eval is added to evals.md but the runner doesn't score it (e.g., added mid-session and the runner only scored the old set).
**Added:** 2026-06-02
**Notes:** This is a meta-eval — it verifies the eval system itself is working. Should always be the last eval in the table (scored after all others). If this fails, the invocation log's eval_results array is incomplete and trend queries will undercount failures.
