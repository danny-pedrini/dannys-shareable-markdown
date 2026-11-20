# Anthropic Skill Best Practices — Reference Collection

> **Fetched:** 2026-06-01
> **Purpose:** Canonical collection of Anthropic's official documentation on creating, structuring, and optimizing Agent Skills for Claude Code, claude.ai, and the Claude API.

## Contents

| # | File | Source | Description |
|---|------|--------|-------------|
| 1 | [01-agent-skills-overview.md](01-agent-skills-overview.md) | [platform.claude.com](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) | Foundational concepts: what skills are, progressive disclosure architecture, three-level loading, security, platform availability |
| 2 | [02-skill-authoring-best-practices.md](02-skill-authoring-best-practices.md) | [platform.claude.com](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | Core authoring guide: conciseness, degrees of freedom, naming, descriptions, progressive disclosure patterns, workflows, feedback loops, eval-driven development, anti-patterns, checklist |
| 3 | [03-claude-code-skills-guide.md](03-claude-code-skills-guide.md) | [code.claude.com](https://code.claude.com/docs/en/skills) | Claude Code-specific: skill directories, frontmatter reference, dynamic context injection, subagent execution, invocation control, arguments, visual output, troubleshooting |
| 4 | [04-creating-custom-skills-help-center.md](04-creating-custom-skills-help-center.md) | [support.claude.com](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) | Help center tutorial: SKILL.md structure, adding resources/scripts, packaging, testing protocol, security |
| 5 | [05-equipping-agents-engineering-blog.md](05-equipping-agents-engineering-blog.md) | [anthropic.com/engineering](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | Engineering blog: design philosophy, progressive disclosure rationale, context window management, code execution integration, future directions |
| 6 | [06-anthropics-skills-github-repo.md](06-anthropics-skills-github-repo.md) | [github.com/anthropics/skills](https://github.com/anthropics/skills) | Public skills repository: README, installation instructions, example skills catalog, plugin/API/claude.ai usage |

## How to use this collection

- **Starting from scratch?** Read #1 (overview) then #2 (best practices).
- **Building for Claude Code specifically?** Read #3 after the above.
- **Want the design philosophy?** Read #5 (engineering blog).
- **Need the quick-start tutorial?** Read #4 (help center).
- **Looking for example skills to reference?** Read #6 (GitHub repo).

## Key cross-cutting principles

1. **Progressive disclosure** — metadata loads at startup (~100 tokens), SKILL.md loads on trigger, reference files load on demand
2. **Conciseness is a constraint** — SKILL.md body under 500 lines; context window is a shared resource
3. **Eval-driven development** — measure gaps first, write minimal instructions, iterate from real usage
4. **Descriptions are critical** — third person, specific, include both "what" and "when to use"
5. **References one level deep** — no nested file references; all links from SKILL.md directly
6. **Test across models** — Haiku needs more guidance, Opus needs less
