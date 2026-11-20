---
name: meeting-transcription
description: Transcribe and process meeting recordings using the insourced WhisperX pipeline. Handles audio capture (native macOS system audio tap via pysysaudio), speaker diarization, speaker-to-name mapping, and meeting synthesis. Use when the user mentions meeting transcription, meeting notes, speaker mapping, speaker diarization, or processing meeting audio.
---

## Quick Start

**Automated (recommended):** Run the setup script — it handles dependencies, venv, speaker profiles, and guides you through the rest:

```bash
bash .claude/skills/meeting-transcription/setup.sh
```

**Manual setup** (4 required + 1 optional):

1. **Install dependencies:** `brew install ffmpeg && curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **Python venv:** `uv venv ~/.local/share/meeting-transcription/venv --python 3.12` then `uv pip install --python ~/.local/share/meeting-transcription/venv/bin/python -r .claude/skills/meeting-transcription/scripts/requirements.txt` (includes pysysaudio for native system audio capture)
3. **Set HuggingFace token:** `export HF_TOKEN="hf_xxx"` (add to ~/.zshrc). Accept model license: [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1)
4. **Output directory:** `mkdir -p ~/meetings`
5. **Optional — Google Workspace MCP:** Add `google-workspace` via `claude mcp add` — includes Calendar + Sheets + Docs + Drive + Slides. Enables automatic attendee lookup; without it, provide attendees manually. (MCP config is written to `~/.claude.json` for user-scoped servers or workspace `.mcp.json` for project-scoped; let `claude mcp add` manage it rather than hand-editing.)

**Permission:** On first recording, macOS will prompt for "Screen & System Audio Recording" permission. [Care Delivery director] it for your Python interpreter or Terminal. This is a one-time step.

## Per-Meeting Workflow

Three steps — record, map, synthesize.

### Keyboard Shortcuts

| Shortcut | Action | Scope |
|----------|--------|-------|
| `Ctrl+Shift+R` | Start recording | While Cursor has focus (active setup — see [Cursor-Only Hotkey](#cursor-only-hotkey) below). Can be extended to work anywhere in macOS — see [OS-Level Hotkeys](#os-level-hotkeys). |
| `Ctrl+Shift+S` | Stop recording | Same as above |
| `Ctrl+C` | Stop recording (alternative) | In the terminal where the recorder is running |

### Step 1: Record

**Press `⌃⇧R` (Ctrl+Shift+R) while Cursor has focus.** It:
- Opens a new terminal inside Cursor with the recorder running (see [Cursor-Only Hotkey](#cursor-only-hotkey))
- Captures system audio natively via Core Audio tap (no virtual audio device needed)
- Includes microphone input (`--mic`) for your voice
- Enables speaker diarization (`--diarize`)

Works with any meeting app (Meet, Teams, Zoom) and any audio output (headphones, speakers) — no configuration needed. To trigger it from outside Cursor too (Slack, browser, mid-meeting in Meet/Zoom), set up the [OS-Level Hotkeys](#os-level-hotkeys) path, which opens Terminal.app instead and is not yet configured on Danny's machine.

**Alternative — CLI** (if you'd rather invoke directly):

```bash
# All meeting types (Meet, Teams, Zoom — all captured the same way):
record-meeting --mic --diarize
```

Press `⌃⇧S` when the meeting ends (or `Ctrl+C` in the terminal running the recorder). Auto-stops after 10 min silence. Output: `Meeting Transcripts/YYYY-MM-DD_HHMMSS/recording.json` (folder is renamed to include the meeting name during Step 2)

**Shell function** (already in `~/.zshrc`; auto-routes audio and forwards all flags):
```bash
record-meeting() {
    local python_bin="$HOME/.local/share/meeting-transcription/venv/bin/python"
    local record_py="$HOME/Library/CloudStorage/GoogleDrive-you@example.com/My Drive/Cursor Files/.claude/skills/meeting-transcription/scripts/record_meeting.py"
    local orig_output_file="$HOME/.meeting-recording.original-output"
    local dev=""
    if command -v SwitchAudioSource >/dev/null 2>&1; then
        # Save current output so Ctrl+Shift+S (os-hotkey-stop.sh) can restore it later,
        # even though this recording was started manually, not via a hotkey.
        SwitchAudioSource -c -t output > "$orig_output_file" 2>/dev/null || rm -f "$orig_output_file"
        if SwitchAudioSource -a -t output | grep -q "JBL TUNE770NC"; then
            SwitchAudioSource -s "Headphones + Capture" && dev="BlackHole 2ch" && echo "[audio] Headphones detected → routing via Headphones + Capture"
        else
            SwitchAudioSource -s "Meeting Capture" && dev="Meeting Capture" && echo "[audio] No headphones → routing via Meeting Capture (speaker mode)"
        fi
    fi
    if [ -n "$dev" ]; then
        "$python_bin" "$record_py" --device "$dev" "$@"
    else
        "$python_bin" "$record_py" "$@"
    fi
}
```

> **Legacy device fallback:** If you need to capture from a specific audio device (e.g., ZoomAudioDevice), pass `--device "ZoomAudioDevice"`. This bypasses the native system audio tap and uses sounddevice directly, which may require additional audio routing setup.

### Step 2: Map Speakers

After stopping the recording, say **"my meeting just ended"** or **"process my recording"** in Claude Code. The speaker-mapping agent selects a recording from `Meeting Transcripts/` automatically. No need to open the file or invoke the agent manually.

- Agent picks unprocessed recordings (have `recording.json` but no `mapping.json`): exactly 1 → auto-selects; multiple → lists and asks you to pick; 0 → tells you all are processed and offers re-process
- You can always override with an explicit path
- Agent auto-fetches attendees from Google Calendar MCP (or provide names manually)
- Optionally identify yourself ("SPEAKER_02 is me")
- Review and confirm the mapping
- Agent writes `*_named.txt` + `mapping.json` + updates speaker profiles with new evidence

### Step 3: Synthesize

Choose a synthesis mode based on the meeting type:

| Mode | When to Use | Skill |
|------|-------------|-------|
| **Discovery** (default) | Discovery sessions, research interviews, deep-dives | `discovery-synthesis` |
| **Skip** | Named transcript is sufficient | None — stop at Step 2 |

**Discovery synthesis** produces structured research notes with key findings, verbatim quotes, workflow documentation, and action items. **Skip** when the named transcript is the deliverable.

**Output locations:**
- WAV staging (temporary) in `~/meetings/YYYY-MM-DD_HHMMSS/` — deleted after processing
- All meeting artifacts live in one folder: `Meeting Transcripts/YYYY-MM-DD_Meeting_Name/`
  - Recording JSON initially saved to `Meeting Transcripts/YYYY-MM-DD_HHMMSS/`; during speaker mapping (Step 2), the folder is **renamed** using the Calendar event title (e.g., `2026-03-16_Outbound_Staging_&_Manifesting_Qs`). Falls back to timestamp if no Calendar event found.
  - `transcript.md` — human-readable named transcript with meeting header (date, attendees)
  - `mapping.json` — speaker mapping with confidence and evidence
  - `recording.json` — raw WhisperX output
- Synthesis outputs go wherever the user directs — synthesis agents ask the user where to save

## Cursor-Only Hotkey

`⌃⇧R` / `⌃⇧S` are bound in Cursor's own keybindings, independent of macOS Shortcuts.app. This is the active setup on Danny's machine. It only fires while a Cursor window has focus — editor, sidebar, or terminal. For a hotkey that also works in Slack, the browser, or a meeting app, see [OS-Level Hotkeys](#os-level-hotkeys) below; the two mechanisms don't conflict and can run side by side.

**How it works:** each keybinding uses VS Code's built-in `runCommands` to open a new integrated terminal, then types the recorder command into it.

| Key | Config | Behavior |
|-----|--------|----------|
| `Ctrl+Shift+R` | `~/Library/Application Support/Cursor/User/keybindings.json` | Opens a new Cursor terminal, runs `scripts/cursor-hotkey-start.sh` — resolves audio routing (JBL → `Headphones + Capture`/`BlackHole 2ch`; otherwise → `Meeting Capture`), then execs `record_meeting.py --mic --diarize` in the foreground so live status (audio levels, mic gain) is visible in that terminal panel. |
| `Ctrl+Shift+S` | Same file | Opens a new Cursor terminal, runs `scripts/os-hotkey-stop.sh` — reads the PID from `~/.meeting-recording.pid` and sends SIGINT for a graceful stop (flush WAV, transcribe, write `recording.json`), then restores the pre-recording audio output device. Terminal-agnostic: it works regardless of which terminal started the recording. |

Both keybindings log to `~/.meeting-recording.log` (prefixes `[cursor-start]` / `[stop]`) alongside the OS-level hotkey log entries, so `tail -f ~/.meeting-recording.log` shows a unified history across both trigger paths.

**Setup (already done on Danny's machine):** the two entries live in `~/Library/Application Support/Cursor/User/keybindings.json`. To replicate on another machine, add the `ctrl+shift+r` / `ctrl+shift+s` entries there, pointing at the absolute path to this repo's `.claude/skills/meeting-transcription/scripts/` directory (keybindings.json is user-level and doesn't resolve `${workspaceFolder}`, so the path must be hardcoded).

**Limitation:** `.vscode/tasks.json` was the first design considered here, but Cursor's agent tooling refuses to write under `.vscode/` (task/settings files there can auto-execute code, so writes are blocked as a guardrail). The `runCommands` + `sendSequence` approach avoids that file entirely.

**If the hotkey does nothing:** check Cursor's Keyboard Shortcuts search (Cmd+K Cmd+S, search "ctrl+shift+r") for a conflicting default binding, and confirm `runCommands` is supported in your Cursor version (stable in VS Code since 1.77; Cursor tracks upstream closely).

## OS-Level Hotkeys

Recording start/stop can also work **anywhere in macOS** — Claude Code, Slack, browser, mid-meeting in Meet/Zoom — by binding the helper scripts via macOS Shortcuts.app. This path is not currently set up (no Shortcuts.app automations exist on Danny's machine as of Oct 2026); use it if you need the hotkey outside Cursor.

**Helper scripts (already shipped with the skill):**

| Script | Action | Behavior |
|--------|--------|----------|
| `scripts/os-hotkey-start.sh` | Start recording | Pre-resolves audio routing via `SwitchAudioSource` (JBL detected → `Headphones + Capture` multi-output → captures `BlackHole 2ch`; otherwise → `Meeting Capture` multi-output → captures `Meeting Capture`). Saves the pre-recording output device to `~/.meeting-recording.original-output` so stop.sh can restore it. Opens Terminal.app with the resolved command + `--mic --diarize`. Detects existing recording (notifies, exits cleanly) so double-presses don't break things. macOS notification announces the chosen audio route. |
| `scripts/os-hotkey-stop.sh` | Stop recording | Sends SIGINT to the process in `~/.meeting-recording.pid`, then restores the original output device from `~/.meeting-recording.original-output` (so the volume slider / F11-F12 work again — Multi-Output Devices disable software volume control by macOS design). Plays Glass.aiff on success, Funk.aiff on no-op. macOS notification confirms the action. |

Both scripts append a timestamped entry to **`~/.meeting-recording.log`** on every press — including no-ops and errors — so you can verify whether a hotkey actually fired even if you missed the macOS notification. Tail it live during testing: `tail -f ~/.meeting-recording.log`.

Both scripts are idempotent and degrade gracefully — safe to bind to a hotkey. If `SwitchAudioSource` isn't installed or a multi-output device is missing, `os-hotkey-start.sh` falls back to the pysysaudio system tap with a warning in the notification.

**Audio routing prerequisites** (already configured on Danny's machine):
- `brew install switchaudio-osx` provides `SwitchAudioSource`
- `Audio MIDI Setup.app` → create two Multi-Output Devices: `Headphones + Capture` (JBL + BlackHole) and `Meeting Capture` (MacBook Pro Speakers + BlackHole). The recorder captures from the BlackHole side; you hear via the speaker/headphone side.

**Customizing device names:** edit the `HEADPHONE_*` / `SPEAKER_*` variables at the top of `os-hotkey-start.sh` if your devices are renamed or you switch headsets. This only affects the OS-level path — if you're using the active [Cursor-Only Hotkey](#cursor-only-hotkey) instead, edit the same variables in `cursor-hotkey-start.sh`.

**One-time setup (~90 seconds):**

1. Open **Shortcuts.app** (Spotlight → "Shortcuts")
2. Create the **start** shortcut:
   - `+` to create new → name it `Start Meeting Recording`
   - Search the action library for **"Run Shell Script"** → drag into the workflow
   - In the script box, paste: `bash "$HOME/Library/CloudStorage/GoogleDrive-you@example.com/My Drive/Cursor Files/.claude/skills/meeting-transcription/scripts/os-hotkey-start.sh"`
   - Set "Pass Input" to **None**
   - Click the shortcut name at top → **"Add Keyboard Shortcut"** → press `⌃⇧R`
3. Repeat for the **stop** shortcut, naming it `Stop Meeting Recording`, pointing at `os-hotkey-stop.sh`, bound to `⌃⇧S`
4. Test: press `⌃⇧R` from anywhere → Terminal opens with the recorder. Press `⌃⇧S` → notification fires, Terminal shows transcription beginning.

**To customize recording flags** (e.g., add `--no-diarize` or change to a USB mic): edit the `PY_CMD` line near the bottom of `os-hotkey-start.sh`, where `--mic --diarize` is hardcoded.

**No automation permission required.** The start script launches Terminal.app via a `.command` file + `open -a Terminal` rather than AppleScript, so no "Send Apple events" permission prompt fires (avoids macOS error `-1743`). macOS may show a one-time notification permission prompt the first time `osascript -e "display notification..."` runs from a new caller — allow it.

## Configuration

**Hotkey config:**

| Config | Path | Purpose |
|--------|------|---------|
| OS-level helpers | `.claude/skills/meeting-transcription/scripts/os-hotkey-{start,stop}.sh` | Start/stop scripts bound via macOS Shortcuts.app (see [OS-Level Hotkeys](#os-level-hotkeys) above). Not currently configured on Danny's machine. |
| Cursor keybinding | `~/Library/Application Support/Cursor/User/keybindings.json` | Start/stop bound via Cursor's `runCommands` (see [Cursor-Only Hotkey](#cursor-only-hotkey) above). Active setup on Danny's machine. Uses `scripts/cursor-hotkey-start.sh` for start and reuses `scripts/os-hotkey-stop.sh` for stop. |

The OS-level path always runs the recorder in Terminal.app (separate window), regardless of which app has focus when you press the hotkey — same behavior every time, no behavior drift between contexts. The Cursor keybinding path instead opens a new terminal inside Cursor itself.

**Script options** — no config file. All options are CLI args:

| Flag | Default | Purpose |
|------|---------|---------|
| `--mic` | off | Include microphone input |
| `--device` | None (native system audio tap) | Legacy: capture from a named audio device via sounddevice (e.g., "ZoomAudioDevice") |
| `--mic-device` | built-in laptop mic | Mic device when using --mic. Precedence: `--mic-device` > `$MEETING_MIC_DEVICE` env var > built-in laptop mic (MacBook Pro/Air Microphone, Built-in Microphone) > macOS system default. Locked to built-in mic by default to prevent Bluetooth headsets from being silently picked up and stolen by the meeting app. |
| `--silence-timeout` | 600 | Auto-stop after N seconds silence |
| `--model` | large-v3-turbo | Whisper model |
| `--language` | en | Language code |
| `--initial-prompt` | domain terms | Whisper vocabulary prompt |
| `--no-condition-previous` | off | Disable conditioning on previous text |
| `--diarize` | on | Enable speaker diarization |
| `--no-diarize` | — | Disable diarization |
| `--min-speakers` | — | Hint for pyannote |
| `--max-speakers` | — | Hint for pyannote |
| `--hf-token` | $HF_TOKEN | HuggingFace token |
| `--output-dir` | `Meeting Transcripts/YYYY-MM-DD_HHMMSS` (JSON); `~/meetings/YYYY-MM-DD_HHMMSS` (WAV staging) | Output directory |
| `--keep-audio` | off | Keep WAV after transcription |
| `--file` | — | Transcribe existing file instead of recording |

**Workspace output:** Each meeting gets one folder directly under `Meeting Transcripts/` — e.g., `Meeting Transcripts/YYYY-MM-DD_Meeting_Name/` containing `recording.json`, `transcript.md`, and `mapping.json`. Synthesis agents ask the user where to save (e.g., `Initiatives/[Name]/Discovery Notes/`); synthesis is not stored in `Meeting Transcripts/` by default.

## Architecture Note

`record_meeting.py` captures system audio via **pysysaudio** (macOS native Core Audio process taps — no virtual audio device needed), then feeds it to **WhisperX** (which uses **faster-whisper** / CTranslate2 for transcription) and **pyannote Community-1** for diarization. Pipeline: capture → transcribe → align (word-level timestamps) → diarize → JSON. Same model weights (large-v3-turbo), comparable accuracy to mlx-whisper, but typically 4–7x slower on Apple Silicon. Tradeoff: single-command capture + transcription + diarization with no external service.

When `--device` is specified, the script falls back to **sounddevice** (PortAudio) for capturing from a named device (e.g., ZoomAudioDevice for Zoom-only audio isolation).

### Pre-flight & Runtime Audio Health Checks

The script validates audio capture at three points so you don't lose 28 minutes of meeting to a silent recording:

- **Pre-flight (before recording starts):** Prints a summary of the resolved mic device, current audio output device (flags Bluetooth), and macOS mic input volume via `osascript`. Warns loudly if mic volume < 100% (yellow); red warning + 5-second abort window if < 50%. Lets you catch wrong-device and wrong-volume errors in 5 seconds.
- **Runtime (5s into recording):** If `sys_db` stays below -90 dB for 5s, prints a red `[WARNING]` that system audio is not being captured (common with Bluetooth output or denied Screen Recording permission). If `mic_db` stays below -80 dB for 5s AND `--mic` is enabled, warns that your voice is likely not being captured (wrong mic device or meeting app holding the mic exclusively).
- **Post-flight (after recording ends):** Prints a `CAPTURE FAILURE DETECTED` summary if final sys or mic RMS indicate silent capture, recommending you skip transcription and fix the setup before re-recording.

All warnings include specific remediation steps. Skip the transcription phase when you see them — WhisperX will run for 15+ minutes on junk audio otherwise.

### Mic Device Resolution (Tool-Agnostic)

When `--mic` is enabled, the script resolves the input device at runtime — not via tool-specific config — so the same default applies whether invoked via the OS-level hotkey, Claude Code, or raw CLI. Precedence (highest → lowest):

1. `--mic-device "Device Name"` — explicit per-recording override
2. `$MEETING_MIC_DEVICE` env var — set in `~/.zshrc` for a permanent per-machine pin
3. Built-in laptop mic (`MacBook Pro Microphone` → `MacBook Air Microphone` → `Built-in Microphone`) — the safe default
4. macOS system default input — last resort, prints a warning

This locks the mic away from Bluetooth headsets that get exclusive-claimed by Meet/Zoom/Teams. To switch to a USB mic permanently: `echo 'export MEETING_MIC_DEVICE="Blue Snowball"' >> ~/.zshrc && source ~/.zshrc`.

### Mic Gain Matching

When `--mic` is enabled, the script dynamically matches the microphone RMS level to the system audio RMS level before mixing. Without this, mic audio (your voice) is typically much quieter than system audio (remote participants), causing WhisperX to under-detect or mis-diarize the local speaker.

- **Warmup:** First ~3 seconds of audio establish baseline RMS levels for both sources
- **Dynamic gain:** After warmup, mic signal is boosted by `sys_rms / mic_rms` (floor: 3x, cap: 40x) before mixing. Gain starts at the floor (3x) immediately — no silent first few seconds.
- **Fast adaptation:** EMA smoothing factor of 0.15 means the gain adjusts meaningfully within ~7 chunks (~0.7s), not the ~60 chunks the old 0.05 required.
- **Real-time monitoring:** The recording status line shows live dB levels and gain: `[sys:-18dB mic:-42dB gain:5.2x]`
- **Metadata:** Final gain stats are saved in `recording.json` under `metadata.mic_gain` for post-hoc analysis

## Domain Vocabulary

Solved via `--initial-prompt`. The script includes a built-in default with pharmacy/fulfillment terms (PV2, beyondRx, HighJump, etc.). Override for other domains:

```bash
record-meeting --initial-prompt "Terms: acronym1, acronym2, proper nouns"
```

See `reference/domain-vocabulary.md` for the full term list and known misrecognition patterns.

## Agent Rules

This pipeline uses Claude Code skills for speaker mapping and synthesis:

| Agent | File | Trigger | Purpose |
|-------|------|---------|---------|
| Speaker Mapping | `.claude/skills/speaker-mapping/SKILL.md` | "My meeting just ended" / "process my recording" | Maps SPEAKER_XX → real names; auto-selects unprocessed recording (or lists/asks if multiple; offers re-process if all done) |
| Discovery Synthesis | `.claude/skills/discovery-synthesis/SKILL.md` | Manual invocation | Transforms named transcript into structured research notes (default for discovery meetings) |

## Speaker Profiles

Profiles help the speaker-mapping agent identify speakers by their voiceprints, topics, verbal patterns, structured behavior summary, comms preferences, and recent-meeting recency.

- **Location:** `.claude/skills/meeting-transcription/profiles/speaker-profiles.json`
- **Schema reference:** `<speaker_profile_format>` block in `.claude/skills/speaker-mapping/SKILL.md`

Each profile carries: identity (name/email/role/team), `topics` (cap 30), `verbal_patterns` (cap 20), `behavior_notes` (immutable historical prose), `behavior_summary` (structured fields), `recent_observations` (cap 10), `comms_prefs`, `recency`, and `voice_embedding` (pyannote vector for cross-meeting speaker matching). Org-chart relationships (`reports_to`, `direct_reports`) live in `Stakeholder Management/stakeholder-directory.md`, not in profiles.

To add a new person: copy an existing profile entry, update the fields. The speaker-mapping agent also creates new profiles automatically when it encounters unrecognized speakers (Step 8).

## CLI Quick Reference

| Command | Purpose |
|---------|---------|
| `record-meeting --mic --diarize` | Record any meeting (system audio + mic) |
| `record-meeting --file recording.wav` | Transcribe existing audio file |
| `record-meeting --no-diarize` | Transcribe only, no speaker IDs |
| `record-meeting --keep-audio` | Keep WAV after transcription |
| `record-meeting --device "ZoomAudioDevice" --mic --diarize` | Legacy: capture from a specific audio device |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Hotkey (`⌃⇧R` / `⌃⇧S`) silently does nothing | Check `~/.meeting-recording.log` — every press is logged with timestamp + outcome (success, no-op, error), with `[cursor-start]`/`[stop]` prefixes. If the log is empty: for the Cursor keybinding, check Cursor's Keyboard Shortcuts search for a conflicting default binding on `ctrl+shift+r`/`ctrl+shift+s`; for the OS-level path, verify the macOS Shortcut binding in Shortcuts.app. If the log shows `ERROR: record_meeting.py missing`, the path in the triggering script (`cursor-hotkey-start.sh` or `os-hotkey-start.sh`) is wrong (should be `.claude/skills/...`, not `.cursor/skills/...`). |
| "Screen & System Audio Recording permission not granted" | System Settings → Privacy & Security → Screen & System Audio Recording → enable for Python/Terminal |
| No audio captured | Verify permission is granted; check that a meeting app is playing audio |
| Only captured your voice, not remote participants | System audio capture should get remote audio. If using `--device`, ensure the device routes meeting audio. |
| Only hearing remote participants, not your voice | Add `--mic` flag |
| Your voice transcribed poorly or merged with another speaker | **First:** check macOS mic input volume — System Settings → Sound → Input → set to 100% (50% is the macOS default and too low). The script now checks this at startup and prints a prominent `[WARNING]` if below 100% (red + 5s abort window if <50%). **Then:** check gain stats in `recording.json` → `metadata.mic_gain`. If `mic_rms_db` is much lower than `sys_rms_db` (>20dB gap) and `mic_gain_applied` is at max (40x), your mic input level is still too low — try an external mic or move closer. Also check the real-time status line during recording: `[sys:-18dB mic:-42dB gain:5.2x]` shows live levels. |
| Entire recording is silent (sys_db stays at -120) | The system audio tap captured nothing for the full session. Usually caused by: (1) Bluetooth output device (AirPods/Beats) — process taps fail on some macOS versions, try wired headphones; (2) Screen & System Audio Recording permission not granted to the Python binary running `record_meeting.py`; (3) pysysaudio version bug — try `pip install --upgrade pysysaudio`. The script now fires a red runtime `[WARNING]` after 5s if `sys_db < -90`, so you'll see the failure live instead of 28 minutes in. |
| Your voice missing entirely from transcript (only remote participants captured) | Root cause: your headset mic is owned by the meeting app (Meet/Zoom/Teams), so the recorder got a degraded/silent stream from the same Bluetooth device. **The script now defaults to the built-in laptop mic to avoid this entirely** — see `BUILTIN_MIC_CANDIDATES` in `record_meeting.py`. To pin a different mic permanently across Claude Code and CLI, set `export MEETING_MIC_DEVICE="Your USB Mic Name"` in `~/.zshrc`. To override per-recording, pass `--mic-device "Device Name"`. The pre-flight summary prints the resolved mic device so you can verify before the meeting starts. |
| Echo/feedback | Use headphones (mic picks up speaker output without headphones) |
| Diarization not working | Check `HF_TOKEN` is set; accept model licenses on huggingface.co |
| Memory pressure / OOM | 16 GB RAM recommended; try `--model medium` |
| Speaker IDs change between meetings | Expected — speaker mapping resolves this per-meeting |
| 0 segments / "No active speech found" | VAD found no speech. **Solo 1:1-with-yourself recordings:** system audio tap captures remote participants' audio — in a solo call there are none, so the recording is near-silent. The pipeline now auto-normalizes quiet audio and uses a lower VAD threshold, which helps when mic captures your voice. If it still fails, the WAV is auto-retained for re-processing. |
| Domain terms misrecognized | Customize `--initial-prompt` with your vocabulary |
| Headphones/mic disconnected mid-recording | Handled automatically — script detects the device loss, logs `[mic disconnected]`, and continues recording system audio only. Audio is streamed to disk so nothing is lost. |
| pysysaudio not working / zero audio | Try updating: `pip install --upgrade pysysaudio`. If persistent, use `--device` fallback with any virtual audio device (e.g., `--device "ZoomAudioDevice"`). |
| Volume slider greyed out / F11-F12 do nothing after recording | macOS does not support software volume control on **Multi-Output Devices** — while output is routed via `Headphones + Capture` or `Meeting Capture`, the volume slider is intentionally disabled by Apple. `os-hotkey-stop.sh` now auto-restores your original output device on stop (saved to `~/.meeting-recording.original-output` by whichever start script ran — `os-hotkey-start.sh` or `cursor-hotkey-start.sh`), so volume control returns automatically. **Manual fix if it ever gets stuck:** run `SwitchAudioSource -s "MacBook Pro Speakers"` (or your preferred output) — re-selecting the device resets Core Audio's volume-control state. |

## Roadmap

Future improvements, roughly priority-ordered:

| # | Item | Why It Matters |
|---|------|---------------|
| 1 | Remove `Ctrl+C` as stop-recording method | Fragile UX — accidental presses kill the process; `Ctrl+Shift+S` is the proper path |
| 2 | Automate speaker-mapping trigger after recording stops | Eliminates manual "my meeting just ended" step; end-to-end hands-free pipeline |
| 3 | Streamline discovery synthesis agent questions | Too many prompts slow the user down; reduce to essentials or infer from context |
| 4 | Improve discovery synthesis output format | Better readability and scannability |
| 5 | Capture periodic screenshots during recording for additional context | Leverage existing Screen Recording permission to grab screen images throughout the meeting; feed to synthesis agents for richer context (shared screens, slides, diagrams) that audio alone misses |

## Additional Resources

- Full implementation spec: see [implementation-spec](reference/Meeting-Transcription-Pipeline-Implementation-Spec.md)
- Speaker ID accuracy expectations and improvement roadmap: implementation spec, Section 4
- Speaker ID research and techniques: see [Speaker-Identification-Accuracy-Improvements-2026.md](reference/Speaker-Identification-Accuracy-Improvements-2026.md)
- Domain vocabulary and known misrecognitions: see [domain-vocabulary.md](reference/domain-vocabulary.md)
