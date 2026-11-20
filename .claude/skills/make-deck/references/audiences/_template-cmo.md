# Audience: your CMO / clinical or medical leader

> Template. Copy this to `<name>.md` and edit the four sections marked with EDIT.

## Role

EDIT: Their title, what they sign off on, scope of clinical authority.

Example: "CMO at Acme. Medical lead. Sign-off audience for any clinical-safety change. Reads decks for safety risk and compliance posture first; everything else second."

## What they care about

1. Clinical safety. Will this change harm a patient?
2. Medical quality. Does this meet or exceed standard of care?
3. Regulatory compliance (HIPAA, DEA, PDMP, state pharmacy boards, etc., as applicable to your domain).
4. Provider workflow impact. Will clinicians push back on this?
5. The audit trail. Who decided what, when, with what justification.

## Default framing

Open with the clinical-safety frame. State the safety claim explicitly: "This change does not introduce a new patient-safety risk because X." Or, if it does, surface the risk + mitigation up front.

Default spine: **B (recommendation)** for new policies. **D (pre-mortem)** when changing a clinical workflow.

Exec summary lens (3 cards):
- Card 1: clinical-safety claim ("No new safety risk introduced because of guardrail X")
- Card 2: compliance posture ("HIPAA/state-board OK; legal sign-off pending")
- Card 3: provider impact ("Workflow add: 15 sec/encounter; offset by automation Y")

## Content cuts

- **Include**: safety claim with the reasoning, compliance status by jurisdiction, provider workflow delta with timing, clinical evidence behind any clinical claim.
- **Cut**: business-impact framing as the lead, customer-acquisition language, growth metrics (those go in the appendix or speaker notes if relevant).
- **Translate**: engineering acronyms on first mention. Don't assume tech-stack context.

## Tone adjustments

This is the one place to formalize slightly — clinical-safety topics demand precise, clinical-formal language. State claims explicitly. Avoid casual register on safety statements. Cite evidence with source + date for any clinical claim.

Avoid: hedging on safety. If you're not sure, say "we don't yet know" — never imply safety where unproven.

## Slide-level defaults

| Slide type | Default behavior |
|---|---|
| cover | Subtitle states the clinical change in plain medical language. Date stamped. |
| exec_summary | Lead is the safety claim. Cards: safety / compliance / provider impact. |
| comparison_2x2 | Use for risk register: clinical-impact × likelihood, with named mitigations. |
| do_dont | Use for provider-facing behavior contracts (the DO/DON'T pattern is exactly how clinical SOPs read). |
| section_divider | "Safety" / "Compliance" / "Workflow" / "Decision needed" |
| close slide | Default ask: explicit clinical sign-off on a date. "Need your sign-off on X by <date>." |

## Things they will ask

1. What's the safety claim, and what's the evidence?
2. Are there any cases where this could harm a patient?
3. What states / jurisdictions are affected? Any board notification needed?
4. How does this change a clinician's workflow, in seconds?
5. Who decided this, and was clinical leadership consulted?

## Things to NEVER do for this audience

- Present a clinical workflow change without naming the safety angle.
- Use marketing language ("revolutionary", "best-in-class") in any clinical claim.
- Bury PDMP / DEA / state-board implications in an appendix.
- Make a clinical claim without a citable source.
- Assume sign-off is implied. Always make the ask explicit.

## When this is the wrong audience config

- If the deck is operational and has no clinical change, use `_template-cpo.md` or the eng templates.
- If the deck is for a multi-stakeholder review where the CMO is one reader among several, still apply the CMO frame on the safety slides specifically and note in the cover that the deck has multiple audiences.
- If you're not in a regulated domain (no HIPAA / no clinical compliance applicable), this template doesn't apply.
