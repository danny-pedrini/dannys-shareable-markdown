# Data methods

How each fact in the update is produced. Rules are general; lines marked *Example (Round 1)* are eval examples from the Week 1 update, not rules.

## 1. Theme rollup

- **Scope.** Counts cover the rounds new since the prior update (`feature.json` `rounds[]` with `first_update` empty, confirmed at Step 0). If no round is new, the feedback section says so and shows no counts.
- **Assignment.** Copy `themes.md` to `themes-working.md`. For each failure mode in a new round, propose an existing theme or "new theme" from its `failure-modes.md` description, and mark the proposal `(proposed)`. Run `theme_counts.py --themes themes-working.md`.

  Danny rules at Gate 1; update the working copy and rerun. Only `theme_counts.py` writes counts.
- **Drafts flagged.** Distinct counted drafts per theme across all of a round's sources (`counted_drafts`). A draft counts when its `row-map.md` row is Counted `yes`. An older round's row map has no Counted column, so `theme_counts.py` applies the failure-mode skill's allow-list to its ledgers (`priority-rubric.md` section 2). Audit rows (Evidence basis `inferred`) count separately as "found on review" (`audit_only`). An uncounted provider edit is supporting evidence, not an audit finding. Never present audit findings as what providers flagged. *Example (Round 1): Pricing was 5 flagged plus 7 found on review.*
- **Counted once per theme.** A draft a prior update counted under a theme doesn't count again under that theme (`already_counted`). It can still count under another theme.
- **Interviewees.** Count the people who raised each theme from the syntheses and session notes (section 4). The script's session-row count is a floor: the doc's count is at or above it. *Example (Round 1): session rows gave Pricing 0 and Clinical judgment 1; the syntheses gave 3 of 5 for each.*
- **Tickets per theme.** The open `Filed:` keys of the theme's failure modes in the new rounds, counted with `tickets.json` (live Jira plus Danny's ticket rulings; section 5). *Example (Round 1): the published clinical-judgment cell said 11 after Danny dropped a P1; the counted value is 10.*
- **Ranking.** Rank by how consistently a theme recurs across providers and sources, not by severity. Say in the doc that ticket priority carries severity and frequency.
- **Split by source.** The theme table counts every source together. Show the split by source (`by_source`) where it helps a reader, for example when one source drives a theme. A draft two sources back counts under each, so the split can sum past the total. Source-specific detail, such as edit depth, goes in the round's appendix (doc-spec Round appendices).
- **Carrying a round's section forward** (Step 0 ruling). Rebuild it from the sources Danny names, read this run. Never copy the prior tab's text or numbers into it. When a ruling links the prior tab's section instead, keep the section's heading and put only that link under it.
- **Comparability.** A theme change (split, merge, new theme) bumps the `themes.md` version, and the doc says which counts aren't comparable to the prior update.

## 2. Lessons worth computing every round

From `theme-counts.json`, for each new round:

- Held one-offs (`held.one_offs` of `failure_modes`): this round's failure modes held at one counted instance. The watch list's row count (`held.watch_list`) can be larger, since it adds audit-only holds and earlier rounds' items. A high share argues for fixing classes of failure, not one ticket at a time. An older round has no watch list, so report its failure modes resting on a single draft instead (`single_draft_fms` of `failure_modes`). *Example (Round 1): 36 of 46 rested on a single draft.*
- Drafts with only input issues (`input_only_drafts` of `drafts`): no row maps to a failure mode and at least one is an input issue. These need EMR or Care Ops owners, not prompt fixes. Name the input problems from the round's `input-issues.md`. *Example (Round 1): 15 of 77.*
- How sensitive the signal is, from how the round was collected (for example, providers coached to flag a single sentence). State it only from a source read this run.

## 3. Since last update

- Build every number fresh from this run's sources. Never carry a number forward from the prior tab or the prior `facts.md` as a current value.
- When a prior update exists, add a "Since last update" block under the TL;DR: what changed in tickets, gates, metric status, model and content changes, and eval coverage.
- Compare against what readers saw: the prior tab, read this run (`prior-tab.md`). Each prior value the block uses enters this run's `facts.md` as a `read` fact cited to the prior tab, and appears only in the block.
- When the prior update has a folder (`feature.json` `updates[].folder`), list at Gate 1 each published number that differs from its `facts.md`. They may be Danny's hand edits; the block compares against the published number either way.
- Where this run's sources contradict a published number for the same period, list it at Gate 1 for Danny's ruling. *Example (Round 1): the filing ledger and Jira give 33 tickets and 13 safety; the published tab says 32 and 11, after Danny's two ticket rulings.*

## 4. Interviews

- Read every interview source each new round lists: its `round.json` `sources[]` entries of kind `interviews`, or `extra_sources` in an older round. Read syntheses and session notes both.
- Write one `interview-claims.md` row per claim per speaker. Count each claim by who said it, not how often it appears.
- Copy every quote character for character, with its location in the source (quote index number or heading).
- Compare attributions across sources. When the notes and a synthesis credit the same words to different people, mark the conflict and leave the quote out.
- A theme backed only by thin data stays in the doc only when two sources support it, and the doc says how many.
- Attribute quotes in the doc by provider name and date. Never link session notes or recordings.

## 5. Tickets

- Read keys from the merged `filing-ledger.md` (with its Amendments section) of every filed round in `feature.json` `rounds[]`, in scope or not, and evidence comments from `comment-ledger.md`, never from draft files.
- Query the epic in `feature.json` `jira` for every key created since the prior update, and for every open ticket a ramp gate names (for example, open P0s). A key from the created-since query that is in no round's ledger is "filed outside a round" and gets its own line in the doc. Keys from the gate query feed only the gate's status.
- Carry forward every key the prior update listed as filed outside a round, so it stays counted while open. Take those keys from the prior update's `tickets.json`, or from `prior-tab.md` when the prior update has no folder.
- Read every key live in Jira into `tickets.json`, with its status category. Apply `feature.json` `ticket_rulings` (`counted`, `category`). Jira wins over the ledgers for status, priority and labels; a ruling wins over Jira, and the doc reflects the ruling.
- **Which tickets count** (`feature.json` `rulings[]`, 2026-11-05). Ticket counts cover open tickets only: Jira status category not Done. Doc-wide counts and Appendix A cover every filed round plus tickets filed outside a round, so they update even when no round is new. A theme's count covers the new rounds' open tickets in that theme. A Done ticket drops out of every count, and the "Since last update" block gives the open count's change from the prior tab.
- Recompute every dependent count from `theme_counts.py` output: TL;DR, pilot table, priority table, theme table and appendix.
- Use `feature.json` `priority_scale`, and name the efficiency issues raised to P1.
- Re-read every key at Step 5, before the push. If anything changed since Gate 2, go back to Gate 2 with the changes.

## 6. Model and content changes

- Read the Slack channels and Confluence pages in `feature.json` `change_sources` for the window since the prior update, plus any source Danny adds at Step 0.
- Cite each Slack fact to the specific message's permalink, not the thread root. Record each cited message in `sources.md`.
- Each content change gets a status and an ask to a named owner from `feature.json` `owners`, with a mailto link.

## 7. Metrics status

- Read the metrics status sheet and the definitions page live.
- Report which metrics have data, not their values, until Danny rules `values_publishable` true at Gate 1.
- Stamp the status with an "as of" time from the read, and name the instrumentation owner.

## 8. Sizing and precedents

- Read the sizing sheet directly (tab and scenario from `feature.json`). At Gate 1, ask whether `sizing.current_figure` is still current. Never cite a superseded figure.
- Label every number you derive (for example, a per-point savings sensitivity) as `derived` in `facts.md` with its formula. Recompute it after any ruling that changes an input.
- Precedent rates come from `feature.json` `precedents`, stated plainly in the doc.

## 9. Ramp plan

- Gates, dates and bars come from `feature.json` `ramp`. When the launch brief disagrees, use the feature file and say so in the doc. *Example (Round 1): "one day later than the launch brief".*
- Report each gate's status from a source read this run. A gate on open tickets uses the epic query in section 5.
- An item under `open_challenges` stays visibly open in the doc ("under discussion") until Danny rules.
- Keep the rulings in `ramp.pilot_alongside` and `rulings[]`; restate them only as Danny worded them.

## 10. Comments on the doc

- Read every unresolved comment and reply on the doc (Drive `list_comments`) into `comments.md` at Step 2, and again at Step 5.
- Flag every comment that challenges a gate, number or claim. Danny rules at Gate 1.
- Never reply to, resolve or edit a comment.
