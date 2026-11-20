# Clustering and dedup

## 1. Failure-mode definition

One failure mode (FM) is one wrong behavior, with one fix and one testable expected behavior. Name it the way a ticket title would ("don't re-ask a fact already in the chart"). The ledger's `Issue type:` phrases are raw material: harmonize the wording, but let the fix location and the behavior decide the grouping. An FM's title, behavior and expected behavior carry no rule IDs or file names; name the guidance source in plain words.

**Group from the ledgers alone first.** Only then read `existing-tickets.md` and prior rounds' `cluster_defs.py`, to fill candidate ticket keys and reuse decision numbering, never to decide how rows group.

**Merge test.** Would one change make every row pass its expected behavior: one prompt edit in one place, one data fix, or one rule added? If yes, one FM. If the rows need different fixes, split.

**Split rules:**
- **By action type**, unless the shared text is confirmed identical across types (each action type has its own prompt file). Exception: when a byte-identical shared prompt file or shared sentence is confirmed across types (checked directly, not assumed), one FM may span them; state the confirmation in the FM's notes.
- **By fix location**, regardless of action type: a different prompt file, a different data source, template text versus model behavior, or EMR versus CDS. A reviewer complaint that spans two fix locations (for example, a missing switch instruction and a separate invented reason for it) splits into two rows and, if warranted, two FMs.

## 2. Mapping rule

Every ledger row maps to exactly one of:
- a failure mode,
- `input-issues.md` (an input-issue row, per `rules-core.md` section 1),
- "not a failure mode" with a stated reason,
- "logged" (a proof-rule case that depends on chart data not shown; see `rules-core.md` section 5),
- a decision item (section 4 below).

Thumbs-only rows map to coverage only (thumbs-only). `build_cluster.py` enforces one destination per row and fails the round on any row left unmapped or mapped twice (see `round.json` round-folder-layout, section 3, `cluster_defs.py`).

**Mapping by row kind:**
- **Disagreement rows** (ledger versus second opinion) map by the side their `Recommendation:` line picks. Each real split gets one `INPUT_NOTES` line: `disagreement: <row> -> <working call> (<ledger|second opinion>)`. A `mixed` working call maps to the draft-controlled failure mode, with the input part in `INPUT_NOTES`.
- **`not counted:` rows** map to "not a failure mode" with their type (`sign-off`, `intro` or `added counseling`) and one clause. Gate 2 lists them.
- **`contradicted by the draft:` rows** (a failed judge verdict the draft disproves) map to "not a failure mode: contradicted by the draft". Gate 2 lists them with the section 3 cases.
- **Input-issue rows** go to `input-issues.md`. When the draft could still have handled the case better, a separate draft-controlled row should exist. If the ledger lacks it, add `possible draft part: <row>: <one clause>` to `INPUT_NOTES`; never invent a row.
- **Uncodified reviewer claims** (Expected behavior starts `uncodified, needs clinical confirmation`) join a failure mode when the draft-controlled defect stands without the claim. Otherwise they become a decision item.
- **Supporting-evidence-only rows** (medium- or low-confidence diff-only edits) group like any row. A failure mode backed only by such rows has zero counted instances (`priority-rubric.md` section 0, band `none`).

## 2a. Counts, spread and severity class

**Counts.** `build_cluster.py` computes each failure mode's counted drafts, counted instances, providers, sources, band and filing call from `priority-rubric.md` section 2. It writes them to `failure-modes.md` with each FM's severity class. After consolidation, `CONSOLIDATE` pools the counts (`round-folder-layout.md` section 3). Never count by hand.

**Spread.** `SPREAD_TRACES` lists, per failure mode, the full trace IDs of drafts that carry the identical defective text, from `ledger/qa/phrase-scan.md`. The scan is a string match, and a masked match counts as identical.

Spread adds counted drafts but no provider. It counts only once a draft backed by provider evidence or an eval failure shows the text is a defect. Never create a failure mode from repetition alone. `build_cluster.py` writes each spread draft into `row-map.md` as an `SP-<nnn>` row.

**Severity class.** Set `SEVERITY` per failure mode at 2c from its worst credible instance (`priority-rubric.md` section 1), counted or supporting. Gate 2 confirms it, because the filing call needs it before Step 3 scores priority.

**Filing call.** One of four values per failure mode:
- `file`: it clears the floor and dedup is New or Regression.
- `comment`: an open ticket covers it, or it goes to re-eval.
- `hold`: it's below the floor. It becomes a `held` row in the evidence ledger (section 15), with an evidence comment on a covering ticket where one helps.
- `product owner`: a held topic (section 3), a severe-safety failure mode with zero counted instances, a Won't Do match, or a ledger match that carries a hold flag.

The Gate 2 call is per failure mode. Step 3 recomputes it after consolidation, counting each draft and provider once.

## 3. Contradicted-by-ruling handling

A reviewer rule that conflicts with a Danny ruling (a ruling memory or a `CR-R<n>` entry in `clinical-rules.md`) or with a clinical answer in `clinical-rules.md` maps to **"not a failure mode: contradicted by `<source>`"** and goes to Danny at Gate 2. It is never dropped silently, and it is never filed as written.

**Held topics.** Rows tagged `[<topic>]` (`rules-core.md` section 8, extraction rule 17) group into their own failure modes like any others. Each such failure mode carries `flags="HELD: <topic> (product owner rules at Gate 2)"`. Never merge one with an untagged failure mode, drop it, or mark it contradicted. Nothing is filed or commented on for it before the product owner rules.

## 4. Decision items

A reviewer disagreement that no clinical answer or ruling settles becomes a decision item, not a bug. Give each one a short ID (`D1`, `D2`, ...), the question, the rows it covers, and, where relevant, a proposed default. Decision items go to Gate 2, always (`human_in_the_loop` table, SKILL.md).

## 5. Dedup categories

Read a candidate ticket's **full description and every comment**, plus its Development field, before any dedup call stands (`rules-core.md`-level hard constraint; never call from a summary).

| Category | Rule |
| --- | --- |
| New | No ticket covers this behavior and this action type |
| Recurrence of a prior-round ticket | The matched ticket is one of a named prior round's filed tickets (`round.json` `prior_rounds`). **Open:** draft a comment adding the new evidence. **Closed Done**, and the fix is confirmed in the generating build (section 7): the behavior is fixed; no action. **Closed Done**, and the fix is not confirmed in the build: propose re-eval. **Closed Won't Do:** flag Danny; do not file and do not assume dismissal. |
| Covered by an open ticket | The open ticket's final scope (section 6) already covers this behavior and action type. Draft a comment that adds this round's evidence. |
| Done after generation | The fix is not confirmed to have been in the generating build (section 7). Propose verification in a re-eval comment on the existing ticket, or file New if no ticket exists yet for the underlying behavior. |
| Regression | The fix **is** confirmed in the generating build (section 7) and the behavior is still present in this round's drafts. File a new ticket that links the old one. |
| Won't Do match | A closed Won't Do ticket's scope matches this behavior. Flag Danny; never silently treat it as settled either way. |

Open means Backlog, Selected for Development, In Progress or Blocked. When an open ticket and a Done ticket both match, the open ticket wins: Covered by an open ticket.

A ticket Jira shows as Done whose comments say it closed as won't do or obsolete is still Done for the category. Apply the timing rule, and flag that it closed as not done.

> **Source:** Danny, 2026-11-04 (Round 1 edits pass): "if they're marked done, then we should open new tickets if tickets don't already exist for these outstanding issues."

## 6. Scope check

A ticket covers a failure mode only if its **final scope, after every comment**, names both this action type and this behavior. Match on the problem and expected behavior, not on cited traces: a ticket covers a failure mode whether or not it cites these drafts. A ticket whose evidence happens to quote the offending sentence, but whose expected behavior or eval check never tests it, does not cover the FM (Round 3 example: MLENG-5405's own "Out of scope" note named the sign-off as a separate ticket's job, and that other ticket's scope never tested it: both FM-21 and FM-49/50 stayed New on this basis). State the final scope in one line in the dedup write-up regardless of the verdict.

## 7. Deploy and timing check

Go with **Jira's Development field** (Danny, 2026-10-21). This is the entire basis for "is the fix in the generating build":

- A fix counts as in the generating build **only if** Jira's Development field shows a production deploy **before** `round.json` `generation.bound_utc`.
- A fix merged at or after `round.json` `generation.window_start_utc` and before `generation.bound_utc` is a **re-eval**, **never** a Regression, regardless of what the Development field shows.
- A fix merged before `generation.window_start_utc` **with** a confirmed production deploy before `generation.bound_utc`, and the behavior still present, is a **Regression**.
- A fix merged before `generation.window_start_utc` **without** a confirmed pre-bound production deploy: assume it was not in the build. The FM is Done after generation (re-eval), or a prior-round recurrence for re-eval, never a Regression.
- No merged PR found for a candidate ticket: state that plainly ("no merged PR found"); do not guess a timing class.
- A production deploy after the first draft was generated and before `generation.bound_utc` goes under Flag for Danny, because some drafts may predate it.

`generation.window_start_utc` defaults to the prior round's `generation.bound_utc` (`round-folder-layout.md` section 1). Record every timing-dependent ticket's merge time, deploy state and resulting class in `generation-provenance.md`'s Timing table (section 11 below); the Final verdicts table (section 10) only needs the resulting Category.

**Draft-text evidence bounds the build for reporting only.** If the drafts contain text that first merged in PR X, that sets a lower bound on the generating commit ("the run used code at or after X"). Record this in `generation-provenance.md` and the report's caveats. It **never** changes a dedup category: Jira's deploy record is the only input to that call, even when draft-text evidence and the deploy record disagree (Round 3 example: MLENG-5372 showed no deploy at all, yet its PR's text was plainly in the drafts; the dedup category still went by the deploy record, and the discrepancy was flagged as a note for Danny, not used to override the category).

## 8. Jira gotchas

- **JQL misses some epic children.** Build and reconcile `existing-tickets.md` against the Teamwork Graph (`getGraphContext`), not JQL alone. Verify any ticket JQL can't find with a direct `getJiraIssue` on its key.
- **Keys get renamed.** When a ticket was renamed across an epic migration, cite both keys the first time it's mentioned in any file read outside the session.
- **`getJiraIssue` can time out.** Retry once. If it times out again, fall back to JQL `key = X`, one key per query. Never batch a large JQL query for anything but the single epic-wide duplicate check at filing (`parent = <epic> AND created >= <date>`).

## 9. Dedup agent brief

One agent per batch group (the orchestrator splits the FM list into groups small enough for one context). FMs that share a candidate ticket go in the same group, so no ticket is read by two dedup agents.

**Do not launch subagents.** Read every ticket, commit or file yourself, including every ticket a better-match search turns up.

**Inputs:** the group's FMs' candidate ticket keys (from `cluster_defs.FM[].dedup`), `existing-tickets.md`, `generation-provenance.md`, `snippets.md`, `round.json`.

**Task.** For every candidate ticket:
1. Read it in full with `getJiraIssue` (description, every comment, Development field).
2. Write one `Read:` line per key in the exact format `round-folder-layout.md` section 4 requires: `Read: <key> · description yes · comments <n> · Development <state> · <UTC time>`.
3. Build a per-FM table, one row per candidate ticket, with columns: Ticket | Status, resolution date | Final scope after comments (one line) | Action types in scope | Behavior match | PR, merge UTC | Prod deploy (Development field) | Timing class.
4. Apply the scope check (section 6) and the deploy-and-timing check (section 7) to reach a verdict.
5. Search the epic inventory for better matches beyond the given candidates (a keyword sweep of `existing-tickets.md`); log what was checked even when nothing new is found. Scan the titles of every ticket a `prior_rounds` round filed (its `filing-ledger.md`), and read in full any whose title could match.
6. Write, per FM: **Verdict**, **Why** (one paragraph tying the verdict to the scope and timing evidence), **Adds something the ticket lacks** (covered FMs only: yes or no, and what, such as a case, a wording, a constraint or an action type its scope omits), **Comment target** (that ticket only when it adds something, otherwise "none"), **Flag for Danny** (anything that needs his call, such as a Won't Do match, an unverified deploy or a conflicting reading; or "none"), **Better matches checked** (what was searched and the result).

A held-topic FM (section 3) gets the full dedup; its flag only means nothing is filed or commented on before the product owner rules. Say under Flag for Danny whether the matching ticket's expected behavior conflicts with any ruling on that topic.

**Output:** `dedup/<group>.md`, plus `dedup/<group>-timing.md` holding this group's rows for the Timing table (section 11 format). The orchestrator merges them into `generation-provenance.md`; dedup agents never edit it.

**Returns:** path, keys read, keys unreadable.

**Stop conditions:** a candidate key is unreadable after one retry: stop and report; never call a verdict without a full read of every candidate (`rules-core.md`-level hard constraint, restated: no dedup call stands without a full read).

## 10. `dedup-verdicts.md` structure

The orchestrator writes this file from every `dedup/<group>.md`. It must contain, in order:

1. A one-paragraph summary of counts by category.
2. "How the calls were made": restate the scope check and the deploy-and-timing check (point to this file, don't retype them elsewhere).
3. A verdicts table: FM | Verdict | Tickets | Step 3 action.
4. "Calls that changed from the candidate labels": anywhere a dedup agent's verdict differs from what `cluster_defs.py` assumed going in.
5. "Questions for Danny": every Won't Do match, unverified deploy, or conflicting read that needs his call.
6. "Step 3 comments": the list of tickets that will get a comment instead of a new filing.
7. "Re-eval list": table FM | Ticket | Merge (UTC) | Class, for every FM going to re-eval.
8. "Dedup QA": a short pointer to the QA findings (section 13 below handles the full report).
9. **"Final verdicts"**: the mandatory section `round-folder-layout.md` section 4 and evals E10/E17 parse: a table `FM | Category | Basis | Tickets`, where Category is one of the six names in section 5 above, exactly spelled. This table is the only thing E10 and E17 read; keep it current through every Gate 2 edit and rebuild.

## 11. `generation-provenance.md` Timing table format

Required section, format fixed for eval E17:

```
## Timing table
| Key | PR | Merged UTC | Prod deploy UTC | Category |
```

Use `none` in the Prod deploy UTC column when the Development field shows no deployment-environment entry at all. One row per candidate ticket whose timing mattered to a dedup call, not only the ones that became Regressions.

## 12. 2d structure QA brief

Fresh subagent, run in parallel with the dedup QA brief (section 13).

**Inputs:** `failure-modes.md`, `row-map.md`, `input-issues.md`, `cluster_defs.py`, every `ledger/<code>.md` (one at a time, never all at once), `ledger/qa/2b-summary.md`, every `*-second-opinion-diff.md`, `ledger/qa/phrase-scan.md`, `watch-list-prior.md`, `generation-provenance.md`, `clinical-rules.md`, `existing-tickets.md`, `rules-core.md`, `priority-rubric.md`, this file.

**Task.** Check, and report findings as DEFECT, ADDITION or QUESTION rows:

1. **Orphans and double mapping.** Run `build_cluster.py`; confirm it exits 0 and that every FM's row list resolves to real ledger row IDs with no stray IDs.
2. **Over-merged / under-split FMs.** Apply the merge test (section 1) to every FM, with extra scrutiny on any FM spanning more than one action type.
3. **Input-issue calls.** Re-apply `rules-core.md` section 1 to every second-opinion disagreement and a broad sample of the other `input-issue` rows; confirm each names its input and owner.
4. **Missed conflict flags.** Check every row with a Conflict-flag basis against `generation-provenance.md`'s conflict-flag verdict for consistency, and check for any row that should carry a Conflict-flag basis but doesn't.
5. **Rulings and clinical answers.** Check every FM against the ruling memories and `clinical-rules.md` for an unflagged contradiction, and check that every FM citing a rule states its scope correctly.
6. **Scope of guidance.** Confirm every cited rule or snippet is invoked only within the scope stated for it (action type and trigger); see `ledger-schema.md` column "Expected behavior + guidance source".
7. **Dedup candidates, summaries only.** A keyword sweep of `existing-tickets.md` for anything cited; this is a sanity check on candidate selection, not a dedup call (full reads happen only in the dedup agent brief, section 9).
8. **Not-a-failure-mode and decision-item soundness.** Confirm each "not a failure mode" row has a real, checkable reason, and each decision item is genuinely unsettled by any rule or ruling, not a bug in disguise.
9. **Severity, spread and ledger matches.** Check each FM's `SEVERITY` against `priority-rubric.md` section 1 and its worst credible instance. Confirm every `SPREAD_TRACES` draft carries the identical text, on an FM with a counted draft that shows the text is a defect. Apply the merge test to every `WATCH` match, and check every unmatched `watch-list-prior.md` item for a match 2c missed.

**Output:** `qa-2d-structure.md`, a findings table (ID | Type | FM or Row | Finding | Evidence | Recommended fix), followed by a numbered section per check above stating PASS or listing the findings.

**Returns:** path, counts by type.

## 13. Dedup QA brief

One or more fresh subagents run in parallel with structure QA. Each covers a disjoint set of the ticket keys `dedup-verdicts.md` cites, so every cited key sits in exactly one set.

**Do not launch subagents.** Read every ticket yourself.

**Inputs:** the agent's set of ticket keys, `dedup-verdicts.md`, every `dedup/<group>.md` that cites a key in the set, `existing-tickets.md`, `generation-provenance.md`, this file.

**Task.** Re-read, from scratch, every ticket in this set. Do not trust the write-up in `dedup/<group>.md`. For each ticket, and each FM that cites it, confirm the scope-check reading, the timing class, and the verdict independently. Where the re-read disagrees, state the evidence and recommend a fix; where it agrees, say so plainly.

**Output:** a QA file (for example `dedup-qa-1.md`) with:
- a findings table: FM | Call under review | Result (OK / QUESTION / DEFECT) | Evidence | Proposed fix;
- a "Tickets read" table: Key | Read UTC | Comments read | Final scope after comments (one line) | Failures (including any timeout and its retry outcome). The format checker reuses the Read UTC and scope cells at Step 3 (`ticket-qa-briefs.md` section 4), and E28 checks every cited key has a row.

**Returns:** path, counts by result type.

## 14. Gate 2 tables (plain language)

Per memory `gate-tables-plain-language`: say what changes and why. Never present a bare FM, row, or rule ID as if it explains itself; name the behavior and the fix in the same cell.

**Failure-mode table** (columns: failure mode | action types | severity class | counted drafts | counted instances | providers | sources | band | dedup status | filing call). Take every count from `failure-modes.md` (section 2a). Sort by filing call (`file`, then `product owner`, then `comment`, then `hold`), then by the rubric's order within a level.
- "Failure mode" names the wrong behavior and its fix in one phrase (for example "diabetes-attestation content fires on family history, not a personal diagnosis; needs a tighter trigger"), not a bare ID.
- "Providers" gives the count, and says "one provider" when every counted instance comes from one.
- "Sources" names the source kinds behind the counted drafts in plain words, such as "thumbs-downs, edits".
- "Dedup status" names the category in plain words and, where relevant, the ticket it relates to and why (for example "New: no existing ticket restricts this content to a personal diagnosis" or "Re-eval: a fix merged the same day drafts were generated; needs confirming it shipped").
- "Filing call" says why in words, such as "hold: seen once, efficiency" or "file: 3 drafts from 2 providers, minor safety". A ledger match says which ledger row it matched and what it added.

**Held-items table** (columns: failure mode | severity class | counted instances | why held | evidence comment target | rounds waited). One row per `hold` FM and per prior `held` ledger row no FM matched, so the product owner sees every `held` row the ledger will carry.

**Product owner rows**, each in plain words with its evidence. They cover every severe-safety failure mode with zero counted instances (a safety row: file or hold), every held-topic FM, every Won't Do match, and every ledger match that carries a hold flag. Also list unresolved session handles (`ledger-schema.md` section 2a), `not counted:` rows by type, and `contradicted by the draft:` rows.

**Input-issue table** (columns: owner | count | example traces):
- "Owner" is one of the four plain names in `rules-core.md` section 1, never a code or tag name.
- "Example traces" are trace IDs, not row IDs.

Never put a row ID, rule ID, or decision-item ID into any table without also saying in words what it is and why it matters.

## 15. Held failure modes and the evidence ledger

A held failure mode stays visible across rounds as a `held` row in the evidence ledger (`evidence-ledger.md`), so a second occurrence files. There is no separate watch list and no legacy seed: the 2026-11-10 ledger seeding covered Round 1.5, Round 3 and both Provider Pilot Round 1 passes.

**The prior list (Step 1).** `ledger_tool.py prior` writes `watch-list-prior.md` from the ledger's `held` rows. Item is the ledger ID, such as `L-132`. Gate 1 shows the held rows and how many rounds each has waited.

**Matching (2c).** Check every FM against every `watch-list-prior.md` item with the merge test (section 1), and record each match in `WATCH` by ledger ID. A match adds the item's counted drafts and providers, counting each once (`priority-rubric.md` section 2). Drafts match on `tr-` plus the first 8 hex characters. A match whose item carries a hold flag goes to the product owner at Gate 2, never straight to filing.

**The new rows.** After Step 4 the ledger writer adds each held FM as a `held` row, including ones with zero counted instances (they add nothing to a later count), or adds the FM's evidence to the row it matched (`evidence-ledger.md` section 5). A matched FM that still holds stays on the same row with both rounds' evidence. A matched FM that files turns the row's Status to `filed`. `build_cluster.py` writes no watch-list.md.
