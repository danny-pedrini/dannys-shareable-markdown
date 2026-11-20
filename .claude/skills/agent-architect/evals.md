# Evals: agent-architect

These evals guard the token-efficiency changes in `AI-Learning/Claude-Code-and-Skills/Token-Spend/skill-plans/agent-architect.md` section 3. None has run yet.

## Active Evals

| ID | Name | Type | Check | Added | Last Result |
|----|------|------|-------|-------|-------------|
| AA1 | Handoff carries what the build used | Generalization | Judge | 2026-11-06 | not run |
| AA2 | Grader type matches its sources | Generalization | Code | 2026-11-06 | not run |
| AA3 | Core rules survive the split | Generalization | Code | 2026-11-06 | not run |
| AA4 | Observability script matches recorded verification | Generalization | Code | 2026-11-06 | not run |
| AA5 | One eval-runner template | Generalization | Code | 2026-11-06 | not run |
| AA6 | Lint agrees with the grader | Generalization | Code | 2026-11-06 | not run |

## Definitions

### AA1: Handoff carries what the build used

**Pass:** Every file path, decision and open question the resumed build cites appears in the handoff file written at Pre-Flight Check 4.
**Fail:** The resumed build cites a file path, decision or open question the handoff lacks.
**Check type:** LLM judge

**Implementation:**

```judge
Criterion: The handoff file names every file path, decision and open question the build later used.
Pass definition: Each file path, decision and open question cited in the resumed build's design, draft and QA briefs appears in the handoff file.
Fail definition: At least one cited file path, decision or open question is missing from the handoff file.
Examples: add from your own runs, do not fabricate
```

**Source:** agent-architect token-efficiency plan, change C1.
**Added:** 2026-11-06
**Notes:** Runs only when Check 4 fired and the user accepted the handoff. Grade in a fresh context with the handoff file and the resumed session's briefs.

### AA2: Grader type matches its sources

**Pass:** Every grader or producer brief that names an MCP source spawns as general-purpose, and every brief that names only local paths spawns as `local-grader`.
**Fail:** A brief that names an MCP source spawns as `local-grader`, or a local-only brief spawns as general-purpose.
**Check type:** Code-based

**Implementation:**

```check
Type: comparison
Source field: each subagent brief in the run (description and prompt), and whether it names an MCP tool, connector, or live-source URL
Target field: the subagent type each spawn used (from the transcript's Agent tool input or the subagent .meta.json)
Logic: For each spawn that is not a Care reviewer persona or the evals-advisor, grep the brief for mcp__, Slack, Confluence, Jira, Google Doc, Figma, Looker or an http URL. If any match, the type must be general-purpose. If none match, the type must be local-grader. FAIL on any mismatch.
```

**Source:** agent-architect token-efficiency plan, change C2.
**Added:** 2026-11-06
**Notes:** Downstream, prd-generator E18 and acceptance-testing-generator G1 would catch a grader that lost a source.

### AA3: Core rules survive the split

**Pass:** Every line of `<hard_constraints>`, Step 2.5b and Step 2.6 in the last committed SKILL.md appears unchanged in the working SKILL.md, and every `references/` path SKILL.md names exists.
**Fail:** A line from those sections is missing from the core, or a pointer names a reference file that does not exist.
**Check type:** Code-based

**Implementation:**

```check
Type: structural
Source field: <hard_constraints> block, "### Step 2.5b" section and "### Step 2.6" section of `git show HEAD:.claude/skills/agent-architect/SKILL.md`
Target field: the working `.claude/skills/agent-architect/SKILL.md`, and every `references/<name>` path it names
Logic: For each non-blank line in the source sections, grep -F for the line in the working SKILL.md; FAIL on any miss unless the run's change set edits that line on purpose. Then grep -o "references/[A-Za-z0-9_.-]*" in SKILL.md and test -f each path under the skill folder; FAIL on any missing file.
```

**Source:** agent-architect token-efficiency plan, change C3.
**Added:** 2026-11-06
**Notes:** Run on any edit that moves text out of SKILL.md.

### AA4: Observability script matches recorded verification

**Pass:** On every existing trace, the script's mechanical result agrees with the trace's recorded `verified` flag.
**Fail:** Any trace where the script's mechanical result and the recorded `verified` flag disagree.
**Check type:** Code-based

**Implementation:**

```check
Type: comparison
Source field: recorded `verified` flag in each trace under `.claude/skills/<skill>/observability/traces/`
Target field: mechanical_pass from `python3 .claude/skills/agent-architect/references/verify_observability.py --skill-dir .claude/skills/<skill> --all-traces`
Logic: Run the script with --all-traces (it skips the recency check) for each skill with Full observability. FAIL when "disagreements" is above 0. Read each disagreement before acting, since a recorded false can come from the judgment check alone.
```

**Source:** agent-architect token-efficiency plan, change C4.
**Added:** 2026-11-06
**Notes:** Run when the script or the verification step template changes.

### AA5: One eval-runner template

**Pass:** Exactly one eval-runner step template exists across agent-architect's references.
**Fail:** Two or more reference files hold an eval-runner step template.
**Check type:** Code-based

**Implementation:**

```check
Type: pattern
Source field: n/a
Target field: `.claude/skills/agent-architect/references/*.md`
Logic: grep -l "### Step \[N\]: Run Evals" across the references. PASS when exactly one file matches and it is evals-advisor-step.md.
```

**Source:** agent-architect token-efficiency plan, change C5.
**Added:** 2026-11-06
**Notes:** None.

### AA6: Lint agrees with the grader

**Pass:** On each skill's final files, `scripts/lint_skill.py` gives the same verdict as the grader's last QA verdict on every structural check it covers.
**Fail:** The lint and the grader disagree on any structural check.
**Check type:** Code-based

**Implementation:**

```check
Type: comparison
Source field: the grader's last QA report verdicts on frontmatter, labeled sections, When NOT to Use per tool, stop message per tool, and subagent type per spawn
Target field: L1 to L5 results from `python3 .claude/skills/agent-architect/scripts/lint_skill.py <skill-folder>`
Logic: Map L1 through L5 to the matching grader rows. FAIL on any check where one says PASS and the other says FAIL.
```

**Source:** agent-architect token-efficiency plan, change C8.
**Added:** 2026-11-06
**Notes:** The grader brief never mentions lint results, so agreement is a real cross-check.
