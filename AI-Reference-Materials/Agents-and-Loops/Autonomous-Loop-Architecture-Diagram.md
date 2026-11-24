# Autonomous Loop Architecture

**How to build AI systems that run themselves — and get smarter over time**

*Reference diagram for the Autonomous Loop pattern from the agent-architect skill. See also: [From Prompts to Loops](From-Prompts-to-Loops-AI-Review-Automation-for-PMs.md)*

---

## The Runtime Loop

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                                                                          │
│  ┌───────────┐    ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐    ┌──────────────────────────┐ │
│  │           │    │  STEP EXECUTION LOOP (repeats for each workflow step)                                                             │    │                          │ │
│  │  TRIGGER  │    │                                                                                                                   │    │  FINAL OUTPUT EVAL       │ │
│  │           │    │  ┌──────────────────┐          ┌─────────────────────────────────────────────────────────────────────────────┐     │    │  (independent subagent)  │ │
│  │  cron     │    │  │ ORCHESTRATING    │  step    │ EVAL SUBAGENT (independent)                                                 │     │    │                          │ │
│  │  /loop    │───▶│  │ AGENT            │  output  │                                                                             │     │    │  Reads: final artifact   │ │
│  │  event    │    │  │                  │─────────▶│ Reads: step output + evals.md criteria for Step N                           │     │all │  + evals.md criteria     │ │
│  │  manual   │    │  │ Executes Step N  │          │ Judges: Pass / Fail (binary, per criterion)                                │     │steps                          │ │
│  │           │    │  │                  │          │                                                                             │     │done│  Judges: Pass / Fail     │ │
│  └───────────┘    │  │ (does NOT eval   │          │ PASS ──▶ next step                                                         │     │───▶│                          │ │
│                   │  │  its own work)   │          │ FAIL ──▶ self-correct ──▶ re-eval by subagent                              │     │    │  PASS → deliver          │ │
│                   │  │                  │          │          ├── PASS ──▶ next step                                             │     │    │  FAIL → retry or flag    │ │
│                   │  └──────────────────┘          │          └── still FAIL ──▶ flag + continue                                 │     │    │                          │ │
│                   │                                └─────────────────────────────────────────────────────────────────────────────┘     │    └────────────┬─────────────┘ │
│                   └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘                 │               │
│                                                                                                                                                        ▼               │
│                   ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│                   │  TRACE + DELIVER                                                                                                                               │ │
│                   │                                                                                                                                                │ │
│                   │  Every run writes a structured trace: inputs received, context sources consulted, tool calls made,                                              │ │
│                   │  per-step pass/fail with eval details, decisions made + rationale, self-corrections attempted, and final output summary.                        │ │
│                   │  The trace is the audit trail that makes the IMPROVE step precise instead of vague.                                                            │ │
│                   └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬──────────────────────────────┘ │
│                                                                                                                                     │                                │
│                   after early runs, human reviews output + trace and diagnoses each issue                                            │                                │
│                                                                                                                                     ▼                                │
│                   ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│                   │  IMPROVE                                                                                                                                       │ │
│                   │                                                                                                                                                │ │
│                   │  Prompt was unclear?                     → SPECIFICATION issue    → fix the prompt                                                             │ │
│                   │  Prompt was clear, AI didn't follow it?  → GENERALIZATION issue   → add eval to evals.md                                                      │ │
│                   │                                                                                                                                                │ │
│                   │  Both fixes take effect on the next run automatically.                                                                                         │ │
│                   └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## How to Build One

```
    1. DEFINE       What's the job? How can it fail?
                    What does "good" look like?
         │
         ▼
    2. BREAK INTO   Step 1: Gather data
       STEPS        Step 2: Analyze
                    Step 3: Draft output
         │
         ▼
    3. WRITE        For each step, a specific pass/fail check.
       QUALITY      Not "good summary" — but "one sentence,
       CHECKS       ≤20 words, names the issue, no filler."
         │
         ▼
    4. RUN IT       ┌────────────┐     ┌────────────────┐
                    │ AI does    │────▶│ A different AI  │
                    │ the work   │     │ checks the work │
                    └────────────┘     └───────┬────────┘
                                               │
                                         ┌─────┴─────┐
                                       PASS        FAIL
                                         │           │
                                      Apply     Fix + recheck
                                                     │
                                                Still fails?
                                                     │
                                              Surface to human
         │
         ▼
    5. TIGHTEN      Run 10 times. See what fails.
                    Sharpen the checks. Repeat.
                    Each cycle, the loop handles more,
                    you review less.


    THE RULE: The AI that does the work never
              judges its own work.
```
