#!/bin/bash
# Meeting Transcription Pipeline Setup
# macOS Apple Silicon only. Automates WhisperX + pyannote + pysysaudio pipeline.
#
# Usage: bash setup.sh [--skip-warmup] [--force]
#   --skip-warmup   Skip pre-downloading WhisperX + pyannote models (~2-4 GB)
#   --force         Overwrite existing config files without prompting
#
# Idempotent: safe to run multiple times.

set -uo pipefail
IFS=$'\n\t'

# --- Paths (script locates itself) ---
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
SCRIPTS_DIR="$SKILL_DIR/scripts"
VENV_DIR="$HOME/.local/share/meeting-transcription/venv"
VENV_PYTHON="$VENV_DIR/bin/python"
REQUIREMENTS="$SCRIPTS_DIR/requirements.txt"
SPEAKER_PROFILES_DEST="$SKILL_DIR/profiles/speaker-profiles.json"
MCP_JSON="$WORKSPACE_ROOT/.mcp.json"
SKILLS_DIR="$WORKSPACE_ROOT/.claude/skills"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

# --- State ---
SKIP_WARMUP=false
FORCE=false
ERRORS=()
WARNINGS=()

# --- Parse args ---
for arg in "$@"; do
  case "$arg" in
    --skip-warmup) SKIP_WARMUP=true ;;
    --force)       FORCE=true ;;
    -h|--help)
      sed -n '1,12p' "$0" | grep -E '^#'
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $arg${RESET}"
      echo "Usage: bash setup.sh [--skip-warmup] [--force]"
      exit 1
      ;;
  esac
done

# --- Helpers ---
section() { echo -e "\n${BOLD}=== $* ===${RESET}"; }
ok()      { echo -e "${GREEN}✓ $*${RESET}"; }
warn()    { echo -e "${YELLOW}⚠ $*${RESET}"; WARNINGS+=("$*"); }
fail()    { echo -e "${RED}✗ $*${RESET}"; ERRORS+=("$*"); }

version_gte() {
  local a="$1" b="$2"
  if [ "$(printf '%s\n' "$a" "$b" | sort -V | head -1)" == "$b" ] && [ "$a" != "$b" ]; then
    return 0
  elif [ "$a" == "$b" ]; then
    return 0
  else
    return 1
  fi
}

check_cmd() { command -v "$1" &>/dev/null; }

# --- 1. Banner ---
section "Meeting Transcription Pipeline Setup"
echo "Setting up local meeting transcription pipeline (WhisperX + pyannote + pysysaudio)"
echo "Skill directory: $SKILL_DIR"

# --- 2. Pre-flight checks ---
section "Pre-flight Checks"

# macOS 14.2+
MACOS_VER="$(sw_vers -productVersion 2>/dev/null || echo "0")"
if version_gte "$MACOS_VER" "14.2"; then
  ok "macOS $MACOS_VER (14.2+ required for system audio capture)"
else
  fail "macOS $MACOS_VER — need 14.2+ (Sonoma) for native system audio capture"
fi

# Apple Silicon
ARCH="$(uname -m 2>/dev/null || echo "")"
if [ "$ARCH" == "arm64" ]; then
  ok "Apple Silicon ($ARCH)"
else
  fail "Not Apple Silicon (got $ARCH). This pipeline is optimized for M1/M2/M3/M4."
fi

# Python 3.12+
PY_VER=""
if check_cmd python3.12; then
  PY_VER="$(python3.12 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' || echo "")"
elif check_cmd python3; then
  PY_VER="$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' || echo "")"
fi
if [ -n "$PY_VER" ] && version_gte "$PY_VER" "3.12"; then
  ok "Python $PY_VER"
elif [ -n "$PY_VER" ]; then
  warn "Python $PY_VER found; pipeline needs 3.12+. uv will install it when needed."
else
  warn "Python not found in PATH; uv will install 3.12 when creating venv."
fi

# Node.js 18+ (optional, for Google Calendar MCP)
if check_cmd node; then
  NODE_VER="$(node --version 2>/dev/null | sed 's/^v//' | cut -d. -f1 | grep -E '^[0-9]+$' || echo "0")"
  if [ "${NODE_VER:-0}" -ge 18 ]; then
    ok "Node.js $(node --version)"
  else
    warn "Node.js $NODE_VER — need 18+ for Google Calendar MCP (optional)"
  fi
else
  warn "Node.js not found — required for optional Google Calendar MCP"
fi

# --- 3. Install dependencies ---
section "Dependencies"

# Homebrew
if ! check_cmd brew; then
  fail "Homebrew not installed. Install from https://brew.sh"
else
  ok "Homebrew installed"
fi

# ffmpeg
if check_cmd ffmpeg; then
  ok "ffmpeg installed"
else
  echo "Installing ffmpeg..."
  if brew install ffmpeg 2>/dev/null; then
    ok "ffmpeg installed"
  else
    fail "Failed to install ffmpeg (brew install ffmpeg)"
  fi
fi

# uv
if check_cmd uv; then
  ok "uv installed"
else
  echo "Installing uv..."
  if curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null; then
    export PATH="$HOME/.local/bin:$PATH"
    if check_cmd uv; then
      ok "uv installed"
      echo "  Add to your shell profile: export PATH=\"\$HOME/.local/bin:\$PATH\""
    else
      fail "uv installed but not in PATH. Add: export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
  else
    fail "Failed to install uv (curl -LsSf https://astral.sh/uv/install.sh | sh)"
  fi
fi

export PATH="$HOME/.local/bin:$PATH"

# --- 4. Python venv and dependencies ---
section "Python environment"

mkdir -p "$(dirname "$VENV_DIR")"
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating venv at $VENV_DIR (Python 3.12)..."
  if uv venv "$VENV_DIR" --python 3.12 2>/dev/null; then
    ok "Venv created"
  else
    fail "Failed to create venv (uv venv $VENV_DIR --python 3.12)"
  fi
else
  ok "Venv already exists at $VENV_DIR"
fi

if [ ! -f "$REQUIREMENTS" ]; then
  fail "requirements.txt not found: $REQUIREMENTS"
else
  echo "Installing Python dependencies (pysysaudio, whisperx, sounddevice, torch, etc.)..."
  if uv pip install --python "$VENV_PYTHON" -r "$REQUIREMENTS" 2>/dev/null; then
    ok "Dependencies installed"
  else
    fail "Failed to install dependencies (uv pip install -r $REQUIREMENTS)"
  fi
fi

# --- 5. System audio permission check ---
section "System Audio Permission"

echo "pysysaudio uses macOS native Core Audio taps to capture system audio."
echo "This requires 'Screen & System Audio Recording' permission."
echo ""
if "$VENV_PYTHON" -c "
from pysysaudio import SystemAudioRecorder
if SystemAudioRecorder.check_permission():
    print('GRANTED')
else:
    print('NOT_GRANTED')
" 2>/dev/null | grep -q "GRANTED"; then
  ok "Screen & System Audio Recording permission is granted"
else
  warn "Screen & System Audio Recording permission not yet granted."
  echo "  On first recording, macOS will prompt for permission."
  echo "  Or grant manually: System Settings → Privacy & Security → Screen & System Audio Recording"
  echo "  Enable permission for your Python interpreter or Terminal."
fi

# --- 6. Output directory ---
section "Output directory"

mkdir -p "$HOME/meetings"
ok "Output directory: $HOME/meetings"

# --- 7. Configure speaker profiles ---
section "Configure speaker profiles"

mkdir -p "$SKILL_DIR/profiles"
if [ -f "$SPEAKER_PROFILES_DEST" ]; then
  ok "Speaker profiles already exist: $SPEAKER_PROFILES_DEST"
else
  echo '{}' > "$SPEAKER_PROFILES_DEST"
  ok "Created empty speaker profiles at $SPEAKER_PROFILES_DEST (the speaker-mapping agent will populate this automatically)"
fi

# --- 8. Check HF_TOKEN ---
section "HuggingFace Token (for diarization)"

if [ -n "${HF_TOKEN:-}" ] && [ "$HF_TOKEN" != "" ]; then
  ok "HF_TOKEN is set"
else
  warn "HF_TOKEN is not set — diarization will not work until you configure it."
  echo ""
  echo "To set up:"
  echo "  1. Create a HuggingFace account: https://huggingface.co/join"
  echo "  2. Accept model licenses:"
  echo "     - https://huggingface.co/pyannote/speaker-diarization-community-1"
  echo "  3. Create a token: https://huggingface.co/settings/tokens"
  echo "  4. Add to your shell profile (~/.zshrc):"
  echo "     export HF_TOKEN=\"hf_your_token_here\""
  echo ""
fi

# --- 9. Pre-warm models ---
section "Pre-warm models"

if [ "$SKIP_WARMUP" == true ]; then
  warn "Skipping warmup (--skip-warmup). Models will download on first run."
else
  echo "Downloading WhisperX large-v3-turbo model..."
  if "$VENV_PYTHON" -c "
import whisperx
print('Downloading transcription model...')
whisperx.load_model('large-v3-turbo', device='cpu', compute_type='int8')
print('Done.')
" 2>/dev/null; then
    ok "Transcription model warmed up"
  else
    fail "Transcription warmup failed. Run manually: $VENV_PYTHON -c \"import whisperx; whisperx.load_model('large-v3-turbo', device='cpu', compute_type='int8')\""
  fi

  if [ -n "${HF_TOKEN:-}" ] && [ "$HF_TOKEN" != "" ]; then
    echo "Downloading diarization model..."
    if "$VENV_PYTHON" -c "
import os
from whisperx.diarize import DiarizationPipeline
token = os.environ.get('HF_TOKEN', '')
if token:
    print('Downloading diarization model...')
    try:
        DiarizationPipeline(use_auth_token=token, device='cpu')
    except TypeError:
        DiarizationPipeline(token=token, device='cpu')
    print('Done.')
else:
    print('HF_TOKEN not set, skipping diarization warmup.')
" 2>/dev/null; then
      ok "Diarization model warmed up"
    else
      warn "Diarization warmup failed. May retry after setting HF_TOKEN."
    fi
  else
    warn "HF_TOKEN not set, skipping diarization warmup."
  fi
fi

# --- 10. Google Calendar MCP (optional) ---
section "Google Calendar MCP (optional)"

if [ -f "$MCP_JSON" ] && grep -q "google-workspace\|google-calendar\|google_calendar" "$MCP_JSON" 2>/dev/null; then
  ok "Google Workspace / Calendar MCP configured in workspace .mcp.json"
elif [ -f "$HOME/.claude.json" ] && grep -q "google-workspace\|google-calendar\|google_calendar" "$HOME/.claude.json" 2>/dev/null; then
  ok "Google Workspace / Calendar MCP configured in ~/.claude.json"
else
  warn "Google Workspace / Calendar MCP not found in workspace .mcp.json or ~/.claude.json"
  echo "  Optional: enables the speaker-mapping skill to auto-fetch meeting attendees."
  echo "  Install via: claude mcp add (Claude Code) — see Claude Code docs for MCP setup."
fi

# --- 11. Verify Claude Code agent skills ---
section "Claude Code agent skills"

MISSING_SKILLS=()
[ ! -f "$SKILLS_DIR/speaker-mapping/SKILL.md" ] && MISSING_SKILLS+=("speaker-mapping")
[ ! -f "$SKILLS_DIR/discovery-synthesis/SKILL.md" ] && MISSING_SKILLS+=("discovery-synthesis")

if [[ ${#MISSING_SKILLS[@]} -eq 0 ]]; then
  ok "All companion skills found (speaker-mapping, discovery-synthesis)"
else
  warn "Missing companion skills: ${MISSING_SKILLS[*]}"
  echo "  These skills are required for the pipeline. Each lives at $SKILLS_DIR/<name>/SKILL.md"
fi

# --- 12. Summary ---
section "Summary"

echo ""
echo "Installed / configured:"
echo "  • pysysaudio (native system audio capture via Core Audio taps)"
echo "  • Python venv: $VENV_DIR"
echo "  • ffmpeg, uv"
echo "  • Speaker profiles: $SPEAKER_PROFILES_DEST"
echo "  • Output directory: $HOME/meetings"
echo ""
echo "Manual steps remaining:"
[ -z "${HF_TOKEN:-}" || "$HF_TOKEN" == "" ] && echo "  • Set HF_TOKEN (see HuggingFace instructions above)"
[ "$SKIP_WARMUP" == true ] && echo "  • Models will download on first run"
echo "  • [Care Delivery director] 'Screen & System Audio Recording' permission on first recording (macOS will prompt)"
echo ""
echo "Next steps:"
echo "  1. Record a meeting: press ⌃⇧R from anywhere in macOS (or run: record-meeting --mic --diarize)"
echo "  2. In Claude Code, say 'my meeting just ended' — the speaker-mapping skill picks the recording automatically"
echo "  3. Synthesize (optional):"
echo "     - Discovery: invoke the discovery-synthesis skill for structured research notes"
echo "     - Skip: stop at the named transcript when no synthesis is needed"
echo ""

if [[ ${#ERRORS[@]} -gt 0 ]]; then
  echo -e "${RED}Errors encountered:${RESET}"
  for e in "${ERRORS[@]}"; do echo "  • $e"; done
  echo ""
  exit 1
fi

if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  echo -e "${YELLOW}Warnings:${RESET}"
  for w in "${WARNINGS[@]}"; do echo "  • $w"; done
  echo ""
fi

echo -e "${GREEN}Setup complete.${RESET}"
