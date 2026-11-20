"""Apply edits to an existing Google Slides deck from a JSON edit plan.

Usage:
  python3 edit_deck.py edit_plan.json
  python3 edit_deck.py -                 # read plan from stdin

Edit-plan schema:
{
  "presentation_id": "1ABC...",
  "edits": [
    {"op": "delete_slide", "slide_index": 3},
    {"op": "reorder", "from": 5, "to": 2},
    {"op": "replace_text", "slide_index": 1, "find": "May 12", "replace": "May 13"},
    {"op": "add_notes", "slide_index": 4, "text": "...", "append": true},
    {"op": "replace_image", "slide_index": 7, "image_index": 1, "url": "https://..."}
  ]
}

All slide_index / from / to / image_index values are 1-indexed.

Validation runs first. If any edit is malformed, the script prints all errors
to stderr and exits non-zero before touching the API. Edits then execute in
order; on the first failure the script stops, reports which edit failed, and
exits non-zero. The deck URL is always the last line of stdout on success.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make slides_client importable from this dir regardless of cwd
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from slides_client import SlidesClient  # noqa: E402


VALID_OPS = {
    "delete_slide",
    "reorder",
    "replace_text",
    "add_notes",
    "replace_image",
}

# Required keys per op (excluding "op" itself).
# "type" entry below: int | str | bool. We check existence + type.
REQUIRED_FIELDS: dict[str, list[tuple[str, type]]] = {
    "delete_slide": [("slide_index", int)],
    "reorder": [("from", int), ("to", int)],
    "replace_text": [("slide_index", int), ("find", str), ("replace", str)],
    "add_notes": [("slide_index", int), ("text", str)],
    "replace_image": [("slide_index", int), ("image_index", int), ("url", str)],
}


def validate_plan(plan: dict) -> list[str]:
    """Return a list of validation errors; empty list means valid."""
    errors: list[str] = []
    pid = plan.get("presentation_id")
    if not pid or not isinstance(pid, str):
        errors.append("plan.presentation_id is required and must be a string")
    edits = plan.get("edits")
    if not isinstance(edits, list) or not edits:
        errors.append("plan.edits is required and must be a non-empty list")
        return errors
    for i, e in enumerate(edits):
        if not isinstance(e, dict):
            errors.append(f"edits[{i}] must be an object")
            continue
        op = e.get("op")
        if op not in VALID_OPS:
            errors.append(
                f"edits[{i}].op={op!r} is not one of {sorted(VALID_OPS)}"
            )
            continue
        for field, expected_type in REQUIRED_FIELDS[op]:
            if field not in e:
                errors.append(f"edits[{i}].{field} is required for op={op}")
                continue
            value = e[field]
            # Booleans are technically int in Python, exclude them explicitly when expecting int
            if expected_type is int and (isinstance(value, bool) or not isinstance(value, int)):
                errors.append(
                    f"edits[{i}].{field} must be an int (got {type(value).__name__})"
                )
            elif expected_type is str and not isinstance(value, str):
                errors.append(
                    f"edits[{i}].{field} must be a string (got {type(value).__name__})"
                )
        # Op-specific extra checks
        if op == "add_notes" and "append" in e and not isinstance(e["append"], bool):
            errors.append(
                f"edits[{i}].append must be a bool when provided "
                f"(got {type(e['append']).__name__})"
            )
        # Reject slide_index / from / to / image_index <= 0
        for field in ("slide_index", "from", "to", "image_index"):
            if field in e and isinstance(e[field], int) and not isinstance(e[field], bool):
                if e[field] < 1:
                    errors.append(
                        f"edits[{i}].{field}={e[field]} must be >= 1 (1-indexed)"
                    )
    return errors


def apply_edit(client: SlidesClient, pid: str, edit: dict) -> str:
    """Apply a single edit and return a short human-readable status string."""
    op = edit["op"]
    if op == "delete_slide":
        client.delete_slide_at(pid, edit["slide_index"])
        return f"deleted slide {edit['slide_index']}"
    if op == "reorder":
        client.reorder_slide(pid, edit["from"], edit["to"])
        return f"moved slide {edit['from']} -> {edit['to']}"
    if op == "replace_text":
        count = client.replace_text_on_slide(
            pid, edit["slide_index"], edit["find"], edit["replace"]
        )
        return (
            f"replaced text on slide {edit['slide_index']}: "
            f"{count} occurrence(s) of {edit['find']!r}"
        )
    if op == "add_notes":
        append = bool(edit.get("append", False))
        client.add_speaker_notes(
            pid, edit["slide_index"], edit["text"], append=append
        )
        mode = "appended to" if append else "set on"
        return f"notes {mode} slide {edit['slide_index']}"
    if op == "replace_image":
        client.replace_image_on_slide(
            pid, edit["slide_index"], edit["image_index"], edit["url"]
        )
        return (
            f"replaced image #{edit['image_index']} on slide "
            f"{edit['slide_index']}"
        )
    raise ValueError(f"Unhandled op: {op}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Apply edits to an existing Google Slides deck from a JSON edit plan."
    )
    ap.add_argument("plan", help="Path to edit-plan JSON file (or '-' for stdin)")
    args = ap.parse_args()

    if args.plan == "-":
        plan = json.load(sys.stdin)
    else:
        plan = json.loads(Path(args.plan).read_text())

    errors = validate_plan(plan)
    if errors:
        print("Edit-plan validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    pid: str = plan["presentation_id"]
    edits: list[dict] = plan["edits"]
    client = SlidesClient()

    for i, edit in enumerate(edits):
        try:
            status = apply_edit(client, pid, edit)
        except Exception as e:
            print(
                f"Edit {i} ({edit.get('op')}) failed: {type(e).__name__}: {e}",
                file=sys.stderr,
            )
            return 2
        print(f"[{i + 1}/{len(edits)}] {status}", file=sys.stderr)

    print(client.url(pid))
    return 0


if __name__ == "__main__":
    sys.exit(main())
