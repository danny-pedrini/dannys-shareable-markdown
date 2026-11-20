# Meeting Transcription Pipeline: Implementation Spec

**Date:** March 2026
**Platform:** macOS Apple Silicon (M1/M2/M3/M4)
**Purpose:** End-to-end implementation guide for a personal meeting transcription pipeline. Insourced WhisperX + pysysaudio + pyannote.

---

## Pipeline Overview

```
Meeting (Zoom/Meet/Teams)
    ↓ [1. Record] record_meeting.py --mic --diarize (pysysaudio + WhisperX + pyannote) — Ctrl+Shift+S or Ctrl+C to stop
    │   WAV staging: ~/meetings/YYYY-MM-DD_HHMMSS/ (local only, deleted after processing)
Meeting Transcripts/JSON Files/YYYY-MM-DD_HHMMSS/recording.json (diarized transcript)
    ↓ [2. Speaker Mapping] speaker-mapping skill + attendee list + profiles
    │   Step 0: Mandatory timezone check via Google Calendar MCP get-current-time (never assume timezone)
    │   Attendees from: Google Calendar MCP (recommended) OR manual input
    │   Auto-detect: unprocessed folders (recording.json, no mapping.json); 1 → auto-select; >1 → list for user; 0 → all processed
Named transcript + mapping.json → same dir as recording.json (includes mentioned_not_speaking)
    ↓ [8. Profile Update] Mandatory — update .claude/skills/meeting-transcription/profiles/speaker-profiles.json
    ↓ [3. Synthesize] Choose mode per meeting:
    │   3a. Discovery synthesis (default) — structured research notes
    │   3b. General synthesis — summary + actions + decisions
    │   3c. Skip — stop at named transcript
Output: synthesis document (user-directed) + named transcript in Meeting Transcripts/
    ↓ [4. Cleanup] Auto-delete WAV from ~/meetings/; persistent files in Meeting Transcripts/
```

> **Architecture note:** The insourced script calls **WhisperX → faster-whisper** (CTranslate2) directly for transcription. WhisperX passes `initial_prompt` and `condition_on_previous_text` through to the ASR model natively. The script also handles both WhisperX auth kwargs (`use_auth_token` and `token`) to avoid upstream compatibility issues. **mlx-whisper** remains an option for speed-critical transcription (4–7x faster on Apple Silicon) but requires a separate manual pipeline — see [Appendix A: Alternative mlx-whisper](#appendix-a-alternative-mlx-whisper).

---

## Table of Contents

1. [Prerequisites and Setup](#1-prerequisites-and-setup)
2. [Per-Meeting Workflow](#2-per-meeting-workflow)
3. [Speaker Mapping Reference](#3-speaker-mapping-reference)
4. [Speaker Identification Accuracy](#4-speaker-identification-accuracy)
5. [Configuration Reference](#5-configuration-reference)
6. [Appendix A: Alternative mlx-whisper](#appendix-a-alternative-mlx-whisper)
7. [Appendix B: Troubleshooting](#appendix-b-troubleshooting)
8. [Appendix C: Batch Pipeline Utilities](#appendix-c-batch-pipeline-utilities)

---

# 1. Prerequisites and Setup

**One-time setup.** Complete before first use.

## Automated Setup

Run the setup script to automate most of the steps below:

```bash
bash .claude/skills/meeting-transcription/setup.sh
```

The script checks prerequisites, installs dependencies (ffmpeg, uv, Python venv with pysysaudio), checks permissions, and guides you through manual steps. Supports `--skip-warmup` (skip model download) and `--force` (overwrite existing configs). Safe to run multiple times.

## Requirements

| Requirement | Version/Command |
|-------------|-----------------|
| macOS | 14.2+ (Sonoma) |
| Apple Silicon | M1/M2/M3/M4 |
| Python | 3.12+ |
| ffmpeg | `brew install ffmpeg` |
| uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| pysysaudio | Installed via `pip install pysysaudio` (included in requirements.txt) |

## System Audio Capture

System audio is captured natively via **pysysaudio** (macOS Core Audio process taps). This requires:
- **macOS 14.2+** (Core Audio tap API)
- **"Screen & System Audio Recording" permission** — macOS prompts on first use, or grant manually via System Settings → Privacy & Security → Screen & System Audio Recording

No virtual audio device (BlackHole), audio output switching (SwitchAudioSource), or Audio MIDI Setup configuration is needed. The native tap captures all system audio regardless of output device (headphones, speakers, etc.).

**Recommended workflow:**
- **All meeting apps (Meet, Teams, Zoom):** `record-meeting --mic --diarize` or `Ctrl+Shift+R` — works with any audio output configuration

**Legacy fallback:** Pass `--device "DeviceName"` to bypass native capture and use sounddevice with a specific device (e.g., `--device "ZoomAudioDevice"` or `--device "BlackHole 2ch"`).

**Speaker mode caveat:** Without headphones, the mic picks up speaker audio. This can cause echo for remote participants and may reduce diarization accuracy.

## HuggingFace Token (Required for Diarization)

1. Create account: https://huggingface.co/join
2. Accept license: [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1)
3. Create token: https://huggingface.co/settings/tokens → choose **Read** token type (not Fine-grained) → name it (e.g., "meeting-transcription") → Create
4. `export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"` (add to `.zshrc` or shell profile)

## Pre-warm Models

The setup script runs model warmup automatically (unless `--skip-warmup`). To run manually:

```bash
~/.local/share/meeting-transcription/venv/bin/python -c "
import whisperx
whisperx.load_model('large-v3-turbo', device='cpu', compute_type='int8')
# With HF_TOKEN set, also warm diarization:
# from whisperx.diarize import DiarizationPipeline
# DiarizationPipeline(token=..., device='cpu')
"
```

First-run downloads: ~2–4 GB (WhisperX + pyannote).

## Speaker Profiles

Create `.claude/skills/meeting-transcription/profiles/speaker-profiles.json`:

```json
{
  "eric_spencer": {
    "name": "[Pharmacy Eng director]",
    "email": "teammate@example.com",
    "role": "Director of Engineering, Outbound Squad Lead",
    "team": "Fulfillment Engineering",
    "topics": ["system architecture", "Kotlin services", "beyondRx", "HighJump migration"],
    "verbal_patterns": ["tends to discuss technical tradeoffs", "often says 'let me check with the team'"],
    "meeting_behavior": "Usually speaks early, provides technical estimates"
  },
  "wesley_crouch": {
    "name": "[Director of Pharmacy & Fulfillment Product]",
    "email": "teammate@example.com",
    "role": "Director of Pharmacy & Fulfillment Product",
    "team": "Pharmacy Product",
    "topics": ["prioritization", "roadmap", "change management"],
    "verbal_patterns": ["asks clarifying questions", "frames decisions"],
    "meeting_behavior": "Often facilitates, summarizes decisions"
  }
}
```

## Google Calendar MCP (Optional — Attendee Lookup)

The speaker-mapping skill can use Google Calendar to automatically fetch meeting attendees. This is **recommended but optional** — without it, you provide attendees manually each meeting ("Attendees: [Pharmacy Eng director], [Director of Pharmacy & Fulfillment Product], Danny Pedrini"). One-time setup:

### 1. Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the **Google Calendar API**: APIs & Services → Library → search "Google Calendar API" → Enable
4. Create OAuth credentials:
   - APIs & Services → Credentials → Create Credentials → **OAuth client ID**
   - Application type: **Desktop app**
   - Download the JSON file (filename will be long, e.g., `client_secret_XXXXX.apps.googleusercontent.com.json`) → rename and save:
     ```bash
     mkdir -p ~/.config/google-calendar-mcp
     mv ~/Downloads/client_secret_*.json ~/.config/google-calendar-mcp/gcp-oauth.keys.json
     ```
     If the glob fails (`no matches found`), list `ls ~/Downloads/*.json` to find the exact filename.
5. Configure OAuth consent screen:
   - APIs & Services → OAuth consent screen → **External** (or Internal if Google Workspace)
   - Add scopes: `calendar.events`, `calendar.readonly`
   - Add your email as a **test user**

> **Note:** In test mode, OAuth tokens expire every 7 days. When this happens, re-run the `auth` command from Step 4. To avoid re-auth entirely, publish the app (or use Internal if your org allows it).

### 2. Install MCP Server

Requires Node.js 18+. No global install needed — `npx` handles it.

### 3. Add to Claude Code

MCP servers are configured in `~/.claude.json` (Claude Code's global MCP config). Add the `google-calendar` entry under `mcpServers`:

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "npx",
      "args": ["-y", "@cocal/google-calendar-mcp"],
      "env": {
        "GOOGLE_OAUTH_CREDENTIALS": "/Users/<your-username>/.config/google-calendar-mcp/gcp-oauth.keys.json"
      }
    }
  }
}
```

> **Important:** Use the full absolute path (e.g., `/Users/dpedrini/.config/...`), not `~`. The MCP server does not expand `~` and will resolve it relative to the workspace root, causing an `ENOENT` error.

### 4. Authenticate

Restarting Claude Code will **not** trigger the OAuth flow. You must run the auth command explicitly in your terminal:

```bash
GOOGLE_OAUTH_CREDENTIALS="/Users/<your-username>/.config/google-calendar-mcp/gcp-oauth.keys.json" \
  npx -y @cocal/google-calendar-mcp auth
```

This opens a browser for Google OAuth consent. Approve access. Tokens are saved to `~/.config/google-calendar-mcp/tokens.json` and refresh automatically until they expire (7 days in test mode). After auth completes, restart Claude Code so the MCP server picks up the new tokens.

### 5. Verify

In Claude Code, ask: "List my calendar events for today." If it returns events, the MCP is working. The speaker-mapping skill will use `list_events` to fetch attendees for the meeting window matching your recording timestamp.

**Package:** [`@cocal/google-calendar-mcp`](https://github.com/nspady/google-calendar-mcp) (1K+ stars, actively maintained)

## Claude Code Skills

Ensure these skills exist in `.claude/skills/`:

- **speaker-mapping** — Maps SPEAKER_XX to real names (uses Calendar MCP for attendee lookup)
- **discovery-synthesis** — Transforms named transcript → structured research notes
- **general-synthesis** — Transforms named transcript → lightweight meeting notes (decisions, action items, open questions)

---

# 2. Per-Meeting Workflow

## Step 1: Record

**Hotkey (recommended):** `Ctrl+Shift+R` from anywhere in Claude Code. Opens dedicated task terminal, captures system audio via pysysaudio, starts recording. Works with any meeting app (Meet, Teams, Zoom).

**CLI (alternative):**

```bash
# Any meeting app (system audio + mic):
record-meeting --mic --diarize

# Zoom-only audio isolation (optional — captures Zoom audio only, not other apps):
record-meeting --device "ZoomAudioDevice" --mic --diarize
```

- **All meeting apps (Meet, Teams, Zoom):** System audio captured natively via Core Audio tap. No device routing needed.
- **Both sides:** `--mic` captures system audio + your microphone
- **Stop:** `Ctrl+Shift+S` from anywhere in Claude Code (recommended), or `Ctrl+C` in task terminal. Auto-stops after 10 min silence (configurable via `--silence-timeout`).
- **Script location:** `.claude/skills/meeting-transcription/scripts/record_meeting.py`
- **Venv:** `~/.local/share/meeting-transcription/venv`

**Output:** `Meeting Transcripts/JSON Files/YYYY-MM-DD_HHMMSS/` (JSON); WAV staged in `~/meetings/` (deleted)

| File | Description |
|------|-------------|
| `recording.json` | Diarized transcript (SPEAKER_00, SPEAKER_01, …) |
| `recording.wav` | Raw audio (deleted unless `--keep-audio`) |

## Step 2: Speaker Mapping

1. Invoke the **speaker-mapping** skill
2. **Step 0 (timezone):** Agent calls Google Calendar MCP `get-current-time` first — never assumes a timezone when interpreting timestamps
3. **Input:** User can say "my meeting just ended" (agent auto-detects unprocessed folders: those with `recording.json` but no `mapping.json`. If exactly 1 → auto-selects it; if >1 → lists them for user to pick; if 0 → reports all processed, offers re-process) — or provide explicit path and recording time. Agent uses Calendar MCP `list_events` to auto-fetch attendees. Optionally identify yourself ("SPEAKER_02 is me")
4. Agent runs 3-pass mapping (anchor → profile → elimination)
5. Confirm or correct the proposed mapping (table includes `mentioned_not_speaking` — names referenced in transcript but not mapped to any speaker, e.g., "Spence said he'd be late" when Spence didn't speak)
6. Agent writes: named transcript (`*_named.txt`) + `mapping.json` (includes `mentioned_not_speaking` array) — both to the same JSON Files subdirectory as the input
7. **Step 8 (mandatory):** Update `.claude/skills/meeting-transcription/profiles/speaker-profiles.json`. Workflow does not end at output generation. Profile updates: merge by email first (then nickname matching), append-only with dedup, string-merge for `meeting_behavior`, cap `topics` at 15 and `verbal_patterns` at 10

> **No Calendar MCP?** You can provide attendees manually instead — "Attendees: [Pharmacy Eng director], [Director of Pharmacy & Fulfillment Product], Danny Pedrini"

## Step 3: Synthesize

Choose a synthesis mode based on the meeting type:

| Mode | When to Use | Agent |
|------|-------------|-------|
| **3a. Discovery** (default) | Discovery sessions, research interviews, deep-dive meetings | `discovery-synthesis` skill |
| **3b. General** | Standups, 1:1s, planning, reviews | `general-synthesis` skill (lightweight summary + actions + decisions) |
| **3c. Skip** | When the named transcript is sufficient | None — stop at Step 2 |

### 3a. Discovery Synthesis (Default)

1. Invoke the **discovery-synthesis** skill on the named transcript
2. Answer intake: initiative, decision context, participants (and optional hypotheses/audience)
3. Agent produces structured research document with findings, workflows, quote index
4. Save to user-directed path — synthesis agents ask where to save (e.g., `Initiatives/[Name]/Discovery Notes/`); not in `Meeting Transcripts/`

### 3b. General Synthesis

1. Invoke the general synthesis skill on the named transcript
2. Agent produces a lightweight document: executive summary, action items with owners, decisions made, open questions
3. Suitable for recurring meetings where the full discovery format is overkill

### 3c. Skip

Stop at the named transcript from Step 2. Useful for standups or meetings where the transcript itself is the deliverable.

## Step 4: Cleanup

- **Automatic:** Script deletes WAV from `~/meetings/` when `--keep-audio` is not used
- **Preserved:** `recording.json`, named transcript, synthesis document, `mapping.json`
- **Output locations:** `~/meetings/` is WAV staging only (ephemeral). All persistent files — JSON, named transcript, synthesis — live in `Meeting Transcripts/` (or user-directed path for synthesis)

---

# 3. Speaker Mapping Reference

## 3-Pass Logic

| Pass | Purpose |
|------|---------|
| **Anchor** | Find explicit name mentions ("Thanks [teammate]", "As [Director of Pharmacy & Fulfillment Product] said") → high-confidence bindings |
| **Profile** | Match topics, verbal patterns, meeting behavior from `.claude/skills/meeting-transcription/profiles/speaker-profiles.json` to remaining speakers |
| **Elimination** | When N speakers and N attendees remain, assign by process of elimination (confidence 0.5) |

Details are in the `speaker-mapping` skill.

## Speaker Profile Schema

```json
{
  "slug": {
    "name": "Full Name",
    "email": "email@domain.com",
    "role": "Title",
    "team": "Team Name",
    "topics": ["topic1", "topic2"],
    "verbal_patterns": ["pattern1", "pattern2"],
    "meeting_behavior": "When/how they speak"
  }
}
```

Profile updates cap `topics` at 15 and `verbal_patterns` at 10.

## Google Calendar Integration

The speaker-mapping skill uses the Google Calendar MCP (`@cocal/google-calendar-mcp`) to fetch attendees automatically. Setup is in [Section 1: Google Calendar MCP](#google-calendar-mcp-optional--attendee-lookup).

**How it works:** Agent calls `list_events` with a time window around the recording timestamp → extracts attendee names/emails → matches against speaker profiles → proceeds with 3-pass mapping.

**Fallback:** Manual attendee input or Python implementation for batch pipelines outside Claude Code — see [Appendix C](#appendix-c-batch-pipeline-utilities).

## Post-Meeting Confirmation

Conversational: tell the agent "SPEAKER_02 is actually [Director of Pharmacy & Fulfillment Product]" and it updates the mapping inline. No terminal prompt loop.

---

# 4. Speaker Identification Accuracy

## What to Expect

Local diarization uses **pyannote Community-1** (pyannote.audio 4.x, bundled via WhisperX). Community-1 has ~14–20% DER on meeting benchmarks vs. ~3.1% for commercial APIs like AssemblyAI. This is a ~1.5–4 pt improvement over the older pyannote 3.1 model. The 3-pass speaker mapping layer compensates further, but accuracy varies by meeting size.

**Baseline (current pipeline — Community-1, no additional optimizations):**

| Meeting Type | Speakers | Diarization DER | Mapping Accuracy | End-to-End |
|---|---|---|---|---|
| 1:1 | 2 | ~7–11% | 95%+ | 90–95% |
| 3-person | 3 | ~9–14% | 80–90% | 74–86% |
| 5-person | 5 | ~11–17% | 65–80% | 57–72% |
| 8+ person | 8+ | ~14–20% | 50–70% | 42–62% |

**With all optimizations applied (Community-1 + min/max_speakers + DiarizationLM + self-voice + priors + feedback):**

| Meeting Type | End-to-End (Optimized) |
|---|---|
| 1:1 | ~97% |
| 3-person | ~91% |
| 5-person | ~83% |
| 8+ person | ~76% |

## Improvement Roadmap

### Phase 1 — Quick Wins (1–2 weeks)

| Improvement | Accuracy Lift | Effort | How |
|---|---|---|---|
| **Self-voice enrollment** | +3–8% | Low | Record 30s sample; always identify yourself. See [Appendix C: Self-Voice Identification](#self-voice-identification-optional). |
| **Meeting-type priors** | +2–5% | Low | Add `meeting_type` to speaker-mapping agent prompt (standup / 1:1 / planning / review / discovery). |
| **Profile feedback loop** | Compounds | Low | On correction, agent updates `.claude/skills/meeting-transcription/profiles/speaker-profiles.json` with richer evidence for future mappings. |

### Phase 2 — Diarization Quality (2–4 weeks)

| Improvement | Accuracy Lift | Effort | How |
|---|---|---|---|
| **pyannote min/max_speakers** | +5–12% | Low–Med | Pass attendee count from Calendar into pyannote. Use `--min-speakers` / `--max-speakers` CLI flags. |
| **DiarizationLM post-processing** | +10–25% DER | Medium | Google Research (2024). LLM fixes speaker turn errors using transcript context. `pip install diarizationlm`. Can use Claude Code's LLM. |
| **pyannote tuning** | Variable | Medium | Tune `segmentation.threshold`, `clustering.threshold`, `min_duration_off` for meeting audio. |

### Phase 3 — Advanced (4–8 weeks)

| Improvement | Accuracy Lift | Effort | How |
|---|---|---|---|
| **Cross-meeting lazy enrollment** | +5–15% | High | Save confirmed speaker embeddings; match recurring attendees via cosine similarity. |
| **Temporal signal fusion** | +3–5% | Medium | Correlate join/leave times with speaker start/stop in diarization. Requires Meet/Zoom API. |
| **speech-swift evaluation** | TBD | Medium | Native Swift/MLX diarization with `--target-speaker`. Limited to ≤3 concurrent speakers. |

> **Accuracy ceiling (fully local, Community-1):** ~83% for 5-person meetings, ~76% for 8+. To exceed this, you would need commercial diarization APIs (violates no-API-fees constraint), biometric enrollment for others (privacy concern), or platform-native speaker attribution (e.g., Google Meet Transcript API).

Full research and implementation details: `reference/Speaker-Identification-Accuracy-Improvements-2026.md`

---

# 5. Configuration Reference

## record_meeting.py CLI Arguments

No config file. All options via CLI flags.

**Precedence:** CLI flags > environment variables (`HF_TOKEN`) > script defaults.

| Group | Flag | Default | Description |
|------|------|---------|-------------|
| Recording | `--mic` | off | Include microphone input (both sides) |
| | `--device` | None (native system audio tap) | Legacy: capture from a named audio device via sounddevice |
| | `--mic-device` | system default | Microphone when using `--mic` |
| | `--silence-timeout` | 600 | Auto-stop after N seconds of silence |
| Transcription | `--model` | `large-v3-turbo` | Whisper model |
| | `--language` | `en` | Language code |
| | `--initial-prompt` | domain terms preset | Domain vocabulary prompt for Whisper |
| | `--no-condition-previous` | off | Disable conditioning on previous text |
| Diarization | `--diarize` | on | Enable speaker diarization |
| | `--no-diarize` | — | Disable diarization |
| | `--min-speakers` | — | Minimum expected speakers |
| | `--max-speakers` | — | Maximum expected speakers |
| | `--hf-token` | `$HF_TOKEN` | HuggingFace token |
| Output | `--output-dir` | JSON: `Meeting Transcripts/JSON Files/YYYY-MM-DD_HHMMSS`; WAV: `~/meetings/YYYY-MM-DD_HHMMSS` | JSON (persistent) and WAV (staging) directories |
| | `--keep-audio` | off | Keep WAV file after transcription |
| Transcription-only | `--file` | — | Transcribe existing audio file instead of recording |

**Domain vocabulary:** The script uses a default `--initial-prompt` with fulfillment/ pharmacy terms (PV2, beyondRx, HighJump, etc.). Override via `--initial-prompt "your terms"` or pass empty string to disable.

## Command Equivalents

| Task | Command |
|------|---------|
| Start recording (any meeting app) | `Ctrl+Shift+R` (Claude Code keybinding) |
| Stop recording | `Ctrl+Shift+S` (Claude Code keybinding) or `Ctrl+C` |
| Record with mic + diarize (CLI) | `record-meeting --mic --diarize` |
| Record Zoom-only audio (CLI) | `record-meeting --device "ZoomAudioDevice" --mic --diarize` |
| Record system audio only | `record-meeting --diarize` (omit `--mic`) |
| Transcribe existing file | `record-meeting --file /path/to/audio.wav --diarize` |
| List audio devices | `python -c "import sounddevice; print(sounddevice.query_devices())"` |
| Pre-warm models | `setup.sh` (or see [Pre-warm Models](#pre-warm-models)) |

---

# Appendix A: Alternative mlx-whisper

When transcription speed matters, **mlx-whisper** is 4–7x faster on Apple Silicon than faster-whisper. The default pipeline uses faster-whisper for integrated capture + transcription + diarization. mlx-whisper requires a separate manual flow: capture audio → transcribe with mlx-whisper → diarize separately.

## When to Use mlx-whisper vs. Default Pipeline

| Scenario | Use Default Pipeline | Use mlx-whisper |
|---|---|---|
| Typical meeting, convenience matters | **Yes** — single command | No |
| Transcription speed critical (long meetings, batch) | No | **Yes** — 4–7x faster |
| Domain terms need `initial_prompt` | Yes — built-in | Yes |
| Single-command capture + transcribe + diarize | **Yes** | No (multi-step) |

## Audio Capture

- **pysysaudio** (default): Native system audio capture via Core Audio taps. No virtual audio device needed.
- **Legacy:** Pass `--device "DeviceName"` to use sounddevice with a specific device (e.g., `--device "BlackHole 2ch"` if BlackHole is installed)
- **OBS Studio:** `brew install --cask obs` — macOS Audio Capture + Audio Input Capture

## Recording

```bash
# pysysaudio captures system audio natively; no sox/BlackHole needed for the insourced pipeline
# For manual recording with sox (if needed):
sox -t coreaudio default output.wav
```

## Transcription (mlx-whisper)

```bash
mlx_whisper meeting.wav --model mlx-community/whisper-large-v3-turbo --language en \
  --initial-prompt "PV2, beyondRx, HighJump, Tompkins, DEA, USP 797, HIPAA, SLA, wave planning, pick and pack, putwall, conveyance, compounding, Rx, non-Rx." \
  --condition-on-previous-text False --output-format json --output-dir ./output
```

## Diarization (WhisperX)

```bash
whisperx meeting.wav --model large-v3-turbo --diarize --hf_token $HF_TOKEN \
  --device mps --compute_type int8 --output_format all
```

> Use `--device mps` on Apple Silicon for ~10x faster diarization.

## Links

- [mlx-whisper](https://github.com/ml-explore/mlx-whisper) — Native Apple Silicon transcription
- [WhisperX](https://github.com/m-bain/whisperX) — Transcription + word-level diarization
- [DiarizationLM](https://github.com/google/speaker-id/tree/master/DiarizationLM) — LLM-based speaker turn correction

---

# Appendix B: Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Screen & System Audio Recording permission not granted" | macOS permission not enabled | System Settings → Privacy & Security → Screen & System Audio Recording → enable for Python/Claude Code/Terminal |
| No audio captured | Permission not granted, or no audio playing | Verify permission; check that a meeting app is producing audio |
| One side only (remote audio, no mic) | Mic not included | Use `--mic` |
| One side only (mic captured, no remote audio) | System audio capture issue | Verify macOS permission is granted. Try `pip install --upgrade pysysaudio`. If persistent, use `--device` fallback with BlackHole. |
| pysysaudio returns zero/empty audio | Core Audio tap issue on some macOS versions | Update pysysaudio; if persistent, use `--device "BlackHole 2ch"` fallback (requires installing BlackHole) |
| Echo/feedback | Speaker into mic | Use headphones |
| Diarization not working | Missing token or licenses | Set `HF_TOKEN`; accept pyannote model licenses at HuggingFace |
| Speaker IDs not stable across meetings | Expected behavior | Use speaker mapping agent every meeting |
| Repetition loop ("Yes. Yes. Yes.") | Model conditioned on previous text | Use `--no-condition-previous` |
| Silence hallucination | Phantom text during silence | Increase `--silence-timeout`; consider post-processing or WhisperX `--hallucination_silence_threshold` |
| Memory pressure | large-v3-turbo + diarization | 16 GB RAM comfortable; use `--model medium` for lower memory |

---

# Appendix C: Batch Pipeline Utilities

**Use when:** Automating the pipeline outside Claude Code (CI, cron, scripted batch runs).

## Google Calendar — Fetch Attendees

Setup: Google Cloud Console → Enable Calendar API → OAuth client (Desktop) → `credentials.json` → `pip install google-api-python-client google-auth-oauthlib google-auth-httplib2`

```python
import os
from datetime import datetime, timedelta
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_PATH = Path.home() / ".config" / "speaker-mapping" / "credentials.json"
TOKEN_PATH = Path.home() / ".config" / "speaker-mapping" / "token.json"

def get_calendar_service():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def fetch_attendees_for_meeting(meeting_time: datetime, time_window_minutes: int = 60) -> list[dict]:
    service = get_calendar_service()
    time_min = (meeting_time - timedelta(minutes=30)).isoformat() + "Z"
    time_max = (meeting_time + timedelta(minutes=time_window_minutes)).isoformat() + "Z"
    events = service.events().list(
        calendarId="primary", timeMin=time_min, timeMax=time_max,
        singleEvents=True, orderBy="startTime",
    ).execute().get("items", [])

    if not events:
        return []

    best_event = max(events, key=lambda e: _overlap(e, meeting_time), default=None)
    if not best_event:
        return []

    return [
        {"name": a.get("displayName") or a["email"].split("@")[0], "email": a["email"]}
        for a in best_event.get("attendees", [])
        if not a.get("self") and "resource.calendar.google.com" not in a.get("email", "")
    ]

def _overlap(event: dict, meeting_time: datetime) -> float:
    start = event.get("start", {}).get("dateTime", "")
    end = event.get("end", {}).get("dateTime", "")
    if not start or not end:
        return 0
    start_ts = datetime.fromisoformat(start.replace("Z", "+00:00")).timestamp()
    end_ts = datetime.fromisoformat(end.replace("Z", "+00:00")).timestamp()
    mt = meeting_time.timestamp()
    return min(end_ts, mt + 3600) - max(start_ts, mt - 1800)
```

## Speaker Profile Load and Query

```python
import json
import os
from pathlib import Path

# Run from workspace root; or set WORKSPACE_ROOT env var
WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", str(Path.cwd())))
PROFILES_PATH = WORKSPACE_ROOT / ".claude" / "skills" / "meeting-transcription" / "profiles" / "speaker-profiles.json"

def load_speaker_profiles() -> dict:
    if not PROFILES_PATH.exists():
        return {}
    with open(PROFILES_PATH) as f:
        return json.load(f)

def get_profiles_for_attendees(attendees: list[dict], profiles: dict) -> dict:
    result = {}
    for att in attendees:
        slug = att["name"].lower().replace(" ", "_").replace("-", "_")
        email = att.get("email", "")
        for s, p in profiles.items():
            if s == slug or p.get("email", "").lower() == email.lower():
                result[s] = p
                break
    return result
```

## Self-Voice Identification (Optional)

Record 30-second sample:

```bash
sox -d -r 16000 -c 1 -b 16 ~/.config/speaker-mapping/voice_sample.wav trim 0 30
```

Compare to diarization segments (requires `pip install pyannote.audio numpy scipy`). Load segments from `Meeting Transcripts/JSON Files/YYYY-MM-DD_HHMMSS/recording.json` and pass to your identification logic:

```python
import os
import numpy as np

def identify_self_voice(voice_sample_path, meeting_audio_path, segments):
    from pyannote.audio import Model, Inference
    from pyannote.core import Segment
    from scipy.spatial.distance import cdist
    from collections import defaultdict

    token = os.environ.get("HF_TOKEN")
    model = Model.from_pretrained("pyannote/embedding", use_auth_token=token)
    inference = Inference(model, window="whole")

    user_emb = inference(voice_sample_path)

    speaker_segs = defaultdict(list)
    for seg in segments:
        sid = seg.get("speaker", "")
        if sid.startswith("SPEAKER_"):
            speaker_segs[sid].append((seg["start"], seg["end"]))

    best_speaker, best_dist = None, float("inf")
    for sid, segs in speaker_segs.items():
        embs = [inference.crop(meeting_audio_path, Segment(s, e))
                for s, e in segs[:5] if e - s >= 0.5]
        if not embs:
            continue
        avg = np.mean(embs, axis=0).reshape(1, -1)
        dist = cdist(user_emb.reshape(1, -1), avg, metric="cosine")[0, 0]
        if dist < best_dist:
            best_dist, best_speaker = dist, sid

    return best_speaker if best_speaker and best_dist < 0.5 else None
```

---

*Implementation spec compiled March 2026. Insourced pipeline (record_meeting.py + pysysaudio + WhisperX + pyannote). Verify tool versions with `--help` before first use.*
