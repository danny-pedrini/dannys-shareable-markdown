# How to Create Custom Skills (Help Center)

> **Source:** https://support.claude.com/en/articles/12512198-how-to-create-custom-skills
> **Fetched:** 2026-06-01
> **Authoritative source:** Claude Help Center

---

Custom skills enhance Claude with specialized knowledge and workflows. Skills function best when they "Solve a specific, repeatable task" with "clear instructions that Claude can follow."

## Core Structure: The SKILL.md File

Every skill requires a directory with a minimum `SKILL.md` file. This file begins with YAML frontmatter containing required metadata:

**Required Fields:**
- **name:** Human-friendly identifier (maximum 64 characters)
- **description:** Explains purpose and usage (maximum 200 characters)

The description is critical because Claude relies on it to determine when to activate your skill.

**Optional Fields:**
- **dependencies:** Required software packages (e.g., python>=3.8, pandas>=1.5.0)

The markdown body following metadata serves as supplemental detail that Claude accesses after reading the metadata section.

## Adding Resources

For extensive information, create additional files within your skill directory, such as `REFERENCE.md`. Reference these files in `SKILL.md` to help Claude decide whether to access them during execution.

## Adding Scripts

Advanced skills can include executable code files. Supported technologies include:

- Python (with pandas, numpy, matplotlib)
- JavaScript/Node.js
- File editing packages
- Visualization tools

**Important:** All dependencies must be pre-installed; runtime package installation isn't supported for API Skills.

## Packaging Your Skill

Follow this structure for proper ZIP file organization:

```
my-skill.zip
└── my-skill/
    ├── skill.md
    └── resources/
```

Ensure the folder name matches your skill's name, and the ZIP contains the skill folder at its root level.

## Testing Protocol

**Before Uploading:**
1. Review `SKILL.md` for clarity
2. Verify the description accurately reflects when Claude should use it
3. Confirm all referenced files exist in correct locations
4. Test with example prompts

**After Uploading:**
1. Enable the skill in Customize > Skills
2. Try multiple prompts that should trigger it
3. Review Claude's thinking to confirm it loads the skill
4. Refine the description if Claude doesn't use it appropriately

## Best Practices

- Maintain focus by creating separate skills for different workflows
- Write specific descriptions that guide Claude's invocation decisions
- Begin with basic Markdown instructions before adding complex scripts
- Include example inputs and outputs
- Test incrementally after each significant change
- Recognize that skills compose together; Claude can use multiple skills simultaneously
- Reference the Agent Skills specification at agentskills.io for cross-platform compatibility

## Security Considerations

- Exercise caution when adding scripts
- Never hardcode sensitive information (API keys, passwords)
- Review downloaded skills before enabling
- Use appropriate MCP connections for external services

## Availability

Skills are available across free, Pro, Max, Team, and Enterprise plans, plus Claude Code users and all API users with code execution tools enabled.
