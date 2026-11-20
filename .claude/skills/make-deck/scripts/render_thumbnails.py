"""Render every slide of a presentation as a PNG to /tmp.

Used for self-eval: build a deck, render thumbnails, visually inspect
that no text/shape overflows, then iterate on layout if needed.

Usage:
  python3 render_thumbnails.py <presentation_id> [out_dir]
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from slides_client import SlidesClient  # noqa: E402


def render(presentation_id: str, out_dir: str = "/tmp/slides-eval") -> list[str]:
    out = Path(out_dir)
    # Clean and recreate
    if out.exists():
        for f in out.iterdir():
            f.unlink()
    out.mkdir(parents=True, exist_ok=True)
    c = SlidesClient()
    pres = c.slides.presentations().get(presentationId=presentation_id).execute()
    slides = pres.get("slides", [])
    paths = []
    for i, slide in enumerate(slides, start=1):
        page_id = slide["objectId"]
        thumb = (
            c.slides.presentations()
            .pages()
            .getThumbnail(
                presentationId=presentation_id,
                pageObjectId=page_id,
                thumbnailProperties_thumbnailSize="LARGE",
            )
            .execute()
        )
        url = thumb["contentUrl"]
        path = out / f"slide-{i:02d}.png"
        urllib.request.urlretrieve(url, path)
        paths.append(str(path))
        print(f"slide {i:2d}: {path}")
    return paths


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 render_thumbnails.py <presentation_id> [out_dir]", file=sys.stderr)
        sys.exit(1)
    pid = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "/tmp/slides-eval"
    render(pid, out_dir)
