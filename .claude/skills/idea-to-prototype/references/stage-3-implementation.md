# Stage 3 — Implementation

Read `context-contract.md` first if you have not this run.

---

## Step 3.1: Scaffold

Two paths. Check whether `prototypes/_design-system/<app>/starter/` exists.

### Warm path — starter exists (the normal case)

No subagent. The orchestrator does this directly:

```bash
cp -R prototypes/_design-system/<app>/starter/ prototypes/<feature>/
cd prototypes/<feature> && npm install && npm run dev   # confirm boot, then stop
```

Then:

1. Read `prototypes/_design-system/<app>/starter/STARTER.md` for what the template already provides.
2. Update `package.json` name to the feature slug.
3. Create stub files for each new component in the traceability matrix.
4. Add routes for the pages in the traceability matrix.
5. Confirm `npm run dev` boots and `npx tsc --noEmit` is clean **before** dispatching implementers.

This replaces a full scaffolder subagent plus its boot-debug loop. It is also *more* faithful than regeneration: the starter's token files were validated against production and its app shell already scored ≥90 in a prior fidelity review. Regenerating reintroduces the cross-run variance the app-wide design system exists to prevent.

**If the starter fails to boot:** it has drifted (dependency rot, Node version). Fix it in the starter directory itself, verify, then re-copy — so the fix benefits every future run. Note the fix at Gate 3.

### 🧊 Cold path — no starter yet (first prototype for this app)

Spawn one scaffolder (`general-purpose`) — note that its output gets promoted to a starter every future run inherits, so it must be built to last:

```
You are scaffolding the first prototype for <app>. Your output will be promoted to a
reusable starter template that every future prototype for this app inherits, so build it
to last.

Design brief: <paste FULL content of design-brief.md>
Tech Stack + Visual Identity + Common Mistakes: <paste those three sections from the
  app-wide design-system.md>

App-wide design system — READ BY PATH for all token values:
  prototypes/_design-system/<app>/design-system.md

Before writing files, quote from the app-wide file: the framework + version, the exact
page background color, and the base font with its loading strategy. If any is missing,
stop and report it.

Your job:
1. Initialize in prototypes/<feature>/ using the EXACT production framework and router
   from Tech Stack. Not a similar one. Not one you prefer.
2. Install dependencies matching the production stack, at compatible versions.
3. Create theme/token files mirroring production's structure and file names. Copy values
   VERBATIM from the app-wide design system — do not approximate, round, or rename.
   Mirror production's own file organization (whatever recon found: a theme dir, a tokens
   package, a tailwind config).
4. Set up font loading per the Font Handling section — production font or its documented
   fallback, never a generic sans-serif.
5. Set up the mock API layer per the Data Layer section (MSW handlers if production uses MSW).
6. Build the app shell — header, nav, page-layout wrapper — matching the structural
   patterns in Visual Identity exactly. This is the highest-leverage thing you build: it
   appears on every page of every future prototype.
7. Create the URL-param state-simulation utility (?loading, ?error, ?empty).
8. Create stub files for each component in the traceability matrix and routes for each page.

Critical:
- The dev server MUST boot. Run `npm install && npm run dev` and confirm.
- `npx tsc --noEmit` must be clean.
- Token files must be copy-paste faithful to the documented production values.
- Report any setup error rather than working around it silently.

Report back: files created, the boot confirmation, tsc result, and any value you could
not find in the app-wide design system.
```

---

## Step 3.2: Implementer / Validator pairs

One implementer + one independent validator per component spec, dispatched in parallel.

### Implementer prompt (`general-purpose`)

```
You are implementing ONE component to spec.

Spec: <paste the FULL content of tasks/NN-component.md>
Design brief: <paste the FULL content of design-brief.md>
App Visual Identity: <paste that section from the app-wide design-system.md>
App Common Mistakes To Avoid: <paste that section from the app-wide design-system.md>
Project root: prototypes/<feature>/

CONTRACT DEFINITIONS (paste the `## Contract Authority` table from tasks/_traceability.md,
PLUS the actual definitions of every item it owns, copied verbatim from the contract
authority spec):
<paste here>

Your spec REFERENCES these shared types and props by name rather than restating them — the
definitions above are the only place their real shapes appear. Use them exactly as written.
Never infer a shared type's shape from how your spec uses it, and never redefine one
locally. If your spec references a contract item that is not in the definitions above, STOP
and report it — that is a Stage 2 gap, not something to guess at.

App-wide design system — READ BY PATH. This is your allowlist together with the brief:
  prototypes/_design-system/<app>/design-system.md
Look up in it: exact token values, the Components table (for base components and their
prop signatures), Type Interfaces, Reusable Style Objects, Data Layer, Forms.

PROOF OF READ — before writing any code, quote:
1. The exact value + citation of the most important token you will use (typically the
   background or primary text color).
2. The exact prop signature of the primary base component you will reuse.
3. The exact name + source of the TypeScript interface your mock data will use.
If you cannot find any of these, STOP and report which lookup failed. Do not proceed on
assumption. Do not substitute a value you consider likely.

Hard rules:
- Use ONLY values from the app-wide design system (Established status) or the design brief.
  The allowlist is the union of those two files. Nothing else.
- NEVER invent a color, gradient, font, or visual pattern. If you need something absent
  from both files, stop and flag it.
- Match production coding conventions: file structure, naming, import style.
- Implement EVERY acceptance criterion.
- Implement ALL states listed in the spec (default, loading, empty, error, edge cases).
- Wire state simulation via URL params (?loading, ?error, ?empty).
- Use the app's data-fetching library with mock fetchers — NEVER raw useState for data
  that would be server-fetched in production. Mock hook signatures must match production
  so engineers swap mock → real with zero component changes.
- Reuse base components by their EXACT prop interfaces. Never hand-roll a Button, Input,
  or Select the app already provides.
- Mock data types MUST come from the Type Interfaces section where one applies.
- Forms use the app's form library with proper labels and a11y wiring.
- Follow the structural pattern named in the spec's Visual Reference section. If it says
  the inspiration uses a Table with custom Cell wrappers, do that — not a DataGrid, not a
  hand-rolled table.

When done, list every file created/modified and confirm each AC is implemented, with the
proof-of-read block at the top of your response.
```

### Validator prompt (`general-purpose`, separate invocation)

```
You are validating a component implementation. You did not write this code. Default to FAIL.

Spec: <paste the FULL content of tasks/NN-component.md>
Design brief: <paste the FULL content of design-brief.md>
Contract definitions: <paste the same Contract Authority table + owned definitions given to the implementer>
Files created/modified: <list>

App-wide design system — READ BY PATH. Allowlist = this file UNION the brief:
  prototypes/_design-system/<app>/design-system.md

PROOF OF READ — before validating, quote the exact value + citation for two tokens the
implementation uses. If a value in the code does not appear in either file, that is a
Critical finding.

Validation checklist — cite file:line for every finding:

1. Spec coverage: every AC implemented? Quote the AC, then quote the code.
2. Allowlist fidelity: EVERY color, font, spacing value, and style object in the code —
   verify each against the app-wide file or the brief by lookup. List each value and where
   you found it. Anything unfound = Critical.
3. Inspiration alignment: does the implementation follow the structural pattern from the
   spec's Visual Reference and the brief's "Build It Like This"? Wrong primitive (DataGrid
   where the inspiration uses Table) = High.
4. Base component reuse: Button/Input/Select/etc. imported from the app's library? Any
   hand-rolled base component = High.
5. Data layer: server-shaped data via the app's data library? useState holding
   API-response-typed data = High.
6. Form compliance: form library with labels and a11y? Raw <input> + useState = High.
7. Type interface reuse: mock data references a real interface from the app-wide file?
7b. Contract compliance: every shared type/prop the code uses matches the Contract
    Authority definitions exactly — same name, same shape. A locally-redefined or
    shape-drifted contract item = High. This is the implementation-time manifestation of
    the drift that cost three fix-loop rounds in a prior run.
8. States: all spec states implemented AND reachable via URL params? Verify the param
   actually changes rendered output — a variable assignment that nothing reads is a FAIL.
9. Edge cases from the spec handled?
10. Mock data shape matches the spec?
11. No invented visuals: scan every hex, rgb/rgba, hsl, gradient, AND font-family
    declaration. Each must trace to the allowlist.
12. Convention match: file organization and naming match the app and the inspiration
    source? (Framework correctness is eval G2's job — this covers organization only.)

Write to: prototypes/<feature>/.pipeline/reviews/<NN>-impl-validation.md
End the file with exactly one line: "Verdict: PASS" or "Verdict: FAIL"

FAIL on ANY Critical/High finding.
```

---

## Step 3.3: Retry loop

For each FAIL, spawn a **fresh** implementer with:

- The validation report pasted in full (it is the framing for the fix)
- The same spec and brief pasted
- The same app-wide path plus proof-of-read requirement

Max 2 retries per component, then escalate to the user with the outstanding findings.

If a retry fails because a needed value genuinely is not in the allowlist, that is not an implementation failure — it is a Gate 1 gap. Surface it to the user for an allowlist addition rather than retrying a third time.

---

## Step 3.4: All-components-pass gate

Do not start Stage 4 until every component has `Verdict: PASS` on disk in `.pipeline/reviews/`.

---

## Starter promotion (after Gate 3, cold-start runs only)

**Trigger:** the run reached Gate 3 with fidelity ≥90 **and** no starter exists for this app yet.

Gating on the score is the point — you are freezing this scaffold for every future prototype, so only freeze one that demonstrably looks right.

Steps:

1. Create `prototypes/_design-system/<app>/starter/`.
2. Copy from the finished prototype: framework config, `package.json` (+ lockfile), theme/token files, font loading, mock-API setup, the app shell (header/nav/layout), and the URL-param state utility.
3. **Exclude** everything feature-specific: feature components, feature routes, feature mock fixtures, `.pipeline/`, `node_modules/`, `design-brief.md`, `tasks/`.
4. Verify in isolation: `cp -R` to a temp dir, `npm install && npm run dev`, `npx tsc --noEmit`. It must boot clean with no feature code present.
5. Write `STARTER.md` recording: source feature, promotion date, fidelity score at promotion, app-wide design-system schema version, what is included, and what each new prototype must add.
6. Report the promotion at Gate 3 so the user knows a reusable asset now exists.

**Maintenance:** the Stage 1A freshness check verifies the starter's token files against production alongside the design-system claims. On drift, patch the starter and bump its `STARTER.md` version.
