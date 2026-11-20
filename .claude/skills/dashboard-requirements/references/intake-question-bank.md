# Intake question bank

Source for Step 2. The orchestrator reads the inputs first, drops every question the inputs already answer, and asks the rest in one numbered batch in chat with a default per question. Never the AskUserQuestion tool. The twelve section names below are the rows of the intake gate coverage table.

Write each question as one sentence. Give the default in the form "Default: X." When the inputs half-answer a question, state what was found and ask only for the gap.

## A. Purpose and audience

1. What single question should the dashboard answer? Default: whether [Build] achieved its primary outcome without breaking a guardrail.
2. Who are the ADS leads, and does ADS split the work across teams (for example AI analytics and care analytics)? Default: one ADS lead named at intake.
3. Who beyond ADS reads this document? Default: Care Ops, Clinical Quality, Finance as stakeholders; Eng, Product, Design as informed.
4. Where should the finished document be saved? No default.

## B. Build, rollout, and arm assignment

5. In one sentence, what does the build do for the user? Default: taken from the PRD's problem statement.
6. How does it roll out: randomized experiment, staged ramp without a control, or fleet-wide? Default: randomized with a permanent control.
7. What is the randomization unit (member, provider, visit), and why that unit? Default: whatever the PRD or Eng has stated; flag if unstated.
8. What are the ramp steps and the control share? Default: `[TBD: Eng]` for steps; control share as stated in the PRD.
9. Is arm assignment recorded and queryable in the warehouse today? Default: unknown; becomes the hard dependency and an open question.
10. Are there other builds shipping together that need their own section? Default: no.

## C. Exposure and population

11. Who is eligible, stated as a population the denominators can rest on? Default: the PRD's target population at the trigger point.
12. What is excluded (test accounts, escalations, consent, sync visits)? Default: internal and test accounts, plus PRD-cited carve-outs.
13. Does exposure depend on another experiment's treatment group (nesting)? Default: no.
14. Are there state distinctions a reader could conflate (member against subscriber, gross against net eligible)? Default: none; if yes, §2 gets the state-progression paragraph.
15. What is the launch scope, and what expands the denominator later? Default: the PRD's launch scope.
16. Which child objects inherit the arm (visits, tasks, asks)? Default: every visit and task inherits its member's or provider's arm.

## D. Business outcomes

17. What is the primary business outcome, in dollars or another unit? Default: cost savings.
18. Where is the sizing model, and which scenario is the source of truth? No default; if none exists, business outcomes carry `[TBD: owner]`.
19. Which reconciling metric feeds each dollar figure, and what rate converts it? Default: payable hours × blended provider rate, rate owner named.
20. Does the PRD require the booked, committed, pipeline split? Default: yes if the PRD says so.
21. Which levers are committed and which are optimistic? Default: only the primary outcome is committed; the rest are measured but not committed, stated in Scope notes.

## E. Hero metrics

22. What one or two metrics decide whether the build worked? Default: the PRD's primary success metric.
23. Are they measurable today, and at what grain? Default: unknown until the inventory step.
24. Where does the baseline come from, and who owns pulling it? Default: `[TBD: ADS lead]`.
25. Where does the target come from? Default: `[TBD: PM]`; never derived from a sizing coefficient without approval.

## F. Reconciling metrics

26. Which sizing coefficients should the dashboard reconcile to? Default: every coefficient in the source-of-truth scenario.
27. What number does leadership already read for this problem, and should the dashboard show it? Default: yes, as a reconciling row.

## G. Driver metrics

28. Which patient-side behaviors drive the hero (reply, completion, abandonment)? Default: taken from the PRD's leading indicators.
29. Which provider-side behaviors drive the hero (time to decision, skips, review depth)? Default: same.
30. Which system behaviors drive the hero (latency, write-back quality)? Default: same.

## H. Guardrail metrics

31. Which clinical quality signal guards the build, and who owns it? Default: the existing Clinical Quality Score, owner Clinical Quality.
32. Which patient experience signals guard it (cancellation, false-positive asks)? Default: from the PRD.
33. Which provider experience signals guard it (VoC, skip rate)? Default: Care Ops VoC, owner named at intake.
34. For each guardrail, is there a sourced alarm threshold, and if not who sets it? Default: `alarm threshold: [owner]`.

## I. Slices

35. Which slices matter beyond time period and arm? Default: cohort (new against existing), ramp step.
36. Which slices are deliberately excluded, and why? Default: brand, treatment type, channel when the launch is single-brand, single-treatment, single-channel.

## J. Instrumentation and sources

37. Which metrics need instrumentation that does not exist yet? Default: unknown; flagged in Next steps.
38. Are user-behavior metrics needed, and do they live in Amplitude or the warehouse? Default: flagged as an open question, one mention.
39. Which existing metrics must be referenced rather than redefined? Default: any metric another team already publishes.

## K. Ownership

40. Who owns each open question? Default: named per question; no row without an owner.
41. How does ADS split the metrics into workstreams? Default: illustrative split by system of record, ADS finalizes.

## L. Process

42. Is there an upstream working copy (Google Doc, Confluence), and should the local file track it? Default: yes if provided; source block records divergence.
43. Are there review comments or threads to treat as candidates? Default: read and surface at the selection gate, never auto-adopt.
44. Who reviews the draft, beyond the default reviewer set? Default: data-analytics-eng and pm-exec, plus conditional reviewers per the rules.
45. What is explicitly out of scope for this document? Default: later phases, other builds, experiment design, launch plan.
