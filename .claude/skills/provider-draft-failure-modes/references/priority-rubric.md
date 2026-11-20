# Priority rubric

One rubric, approved once and reused every round.

Two things set a failure mode's level. **Severity** comes from its **worst credible instance if a provider sends the draft unedited**, and puts it in a severity class (section 1). **Frequency** comes from how many counted instances back it, and puts it in a band (section 2). The scale in section 0 turns class and band into a level and a filing call.

**This is a recommendation, not the decision.** The product owner sets final priority at Gate 3, ticket by ticket. Round 3 example: Danny reviewed all 46 cards and kept every ticket below the rubric's scored level where he judged the harm didn't warrant it; no P0 was filed even though the rubric scored three failure modes at P0. Carry the rubric's level into the ticket plan and the review card as "Recommended," never as the filed priority.

> **Source:** Round 1.5 rubric, approved by Danny 2026-10-06 (hypothesis: task prompt 2026-10-06; epic evidence: `priority-evidence.md`, 35 MLENG-4732 children read in full). Clinical answers: "Rx guideline questions" sheet, Questions tab ((internal link)), answered 2026-10-01 by [Care Delivery Experience lead] (Q1 to Q18) and Danny Pedrini (Q19). Round 3 replacements: `plan.md` section 10, approved by Danny 2026-10-21, merged in below with no separate layer. Metric order: quality of care, then patient experience with an eye on retention, then cost (root `AGENTS.md`).
>
> **Source:** Severity-and-frequency scale, filing floor and counting rules: Danny, chat, 2026-11-05 (`Project-Galen/Phase-3/Launch/Failure-Mode-Rules-Skill-Fix-Handoff.md` sections 1, 2 and 5).
> **Source:** Level changes (severe-safety one-off to P1; minor-safety recurring to P2; minor-safety common stays P1): Danny, chat, 2026-11-10 (skill v2.2).
> **Source:** Eval-only rule (5 or more distinct eval-judge drafts are common), the P3 rule (existing tickets below the floor only, never a new ticket) and the evidence ledger replacing the watch list: Danny, chat, 2026-11-10 (skill v2.3).

## 0. The scale, the filing floor and the safety or efficiency label (rewritten 2026-11-05, skill v2.0; levels changed 2026-11-10, skill v2.2)

| Severity class of the worst credible instance | One-off: 1 counted instance | Recurring: 2+ counted instances | Common: 5+ counted drafts from 2+ providers |
| --- | --- | --- | --- |
| Severe safety | P1, file it | P0 | P0 |
| Minor safety | Hold | P2 | P1 |
| Efficiency or quality | Hold | P2 | P1 |

Section 1 defines the classes. Section 2 defines counted drafts, counted instances and providers.

**The filing floor.** One instance of an issue is not grounds for a new ticket unless it's severe safety. Below the floor, the call is hold.

- **Scope.** The floor applies to Bugs, Regressions included. It doesn't apply to decision items (section 3). It applies after the consolidation rule: failure modes that share one fix location and one expected behavior pool their counted drafts, instances and providers before the call, counting each draft and provider once.
- **Hold.** No new ticket. The failure mode is recorded as a `held` row in the evidence ledger (`evidence-ledger.md`), which the next round reads, so a second occurrence files. An item with the price-hold flag goes to the product owner at Gate 2 instead of filing. An evidence comment on an open ticket that covers it stays allowed where it helps.
- **No counted instance.** Zero counted instances is band `none`. When the worst credible instance is severe safety, the failure mode shows at Gate 2 for the product owner's call. It is filed only on that go. Below severe safety, it holds and adds nothing to a later round's count.

**Every ticket carries a `safety` or an `efficiency` label**, in addition to the round's labels in `round.json`. `safety` goes on severe-safety and minor-safety tickets. `efficiency` goes on efficiency-or-quality tickets, including those at P1 because they're common. Pre-fill the label in the ticket plan and show the list at Gate 3 so Danny can flip any.

**Fixing length.** A length or verbosity ticket never asks for more concise generated text. Its fix is to remove repeated content and over-applied clinical protocols first and cut wording second.

**Calibration evidence.**

- **Severity (Provider Pilot Round 1, Gate 3, 2026-11-03).** Of 36 cards, Danny kept 1 at P0 (a paraphrased suicide-risk screener) and judged three "not a bug". He lowered five of the rubric's P0s to P1: an interim-dosing step called "not recommended", skipped doses ignored, an unaddressed drug interaction, a mismatched self-reported dose and two target doses in one sentence. Both blind scorers had scored more severely than the plan. On this scale, those five are minor safety.
- **The floor (Provider Pilot Round 1 edits pass, Gate 2, 2026-11-05).** "I don't want to file tickets for every issue that happened one time. That feels whack-a-mole-like and probably isn't very impactful." Danny skipped twelve one-off issue types, including a one-off Regression. He allowed evidence comments on existing tickets "even for one-off issues, where helpful."

## 1. Severity classes and levels

Classify each failure mode on its worst credible instance (section 2, step 1).

| Class | Definition | Typical failure modes |
| --- | --- | --- |
| **Severe safety** (drives P0 and P1) | The patient could get a clinically wrong or unsafe instruction, or miss an instruction needed to take the medication safely. | Wrong dose or titration step. Unsafe interim or taper instruction. A dose the patient cannot carry out (mg only for a compounded syringe). A missing dose-transition or stop instruction. A missed urgent-symptom escalation. Contradicting an allergy or contraindication. A false statement about the patient's own treatment (current drug, dose, last dose) that could change what the patient takes. |
| **Minor safety** | The draft could change what the patient does or believes about their care, short of the risk above. For a stated fact, one sign: the sentence states a fact about the patient's plan, timing, shipment, pharmacy or reason for a decision, and it reads plausibly. | An unverifiable fulfillment promise (ship dates, pharmacy outcomes) or benign invented history (section 3), when it passes the test above. A wrong reason given for a decision. A plausible false fact the provider could confirm only by checking the chart or another system. The dosing calibration cases in section 0. |
| **Efficiency or quality** | Costs provider handle time or patient experience without changing what the patient does or believes about their care. Clinical content alone doesn't make a defect safety: a defect with clinical content that fails the minor-safety test lands here. Writing defects visible on a read-through (run-ons, repeats, empty filler lines) always land here. | Ignoring the patient's actual question or answering a different one. A systemic tone or template pattern. A run-on sentence. A repeated sentence. An empty filler line. A placement slip. An unresolved greeting token. |

The typical lists are a starting point; the worst credible instance decides. A wrong dose that carries no real risk to the patient is minor safety (section 0 calibration).

**Where the pre-v2.0 P1 categories land.** The old scale put each of these at P1 on one instance. Here, the minor-safety test is the class definition above: the draft could change what the patient does or believes about their care.

| Old P1 category | Class now |
| --- | --- |
| Clinically inaccurate or incomplete content that is not immediately unsafe, such as missing side-effect education | Minor safety when it passes the minor-safety test; efficiency or quality otherwise |
| Legal-flagged language, such as banned refer language | Minor safety when it passes the minor-safety test; efficiency or quality when the only risk is legal |
| Unverifiable promises (ship dates, pharmacy outcomes) | Minor safety when it passes the minor-safety test; efficiency or quality otherwise |
| Invented patient history that does not change dosing | Minor safety when it passes the minor-safety test; efficiency or quality otherwise (section 3) |
| A plausible false fact a busy provider would likely miss | Minor safety when it passes the minor-safety test, whether or not a provider would catch it (section 2, step 5) |
| Ignores the patient's actual question | Efficiency or quality, so P2 until common |
| A systemic tone or template pattern | Efficiency or quality, so P1 when common |

| Level | When (section 0) |
| --- | --- |
| **P0 - Unbreak NOW** | Severe safety at 2+ counted instances (recurring or common). |
| **P1 - Feature Blocker** (blocks the ramp) | Severe safety at one counted instance; minor safety that is common; efficiency or quality that is common. |
| **P2 - Non-Blocker** | Minor safety at 2+ counted instances that is not common; efficiency or quality at 2+ counted instances that is not common. |
| **Needs Prioritization** | Not used for defects. Reserved for decision items whose answer cannot reveal a patient-safety defect. Typical: a product question with no safety tail. |

P3 ("P3 - Everything Else", Jira id 10004) applies only to an existing ticket below the filing floor, after the product owner approves the list. Never create a new ticket at P3: a new issue below the floor stays unticketed and is tracked in the evidence ledger until it recurs. P4 is not used.

**Precedent (Round 1.5 epic read, for calibration only, not a source to cite in a filed ticket):** MLENG-4760 and MLENG-4923 (missing dose-transition instruction), MLENG-5199 (mg not units), MLENG-5226 (no stop instruction for a GLP-1 still being taken), MLENG-5003 (gap restart dose), MLENG-5097 (allergy, filed P0) anchor the P0 row. MLENG-4762 (unanswered request), MLENG-4757 (wrong name, legal floor), MLENG-4772 (pharmacy/CS workflows), MLENG-4773 (tone pattern) anchor P1. MLENG-4756 (`{{provider_greeting}}`), MLENG-4984 (confusing verbs) anchor P2. On this newer scale, the unanswered-request and tone-pattern anchors are efficiency or quality, and the legal and pharmacy anchors take the minor-safety test (placement table above).

## 2. Counting and scoring procedure

### Counting

**Counted draft.** A distinct draft (one `tr-` trace) with at least one ledger row or `row-map.md` spread row that maps to the failure mode and has an Evidence basis on this list. A draft counts once per failure mode, however many sources back it: a draft that was thumbs-downed and edited is one counted draft.

| Evidence basis | Counts when | Provider credited |
| --- | --- | --- |
| `reviewer-stated` | Always: a thumbs-down note, or a labeling verdict with a reason | The row's reviewer |
| `reviewer-edit-on-good` | Always | The row's reviewer |
| `provider-edit` | Confidence `high` only. Medium- and low-confidence diff-only rows are supporting evidence only. | The row's reviewer (the sending provider, or the trace's rater when the source names no sender); on legacy rows with Reviewer `audit`, the trace's rater |
| `eval-judge` | Always. It gets the same classification and contradiction checks as a provider comment. | The provider whose task the draft was for, when the export shows it; otherwise none |
| `phrase-scan` | Only when the failure mode also has a counted draft backed by provider evidence or an eval failure. The scan is a string match, and a masked match counts as identical text. | None |
| `slack` | Always: a provider's Slack report of a draft problem | The reporting provider |
| `provider-edit+note` | Always: an edit the provider's note explains | The row's reviewer |
| `note` (legacy edits-round value: a note with no matching edit) | Always | The row's reviewer |

Not on the list: a legacy row with Evidence basis `inferred`. Scripts read it as not counted and never rewrite the ledger. Thumbs-only rows (a verdict with no reason) are never evidence (`rules-core.md` section 5).

**Counted instance.** A counted draft, or a provider who raised the issue in an interview session and isn't already credited through a counted draft for this failure mode. A session mention from a provider whose draft already counts adds nothing. So a failure mode backed only by sessions needs 2+ providers to clear the floor unless it's severe safety, and it never reaches common, which needs drafts.

**Providers.** The distinct providers credited through counted drafts or sessions. Every row whose Reviewer is `unresolved` credits the same one provider, never one per draft; `sender_n` and `provider_n` handles count as written. An unmatched interview session handle stays its own provider (`ledger-schema.md` section 2a). Gate 2 flags every failure mode whose counted instances all come from one provider.

**Ledger matches.** When a failure mode matches a `held` row in the evidence ledger, the row's counted instances and providers add to this round's, counting each draft and provider once.

**Bands.** One-off is exactly 1 counted instance. Recurring is 2+. Common is 5+ counted drafts with 2+ distinct providers credited through counted drafts; providers credited only through sessions don't count toward the 2. Zero counted instances is band `none`.

**Eval-only evidence.** Five or more distinct `eval-judge` drafts for one failure mode count as common, even when the export credits no provider. Fewer than five follow the normal bands. Record eval-only drafts separately with their model era, and never pool Gemini 3.5 Flash drafts with Sonnet 5.5 or provider drafts without saying so.

Counted instances set only the floor and the band. Severity still comes from the worst credible instance, counted or supporting.

### Scoring procedure

1. **Severity class from the worst credible instance.** "Credible" means the instance is real in the evidence. A provider stated it, an edit shows it, or an eval judge or a Slack report raised it. Counted rows and supporting rows both qualify. A theoretical extension does not count.
2. **Evidence strength never lowers the level.** A missing comment is not evidence of a minor issue. A severe-safety failure mode with zero counted instances still needs the product owner's call at Gate 2 (section 0).
3. **Band from the counted instances**, after the consolidation rule.
4. **Level and filing call from the section 0 table.**
5. **No downgrades.** A defect a provider "would catch" stays at its level. The provider is the only check on every draft, and the bar is "sent as written." A provider's ability to catch a defect never moves it between classes either.
6. **Order within a level:** frequency (more counted instances first, then more providers), then worst-instance harm, then likelihood a provider misses it, then evidence strength (provider evidence, then eval only).

## 3. Special cases

| Case | Rule |
| --- | --- |
| **Upstream provider decision conflicts with protocol** (allergy, a premature increase, the wrong action type for the patient's need) | The decision itself is an input issue (classification rule in `clustering-and-dedup.md`). A missed flag becomes a ticket only if the generating prompts at the time of this round instruct the model to flag such conflicts; check this every round, it is not assumed. If they do not, log it in `input-issues.md` with the conflict noted; it is not a ticket. If `round.json` `scope.conflict_flags_in_scope` is true and a ticket is warranted, score it on the harm of sending the unflagged message (an allergy conflict is severe safety: P1 at one instance, P0 at 2+) and file one ticket per conflict type, because each has its own testable expected behavior. Round 3 example: conflict flagging was out of scope for the whole round (Danny, 2026-10-21), so every missed flag stayed in `input-issues.md` and no conflict-flag ticket was filed. |
| **Reviewer rule contradicted by a clinical answer or a product-owner ruling** | Do not file it as stated. Map it to "not a failure mode: contradicted by <clinical answer or ruling>" and show the product owner. Reframe it if a narrower version survives. |
| **Unfilled placeholder** (for example `[INSERT INTERIM INSTRUCTION - provider to specify]`) | A value the EMR or provider fills into a placeholder is an input issue (classification rule in `clustering-and-dedup.md`). Classify by who the generating prompts tell to author the token's content: if the model is told to write it, a leftover token is draft-controlled and scores by the severe-safety test above (a missing instruction needed to take the medication safely) unless the EMR is shown to block sending with the placeholder in place. If the model is told to leave the token for the provider or EMR to fill, it is an input issue, logged, not scored. |
| **Invented patient history** | Severe safety if it could change what the patient takes or a safety decision (P1 at one instance, P0 at 2+). Otherwise benign invented history, classed by the minor-safety test (section 1): at minor safety, P2 when recurring, P1 when common; held as a one-off. |
| **Decision items that gate a possible defect** | Give the decision ticket the level of the worst defect its answer could reveal, not Needs Prioritization. Untriaged Needs Prioritization tickets go stale. File as a `[Product Discovery]` Task under the discovery ticket conventions, at that level. The filing floor doesn't apply to decision items. |

## 4. Clinical answers that change expected behavior

Rows in extraction and ticket drafting use these answers to set expected behavior, in place of a reviewer's rule where they conflict. **Add a new row here, dated and sourced, when a later round gets a new clinical answer. Do not start a second table or a separate file.**

| Topic | Answer | Source |
| --- | --- | --- |
| 4-week minimum | The provider can adjust the dose; the next dose doesn't ship until the next refill. Patients must be on the dose 4 weeks (injectable) or 30 days (oral), but dosage adjustments before that are appropriate given the shipping schedule, since the patient will have been on the dose 4 weeks by the time the refill arrives. Medical Affairs: recommend the patient check in after 2+ weeks on the current dose before an increase. | Q3, [Care Delivery Experience lead], 2026-10-01 |
| Minimum wait length | Oral GLP-1: 30 days. Injectable: 28 days, or 4 weeks. | Q5, [Care Delivery Experience lead], 2026-10-01 |
| Treatment-gap restart table | [Care Delivery Experience lead] believes this was addressed with the new dose-down logic but didn't confirm which table applies. Treat the gap rule as still uncodified until a round confirms it. | Q1, [Care Delivery Experience lead], 2026-10-01 |
| Zofran | Consider Zofran on platform if the patient meets the clinical criteria and has had 2 or fewer Zofran prescriptions. Otherwise, lifestyle or OTC support. | Q10, [Care Delivery Experience lead], 2026-10-01 |
| Another GLP-1 on the chart at first prescription | The patient may continue a weight-loss drug the platform does not offer. Otherwise the intake attestation covers stopping it, so the message need not repeat it. | Q14, [Care Delivery Experience lead], 2026-10-01 |
| Prior dose unconfirmed at first prescription | Dose must be confirmed before the initial prescription. | Q15, [Care Delivery Experience lead], 2026-10-01 |
| Price on increase | Pricing consent is always required. | Q17, [Care Delivery Experience lead], 2026-10-01 |
| Plateau or regain on repeat step | Not a referral. Provide alternative dosing, alternative medications, and lifestyle support. | Q18, [Care Delivery Experience lead], 2026-10-01 |
| Draft versus protocol conflict | Write the draft and flag the conflict; evaluate only what the model controls. | Q19, Danny Pedrini, 2026-10-01 |

## 5. Standing decisions (apply every round unless a later round's gate overrides one)

1. **Order now versus decline on a 4-week-minimum case:** follow the Q3 answer above. Order the increase and tell the patient to finish the current dose first. "Decline until the next check-in" is not the expected behavior.
2. **Frequency bands:** one-off at 1 counted instance, recurring at 2+, common at 5+ counted drafts from 2+ providers (section 2). They replace the earlier breadth raise from P2 to P1 at 3+ drafts or 2+ action types.
3. **Benign invented history** (it cannot change what the patient takes): classed by the minor-safety test (section 1). At minor safety, P2 when recurring, P1 when common; held as a one-off.
4. **Decision items:** file as `[Product Discovery]` Tasks under the product-discovery ticket conventions, at the level of the worst defect the answer could reveal.
5. **"Draft did not flag the conflict" cases, when conflict flagging is in scope for the round:** one ticket per conflict type (allergy, timing, wrong action), because each has its own testable expected behavior. Each still has to clear the filing floor. When out of scope, log instead; see section 3.
