#!/usr/bin/env python3
"""Render a journey-map spec (JSON) as one native Google Slides slide.

Reuses make-deck's SlidesClient for auth, brand palette, Poppins, the
confidentiality footer, and speaker notes. Layout is computed from the spec,
so nobody hand-places coordinates. Spec format: references/spec-schema.md.

Usage:
  python3 render_journey.py spec.json --dry-run   # validate + layout report, no API calls
  python3 render_journey.py spec.json             # build the slide

Exit code 1 with a list of problems if the spec fails validation or a callout
cannot fit. The last stdout line of a real run is the slide URL.

Python 3.9 compatible (macOS system python): no `X | None` annotations.
"""
import argparse
import json
import math
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAKE_DECK_SCRIPTS = HERE.parents[1] / "make-deck" / "scripts"
sys.path.insert(0, str(MAKE_DECK_SCRIPTS))

try:  # brand tokens from make-deck; fallback copy keeps --dry-run working without Google libs
    from slides_client import HH, HH_FONT  # noqa: E402
except Exception:  # pragma: no cover
    HH = {
        "ink": "1C1C1C", "white": "FFFFFF", "off_white": "FBF8F5", "sage_tint": "F5FAF6",
        "sage_light": "D9EAD3", "sage_accent": "0097A7", "blue_powder": "D5E3EE",
        "blue_panel": "ECF2F6", "blue_mid": "84ADCD", "beige": "EEE2D6", "warm_gray": "D7D7D2",
        "line": "D9D9D9",
    }
    HH_FONT = "Poppins"

# ---------------------------------------------------------------- layout grid (720 x 405 pt)
W, M = 720.0, 30.0
RIGHT = W - M
TITLE_Y, TITLE_H, TITLE_PT = 6.0, 30.0, 22
PERSONA_Y, PERSONA_H = 40.0, 44.0
COL_TOP, HDR_H = 88.0, 18.0
STEP_MIN, STEP_MAX = 30.0, 72.0                   # step-text area grows to fit the wordiest stage
COL_GAP = 3.0
COL_BOTTOM_WITH_BAND, COL_BOTTOM_NO_BAND = 318.0, 368.0
BOTTOM_Y, BOTTOM_H = 320.0, 51.0
FINE_Y, FINE_H, FINE_PT = 372.0, 17.0, 6.5
CURVE_CLEARANCE = 8.0
DEAD_SPACE_MAX = 40.0                              # empty pt under a column's step text before it reads as a hole
COLUMN_FILLS = ["blue_powder", "sage_light", "blue_panel", "sage_tint", "beige", "warm_gray"]
SUPERSCRIPTS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
EM_DASH = "—"

LIMITS = {
    "title": 60, "persona_name": 45, "persona_description": 130, "stage_name": 18,
    "line": 95, "stat_text": 45, "stat_detail": 60, "bullet": 60, "quote": 120,
    "attribution": 45, "research_text": 110, "citation": 120, "turn": 110, "caption": 40,
    "cost_value": 8, "cost_label": 45, "built_line": 110,
}


def sup(n):
    return str(n).translate(SUPERSCRIPTS)


def u16(s):
    """Slides API text indexes count UTF-16 code units (emoji are 2)."""
    return len(s.encode("utf-16-le")) // 2


def pt_to_emu(n):
    return int(round(n * 12700))


def color(c):
    """'theme:LIGHT2', a palette key, or a raw hex string -> Slides color object."""
    if c.startswith("theme:"):
        return {"themeColor": c.split(":", 1)[1]}
    h = HH.get(c, c).lstrip("#")
    return {"rgbColor": {"red": int(h[0:2], 16) / 255.0, "green": int(h[2:4], 16) / 255.0,
                         "blue": int(h[4:6], 16) / 255.0}}


def parse_markup(s):
    """Split '**bold** rest' into [(text, {'bold': True}), (text, {})]."""
    out = []
    for i, part in enumerate(re.split(r"\*\*", s)):
        if part:
            out.append((part, {"bold": True} if i % 2 else {}))
    return out


def est_lines(text, size, width, bold=False):
    cpl = max(6, int((width - 15) / (size * (0.53 if bold else 0.50))))  # ~7pt insets each side
    return sum(max(1, math.ceil(len(p) / cpl)) for p in text.split("\n"))


def est_height(paras, width):
    """paras: [(text, size, bold)] -> box height in pt including insets."""
    return sum(est_lines(t, s, width, b) * s * 1.2 for t, s, b in paras) + 13.0


# ---------------------------------------------------------------- curve geometry
def _bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def curve_samples(pts, per_half=24):
    """Sample the CURVED_CONNECTOR_3 path Slides draws between consecutive points.

    curvedConnector3 is two cubics meeting at the box midpoint; both endpoints
    have horizontal tangents, which is why a point mid-descent reads as a flat
    step and gets dropped by keep_extrema().
    """
    out = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        w, h = x2 - x1, y2 - y1
        a = [(x1, y1), (x1 + w / 4, y1), (x1 + w / 2, y1 + h / 4), (x1 + w / 2, y1 + h / 2)]
        b = [(x1 + w / 2, y1 + h / 2), (x1 + w / 2, y1 + 3 * h / 4), (x1 + 3 * w / 4, y2), (x2, y2)]
        for seg in (a, b):
            out += [_bez(*seg, t=i / per_half) for i in range(per_half + 1)]
    return out


def curve_span(samples, xa, xb):
    ys = [y for x, y in samples if xa - 1 <= x <= xb + 1]
    return (min(ys), max(ys)) if ys else (None, None)


def keep_extrema(centers):
    """Keep endpoints, peaks, troughs, and plateaus; drop monotonic mid-points."""
    kept = [centers[0]]
    for prev, cur, nxt in zip(centers, centers[1:], centers[2:]):
        if (cur[1] - prev[1]) * (nxt[1] - cur[1]) <= 0:
            kept.append(cur)
    kept.append(centers[-1])
    return kept


# ---------------------------------------------------------------- validation
def validate(spec):
    errs = []

    def chk(val, key, where):
        if val is None:
            return
        if not isinstance(val, str):
            errs.append(f"{where}: expected text")
            return
        plain = val.replace("**", "")
        if len(plain) > LIMITS[key]:
            errs.append(f"{where}: {len(plain)} chars, limit {LIMITS[key]}; shorten or move detail to notes")

    def walk(o, path="spec"):
        if isinstance(o, dict):
            for k, v in o.items():
                if k != "url":
                    walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
        elif isinstance(o, str) and EM_DASH in o:
            errs.append(f"{path}: contains an em dash; use a comma, colon, period, or parentheses")

    walk(spec)
    chk(spec.get("title"), "title", "title")
    personas = spec.get("personas") or []
    if not 1 <= len(personas) <= 2:
        errs.append("personas: need 1 or 2")
    keys = set()
    for i, p in enumerate(personas):
        for f in ("key", "short", "name", "description", "avatar"):
            if not p.get(f):
                errs.append(f"personas[{i}].{f} is required")
        keys.add(p.get("key"))
        chk(p.get("name"), "persona_name", f"personas[{i}].name")
        av = p.get("avatar") or ""
        if "‍" in av or any(0x1F3FB <= ord(ch) <= 0x1F3FF for ch in av) or len(av.replace("️", "")) > 1:
            errs.append(f"personas[{i}].avatar: use one single-codepoint emoji (e.g. \U0001F469 \U0001F9D1 \U0001FA7A "
                        "\U0001F3A7); joined or skin-tone sequences break apart in Slides")
        if p.get("illustrative") and "(illustrative)" not in (p.get("name") or "").lower():
            errs.append(f"personas[{i}].name must include \"(illustrative)\" because illustrative is true")
        chk(p.get("description"), "persona_description", f"personas[{i}].description")
    curve = spec.get("curve") or {}
    if curve.get("persona") not in keys:
        errs.append("curve.persona must match a persona key")
    sources = spec.get("sources") or {}
    for k, s in sources.items():
        if not (s.get("label") and s.get("url")):
            errs.append(f"sources.{k}: needs label and url (claims with no linkable source carry source: null)")

    def src_ok(ref, where):
        if ref is not None and ref not in sources:
            errs.append(f"{where}: source '{ref}' is not defined in sources")

    stages = spec.get("stages") or []
    if not 3 <= len(stages) <= 6:
        errs.append("stages: need 3 to 6")
    for i, st in enumerate(stages):
        w = f"stages[{i}]"
        chk(st.get("name"), "stage_name", f"{w}.name")
        if st.get("sentiment") not in (1, 2, 3, 4, 5):
            errs.append(f"{w}.sentiment must be an integer 1 (best) to 5 (worst)")
        lines = st.get("lines") or []
        if not 1 <= len(lines) <= 2:
            errs.append(f"{w}.lines: need 1 or 2 (order by who acts first; drop a lane with nothing meaningful)")
        for j, ln in enumerate(lines):
            if ln.get("persona") not in keys:
                errs.append(f"{w}.lines[{j}].persona must match a persona key")
            chk(ln.get("text"), "line", f"{w}.lines[{j}].text")
        callouts = st.get("callouts") or []
        if len(callouts) > 2:
            errs.append(f"{w}.callouts: max 2 per stage; move the rest to notes")
        for j, c in enumerate(callouts):
            cw = f"{w}.callouts[{j}]"
            t = c.get("type")
            if t == "stat":
                chk(c.get("text"), "stat_text", f"{cw}.text")
                chk(c.get("detail"), "stat_detail", f"{cw}.detail")
                src_ok(c.get("source"), cw)
            elif t == "bullets":
                items = c.get("items") or []
                if not 1 <= len(items) <= 3:
                    errs.append(f"{cw}.items: need 1 to 3")
                for k, it in enumerate(items):
                    chk(it.get("text"), "bullet", f"{cw}.items[{k}].text")
                    src_ok(it.get("source"), f"{cw}.items[{k}]")
            elif t == "quote":
                chk(c.get("text"), "quote", f"{cw}.text")
                chk(c.get("attribution"), "attribution", f"{cw}.attribution")
                if not c.get("attribution"):
                    errs.append(f"{cw}.attribution is required (role, not name)")
                src_ok(c.get("source"), cw)
            elif t == "research":
                chk(c.get("text"), "research_text", f"{cw}.text")
                chk(c.get("citation"), "citation", f"{cw}.citation")
                if not c.get("citation"):
                    errs.append(f"{cw}.citation is required")
                src_ok(c.get("source"), cw)
            elif t == "exchange":
                chk(c.get("caption"), "caption", f"{cw}.caption")
                turns = c.get("turns") or []
                if not 2 <= len(turns) <= 3:
                    errs.append(f"{cw}.turns: need 2 or 3")
                for k, tn in enumerate(turns):
                    if not tn.get("speaker"):
                        errs.append(f"{cw}.turns[{k}].speaker is required (e.g. Patient, Provider)")
                    chk(tn.get("text"), "turn", f"{cw}.turns[{k}].text")
                src_ok(c.get("source"), cw)
            else:
                errs.append(f"{cw}.type must be stat, bullets, quote, research, or exchange")
    band = spec.get("bottom_band")
    if band:
        left = band.get("left") or {}
        stats = left.get("stats") or []
        if left and not 1 <= len(stats) <= 4:
            errs.append("bottom_band.left.stats: need 1 to 4")
        for k, s in enumerate(stats):
            chk(s.get("value"), "cost_value", f"bottom_band.left.stats[{k}].value")
            chk(s.get("label"), "cost_label", f"bottom_band.left.stats[{k}].label")
            src_ok(s.get("source"), f"bottom_band.left.stats[{k}]")
        src_ok(left.get("subheader_source"), "bottom_band.left.subheader_source")
        for k, ln in enumerate((band.get("right") or {}).get("lines") or []):
            chk(f"{ln.get('lead', '')} {ln.get('text', '')}", "built_line", f"bottom_band.right.lines[{k}]")
            src_ok(ln.get("source"), f"bottom_band.right.lines[{k}]")
    dest = spec.get("destination") or {}
    if dest.get("mode", "new") not in ("new", "append"):
        errs.append("destination.mode must be new or append")
    if dest.get("mode") == "append" and not dest.get("presentation_id"):
        errs.append("destination.presentation_id is required for append")
    if isinstance(spec.get("notes"), str) and not spec["notes"].strip():
        errs.append("notes: empty; every number and quote needs a sourced talk-track line")
    return errs


# ---------------------------------------------------------------- request builder
class Slide:
    def __init__(self, slide_id, run):
        self.slide_id, self.run, self.n = slide_id, run, 0
        self.reqs, self.report, self.warnings = [], [], []

    def _id(self):
        self.n += 1
        return f"jm{self.run}_{self.n:04d}"

    def _el(self, x, y, w, h, sy=1):
        return {"pageObjectId": self.slide_id,
                "size": {"width": {"magnitude": pt_to_emu(w), "unit": "EMU"},
                         "height": {"magnitude": pt_to_emu(h), "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": sy, "translateX": pt_to_emu(x),
                              "translateY": pt_to_emu(y), "unit": "EMU"}}

    def box(self, kind, x, y, w, h, segments=None, size=8, fill=None, outline=None,
            shape="RECTANGLE", align="START", valign="TOP", color_key="ink"):
        """segments: [(text, style)] where style may set size/bold/italic/color/url."""
        oid = self._id()
        self.report.append((kind, round(x, 1), round(y, 1), round(w, 1), round(h, 1)))
        self.reqs.append({"createShape": {"objectId": oid,
                                          "shapeType": shape if (fill or outline) else "TEXT_BOX",
                                          "elementProperties": self._el(x, y, w, h)}})
        props, fields = {"contentAlignment": valign}, ["contentAlignment"]
        if fill:
            props["shapeBackgroundFill"] = {"solidFill": {"color": color(fill)}}
            fields.append("shapeBackgroundFill.solidFill.color")
        if outline:
            props["outline"] = {"outlineFill": {"solidFill": {"color": color(outline)}},
                                "weight": {"magnitude": 1, "unit": "PT"}}
            fields += ["outline.outlineFill.solidFill.color", "outline.weight"]
        elif fill:
            props["outline"] = {"outlineFill": {"solidFill": {"alpha": 0}}}
            fields.append("outline")
        self.reqs.append({"updateShapeProperties": {"objectId": oid, "shapeProperties": props,
                                                    "fields": ",".join(fields)}})
        if not segments:
            return oid
        text = "".join(t for t, _ in segments)
        self.reqs.append({"insertText": {"objectId": oid, "text": text}})
        self.reqs.append({"updateTextStyle": {
            "objectId": oid, "textRange": {"type": "ALL"},
            "style": {"fontFamily": HH_FONT, "bold": False, "italic": False,
                      "fontSize": {"magnitude": size, "unit": "PT"},
                      "foregroundColor": {"opaqueColor": color(color_key)}},
            "fields": "fontFamily,bold,italic,fontSize,foregroundColor"}})
        self.reqs.append({"updateParagraphStyle": {"objectId": oid, "textRange": {"type": "ALL"},
                                                   "style": {"alignment": align}, "fields": "alignment"}})
        pos = 0
        for t, st in segments:
            n = u16(t)
            if st and n:
                style, f = {}, []
                for key in ("bold", "italic"):
                    if key in st:
                        style[key] = st[key]
                        f.append(key)
                if "size" in st:
                    style["fontSize"] = {"magnitude": st["size"], "unit": "PT"}
                    f.append("fontSize")
                if "color" in st:
                    style["foregroundColor"] = {"opaqueColor": color(st["color"])}
                    f.append("foregroundColor")
                if "url" in st:
                    style["link"] = {"url": st["url"]}
                    f.append("link")
                if "font" in st:
                    style["fontFamily"] = st["font"]
                    f.append("fontFamily")
                if f:
                    self.reqs.append({"updateTextStyle": {
                        "objectId": oid,
                        "textRange": {"type": "FIXED_RANGE", "startIndex": pos, "endIndex": pos + n},
                        "style": style, "fields": ",".join(f)}})
            pos += n
        return oid

    def curve(self, x1, y1, x2, y2):
        oid = self._id()
        w = max(x2 - x1, 1)
        el = self._el(x1, y1, w, max(abs(y2 - y1), 1), sy=1 if y2 >= y1 else -1)
        self.reqs.append({"createLine": {"objectId": oid, "lineCategory": "CURVED", "elementProperties": el}})
        self.reqs.append({"updateLineProperties": {"objectId": oid, "lineProperties": {
            "lineFill": {"solidFill": {"color": color("ink")}}, "weight": {"magnitude": 2, "unit": "PT"}},
            "fields": "lineFill.solidFill.color,weight"}})


# ---------------------------------------------------------------- layout
def build(spec, slide_id, run, footer_reqs_fn=None):
    s = Slide(slide_id, run)
    sources = spec.get("sources") or {}
    order = []  # footnote numbering by first appearance

    def mark(ref):
        if ref is None:
            return ""
        if ref not in order:
            order.append(ref)
        return sup(order.index(ref) + 1)

    s.reqs.append({"updatePageProperties": {"objectId": slide_id, "pageProperties": {
        "pageBackgroundFill": {"solidFill": {"color": color("white")}}},
        "fields": "pageBackgroundFill.solidFill.color"}})
    s.box("title", M, TITLE_Y, W - 2 * M, TITLE_H, [(spec["title"], {"bold": True})], size=TITLE_PT)

    # personas
    personas = spec["personas"]
    by_key = {p["key"]: p for p in personas}
    s.box("persona_band", M, PERSONA_Y, W - 2 * M, PERSONA_H, fill="theme:LIGHT2", outline="line")
    slot = (W - 2 * M) / len(personas)
    for i, p in enumerate(personas):
        px = M + 8 + i * slot
        # Slides silently skips drawing a glyph that doesn't fit inside the text box after its ~7pt
        # insets, so the emoji sits in its own larger box centered over a text-free circle.
        s.box("avatar", px, PERSONA_Y + 6, 32, 32,
              fill=p.get("color", "sage_accent" if i == 0 else "blue_mid"), shape="ELLIPSE")
        s.box("avatar_glyph", px - 6, PERSONA_Y, 44, 44, [(p["avatar"], {"font": "Arial"})], size=16,
              align="CENTER", valign="MIDDLE")
        s.box("persona_text", px + 38, PERSONA_Y + 1, slot - 50, PERSONA_H - 2,
              [(p["name"], {"bold": True, "size": 9.5}), ("\n" + p["description"], {})],
              size=8, valign="MIDDLE")

    # columns + step lines
    stages = spec["stages"]
    n = len(stages)
    col_w = (W - 2 * M - COL_GAP * (n - 1)) / n
    band = spec.get("bottom_band")
    col_bottom = COL_BOTTOM_WITH_BAND if band else COL_BOTTOM_NO_BAND
    band_bottom = col_bottom - 6

    def col_x(i):
        return M + i * (col_w + COL_GAP)

    # step text: each column sized to its own text, so callouts start right under it
    step_segs, step_h = [], []
    for i, st in enumerate(stages):
        segs = []
        for j, ln in enumerate(st["lines"]):
            segs.append((("\n" if j else "") + by_key[ln["persona"]]["short"] + ":",
                         {"bold": True, "color": "sage_accent"}))
            segs.append((" " + ln["text"], {}))
        need = est_height([(p, 7.5, False) for p in "".join(t for t, _ in segs).split("\n")], col_w - 4)
        if need > STEP_MAX:
            raise LayoutError(f"stages[{i}].lines need {need:.0f}pt of step text (max {STEP_MAX:.0f}); shorten them")
        step_segs.append(segs)
        step_h.append(max(STEP_MIN, need))
    col_top = [COL_TOP + HDR_H + h + 6.0 for h in step_h]   # where each column's callout space begins

    # curve: sentiment maps to one shared scale that starts as high as the shortest step text
    # allows; if the curve would touch any column's step text, the whole scale shifts down
    curve_top = min(col_top) + 8
    for _ in range(12):
        span = band_bottom - curve_top - 24
        centers = [(col_x(i) + col_w / 2, curve_top + 12 + (st["sentiment"] - 1) / 4.0 * span)
                   for i, st in enumerate(stages)]
        pts = [(M + 2, centers[0][1] + 6)] + keep_extrema(centers) + [(RIGHT, centers[-1][1] - 6)]
        samples = curve_samples(pts)
        clash = max(col_top[i] + 4 - curve_span(samples, col_x(i), col_x(i) + col_w)[0] for i in range(n))
        if clash <= 0:
            break
        curve_top += clash
    else:
        raise LayoutError("the curve cannot clear the step text; shorten the longest stage lines")

    for i, st in enumerate(stages):
        x = col_x(i)
        s.box("column", x, COL_TOP, col_w, col_bottom - COL_TOP, fill=COLUMN_FILLS[i % len(COLUMN_FILLS)])
        s.box("stage_header", x, COL_TOP, col_w, HDR_H, [(f"{i + 1}  {st['name']}", {"bold": True})],
              size=9.5, align="CENTER", valign="MIDDLE")
        s.box("rule", x, COL_TOP + HDR_H, col_w, 1.5, fill="white")
        s.box("steps", x + 2, COL_TOP + HDR_H + 2, col_w - 4, step_h[i], step_segs[i], size=7.5)

    curve = spec["curve"]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        s.curve(xa, ya, xb, yb)
    if curve.get("markers", True):
        # 30pt-wide boxes: a 12pt glyph needs >= ~27pt of box width to survive the insets
        s.box("marker_good", 0, curve_top - 6, 30, 28, [("\U0001F642", {"font": "Arial"})], size=12,
              align="CENTER", valign="MIDDLE")
        s.box("marker_bad", 0, band_bottom - 22, 30, 28, [("\U0001F641", {"font": "Arial"})], size=12,
              align="CENTER", valign="MIDDLE")

    # callouts: clear of the curve when possible. A callout may be tucked over the curve (the line
    # passes behind its white box) only if it is alone in its column, and at most once per slide.
    first_above, tucked, heights = False, [], []
    for i, st in enumerate(stages):
        xa = col_x(i) + 6
        cw = col_w - 12
        cmin, cmax = curve_span(samples, xa, xa + cw)
        above_bottom = cmin - CURVE_CLEARANCE
        below_top = cmax + CURVE_CLEARANCE
        top_i = col_top[i]
        cursor = {"above": top_i, "below": below_top}
        taken = []  # (y0, y1) already used in this column
        callouts = st.get("callouts") or []

        def free(y, h):
            return top_i <= y and y + h <= band_bottom and all(y + h + 4 <= a or y >= b + 4 for a, b in taken)

        for j, c in enumerate(callouts):
            h = callout_height(c, cw)
            room = {"above": above_bottom - cursor["above"], "below": band_bottom - cursor["below"]}
            pref = c.get("position") or max(room, key=room.get)
            other = "below" if pref == "above" else "above"
            y = None
            for side in ([pref] if c.get("position") else [pref, other]):
                if h <= room[side] and free(cursor[side], h):
                    y = cursor[side]
                    break
            if y is None:
                if len(callouts) > 1:
                    raise LayoutError(
                        f"stages[{i}] has 2 callouts but callouts[{j}] can't clear the curve; the line would "
                        "weave between the boxes. Move one callout to notes, or shorten both")
                for cand in (cursor["above"], band_bottom - h, cursor["below"]):
                    if free(cand, h):
                        y = cand
                        break
                if y is None:
                    raise LayoutError(
                        f"stages[{i}].callouts[{j}] needs {h:.0f}pt and the column has no free space; "
                        "shorten it or move it to notes")
                tucked.append(f"stages[{i}].callouts[{j}]")
            draw_callout(s, c, xa, y, cw, h, mark)
            taken.append((y, y + h))
            if c["type"] != "exchange":
                heights.append((h, f"stages[{i}].callouts[{j}]"))
            side_used = "above" if y + h <= cmin else "below"
            cursor[side_used] = max(cursor[side_used], y + h + 6)
            if i == 0 and y + h <= centers[0][1]:
                first_above = True
        first_below_steps = min([a for a, _ in taken] + [cmin])
        if first_below_steps - top_i > DEAD_SPACE_MAX:
            s.warnings.append(f"stages[{i}]: {first_below_steps - top_i:.0f}pt of empty space under the step text "
                              f"(limit {DEAD_SPACE_MAX:.0f}); a FAIL in visual QA unless the column is deliberately sparse")
    if len(tucked) > 1:
        raise LayoutError(f"{len(tucked)} callouts would sit over the curve ({', '.join(tucked)}); the limit is 1. "
                          "Move callouts to notes, shorten them, or ask the user whether a stage's sentiment is right")
    for t in tucked:
        s.warnings.append(f"{t} sits over the curve; visual QA must confirm the line still reads")
    if len(heights) > 1:
        median = sorted(h for h, _ in heights)[len(heights) // 2]
        for h, where in heights:
            if h > 1.5 * median:
                s.warnings.append(f"{where} is {h / median:.1f}x the median callout height; tighten its copy")
    label_y = (centers[0][1] + 10) if first_above else (centers[0][1] - 16)
    s.box("curve_label", M + 4, label_y, 90, 14, [(curve.get("label", "Experience"), {"italic": True})], size=7.5)

    # bottom band
    if band:
        s.box("bottom_band", M, BOTTOM_Y, W - 2 * M, BOTTOM_H, fill="theme:LIGHT2", outline="line")
        left, right = band.get("left"), band.get("right")
        left_w = 320.0 if right else W - 2 * M - 16
        if left:
            hdr = [(left.get("header", "What it costs"), {"bold": True, "size": 9})]
            if left.get("subheader"):
                hdr.append((" (" + left["subheader"] + mark(left.get("subheader_source")) + ")", {"size": 7}))
            s.box("cost_header", M + 8, BOTTOM_Y + 1, left_w, 14, hdr, size=9, color_key="sage_accent")
            stats = left["stats"]
            sw = left_w / len(stats)
            for k, stt in enumerate(stats):
                sx = M + 8 + k * sw
                # labels get extra width (text is left-aligned, so overlap into the next slot is blank space)
                lw = min(sw + 18, left_w - k * sw)
                label = stt["label"] + mark(stt.get("source"))
                if est_lines(label, 6.5, lw) > 2:
                    raise LayoutError(f"bottom_band.left.stats[{k}].label wraps past 2 lines; shorten it")
                s.box("cost_value", sx, BOTTOM_Y + 12, sw - 2, 18, [(stt["value"], {"bold": True})],
                      size=13, color_key="sage_accent")
                s.box("cost_label", sx, BOTTOM_Y + 29, lw, 20, [(label, {})], size=6.5)
        if right:
            rx = M + 8 + left_w + 10 if left else M + 8
            if left:
                s.box("band_rule", rx - 6, BOTTOM_Y, 1, BOTTOM_H, fill="line")
            s.box("built_header", rx, BOTTOM_Y, RIGHT - rx - 6, 13,
                  [(right.get("header", "What we built"), {"bold": True})], size=9, color_key="sage_accent")
            segs = []
            for k, ln in enumerate(right.get("lines") or []):
                segs.append((("\n" if k else "") + ln.get("lead", ""), {"bold": True}))
                segs.append((" " + ln["text"] + mark(ln.get("source")), {}))
            lines_h = BOTTOM_H - 13
            need = est_height([(p, 7.5, False) for p in "".join(t for t, _ in segs).split("\n")], RIGHT - rx - 6)
            if need > lines_h + 10:
                raise LayoutError(f"bottom_band.right.lines need {need:.0f}pt (have {lines_h:.0f}); shorten them")
            s.box("built_lines", rx, BOTTOM_Y + 12, RIGHT - rx - 6, lines_h, segs, size=7.5)

    # fine print
    if order:
        segs = [("Sources:", {"bold": True})]
        for k, ref in enumerate(order, start=1):
            segs.append((("  " if k > 1 else " ") + sup(k) + " ", {}))
            segs.append((sources[ref]["label"], {"url": sources[ref]["url"]}))
        flat = "".join(t for t, _ in segs)
        if est_lines(flat, FINE_PT, W - 2 * M) > 2:
            raise LayoutError("fine print wraps past 2 lines; shorten source labels")
        s.box("fine_print", M, FINE_Y, W - 2 * M, FINE_H, segs, size=FINE_PT)
    if footer_reqs_fn:
        s.reqs += footer_reqs_fn(slide_id)
    return s, order


class LayoutError(Exception):
    pass


def callout_height(c, w):
    t = c["type"]
    if t == "stat":
        paras = [(c["text"] + "x", 9, True)] + ([(c["detail"], 7.5, False)] if c.get("detail") else [])
    elif t == "bullets":
        paras = [("• " + it["text"].replace("**", "") + "x", 8, False) for it in c["items"]]
    elif t == "quote":
        paras = [("“" + c["text"] + "”", 8, False), (c["attribution"] + "x", 7, True)]
    elif t == "research":
        paras = [(c["text"], 8, False), (c["citation"] + "x", 6.5, False)]
    else:  # exchange: caption + one bubble per turn, 4pt gaps
        return caption_height(c, w) + 2 + sum(
            est_height([(tn["speaker"] + ": “" + tn["text"] + "”", 7.5, False)], w) + 4
            for tn in c["turns"])
    return est_height(paras, w)


def caption_height(c, w):
    cap = c.get("caption", "Real exchange, de-identified") + "x"
    return est_lines(cap, 7, w, bold=True) * 7 * 1.22 + 6


def draw_callout(s, c, x, y, w, h, mark):
    t = c["type"]
    if t == "stat":
        segs = [(c["text"] + mark(c.get("source")), {"bold": True, "size": 9, "color": "sage_accent"})]
        if c.get("detail"):
            segs.append(("\n" + c["detail"], {"size": 7.5}))
        s.box("stat", x, y, w, h, segs, fill="white", outline="sage_accent", shape="ROUND_RECTANGLE",
              align="CENTER", valign="MIDDLE")
    elif t == "bullets":
        segs = []
        for k, it in enumerate(c["items"]):
            segs.append((("\n" if k else "") + "• ", {}))
            segs += parse_markup(it["text"])
            segs.append((mark(it.get("source")), {}))
        s.box("bullets", x, y, w, h, segs, size=8, fill="white", outline="sage_accent",
              shape="ROUND_RECTANGLE", valign="MIDDLE")
    elif t == "quote":
        segs = [("“" + c["text"] + "”", {"italic": True}),
                ("\n" + c["attribution"] + mark(c.get("source")), {"bold": True, "size": 7, "color": "sage_accent"})]
        s.box("quote", x, y, w, h, segs, size=8, fill="white", outline="ink",
              shape="WEDGE_ROUND_RECTANGLE_CALLOUT", align="CENTER", valign="MIDDLE")
    elif t == "research":
        segs = [(c["text"], {}), ("\n" + c["citation"] + mark(c.get("source")), {"size": 6.5})]
        s.box("research", x, y, w, h, segs, size=8, fill="white", outline="sage_accent",
              shape="ROUND_RECTANGLE", align="CENTER", valign="MIDDLE")
    elif t == "exchange":
        cap = c.get("caption", "Real exchange, de-identified") + mark(c.get("source"))
        cap_h = caption_height(c, w)
        s.box("exchange_caption", x, y, w, cap_h, [(cap, {"bold": True})],
              size=7, align="CENTER", color_key="sage_accent")
        cy = y + cap_h + 2
        for k, tn in enumerate(c["turns"]):
            body = tn["speaker"] + ": “" + tn["text"] + "”"
            th = est_height([(body, 7.5, False)], w)
            alt = k % 2 == 1
            s.box("exchange_turn", x, cy, w, th,
                  [(tn["speaker"] + ":", {"bold": True}), (" “" + tn["text"] + "”", {"italic": True, "bold": alt})],
                  size=7.5, fill="blue_panel" if alt else "white", outline="blue_mid" if alt else "ink",
                  shape="WEDGE_ROUND_RECTANGLE_CALLOUT", align="CENTER", valign="MIDDLE")
            cy += th + 4


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("spec")
    ap.add_argument("--dry-run", action="store_true", help="validate and print layout; no API calls")
    args = ap.parse_args()
    spec = json.loads(Path(args.spec).read_text())

    errs = validate(spec)
    if errs:
        print("Spec validation failed:\n  " + "\n  ".join(errs), file=sys.stderr)
        return 1
    run = format(int(time.time() * 1000) % 16 ** 7, "x")  # unique object-id prefix per run
    slide_id = f"jm{run}_slide"
    try:
        slide, order = build(spec, slide_id, run)
    except LayoutError as e:
        print(f"Layout failed: {e}", file=sys.stderr)
        return 1
    print("Layout (kind, x, y, w, h):", file=sys.stderr)
    for row in slide.report:
        print("  " + ", ".join(str(v) for v in row), file=sys.stderr)
    print("Footnotes: " + ", ".join(f"{sup(i + 1)} {r}" for i, r in enumerate(order)), file=sys.stderr)
    for w in slide.warnings:
        print(f"WARN: {w}", file=sys.stderr)
    unused = sorted(set(spec.get("sources") or {}) - set(order))
    if unused:
        print(f"WARN: sources defined but never cited on the slide (dropped from fine print): {', '.join(unused)}",
              file=sys.stderr)
    if args.dry_run:
        print("Dry run OK", file=sys.stderr)
        return 0

    from slides_client import SlidesClient  # needs google-api-python-client + OAuth
    c = SlidesClient()
    dest = spec.get("destination") or {}
    if dest.get("mode", "new") == "append":
        pid = dest["presentation_id"]
        if dest.get("replace_slide_id"):
            c._batch(pid, [{"deleteObject": {"objectId": dest["replace_slide_id"]}}])
        n_slides = len(c.slides.presentations().get(presentationId=pid).execute().get("slides", []))
        index = dest.get("insert_index", n_slides)
    else:
        pid = c.create_deck(dest.get("deck_title", spec["title"]), parent_folder_id=dest.get("parent_folder_id"))
        c.delete_default_first_slide(pid)  # deletes by position, so it must run before our insert
        index = 0
    slide, order = build(spec, slide_id, run, footer_reqs_fn=c._add_footer_reqs)
    create = [{"createSlide": {"objectId": slide_id, "insertionIndex": index,
                               "slideLayoutReference": {"predefinedLayout": "BLANK"}}}]
    c._batch(pid, create + slide.reqs)
    if spec.get("notes"):
        c._set_notes_on_slide_object(pid, slide_id, spec["notes"])
    print(f"presentation_id={pid} slide_id={slide_id}", file=sys.stderr)
    print(f"{c.url(pid)}#slide=id.{slide_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
