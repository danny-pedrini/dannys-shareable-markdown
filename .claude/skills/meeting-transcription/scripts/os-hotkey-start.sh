#!/usr/bin/env bash
# OS-level hotkey: START a meeting recording.
#
# Designed to be triggered by a system-wide keyboard shortcut (e.g., Ctrl+Shift+R)
# via macOS Shortcuts.app, so it works in ANY app — Claude Code, Slack,
# browser, etc. — without depending on tool-specific keybindings.
#
# Audio routing strategy:
#   1. If SwitchAudioSource is installed AND multi-output capture devices exist:
#        - JBL TUNE770NC connected → route via "Headphones + Capture" multi-output,
#          recorder captures from "BlackHole 2ch" (sounddevice path).
#        - Otherwise → route via "Meeting Capture" multi-output, recorder captures
#          from "Meeting Capture" (sounddevice path).
#      This is the proven path that reliably captures system audio while letting
#      the user hear it through their preferred output device.
#   2. Fallback (no SwitchAudioSource): use pysysaudio system tap (no --device
#      flag). Less reliable on Bluetooth output but zero-config.
#
# In all cases, --mic --diarize is added so your voice is captured and speakers
# are diarized. The script's mic device resolver picks the laptop built-in mic
# by default (see BUILTIN_MIC_CANDIDATES in record_meeting.py).
#
# Behavior:
#   - If a recording is already in progress: shows a macOS notification, exits 0.
#   - Otherwise: opens Terminal.app with a visible window so you can see pre-flight
#     warnings, live audio levels, and stop the recording with Ctrl+C as a fallback.

set -euo pipefail

PYTHON_BIN="$HOME/.local/share/meeting-transcription/venv/bin/python"
WORKSPACE_DIR="$HOME/Library/CloudStorage/GoogleDrive-you@example.com/My Drive/Cursor Files"
RECORD_PY="$WORKSPACE_DIR/.claude/skills/meeting-transcription/scripts/record_meeting.py"
PID_FILE="$HOME/.meeting-recording.pid"
ORIG_OUTPUT_FILE="$HOME/.meeting-recording.original-output"
LOG_FILE="$HOME/.meeting-recording.log"

log() {
    printf '[%s] [start] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG_FILE"
}

log "hotkey pressed"

# Names of devices in the user's audio setup. Edit these if your devices are renamed.
HEADPHONE_OUTPUT_NAME="JBL TUNE770NC"
HEADPHONE_MULTIOUT="Headphones + Capture"
HEADPHONE_CAPTURE_DEV="BlackHole 2ch"
SPEAKER_MULTIOUT="Meeting Capture"
SPEAKER_CAPTURE_DEV="Meeting Capture"

notify() {
    osascript -e "display notification \"$1\" with title \"Meeting Recording\""
}

# ─── Idempotency: bail if a recording is already running ─────────────────────
if [ -f "$PID_FILE" ]; then
    existing_pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [ -n "$existing_pid" ] && kill -0 "$existing_pid" 2>/dev/null; then
        log "no-op: recording already running (PID $existing_pid)"
        notify "Recording already running (PID $existing_pid). Use Ctrl+Shift+S to stop."
        afplay /System/Library/Sounds/Funk.aiff &>/dev/null &
        exit 0
    fi
    rm -f "$PID_FILE"
fi

# ─── Environment validation ──────────────────────────────────────────────────
if [ ! -x "$PYTHON_BIN" ]; then
    log "ERROR: Python venv missing at $PYTHON_BIN"
    notify "ERROR: Python venv not found at $PYTHON_BIN. Run setup.sh first."
    afplay /System/Library/Sounds/Basso.aiff &>/dev/null &
    exit 1
fi
if [ ! -f "$RECORD_PY" ]; then
    log "ERROR: record_meeting.py missing at $RECORD_PY"
    notify "ERROR: record_meeting.py not found. Check workspace path in this script."
    afplay /System/Library/Sounds/Basso.aiff &>/dev/null &
    exit 1
fi

# ─── Audio routing (pre-Terminal) ────────────────────────────────────────────
# Resolves the capture device name *before* opening Terminal so the user sees
# the routing decision in the macOS notification + the Terminal echo line.
CAPTURE_DEVICE=""
ROUTE_NOTE=""

# SwitchAudioSource lives at /opt/homebrew/bin which isn't in Shortcuts.app's PATH.
SAS="/opt/homebrew/bin/SwitchAudioSource"
[ -x "$SAS" ] || SAS="$(command -v SwitchAudioSource 2>/dev/null || true)"

if [ -n "$SAS" && -x "$SAS" ]; then
    # Capture current output device so stop.sh can restore it. Multi-Output Devices
    # disable software volume control, so the original device must be re-selected
    # to give the user back their volume slider / F11-F12 hotkeys.
    "$SAS" -c -t output > "$ORIG_OUTPUT_FILE" 2>/dev/null || rm -f "$ORIG_OUTPUT_FILE"

    available_outputs="$("$SAS" -a -t output 2>/dev/null || true)"
    if echo "$available_outputs" | grep -qF "$HEADPHONE_OUTPUT_NAME"; then
        if "$SAS" -s "$HEADPHONE_MULTIOUT" >/dev/null 2>&1; then
            CAPTURE_DEVICE="$HEADPHONE_CAPTURE_DEV"
            ROUTE_NOTE="$HEADPHONE_OUTPUT_NAME detected → routing via $HEADPHONE_MULTIOUT (capture: $HEADPHONE_CAPTURE_DEV)"
        else
            ROUTE_NOTE="WARNING: $HEADPHONE_OUTPUT_NAME detected but '$HEADPHONE_MULTIOUT' multi-output device missing. Falling back to system tap."
        fi
    else
        if "$SAS" -s "$SPEAKER_MULTIOUT" >/dev/null 2>&1; then
            CAPTURE_DEVICE="$SPEAKER_CAPTURE_DEV"
            ROUTE_NOTE="No headphones → routing via $SPEAKER_MULTIOUT (capture: $SPEAKER_CAPTURE_DEV)"
        else
            ROUTE_NOTE="WARNING: '$SPEAKER_MULTIOUT' multi-output device missing. Falling back to system tap."
        fi
    fi
else
    ROUTE_NOTE="SwitchAudioSource not installed → using pysysaudio system tap (default)"
fi

# ─── Build a self-contained .command file and `open` it ─────────────────────
# Why .command + `open` instead of AppleScript "tell Terminal":
#   AppleScript requires "Send Apple events" automation permission, which
#   triggers macOS error -1743 if the calling app (Cursor, Shortcuts.app, etc.)
#   hasn't been granted access. .command files are natively handled by
#   Terminal.app via macOS's standard file-open mechanism — zero permissions
#   required.
TEMP_SCRIPT="$(mktemp /tmp/meeting-record-XXXXXX.command)"
trap 'rm -f "$TEMP_SCRIPT"' ERR

# Use printf %q to escape every argument safely. Paths have spaces; this handles them.
if [ -n "$CAPTURE_DEVICE" ]; then
    PY_CMD="$(printf '%q %q --device %q --mic --diarize' "$PYTHON_BIN" "$RECORD_PY" "$CAPTURE_DEVICE")"
else
    PY_CMD="$(printf '%q %q --mic --diarize' "$PYTHON_BIN" "$RECORD_PY")"
fi

# Embed self-cleanup so the /tmp file is removed after recorder exits.
# Backgrounded with `(... &)` so cleanup doesn't block Terminal close.
cat > "$TEMP_SCRIPT" <<SHELL_EOF
#!/usr/bin/env bash
# cd to the workspace so record_meeting.py's relative --output-dir
# ('Meeting Transcripts/YYYY-MM-DD_HHMMSS') lands inside the workspace,
# not in \$HOME (Terminal.app's default cwd).
cd $(printf '%q' "$WORKSPACE_DIR") || { echo "ERROR: workspace not found: $WORKSPACE_DIR"; exit 1; }
echo "[audio] $ROUTE_NOTE"
echo "[cwd]   \$(pwd)"
echo
$PY_CMD
exit_code=\$?
(sleep 2 && rm -f "\$0") &
exit \$exit_code
SHELL_EOF

chmod +x "$TEMP_SCRIPT"

# `open -a Terminal` opens the .command file in Terminal.app. macOS's launch
# services route .command extension to Terminal by default. No osascript,
# no Apple events, no permission prompt.
open -a Terminal "$TEMP_SCRIPT"

log "launched Terminal with recorder; route=$ROUTE_NOTE"
afplay /System/Library/Sounds/Glass.aiff &>/dev/null &
notify "Recording started: $ROUTE_NOTE"
