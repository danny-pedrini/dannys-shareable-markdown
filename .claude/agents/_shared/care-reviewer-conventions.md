# Care Reviewer Conventions

Shared reference for all `.claude/agents/*-reviewer.md` agents in this workspace. Apply workspace-specific items **only when the artifact under review names them** — never as assumed background.

> **Source:** [`AGENTS.md`](../../AGENTS.md), [Director of Product] Slack intro to Care team (Aug 2026)

---

## Care mandate

- **Mandate:** the interconnected **quality, pay, and routing** problem — how messaging quality is measured and incentivized, how work routes to the right clinician, and how that ties to patient retention.
- **North star:** build something patients love — improve provider-to-patient quality experience in pursuit of retention, not only provider efficiency and cost reduction.
- **Wedge:** cost-to-serve reduction ([CTO]'s directive). Galen (CDS + provider tooling in the EMR) is the primary wedge; scope is broader than shipping AI features alone.

---

## Default lens

| Lens | When to apply |
|---|---|
| **Provider / clinical-operator (default)** | EMR provider workflow, CDS surfaces, care task queues, provider messaging, chart completeness, routing/pay from the clinician chair |
| **Patient-facing** | Ivy, patient intake, patient portal, consumer app — when the artifact is clearly patient-facing |
| **Care coordinator** | CC queue, CC routing, non-prescribing clinical support — when artifact is CC-facing |

State the active lens explicitly in the TL;DR.

If the artifact spans non-Care systems, state the lens explicitly rather than assuming fulfillment or other domains.

---

## Tool access policy

- Agents **inherit every tool** available to the host session (Cursor or Claude Code): built-ins and all configured MCP servers.
- Preferred tools listed in each agent's `<tool_access>` section are **guidance, not limits** — use any tool when the artifact requires it.
- Use the minimum set needed; read the artifact before fetching externals.

### MCP no-inference rule

When a claim depends on live external data (Confluence, Google Docs, Looker, Jira, Figma, Slack, etc.):

1. Fetch via MCP first.
2. If the fetch fails → **stop** on that claim. Do not infer from repo grep or priors.
3. Flag: `[Source unreadable: paste, export, or fix MCP access]` + link/ID.

---

## Workspace convention glossary

Apply **only when the artifact references these** — do not inject into reviews of generic artifacts.

| Term | Meaning (H&H Care context) |
|---|---|
| **Galen** | Project using AI (LLM/ML CDS + provider tooling) to transform care work in the EMR |
| **CDS** | Clinical Decision Support — recommends; does not decide autonomously |
| **EMR** | Provider-facing system; at core a task/ticketing system being leapfrogged with AI |
| **Ivy** | Patient-facing AI companion / messaging conduit |
| **CQS** | Clinical Quality Score — book-audit + incident based provider quality metric |
| **5D** | Provider messaging quality dimensions (decision quality, drives results, direction, done-in-one, doctor relationship) |
| **MedMatch / TPA** | Today's clinical recommendation/eligibility engines; degradation floor for new CDS |
| **G0–G3 gates** | Launch gates: back-data → shadow → ramp → GA |
| **INS-ID** | Instrumentation ID traceability in Phase metrics inventory |
| **Complete the Chart** | Patient-facing intake pre-work; Phase 1 Galen surface |
| **EMR 2.0 summary card** | Provider chart-orientation support tool (not a substitute for full clinical review) |

### Key stakeholders (sign-off context — not for every finding)

| Role | Names |
|---|---|
| Clinical Quality | [Clinical Quality co-lead], [Clinical Quality co-lead]; CMO [CMO] |
| Care Ops | [SVP of Care Experience] org; [Clinical Ops lead] (Clinical Ops); [Care Delivery director] (Care Delivery) |
| BizOps / routing | [Strategy & Ops partner] |
| Workforce | [Workforce Management lead] |
| Training | [Training lead] |
| CX (Care) | [CX lead] |
| TPM / PMO | [Care PMO project manager], [TPM], [TPM] |

---

## Reviewer lane map

Use for handoffs — do not duplicate another reviewer's lane.

| Agent | Owns | Defers to |
|---|---|---|
| **pm-exec-reviewer** | Strategy, prioritization, metrics quality, business case, narrative, org alignment | eng, design, architecture, clinical sign-off detail |
| **architect-reviewer** | Platform topology, integration contracts, phase sequencing, cross-team NFR envelope | DE (system complexity/AI architecture), backend (endpoint/schema detail) |
| **distinguished-engineer-reviewer** | System complexity, AI/ML architecture, optimization target, reversibility, blast radius, technical-strategy alignment | architect (topology/contracts), ai-eng (eval harness implementation), backend (schema detail) |
| **ai-eng-reviewer** | Eval strategy, prompt/RAG, guardrails, HITL implementation, model routing | DE (system-level AI architecture), pm-exec (eval strategy as product decision) |
| **backend-eng-reviewer** | API/schema, data integrity, resilience, observability, BE security/compliance | architect (boundaries), DE (system topology) |
| **frontend-eng-reviewer** | Component architecture, async states, a11y, Web Vitals, FE security | ux-design-reviewer (heuristics/visual), backend (API contracts) |
| **ux-design-reviewer** | Nielsen heuristics, IA, interaction patterns, visual hierarchy, design-system fidelity | frontend-eng-reviewer (implementation), telehealth-provider (workflow from chair) |
| **data-analytics-eng-reviewer** | Metric definition, grain, instrumentation, experiment design, Looker/dashboard design | pm-exec (strategy/metric targets), clinical-quality (CQS rubric design) |
| **clinical-quality-exec-reviewer** | Patient harm, CQS guardrails, scope-of-practice, clinical sign-off readiness, messaging quality rubric | ai-eng (eval implementation), care-ops (ops readiness), telehealth-provider (ergonomics) |
| **care-ops-exec-reviewer** | Provider workflow ops, workforce impact, training/comms, routing/skip mechanics, ops measurement | clinical-quality (CQS definition), tpm (schedule), pm-exec (strategy) |
| **telehealth-provider-reviewer** | Provider mental model, task-queue ergonomics, adoption, webside manner, clinical safety from the chair | clinical-quality (sign-off/CQS), ux-design (heuristics) |
| **technical-project-manager-reviewer** | Critical path, dependencies, gates, RACI, blocker hygiene, capacity realism | pm-exec (scope/strategy), care-ops/clinical-quality (sign-off content) |

### Overlap boundaries (critical)

- **architect-reviewer** vs **distinguished-engineer-reviewer:** topology/contracts/sequencing vs system-level complexity, AI/ML architecture, optimization target, reversibility.
- **ai-eng-reviewer** vs **distinguished-engineer-reviewer:** eval/guardrail/HITL *implementation* vs system-level AI architecture / optimization target / reversibility.
