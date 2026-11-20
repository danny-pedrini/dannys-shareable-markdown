"""Render a Looker chart to PNG, upload to Drive, return a public image URL.

Why this exists: PMs need to drop Looker charts into Slides decks. Today
they screenshot manually, paste into Slides, and the image is brittle.
`make-deck` calls this helper to land a chart on a slide via Drive image URL,
which Slides ingests as a native image.

Three render paths, in priority order:

Path A, Direct Looker REST:
  If `~/.looker.ini` exists, hit `GET /looks/{look_id}/run/png?width=W&height=H`
  using the API3 client. Best fidelity: exact same chart Looker renders.

Path B, Looker MCP data plus local render:
  If `--data-json <path>` is passed, read JSON rows fetched via the Looker MCP
  `query` tool externally, then render locally with matplotlib using HH palette.
  Use this when Path A is unavailable but you can still pull data through the MCP.

Path C, Sample fallback:
  If `--sample` is passed, render a stub bar chart from a hardcoded dataset.
  Proves the upload pipeline end-to-end without any Looker auth.

Upload step (all paths):
  Auth via SlidesClient (Drive scope already present). Upload PNG via
  Drive `files.create`. [Care Delivery director] `anyone, role=reader`. Print
  (internal link) on the last line of stdout.

==============================================================================
What needs setup to unlock the live Looker path (Path A)
==============================================================================

1. Create a Looker API3 credential.
   In Looker, go to Admin → Users → [your user] → Edit Keys → New API3 Key.
   Save the client_id and client_secret.

2. Create `~/.looker.ini` with:

       [Looker]
       base_url=(internal link):19999
       client_id=YOUR_CLIENT_ID
       client_secret=YOUR_CLIENT_SECRET
       verify_ssl=true

   (Port 19999 is the API port. Confirm the host with Looker admin if hims
   uses a custom domain.)

3. `chmod 600 ~/.looker.ini` so the credentials are not world-readable.

4. Install the SDK if not present: `pip install looker_sdk`.

5. Sanity check:
       python3 -c "import looker_sdk; sdk = looker_sdk.init40(); print(sdk.me().email)"

   Should print your email. If it errors, the .ini path or credentials are wrong.

Once those four steps are done, `looker_to_image.py <look_id> --width 1200`
hits the live REST path automatically.
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
from pathlib import Path
from typing import Any

# Make slides_client importable whether called from anywhere
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from slides_client import SlidesClient, HH  # noqa: E402


LOOKER_INI = Path.home() / ".looker.ini"


def parse_look_id(arg: str) -> str:
    """Accept a bare look ID or a Looker URL like
    (internal link) and return the ID."""
    if arg.isdigit():
        return arg
    m = re.search(r"/looks/(\d+)", arg)
    if m:
        return m.group(1)
    # Last-ditch: maybe it is a slug; pass through and let Looker reject.
    return arg


# ----------------------------- Path A: REST -------------------------------- #

def render_via_looker_rest(look_id: str, width: int, height: int) -> bytes:
    """TODO(looker-auth): blocked until ~/.looker.ini exists. See module docstring."""
    if not LOOKER_INI.exists():
        raise FileNotFoundError(
            f"{LOOKER_INI} not found. See the 'What needs setup' section of "
            "this script's docstring to enable Path A."
        )
    try:
        import looker_sdk  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "looker_sdk not installed. Run: pip install looker_sdk"
        ) from exc
    # TODO(looker-auth): test end-to-end once a real API3 key is provisioned.
    sdk = looker_sdk.init40(str(LOOKER_INI))
    png_bytes = sdk.run_look(
        look_id=look_id,
        result_format="png",
        image_width=width,
        image_height=height,
    )
    if isinstance(png_bytes, str):
        png_bytes = png_bytes.encode("latin-1")
    return png_bytes


# ----------------------- Path B: data JSON + matplotlib -------------------- #

def _hh_color_cycle() -> list[str]:
    """Return hex colors (with #) in HH brand order for series rendering."""
    keys = ["sage_accent", "blue_mid", "beige", "blue_header", "warm_gray", "sage_light"]
    return [f"#{HH[k]}" for k in keys]


def _apply_hh_chart_style(ax) -> None:
    import matplotlib.pyplot as plt  # noqa: F401  (ensures backend wiring)
    ax.set_facecolor(f"#{HH['off_white']}")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(f"#{HH['warm_gray']}")
    ax.tick_params(colors=f"#{HH['ink']}", labelsize=10)
    ax.yaxis.label.set_color(f"#{HH['ink']}")
    ax.xaxis.label.set_color(f"#{HH['ink']}")
    ax.title.set_color(f"#{HH['ink']}")
    ax.grid(axis="y", color=f"#{HH['line']}", linewidth=0.6, alpha=0.7)


def render_via_data_json(data_path: Path, width: int, height: int) -> bytes:
    """Render a chart from a JSON file shaped like Looker `query` MCP output.

    Accepts two flexible shapes:
      1. List of row dicts (looker-mcp `query` returns this by default).
         Auto-picks first string-ish field as the x-axis label and the
         first numeric field as y.
      2. Dict with explicit keys: {"title": str, "x_label": str, "y_label": str,
         "series": [{"name": str, "x": [...], "y": [...]}]}
    """
    import json
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    raw = json.loads(data_path.read_text())

    fig, ax = plt.subplots(figsize=(width / 100.0, height / 100.0), dpi=100)

    colors = _hh_color_cycle()

    if isinstance(raw, dict) and "series" in raw:
        for i, s in enumerate(raw["series"]):
            ax.bar(s.get("x", []), s.get("y", []),
                   color=colors[i % len(colors)], label=s.get("name", f"Series {i+1}"))
        ax.set_title(raw.get("title", ""), fontsize=14, fontweight="bold")
        ax.set_xlabel(raw.get("x_label", ""))
        ax.set_ylabel(raw.get("y_label", ""))
        if len(raw["series"]) > 1:
            ax.legend(frameon=False)
    elif isinstance(raw, list) and raw and isinstance(raw[0], dict):
        keys = list(raw[0].keys())
        x_key = next((k for k in keys if not isinstance(raw[0][k], (int, float))), keys[0])
        y_key = next((k for k in keys if isinstance(raw[0][k], (int, float))), keys[-1])
        xs = [str(r.get(x_key, "")) for r in raw]
        ys = [float(r.get(y_key, 0) or 0) for r in raw]
        ax.bar(xs, ys, color=colors[0])
        ax.set_xlabel(x_key)
        ax.set_ylabel(y_key)
    else:
        raise ValueError(
            "Unrecognized --data-json shape. Expected list of row dicts or "
            "dict with 'series'."
        )

    _apply_hh_chart_style(ax)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=f"#{HH['white']}")
    plt.close(fig)
    return buf.getvalue()


# ------------------------- Path C: sample stub ----------------------------- #

def render_sample(width: int, height: int) -> bytes:
    """Render a stub chart with a hardcoded HH-styled dataset."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = ["Jan", "Feb", "Mar", "Apr", "May"]
    values = [42, 58, 71, 76, 83]

    fig, ax = plt.subplots(figsize=(width / 100.0, height / 100.0), dpi=100)
    ax.bar(labels, values, color=f"#{HH['sage_accent']}")
    for i, v in enumerate(values):
        ax.text(i, v + 1.5, f"{v}%", ha="center", fontsize=10,
                color=f"#{HH['ink']}", fontweight="bold")
    ax.set_title("PHD migration progress (sample)", fontsize=14, fontweight="bold")
    ax.set_ylabel("% complete")
    ax.set_ylim(0, 100)
    _apply_hh_chart_style(ax)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=f"#{HH['white']}")
    plt.close(fig)
    return buf.getvalue()


# ----------------------------- Upload to Drive ----------------------------- #

def upload_png_to_drive(
    png_bytes: bytes,
    filename: str,
    parent_folder_id: str | None = None,
) -> str:
    """Upload PNG to Drive, set public read, return drive.google.com/uc URL."""
    from googleapiclient.http import MediaIoBaseUpload

    client = SlidesClient()
    drive = client.drive

    meta: dict[str, Any] = {"name": filename, "mimeType": "image/png"}
    if parent_folder_id:
        meta["parents"] = [parent_folder_id]

    media = MediaIoBaseUpload(io.BytesIO(png_bytes), mimetype="image/png", resumable=False)
    created = drive.files().create(body=meta, media_body=media, fields="id").execute()
    file_id = created["id"]

    drive.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
        fields="id",
    ).execute()

    return f"(internal link)"


# ---------------------------------- CLI ------------------------------------ #

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Render a Looker chart (or sample) to PNG and upload to Drive."
    )
    p.add_argument(
        "look",
        nargs="?",
        default=None,
        help="Looker look ID or URL. Optional when --sample is used.",
    )
    p.add_argument("--width", type=int, default=1200, help="Chart width in pixels.")
    p.add_argument("--height", type=int, default=675, help="Chart height in pixels.")
    p.add_argument("--format", default="png", choices=["png"], help="Output format.")
    p.add_argument("--folder", default=None, help="Drive folder ID to drop the upload into.")
    p.add_argument(
        "--data-json",
        type=Path,
        default=None,
        help="Path B: local JSON file (data fetched via Looker MCP).",
    )
    p.add_argument(
        "--sample",
        action="store_true",
        help="Path C: render a hardcoded sample chart. No Looker auth needed.",
    )
    args = p.parse_args(argv)

    # Pick path: --sample > --data-json > REST > error
    if args.sample:
        png_bytes = render_sample(args.width, args.height)
        filename = "looker_sample.png"
    elif args.data_json is not None:
        if not args.data_json.exists():
            print(f"--data-json file not found: {args.data_json}", file=sys.stderr)
            return 2
        png_bytes = render_via_data_json(args.data_json, args.width, args.height)
        filename = f"looker_{args.data_json.stem}.png"
    elif args.look:
        look_id = parse_look_id(args.look)
        try:
            png_bytes = render_via_looker_rest(look_id, args.width, args.height)
        except (FileNotFoundError, ImportError) as exc:
            print(
                f"Looker REST path unavailable: {exc}\n"
                "Fallback options: pass --sample, or fetch data via Looker MCP "
                "and pass --data-json <path>.",
                file=sys.stderr,
            )
            return 3
        filename = f"look_{look_id}.png"
    else:
        p.print_usage(sys.stderr)
        print("Provide a look ID/URL, or --data-json, or --sample.", file=sys.stderr)
        return 2

    try:
        url = upload_png_to_drive(png_bytes, filename, parent_folder_id=args.folder)
    except Exception as exc:  # pragma: no cover  (network/auth issues surface at runtime)
        print(f"Upload failed: {exc}", file=sys.stderr)
        return 4

    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
