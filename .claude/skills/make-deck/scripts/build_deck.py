"""Build a complete Google Slides deck from a JSON outline.

Usage:
  python3 build_deck.py outline.json
  python3 build_deck.py outline.json --no-save-state

Outline schema:
{
  "title": "Deck title (required)",
  "parent_folder_id": "drive-folder-id-or-null",
  "slides": [
    {"template": "cover", "title": "...", "subtitle": "optional", "notes": "optional speaker notes"},
    {"template": "exec_summary", "title": "...", "lead": "...",
     "principles_header": "Launch principles", "cards": ["...", "...", "..."], "notes": "..."},
    {"template": "section_divider", "title": "...", "subtitle": "optional"},
    {"template": "bullets", "title": "...", "lead": "optional",
     "bullets": ["...", "..."]},
    {"template": "two_column", "title": "...",
     "left_header": "...", "left_bullets": ["..."],
     "right_header": "...", "right_bullets": ["..."]},
    {"template": "do_dont", "title": "...",
     "dos": ["..."], "donts": ["..."]}
  ]
}

Every slide may include an optional `notes` field (string) for speaker notes.

Why this exists: every invocation of make-deck would otherwise write the same
~30 lines of Python. Per skill-creator guidance ("bundle repeated work as
scripts"), the skill calls this CLI with one JSON file instead.

Side effects:
  - Creates the deck in Google Slides
  - Saves outline + deck URL to ~/.claude/skills/make-deck/outputs/YYYY-MM-DD-<slug>.json
    so future runs can reference prior decks (similar to flash-briefing's
    stateful-output pattern).
  - Prints the deck URL to stdout (last line) so the caller can grab it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

# Make slides_client importable whether called from anywhere
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from slides_client import SlidesClient  # noqa: E402

OUTPUTS_DIR = Path.home() / ".claude" / "skills" / "make-deck" / "outputs"

TEMPLATE_DISPATCH = {
    "cover": lambda c, pid, s: c.hh_cover_slide(
        pid, s["title"], s.get("subtitle"), notes=s.get("notes")
    ),
    "exec_summary": lambda c, pid, s: c.hh_executive_summary(
        pid,
        s["title"],
        s["lead"],
        s.get("principles_header", "Launch principles"),
        s["cards"],
        notes=s.get("notes"),
    ),
    "section_divider": lambda c, pid, s: c.hh_section_divider(
        pid, s["title"], s.get("subtitle"), notes=s.get("notes")
    ),
    "bullets": lambda c, pid, s: c.hh_bullets_slide(
        pid, s["title"], s["bullets"], lead=s.get("lead"), notes=s.get("notes")
    ),
    "two_column": lambda c, pid, s: c.hh_two_column_slide(
        pid,
        s["title"],
        s["left_header"],
        s["left_bullets"],
        s["right_header"],
        s["right_bullets"],
        notes=s.get("notes"),
    ),
    "do_dont": lambda c, pid, s: c.hh_do_dont_slide(
        pid, s["title"], s["dos"], s["donts"], notes=s.get("notes")
    ),
    "flow_steps": lambda c, pid, s: c.hh_flow_steps_slide(
        pid, s["title"], s["steps"], lead=s.get("lead"), notes=s.get("notes")
    ),
    "three_card": lambda c, pid, s: c.hh_three_card_slide(
        pid, s["title"], s["cards"], lead=s.get("lead"), notes=s.get("notes")
    ),
    "key_stat": lambda c, pid, s: c.hh_key_stat_slide(
        pid, s["stat"], s["label"], caption=s.get("caption"), title=s.get("title"),
        notes=s.get("notes"),
    ),
    "agenda": lambda c, pid, s: c.hh_agenda_slide(
        pid, s["sections"], title=s.get("title", "Agenda"), notes=s.get("notes")
    ),
    "moving_blueprint": lambda c, pid, s: c.hh_moving_blueprint_slide(
        pid, s["sections"], s["current_index"], subtitle=s.get("subtitle"),
        notes=s.get("notes"),
    ),
    "big_idea": lambda c, pid, s: c.hh_big_idea_slide(
        pid, s["statement"], attribution=s.get("attribution"), notes=s.get("notes")
    ),
    "pull_quote": lambda c, pid, s: c.hh_pull_quote_slide(
        pid, s["quote"], s["author"], role=s.get("role"), notes=s.get("notes")
    ),
    "comparison_2x2": lambda c, pid, s: c.hh_comparison_2x2_slide(
        pid, s["title"], s["x_left"], s["x_right"],
        s["y_bottom"], s["y_top"], s["quadrants"],
        notes=s.get("notes"),
    ),
    "metric_grid": lambda c, pid, s: c.hh_metric_grid_slide(
        pid, s["title"], s["metrics"], lead=s.get("lead"), notes=s.get("notes")
    ),
}


def slugify(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return s[:max_len] or "untitled"


def validate_outline(outline: dict) -> list[str]:
    """Return list of validation errors. Empty list = valid."""
    errors = []
    if "title" not in outline or not outline["title"]:
        errors.append("outline.title is required")
    slides = outline.get("slides") or []
    if not slides:
        errors.append("outline.slides must contain at least one slide")
    for i, s in enumerate(slides):
        tpl = s.get("template")
        if tpl not in TEMPLATE_DISPATCH:
            errors.append(
                f"slides[{i}].template = {tpl!r} is not one of "
                f"{list(TEMPLATE_DISPATCH.keys())}"
            )
            continue
        # `notes` is an optional string with no constraints (length-wise we
        # let users put as much as they want; the Slides API will accept it).
        if "notes" in s and s.get("notes") is not None and not isinstance(s["notes"], str):
            errors.append(f"slides[{i}].notes must be a string when provided")
        # Templates where the "title" field is not required at the top level
        # (because content other than a title carries the headline):
        #   key_stat       -> stat + label IS the headline
        #   big_idea       -> statement IS the headline
        #   pull_quote     -> quote IS the headline
        #   moving_blueprint -> current section name (from sections[current_index]) is the title
        #   agenda         -> uses a default ("Agenda") if title not provided
        TEMPLATES_WITHOUT_REQUIRED_TITLE = {
            "key_stat", "big_idea", "pull_quote", "moving_blueprint", "agenda"
        }
        if tpl not in TEMPLATES_WITHOUT_REQUIRED_TITLE and not s.get("title"):
            errors.append(f"slides[{i}].title is required")
        if tpl == "exec_summary":
            for k in ("lead", "cards"):
                if not s.get(k):
                    errors.append(f"slides[{i}].{k} required for exec_summary")
            if len(s.get("cards", [])) > 3:
                errors.append(
                    f"slides[{i}].cards has {len(s['cards'])} items; max is 3"
                )
        if tpl == "bullets":
            if not s.get("bullets"):
                errors.append(f"slides[{i}].bullets required for bullets template")
            if len(s.get("bullets", [])) > 6:
                errors.append(
                    f"slides[{i}].bullets has {len(s['bullets'])} items; max is 6 "
                    "per hims & hers style guide. Split across multiple slides."
                )
        if tpl == "two_column":
            for k in ("left_header", "left_bullets", "right_header", "right_bullets"):
                if not s.get(k):
                    errors.append(f"slides[{i}].{k} required for two_column")
        if tpl == "do_dont":
            for k in ("dos", "donts"):
                if not s.get(k):
                    errors.append(f"slides[{i}].{k} required for do_dont")
        if tpl == "flow_steps":
            if not s.get("steps"):
                errors.append(f"slides[{i}].steps required for flow_steps")
            if len(s.get("steps", [])) > 5:
                errors.append(
                    f"slides[{i}].steps has {len(s['steps'])} items; max is 5 "
                    "(visual stepper gets unreadable beyond that)"
                )
            if len(s.get("steps", [])) < 3:
                errors.append(
                    f"slides[{i}].steps has {len(s.get('steps', []))} items; "
                    "use bullets or two_column for <3 items"
                )
        if tpl == "three_card":
            if not s.get("cards"):
                errors.append(f"slides[{i}].cards required for three_card")
            if len(s.get("cards", [])) > 4:
                errors.append(
                    f"slides[{i}].cards has {len(s['cards'])} items; max is 4"
                )
            for j, card in enumerate(s.get("cards", [])):
                if not card.get("header") or not card.get("body"):
                    errors.append(
                        f"slides[{i}].cards[{j}] needs both 'header' and 'body'"
                    )
        if tpl == "key_stat":
            for k in ("stat", "label"):
                if not s.get(k):
                    errors.append(f"slides[{i}].{k} required for key_stat")
            # title is optional for key_stat (often the stat IS the title)
            # so we don't enforce title here even though the generic check above did
        if tpl == "agenda":
            if not s.get("sections"):
                errors.append(f"slides[{i}].sections required for agenda")
            if len(s.get("sections", [])) > 6:
                errors.append(
                    f"slides[{i}].sections has {len(s['sections'])} items; max is 6 "
                    "(agenda should be section names, not every slide)"
                )
            if len(s.get("sections", [])) < 3:
                errors.append(
                    f"slides[{i}].sections has {len(s.get('sections', []))} items; "
                    "an agenda with <3 sections doesn't add value - skip the slide"
                )
        if tpl == "moving_blueprint":
            if not s.get("sections"):
                errors.append(f"slides[{i}].sections required for moving_blueprint")
            if "current_index" not in s:
                errors.append(f"slides[{i}].current_index required for moving_blueprint")
            sections = s.get("sections", [])
            idx = s.get("current_index", -1)
            if sections and not (0 <= idx < len(sections)):
                errors.append(
                    f"slides[{i}].current_index={idx} out of range for "
                    f"{len(sections)} sections"
                )
            if len(sections) > 6:
                errors.append(
                    f"slides[{i}].sections has {len(sections)} items; max 6 in blueprint"
                )
        if tpl == "big_idea":
            if not s.get("statement"):
                errors.append(f"slides[{i}].statement required for big_idea")
            word_count = len((s.get("statement", "") or "").split())
            if word_count > 15:
                errors.append(
                    f"slides[{i}].statement has {word_count} words; max is 15 "
                    "(less words is the whole point of big_idea)"
                )
        if tpl == "pull_quote":
            for k in ("quote", "author"):
                if not s.get(k):
                    errors.append(f"slides[{i}].{k} required for pull_quote")
            word_count = len((s.get("quote", "") or "").split())
            if word_count > 30:
                errors.append(
                    f"slides[{i}].quote has {word_count} words; max is 30 "
                    "(longer quotes belong in body text, not on slides)"
                )
        if tpl == "comparison_2x2":
            for k in ("x_left", "x_right", "y_bottom", "y_top", "quadrants"):
                if not s.get(k):
                    errors.append(f"slides[{i}].{k} required for comparison_2x2")
            if len(s.get("quadrants", [])) != 4:
                errors.append(
                    f"slides[{i}].quadrants must have exactly 4 entries "
                    f"(got {len(s.get('quadrants', []))}; order: TL, TR, BL, BR)"
                )
        if tpl == "metric_grid":
            if not s.get("metrics"):
                errors.append(f"slides[{i}].metrics required for metric_grid")
            n_metrics = len(s.get("metrics", []))
            if n_metrics < 2:
                errors.append(
                    f"slides[{i}].metrics has {n_metrics}; use key_stat for a single number"
                )
            if n_metrics > 6:
                errors.append(
                    f"slides[{i}].metrics has {n_metrics}; max is 6 (more becomes unreadable)"
                )
            for j, m in enumerate(s.get("metrics", [])):
                if not m.get("value") or not m.get("label"):
                    errors.append(
                        f"slides[{i}].metrics[{j}] needs both 'value' and 'label'"
                    )
    return errors


def build_deck(outline: dict, save_state: bool = True) -> dict:
    errors = validate_outline(outline)
    if errors:
        raise ValueError("Outline validation failed:\n  " + "\n  ".join(errors))

    c = SlidesClient()
    pid = c.create_deck(
        outline["title"], parent_folder_id=outline.get("parent_folder_id")
    )
    c.delete_default_first_slide(pid)

    slide_ids = []
    for s in outline["slides"]:
        slide_id = TEMPLATE_DISPATCH[s["template"]](c, pid, s)
        slide_ids.append(slide_id)

    result = {
        "presentation_id": pid,
        "url": c.url(pid),
        "title": outline["title"],
        "slide_count": len(slide_ids),
        "template_mix": {
            tpl: sum(1 for s in outline["slides"] if s["template"] == tpl)
            for tpl in TEMPLATE_DISPATCH
            if any(s["template"] == tpl for s in outline["slides"])
        },
        "outline": outline,
    }

    if save_state:
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        slug = slugify(outline["title"])
        out_path = OUTPUTS_DIR / f"{date.today().isoformat()}-{slug}.json"
        # If a deck with this slug already ran today, append a counter
        counter = 2
        while out_path.exists():
            out_path = OUTPUTS_DIR / f"{date.today().isoformat()}-{slug}-{counter}.json"
            counter += 1
        out_path.write_text(json.dumps(result, indent=2))
        result["state_path"] = str(out_path)

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a Google Slides deck from a JSON outline.")
    ap.add_argument("outline", help="Path to outline JSON file (or '-' for stdin)")
    ap.add_argument(
        "--no-save-state",
        action="store_true",
        help="Skip writing outline + URL to outputs/ directory",
    )
    args = ap.parse_args()

    if args.outline == "-":
        outline = json.load(sys.stdin)
    else:
        outline = json.loads(Path(args.outline).read_text())

    try:
        result = build_deck(outline, save_state=not args.no_save_state)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(
        f"Built {result['slide_count']} slides: "
        + ", ".join(f"{k}={v}" for k, v in result["template_mix"].items()),
        file=sys.stderr,
    )
    if "state_path" in result:
        print(f"State saved: {result['state_path']}", file=sys.stderr)
    print(result["url"])  # last line of stdout = the URL
    return 0


if __name__ == "__main__":
    sys.exit(main())
