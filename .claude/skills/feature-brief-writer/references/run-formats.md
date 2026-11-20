# Run folder and file formats

Every file the skill writes during a run, and the exact format the scripts and graders read. `<run>` is `<session scratchpad>/feature-brief-writer/YYYY-MM-DD_<slug>/`. `<slug>` is the feature name in lowercase with hyphens.

## Run folder

```
<run>/
├── intake.md              # Step 0 questions and Danny's answers, verbatim
├── mcp-calls.jsonl        # One line per MCP call, written as it is made
├── preflight.md           # Step 1 table, one row per connector and link
├── sources/               # Step 2 saved copies, one file per source
├── ledger.md              # Step 3 evidence ledger
├── ledger-check.md        # Step 3 grader report, saved verbatim
├── gaps.md                # Step 4 questions and answers, verbatim
├── gate-1.md              # Gate 1 snapshot
├── source-reads/          # Round 1 grader reads, reused in later rounds
├── qa-reports/            # Step 6 reports, one file per grader per round, plus passes.md
├── link-check.md          # Step 6 link table, rewritten each round
├── trace.json             # Step 7 trace, written by the trace author
├── verify.md              # Step 7 verifier report, saved verbatim
└── evals-advisor-mode2.md # Optional, after presenting
```

## intake.md and gaps.md

One block per question. A block saved without the question's text is incomplete.

`intake.md` opens with a Q0 block that holds Danny's invoking message verbatim, notes and brain dump included, so facts he gave without being asked have a locator.

```
### Q0. Invoking message
Answer: <Danny's message, verbatim>
```

```
### Q<n>. <question text, verbatim>
Default offered: <default>
Answer: <Danny's answer, verbatim>
```

## mcp-calls.jsonl

One JSON object per line, appended the moment a call returns. `retry_of` is the line number (1-based) of the failed call this one retries, or `null`.

```json
{"n":1,"ts":"2026-11-18T19:40:02Z","step":"1","tool":"mcp__google-workspace__get_doc_as_markdown","resource":"1AbC...","ok":true,"error":null,"retry_of":null}
```

Link opens at Step 6 that use WebFetch or an MCP tool also get a line, with `step` set to `"6"`.

## preflight.md

```
| # | Input | Connector | Test call | Result |
|---|---|---|---|---|
| 1 | <link or path> | <server> | <tool> | OK |
```

`Result` is `OK` or `Failed: <error>`. Any `Failed` row after one retry stops the run.

## sources/

One file per source, named `<type>-<short-id>.md` (for example `gdoc-10Tx82VV.md`, `slack-C07AB-1731.md`, `proto-galen-tasks.md`, `code-emr-tasks.md`). Screenshots are `<type>-<short-id>-<n>.png`. Line 1 of every markdown copy:

```
> Fetched <ISO 8601 time> via <tool> from <openable link, local path, or repo/path>
```

Then the content exactly as the tool returned it. Never summarize into a saved copy.

## ledger.md

One row per number, quote, name, date, and link the brief may use. A claim with no row cannot appear in the brief.

```
| ID | Claim | Type | Saved copy + locator | Openable link | Section |
|---|---|---|---|---|---|
| L1 | 60% of visits get a response within 15 minutes | number | sources/gdoc-1AbC.md, line 42 | (internal link) | Why |
```

- `Type` is one of `number`, `quote`, `name`, `date`, `link`, `fact`.
- `Saved copy + locator` names the file in `sources/` and a line number or a quoted anchor of up to 8 words. For Danny's own words it names `intake.md, Q<n>` or `gaps.md, Q<n>`.
- `Openable link` is a URL a reader can open, with two exceptions below. For a person named as a source ("per [AI Eng lead]"), it is the Slack or doc link where they said it. For facts Danny gave, in `intake.md` or `gaps.md`, it is `none (Danny)`. Those facts go in the brief stated plainly with no link (AGENTS.md: never cite Danny). For a local prototype, it is `local: <workspace-relative path>` to the file the string came from. For a fact from Code Explorer, it is `code: <repo>/<path>` as the tool returned it. Both kinds go in the brief with no link, or with a screenshot in the Appendix.
- `Section` is the brief section the claim supports: `Summary`, `What`, `Why`, `Risks`, `Options`, `Questions`, `Appendix`.

## gate-1.md

The script parses three labeled lines: `# Gate 1:`, `Options header:`, and `Appendix:`. The trace author checks `Approved:`. Everything else is prose for the trace and the Fidelity judge.

```
# Gate 1: <Feature>

Approved: <ISO 8601 time>

Options header: <the full H2 text, starting "What are our other options" and ending "?">

Appendix:
- A. <title>
- B. <title>

## Purpose and readers
<the purpose, the ask, and who reads the brief>

## The insight
<the one or two sentences the brief turns on, with the ledger IDs behind them>

## Opening
<the ledger IDs or problem the Summary opens with, and one sentence on why>

## Proposal
<the one or two sentences Danny approved>

## Options
- <Option name>: <what it does, what it gives up or gains>

## Question owners
- <Function>: <Name>, <Name> (source: gate | stakeholder-directory.md line <n>)

## Danny's changes, verbatim
<quote every edit he made, or "None">
```

## qa-reports/

`round-<n>-mechanical.md` from the script, `round-<n>-fidelity.md` and `round-<n>-writing.md` from the judges, saved verbatim. Each judge report has one row per assigned eval:

```
| Eval | Result | Location | Evidence | Recommended fix | Persistent or new |
|---|---|---|---|---|---|
| G3 | Fail | Why, bullet 2 | "<quote from the brief>" | <edit> | new |
```

`Result` is `Pass` or `Fail`. A row with no quoted evidence counts as missing.

`passes.md` gets one line from the orchestrator at the start of each QA pass. The first pass starts at round 1. A pass after Gate 2 changes starts at the last round plus 1.

```
Pass 1: first round 1
Pass 2: first round 4
```

## link-check.md

Rewritten in full each round. One row per link in the brief, in order of appearance.

```
Round: <n>

| # | Link text | Target | Opened with | Result |
|---|---|---|---|---|
| 1 | response-time analysis | (internal link) | mcp__google-workspace__get_doc_as_markdown | OK |
```

`Result` is `OK` or `Failed: <error>`.

## Invocation log line

Appended by the orchestrator to `.claude/skills/feature-brief-writer/observability/invocation-log.jsonl`.

```json
{"ts":"2026-11-18T19:40:00Z","skill":"feature-brief-writer","input_summary":"Feature X brief from notes, 3 Google Docs, 1 Slack thread, prototype","duration_s":1500,"tool_calls":64,"outcome":"success","notes":"","version":"1.1","eval_results":[{"id":"G1","r":"P"}]}
```

`ts` is the Step 0 start time, the same value the trace uses.

## trace.json

The schema in `.claude/skills/agent-architect/references/observability-templates.md` §2, plus §5's `gate_evidence` and `independently_authored: true`. `gate_evidence` has exactly these keys, each with `evidence_found` (boolean) and `detail` (string):

| Key | Evidence the trace author looks for |
|---|---|
| `intake` | `intake.md` exists, opens with a Q0 block whose Answer holds Danny's invoking message, and every later block has question text and an answer |
| `ledger_verification` | `ledger-check.md` exists and reports every ledger row checked, with no open Fail |
| `gate_1` | `gate-1.md` exists with all four labeled lines (`# Gate 1:`, `Approved:`, `Options header:`, `Appendix:`) and an `Approved:` time earlier than the brief's file time |
| `qa_loop` | `qa-reports/` has a mechanical, fidelity, and writing report for every round, and no pass in `qa-reports/passes.md` has more than 3 rounds |
| `link_check` | `link-check.md` exists, its round matches the last QA round, and every row is `OK` |

The trace's `ts` equals the log line's `ts`. `output_summary` names the brief's workspace-relative path.
