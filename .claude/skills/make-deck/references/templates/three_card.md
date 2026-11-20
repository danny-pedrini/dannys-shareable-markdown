# Template: three_card

Horizontal cards with a header + body each. Reach for this whenever you have 2-4 parallel items that need a short label and a short description. Cleaner than bullets when items are distinct entities (services, options, audiences, products).

## When to use
- 2-4 parallel items, each with a name + description
- Service inventories ("the three services")
- Option comparisons ("three pricing tiers", "three RFCs in review")
- Pillar layouts ("three priorities for Q2")

## When NOT to use
- 5+ items (gets too narrow per card)
- Items that fit a sequence (use `flow_steps`)
- Items that need full-paragraph descriptions (use `bullets` or split into multiple slides)
- A single number is the point (use `key_stat`)

## Outline schema
```json
{
  "template": "three_card",
  "title": "The three services they touch",
  "lead": "Plus storefront, the thin patient-only gateway.",
  "cards": [
    {
      "header": "emr_service",
      "body": "Kotlin middleware. Owns visits, appointments, Kafka consumption, and OpenSearch for Get Next Task."
    },
    {
      "header": "emr_backend",
      "body": "Spring Boot service. Holds intake-form configs (Marcus's form definition lives here). API key auth."
    },
    {
      "header": "emr-storefront",
      "body": "Patient-token-to-API-key proxy in front of Marcus's path. Not read in code; doc only."
    }
  ]
}
```

## Content rules
- `title`: sentence case, names what the cards are
- `lead`: optional one-line setup
- `cards`: 2-4 entries (validator caps at 4)
- Each card needs `header` (short name, 1-3 words) and `body` (1-2 sentences, ~120 chars)
- Cards render as sage-tint rounded rects with sage-accent header + ink body

## Visual spec (auto-applied)
- White background
- Title top-left, 30 pt Bold ink
- Optional lead at 16 pt
- Cards in horizontal row, equal width, sage-tint (`#F5FAF6`) rounded rects
- Headers: 18 pt Bold sage accent (`#0097A7`)
- Body: 14 pt regular ink
- Confidentiality footer auto-added

## Common mistakes
- Headers that are sentences ("The first service is emr_service") — just "emr_service"
- Imbalanced bodies (1 sentence + 4 sentences) — match length across cards
- 5+ cards crammed in — split into two slides
- Cards that aren't actually parallel (one is a service, one is a metric, one is a person) — that's a list, use `bullets`
