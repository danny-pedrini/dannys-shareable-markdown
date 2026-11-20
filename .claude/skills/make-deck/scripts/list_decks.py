"""Index prior make-deck runs from ~/.claude/skills/make-deck/outputs/.

Usage:
  python3 list_decks.py                        # most recent 20
  python3 list_decks.py --all                  # no limit
  python3 list_decks.py --audience the CPO     # filter by outline.audience
  python3 list_decks.py --search emr           # filter slug or title
  python3 list_decks.py --json                 # JSON for piping

State files are named YYYY-MM-DD-<slug>.json (build_deck.py convention).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

OUTPUTS_DIR = Path.home() / ".claude" / "skills" / "make-deck" / "outputs"

# Filename pattern: 2026-05-13-some-slug.json
FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.json$")


def load_state(path: Path) -> dict | None:
    """Load a state file. Returns enriched dict or None on parse error."""
    m = FILENAME_RE.match(path.name)
    if not m:
        return None
    date_prefix, slug = m.group(1), m.group(2)
    try:
        data = json.loads(path.read_text())
    except Exception:
        return None
    outline = data.get("outline") or {}
    template_mix = data.get("template_mix") or {}
    return {
        "path": str(path),
        "date": date_prefix,
        "slug": slug,
        "title": data.get("title") or outline.get("title") or slug,
        "audience": outline.get("audience"),
        "slide_count": data.get("slide_count", 0),
        "template_mix": template_mix,
        "url": data.get("url", ""),
        "presentation_id": data.get("presentation_id", ""),
    }


def collect(outputs_dir: Path) -> list[dict]:
    if not outputs_dir.exists():
        return []
    decks = []
    for p in outputs_dir.glob("*.json"):
        d = load_state(p)
        if d:
            decks.append(d)
    # Newest first: sort by date desc, then path desc (so -2, -3 suffixes
    # come after the base in the same day).
    decks.sort(key=lambda x: (x["date"], x["path"]), reverse=True)
    return decks


def filter_decks(
    decks: list[dict],
    audience: str | None = None,
    search: str | None = None,
) -> list[dict]:
    out = decks
    if audience:
        a_lower = audience.lower()
        out = [d for d in out if (d.get("audience") or "").lower() == a_lower]
    if search:
        s_lower = search.lower()
        out = [
            d for d in out
            if s_lower in d["slug"].lower() or s_lower in (d["title"] or "").lower()
        ]
    return out


def fmt_template_mix(mix: dict) -> str:
    """Compact 'cov,exec,3card×2,bul' style summary."""
    short = {
        "cover": "cov",
        "exec_summary": "exec",
        "section_divider": "sec",
        "agenda": "agenda",
        "moving_blueprint": "mblp",
        "bullets": "bul",
        "two_column": "2col",
        "do_dont": "do_dont",
        "flow_steps": "flow",
        "three_card": "3card",
        "key_stat": "kstat",
        "big_idea": "big",
        "pull_quote": "quote",
        "comparison_2x2": "2x2",
        "metric_grid": "mgrid",
    }
    parts = []
    for k, v in mix.items():
        label = short.get(k, k[:5])
        parts.append(f"{label}×{v}" if v > 1 else label)
    return ",".join(parts)


def print_table(decks: list[dict]) -> None:
    if not decks:
        print("No decks found.")
        return
    header = ("Date", "Slug", "Slides", "Templates", "URL")
    rows = [
        (
            d["date"],
            d["slug"][:40],
            str(d["slide_count"]),
            fmt_template_mix(d["template_mix"])[:32],
            d["url"],
        )
        for d in decks
    ]
    widths = [
        max(len(header[i]), max(len(r[i]) for r in rows))
        for i in range(len(header))
    ]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*header))
    print(fmt.format(*("-" * w for w in widths)))
    for r in rows:
        print(fmt.format(*r))


def main() -> int:
    ap = argparse.ArgumentParser(description="Index prior make-deck runs.")
    ap.add_argument("--all", action="store_true", help="Show all (no limit)")
    ap.add_argument("--audience", help="Filter by outline.audience")
    ap.add_argument("--search", help="Substring match against slug or title")
    ap.add_argument("--json", action="store_true", help="JSON output for piping")
    ap.add_argument("--outputs-dir", default=str(OUTPUTS_DIR),
                    help="Override outputs directory (testing)")
    args = ap.parse_args()

    decks = collect(Path(args.outputs_dir))
    decks = filter_decks(decks, audience=args.audience, search=args.search)
    if not args.all:
        decks = decks[:20]

    if args.json:
        print(json.dumps(decks, indent=2))
    else:
        print_table(decks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
