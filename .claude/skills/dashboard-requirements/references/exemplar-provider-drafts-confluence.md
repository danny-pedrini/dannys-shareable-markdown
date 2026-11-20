# Provider Drafts: Experimentation & Dashboard Requirements

> **Source:** Confluence live doc Provider Drafts: Experimentation & Dashboard Requirements, page 3480027223, version 1 (live-doc step 2592), read via Atlassian MCP on 2026-09-29 at 23:19 ET. This is Danny's published edit of the skill's Provider Drafts run, kept verbatim as the second gold exemplar. Live docs change without a version bump, so the live page may have moved on.
>
> The markdown export is lossy: underline formatting is dropped, and table header cells come out bold, which the template does not allow (E29). One known error is listed in `exemplars.md` under the Provider Drafts "Do not imitate" table.

| **Doc status** | **DRAFT** |
| --- | --- |
| **Last updated** | 9/29/26 |
| **PM lead** | [Danny Pedrini](mailto:you@example.com) |
| **ADS leads** | [Care Analytics lead, Analytics and Data Science] [teammate] (Care Analytics)[teammate] [teammate] (AI Analytics) |

## Summary

**What ADS should build:** one dashboard answering whether Provider Drafts improves messaging quality and lowers average handle time (AHT) without harming safety or experience: 18 metrics across business outcomes, hero metrics, reconciling metrics, drivers, and guardrails.

**Primary outcome and sizing:** messaging quality (metric A1, aka Clinical Interaction Score) is the hero leading indicator of patient experience and retention (metric O2) is the corresponding lagging business outcome we hope it drives; similarly, Messaging AHT (metric A2) is the hero leading indicator on the cost side and cost savings from AHT reduction (metric O1) is the lagging business outcome it drives. O1's sizing estimate is $1,218,434 for FY2027 for Hers WL alone and $2,290,001 across all treatments (ADS Sizing SOT, Scenario 4).

**Launch date:** 10/12/2026 (program status yellow a/o 9/29/26)

**Links:** PRD | Message Content and Eval Requirements | Acceptance Criteria | ADS Sizing SOT | Care Coach Drafts dashboard | [AI Eng lead] launch plan 

**What this is not:** 

- Not a Looker build spec, so no SQL, LookML, event schemas, or tile layout. 
- Not a launch plan, so eng owners and dates live elsewhere. 
- Instrumentation requirements are Eng's. 
- Test plan with experiment power and sample size details are ADS’s. 
- Out of scope: AI Recommended Actions (Phase 2), Complete the Chart and EMR 2.0 metrics, launch plan and ramp criteria, judge calibration, and provider pay use of CIS.

**Scope notes:** CIS launches on semi-calibrated judges (they haven’t yet gone through round of human labeling, though a business case is being made to secure the necessary resources post-launch). LLM-judge-based metrics are inherently directional, and we will live with the directionality in our measurement of message quality and its association to retention.

### Stakeholders

| Care Ops | [Care Delivery director], [Care PMO project manager], [Strategy & Ops partner], [Clinical Ops lead], [Lead, Program Management], [Care Delivery Experience lead], [Workforce Management lead] |
| --- | --- |
| Clinical Quality | [Clinical Quality co-lead] |
| Finance | [VP of Engineering], [Finance partner] |

### Informed

| Engineering | [Eng manager], [Distinguished Engineer], [AI Eng lead], [backend engineer], [frontend engineer], [Eval lead], [teammate] |
| --- | --- |
| Product | [Director of Product] |
| Design | [product designer] |

---

## 1. Build, rollout, and arm assignment

Provider Drafts pre-generates one AI message draft per eligible provider action, and exposure to these drafts are randomized at the patient level.

| **Build** | **What it does** | **Rollout** | **Arm assignment** |
| --- | --- | --- | --- |
| **Provider Drafts** | Anywhere a Hers WL provider composes a patient message in the EMR, the Clinical Decision Support (CDS) service pre-generates one draft per eligible action (Prescribe, Refer, Increase Dose, Decrease Dose, Repeat Step, Send Message) at task creation. The provider reviews, edits, and explicitly sends; nothing auto-sends. | UAT, then a patient-level A/B: 1% of Hers WL patients in treatment and 1% in control, ramping to a 50/50 split until CIS and AHT reach statistical significance, then enrollment ramps to a full release with a permanent 5% control. | Patient. Sticky: an arm never changes across ramp steps. Recorded per patient (arm, assignment date, ramp step at assignment, assignment version) and inherited per task. |

**Why patient level, not provider level.** Retention (metric O2) needs patient-level assignment so drafts follow the patient across every task, and providers work both arms regardless of unit. Patient-level assignment also supports a within-provider AHT comparison, which reduces provider-to-provider variance.

---

## 2. Exposure and population

**Pre-Rx member → post-Rx WL subscriber.** Provider Drafts applies to both states; retention (metric O2) is measured on subscribers only. Randomization happens at the patient level at experiment entry, before Rx status is known. Every task, stored draft, and sent message for that patient then inherits the assigned arm, regardless of which state the patient is in when the task is created.

| **Field** | **Definition** |
| --- | --- |
| **Eligible** | Hers WL clinician tasks created after the patient's randomization, all task categories where the six actions above are available. Hims WL and other categories expand the task population later. |
| **Exclusions** | [Per Legal](https://hims.streamline.ai/requests/6a93b84705708c9421b773e2), patients whose state of residence or shipping state is Maryland must be excluded during rollout. A patient whose state changes to Maryland after assignment keeps the arm and is flagged. |
| **Exposure / Control** | Set at the patient level, randomized. Assignment is sticky; each ramp step moves only unenrolled patients into treatment. Every task, stored draft, and sent message inherits the patient's arm. |
| **Evals scope** | Judges score the message the provider sent and the stored draft for the action the provider took only, never all six stored drafts |
| **Nesting** | None. Complete the Chart's member arm and the EMR 2.0 Summary Card's provider arm are available as slices of data, but the experiments are intended to run and be evaluated independently. |

---

## O. Business outcomes

Where all cost savings and retention are reported. Each dollar figure is split three ways, never conflated: booked, committed, and pipeline; the PRD requires the split (CDS-04).

| **#** | **Metric** | **Definition (numerator / denominator)** | **Grain** | **Window** | **Baseline** | **Target** | **Good** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| O1 | **Cost savings, AHT ($)** | - (Control-arm minus treatment-arm modeled pay cost per completed task, A6) × treatment-arm completed tasks - Pay calculation: `[TBD: pay calculation logic from Care Ops ([Workforce Management lead]) when the task-based model is final]` - Pay model context: Provider Pay Refactor Project Plan, Care Quality WBR (Aug 31) | Portfolio | Monthly, plus cumulative, starting at the task-based pay go-live. Before go-live, A2 is the only cost read. | $0 (no AI-drafted-message savings before launch, by definition) | Pipeline: $1,218,434 FY2027 Hers WL (ADS Sizing SOT, Scenario 4, a sizing estimate) | ↑ |
| O2 | **Retention** | - Subscribers who don’t cancel within the window ÷ subscribers, by assigned patient arm, at D0, D7, D14, D30, D90, in two cohorts read side by side:     - Subscribed at assignment (primary): D0 is the assignment date     - Subscribed after assignment (secondary): D0 is subscription start; read with A16 - A cohort enters a DN read only once N days have elapsed. - Reported with the post-assignment subscribe share by arm as a balance check. | Member (subscriber) | N days post D0 (D0, D7, D14, D30, D90) | `[TBD: [teammate]]` | `[TBD: Danny Pedrini]` | ↑ |

---

## A. Provider Drafts

### Hero metrics

How we determine the success of Provider Drafts, assuming no guardrails broken.

| **#** | **Metric** | **Definition (numerator / denominator)** | **Grain** | **Window** | **Baseline** | **Target** | **Good** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | **Clinical Interaction Score (CIS)** | - Uniform-weighted mean of per-judge pass rates across the production judges that apply to both arms - Per-judge pass rate is Pass ÷ (Pass + Fail), with N/A excluded from the denominator.  - Scored on the message the provider sent, all eligible Hers WL tasks, by patient arm.  - A judge added later starts CIS v2 | Message | Batch, cadence `[TBD: [Eval lead]]`, at least one batch per ramp step | `[TBD: [Eval lead] with [teammate]]` | `[TBD: Danny Pedrini]`, set as a treatment-minus-control lift, not an absolute level | ↑ |
| A2 | **Messaging AHT** | - Average total task handle time (minutes) per eligible Hers WL task, by patient arm (intent-to-treat), task class (decision against non-decision), and action type - Report the p10, p50, p90, and the mean | Task | Monthly, plus MoM change | N/A | 30% (reconciles to the sizing model's AHT-reduction coefficient) | ↓ |

**CIS lags the deterministic metrics by its batch interval.** CIS runs as a manual offline batch, not a production pipeline, so its readout arrives after the warehouse-native rows. The Window column carries the batch cadence once [Eval lead] sets it. 

**CIS alone is not sufficient.** A CIS gain fails if Metric A3's groundedness or rx\_guideline\_adherence rows, which [Clinical Quality co-lead] reviews each batch, show a significant negative arm delta on unedited sends. Metric A3 is both a guardrail and a reconciling metric, because the judges live inside CIS. 

**How CIS gets computed at launch:**

- Launch CIS is a manual batch: a sample of sent messages by arm (metric A5), judges run offline, and the output processed into CIS. **(Evals team)**
- Read CIS as a treatment-minus-control lift in the Dashboard **(ADS in partnership with Evals team)**
- Eventually build a recurring pipeline after launch to support ongoing measurement **(ADS)**

### Reconciling metrics

Making visible the building blocks used to calculate or contextualize the hero metrics.

| **#** | **Metric** | **Definition (numerator / denominator)** | **Grain** | **Window** | **Good** |
| --- | --- | --- | --- | --- | --- |
| A3 | **Pass rate and N/A rate by judge** | For each production judge: Pass ÷ (Pass + Fail), and N/A ÷ messages scored by that judge, reported side by side, on sent messages from eligible Hers WL tasks, by patient arm | Message | Batch, same cadence as Metric A1 | ↑ pass rate, Hold N/A rate |
| A4 | **Draft-level CIS (treatment arm)** | - Metric A1's formula plus semantic\_coverage, applied to the stored draft for the action the provider took and that reached the composer, paired to its sent message (task × action × draft) - Reported as the composite and per judge; treatment arm only | Message (draft) | Batch, same cadence as Metric A1 | ↑ |
| A5 | **CIS sample coverage** | - Sent messages scored by the judge batch ÷ eligible sent messages, by patient arm - The batch is a stratified random sample by arm and action type with a fixed per-arm count, and each batch's sample is logged so it can be re-drawn exactly | Message | Batch, same cadence as Metric A1, trended | ↑ |
| A6 | **Modeled pay cost per completed task, by arm** | - Modeled pay per completed eligible task, by patient arm, priced per Care Ops logic: `[TBD: pay calculation logic from Care Ops ([Workforce Management lead]) when the task-based model is final]` - Reconciles to the ADS Sizing SOT Scenario 4 tab | Hour | Monthly, plus cumulative, starting at the task-based pay go-live | ↓ |
| A7 | **Sent-message input-type distribution** | - Sent messages by primary input (AI draft sent unedited, AI draft edited, snippet, manual) ÷ sent messages from eligible Hers WL tasks, by surface, action type, and patient arm.  - Input type is the last content source before send:      - An AI load or reload is unedited if the text matches the draft after whitespace normalization and edited otherwise     - A snippet selected without re-retrieving the draft is snippet     - A cleared composer is manual - Draft discard rate: the manual share + the snippet share (shown alongside the distribution) | Message | Monthly | Hold |

**A7 and A8 will not match.** A7 is a categorical record and A8 a continuous similarity score over the same draft-to-sent comparison, so the two acceptance reads move differently and neither is wrong.

### Driver metrics

The levers we investigate to understand over- or under-performance in the hero metrics.

| **#** | **Metric** | **Definition (numerator / denominator)** | **Grain** | **Window** | **Good** |
| --- | --- | --- | --- | --- | --- |
| A8 | **Draft-to-sent edit magnitude** | - Text similarity between the stored draft and the sent message on sends typed AI unedited or AI edited: the Care Coach acceptance construction (Jaccard index above 0.95 plus a normalized edit-distance threshold and the continuous similarity score).  - On Prescribe, scored on the AI opening only, so the opening and the deterministic block must be stored separately. Treatment arm, by action type | Message | Weekly | ↑ |
| A9 | **BAU trigger rate by reason** | - Treatment-arm eligible actions reaching BAU ÷ treatment-arm eligible actions with a draft resolution, by reason from one enum (not generated, generation failed, invalidated, placeholder unresolved, value mismatch, superseded offering, drafting off, excluded Maryland) and action type.  - Metric A9's complement is the drafts-shown rate: actions whose first draft resolution rendered a draft in the composer | Action (task × action type) | Weekly | ↓ |
| A10 | **Draft generation latency** | Elapsed time from task creation to all eligible drafts stored, by action type, treatment arm | Task | p50 and p90, weekly | ↓ |
| A11 | **Time from composer open to message sent** | - Elapsed minutes from the first composer or drawer open for the action to message send, by action type, surface, and patient arm - The open event exists in both arms. Reveal-to-send is the treatment-only sub-cut | Message | p10, p50, and p90, monthly | ↓ |
| A12 | **"Why this draft" open rate** | Revealed drafts with at least one Why this draft expand ÷ AI drafts revealed, by action type | Revealed draft | Weekly | Hold |

**A9 carries exposure as well as its causes.** Its complement is the drafts-shown rate, which corrects the intent-to-treat read for actual exposure; the reason breakdown explains why exposure fell short. Build the denominator once from the draft-resolution record; A10's never-stored tail (tasks opened before drafts existed) appears as A9's not-generated reason.

**A12's direction is deliberately Hold.** A rising "Why this draft" open rate can mean providers trust drafts less and verify them more, or that a useful feature is getting used. The two readings pull in opposite directions. Good is Hold until a pattern emerges alongside metric A15.

### Guardrail metrics

How we ensure Provider Drafts does not degrade quality of care or patient experience.

| **#** | **Metric** | **Definition (numerator / denominator)** | **Grain** | **Window** | **Good** |
| --- | --- | --- | --- | --- | --- |
| A13 | **Clinical Quality Score (CQS)** | - References the existing CQS scoring (earned ÷ possible points from provider book audits and incident reports - Looker dashboard 5696), computed at the audited-case grain for Hers WL tasks and tagged with the patient's arm - The provider-level CQS stays as the lagging confirmation. Do not redefine the scoring. | Audited case | Per audit book, monthly reads (CQA team) | Hold or ↑ *(alarm: statistically significant regression against control once the minimum audited-case count is met)* |
| A14 | **Patient reaction distribution on provider messages** | - Thumbs-down, thumbs-up, and no reaction, each ÷ threads whose last provider message came from an eligible task, by patient arm - Thumbs-down rate + thumbs-up rate = react rate, shown in line | Thread | Weekly | ↓ thumbs-down *(alarm: statistically significant regression against control once the minimum thread count is met)* |
| A15 | **Provider thumbs-down rate** | Submitted, reasoned thumbs-down records ÷ AI drafts revealed, treatment arm, by action type and stated reason | Revealed draft | Weekly | ↓ *(alarm: threshold set by Danny Pedrini with **Care Coach Drafts thumbs-down rate** as context)* |
| A16 | **Submit-to-Subscribe** | References Complete the Chart's Metric A2 (Growth's measure): patients who pay for the prescription ÷ patients reaching treatment submit, pre-Rx-randomized patients only, by patient arm; do not redefine | Patient | However Growth measures it today, by arm | Hold or ↑ *(alarm: statistically significant regression against control once the minimum count is met)* |

**Metric A14's three readings are not inverses.** Most sent messages get no reaction at all, so thumbs-up cannot stand in for thumbs-down. Thumbs-down alone carries the alarm; react rate is context, not a target.

**Metric A16 reads conversion where the Prescribe draft lands.** The Prescribe message is the last message a patient reads before paying for the Rx, so a worse draft could depress conversion. Read it intent-to-treat on everyone randomized pre-Rx; "received a drafted Prescribe message" is a drill-down, not the population. It adds no experiment scope because patient-level randomization already covers it.

---

## 3. Slices

| **Slice** | **Why it matters** |
| --- | --- |
| **Time period** | How users define their own baseline. Replaces static baselines entirely |
| **Patient arm** | The comparison every hero, reconciling, and driver metric rests on |
| **Message type** | The six eligible actions (Prescribe, Refer, Increase Dose, Decrease Dose, Repeat Step, Send Message) behave differently; blending them hides which action drives a change |
| **Task category** | Distinguishes Hers WL task categories from the message-type slice above (see Task Type: EMR Displayed Name and Description) |
| **Draft outcome** | Sent unedited, edited, discarded, or BAU; separates the population that saw and used a draft from the population that fell back to BAU (Metric A9). Treatment-arm descriptive views only, since control has no draft outcome. |
| **Patient tenure** | New against existing customers; the AIAL-25 segment |
| **Ramp step** | Impact reads differently at 1% than at later steps |
| **CTC member arm** | Complete the Chart is live at the same time; slice is available for further analyses on shared metrics like S2S |
| **Summary Card provider arm** | The EMR 2.0 Summary Card is live at the same time; slice is available for further analyses on shared metrics like AHT |

**Not sliced:** Brand, because launch is Hers only. Treatment type, because launch is WL only. State, because Maryland is excluded (§2 Exclusions). Individual provider, because Provider Drafts reports aggregate only.

---

## 4. Next steps for ADS

ADS splits the work into AI Analytics (the judge-batch metrics) and Care Analytics (everything else); the split below is illustrative and ADS finalizes it. ADS defines the metrics with proper data sources, flags instrumentation gaps to Eng, and works with Product to prioritize metrics that will be available at launch (and the prioritization of those that will come later). 

| **Workstream** | **Metrics** | **Owner** |
| --- | --- | --- |
| AI Analytics | A1, A3, A4, A5 | [teammate], [teammate] |
| Care Analytics | O1, O2, A2, A6 through A16 | [Care Analytics lead, Analytics and Data Science], [teammate] |

---

## 5. Open questions

| **Question** | **Owner** | **Blocks** |
| --- | --- | --- |
| CIS batch cadence, coverage, compute budget, and batch operator | [Eval lead] | A1, A3, A4, A5 |
| CIS baseline batch on historical provider messages | [Eval lead] with [teammate] | A1 |
| Pay calculation logic under the task-based model: matrices, cutover date, and how provider-day pay splits across arms | [Workforce Management lead] (Care Ops) with [teammate] | O1, A6 |

---

## 6. Change log

| **Date** | **Change** | **Requester** |
| --- | --- | --- |
| 2026-09-28 | Initial version | Danny Pedrini |
