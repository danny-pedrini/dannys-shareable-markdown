# QA briefs

The orchestrator writes; subagents grade. Every grader is a fresh subagent with no memory of earlier rounds. It reports and never edits.

## Rules for every subagent

Paste these into every brief: gate graders, both reviewers and the trace author.

- Read `AGENTS.md` first. The MCP no-inference rule applies to you.
- You report only. Write exactly one file, your report or trace at the path given. Edit nothing else.
- If you can't open a source you need (a tool is missing, a read fails twice, a link won't open), write `STOP: <server> <tool> <resource> <error>` at the top of your report and stop. The trace author puts that line in its reply and in the trace's `observations`, so the file stays valid JSON. Never work from memory or a summary.

## Rules for gate graders

Paste these too into every gate grader's brief:

- Grade every eval your brief lists as Pass or Fail, with evidence: a file and line, a source link, or a quoted passage. By default, your brief lists every eval for your gate in `evals.md` except those the trace author grades. A Fail with no evidence is not a Fail.
- Findings beyond the evals go in a separate list, each marked `defect` (wrong number, broken reference, contradiction with a source) or `addition` (anything else).

## Round protocol (orchestrator)

1. Spawn the grader. Log it with `log_event.py subagent`.
2. Fix every defect yourself, in your own files. Confirm each fix against its source first.
3. Spawn a fresh grader on the fixed files. Log the round with `log_event.py qa_round`.
4. Stop after 2 fix rounds. Present any remaining Fail to Danny at the gate, with its evidence.
5. Bring every `addition` to Danny row by row at the gate. Never adopt one on your own.

## Gate 1: fact grader

**Inputs:** the update folder; `feature.json`; `themes-working.md`; every round folder in scope; the references `data-methods.md`, `eval-coverage-method.md` and `ledger-formats.md`; `evals.md`.

**Brief:**

> You are grading the fact ledger for an AI pilot update before the author drafts anything. Re-open every source in `sources.md` yourself, not a sample: MCP reads for live sources, repo reads for files.
>
> For each row of `facts.md`, check the Value against the source. For `computed` rows, rerun the script named in Source. For `derived` rows, recompute the formula. Check `tickets.json` against a live Jira read of every key.
>
> Check every quote in `interview-claims.md` character for character against its source, and check attribution against the session notes. Check every `eval-coverage.md` verdict by opening each cited file at its blob SHA and finding the quoted rule. A claim about what judges see or receive must cite the adapter or `feature.json` `evals.context_confirmed`. Check `comments.md` holds every unresolved comment `list_comments` returns.
>
> Then grade the Gate 1 evals. Write your report to `qa-gate1-r<k>.md`.

**Post-ruling brief (Gate 1 step 4):** the same inputs plus `STATUS.md`.

> You are grading the fact ledger after Danny's Gate 1 rulings, which `STATUS.md` records in his words. Grade only these evals: <the list from SKILL.md Gate 1 step 4>. For each, re-open the sources its definition in `evals.md` names, and check that every ruling was applied as he worded it. Write your report to `qa-gate1-post-r<k>.md`.

## Gate 2: general doc grader

**Inputs:** `update.md`; the `check_doc.py` and `check_facts.py` output; `facts.md`; `interview-claims.md`; `eval-coverage.md`; `comments.md`; `feature.json`; `doc-spec.md`; `forbidden-writing-patterns.md`; `prior-tab.md`; `evals.md`; any `update-danny-<n>.md` snapshot.

**Brief:**

> You are grading a draft stakeholder update on an AI feature in pilot or ramp. Its readers include engineering leaders, who need a data-driven, methodical path to the feature's outcomes. Check that every number, date, status and quote matches its row in `facts.md` or `interview-claims.md` for that specific place in the doc, and that no superseded figure appears.
>
> Check structure and content against `doc-spec.md`, and run the workspace writing checklist line by line. Check that no challenged gate or claim in `comments.md` is stated as settled. If a snapshot of Danny's edits exists, check every line he changed survives verbatim.
>
> Then grade the Gate 2 evals. Write your report to `qa-gate2-r<k>.md`.

## Gate 2: specialized reviewers

Spawn `ai-eng-reviewer` and `pm-exec-reviewer` in parallel with the first Gate 2 grader. They review once per run, on the first draft.

**`ai-eng-reviewer` brief:**

> Review this draft update on an AI feature in pilot (`update.md`), as a senior AI engineer would before trusting it. Focus on the eval-coverage verdicts, what the eval gaps mean for the ramp, the model-change reasoning, and whether the gates can catch a quality regression. `eval-coverage.md` holds the judge rules quoted from the code at recorded SHAs.
>
> Any claim you make about what a judge checks or sees must quote a passage from a file listed in `sources.md`. Mark it `unverified` otherwise. Return Must Fix, Should Fix and Consider, each marked `defect` or `addition`. Write to `review-ai-eng.md`.

**`pm-exec-reviewer` brief:**

> Review this draft update on an AI feature in pilot (`update.md`), as a product executive would before acting on it. Focus on whether the TL;DR leads with what readers must know and whether the ramp bar and business case are clear and sourced. Check that each ask has an owner and that the doc is ready for its readers (`feature.json` `readers`).
>
> Every number must trace to `facts.md`; flag any that doesn't. Return Must Fix, Should Fix and Consider, each marked `defect` or `addition`. Write to `review-pm-exec.md`.

The orchestrator adopts a reviewer's claim about judge behavior only when a file read this run confirms it (eval-coverage-method section 4).

## Gate 3: render grader

**Inputs:** the page images and page text in the render folder; `links.tsv`; the `compare_tab.py` output; the last `check_doc.py` output; `readback.json`; `build-log.md`; `update.md`; `doc-spec.md` (layout targets); `evals.md`.

**Brief:**

> You are checking a Google Docs tab as readers will see it. The page images are the rendered tab. Look at every page.
>
> Check every table against the layout targets in `doc-spec.md`: no equal-width default columns, no header word broken mid-word, bold shaded headers, 9-point text in wide tables, and nothing cut off or overflowing. Check that nested bullets nest and numbered lists number as `update.md` intends. Read the `compare_tab.py` output and confirm each difference it lists against the page images.
>
> Then grade the Gate 3 evals. Write your report to `qa-gate3-r<k>.md`, with each layout problem named by page and table.

## Trace author (Steps 6 and 7)

**Inputs:** the update folder (`run-log.md`, `STATUS.md`, `sources.md`, `eval-results.md`, every QA and review report, `build-log.md`, `readback.json`), the last line of `observability/invocation-log.jsonl`, `evals.md`, `trace-schema.md`.

**Brief:**

> You are an independent auditor for an `ai-pilot-update` run. You did not run it; you inspect the files after the fact. Author the run's trace at the path given, following `trace-schema.md` exactly.
>
> Compile `steps`, `gates`, `mcp_errors`, `stops`, `subagents`, `qa_rounds` and `checks` from `run-log.md`. Recount `counts` from the files. List `context_sources` from `sources.md`, and confirm each local path exists. Record decisions beyond default behavior from `STATUS.md`.
>
> Fill `gate_evidence` per `trace-schema.md` section 3; ambiguous evidence is `false`, with the reason. Base every finding on the files, not on the invocation-log line. Write "not recorded" for anything missing.
>
> At Step 7, also grade every eval whose Gate in `evals.md` says "trace author" as Pass or Fail, and add each to `eval_results` with its evidence in `detail`. On a resume after a stop, grade O-2 the same way. A Fail with no evidence is not a Fail.
>
> Edit nothing except the trace file. Report: "Trace authored. Context sources: N. Decisions: N. Gate evidence: N of 4 gates confirmed", plus any issues.
