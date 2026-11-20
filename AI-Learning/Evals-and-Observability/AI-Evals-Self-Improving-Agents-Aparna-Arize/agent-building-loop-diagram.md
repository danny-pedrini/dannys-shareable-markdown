# Aparna Dhinakaran's Agent-Building & Self-Improvement Loop

**Source:** Aparna Dhinakaran (CPO, Arize AI) on "Land a PM Job" podcast with Akash Gupta
**Core thesis:** Product taste is the alpha. Evals and observability are the foundation for self-improving agents.

---

## The Full Loop

```
  CONTEXT SOURCES                         BUILD
  (Your "Taste" Inputs)                   (Claude Code)
 ┌─────────────────────┐                 ┌──────────────────────────────┐
 │  GitHub Issues       │                 │  1. CREATE AGENT             │
 │  GitHub Discussions  │────────────────>│     - Pick your product      │
 │  Slack / Discord     │  Aggregate      │     - Write a good prompt    │
 │  Gong Transcripts    │  feedback into  │     - Define scoring logic   │
 │  Product Analytics   │  a context      │       (bugs vs features,     │
 │  Twitter / Community │  graph          │        recency, reactions)   │
 │  Customer Calls      │                 │     - Output: PM report      │
 └─────────────────────┘                 │       (P0-P3 priorities)     │
                                          └──────────────┬───────────────┘
                                                         │
                                                         v
                                          ┌──────────────────────────────┐
                                          │  2. INSTRUMENT WITH TRACING  │
                                          │     - Add observability      │
                                          │       (Arize skill / Phoenix)│
                                          │     - Every LLM call, tool   │
                                          │       call, and step becomes │
                                          │       a visible span/trace   │
                                          └──────────────┬───────────────┘
                                                         │
                                                         v
                              ┌───────────────────────────────────────────────────┐
                              │  3. RUN AGENT & COLLECT TRACES                    │
                              │     - Run once, or set up a loop (cron / Claude   │
                              │       loop skill) to run on a cadence             │
                              │     - Traces stream into observability platform   │
                              └────────────────────────┬──────────────────────────┘
                                                       │
                                                       v
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                          │
│                          THE EVAL & IMPROVEMENT LOOP                                     │
│                          (this is where it gets good)                                    │
│                                                                                          │
│   ┌─────────────────────────┐         ┌──────────────────────────────┐                   │
│   │  4. SUGGEST EVALS       │         │  5. RUN EVALS ON TRACES      │                   │
│   │     - Ask Claude Code   │────────>│     - Score each span/issue  │                   │
│   │       "suggest a good   │         │     - Label: accurate or     │                   │
│   │        eval for my      │         │       inaccurate             │                   │
│   │        agent"           │         │     - Surface failures       │                   │
│   │     - Start with vibe   │         └──────────────┬───────────────┘                   │
│   │       eval (first pass) │                        │                                   │
│   └─────────────────────────┘                        v                                   │
│                                        ┌──────────────────────────────┐                  │
│                ^                       │  6. DIAGNOSE FAILURES        │                  │
│                │                       │                              │                  │
│                │                       │  "Was my eval wrong,         │                  │
│                │                       │   or was my agent wrong?"    │                  │
│                │                       │                              │                  │
│                │                       │  Ask: "What are the common   │                  │
│                │                       │   reasons my priority        │                  │
│                │                       │   accuracy is inaccurate?"   │                  │
│                │                       │                              │                  │
│                │                       │  Categorize failure modes:   │                  │
│                │                       │   - Bug scoring too low?     │                  │
│                │                       │   - Feature requests off?    │                  │
│                │                       │   - Legacy scoring drift?    │                  │
│                │                       └──────────┬───────┬───────────┘                  │
│                │                                  │       │                               │
│                │                    ┌─────────────┘       └──────────────┐                │
│                │                    v                                    v                │
│   ┌────────────┴────────────────────────┐    ┌───────────────────────────────────┐       │
│   │  7a. REFINE THE EVAL               │    │  7b. IMPROVE THE AGENT            │       │
│   │      - Eval was wrong              │    │      - Agent was wrong             │       │
│   │      - Add human annotations       │    │      - "Go fix this issue"         │       │
│   │      - Align eval to your taste    │    │      - Update prompt / scoring     │       │
│   │      - Give ruthless criticism     │    │      - Add missing context         │       │
│   │                                     │    │      - Ship new agent version      │       │
│   │  [HUMAN IN THE LOOP]              │    │                                     │       │
│   └─────────────────────────────────────┘    │  [HUMAN IN THE LOOP]              │       │
│                │                              └──────────────┬────────────────────┘       │
│                │                                             │                            │
│                └──────────────┬───────────────────────────────┘                           │
│                               │                                                          │
│                               v                                                          │
│                ┌──────────────────────────────┐                                          │
│                │  8. COLLECT NEW TRACES       │                                          │
│                │     from improved agent/eval │──────── loop back to step 5 ────>        │
│                └──────────────────────────────┘                                          │
│                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────┘


                     AUTOMATION LAYER (The Vision)
 ┌─────────────────────────────────────────────────────────────────────┐
 │                                                                     │
 │   Once evals are trustworthy, automate the loop:                   │
 │                                                                     │
 │   Claude Loop Skill (cron)                                         │
 │   ┌──────────┐    ┌──────────┐    ┌────────────┐    ┌───────────┐  │
 │   │  Run      │───>│  Run     │───>│  Fetch     │───>│  Suggest  │  │
 │   │  Agent    │    │  Evals   │    │  Failures  │    │  Fix &    │  │
 │   │  Daily    │    │  on New  │    │  & Common  │    │  Open PR  │  │
 │   │          │    │  Traces  │    │  Reasons   │    │           │  │
 │   └──────────┘    └──────────┘    └────────────┘    └─────┬─────┘  │
 │                                                           │        │
 │                                                           v        │
 │                                                    ┌───────────┐   │
 │                                                    │  HUMAN    │   │
 │                                                    │  REVIEWS  │   │
 │                                                    │  PR       │   │
 │                                                    └───────────┘   │
 │                                                                     │
 └─────────────────────────────────────────────────────────────────────┘
```

---

## Where Humans Stay In The Loop

```
 ┌───────────────────────────────────────────────────────────────┐
 │                    HUMAN REQUIRED AT:                         │
 │                                                               │
 │   1. EVAL CHANGES ──── Curate taste: what is good/not good   │
 │                                                               │
 │   2. AGENT CHANGES ─── Code review every PR from the loop    │
 │                                                               │
 │   3. IMPROVEMENT SKILL DESIGN ─── What context does the      │
 │      improvement workflow need access to?                     │
 │                                                               │
 │   The RADIUS of autonomous changes grows over time:           │
 │                                                               │
 │   Now:    prompts, tools, simple scoring logic                │
 │   Soon:   entire new workflows the agent didn't have          │
 │   Future: real-time self-improvement across millions of users │
 │                                                               │
 └───────────────────────────────────────────────────────────────┘
```

---

## Key Quotes

> "Product taste is really the alpha today."

> "A good eval is like you're getting some healthy percentage right, but also healthy wrong so that you can make progress."

> "Vibe evals are going to fall short very very quickly... it's not grounded on any actual human."

> "The evals don't just come out of magic, they come out of your traces."

> "Any product person that has used observability and is looking at their traces and looking at their evals, you're probably already in the top 1% of PMs."
