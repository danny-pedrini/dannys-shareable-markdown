# Intake Question Bank

Used in SKILL.md Step 2. Drop every question the inputs or Step 0 already answer, and say which input answered it. Ask the rest in one numbered batch in chat, each with its default. Never use AskUserQuestion. Section letters match the rows of `<intake_gate>`.

A default is a proposal for Danny to confirm, drawn from the inputs. Never default to a number, name, or date the inputs don't contain; default to `[TBD: needs data]` or `[TBD: owner]` instead.

## A. Subject, launch and persona

Answered at Step 0 (subject, persona, AI launch). Row A passes from those answers.

## B. User problem

1. Who has the problem, and what job are they trying to do? **Default:** the persona from Step 0 and the job the inputs describe.
2. What is the biggest discovery insight behind it? **Default:** the strongest insight in the inputs, named with its source.
3. Which evidence backs it (research, analysis, tickets, Slack)? **Default:** the hosted links in the inputs; any claim without one gets an `[Assumption: X (needs validation)]` tag.
4. How does it work today, and what is the workaround? **Default:** the current state the inputs describe. *Skip when* the inputs describe today's workflow.

## C. Business problem

1. What impact is this change sized at, on cost and on quality (savings, cost avoided, revenue, or a metric's movement), and which doc sizes it? This is the Feature impact line, never the baseline. **Default:** the sized figure and hosted link in the sizing input; otherwise `[TBD: needs data]`.
2. What baseline is that impact measured against (current spend, volume, or rate), and which doc backs it? **Default:** the baseline the sizing input or other inputs state, with its hosted link.
3. Why is the business making this change? List every motivation the inputs give (cost, quality, provider or patient behavior, operations). **Default:** the motivations the inputs state, each with its source.
4. Is this PRD one team's part of a larger initiative? If so, who drives it, and why does it need this part? **Default:** the initiative the inputs name; otherwise standalone.

## D. Goals and metrics

1. What are the goals, in priority order (3 max)? **Default:** outcomes derived from the problem section, for confirmation.
2. What is the primary metric, with its baseline, target, and source? **Default:** the cost metric the inputs name; unknown values are `[TBD: needs data]`.
3. Which guardrails apply, with baselines and targets? **Default for an AI launch:** the clinical quality measure the inputs name; otherwise `[TBD: needs data]` and an Open question to Clinical.
4. Are there leading metrics worth tracking? **Default:** none unless the inputs name one.

## E. Not doing

1. Which outcomes are we explicitly not pursuing? **Default:** any the inputs rule out.
2. What work is excluded from this launch, and where does it land? **Default:** later phases and categories the inputs mention, one line each.

## F. What we're building

1. What is the hypothesis: if we change what, which metric moves, and why? **Default:** drafted from the problem and the primary metric, for confirmation.
2. Which screens or surfaces change? **Default:** those in the prototype or Figma captures. *Skip when* no screens change.

## G. User stories

1. What must each persona be able to do at launch? **Default:** the stories the inputs describe, listed one line each for Danny to add to or cut.
2. What priority does each story carry (P0 launch blocker, P1 targeted for launch, P2 after launch)? **Default:** P0 for anything the inputs call required for launch, P1 otherwise.
3. Which story ID prefix(es) apply? **Default:** the prefix the inputs or the initiative already use (e.g., MSG- for Galen drafting); otherwise one short prefix per surface, proposed.

## H. Rollout and fallback

1. Which stages, and which audience at each? **Default for an AI launch:** Back data, Shadow, Phased ramp (with the holdout the inputs name), GA. **Otherwise:** Phased ramp, GA.
2. What exit criteria gate each stage? **Default:** the thresholds the inputs state; otherwise `[TBD: needs data]`.
3. What does the user see when there is no AI output? **Default:** today's experience, as the inputs describe it. *Skip when* not an AI launch.
4. Who makes the final clinical decision? **Default:** the provider, as the inputs state it, for confirmation. *Skip when* not an AI launch.

## I. Risks

1. What could go wrong, with what mitigation and owner? **Default:** the risks the inputs raise.
2. Which claims in the inputs are unconfirmed or disputed? **Default:** each one, asked as a question here; a disputed belief that a decision rests on becomes a Risks row.

## J. Dependencies

1. What does the launch need from another team, including Care Ops workstreams (pay model, training, sign-offs)? Who owns each, and does the launch wait on it? **Default:** the cross-team asks the inputs name.

## K. Open questions

1. What is still undecided, who owns it, and by when? **Default:** the open items the inputs list.

## L. People and related docs

1. Who are the PM, tech lead (or backend and frontend leads), design lead, and, for a clinical launch, clinical lead? **Default:** names from the inputs or the stakeholder directory; otherwise `[TBD: owner]`.
2. Which functions approve, and which don't apply to this launch? **Default:** the template's rows (Product, Engineering, Design, Clinical, Legal, Care Ops), with functions the inputs show as uninvolved removed.
3. Which related docs exist, as hosted links: background docs, sizing, acceptance criteria, prototype, mocks, dashboard requirements, and the eval bar for an AI launch? **Default:** the hosted links in the inputs; every other standard row stays as an empty slot.
4. Were 2 or more solution approaches debated? **Default:** no; the Alternatives considered section is omitted.
