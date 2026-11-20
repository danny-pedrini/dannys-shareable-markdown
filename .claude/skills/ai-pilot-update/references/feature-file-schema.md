# Feature files and the update folder

Each feature in pilot or ramp has one folder holding `feature.json`, `themes.md` and one subfolder per update. The worked example is `Project-Galen/Phase-3/Launch/Pilot-Updates/AI-Drafted-Messages/`.

```
<feature folder>/
  feature.json          standing config and Danny's rulings (section 1)
  themes.md             versioned theme map (section 2)
  updates/<YYYY-MM-DD>/ one folder per update (section 3)
```

## 1. `feature.json`

Every value is sourced. Change a value only through Danny's ruling (at Step 0 or a gate). Record the ruling (date, Danny's words, where he said it) in `rulings[]` when he gives it, so the rest of the run uses it. Outside a ruling, the skill edits `feature.json` only at Step 0 (creation) and Step 7 (wrap-up).

| Field | What it holds | Used in |
| --- | --- | --- |
| `feature`, `stage`, `author`, `readers` | Feature name, `pilot` or `ramp`, byline name, who reads the doc | H1, byline, reviewer briefs |
| `doc.id`, `doc.url` | The running update doc; one new tab per update | Steps 1, 5, 6 |
| `doc.tab_title_format` | strftime format of the dated tab title Danny adds (for example `%b %-d, %Y` gives `Nov 10, 2026`) | Step 5 tab match |
| `doc.h1_format` | H1 inside the tab, with `{feature}`, `{stage_title}`, `{week}` | Step 4 |
| `doc.text_width_pt` | Page width minus both margins, in points, measured from the first update's export | Step 5 column widths |
| `doc.sections` | H2 headings in order, as the prior tab published them | `check_doc.py` structure |
| `doc.theme_table` | Column names of the theme table | `check_doc.py` themes |
| `doc.number_exempt_tokens` | Strings whose digits are names, not facts (model versions, doc titles) | `check_doc.py` numbers |
| `updates[]` | One row per published update: date, week, tab ID and title, H1, folder | prior-tab lookup, `compare_tab.py` |
| `rounds[]` | Round folders (repo paths), slug, `evidence` (the list of the round's source kinds), the first update that used each, and `published_as` when a round got its own section or appendix. Each kind is one of `thumbs-downs`, `labeling`, `edits`, `evals`, `interviews` or `slack`, spelled as in `round.json` `sources[]`. | Steps 0, 2 |
| `jira` | Site, cloud ID, epic, labels, launch-blockers dashboard | Step 2 tickets |
| `priority_scale[]` | Danny's priority definitions | Bug tickets section |
| `change_sources` | Slack channels and Confluence pages to read for model and content changes | Step 2 changes |
| `evals` | Run-set source (launch brief), repo, ref, judge folder pattern, catalog, adapter, unit tests, overlays (repo, ref, folder and the spec that wires them), eval owner, confirmed context facts | Step 3 |
| `owners[]` | Name, email, what each owns; doc names owners with mailto links | asks, `check_doc.py` owners |
| `metrics` | Status sheet, definitions page, critical metric IDs, `values_publishable` | Step 2 metrics |
| `sizing` | Sizing sheet, tab, scenario, the current figure Danny ruled, superseded figures | Step 2 sizing |
| `precedents[]` | Precedent rates Danny provided, with his date | Ramp plan |
| `ramp` | Launch brief, ramp steps with dates and gates, the pilot-alongside ruling | Ramp plan, Gate 1 |
| `ticket_rulings[]` | Per-ticket rulings: `counted: false` drops it from counts; `category` overrides the Jira label | `tickets.json`, `theme_counts.py` |
| `rulings[]` | Every other standing ruling, verbatim where Danny gave words. A `superseded` entry (date and what replaced it) retires the ruling, except any part it says stands. | Gate 1 reconfirmation, draft |
| `open_challenges[]` | Reader challenges to a gate or claim that Danny has not ruled on (from doc comments) | Gate 1, draft |
| `banned_link_patterns[]` | URL fragments the doc must never link (session notes, recordings) | `check_doc.py` artifacts |

A new feature has no `feature.json`. Step 0 stops and offers to build one with Danny: every field from a source he names or an answer he gives, with no defaults invented.

## 2. `themes.md`

```
# Themes: <feature>

Version: <n>

> **Source:** <where the mapping came from and who approved it>

## Themes

| # | Theme | What goes wrong | Failure modes |
| --- | --- | --- | --- |
| 1 | <label> | <one line, reader-facing> | <round-slug>: FM-01, FM-16; <round-slug>: FM-04 |

## Not in a theme

| Round | Failure mode | Reason | Ruled by |
| --- | --- | --- | --- |

## Version log

| Version | Date | Change | Ruled by |
| --- | --- | --- | --- |
```

Rules:

- `#` is the rank from the last published update. Ranking is by consistency across providers and sources, not severity (data-methods section 1).
- `Failure modes` names IDs per round slug, because each round numbers its failure modes from FM-01.
- Every failure mode in every round in scope is in exactly one theme or in "Not in a theme". `theme_counts.py` exits 3 and lists any with neither. It exits 2 for one in two themes, or in a theme and "Not in a theme".
- Labels and "What goes wrong" text are reader-facing prose; they pass the writing checks.
- During a run the skill edits a working copy, `updates/<date>/themes-working.md`, never `themes.md` itself. Step 7 promotes the working copy with a version bump and a version-log row when Gate 1 changed it.

## 3. The update folder

`updates/<YYYY-MM-DD>/`, named for the update date (the dated tab's date).

| File | Written by | What it is |
| --- | --- | --- |
| `PROMPT.md` | orchestrator, Step 0 | Danny's invocation, verbatim |
| `STATUS.md` | orchestrator | Current step, next step, decisions in chat (Danny's words), what exists only in chat |
| `run-log.md` | `log_event.py` only | One line per event (trace-schema section 1) |
| `sources.md` | orchestrator | Every resource read this run (ledger-formats section 1) |
| `facts.md` | orchestrator | The fact ledger (ledger-formats section 2) |
| `tickets.json` | orchestrator | Live Jira read of every ticket in scope (ledger-formats section 3) |
| `themes-working.md` | orchestrator | Working copy of `themes.md` with proposed and ruled assignments |
| `theme-counts.md`, `theme-counts.json` | `theme_counts.py` only | Counts; never edited by hand |
| `interview-claims.md` | orchestrator | Claims and verbatim quotes (ledger-formats section 4) |
| `eval-coverage.md` | orchestrator | Theme-by-judge verdicts (ledger-formats section 5) |
| `comments.md` | orchestrator | Unresolved comments on the doc (ledger-formats section 6) |
| `update.md` | orchestrator | The draft, mirrored to the tab |
| `update-agent.md`, `update-agent-<n>.md` | orchestrator | Copy of `update.md` after the orchestrator's last write; renamed to `-<n>` when Danny's edit `<n>` is found |
| `update-danny-<n>.md` | orchestrator | Snapshot of `update.md` each time Danny edits it |
| `build-log.md` | orchestrator | Step 5 write log: each write, its range, the revision ID returned |
| `readback.json` | orchestrator | Step 5 read-back of the tab: tab ID, revision ID, text, element count, table shapes, differences; refreshed after each later write |
| `prior-tab.md` | orchestrator, Step 1 | Text of the prior tab as read this run, with its revision ID |
| `round-hashes.txt` | orchestrator, Step 1 | `shasum -a 256` output for every round file read at Step 1 (eval O-3) |
| `qa-gate<n>-r<k>.md`, `qa-gate1-post-r<k>.md`, `review-<reviewer>.md` | graders | Reports; graders write nothing else |
| `eval-results.md` | orchestrator, from grader reports and script output | Per-eval Pass or Fail with evidence |

Rendered pages go to `/tmp/ai-pilot-update/<feature-slug>/<date>/render/`, not the repo: they are large binaries and need no history. Never write patient names, member IDs, trace contents or other PHI into any file here; quotes are provider words about the tool.
