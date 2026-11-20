# Round folder layout and contracts

The round folder is the only state the skill keeps. Every step reads and writes there, so any step resumes in a fresh session. Scripts run with the round folder as the current directory: `python3 -I <skill>/scripts/<name>.py`. `<skill>` is `.claude/skills/provider-draft-failure-modes` under the repo root.

Default location: `Project-Galen/Phase-3/Discovery/Round-<n>-Failure-Modes/`. Worked example: `Project-Galen/Phase-3/Discovery/Round-3-Failure-Modes/` (built before this skill existed, so a few file names differ; it has no `round.json`).

## 1. `round.json`

Written in Step 0. Every script reads it. Unknown values are `null`, never guessed.

```json
{
  "round": "Round 4",
  "slug": "round-4",
  "vertical": "Weight loss",
  "sources": [
    {"code": "TH", "kind": "thumbs-downs", "sheet_id": "<Google Sheet ID>", "tab": "<tab name>", "gid": "<gid>",
     "url": "<openable link to the tab>", "draft_column": "draft_message",
     "evidence_opener": "<optional: Evidence opener for tickets this source backs>"},
    {"code": "ED", "kind": "edits", "sheet_id": "<Google Sheet ID>", "tab": "<tab name>", "gid": "<gid>",
     "url": "<openable link to the tab>", "draft_column": "draft_message", "sent_column": "sent_message",
     "sender_column": "<column naming the provider who sent the message, or null>"},
    {"code": "EV", "kind": "evals", "run_id": "<MLflow run name>", "judges": ["<judge name>"],
     "file": "<saved per-trace judge verdicts in the round folder>", "url": "<openable link, or null>"},
    {"code": "FA", "kind": "interviews", "file": "<session notes or synthesis in the round folder>",
     "dates": ["<YYYY-MM-DD>"], "providers": {"session_a": "<reviewer handle, or null>"}},
    {"code": "SL", "kind": "slack", "file": "<saved copy of the Slack reports in the round folder>"}
  ],
  "export": {
    "source": "<one line: what the export is and who produced it>",
    "doc_url": "<openable link, or null>",
    "doc_title": "<title shown in ticket Source sections>",
    "run_id": "<MLflow run name, or null>"
  },
  "generation": {
    "bound_utc": "<latest time the drafts can have been generated, ISO 8601>",
    "bound_evidence": "<where the bound comes from>",
    "window_start_utc": "<start of the 'around generation time' window>",
    "build_floor": "<e.g. 'at or after PR #654 (2026-10-14 19:45 UTC)', or null>",
    "commit": "<sha if AI Eng named it, else null>"
  },
  "batches": [
    {"code": "PI", "label": "Prescribe (initial)", "action": "prescribe_visit"},
    {"code": "TU", "label": "Increase dose", "action": "increase_dose"},
    {"code": "FA", "label": "Feedback sessions", "action": "feedback_session"}
  ],
  "batch_cap": 16,
  "reviewers": ["bthe", "dpedrini"],
  "product_reviewer": "dpedrini",
  "jira": {
    "site": "(internal link)",
    "cloud_id": "0c7c1cb2-1d1e-44a7-bf30-bbdfc3717f44",
    "connector": "<MCP server name that worked at preflight>",
    "project": "QCARE",
    "epic": "QCARE-7",
    "issue_type": "Bug",
    "labels": ["Provider-draft-model", "provider-labeling"]
  },
  "prompts_repo": "your-org/clinician-support",
  "snippets_ticket": "QCARE-31",
  "prior_rounds": ["../Round-3-Failure-Modes"],
  "scope": {"conflict_flags_in_scope": false, "draft_and_thread": true},
  "evidence_opener": "Round 4 provider review (ratings <dates>). Drafts from run <run>, generated on or before <date>.",
  "evidence_opener_session": "<optional: opener for a ticket backed only by feedback-session evidence>",
  "source_links": [
    {"label": "<ratings link text>", "url": "<url>", "what": "reviewer verdicts and comments, by trace ID"},
    {"label": "<export link text>", "url": "<url>", "what": "the drafts and the messages before them, by trace ID"}
  ],
  "judges_doc": "Project-Galen/Phase-3/Evals/Provider-Draft-Eval-Nine-Judges-teammate.md",
  "report": {
    "file": "Round-4-Failure-Mode-Cluster-Analysis.md",
    "csv": "round-4-rating-rows.csv",
    "google_doc_url": null,
    "google_sheet_url": null
  }
}
```

- `sources[]` holds one entry per source. A round takes any mix of sources for one window, and failure modes cluster across them. `kind` is one of `thumbs-downs`, `labeling` (a provider labeling round: GOOD or BAD with reasons), `edits`, `evals`, `interviews` or `slack`, spelled as in ai-pilot-update's `feature-file-schema.md`.
- `sources[].code` is two capital letters, unique within `sources[]`. An `interviews` or `slack` source whose rows sit in their own batch uses that batch's code. Any other source code matches no batch code.
- Per-kind fields. `thumbs-downs` and `labeling` take the sheet fields and `draft_column`. `edits` adds `sent_column` and `sender_column`. `evals` takes `run_id`, `judges` and `file`. `interviews` takes `file`, `dates` and `providers`, which maps each session handle to a rater handle, or to `null` when the speaker isn't a rater. `slack` takes `file`.
- `sources[].evidence_opener` is optional. A ticket's Evidence opener falls back to the top-level `evidence_opener`, and a session-only ticket's to `evidence_opener_session`.
- **Legacy rounds** have no `sources[]`, and their `round.json` is never rewritten. Scripts read the `ratings` block as one source, of kind `edits` when the round has an `edits_pass` block and `thumbs-downs` otherwise. Each `extra_sources` entry reads as an `interviews` source with its batch code and no `providers` map.
- **A row's source kind is derived, never typed.** A session Trace ID takes its batch's `interviews` source. Evidence basis `eval-judge` gives `evals`; `provider-edit` or `provider-edit+note` gives `edits`; `slack` gives `slack`. Any other `tr-` row with a Rating ref takes the source that loaded that rating (`ratings.md` records it when a round has more than one ratings source). A legacy row whose Evidence basis is `inferred`, or blank on a legacy `inferred` row, is `audit`. Evidence basis decides before Provenance. New rounds do not write that basis.
- `batches[].code` is two capital letters, unique. Ledger row IDs are `<code>-<nnn>`. `SP` is reserved for spread rows in `row-map.md` and is never a batch or source code.
- `batches[].action` is the prompt's action name, used in ticket titles.
- `prior_rounds` lists rounds oldest first, by evidence window end, as folder paths relative to the round folder. The prior held list comes from the evidence ledger, not from a prior round (`evidence-ledger.md` section 4). Scripts read each listed round's `export/*.md` (and its `round.json` `batches[]` for action names) to resolve an `Earlier round:` Evidence bullet (v2.4). `ledger` is optional: a path to the ledger, default `../Failure-Mode-Evidence-Ledger.md` from the round folder.
- `generation.window_start_utc` defaults to the prior round's generation bound. A fix merged in the window is a re-eval, never a Regression.
- `judges_doc` is relative to the repo root.

## 2. Folder map

| File | Written by | Read by |
| --- | --- | --- |
| `round.json` | Step 0 | Every script |
| `PROMPT.md` | Step 0 (Danny's invocation and answers, verbatim) | Reference |
| `STATUS.md` | Orchestrator, every step | Every step; resume |
| `run-log.md` | `scripts/log_event.py` only, as events happen | `scripts/log_check.py` at every gate; Step 6 trace; E16 |
| `plan.md` | Step 1 (round facts only) | Every agent |
| `ratings.md` | `load_ratings.py` (Step 1) | Extractors, mechanical checks, review sheet, report |
| `export/<code>.md` | Step 1 join | Extractors, blind and second-opinion agents (one batch each), scripts |
| `export-gaps.md` | Step 1 | Extractors, Gate 1 |
| `existing-tickets.md` | Step 1 | Dedup |
| `generation-provenance.md` | Step 1, extended in Step 2c | Dedup, extractors (conflict-flag basis), report caveats |
| `clinical-rules.md` | Step 1 (prior round's copy, updated) | Every judgment agent |
| `snippets.md` | Step 1 (approved snippets and scope) | Extractors, drafters |
| `docebo-<date>.md`, `docebo-delta-<date>.md` | Step 1 | Rule recheck |
| `ledger/<code>.md` | 2a extractors, amended in 2b | 2b, 2c, scripts |
| `ledger/qa/<code>-*.md` | 2b agents and scripts | 2c, Gate 2 |
| `ledger/qa/mechanical-checks.md`, `ledger/qa/phrase-scan.md` | Scripts | 2c |
| `watch-list-prior.md` | Step 1 (`ledger_tool.py prior`, from the ledger's `held` rows) | 2c matching, 2d structure QA, Gate 1 |
| `cluster-working-notes.md` | 2c writer (a digest after each ledger, so a restart skips digested ledgers) | 2c writer on restart |
| `cluster_defs.py` | Orchestrator (2c), updated at every gate | `build_cluster.py`, every later script |
| `failure-modes.md`, `row-map.md`, `input-issues.md` | `build_cluster.py` only | Steps 2d to 5 |
| `dedup/<group>.md`, `dedup/<group>-timing.md` | Dedup agents | `dedup-verdicts.md`, the Timing table, dedup QA, E11 |
| `dedup-verdicts.md` | Orchestrator | `cluster_defs.STATUS`, Step 3, E10, E17 |
| `qa-*.md` | QA agents | Orchestrator, gates |
| `ticket-plan.md` | Step 3 | Drafters, plan QA |
| `briefs/3-<role>.md` | Orchestrator (a filled copy of the `ticket-qa-briefs.md` section for that role, with the round's paths and `{placeholders}`) | The subagent it names |
| `ticket-drafts-<code>.md`, `ticket-comments.md` | Drafters (one file per ticket, named for the batch code of the ticket's title trace; a file for a batch with no ticket is not needed) | Merge, QA |
| `thread-blocks/<code>.md`, `thread-blocks/EARLIER.md` | `make_thread_blocks.py`, then the anonymizer (`EARLIER` holds the blocks for `- Earlier round:` bullets) | `add_threads.py` |
| `ticket-drafts.md` | Orchestrator (merged, approval table first) | Gate 3, filing |
| `ticket-drafts-blind.md` | `make_blind.py` | Blind scorers |
| `blind-scores-clinical-quality.md`, `blind-scores-provider.md` | Blind scorers | Approval table |
| `ticket-review.md` | `build_review_sheet.py`, then Danny's calls | Gate 3, E8 |
| `bodies/<draft id>.md`, `bodies/index.json` | Step 4 | Filing agents, E12, E14, E19 |
| `filing-ledger.md`, `filing-ledger-<x>.md`, `comment-ledger.md` | Step 4 | Report, evals |
| `report_defs.py` | Step 5 | `build_cluster_analysis.py`, E22 |
| `cluster_analysis_prose.md` | Step 5 prose agent | `build_cluster_analysis.py` |
| Report file and CSV (names in `round.json`) | `build_cluster_analysis.py` | Evals team, Google push |

The list of replaced names (`names/<code>.txt`, or an older `names-replaced.txt`) lives in the session scratchpad only. Never write it to the round folder or commit it.

## 3. Data files the orchestrator writes

### `cluster_defs.py`

```python
PENDING = "<one line: how dedup was done and when, or why it is still pending>"
FM = [
  dict(id="FM-01", types="PI TU", kind="draft",          # kind: "draft" or "conflict-flag"
       title="...", behavior="...", expected="...",
       rows="PI-009 PI-016",                              # space-separated ledger row IDs; "" for mechanical-only
       other="...", flags="...", dedup="<candidate tickets and why>"),
]
OTHER = {"PI-047": ("not a failure mode", "<reason>"),    # destinations: "not a failure mode", "logged",
         "TU-004": ("input-issue", "<reason>"),            # "input-issue", "decision D<n>"
        }
INPUT_OWNERS = {"Provider decision (for Clinical Quality)": "PI-031 TU-018",
                "EMR (action details, fields, workflow)": "TU-004",
                "Chart or catalog data": "TD-006",
                "Eval dataset or tool": "RF-039"}
INPUT_NOTES = ["<extra bullet lines for input-issues.md>"]
DECISIONS = {"D1": "<question, default, rows>"}
STATUS = {"FM-01": "<dedup category and basis> | Filed: QCARE-183 (2026-10-21)"}
SPREAD = {"FM-05": "<mechanical spread, e.g. 'all 15 PI drafts'>"}
SPREAD_TRACES = {"FM-05": "tr-<32 hex> tr-<32 hex>"}       # identical defective text, full trace IDs
SEVERITY = {"FM-01": "efficiency"}                          # "severe safety", "minor safety" or "efficiency"
WATCH = {"FM-01": "L-132"}                                  # held ledger rows this FM matches (ledger IDs)
CONSOLIDATE = {"FM-03": "FM-07 FM-12"}                     # Step 3: absorbing FM -> FMs it absorbed
CALL = {"FM-09": "file"}                                    # Gate 2: Danny's call where it differs from the script's
FLAG_EXTRA = {"RS-012": "<missed-flag note for a row whose basis is not in its ledger cell>"}
```

Every `input-issue` destination must appear in exactly one `INPUT_OWNERS` list; `build_cluster.py` asserts it. Every `kind="draft"` FM needs a `SEVERITY` entry, set at 2c and confirmed at Gate 2 (`clustering-and-dedup.md` section 2a).

`WATCH` values are space-separated item IDs from `watch-list-prior.md`. `CONSOLIDATE` pools the absorbed FMs' counts into the absorbing FM, counting each draft and provider once. An FM can absorb or be absorbed, not both.

`CALL` records each Gate 2 filing call that differs from the script's: `file`, `hold`, `product owner` or `comment`. A product-owner row Danny rules on gets an entry too. A one-off moved to `file` scores at its recurring level (`priority-rubric.md` section 0). `CALL` never overrides `merged`. The ledger update waits until every product-owner row has a `CALL` entry; until then `build_cluster.py` prints the FMs still waiting on a product-owner call or on dedup.

`build_cluster.py` checks every key of these dicts is an FM, every `SEVERITY` and `CALL` value is allowed, every `SPREAD_TRACES` value is full `tr-<32 hex>` IDs and every `WATCH` item is in `watch-list-prior.md`. A round whose `cluster_defs.py` has no `SEVERITY` dict (built before v2.0) gets counts but no filing call.

`build_cluster.py` reads the dedup category from the start of `STATUS`. `New` and `Regression` keep their names. A category that starts `Won't Do` goes to the product owner, and so does a `Recurrence` whose first clause after the colon says `closed Won't Do`, as in `Recurrence: <key> (closed Won't Do)`. Any other category reads as a comment, and an empty `STATUS` reads as pending dedup. After filing, each filed FM's `STATUS` ends `| Filed: <key> (<date>)`. A merged ticket puts the same key on every FM it absorbed.

### `watch-list-prior.md`

Generated by `ledger_tool.py prior` from the evidence ledger's `held` rows (`evidence-ledger.md`). One table:

```
| Item | Behavior | Action types | Severity class | Counted drafts | Providers | Hold flag | First held | Rounds waited |
```

- `Item` is the ledger ID, such as `L-132`.
- `Behavior` is the ledger row's Behavior.
- `Action types` is `-`; the ledger does not track it.
- `Counted drafts` holds `tr-` plus 8 hex characters per draft, space-separated, or `none`. `Providers` holds the reviewer handles credited through drafts, then `session:<handle>` for each provider seen only in a session, or `none`.
- `Hold flag` is the topic after `held:` in the ledger Status (such as `price`), or `none`.
- `First held` is the earliest evidence date. `Rounds waited` counts the rounds dated after it.

No `watch-list.md` is written for a round. `build_cluster.py` reads `watch-list-prior.md` and matches drafts on `tr-` plus 8 hex characters.

### `report_defs.py`

```python
CATEGORIES = ["Clinical safety: core", "Clinical safety: edge case", "Writing quality",
              "Templated repetition", "Conversation handling", "Factual fidelity", "Operational routing"]
CAT = {"QCARE-183": ("Clinical safety: core", "", "rx_guideline_adherence, completeness")}
EXISTING = [  # existing tickets that got this round's evidence (comment units)
  dict(key="MLENG-5405", unit="MLENG-5405 (repeat step)", fms="FM-27", title="...", status="..."),
]
```

`CAT` holds one entry per filed key and per `EXISTING` unit. Keys are unit names when one ticket carries two units.

## 4. Record formats the evals parse

These lines are fixed. The orchestrator and agents write them exactly as shown.

| File | Format | Eval |
| --- | --- | --- |
| `dedup/<group>.md` | One line per ticket read: `Read: <key> · description yes · comments <n> · Development <state> · <UTC time>` | E11 |
| `dedup-verdicts.md` | Section "Final verdicts": table `FM \| Category \| Basis \| Tickets` with Category from the categories in `clustering-and-dedup.md` | E10, E17 |
| `generation-provenance.md` | Section "Timing table": `Key \| PR \| Merged UTC \| Prod deploy UTC \| Category` (`none` when Jira shows no prod deploy) | E17 |
| `ledger/qa/<code>-second-opinion-diff.md` | Each disagreement row ends with `Recommendation: <ledger\|second opinion> (<one line why>)` | E3 |
| `ticket-drafts.md` | Approval table columns `Draft \| Title \| Recommended \| Clinical blind \| Provider blind \| Disagreement \| Rationale`; Disagreement is `yes` or empty; `yes` rows first | E5 |
| `ticket-review.md` | Each card has one line `Your call: keep <P0\|P1\|P2>` or `Your call: drop (<reason>)`, followed by Danny's words verbatim on the next line | E8 |
| `qa-step4.md` | Line `Epic query: <n> issues, <d> duplicate summaries`; check row `Description not truncated` with `<pass>/<total>` | E9, E19 |
| `filing-ledger.md` | Table `Draft \| Key \| Title \| Priority \| Parent \| Labels \| Verified by` (`getJiraIssue` or `JQL key=`); header only when Gate 3 approved no ticket | E7, E8, E9 |
| `STATUS.md` | Sections "Gate 2 answers" (`<row or item>: <ledger\|second opinion\|other> (<Danny's words>)`), "Gate 3 record" (`Merge requested: <drafts>` per request), "Gate 4 record" (`Render: OK` or `Render: issue (<what>)`) | E3, E4, E6, E27 |
| `dedup-qa-*.md` | Table "Tickets read": `Key \| Read UTC \| Comments read \| Final scope after comments (one line) \| Failures` | E28; the format checker's scope reuse |
| `qa-step3-format.md` | Table "Jira keys verified": `Key \| Method \| Result`, Method `full read` or `scope cell (<dedup-qa file>)` | E29 |
| `run-log.md` | First event of each session: `note` with `text=session <id>` (first session) or `text=resumed from STATUS.md, session <id>` | E26, E27 |

## 5. `STATUS.md` template

```markdown
# <Round> failure modes: status and handoff (read this first)

**Current step:** <step and sub-step>. **Next:** <what runs next, or which gate is waiting>.

> **Source:** Danny's invocation (<date>), saved as `PROMPT.md`. This file records what exists only in chat.

## Done; do not redo
- <step>: <outputs> (<date>)

## Decisions made in chat
### <date>, <gate or step>
1. **<topic>:** "<Danny's words>". Effect: <what changed, in which file>.

## Gate 2 answers
## Gate 3 record
## Gate 4 record

## Open follow-ups
## Gotchas a new session needs
- Atlassian connector that works: <name>. Jira key renames: <map or none>.
```

Decisions in `STATUS.md` override `PROMPT.md` and the skill defaults for this round. Newest decisions go first within each section.

## 6. Script-parsed formats

The formats of `ratings.md`, `export/<code>.md`, `ledger/<code>.md`, `thread-blocks/<code>.md` and the ticket draft files are defined by the scripts that read them. See section 6a, written with the scripts.

### 6a. Formats (filled in with the scripts)

Every script lives in `<skill>/scripts/`, reads `round.json` from the current directory (the
round folder), and is run as `python3 -I <skill>/scripts/<name>.py` from that folder. `round_config.py`
is the shared helper (`load`, `batch_codes`, `action_map`, `jira_browse`, `parse_tables`,
`parse_table_after`, `col`). Its `sources`, `sources_of_kind`, `session_batches` and
`session_provider` read `sources[]` and a legacy round's blocks the same way. Every other script
imports it, plus `mechanical_check.ledger_rows` and `.col` where it needs ledger rows.
`counting.py` holds the counting rules (`priority-rubric.md` section 2) and the row source kind
(section 1 above), so every script counts a draft the same way.

**`ratings.md` row table** (written by `load_ratings.py`; parsed by `mechanical_check.py`,
`build_cluster_analysis.py`, `run_evals.py` via `load_ratings.rating_rows()`):

```
| Sheet row | Label ID | Trace ID | Rating ref | Verdict | Tags | Text type | Reviewer text (redacted) |
```

`Rating ref` is `<handle> · <YYYY-MM-DD HH:MM>` (UTC). `Verdict` is lower-case `good`/`bad`. `Tags`
is comma-separated or `none`. `Text type` is `default note only`, `reasons`, `custom note`, or
`reasons+note`. Any `|` in reviewer text becomes `/`; newlines are collapsed. This table can sit
anywhere in the file; every script scans the whole document for lines matching this shape rather
than anchoring to a section number, so the file's narrative sections (headline counts, per-reviewer
table, repeats, tags, `expected_flag_for`, per-trace roll-up) can be in any order or omitted.

A round with one sheet source runs `load_ratings.py <saved file>`. A round with more passes one
`<code>=<saved file>` argument per sheet source (`thumbs-downs`, `labeling` or `edits`). The row
table then holds the rating rows from every sheet, and `ratings.md` gains section 9, parsed by
`load_ratings.source_rows()`:

```
## 9. Rows by source

| Source | Sheet row | Trace ID | Rating ref | Sent message | Sender |
```

One row per sheet row. `Rating ref` is blank on an edits row with no rating, and `Sent message`
is `yes` when the edits sheet's `sent_column` holds a message. An edits sheet needs `trace_id` and
its `sent_column`. A rating sheet needs `trace_id`, `verdict`, `labeler` and `created_at`. Every
row bound for the row table needs a label ID of 36 hex-or-dash characters, and each code is
passed once. A label ID two sheets both hold enters the row table once, with the kind of the
sheet passed first; section 9 keeps every copy. Repeats within one sheet all stay.

**`export/<code>.md` record** (hand-built per round by the orchestrator from the round's export
source; read by `check_export.py`, `phrase_scan.py`, `make_thread_blocks.py`,
`build_cluster_analysis.py`):

```
## <n>. <label> – <sub-label, optional>

*Trace tr-<32 hex>  ·  Medication: <medication line, or "none">  ·  Provider: <handle>*   <- Provider optional

**Last messages before the draft**

**<Role>**<em>  (<timestamp>, <type>)</em>

<message text, one paragraph per Doc entry, may be collapsed to one line>

**Provider draft**

<draft text, collapsed to one line; {{provider_intro}} and other platform tokens appear literally>

**Message the provider sent**                <- edits sources only

<sent text, collapsed to one line, or "(none recorded)">

**Explanation**

<the model's stated reasoning; never a source of defects, only of what it believed>

**Judge verdicts**                           <- evals sources only

- <judge name>: <pass|fail>. <judge reason, redacted per Regime A>

**Ratings (from `ratings.md`)**              <- when the trace has rating rows

<the ratings.md row table, filtered to this trace's rows>
```

`Provider` names the provider whose task the draft was for, as a `round.json` `reviewers[]` handle, when the source shows it. Eval evidence credits that provider; with no `Provider`, it credits none (`priority-rubric.md` section 2).

One `## <n>. ` record per trace; records are split on that heading. `check_export.py` (no flags)
checks every trace any source names has a record, and every record has the three core sections (last messages, draft, explanation). When no draft was generated, the draft section reads `(no draft generated)`; scripts also accept older wordings that start `(no draft`. An edits trace also needs **Message the provider sent**, an evals trace **Judge verdicts**, and a rated trace the ratings table. Sections after the header line may come in any order, because scripts read each section up to the next known heading.

The traces a source names: rating rows and section 9 rows in `ratings.md`; the Trace ID column of an evals source's `file`; and every full `tr-<32 hex>` ID in a Slack source's `file`. An evals `file` is a markdown table with a `Trace ID` column, one row per trace and judge, such as `| Trace ID | Judge | Verdict |`. A Slack `file` is the saved reports with each reported trace written as a full ID. A missing source file is a `check_export.py` failure.

A source's configured
`draft_column` (legacy: `ratings.draft_column`) is cross-checked against a saved raw sheet read if `--ratings-file <path>`
is given. `check_export.py --ids` prints just the trace IDs present in `export/` (full `tr-<32
hex>` form, one per line) and exits 0, so a subagent (the format checker) can verify trace IDs
against the export without reading the export files themselves.

**`ledger/<code>.md`** columns (written by extractor/adjudicator agents; read by
`mechanical_check.ledger_rows`/`.col`, which every other script imports rather than re-parsing):

```
| Row ID | Trace ID | Action type | Provenance | Evidence basis | Reviewer | Verdict | Rating ref |
Error tag | Verbatim reviewer quote | Offending draft sentence | Atomic issue | Classification |
Input named | Conflict-flag basis | Expected behavior + guidance source | Confidence | Export ref |
```

`Row ID` is `<code>-<nnn>`. `col(row, name)` matches by case-insensitive header prefix, so a column
can carry a footnote or be renamed slightly without breaking every reader. Full column rules in
`plan.md` section 6 (per-round); the schema itself does not change round to round.

**`failure-modes.md` and `row-map.md`** (written by `build_cluster.py`; read by
`build_review_sheet.py`, `build_cluster_analysis.py`, `run_evals.py` and ai-pilot-update's
`theme_counts.py`). The "## 1. Summary" table is one table with one `| FM-<nn> |` line per FM.
Its last eight columns are the counts:

```
| Severity class | Counted drafts | Counted instances | Providers | Sources | Band | Level (rubric) | Filing call |
```

`Level (rubric)` is the section 0 level before Danny's Gate 3 call. `Filing call` is the call and
its reason, such as `hold: seen once, efficiency`. Beyond the four calls, the script writes
`merged` for an absorbed FM, `pending dedup` for an FM that clears the floor while its `STATUS`
is empty, and `-` on a pre-v2.0 round.
Any `|` inside a status or flags value prints as `;`. Each FM's detail adds Severity class,
Counts, Filing call and Watch-list match lines, and a Spread line when spread is listed but not
yet backed.

```
| Row | Trace | Reviewer | Provenance | Classification | Destination | Source | Evidence basis | Counted |
```

`row-map.md` has one line per ledger row, plus one `SP-<nnn>` line per spread draft, with
Reviewer `scan` and Provenance `phrase-scan`. Destination stays the sixth column, which readers
parse by position. `Source` is the derived source kind, `scan` on an `SP-` row. A rated row
whose sheet isn't recorded shows `ratings` when the sheets differ in kind. `Counted` is `yes` or `no`.

**`thread-blocks/<code>.md`** (written raw by `make_thread_blocks.py`, then anonymized in place by
a subagent before `add_threads.py` runs):

```
# Thread blocks: <code>

Names must be anonymized before use. One block per trace.

### `tr-<10 hex>` (<action>)

**Messages before the draft**

*<Role>:*

> <message, one blockquoted paragraph at a time>

**Draft**

> <draft, one blockquoted paragraph at a time>
```

`make_thread_blocks.py` writes one block per trace cited in a ticket's "## Evidence" bullets or a
comment's evidence bullets (in any `ticket-drafts*.md` except `-blind`, plus `ticket-comments.md`),
excluding "Also:" lines; it reconstructs paragraph breaks from the export's collapsed text with a
heuristic, so treat exact line breaks as best effort, not a transcription. The heuristic never cuts
inside a URL or a word (v2.4). A bullet that starts `- Earlier round:` cites a trace from a round in
`prior_rounds`: its block is built from that round's `export/*.md` and written to
`thread-blocks/EARLIER.md`, which gets its own anonymizer. `add_threads.py` inserts
`#### \`tr-...\`` copies of these blocks (one level deeper) into each ticket's "## Draft and
thread" section, built only from the traces that ticket's own Evidence list cites.

**Ticket record** (`ticket-drafts-<code>.md` per batch, merged into `ticket-drafts.md`; read by
`check_tickets.py`, `add_threads.py`, `make_blind.py`, `build_review_sheet.py`,
`build_cluster_analysis.py`):

```
### T-<n>. <action[/action...]|all actions>: <text> (tr-<10 hex>)   <- or "(session YYYY-MM-DD)" when no trace backs it
- Source failure mode (working ref, not for Jira): FM-<n>
- Dedup status: ...
- Issue type: Bug
- Labels: ...
- Recommended priority: ...
- Approved priority: ...                            <- added after Gate 3 (v1.2)
- Rationale: <two sentences>
- Needs clinical confirmation: yes|no

## Problem
## Layer
## Evidence
- `tr-...` (<action>). <reviewer> (<verdict>): "<quote>" Draft: <quoted or paraphrased sentence>
- Earlier round: `tr-...` (<action>), <round name>, <date>. <the form's wording from the handle on>   <- a trace from a prior_rounds round (v2.4)
- Also: ...                                        <- excluded from evidence-trace scans
## Draft and thread                                 <- inserted by add_threads.py, after Evidence
## Expected behavior
## Eval check
## Out of scope
## Related
## Source
## Parent
```

The approval table at the top of `ticket-drafts.md` (section "## 1.") has columns `Draft` (or
`Ticket`) `| Title | Recommended | Clinical blind | Provider blind | Disagreement | Rationale`
before Gate 3, and gains `Approved` / loses `Disagreement` after Danny fills it in; every script
reads it by header name (`round_config.parse_table_after`), not column position, so it works in
either state. A ticket's title must match `^(?:[a-z][a-z0-9_]*(?:/[a-z][a-z0-9_]*)*|all
actions): .+ \((?:tr-[0-9a-fA-F]{10}|sessions? \d{4}-\d{2}-\d{2}(?:, \d{4}-\d{2}-\d{2})*)\)$` (a session-only ticket ends in the session date, v1.1). Body length is measured from `## Problem` to the end of the
ticket's text, trailing separators stripped; must stay under 32,000 characters (Jira's limit).

**`round-<n>-rating-rows.csv`** columns (written by `build_cluster_analysis.py`; name comes from
`round.json` `report.csv`):

```
label_id, trace_id, action_type, medication, reviewer, rated_at_utc, verdict, tags, outcome,
failure_mode_tickets, categories, judge_pass_fail, judge_notes, source
```

One row per `ratings.md` row (not per trace), then one row per other evidence row: a session row,
or a `tr-` row with no Rating ref whose source kind is `edits`, `evals`, `slack` or `interviews`.
Legacy checklist rows add none. `source` is the row's source kind. `failure_mode_tickets` holds the filed or
existing ticket keys a row maps to, and `categories` their `report_defs.CAT` categories.
`outcome` holds only the non-ticket destinations, semicolon-joined, using the values in
`cluster-report-spec.md`. It is blank when the row maps only to a ticket. A working
decision-item destination prints as `logged`. A failure mode held without a ticket prints as
`failure mode (held, no ticket)`, and one whose ticket was dropped at Gate 3 as
`failure mode (dropped by the product owner)`. `judge_pass_fail`/`judge_notes` are left blank for the
Evals team. The in-document evidence table's Outcome column still shows the ticket keys too.

**`report_defs.py`** (round folder; Step 5) extends the shape in section 3 above with one optional
field per `EXISTING` item: `rows` (a space-separated row-ID string). Omit it when the unit's
evidence is the whole failure mode; set it when the failure mode was split between a filed ticket
and this existing-ticket comment, so `build_cluster_analysis.py` does not double-count a row
between the two units. The filed ticket for the other part of a split failure mode automatically
gets the remainder (its FM's full rows minus whatever an `EXISTING` item's `rows` claims); no
separate override is needed on the filed side.

**`ledger/qa/<code>-second-opinion-diff.md`** gains a `Recommendation` column (last cell per row,
per section 4) that `compare_second_opinion.py` always writes as `Recommendation: TBD`: choosing
the ledger's call or the second opinion's needs clinical/product judgment the script cannot supply.
The 2b adjudicator agent edits each disagreement row to replace `TBD` with `ledger` or `second
opinion` and a one-line reason before Gate 2 shows it; `run_evals.py` (E3) reads whichever is there.

#### Script reference

Run each script exactly as shown in SKILL.md. Only `check_tickets.py` parses flags strictly; the others treat `--help` as a normal run (and overwrite their output) or as a missing input file. Read the docstring at the top of a script for its usage.

| Script | Reads | Writes | Exit non-zero when | Orchestrator step |
| --- | --- | --- | --- | --- |
| `round_config.py` | `round.json` | (nothing; a library) | n/a | every script |
| `counting.py` | `round.json`, `ratings.md`, `export/*.md` (through its callers) | (nothing; a library) | n/a | `build_cluster.py`, `mechanical_check.py`, `build_cluster_analysis.py` |
| `mechanical_check.py` | `ratings.md`, `export/*.md`, `ledger/*.md`, the evals and Slack source files | stdout only | a row unmapped or untext-covered, an input-issue row with no input named, or (with those sources) an edited draft with no edit row, a failed judge verdict with no `judge:` row, a Slack-reported trace with no `slack` row, or a missing evals or Slack source file | 2b |
| `phrase_scan.py` | `export/*.md` | `ledger/qa/phrase-scan.md` (sentences in 2 or more drafts, with full trace IDs) | never (a report, not a gate) | 2b |
| `load_ratings.py` | one saved sheet read (CSV/TSV/JSON rows), or one `<code>=<file>` per sheet source | `ratings.md` | the input is missing required columns, a row bound for the row table has a blank or malformed label ID, or a code is not a sheet source or is passed twice | 1 |
| `check_export.py` | `round.json`, `ratings.md`, `export/*.md`, the evals and Slack source files, optionally a saved sheet read | stdout only (or trace IDs with `--ids`) | a trace any source names has no record, a record is missing a section, a source file is missing, or a draft/sheet mismatch | 1; `--ids` on demand for the format checker |
| `make_second_opinion_input.py <code>` | `ledger/<code>.md`, `ledger/qa/<code>-adjudication.md` | `ledger/qa/<code>-second-opinion-targets.md` | never (a feed for the next agent) | 2b |
| `compare_second_opinion.py <code>` | the targets file and `ledger/qa/<code>-input-second-opinion.md` | `ledger/qa/<code>-second-opinion-diff.md` | never (a report; Gate 2 judges it) | 2b |
| `make_thread_blocks.py` | `round.json`, `export/*.md`, the `export/*.md` of each `prior_rounds` round, `ticket-drafts*.md` (not `-blind`), `ticket-comments.md` | `thread-blocks/<code>.md`, `thread-blocks/EARLIER.md` | a cited trace has no export record, or an `Earlier round:` trace is in no prior round's export | 3, before the anonymizer |
| `build_cluster.py` | `round.json`, `cluster_defs.py`, the ledgers, `watch-list-prior.md`, and after Gate 3 `ticket-plan.md` and `ticket-drafts.md` | `failure-modes.md` (with counts, severity class and filing call), `row-map.md` (with `SP-` spread rows), `input-issues.md` | any row unmapped or mapped twice, an input-issue owner mismatch, or a dict check in section 3 fails | 2c, every rebuild, and Step 3 after consolidation |
| `ledger_tool.py check <ledger>` | the evidence ledger | stdout only | a computed cell is stale, an Evidence row is malformed, or a Summary row has no valid severity class or status | 1, after the ledger update, E30 |
| `ledger_tool.py write <ledger>` | the evidence ledger | the ledger's Summary table, computed cells only | the ledger has a structural error | after every Evidence edit |
| `ledger_tool.py prior <ledger> watch-list-prior.md` | the evidence ledger | `watch-list-prior.md` (the `held` rows) | the ledger has a structural error | 1 |
| `add_threads.py` | `round.json`, `thread-blocks/*.md`, `ticket-drafts.md` | `ticket-drafts.md` (in place) | a cited trace has no thread block, or no "## 4." section | 3, after the anonymizer |
| `make_blind.py` | `round.json`, `ticket-drafts-<code>.md` (a batch with no file is skipped) | `ticket-drafts-blind.md` | no ticket found in any file | 3 |
| `check_tickets.py --tickets <files>` | the ticket file(s), `round.json` | stdout only | a title, length, session-artifact or writing-checklist hit | 3 (drafts and bodies), 4 (bodies) |
| `check_tickets.py --writing <files>` | the file(s) | stdout only | a writing-checklist hit | 5 (report prose), E20 |
| `check_tickets.py --conflict` | `round.json`, `cluster_defs.py` | stdout only | a filed FM has `kind: conflict-flag` while the scope is off | 3, E21 |
| `check_tickets.py --traces <files>` | the file(s), `round.json`, `export/*.md` (through `check_export.py`), each `prior_rounds` round's `export/*.md` | stdout only | a `tr-` ID is not 10 hex characters or matches no export trace; an `Earlier round:` ID is in this round's export or in no prior round's | 3 |
| `check_tickets.py --threads <files>` | the ticket file(s), `round.json` | stdout only | a Draft and thread section is missing, extra, or has a subheading count that differs from the Evidence traces | 3 |
| `build_review_sheet.py` | `ticket-plan.md`, the ledgers, `cluster_defs.py`, `failure-modes.md`, `ratings.md`, `ticket-drafts.md` (approval table and full drafts) | `ticket-review.md` | ticket-plan.md has no parseable ticket rows | 3, before Gate 3 |
| `build_cluster_analysis.py` | `round.json`, `report_defs.py`, `cluster_defs.py`, the ledgers, `row-map.md`, `failure-modes.md`, `ratings.md`, `export/*.md`, `thread-blocks/*.md` (including `EARLIER.md`), `ticket-drafts.md`, `ticket-comments.md`, `filing-ledger.md`, `ticket-plan.md`, `cluster_analysis_prose.md` | the report file and CSV named in `round.json` | units and `report_defs.CAT` disagree, or a `T-n` has no plan row | 5 |
| `run_evals.py` | everything above, plus `STATUS.md`, `run-log.md`, `dedup-verdicts.md`, `generation-provenance.md`, `dedup/*.md`, `dedup-qa-*.md`, `qa-step3-format*.md`, `qa-step4.md`, `bodies/*.md`, a trace file, the session subagent metadata under `~/.claude/projects/` | stdout only | any eval FAILs (NOT MEASURABLE never fails the run) | 6 |

`run_evals.py` shells out to the other scripts for E1, E2, E20 and E21 rather than re-implementing
their checks, so a fix to one script's logic never drifts out of sync with its eval.
