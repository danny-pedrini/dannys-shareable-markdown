# Post-Deployment Iteration Support

Reference file loaded by agent-architect only when the user says the agent will be refined over time (Phase 5 Deliverables Checklist).

## POST-DEPLOYMENT: Iteration Support (Optional)

**Include this section only if the user answers YES to:** "Will this agent be used repeatedly and refined over time?"

If the agent is a one-off or disposable, skip this section entirely.

---

### When to Ask

At the end of Phase 5, before delivering:

> "Will you be refining this agent over time, or is this a one-time use?
> - **Refine over time** → I'll include iteration support (version tracking, debugging guide, feedback template)
> - **One-time use** → I'll skip the iteration scaffolding to keep it lean"

---

### Iteration Support Package

If user wants iteration support, include these sections in the deliverable:

#### 1. Debugging Playbook

```markdown
## Debugging Guide

When this agent misbehaves, diagnose systematically:

| Symptom | Check | Fix |
|---------|-------|-----|
| Wrong output format | Output schema section | Add stricter format requirements |
| Missed requirement | Hard constraints | Add specific NEVER/ALWAYS rule |
| Used wrong tool | Tool selection rules | Add "When NOT to Use" guidance |
| Hallucinated information | Context/examples | Add grounding examples or constraints |
| Ignored instructions | Attention strategy | Move critical instruction to start or end |
| Inconsistent behavior | Examples section | Add more diverse examples |

**Quick Diagnosis Flow:**
1. What input did you provide? (Was it what the agent expected?)
2. What output did you get? (Which part is wrong?)
3. What should have happened? (What's the gap?)
4. Which prompt section should have prevented this? (Hard constraints? Examples? Task instructions?)
```

#### 2. Version History Template

```markdown
## Version History

| Version | Date | Change | Reason | Result |
|---------|------|--------|--------|--------|
| 1.0 | [Date] | Initial release | — | Baseline |
| | | | | |

**Changelog Format:**
- **Version:** Increment minor (1.1) for fixes, major (2.0) for significant changes
- **Change:** What was modified in the prompt
- **Reason:** What failure or feedback triggered this
- **Result:** Did it fix the issue? Any side effects?
```

#### 3. Feedback Log Template

```markdown
## Feedback Log

### Issue #[N]
**Date:** [Date]
**Reported by:** [Who noticed the issue]
**Input:** [What was provided to the agent]
**Expected:** [What should have happened]
**Actual:** [What actually happened]
**Root Cause:** [Why it failed — which prompt section?]
**Fix:** [What was changed]
**Status:** 🔴 Open | 🟡 In Progress | 🟢 Fixed | ⚪ Won't Fix
```

#### 4. Rebuild vs. Patch Decision

```markdown
## When to Rebuild vs. Patch

| Signal | Action |
|--------|--------|
| Single edge case failure | **Patch:** Add example |
| Missing constraint | **Patch:** Add NEVER/ALWAYS rule |
| Multiple related failures | **Patch:** Refine task instructions |
| Fundamental job misunderstanding | **Rebuild:** Re-do Phase 1 Discovery |
| Scope creep (doing too much) | **Rebuild:** Decompose into multiple agents |
| >5 patches and still unstable | **Rebuild:** Start fresh with learnings |
| New requirements change the job | **Rebuild:** New agent, retire old one |
```

#### 5. Performance Monitoring (For High-Use Agents)

```markdown
## Performance Tracking

**Track these metrics periodically:**

| Metric | How to Measure | Target |
|--------|----------------|--------|
| Accuracy | % outputs that are correct | >90% |
| Adoption | % outputs accepted without edits | >80% |
| Failure patterns | Most common error types | Decreasing over time |

**Review Schedule:** [Weekly / Monthly / After N uses]
```

---

### Compact Version (For Simpler Agents)

If the agent is moderately important but doesn't need full monitoring, include just:

```markdown
## Iteration Notes

**If this agent misbehaves:**
1. Check which part of the output is wrong
2. Find the prompt section that should have prevented it
3. Add a specific constraint, example, or instruction

**Version:** 1.0 | **Last Updated:** [Date]
**Known Limitations:** [List any known edge cases]
```

---

### Integration with Deliverables

**Full Iteration Support** (for important, long-lived agents):
```markdown
# [Agent Name]

## Quick Start
...

## Prompt
...

## Test Cases
...

## Debugging Guide
[From section 1 above]

## Version History
[From section 2 above]

## Feedback Log
[From section 3 above]
```

**Compact Iteration Support** (for moderate-use agents):
```markdown
# [Agent Name]

## Quick Start
...

## Prompt
...

## Iteration Notes
[Compact version above]
```

**No Iteration Support** (for one-off agents):
```markdown
# [Agent Name]

## Quick Start
...

## Prompt
...
```
