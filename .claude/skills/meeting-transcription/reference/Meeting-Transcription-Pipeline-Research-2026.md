# Meeting Transcription Pipeline: Component Research & Recommendations (2026)

**Research date:** March 2026
**Use case:** Personal meeting transcription on macOS Apple Silicon. Business meetings (3–8 participants) via Zoom/Meet/Teams. Company banned third-party AI note-taking tools (Otter, Fireflies, Gong) due to legal discovery risk. Privacy-first; local preferred, transient API acceptable.

---

## TL;DR — Recommended Pipeline

| Step | Component | Recommendation | Why |
|------|-----------|---------------|-----|
| 1 | **Audio Capture** | **ownscribe** (Core Audio Taps) or **OBS Studio 30+** (ScreenCaptureKit) | No virtual audio drivers needed on macOS 14.2+. ownscribe is end-to-end; OBS is capture-only for custom pipelines. |
| 2 | **Local Recording** | **SoX** (file-based) or **Python sounddevice** (real-time streaming) | SoX is artifact-free with BlackHole; sounddevice enables real-time chunk streaming into the transcription engine. |
| 3 | **Transcription** | **mlx-whisper with large-v3-turbo** (local) | Native Apple Silicon MLX optimization; faster than real-time on M1+; ~95% accuracy; 100% on-device. |
| 4 | **Speaker Diarization** | **WhisperX** (local, pyannote-based) or **AssemblyAI API** (best accuracy) | WhisperX: fully local, word-level output, DER ~11–19%. AssemblyAI: 3.1% DER if transient API is acceptable. |
| 5 | **Speaker Mapping** | **LLM-assisted mapping + Calendar attendee list** | Zero enrollment, no biometrics, 70–90% accuracy. Calendar roster constrains the mapping problem. |

**Key finding vs. original document:** The original recommended BlackHole + Deepgram API. This research found that **Core Audio Taps (macOS 14.2+) eliminates the need for virtual audio drivers entirely**, and **mlx-whisper provides cloud-competitive transcription fully on-device** on Apple Silicon. The biggest tradeoff remains diarization: local (WhisperX) is adequate for most meetings but APIs remain ~2–3x more accurate.

---

## 1. Audio Capture

### Recommendation: ownscribe or OBS Studio 30+

The original document recommended **BlackHole** (free virtual audio driver) or **Loopback** ($99). Both still work, but macOS 14.2+ introduced **Core Audio Taps**, which captures system audio without any virtual audio driver. This changes the recommendation.

### Comparison

| Option | Cost | Both Sides | Setup | macOS Sequoia/AS | Privacy | Key Insight |
|--------|------|------------|-------|------------------|---------|-------------|
| **ownscribe** | Free (MIT) | Yes (`--mic`) | Low | Yes | 100% local | End-to-end pipeline: capture → transcribe → diarize → summarize. Uses Core Audio Taps — no drivers. |
| **OBS Studio 30+** | Free | Yes (multi-source) | Medium | Yes | 100% local | Native ScreenCaptureKit audio capture (macOS 13+). Capture-only — feed WAV into your pipeline. |
| **BlackHole** | Free (MIT) | Yes (Multi-Output + Aggregate) | Medium–High | ⚠️ Sequoia glitches | 100% local | Proven but requires Multi-Output Device setup. Some audio glitches reported on Sequoia. |
| **Loopback** | $99 | Yes (built-in mixing) | Low | Yes (ARK plugin) | 100% local | Most polished setup. Per-app capture. Worth it if you want zero config friction. |
| **Sound Siphon** | $49 | Yes | Low | Yes | 100% local | Per-app capture with built-in recording. Subscription on App Store. |
| **Core Audio Taps (DIY)** | Free | Yes | High (Swift/ObjC) | Yes (14.2+) | 100% local | Apple API; ownscribe is a ready-made wrapper. |

### What Does NOT Work

- **macOS built-in screen recording (Cmd+Shift+5) and QuickTime** — Cannot capture system audio due to Apple's privacy design.
- **Soundflower** — Deprecated. BlackHole is the modern replacement.

### Verdict

- **Ready-made pipeline:** `uvx ownscribe --mic` — captures both sides, transcribes, diarizes, summarizes. All local.
- **Custom pipeline:** OBS 30+ for capture → feed WAV into your transcription stack.
- **Fallback:** BlackHole (if you need virtual routing flexibility) or Loopback (if willing to pay $99 for simpler setup).

---

## 2. Local Recording

### Recommendation: SoX (file-based) or Python sounddevice (real-time)

The original document suggested QuickTime / sox / ffmpeg. Research confirms **SoX is the most reliable CLI option** — ffmpeg has known crackling issues with BlackHole, and QuickTime requires an export step. The real finding: **Python sounddevice enables real-time streaming** into the transcription engine, eliminating "record then transcribe" latency.

### Comparison

| Option | Format | Scriptable | BlackHole | Real-time Stream | Pipeline Integration | Notes |
|--------|--------|------------|-----------|------------------|---------------------|-------|
| **SoX** | WAV, FLAC | CLI, subprocess | ✅ No artifacts | ❌ File only | ✅ subprocess | `sox -t coreaudio "BlackHole 2ch" output.wav` — reliable, clean. |
| **Python sounddevice** | NumPy → WAV | Native Python | ✅ | ✅ Chunk streaming | ✅ Excellent | `InputStream` callback feeds chunks to Whisper in real time. |
| **FFmpeg** | WAV, many | CLI | ⚠️ Crackling reported | ❌ | ✅ | **Avoid for BlackHole recording.** Use for post-processing (format conversion). |
| **QuickTime + AppleScript** | m4a → WAV | osascript | ✅ | ❌ | ⚠️ Export step | Built-in, no install. Requires format conversion for transcription. |
| **Audio Hijack** | WAV, many | JS API | ✅ | ❌ | ⚠️ External app | Professional, $64. Overkill for this pipeline. |
| **audio-rec** | WAV | CLI | N/A (process tap) | ❌ | ✅ | Per-process capture (macOS 14.4+). Different model than system loopback. |

### Verdict

- **File-based (simplest):** SoX — `brew install sox`, one-line recording command, no quality issues with BlackHole.
- **Real-time streaming (lowest latency):** Python sounddevice — `InputStream` callback streams audio chunks directly into local Whisper/faster-whisper.
- **Avoid:** FFmpeg for recording from BlackHole (crackling). Use FFmpeg only for post-processing.

### If Using ownscribe or OBS

Recording is handled by the capture tool itself — this component becomes unnecessary as a separate step. SoX/sounddevice are relevant only if building a fully custom pipeline from individual components.

---

## 3. Transcription (Speech-to-Text)

### Recommendation: mlx-whisper with large-v3-turbo (local)

The original document suggested Whisper.cpp / faster-whisper (local) or Deepgram / AssemblyAI (API). The key finding: **mlx-whisper is purpose-built for Apple Silicon** and delivers 30–40% faster inference than whisper.cpp with equivalent accuracy. It's the clear local winner for M-series Macs.

### Comparison

| Option | Type | WER (English) | Speed on Apple Silicon | Privacy | Cost | Diarization | Setup |
|--------|------|---------------|----------------------|---------|------|-------------|-------|
| **mlx-whisper turbo** | Local | 2.7–7.4% | Faster than real-time (★★★★★) | 100% local | Free | No (add WhisperX) | `uv tool install mlx-whisper` |
| **faster-whisper turbo** | Local | ~2–6% | Fast (★★★★) | 100% local | Free | No (add WhisperX) | `pip install faster-whisper` |
| **whisper.cpp turbo** | Local | ~2.7–6% | Fast w/ CoreML (★★★★) | 100% local | Free | No | Build from source |
| **WhisperX** | Local | Same as Whisper | ~70x real-time (★★★★) | 100% local | Free | Yes (pyannote) | HuggingFace token |
| **Deepgram Nova-3** | API | 4.3–5.8% | Real-time | Transient | $0.17/hr | Yes | API key |
| **AssemblyAI U3** | API | 4.5–6% | Real-time | 3-day default | $0.08/hr base | Yes (3.1% DER) | API key |
| **Distil-Whisper** | Local | Within 1% of Whisper | 6x faster | 100% local | Free | No | pip install |
| **NVIDIA Canary** | Local | 5.63% (best) | N/A — requires NVIDIA GPU | Local | Free | No | **Not viable on macOS** |
| **Google Chirp2** | API | 11.6–12.5% | Variable | Transient | $0.53/hr | Yes | GCP project |
| **Vosk / Coqui STT** | Local | 52–79% | Fast | Local | Free | No | **Not competitive** |

### Technical Vocabulary Handling

For pharmacy, fulfillment, and software terminology:

| Method | Approach | Limitation |
|--------|----------|------------|
| **mlx-whisper / Whisper (local)** | 224-token initial prompt with domain terms (e.g., "PV2, beyondRx, HighJump, USP, DEA") | Effect strongest in first ~30s of each segment |
| **Deepgram** | Keyterm Prompting (100 terms) — best for custom vocab | Nova-3 only |
| **AssemblyAI** | Entity recognition | General, not domain-specific |
| **AWS Transcribe** | Custom medical vocabulary (up to 50KB) | Per-account limits |

### Verdict

- **Default:** mlx-whisper large-v3-turbo — fastest on Apple Silicon, fully local, strong accuracy.
- **With diarization:** WhisperX (uses faster-whisper backend + pyannote for speaker labels).
- **Cloud fallback (if local accuracy insufficient):** Deepgram Nova-3 with Keyterm Prompting for technical terms.
- **Known gotcha:** Use `--condition-on-previous-text False` to avoid Whisper's repetition loop bug.

### Quick Start

```bash
uv tool install mlx-whisper

mlx_whisper \
  --model mlx-community/whisper-large-v3-turbo \
  --language en \
  --condition-on-previous-text False \
  --output-format srt \
  meeting.wav
```

---

## 4. Speaker Diarization

### Recommendation: WhisperX (local) or AssemblyAI (API)

The original document recommended WhisperX (pyannote-based) for local and Deepgram for API. Research confirms **diarization is still the hardest part of the pipeline in 2026**, but the gap has narrowed. Key finding: **AssemblyAI has overtaken Deepgram** in diarization accuracy (3.1% vs. 4.8% DER).

### Comparison

| Solution | Type | DER | Speaker Count | Overlap | Apple Silicon | Privacy | Cost | Word-Level |
|----------|------|-----|---------------|---------|---------------|---------|------|------------|
| **AssemblyAI** | API | ~3.1% | Auto-detect | Good | N/A | Delete after use | ~$0.24/hr | Yes |
| **Deepgram** | API | ~4.8% | Auto-detect | Strong (best overlap) | N/A | SOC 2/HIPAA | ~$0.18/hr | Yes |
| **WhisperX** | Local | 11–19% | Auto (≤7–8) | Reasonable | MPS support | 100% local | Free | Yes |
| **pyannote 3.1** | Local | 11–19% | Auto (≤7–8) | Dedicated overlap model | MPS support | 100% local | Free | Segment only |
| **Picovoice Falcon** | Local | Not published | Unlimited | Not detailed | Native macOS | 100% local | Free (AccessKey) | No |
| **speech-swift** | Local | Not benchmarked | ≤3 concurrent | Limited | Native MLX | 100% local | Free | TBD |
| **NeMo MSDD** | Local | ~8.1% | 4–14 tested | Best (40% overlap) | **Not viable** (needs NVIDIA) | Local | Free | No |

### The Accuracy Gap (2026)

- **Commercial APIs:** 3–5% DER (AssemblyAI, Deepgram)
- **Best local models:** 11–19% DER (pyannote/WhisperX)
- **Gap:** APIs are ~2–3x more accurate
- **In practice:** For clean meetings with 3–6 speakers, local is usually acceptable. For 6+ speakers or heavy crosstalk, APIs are safer.

### Voice Enrollment / Cross-Meeting Speaker ID

Not widely available in production tools yet. pyannoteAI's commercial platform supports voiceprints but requires paid plan. Most open-source tools (WhisperX, pyannote.audio) produce anonymous labels that aren't stable across meetings.

### Verdict

- **Privacy-first (fully local):** WhisperX — word-level speaker alignment, good enough for 3–8 speaker meetings.
- **Best accuracy (transient API OK):** AssemblyAI — lowest DER, delete audio after processing.
- **Heavy overlap/noisy meetings:** Deepgram — strongest overlap handling.
- **Watch list:** speech-swift (native Swift/MLX) — promising but limited to 3 concurrent speakers today.
- **Avoid on Mac:** NVIDIA NeMo — requires NVIDIA GPU.

---

## 5. Speaker Mapping

### Recommendation: LLM-Assisted Mapping + Calendar Attendee List

The original document suggested a simple config file for mapping SPEAKER_01 → names. Research found this is **unreliable for 3+ speakers** because speaker order is unstable. The pragmatic solution is **LLM-assisted inference** using context clues from the transcript + the attendee list as a constraint.

### Comparison

| Approach | Accuracy | Automation | Setup | Privacy | Scalability (20–30 people) |
|----------|----------|------------|-------|---------|---------------------------|
| **LLM + Calendar roster** | 70–90% | Semi-auto | Low | No biometrics | Excellent |
| **Google Meet Transcript API** | 95%+ | Fully auto | None (if enabled) | Platform-handled | N/A |
| **Voice enrollment (pyannote Precision-2)** | 80–95% | Fully auto (enrolled) | High (30s/person + maintenance) | **Biometric** (GDPR Art. 9) | Poor (enrollment fatigue) |
| **Zoom local recording (separate tracks)** | ~100% | Fully auto | Local recording required | Low | N/A |
| **Teams live transcription** | Variable | Semi-auto | Voice profile setup | Biometric | Org-dependent |
| **Manual post-meeting** | 100% | Manual | None | None | Poor (time cost) |
| **Simple config file (order-based)** | Unreliable | Manual | Low | None | **Avoid for 3+ speakers** |
| **Hybrid (voice + LLM fallback)** | 85–95% | Auto for enrolled, semi for others | High | Biometric for enrolled | Medium |

### Is Fully Automatic Voice ID Practical in 2026?

**Partially.** The tools exist (pyannote Precision-2, SpeechBrain, Resemblyzer), but for a PM with 20–30 regular meeting participants:

- **Enrollment fatigue** — 30s per person, ongoing maintenance for new joiners
- **Accuracy degrades** with typical meeting audio (VoIP codecs, room noise, reverberation)
- **Privacy overhead** — voice embeddings are biometric data under GDPR Art. 9; requires consent, encryption, deletion workflows

### Recommended Flow

| Step | Action |
|------|--------|
| 1 | Fetch meeting attendees via Google Calendar API |
| 2 | Run transcription + diarization (WhisperX or API) |
| 3 | Format: `SPEAKER_01: [utterance]... SPEAKER_02: [utterance]...` |
| 4 | Prompt LLM: "Map each speaker label to an attendee using context clues. Attendees: [list]. Return JSON." |
| 5 | Optional: Human review for high-stakes meetings |

### Verdict

- **Default:** LLM + calendar roster. Zero enrollment, no biometrics, works across platforms, 70–90% accuracy.
- **If Google Meet transcript is enabled:** Use the Meet Transcript API directly — named speakers with no mapping needed.
- **Stretch goal:** Add voice enrollment for a small core group (<10 people) to push accuracy above 90%.
- **Avoid:** Simple config file mapping — speaker order is unstable, fails for 3+ speakers.

---

## What Changed from the Original Analysis

| Component | Original Recommendation | Updated Recommendation | What Changed |
|-----------|------------------------|----------------------|-------------|
| **Audio Capture** | BlackHole / Loopback | **ownscribe** (Core Audio Taps) / OBS 30+ | macOS 14.2+ Core Audio Taps eliminates need for virtual audio drivers entirely |
| **Local Recording** | QuickTime / sox / ffmpeg | **SoX** (file) / **sounddevice** (streaming) | FFmpeg has crackling issues with BlackHole; sounddevice enables real-time streaming |
| **Transcription** | Whisper.cpp / faster-whisper / Deepgram | **mlx-whisper** large-v3-turbo | Purpose-built for Apple Silicon; 30–40% faster than whisper.cpp |
| **Diarization** | WhisperX / Deepgram | **WhisperX** (local) / **AssemblyAI** (API) | AssemblyAI surpassed Deepgram in DER accuracy (3.1% vs 4.8%) |
| **Speaker Mapping** | Simple config file | **LLM + Calendar roster** | Config-based mapping unreliable for 3+ speakers; LLM inference is more robust |

---

## Recommended Architecture: Two Options

### Option A: Fully Local (Privacy-First)

```
Meeting (Zoom/Meet/Teams)
    ↓ ownscribe (Core Audio Taps, --mic)
    OR: OBS 30+ → SoX/sounddevice → WAV file
Audio File (.wav)
    ↓ WhisperX (mlx/faster-whisper + pyannote)
Diarized Transcript (SPEAKER_01: "...", SPEAKER_02: "...")
    ↓ Calendar API → attendee list
    ↓ LLM prompt (local or API)
Named Transcript ([teammate]: "...", [Director of Pharmacy & Fulfillment Product]: "...")
    ↓ Synthesis agent
Structured Meeting Notes
    ↓ Auto-cleanup: delete raw audio + verbatim transcript
Only synthesized notes persist
```

**Pros:** Nothing leaves the machine (except optional LLM call). Minimal discovery risk.
**Cons:** Diarization accuracy ~11–19% DER. May struggle with 6+ speakers or heavy overlap.

### Option B: Local Capture + API Diarization (Best Accuracy)

```
Meeting (Zoom/Meet/Teams)
    ↓ ownscribe (Core Audio Taps, --mic) or OBS/SoX
Audio File (.wav)
    ↓ AssemblyAI API (transcription + diarization, delete after)
Diarized Transcript (Speaker A: "...", Speaker B: "...")
    ↓ Calendar API → attendee list
    ↓ LLM prompt
Named Transcript ([teammate]: "...", [Director of Pharmacy & Fulfillment Product]: "...")
    ↓ Synthesis agent
Structured Meeting Notes
    ↓ Auto-cleanup: delete raw audio + verbatim transcript
Only synthesized notes persist
```

**Pros:** Best diarization accuracy (~3.1% DER). Word-level speaker alignment.
**Cons:** Audio briefly sent to API. Configure delete-after-processing. Check enterprise data retention terms.

### Recommendation

Start with **Option A (fully local)** using ownscribe + WhisperX. If diarization accuracy is insufficient for your meetings (particularly if you regularly have 6+ speakers or heavy crosstalk), move to **Option B** with AssemblyAI.

This is a **Type 2 decision** — fully reversible. The downstream synthesis pipeline is identical regardless of which upstream components you use.

---

## Improving Speaker Mapping Accuracy

The baseline LLM + calendar roster approach achieves 70–90% accuracy. The following techniques stack additively to push accuracy toward 90–98% — all without biometric enrollment.

### Accuracy Improvement Layers

| Layer | What | Accuracy Lift | Effort |
|-------|------|---------------|--------|
| **Baseline** | LLM + calendar roster | 70–90% | Low |
| **+ Speaker profiles** | Persistent participant knowledge base | +5–10% | Low (one-time) |
| **+ Multi-pass anchoring** | Extract explicit name mentions first, then infer | +5–10% | Low |
| **+ Self-voice ID** | Always know which speaker is you | +3–5% | Low (one-time) |
| **+ Temporal signals** | Join/leave times → speaker correlation | +3–5% | Medium |
| **+ Confirmation feedback loop** | Corrections improve profiles over time | Compounds over weeks | Low |
| **Combined estimate** | | **90–98%** | |

### Technique Details

**1. Speaker Profile Database**
Maintain a persistent `speaker-profiles.json` with attributes for each regular participant: role, team, projects they own, topics they typically discuss, verbal patterns, and how they tend to open/close contributions. An agent builds this once by asking targeted questions about your top 15–20 meeting participants. Every mapping prompt includes the relevant profiles as context, turning generic "who said what?" into a highly constrained inference problem.

**2. Multi-Pass LLM Mapping with Anchor Extraction**
Instead of a single prompt mapping all speakers at once:
- **Pass 1:** Extract explicit anchors ("Thanks [teammate]," "As [Director of Pharmacy & Fulfillment Product] mentioned," "I'm Danny, and I'll...")
- **Pass 2:** Map anchored speakers with high confidence
- **Pass 3:** Use anchored speakers as context to infer remaining speakers (e.g., "SPEAKER_03 is the only unidentified speaker, and Madeline is the only unmapped attendee")

Each pass narrows the problem space, making the final inference significantly more reliable.

**3. Post-Meeting Confirmation → Feedback Loop**
After mapping, the agent presents its result for confirmation or correction. Corrections feed back into the speaker profile database, improving future accuracy. Misidentified speakers get richer profiles; the system learns which contextual clues are reliable vs. misleading.

**4. Temporal Signal Fusion (Join Times + Diarization)**
Pull participant join/leave timestamps from Calendar API or Meet/Zoom metadata. Cross-reference with diarization: a new speaker appearing at 14:05 in the transcript + Casey joining the call at 14:04 is a strong signal. Particularly powerful for late joiners and early leavers where the LLM has less context.

**5. Self-Voice Identification**
Record a 30-second sample of your own voice once. Use speaker verification to identify which SPEAKER_XX is you in every meeting. One speaker mapped with near-certainty constrains all remaining assignments.

**6. Meeting-Type Priors**
Encode meeting format into the mapping prompt:
- **Standup:** Speakers rotate in roughly consistent order
- **1:1:** Only two speakers; trivial if you know your own voice
- **Review/demo:** One person dominates (presenter); others ask short questions
- **Planning:** More balanced; facilitator speaks first and most

**7. Cross-Meeting Voice Consistency**
Save speaker embeddings (generated internally by pyannote/WhisperX) from meetings with confirmed mappings. For the next meeting with overlapping attendees, compare new embeddings against the confirmed library. This is "lazy enrollment" — no explicit samples needed, the system learns from confirmed meetings over time.

**8. Action Item Cross-Reference**
If the synthesis agent produces "[teammate] will investigate the HighJump timeout issue" and SPEAKER_02 said "I'll look into the HighJump timeout" — that's a mapping confirmation. Run mapping *after* synthesis and use action items as additional evidence.

### Recommended Implementation Order

Build these in sequence — each is additive and independently valuable:
1. **Speaker profiles + multi-pass anchoring** — highest ROI, build first
2. **Self-voice ID + confirmation feedback loop** — quick wins that compound
3. **Temporal signals + meeting-type priors** — situational but valuable
4. **Cross-meeting voice consistency + action item cross-reference** — longer-term refinements

---

## Open Items

1. **Validate ownscribe** — Run `uvx ownscribe --mic` on a test call to confirm capture quality and transcription accuracy on your hardware.
2. **mlx-whisper accuracy** — Test with a sample meeting; verify pharmacy/fulfillment terms are transcribed correctly with initial prompt.
3. **Diarization adequacy** — Run WhisperX on a 5+ speaker meeting and assess whether local DER is acceptable.
4. **Google Meet transcript** — Confirm whether native transcription is still enabled in your Workspace (if so, skip diarization + mapping entirely).
5. **LLM for mapping** — Test the speaker mapping prompt with a real diarized transcript + attendee list to calibrate accuracy.
6. **Legal validation** — Confirm local-only transcription is acceptable under company policy (assumption: personal notes are fine; verbatim storage on vendor servers is not).

---

## Sources

- ownscribe: [GitHub](https://github.com/) — Core Audio Taps-based capture + transcription
- BlackHole: [existential.audio](https://existential.audio/blackhole/)
- Loopback: [rogueamoeba.com](https://rogueamoeba.com/loopback/)
- mlx-whisper: Apple MLX ecosystem — [mlx-community/whisper-large-v3-turbo](https://huggingface.co/mlx-community)
- WhisperX: [m-bain/whisperX](https://github.com/m-bain/whisperX)
- pyannote.audio: [pyannote.ai](https://www.pyannote.ai/)
- AssemblyAI: [assemblyai.com](https://www.assemblyai.com/)
- Deepgram: [deepgram.com](https://deepgram.com/)
- DiarizationLM (Google Research, Interspeech 2024)
- pyannote.ai Benchmark: DER comparison of commercial and OSS systems
- VoicePing NeMo vs Pyannote evaluation (Dec 2025)
- Northflank STT benchmarks 2026

*Research conducted via parallel sub-agent investigation, March 2026.*
