# Care Test Category Library

Reference for the `acceptance-testing-generator` skill. Replaces the fulfillment-domain category list.

Include only the categories the requirements actually touch. An unused category is noise, and an
empty category header in the output is a defect. Let coverage drive the count, never a target.

**Comprehensive mode** typically spans 6 to 12 categories. **UAT mode** typically collapses to 4 to 7
sections, because several categories fold into one provider-facing scenario. `[estimate range]`

---

## Category selection

| # | Category | Include when | Care-specific test angles |
| --- | --- | --- | --- |
| 1 | **Task Queue & Routing** | Requirements change how tasks are created, held, released, or assigned | Task creation held until a precondition clears; held task releases when the condition resolves; escalations and urgent cases are never held; get-next-task ordering; a held task does not double-create on retry |
| 2 | **Chart & Center Pane Display** | Requirements define what a provider sees when opening a task | Named data elements surface in one view; provenance indicators distinguish AI-captured from clinician-entered; the pane renders without the provider scrolling to find the decision-relevant field; check-in view shows what changed since last visit |
| 3 | **Provider Decision Flow** | Requirements cover accept, dismiss, modify, prescribe, or SOAP note | Accept pre-populates the treatment plan; dismiss collapses to today's experience; the prescribe path still runs existing validators; nothing sends without explicit provider confirmation |
| 4 | **Patient-Facing Flow** | Requirements cover patient asks, nudges, app surfaces, or consent | Questions arrive as one cohesive sequence, not trickled; the action item reflects real chart state; nudge cap is respected; the patient can reach the surface in the state the requirement specifies |
| 5 | **Chart Write-Back & Data Integrity** | Requirements persist anything to the chart or PHD | Free text is normalized to structured data before write; a raw reply cannot bypass a structured control; writes are attributed and dated; partial progress persists on drop-off; the value lands where that data lives today |
| 6 | **Clinical Safety Guardrails** | Requirements touch medication, dosing, interactions, or eligibility | The interaction engine still receives structured input; the existing clinical checker is not degraded; prescribe-time validators run unchanged; a misspelled or nonsensical entry is caught before save |
| 7 | **AI Guardrail Mechanism** | Requirements include a quality gate, confidence threshold, or virtual judge | Below threshold, nothing is vended and the surface is unchanged; the gate blocks rather than warns; a blocked output is logged; the gate runs per output, not per session. **Tests the mechanism. Never the model's quality.** See the scope rules in SKILL.md |
| 8 | **Degraded Path & Fallback** | Requirements name any no-consent, no-response, timeout, or service-down path | No consent falls back to today's behavior; no response after the specified nudges does not escalate; service unavailable degrades to the named floor rather than failing open; each fallback is reachable and observable |
| 9 | **Escalation & Flagging** | Requirements include a flag, report, or escalation affordance | The flag never blocks the workflow; the flag captures the output, its inputs, and what the user actually did; flags route to the named review queue; the flagged surface behaves as specified afterward |
| 10 | **Audit Trail & Versioning** | Requirements require replay, versioning, or decision capture | Each output is logged with its version and reasoning; any decision can be replayed; accept, modify, and dismiss are each captured with reason; the audit record survives a subsequent edit |
| 11 | **Latency & Perceived Responsiveness** | Requirements state a rendering, streaming, or sequencing expectation | The view renders atomically rather than piecemeal; a surface never appears after the user has started working; output streams progressively where specified. **Use the requirement's own wording. Never invent a millisecond budget** |
| 12 | **Scope of Practice & Authorization** | Requirements involve roles, licensure, or permission | Each role sees only what its permission allows; a licensure-gated action is blocked for an ineligible user; no action auto-executes without the required human step |
| 13 | **Instrumentation & Analytics** | Requirements name events, dashboards, or measured outcomes | The named event fires with its specified fields; per-item outcome is recorded at the specified grain; the dashboard view exists and is populated; an alarm threshold is wired, not just described |
| 14 | **Cross-System Sync** | Requirements span two or more systems | State agrees across both systems after the flow completes; the second system reflects the change within the specified window; a failure on one side does not silently diverge the other |
| 15 | **UI Design Verification** | Mocks or a prototype were provided | Surfaces match the approved mocks. Tag each with **Verified by: Design ([named reviewer])**. Typically 2 to 8 tests in Comprehensive `[estimate range]`. In UAT, **only where a section has a real design surface**, wherever that lands. Never one per section: that forces a contrived row on sections with nothing to look at |
| 16 | **Accessibility** | Requirements or the prototype involve keyboard, focus, or screen-reader behavior | Focus moves to the specified element; the interactive surface is reachable by keyboard; state changes are announced; contrast and target size meet the stated bar |
| 17 | **Empty, Loading & Error States** | Any surface can be empty, pending, or failed | The empty state matches the specified copy and affordance; the loading state blocks the actions it must block; an error is shown inline with a recovery path |
| 18 | ~~Scope Verification~~ | Retired 2026-10-27 | Tests trace only to the PRD's requirements and metrics. A clinically weighty exclusion is tested only when the PRD states it as a requirement |
| 19 | **Launch Gate Readiness** | The feature ships behind a flag or ramps by stage | The flag enables and disables cleanly; rollback has been executed, not just written down; monitoring and the named alarm are live; the ramp can be reduced without data loss |
| 20 | ~~Training & Enablement Readiness~~ | Retired 2026-10-27 | Training and enablement are Care Ops processes, not PRD requirements. No tests |
| 21 | **Performance & Volume** | Requirements state a volume, concurrency, or throughput expectation | Behavior holds at the stated volume; concurrent actors do not collide; no degradation of the named guardrail under load |
| 22 | **Privacy & Consent** | The feature is patient-facing, writes to the chart, or handles PHI | Consent state is respected before any outreach; the required disclaimer displays where specified; data is minimized to what the requirement names; access is logged |

---

## Common patterns by feature type

Use these as a starting shape, then adjust to the requirements in front of you.

| Feature type | Categories to reach for first |
| --- | --- |
| **Provider task surface** (center pane, summary card) | 2, 3, 11, 15, 17, 16 |
| **AI recommendation or draft surface** | 3, 7, 8, 9, 10, 11, 13, 15 |
| **Patient-facing conversational flow** | 4, 5, 8, 22, 17, 13 |
| **Chart data pipeline** (write-back, normalization) | 5, 6, 10, 14, 13 |
| **Task routing or queue change** | 1, 8, 12, 13, 21 |
| **Service contract or stub** | 10, 14, 13, 8 |
| **Launch or ramp change** | 19, 13, 8, 12 |

---

## Test naming

Format: `**[Area] - [Specific behavior]**`

Use a hyphen, never an em dash. Em dashes are a forbidden pattern in this workspace.

| Good | Why |
| --- | --- |
| `**Task Hold - Escalation Never Held**` | Names the area and the exact behavior |
| `**Write-Back - Free Text Normalization**` | A reader knows what is being checked before reading the cell |
| `**Recommendation Card - Below Threshold**` | Specific enough to file a defect against |

| Bad | Why |
| --- | --- |
| `**Data**` | No behavior named |
| `**Chart works**` | Not a behavior, and not binary |
| `**Recommendation Quality**` | Out of scope. This is eval measurement, not acceptance testing |
