# Evals Storage Template

Reference file used by agent-architect when scaffolding `evals.md` for new skills, and by the evals advisor when recording adopted evals. Contains the canonical schema for eval storage. The eval runner step template lives in `references/evals-advisor-step.md`.

---

## evals.md Schema

Each skill with evals enabled gets an `evals.md` file at the skill root. This file is both a registry (quick scan) and a definition store (executable detail).

### File Structure

```markdown
# Evals: [skill-name]

## Active Evals

| ID | Name | Type | Check | Added | Last Result |
|----|------|------|-------|-------|-------------|
| G1 | [name] | Generalization | Code / Judge | YYYY-MM-DD | Pass / Fail / — |

## Definitions

### G1: [Failure mode name]

**Pass:** [Specific binary definition of what a passing output looks like]
**Fail:** [Specific binary definition of what a failing output looks like]
**Check type:** Code-based / LLM judge

**Implementation:**

[For code-based evals:]
```check
Type: comparison | presence | absence | structural | pattern
Source field: [what to extract from — e.g., "source document Dependencies section"]
Target field: [what to check in — e.g., "output Dependencies section"]
Logic: [plain-language description of the check, precise enough to execute with grep/bash]
```

[For LLM judge evals:]
```judge
Criterion: [one-sentence criterion the judge evaluates]
Pass definition: [1-2 sentences]
Fail definition: [1-2 sentences]
Examples: [note — add from your own runs, do not fabricate]
```

**Source:** [How this eval was identified — evals advisor run, manual observation, etc.]
**Added:** [YYYY-MM-DD]
**Notes:** [Any context — when this tends to trigger, known edge cases]
```

### Field Definitions

| Field | Required | Description |
|-------|----------|-------------|
| `ID` | Yes | Sequential ID prefixed by type: `G` for generalization evals (e.g., G1, G2). Specification issues become prompt fixes, not evals. |
| `Name` | Yes | Short descriptive name for the failure mode |
| `Type` | Yes | Always `Generalization` — specification issues are prompt fixes, not evals |
| `Check` | Yes | `Code` (grep, structural, comparison) or `Judge` (LLM assessment) |
| `Added` | Yes | Date the eval was adopted |
| `Last Result` | No | Updated by the eval runner after each run. `Pass` / `Fail` / `—` (not yet run) |
| `Pass` | Yes | Binary definition — what a passing output looks like |
| `Fail` | Yes | Binary definition — what a failing output looks like |
| `Implementation` | Yes | Executable definition using `check` or `judge` code block (see below) |
| `Source` | Yes | How this eval was identified |

### Implementation Block Types

#### Code-based (`check` block)

Used when the failure mode can be caught with structural/textual checks.

| Subtype | When to Use | Example |
|---------|-------------|---------|
| `comparison` | Source content should appear in output | Dependencies in source → Dependencies in output |
| `presence` | Output must contain specific elements | "Every metric has baseline → target format" |
| `absence` | Output must NOT contain specific elements | "No invented thresholds not in source" |
| `structural` | Output must have required sections/format | "All 5 template sections present with content" |
| `pattern` | Output must match a format pattern | "User stories follow US-NNN sequential numbering" |

The eval runner reads the `Logic` field and executes the appropriate bash/grep commands.

#### LLM judge (`judge` block)

Used when the failure mode involves interpretation or nuance code can't capture.

The eval runner spawns a grader subagent with the criterion, pass/fail definitions, and any examples, then collects the verdict. Judge evals that share one input set share one grader (`references/evals-advisor-step.md` Step 1).

**Cost note:** Judge evals consume tokens on every run. Prefer code-based checks when possible.

---

## Eval Runner Step Template

The eval runner step template lives in `references/evals-advisor-step.md` Step 1. Use that copy. It runs BEFORE the observability logging step so eval results can be included in the trace, and it skips silently when no evals exist.

---

## Scaffolding

When agent-architect creates a skill with evals advisor enabled, create:

```
.claude/skills/<skill-name>/evals.md
```

With this initial content:

```markdown
# Evals: [skill-name]

## Active Evals

| ID | Name | Type | Check | Added | Last Result |
|----|------|------|-------|-------|-------------|

_No evals yet. Run the evals advisor after a skill run to get suggestions._

## Definitions

_Eval definitions will be added here as you adopt suggestions from the evals advisor._
```
