"""Clone a prior outline as a new build (writes to /tmp/cloned-outline.json).

Usage:
  python3 clone_deck.py <slug-or-id> [--new-title "..."] [--audience <name>] [--save-as <new-slug>]

Match order:
  1. Exact slug match (filename minus YYYY-MM-DD prefix and .json)
  2. Presentation ID match (data.presentation_id)
  3. Deck URL substring match
  4. Partial slug substring (newest wins; if multiple, list and exit 1)

Writes the modified outline to /tmp/cloned-outline.json and prints the path.
Does NOT call build_deck.py — that's the caller's job, so the user can review
the cloned outline first.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

OUTPUTS_DIR = Path.home() / ".claude" / "skills" / "make-deck" / "outputs"
DEFAULT_OUT_PATH = Path("/tmp/cloned-outline.json")

FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.json$")


def _load_states(outputs_dir: Path) -> list[dict]:
    states = []
    if not outputs_dir.exists():
        return states
    for p in sorted(outputs_dir.glob("*.json"), reverse=True):
        m = FILENAME_RE.match(p.name)
        if not m:
            continue
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        states.append({
            "path": p,
            "date": m.group(1),
            "slug": m.group(2),
            "data": data,
        })
    return states


def find_matches(needle: str, states: list[dict]) -> list[dict]:
    """Return matches in priority order. May contain >1 for partial-slug hits."""
    needle_lower = needle.lower()
    # 1. Exact slug
    exact = [s for s in states if s["slug"].lower() == needle_lower]
    if exact:
        return exact
    # 2. Presentation ID exact
    pid_match = [s for s in states if s["data"].get("presentation_id") == needle]
    if pid_match:
        return pid_match
    # 3. URL substring (handles passing the full URL)
    url_match = [s for s in states if needle in s["data"].get("url", "")]
    if url_match:
        return url_match
    # 4. Partial slug substring
    partial = [s for s in states if needle_lower in s["slug"].lower()]
    return partial


def clone(
    source_outline: dict,
    new_title: str | None = None,
    audience: str | None = None,
) -> dict:
    """Return a modified outline. Source is not mutated."""
    outline = json.loads(json.dumps(source_outline))  # deep copy via JSON
    if new_title:
        outline["title"] = new_title
        # Cover slide title typically mirrors deck title; refresh it.
        for s in outline.get("slides", []):
            if s.get("template") == "cover" and s.get("title") == source_outline.get("title"):
                s["title"] = new_title
                break
    if audience:
        outline["audience"] = audience
    return outline


def main() -> int:
    ap = argparse.ArgumentParser(description="Clone a prior make-deck outline.")
    ap.add_argument("identifier", help="Slug, partial slug, presentation ID, or deck URL")
    ap.add_argument("--new-title", help="Override outline.title")
    ap.add_argument("--audience", help="Set outline.audience")
    ap.add_argument("--save-as", help="Write to /tmp/<save-as>.json instead of cloned-outline.json")
    ap.add_argument("--outputs-dir", default=str(OUTPUTS_DIR),
                    help="Override outputs directory (testing)")
    args = ap.parse_args()

    states = _load_states(Path(args.outputs_dir))
    if not states:
        print(f"Error: no state files in {args.outputs_dir}", file=sys.stderr)
        return 1

    matches = find_matches(args.identifier, states)
    if not matches:
        print(f"Error: no match for {args.identifier!r}", file=sys.stderr)
        return 1
    if len(matches) > 1:
        print(f"Multiple matches for {args.identifier!r}:", file=sys.stderr)
        for m in matches:
            print(f"  {m['date']}  {m['slug']}", file=sys.stderr)
        print("Disambiguate with a more specific slug.", file=sys.stderr)
        return 1

    src = matches[0]
    source_outline = src["data"].get("outline")
    if not source_outline:
        print(f"Error: {src['path']} has no 'outline' field", file=sys.stderr)
        return 1

    new_outline = clone(source_outline, new_title=args.new_title, audience=args.audience)

    if args.save_as:
        name = args.save_as if args.save_as.endswith(".json") else f"{args.save_as}.json"
        out_path = Path("/tmp") / name
    else:
        out_path = DEFAULT_OUT_PATH

    out_path.write_text(json.dumps(new_outline, indent=2))
    print(f"Source: {src['path']}", file=sys.stderr)
    print(f"Title:  {new_outline.get('title')}", file=sys.stderr)
    if new_outline.get("audience"):
        print(f"Audience: {new_outline['audience']}", file=sys.stderr)
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
