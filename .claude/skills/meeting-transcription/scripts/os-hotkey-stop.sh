#!/usr/bin/env bash
# OS-level hotkey: STOP an in-progress meeting recording.
#
# Designed to be triggered by a system-wide keyboard shortcut (e.g., Ctrl+Shift+S)
# via macOS Shortcuts.app, so it works in ANY app without depending on
# tool-specific keybindings.
#
# Sends SIGINT (same as Ctrl+C) to the recorder process, which triggers the
# graceful stop path: flush WAV, run transcription, write recording.json.

set -euo pipefail

PID_FILE="$HOME/.meeting-recording.pid"
ORIG_OUTPUT_FILE="$HOME/.meeting-recording.original-output"
LOG_FILE="$HOME/.meeting-recording.log"

log() {
    printf '[%s] [stop]  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG_FILE"
}

log "hotkey pressed"

notify() {
    osascript -e "display notification \"$1\" with title \"Meeting Recording\""
}

# Restore the audio output device to whatever was active before recording started.
# Multi-Output Devices used during recording disable macOS software volume control,
# so re-selecting a non-Multi-Output device is what gives the volume slider back.
# If the original device disconnected during recording (e.g., Bluetooth headphones),
# fall back to MacBook Pro Speakers so the user is never left volume-locked.
FALLBACK_OUTPUT="MacBook Pro Speakers"
restore_output_device() {
    local sas="/opt/homebrew/bin/SwitchAudioSource"
    [ -x "$sas" ] || sas="$(command -v SwitchAudioSource 2>/dev/null || true)"
    if [ -z "$sas" || ! -x "$sas" ]; then
        log "restore: SwitchAudioSource not available, skipping"
        rm -f "$ORIG_OUTPUT_FILE"
        return 0
    fi

    local orig=""
    [ -f "$ORIG_OUTPUT_FILE" ] && orig="$(cat "$ORIG_OUTPUT_FILE" 2>/dev/null || true)"

    if [ -n "$orig" ] && "$sas" -s "$orig" >/dev/null 2>&1; then
        log "restore: output set to '$orig'"
    else
        if "$sas" -s "$FALLBACK_OUTPUT" >/dev/null 2>&1; then
            log "restore: original '${orig:-<none>}' unavailable, fell back to '$FALLBACK_OUTPUT'"
        else
            log "restore: ERROR — failed to restore '${orig:-<none>}' AND fallback '$FALLBACK_OUTPUT'; volume may still be locked"
        fi
    fi
    rm -f "$ORIG_OUTPUT_FILE"
}

if [ ! -f "$PID_FILE" ]; then
    log "no-op: no PID file (no active recording)"
    restore_output_device
    notify "No active recording found."
    afplay /System/Library/Sounds/Funk.aiff &>/dev/null &
    exit 1
fi

pid="$(cat "$PID_FILE" 2>/dev/null || true)"

if [ -z "$pid" ]; then
    log "no-op: empty PID file (removed)"
    rm -f "$PID_FILE"
    restore_output_device
    notify "Stale PID file (empty). Removed."
    afplay /System/Library/Sounds/Funk.aiff &>/dev/null &
    exit 1
fi

if ! kill -0 "$pid" 2>/dev/null; then
    log "no-op: PID $pid already exited (stale file removed)"
    rm -f "$PID_FILE"
    restore_output_device
    notify "No active recording (process $pid already exited). Removed stale PID file."
    afplay /System/Library/Sounds/Funk.aiff &>/dev/null &
    exit 1
fi

if kill -INT "$pid" 2>/dev/null; then
    log "SIGINT sent to PID $pid"
    restore_output_device
    afplay /System/Library/Sounds/Glass.aiff &>/dev/null &
    notify "Stop signal sent. Transcription will run in the recording terminal."
else
    log "ERROR: failed to signal PID $pid"
    notify "ERROR: failed to signal PID $pid. Check process state manually."
    afplay /System/Library/Sounds/Basso.aiff &>/dev/null &
    exit 1
fi
