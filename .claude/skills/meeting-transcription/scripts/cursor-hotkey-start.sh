#!/usr/bin/env bash
# Cursor keybinding hotkey: START a meeting recording inside Cursor's own
# integrated terminal — NOT Terminal.app, and NOT a .vscode/tasks.json task
# (Cursor's agent tooling refuses to write under .vscode/, so that design
# was dropped).
#
# Triggered by a Cursor keybinding (default: Ctrl+Shift+R) in
# ~/Library/Application Support/Cursor/User/keybindings.json, which uses the
# built-in `runCommands` command to open a new integrated terminal and type
# this script's path into it. This only fires while Cursor has focus. For a
# system-wide hotkey that works in any app (Slack, browser, etc.), use the
# OS-Level Hotkeys path instead (scripts/os-hotkey-start.sh + macOS
# Shortcuts.app).
#
# Runs in the foreground as the terminal's own process, so record_meeting.py's
# live status line (audio levels, mic gain) is visible in the Cursor
# terminal panel. Stop with Ctrl+Shift+S, which reuses scripts/os-hotkey-stop.sh
# unmodified — that script is terminal-agnostic: it reads the PID file
# record_meeting.py writes to ~/.meeting-recording.pid regardless of which
# terminal started it.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$HOME/.local/share/meeting-transcription/venv/bin/python"
RECORD_PY="$SCRIPT_DIR/record_meeting.py"
PID_FILE="$HOME/.meeting-recording.pid"
ORIG_OUTPUT_FILE="$HOME/.meeting-recording.original-output"
LOG_FILE="$HOME/.meeting-recording.log"

log() {
    printf '[%s] [cursor-start] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG_FILE"
}

log "hotkey pressed"

# ─── Idempotency: bail BEFORE touching audio routing or ORIG_OUTPUT_FILE ─────
# if a recording is already running. Without this check, a second Ctrl+Shift+R
# would overwrite the saved pre-recording output device with the current
# multi-output device, so Ctrl+Shift+S would restore the wrong device and
# leave the volume slider locked. record_meeting.py also guards against a
# second process via this same PID file, but only after routing has already run.
if [ -f "$PID_FILE" ]; then
    existing_pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [ -n "$existing_pid" ] && kill -0 "$existing_pid" 2>/dev/null; then
        echo "A recording is already running (PID $existing_pid). Use Ctrl+Shift+S to stop it first." >&2
        log "no-op: recording already running (PID $existing_pid)"
        exit 0
    fi
    rm -f "$PID_FILE"
fi

if [ ! -x "$PYTHON_BIN" ]; then
    echo "ERROR: Python venv missing at $PYTHON_BIN. Run setup.sh first." >&2
    log "ERROR: Python venv missing at $PYTHON_BIN"
    exit 1
fi
if [ ! -f "$RECORD_PY" ]; then
    echo "ERROR: record_meeting.py missing at $RECORD_PY" >&2
    log "ERROR: record_meeting.py missing at $RECORD_PY"
    exit 1
fi

# Same device names as scripts/os-hotkey-start.sh. Edit both if your devices
# are renamed or you switch headsets.
HEADPHONE_OUTPUT_NAME="JBL TUNE770NC"
HEADPHONE_MULTIOUT="Headphones + Capture"
HEADPHONE_CAPTURE_DEV="BlackHole 2ch"
SPEAKER_MULTIOUT="Meeting Capture"
SPEAKER_CAPTURE_DEV="Meeting Capture"

SAS="/opt/homebrew/bin/SwitchAudioSource"
[ -x "$SAS" ] || SAS="$(command -v SwitchAudioSource 2>/dev/null || true)"

CAPTURE_DEVICE=""
ROUTE_NOTE="SwitchAudioSource not installed -> using pysysaudio system tap (default)"

if [ -n "$SAS" && -x "$SAS" ]; then
    # Capture current output device so the stop task can restore it. Multi-Output
    # Devices disable macOS software volume control, so the original device must
    # be re-selected afterward to give the volume slider / F11-F12 back.
    "$SAS" -c -t output > "$ORIG_OUTPUT_FILE" 2>/dev/null || rm -f "$ORIG_OUTPUT_FILE"

    available_outputs="$("$SAS" -a -t output 2>/dev/null || true)"
    if echo "$available_outputs" | grep -qF "$HEADPHONE_OUTPUT_NAME"; then
        if "$SAS" -s "$HEADPHONE_MULTIOUT" >/dev/null 2>&1; then
            CAPTURE_DEVICE="$HEADPHONE_CAPTURE_DEV"
            ROUTE_NOTE="$HEADPHONE_OUTPUT_NAME detected -> routing via $HEADPHONE_MULTIOUT (capture: $HEADPHONE_CAPTURE_DEV)"
        else
            ROUTE_NOTE="WARNING: $HEADPHONE_OUTPUT_NAME detected but '$HEADPHONE_MULTIOUT' multi-output device missing. Falling back to system tap."
        fi
    else
        if "$SAS" -s "$SPEAKER_MULTIOUT" >/dev/null 2>&1; then
            CAPTURE_DEVICE="$SPEAKER_CAPTURE_DEV"
            ROUTE_NOTE="No headphones -> routing via $SPEAKER_MULTIOUT (capture: $SPEAKER_CAPTURE_DEV)"
        else
            ROUTE_NOTE="WARNING: '$SPEAKER_MULTIOUT' multi-output device missing. Falling back to system tap."
        fi
    fi
fi

echo "[audio] $ROUTE_NOTE"
echo "[cwd]   $(pwd)"
echo
log "launched recorder in Cursor terminal; route=$ROUTE_NOTE"

if [ -n "$CAPTURE_DEVICE" ]; then
    exec "$PYTHON_BIN" "$RECORD_PY" --device "$CAPTURE_DEVICE" --mic --diarize
else
    exec "$PYTHON_BIN" "$RECORD_PY" --mic --diarize
fi
