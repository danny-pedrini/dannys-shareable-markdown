# Gold Exemplar

The PRD to imitate. Loaded by the orchestrator at Step 1 and routed to the plan and draft subagents (SKILL.md `<input_routing>`).

> **Source:** "[PRD] Provider Pay: EMR Changes for the December Pay Model," PM Danny Pedrini. A prd-generator run that Danny edited by hand and published. Local file `Project-Galen/Provider-Pay/Provider-Pay-EMR-December-PRD.md`; Confluence page. Named the gold exemplar by Danny on 2026-11-02.

Read the local file in full. It is not copied here, so this pointer stays current as Danny edits it.

## Imitate

| Pattern | Where in the Provider Pay PRD |
| --- | --- |
| TL;DR moves from today to the sized impact to what we build, and cites story ID ranges instead of restating stories | TL;DR |
| Business problem opens with the baseline, then gives each motivation as a bolded line that walks through the mechanism in plain steps | Business problem |
| Feature impact on its own bolded line; the Note frames the larger initiative's phases and why it needs this launch | Feature impact, Note |
| Metric baselines carry real figures with a source; a never-measured metric reads "None (new metric)"; every target is numeric or `[TBD: needs data]` | Metrics |
| Each Out of scope line gives one line of why; a planned item also says where it lands and cross-references the section that holds the detail | Out of scope |
| Story groups open with one sentence per group, then a `####` header and table each | User stories |
| Today cells describe the current state concretely enough for a cold reader | PAY and PIN tables |
| Rollout names who checks each exit bar and who makes the go/no-go call | How does it roll out? |
| Each dependency states what we need and which story waits on it | What do we need from others? |
| Each open question ties its Needed by to the decision it unblocks | What's still open? |
| Alternatives considered records an option that was actually debated, and who preferred it | Appendix |

## Do not carry over

- **Revision markers and the Change log.** That PRD carries them because Engineering and Design had seen it. An unshared PRD edits in place (SKILL.md Step 0, question 7).
- **Engineering detail in a Today cell.** PAY-08's Today cell names an API path and a feature flag. That is E09 encroachment, so don't imitate it.
- **Its launch type.** It is a non-AI launch, so it has no Back data or Shadow stages, no Eval bar row, and no clinical quality guardrail. For an AI launch, take those from the template rules.
- **Its facts.** Every name, number, and date in it belongs to Provider Pay.
