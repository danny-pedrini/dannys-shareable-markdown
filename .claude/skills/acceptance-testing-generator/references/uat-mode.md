# UAT Mode

Reference for the `acceptance-testing-generator` skill. The UAT-only generation rules for Step 7.
UAT runs read this file at Step 2, beside `references/exemplar-uat.md`. Comprehensive runs do not load it.

---

## Generating UAT tests

**UAT.** Group requirements into sections with prefixed IDs. Each section: 10 to 15 tests
`[estimate range]` and one launch-readiness or production-smoke test. Add cross-section scenarios that
test the seams between sections, not repeats of section tests.

**What NOT to generate in UAT mode.** These three rules exist because each one produced a test that got
deleted on review:

| Do not generate | Why | Instead |
| --- | --- | --- |
| A test confirming a non-goal or out-of-scope item is absent | Tests trace only to the PRD's requirements and metrics | Point Scope to the PRD's out-of-scope section. If an exclusion carries clinical or trust weight ("the pane shows no AI recommendation," "no action executes without a provider step") and the PRD doesn't state it as a requirement, raise it with Danny in the Step 14 summary as a candidate requirement |
| A design-verification test per section | It forces a contrived row wherever a section has no design surface | Write design-verification tests only where a real design surface exists, wherever that lands. A document with three sections may have two design tests, or one |
| A test for an engineering-internal interface | A Care Ops or provider executor cannot run it, and a `[Eng]`-tagged row in a stakeholder document is dead weight | Name the requirement in Scope under a heading like "In the launch, verified outside this document" and say who verifies it |

**Ownership: one document-level default.** Fill the Execution section rather than adding columns. State
one Setup By and one Executed By for the whole document. Care's normal shape is setup by Eng or QA,
executed by Care Ops and providers. Use a per-section pair only when an entire section genuinely has a
different executor, and say why in a sentence. Then tag individual rows that depart from the default,
using the closed six-tag vocabulary: `[Staging]`, `[UAT]`, `[Prod]`, `[Design]`, `[Clinical]`, `[Eng]`.

**A tag that matches the document default is noise. Delete it.** If the environment is Staging, no row
carries `[Staging]`. If Eng executes a whole section, tag the section in prose rather than tagging every
row in it.

**No tag-density rule.** A document-level default plus honest per-row exceptions is the goal, and a
section where most rows are `[Eng]` is fine when engineering genuinely runs most of that section. Do not
restructure ownership to reduce tag count.

## Multi-source orchestration (several requirement documents)

A Galen launch spans several requirement documents. Complete the Chart, EMR 2.0, AI-drafted messages,
and the CDS guarantees are separate specs that ship as one provider-facing release. When more than one
requirement document is in scope, fan out rather than working through them serially in this thread.

1. **Confirm scope with Danny first.** List the documents you found and which you plan to include.
   Do not decide the boundary yourself
2. **Assign a section prefix per document.** Three to four letters, derived from the document, stable
   across runs. `CTC` for Complete the Chart, `CHT` for the chart experience, `MSG` for drafted
   messages, `CDS` for the service guarantees
3. **Spawn one subagent per pair of documents.** Pair two documents when their combined requirement
   text fits one subagent context with room for the output. `[Assumption: a combined size under
   60,000 characters fits (needs validation)]` A document too large to pair, or the odd one left over,
   gets its own subagent. Each subagent receives: each document's content with its prefix, the mode's
   altitude rules, the exception-tag list, and the instruction to return, per document,
   only a purpose line plus a test table. No appendix, no metadata, no boilerplate
4. **Run Eval Gate 2 on each document's test table,** not once at the end. Subagents return one test
   table per document, so Gate 2 is the applicable gate. Bad draft tests in one section are cheaper to catch before
   consolidation mixes them in. Eval Gate 1 stays a single pass in Step 5, before any fan-out,
   against the combined inventory
5. **Consolidate in this thread.** Deduplicate across sections, build the cross-section dedup table
   naming the authoritative section for each shared area, and add the cross-source scenarios that
   test the seams between documents
6. **Sweep for altitude drift.** Sections generated independently drift toward field-level detail.
   Any section over 15 tests gets consolidated

Subagent prompt skeleton:

> "Generate UAT acceptance tests for one or two requirement documents. For each document:
> requirements `[content]`, section prefix `[PFX]`. Keep each document's tests in its own table under
> its own prefix. Use only that document's own terms in its table, never a term from the other document.
> Engineering has completed integration testing, so generate high-level
> scenarios a provider or Care Ops stakeholder can execute, NOT field-level validation. Target 10 to
> 15 tests per document. `[estimate range]` Columns, exactly four: Test #, Area/Theme, Validation and Behavior,
> Pass/Fail Note. Do not add an environment or ownership column. Instead, report separately: the
> Setup By and Executed By pair for this section ONLY if it differs from the document default of setup
> by Eng or QA and execution by Care Ops and providers, chosen from Setup By (Eng, Ivy Team, Care Ops,
> Clinical) and Executed By (Provider, Clinical Ops, Care Ops QA, Eng, Design). Tag any row departing
> from that default using only these six tags: `[Staging]`, `[UAT]`, `[Prod]`, `[Design]`,
> `[Clinical]`, `[Eng]`, placed in its Area/Theme cell. Invent no other tag.
> Cite requirement IDs inline. Include one launch-readiness or production-smoke test. Include a
> design-verification test ONLY if this section has a real design surface; if it does not, say so and
> write none. Do not write a test for a non-goal or out-of-scope item; tests trace only to
> requirements and metrics. Do not write a test for an engineering-internal interface
> that a Care Ops or provider executor could not run. Never invent a threshold the requirements do not
> state. Never write a test measuring AI output quality. Return, for each document, three things and
> nothing else: a one-line purpose statement, any ownership departure from the document default, and
> the four-column test table."
