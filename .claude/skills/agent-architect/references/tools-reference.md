# Claude Code Tools Reference

Reference file loaded by agent-architect when Phase 2 designs a tool set (Steps 2.5 and D3), or when the agent calls external APIs. The stop rule in SKILL.md Step 2.5b governs every failure path below.

### Claude Code Tools Reference (Platform-Specific)

**Use this section when designing tool architecture in Phase 2. Map your agent's needs to Claude Code's actual toolset.**

#### Core Claude Code Tools

| Tool | Category | When to Use | When NOT to Use | Failure Modes |
|------|----------|-------------|-----------------|---------------|
| `Read` | File System | Reading known files, inspecting code, loading context | Large binary files, files you haven't verified exist | File not found, permission denied, file too large |
| `Write` | File System | Creating new files, overwriting entire files | Partial edits (use `Edit`), files you haven't read first | Path doesn't exist, permission denied |
| `Edit` | File System | Targeted edits to existing files, find-and-replace operations | Creating new files, large rewrites (use `Write`) | `old_string` not found, not unique, file doesn't exist |
| `Bash` (e.g., `rm`) | File System | Removing files no longer needed (use carefully — destructive) | Files that might be referenced elsewhere | File not found, permission denied |
| `Bash` (e.g., `ls`) | File System | Exploring directory structure, finding files | Deep recursive searches (use `Glob`) | Directory doesn't exist |
| `Glob` | File System | Finding files by name pattern (e.g., `*.md`, `test_*.py`) | Searching file contents (use `Grep`) | No matches found |
| `Grep` | Search | Exact text/regex matches, finding specific strings, symbol lookups | Semantic/meaning-based searches (use an `Explore` subagent or code-explorer MCP) | Pattern too broad, no matches |
| `Explore` subagent / code-explorer MCP | Search/RAG | Finding code by meaning, "how does X work?" questions, exploring unfamiliar code | Exact string matches (use `Grep`), known file paths (use `Read`) | Query too vague, results not relevant |
| `WebSearch` / `WebFetch` | Web Access | Real-time information, current events, external documentation | Information that should be in the codebase, sensitive queries | Rate limits, no relevant results |
| `Bash` | Code Execution | Running scripts, CLI tools, build commands, git operations | File operations (use dedicated tools), long explanations (use response text) | Command fails, timeout, permission denied, sandbox restrictions |
| `TodoWrite` | Memory/State | Tracking multi-step tasks, complex workflows, showing progress | Simple single-step tasks, operational sub-tasks (linting, searching) | N/A |

#### Claude Code Tool Selection Decision Tree

```
Agent needs to...
├── READ existing content
│   ├── Know the file path? → Read
│   ├── Know the file name pattern? → Glob → Read
│   ├── Know exact text to find? → Grep
│   └── Know the concept but not location? → Explore subagent / code-explorer MCP
├── WRITE/MODIFY content
│   ├── Create new file? → Write
│   ├── Replace entire file? → Read first → Write
│   ├── Edit specific part? → Edit
│   └── Delete file? → Bash (`rm` — destructive, use carefully)
├── EXPLORE structure
│   ├── Single directory? → Bash (`ls`)
│   └── Find files by pattern? → Glob
├── EXECUTE commands
│   └── Run CLI/scripts? → Bash
└── ACCESS external data
    ├── Web/current info? → WebSearch / WebFetch
    └── Integrated services? → MCP tools (see below)
```

#### MCP Tools (Model Context Protocol)

**Available MCP Servers in This Workspace:**

| MCP Server | Primary Use Cases | Key Tools | When to Recommend Adding |
|------------|-------------------|-----------|-------------------------|
| **GitHub** | PR management, issue tracking, code search across repos, repository operations | `mcp_github_*` (create_pull_request, list_issues, search_code, etc.) | Agent needs to interact with GitHub repos, PRs, or issues |
| **Figma** | Design data extraction, component information, image downloads | `mcp_figma_get_figma_data`, `mcp_figma_download_figma_images` | Agent needs to reference or extract from Figma designs |
| **Neon** | PostgreSQL database operations, schema management, query execution | `mcp_Neon_run_sql`, `mcp_Neon_describe_table_schema`, etc. | Agent needs database access or SQL operations |
| **Atlassian** | Jira/Confluence integration, ticket management, documentation | `mcp_atlassian_*` | Agent needs to create/update Jira tickets or Confluence pages |

**When to Recommend Additional MCP Servers:**

If the agent needs capabilities not covered above, include this guidance in the prompt:

```
NOTE: This agent would benefit from [MCP_SERVER_NAME] for [CAPABILITY].
To add: Check Claude Code MCP documentation or your organization's approved integrations.
Check with your SecOps team before installing new MCP servers.
```

**Common MCP additions to recommend:**
- **Slack MCP** — If agent needs to post messages or read channels
- **Linear MCP** — If using Linear instead of Jira
- **Notion MCP** — If documentation lives in Notion
- **Google Drive MCP** — If agent needs to access Drive files programmatically

#### Security Tools

Security scanners are not built into Claude Code. If a Snyk MCP server (or equivalent) is configured in the workspace, the agent can invoke it via `mcp__*` tools after generating code or changing infrastructure-as-code files. Otherwise, treat scanning as a manual step the user runs outside the agent loop.

**Security Workflow (when scanner MCP available):** Generate code → Scan via MCP tool → Fix issues → Re-scan until clean

#### External API Configuration (For Pipeline Agents)

**When designing agents that use external APIs (search, scraping, AI services), document the setup requirements.**

**Common External APIs for Research/Knowledge Agents:**

| API | Purpose | Free Tier | Setup |
|-----|---------|-----------|-------|
| **Serper** | Google search API | 2,500 searches free | `export SERPER_API_KEY="xxx"` — Get at [serper.dev](https://serper.dev) |
| **Exa** | Neural/semantic search | 1,000 searches/month | `export EXA_API_KEY="xxx"` — Get at [exa.ai](https://exa.ai) |
| **Jina Reader** | Web scraping to markdown | Unlimited (free) | No key needed — use `https://r.jina.ai/{url}` |
| **Firecrawl** | Advanced web scraping | 500 pages free | `export FIRECRAWL_API_KEY="xxx"` — Get at [firecrawl.dev](https://firecrawl.dev) |
| **Tavily** | AI-optimized search | 1,000 searches free | `export TAVILY_API_KEY="xxx"` — Get at [tavily.com](https://tavily.com) |

**API Configuration Checklist (Include in Agent Deliverable):**

```markdown
## External API Requirements

### Required APIs
| API | Environment Variable | Required? | Get Key At |
|-----|---------------------|-----------|------------|
| [API Name] | `[VAR_NAME]` | Yes/No | [URL] |

### Setup Instructions
\`\`\`bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)
export SERPER_API_KEY="your_key_here"
export EXA_API_KEY="your_key_here"

# Reload shell
source ~/.zshrc
\`\`\`

### Verify Configuration
\`\`\`bash
# Check if keys are set
echo $SERPER_API_KEY
echo $EXA_API_KEY
\`\`\`

### If an API Is Unavailable
- Retry once, then stop the run: "Stopped. [API] failed: [error]. Check the key or service status, and I'll resume."
- Do not switch to another API mid-run (Step 2.5b)
```

**API Selection Decision Tree:**

```
Agent needs external data...
├── Web search (Google-style)
│   ├── High volume (>2.5k/month)? → Serper (paid) or Tavily
│   └── Low volume? → Serper free tier
├── Semantic/neural search
│   └── → Exa (best for finding similar content)
├── Web scraping
│   ├── Simple pages? → Jina Reader (free, no key)
│   └── Complex/JS-heavy? → Firecrawl
└── Real-time info in Claude Code
    └── → WebSearch / WebFetch tool (built-in)
```

**Cost Awareness:**
- Always start with free tiers during development
- Document monthly usage limits in agent deliverable
- Implement caching to reduce API calls (the research pipeline caches scraped content)
- When an API's quota is exhausted, the run stops and says so; pick a higher tier or a different API at design time, not mid-run

**Security Notes:**
- NEVER commit API keys to version control
- Use environment variables, not hardcoded strings
- For team sharing, document required keys in README without exposing values
- Consider using a secrets manager for production agents

#### Tool Failure Handling Patterns

When designing agents, specify the response to each failure. An unavailable tool, file, or link always stops the run (Step 2.5b):

| Failure Type | Recommended Response |
|--------------|---------------------|
| `Read` - file not found | Stop and ask the user to confirm the path. `Glob` may propose candidates; use one only after the user confirms |
| `Edit` - old_string not found | Read file first to verify content, expand context in old_string |
| `Edit` - old_string not unique | Add more surrounding context to make unique |
| Semantic search - no relevant results | Rephrase the query once. If results are still empty where data is expected, stop and report (Step 2.5b) |
| `Bash` - permission denied | Request appropriate permissions, or escalate to a more permissive permission mode (`acceptEdits`, `bypassPermissions`) if appropriate. If not granted, stop and report the command and error |
| `Bash` - sandbox restriction | Request the permission through the normal prompt. If not granted, stop and report the command and error |
| MCP tool - connection failed | Stop the run. Report server, tool, resource and error, and wait for the user to fix access or paste the source |
| MCP tool - rate limited | Wait and retry once. If it fails again, stop and report |

#### Claude Code-Specific Behavioral Notes

1. **Parallel Tool Calls**: Claude Code supports parallel tool execution. When multiple reads/searches are independent, batch them in a single response for speed.

2. **Permission Modes & Subagents**: Claude Code runs in one of four permission modes — `plan` (read-only; no edits or destructive actions), `default` (asks before destructive actions), `acceptEdits` (auto-approves file edits), and `bypassPermissions` (no prompts). The `Agent` tool also lets the main thread spin up isolated subagents that operate in their own context window and return a summary. When designing a prompt, decide what it should assume about its execution context: does it need write access, can it tolerate `plan` mode for a dry-run/review pattern, and should heavy multi-file exploration be delegated to a subagent to preserve the parent's context? Document these expectations in the prompt so users invoke it correctly.

3. **Sandbox Restrictions**: Default `Bash` commands run in a sandbox. Network access, git writes, and some syscalls may require an elevated permission mode (`acceptEdits` or `bypassPermissions`) or explicit user approval.

4. **Context Window**: Claude Code injects file contents, conversation history, and rule content into context. Design agents to be token-efficient; avoid requesting unnecessary file reads.

5. **Rule Composition**: Multiple rules can be active simultaneously. Avoid tool guidance that conflicts with other workspace rules (e.g., your security scanning requirements).
