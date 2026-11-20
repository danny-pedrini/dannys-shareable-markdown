# Danny Pedrini's AI PM workspace

This is the AI setup I use every day as a Staff PM at Hims & Hers, where I work on AI in clinical care: tools that help providers make treatment decisions and write to patients. It holds the Claude Code skills, reviewer agents, rules, and templates that turn my workspace into a copilot. It syncs from my private workspace every 15 minutes, so what you see is what I actually run, not a cleaned-up demo.

I'm Danny Pedrini. You can find me on [LinkedIn](https://www.linkedin.com/in/danielpedrini/).

## Where to start

If you're short on time, start with these five.

1. **[AGENTS.md](AGENTS.md)** is the operating manual every AI session reads first. It tells the model to push back when I'm wrong, to stop and ask rather than guess when a source won't load, and to run a writing checklist before it hands me anything.
2. **[prd-generator](.claude/skills/prd-generator/SKILL.md)** writes and revises PRDs through a gated loop. It asks all its questions in one batch and plans with parallel subagents. An independent QA judge checks every phase before a reviewer round and a final revision. Its [37 evals](.claude/skills/prd-generator/evals.md) came from real misses, one rule at a time.
3. **[provider-draft-failure-modes](.claude/skills/provider-draft-failure-modes/SKILL.md)** turns provider feedback on AI-drafted patient messages into prioritized bugs. Severity and frequency set priority. An evidence ledger counts every failure mode across rounds, and I approve each ticket before anything gets filed.
4. **[The reviewer agents](.claude/agents/)** are 12 expert personas I run against my own docs before anyone else sees them. They include a licensed telehealth prescriber, a clinical quality executive, an AI engineer, and a VP of Product. Each one returns Must Fix, Should Fix, and Consider.
5. **[Token-spend analysis](AI-Learning/Claude-Code-and-Skills/Token-Spend/)** is how I measured what my AI use costs and planned cuts that keep every quality check.

## How the skills are built

These rules show up in almost every skill, because I learned each one the hard way.

- **The model doesn't grade its own homework.** Anything a stakeholder will read goes through an independent QA subagent before it reaches me.
- **Feedback becomes an eval.** When I catch a problem in a skill's output, I write a general rule a check can test, rather than patching that one document. The skills in this repo carry more than 260 evals between them.
- **A human approves anything that leaves the building.** Skills that file tickets, update docs, or draft messages stop at a gate and wait for me.
- **No inference from missing sources.** If Slack, Confluence, or a Google Doc fails to load, the skill says so and stops. It never fills the gap with a plausible guess.
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
