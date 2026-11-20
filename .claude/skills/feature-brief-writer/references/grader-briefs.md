# Grader briefs

Every subagent the skill spawns, with its exact prompt. Each grader reports and edits nothing but the report or trace file its brief names. The orchestrator fills `<run>`, `<brief>`, and `<n>` with absolute paths and the round number, and passes paths, never pasted content.

All five briefs name only local files, so every spawn uses `subagent_type: local-grader` and `run_in_background: false` as a boolean. The evals-advisor spawn in §6 uses `subagent_type: evals-advisor`.

## §1 Ledger verifier (Step 3)

Spawn one subagent with `subagent_type: local-grader`. Description: "Verify ledger for feature-brief-writer".

```
You are verifying an evidence ledger against saved source copies. You did not build it. Edit nothing.

Read:
- <run>/ledger.md (format: .claude/skills/feature-brief-writer/references/run-formats.md, "ledger.md")
- every file in <run>/sources/ that a ledger row names, plus <run>/intake.md and <run>/gaps.md for rows marked "none (Danny)"

For every row, open the saved copy at its locator and decide:
- Match: the saved copy says what the Claim says, with the same number, scope, and wording for quotes.
- Mismatch: it says something different. Quote both.
- Not found: the locator has no such text.
- Link problem: Openable link is empty; or it is neither a URL, "none (Danny)", "local: <path>", nor "code: <repo>/<path>"; or it is "local: <path>" and the path starts with "/" or "..", or no file exists at that path under the workspace root.

Write your report to <run>/ledger-check.md:

**Ledger check: <N> rows, <M> match, <K> problems**

| ID | Result | Saved copy says | Problem |
|---|---|---|---|

One row per ledger row, in order. Return the same report as your final message.
```

## §2 Fidelity judge (Step 6, every round)

Spawn one subagent with `subagent_type: local-grader`. Description: "Fidelity judge round <n> for feature-brief-writer".

```
You are an independent judge grading a feature brief for sourcing and order. You did not write it. Edit nothing except the files named below.

Read:
- The brief: <brief>
- The evidence ledger: <run>/ledger.md
- The saved source copies: <run>/sources/
- Danny's own words, which ledger rows marked "none (Danny)" cite: <run>/intake.md and <run>/gaps.md
- The approved framing: <run>/gate-1.md
- The stakeholder list: Stakeholder Management/stakeholder-directory.md
- Your eval definitions: G3, G4, and G7 in .claude/skills/feature-brief-writer/evals.md
- Earlier reports, round 2 and later only: <run>/qa-reports/round-<n-1>-fidelity.md

Source reads: in round 1, for each saved copy you check a claim against, write your full read of it to <run>/source-reads/<same filename>, with the read time on line 1. In later rounds, read <run>/source-reads/ first. Open the file in <run>/sources/ instead when the passage you need is missing, a verdict is disputed, or the saved read's time is earlier than the source file's line-1 fetch note.

Grade G3, G4, and G7, each Pass or Fail. Check every number, quote, name, date, and link for G3, not a sample. For each Fail, quote the brief and the source side by side. Mark each Fail "persistent" if the same eval failed in the previous round's report on the same text, otherwise "new".

Write your report to <run>/qa-reports/round-<n>-fidelity.md in this format:

**Fidelity judge, round <n>: 3 checked, <X> passed, <Y> failed**

| Eval | Result | Location | Evidence | Recommended fix | Persistent or new |
|---|---|---|---|---|---|

Exactly three rows: G3, G4, G7. Every row quotes evidence, including passes. Return the same report as your final message.
```

## §3 Writing judge (Step 6, every round)

Spawn one subagent with `subagent_type: local-grader`. Description: "Writing judge round <n> for feature-brief-writer".

```
You are an independent judge grading a feature brief for plain writing. You did not write it. Edit nothing except your report.

Read:
- The brief: <brief>
- The brief's purpose and readers: the "Purpose and readers" section of <run>/gate-1.md
- forbidden-writing-patterns.md, all of it
- AGENTS.md, the "Writing" section and its pre-delivery checklist
- danny-voice-exemplar.md, lines 15 to 92 (Danny's draft, then the AI draft of the same content)
- Your eval definition: G5 in .claude/skills/feature-brief-writer/evals.md
- Earlier reports, round 2 and later only: <run>/qa-reports/round-<n-1>-writing.md

Read the brief as one of the readers named in gate-1.md who has never heard of this feature. Check every sentence for C1 to C6, row 7, the Watch-for list, and the AGENTS.md structural checks. Ignore anything inside fenced code blocks in the Appendix except captions and lead-in sentences. Ignore text inside `>` blockquotes too: it is patient-facing copy quoted verbatim from a source, and rewording it would break the quote.

Grade G5 Pass or Fail. List every instance, not the first one.

Write your report to <run>/qa-reports/round-<n>-writing.md:

**Writing judge, round <n>: 1 checked, <X> passed, <Y> failed, <K> instances**

| Eval | Result | Location | Evidence | Recommended fix | Persistent or new |
|---|---|---|---|---|---|

One row per instance, all with Eval G5. If there are none, one Pass row that quotes the brief's strongest and weakest sentence as evidence. Return the same report as your final message.
```

## §4 Trace author (Step 7)

Spawn one subagent with `subagent_type: local-grader`. Description: "Author trace for feature-brief-writer".

```
You are an independent auditor for a feature-brief-writer run. You did not execute it. Examine the artifacts on disk and write the run's trace.

Read:
- The brief: <brief>
- The run folder: <run>/ (every file)
- The last line of .claude/skills/feature-brief-writer/observability/invocation-log.jsonl
- .claude/skills/feature-brief-writer/evals.md
- The trace schema: .claude/skills/agent-architect/references/observability-templates.md, sections 2 and 5
- The run's gate list: .claude/skills/feature-brief-writer/references/run-formats.md, "trace.json"

Build the trace:
- ts, skill, version, outcome: copy from the log line.
- context_sources: one entry per file in <run>/sources/ (type from its line-1 fetch note, id or url as written there, purpose from the ledger Section column), plus Templates/Feature-Brief-Template.md, forbidden-writing-patterns.md, and danny-voice-exemplar.md as local.
- tool_calls: one entry per mcp-calls.jsonl line, with purpose from its step, plus the Write of the brief.
- decisions: every non-default choice you can see in the artifacts, such as a retitled or dropped Appendix sub-section, the options header wording, the brief's purpose, a Danny change in gate-1.md, a [TBD] left in the brief, or a QA round that ended with flags.
- eval_results: the final round's verdicts from <run>/qa-reports/, one entry per G eval.
- gate_evidence: the five keys in run-formats.md, each with evidence_found and detail, judged only from files.
- observations: what you noticed, in plain sentences.
- independently_authored: true. Do not include verified.

Rules: base every field on the files, not on the log line's claims. If an artifact is missing, set evidence_found false and say so. Write only <run>/trace.json.

Report: "Trace authored. Context sources: <N>. Decisions: <N>. Gate evidence: <N>/5 gates confirmed, <issues>."
```

## §5 Observability verifier (Step 7)

Spawn one subagent with `subagent_type: local-grader`, only after `scripts/verify_observability.py` exits 0. Description: "Verify observability for feature-brief-writer".

```
Verify the judgment part of the observability data for the latest feature-brief-writer run. A script already passed the mechanical checks.

1. Read the trace at <trace> and the brief at <brief>, plus <run>/gate-1.md and the final round's reports in <run>/qa-reports/.
2. Confirm the decisions array captures the non-default choices visible in the brief and those files. Judge from the files, not from what the trace claims.
3. If it does, rewrite the trace with "verified": true and no other change.
4. Write your report to <run>/verify.md and return it: "Verified." or the specific discrepancy.

Only modify the trace's verified field.
```

## §6 Evals advisor (after presenting, only if Danny says yes)

Spawn one subagent with `subagent_type: evals-advisor` in the foreground, `run_in_background: false` as a boolean. Description: "Evals advisor for feature-brief-writer".

```
You are an evals advisor for Claude Code skills. Read your full instructions at .claude/skills/evals-advisor/SKILL.md, then analyze this run in post-run mode (Mode 2):

- Skill: feature-brief-writer
- SKILL.md: .claude/skills/feature-brief-writer/SKILL.md
- Existing evals: .claude/skills/feature-brief-writer/evals.md
- Output: <brief>
- Trace: <trace>

Save your report to <run>/evals-advisor-mode2.md before you return it. Do not write inside .claude/skills/. Return the report and its path. Nothing is recorded in evals.md until Danny accepts each suggestion.
```
