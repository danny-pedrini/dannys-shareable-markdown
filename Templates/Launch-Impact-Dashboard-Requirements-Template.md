# Launch Impact Dashboard — Requirements Template

**Purpose:** Hand this one-pager to your analytics team to scope and build a launch-impact dashboard. Fill every `[TK]` block before sharing.

**Out of scope for this doc (by design):**
- **Instrumentation and data pipeline requirements** → owned by Eng (link to eng spec / event taxonomy)
- **Alerting and incident thresholds** → define separately with Analytics/Ops if needed

---

## 1. Executive summary

| Field | Value |
| --- | --- |
| **Product / feature** | [TK] |
| **Launch date** | [TK] (timezone: [TK]) |
| **Primary audience for this dashboard** | [TK — e.g., PM, exec, ClinOps] |
| **The one question this dashboard answers** | [TK] |
| **Primary success metric** | [TK — see §6 for targets/thresholds] |
| **Dashboard DRI (Analytics)** | [TK] |
| **PM DRI** | [TK] |
| **First readout date** | [TK] |
| **Links** | PRD: [TK] · Launch plan: [TK] · Feature flag / rollout doc: [TK] |

---

## 2. Launch scope and exposure definition

Define exactly who is "in the launch." Analytics cannot build cohort logic without this.

| Field | Definition |
| --- | --- |
| **Rollout plan** | [TK — % ramp schedule, markets, user types] |
| **Inclusion criteria** | [TK — who sees the feature] |
| **Exclusion criteria** | [TK — internal users, test accounts, partial exposure, etc.] |
| **Control group** | [TK — holdout, pre/post, matched cohort, or none] |
| **Unit of analysis** | [TK — patient, visit, message thread, provider shift, etc.] |
| **Exposure event / flag** | [TK — how analytics identifies treated users] |

---

## 3. Decision framework — metric tiers

Assign every metric to a tier. State **direction of good** (↑ or ↓) and whether it is **blocking** for scale-up decisions.

| Tier | Purpose | Metrics |
| --- | --- | --- |
| **North star / primary** | Did we achieve the intended outcome? | [TK] |
| **Input / driver** | Why did the north star move (or not)? | [TK] |
| **Guardrail** | What must *not* get worse? | [TK] |
| **Diagnostic / debug** | Triage when something looks off | [TK] |

**Heuristic for v1:** 1 primary · 3–5 drivers · 5–8 guardrails.

---

## 4. Metric dictionary

One row per metric. This is what analytics implements.

| Name (dashboard label) | Tier | Definition (numerator / denominator) | Formula or canonical spec | Population filter | Attribution window | Grain | Direction of good | Blocking? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [TK] | [TK] | [TK] | [TK — link or inline] | [TK] | [TK — e.g., 7-day post-exposure] | [TK — daily, weekly, per cohort] | [TK — ↑ or ↓] | [TK — Y/N] |
| | | | | | | | | |
| | | | | | | | | |

---

## 5. Segmentation and cuts

List the slices you expect to review every week — not "all segments."

| Segment | Why it matters | Minimum sample size / suppression rule |
| --- | --- | --- |
| Rollout cohort (treatment vs control) | [TK] | [TK] |
| [TK — e.g., tenure: new vs returning] | [TK] | [TK] |
| [TK — e.g., specialty / condition] | [TK] | [TK] |
| [TK — e.g., geography / platform] | [TK] | [TK] |

**Default dashboard filters:** [TK — e.g., last 28 days, treatment only, exclude internal]

---

## 6. Targets, baselines, and success criteria

Analytics needs numbers, not vibes. Define what the dashboard should compare against and what "success" means for each readout.

### Baselines and targets

| Metric | Pre-launch baseline | Baseline period | Target | Minimum detectable effect | Link to launch plan |
| --- | --- | --- | --- | --- | --- |
| [TK — primary] | [TK] | [TK — e.g., 4–8 weeks pre-launch] | [TK] | [TK] | [TK] |
| [TK — guardrail] | [TK] | [TK] | [TK — max acceptable degradation] | [TK] | [TK] |
| | | | | | |

### Statistical approach *(if applicable)*

| Field | Value |
| --- | --- |
| **Method** | [TK — e.g., two-proportion z-test, sequential monitoring, none] |
| **Significance level** | [TK — e.g., α = 0.05] |
| **Power / sample size assumptions** | [TK] |
| **Analysis plan link** | [TK] |

### Decision gates by timeframe

| Timeframe | What you read | Go / no-go criteria |
| --- | --- | --- |
| **Day 1–3** | [TK — sanity checks, guardrails only] | [TK] |
| **Week 1** | [TK — early signal on drivers] | [TK] |
| **Day 30** | [TK — primary readout] | [TK] |
| **Day 90** | [TK — retention / quality durability, if relevant] | [TK] |

### Stop / rollback triggers

List guardrail breaches that block scale-up or trigger rollback. Analytics should surface these prominently on the outcome scorecard (§7, View 2).

| Guardrail metric | Trigger condition | Action |
| --- | --- | --- |
| [TK] | [TK — e.g., >X% degradation vs baseline] | [TK — pause ramp / rollback / investigate] |
| | | |

---

## 7. Dashboard information architecture

Describe how you want to *consume* the data, not just what to measure.

### View 1 — Launch pulse

| Field | Value |
| --- | --- |
| **Purpose** | [TK — exposure, adoption, activation funnel] |
| **Audience** | [TK] |
| **Default time range** | [TK] |
| **Refresh cadence** | [TK — e.g., daily T+1] |
| **Key metrics / charts** | [TK] |

### View 2 — Outcome scorecard

| Field | Value |
| --- | --- |
| **Purpose** | [TK — primary + guardrails vs baseline] |
| **Audience** | [TK] |
| **Default time range** | [TK] |
| **Refresh cadence** | [TK] |
| **Key metrics / charts** | [TK] |

### View 3 — Drivers

| Field | Value |
| --- | --- |
| **Purpose** | [TK — decomposition of primary metric movement] |
| **Audience** | [TK] |
| **Default time range** | [TK] |
| **Refresh cadence** | [TK] |
| **Key metrics / charts** | [TK] |

### View 4 — Quality and trust *(if applicable — e.g., AI launches)*

| Field | Value |
| --- | --- |
| **Purpose** | [TK — override rate, error rate, human-in-the-loop signals] |
| **Audience** | [TK] |
| **Default time range** | [TK] |
| **Refresh cadence** | [TK] |
| **Key metrics / charts** | [TK] |

### View 5 — Operational health

| Field | Value |
| --- | --- |
| **Purpose** | [TK — latency, failure modes, support ticket proxy] |
| **Audience** | [TK] |
| **Default time range** | [TK] |
| **Refresh cadence** | [TK] |
| **Key metrics / charts** | [TK] |

### View 6 — Cohort explorer

| Field | Value |
| --- | --- |
| **Purpose** | [TK — segment cuts with consistent filters] |
| **Audience** | [TK] |
| **Default time range** | [TK] |
| **Refresh cadence** | [TK] |
| **Key metrics / charts** | [TK] |

*Delete views that do not apply. Add views if needed.*

---

## 8. Experiment and causality notes

Skip or shorten if this is a full-fleet launch with no control.

| Field | Value |
| --- | --- |
| **Design** | [TK — RCT, staggered rollout, diff-in-diff, pre/post, none] |
| **Known biases** | [TK — selection, novelty, seasonality] |
| **Allowed claims** | [TK — "associated with" vs "caused by"] |
| **Pre-registered primary metric** | [TK — yes/no; link if yes] |
| **Analysis plan link** | [TK] |

---

## 9. Governance

| Field | Value |
| --- | --- |
| **Dashboard DRI (Analytics)** | [TK] |
| **Metric definition approvers** | [TK — PM, DS, ClinOps as needed] |
| **Review cadence** | [TK — e.g., daily during ramp, weekly after] |
| **Change control** | [TK — how definition changes are logged] |
| **Stakeholder distribution** | [TK — who gets access / weekly digest] |

---

## 10. Appendix

- **Mock / wireframe:** [TK — link or embed]
- **Looker / SQL logic stubs:** [TK]
- **Glossary:** [TK — domain terms analytics may not know]
- **Open questions**

| Question | Owner | Due |
| --- | --- | --- |
| [TK] | [TK] | [TK] |
| | | |

---

## How to use this template

**v1 scope heuristic:** 1 primary metric · 3–5 drivers · 5–8 guardrails · 6 segments max.

**Definition principles (§4):**
- Numerator and denominator in plain English — no ambiguous "active user" language
- Population filters consistent across related metrics in the same view
- Attribution windows explicit and aligned to the product behavior being measured

**Pass/fail test:** If you can run a 15-minute launch review on Friday of week 2 using only this dashboard spec, the doc is ready to hand off. If it reads like a metrics wish list, trim until it isn't.
