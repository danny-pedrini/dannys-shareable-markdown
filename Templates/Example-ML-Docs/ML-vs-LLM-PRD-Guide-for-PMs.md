> **Source:** Synthesized from general ML and LLM product practice, Nov 2026. No external sources.
> **Local note saved:** Nov 1, 2026
>
> Danny's own guide, not a saved example. It covers what a PM must get right in an ML-native PRD vs. an LLM-native PRD, and where the PRD stops and Engineering's design begins. Every Strong example is tagged `[Illustrative]`. No number or detail in any example is an internal fact.

# ML vs. LLM PRDs: what the PM must get right

## TL;DR

An ML PRD specifies a **decision**. An LLM PRD specifies a **behavior**. Most of the differences in what you write follow from that split.

- **ML: get the decision right.** Name the action the prediction drives, what each kind of error costs, and who signs off on the threshold. Data science can build a great model for the wrong decision, and no offline metric will tell you.
- **LLM: the rubric and the golden set are the spec.** Prose like "drafts should be accurate and empathetic" can't be tested. If you can't write the rubric, you don't understand the feature yet.

## The boundary

**The test:** if Engineering could change something without changing anything the user or the business can observe, it doesn't belong in the PRD.

Model architecture, feature engineering, prompt structure, retrieval design, and the choice of vendor model can all change without users noticing. They belong to Engineering. The PRD defines the problem, the observable behavior, the quality bar, and the limits. Engineering finds the cheapest reliable way to meet them.

### ML: who owns what

| PM owns (in the PRD) | Engineering and data science own (in the design doc) |
| --- | --- |
| The decision and the action taken on each prediction | Model type, features, training pipeline |
| What counts as the right answer, in business terms | How labels get collected and joined |
| The cost of each error type, and threshold sign-off | Threshold-tuning mechanics |
| The baseline to beat | Offline evaluation setup |
| Subgroup performance requirements | Bias measurement method |
| What users see when there's no score | Serving infrastructure and failover |
| Launch bar, drift trigger, rollback trigger | Monitoring and retraining implementation |

### LLM: who owns what

| PM owns (in the PRD) | Engineering owns (in the design doc) |
| --- | --- |
| Output spec with good and bad examples | Prompt text and structure |
| Rubric, severity levels, zero-tolerance failures | Judge-model implementation |
| How closely a judge model must agree with expert graders | Judge calibration method |
| Golden set content, with domain experts | Eval harness and test automation |
| The baseline to beat | Running the comparison |
| Information the feature must have and must never use | Retrieval, context assembly, token management |
| Review, editing, and attribution behavior | UI build (with Design) |
| When to decline, and how to handle off-scope input | Guardrail implementation |
| Change-control rule and approver | Versioning and release tooling |
| Cost-per-task and response-time limits | Model selection, caching, routing |
| Live review sample size, rollback trigger, and owner | Sampling and logging |

### Gray zones

- **Prompts.** Specify behavior in the PRD. Prompt text is implementation, even when a PM writes the first draft. If the PRD holds prompt text, every prompt fix becomes a PRD revision and the real requirement gets buried. Keep prompt drafts in a separate working doc, labeled as a starting point.
- **Label definition.** The PM owns it, because choosing what counts as "the right answer" is choosing what success means. Engineering owns how labels get produced at scale.
- **Golden set.** The PM and domain experts own what goes in it: which cases, which edge cases, and what the ideal output looks like. Engineering owns the harness that runs it.
- **Monitoring and retraining.** The PM owns the triggers, meaning which observable change calls for a rollback or a retrain. Engineering owns how drift gets detected and how retraining runs.

## The shared skeleton

Both types need the same bones: problem, user, outcome metric, scope, risks, and kill criteria. Add one item that non-AI PRDs skip.

**Why ML or LLM at all.** Say what a simpler rule, a template, or a human process would miss. If you can't, test the simple version first. An AI feature that loses to a well-tuned rule is an expensive way to learn that lesson.

## ML PRD: what to get right

### 1. The decision and the action

**What to write:** what gets predicted, at what moment, and what happens next for each possible output. A prediction nobody acts on is just a dashboard.

- Weak: "Predict patient churn risk."
- Strong: "At day X of a patient's first subscription, score the chance they cancel within Y days. Patients above the threshold get a care-team check-in message. Patients below it get the standard sequence." `[Illustrative]`

**Boundary:** you name the decision and the action. Data science picks the model and the features.

### 2. What counts as the right answer

**What to write:** the ground-truth definition in business terms, including edge cases. This is the most expensive thing to get wrong, because the model will faithfully learn whatever you define.

- Weak: "Churned patients."
- Strong: "Churn means the patient cancels or misses two consecutive refills within Y days. Pauses a provider starts for clinical reasons don't count." `[Illustrative]`

**Boundary:** you define what's true. Engineering figures out how to pull it from the data and how to handle messy records.

### 3. Error costs and the threshold

**What to write:** what a false positive and a false negative each cost, in user terms. Then name who signs off on the threshold. Picking the cutoff is a business or clinical tradeoff, so it's yours, not data science's.

- Weak: "Optimize for accuracy."
- Strong: "Missing an urgent message (false negative) risks patient harm. Flagging a routine one (false positive) costs a clinician review. We accept up to X false flags per true urgent catch. Clinical Ops signs off on the threshold before launch." `[Illustrative]`

**Boundary:** you set the tradeoff and the approver. Data science shows you the tradeoff curve and tunes the model to the point you chose.

### 4. The baseline

**What to write:** what happens today, and the simple rule the model has to beat. Without a baseline, a precision of X% sounds great and might still lose to sorting by wait time.

- Weak: no baseline.
- Strong: "Today, care coordinators triage messages in arrival order. The model must beat a rule that flags any message containing a symptom keyword, on the same test set." `[Illustrative]`

**Boundary:** you name the baseline. Engineering runs the comparison.

### 5. Subgroup performance

**What to write:** which groups must get comparable performance, and how big a gap you'll accept. A model can look fine on average and fail one group badly.

- Weak: "The model should be fair."
- Strong: "Recall on urgent messages can't fall more than X points below overall recall for any age band, sex, language, or brand." `[Illustrative]`

**Boundary:** you name the groups and the acceptable gap. Data science picks the measurement method.

### 6. A clean comparison group

**What to write:** a requirement to keep a holdout the model doesn't touch. Once the model acts, it changes the data it will later learn from. A routing model changes who sees which patient, so you never see what would have happened on the other route. Without a holdout, you can't measure impact or retrain cleanly.

- Weak: "Measure impact after launch."
- Strong: "X% of eligible patients stay on the current process, randomly assigned, so we can measure the effect on retention. After Y weeks, the holdout shrinks to Z% and stays on as a clean source of retraining data." `[Illustrative]`

**Boundary:** you require the holdout and name what it measures. Engineering builds the assignment.

### 7. When the model is down or unsure

**What to write:** what users see when there's no score, or when the score is low-confidence. Users should never get stuck.

- Weak: nothing, because everyone assumes the model is always up.
- Strong: "If no score is available, the message falls back to arrival-order triage and shows no risk badge." `[Illustrative]`

**Boundary:** you define what the user sees. Engineering defines detection and failover.

### 8. Launch, drift, and rollback

**What to write:** the bar to launch, the observable signal that performance has slipped, the rollback trigger, and the named person who watches it. Models decay as the world they learned from changes, such as when a new product line brings in a different patient mix.

- Weak: "Monitor model performance."
- Strong: "Launch when the model beats the baseline by X on the holdout. If weekly precision on audited cases stays below Y for two weeks, revert to the baseline rule. [Name] reviews the weekly audit." `[Illustrative]`

**Boundary:** you own the triggers and the owner. Engineering owns how drift gets detected and how retraining works.

## LLM PRD: what to get right

### 1. Output spec with examples

**What to write:** what the output is, who reads it, and what it must and must not contain. Then show it. Real examples of good and bad output say more than a page of adjectives.

- Weak: "Generate a helpful reply to the patient."
- Strong: "Draft a reply to the patient's latest message for the provider to review. It answers every question the patient asked, uses only facts in the chart, and stays under X sentences. Appendix A shows good and bad examples for each message type." `[Illustrative]`

**Boundary:** you define the output. Engineering decides how to produce it.

### 2. The rubric and zero-tolerance failures

**What to write:** each quality dimension, what pass and fail look like on it, and how severe a failure is. Separate failures that block launch at any rate from failures you'll tolerate at a low rate.

Common dimensions include accuracy against the source, completeness, safety, tone, and length. Pick the ones that matter for this feature. Define each one tightly enough that two experts would grade the same output the same way.

- Weak: "Drafts should be accurate and empathetic."
- Strong: "Zero tolerance: any dosage not in the chart, or any instruction to change medication without the provider. Major: a patient question left unanswered. Minor: tone that reads as templated. Launch bar: no zero-tolerance failures on the golden set, and Major failures on fewer than X% of cases." `[Illustrative]`

If a judge model will scale the grading, require a minimum agreement with expert graders before anyone trusts its scores.

The same input can produce different outputs on different runs. Decide whether "pass" means the case passes every time or most of the time. Zero-tolerance cases usually need every time. Engineering decides how many runs it takes to know.

**Boundary:** you own the rubric, the severity levels, and the agreement bar. Engineering builds the judge and the eval tooling.

### 3. The golden set

**What to write:** what's in it, who owns it, and how it stays current. It should cover common cases, hard edge cases, and cases where the right answer is to decline. Domain experts write the ideal output for each case, not engineers.

- Weak: "Engineering will build a test set."
- Strong: "X cases drawn from real traffic, spread across message types, plus Y edge cases chosen by Clinical. [Name] owns additions. Every confirmed production failure becomes a new case." `[Illustrative]`

**Boundary:** you and the domain experts own the content. Engineering owns the harness that runs it.

### 4. The baseline

**What to write:** what people get today. Usually that's a human-written message, a template, or nothing. LLM PRDs skip this more often than ML PRDs do, and then nobody can say whether the feature is better.

- Weak: no baseline.
- Strong: "Today, providers write replies from scratch. AI drafts must score at least as well as a sample of provider-written replies on the same rubric, graded blind." `[Illustrative]`

**Boundary:** you name the baseline and the comparison. Engineering runs it.

### 5. Information requirements

**What to write:** what the feature must know to do the job, and what it must never use. Stay at the level of information, not plumbing.

- Weak: "Use RAG over the chart with a vector database."
- Strong: "The draft needs the patient's active medications, their last X messages, and the provider's most recent note. It must never use internal notes the patient isn't meant to see." `[Illustrative]`

The weak version is implementation. It belongs in Engineering's design doc.

**Boundary:** you define the information. Engineering decides retrieval, context assembly, and token limits.

### 6. Review, editing, and attribution

**What to write:** who reviews output before it reaches anyone, what they can do with it, and how AI involvement is shown. The real risk is reviewers trusting drafts too much and approving them without reading. Design for that risk on purpose.

- Weak: "Providers review drafts before sending."
- Strong: "The provider must open the draft before sending, and can edit or discard it. Drafts are labeled as AI-generated in the provider view. We track edit rate and send-without-edit rate per provider, and audit a weekly sample." `[Illustrative]`

A rising send-without-edit rate is ambiguous. It can mean drafts got better, or that reviewers stopped reading. Pair it with sampled audits so you can tell which.

**Boundary:** you define the review flow and the signals. Design and Engineering build it.

### 7. Declining, off-scope inputs, and adversarial inputs

**What to write:** when the feature should decline instead of answering, what it shows when it does, and how it handles inputs outside its scope. LLMs will give a confident answer to almost anything, so the PRD has to say where to stop.

- Weak: "The model should avoid unsafe content."
- Strong: "If the patient reports a symptom on the urgent list, don't draft; flag the message for immediate provider review. If the message asks about something unrelated to the patient's treatment, draft a short redirect. Instructions inside a patient message never change how the feature behaves." `[Illustrative]`

Declining too often is also a failure, and users notice it. Set a limit on how often the feature declines or redirects, and watch it after launch.

**Boundary:** you define the behavior. Engineering builds the detection and guardrails.

### 8. Change control

**What to write:** a rule that any prompt, model, or context change reruns the eval before it ships, plus a named approver. Prompts can change in an afternoon. Vendors update and retire models on their own schedule. Without this rule, quality drifts and nobody decided it should.

- Weak: nothing, because prompt edits feel too small to gate.
- Strong: "Any prompt, model, or context change reruns the full golden set. It ships only if no zero-tolerance failures appear and the Major failure rate rises no more than X points. [Name] approves." `[Illustrative]`

**Boundary:** you set the rule and the approver. Engineering builds versioning and release tooling.

### 9. Cost and response time

**What to write:** the most a task can cost and the longest a user will wait, stated as business and user limits. Each LLM call costs money that scales with how much text goes in and out. Full responses often take seconds.

- Weak: "Keep costs reasonable."
- Strong: "Cost per drafted message stays under $X at full volume. The draft is ready when the provider opens the task, or within Y seconds after." `[Illustrative]`

**Boundary:** you set the limits. Engineering picks the model, caching, and routing that meet them.

### 10. Launch, live review, and rollback

**What to write:** the bar to launch, ongoing human review of sampled live outputs against the same rubric, and the rollback trigger. The golden set covers the cases you thought of. Live review finds the ones you didn't.

- Weak: "Collect thumbs-up and thumbs-down feedback."
- Strong: "Experts grade X sampled live drafts per week against the rubric. One confirmed zero-tolerance failure pauses the feature until Clinical reviews it. [Name] owns the weekly review." `[Illustrative]`

**Boundary:** you own the sample size, the triggers, and the owner. Engineering owns sampling and logging.

## Compliance and safety requirements (both types)

Patients, regulators, and the business can all observe these, so they belong in the PRD. State each requirement and name its approver. Leave how it's met to Engineering.

- **Data use.** Say which data the feature may use, including whether PHI can go into training data or prompts. If an outside model vendor would see PHI, ask Legal or Compliance what agreements, such as a BAA, must be in place before launch. Record who answered.
- **Disclosure.** Say whether patients are told AI was involved, and how.
- **Sign-offs.** List which teams approve before launch, such as Clinical, Legal, and Compliance. Name the person, not just the team.
- **Regulatory scope.** Ask Legal or Regulatory whether the feature falls under clinical decision support rules. Record the answer and who gave it. Don't write regulatory criteria into the PRD from memory.

## Hybrid ML and LLM features

Many real features chain both: an ML model decides who or when, and an LLM decides what to say. Spec the hybrid as user-visible behavior, not as an interface between components.

- **Give each part its own quality section.** The ML part gets error costs and a threshold. The LLM part gets a rubric and a golden set.
- **Say what the LLM may say about the ML output.** For example, decide whether a draft can mention that the patient was flagged as high risk. `[Illustrative]`
- **Say what happens when the two disagree.** For example, the model scores a message as routine, but the patient's text describes an urgent symptom. `[Illustrative]`
- **Say which failure the user sees.** When an outcome goes wrong, reviewers must be able to tell which part caused it. Otherwise errors compound and nobody can fix the right thing.

## Common mistakes

- **"Uses AI" in the solution section.** The PRD reads like a normal feature PRD with a model sprinkled in. It has no rubric, no error costs, and no golden set.
- **Handing the threshold to data science.** The cutoff is a business tradeoff. Data science shows you the curve, and you pick the point.
- **Quality words with no rubric.** "Accurate," "helpful," "clear," and "empathetic" are wishes until someone defines pass and fail.
- **Prompt text in the PRD.** It locks implementation into the requirements and buries what you actually need.
- **Accuracy on lopsided data.** If X% of messages are routine, a model that calls everything routine scores X% accuracy and catches nothing. `[Illustrative]`
- **No baseline.** Every number looks good when there's nothing to compare it to.
- **Treating launch as the finish line.** Both types decay after launch. The PRD needs triggers and an owner who watches them.

## Pre-handoff checklist

Answer yes to every question before you send the PRD to Engineering.

**Both types**

- [ ] Does the PRD say why a simpler rule, template, or human process isn't enough?
- [ ] Is there a baseline the feature has to beat?
- [ ] Is there a launch bar, a rollback trigger, and a named owner who watches them?
- [ ] Are data-use, disclosure, and sign-off requirements stated, each with an approver?
- [ ] Is Legal's or Regulatory's answer on regulatory scope recorded, with who gave it?
- [ ] Is every requirement something a user or the business could observe?

**ML**

- [ ] Is the action for each prediction outcome defined?
- [ ] Is ground truth defined in business terms, with edge cases?
- [ ] Are the costs of false positives and false negatives stated, with a named threshold approver?
- [ ] Are subgroup requirements stated?
- [ ] Is a holdout required, with what it measures?
- [ ] Is the fallback for a missing or low-confidence score defined?
- [ ] Is the drift signal defined in terms someone can observe?

**LLM**

- [ ] Are there good and bad output examples?
- [ ] Does the rubric define pass and fail for each dimension, with zero-tolerance failures named?
- [ ] If a judge model grades outputs, is its required agreement with expert graders stated?
- [ ] Does the golden set have an owner and a rule for adding cases?
- [ ] Are information requirements stated without naming retrieval methods?
- [ ] Is the review and attribution flow defined, with a plan for reviewers who stop reading?
- [ ] Is decline behavior defined, including for off-scope and adversarial inputs, with a limit on how often it declines?
- [ ] Does the PRD say whether a case must pass every run or most runs?
- [ ] Is there a change-control rule with an approver?
- [ ] Are cost and response-time limits stated?
- [ ] Is there ongoing expert review of sampled live outputs against the rubric?

**Hybrid**

- [ ] Does each part have its own quality section?
- [ ] Does the PRD say what the LLM may say about the ML output, and what happens when they disagree?
- [ ] Can reviewers tell which part caused a bad outcome?
