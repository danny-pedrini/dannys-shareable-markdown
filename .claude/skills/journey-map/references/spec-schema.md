# Journey spec schema

`scripts/render_journey.py` takes one JSON spec and renders one slide. See `examples/patient-provider-journey.json` for a complete spec.

Run `--dry-run` first. It validates every field below, checks text against its length limit, computes layout, numbers the footnotes, and lists callouts it had to tuck over the curve. It makes no API calls and doesn't need Google libraries.

## Top level

| Field | Required | Type | Notes |
|---|---|---|---|
| `destination` | No | object | See below. Defaults to a new deck. |
| `title` | Yes | string ≤ 60 | Plain label when the slide is inserted into a larger deck. |
| `personas` | Yes | array of 1 or 2 | The first persona sits on the left of the header. |
| `curve` | Yes | object | Whose experience the line tracks. |
| `stages` | Yes | array of 3 to 6 | Rendered as columns, left to right. |
| `bottom_band` | No | object | Omit it to give the columns more height. |
| `sources` | If anything is cited | object of key → source | Keys are referenced by `source` fields. |
| `notes` | Yes | string | Speaker-notes talk track. It can't be empty. |

## destination

| Field | Type | Notes |
|---|---|---|
| `mode` | `"new"` or `"append"` | `new` creates a standalone deck. `append` inserts into `presentation_id`. |
| `deck_title` | string | For `new`. |
| `parent_folder_id` | string | For `new`. A Drive folder ID. |
| `presentation_id` | string | Required for `append`. |
| `insert_index` | int | For `append`; 0-based. Defaults to the end. |
| `replace_slide_id` | string | For `append`. Deletes this slide first; use it to re-render in place. |

## personas[]

| Field | Limit | Notes |
|---|---|---|
| `key` | | ID used by `curve.persona` and `lines[].persona`. |
| `short` | | Bold label before each line ("Meg", "Provider"). |
| `name` | 45 | e.g. "Meg, Hers WL patient (illustrative)". |
| `description` | 130 | Scenario or forces, one sentence. |
| `avatar` | | One emoji. |
| `illustrative` | | `true` for a made-up persona. The validator then requires "(illustrative)" in `name`. Omit it for a generic role persona ("Meg's provider"). |
| `color` | | Palette key or hex for the avatar circle. Defaults: `sage_accent` for the first persona, `blue_mid` for the second. |

## curve

`{"persona": "<key>", "label": "Meg's experience", "markers": true}`. `markers` draws 🙂 and 🙁 at the top and bottom of the curve band.

## stages[]

| Field | Limit | Notes |
|---|---|---|
| `name` | 18 | Rendered as "1  Submit". |
| `sentiment` | int 1 to 5 | 1 = best (high on the slide), 5 = worst. The curve bends only at peaks and troughs, so a stage mid-descent doesn't make a flat step. |
| `lines` | 1 or 2, ≤ 95 chars each | `{"persona": "<key>", "text": "..."}`, ordered by who acts first. |
| `callouts` | 0 to 2 | See types below. Optional `"position": "above"` or `"below"` forces a side. |

### Callout types

| type | Fields | Renders as |
|---|---|---|
| `stat` | `text` ≤ 45, `detail` ≤ 60 (optional), `source` | Rounded box: bold accent headline, small detail line. |
| `bullets` | `items`: 1 to 3 of `{text ≤ 60, source}` | Rounded box with bullets. `**bold**` markup emphasizes a number or word. |
| `quote` | `text` ≤ 120 (verbatim; the renderer adds curly quotes), `attribution` ≤ 45 (role), `source` | Speech bubble. |
| `research` | `text` ≤ 110 (paraphrase), `citation` ≤ 120 ("Author, Journal, Year"), `source` | Rounded box with a small citation line. |
| `exchange` | `caption` ≤ 40, `source`, `turns`: 2 or 3 of `{speaker, text ≤ 110}` | Caption plus one bubble per turn, alternating styles. |

`source` is a key from `sources`, or `null` for a claim that is deliberately uncited on the slide.

## bottom_band

```json
{"left":  {"header": "What it costs", "subheader": "baseline LLM judge pass rates",
           "subheader_source": "scorecard",
           "stats": [{"value": "56%", "label": "Doctor Relationship\n(knows my history)", "source": null}]},
 "right": {"header": "What we built",
           "lines": [{"lead": "Complete the Chart + EMR 2.0:", "text": "Ivy fills chart gaps before chart review", "source": null}]}}
```

- `left.stats` holds 1 to 4 items. `value` is at most 8 characters. `label` is at most 45 characters and must fit on 2 lines (use `\n` to control the break).
- `right.lines` should fit on one line each at full width. Each line is at most 110 characters, and the validator measures their combined height.
- Either side may be omitted.

## sources

```json
"sources": {"prerx": {"label": "Pre-Rx funnel monitoring", "url": "https://..."}}
```

Every source needs a `label` and a `url`. Keep labels short: all labels together must fit 2 lines of 6.5pt fine print.

## Validation and layout errors, and how to fix them

| Message | Fix (in this order) |
|---|---|
| `N chars, limit L` | Tighten the copy, and move the rest to notes. Quotes: cut with "..." only. |
| `contains an em dash` | Use a comma, colon, period, or parentheses. |
| `lines need Npt of step text` | Shorten the stage lines. |
| `callouts[j] needs Npt and the column has no free space` | Shorten it, or move it to notes. Adjusting sentiment changes the story, so ask the user. |
| `has 2 callouts but callouts[j] can't clear the curve` | Move one callout to notes (ask the user which), or shorten both. |
| `N callouts would sit over the curve; the limit is 1` | Move callouts to notes or shorten them. If a stage's sentiment looks wrong, ask the user. |
| `avatar: use one single-codepoint emoji` | Replace a joined or skin-tone emoji (👨🏽‍⚕️) with a single one (🩺). |
| `WARN ... empty space under the step text` | Add a callout to that column, move one there, or accept it, since visual QA judges it against the reference. |
| `WARN ... x the median callout height` | Tighten that callout's copy. |
| `label wraps past 2 lines` | Shorten it, or set the break with `\n`. |
| `fine print wraps past 2 lines` | Shorten the source labels. |
| `WARN ... sits over the curve` | The one allowed tuck. Visual QA confirms the curve still reads. |
| `WARN sources defined but never cited` | Remove the unused sources, or cite them. |
