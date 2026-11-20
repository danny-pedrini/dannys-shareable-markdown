# Meeting Transcription Pipeline — Architecture Diagram

**Date:** March 12, 2026 | **Source:** `Meeting-Transcription-Pipeline-Implementation-Spec.md`

---

## End-to-End Pipeline

```
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │                         MEETING (Zoom / Meet / Teams)                        │
 └────────────────────────────────┬─────────────────────────────────────────────┘
                                  │
                                  ▼
 ╔════════════════════════════════════════════════════════════════════════════════╗
 ║  STEP 1: RECORD  (record_meeting.py)                                        ║
 ║                                                                              ║
 ║  ┌───────────────────────────┐                                               ║
 ║  │ pysysaudio                │                                               ║
 ║  │ (Core Audio tap —         │                                               ║
 ║  │  native system audio)     │                                               ║
 ║  └─────────┬─────────────────┘                                               ║
 ║            │                                                                 ║
 ║            ▼                                                                 ║
 ║  ┌───────────────────────────┐                                               ║
 ║  │ WhisperX / faster-whisper │                                               ║
 ║  │ (CTranslate2)            │                                               ║
 ║  │ Model: large-v3-turbo    │                                               ║
 ║  │ • initial_prompt (domain  │                                               ║
 ║  │   vocabulary: PV2,       │                                               ║
 ║  │   beyondRx)              │                                               ║
 ║  │ • condition_on_previous_ │                                               ║
 ║  │   text control           │                                               ║
 ║  └─────────┬─────────────────┘                                               ║
 ║            │                                                                 ║
 ║            ▼                                                                 ║
 ║  ┌───────────────────────────┐                                               ║
 ║  │ pyannote Community-1      │──► HuggingFace (HF_TOKEN)                    ║
 ║  │ (pyannote.audio 4.x)     │                                               ║
 ║  │ Speaker diarization      │                                               ║
 ║  └─────────┬─────────────────┘                                               ║
 ║            │                                                                 ║
 ╚════════════╪═════════════════════════════════════════════════════════════════════╝
                 │
                 ▼
      ┌──────────────────────────────────────────────────────────┐
      │ recording.json → Meeting Transcripts/JSON Files/          │
      │   YYYY-MM-DD_HHMMSS/  (SPEAKER_00, SPEAKER_01, …)         │
      │                                                            │
      │ recording.wav → ~/meetings/YYYY-MM-DD_HHMMSS/              │
      │   (staging; deleted unless --keep-audio)                   │
      └────────────────────────┬──────────────────────────────────┘
                   │
                   ▼
 ╔════════════════════════════════════════════════════════════════════════════════╗
 ║  STEP 2: SPEAKER MAPPING       (speaker-mapping skill)                        ║
 ║                                                                              ║
 ║  STEP 0 (first): Get Timezone via Calendar MCP (get-current-time)            ║
 ║  • Required before any lookup — never assume timezone (e.g., Arizona)         ║
 ║  • Agent auto-detects most recent Meeting Transcripts/JSON Files/ recording   ║
 ║    ended") — user need not provide path                                       ║
 ║                                                                              ║
 ║  ┌────────────────┐   ┌──────────────────┐   ┌────────────────────────────┐  ║
 ║  │ Google Calendar │   │  Speaker Profiles │   │  User Hints               │  ║
 ║  │ MCP             │   │  (.claude/skills/  │   │  "SPEAKER_02 is me"       │  ║
 ║  │ (list_events)   │   │   meeting-transcription/│   │  "Attendees: [teammate], [Director of Pharmacy & Fulfillment Product]"   │  ║
 ║  │                 │   │   profiles/speaker-│   │                           │  ║
 ║  │ Auto-fetch      │   │   profiles.json)   │   │                           │  ║
 ║  │ attendees by    │   │                    │   │                           │  ║
 ║  │ recording time  │   │  name, email,      │   │                           │  ║
 ║  └───────┬─────────┘   │  role, topics,     │   └─────────────┬─────────────┘  ║
 ║          │             │  verbal_patterns,  │                 │              ║
 ║          │             │  meeting_behavior  │                 │              ║
 ║          │             └────────┬───────────┘                 │              ║
 ║          │                      │                             │              ║
 ║          └──────────┬───────────┴─────────────────────────────┘              ║
 ║                     │                                                        ║
 ║                     ▼                                                        ║
 ║          ┌─────────────────────────────────────────────────┐                 ║
 ║          │            3-PASS MAPPING ENGINE                 │                 ║
 ║          │                                                  │                 ║
 ║          │  Pass 1: ANCHOR                                  │                 ║
 ║          │    "Thanks [teammate]" → SPEAKER_01 = [Pharmacy Eng director]    │                 ║
 ║          │    Explicit name mentions → high confidence      │                 ║
 ║          │                     │                            │                 ║
 ║          │                     ▼                            │                 ║
 ║          │  Pass 2: PROFILE                                 │                 ║
 ║          │    Match topics, verbal patterns, behavior       │                 ║
 ║          │    from speaker-profiles.json                    │                 ║
 ║          │                     │                            │                 ║
 ║          │                     ▼                            │                 ║
 ║          │  Pass 3: ELIMINATION                             │                 ║
 ║          │    N speakers, N attendees → assign remaining     │                 ║
 ║          │    confidence: 0.5                               │                 ║
 ║          └──────────────────────┬───────────────────────────┘                 ║
 ║                                 │                                            ║
 ║                                 ▼                                            ║
 ║                     ┌───────────────────────┐                                ║
  ║                     │ User Confirmation      │                                ║
 ║                     │ (correct/accept)       │                                ║
 ║                     └───────────┬────────────┘                                ║
 ║                                 │                                            ║
 ║                     ┌───────────▼────────────┐                                ║
 ║                     │ Step 8: UPDATE         │  (MANDATORY — workflow          ║
 ║                     │ speaker profiles      │   does not end until done)      ║
 ║                     └───────────┬────────────┘                                ║
 ║                                 │                                            ║
 ╚═════════════════════════════════╪════════════════════════════════════════════════╝
                                   │
                                   ▼
      ┌────────────────────────────────────────────────────────────┐
      │ Meeting Transcripts/JSON Files/YYYY-MM-DD_HHMMSS/           │
      │   ├── recording.json                                        │
      │   ├── recording_named.txt  ◄── Named transcript              │
      │   └── mapping.json         ◄── Speaker-to-name map + conf.  │
      │       + mentioned_not_speaking                               │
      └───────────────────────┬────────────────────────────────────┘
                          │
                          ▼
 ╔════════════════════════════════════════════════════════════════════════════════╗
 ║  STEP 3: SYNTHESIZE        (choose one mode per meeting)                     ║
 ║                                                                              ║
 ║  ┌──────────────────────┐ ┌─────────────────────┐ ┌──────────────────────┐   ║
 ║  │ 3a. DISCOVERY        │ │ 3b. GENERAL         │ │ 3c. SKIP             │   ║
 ║  │ (default)            │ │                     │ │                      │   ║
 ║  │                      │ │ Standups, 1:1s,     │ │ Named transcript     │   ║
 ║  │ discovery-synthesis  │ │ planning, reviews   │ │ is the deliverable   │   ║
 ║  │ skill                │ │                     │ │                      │   ║
 ║  │                      │ │ Output:             │ │ No synthesis step    │   ║
 ║  │ Output:              │ │ • Exec summary      │ │                      │   ║
 ║  │ • Structured research│ │ • Action items      │ │                      │   ║
 ║  │   document           │ │ • Decisions         │ │                      │   ║
 ║  │ • Findings           │ │ • Open questions   │ │                      │   ║
 ║  │ • Workflows          │ │                     │ │                      │   ║
 ║  │ • Quote index        │ │                     │ │                      │   ║
 ║  └──────────┬───────────┘ └──────────┬──────────┘ └──────────┬───────────┘   ║
 ║             │                        │                       │               ║
 ╚═════════════╪════════════════════════╪═══════════════════════╪═══════════════════╝
               │                        │                       │
               ▼                        ▼                       ▼
 ╔════════════════════════════════════════════════════════════════════════════════╗
 ║  STEP 4: CLEANUP                                                             ║
 ║                                                                              ║
 ║  Auto-deleted:  recording.wav (unless --keep-audio)                          ║
 ║                                                                              ║
 ║  Preserved:     recording.json        (raw diarized transcript)              ║
 ║                 recording_named.txt   (named transcript)                      ║
 ║                 mapping.json          (speaker mapping + confidence +         ║
 ║                                        mentioned_not_speaking)                 ║
 ║                 synthesis document    (if 3a or 3b was run — user-directed)   ║
 ║  Locations:     All in Meeting Transcripts/JSON Files/; synthesis wherever   ║
 ║                 user directs                                                  ║
 ╚════════════════════════════════════════════════════════════════════════════════╝
```

---

## External Dependencies

```
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                          PIPELINE CORE                                  │
 │                                                                         │
 │   record_meeting.py ─────┬──────────────────────────────────────────┐   │
 │                          │                                          │   │
 │                          ▼                                          │   │
 │               ┌──────────────────┐    ┌─────────────────────┐       │   │
 │               │ WhisperX 3.8+    │    │ pyannote.audio 4.x  │       │   │
 │               │ faster-whisper   │    │ Community-1 model    │       │   │
 │               │ (CTranslate2)    │    │                     │       │   │
 │               └────────┬─────────┘    └──────────┬──────────┘       │   │
 │                        │                         │                  │   │
 └────────────────────────┼─────────────────────────┼──────────────────┘   │
                          │                         │                      │
           ┌──────────────┴──────────┐    ┌─────────┴──────────┐           │
           ▼                         ▼    ▼                    ▼           │
 ┌──────────────────┐  ┌─────────────────────┐  ┌──────────────────────┐   │
 │ HuggingFace Hub  │  │ Audio Capture        │  │ Google Calendar MCP  │   │
 │                  │  │                      │  │ (@cocal/google-      │   │
 │ • Model weights  │  │ • pysysaudio         │  │  calendar-mcp)       │   │
 │   (large-v3-     │  │   (Core Audio tap —  │  │                      │   │
 │    turbo)        │  │    native macOS      │  │ • Attendee lookup    │   │
 │ • pyannote       │  │    system audio)     │  │ • Time-window match  │   │
 │   diarization    │  │                      │  │                      │   │
 │ • MPS (GPU accel │  │ • sounddevice        │  │ Optional (manual     │   │
 │   for diarize)   │  │   (mic input; legacy │  │ fallback available)  │   │
 │ • HF_TOKEN auth  │  │    --device fallback)│  │                      │   │
 │                  │  │                      │  │                      │   │
 └──────────────────┘  └──────────────────────┘  └──────────────────────┘
           │
           ▼
 ┌─────────────────────────────────────────┐
 │ Python venv                             │
 │ ~/.local/share/meeting-transcription/   │
 │ venv                                    │
 └─────────────────────────────────────────┘
```

---

## Claude Code Skill Orchestration

```
 ┌──────────────────────────────────────────────────────────────────────┐
 │                         CLAUDE CODE                                  │
 │                                                                      │
 │  ┌────────────────────────────────────────────────────────────────┐  │
 │  │  .claude/skills/                                               │  │
 │  │                                                                │  │
 │  │  ┌───────────────────────┐ ┌────────────────────────┐ ┌────────────────────┐ │  │
 │  │  │ speaker-mapping       │ │ discovery-synthesis    │ │ general-synthesis   │ │  │
 │  │  │ (skill)               │ │ (skill)                │ │ (skill)             │ │  │
 │  │  │                       │ │                        │ │                     │ │  │
 │  │  │ • 3-pass mapping      │ │ • Structured research  │ │ • Exec summary      │ │  │
 │  │  │ • Calendar MCP lookup │ │ • Findings + workflows │ │ • Action items      │ │  │
 │  │  │ • Profile matching    │ │ • Quote index          │ │ • Decisions         │ │  │
 │  │  │ • Domain term fixes   │ │ • Decision context     │ │ • Open questions    │ │  │
 │  │  └──────────┬────────────┘ └──────────┬─────────────┘ └─────────┬───────────┘ │  │
 │  │             │                         │                         │             │  │
 │  └─────────────┼─────────────────────────┼─────────────────────────┼─────────────┘  │
 │                │                         │                         │                │
 │                ▼                         ▼                         ▼                │
 │  ┌────────────────────────────────────────────────────────────────┐  │
 │  │  .claude/skills/meeting-transcription/                         │  │
 │  │                                                                │  │
 │  │  SKILL.md ──► Orchestrates full workflow (Steps 1-4)           │  │
 │  │  setup.sh ──► One-time environment setup                       │  │
 │  │  scripts/ ──► record_meeting.py + requirements.txt            │  │
 │  │  reference/ ──► Implementation spec, domain vocab, accuracy   │  │
 │  └────────────────────────────────────────────────────────────────┘  │
 │                                                                      │
 │  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Claude Code Keybindings (~/.claude/keybindings.json)         │  │
│  │                                                                │  │
│  │  Ctrl+Shift+R ──► "Record Meeting"                            │  │
│  │                   record_meeting.py --mic --diarize            │  │
│  │                   pysysaudio (system audio) + sounddevice (mic)│  │
│  │                   Writes PID to ~/.meeting-recording.pid       │  │
│  │                                                                │  │
│  │  Ctrl+Shift+S ──► "Stop Meeting Recording"                   │  │
│  │                   kill -INT via PID file → graceful stop       │  │
│  │                   PID file auto-removed on script exit         │  │
 │  └────────────────────────────────────────────────────────────────┘  │
 │                                                                      │
 │  ┌────────────────────────────────────────────────────────────────┐  │
 │  │  MCP Servers (configured in ~/.claude.json)                    │  │
 │  │                                                                │  │
 │  │  google-calendar ──► Attendee lookup (list_events)             │  │
 │  └────────────────────────────────────────────────────────────────┘  │
 │                                                                      │
 └──────────────────────────────────────────────────────────────────────┘
```

---

## Diarization Accuracy by Meeting Size

```
  End-to-End Accuracy
  100% ┬
       │
   95% ┤  ●─── 1:1 (optimized: ~97%)
       │  ○─── 1:1 (baseline: ~90-95%)
   90% ┤
       │       ●─── 3-person (optimized: ~91%)
   85% ┤
       │       ○─── 3-person (baseline: ~74-86%)
   80% ┤
       │             ●─── 5-person (optimized: ~83%)
   75% ┤
       │                   ●─── 8+ person (optimized: ~76%)
   70% ┤
       │             ○─── 5-person (baseline: ~57-72%)
   65% ┤
       │
   60% ┤
       │                   ○─── 8+ person (baseline: ~42-62%)
   55% ┤
       │
   50% ┤
       └──┬──────────┬──────────┬──────────┬──
          2          3          5          8+     Speakers

  ● = With all optimizations (Community-1 + min/max_speakers + DiarizationLM + self-voice + priors)
  ○ = Baseline (Community-1, no additional optimizations)
```

---

## File System Layout

```
 ~/
 ├── .meeting-recording.pid           ← PID file (exists only while recording is active;
 │                                       read by "Stop Meeting Recording" task to send SIGINT)
 ├── .config/
 │   └── speaker-mapping/
 │       ├── credentials.json         ← Google OAuth (batch pipeline only)
 │       ├── token.json               ← Cached OAuth token (batch pipeline only)
 │       └── voice_sample.wav         ← 30s self-voice enrollment (optional)
 │
 ├── meetings/                        ← WAV staging (deleted after processing unless
 │   └── YYYY-MM-DD_HHMMSS/            --keep-audio)
 │       └── recording.wav             ← Staging; deleted after processing
 │
 ├── .local/share/meeting-transcription/
 │   └── venv/                        ← Python venv for record_meeting.py
 │
 └── <workspace>/
     ├── Meeting Transcripts/         ← Transcript output root
     │   └── JSON Files/
     │       └── YYYY-MM-DD_HHMMSS/
     │           ├── recording.json       ← Diarized transcript (SPEAKER_XX segments)
     │           ├── recording_named.txt  ← Named transcript (post speaker-mapping)
     │           └── mapping.json         ← Speaker-to-name map + confidence +
     │                                        mentioned_not_speaking
     └── .claude/
         └── skills/
             ├── speaker-mapping/           ← speaker-mapping skill
             ├── discovery-synthesis/       ← discovery-synthesis skill
             ├── general-synthesis/         ← general-synthesis skill
             └── meeting-transcription/
                 ├── profiles/
                 │   └── speaker-profiles.json  ← Known speaker profiles (name, role, patterns)
                 ├── SKILL.md
                 ├── setup.sh
                 ├── scripts/
                 │   ├── record_meeting.py
                 │   └── requirements.txt
                 └── reference/
                     ├── Meeting-Transcription-Pipeline-Implementation-Spec.md
                     ├── architecture-diagram.md     ← This file
                     └── ...

 ~/.claude.json                       ← Claude Code MCP config (Google Calendar MCP server)
```

---

## Appendix: Future Enhancements (Not Yet Implemented)

### A. Screen Capture for Visual Context

**Status:** Deferred — evaluate if repeated loss of visual context becomes a problem.

**Problem:** Transcript captures "as you can see here, this metric is trending down" but loses what "here" refers to when someone is sharing a dashboard, Jira board, or diagram.

**Approach:** ScreenCaptureKit (already required if adopting audio-only SCK capture) can capture both audio and video. Instead of continuous video (1-2 GB/hr at 1080p), use **periodic screenshots + VLM analysis**:

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │  SCREEN CAPTURE (optional, alongside audio)                         │
 │                                                                     │
 │  ScreenCaptureKit (SCStreamConfiguration)                           │
 │  • capturesAudio = true  (same as audio-only mode)                  │
 │  • width = 1920, height = 1080                                      │
 │  • minimumFrameInterval = 1/2 FPS (one frame every 30s)             │
 │                                                                     │
 │  Every 30-60s:                                                      │
 │    CMSampleBuffer (.screen) → save PNG screenshot                   │
 │    Screenshots stored in Meeting Transcripts/JSON Files/            │
 │    YYYY-MM-DD_HHMMSS/screenshots/                                   │
 │                                                                     │
 │  During synthesis:                                                   │
 │    Screenshots → VLM (Claude vision / Gemini) → text annotations    │
 │    Appended to transcript as:                                        │
 │    [Screen context at 12:35: "Looker dashboard showing SLA %        │
 │     at 94.2%, trending down from 96.1% last month"]                  │
 │                                                                     │
 │  Storage: ~60-120 PNGs per 1-hour meeting (~50-150 MB)              │
 └─────────────────────────────────────────────────────────────────────┘
```

**Tradeoffs:**
- **Privacy/Compliance:** Screen captures may contain PHI, credentials, Slack DMs, personal tabs. `[Compliance Review Required]` before enabling at a healthcare company.
- **Storage:** ~50-150 MB/meeting in screenshots vs. ~0 today. Manageable but adds up.
- **Processing cost:** VLM calls per screenshot during synthesis. ~$0.01-0.05/image with Claude vision.
- **Signal-to-noise:** Most shared screens are slides or dashboards obtainable from the original artifact (the deck, the Looker link). Screenshots are a lossy copy.
- **Alternative:** Ask the presenter to share the artifact directly — 80% of the value at 0% of the complexity.

**Decision:** Type 2 (reversible). Low priority. Revisit if pattern emerges of lost visual context across multiple meetings.

---

## Appendix: Migration History

### B. BlackHole → pysysaudio (Native System Audio Capture) (Superseded)

> **Historical context only.** The BlackHole-based audio stack described below was replaced by native pysysaudio capture in March 2026. See the main architecture diagrams above for the current setup.

**Date:** March 12, 2026
**Type:** Type 2 (reversible) — rollback path preserved in code
**Status:** Active

#### What Changed

Replaced the BlackHole virtual audio driver stack with `pysysaudio`, a Python package that uses macOS native Core Audio process taps to capture system audio directly. Apple provides two APIs for this — ScreenCaptureKit (macOS 13+, screen + audio) and Core Audio process taps (macOS 14.2+, audio-only). `pysysaudio` uses Core Audio taps under the hood but shares the same "Screen & System Audio Recording" permission.

#### Why

The BlackHole stack required 5+ manual setup steps and was the #1 barrier to portability:

| Eliminated Component | What It Was | Pain Point |
|---------------------|-------------|------------|
| BlackHole 2ch (brew) | Virtual audio device | Required macOS reboot after install |
| SwitchAudioSource (brew) | Audio output switcher | Required per-recording audio routing |
| "Headphones + Capture" | Multi-Output Device | Manual Audio MIDI Setup creation |
| "Meeting Capture" | Aggregate Device | Manual Audio MIDI Setup creation |
| Headphone detection logic | JBL TUNE770NC grep | Hardcoded to specific headphones; broke on device change |

The new stack: `pip install pysysaudio` + grant one macOS permission. Works with any headphones, speakers, or meeting app with zero per-recording configuration.

#### Architecture Before and After

```
BEFORE (BlackHole):
  Meeting App → macOS Audio Output → Multi-Output Device → BlackHole 2ch
                                                         → Headphones
  BlackHole 2ch → sounddevice.InputStream → record_meeting.py

AFTER (pysysaudio):
  Meeting App → macOS Audio Output → Headphones / Speakers (unchanged)
                                   → Core Audio tap (pysysaudio) → record_meeting.py
```

#### Files Changed

| File | Nature of Change |
|------|-----------------|
| `scripts/record_meeting.py` | New `_record_system_tap()` (pysysaudio); preserved `_record_sounddevice()` as `--device` fallback; `--device` default changed from `"BlackHole 2ch"` to `None`; metadata field renamed `device` → `capture_method` |
| `scripts/requirements.txt` | Added `pysysaudio>=0.1.3` |
| `setup.sh` | Removed BlackHole/SwitchAudioSource install; removed Audio MIDI Setup instructions; added pysysaudio permission check |
| `.vscode/tasks.json` | Consolidated 2 recording tasks → 1 "Record Meeting" (no SwitchAudioSource) |
| `keybindings.json` | Removed `Ctrl+Shift+Z` (Zoom task); `Ctrl+Shift+R` → "Record Meeting" |
| `SKILL.md` | Simplified prerequisites (4 steps vs 5+MIDI); removed Audio Auto-Detection section |
| `reference/*` | Updated architecture diagram, setup inventory, task config, user journey, implementation spec |

#### Known Risks

| Risk | Severity | Observed? |
|------|----------|-----------|
| `pysysaudio` is Alpha (v0.1.3, ~760 downloads/mo as of Feb 2026) | Medium | Not yet |
| Core Audio tap returning zero-value audio on some macOS versions | Medium | Not yet |
| `pysysaudio.stream()` chunk sizes vary, complicating real-time mic mixing | Low | Not yet |
| macOS permission must be granted per-app (Python, Claude Code, Terminal) | Low | Expected — one-time |

#### Rollback Procedure

The `--device` flag preserves the full legacy sounddevice path in `record_meeting.py`. To revert:

1. **Install BlackHole:**
   ```bash
   brew install blackhole-2ch
   # Reboot macOS (required for BlackHole device to appear)
   ```

2. **Recreate Audio MIDI devices:**
   - "Headphones + Capture": Audio MIDI Setup → + → Multi-Output Device → enable headphones + BlackHole 2ch → Drift Correction on BlackHole only
   - "Meeting Capture": Audio MIDI Setup → + → Aggregate Device → enable Built-in Output + BlackHole 2ch + Built-in Microphone

3. **Install SwitchAudioSource:**
   ```bash
   brew install switchaudio-osx
   ```

4. **Update `.vscode/tasks.json`** — restore the SwitchAudioSource headphone detection command:
   ```json
   {
     "label": "Record Meeting (Meet/Teams)",
     "command": "bash -c 'if SwitchAudioSource -a -t output | grep -q \"JBL TUNE770NC\"; then SwitchAudioSource -s \"Headphones + Capture\" && DEV=\"BlackHole 2ch\"; else SwitchAudioSource -s \"Meeting Capture\" && DEV=\"Meeting Capture\"; fi && ~/.local/share/meeting-transcription/venv/bin/python \"...record_meeting.py\" --device \"$DEV\" --mic --diarize'"
   }
   ```

5. **Pass `--device` explicitly** on every recording:
   ```bash
   record-meeting --device "BlackHole 2ch" --mic --diarize
   ```

6. **Update keybindings** — re-add `Ctrl+Shift+Z` for Zoom task if needed.

No code changes required in `record_meeting.py` — the `_record_sounddevice()` path is still present and activates whenever `--device` is specified.
