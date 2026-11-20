# Source Ingestion

Reference for the `acceptance-testing-generator` skill. How to obtain each input, in what order of
precedence, and what to do when retrieval fails.

---

## Precedence: which source wins

| Rank | Source | Role |
| --- | --- | --- |
| 1 | **Requirements** (PRD, user stories, acceptance criteria, one-pager, spec) | Source of truth. Every test traces here |
| 2 | **Figma mocks** | Design intent. Drives design-fidelity tests only |
| 2 | **Prototype code** | Implementation detail. Enumerates states the requirements leave implicit |
| 2 | **Deployed prototype** | Rendered reality. Evidence for states the code read cannot confirm |

The ranking above is the **default**, and it holds unless Danny declares otherwise at intake. See
`<source_precedence>` in SKILL.md, which is authoritative.

**Under the default (requirements win),** when a rank 2 source contradicts the requirements:

1. The requirement wins.
2. The conflict goes in the Source Precedence and Discrepancies table. In Comprehensive mode that table
   is published; in UAT mode it is a working section reported in chat.
3. Never encode the rank 2 behavior as a test without flagging it.

**Exception:** when the requirements are genuinely silent on a detail (exact spacing, icon choice,
hover treatment), a rank 2 source may be used directly. Note the source in the test.

**Under a declared mocks-win override,** the ranking inverts for that run only. The realistic case is a
launch gate where design has iterated for weeks past a PRD nobody has touched. Then:

1. The mock wins, and it is the spec rather than a conflict.
2. **Build no discrepancy table.** Cataloguing "conflicts" against a superseded PRD is noise, and a test
   resolved to a superseded statement is simply wrong.
3. Report to Danny in chat which PRD statements the mocks have superseded, so he can decide whether the
   PRD needs updating.

**Never overridable, under any precedence:** fixture data is not a requirement, and a failed retrieval
is never reconstructed. Both rules below hold regardless of which source wins a conflict.

---

## The retrieval hard stop

**Non-negotiable.** If any retrieval fails, stop the run and alert Danny. Never infer, reconstruct,
or approximate a source you could not read.

Failure means any of: auth error, `not_found`, empty result, timeout, partial content, a truncated
read you did not complete, a rate limit, or an MCP server that is unavailable.

### On failure

1. **Stop.** Do not proceed to test generation. Do not substitute repo grep, prior sessions,
   filenames, URLs, or "probably about X" reasoning.
2. **Report** plainly: which source, which tool, which resource ID, and the error text.
3. **Ask** for one of: a paste, a screenshot, fixed MCP access, or an exported copy saved to the repo.
4. **Resume** only after primary-source content arrives.

### One retry is allowed

Retry once with corrected parameters (fixed path, corrected page ID, different ref). If the retry
fails, stop and report. Do not retry a third time.

### What you may still do without access

- Troubleshoot the auth or access problem with Danny.
- Save Danny-provided content to the repo with a `> **Source:**` block.
- Proceed with the sources you *did* successfully retrieve, **if and only if** Danny explicitly says
  to continue without the failed one. Record the omission in the output and the trace.

### Placeholder pattern

When Danny approves proceeding without a source, mark every affected spot:

```
[Source unreadable: paste, export, or fix MCP access]
```

Include the link or resource ID next to it. Never invent an owner, date, threshold, quote, or number
to fill the hole.

---

## Requirements: how to get them

### Paste (primary path)

The default. Danny pastes requirement content into the conversation. Nothing to retrieve, nothing to
fail. Confirm back what you received before generating: the requirement IDs found, the sections
covered, and anything that looks truncated.

**If the paste looks partial** (a table cut mid-row, a section header with no body, a referenced ID
that never appears), say so and ask for the rest. A silently truncated paste produces silently
missing tests.

### Local repo path

`Read` the file. Care requirements commonly live in:

- `Project-Galen/Project-Docs/Requirements/`
- `Project-Galen/Phase-1/`, `Phase-2/`, `Phase-3/`
- `Templates/Example-PRDs/`

Local copies of Confluence pages are **exports**, and may be stale. Check the `> **Source:**` block
for a captured date. If it is old, tell Danny and offer to fetch the live page.

### Confluence

Use the Atlassian MCP page-fetch tool with the page ID from the URL. The retrieval hard stop applies.

---

## Figma mocks

Two paths, both acceptable:

| Path | When | How |
| --- | --- | --- |
| **Pasted screenshots** | Default. Cheapest and most reliable | Danny attaches images. Read them directly |
| **Figma MCP** | Danny provides a file or node link | Use the Figma MCP screenshot and design-context tools |

Extract only what generates tests:

- Labels, headers, and button copy as they will appear
- Section organization and ordering
- Empty, loading, and error state treatments
- Focus, hover, and disabled treatments
- Indicator systems (provenance, severity, confidence)

Do not extract pixel spacing into test criteria unless the requirements make spacing a requirement.

**A component's states are not automatically in scope.** Design files carry speculative explorations
for future work alongside the current spec, and a component's variant list will not tell you which is
which. Confirm at the Step 1b model interview which states are spec for this launch before writing a
criterion for or against any of them. *Observed 2026-09-18:* the Sprout Composer component carried
four states; one (QualityCheck) was a future-feature exploration, and treating the variant list as
canonical produced both a wrong state model and a scope-verification test against a state nobody had
proposed shipping.

**Copy caveat.** Mocks evolve during implementation. Add this note to any output that cites mock copy:

> **Note on UI copy:** exact copy reflects the mocks at time of writing. Verify against the current
> mocks before sign-off, as designs may evolve during implementation.

---

## Prototype code

### The size constraint

Care prototypes in `your-org/emr-designs` are self-contained single-file HTML applications. One
observed file is 278,289 characters, roughly 70,000 tokens. **Never read a prototype file into the
main thread.**

### Required approach

Delegate to a subagent. See `prototype-analysis-subagent.md` for the full prompt. The subagent
fetches and reads the prototype, then returns a compact state inventory. The main thread receives the
inventory, never the source.

**The main thread does not fetch prototype content.** Pass the location to the subagent and let it
fetch. Directory listings are safe from the main thread, because they return sizes without content.

### Locating the prototype

| Location | How |
| --- | --- |
| GitHub repo | List the directory from the main thread to confirm the path and size. Pass owner, repo, and path to the subagent. `your-org/emr-designs` holds Galen prototypes under `projects/` |
| Local path | `Glob` to confirm it exists, check size, then pass the path to the subagent |
| Deployed only | No code access. Use the deployed-prototype path below instead |

Files under roughly 40,000 characters can be read directly. Above that, always use the subagent.

### What prototype code is good for

Enumerating states exhaustively. Conditional visibility attributes, disabled states, event handlers,
and branch functions are all countable, which means you can find the empty, loading, error, and
variant states that requirements usually leave implicit.

### What prototype code is not

Not a requirement. Specifically:

- **A present control is not a confirmed requirement.** A prototype carries placeholder UI, controls
  awaiting redesign, and affordances that exist only to make a demo navigable. Before writing a
  criterion that depends on what a control is *for*, confirm its purpose at the Step 1b model
  interview. When it is unconfirmed, describe the behavior and leave the control unnamed.
  *Observed 2026-09-18:* the Galen2 prototype's dropdown above the composer was read as a selector for
  AI message types and six criteria were built on it. It was the snippet picker, placeholder UI the
  designer had not yet replaced. No downstream gate caught it, because the document was internally
  consistent and only the model was wrong.
- **Fixture data is not a requirement.** Hardcoded patient names, doses, dates, and vitals in a
  prototype are placeholders. Never write a test asserting a fixture value.
- **A missing state is not a non-requirement.** A prototype that lacks an error state does not mean
  the feature has no error state. That is a gap to flag, not an absence to encode.
- **Prototype copy is provisional.** Treat it like mock copy.

---

## Deployed prototype

Optional. Use when the prototype is deployed and you need evidence the code read cannot give you:
rendered state after interaction, responsive breakpoints, console errors, or the real accessibility tree.

Use the Chrome DevTools MCP: list pages, navigate, snapshot, screenshot, read console messages.

**Before relying on it,** confirm the browser is reachable and the page loads. If it does not, the
retrieval hard stop applies. Do not describe states you did not observe.

**Cost note.** Driving a browser is slower than reading code. Use it for the states that matter, not
for a full sweep. If prototype code is available, read the code first and use the browser to confirm
the handful of states you could not resolve.

---

## Confirming intake before generation

Restate to Danny before generating:

| Item | Confirm |
| --- | --- |
| Mode | Comprehensive or UAT |
| Requirements received | Which IDs, which sections, how obtained |
| Implementation sources | Which were retrieved, which failed, which Danny declined |
| Target path | Where the document will be written |
| Participants | Comprehensive: product lead, engineering leads, design lead, epic, and a clinical lead for a clinical launch. UAT: author, design reviewer, clinical reviewer, teams. Placeholder anything unknown |
| Existing document | Whether this is a new document or a revision of an existing one |

If this is a revision, `Read` the existing document first. If it has been shared with Design and Eng,
preserve its test numbering, add new tests as sub-IDs, apply revision markers, and never renumber or
reuse a number. If not, edit in place and renumber freely.
