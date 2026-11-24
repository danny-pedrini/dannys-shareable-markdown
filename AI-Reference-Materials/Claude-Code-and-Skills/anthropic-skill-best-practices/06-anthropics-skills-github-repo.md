# Anthropic Skills GitHub Repository

> **Source:** https://github.com/anthropics/skills
> **Fetched:** 2026-06-01
> **Authoritative source:** Anthropic official GitHub repository

---

## About

This repository contains skills that demonstrate what's possible with Claude's skills system. These skills range from creative applications (art, music, design) to technical tasks (testing web apps, MCP server generation) to enterprise workflows (communications, branding, etc.).

Each skill is self-contained in its own folder with a `SKILL.md` file containing the instructions and metadata that Claude uses. Browse through these skills to get inspiration for your own skills or to understand different patterns and approaches.

> **Note:** This repository contains Anthropic's implementation of skills for Claude. For information about the Agent Skills standard, see [agentskills.io](http://agentskills.io).

## Skills Overview

Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. Skills teach Claude how to complete specific tasks in a repeatable way, whether that's creating documents with your company's brand guidelines, analyzing data using your organization's specific workflows, or automating personal tasks.

### Related Resources

- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Equipping agents for the real world with Agent Skills](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

## Repository Structure

- **[./skills](https://github.com/anthropics/skills/tree/main/skills)**: Skill examples for Creative & Design, Development & Technical, Enterprise & Communication, and Document Skills
- **[./spec](https://github.com/anthropics/skills/tree/main/spec)**: The Agent Skills specification
- **[./template](https://github.com/anthropics/skills/tree/main/template)**: Skill template

### Document Skills (Source-Available)

The repository includes the document creation & editing skills that power Claude's document capabilities under the hood:

- **[skills/docx](https://github.com/anthropics/skills/tree/main/skills/docx)** — Word document creation and editing
- **[skills/pdf](https://github.com/anthropics/skills/tree/main/skills/pdf)** — PDF document generation
- **[skills/pptx](https://github.com/anthropics/skills/tree/main/skills/pptx)** — PowerPoint presentation creation
- **[skills/xlsx](https://github.com/anthropics/skills/tree/main/skills/xlsx)** — Excel spreadsheet creation

These are source-available (not open source) but shared as a reference for more complex skills that are actively used in a production AI application.

### Disclaimer

These skills are provided for demonstration and educational purposes only. While some of these capabilities may be available in Claude, the implementations and behaviors you receive from Claude may differ from what is shown in these skills.

## Installation

### Claude Code

Register this repository as a Claude Code Plugin marketplace:

```bash
/plugin marketplace add anthropics/skills
```

Then install specific skill sets:

1. Select `Browse and install plugins`
2. Select `anthropic-agent-skills`
3. Select `document-skills` or `example-skills`
4. Select `Install now`

Or directly install via:

```bash
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

### claude.ai

These example skills are already available to paid plans in Claude.ai.

To use any skill from this repository or upload custom skills, follow the instructions in [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude#h_a4222fa77b).

### Claude API

Use Anthropic's pre-built skills, and upload custom skills, via the Claude API. See the [Skills API Quickstart](https://docs.claude.com/en/api/skills-guide#creating-a-skill) for more.

## Creating a Basic Skill

Skills are simple to create — just a folder with a `SKILL.md` file containing YAML frontmatter and instructions. Use the **template-skill** in this repository as a starting point:

```yaml
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Add your instructions here that Claude will follow when this skill is active]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

The frontmatter requires only two fields:

- `name` — A unique identifier for your skill (lowercase, hyphens for spaces)
- `description` — A complete description of what the skill does and when to use it

The markdown content below contains the instructions, examples, and guidelines that Claude will follow.

## Partner Skills

- **Notion** — [Notion Skills for Claude](https://www.notion.so/notiondevs/Notion-Skills-for-Claude-28da4445d27180c7af1df7d8615723d0)

## Repository Statistics

- **Stars**: ~145k
- **Language Breakdown**: Python 84.4%, HTML 12.4%, Shell 1.9%, JavaScript 1.3%
- **License**: Apache 2.0 (example skills); source-available (document skills)
