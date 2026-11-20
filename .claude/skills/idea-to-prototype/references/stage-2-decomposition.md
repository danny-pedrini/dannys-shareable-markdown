# Stage 2 — Idea Decomposition

Produces `tasks/_traceability.md` and one spec per component in `tasks/`. Read `context-contract.md` first if you have not this run.

**Context rule for this stage:** the design brief is PASTED into every dispatch (it is small and it is framing). The app-wide design system is PATHED. Specs themselves are always pasted in full to their auditor.

---

## The failure mode this stage is built around

Both logged production runs failed Stage 2 the same way, and it was not per-spec quality:

- `non-rx-combo-pack`: *"All 8 specs FAILED round-1 adversarial audit on **cross-spec seam conflicts**; 18 resolutions + 4 paired fix editors + 4 re-audit verifiers → 8/8 PASS."*
- `non-rx-bulk-pack`: *"3 rounds of spec audit fix-loops (**contract drift across parallel writers**, resolved by declaring spec 01 single contract authority)."*

Eight for eight, on conflicts *between* specs. Parallel spec writers each produce a locally-correct spec and collectively produce an inconsistent set — and isolated per-spec auditors structurally cannot see it. The cost is not the audit; it is the multi-round fix-loop afterward.

Stage 2 therefore attacks this twice:

1. **Preventively** — Step 2.1 designates a **contract authority** so parallel writers share one definition of every cross-cutting type and prop. This is the `non-rx-bulk-pack` fix, applied up front instead of after three rounds.
2. **Detectively** — Step 2.3 runs a dedicated **cross-spec auditor** in parallel with the per-spec auditors, whose only job is seam conflicts.

---

## Step 2.1: Requirements parser

Spawn one parser (`general-purpose`):

```
You are decomposing an idea into a build plan for a front-end prototype.

Idea source: <paste the full idea source — PRD, one-pager, brief, transcript, or bullets>

Design brief (feature framing): <paste the FULL content of prototypes/<feature>/design-brief.md>

App-wide design system (components, types, data layer, routes) — READ BY PATH:
  prototypes/_design-system/<app>/design-system.md

Before producing your output, quote from the app-wide file: the framework line, and the
names of 3 components from the Components table that this feature will likely reuse. If
you cannot find the Components table, stop and report that.

Your job:
1. Extract every UI requirement: screens, components, user flows, states, edge cases.
2. Produce a numbered R# list with binary-testable acceptance criteria.
3. Build a requirement-to-component traceability matrix.
4. For each component, decide: reuse an existing app component (name it from the app-wide
   Components table), or build new? Default to reuse. A new component needs justification.
5. Identify missing/ambiguous requirements.
6. **Designate the CONTRACT AUTHORITY.** Parallel spec writers drift on shared types and
   props — in a prior run this cost three rounds of fix-loops. Prevent it: pick the ONE
   spec that will own the canonical definition of every cross-cutting type, prop name, and
   shared interface, and enumerate exactly what it owns. Every other spec must reference
   those definitions rather than restating them. Choose the spec closest to the data source
   (usually the mock-data/hooks spec or the primary page spec).

   **Scope boundary — what the authority does NOT own.** Types that already exist app-wide
   belong to the app-wide design system's `## Type Interfaces` section and are referenced
   from there, not re-owned here. The contract authority owns only types and props that are
   *new to this feature* and used by more than one spec. A type has exactly one home: check
   the app-wide file first, and if it exists there, cite it rather than listing it as owned.

Write to: prototypes/<feature>/tasks/_traceability.md

Schema:

# Traceability Matrix — <feature>

## Requirements (R# List)
| ID | Requirement | AC (binary, testable) | Component(s) | Notes |
|---|---|---|---|---|

## Components Identified
| Component | Description | Reuse or New | If reuse: source | Source Requirements |
|---|---|---|---|---|

## Pages / Screens
| Page | Route | Components | File path |
|---|---|---|---|
[The Pages table is read by eval G3 — every page listed here must implement URL-param
state simulation. Give exact intended file paths.]

## Contract Authority
**Authoritative spec:** <NN>-<slug>.md
**Rationale:** [why this spec owns the contract]

It owns the canonical definition of:
| Item | Kind | Consumed by specs |
|---|---|---|
| [e.g. PackageWeightRow] | shared interface | 02, 03, 05 |
| [e.g. shipmentId: string] | cross-cutting prop | 02, 04, 06 |
| [e.g. useWeightQueue()] | shared hook signature | 03, 05 |

Every other spec REFERENCES these by name and must not restate or redefine them.

## Open Questions
## Out of Scope

Report back: R# count, component count (new vs. reuse), page count, and which spec is the
contract authority with the item count it owns.
```

---

## Step 2.2: Spec writers (parallel, one per new component, `general-purpose`)

Only new components need specs. Reused components are handled by the integrator.

```
You are writing a build spec for ONE component: <component-name>.

Traceability row: <paste the row>
Requirements this component satisfies: <paste the relevant R# rows in full>
Design brief: <paste the FULL content of design-brief.md>
Reference materials: <screenshot paths, Figma node IDs>

CONTRACT AUTHORITY: <paste the full Contract Authority section from _traceability.md>
<If this spec IS the contract authority:>
  You OWN the canonical definitions listed above. Define each one explicitly and completely
  — other specs will reference your definitions. Be exact about types and prop names.
<If this spec is NOT the contract authority:>
  You MUST reference the authority's definitions by name and MUST NOT restate, rename, or
  redefine them. Writing `shipmentId: number` when the authority says `shipmentId: string`
  is the single most common Stage 2 failure. If you need something cross-cutting that the
  authority does not define, do NOT invent it — list it under Open Questions as a needed
  contract addition.

App-wide design system — READ BY PATH:
  prototypes/_design-system/<app>/design-system.md
Consult it for: exact token names, the Components table, Type Interfaces, Data Layer
pattern, Forms pattern.

Before writing the spec, quote from the app-wide file: the exact type interface you will
reuse for this component's data (name + source), and the exact name of the base component
you will build on. If neither exists for this component, say so explicitly.

Write to: prototypes/<feature>/tasks/<NN>-<component-slug>.md

Schema:

# <Component Name>

## Purpose
[One sentence.]

## Requirement Traceability
- [R#] [requirement + AC]

## Visual Reference & Inspiration
[Which ranked inspiration source from design-brief.md this draws from, with the specific
file:line of the production component to model on, and the screenshot path. Be concrete
about structure: which wrapper, which table primitive, which layout.]

## Props / Inputs
| Prop | Type | Required | Default | Description |
|---|---|---|---|---|

## States
- Default
- Loading [skeleton or spinner — say which, per the app's convention]
- Empty (zero results)
- Error (fetch failure with retry)
- [Any others from requirements]

## Behavior
[Numbered interactions.]

## Design System References
[Every app-wide token/component/type this depends on, BY NAME with the section it lives
in. Do not paste values — name them so the implementer looks them up. If something needed
is absent from both the app-wide file and the brief, list it under Required Additions.]

### Required Additions
[Anything not in the allowlist. Each needs user approval before implementation.]

## Mock Data
- Shape: MUST reuse a TypeScript interface from the app-wide Type Interfaces section — cite it by name
- Fetcher: MUST use the app-wide Data Layer pattern
- State simulation: URL params ?loading=true, ?error=true, ?empty=true

## Acceptance Criteria
- [ ] [Specific, binary, testable — one per line]

## Edge Cases
[Empty list? 1000 rows? Long strings? Truncation? Concurrent updates?]

## Open Questions

Report back: AC count, Required Additions count (0 is the goal), and the interface you
are reusing for mock data.
```

---

## Step 2.3: Spec auditors + cross-spec auditor (all parallel, independent of writers)

Dispatch all of the following in a SINGLE message, all `general-purpose` (each writes its audit file to disk — `Explore` cannot). Auditors are always different invocations from writers — a subagent never audits a spec it wrote. Independence holds regardless of how specs are grouped: an auditor that wrote none of the specs it reviews is independent of all of them.

### Who audits what

| Spec profile | Assignment |
|---|---|
| The contract authority spec | **Dedicated auditor**, always — everything else depends on it |
| ≥8 AC, or ≥150 lines, or page-level, or has Required Additions | **Dedicated auditor** |
| Everything else (stubs, placeholders, simple buttons, fixtures) | **One batched auditor** for the group |

Plus, unconditionally, **one cross-spec auditor** — a dedicated agent that reads ALL specs and whose only job is seam conflicts.

Spec size varies about tenfold in practice (28 to 387 lines measured), so a dedicated adversarial auditor per placeholder is waste while a shared one for a 387-line spec is negligent. Batching the low-risk group pays for the cross-spec agent — which is the one that catches what actually broke both prior runs.

### Per-spec auditor prompt (dedicated or batched)

For a batched auditor, paste each assigned spec in full and clearly delimited, and have it write one audit file per spec, each ending with its own verdict line.

```
You are auditing ONE component spec. Your stance is adversarial — default to FAIL.

Spec: <paste the FULL spec content>
Design brief: <paste the FULL content of design-brief.md>
Requirements: <paste the relevant R# rows>

App-wide design system — READ BY PATH:
  prototypes/_design-system/<app>/design-system.md

Before auditing, quote from the app-wide file the exact value or signature of two things
the spec claims to reuse. If a claimed reference does not exist there, that is an
automatic FAIL and you should say which.

Audit checklist — cite specific spec lines for every finding:
1. Ambiguity: any AC interpretable two ways?
2. Allowlist fidelity: every token/component/type named in the spec — does it exist in the
   app-wide file or the brief? Verify by lookup, not assumption.
3. Requirement coverage: does the spec satisfy every R# it claims?
4. Acceptance criteria: each one binary and testable?
5. Edge cases: empty / error / loading / long-content considered?
6. Mock data: shape concrete enough to implement? Reuses a real interface?
7. Internal consistency: props, states, and behaviors agree?
8. Inspiration specificity: does "Visual Reference" name a concrete production file to
   model on, or is it vague? Vague is a FAIL — implementers need a target.
9. Contract compliance: if this spec is NOT the contract authority, does it reference the
   authority's shared types/props by name without restating or redefining them? Any
   redefinition of a contract item = FAIL. If it IS the authority, is every item it owns
   defined explicitly and completely?

Write to: prototypes/<feature>/.pipeline/reviews/<NN>-spec-audit.md
End the file with exactly one line: "Verdict: PASS" or "Verdict: FAIL"

A PASS requires all checks passed and zero Critical/High findings.
```

### Cross-spec auditor prompt

This agent exists because both prior production runs failed on conflicts *between* specs that every isolated per-spec auditor passed. Give it the whole set.

```
You are the cross-spec auditor. You did not write any of these specs. Your ONLY job is
conflicts BETWEEN specs — do not re-audit any spec's internal quality; dedicated auditors
are doing that in parallel.

All specs: <paste EVERY spec in full, clearly delimited by filename>
Traceability matrix: <paste _traceability.md in full, including the Contract Authority section>
Design brief: <paste FULL content of design-brief.md>

App-wide design system — READ BY PATH:
  prototypes/_design-system/<app>/design-system.md

Before auditing, do both:
1. List every spec filename you received and the contract-authority spec named in the
   traceability matrix. If any spec in the matrix is missing from what you received, stop
   and say which.
2. PROOF OF READ on the app-wide file — quote the exact name and signature of one shared
   type interface from its `## Type Interfaces` section. You need this to tell a genuine
   contract violation (two specs disagreeing about a feature-local type) from a false
   positive (two specs correctly using the same app-wide type). If you cannot find that
   section, say so and treat app-wide type claims as unverified.

Find every one of these:

1. **Contract violations** — any spec that restates, renames, or redefines an item the
   contract authority owns. Quote both definitions side by side. This is the highest-value
   finding you can produce.
2. **Type disagreements** — the same named field, prop, or interface typed differently in
   two specs (e.g. `shipmentId: string` vs `shipmentId: number`).
3. **Naming drift** — the same concept under two names (OrderTable vs. OrdersTable,
   packageWeight vs. weightValue).
4. **Duplicated responsibility** — two specs claiming to own the same behavior, state, or
   rendering concern. Say which should own it.
5. **Seam gaps** — component A's spec assumes a prop, callback, or event that no other
   spec provides; or a page's specs collectively fail to satisfy that page's requirements.
6. **State-simulation divergence** — pages implementing the URL-param state contract
   differently from one another.
7. **Shared-interface inconsistency** — the same app-wide type interface used with
   different field expectations across specs.

Write to: prototypes/<feature>/.pipeline/reviews/_cross-spec-audit.md

For every finding: severity (Critical/High/Medium), the specs involved, both quoted texts,
and a concrete resolution naming which spec changes and how.

End the file with exactly one line: "Verdict: PASS" or "Verdict: FAIL"
FAIL on any Critical/High finding. A clean set is genuinely possible when the contract
authority did its job — do not manufacture findings, but do not rubber-stamp either.
```

**Resolving cross-spec findings.** Fix at the source: apply the resolution to the specs named, with the contract authority's definition winning any tie. Then re-audit the changed specs with fresh invocations (`-v2`), and re-run the cross-spec auditor once. If a second cross-spec pass still FAILs, escalate to the user rather than looping — repeated seam failures mean the decomposition itself is wrong, not the specs.

---

## Step 2.4: Question synthesizer

Dispatch with **`model: claude-5-5-haiku`** — this agent originates no judgment, it only consolidates.

Consolidate all open questions from the specs, their per-spec audits, and the cross-spec audit into one file: `prototypes/<feature>/.pipeline/reviews/_gate-2-questions.md`. Group by what the answer unblocks. Surface any requested **contract addition** (a spec needing a cross-cutting item the authority does not define) as its own group — those block the most downstream work.

---

## 🛑 Gate 2: User answers questions, approves the spec set

Present the consolidated questions plus any Required Additions needing approval. Wait for answers.

Re-run any spec that needs updating, then re-audit it with a **fresh** invocation (never the same agent that wrote the revision). Name revised audits `<NN>-spec-audit-v2.md`.

**Implementation cannot start until every spec has a PASS verdict AND the cross-spec audit has a PASS verdict.** Eval G4 checks the latest audit file per spec, so an earlier FAIL followed by a v2 PASS is the expected fix-loop shape.
