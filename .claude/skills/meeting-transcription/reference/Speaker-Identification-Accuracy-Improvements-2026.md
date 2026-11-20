# Speaker Identification Accuracy Improvements — Research & Recommendations (2026)

**Research date:** March 2026  
**Use case:** Fully local meeting transcription on macOS Apple Silicon. ownscribe + WhisperX 3.8+ + pyannote Community-1 (pyannote.audio 4.x) + LLM speaker mapping. Target: maximize end-to-end speaker accuracy within constraints (no new API fees, no biometric enrollment for others, self-voice OK).

---

## TL;DR

| Priority | Improvement | Est. Accuracy Lift | Effort | Dependencies |
|----------|-------------|-------------------|--------|--------------|
| 1 | **pyannote min/max_speakers** | +5–12% mapping | Low | Custom pipeline or ownscribe PR |
| 2 | **Self-voice enrollment** | +3–8% mapping | Low | 30s voice sample, Python script or speech-swift |
| 3 | **DiarizationLM post-processing** | +10–25% DER reduction | Medium | Claude Code LLM (acceptable), pip install |
| 4 | **Meeting-type priors** | +2–5% mapping | Low | Agent prompt edit |
| 5 | **Profile feedback loop** | Compounds over time | Low | Profile schema + agent update |
| 6 | **Temporal signals (join/leave)** | +3–5% for late joiners | Medium | Meet/Zoom API (data availability uncertain) |
| 7 | **Cross-meeting lazy enrollment** | +5–15% for recurring attendees | High | Custom Python, embedding storage |
| 8 | **speech-swift evaluation** | TBD (≤3 speakers only) | Medium | Swift build, benchmark |

**Accuracy ceiling (fully local, Community-1):** ~77–90% end-to-end for 5+ speaker meetings with all optimizations. APIs (AssemblyAI 3.1% DER) remain ~2–3× more accurate at diarization; mapping layer can approach 90%+ with stacking.

---

## 1. Ranked Improvement List

### 1.1 pyannote min_speakers / max_speakers (Highest ROI)

**What it does:** When you know the attendee count (from Calendar), pass `min_speakers` and `max_speakers` to pyannote. This constrains the clustering stage so it doesn't over-split (e.g., one person → 3 labels) or under-merge (2 people → 1 label).

**How it works:** pyannote uses agglomerative clustering on speaker embeddings. Without bounds, it heuristically chooses cluster count. With `num_speakers=N` or `min_speakers=m, max_speakers=M`, clustering stops when the count is satisfied, reducing label confusion.

**Accuracy estimate:** +5–12% on mapping (fewer bogus SPEAKER_XX, cleaner input for LLM). DER improvement is indirect — fewer clustering mistakes.

**Effort:** Low (parameter change). **Dependency:** ownscribe does not expose these. Options:
- Custom Python pipeline that calls WhisperX + pyannote directly with `pipeline(audio, min_speakers=n, max_speakers=n)` when attendees are known
- PR to ownscribe: add `[diarization] min_speakers` and `max_speakers` in config.toml
- Use `list_events` output (attendee count) → pass to custom diarization step

**Implementation snippet:**

```python
# In custom pipeline after fetching attendees from Calendar
from pyannote.audio import Pipeline
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=token)
n = len(attendees)  # e.g. 5
diarization = pipeline(audio_path, min_speakers=max(1, n-1), max_speakers=min(8, n+1))
```

---

### 1.2 Self-Voice Identification

**What it does:** You record a ~30s sample of your own voice once. Before or during speaker mapping, a script identifies which SPEAKER_XX is you via embedding similarity.

**How it works:** pyannote/embedding (or WeSpeaker in speech-swift) produces 256-dim vectors. Compare your sample embedding to per-speaker segment embeddings (or centroids). Lowest cosine distance → you.

**Accuracy estimate:** +3–8% mapping (one high-confidence anchor; simplifies elimination). Near-deterministic for you if audio quality is decent.

**Effort:** Low. The implementation spec already includes a Python script; speech-swift has `--target-speaker enrollment.wav`.

**Prerequisites:**
- 30s clean voice sample: `sox -d -r 16000 -c 1 -b 16 ~/.config/speaker-mapping/voice_sample.wav trim 0 30`
- HuggingFace token for `pyannote/embedding`

---

### 1.3 DiarizationLM Post-Processing

**What it does:** Converts ASR + diarization output into a compact text format, sends to an LLM (local or API), and uses the LLM to fix speaker labels using transcript context. No retraining of pyannote or Whisper.

**How it works:** DiarizationLM (Google, Interspeech 2024) uses a Transcript-Preserving Speaker Transfer (TPST) algorithm. It feeds the LLM a structured prompt of utterances with current speaker labels; the LLM corrects misassignments using semantic coherence (e.g., "thanks [teammate]" implies the next speaker might be [teammate]).

**Accuracy estimate:** Paper reports 55.5% relative WDER reduction on Fisher, 44.9% on Callhome. For your pipeline: expect ~10–25% relative DER reduction. Exact lift depends on meeting style.

**Effort:** Medium. `pip install diarizationlm`. Integrates as post-processing after WhisperX. Can use Claude Code's LLM (acceptable per constraints) or local Llama 8B (4-bit fits 16GB).

**Dependencies:** diarizationlm package; LLM (Claude Code or local). Finetuned models (DiarizationLM-8b-Fisher) improve over base LLM but add setup.

---

### 1.4 Meeting-Type Priors

**What it does:** Encode meeting format into the speaker-mapping prompt so the LLM uses structure (e.g., standup → rotating order; 1:1 → trivial with self-voice; review → one presenter).

**How it works:** Add a `meeting_type` field to the agent input: `standup | 1:1 | planning | review | general`. Agent rule includes prior-specific instructions (e.g., "In standups, speakers often rotate; first speaker is often the facilitator").

**Accuracy estimate:** +2–5% mapping for structured meetings.

**Effort:** Low. Edit the `speaker-mapping` skill to accept and use `meeting_type`.

---

### 1.5 Profile Feedback Loop

**What it does:** When the user corrects a mapping ("SPEAKER_02 is actually [Director of Pharmacy & Fulfillment Product]"), persist that correction into the speaker profile (e.g., stronger topic/pattern signals for [Director of Pharmacy & Fulfillment Product], or "commonly confused with X").

**How it works:** After confirmation/correction, agent updates `speaker-profiles.json` with new evidence. Future mappings get richer context.

**Accuracy estimate:** Compounds over weeks; hard to isolate, but +3–8% for frequent attendees.

**Effort:** Low. Extend mapping agent Step 7 to write profile updates when user corrects.

---

### 1.6 Temporal Signal Fusion (Join/Leave Times)

**What it does:** Use participant join/leave timestamps to correlate new speakers (e.g., SPEAKER_03 starts at 14:05; Casey joined at 14:04 → strong prior for Casey).

**How it works:** Google Meet REST API and Zoom API can expose participant join times. Cross-reference diarization segment start times with join events.

**Accuracy estimate:** +3–5% for meetings with late joiners or early leavers.

**Effort:** Medium. **Caveat:** Google Calendar API does **not** provide join times. Need Meet Transcript API or Zoom Report API. Data availability is org-dependent.

---

### 1.7 Cross-Meeting Lazy Enrollment

**What it does:** After a confirmed mapping, save speaker embeddings from pyannote (`return_embeddings=True`). In future meetings with overlapping attendees, compare new embeddings to the stored library and pre-identify recurring speakers.

**How it works:** Manual persistence layer:
1. Run diarization with `return_embeddings=True`
2. After user confirms mapping, store `{name: embedding}` in `~/.config/speaker-mapping/embeddings.json` (or safetensors)
3. Next meeting: for each detected speaker centroid, compute cosine similarity to stored embeddings; if above threshold, assign name before LLM pass

**Accuracy estimate:** +5–15% for recurring meetings with the same people. Degrades with audio quality changes (different mics, VoIP).

**Effort:** High. Custom Python, storage format, threshold tuning. pyannote has no built-in cross-file persistence.

---

### 1.8 speech-swift / MLX-Native Diarization

**What it does:** [speech-swift](https://github.com/soniqo/speech-swift) (Feb 2026) provides native Swift/MLX diarization: Silero VAD + pyannote segmentation 3.0 + WeSpeaker embeddings. No Python, no PyTorch. Includes `--target-speaker enrollment.wav` for self-voice extraction.

**Limitation:** pyannote powerset supports **≤3 concurrent speakers** (7-class output). For meetings with 4+ overlapping speakers, it will merge or mislabel. Fine for 1:1, 3-person, low-overlap 5-person.

**Accuracy estimate:** No published DER vs pyannote. Likely similar for ≤3 speakers; worse for 5+ overlap. Worth benchmarking.

**Effort:** Medium. `git clone`, `swift build`, `audio diarize meeting.wav`. Would require replacing WhisperX diarization step or running speech-swift separately and merging with WhisperX transcript.

---

## 2. pyannote Tuning Guide

ownscribe does **not** expose pyannote parameters. Use a **custom pipeline** or contribute an ownscribe PR to add config. Below are recommended values for meeting audio.

### 2.1 Parameters to Tune

| Parameter | Scope | Recommended for Meetings | Effect |
|-----------|-------|--------------------------|--------|
| `min_speakers` | Pipeline | `max(1, attendee_count - 1)` | Lower bound for clustering |
| `max_speakers` | Pipeline | `min(8, attendee_count + 1)` | Upper bound; avoids over-splitting |
| `num_speakers` | Pipeline | Use when count is exact | Exact count (overrides min/max) |
| `segmentation.min_duration_off` | Segmentation | `0.3`–`0.5` | Shorter = more segments; 0.5 bridges short pauses |
| `segmentation.threshold` | Segmentation | `0.5`–`0.6` | Higher = less aggressive speech detection |
| `clustering.threshold` | Clustering | `0.5`–`0.65` | Higher = fewer merges (more speakers) |
| `clustering.min_cluster_size` | Clustering | `3`–`15` | Minimum segments per cluster |

### 2.2 Retrieving Defaults

```python
from pyannote.audio import Pipeline
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=HF_TOKEN)
params = pipeline.parameters(instantiated=True)
# Inspect: params["segmentation"], params["clustering"]
```

### 2.3 Suggested Override for 5-Person Meeting

```python
params = pipeline.parameters(instantiated=True)
params["min_speakers"] = 4
params["max_speakers"] = 6
params["segmentation"]["min_duration_off"] = 0.4
params["segmentation"]["threshold"] = 0.55
params["clustering"]["threshold"] = 0.55
pipeline.instantiate(params)
diarization = pipeline("meeting.wav")
```

### 2.4 Apple Silicon

pyannote uses MPS when `device="auto"` or `device="mps"`. No Apple-specific tuning; MPS is already enabled in ownscribe config. speech-swift uses MLX and is natively optimized; consider for ≤3-speaker use cases.

---

## 3. Realistic Accuracy Expectations by Meeting Type

| Meeting Type | Speakers | DER (Community-1) | Mapping Accuracy | End-to-End (Est.) |
|--------------|----------|-------------------|------------------|-------------------|
| 1:1 | 2 | ~7–11% | 95%+ (with self-voice) | 90–95% |
| 3-person | 3 | ~9–14% | 80–90% | 74–86% |
| 5-person | 5 | ~11–17% | 65–80% | 57–72% |
| 8+ person | 8+ | ~14–20% | 50–70% | 42–62% |

**With all optimizations applied (min/max_speakers, self-voice, DiarizationLM, priors, feedback):**

| Meeting Type | End-to-End (Optimized) |
|--------------|------------------------|
| 1:1 | 93–97% |
| 3-person | 82–91% |
| 5-person | 72–83% |
| 8+ person | 62–76% |

---

## 4. Implementation Roadmap

### Phase 1 — Quick Wins (1–2 weeks)

1. **Self-voice** — Record sample, add identification step before mapping agent (use existing spec script or speech-swift `--target-speaker`).
2. **Meeting-type priors** — Add `meeting_type` to speaker-mapping agent; user or Calendar-derived.
3. **Profile feedback** — On correction, update `speaker-profiles.json` with new evidence.

### Phase 2 — Diarization Quality (2–4 weeks)

4. **pyannote min/max_speakers** — Build thin custom pipeline (or PR ownscribe) that passes attendee count to pyannote.
5. **pyannote segmentation/clustering tuning** — A/B test `min_duration_off`, `threshold` on 3–5 sample meetings.
6. **DiarizationLM** — Integrate as post-process; start with Claude Code LLM, evaluate WDER on a small test set.

### Phase 3 — Advanced (4–8 weeks)

7. **Temporal signals** — If Meet/Zoom participant API is available, add join-time correlation.
8. **Cross-meeting lazy enrollment** — Design embedding storage, implement persistence + matching script.
9. **speech-swift evaluation** — Benchmark for ≤3-speaker meetings; compare DER and latency to WhisperX+pyannote.

---

## 5. Honest Accuracy Ceiling Assessment

**Diarization (DER):** Local pyannote/WhisperX stays in the 11–19% range. Commercial APIs (AssemblyAI ~3.1%) remain ~2–3× better. DiarizationLM can improve WDER by 10–25% relative, but the base DER gap remains.

**Mapping:** With stacked improvements (profiles, anchors, self-voice, priors, feedback), mapping can reach ~85–95% for typical 3–5 person meetings. For 8+ speakers, 60–75% is realistic.

**End-to-end ceiling (fully local, Community-1, all optimizations):**
- 1:1: ~97%
- 3-person: ~91%
- 5-person: ~83%
- 8+ person: ~76%

To exceed this, you would need either:
- **Commercial diarization API** (violates "no new API fees")
- **Biometric enrollment for others** (violates privacy constraint)
- **Platform-native speaker attribution** (e.g., Google Meet Transcript API with participant IDs — if available in your org)

---

## 6. Summary Table

| Improvement | Accuracy Lift | Effort | Prerequisites |
|-------------|--------------|--------|----------------|
| min/max_speakers | +5–12% mapping | Low | Custom pipeline / ownscribe PR |
| Self-voice | +3–8% mapping | Low | 30s sample, pyannote/embedding |
| DiarizationLM | +10–25% DER rel. | Medium | pip, LLM (Claude Code OK) |
| Meeting-type priors | +2–5% mapping | Low | Agent prompt |
| Profile feedback | Compounds | Low | Profile schema |
| Temporal signals | +3–5% (late joiners) | Medium | Meet/Zoom API access |
| Lazy enrollment | +5–15% (recurring) | High | Custom Python |
| speech-swift | TBD (≤3 spk) | Medium | Swift build |

---

## Appendix: Additional Notes

- **WhisperX alignment:** PR #625 (audio normalization) improves word-level MAE. Ensure ownscribe uses WhisperX ≥3.7. Not a diarization fix but better segment boundaries help mapping.
- **Self-voice script:** Full Python implementation in `Meeting-Transcription-Pipeline-Implementation-Spec.md` (Appendix — Self-Voice Identification).
- **DiarizationLM model size:** DiarizationLM-8b-Fisher is Llama 3 8B; 4-bit quantized fits 16GB Apple Silicon. Base LLM (Claude Code) also works without finetuned model.

---

*Research conducted March 2026. Verify package versions and API availability before implementation.*
