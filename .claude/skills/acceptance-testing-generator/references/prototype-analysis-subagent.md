# Prototype Analysis Subagent

Reference for the `acceptance-testing-generator` skill. Delegating prototype code analysis so a
large prototype file never enters the main thread.

---

## Why a subagent

Care prototypes are single-file HTML applications. One observed file in `your-org/emr-designs` is
278,289 characters, roughly 70,000 tokens. Reading it in the main thread would consume a large share
of context before the first test is written, and most of that content is styling and fixture data
that generates no tests.

The subagent reads the file. The main thread receives only the state inventory.

---

## Do not fetch the file yourself

**The subagent fetches its own content.** Never call a content-fetch tool on a prototype file from
the main thread. A fetch that returns inline rather than writing to disk would put the whole file in
this context, which is the exact failure this pattern exists to prevent.

What the main thread passes to the subagent:

| Case | Pass |
| --- | --- |
| Local path | The absolute path |
| GitHub repo | Owner, repo, and file path. The subagent fetches |
| Deployed only | The URL, and use the Chrome DevTools path instead |

**Sizing is safe to do from the main thread.** A directory listing returns names, types, and sizes
without content. Use it to decide whether a file needs the subagent at all:

- Under roughly 40,000 characters: reading it directly is acceptable
- Above that: subagent, always

**Fallback if the subagent's fetch returns too much to handle:** download the raw file to the
scratchpad with `curl` against the raw content URL, then read it in bounded chunks with `grep -n`
plus `Read` using `offset` and `limit`.

If the fetch fails or returns partial content, the retrieval hard stop applies. The subagent reports
the failure, and the main thread stops and alerts Danny. A subagent must never substitute a guess for
content it could not read.

---

## Subagent prompt

Use the Agent tool with:

**Description:** `"Prototype state inventory"`

**Prompt:**

````
You are analyzing a front-end prototype to build a state inventory for acceptance test generation.
You are NOT writing tests. You are producing a structured inventory another agent will use.

## File

`[absolute local path, OR: GitHub owner + repo + path for you to fetch yourself]`

If given a GitHub location, fetch it yourself. If the fetch returns more content than you can hold,
download the raw file to the scratchpad with `curl` and work from disk. If the fetch fails or returns
partial content, stop and report the failure. Never infer prototype content you could not read.

## Feature context

`[one paragraph: what this prototype demonstrates, and which requirement IDs it relates to]`

## Step 1: Structural survey (do this before reading any content)

Run grep-based counts to map the file. Do not read the file top to bottom.

```bash
F="[path]"
wc -c "$F"
# State-bearing attributes
for p in 'hidden' 'disabled' 'aria-' 'role=' 'data-state' 'data-' 'onclick' 'addEventListener' 'function '; do
  printf "%-18s %s\n" "$p" "$(grep -o "$p" "$F" | wc -l | tr -d ' ')"
done
# Element identifiers
grep -oE 'id=\\?"[a-zA-Z0-9_-]{2,40}\\?"' "$F" | sort -u
# Function names
grep -oE 'function [a-zA-Z0-9_]+' "$F" | sort -u
# Modal, scrim, banner, toast, empty, error indicators
grep -oiE 'id=\\?"[a-zA-Z0-9_-]*(modal|scrim|banner|toast|empty|error|loading|spinner|warning|confirm)[a-zA-Z0-9_-]*\\?"' "$F" | sort -u
```

## Step 2: Targeted reads

Using the survey, read ONLY the slices that matter:

- Blocks around each `hidden` attribute. These are conditional states
- Each `disabled` occurrence and what re-enables it
- Function bodies for handlers that change visible state
- Any block containing user-visible copy for empty, error, loading, or confirmation states

Use `grep -n` to find line numbers, then `Read` with `offset` and `limit` to pull a narrow window.
Never read more than 400 lines in one call. If a line is extremely long (minified or inline),
use `grep -o` with a pattern rather than reading the line.

Skip entirely: CSS blocks, SVG path data, base64 assets, font declarations, color definitions.

## Step 3: Classify fixture data

Identify hardcoded sample values: patient names, doses, dates, vitals, medication names, message
text. List them separately as FIXTURES. These are placeholders and must never become test criteria.

## Step 4: Return the inventory

Return exactly this structure. No preamble, no summary of your process.

### Screens and views
| ID or name | What it shows | How it is reached |
| --- | --- | --- |

### Conditional states
| State | Trigger | Visible result | Element |
| --- | --- | --- | --- |
(One row per `hidden` toggle, disabled state, or branch that changes what the user sees.
Include empty, loading, error, success, and variant states.)

### Interactive elements
| Element | Action | Result | Guard |
| --- | --- | --- | --- |
(Guard = any condition that blocks the action, e.g. disabled until X.)

### Modals and overlays
| ID | Purpose *(inferred from code, UNCONFIRMED)* | Open trigger | Close paths | Required fields |
| --- | --- | --- | --- | --- |
(Purpose is your reading of what the element is for. It is a hypothesis for the Step 1b model
interview, never a requirement. Say "appears to" rather than asserting, and flag anything whose
purpose you cannot determine from the code rather than guessing at it.)

### User-visible copy
| Context | Exact string |
| --- | --- |
(Only copy that a test would assert: error messages, empty-state text, confirmation prompts,
banner text, button labels. Not body prose.)

### Accessibility signals
| Element | Attribute | Value |
| --- | --- | --- |
(aria-*, role=, tabindex, focus management. Note anything interactive that has none.)

### FIXTURES (never test against these)
| Value | Where | Type |
| --- | --- | --- |

### States absent from the prototype
List states a production feature would need that this prototype does not implement. Be specific.
Example: "No error state for a failed chart write. The write path assumes success."

### Coverage note
State what portion of the file you examined and what you skipped. If you could not read some part,
say which part and why. Do not claim completeness you did not achieve.
````

---

## Handling the returned inventory

**Nothing in this inventory becomes a test until Step 1b confirms it.** The inventory says what the
prototype *does*; only the model interview says what the product *should* do. In the 2026-09-18 run a
dropdown inventoried with the purpose "select AI message type" was the snippet picker, and six
criteria were built on the inventory's reading of it. Route every Purpose value and every
state-in-context reading through Step 1b question 5 first.

| Inventory section | Feeds |
| --- | --- |
| Screens and views | Navigation and access tests |
| Conditional states | Empty, loading, error state tests. Often the highest-value tests, because requirements leave these implicit |
| Interactive elements | User action tests, and guard-state tests |
| Modals and overlays | Decision flow tests. Consolidate close paths into one test |
| User-visible copy | Design verification tests, and error handling tests |
| Accessibility signals | Accessibility tests. An interactive element with no aria or focus handling is a gap to flag |
| FIXTURES | Nothing. Never write a test asserting a fixture value |
| States absent | The Potential requirement gaps working list, not tests |

**If the subagent reports incomplete coverage,** treat it as a partial retrieval. Tell Danny which
portion was not read before generating, so he can decide whether to proceed.
