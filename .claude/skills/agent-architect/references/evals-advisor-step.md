# Evals Runtime Step Templates

Templates for the eval-related steps that agent-architect embeds in generated skills when the user opts into evals. Includes both the automatic eval runner and the optional evals advisor.

The eval runner executes adopted evals from `evals.md`. The evals advisor (`.claude/skills/evals-advisor/SKILL.md`) suggests new evals and records adopted ones.

---

## Step 1: Eval Runner (Automatic)

Runs AFTER the last substantive step, BEFORE observability logging. Skips silently if no evals exist.

```markdown
### Step [N]: Run Evals

If `evals.md` exists and has active evals, run each eval against this run's output:

1. **Read** `evals.md` to get active evals and their definitions
2. **For each active eval:**
   - **Code-based (`check` block):** Execute the described check using Bash/grep against the output. Its result is the Pass or Fail verdict, recorded unchanged (agent-architect Step 2.6).
   - **LLM judge (`judge` block):** Group the judge evals by the input set they read. Spawn one grader subagent per group with each eval's criterion, its pass/fail definitions and the input paths. Cap each group at the evals that share one input set. The grader returns Pass or Fail with reasoning per eval and edits nothing. Before recording, check that its report covers exactly its assigned eval IDs; re-spawn a fresh grader for any missing ID. Spawn it as `local-grader` when its inputs are local files only, and as general-purpose when it reads an MCP source. Every judge eval runs on every run and every fix round. The orchestrator never judges its own output (agent-architect Step 2.6).
3. **Report results** to the user:

   **Eval Results: [N] run, [X] passed, [Y] failed**

   | Eval | Result | Detail |
   |------|--------|--------|
   | G1: [name] | Pass | — |
   | G2: [name] | Fail | [brief explanation] |

4. **Update** the `Last Result` column in `evals.md`
5. **Pass results forward** to the observability step (if enabled) for inclusion in the trace and invocation log

If `evals.md` doesn't exist or has no active evals, skip this step silently.
```

## Step 2: Evals Advisor (Optional, User-Triggered)

Runs as the FINAL step, after observability logging. The user chooses at runtime whether to invoke it.

```markdown
### Step [N]: Suggest Evals (Optional)

Ask the user: **"Want me to suggest evals based on this run?"**

If yes, use the Agent tool to launch the `evals-advisor` agent type (`.claude/agents/evals-advisor.md`) in the foreground, passing `run_in_background` as a boolean `false`. Wait for its report before you reply to the user.

**Description:** "Evals advisor for [skill-name]"

**Prompt:**
"You are an evals advisor for Claude Code skills. Read your full instructions at `.claude/skills/evals-advisor/SKILL.md`, then analyze this skill run:

- **Skill:** [skill-name]
- **SKILL.md:** [path to this skill's SKILL.md]
- **Output:** [describe what was produced, or provide the file path]
- **Trace:** [path to trace file if observability is enabled, or 'no trace available']

Follow the evals-advisor workflow. Save your report to `[this run's folder, or the session scratchpad]/evals-advisor-mode2.md` before you return it. Do not write inside `.claude/skills/`. Return the report and its path. Record in the skill's evals.md only the suggestions I accept, one by one."

`Read` the saved report and `Write` it unchanged to `.claude/skills/[skill-name]/observability/evals-advisor/[YYYY-MM-DD]-mode2.md`. Present the report and that path. Adoption can resume in a fresh session that reads the saved report. Nothing goes into `evals.md` until the user accepts it, item by item.

If no or skipped, end.
```

## For Fast Path Skills

Add after the main output:

```markdown
**Optional:** "Want me to suggest evals for this run?" → If yes, launch the evals-advisor subagent in the foreground per the step template above (`evals-advisor` agent type, `run_in_background` as a boolean `false`).
```

## Step Ordering (Full Picture)

```
[Last substantive step]
  ↓
Step N: Run Evals (automatic — checks output against evals.md, skips if empty)
  ↓
Step N+1: Log Observability (automatic — includes eval results in trace and log)
  ↓
Step N+2: Verify Observability (automatic — confirms trace + log were written correctly)
  ↓
Step N+3: Suggest New Evals (optional — user-triggered, after reviewing everything)
```

Eval runner goes first so results feed into the observability trace. Verify step confirms the trace and log were written correctly. Evals advisor goes last so the user has the complete picture before deciding whether to request suggestions.
