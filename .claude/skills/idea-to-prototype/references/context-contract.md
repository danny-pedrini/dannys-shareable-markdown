# Context Contract

**Read this once, at Stage 0.** It governs every subagent dispatch in the pipeline. Every other reference file assumes these rules.

---

## Why this file exists

v3.1 of this skill split context across 44 files and produced *worse* prototypes than the single-file v1 — hallucinated gradients, wrong font, wrong framework. Root cause: **context dilution.** Each subagent saw roughly a twelfth of what v1's agents saw.

The lesson recorded in `iteration-notes.md` was "less process, more context per agent." This contract is how we cut token cost **without** re-triggering that failure. The rule is not "send less context." It is:

> **Paste what the subagent must reason *from*. Path what the subagent must look values *up* in.**

Framing content shapes judgment and must be in-context before the agent starts thinking. Lookup content is consulted on demand, when the agent already knows what it needs. Getting this backwards is what broke v3.1.

---

## The two-file design system

There is exactly **one** source of truth for app-wide design facts:

```
prototypes/_design-system/<app>/
├── design-system.md         # SINGLE SOURCE OF TRUTH — app-wide tokens, components, data layer, types
└── starter/                 # Validated runnable scaffold (see stage-3-implementation.md)
```

Each prototype gets a **small feature-local brief**, not a copy:

```
prototypes/<feature>/
├── design-brief.md          # ~60–150 lines. Feature-specific ONLY. Points at the app-wide file.
├── tasks/                   # Specs
└── .pipeline/               # Working artifacts (gitignored)
```

### What lives where

| Content | Location | Why |
|---|---|---|
| Tech stack, framework, styling approach | App-wide | Never varies by feature |
| Color tokens, typography, spacing scales | App-wide | Never varies by feature |
| Reusable style objects, base components | App-wide | Never varies by feature |
| Data layer + form library patterns | App-wide | Never varies by feature |
| Shared domain type interfaces | App-wide | Never varies by feature |
| Visual Identity (gestalt + structural patterns) | App-wide | Never varies by feature |
| Per-app "common mistakes to avoid" | App-wide | Accumulates across runs for that app |
| **Ranked inspiration sources + "build it like this"** | **Brief** | Entirely feature-specific |
| **Feature-local routes and component list** | **Brief** | Entirely feature-specific |
| **Probable / Single-instance findings** | **Brief** | Below promotion threshold — scoped to this prototype only |
| **Conflicts resolved at Gate 1** | **Brief** | Decision record for this run |
| **Screenshot index for this feature** | **Brief** | Feature-specific reference set |

### Why this replaced the full copy

The old model copied the entire app-wide file into every prototype and interleaved feature findings. Measured on disk: `non-rx-combo-pack/design-system.md` was 1,216 lines against an app-wide 655 — roughly 655 duplicated lines per prototype, across 7 prototype copies ranging 117–1,216 lines.

Worse, it stranded app-wide discoveries in per-feature files. Real examples found in that copy, both tagged `[Feature-specific]`:

- `data-grid-styles.ts` — Established, **17 importing files**
- `DialogContext + SetDialogOptions` — Established, **215 call sites**

Neither is feature-specific. Both were re-discovered from scratch by later runs. The **promotion protocol** in `stage-1b-research.md` fixes this: Established feature findings graduate into the app-wide file at Gate 1, so the app-wide file gets richer every run and later features start from more.

### The allowlist is the union

> **The design system allowlist = app-wide `design-system.md` ∪ the prototype's `design-brief.md`.**

Any subagent checking whether a value is permitted must consult both. Every dispatch that involves token compliance must name both paths. `evals.md` G1/G2/G5/G6 are defined against this union.

---

## Dispatch rules

### Always PASTE (framing — needed before reasoning starts)

- The component **spec** being implemented or audited (`tasks/NN-*.md`) — full content, always
- The **`## Contract Authority`** section from `tasks/_traceability.md`, plus the verbatim definitions of every item it owns. Non-authority specs reference shared types by name only, so these definitions are the sole place their real shapes appear — an implementer without them has nothing to resolve the type from
- **Tech Stack** section from app-wide design-system.md (~15 lines)
- **Visual Identity** section from app-wide design-system.md (~20 lines)
- **Common mistakes to avoid** section from app-wide design-system.md (~10 lines)
- The **entire `design-brief.md`** (~60–150 lines) — it is small by design and it is pure framing
- Relevant **R# requirement excerpts** from the traceability matrix
- The **validation or audit report** a retry is responding to
- Any **user answers** from a gate

### Always PATH (lookup — consulted on demand)

- Color token tables (app-wide `## Color Tokens`)
- Typography scale tables (app-wide `## Typography`)
- Spacing scale tables (app-wide `## Spacing Scale`)
- Reusable style objects (app-wide `## Reusable Style Objects`)
- Component inventory table (app-wide `## Components`)
- Type interfaces (app-wide `## Type Interfaces`)
- Data layer and forms pattern detail (app-wide `## Data Layer`, `## Forms`)
- Routes table (app-wide `## Routes`)
- Prior extractor findings (`.pipeline/extraction/*.md`)
- Prior review reports not being directly responded to

### Never send at all

- The full production repo tree (that is what Code Explorer is for)
- Other components' implementations, unless the current component composes them
- Observability schemas to any agent other than the trace author

---

## Proof-of-read requirement

Every dispatch that includes a PATH also includes a **proof-of-read instruction**. This is the guard that keeps path-ification from becoming v3.1-style dilution. The subagent must demonstrate it opened the file before producing its main deliverable.

Template:

```
Before writing any code, open <path> and quote:
1. The exact value + source citation for the single most important token
   you will use (e.g., the page background color).
2. The exact prop signature of the primary base component you will reuse.

If you cannot find either, STOP and report the specific lookup that failed.
Do not proceed on assumption. Do not substitute a value you consider likely.
```

Three properties make this cheap and effective:

1. **Cost is trivial** — two quoted lines, not a summary of the file.
2. **Failure is loud** — a subagent that skipped the read cannot fabricate a citation that survives the validator, which reads the same file.
3. **It is verifiable after the fact** — the quoted values appear in the subagent's response and can be grepped against the source.

If a subagent returns without the proof-of-read block, treat its output as unvalidated and re-dispatch. Do not accept it.

---

## Escape hatch

If a subagent reports that a PATH lookup was insufficient — the section was ambiguous, the value it needed was genuinely absent, the file was malformed — **escalate that section to PASTE for the retry**, and note it at the gate. A recurring escalation for the same section means the boundary above is wrong for that section; fix this file rather than working around it per-run.

Never resolve a failed lookup by guessing a value. That is the failure mode this entire skill exists to prevent.
