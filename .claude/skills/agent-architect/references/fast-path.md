# Fast Path

Reference file loaded by agent-architect when the Pre-Flight Assessment selects Fast Path. The Observability and Evals sections it mentions stay in SKILL.md.

## FAST PATH: Simple Agent Workflow

**Use when:** Single responsibility, minimal tools, non-critical output

**Time:** ~10-15 minutes vs. 45-60 minutes for full process

---

### Fast Path Examples

**✅ Good Fast Path Candidates:**
- Meeting notes summarizer
- Jira ticket formatter
- PRD section drafter (single section)
- Status update generator
- User story expander
- Glossary term definer
- Competitive feature comparison table

**❌ Requires Full Process:**
- Discovery synthesis agent (multiple responsibilities)
- Full PRD generator (4+ sections, different expertise needed)
- Order exception handler (critical, conditional logic)
- Release coordinator (multi-step orchestration, multiple tools)
- Compliance-related agents (failure modes are serious)

---

### Fast Path Workflow (3 Steps)

#### Step 1: Quick Intake (2 minutes)

Gather these 6 essentials:

| Field | Your Answer |
|-------|-------------|
| **Job** (≤10 words) | |
| **Input** | |
| **Output format** | |
| **Example of good output** | |
| **Must NEVER do** (top 1-2) | |
| **Tools needed?** | None / Read / [other] |

**Confirm with user:** "This agent will [JOB] by taking [INPUT] and producing [OUTPUT]. It must never [CONSTRAINT]. Tools: [TOOLS or 'none']. Is that right?"

#### Step 2: Generate Prompt (5 minutes)

Use the **Fast Path Template**:

```xml
<system_role>
You are a [SPECIFIC ROLE] that [ONE JOB IN 10 WORDS].
You are NOT a general assistant—you only do this one thing.
</system_role>

<hard_constraints>
NEVER:
- [FAILURE MODE 1]
- [FAILURE MODE 2 if applicable]
- Deviate from the specified output format
- Continue after a tool, file, or link fails. Retry once, then stop and report (Step 2.5b)

ALWAYS:
- [KEY SUCCESS BEHAVIOR]
- Follow the output format exactly
</hard_constraints>

<task>
**Your Job:** [ONE SENTENCE DESCRIPTION]

**Input:** {{input}}

**Output Format:**
[EXACT FORMAT SPECIFICATION]
</task>

<example>
**Input:** [EXAMPLE INPUT]
**Output:** [EXAMPLE OUTPUT]
</example>
```

**Tool Addition (if needed):**

If agent needs 1-2 tools, add this section after `<hard_constraints>`:

```xml
<tools>
You have access to: [TOOL_NAME]
- Use it when: [SPECIFIC CONDITION]
- Do NOT use it when: [ANTI-PATTERN]
- If it fails: retry once with corrected parameters, then stop and report the tool, resource and error (Step 2.5b)
</tools>
```

#### Step 3: Mini-Eval (3 minutes)

Quick quality check—all must pass:

| Check | Pass? |
|-------|-------|
| Job is clear in first 50 tokens? | ☐ |
| Output format is exact (not vague)? | ☐ |
| NEVER constraints are specific? | ☐ |
| Example matches expected output? | ☐ |
| (If tools) Stops and reports on any unavailable tool or link? | ☐ |

**All pass?** → Ship it
**Any fail?** → Fix that specific issue and re-check

---

### Fast Path Deliverable

```markdown
# [Agent Name]

## Quick Start
[One sentence: what this agent does]

## Prompt
\`\`\`xml
[The prompt from Step 2]
\`\`\`

## Test It
**Input:** [Test input]
**Expected:** [What good output looks like]
```

**Optional:** Ask if user wants observability (Full/Light/None) and/or evals advisor (Yes/No). If yes, generate the respective scaffolding per the Observability and Evals Advisor sections. If both are enabled, observability logs first (automatic), then evals advisor runs (optional, user-triggered).

---

### Escalation: When to Switch to Full Process

If during Fast Path you discover:
- The job is actually 2+ distinct responsibilities → **STOP, use Full Process**
- You need 3+ tools or complex tool orchestration → **STOP, use Full Process**
- Failure modes are more serious than expected → **STOP, use Full Process**
- User can't provide a clear example of good output → **STOP, use Full Process Phase 1**

**It's okay to start Fast Path and escalate.** The Pre-Flight Assessment catches most cases, but sometimes complexity reveals itself during intake.
