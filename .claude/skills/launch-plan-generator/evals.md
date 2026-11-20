# Evals: launch-plan-generator

## Active Evals

| ID | Name | Type | Check | Added | Last Result |
|----|------|------|-------|-------|-------------|
| G1 | Brain dump coverage | Generalization | Judge | 2026-06-11 | — |
| G2 | Prereq vs open item categorization | Generalization | Judge | 2026-06-11 | — |
| G3 | No redundancy | Generalization | Judge | 2026-06-11 | — |
| G4 | Date consistency | Generalization | Code | 2026-06-11 | — |
| G5 | Stakeholder accuracy | Generalization | Code | 2026-06-11 | — |
| G6 | Scope-appropriate sections | Generalization | Judge | 2026-06-11 | — |
| G7 | Owner completeness | Generalization | Code | 2026-06-11 | — |

## Definitions

### G1: Brain dump coverage

**Pass:** Every distinct point from the user's brain dump has a corresponding element in the generated plan (a section, table row, prereq, or open item).
**Fail:** One or more brain dump points have no representation in the plan.
**Check type:** LLM judge

```judge
Criterion: Does every point from the user's brain dump appear somewhere in the generated launch plan?
Pass definition: Every distinct requirement, constraint, date, person, or decision from the brain dump maps to a specific element in the plan.
Fail definition: At least one brain dump point is absent from the plan — not represented in any section, prereq, or open item.
Examples: Add from runs.
```

**Source:** Phase 2 rollout plan audits — brain dump coverage was checked in every audit round.
**Added:** 2026-06-11

### G2: Prereq vs open item categorization

**Pass:** Every prerequisite is a known task with an unambiguous owner and clear deliverable. Every open item requires a decision or clarification that hasn't been made yet.
**Fail:** A prereq is actually a question/clarification (should be an open item), or an open item is actually a known task with a clear owner (should be a prereq).
**Check type:** LLM judge

```judge
Criterion: Are prerequisites and open items correctly categorized?
Pass definition: Prerequisites are all known tasks with named owners. Open items all require decisions or clarifications not yet resolved.
Fail definition: At least one item is in the wrong category — a known task in open items, or a question/clarification in prerequisites.
Examples: Add from runs.
```

**Source:** Explicit user feedback during Phase 2 plan iteration — "Prereqs are known to-dos with unambiguous tasks and owners. Open items require clarifications."
**Added:** 2026-06-11

### G3: No redundancy

**Pass:** Each idea, fact, or requirement appears in exactly one location in the plan. No section restates what another section covers.
**Fail:** The same idea appears in two or more places (e.g., a date in the key dates table AND restated in a body paragraph, or a prerequisite that duplicates an open item).
**Check type:** LLM judge

```judge
Criterion: Is each idea stated exactly once in the plan?
Pass definition: No concept, requirement, or fact is repeated across sections. Cross-references (e.g., "see P-11") are acceptable; restating the content is not.
Fail definition: At least one idea appears in two or more places in substantively the same form.
Examples: Add from runs.
```

**Source:** User's primary complaint about the Phase 2 plan was length and redundancy — "It should only communicate each idea a singular time."
**Added:** 2026-06-11

### G4: Date consistency

**Pass:** All dates in the key dates table match dates referenced in body text. No date contradictions anywhere in the document.
**Fail:** A date in the key dates table differs from how it's referenced in the body (e.g., table says "July 2" but body says "July 1"), or two body sections reference different dates for the same milestone.
**Check type:** Code-based

```check
Type: comparison
Source field: Key dates table (all date values)
Target field: All date references in body text
Logic: Extract all dates from the key dates table. For each, grep the body text for references to the same milestone. Verify the dates match. Flag any discrepancy.
```

**Source:** Audit round 3 found testing window date discrepancy (July 1 vs July 2). Audit round 4 found key dates table not updated when testing section was reframed.
**Added:** 2026-06-11

### G5: Stakeholder accuracy

**Pass:** Every person named in the plan exists in `Stakeholder Management/stakeholder-directory.md` or was explicitly provided by the user in the brain dump.
**Fail:** A name appears in the plan that is not in the stakeholder directory and was not mentioned by the user.
**Check type:** Code-based

```check
Type: presence
Source field: All person names in the generated plan
Target field: Stakeholder directory + user brain dump
Logic: Extract all person names from the plan. For each, grep the stakeholder directory. If not found, check the user's brain dump. Flag any name not found in either source.
```

**Source:** Phase 2 plan had "[teammate]" (should be "[Sr. Operations Manager, Dispense & Fulfillment]") and "[teammate]" (corrected to "[Director, Learning]"). Name accuracy matters.
**Added:** 2026-06-11

### G6: Scope-appropriate sections

**Pass:** Only sections relevant to the assessed launch scope are present. No empty or unnecessary sections (e.g., no "Volume Ramp" section for a software feature rollout).
**Fail:** A section is included that doesn't apply to the launch scope, or a section that should be included based on scope is missing.
**Check type:** LLM judge

```judge
Criterion: Are the included sections appropriate for the assessed launch scope?
Pass definition: Every section present is relevant to the launch type. No section is included just because the template has it. No required section is missing.
Fail definition: At least one section is present but irrelevant to this launch type, or a section that should be present based on the scope assessment is missing.
Examples: Add from runs.
```

**Source:** User's feedback to "assess scope and include/exclude sections accordingly" rather than always using the full template.
**Added:** 2026-06-11

### G7: Owner completeness

**Pass:** Every prerequisite has a specific named owner (person or team with a named lead). Every open item has an owner and a deadline.
**Fail:** A prereq has no owner, uses a vague owner like "Engineering" when a specific person is known, or an open item lacks an owner or deadline.
**Check type:** Code-based

```check
Type: presence
Source field: All prereq and open item rows
Target field: Owner and Deadline columns
Logic: For each prereq row, verify the Owner column is not empty and not "TBD". For each open item row, verify both Owner and Deadline columns are populated. Flag any gaps.
```

**Source:** Multiple audit rounds checked prereq/open item completeness. Owners were updated from generic "Engineering" to specific names (e.g., "[Pharmacy Eng director] + [Engineering]").
**Added:** 2026-06-11
