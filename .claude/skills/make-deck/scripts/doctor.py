"""Health check for the make-deck skill.

Verifies that deps, OAuth, Slides API, Drive write access, output state,
disk space, and (best-effort) Poppins font availability are all wired up.

Usage:
  python3 doctor.py
  python3 doctor.py --smoke-deck <presentation_id>   # override Poppins probe target
  python3 doctor.py --json

Exits 0 on GREEN, 1 on YELLOW or RED.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

OAUTH_CLIENT_PATH = Path.home() / ".config" / "gcloud" / "slides-oauth.json"
TOKEN_PATH = Path.home() / ".config" / "gcloud" / "slides-token.json"
OUTPUTS_DIR = Path.home() / ".claude" / "skills" / "make-deck" / "outputs"
SMOKE_DECK_DEFAULT = "1JOn3tZzFnOGY0wr_MXRbNmZwo4bwizN4WCycDki5XUk"

# Severity → glyph for human output. Kept ASCII-friendly so the checker
# is readable in any terminal.
SYM = {"PASS": "OK ", "WARN": "WARN", "FAIL": "FAIL"}


def _record(results: list[dict], name: str, status: str, detail: str = "") -> None:
    results.append({"name": name, "status": status, "detail": detail})


def check_python_deps(results: list[dict]) -> None:
    """Verify required Google API libraries are importable."""
    try:
        import googleapiclient  # noqa: F401
        import google_auth_oauthlib  # noqa: F401
        import google.oauth2  # noqa: F401
        import google.auth.transport.requests  # noqa: F401
    except ImportError as e:
        _record(results, "Python deps", "FAIL", f"missing import: {e}")
        return
    try:
        from importlib.metadata import version
        gac = version("google-api-python-client")
        gao = version("google-auth-oauthlib")
        detail = f"google-api-python-client {gac}, google-auth-oauthlib {gao}"
    except Exception:
        detail = "imports succeeded; versions not introspected"
    _record(results, "Python deps", "PASS", detail)


def check_oauth_client(results: list[dict]) -> None:
    """OAuth client JSON exists, readable, perms 600."""
    if not OAUTH_CLIENT_PATH.exists():
        _record(
            results, "OAuth client JSON", "FAIL",
            f"missing at {OAUTH_CLIENT_PATH}. Download desktop OAuth client from GCP Console."
        )
        return
    try:
        json.loads(OAUTH_CLIENT_PATH.read_text())
    except Exception as e:
        _record(results, "OAuth client JSON", "FAIL", f"unreadable JSON: {e}")
        return
    mode = stat.S_IMODE(OAUTH_CLIENT_PATH.stat().st_mode)
    if mode & 0o077:
        _record(
            results, "OAuth client JSON", "WARN",
            f"perms 0{mode:o} (world or group readable); recommend chmod 600"
        )
    else:
        _record(results, "OAuth client JSON", "PASS", f"perms 0{mode:o}")


def check_token(results: list[dict]) -> None:
    """Cached token loads, refreshes if expired."""
    if not TOKEN_PATH.exists():
        _record(
            results, "Cached token", "WARN",
            f"missing at {TOKEN_PATH}; first build_deck.py run will trigger OAuth flow"
        )
        return
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        scopes = [
            "https://www.googleapis.com/auth/presentations",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), scopes)
        if creds.valid:
            exp = creds.expiry.isoformat() if creds.expiry else "n/a"
            _record(results, "Cached token", "PASS", f"valid (expires {exp})")
            return
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
            os.chmod(TOKEN_PATH, 0o600)
            exp = creds.expiry.isoformat() if creds.expiry else "n/a"
            _record(results, "Cached token", "PASS", f"refreshed (now expires {exp})")
            return
        _record(results, "Cached token", "FAIL", "invalid and not refreshable; re-auth needed")
    except Exception as e:
        _record(results, "Cached token", "FAIL", f"could not load: {e}")


def check_slides_api(results: list[dict]) -> str | None:
    """End-to-end ping: create a deck, then delete it via Drive."""
    try:
        from slides_client import SlidesClient
    except Exception as e:
        _record(results, "Slides API ping", "FAIL", f"slides_client import failed: {e}")
        return None
    try:
        c = SlidesClient()
        pid = c.create_deck("make-deck doctor check")
        c.drive.files().delete(fileId=pid).execute()
        _record(results, "Slides API ping", "PASS", "create+delete round-trip ok")
        return pid
    except Exception as e:
        _record(results, "Slides API ping", "FAIL", str(e))
        return None


def check_poppins(results: list[dict], smoke_deck: str) -> None:
    """Best-effort: read the smoke-test deck and confirm Poppins was requested.

    Note: this only confirms the API request was made with Poppins. It does not
    guarantee the user's Google account has Poppins loaded; Slides will silently
    substitute another font if the user has not added Poppins via 'More fonts'.
    """
    try:
        from slides_client import SlidesClient
        c = SlidesClient()
        pres = c.slides.presentations().get(presentationId=smoke_deck).execute()
    except Exception as e:
        _record(results, "Poppins font (request-side)", "WARN",
                f"could not read smoke deck {smoke_deck}: {e}")
        return

    families: set[str] = set()
    for slide in pres.get("slides", []):
        for el in slide.get("pageElements", []):
            shape = el.get("shape", {})
            text = shape.get("text", {})
            for te in text.get("textElements", []):
                tr = te.get("textRun", {})
                style = tr.get("style", {})
                ff = style.get("fontFamily")
                if ff:
                    families.add(ff)
    if "Poppins" in families:
        _record(
            results, "Poppins font (request-side)", "PASS",
            "API requests use Poppins. Cannot verify user account has it loaded; if "
            "rendered slides look wrong, add Poppins via Slides UI 'More fonts'."
        )
    elif not families:
        _record(results, "Poppins font (request-side)", "WARN",
                "no text elements found in smoke deck; cannot probe")
    else:
        _record(
            results, "Poppins font (request-side)", "WARN",
            f"smoke deck uses {sorted(families)} (no Poppins); deck may pre-date the style guide"
        )


def check_drive_write(results: list[dict]) -> None:
    """Create + delete an empty Drive folder."""
    try:
        from slides_client import SlidesClient
        c = SlidesClient()
        folder = c.drive.files().create(
            body={"name": "make-deck-doctor-test", "mimeType": "application/vnd.google-apps.folder"},
            fields="id",
        ).execute()
        c.drive.files().delete(fileId=folder["id"]).execute()
        _record(results, "Drive write", "PASS", "create+delete folder ok")
    except Exception as e:
        _record(results, "Drive write", "FAIL", str(e))


def check_outputs_dir(results: list[dict]) -> None:
    """Output state directory exists; count prior runs."""
    if not OUTPUTS_DIR.exists():
        _record(results, "Output state dir", "WARN",
                f"{OUTPUTS_DIR} does not exist (will be created on first build)")
        return
    files = sorted(OUTPUTS_DIR.glob("*.json"))
    _record(results, "Output state dir", "PASS", f"{len(files)} prior decks")


def check_disk_space(results: list[dict]) -> None:
    """Need ~5 MB per deck for thumbnail rendering."""
    probe = Path("/tmp")
    try:
        usage = shutil.disk_usage(str(probe))
    except Exception as e:
        _record(results, "/tmp space", "WARN", f"could not stat: {e}")
        return
    free_gb = usage.free / (1024 ** 3)
    if free_gb < 0.5:
        _record(results, "/tmp space", "FAIL", f"{free_gb:.2f} GB free (<0.5 GB)")
    elif free_gb < 2:
        _record(results, "/tmp space", "WARN", f"{free_gb:.2f} GB free (tight)")
    else:
        _record(results, "/tmp space", "PASS", f"{free_gb:.1f} GB free")


def verdict_for(results: list[dict]) -> str:
    statuses = {r["status"] for r in results}
    if "FAIL" in statuses:
        return "RED"
    if "WARN" in statuses:
        return "YELLOW"
    return "GREEN"


def print_human(results: list[dict], verdict: str) -> None:
    print(f"make-deck doctor — verdict: {verdict}")
    for r in results:
        sym = SYM.get(r["status"], r["status"])
        line = f"  {sym}  {r['name']}"
        if r["detail"]:
            line += f" — {r['detail']}"
        print(line)


def run_all(smoke_deck: str) -> list[dict]:
    results: list[dict] = []
    check_python_deps(results)
    check_oauth_client(results)
    check_token(results)
    check_slides_api(results)
    check_poppins(results, smoke_deck)
    check_drive_write(results)
    check_outputs_dir(results)
    check_disk_space(results)
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Health check for the make-deck skill.")
    ap.add_argument("--smoke-deck", default=SMOKE_DECK_DEFAULT,
                    help="Deck ID for Poppins probe")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of human output")
    args = ap.parse_args()

    results = run_all(args.smoke_deck)
    verdict = verdict_for(results)

    if args.json:
        print(json.dumps({
            "verdict": verdict,
            "checked_at": datetime.now().isoformat(timespec="seconds"),
            "results": results,
        }, indent=2))
    else:
        print_human(results, verdict)

    return 0 if verdict == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
