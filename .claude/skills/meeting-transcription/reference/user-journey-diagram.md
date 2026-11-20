# Meeting Transcription Pipeline — User Journey

**Date:** March 12, 2026 | **Source:** `SKILL.md` + `Meeting-Transcription-Pipeline-Implementation-Spec.md`

---

## What This Is

This pipeline records your meeting audio locally on your Mac, transcribes it with
AI (WhisperX), identifies who said what (speaker diarization), maps anonymous speaker
labels to real names, and optionally synthesizes the transcript into structured notes.

Everything runs locally — no cloud transcription service. System audio is captured
natively via macOS Core Audio taps (pysysaudio) — no virtual audio device or audio
routing setup needed. Just grant the "Screen & System Audio Recording" permission
once and you're set.

**Prerequisites:** Complete the Quick Start in `SKILL.md` before your first meeting.
The setup script handles dependencies, audio devices, and Python environment.

```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                    MEETING TRANSCRIPTION — USER JOURNEY                             ║
║                                                                                    ║
║  5-6 user actions across 3 phases:                                                 ║
║                                                                                    ║
║  RECORD PHASE (Terminal)                                                           ║
║    ❶ Start Recording ── Ctrl+Shift+R / CLI / Task            (meeting starts)      ║
║    ❷ Stop Recording  ── Ctrl+Shift+S (or Ctrl+C in terminal)     (meeting ends)     ║
║                                                                                    ║
║  SPEAKER MAP PHASE (Claude Code Chat)                                                   ║
║    ❸ Initiate Mapping ── "my meeting just ended"             (switch to chat)      ║
║    ❹ Confirm Mapping  ── "looks good" or corrections         (agent prompts you)   ║
║                                                                                    ║
║  SYNTHESIZE PHASE (Claude Code Chat — optional)                                         ║
║    ❺ Choose Synthesis Mode ── discovery / general / skip     (agent prompts you)   ║
║    ❻ Specify Save Location ── file path                      (if ❺ ≠ skip)         ║
║                                                                                    ║
╚══════════════════════════════════════════════════════════════════════════════════════╝


══════════════════════════════════════════════════════════════════════════════════
 USER ACTION ❶ — START RECORDING
 Where: Claude Code (terminal)  |  When: Meeting is starting (you initiate)
══════════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────┐
  │  🖥  YOU: Start recording                                  │
  │                                                            │
 │  Trigger: Meeting is starting                              │
 │           Ctrl+Shift+R (any meeting app)                    │
  │                                                            │
  │  Prerequisite: Claude Code must be open and in focus with  │
  │  this workspace loaded. The hotkey is a Claude Code        │
  │  keybinding — it won't launch Claude Code or work from     │
  │  other apps.                                               │
  └──────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  SYSTEM: RECORD                                                        ║
 ║                                                                        ║
 ║  All meeting apps (Meet, Teams, Zoom):                                 ║
 ║  ┌──────────────────────────────────────────────────────────────────┐  ║
 ║  │  A. Ctrl+Shift+R → Runs "Record Meeting" task                   │  ║
 ║  │     (anywhere in Claude Code; auto-opens terminal)              │  ║
 ║  │  B. CLI: record-meeting --mic --diarize                         │  ║
 ║  └──────────────────────────────────────────────────────────────────┘  ║
 ║                                                                        ║
 ║  What happens (automatic — same for all meeting apps):                  ║
 ║  ┌──────────────────────────────────────────────────┐                  ║
 ║  │ record_meeting.py starts                         │                  ║
 ║  │ • pysysaudio captures system audio via Core      │                  ║
 ║  │   Audio tap (remote participants)                │                  ║
 ║  │ • sounddevice captures mic audio (you)           │                  ║
 ║  │ • Works with any headphones/speakers — no        │                  ║
 ║  │   audio routing or device switching needed       │                  ║
 ║  │ • Streams to WAV in ~/meetings/YYYY-MM-DD_HHMMSS │                  ║
 ║  └──────────────────────────────────────────────────┘                  ║
 ║                                                                        ║
 ║  WHAT YOU'LL SEE IN THE TERMINAL:                                       ║
 ║  ┌──────────────────────────────────────────────────────────────┐       ║
 ║  │ Recording (system audio tap)... (Ctrl+Shift+S or Ctrl+C     │       ║
 ║  │ to stop; silence auto-stop at 600s)                         │       ║
 ║  │   42s                                                       │       ║
 ║  └──────────────────────────────────────────────────────────────┘       ║
 ║  If you see the elapsed timer incrementing, audio capture is working.  ║
 ║  If no audio: check permissions (see Troubleshooting in SKILL.md).     ║
 ║                                                                        ║
 ║  ─ ─ ─ ─ ─ ─  MEETING HAPPENS  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─                  ║
 ║                                                                        ║
 ╚════════════════════════════════════════════════════════════════════════╝


══════════════════════════════════════════════════════════════════════════════════
 USER ACTION ❷ — STOP RECORDING
 Where: Claude Code (Ctrl+Shift+S)  |  When: Meeting ends (you initiate) or 10 min silence auto-stops
══════════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────┐
  │  🖥  YOU: Press Ctrl+Shift+S         │
  │                                     │
  │  Trigger: Meeting ends              │
  │           (or 10 min silence         │
  │            auto-stops it; Ctrl+C    │
  │            in terminal also works)   │
  └──────────────┬──────────────────────┘
                 │
                 ▼
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  SYSTEM: POST-RECORD PROCESSING (automatic — runs after stop signal)  ║
 ║                                                                        ║
 ║  This takes ~1-3 min per 30 min of audio on Apple Silicon.             ║
 ║  The terminal shows progress for each step. Just wait.                 ║
 ║                                                                        ║
 ║  ┌────────────────┐   ┌─────────────────┐   ┌───────────────────────┐  ║
 ║  │ WhisperX       │──►│ Word-level      │──►│ Speaker Diarization   │  ║
 ║  │ (speech → text)│   │ Alignment       │   │ (who said what —      │  ║
 ║  │                │   │ (timestamps)    │   │  labels: SPEAKER_00,  │  ║
 ║  │                │   │                 │   │  _01 ... names next)  │  ║
 ║  └────────────────┘   └─────────────────┘   └───────────┬───────────┘  ║
 ║                                                         │              ║
 ╚═════════════════════════════════════════════════════════╪══════════════╝
                                                           │
                                  ┌────────────────────────┘
                                  ▼
                     ┌─────────────────────────────────────────────┐
                     │  OUTPUT (on disk):                           │
                     │  Meeting Transcripts/JSON Files/             │
                     │    YYYY-MM-DD_HHMMSS/recording.json           │  ◄── unmapped / anonymous
                     │    (SPEAKER_00: ...)                          │      speakers
                     │                                               │
                     │  WAV staging in ~/meetings/ (auto-deleted)      │
                     └─────────────────────────────────────────────┘


══════════════════════════════════════════════════════════════════════════════════
 USER ACTION ❸ — INITIATE SPEAKER MAPPING
 Where: Claude Code chat  |  When: After recording completes (you initiate; switch from terminal)
══════════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────┐
  │  💬 YOU: Type in Claude Code chat                                       │
  │                                                                    │
  │  Trigger: "my meeting just ended" or "process my recording"        │
  │                                                                    │
  │  (Optionally: "SPEAKER_02 is me")                                  │
  └──────────────────────────────┬──────────────────────────────────────┘
                                 │
                                 ▼
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  SYSTEM: SPEAKER MAPPING      (speaker-mapping skill activates)       ║
 ║                                                                        ║
 ║  Agent does this automatically:                                        ║
 ║                                                                        ║
 ║  a. Selects recording                                                  ║
 ║     │  Processed = has mapping.json; unprocessed = recording.json only  ║
 ║     │  • 1 unprocessed → auto-selects                                  ║
 ║     │  • >1 unprocessed → lists folders, asks you to pick               ║
 ║     │  • 0 unprocessed → reports all done, offers re-process           ║
 ║     │  • Explicit path always overrides                                 ║
 ║     ▼                                                                  ║
 ║  b. Gets timezone via Google Calendar MCP                              ║
 ║     │  Calls get-current-time (never assumes timezone)                 ║
 ║     ▼                                                                  ║
 ║  c. Fetches attendees via Google Calendar MCP                          ║
 ║     │  Calls list_events for recording time window                     ║
 ║     │  (OR you provide names manually: "Attendees: [teammate], [Director of Pharmacy & Fulfillment Product]")         ║
 ║     ▼                                                                  ║
 ║  d. Loads speaker profiles                                             ║
 ║     │  .claude/skills/meeting-transcription/profiles/                  ║
 ║     │  speaker-profiles.json                                           ║
 ║     ▼                                                                  ║
 ║  e. Runs 3-pass mapping                                                ║
 ║     │  Pass 1 — ANCHOR:      "Thanks [teammate]" → SPEAKER_01 = [teammate]        ║
 ║     │  Pass 2 — PROFILE:     Match topics, verbal patterns             ║
 ║     │  Pass 3 — ELIMINATION: Remaining speakers ↔ remaining names      ║
 ║     ▼                                                                  ║
 ║  f. Presents mapping table for review                                  ║
 ║     ┌────────────────────────────────────────────────────────┐         ║
 ║     │  SPEAKER_00 → Danny Pedrini    (confidence: 0.9)      │         ║
 ║     │  SPEAKER_01 → [Pharmacy Eng director]     (confidence: 0.8)      │         ║
 ║     │  SPEAKER_02 → [Director of Pharmacy & Fulfillment Product]    (confidence: 0.7)      │         ║
 ║     │  mentioned_not_speaking: [teammate]                   │         ║
 ║     └────────────────────────────────────────────────────────┘         ║
 ║                                                                        ║
 ╚════════════════════════════════════════════════════════════════════════╝


══════════════════════════════════════════════════════════════════════════════════
 USER RESPONSE ❹ — CONFIRM OR CORRECT MAPPING
 Where: Claude Code chat  |  When: Agent presents mapping table (agent prompts you)
══════════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────┐
  │  💬 Agent prompts you: Respond to the mapping table                  │
  │                                                                    │
  │  Options:                                                          │
  │    • "Looks good" → agent proceeds                                 │
  │    • "SPEAKER_02 is actually [Director of Pharmacy & Fulfillment Product]" → agent corrects & proceeds      │
  └──────────────────────────────┬──────────────────────────────────────┘
                                 │
                                 ▼
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  SYSTEM: WRITE OUTPUT + UPDATE PROFILES (automatic after confirmation) ║
 ║                                                                        ║
 ║  ┌─────────────────────────────────────────────────┐                   ║
 ║  │ Writes to Meeting Transcripts/JSON Files/      │                   ║
 ║  │   YYYY-MM-DD_HHMMSS/ (same dir as input):      │                   ║
 ║  │   • recording_named.txt  ([Pharmacy Eng director]: "...")   │                   ║
 ║  │   • mapping.json         (map + confidence)      │                   ║
 ║  │                                                  │                   ║
 ║  │ Formatted workspace copy:                       │                   ║
 ║  │   • Meeting Transcripts/YYYY-MM-DD-meeting-name.md │                 ║
 ║  │                                                  │                   ║
 ║  │ Updates speaker profiles (MANDATORY):            │                   ║
 ║  │   • .claude/skills/meeting-transcription/        │                   ║
 ║  │     profiles/speaker-profiles.json               │                   ║
 ║  │   • Merges new topics, patterns, behavior        │                   ║
 ║  └─────────────────────────────────────────────────┘                   ║
 ║                                                                        ║
 ╚════════════════════════════════════════════════════════════════════════╝


══════════════════════════════════════════════════════════════════════════════════
 USER RESPONSE ❺ — CHOOSE SYNTHESIS MODE (optional)
 Where: Claude Code chat  |  When: Agent asks after mapping (agent prompts you)
══════════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────┐
  │  💬 Agent prompts you: Choose synthesis mode (or skip)              │
  │                                                                    │
  │  Options:                                                          │
  │    A. "Synthesize as discovery"   → deep research notes            │
  │    B. "Synthesize as general"     → lightweight summary            │
  │    C. (say nothing / "that's it") → stop here, transcript is done  │
  └──────────┬───────────────────┬──────────────────┬───────────────────┘
             │                   │                  │
       ┌─────┘             ┌─────┘            ┌─────┘
       ▼                   ▼                  ▼
 ╔══════════════╗  ╔══════════════╗  ╔══════════════╗
 ║  DISCOVERY   ║  ║  GENERAL     ║  ║  SKIP        ║
 ║              ║  ║              ║  ║              ║
 ║  discovery-  ║  ║  general-    ║  ║  Done.       ║
 ║  synthesis   ║  ║  synthesis   ║  ║  Named       ║
 ║  skill       ║  ║  skill       ║  ║  transcript  ║
 ║              ║  ║              ║  ║  is the       ║
 ║  Agent asks: ║  ║  Agent       ║  ║  deliverable. ║
 ║  • Initiative║  ║  produces:   ║  ║              ║
 ║  • Decision  ║  ║  • Summary   ║  ╚══════════════╝
 ║    context   ║  ║  • Actions   ║
 ║  • Audience  ║  ║  • Decisions ║
 ║              ║  ║  • Open Qs   ║
 ║  Produces:   ║  ║              ║
 ║  • Findings  ║  ║  Agent asks  ║
 ║  • Workflows ║  ║  where to    ║
 ║  • Quote idx ║  ║  save.       ║
 ║  • Actions   ║  ╚═══════╤══════╝
 ║              ║          │
 ║  Agent asks  ║          │
 ║  where to    ║          │
 ║  save.       ║          │
 ╚═══════╤══════╝          │
         │                 │
         └────────┬────────┘
                  │
                  ▼

══════════════════════════════════════════════════════════════════════════════════
 USER RESPONSE ❻ — SPECIFY SAVE LOCATION (if ❺ ≠ skip)
 Where: Claude Code chat  |  When: Synthesis agent asks (agent prompts you)
══════════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────┐
  │  💬 Agent prompts you: Specify save location                        │
  │                                                                    │
  │  Example: "Save to Initiatives/HighJump Deprecation/Discovery/"    │
  └──────────────────────────────┬──────────────────────────────────────┘
                                 │
                                 ▼

══════════════════════════════════════════════════════════════════════════════════
 FINAL OUTPUT — FILES ON DISK
══════════════════════════════════════════════════════════════════════════════════

 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  <workspace>/Meeting Transcripts/JSON Files/YYYY-MM-DD_HHMMSS/         ║
 ║    ├── recording.json .............. raw diarized transcript (SPEAKER_) ║
 ║    │   Machine output. You rarely read this directly — it's input      ║
 ║    │   for the speaker-mapping agent.                                   ║
 ║    ├── recording_named.txt ......... named transcript (real names)      ║
 ║    │   The human-readable transcript. This is what you'd read, search, ║
 ║    │   or share. Created after you confirm the speaker mapping.         ║
 ║    └── mapping.json ................ speaker map + confidence scores    ║
 ║        Records which SPEAKER_XX → which person, with confidence.       ║
 ║        Also marks the recording as "processed" so the agent skips it.  ║
 ║                                                                        ║
 ║  <workspace>/Meeting Transcripts/                                      ║
 ║    └── YYYY-MM-DD-meeting-name.md .. formatted workspace copy          ║
 ║        A markdown copy with meeting name — easier to browse than the   ║
 ║        timestamped JSON Files/ subfolder.                               ║
 ║                                                                        ║
 ║  ~/meetings/ ...................... WAV staging only (auto-deleted)     ║
 ║        Temporary audio files. Deleted after transcription completes.   ║
 ║                                                                        ║
 ║  <workspace>/<user-specified-path>/                                     ║
 ║    └── synthesis document .......... (if discovery or general was run)  ║
 ║        Structured notes (discovery) or meeting summary (general).      ║
 ║                                                                        ║
 ║  <workspace>/.claude/skills/meeting-transcription/profiles/            ║
 ║    └── speaker-profiles.json ....... updated with new evidence         ║
 ║        The agent learns from each meeting — topics, verbal patterns,   ║
 ║        etc. — to improve future speaker identification accuracy.       ║
 ║                                                                        ║
 ╚════════════════════════════════════════════════════════════════════════╝


 ═══════════════════════════════════════════════════════════════════════════
  USER ACTION SUMMARY
 ═══════════════════════════════════════════════════════════════════════════

  Action  What You Do                       Where         Phase      Initiation
  ──────  ────────────────────────────────   ───────────   ─────────   ─────────────
  ❶       Start recording                Claude Code (anywhere)   Record   You initiate
          Ctrl+Shift+R (any meeting app)
          CLI: record-meeting ...
  ❷       Stop recording                 Claude Code (anywhere)   Record   You initiate
          Ctrl+Shift+S (or Ctrl+C)
          (or 10 min silence auto-stop)
  ❸       "my meeting just ended"           Claude Code chat   Map      You initiate
          (optionally: "SPEAKER_02 is me")
  ❹       Confirm or correct mapping        Claude Code chat   Map      Agent prompts
          "looks good" / corrections
  ❺       Choose synthesis mode             Claude Code chat   Synthesize Agent prompts
          discovery / general / skip
  ❻       Specify save location             Claude Code chat   Synthesize Agent prompts
          (only if ❺ ≠ skip)

  Total user actions: 5-6 (❻ only if synthesizing)
  You initiate: ❶ ❷ ❸ — You decide when. Agent prompts: ❹ ❺ ❻ — Agent asks; you respond.
  Everything else is automatic (transcription, diarization, mapping, output).
 ═══════════════════════════════════════════════════════════════════════════
```
