# Layout engine, visual QA, and runtime notes

## How the renderer lays out a slide (720 x 405 pt canvas)

| Region | Y range (pt) | Notes |
|---|---|---|
| Title | 6 to 36 | 22pt bold. |
| Persona header | 40 to 84 | Theme LIGHT2 fill. One slot per persona, each with an emoji avatar circle, a bold name, and an 8pt description. |
| Stage columns | 88 to 318 (368 with no bottom band) | Pastel fills cycle. The 18pt header reads "N  Name". |
| Step text | below the header | Each column is sized to its own text (30 to 72pt). Its callouts may start 6pt below it. |
| Curve band | shortest column's step bottom + 8 to column bottom minus 6 | Sentiment 1 to 5 maps to one shared, evenly spaced scale. If the curve would touch any column's step text, the whole scale shifts down until it clears. |
| Bottom band | 320 to 371 | "What it costs" stats on the left (labels may extend into the next slot), "What we built" on the right. |
| Fine print | 372 to 389 | 6.5pt, at most 2 lines, numbered and hyperlinked. |
| Footer | 390 | From make-deck's `_add_footer_reqs`. |

### The curve
- It's drawn from Slides `CURVED_CONNECTOR_3` segments. Each segment is two cubic curves with **horizontal tangents at both endpoints**. A point placed mid-descent would make a flat "step," so the renderer keeps only the endpoints, peaks, troughs, and plateaus (`keep_extrema`).
- Rising segments are drawn with `scaleY = -1`, a vertical flip, so they run from bottom-left to top-right.
- `curve_samples` reproduces the connector's exact bezier path, so callout placement measures the real curve, not a straight-line guess.

### Callout placement
1. For each column, find the curve's min and max y across the callout's width. Callouts go **above** the curve (stacking down from that column's step text) or **below** it (stacking down from curve max + 8pt), whichever side has more room. Use `position` to force a side.
2. **Tucking.** If neither side fits, a callout may be placed over the curve, with the line passing behind its white box. This is allowed only when the callout is **alone in its column**, and only **once per slide**. In any other case the render fails and tells you to move a callout to notes or shorten copy. Two boxes plus a steep curve in one column always reads as clutter: the line weaves out between them.
3. **Warnings, which visual QA must resolve:**
   - more than 40pt of empty space under a column's step text
   - any callout more than 1.5× the median callout height
   - the one tucked callout

### Avatars
Use one single-codepoint emoji (👩 🧑 🩺 🎧 💻). The validator rejects joined sequences (ZWJ, e.g. 👨‍⚕️) and skin-tone modifiers, because Slides splits them into separate glyphs that spill out of the circle onto the persona text.

### Text estimates
The renderer estimates wrapping from character counts at Poppins widths, with about 7pt insets on each side. Estimates run slightly conservative. When a validator error looks borderline, shorten the copy before you loosen a limit.

## Capturing the slide with DevTools (Step 6a)

The **QA subagent captures the slide itself**, so the grader sees the slide first-hand. DevTools can only save screenshot files inside the workspace roots (`/tmp` and the scratchpad are refused), and a capture saved into a synced repo would get committed. So the subagent takes the screenshot inline instead of saving a file.

1. `new_page` with `(internal link)>/embed?slide=id.<slide_id>`. Using `/embed` shows the slide without editor chrome.
2. If the page URL is `accounts.google.com`, stop. Ask the user to sign in once in the DevTools Chrome window (the session persists), then retry. Never type credentials. If the user declines, fall back to asking for their own screenshot.
3. Optional: `resize_page` to 1920 x 1080. It errors when the window is maximized; skip it then, since a maximized window already captures at about 3400px wide.
4. `take_screenshot` with no `filePath`. Don't `wait_for` text: Slides draws text as graphics, so the wait times out. Allow about 3 seconds after load instead.
5. If a screenshot times out, a heavy tab (e.g. a large deck opened earlier) is stalling the browser. `close_page` the other tabs, then retry.

If the DevTools browser can't start ("browser is already running for ... chrome-profile"), a stale automation Chrome holds the profile. Ask the user before killing it.

**Emoji rendering rule, learned from a DevTools capture:** Slides silently skips drawing a glyph that doesn't fit inside its text box after the roughly 7pt insets. Emoji in 32pt circles came out blank in the real browser, not only in thumbnails. The renderer therefore puts each emoji in its own box, at least 2× the glyph size plus 15pt wide, centered over a text-free shape.

## Visual QA rubric (journey-specific, on top of make-deck's qa-rubric.md)

The quality bar is `examples/patient-provider-journey-reference.png`, a presenter's hand-finished map. Grade the candidate for spacing, density, and polish against it. Two things in the reference are not the bar: its content (it predates the content rules), and its blank emoji (it's an API thumbnail).

**FAIL**
- Any text clipped, cut off, overflowing its box, or overlapped by another element. That includes:
  - an avatar glyph spilling onto the persona text
  - cost labels running into the fine print
  - an exchange caption hidden behind a bubble
- A callout covering stage-line text.
- A visible curve segment poking out between two stacked boxes, or the curve passing behind more than one callout on the slide.
- The curve hidden at its lowest or highest point, so the emotional shape no longer reads.
- More than about 40pt of dead space between a column's step text and its first callout or the curve, when other columns are full.
- Fine print wrapping to 3 lines, or touching the footer.
- An em dash anywhere.

**WARN**
- A callout box more than 1.5× the height of its siblings, or callouts with visibly uneven padding.
- Any text smaller than 6.5pt, other than the fine print.
- Speech-bubble tails pointing at something that confuses the reading.

**Exempt** (the only exemptions)
- The fine print's intentionally small size.
- A claim with no superscript, when the spec marks it `source: null` and the user approved that.

**Unverified (API thumbnail capture only)**
- Emoji: avatars, 🙂 and 🙁. The thumbnail renderer drops or misplaces them. List them as unverified and tell the user; don't pass them.

**Reject these QA "fixes"**
- Rewording a quote to fit.
- Reusing one source's footnote for a different claim.
- Changing a stage's sentiment just to make room.

## Runtime notes

| Symptom | Cause | Fix |
|---|---|---|
| `No module named 'googleapiclient'` | Wrong Python | Use the interpreter that has the Google libs (macOS: `/usr/bin/python3`). |
| Doctor says OAuth JSON is missing, but it exists | The sandbox blocks reads of `~/.config/gcloud` | Run outside the sandbox. The user approves a permission prompt. |
| `PermissionError` writing a skill file from Bash | The sandbox blocks `.claude/skills/` writes | Use the Write or Edit tools. Keep run files in `$TMPDIR` or the scratchpad. |
| `TypeError: unsupported operand type(s) for \|` | `str \| None` annotations on Python 3.9 | Don't use that syntax in the scripts. |
| A new deck appears on every iteration | Using `mode: new` while iterating | Iterate with `mode: append`, the same `presentation_id`, and `replace_slide_id`. |
| Object ID collision | Re-running a script with a fixed ID scheme | The renderer prefixes every object ID with a per-run token. |
| The default slide deletes your new slide | `delete_default_first_slide` deletes by position | The renderer deletes it before inserting. Keep that order. |
| Thumbnails overwrite another deck's | The default `/tmp/slides-eval` is shared | Pass an `out_dir` to `render_thumbnails.py`. |
| Hyperlinks in the wrong place | UTF-16 offsets (emoji count as 2) | The renderer computes UTF-16 offsets. Verify by reading the slide back with `presentations.get`. |
