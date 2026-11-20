# Template: flow_steps

Horizontal numbered stepper. Use instead of a bullets slide whenever content is a sequence: a flow, a process, a chain of events. Visually shows progression.

## When to use
- Any "this happens, then this, then this" sequence (3-5 steps)
- End-to-end flows (e.g., "Sarah's visit, end to end")
- Technical request paths (e.g., "patient submits intake → storefront → emr_backend → ...")
- Onboarding journeys, escalation paths

## When NOT to use
- 1-2 steps (use bullets or just a sentence)
- 6+ steps (gets visually cramped; split across two slides or rethink granularity)
- Parallel items that aren't sequential (use `three_card` instead)

## Outline schema
```json
{
  "template": "flow_steps",
  "title": "What happens when Sarah's clinician opens her chart",
  "lead": "Every call goes to emr_service at NEXT_PUBLIC_EMR_SERVICE_URL with an auth header.",
  "steps": [
    "Clinician opens EMR web (emr-clients)",
    "App fires getVisitById, GET /v1/visit/:id",
    "Follow-up calls: health info, intake answers, modality",
    "For video, join_call returns the room token",
    "start_appointment and complete_appointment record timing"
  ]
}
```

## Content rules
- `title`: sentence case, names the flow (e.g., "Marcus's intake hits the chart")
- `lead`: optional one-line setup (often the rule that governs the flow)
- `steps`: 3-5 entries. Each is one phrase (≤80 chars). Imperative or noun-first.
- Steps render as numbered sage-accent circles with the phrase below each
- Each step should be one clear action or moment, not a paragraph

## Visual spec (auto-applied)
- White background
- Title top-left, 30 pt Bold ink
- Optional lead at 16 pt
- Steps row centered horizontally
- Each step: 70 pt sage-accent (`#0097A7`) circle with white number, 14 pt ink phrase below
- Confidentiality footer auto-added

## Common mistakes
- Steps that are full sentences ("Then the application proceeds to fire the getVisitById endpoint which returns the visit object") — cut to "App fires getVisitById"
- Mixing tenses across steps (some "Clinician opens", some "App fired") — pick one
- Splitting one logical step into two ("Open EMR" / "Click visit") — combine
- Putting a CTA in step 5 ("Read the source doc") — separate "next up" goes on a section_divider or do_dont
