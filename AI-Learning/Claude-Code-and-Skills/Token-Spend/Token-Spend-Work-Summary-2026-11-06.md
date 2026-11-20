# Token spend work summary, Nov 6, 2026

The plan's files are built and tested. Five steps still need you, and Cursor stays on Auto at your direction.

## Waiting on you

1. In Claude Code here, open `/mcp` and disable Neon, Netlify, Amplitude, and claude.ai Google Drive.
2. In Cursor's MCP and plugin settings, turn off Neon and Vercel.
3. Run `SESSION_NUDGE_TOKENS=1 claude -p "hi"` and confirm the macOS notification.
4. In a new Cursor chat, run `/handoff` to confirm Cursor loads the skill.
5. Check the user-level Vercel plugin. `~/.claude/settings.json` still has it `true`. The workspace file sets it `false`. I did not verify which setting wins, so check on the next Claude session.

## What changed

- `~/.claude/settings.json`: model `sonnet`, effort `medium`. `claude-opus-5-5` stays at `high`. Added a `Stop` hook and a `Task|Agent` PreToolUse hook. Backup: `settings.json.bak-20261106-tokenspend`.
- `~/.claude/hooks/subagent-guard.py` (new): denies Opus subagents and the 9th launch in an ad hoc session. Skill runs skip the cap. `SUBAGENT_ALLOW_OPUS=1` overrides the Opus deny.
- `~/.claude/hooks/session-nudge.py` (new): notifies at 200k context tokens, then each further 150k.
- `~/.cursor/hooks.json` (new), with `~/.cursor/hooks/subagent-guard.py` and `~/.cursor/hooks/session-nudge.py`. The Opus guard is live. The nudge reads `contextTokensUsed` read-only from `state.vscdb`.
- `.claude/settings.json` (workspace): Vercel plugin set to `false`.
- `.gitignore`: added `Session-Handoffs/`.
- `.claude/skills/handoff/SKILL.md` (new).
- `AGENTS.md`: added the subagent-brief line and changed the QA rules to one QA subagent per change-set.
- `.claude/skills/agents-md-writer/SKILL.md`: updated the ground-truth table. The plan did not list this edit.
- `AI-Best-Practices/Token-Spend/token-spend-report.py` and `baseline.json` (new).
- `Danny's To Do List.md`: updated the last-updated line and added the 16 Nov and 30 Nov check-ins.

## Results

**Step 0 findings.** The Cursor `preToolUse` payload carries `conversation_id` and `tool_input`. Its top-level `model` is empty. The `stop` payload carries `conversation_id`, token counts, and the model. Neither payload has a subagent launch count, so the Cursor launch cap is not built.

**Claude Code baseline.** The report reproduces 75 sessions and $672.90 ($673 rounded) from 21 Sep through 2 Nov. That is 17 active days, or $106.98 per active day. One session started 2 Nov at 21:51 ($166.69) sits outside the window.

**Cursor chats, drafts and subagent records excluded:**

| Month | Chats | At or over 150k | Median context | Null share |
| --- | --- | --- | --- | --- |
| Sep 2026 | 287 | 41 | 124,058 | 60% |
| Oct 2026 | 233 | 46 | 101,482 | 12% |

The plan's recount had 249 October chats, 38 September chats at or over 150k, and a 39% September null share. The report uses the live counts. The gap is noted in `baseline.json`.

**Verification.**
- FM1 through FM8 on `AGENTS.md`: all passed.
- One QA subagent on the other files: all passed. It flagged two wording fixes, which I made.
- Claude guard and nudge: tested with synthetic payloads. Opus denied, 9th launch denied, skill run allowed, nudge fired once per level.
- Cursor guard: a live Task with an Opus model was denied.

**Bug found and fixed.** Cursor also loads the Claude hooks. The Claude guard fired on Cursor's Opus test and showed a Claude-only override message. Both Claude hooks now skip payloads with `cursor_version`.

**Not tested live.** The Claude guard inside a real session, and both nudge notifications.

## Deviations from the plan

- The Cursor default model stays on Auto, per your choice. The plan's Sonnet at medium did not apply. Subagent inheritance is unconfirmed. The one test subagent reported Auto.
- The Cursor launch cap is not built, because the payload has no count.
- The `agents-md-writer` edit was not in the plan.
- The Claude hooks are user-level. They apply in every project, not only this workspace.
- Auto-sync committed these edits at 01:09 (`f5716a5`), along with unrelated files from other work. I did not run `git commit`.

## Check-ins

The 16 Nov quality check and the 30 Nov report rerun are on your to-do list. The 30 Nov pass bar uses `token-spend-report.py` against `baseline.json`.
