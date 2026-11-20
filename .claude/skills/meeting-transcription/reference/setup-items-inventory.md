# Meeting Transcription Pipeline — Setup Items Inventory

> **Purpose:** Exhaustive list of everything that must be installed, configured, or created to run this pipeline. Seed for a future setup guide.

## Hardware / OS Prerequisites

| # | Item | Detail |
|---|------|--------|
| 1 | **macOS 14.2+ (Sonoma)** | `sw_vers -productVersion` — required for native system audio capture (Core Audio taps) |
| 2 | **Apple Silicon (arm64)** | WhisperX + torch optimized for M1/M2/M3/M4; Intel not supported |
| 3 | **16 GB RAM recommended** | `large-v3-turbo` model + diarization can cause OOM on 8 GB |

## Homebrew Packages

| # | Item | Install | Why |
|---|------|---------|-----|
| 4 | **Homebrew** | https://brew.sh | Package manager — prerequisite for everything below |
| 5 | **ffmpeg** | `brew install ffmpeg` | Audio format conversion (WhisperX dependency) |

## Python Environment

| # | Item | Detail |
|---|------|--------|
| 6 | **uv** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` — fast Python package manager. Installs to `~/.local/bin` (add to PATH). |
| 7 | **Python 3.12+** | uv installs it automatically if missing |
| 8 | **Dedicated venv** | `uv venv ~/.local/share/meeting-transcription/venv --python 3.12` |
| 9 | **Python dependencies** | `uv pip install --python ~/.local/share/meeting-transcription/venv/bin/python -r .claude/skills/meeting-transcription/scripts/requirements.txt` |
| 10 | **requirements.txt contents** | `pysysaudio>=0.1.3`, `whisperx>=3.3.0`, `sounddevice>=0.5.1`, `soundfile>=0.12.1`, `numpy>=1.26.0,<2.0`, `torch>=2.5.0` |

## macOS Permission

| # | Item | Detail |
|---|------|--------|
| 11 | **Screen & System Audio Recording** | System Settings → Privacy & Security → Screen & System Audio Recording → enable for Python interpreter or Terminal. macOS prompts on first use. One-time grant. |

## HuggingFace (Diarization)

| # | Item | Detail |
|---|------|--------|
| 12 | **HuggingFace account** | https://huggingface.co/join |
| 13 | **Accept pyannote model license** | https://huggingface.co/pyannote/speaker-diarization-community-1 |
| 14 | **HF_TOKEN env var** | Create token at https://huggingface.co/settings/tokens → add `export HF_TOKEN="hf_xxx"` to `~/.zshrc` |

## Model Downloads (~2–4 GB)

| # | Item | Detail |
|---|------|--------|
| 15 | **WhisperX large-v3-turbo** | Auto-downloads on first run, or pre-warm via `setup.sh` |
| 16 | **pyannote speaker-diarization-community-1** | Auto-downloads on first run (requires HF_TOKEN), or pre-warm via `setup.sh` |

## Output Directories

| # | Item | Detail |
|---|------|--------|
| 17 | **WAV staging dir** | `mkdir -p ~/meetings` — temporary audio files during recording (deleted after processing) |
| 18 | **Workspace transcript dir** | `Meeting Transcripts/` — recording JSON, named transcripts, mapping files. Created automatically by the script. |

## OS-Level Hotkeys

| # | Item | Path | Detail |
|---|------|------|--------|
| 19 | **macOS Shortcuts.app bindings** | Shortcuts.app | Two shortcuts: `Start Meeting Recording` (bound to `⌃⇧R`) → runs `os-hotkey-start.sh`; `Stop Meeting Recording` (bound to `⌃⇧S`) → runs `os-hotkey-stop.sh`. One-time setup (~90 seconds — see SKILL.md "One-time setup"). |
| 20 | **OS-hotkey helper scripts** | `.claude/skills/meeting-transcription/scripts/os-hotkey-{start,stop}.sh` | Tool-agnostic start/stop. Shipped with the skill. Triggers Terminal.app with the recorder; works from any app (Claude Code, Slack, browser, etc.). |

## Claude Code Companion Skills

| # | Item | Path | Purpose |
|---|------|------|---------|
| 21 | **Speaker Mapping skill** | `.claude/skills/speaker-mapping/SKILL.md` | Maps SPEAKER_XX labels → real names after recording. Auto-invoked when you say "my meeting just ended" / "process my recording". |
| 22 | **Discovery Synthesis skill** | `.claude/skills/discovery-synthesis/SKILL.md` | Structured research notes from named transcript. Manual invocation. |

## Speaker Profiles

| # | Item | Detail |
|---|------|--------|
| 23 | **speaker-profiles.json** | `.claude/skills/meeting-transcription/profiles/speaker-profiles.json` — JSON store of known speakers (topics, verbal patterns, behavior summary, comms preferences, recency, voice embeddings). Created empty by `setup.sh`; populated automatically by the speaker-mapping skill. |

## Shell Function (Optional but Recommended)

| # | Item | Detail |
|---|------|--------|
| 24 | **`record-meeting` shell function** | Add to `~/.zshrc`. Wraps `record_meeting.py` invocation. See SKILL.md for the function body. |

## Google Workspace MCP (Optional)

| # | Item | Detail |
|---|------|--------|
| 25 | **Node.js 18+** | Required to run the MCP server |
| 26 | **Google Cloud project** | Calendar API enabled, OAuth Desktop credentials |
| 27 | **`google-workspace` MCP** | Install via `claude mcp add` (or edit Claude MCP config at workspace `.mcp.json` / `~/.claude.json` directly). Enables auto-fetching meeting attendees for speaker mapping. Without it, provide attendees manually. |

## Personalization Points

| # | Item | Where | Why |
|---|------|-------|-----|
| 28 | **Domain vocabulary prompt** | `record_meeting.py` `DEFAULT_DOMAIN_PROMPT` or `--initial-prompt` CLI flag | Built-in prompt is pharmacy/fulfillment-specific — customize for other domains |
| 29 | **Workspace path** | Shortcuts.app binding (script path) + `record-meeting` shell function in `~/.zshrc` | Hardcoded absolute Google Drive path — update if workspace moves |

## Automated Setup

| # | Item | Detail |
|---|------|--------|
| 30 | **`setup.sh`** | `bash .claude/skills/meeting-transcription/setup.sh` — automates items 4–10, 14–18, 23. Checks permission (11). Flags 12–13 if missing. Checks 21–22, 25–27. User-driven (not automated): 19 (Shortcuts.app bindings — one-time manual setup, ~90 seconds; see SKILL.md). |
