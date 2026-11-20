#!/usr/bin/env python3
"""
Local meeting transcription: record → transcribe → align → diarize → JSON.
Insourced WhisperX pipeline for local meeting transcription.
"""

import argparse
import atexit
import gc
import json
import os
import queue
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import soundfile as sf

DEFAULT_DOMAIN_PROMPT = (
    "Discussion of pharmacy fulfillment operations at Hims and Hers. "
    "Terms: PV1, PV2, beyondRx, BeyondFC, beyondWMS, HighJump, Tompkins, Shipium, "
    "DEA, USP 795, USP 797, HIPAA, SLA, wave planning, pick and pack, putwall, "
    "conveyance, compounding, shipment, carrier management, Rx, non-Rx, FPSE, UPH, "
    "SOX, RBAC, MRC, OMS, WMS, dispense, verification, manifesting, staging, "
    "BDOT, CPT, OH1, OH2, AZ1, AZ2, AZ3, iARX, 503A, 503B, FDA, DUR, NDC, "
    "Medispan, Pack Queue, Pack Recipe, Shipment Rule Builder, Problem Solve, "
    "Import All Shipments, Shipment Authority, VCpO, Gaylord, cold chain, lab kits, "
    "Curexa, RedRock, Anaseo, AC3, NetSuite, Looker, Retool, Zebra. "
    "People: [Director of Pharmacy & Fulfillment Product], [Pharmacy Eng director], [teammate], [Ops Program director], [Sr. Program Manager, Operations Strategy], "
    "[SVP of Operations and Fulfillment], [Director, Order Management], [PM], [Pharmacy PM], [PM], "
    "[Software Team Lead], [Pharmacy Systems & Architecture], [Sr. SWE, Backend], [Technical Program Manager, Pharmacy & Compounding Squads], Danny Pedrini."
)
SAMPLE_RATE = 16000

# Mic device resolution: explicit --mic-device > $MEETING_MIC_DEVICE > built-in laptop mic > system default.
# Locking to the built-in mic prevents Bluetooth headsets (which get exclusive-claimed by Meet/Zoom/Teams
# and downgraded to HFP mode) from being silently picked up as the recorder mic — historically the #1
# cause of "my voice missing from the transcript" failures (mic_rms_db stuck at the noise floor).
BUILTIN_MIC_CANDIDATES = (
    "MacBook Pro Microphone",
    "MacBook Air Microphone",
    "Built-in Microphone",
)


def _find_workspace_root() -> Path:
    # Anchor on the workspace's CLAUDE.md + .claude/ pair — a bare .cursor/ falsely
    # matched ~/.cursor and routed recordings to ~/Meeting Transcripts/ instead of
    # the actual Cursor Files workspace.
    path = Path(__file__).resolve().parent
    for ancestor in [path] + list(path.parents):
        if (ancestor / "CLAUDE.md").is_file() and (ancestor / ".claude").is_dir():
            return ancestor
    return Path(__file__).resolve().parents[4]


_WORKSPACE_ROOT = _find_workspace_root()
CHUNK_MS = 100
SILENCE_RMS_THRESHOLD = 0.002
PID_FILE = Path.home() / ".meeting-recording.pid"


def _write_pid_file() -> None:
    if PID_FILE.exists():
        try:
            existing_pid = int(PID_FILE.read_text().strip())
            os.kill(existing_pid, 0)
            raise SystemExit(
                f"Another recording is already running (PID {existing_pid}). "
                "Stop it first, or delete ~/.meeting-recording.pid if stale."
            )
        except (ValueError, ProcessLookupError, PermissionError):
            pass
    PID_FILE.write_text(str(os.getpid()))


def _remove_pid_file() -> None:
    PID_FILE.unlink(missing_ok=True)


def _get_device_index(name: str) -> int:
    """Resolve a sounddevice device name to its index (for --device fallback and --mic)."""
    import sounddevice as sd
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if name.lower() in d["name"].lower():
            return i
    raise SystemExit(f"Device not found: {name}. Run: python -c \"import sounddevice; print(sounddevice.query_devices())\"")


def _resolve_mic_device(explicit: str | None) -> str:
    """Resolve the mic device name with a tool-agnostic precedence chain.

    Precedence (highest → lowest):
      1. explicit --mic-device flag
      2. $MEETING_MIC_DEVICE env var (works in Claude Code, raw CLI, any agent)
      3. Built-in laptop mic (BUILTIN_MIC_CANDIDATES) — the safe default
      4. macOS system default input (last resort, prints a warning)

    Returns the resolved device NAME (the substring matcher in _get_device_index handles index lookup).
    """
    import sounddevice as sd

    if explicit:
        return explicit

    env_device = os.environ.get("MEETING_MIC_DEVICE")
    if env_device:
        return env_device

    input_devices = [d for d in sd.query_devices() if d.get("max_input_channels", 0) > 0]
    available_names = [d["name"] for d in input_devices]
    for candidate in BUILTIN_MIC_CANDIDATES:
        for name in available_names:
            if candidate.lower() in name.lower():
                return name

    print(
        f"\n  {_ANSI_YELLOW}[WARNING]{_ANSI_RESET} Built-in laptop mic not found in available devices.\n"
        f"           Available input devices: {available_names}\n"
        f"           Falling back to macOS system default input — verify it's the right mic in the pre-flight summary below.\n"
        f"           To pin a specific mic permanently, set MEETING_MIC_DEVICE env var (e.g., in ~/.zshrc).",
        file=sys.stderr,
    )
    default_input = sd.query_devices(kind="input")
    if isinstance(default_input, dict):
        return default_input["name"]
    raise SystemExit(
        "Could not determine default input device. "
        "Specify one with --mic-device or set MEETING_MIC_DEVICE env var."
    )


# ANSI color codes for highly-visible warnings (macOS Terminal / iTerm all support).
_ANSI_RED = "\033[1;31m"
_ANSI_YELLOW = "\033[1;33m"
_ANSI_GREEN = "\033[1;32m"
_ANSI_RESET = "\033[0m"

# macOS alert sounds — played asynchronously so recording isn't interrupted.
# Glass = bright, positive ding ("all clear"). Basso = deep, ominous thud ("something's wrong").
# Distinct tones so the user knows the outcome without looking at the terminal.
_SOUND_SUCCESS = "/System/Library/Sounds/Glass.aiff"
_SOUND_WARNING = "/System/Library/Sounds/Basso.aiff"
_SOUND_FALLBACK = "/System/Library/Sounds/Funk.aiff"


def _play_alert_sound(repeat: int = 1, sound: str | None = None) -> None:
    """Fire-and-forget macOS alert sound via afplay.

    Plays even when the user is on a different screen/app — audio alerts are the
    only reliable way to surface recording failures when the terminal isn't visible.
    Repeats the sound `repeat` times (with a short gap) for severity: 1x for warnings,
    3x for critical failures. Pass sound=_SOUND_SUCCESS for the positive confirmation tone.
    """
    if sys.platform != "darwin":
        return
    snd = sound or _SOUND_WARNING
    if not os.path.exists(snd):
        snd = _SOUND_FALLBACK
    if not os.path.exists(snd):
        return
    try:
        cmd = " && sleep 0.3 && ".join([f"afplay '{snd}'"] * repeat)
        subprocess.Popen(["bash", "-c", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (FileNotFoundError, OSError):
        pass


def _macos_mic_input_volume() -> int | None:
    """Return macOS system input (mic) volume 0-100, or None if unavailable.

    Uses `osascript` — the most reliable, permission-free way to read this on macOS.
    Returns None on non-Darwin platforms or if the command fails (so callers can skip
    the check gracefully instead of blocking recording).
    """
    if sys.platform != "darwin":
        return None
    try:
        result = subprocess.run(
            ["osascript", "-e", "input volume of (get volume settings)"],
            capture_output=True, text=True, timeout=2, check=True,
        )
        value = result.stdout.strip()
        if value == "missing value" or not value:
            return None
        return int(value)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError, FileNotFoundError):
        return None


def _warn_mic_volume(volume: int | None, allow_low: bool = False) -> bool:
    """Print a prominent warning if the system mic input volume is below 100%.

    macOS defaults the mic to 50% after OS updates / device reconnects, which yields
    mic RMS ~15-20 dB below speech threshold — your voice gets transcribed poorly or
    not at all. We want this to fail loud at recording start, not silently 28 min in.

    Returns True if a warning was issued (caller should skip the success sound).

    Behavior:
    - None (platform unsupported / osascript failed): silent skip → False
    - 100:           green OK line → False
    - 50 <= v < 100: yellow WARNING (continue immediately) → True
    - v < 50:        red WARNING + 5-second countdown so user can Ctrl+C and fix
                     (unless allow_low=True, which downgrades to a yellow warning) → True
    """
    if volume is None:
        return False
    if volume >= 100:
        print(f"  {_ANSI_GREEN}[OK]{_ANSI_RESET} Mic input volume: {volume}%")
        return False
    if volume >= 50 or allow_low:
        _play_alert_sound(repeat=1)
        print(
            f"\n  {_ANSI_YELLOW}[WARNING]{_ANSI_RESET} Mic input volume is {volume}% (recommended: 100%).\n"
            f"           Your voice may be transcribed poorly. Fix: System Settings → Sound → Input → slider to max.\n"
            f"           Continuing with recording..."
        )
        return True
    _play_alert_sound(repeat=3)
    print(
        f"\n  {_ANSI_RED}[WARNING]{_ANSI_RESET} Mic input volume is dangerously low ({volume}%).\n"
        f"           Your voice will almost certainly NOT be captured at this level.\n"
        f"           Fix: System Settings → Sound → Input → slider to max.\n"
        f"           Press Ctrl+C within 5 seconds to abort, or wait to record anyway..."
    )
    try:
        for i in range(5, 0, -1):
            print(f"           Starting in {i}...", end="\r", flush=True)
            time.sleep(1)
        print(" " * 40, end="\r")
    except KeyboardInterrupt:
        print(f"\n  Aborted by user. Fix mic volume and re-run.")
        raise SystemExit(1)
    return True


def _macos_current_output_device() -> str | None:
    """Return the active audio output device name on macOS, or None if unavailable.

    Useful for flagging Bluetooth output in the pre-flight summary — not every version
    of macOS reliably captures Bluetooth-routed audio via Core Audio process taps.
    """
    if sys.platform != "darwin":
        return None
    try:
        result = subprocess.run(
            ["osascript", "-e",
             'try\n'
             ' set outputDevice to do shell script "system_profiler SPAudioDataType | awk \'/Default Output Device: Yes/{found=1} found && /^[:space:]{4,8}[^:]+:/ && !/Default/ {gsub(/:$/, \\"\\"); gsub(/^[:space:]+/, \\"\\"); print; exit}\'"\n'
             ' return outputDevice\n'
             'on error\n'
             ' return ""\n'
             'end try'],
            capture_output=True, text=True, timeout=3, check=False,
        )
        name = result.stdout.strip()
        return name or None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _preflight_audio_summary(mic_device_name: str | None, using_system_tap: bool) -> None:
    """Print a visible pre-flight summary of the audio capture setup.

    Shows exactly what will be captured BEFORE recording starts so the user can
    spot misconfigurations (wrong mic, Bluetooth output, etc.) in <5 seconds
    instead of 28 minutes in. This is the first line of defense against silent
    capture failures.
    """
    print(f"\n{_ANSI_GREEN}━━━ Pre-flight audio check ━━━{_ANSI_RESET}")
    has_warning = False
    if using_system_tap:
        print(f"  Sys audio: macOS Core Audio process tap (pysysaudio)")
    else:
        print(f"  Sys audio: sounddevice device capture (legacy --device)")
    if mic_device_name:
        print(f"  Mic:       {mic_device_name}")
    else:
        print(f"  Mic:       {_ANSI_YELLOW}[disabled]{_ANSI_RESET} (no --mic flag — your voice will NOT be captured)")
    output_device = _macos_current_output_device()
    if output_device:
        bt_hint = ""
        if any(k in output_device.lower() for k in ("airpods", "bluetooth", "beats", "bose")):
            bt_hint = f" {_ANSI_YELLOW}[Bluetooth — sys-tap may fail on some macOS versions; fallback to wired if sys_db stays at -120]{_ANSI_RESET}"
            has_warning = True
        print(f"  Output:    {output_device}{bt_hint}")
    if mic_device_name:
        if _warn_mic_volume(_macos_mic_input_volume()):
            has_warning = True
    print(f"{_ANSI_GREEN}━━━{_ANSI_RESET}\n")
    if not has_warning:
        _play_alert_sound(repeat=1, sound=_SOUND_SUCCESS)


def _silence_check(chunk: np.ndarray, chunks_silent: int, silence_chunks: int) -> tuple[int, bool]:
    """Returns (updated_chunks_silent, should_stop)."""
    rms = np.sqrt(np.mean(chunk ** 2))
    if rms < SILENCE_RMS_THRESHOLD:
        chunks_silent += 1
        return chunks_silent, chunks_silent >= silence_chunks
    return 0, False


def _check_and_normalize_audio(wav_path: Path, threshold_db: float = -35.0) -> Path:
    """Peak-normalize audio if mean RMS is below threshold.

    Solo recordings (mic-only, no remote participants) produce very quiet audio
    that falls below the VAD detection threshold. This normalizes the audio to
    make speech detectable.

    Returns the original path if levels are adequate, or a normalized copy.
    """
    data, sr = sf.read(str(wav_path))
    if len(data) == 0:
        return wav_path

    rms = np.sqrt(np.mean(data ** 2))
    if rms == 0:
        return wav_path

    rms_db = 20 * np.log10(rms)
    if rms_db >= threshold_db:
        return wav_path

    peak = np.abs(data).max()
    if peak == 0:
        return wav_path

    target_peak = 10 ** (-1.0 / 20)  # -1 dB headroom
    gain = target_peak / peak
    normalized = (data * gain).astype(np.float32)
    new_rms_db = 20 * np.log10(np.sqrt(np.mean(normalized ** 2)))

    normalized_path = wav_path.parent / f"{wav_path.stem}_normalized{wav_path.suffix}"
    sf.write(str(normalized_path), normalized, sr, subtype="FLOAT")
    print(f"  Audio quiet ({rms_db:.1f} dB mean) — normalized to {new_rms_db:.1f} dB → {normalized_path.name}")

    return normalized_path


def _drain_audio_queue(q: queue.Queue, target_frames: int, block_timeout: float = 0.0) -> np.ndarray | None:
    """Drain audio from a callback queue, returning exactly target_frames.

    Drains all available data (keeps newest portion for time alignment).
    block_timeout > 0 waits for the first chunk; 0 returns None immediately if empty.
    """
    chunks: list[np.ndarray] = []
    try:
        chunks.append(q.get(timeout=block_timeout) if block_timeout > 0 else q.get_nowait())
    except queue.Empty:
        return None
    while True:
        try:
            chunks.append(q.get_nowait())
        except queue.Empty:
            break
    audio = np.concatenate(chunks)
    if len(audio) >= target_frames:
        return audio[len(audio) - target_frames:]
    return np.pad(audio, (target_frames - len(audio), 0))


class _MicGainTracker:
    """Dynamically matches mic RMS to system audio RMS before mixing.

    Without gain matching, mic audio (your voice) is typically much quieter than
    system audio (remote participants via Meet/Teams/Zoom). This causes WhisperX
    to under-detect or mis-diarize the local speaker. The tracker computes a
    smoothed gain factor from rolling RMS of both sources and applies it to the
    mic signal before summing.
    """

    def __init__(
        self,
        warmup_chunks: int = 30,
        smoothing: float = 0.15,
        max_gain: float = 40.0,
        min_gain: float = 3.0,
        min_rms: float = 1e-6,
    ):
        self._warmup = warmup_chunks  # ~3s at 10 chunks/sec before gain kicks in
        self._alpha = smoothing
        self._max_gain = max_gain
        self._min_gain = min_gain
        self._min_rms = min_rms
        self._sys_ema: float = 0.0
        self._mic_ema: float = 0.0
        self._gain: float = min_gain
        self._n: int = 0

    def update_sys_only(self, sys_chunk: np.ndarray) -> None:
        """Update sys EMA and warmup counter using only system audio.

        Called when mic data is unavailable (--mic not passed, mic queue empty,
        or mic failed). Keeps sys_db tracking and health checks alive without
        touching mic EMA or gain.
        """
        sys_rms = float(np.sqrt(np.mean(sys_chunk ** 2)))
        if self._n == 0:
            self._sys_ema = sys_rms
        else:
            self._sys_ema = self._alpha * sys_rms + (1 - self._alpha) * self._sys_ema
        self._n += 1

    def update_and_mix(self, sys_chunk: np.ndarray, mic_chunk: np.ndarray) -> np.ndarray:
        sys_rms = float(np.sqrt(np.mean(sys_chunk ** 2)))
        mic_rms = float(np.sqrt(np.mean(mic_chunk ** 2)))

        if self._n == 0:
            self._sys_ema = sys_rms
            self._mic_ema = mic_rms
        else:
            a = self._alpha
            self._sys_ema = a * sys_rms + (1 - a) * self._sys_ema
            self._mic_ema = a * mic_rms + (1 - a) * self._mic_ema
        self._n += 1

        if self._n >= self._warmup and self._mic_ema > self._min_rms:
            self._gain = max(self._min_gain, min(self._sys_ema / self._mic_ema, self._max_gain))

        mixed = sys_chunk + mic_chunk * self._gain
        peak = float(np.abs(mixed).max())
        if peak > 1.0:
            mixed = mixed / peak
        return mixed.astype(np.float32)

    def _to_db(self, rms: float) -> float:
        return 20 * np.log10(max(rms, self._min_rms))

    @property
    def sys_db(self) -> float:
        return self._to_db(self._sys_ema)

    @property
    def mic_db(self) -> float:
        return self._to_db(self._mic_ema)

    @property
    def gain(self) -> float:
        return self._gain

    @property
    def warmed_up(self) -> bool:
        return self._n >= self._warmup

    def status_str(self) -> str:
        if not self.warmed_up:
            return "[mic: calibrating]"
        return f"[sys:{self.sys_db:+.0f}dB mic:{self.mic_db:+.0f}dB gain:{self.gain:.1f}x]"

    def summary(self) -> dict:
        return {
            "sys_rms_db": round(self.sys_db, 1),
            "mic_rms_db": round(self.mic_db, 1),
            "mic_gain_applied": round(self.gain, 2),
            "min_gain": self._min_gain,
            "max_gain": self._max_gain,
            "chunks_processed": self._n,
        }


_HEALTH_SYS_SILENCE_DB = -90.0     # sys_db this low means "effectively zero signal"
_HEALTH_MIC_SILENCE_DB = -80.0     # mic_db this low means "at the noise floor, no speech"
_HEALTH_GRACE_SECONDS = 5.0        # gain tracker warms up in ~3s; 5s avoids false positives
                                   # while catching failures fast (user switches screens quickly)


def _check_runtime_health(
    gain_tracker: "_MicGainTracker",
    elapsed: float,
    warned: dict[str, bool],
    has_mic: bool,
) -> None:
    """Fire ONE-TIME runtime warnings when sys or mic audio stays at silence thresholds.

    This is the second line of defense (after pre-flight) against silent-capture
    failures. Without this, a busted sys-tap or wrong-mic config runs invisibly for
    the full meeting — exactly the 2026-04-22 failure mode we're patching. Warnings
    print on their own line above the status indicator so the user sees them during
    the call (they're easy to miss in `\r` overwrites otherwise).

    Thresholds are conservative: we only warn if levels stay at silence for
    `_HEALTH_GRACE_SECONDS` — enough time for the EMA to settle past startup
    artifacts and for early meeting silence before someone speaks.
    """
    if elapsed < _HEALTH_GRACE_SECONDS:
        return
    if not gain_tracker.warmed_up:
        return

    if not warned.get("sys") and gain_tracker.sys_db < _HEALTH_SYS_SILENCE_DB:
        _play_alert_sound(repeat=2)
        print(
            f"\n  {_ANSI_RED}[WARNING]{_ANSI_RESET} System audio silent for {elapsed:.0f}s "
            f"(sys_db={gain_tracker.sys_db:.0f}). Meeting audio is NOT being captured.\n"
            f"           Likely causes: (1) Screen & System Audio Recording permission not granted "
            f"to this Python binary, (2) Bluetooth output device (try wired), "
            f"(3) pysysaudio failed silently — try `pip install --upgrade pysysaudio`."
        )
        warned["sys"] = True

    if has_mic and not warned.get("mic") and gain_tracker.mic_db < _HEALTH_MIC_SILENCE_DB:
        _play_alert_sound(repeat=2)
        print(
            f"\n  {_ANSI_RED}[WARNING]{_ANSI_RESET} Mic at noise floor for {elapsed:.0f}s "
            f"(mic_db={gain_tracker.mic_db:.0f}). Your voice is likely NOT being captured.\n"
            f"           Likely causes: (1) Wrong mic device (set --mic-device explicitly), "
            f"(2) Mic input volume <100% (System Settings → Sound → Input), "
            f"(3) Meeting app exclusively holding your headset mic (AirPods/Zoom/Meet) — "
            f"use a separate mic or switch to laptop built-in."
        )
        warned["mic"] = True


def _post_recording_sanity_check(
    gain_tracker: "_MicGainTracker",
    has_mic: bool,
    total_frames: int,
) -> None:
    """Print a loud, unmissable error summary if the recording captured silence.

    Last line of defense. If neither pre-flight nor runtime warnings caught the
    issue (e.g., levels hovered just above thresholds), this runs after stop_recording
    and tells the user their recording is likely useless BEFORE 20+ minutes of
    transcription runs on junk audio.
    """
    if not gain_tracker.warmed_up:
        return
    problems: list[str] = []
    if gain_tracker.sys_db < _HEALTH_SYS_SILENCE_DB:
        problems.append(f"system audio silent (sys_db={gain_tracker.sys_db:.0f} — expected >-60 during speech)")
    if has_mic and gain_tracker.mic_db < _HEALTH_MIC_SILENCE_DB:
        problems.append(f"mic at noise floor (mic_db={gain_tracker.mic_db:.0f} — expected >-50 during speech)")
    if not problems:
        return
    _play_alert_sound(repeat=3)
    print(f"\n{_ANSI_RED}━━━ CAPTURE FAILURE DETECTED ━━━{_ANSI_RESET}")
    for p in problems:
        print(f"  • {p}")
    print(
        f"  Transcription will run but will likely produce empty or useless output.\n"
        f"  {_ANSI_YELLOW}Recommendation:{_ANSI_RESET} skip transcription (Ctrl+C now), fix the setup per the "
        f"warnings above, and re-record.\n"
        f"{_ANSI_RED}━━━{_ANSI_RESET}"
    )


def record_audio(
    output_path: Path,
    device_name: str | None,
    mic_device_name: str | None,
    silence_timeout: int,
) -> tuple[float, dict | None]:
    """Record audio to WAV. Returns (duration_seconds, mic_gain_stats_or_None).

    Default (device_name is None): captures system audio via pysysaudio (Core Audio tap).
    Legacy (device_name specified): captures from a named device via sounddevice.
    In both modes, mic_device_name adds microphone input mixed in real-time with
    dynamic RMS-based gain matching.
    """
    if device_name:
        return _record_sounddevice(output_path, device_name, mic_device_name, silence_timeout)
    return _record_system_tap(output_path, mic_device_name, silence_timeout)


def _record_system_tap(
    output_path: Path,
    mic_device_name: str | None,
    silence_timeout: int,
) -> tuple[float, dict | None]:
    """Capture system audio via pysysaudio (Core Audio tap), optionally mixing with mic.

    Resilience: streams audio to disk via sf.SoundFile (crash-safe), uses callback-based
    mic capture (non-blocking — immune to device disconnection hangs), and degrades
    gracefully if the mic device disappears mid-recording.
    """
    from pysysaudio import SystemAudioRecorder

    if not SystemAudioRecorder.check_permission():
        raise SystemExit(
            "Screen & System Audio Recording permission not granted.\n"
            "Go to System Settings → Privacy & Security → Screen & System Audio Recording\n"
            "and enable permission for your Python interpreter or terminal app.\n"
            "Fallback: install a virtual audio device and use --device to capture via sounddevice instead."
        )

    chunks_silent = 0
    chunks_per_second = 1000 // CHUNK_MS
    silence_chunks = silence_timeout * chunks_per_second
    stopped = False

    def signal_handler(*_):
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGINT, signal_handler)

    # Mic uses callback mode + queue so the main loop never blocks on PortAudio.
    # If the mic device disappears (e.g. headphones disconnected), the callback
    # stops firing but the main loop continues with system audio only.
    # Transient PortAudio errors (common after device state changes or AUHAL
    # errors in prior sessions) are tolerated — only consecutive errors past
    # the threshold kill the mic stream.
    mic_q: queue.Queue | None = None
    mic_stream = None
    mic_error_count = 0
    MIC_ERROR_THRESHOLD = 50  # ~5s of consecutive errors at 10 chunks/sec

    if mic_device_name:
        import sounddevice as sd
        mic_id = _get_device_index(mic_device_name)
        mic_q = queue.Queue(maxsize=1000)

        def _mic_cb(indata, _frames, _time_info, status):
            nonlocal mic_error_count
            if status and not (status.input_overflow or status.input_underflow):
                mic_error_count += 1
                if mic_error_count >= MIC_ERROR_THRESHOLD:
                    return
            else:
                mic_error_count = 0
            try:
                mic_q.put_nowait(indata.copy().flatten())
            except queue.Full:
                pass

        mic_stream = sd.InputStream(
            device=mic_id, samplerate=SAMPLE_RATE, channels=1,
            dtype="float32", callback=_mic_cb,
            blocksize=SAMPLE_RATE * CHUNK_MS // 1000,
        )

    recorder = SystemAudioRecorder(sample_rate=SAMPLE_RATE, channels=1, format="numpy", dtype="float32")

    gain_tracker = _MicGainTracker()
    total_frames = 0
    last_flush = 0.0
    mic_lost_logged = False
    mic_empty_since: float | None = None
    mic_chunks_mixed = 0
    health_warned: dict[str, bool] = {}

    _preflight_audio_summary(mic_device_name, using_system_tap=True)
    print(f"Recording (system audio tap)... (Ctrl+Shift+S or Ctrl+C to stop; silence auto-stop at {silence_timeout}s)")
    start = datetime.now()

    wav_out = sf.SoundFile(str(output_path), mode="w", samplerate=SAMPLE_RATE, channels=1, subtype="FLOAT")
    try:
        recorder.start_recording()
        if mic_stream:
            mic_stream.start()

        for sys_chunk in recorder.stream(timeout=0.1):
            if stopped:
                break
            chunk = sys_chunk.flatten().astype(np.float32)
            if not len(chunk):
                continue

            elapsed = (datetime.now() - start).total_seconds()
            mic_failed = mic_error_count >= MIC_ERROR_THRESHOLD
            if mic_q is not None and not mic_failed:
                mic_data = _drain_audio_queue(mic_q, len(chunk))
                if mic_data is not None:
                    mic_empty_since = None
                    mic_chunks_mixed += 1
                    chunk = gain_tracker.update_and_mix(chunk, mic_data)
                else:
                    gain_tracker.update_sys_only(chunk)
                    if mic_empty_since is None:
                        mic_empty_since = elapsed
                    elif elapsed - mic_empty_since > 3.0 and not mic_lost_logged:
                        print(f"\n  [WARNING: no mic data for {elapsed - mic_empty_since:.0f}s — mic may not be working]")
                        mic_lost_logged = True
            elif mic_q is not None and mic_failed and not mic_lost_logged:
                gain_tracker.update_sys_only(chunk)
                print(f"\n  [WARNING: mic failed ({mic_error_count} consecutive PortAudio errors) — continuing with system audio only]")
                mic_lost_logged = True
            else:
                gain_tracker.update_sys_only(chunk)

            wav_out.write(chunk)
            total_frames += len(chunk)

            chunks_silent, should_stop = _silence_check(chunk, chunks_silent, silence_chunks)
            if should_stop:
                print("\nSilence timeout reached.")
                break

            mic_indicator = ""
            if mic_device_name:
                if mic_lost_logged:
                    mic_indicator = " [MIC LOST]"
                elif mic_chunks_mixed == 0 and elapsed > 5:
                    mic_indicator = " [mic: waiting]"
                else:
                    mic_indicator = f" {gain_tracker.status_str()}"
            print(f"\r  {elapsed:.0f}s{mic_indicator}  ", end="", flush=True)

            _check_runtime_health(gain_tracker, elapsed, health_warned, has_mic=bool(mic_device_name))

            if elapsed - last_flush >= 30:
                wav_out.flush()
                last_flush = elapsed
    except Exception as e:
        print(f"\n  [Recording error: {e} — saving {total_frames / SAMPLE_RATE:.0f}s of captured audio]")
    finally:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        wav_out.close()
        try:
            recorder.stop_recording()
        except Exception:
            pass
        if mic_stream:
            try:
                mic_stream.stop()
                mic_stream.close()
            except Exception:
                pass

    if gain_tracker.warmed_up:
        print(f"\n  Gain stats: {gain_tracker.status_str()}")
    _post_recording_sanity_check(gain_tracker, has_mic=bool(mic_device_name), total_frames=total_frames)

    if total_frames == 0:
        raise SystemExit("No audio captured. Recording stopped before any data was received.")
    return total_frames / SAMPLE_RATE, gain_tracker.summary()


def _record_sounddevice(
    output_path: Path,
    device_name: str,
    mic_device_name: str | None,
    silence_timeout: int,
) -> tuple[float, dict | None]:
    """Legacy path: capture from a named audio device via sounddevice (e.g., ZoomAudioDevice).

    Uses callback-based streams (non-blocking) and streams audio to disk for crash safety.
    """
    import sounddevice as sd

    device_id = _get_device_index(device_name)
    chunks_silent = 0
    chunks_per_second = 1000 // CHUNK_MS
    silence_chunks = silence_timeout * chunks_per_second
    chunk_frames = SAMPLE_RATE * CHUNK_MS // 1000
    stopped = False
    main_error_count = 0
    MAIN_ERROR_THRESHOLD = 50

    def signal_handler(*_):
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGINT, signal_handler)

    main_q: queue.Queue = queue.Queue(maxsize=1000)

    def _main_cb(indata, _frames, _time_info, status):
        nonlocal main_error_count
        if status and not (status.input_overflow or status.input_underflow):
            main_error_count += 1
            if main_error_count >= MAIN_ERROR_THRESHOLD:
                return
        else:
            main_error_count = 0
        try:
            main_q.put_nowait(indata.copy().flatten())
        except queue.Full:
            pass

    main_stream = sd.InputStream(
        device=device_id, samplerate=SAMPLE_RATE, channels=1,
        dtype="float32", callback=_main_cb,
        blocksize=chunk_frames,
    )

    mic_q: queue.Queue | None = None
    mic_stream = None
    mic_error_count = 0
    MIC_ERROR_THRESHOLD = 50

    if mic_device_name:
        mic_id = _get_device_index(mic_device_name)
        mic_q = queue.Queue(maxsize=1000)

        def _mic_cb(indata, _frames, _time_info, status):
            nonlocal mic_error_count
            if status and not (status.input_overflow or status.input_underflow):
                mic_error_count += 1
                if mic_error_count >= MIC_ERROR_THRESHOLD:
                    return
            else:
                mic_error_count = 0
            try:
                mic_q.put_nowait(indata.copy().flatten())
            except queue.Full:
                pass

        mic_stream = sd.InputStream(
            device=mic_id, samplerate=SAMPLE_RATE, channels=1,
            dtype="float32", callback=_mic_cb,
            blocksize=chunk_frames,
        )

    gain_tracker = _MicGainTracker()
    total_frames = 0
    last_flush = 0.0
    mic_lost_logged = False
    mic_empty_since: float | None = None
    mic_chunks_mixed = 0
    health_warned: dict[str, bool] = {}

    _preflight_audio_summary(mic_device_name, using_system_tap=False)
    print(f"Recording via {device_name}... (Ctrl+Shift+S or Ctrl+C to stop; silence auto-stop at {silence_timeout}s)")
    start = datetime.now()

    wav_out = sf.SoundFile(str(output_path), mode="w", samplerate=SAMPLE_RATE, channels=1, subtype="FLOAT")
    try:
        main_stream.start()
        if mic_stream:
            mic_stream.start()

        while not stopped and main_error_count < MAIN_ERROR_THRESHOLD:
            try:
                chunk = main_q.get(timeout=0.1)
            except queue.Empty:
                continue

            elapsed = (datetime.now() - start).total_seconds()
            mic_failed = mic_error_count >= MIC_ERROR_THRESHOLD
            if mic_q is not None and not mic_failed:
                mic_data = _drain_audio_queue(mic_q, len(chunk))
                if mic_data is not None:
                    mic_empty_since = None
                    mic_chunks_mixed += 1
                    chunk = gain_tracker.update_and_mix(chunk, mic_data)
                else:
                    gain_tracker.update_sys_only(chunk)
                    if mic_empty_since is None:
                        mic_empty_since = elapsed
                    elif elapsed - mic_empty_since > 3.0 and not mic_lost_logged:
                        print(f"\n  [WARNING: no mic data for {elapsed - mic_empty_since:.0f}s — mic may not be working]")
                        mic_lost_logged = True
            elif mic_q is not None and mic_failed and not mic_lost_logged:
                gain_tracker.update_sys_only(chunk)
                print(f"\n  [WARNING: mic failed ({mic_error_count} consecutive PortAudio errors) — continuing with main device only]")
                mic_lost_logged = True
            else:
                gain_tracker.update_sys_only(chunk)

            wav_out.write(chunk)
            total_frames += len(chunk)

            chunks_silent, should_stop = _silence_check(chunk, chunks_silent, silence_chunks)
            if should_stop:
                print("\nSilence timeout reached.")
                break

            mic_indicator = ""
            if mic_device_name:
                if mic_lost_logged:
                    mic_indicator = " [MIC LOST]"
                elif mic_chunks_mixed == 0 and elapsed > 5:
                    mic_indicator = " [mic: waiting]"
                else:
                    mic_indicator = f" {gain_tracker.status_str()}"
            print(f"\r  {elapsed:.0f}s{mic_indicator}  ", end="", flush=True)

            _check_runtime_health(gain_tracker, elapsed, health_warned, has_mic=bool(mic_device_name))

            if elapsed - last_flush >= 30:
                wav_out.flush()
                last_flush = elapsed

        if main_error_count >= MAIN_ERROR_THRESHOLD:
            print(f"\n  [main audio device failed ({main_error_count} consecutive errors) — saving {total_frames / SAMPLE_RATE:.0f}s of captured audio]")
    except Exception as e:
        print(f"\n  [Recording error: {e} — saving {total_frames / SAMPLE_RATE:.0f}s of captured audio]")
    finally:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        wav_out.close()
        try:
            main_stream.stop()
            main_stream.close()
        except Exception:
            pass
        if mic_stream:
            try:
                mic_stream.stop()
                mic_stream.close()
            except Exception:
                pass

    if gain_tracker.warmed_up:
        print(f"\n  Gain stats: {gain_tracker.status_str()}")
    _post_recording_sanity_check(gain_tracker, has_mic=bool(mic_device_name), total_frames=total_frames)

    if total_frames == 0:
        raise SystemExit("No audio captured. Recording stopped before any data was received.")
    return total_frames / SAMPLE_RATE, gain_tracker.summary()


def transcribe_file(
    wav_path: Path,
    model_name: str,
    language: str,
    initial_prompt: str | None,
    condition_on_previous: bool,
    diarize: bool,
    min_speakers: int | None,
    max_speakers: int | None,
    hf_token: str | None,
) -> tuple[dict, int]:
    import torch
    import whisperx

    if diarize and not hf_token:
        raise SystemExit("Diarization requires HF_TOKEN. Set it or pass --hf-token.")

    asr_device = "cpu"
    diarize_device = "mps" if torch.backends.mps.is_available() else "cpu"

    print("Loading model...")
    asr_options = {
        "initial_prompt": initial_prompt,
        "condition_on_previous_text": condition_on_previous,
    }
    model = whisperx.load_model(
        model_name,
        device=asr_device,
        compute_type="int8",
        asr_options=asr_options,
        vad_options={"vad_onset": 0.2, "vad_offset": 0.15},
    )

    print("Transcribing...")
    audio = whisperx.load_audio(str(wav_path))
    result = model.transcribe(audio, batch_size=16)
    del model
    gc.collect()

    if not result.get("segments"):
        print("\n⚠️  WARNING: No speech segments detected — VAD found no active speech in the audio.")
        print("   Possible causes: mic not capturing, meeting audio not routed, or audio below VAD threshold.")
        return {"segments": []}, 0

    print("Aligning...")
    align_model, align_metadata = whisperx.load_align_model(
        language_code=language or result.get("language", "en"),
        device=asr_device,
    )
    result = whisperx.align(result["segments"], align_model, align_metadata, audio, asr_device)
    del align_model
    gc.collect()

    num_speakers = 0
    if diarize:
        print("Diarizing...")
        from whisperx.diarize import DiarizationPipeline, assign_word_speakers
        try:
            diarize_model = DiarizationPipeline(use_auth_token=hf_token, device=diarize_device)
        except TypeError:
            diarize_model = DiarizationPipeline(token=hf_token, device=diarize_device)
        diarize_kwargs = {k: v for k, v in (("min_speakers", min_speakers), ("max_speakers", max_speakers)) if v is not None}
        diarize_segments = diarize_model(str(wav_path), **diarize_kwargs)
        result = assign_word_speakers(diarize_segments, result)
        speakers = {seg.get("speaker") for seg in result["segments"] if seg.get("speaker")}
        num_speakers = len(speakers)

        # Per-speaker voiceprints (averaged pyannote embeddings) for cross-meeting matching.
        # Best-effort: failures here do not abort transcription. Output stored on
        # result["speaker_embeddings"] = { "SPEAKER_00": [floats], ... } and consumed by
        # the speaker-mapping skill's Pass 0.
        try:
            from pyannote.audio import Inference, Model
            from pyannote.core import Segment
            import numpy as np
            print("Extracting speaker voiceprints...")
            embedding_model = Model.from_pretrained("pyannote/embedding", use_auth_token=hf_token)
            inference = Inference(embedding_model, window="whole", device=diarize_device)
            speaker_segments: dict[str, list[tuple[float, float]]] = {}
            for seg in result["segments"]:
                spk = seg.get("speaker")
                if not spk:
                    continue
                speaker_segments.setdefault(spk, []).append((float(seg["start"]), float(seg["end"])))
            speaker_embeddings: dict[str, list[float]] = {}
            for spk, spans in speaker_segments.items():
                vecs = []
                weights = []
                for start, end in spans:
                    if end - start < 0.5:  # skip very short crops — embeddings unreliable
                        continue
                    try:
                        emb = inference.crop(str(wav_path), Segment(start, end))
                        vecs.append(np.asarray(emb).flatten())
                        weights.append(end - start)
                    except Exception:
                        continue
                if vecs:
                    arr = np.stack(vecs, axis=0)
                    w = np.asarray(weights, dtype=arr.dtype)
                    w = w / w.sum()
                    avg = (arr * w[:, None]).sum(axis=0)
                    # L2-normalize so cosine similarity == dot product downstream
                    norm = np.linalg.norm(avg)
                    if norm > 0:
                        avg = avg / norm
                    speaker_embeddings[spk] = avg.tolist()
            if speaker_embeddings:
                result["speaker_embeddings"] = speaker_embeddings
                result["speaker_embedding_model"] = "pyannote/embedding"
                print(f"  Captured voiceprints for {len(speaker_embeddings)} speaker(s).")
            else:
                print("  No voiceprints captured (segments too short or extraction failed).")
            del embedding_model, inference
            gc.collect()
        except Exception as e:
            print(f"  ⚠️  Voice embedding extraction skipped: {e}")

    return result, num_speakers


def build_output_schema(result: dict, metadata: dict) -> dict:
    segments = []
    for seg in result.get("segments", []):
        words = seg.get("words") or []
        segment_out = {
            "start": seg["start"],
            "end": seg["end"],
            "text": seg.get("text", "").strip(),
            "speaker": seg.get("speaker") or "SPEAKER_00",
            "words": [
                {"word": w.get("word", ""), "start": w.get("start", 0.0), "end": w.get("end", 0.0)}
                for w in words if "word" in w
            ],
        }
        segments.append(segment_out)

    output = {"segments": segments, "metadata": metadata}
    if "speaker_embeddings" in result:
        output["speaker_embeddings"] = result["speaker_embeddings"]
        output["speaker_embedding_model"] = result.get("speaker_embedding_model", "pyannote/embedding")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Record and transcribe meetings locally.")
    rec = parser.add_argument_group("Recording options")
    rec.add_argument("--mic", action="store_true", help="Include microphone input (default: system audio only)")
    rec.add_argument("--device", default=None, help="Audio input device for legacy sounddevice capture (default: None — uses native system audio tap). Pass a device name like 'ZoomAudioDevice' to use sounddevice instead.")
    rec.add_argument(
        "--mic-device",
        help=(
            "Microphone device when using --mic. Precedence: this flag > $MEETING_MIC_DEVICE env var > "
            f"built-in laptop mic ({', '.join(BUILTIN_MIC_CANDIDATES)}) > macOS system default."
        ),
    )
    rec.add_argument("--silence-timeout", type=int, default=600, help="Auto-stop after N seconds of silence (default: 600)")
    trans = parser.add_argument_group("Transcription options")
    trans.add_argument("--model", default="large-v3-turbo", help="Whisper model (default: large-v3-turbo)")
    trans.add_argument("--language", default="en", help="Language code (default: en)")
    trans.add_argument("--initial-prompt", default=DEFAULT_DOMAIN_PROMPT, help="Domain vocabulary prompt for Whisper")
    trans.add_argument("--no-condition-previous", action="store_true", help="Disable conditioning on previous text")
    diar = parser.add_argument_group("Diarization options")
    diar.add_argument("--diarize", action=argparse.BooleanOptionalAction, default=True, help="Enable speaker diarization (default: on)")
    diar.add_argument("--min-speakers", type=int, help="Minimum expected speakers")
    diar.add_argument("--max-speakers", type=int, help="Maximum expected speakers")
    diar.add_argument("--hf-token", help="HuggingFace token (default: $HF_TOKEN env var)")
    out = parser.add_argument_group("Output options")
    out.add_argument("--output-dir", help="Override output directory for both WAV and JSON (bypasses split-dir default)")
    out.add_argument("--keep-audio", action="store_true", help="Keep WAV file after transcription")
    trans_only = parser.add_argument_group("Transcription-only mode")
    trans_only.add_argument("--file", type=Path, help="Transcribe existing audio file instead of recording")

    args = parser.parse_args()
    hf_token = args.hf_token or os.environ.get("HF_TOKEN")
    if args.min_speakers is not None and args.max_speakers is not None:
        if args.min_speakers > args.max_speakers:
            raise SystemExit(f"--min-speakers ({args.min_speakers}) cannot exceed --max-speakers ({args.max_speakers}).")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    if args.file:
        wav_path = args.file.resolve()
        if not wav_path.exists():
            raise SystemExit(f"File not found: {wav_path}")
        if args.output_dir:
            json_output_dir = Path(args.output_dir).expanduser().resolve()
        else:
            json_output_dir = _WORKSPACE_ROOT / "Meeting Transcripts" / timestamp
        json_output_dir.mkdir(parents=True, exist_ok=True)
        # Convert non-WAV files (mp4, m4a, mp3, etc.) to WAV via ffmpeg
        if wav_path.suffix.lower() not in ('.wav', '.wave'):
            converted_path = json_output_dir / "recording.wav"
            print(f"Converting {wav_path.name} to WAV via ffmpeg...")
            import subprocess as _sp
            result = _sp.run(
                ["ffmpeg", "-i", str(wav_path), "-ac", "1", "-ar", "16000", "-y", str(converted_path)],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                raise SystemExit(f"ffmpeg conversion failed:\n{result.stderr}")
            print(f"  Converted → {converted_path}")
            wav_path = converted_path
        info = sf.info(str(wav_path))
        duration = info.frames / info.samplerate
        mic_gain_stats = None
    else:
        _write_pid_file()
        atexit.register(_remove_pid_file)

        if args.output_dir:
            wav_staging_dir = Path(args.output_dir).expanduser().resolve()
            json_output_dir = wav_staging_dir
        else:
            wav_staging_dir = Path(f"~/meetings/{timestamp}").expanduser().resolve()
            json_output_dir = _WORKSPACE_ROOT / "Meeting Transcripts" / timestamp
        wav_staging_dir.mkdir(parents=True, exist_ok=True)
        json_output_dir.mkdir(parents=True, exist_ok=True)
        wav_path = wav_staging_dir / "recording.wav"
        mic_device = _resolve_mic_device(args.mic_device) if args.mic else None
        duration, mic_gain_stats = record_audio(wav_path, args.device, mic_device, args.silence_timeout)

    transcription_wav = _check_and_normalize_audio(wav_path)
    audio_normalized = transcription_wav != wav_path

    result, num_speakers = transcribe_file(
        transcription_wav,
        args.model,
        args.language,
        args.initial_prompt or None,
        not args.no_condition_previous,
        args.diarize,
        args.min_speakers,
        args.max_speakers,
        hf_token,
    )

    if audio_normalized:
        transcription_wav.unlink(missing_ok=True)

    capture_method = args.device or "system_audio_tap"
    metadata = {
        "model": args.model,
        "language": args.language,
        "duration_seconds": duration,
        "num_speakers": num_speakers,
        "initial_prompt": args.initial_prompt or None,
        "recorded_at": datetime.strptime(timestamp, "%Y-%m-%d_%H%M%S").isoformat(),
        "capture_method": capture_method,
        "audio_normalized": audio_normalized,
        "mic_gain": mic_gain_stats,
    }
    output = build_output_schema(result, metadata)

    json_path = json_output_dir / "recording.json"
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)

    no_speech = not output.get("segments")
    if not args.keep_audio and not args.file:
        if no_speech:
            print(f"\n⚠️  WAV auto-retained (transcription produced 0 segments): {wav_path}")
            print(f"   To re-process: record-meeting --file \"{wav_path}\" --diarize")
        else:
            wav_path.unlink()
            try:
                wav_path.parent.rmdir()
            except OSError:
                pass

    if no_speech:
        print(f"\n⚠️  FAILED: No speech detected in {duration:.1f}s of audio. WAV kept for debugging/re-processing.")
        print(f"   Output (empty): {json_path}")
    else:
        print(f"\nDone. Duration: {duration:.1f}s, speakers: {num_speakers}, output: {json_path}")


if __name__ == "__main__":
    main()
