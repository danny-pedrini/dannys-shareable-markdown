# Evidence ledger

One file counts every failure mode across every round, so a repeat becomes visible. It replaces the per-round watch list: a held failure mode is a ledger row with Status `held`.

**Path:** `Project-Galen/Phase-3/Discovery/Failure-Mode-Evidence-Ledger.md`. From a round folder that is `../Failure-Mode-Evidence-Ledger.md`. A `ledger` key in `round.json` overrides the path.

> **Source:** Danny, chat, 2026-11-10 (ledger design and defaults); `priority-rubric.md` section 2 (counting); eval-only rule and P3 rule: Danny, chat, 2026-11-10. The rubric file does not yet state the eval-only rule or the P3 rule.

## 1. Tables

Three tables under the headings `## 1. Summary`, `## 2. Evidence` and `## 3. Notes`. `scripts/ledger_tool.py` parses them, so keep the headings and column names exact.

**Summary** has one row per failure mode. A ticket that covers more than one unrelated failure mode gets one row each. Failure modes that share one fix location and one expected behavior share a row (`priority-rubric.md` section 0, consolidation).

| Column | Kept by | Meaning |
| --- | --- | --- |
| ID | hand | `L-001` and up. Never reused or renumbered. |
| Behavior | hand | Plain words, no PHI, no real names. |
| Ticket | hand | The ticket key, or `unticketed`. |
| Severity class | hand | `severe safety`, `minor safety`, `efficiency` or `not a draft defect`. Add ` [inferred]` when you chose the class instead of reading it from a label or a decision. |
| Jira priority now | hand | Read from Jira on the update date, or `none`. |
| Provider drafts, Providers, Eval-only drafts (era), Session-only providers, Counted instances, Band, Band incl. eval, Rubric level, Last seen | `ledger_tool.py write` | Computed from the Evidence rows. Never edit by hand. |
| Status | hand | See section 3. |

**Evidence** has one row per round, source kind and group of drafts: ID, Round, Date, Source kind, Trace IDs or handles, Providers credited, Model era, In ticket text, Source. Every row ends in a `> **Source:**` cell that names the file and line, or the Jira key and comment date.

**Notes** has one row per failure mode: the working key `<round slug>/<FM id>` for every round that touched it, the Jira status, the class source, related tickets, open questions and discrepancies.

## 2. Counting

`ledger_tool.py write` applies `priority-rubric.md` section 2 to the Evidence rows.

- **A draft counts once**, however many rounds or sources back it. Drafts match on `tr-` plus the first 8 hex characters of the trace ID.
- **Provider evidence:** `thumbs-down-note`, `labeling-verdict`, `edit` (confidence high only), `edit+note`, `slack`, `reviewer-edit-on-good`. They credit the row's reviewer.
- **Eval-only:** `eval-judge`. It credits no provider unless the export names one. Eval drafts sit in their own column with the model era, and are never pooled with provider drafts without saying so.
- **Session-only providers:** `session` rows with `session:<handle>`. A handle already credited through a counted draft adds nothing.
- **Not counted:** `audit` (legacy rows from before v3.0), `thumbs-only`, `unverified-claim`, and `phrase-scan` unless the failure mode also has a counted provider or eval draft.
- **Band** uses provider drafts and session-only providers: `one-off`, `recurring`, `common`, `none`, or `eval-only` when the only counted evidence is eval-judge drafts. **Band incl. eval** adds eval drafts and applies Danny's 2026-11-10 rule: 5 or more distinct eval-judge drafts are common with no credited provider. Common otherwise needs 5 or more drafts from 2 or more providers.
- **Rubric level** is the section 0 level for Band incl. eval and the severity class. It is a recommendation; Jira priority is the decision.
- **Model era:** write what the source states. Eval tickets from Gemini 3.5 Flash drafts say so. Sonnet 5.5 went live 2026-11-03. Write `not stated` when the source is silent; never guess.

## 3. Status

`filed`, `held`, `P3`, `closed` or `re-run pending`.

- `held` means unticketed and below the filing floor. Add the topic after a colon when a held topic applies (`held: price`). A new issue below the floor never becomes a ticket and never becomes P3: it stays a `held` row until it recurs.
- `P3` applies only to an existing ticket below the floor, set to "P3 - Everything Else" (Jira id 10004) after Danny approves the list. No round creates a ticket at P3.
- `closed` covers Done and Won't Do tickets. A closed ticket stays in the ledger only when a later round matched it (a Regression or a re-eval comment).
- `re-run pending` marks a ticket whose evidence is from an earlier model and waits for a re-run on the current one.

## 4. Reading it (Step 1)

1. Run `python3 -I <skill>/scripts/ledger_tool.py check <ledger>`. A non-zero exit stops the step until the ledger is fixed.
2. Run `python3 -I <skill>/scripts/ledger_tool.py prior <ledger> watch-list-prior.md`. It writes the prior list from the `held` rows, with the ledger ID as the Item. No subagent writes the prior list.
3. Matching at 2c is unchanged (`clustering-and-dedup.md` section 15): `WATCH` names ledger IDs. A match adds the row's counted drafts and providers, counting each once.
4. At Gate 2 and in Step 6, the held list and "rounds waited" come from the ledger's `held` rows.

## 5. Writing it (after Step 4, and after Gate 3 when nothing files)

Launch one `pdfm-worker` ledger writer. Its brief names `failure-modes.md` section 1 and section 2, `row-map.md`, `cluster_defs.py`, `ledger/<code>.md` (one at a time), `filing-ledger.md`, `comment-ledger.md`, `round.json`, `generation-provenance.md` and the ledger. For every failure mode that is not an input issue, a decision item, dropped at Gate 3, or merged into another:

1. **Find the row.** Use the `WATCH` ledger ID if there is one. Otherwise use the ticket key from `STATUS` (`Filed:` or `Covered by`). If two rows share the ticket, stop and ask. With neither, add a row with the next ID.
2. **Add Evidence rows** for each counted ledger row: Round is the round slug, Date is the round's evidence date, Source kind maps from the ledger's basis (`reviewer-stated` to `thumbs-down-note` or `labeling-verdict` by source kind, `provider-edit` to `edit`, `provider-edit+note` to `edit+note`), Trace ID is the first 10 hex characters, Providers credited is the row's reviewer, Model era comes from `generation-provenance.md`. A legacy row with basis `inferred` maps to Source kind `audit`, and scripts still read that kind as not counted. New rounds do not write that mapping. Add `phrase-scan` rows only for traces `SPREAD_TRACES` lists.
3. **Set the hand-kept cells.** Behavior is the failure mode title. Severity class comes from `SEVERITY`. Jira priority is the filed priority. Status is `filed` for a filed ticket, `held` (with the held topic) for a `hold` call, `closed` when the ticket is Done or Won't Do.
4. **Write the Note** with `<round slug>/<FM id>` and any dedup or scope question. E24 looks for that working key on a `held` row. Rows seeded on 2026-11-10 for unticketed failure modes carry the older form `UNT-<round slug>-FM<nn>` (for example `UNT-pilot-1-edits-FM14`), which E24 also accepts.
5. **Run** `ledger_tool.py write`, then `ledger_tool.py check`. A failure is a defect in the Evidence rows; fix them and rerun.

A failure mode dropped at Gate 3 adds no row. If it matched an existing row, leave that row's evidence alone and record the ruling in its Note.

Filing QA reads the writer's rows against `failure-modes.md` (`ticket-qa-briefs.md` section 7). E30 checks that every filed or commented key has a ledger row and that `check` passes.

## 6. Amending

A priority change to a ticket in Jira (the Amend steps, or a P3 move Danny approves) updates `Jira priority now` and `Status` in the same sitting. The ledger never changes Jira.
