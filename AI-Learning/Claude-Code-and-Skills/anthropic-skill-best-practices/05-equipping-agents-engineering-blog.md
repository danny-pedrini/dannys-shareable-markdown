# Equipping Agents for the Real World with Agent Skills

> **Source:** https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
> **Fetched:** 2026-06-01
> **Authoritative source:** Anthropic Engineering Blog (published October 16, 2025)

---

## What Are Agent Skills?

Agent Skills are "organized folders of instructions, scripts, and resources that agents can discover and load dynamically to perform better at specific tasks." The metaphor is straightforward: building a skill resembles creating an onboarding guide for a new employee, allowing anyone to specialize general-purpose agents with composable capabilities.

## Anatomy of a Skill

### Core Structure

Each skill is a directory containing a `SKILL.md` file. This file must begin with YAML frontmatter including required metadata: `name` and `description`. These metadata elements are preloaded into the system prompt at startup, representing the first level of "progressive disclosure."

### Progressive Disclosure Design

The architecture follows a tiered approach:

- **Level 1**: Skill metadata (name and description) help Claude determine when to use a skill
- **Level 2**: Full `SKILL.md` content loads if Claude deems the skill relevant
- **Level 3+**: Additional bundled files (referenced from `SKILL.md`) load only as needed

This design principle mirrors a well-organized manual with table of contents, chapters, and appendices.

## Real-World Example: PDF Skills

The blog illustrates concepts using a PDF skill that enhances Claude's document editing abilities. While Claude understands PDFs well, the skill enables direct manipulation capabilities like form filling. The PDF skill bundles two additional files (`reference.md` and `forms.md`) alongside the core skill, keeping the primary file lean while providing comprehensive functionality.

## Context Window Management

Skills integrate thoughtfully with context windows. The sequence works as follows:

1. Context window starts with core system prompt, skill metadata, and user message
2. Claude invokes a Bash tool to read `SKILL.md` contents when triggered
3. Claude selectively reads additional bundled files as needed
4. Task proceeds with loaded relevant instructions

This approach means "the amount of context that can be bundled into a skill is effectively unbounded" since agents with filesystem and code execution tools needn't read everything into their context window.

## Code Execution Integration

Skills can include executable code that Claude runs as tools. Certain operations — sorting algorithms, for instance — function more efficiently and reliably through deterministic code execution rather than token generation. The PDF skill exemplifies this by including a Python script that extracts form fields without requiring the full PDF to be loaded into context.

## Development and Evaluation Guidelines

### Starting Points

- **Identify gaps**: Run agents on representative tasks and observe where additional context helps
- **Build incrementally**: Address shortcomings progressively rather than comprehensively upfront

### Scaling Considerations

- Split unwieldy `SKILL.md` files into separate files when needed
- Keep mutually exclusive contexts separate to reduce token usage
- Use code as both executable tools and documentation, clarifying whether Claude should run or read scripts

### Iterative Improvement

- Monitor how Claude uses skills in real scenarios
- Pay special attention to skill names and descriptions — Claude relies on these when deciding triggers
- Ask Claude to self-reflect on missteps and capture successful approaches into reusable context

## Security Considerations

The blog emphasizes installing skills only from trusted sources. When evaluating less-trusted skills:

- Read bundled file contents thoroughly
- Pay particular attention to code dependencies and resources
- Monitor instructions directing Claude to connect with external, potentially untrusted networks

## Platform Support and Future Directions

Agent Skills are supported across Claude.ai, Claude Code, the Claude Agent SDK, and the Claude Developer Platform.

Future enhancements will support the complete lifecycle of creating, editing, discovering, and sharing skills.

The blog expresses excitement about potential complementary relationships with Model Context Protocol (MCP) servers for teaching agents complex workflows involving external tools. Looking further ahead, Anthropic hopes to enable agents to create, edit, and evaluate their own skills, allowing codification of behavioral patterns into reusable capabilities.

## Key Takeaway

Agent Skills leverage simplicity — both conceptual and in format — to democratize agent customization, making it accessible to organizations, developers, and end users seeking to build specialized agents with new capabilities.
