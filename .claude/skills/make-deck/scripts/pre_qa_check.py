"""Programmatic pre-QA checks for a built deck (runs before vision QA agent).

Usage:
  python3 pre_qa_check.py <presentation_id>
  python3 pre_qa_check.py <presentation_id> --json

Checks:
  1. bullet-overflow: any slide with >6 bullet-like items
  2. missing-footer: confidentiality footer absent on content slides
  3. em-dash: U+2014 or "--" anywhere in text (skill hard rule)
  4. missing-title: no title text near top (y < 60pt) on title-bearing slides
  5. empty-slide: zero pageElements
  6. overflow-heuristic: text length > capacity heuristic
  7. image-no-alt: WARN only
  8. low-contrast: WARN heuristic on text vs. shape fill luminance

Exit 0 if PASS (no FAIL), 1 if any FAIL.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

EMU_PER_PT = 12700

# Confidentiality footer text required on most content slides.
FOOTER_NEEDLE = "[Company confidentiality footer]"

# Templates that legitimately have NO footer per slides_client.py:
#   cover, section_divider, key_stat (sometimes), big_idea, agenda (has footer),
#   moving_blueprint, pull_quote (has footer).
# Inspecting slides_client: NO footer on cover, section_divider, moving_blueprint, big_idea.
# Per the user's spec: skip cover, section_divider, key_stat, agenda, moving_blueprint, big_idea.
SLIDES_WITHOUT_FOOTER_KIND = {
    "cover", "section_divider", "key_stat",
    "agenda", "moving_blueprint", "big_idea",
}


def _emu_to_pt(emu: int | float | None) -> float:
    if emu is None:
        return 0.0
    return float(emu) / EMU_PER_PT


def _shape_text(shape: dict) -> str:
    """Flatten all textRun content in a shape."""
    text = shape.get("text", {})
    parts = []
    for te in text.get("textElements", []):
        tr = te.get("textRun")
        if tr and "content" in tr:
            parts.append(tr["content"])
    return "".join(parts)


def _shape_bbox_pt(el: dict) -> tuple[float, float, float, float]:
    """Return (x, y, w, h) in pt. Slides API stores size in EMU, transform translates in EMU.

    Width/height returned scale by transform.scaleX/scaleY when present.
    """
    size = el.get("size", {})
    tr = el.get("transform", {}) or {}
    w_unit = size.get("width", {}).get("unit", "EMU")
    h_unit = size.get("height", {}).get("unit", "EMU")
    w_mag = float(size.get("width", {}).get("magnitude", 0) or 0)
    h_mag = float(size.get("height", {}).get("magnitude", 0) or 0)
    if w_unit == "PT":
        w_pt = w_mag
    else:
        w_pt = _emu_to_pt(w_mag)
    if h_unit == "PT":
        h_pt = h_mag
    else:
        h_pt = _emu_to_pt(h_mag)
    sx = float(tr.get("scaleX", 1) or 1)
    sy = float(tr.get("scaleY", 1) or 1)
    w_pt *= sx
    h_pt *= sy
    tx_unit = tr.get("unit", "EMU")
    tx = float(tr.get("translateX", 0) or 0)
    ty = float(tr.get("translateY", 0) or 0)
    if tx_unit == "EMU":
        tx = _emu_to_pt(tx)
        ty = _emu_to_pt(ty)
    return tx, ty, w_pt, h_pt


def _classify_kind(slide: dict) -> str:
    """Heuristic kind detection from page elements.

    The Slides API does not store our template name. We classify by content
    signals: background color, presence of footer, large stat text, etc.
    """
    background = (
        slide.get("pageProperties", {})
        .get("pageBackgroundFill", {})
        .get("solidFill", {})
        .get("color", {})
        .get("rgbColor", {})
    )

    def is_dark(rgb: dict) -> bool:
        r, g, b = rgb.get("red", 1), rgb.get("green", 1), rgb.get("blue", 1)
        return (r + g + b) / 3 < 0.2

    elements = slide.get("pageElements", [])
    # Cover: dark background, no footer
    if background and is_dark(background):
        return "cover"
    # Look for the largest font size; key_stat / big_idea have very large text
    max_font_pt = 0.0
    has_footer = False
    has_title_top = False
    for el in elements:
        shape = el.get("shape")
        if not shape:
            continue
        text = _shape_text(shape)
        if FOOTER_NEEDLE in text:
            has_footer = True
        _, y, _, _ = _shape_bbox_pt(el)
        for te in shape.get("text", {}).get("textElements", []):
            tr = te.get("textRun", {})
            style = tr.get("style", {})
            fs = style.get("fontSize", {}).get("magnitude")
            if fs:
                max_font_pt = max(max_font_pt, float(fs))
                if y < 60 and float(fs) >= 18 and text.strip():
                    has_title_top = True
    # Beige background with no footer ~ section_divider or moving_blueprint
    if background and not is_dark(background) and not has_footer:
        # beige rgb ~ (0.93, 0.89, 0.84); sage_tint similar
        r = background.get("red", 1)
        g = background.get("green", 1)
        b = background.get("blue", 1)
        if r > 0.85 and g > 0.85 and b > 0.7 and b < g:
            return "section_divider"
    # Very large font (>= 60pt) suggests key_stat
    if max_font_pt >= 60:
        return "key_stat"
    # >= 40pt with no footer: big_idea
    if max_font_pt >= 40 and not has_footer:
        return "big_idea"
    if has_title_top:
        return "content"
    return "content"


def _count_bullets(slide: dict) -> int:
    """Count bullet-like items. A 'bullet' is a line starting with '• ' or a
    list-item paragraph (paragraphMarker.bullet present)."""
    n = 0
    for el in slide.get("pageElements", []):
        shape = el.get("shape")
        if not shape:
            continue
        text = shape.get("text", {})
        for te in text.get("textElements", []):
            pm = te.get("paragraphMarker")
            if pm and pm.get("bullet"):
                n += 1
        # Also count "• " prefix style (slides_client.py renders bullets this way)
        flat = _shape_text(shape)
        for line in flat.split("\n"):
            if line.lstrip().startswith("• "):
                n += 1
    return n


def _relative_luminance(rgb: dict) -> float:
    def chan(v: float) -> float:
        v = max(0.0, min(1.0, v))
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r = chan(rgb.get("red", 0))
    g = chan(rgb.get("green", 0))
    b = chan(rgb.get("blue", 0))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _page_background_rgb(slide: dict) -> dict | None:
    fill = (
        slide.get("pageProperties", {})
        .get("pageBackgroundFill", {})
        .get("solidFill", {})
        .get("color", {})
        .get("rgbColor")
    )
    return fill


def check_slide(idx: int, slide: dict) -> list[dict]:
    issues: list[dict] = []
    elements = slide.get("pageElements", [])
    kind = _classify_kind(slide)

    # 5. empty slide
    if not elements:
        issues.append({
            "slide": idx, "check": "empty-slide", "severity": "FAIL",
            "detail": "no pageElements"
        })
        return issues

    # 1. bullet overflow
    n_bullets = _count_bullets(slide)
    if n_bullets > 6:
        issues.append({
            "slide": idx, "check": "bullet-overflow", "severity": "WARN",
            "detail": f"{n_bullets} bullets, max is 6"
        })

    # 2. footer presence — only on content slides
    if kind not in SLIDES_WITHOUT_FOOTER_KIND:
        has_footer = any(
            FOOTER_NEEDLE in _shape_text(el.get("shape", {}))
            for el in elements if el.get("shape")
        )
        if not has_footer:
            issues.append({
                "slide": idx, "check": "missing-footer", "severity": "WARN",
                "detail": "no confidentiality footer detected"
            })

    # 3. em-dash and double-hyphen
    for el in elements:
        shape = el.get("shape")
        if not shape:
            continue
        txt = _shape_text(shape)
        if "—" in txt or re.search(r"(?<!-)--(?!-)", txt):
            sample = txt.strip().splitlines()[0][:80] if txt.strip() else ""
            issues.append({
                "slide": idx, "check": "em-dash", "severity": "FAIL",
                "detail": f"em-dash or '--' in text: {sample!r}"
            })
            break  # one report per slide is enough

    # 4. title presence — skip kinds where the headline IS the content
    if kind not in {"cover", "key_stat", "big_idea", "moving_blueprint"}:
        has_title = False
        for el in elements:
            shape = el.get("shape")
            if not shape:
                continue
            _, y, _, _ = _shape_bbox_pt(el)
            if y >= 60:
                continue
            for te in shape.get("text", {}).get("textElements", []):
                tr = te.get("textRun", {})
                style = tr.get("style", {})
                fs = style.get("fontSize", {}).get("magnitude") or 0
                txt = (tr.get("content") or "").strip()
                if txt and float(fs) >= 16:
                    has_title = True
                    break
            if has_title:
                break
        if not has_title:
            issues.append({
                "slide": idx, "check": "missing-title", "severity": "WARN",
                "detail": "no title text box near top (y<60pt) >=16pt"
            })

    # 6. overflow heuristic
    for el in elements:
        shape = el.get("shape")
        if not shape:
            continue
        txt = _shape_text(shape)
        clean = txt.strip()
        if len(clean) < 40:
            continue
        _, _, w_pt, h_pt = _shape_bbox_pt(el)
        if w_pt <= 0 or h_pt <= 0:
            continue
        # Skip the tiny footer textbox (height ~12pt, font 7pt).
        if h_pt < 16:
            continue
        capacity = (w_pt / 4.0) * (h_pt / 12.0)
        if len(clean) > capacity * 1.2:  # 20% grace
            issues.append({
                "slide": idx, "check": "overflow-heuristic", "severity": "WARN",
                "detail": f"{len(clean)} chars in {w_pt:.0f}x{h_pt:.0f}pt (cap ~{int(capacity)})"
            })

    # 7. image without alt text
    for el in elements:
        if "image" in el:
            alt = el.get("description") or el.get("title")
            if not alt:
                issues.append({
                    "slide": idx, "check": "image-no-alt", "severity": "WARN",
                    "detail": f"image {el.get('objectId', '?')} has no alt-text"
                })

    # 8. contrast heuristic — text foreground vs page background
    bg = _page_background_rgb(slide) or {"red": 1, "green": 1, "blue": 1}
    bg_lum = _relative_luminance(bg)
    for el in elements:
        shape = el.get("shape")
        if not shape:
            continue
        for te in shape.get("text", {}).get("textElements", []):
            tr = te.get("textRun", {})
            style = tr.get("style", {})
            fg_color = (
                style.get("foregroundColor", {})
                .get("opaqueColor", {})
                .get("rgbColor")
            )
            if not fg_color:
                continue
            fg_lum = _relative_luminance(fg_color)
            if abs(fg_lum - bg_lum) < 0.4:
                sample = (tr.get("content") or "").strip()[:40]
                issues.append({
                    "slide": idx, "check": "low-contrast", "severity": "WARN",
                    "detail": f"ΔL={abs(fg_lum-bg_lum):.2f} on text {sample!r}"
                })
                break  # one report per shape is enough

    return issues


def run_checks(presentation_id: str) -> dict:
    """Pull the deck and run every check. Returns structured result."""
    from slides_client import SlidesClient
    c = SlidesClient()
    pres = c.slides.presentations().get(presentationId=presentation_id).execute()
    slides = pres.get("slides", [])
    all_issues: list[dict] = []
    for i, slide in enumerate(slides, start=1):
        all_issues.extend(check_slide(i, slide))
    n_fail = sum(1 for it in all_issues if it["severity"] == "FAIL")
    n_warn = sum(1 for it in all_issues if it["severity"] == "WARN")
    verdict = "FIX_REQUIRED" if n_fail else ("REVIEW" if n_warn else "PASS")
    return {
        "presentation_id": presentation_id,
        "slide_count": len(slides),
        "issues": all_issues,
        "fail_count": n_fail,
        "warn_count": n_warn,
        "verdict": verdict,
    }


def print_human(result: dict) -> None:
    print(f"make-deck pre-QA report for {result['presentation_id']}")
    issues = result["issues"]
    if not issues:
        print("  No issues.")
    else:
        header = ("Slide", "Check", "Severity", "Detail")
        rows = [
            (str(it["slide"]), it["check"], it["severity"], it["detail"])
            for it in issues
        ]
        widths = [
            max(len(header[i]), max(len(r[i]) for r in rows))
            for i in range(len(header))
        ]
        fmt = "  ".join(f"{{:<{w}}}" for w in widths)
        print("  " + fmt.format(*header))
        for r in rows:
            print("  " + fmt.format(*r))
    print()
    print(f"Summary: {result['fail_count']} FAIL, {result['warn_count']} WARN")
    print(f"Verdict: {result['verdict']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Pre-QA checks on a built deck.")
    ap.add_argument("presentation_id")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()

    try:
        result = run_checks(args.presentation_id)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)

    return 0 if result["fail_count"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
