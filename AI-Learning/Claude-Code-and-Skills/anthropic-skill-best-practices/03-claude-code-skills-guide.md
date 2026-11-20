# Extend Claude with Skills (Claude Code)

> **Source:** https://code.claude.com/docs/en/skills
> **Fetched:** 2026-06-01
> **Authoritative source:** Claude Code official documentation

---

Skills extend what Claude can do. Create a `SKILL.md` file with instructions, and Claude adds it to its toolkit. Claude uses skills when relevant, or you can invoke one directly with `/skill-name`.

Create a skill when you keep pasting the same instructions, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact. Unlike CLAUDE.md content, a skill's body loads only when it's used, so long reference material costs almost nothing until you need it.

**Custom commands have been merged into skills.** A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way. Your existing `.claude/commands/` files keep working. Skills add optional features: a directory for supporting files, frontmatter to control whether you or Claude invokes them, and the ability for Claude to load them automatically when relevant.

Claude Code skills follow the [Agent Skills](https://agentskills.io) open standard, which works across multiple AI tools. Claude Code extends the standard with additional features like invocation control, subagent execution, and dynamic context injection.

## Bundled skills

Claude Code includes a set of bundled skills that are available in every session, including `/code-review`, `/batch`, `/debug`, `/loop`, and `/claude-api`. Unlike most built-in commands, which execute fixed logic directly, bundled skills are prompt-based: they give Claude detailed instructions and let it orchestrate the work using its tools.

### Run and verify your app

Three bundled skills work together to launch your app and confirm changes against the running app instead of just tests:

| Skill | Purpose |
|:------|:--------|
| `/run` | Launch and drive your app to see a change working |
| `/verify` | Build and run your app to confirm a code change does what it should, without falling back to tests or type checks |
| `/run-skill-generator` | Teach `/run` and `/verify` how to build and launch your project |

`/run` and `/verify` work without setup. They infer the launch from your project type (CLI, server, TUI, browser-driven) and from what's in your README, `package.json`, or `Makefile`. That inference gets unreliable for projects that need anything beyond a standard launch: a database, an env file, a graphical session, a multi-step build.

`/run-skill-generator` records the recipe instead. It gets your app running from a clean environment, captures what worked (the install commands, the env vars, the launch script), and commits it as a per-project skill at `.claude/skills/run-<name>/`. After that, `/run`, `/verify`, and any other agent in the repo follow the recorded recipe instead of rediscovering it. Run `/run-skill-generator` once per project, and again if the build or launch process changes.

## Getting started

### Create your first skill

This example creates a skill that summarizes the uncommitted changes in your git repository and flags anything risky. It pulls the live diff into the prompt before Claude reads it, so the response is grounded in your actual working tree rather than what Claude can guess from open files.

**Step 1: Create the skill directory**

```bash
mkdir -p ~/.claude/skills/summarize-changes
```

**Step 2: Write SKILL.md**

Save this to `~/.claude/skills/summarize-changes/SKILL.md`:

```yaml
---
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks you notice such as missing error handling, hardcoded values, or tests that need updating. If the diff is empty, say there are no uncommitted changes.
```

The `` !`git diff HEAD` `` line uses dynamic context injection: Claude Code runs the command and replaces the line with its output before Claude sees the skill content.

**Step 3: Test the skill**

Let Claude invoke it automatically by asking "What did I change?" or invoke directly with `/summarize-changes`.

### Where skills live

| Location | Path | Applies to |
|:---------|:-----|:-----------|
| Enterprise | See managed settings | All users in your organization |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<skill-name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Where plugin is enabled |

When skills share the same name across levels, enterprise overrides personal, and personal overrides project. Plugin skills use a `plugin-name:skill-name` namespace, so they cannot conflict with other levels.

#### Live change detection

Claude Code watches skill directories for file changes. Adding, editing, or removing a skill takes effect within the current session without restarting. Creating a top-level skills directory that did not exist when the session started requires restarting Claude Code.

#### Automatic discovery from parent and nested directories

Project skills load from `.claude/skills/` in your starting directory and in every parent directory up to the repository root. When you work with files in subdirectories, Claude Code also discovers skills from nested `.claude/skills/` directories on demand. This supports monorepo setups where packages have their own skills.

Each skill is a directory with `SKILL.md` as the entrypoint:

```text
my-skill/
├── SKILL.md           # Main instructions (required)
├── template.md        # Template for Claude to fill in
├── examples/
│   └── sample.md      # Example output showing expected format
└── scripts/
    └── validate.sh    # Script Claude can execute
```

## Configure skills

### Types of skill content

**Reference content** adds knowledge Claude applies to your current work. Conventions, patterns, style guides, domain knowledge. Runs inline so Claude can use it alongside conversation context.

```yaml
---
name: api-conventions
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
- Include request validation
```

**Task content** gives Claude step-by-step instructions for a specific action. Add `disable-model-invocation: true` to prevent Claude from triggering it automatically.

```yaml
---
name: deploy
description: Deploy the application to production
context: fork
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite
2. Build the application
3. Push to the deployment target
```

Keep the body concise. Once a skill loads, its content stays in context across turns, so every line is a recurring token cost.

### Frontmatter reference

| Field | Required | Description |
|:------|:---------|:------------|
| `name` | No | Display name shown in skill listings. Defaults to directory name. |
| `description` | Recommended | What the skill does and when to use it. Claude uses this to decide when to apply the skill. Truncated at 1,536 characters. |
| `when_to_use` | No | Additional context for when Claude should invoke the skill. Appended to `description`. |
| `argument-hint` | No | Hint shown during autocomplete. Example: `[issue-number]` or `[filename] [format]`. |
| `arguments` | No | Named positional arguments for `$name` substitution. |
| `disable-model-invocation` | No | Set to `true` to prevent Claude from automatically loading this skill. Default: `false`. |
| `user-invocable` | No | Set to `false` to hide from the `/` menu. Default: `true`. |
| `allowed-tools` | No | Tools Claude can use without asking permission when this skill is active. |
| `disallowed-tools` | No | Tools removed from Claude's available pool while this skill is active. |
| `model` | No | Model to use when this skill is active. |
| `effort` | No | Effort level when this skill is active. Options: `low`, `medium`, `high`, `xhigh`, `max`. |
| `context` | No | Set to `fork` to run in a forked subagent context. |
| `agent` | No | Which subagent type to use when `context: fork` is set. |
| `hooks` | No | Hooks scoped to this skill's lifecycle. |
| `paths` | No | Glob patterns that limit when this skill is activated. |
| `shell` | No | Shell to use for inline commands. Accepts `bash` (default) or `powershell`. |

### Available string substitutions

| Variable | Description |
|:---------|:------------|
| `$ARGUMENTS` | All arguments passed when invoking the skill |
| `$ARGUMENTS[N]` | Access a specific argument by 0-based index |
| `$N` | Shorthand for `$ARGUMENTS[N]` |
| `$name` | Named argument declared in the `arguments` frontmatter list |
| `${CLAUDE_SESSION_ID}` | The current session ID |
| `${CLAUDE_EFFORT}` | The current effort level |
| `${CLAUDE_SKILL_DIR}` | The directory containing the skill's SKILL.md file |

### Add supporting files

Skills can include multiple files in their directory. Large reference docs, API specifications, or example collections don't need to load into context every time the skill runs.

```text
my-skill/
├── SKILL.md (required - overview and navigation)
├── reference.md (detailed API docs - loaded when needed)
├── examples.md (usage examples - loaded when needed)
└── scripts/
    └── helper.py (utility script - executed, not loaded)
```

Reference supporting files from `SKILL.md` so Claude knows what each file contains and when to load it.

**Keep `SKILL.md` under 500 lines.** Move detailed reference material to separate files.

### Control who invokes a skill

* **`disable-model-invocation: true`**: Only you can invoke the skill. Use for workflows with side effects.
* **`user-invocable: false`**: Only Claude can invoke the skill. Use for background knowledge.

| Frontmatter | You can invoke | Claude can invoke | When loaded into context |
|:------------|:---------------|:------------------|:------------------------|
| (default) | Yes | Yes | Description always in context, full skill loads when invoked |
| `disable-model-invocation: true` | Yes | No | Description not in context, full skill loads when you invoke |
| `user-invocable: false` | No | Yes | Description always in context, full skill loads when invoked |

### Skill content lifecycle

When you or Claude invoke a skill, the rendered SKILL.md content enters the conversation as a single message and stays there for the rest of the session. Claude Code does not re-read the skill file on later turns.

Auto-compaction carries invoked skills forward within a token budget. When conversation is summarized, Claude Code re-attaches the most recent invocation of each skill after the summary, keeping the first 5,000 tokens of each. Re-attached skills share a combined budget of 25,000 tokens. Claude Code fills this budget starting from the most recently invoked skill.

### Pre-approve tools for a skill

The `allowed-tools` field grants permission for the listed tools while the skill is active. It does not restrict which tools are available.

```yaml
---
name: commit
description: Stage and commit the current changes
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---
```

### Pass arguments to skills

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit
```

When you run `/fix-issue 123`, Claude receives "Fix GitHub issue 123 following our coding standards..."

## Advanced patterns

### Inject dynamic context

The `` !`<command>` `` syntax runs shell commands before the skill content is sent to Claude. The command output replaces the placeholder.

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

When this skill runs:
1. Each `` !`<command>` `` executes immediately (before Claude sees anything)
2. The output replaces the placeholder in the skill content
3. Claude receives the fully-rendered prompt with actual data

For multi-line commands, use a fenced code block opened with ` ```! `:

````markdown
## Environment
```!
node --version
npm --version
git status --short
```
````

To disable this behavior, set `"disableSkillShellExecution": true` in settings.

### Run skills in a subagent

Add `context: fork` to your frontmatter when you want a skill to run in isolation.

| Approach | System prompt | Task | Also loads |
|:---------|:-------------|:-----|:-----------|
| Skill with `context: fork` | From agent type | SKILL.md content | CLAUDE.md, except when the agent is Explore or Plan |
| Subagent with `skills` field | Subagent's markdown body | Claude's delegation message | Preloaded skills + CLAUDE.md |

**Example: Research skill using Explore agent**

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

The `agent` field specifies which subagent configuration to use. Options include built-in agents (`Explore`, `Plan`, `general-purpose`) or any custom subagent from `.claude/agents/`. If omitted, uses `general-purpose`.

### Restrict Claude's skill access

Three ways to control which skills Claude can invoke:

**Disable all skills** by denying the Skill tool in `/permissions`:
```
Skill
```

**Allow or deny specific skills** using permission rules:
```
# Allow only specific skills
Skill(commit)
Skill(review-pr *)

# Deny specific skills
Skill(deploy *)
```

**Hide individual skills** by adding `disable-model-invocation: true` to their frontmatter.

### Override skill visibility from settings

The `skillOverrides` setting controls skill visibility from settings instead of the skill's own frontmatter:

| Value | Listed to Claude | In `/` menu |
|:------|:----------------|:------------|
| `"on"` | Name and description | Yes |
| `"name-only"` | Name only | Yes |
| `"user-invocable-only"` | Hidden | Yes |
| `"off"` | Hidden | Hidden |

```json
{
  "skillOverrides": {
    "legacy-context": "name-only",
    "deploy": "off"
  }
}
```

## Share skills

* **Project skills**: Commit `.claude/skills/` to version control
* **Plugins**: Create a `skills/` directory in your plugin
* **Managed**: Deploy organization-wide through managed settings

### Generate visual output

Skills can bundle and run scripts in any language, giving Claude capabilities beyond what's possible in a single prompt. One powerful pattern is generating visual output: interactive HTML files that open in your browser for exploring data, debugging, or creating reports.

This pattern works for any visual output: dependency graphs, test coverage reports, API documentation, or database schema visualizations. The bundled script does the work while Claude handles orchestration.

## Troubleshooting

### Skill not triggering

1. Check the description includes keywords users would naturally say
2. Verify the skill appears in `What skills are available?`
3. Try rephrasing your request to match the description more closely
4. Invoke it directly with `/skill-name` if the skill is user-invocable

### Skill triggers too often

1. Make the description more specific
2. Add `disable-model-invocation: true` if you only want manual invocation

### Skill descriptions are cut short

All skill names are always included, but if you have many skills, descriptions are shortened to fit the character budget, which can strip the keywords Claude needs to match your request. The budget scales at 1% of the model's context window.

To raise the budget, set the `skillListingBudgetFraction` setting (e.g. `0.02` = 2%) or the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable. To free budget for other skills, set low-priority entries to `"name-only"` in `skillOverrides`.

## Related resources

* **Debug your configuration**: diagnose why a skill isn't appearing or triggering
* **Subagents**: delegate tasks to specialized agents
* **Plugins**: package and distribute skills with other extensions
* **Hooks**: automate workflows around tool events
* **Memory**: manage CLAUDE.md files for persistent context
* **Commands**: reference for built-in commands and bundled skills
* **Permissions**: control tool and skill access
