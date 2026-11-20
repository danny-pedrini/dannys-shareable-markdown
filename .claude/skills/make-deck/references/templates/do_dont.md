# Template: do_dont

The behavior-contract slide. Use for messaging guidance, writing style, escalation rules, policy.

## When to use
- Messaging guides ("when talking to clinicians: DO X, DON'T Y")
- Writing or design guardrails for a team
- Process contracts ("how to file a JDI: DO X, DON'T Y")

## Outline schema
```json
{
  "template": "do_dont",
  "title": "Talking to providers about TPA",
  "dos": [
    "Lead with the safety improvement",
    "Show the soft-flag UX in the demo",
    "Say 'authoritative validation' not 'gatekeeper'"
  ],
  "donts": [
    "Use the word 'AI' without context",
    "Promise a specific date before June 1",
    "Refer to MedMatch and TPA interchangeably"
  ]
}
```

## Content rules
- `title`: sentence case, names the situation or audience
- `dos` / `donts`: 3-5 items each, parallel structure across columns
- Each item should be specific and concrete ("Show the soft-flag UX", not "Be thorough")
- Don't pair DOs with their literal opposite — that's redundant. Pair complementary behaviors.

## Visual spec (auto-applied)
- White background
- Title top-left, 36 pt Bold ink
- DO card on left: powder blue (`#D5E3EE`) rounded rect, "DO" label top-left at 18 pt Bold
- DON'T card on right: warm gray (`#D7D7D2`) rounded rect, "DON'T" label top-left at 18 pt Bold
- Body bullets at 16 pt with `• ` prefix
- Confidentiality footer auto-added

## Common mistakes
- DOs and DON'Ts that are literal inversions ("DO be clear" / "DON'T be vague") — pick the more useful framing and drop the other
- Vague items ("Be respectful") — name the concrete behavior
- Mismatched counts (5 DOs, 2 DON'Ts) — balance to within 1
