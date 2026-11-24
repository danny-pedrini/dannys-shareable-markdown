# From Prompts to Loops: AI Review Automation for Engineers and PMs

**How the best practitioners stopped reviewing AI output line-by-line — and what PMs can steal from them**

*Sources: Boris Cherny (Head of Claude Code, Anthropic) via Acquired podcast, summarized by Guillermo Flor (Jun 8, 2026); synthesized with PM-specific application by Danny Pedrini*

---

## Table of Contents

1. [The Core Insight: Stop Reviewing, Start Designing Systems](#1-the-core-insight)
2. [How Engineers Automate AI Code Review](#2-how-engineers-automate-ai-code-review)
3. [The Loop Mental Model](#3-the-loop-mental-model)
4. [How to Build a Loop: Step by Step](#4-how-to-build-a-loop-step-by-step)
5. [Mapping Engineering Practices to PM Work](#5-mapping-engineering-practices-to-pm-work)
6. [The Taste Window](#6-the-taste-window)
7. [Key Takeaways](#7-key-takeaways)

---

## 1. The Core Insight

Boris Cherny, who built Anthropic's Claude Code agent, said it plainly on the Acquired podcast:

> "I don't prompt Claude anymore. I have loops running. They're the ones prompting Claude and figuring out what to do. My job is to write loops."

The person who built the coding agent doesn't write prompts. He writes systems that prompt themselves.

**The shift is architectural.** In the prompt era, the human is the connective tissue between every step. In the loop era, the human designs the system once and the system runs. This applies to code review, artifact generation, and any repetitive knowledge-work workflow.

The question for PMs: if engineers have figured out how to stop reviewing AI-written code line-by-line, what can we steal for reviewing AI-written PRDs, analyses, and stakeholder communications?

---

## 2. How Engineers Automate AI Code Review

The best engineering teams have built a layered review stack that pushes human attention to where it actually matters:

### Layer 1: Let machines check machines

| Check | What It Catches | Human Effort |
|-------|-----------------|--------------|
| **Type systems + linters** | Syntax, structure, style drift | Zero |
| **Automated tests** (written before/alongside AI code) | Behavioral correctness | Zero at review time (investment is upfront) |
| **AI-powered code review** (second model reviewing first) | Patterns, security issues, logic errors | Human reviews the flags, not the raw diff |
| **Evals** | Deterministic acceptance criteria that execute automatically | Zero — pass/fail |

### Layer 2: Review at the seam, not the stitch

Senior engineers review **interfaces, contracts, and architectural decisions** — not implementation details. If the function signature, error handling strategy, and test coverage are right, the interior is low-risk.

### Layer 3: Progressive trust with guardrails

Start reviewing everything, then gradually exempt categories that have never produced issues (formatting, boilerplate, test scaffolding) while keeping scrutiny on high-risk areas (auth, data mutations, business logic).

### Layer 4: Build for the upgrade

Boris is direct: the step changes in what Claude Code could do weren't driven by UX improvements — they were driven by model upgrades. Sonnet 4, then Opus 4, then Opus 4.5. Each jump increased the percentage of code the model wrote correctly.

**Implication:** Build eval loops that automatically absorb model improvements, rather than brittle prompt chains that need re-tuning every time a new model drops. The tooling matters at the margins. The model is the variable.

---

## 3. The Loop Mental Model

A **prompt** is a one-time instruction. You type, Claude responds, you're done.

A **loop** is a system. It runs a task, evaluates the output against criteria, decides what to do next, and runs again — without you in the middle.

```
┌─────────────────────────────────────┐
│           PROMPT ERA                │
│  Human → AI → Output → Human       │
│  (human reviews every output)       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│            LOOP ERA                 │
│  Trigger → AI runs task             │
│         → AI evals own output       │
│         → Self-corrects if needed   │
│         → Flags only exceptions     │
│         → Human reviews flags only  │
└─────────────────────────────────────┘
```

The difference isn't technical. It's about where human attention goes. A prompt gets you one output. A loop gets you a compounding operation.

### The Underfund Principle

Boris's most counterintuitive practice: when a project feels like a four-engineer job, he puts two engineers on it. On purpose.

The constraint forces the behavior he wants. When you're understaffed, you automate. You build loops instead of doing things manually. You figure out what the AI can handle so you don't have to. And because you've automated it, the next time that task comes up, it's cheaper, faster, and better.

**The framing:** Shift budget from humans to tokens. Raise upfront investment, dramatically lower ongoing cost. The teams that do this compound. The ones that don't pay full price every time.

---

## 4. How to Build a Loop: Step by Step

Adapted from Boris Cherny's workflow, generalized for any knowledge worker:

### Step 1: Pick one repetitive task

Open your AI history. Look at what you've prompted for more than twice this week. That's your loop candidate. The more you're doing it manually, the more value the loop returns.

### Step 2: Map the task as a process, not a prompt

Break the task into explicit stages. Example — "summarizing customer feedback":

1. Receive raw feedback
2. Identify the main complaint or request
3. Categorize it (bug / feature request / UX issue)
4. Write a one-line summary
5. Flag if urgent

Right now, you're probably doing all five in your head every time you prompt. The goal is to make each step explicit so the AI can handle it systematically instead of guessing.

### Step 3: Define your eval criteria

**This is the step most people skip. It's the most important one.**

For each stage, write down what "good output" looks like. Be brutally specific:

| Vague (useless) | Specific (useful) |
|---|---|
| "Clear summary" | "One sentence, under 20 words, identifies the specific feature or issue, no filler words" |
| "Correct category" | "Must be one of: bug / feature request / UX issue / billing / other — if unclear, flag for human review" |

This is your eval rubric. The AI will use it to grade its own output at each stage.

### Step 4: Write the loop prompt as a system instruction

Three parts:

1. **Context:** What it is and what it's doing
2. **Process:** Stage-by-stage breakdown from Step 2
3. **Eval:** Criteria from Step 3 + instruction to self-check before returning output

### Step 5: Run it, break it, fix it

Run the loop on 10 real examples. Look at where it fails:

- Wrong category? Criteria aren't specific enough — add examples
- Output too long? Tighten the constraint
- Missing edge cases? Add a rule
- Flagging too much for human review? Eval is too strict — loosen it

Each fix makes the loop more autonomous. You're not debugging — you're calibrating. This is the compounding effect: the loop gets better not because you rebuild it, but because you tighten it based on what it gets wrong.

### Step 6: Remove yourself from one decision point at a time

Find one place where you're still making a routine judgment call and hand it to the AI. Not a high-stakes decision — a routine one. Watch what happens. Fix what breaks. Then remove yourself from another step.

Boris went from reviewing every Claude output to having hundreds of loops run overnight. He got there by removing himself from one step at a time.

---

## 5. Mapping Engineering Practices to PM Work

The engineering-to-PM parallel is surprisingly clean:

| Engineering Practice | PM Equivalent | Example |
|---|---|---|
| **Type systems + linters** | **Templates + structural quality gates** | A PRD template with required fields is a "type system" for product artifacts. If the AI fills the template correctly, you review substance, not structure. |
| **Tests written before code** | **Acceptance criteria defined before the artifact** | Tell the AI what "good" looks like upfront (metrics need baselines, options need tradeoffs). Check against criteria, not line-by-line prose. |
| **AI reviewing AI** | **Second-pass review agent** | A review agent checks the drafting agent's output against your quality gate. Your CLAUDE.md output quality gate is literally this. |
| **Review at the seam** | **Review decisions and framing, not wordsmithing** | Is the problem framed right? Are the right options on the table? Are the metrics meaningful? If yes, the prose is low-risk. |
| **Evals** | **Rubrics that execute** | Codified checks (like `/audit`) that run against output so you catch structural misses without reading every word. |
| **Progressive trust** | **Graduated autonomy by artifact type** | Let AI handle status updates and meeting notes autonomously. Keep human review on PRDs and stakeholder comms. Expand as trust is earned. |
| **Build for the upgrade** | **Invest in eval criteria, not prompt tricks** | As models improve, good eval criteria automatically capture the improvement. Brittle prompt hacks need rework every cycle. |

### The meta-principle

**Don't review AI output the way you'd review human output.** Humans make creative, unpredictable errors — you have to read carefully. AI makes *systematic, predictable* errors — you can build checks for the failure modes and then only deeply review what the checks can't catch (judgment calls, strategic framing, stakeholder tone).

### Where to apply this as a PM

Look at your most repetitive workflows — the ones where you're manually reviewing AI output, copy-pasting into another tool, or making the same judgment call over and over. That's where the loop goes.

High-value PM loop candidates:
- **Feedback synthesis** — raw input from Slack/support/NPS → categorized, summarized, prioritized
- **Status report generation** — pull from Jira/Amplitude/Slack → structured update → review only the narrative
- **PRD first drafts** — problem canvas + template → draft PRD → review agent checks quality gates → you review framing and strategy only
- **Stakeholder email drafts** — data pull + audience profile + prior comms → draft → tone/accuracy check → you review final positioning
- **Meeting prep** — agenda + stakeholder map + open items → briefing doc → you review and add judgment

---

## 6. The Taste Window

Boris is honest about something most AI optimists won't say out loud.

Right now, the alpha is **product taste** — the ability to look at what AI generates and know what's good, what's wrong, and what direction to push. That judgment, trained over years of building, is genuinely valuable today.

But he gives it **3 to 6 months**.

His loops are already scanning feedback and generating product ideas. Today, maybe 20% of those ideas are good. By the next model cycle, he thinks most of them will be.

**What this means for PMs:**

The window to build taste-driven advantages is real but short. The PMs who move now — who actively use their taste to design better eval criteria, better quality gates, better loops — will have something durable. The ones waiting for the tools to get better before they engage will find the window has closed.

**The moat isn't taste itself. It's taste encoded into systems while taste still matters.**

Every constraint you encode in a template, quality gate, or skill file is a line you never have to review again — and it persists even as the models improve beneath it.

---

## 7. Key Takeaways

1. **The highest-leverage PM skill is now system design, not prompt craft.** Writing a good prompt is table stakes. Designing a loop that prompts itself, evals itself, and surfaces only what needs human judgment — that's the multiplier.

2. **Invest in eval criteria over prompt engineering.** Eval criteria compound (they automatically capture model improvements). Prompt tricks depreciate (they need rework every cycle).

3. **Review at the level of decisions, not prose.** Is the problem framed right? Are the options real? Are the metrics meaningful? If yes, trust the system for the rest.

4. **Remove yourself from one decision point at a time.** Don't try to fully automate on day one. Find the most routine judgment call you're still making and hand it to the loop. Fix what breaks. Repeat.

5. **The constraint creates the behavior.** Deliberately understaffing repetitive work forces automation. The teams that do this compound. The ones that don't pay full price every time.

6. **Encode your taste now.** The window where human product judgment is the bottleneck is 3-6 months. Every quality gate, eval criterion, and template you build today is taste that persists after the window closes.

---

*Boris's golden age of the generalist: the role distinctions — PM, designer, engineer, researcher — are collapsing. Not because those skills don't matter, but because one person can now hold more of them simultaneously than ever before. The people winning aren't the deepest specialists. They're the ones willing to pick up whatever hat the problem needs and use every tool available to wear it well.*
