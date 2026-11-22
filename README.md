# Danny Pedrini's AI PM workspace

I'm a Staff PM at Hims & Hers, where I ship LLM features into the software licensed clinicians use to treat patients. This repo is the agent system I run my own product work on: 25 Claude Code skills, 12 reviewer agents, and the evals, tracing tools, and rules that keep them honest. It syncs from my private workspace every 15 minutes, so what you see is what I actually run, not a demo.

I build these skills the way I think any AI product should be built. I name the ways a skill will fail before I write its prompt, and those failures become its first evals. By default every run is logged, and a separate model checks the output instead of the one that wrote it. Each real miss becomes a new eval, so a skill gets better every time I use it.

You can find me on [LinkedIn](https://www.linkedin.com/in/danielpedrini/).

## Start here: agent-architect

[agent-architect](.claude/skills/agent-architect/SKILL.md) is the skill I use to build my other skills. You describe a job, and it takes you through discovery, design, drafting, evaluation, and delivery. It treats a new skill as a product that will be measured and improved, not a prompt that's finished once it's written. Here's what it designs into the skills it builds:

- **Failure modes first.** Discovery ends with a list of the ways the agent is likely to fail. When a skill has evals, those failure modes become the first ones, so it has a test suite before it has a single run. Skills that run on their own always get evals.
- **The right architecture for the job.** It chooses among seven patterns, from a single prompt to an autonomous loop that runs on a schedule and surfaces only the exceptions it can't resolve. A loop has to pass evals at every step, because no human is watching the middle.
- **Pass/fail evals, checked by code where possible.** Each eval tests one failure mode and returns pass or fail. There are no Likert scales and no vague "helpfulness" scores. Code checks come first, and an LLM judge is used where code can't do the job.
- **An independent grader.** When a skill includes QA or evals, the model that produces an output never grades it. A separate subagent with its own context checks the work, after a [linter](.claude/skills/agent-architect/scripts/lint_skill.py) has checked the skill's structure.
- **Observability on by default.** Every run appends a line to a log and writes a JSON trace of its inputs, decisions, tool calls, and eval results. A [script](.claude/skills/agent-architect/references/verify_observability.py) runs eight checks on each trace, and then a fresh agent confirms the trace matches what happened. When a run goes wrong, I diagnose it from the record instead of from memory.
- **Autonomy that's earned.** Each decision in a workflow is labeled as the agent's call, a human's call, or one that graduates. A graduating decision starts with human review and moves to the agent once it clears a bar set up front, such as the human changing nothing on 90% of items across 10 runs. A demotion rule, such as any critical failure, moves it back.

## How a skill gets better after it ships

1. The skill runs, and its eval runner checks the output against the skill's evals file before I see anything.
2. The run's trace records what happened, including which evals passed.
3. I review the output and any flags.
4. When I catch a miss, [evals-advisor](.claude/skills/evals-advisor/SKILL.md) reads the run and proposes a pass/fail eval for that exact failure. If the instructions were just unclear, it proposes a prompt fix instead.
5. I adopt or reject each proposal. Adopted evals run automatically on every future run.

The skills in this repo carry more than 260 evals between them, most written at design time or adopted this way. [prd-generator's 37 evals](.claude/skills/prd-generator/evals.md) mix code checks, like catching unfilled template text, with judge checks, like catching claims the sources don't support. Run traces stay in my private workspace because they hold internal content, but the [trace schema](.claude/skills/agent-architect/references/observability-templates.md) is here.

## More worth a look

1. **[prd-generator](.claude/skills/prd-generator/SKILL.md)** writes and revises PRDs through a gated loop. It asks all its questions in one batch and plans with parallel subagents. An independent QA judge checks every phase before a reviewer round and a final revision.
2. **[The reviewer agents](.claude/agents/)** are 12 expert personas I run against my own docs before anyone else sees them. They cover frontend, backend, AI, and data engineering, along with architecture, design, program management, and product leadership. Three are clinical and care operations experts for my current domain. Each one returns Must Fix, Should Fix, and Consider.
3. **[Error analysis for a live LLM feature](.claude/skills/provider-draft-failure-modes/SKILL.md)** sorts user feedback (ratings, edits, and eval failures) into failure modes and counts each one across rounds. Severity and frequency set each bug's priority, and I approve every ticket before it's filed.
4. **[AGENTS.md](AGENTS.md)** is the operating manual every AI session reads first. It tells the model to push back when I'm wrong, to stop and ask rather than guess when a source won't load, and to run a writing checklist before it hands me anything.

## Rules every skill follows

- **A human approves anything that leaves the building.** Skills that file tickets, update docs, or draft messages stop at a gate and wait for me.
- **No inference from missing sources.** If Slack, Confluence, or a Google Doc fails to load, the skill says so and stops. It never fills the gap with a plausible guess.
- **Cost gets measured like quality.** The [token-spend analysis](AI-Learning/Claude-Code-and-Skills/Token-Spend/) is how I measured what my AI use costs and planned cuts that keep every quality check.
- **It has to sound like a person wrote it.** [danny-voice-exemplar.md](danny-voice-exemplar.md) shows what my writing sounds like, and [forbidden-writing-patterns.md](forbidden-writing-patterns.md) lists the AI tells every draft gets searched for.

## What's in the repo

| Folder | What's in it |
| --- | --- |
| [`.claude/skills/`](.claude/skills/) | 25 skills: PRDs, acceptance tests, feature briefs, impact sizing, dashboard requirements, launch plans, decks, journey maps, prototypes, meeting transcription, and more |
| [`.claude/agents/`](.claude/agents/) | 12 reviewer personas, plus the lean worker and judge agents the skills launch |
| [`Templates/`](Templates/) | The PRD, feature brief, acceptance testing, and dashboard templates the skills fill in |
| [`AI-Learning/`](AI-Learning/) | My AI learning curriculum, notes on evals, agents, and systems thinking, and a [reading list](AI-Learning/Reading-List.md) of the outside guides I learned from |
| [`.scripts/`](.scripts/) | The automation that runs on its own: workspace sync, a daily Substack briefing, and the sync that publishes this repo |

Skills that call Slack, Jira, Confluence, or Google Workspace need those connections to run, so read them as worked examples more than drop-in tools.

## What's different in this public copy

My private workspace is full of real colleagues and internal company work, so the copy you're reading is scrubbed on the way out.

- Colleagues appear as their roles, like "[Clinical Ops lead]," instead of their names.
- Links to internal docs, dashboards, and tickets are removed.
- Files that hold internal material are replaced with a short note saying what they do.
- Dollar figures in skill examples are altered, but they keep their ratios so the worked examples still add up.
- Articles by other writers appear as short pointer files, each with a link to the original, in the folder where I filed them. The [reading list](AI-Learning/Reading-List.md) collects them in one place.

The scrub is automated too. [shareable-sync.sh](.scripts/shareable-sync.sh) copies an allowlist of folders. Then [shareable-scrub.py](.scripts/shareable-scrub.py) rewrites the copy and checks it, and it refuses to push if a known name, internal link, or work email survives.
