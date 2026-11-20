"""Native Google Slides client with hims & hers brand styling.

Canvas: 720 x 405 pt (Google Slides default 16:9 widescreen at 10 inches).
The Slides API silently ignores `pageSize` in create() calls, so we cannot
force the larger 13.333" canvas the style guide spec assumes. All
coordinates below are scaled for the API default canvas.

Setup:
  OAuth desktop-app credentials at ~/.config/gcloud/slides-oauth.json
  Token cached at ~/.config/gcloud/slides-token.json (auto-created)

Two layers:
  1. SlidesClient generic methods (create_deck, add_bullets_slide, etc.)
     for ad-hoc decks with default Slides theme.
  2. hh_* methods that build slides matching the hims & hers style guide
     (Poppins, sage/beige palette, confidentiality footer, BLANK layouts,
     explicit shape placement). Use these by default for PM decks.

Edit-existing-deck methods live on SlidesClient too: get_deck_outline,
delete_slide_at, reorder_slide, replace_text_on_slide, add_speaker_notes,
get_speaker_notes, replace_image_on_slide. All slide_index args are
1-indexed for human readability.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",
]

CREDS_DIR = Path.home() / ".config" / "gcloud"
OAUTH_CLIENT_PATH = CREDS_DIR / "slides-oauth.json"
TOKEN_PATH = CREDS_DIR / "slides-token.json"

# hims & hers palette (hex, no leading #)
HH = {
    "ink": "1C1C1C",
    "black": "000000",
    "white": "FFFFFF",
    "off_white": "FBF8F5",
    "warm_cream": "FAF9F5",
    "sage_tint": "F5FAF6",
    "sage_light": "D9EAD3",
    "sage_accent": "0097A7",
    "blue_header": "99B3CD",
    "blue_powder": "D5E3EE",
    "blue_panel": "ECF2F6",
    "blue_mid": "84ADCD",
    "beige": "EEE2D6",
    "warm_gray": "D7D7D2",
    "line": "D9D9D9",
    "light_fill": "EFEFEF",
}

HH_FONT = "Poppins"
HH_FOOTER = (
    "[Company confidentiality footer]"
)

# Slide canvas: 16:9 widescreen, 720 x 405 pt (Slides API default; not configurable).
SLIDE_W_PT = 720.0
SLIDE_H_PT = 405.0
EMU_PER_PT = 12700

# Standard content-slide layout grid (used by every hh_* template):
#   - 30pt outer margin on all sides
#   - Title row: y=22, h=66 -> ends y=88
#   - Lead row (optional): y=95, h=55 -> ends y=150
#   - Body start: y=95 (no lead) or y=158 (with lead)
#   - Footer: y=388, h=10 (small)


def pt_to_emu(n: float) -> int:
    return int(round(n * EMU_PER_PT))


def hex_to_rgb(hex_str: str) -> dict:
    h = hex_str.lstrip("#")
    return {
        "red": int(h[0:2], 16) / 255.0,
        "green": int(h[2:4], 16) / 255.0,
        "blue": int(h[4:6], 16) / 255.0,
    }


class SlidesClient:
    def __init__(self, oauth_client_path: Path = OAUTH_CLIENT_PATH, token_path: Path = TOKEN_PATH):
        self.oauth_client_path = oauth_client_path
        self.token_path = token_path
        self._slides = None
        self._drive = None
        self._obj_counter = 0

    # ---------- auth & service handles ----------

    def _auth(self) -> Credentials:
        creds: Credentials | None = None
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.oauth_client_path.exists():
                    raise FileNotFoundError(
                        f"OAuth client JSON missing at {self.oauth_client_path}. "
                        "Download a Desktop-app OAuth client from GCP Console and save it there."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(str(self.oauth_client_path), SCOPES)
                creds = flow.run_local_server(port=0)
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            self.token_path.write_text(creds.to_json())
            os.chmod(self.token_path, 0o600)
        return creds

    @property
    def slides(self):
        if self._slides is None:
            self._slides = build("slides", "v1", credentials=self._auth(), cache_discovery=False)
        return self._slides

    @property
    def drive(self):
        if self._drive is None:
            self._drive = build("drive", "v3", credentials=self._auth(), cache_discovery=False)
        return self._drive

    # ---------- deck-level ----------

    def create_deck(self, title: str, parent_folder_id: str | None = None) -> str:
        # Note: pageSize cannot be set via create() - the API silently ignores it.
        # All hh_* methods are calibrated for the default 720x405 pt canvas.
        pres = self.slides.presentations().create(body={"title": title}).execute()
        pid = pres["presentationId"]
        if parent_folder_id:
            f = self.drive.files().get(fileId=pid, fields="parents").execute()
            prev = ",".join(f.get("parents", []))
            self.drive.files().update(
                fileId=pid,
                addParents=parent_folder_id,
                removeParents=prev,
                fields="id, parents",
            ).execute()
        return pid

    def url(self, presentation_id: str) -> str:
        return f"(internal link)"

    def _batch(self, presentation_id: str, requests: list[dict]) -> dict:
        """Execute a Slides batchUpdate with retry-with-backoff on quota errors.

        Slides API counts each batchUpdate as one write (regardless of how many
        ops are inside). Quota is 60 writes/min/user by default; if hit, sleep
        and retry up to 5 times with exponential backoff.
        """
        import time
        from googleapiclient.errors import HttpError as _HttpError

        max_retries = 5
        for attempt in range(max_retries):
            try:
                return (
                    self.slides.presentations()
                    .batchUpdate(presentationId=presentation_id, body={"requests": requests})
                    .execute()
                )
            except _HttpError as e:
                status = getattr(getattr(e, "resp", None), "status", None)
                if status == 429 and attempt < max_retries - 1:
                    wait = 65 + attempt * 20  # 65, 85, 105, 125
                    import sys as _sys
                    print(
                        f"[slides_client] quota hit on batch ({attempt + 1}/{max_retries}); "
                        f"sleeping {wait}s before retry",
                        file=_sys.stderr,
                    )
                    time.sleep(wait)
                    continue
                raise
        raise RuntimeError("Max retries exceeded on _batch (quota)")

    def _next_id(self, prefix: str) -> str:
        self._obj_counter += 1
        return f"{prefix}_{self._obj_counter:05d}"

    def delete_default_first_slide(self, presentation_id: str) -> None:
        pres = self.slides.presentations().get(presentationId=presentation_id).execute()
        slides = pres.get("slides", [])
        if slides:
            first_id = slides[0]["objectId"]
            self._batch(presentation_id, [{"deleteObject": {"objectId": first_id}}])

    # ---------- generic slide layouts (default Slides theme) ----------
    # Kept for ad-hoc use; not branded.

    def _new_slide(self, presentation_id: str, layout: str) -> tuple[str, list[str]]:
        resp = self._batch(
            presentation_id,
            [{"createSlide": {"slideLayoutReference": {"predefinedLayout": layout}}}],
        )
        slide_id = resp["replies"][0]["createSlide"]["objectId"]
        pres = self.slides.presentations().get(presentationId=presentation_id).execute()
        slide = next(s for s in pres["slides"] if s["objectId"] == slide_id)
        placeholder_ids = [el["objectId"] for el in slide.get("pageElements", []) if "shape" in el]
        return slide_id, placeholder_ids

    def _insert_text(self, object_id: str, text: str) -> dict:
        return {"insertText": {"objectId": object_id, "text": text}}

    def add_title_slide(self, presentation_id: str, title: str, subtitle: str | None = None) -> str:
        slide_id, placeholders = self._new_slide(presentation_id, "TITLE")
        reqs = []
        if placeholders:
            reqs.append(self._insert_text(placeholders[0], title))
        if subtitle and len(placeholders) > 1:
            reqs.append(self._insert_text(placeholders[1], subtitle))
        if reqs:
            self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    def add_section_header(self, presentation_id: str, title: str) -> str:
        slide_id, placeholders = self._new_slide(presentation_id, "SECTION_HEADER")
        if placeholders:
            self._batch(presentation_id, [self._insert_text(placeholders[0], title)])
        return slide_id

    def add_bullets_slide(self, presentation_id: str, title: str, bullets: Iterable[str]) -> str:
        slide_id, placeholders = self._new_slide(presentation_id, "TITLE_AND_BODY")
        bullets = list(bullets)
        reqs: list[dict] = []
        if placeholders:
            reqs.append(self._insert_text(placeholders[0], title))
        if bullets and len(placeholders) > 1:
            body_id = placeholders[1]
            reqs.append(self._insert_text(body_id, "\n".join(bullets)))
            reqs.append(
                {
                    "createParagraphBullets": {
                        "objectId": body_id,
                        "textRange": {"type": "ALL"},
                        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                    }
                }
            )
        if reqs:
            self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    def add_two_column_slide(
        self,
        presentation_id: str,
        title: str,
        left: Iterable[str],
        right: Iterable[str],
    ) -> str:
        slide_id, placeholders = self._new_slide(presentation_id, "TITLE_AND_TWO_COLUMNS")
        left, right = list(left), list(right)
        reqs: list[dict] = []
        if placeholders:
            reqs.append(self._insert_text(placeholders[0], title))
        if len(placeholders) > 1 and left:
            reqs.append(self._insert_text(placeholders[1], "\n".join(left)))
            reqs.append(
                {
                    "createParagraphBullets": {
                        "objectId": placeholders[1],
                        "textRange": {"type": "ALL"},
                        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                    }
                }
            )
        if len(placeholders) > 2 and right:
            reqs.append(self._insert_text(placeholders[2], "\n".join(right)))
            reqs.append(
                {
                    "createParagraphBullets": {
                        "objectId": placeholders[2],
                        "textRange": {"type": "ALL"},
                        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                    }
                }
            )
        if reqs:
            self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    def add_image_slide(self, presentation_id: str, title: str, image_url: str, notes: str | None = None) -> str:
        slide_id, placeholders = self._new_slide(presentation_id, "TITLE_AND_BODY")
        reqs: list[dict] = []
        if placeholders:
            reqs.append(self._insert_text(placeholders[0], title))
        reqs.append(
            {
                "createImage": {
                    "url": image_url,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": 4500000, "unit": "EMU"},
                            "height": {"magnitude": 2531000, "unit": "EMU"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 1125000,
                            "translateY": 1125000,
                            "unit": "EMU",
                        },
                    },
                }
            }
        )
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---------- hims & hers themed slides ----------
    # BLANK layout + explicit shapes. Calibrated for 720x405 pt canvas.

    def _blank_slide_reqs(self, slide_id: str, background_hex: str | None = None) -> list[dict]:
        """Return the createSlide (+ optional updatePageProperties) requests without executing.

        Used by hh_* templates so all slide-construction requests can ship in
        ONE batchUpdate call instead of two. Each batchUpdate counts as one
        write against the 60/min/user quota; bundling reduces quota pressure.
        """
        reqs: list[dict] = [
            {
                "createSlide": {
                    "objectId": slide_id,
                    "slideLayoutReference": {"predefinedLayout": "BLANK"},
                }
            }
        ]
        if background_hex:
            reqs.append(
                {
                    "updatePageProperties": {
                        "objectId": slide_id,
                        "pageProperties": {
                            "pageBackgroundFill": {
                                "solidFill": {"color": {"rgbColor": hex_to_rgb(background_hex)}}
                            }
                        },
                        "fields": "pageBackgroundFill.solidFill.color",
                    }
                }
            )
        return reqs

    def _blank_slide(
        self,
        presentation_id: str,
        background_hex: str | None = None,
        notes_text: str | None = None,
    ) -> str:
        """Auto-batched convenience wrapper. hh_* templates prefer _blank_slide_reqs."""
        slide_id = self._next_id("slide")
        self._batch(presentation_id, self._blank_slide_reqs(slide_id, background_hex))
        if notes_text:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes_text)
        return slide_id

    # ---------- speaker notes (internal) ----------

    def _find_notes_body_id(self, presentation_id: str, slide_object_id: str) -> str | None:
        """Return the objectId of the notes BODY placeholder for the given slide.

        Each slide has a notesPage with a speakerNotesObjectId pointing to the
        notes body shape. Falls back to scanning the notesPage pageElements for
        a BODY placeholder when speakerNotesObjectId is absent.
        """
        pres = self.slides.presentations().get(presentationId=presentation_id).execute()
        for s in pres.get("slides", []):
            if s.get("objectId") != slide_object_id:
                continue
            # Slides API nests notesPage under slideProperties, not at slide top level.
            slide_props = s.get("slideProperties") or {}
            notes_page = slide_props.get("notesPage") or {}
            notes_props = notes_page.get("notesProperties") or {}
            speaker_id = notes_props.get("speakerNotesObjectId")
            if speaker_id:
                return speaker_id
            for el in notes_page.get("pageElements", []):
                shape = el.get("shape") or {}
                placeholder = shape.get("placeholder") or {}
                if placeholder.get("type") == "BODY":
                    return el.get("objectId")
            return None
        return None

    def _set_notes_on_slide_object(
        self,
        presentation_id: str,
        slide_object_id: str,
        notes_text: str,
    ) -> None:
        """Replace speaker-notes text on a slide identified by its objectId.

        Single batch: deleteText ALL then insertText. The deleteText leg is
        wrapped in try/except because empty ranges error out; we fall back to
        insertText only when the notes body is already empty.
        """
        notes_id = self._find_notes_body_id(presentation_id, slide_object_id)
        if not notes_id:
            return
        # Try delete + insert in one batch first
        try:
            self._batch(
                presentation_id,
                [
                    {"deleteText": {"objectId": notes_id, "textRange": {"type": "ALL"}}},
                    {"insertText": {"objectId": notes_id, "text": notes_text}},
                ],
            )
        except Exception:
            # Likely an empty-range error on deleteText; just insert.
            self._batch(
                presentation_id,
                [{"insertText": {"objectId": notes_id, "text": notes_text}}],
            )

    def _create_textbox_reqs(
        self,
        slide_id: str,
        x_pt: float,
        y_pt: float,
        w_pt: float,
        h_pt: float,
        text: str,
        font_size: float,
        bold: bool = False,
        color_hex: str = "1C1C1C",
        align: str = "START",
        font: str = HH_FONT,
    ) -> tuple[str, list[dict]]:
        obj_id = self._next_id("tb")
        reqs: list[dict] = [
            {
                "createShape": {
                    "objectId": obj_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": pt_to_emu(w_pt), "unit": "EMU"},
                            "height": {"magnitude": pt_to_emu(h_pt), "unit": "EMU"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": pt_to_emu(x_pt),
                            "translateY": pt_to_emu(y_pt),
                            "unit": "EMU",
                        },
                    },
                }
            },
            {"insertText": {"objectId": obj_id, "text": text}},
            {
                "updateTextStyle": {
                    "objectId": obj_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "fontFamily": font,
                        "bold": bold,
                        "fontSize": {"magnitude": font_size, "unit": "PT"},
                        "foregroundColor": {
                            "opaqueColor": {"rgbColor": hex_to_rgb(color_hex)}
                        },
                    },
                    "fields": "fontFamily,bold,fontSize,foregroundColor",
                }
            },
            {
                "updateParagraphStyle": {
                    "objectId": obj_id,
                    "textRange": {"type": "ALL"},
                    "style": {"alignment": align},
                    "fields": "alignment",
                }
            },
        ]
        return obj_id, reqs

    def _create_rect_reqs(
        self,
        slide_id: str,
        x_pt: float,
        y_pt: float,
        w_pt: float,
        h_pt: float,
        fill_hex: str,
        shape_type: str = "RECTANGLE",
    ) -> tuple[str, list[dict]]:
        obj_id = self._next_id("rect")
        reqs: list[dict] = [
            {
                "createShape": {
                    "objectId": obj_id,
                    "shapeType": shape_type,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": pt_to_emu(w_pt), "unit": "EMU"},
                            "height": {"magnitude": pt_to_emu(h_pt), "unit": "EMU"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": pt_to_emu(x_pt),
                            "translateY": pt_to_emu(y_pt),
                            "unit": "EMU",
                        },
                    },
                }
            },
            {
                "updateShapeProperties": {
                    "objectId": obj_id,
                    "shapeProperties": {
                        "shapeBackgroundFill": {
                            "solidFill": {"color": {"rgbColor": hex_to_rgb(fill_hex)}}
                        },
                        "outline": {"outlineFill": {"solidFill": {"alpha": 0}}},
                    },
                    "fields": "shapeBackgroundFill.solidFill.color,outline",
                }
            },
        ]
        return obj_id, reqs

    def _add_footer_reqs(self, slide_id: str) -> list[dict]:
        _, reqs = self._create_textbox_reqs(
            slide_id, x_pt=22, y_pt=390, w_pt=676, h_pt=12,
            text=HH_FOOTER, font_size=7, color_hex=HH["ink"], align="START",
        )
        return reqs

    # ---- Template A: Cover ----
    def hh_cover_slide(
        self,
        presentation_id: str,
        title: str,
        subtitle: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Cover slide: dark background, large title, optional subtitle, wordmark."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["ink"])
        _, t_reqs = self._create_textbox_reqs(
            slide_id, x_pt=30, y_pt=130, w_pt=660, h_pt=90,
            text=title, font_size=32, bold=True, color_hex=HH["white"], align="START",
        )
        reqs += t_reqs
        if subtitle:
            _, s_reqs = self._create_textbox_reqs(
                slide_id, x_pt=30, y_pt=230, w_pt=660, h_pt=45,
                text=subtitle, font_size=16, color_hex=HH["beige"], align="START",
            )
            reqs += s_reqs
        _, w_reqs = self._create_textbox_reqs(
            slide_id, x_pt=560, y_pt=370, w_pt=140, h_pt=22,
            text="hims & hers", font_size=11, bold=True, color_hex=HH["white"], align="END",
        )
        reqs += w_reqs
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- Template E: Section divider ----
    def hh_section_divider(
        self,
        presentation_id: str,
        title: str,
        subtitle: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Section divider: beige background, centered title and optional subtitle."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["beige"])
        _, t_reqs = self._create_textbox_reqs(
            slide_id, x_pt=45, y_pt=170, w_pt=630, h_pt=60,
            text=title, font_size=30, bold=True, color_hex=HH["ink"], align="CENTER",
        )
        reqs += t_reqs
        if subtitle:
            _, s_reqs = self._create_textbox_reqs(
                slide_id, x_pt=45, y_pt=235, w_pt=630, h_pt=40,
                text=subtitle, font_size=16, color_hex=HH["ink"], align="CENTER",
            )
            reqs += s_reqs
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- Shared content-slide title bar ----
    # All content slides use this. 30pt margin left, font 22pt, height 66pt
    # accommodates 2-line wrap at 1.2 line-height.
    def _content_title_reqs(self, slide_id: str, title: str) -> list[dict]:
        _, reqs = self._create_textbox_reqs(
            slide_id, x_pt=30, y_pt=22, w_pt=660, h_pt=66,
            text=title, font_size=22, bold=True, color_hex=HH["ink"], align="START",
        )
        return reqs

    # ---- Template B: Executive summary, 3 cards ----
    def hh_executive_summary(
        self,
        presentation_id: str,
        title: str,
        lead_paragraph: str,
        principles_header: str,
        cards: list[str],
        notes: str | None = None,
    ) -> str:
        """Executive summary: title, lead paragraph, sage panel with up to 3 card statements."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["white"])
        reqs += self._content_title_reqs(slide_id, title)
        # Lead at y=95, h=55 -> ends y=150 (handles ~3 lines at 12pt x 1.4 lh)
        _, lead_reqs = self._create_textbox_reqs(
            slide_id, x_pt=30, y_pt=95, w_pt=660, h_pt=55,
            text=lead_paragraph, font_size=12, color_hex=HH["ink"], align="START",
        )
        reqs += lead_reqs
        # Sage panel: y=160, h=215 -> ends y=375, well above footer at y=388
        _, panel_reqs = self._create_rect_reqs(
            slide_id, x_pt=30, y_pt=160, w_pt=660, h_pt=215, fill_hex=HH["sage_tint"]
        )
        reqs += panel_reqs
        _, hdr_reqs = self._create_textbox_reqs(
            slide_id, x_pt=30, y_pt=172, w_pt=660, h_pt=32,
            text=principles_header, font_size=17, bold=True,
            color_hex=HH["sage_accent"], align="CENTER",
        )
        reqs += hdr_reqs
        cards = cards[:3]
        n = len(cards)
        if n:
            margin = 45
            gap = 15
            avail = 660 - 2 * margin - gap * (n - 1)
            card_w = avail / n
            card_h = 140
            card_y = 215
            for i, txt in enumerate(cards):
                cx = 30 + margin + i * (card_w + gap)
                _, card_reqs = self._create_rect_reqs(
                    slide_id, x_pt=cx, y_pt=card_y, w_pt=card_w, h_pt=card_h,
                    fill_hex=HH["white"], shape_type="ROUND_RECTANGLE",
                )
                reqs += card_reqs
                _, ctxt_reqs = self._create_textbox_reqs(
                    slide_id, x_pt=cx + 10, y_pt=card_y + 45, w_pt=card_w - 20, h_pt=60,
                    text=txt, font_size=15, bold=True,
                    color_hex=HH["sage_accent"], align="CENTER",
                )
                reqs += ctxt_reqs
        reqs += self._add_footer_reqs(slide_id)
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- Template D: 2-column DO / DON'T ----
    def hh_do_dont_slide(
        self,
        presentation_id: str,
        title: str,
        dos: list[str],
        donts: list[str],
        notes: str | None = None,
    ) -> str:
        """Two-column DO / DON'T comparison."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["white"])
        reqs += self._content_title_reqs(slide_id, title)
        card_y = 110
        card_h = 265
        gap = 15
        card_w = (660 - gap) / 2
        _, do_bg = self._create_rect_reqs(
            slide_id, x_pt=30, y_pt=card_y, w_pt=card_w, h_pt=card_h,
            fill_hex=HH["blue_powder"], shape_type="ROUND_RECTANGLE",
        )
        reqs += do_bg
        _, do_label = self._create_textbox_reqs(
            slide_id, x_pt=45, y_pt=card_y + 12, w_pt=card_w - 30, h_pt=24,
            text="DO", font_size=14, bold=True, color_hex=HH["ink"],
        )
        reqs += do_label
        _, do_body = self._create_textbox_reqs(
            slide_id, x_pt=45, y_pt=card_y + 42, w_pt=card_w - 30, h_pt=card_h - 50,
            text="\n".join(f"• {d}" for d in dos), font_size=12, color_hex=HH["ink"],
        )
        reqs += do_body
        donts_x = 30 + card_w + gap
        _, dont_bg = self._create_rect_reqs(
            slide_id, x_pt=donts_x, y_pt=card_y, w_pt=card_w, h_pt=card_h,
            fill_hex=HH["warm_gray"], shape_type="ROUND_RECTANGLE",
        )
        reqs += dont_bg
        _, dont_label = self._create_textbox_reqs(
            slide_id, x_pt=donts_x + 15, y_pt=card_y + 12, w_pt=card_w - 30, h_pt=24,
            text="DON'T", font_size=14, bold=True, color_hex=HH["ink"],
        )
        reqs += dont_label
        _, dont_body = self._create_textbox_reqs(
            slide_id, x_pt=donts_x + 15, y_pt=card_y + 42, w_pt=card_w - 30, h_pt=card_h - 50,
            text="\n".join(f"• {d}" for d in donts), font_size=12, color_hex=HH["ink"],
        )
        reqs += dont_body
        reqs += self._add_footer_reqs(slide_id)
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- HH bullets ----
    def hh_bullets_slide(
        self,
        presentation_id: str,
        title: str,
        bullets: list[str],
        lead: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Title plus bulleted body, with optional lead paragraph."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["white"])
        reqs += self._content_title_reqs(slide_id, title)
        body_y = 100  # title (y=22, h=66) ends y=88, gap 12
        if lead:
            _, lead_reqs = self._create_textbox_reqs(
                slide_id, x_pt=30, y_pt=body_y, w_pt=660, h_pt=40,
                text=lead, font_size=13, color_hex=HH["ink"],
            )
            reqs += lead_reqs
            body_y = 150
        # Headline-style bullets: large, breathing room, narrative lives in speaker notes.
        body_text = "\n\n".join(f"• {b}" for b in bullets)
        _, body_reqs = self._create_textbox_reqs(
            slide_id, x_pt=30, y_pt=body_y, w_pt=660, h_pt=380 - body_y,
            text=body_text, font_size=20, bold=True, color_hex=HH["ink"],
        )
        reqs += body_reqs
        reqs += self._add_footer_reqs(slide_id)
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- HH 2-column ----
    def hh_two_column_slide(
        self,
        presentation_id: str,
        title: str,
        left_header: str,
        left_bullets: list[str],
        right_header: str,
        right_bullets: list[str],
        notes: str | None = None,
    ) -> str:
        """Two-column layout with section headers and bullet lists."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["white"])
        reqs += self._content_title_reqs(slide_id, title)
        gap = 22
        col_w = (660 - gap) / 2
        top = 108  # title ends y=88, gap 20
        for i, (hdr, bullets) in enumerate(
            [(left_header, left_bullets), (right_header, right_bullets)]
        ):
            cx = 30 + i * (col_w + gap)
            _, h_reqs = self._create_textbox_reqs(
                slide_id, x_pt=cx, y_pt=top, w_pt=col_w, h_pt=30,
                text=hdr, font_size=16, bold=True, color_hex=HH["sage_accent"],
            )
            reqs += h_reqs
            _, b_reqs = self._create_textbox_reqs(
                slide_id, x_pt=cx, y_pt=top + 38, w_pt=col_w, h_pt=232,
                text="\n\n".join(f"• {b}" for b in bullets), font_size=15, bold=True, color_hex=HH["ink"],
            )
            reqs += b_reqs
        reqs += self._add_footer_reqs(slide_id)
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- Template: flow_steps (numbered horizontal stepper) ----
    def hh_flow_steps_slide(
        self,
        presentation_id: str,
        title: str,
        steps: list[str],
        lead: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Numbered horizontal stepper with up to 5 steps."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["white"])
        reqs += self._content_title_reqs(slide_id, title)
        body_top = 100
        if lead:
            _, lead_reqs = self._create_textbox_reqs(
                slide_id, x_pt=30, y_pt=body_top, w_pt=660, h_pt=45,
                text=lead, font_size=12, color_hex=HH["ink"],
            )
            reqs += lead_reqs
            body_top = 155
        steps = steps[:5]
        n = len(steps)
        if n:
            margin = 30
            gap = 15
            avail = 660 - 2 * margin - gap * (n - 1)
            col_w = avail / n
            circle_size = 52
            for i, step_text in enumerate(steps):
                cx = 30 + margin + i * (col_w + gap)
                circle_x = cx + (col_w - circle_size) / 2
                _, c_reqs = self._create_rect_reqs(
                    slide_id, x_pt=circle_x, y_pt=body_top, w_pt=circle_size, h_pt=circle_size,
                    fill_hex=HH["sage_accent"], shape_type="ELLIPSE",
                )
                reqs += c_reqs
                _, n_reqs = self._create_textbox_reqs(
                    slide_id, x_pt=circle_x, y_pt=body_top + 8, w_pt=circle_size, h_pt=40,
                    text=str(i + 1), font_size=22, bold=True,
                    color_hex=HH["white"], align="CENTER",
                )
                reqs += n_reqs
                _, l_reqs = self._create_textbox_reqs(
                    slide_id, x_pt=cx, y_pt=body_top + circle_size + 12, w_pt=col_w, h_pt=160,
                    text=step_text, font_size=11, color_hex=HH["ink"], align="CENTER",
                )
                reqs += l_reqs
        reqs += self._add_footer_reqs(slide_id)
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- Template: three_card ----
    def hh_three_card_slide(
        self,
        presentation_id: str,
        title: str,
        cards: list[dict],
        lead: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Up to 4 sage cards with header and body text."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["white"])
        reqs += self._content_title_reqs(slide_id, title)
        body_top = 100
        if lead:
            _, lead_reqs = self._create_textbox_reqs(
                slide_id, x_pt=30, y_pt=body_top, w_pt=660, h_pt=45,
                text=lead, font_size=12, color_hex=HH["ink"],
            )
            reqs += lead_reqs
            body_top = 155
        cards = cards[:4]
        n = len(cards)
        if n:
            margin = 15
            gap = 15
            avail = 660 - 2 * margin - gap * (n - 1)
            col_w = avail / n
            card_h = 380 - body_top  # leaves footer space
            for i, card in enumerate(cards):
                cx = 30 + margin + i * (col_w + gap)
                _, bg_reqs = self._create_rect_reqs(
                    slide_id, x_pt=cx, y_pt=body_top, w_pt=col_w, h_pt=card_h,
                    fill_hex=HH["sage_tint"], shape_type="ROUND_RECTANGLE",
                )
                reqs += bg_reqs
                _, h_reqs = self._create_textbox_reqs(
                    slide_id, x_pt=cx + 12, y_pt=body_top + 15, w_pt=col_w - 24, h_pt=40,
                    text=card.get("header", ""), font_size=14, bold=True,
                    color_hex=HH["sage_accent"], align="START",
                )
                reqs += h_reqs
                _, b_reqs = self._create_textbox_reqs(
                    slide_id, x_pt=cx + 12, y_pt=body_top + 58, w_pt=col_w - 24, h_pt=card_h - 70,
                    text=card.get("body", ""), font_size=11, color_hex=HH["ink"], align="START",
                )
                reqs += b_reqs
        reqs += self._add_footer_reqs(slide_id)
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- Template: key_stat (big number + label + caption) ----
    def hh_key_stat_slide(
        self,
        presentation_id: str,
        stat: str,
        label: str,
        caption: str | None = None,
        title: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Single big statistic with label and optional caption."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["white"])
        if title:
            reqs += self._content_title_reqs(slide_id, title)
            stat_y = 110
        else:
            stat_y = 75
        _, s_reqs = self._create_textbox_reqs(
            slide_id, x_pt=30, y_pt=stat_y, w_pt=660, h_pt=130,
            text=stat, font_size=90, bold=True,
            color_hex=HH["sage_accent"], align="CENTER",
        )
        reqs += s_reqs
        _, l_reqs = self._create_textbox_reqs(
            slide_id, x_pt=30, y_pt=stat_y + 140, w_pt=660, h_pt=40,
            text=label, font_size=18, bold=True,
            color_hex=HH["ink"], align="CENTER",
        )
        reqs += l_reqs
        if caption:
            _, c_reqs = self._create_textbox_reqs(
                slide_id, x_pt=60, y_pt=stat_y + 185, w_pt=600, h_pt=80,
                text=caption, font_size=11, color_hex=HH["ink"], align="CENTER",
            )
            reqs += c_reqs
        reqs += self._add_footer_reqs(slide_id)
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id


    # ---- Template: agenda ----
    # Goes at slide 3 of every deck >8 slides. Numbered list of sections (3-6).
    # NOT every slide - just the section names. Orients the audience.
    def hh_agenda_slide(
        self,
        presentation_id: str,
        sections: list[str],
        title: str = "Agenda",
        notes: str | None = None,
    ) -> str:
        """Numbered agenda listing 3 to 6 sections."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["white"])
        reqs += self._content_title_reqs(slide_id, title)
        sections = sections[:6]
        n = len(sections)
        if n:
            list_top = 110
            row_h = (380 - list_top) / max(n, 1)
            for i, sec in enumerate(sections):
                ry = list_top + i * row_h
                # Number column (sage accent)
                _, num_reqs = self._create_textbox_reqs(
                    slide_id, x_pt=40, y_pt=ry, w_pt=60, h_pt=row_h - 4,
                    text=f"{i + 1:02d}", font_size=24, bold=True,
                    color_hex=HH["sage_accent"], align="START",
                )
                reqs += num_reqs
                # Section name
                _, name_reqs = self._create_textbox_reqs(
                    slide_id, x_pt=110, y_pt=ry + 4, w_pt=580, h_pt=row_h - 8,
                    text=sec, font_size=18, bold=True,
                    color_hex=HH["ink"], align="START",
                )
                reqs += name_reqs
                # Thin divider line below row (except last)
                if i < n - 1:
                    _, ln_reqs = self._create_rect_reqs(
                        slide_id, x_pt=40, y_pt=ry + row_h - 2, w_pt=650, h_pt=1,
                        fill_hex=HH["line"],
                    )
                    reqs += ln_reqs
        reqs += self._add_footer_reqs(slide_id)
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- Template: moving_blueprint ----
    # Replaces section_divider in decks >12 slides. Shows full deck spine
    # with the current section highlighted. Audience always knows where they are.
    def hh_moving_blueprint_slide(
        self,
        presentation_id: str,
        sections: list[str],
        current_index: int,
        subtitle: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Section spine with current section highlighted; replaces section_divider in long decks."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["beige"])
        sections = sections[:6]
        n = len(sections)
        if n:
            # Horizontal strip of section pills
            strip_y = 80
            margin = 30
            gap = 10
            avail = 660 - gap * (n - 1)
            pill_w = avail / n
            pill_h = 50
            for i, sec in enumerate(sections):
                px = 30 + i * (pill_w + gap)
                is_current = i == current_index
                fill = HH["sage_accent"] if is_current else HH["white"]
                text_color = HH["white"] if is_current else HH["ink"]
                _, pill_reqs = self._create_rect_reqs(
                    slide_id, x_pt=px, y_pt=strip_y, w_pt=pill_w, h_pt=pill_h,
                    fill_hex=fill, shape_type="ROUND_RECTANGLE",
                )
                reqs += pill_reqs
                # Section number above section name
                _, num_reqs = self._create_textbox_reqs(
                    slide_id, x_pt=px, y_pt=strip_y + 5, w_pt=pill_w, h_pt=18,
                    text=f"{i + 1:02d}", font_size=10, bold=True,
                    color_hex=text_color, align="CENTER",
                )
                reqs += num_reqs
                _, name_reqs = self._create_textbox_reqs(
                    slide_id, x_pt=px + 4, y_pt=strip_y + 22, w_pt=pill_w - 8, h_pt=24,
                    text=sec, font_size=10, bold=is_current,
                    color_hex=text_color, align="CENTER",
                )
                reqs += name_reqs
        # Current section name as big title below the strip
        if 0 <= current_index < len(sections):
            _, t_reqs = self._create_textbox_reqs(
                slide_id, x_pt=45, y_pt=200, w_pt=630, h_pt=60,
                text=sections[current_index], font_size=30, bold=True,
                color_hex=HH["ink"], align="CENTER",
            )
            reqs += t_reqs
            if subtitle:
                _, s_reqs = self._create_textbox_reqs(
                    slide_id, x_pt=45, y_pt=270, w_pt=630, h_pt=40,
                    text=subtitle, font_size=14, color_hex=HH["ink"], align="CENTER",
                )
                reqs += s_reqs
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- Template: big_idea ----
    # Single bold statement, large type, centered. The "one thing to remember"
    # slide. <=15 words total. Visuals support the story, this IS the story.
    def hh_big_idea_slide(
        self,
        presentation_id: str,
        statement: str,
        attribution: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Single large statement, optional attribution; <=15 words."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["white"])
        # Big statement, centered vertically and horizontally
        # Choose font size by length so short statements pop bigger
        word_count = len(statement.split())
        if word_count <= 6:
            font_size = 44
        elif word_count <= 10:
            font_size = 36
        else:
            font_size = 28
        _, s_reqs = self._create_textbox_reqs(
            slide_id, x_pt=50, y_pt=130, w_pt=620, h_pt=180,
            text=statement, font_size=font_size, bold=True,
            color_hex=HH["sage_accent"], align="CENTER",
        )
        reqs += s_reqs
        if attribution:
            _, a_reqs = self._create_textbox_reqs(
                slide_id, x_pt=50, y_pt=320, w_pt=620, h_pt=30,
                text=f"- {attribution}", font_size=14,
                color_hex=HH["ink"], align="CENTER",
            )
            reqs += a_reqs
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- Template: pull_quote ----
    # Customer or stakeholder quote. Uses quotation styling. <=30 words.
    def hh_pull_quote_slide(
        self,
        presentation_id: str,
        quote: str,
        author: str,
        role: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Customer or stakeholder quote with author and optional role; <=30 words."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["sage_tint"])
        # Large opening quote mark, centered
        _, qm_reqs = self._create_textbox_reqs(
            slide_id, x_pt=50, y_pt=80, w_pt=620, h_pt=60,
            text="“", font_size=72, bold=True,
            color_hex=HH["sage_accent"], align="CENTER",
        )
        reqs += qm_reqs
        # Quote body
        word_count = len(quote.split())
        font_size = 22 if word_count <= 15 else 18
        _, q_reqs = self._create_textbox_reqs(
            slide_id, x_pt=60, y_pt=150, w_pt=600, h_pt=140,
            text=quote, font_size=font_size,
            color_hex=HH["ink"], align="CENTER",
        )
        reqs += q_reqs
        # Attribution
        attrib_text = author
        if role:
            attrib_text = f"{author}, {role}"
        _, a_reqs = self._create_textbox_reqs(
            slide_id, x_pt=60, y_pt=310, w_pt=600, h_pt=30,
            text=f"- {attrib_text}", font_size=14, bold=True,
            color_hex=HH["sage_accent"], align="CENTER",
        )
        reqs += a_reqs
        reqs += self._add_footer_reqs(slide_id)
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- Template: comparison_2x2 ----
    # Matrix with x/y axes and 4 labeled quadrants. Effort vs impact,
    # build vs buy, likelihood vs severity, etc.
    def hh_comparison_2x2_slide(
        self,
        presentation_id: str,
        title: str,
        x_left: str,
        x_right: str,
        y_bottom: str,
        y_top: str,
        quadrants: list[dict],
        notes: str | None = None,
    ) -> str:
        """2x2 matrix with axis labels and four labeled quadrants.

        quadrants is exactly 4 dicts: [top_left, top_right, bottom_left, bottom_right].
        Each: {"header": str, "body": str (optional)}.
        """
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["white"])
        reqs += self._content_title_reqs(slide_id, title)
        # Matrix bounds (leave room for axis labels)
        mx = 100
        my = 110
        mw = 540
        mh = 240
        # Grid background - light gridlines
        # Outer border
        _, outer = self._create_rect_reqs(
            slide_id, x_pt=mx, y_pt=my, w_pt=mw, h_pt=mh,
            fill_hex=HH["sage_tint"],
        )
        reqs += outer
        # Vertical divider line
        _, vline = self._create_rect_reqs(
            slide_id, x_pt=mx + mw / 2 - 0.5, y_pt=my, w_pt=1, h_pt=mh,
            fill_hex=HH["white"],
        )
        reqs += vline
        # Horizontal divider line
        _, hline = self._create_rect_reqs(
            slide_id, x_pt=mx, y_pt=my + mh / 2 - 0.5, w_pt=mw, h_pt=1,
            fill_hex=HH["white"],
        )
        reqs += hline
        # Axis labels
        # Y-axis top label
        _, yt = self._create_textbox_reqs(
            slide_id, x_pt=10, y_pt=my, w_pt=85, h_pt=30,
            text=y_top, font_size=11, bold=True,
            color_hex=HH["sage_accent"], align="END",
        )
        reqs += yt
        # Y-axis bottom label
        _, yb = self._create_textbox_reqs(
            slide_id, x_pt=10, y_pt=my + mh - 30, w_pt=85, h_pt=30,
            text=y_bottom, font_size=11, bold=True,
            color_hex=HH["sage_accent"], align="END",
        )
        reqs += yb
        # X-axis left label
        _, xl = self._create_textbox_reqs(
            slide_id, x_pt=mx, y_pt=my + mh + 8, w_pt=mw / 2, h_pt=20,
            text=x_left, font_size=11, bold=True,
            color_hex=HH["sage_accent"], align="CENTER",
        )
        reqs += xl
        # X-axis right label
        _, xr = self._create_textbox_reqs(
            slide_id, x_pt=mx + mw / 2, y_pt=my + mh + 8, w_pt=mw / 2, h_pt=20,
            text=x_right, font_size=11, bold=True,
            color_hex=HH["sage_accent"], align="CENTER",
        )
        reqs += xr
        # Quadrant content - 4 cells: TL, TR, BL, BR
        qw = mw / 2
        qh = mh / 2
        quadrants = (quadrants + [{}, {}, {}, {}])[:4]
        positions = [
            (mx, my),                # TL
            (mx + qw, my),           # TR
            (mx, my + qh),           # BL
            (mx + qw, my + qh),      # BR
        ]
        for (qx, qy), q in zip(positions, quadrants):
            header = q.get("header", "")
            body = q.get("body", "")
            if header:
                _, hreqs = self._create_textbox_reqs(
                    slide_id, x_pt=qx + 8, y_pt=qy + 8, w_pt=qw - 16, h_pt=22,
                    text=header, font_size=12, bold=True,
                    color_hex=HH["ink"], align="START",
                )
                reqs += hreqs
            if body:
                _, breqs = self._create_textbox_reqs(
                    slide_id, x_pt=qx + 8, y_pt=qy + 32, w_pt=qw - 16, h_pt=qh - 40,
                    text=body, font_size=10,
                    color_hex=HH["ink"], align="START",
                )
                reqs += breqs
        reqs += self._add_footer_reqs(slide_id)
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ---- Template: metric_grid ----
    # Multiple stats arranged in a grid. Use when you want to show 3-6
    # related numbers at once instead of one big number per slide.
    def hh_metric_grid_slide(
        self,
        presentation_id: str,
        title: str,
        metrics: list[dict],
        lead: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Grid of 2 to 6 stats; each metric is {"value": "83%", "label": "..."}."""
        slide_id = self._next_id("slide")
        reqs = self._blank_slide_reqs(slide_id, background_hex=HH["white"])
        reqs += self._content_title_reqs(slide_id, title)
        body_top = 100
        if lead:
            _, lead_reqs = self._create_textbox_reqs(
                slide_id, x_pt=30, y_pt=body_top, w_pt=660, h_pt=45,
                text=lead, font_size=12, color_hex=HH["ink"],
            )
            reqs += lead_reqs
            body_top = 155
        metrics = metrics[:6]
        n = len(metrics)
        if n:
            # 2 rows if >3 metrics, 1 row otherwise
            cols = 3 if n > 4 else n
            rows = 2 if n > 3 else 1
            if n == 4:
                cols, rows = 2, 2
            margin = 20
            h_gap = 15
            v_gap = 15
            cell_w = (660 - 2 * margin - h_gap * (cols - 1)) / cols
            cell_h = (380 - body_top - v_gap * (rows - 1)) / rows
            for i, m in enumerate(metrics):
                row = i // cols
                col = i % cols
                cx = 30 + margin + col * (cell_w + h_gap)
                cy = body_top + row * (cell_h + v_gap)
                # Cell background
                _, bg = self._create_rect_reqs(
                    slide_id, x_pt=cx, y_pt=cy, w_pt=cell_w, h_pt=cell_h,
                    fill_hex=HH["sage_tint"], shape_type="ROUND_RECTANGLE",
                )
                reqs += bg
                # Big number
                _, nreqs = self._create_textbox_reqs(
                    slide_id, x_pt=cx + 8, y_pt=cy + 12, w_pt=cell_w - 16, h_pt=cell_h * 0.55,
                    text=m.get("value", ""), font_size=40, bold=True,
                    color_hex=HH["sage_accent"], align="CENTER",
                )
                reqs += nreqs
                # Label
                _, lreqs = self._create_textbox_reqs(
                    slide_id, x_pt=cx + 8, y_pt=cy + cell_h * 0.62, w_pt=cell_w - 16, h_pt=cell_h * 0.35,
                    text=m.get("label", ""), font_size=11, bold=True,
                    color_hex=HH["ink"], align="CENTER",
                )
                reqs += lreqs
        reqs += self._add_footer_reqs(slide_id)
        self._batch(presentation_id, reqs)
        if notes:
            self._set_notes_on_slide_object(presentation_id, slide_id, notes)
        return slide_id

    # ====================================================================
    # Edit-existing-deck methods
    # All slide_index args below are 1-indexed (slide 1 = first slide).
    # ====================================================================

    def _resolve_slide(self, presentation_id: str, slide_index: int) -> tuple[str, list[dict]]:
        """Return (object_id, raw_slide_dict_list) and validate 1-indexed slide_index."""
        pres = self.slides.presentations().get(presentationId=presentation_id).execute()
        slides = pres.get("slides", [])
        if not slides:
            raise ValueError(f"Presentation {presentation_id} has no slides")
        if slide_index < 1 or slide_index > len(slides):
            raise ValueError(
                f"slide_index={slide_index} out of range (deck has {len(slides)} slides, "
                "1-indexed)"
            )
        target = slides[slide_index - 1]
        return target["objectId"], slides

    def _slide_text_preview(self, slide: dict, max_len: int = 80) -> str:
        """Concatenate text runs from page elements; trim to max_len."""
        chunks: list[str] = []
        for el in slide.get("pageElements", []):
            shape = el.get("shape") or {}
            text = shape.get("text") or {}
            for te in text.get("textElements", []):
                tr = te.get("textRun") or {}
                content = tr.get("content")
                if content:
                    chunks.append(content)
        joined = " ".join(c.strip() for c in chunks if c.strip())
        joined = " ".join(joined.split())
        if len(joined) > max_len:
            joined = joined[: max_len - 1] + "..."
        return joined

    def _slide_notes_preview(self, slide: dict, max_len: int = 80) -> str:
        """Pull speaker-notes text from the slide's notesPage."""
        slide_props = slide.get("slideProperties") or {}
        notes_page = slide_props.get("notesPage") or {}
        chunks: list[str] = []
        for el in notes_page.get("pageElements", []):
            shape = el.get("shape") or {}
            placeholder = shape.get("placeholder") or {}
            if placeholder.get("type") != "BODY":
                continue
            text = shape.get("text") or {}
            for te in text.get("textElements", []):
                tr = te.get("textRun") or {}
                content = tr.get("content")
                if content:
                    chunks.append(content)
        joined = " ".join(c.strip() for c in chunks if c.strip())
        joined = " ".join(joined.split())
        if len(joined) > max_len:
            joined = joined[: max_len - 1] + "..."
        return joined

    def _guess_layout_hint(self, slide: dict) -> str:
        """Best-effort layout classification from background color and shape patterns.

        Returns one of: "cover", "section_divider", "pull_quote", "content".
        Heuristic only - the hh_* templates do not record layout metadata, so we
        infer from background color plus shape counts. Good enough for outline
        previews; do not rely on this for programmatic dispatch.
        """
        # Background color
        bg_hex = None
        try:
            page_props = slide.get("pageProperties") or {}
            bg_fill = page_props.get("pageBackgroundFill") or {}
            solid = bg_fill.get("solidFill") or {}
            rgb = solid.get("color", {}).get("rgbColor", {}) or {}
            r = int(round(rgb.get("red", 0) * 255))
            g = int(round(rgb.get("green", 0) * 255))
            b = int(round(rgb.get("blue", 0) * 255))
            bg_hex = f"{r:02X}{g:02X}{b:02X}"
        except Exception:
            bg_hex = None
        # Dark background -> cover
        if bg_hex == HH["ink"] or bg_hex == HH["black"]:
            return "cover"
        # Beige background -> section_divider (also used by moving_blueprint)
        if bg_hex and bg_hex.upper() == HH["beige"].upper():
            return "section_divider"
        # Sage tint background -> pull_quote (the only template that uses it as bg)
        if bg_hex and bg_hex.upper() == HH["sage_tint"].upper():
            return "pull_quote"
        return "content"

    def get_deck_outline(self, presentation_id: str) -> list[dict]:
        """Return one dict per slide with index, id, layout hint, and previews.

        Each entry: {slide_index, object_id, layout_hint, text_preview, notes_preview}.
        slide_index is 1-indexed.
        """
        pres = self.slides.presentations().get(presentationId=presentation_id).execute()
        out: list[dict] = []
        for i, s in enumerate(pres.get("slides", []), start=1):
            out.append(
                {
                    "slide_index": i,
                    "object_id": s.get("objectId", ""),
                    "layout_hint": self._guess_layout_hint(s),
                    "text_preview": self._slide_text_preview(s),
                    "notes_preview": self._slide_notes_preview(s),
                }
            )
        return out

    def delete_slide_at(self, presentation_id: str, slide_index: int) -> None:
        """Delete the slide at the given 1-indexed position."""
        obj_id, _ = self._resolve_slide(presentation_id, slide_index)
        self._batch(presentation_id, [{"deleteObject": {"objectId": obj_id}}])

    def reorder_slide(
        self,
        presentation_id: str,
        from_index: int,
        to_index: int,
    ) -> None:
        """Move slide from one 1-indexed position to another via updateSlidesPosition."""
        obj_id, slides = self._resolve_slide(presentation_id, from_index)
        n = len(slides)
        if to_index < 1 or to_index > n:
            raise ValueError(
                f"to_index={to_index} out of range (deck has {n} slides, 1-indexed)"
            )
        # insertionIndex is 0-indexed in the API
        insertion_index = to_index - 1
        self._batch(
            presentation_id,
            [
                {
                    "updateSlidesPosition": {
                        "slideObjectIds": [obj_id],
                        "insertionIndex": insertion_index,
                    }
                }
            ],
        )

    def replace_text_on_slide(
        self,
        presentation_id: str,
        slide_index: int,
        find: str,
        replace: str,
    ) -> int:
        """Replace `find` with `replace` on the specified slide; returns occurrences replaced."""
        obj_id, _ = self._resolve_slide(presentation_id, slide_index)
        resp = self._batch(
            presentation_id,
            [
                {
                    "replaceAllText": {
                        "containsText": {"text": find, "matchCase": True},
                        "replaceText": replace,
                        "pageObjectIds": [obj_id],
                    }
                }
            ],
        )
        replies = resp.get("replies") or []
        if replies and "replaceAllText" in replies[0]:
            return int(replies[0]["replaceAllText"].get("occurrencesChanged", 0))
        return 0

    def add_speaker_notes(
        self,
        presentation_id: str,
        slide_index: int,
        notes_text: str,
        append: bool = False,
    ) -> None:
        """Set or append speaker notes on a 1-indexed slide."""
        obj_id, _ = self._resolve_slide(presentation_id, slide_index)
        if append:
            existing = self.get_speaker_notes(presentation_id, slide_index)
            combined = f"{existing}\n{notes_text}" if existing else notes_text
            self._set_notes_on_slide_object(presentation_id, obj_id, combined)
        else:
            self._set_notes_on_slide_object(presentation_id, obj_id, notes_text)

    def get_speaker_notes(self, presentation_id: str, slide_index: int) -> str:
        """Return the full speaker-notes text for the 1-indexed slide (empty string if none)."""
        _, slides = self._resolve_slide(presentation_id, slide_index)
        target = slides[slide_index - 1]
        slide_props = target.get("slideProperties") or {}
        notes_page = slide_props.get("notesPage") or {}
        # Prefer the speakerNotesObjectId-pointed shape; fall back to BODY placeholder
        notes_props = notes_page.get("notesProperties") or {}
        target_obj_id = notes_props.get("speakerNotesObjectId")
        for el in notes_page.get("pageElements", []):
            if target_obj_id and el.get("objectId") != target_obj_id:
                continue
            if not target_obj_id:
                shape = el.get("shape") or {}
                placeholder = shape.get("placeholder") or {}
                if placeholder.get("type") != "BODY":
                    continue
            shape = el.get("shape") or {}
            text = shape.get("text") or {}
            chunks: list[str] = []
            for te in text.get("textElements", []):
                tr = te.get("textRun") or {}
                content = tr.get("content")
                if content:
                    chunks.append(content)
            return "".join(chunks).rstrip("\n")
        return ""

    def replace_image_on_slide(
        self,
        presentation_id: str,
        slide_index: int,
        image_index: int,
        new_image_url: str,
    ) -> None:
        """Replace the Nth image (1-indexed) on the slide with a new URL via replaceImage."""
        _, slides = self._resolve_slide(presentation_id, slide_index)
        target = slides[slide_index - 1]
        image_object_ids: list[str] = []
        for el in target.get("pageElements", []):
            if "image" in el:
                image_object_ids.append(el["objectId"])
        if not image_object_ids:
            raise ValueError(
                f"Slide {slide_index} has no images to replace"
            )
        if image_index < 1 or image_index > len(image_object_ids):
            raise ValueError(
                f"image_index={image_index} out of range "
                f"(slide {slide_index} has {len(image_object_ids)} images, 1-indexed)"
            )
        target_image_id = image_object_ids[image_index - 1]
        self._batch(
            presentation_id,
            [
                {
                    "replaceImage": {
                        "imageObjectId": target_image_id,
                        "url": new_image_url,
                        "imageReplaceMethod": "CENTER_INSIDE",
                    }
                }
            ],
        )


if __name__ == "__main__":
    c = SlidesClient()
    pid = c.create_deck("HH style smoke test (720x405)")
    c.delete_default_first_slide(pid)
    c.hh_cover_slide(pid, "HH style smoke test", "Calibrated for the 720x405 canvas")
    c.hh_executive_summary(
        pid, "Executive summary",
        "Native Slides creation now respects the API default canvas size (10 inches, 720x405 pt).",
        "What changed",
        ["All coordinates rescaled", "Fonts proportionally tuned", "No more right-edge cutoff"],
    )
    c.hh_bullets_slide(
        pid, "Coverage", [
            "Cover, exec summary, section divider, bullets, two-column",
            "Do/Don't, flow steps, three card, key stat",
            "Confidentiality footer on every content slide",
        ],
        lead="Six templates plus three visual variants. All fit the 720x405 canvas with margin.",
    )
    print(c.url(pid))
