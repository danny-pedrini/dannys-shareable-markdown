# Ledger formats

The update folder's working files. Scripts parse these formats, so keep the columns exactly. Times are UTC, written `2026-11-10T15:02Z`.

## 1. `sources.md`

One row per read this run. A re-read is a new row.

```
| ID | Resource | Link or path | Tool | Read at (UTC) | OK | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| S-01 | Week 1 tab of the update doc | (internal link)>/edit?tab=t.0 | google-docs read_document | 2026-11-10T15:02Z | yes | revisionId <id> |
| S-14 | [AI Eng lead], Oct 28, latency test | (internal link) | slack slack_read_thread | 2026-11-10T15:20Z | yes | the message itself, not the thread root |
| S-22 | completeness judge, models.py | your-org/ai@<commit>:ai/hdef/judges/library/completeness/models.py | github get_file_contents | 2026-11-10T15:40Z | yes | blob <sha> |
```

- `Link or path` is the exact link the doc will cite, or the repo path. For Slack, record each cited message's own permalink; a fact from a reply cites the reply, not the thread root.
- `OK` is `yes` or `no`. A `no` row means the run stopped there (SKILL.md stop rule). After Danny fixes access, the re-read is a new `yes` row.
- GitHub rows record the commit SHA in the path and the blob SHA in Notes.

## 2. `facts.md`

Every number, date, status, name-with-claim and quote pointer the doc may use.

```
| ID | Fact | Value | Kind | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| F-001 | Thumbs-downed drafts, Round 1 | 77 | computed | theme-counts.json#rounds.0.drafts | |
| F-010 | Providers live today | 8 | read | S-05 | |
| F-031 | Savings at a 20% cut | 1.17 | read | S-09 | $M, 2027, Scenario 2 |
| F-032 | Savings lost per 5 points short of 20% | 0.29 | derived | F-031 | formula: F-031 / 4 ; doc says "about a quarter of the savings" |
| F-040 | Next ramp step date | Nov 10 | ruling | feature.json#ramp.steps.0.date | |
| F-041 | Metric values publishable | no | ruling | Gate 1, 2026-11-09 | |
```

Kinds:

- `read`: straight from a source. `Source` is one or more `S-` IDs.
- `computed`: a script output. `Source` is `<file>.json#<dot.path>`; `check_facts.py` resolves the path and compares the value.
- `derived`: arithmetic the orchestrator did. `Source` lists the input `F-` IDs; Notes holds `formula: <expression over F- IDs>`. When the expression uses only `F-` IDs, numbers, `+ - * / ( )`, `check_facts.py` evaluates it and fails a value more than 1% off. Write any other formula as `formula (manual): ...`; the Gate 1 grader recomputes it.
- `ruling`: Danny's ruling. `Source` is `feature.json#<dot.path>`, `Gate <n>, YYYY-MM-DD` or `Step 0, YYYY-MM-DD` (the ruling is in `STATUS.md` with his words). A date, number or boolean at a `feature.json` path must match the Value.

Values are plain: numbers without units in `Value` when the doc uses them as numbers, units in Notes.

A metric's value gets a Fact starting `Metric value:` and the metric code. While `feature.json` `metrics.values_publishable` is false, `check_doc.py` fails if that Value appears in the doc.

## 3. `tickets.json`

The live Jira read of every ticket the doc counts or links. It covers every round's filed keys, keys filed on the epic since the prior update, the prior update's outside-round keys, open tickets a ramp gate names, and any key the doc mentions.

```json
{"QCARE-286": {"priority": "P1 - Feature Blocker", "labels": ["Provider-draft-model", "pilot-provider-feedback", "safety"],
               "status": "Blocked", "status_category": "In Progress", "summary": "...", "url": "(internal link)",
               "read_at": "2026-11-10T15:31Z", "counted": false, "category": null,
               "reason": "Danny dropped it after filing (feature.json ticket_rulings)", "rounds": ["pilot-1"],
               "outside_round": false}}
```

`status_category` is Jira's status category (`To Do`, `In Progress` or `Done`), read live, never the status. A ticket is open unless it is `Done`, so a Blocked ticket (category In Progress) is open.

`counted` and `category` come only from `feature.json` `ticket_rulings` or a Gate 1 ruling. `outside_round` is true for a key from the created-since query, or carried forward from the prior update, that is in no round's ledger; the doc gives those their own line. Every key has `rounds` and `outside_round`: a key from the ramp-gate query alone has empty `rounds` and `outside_round` false.

## 4. `interview-claims.md`

```
| ID | Speaker | Date | Claim | Verbatim quote | Source and location | Theme | Corroborated by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IC-01 | [teammate] | Nov 2 | Edits are mostly deletions | "I would say it's more deletion than adding to it." | S-07, quote index #12 | Length, repetition and buried asks | S-06 notes |
```

- One row per claim per speaker. Count claims by who said them, not how often they appear.
- `Verbatim quote` is copied character for character from the source. `check_doc.py` matches the doc's quotes against this column.
- When two sources attribute the same quote to different speakers, record both rows with `CONFLICT` in `Corroborated by`; the doc drops the quote.
- A theme backed only by thin data names its two sources here; with one source it stays out of the doc.

## 5. `eval-coverage.md`

```
| Theme | Verdict | Judges | Rule quoted | Files | Fix row |
| --- | --- | --- | --- | --- | --- |
| Re-asking for known facts | Partly | doctor relationship | "asks the patient for information the chart or thread already answers" | S-24 | Re-asks that no rule requires |
| Pricing | Gap | - | none in any run-set judge; unit tests cover past cases | S-30 | Pricing and instruction clarity |
```

- `Theme` matches the `themes-working.md` label exactly.
- `Verdict` is `Yes`, `Partly` or `Gap`. A theme only unit tests cover is `Gap`, and the doc says "(unit tests only)".
- `Judges` uses the judge names as the doc writes them, comma separated, or `-`.
- `Rule quoted` is verbatim from the prompt or output schema file in `Files`.
- `Fix row` is the exact first-cell label of the eval-changes row that closes the gap. Separate more than one with `;`. A `Partly` theme with no planned change says `none: <reason>`, and the doc states the reason. A `Gap` always has a fix row.
- Below the table, list every run-set judge read and every file with its `S-` ID, plus the judge count read first-hand ("10 of 10").

## 6. `comments.md`

```
| # | Author | Date | Anchored text | Comment and replies | Challenges | Ruling |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | <name> | Nov 4 | "<the anchored text, verbatim>" | "<comment, verbatim>" Replies: <name>: "<reply, verbatim>" | ramp bar for 10% and 50% | open |
```

`Challenges` names the gate, number or claim a comment disputes, or `-`. `Ruling` is `open` until Danny rules at Gate 1; an open challenge goes into `feature.json` `open_challenges` and the doc never restates the challenged item as settled.
