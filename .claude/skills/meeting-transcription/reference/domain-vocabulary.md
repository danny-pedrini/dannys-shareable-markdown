# Domain Vocabulary Reference

**Default prompt:** The pipeline's `record_meeting.py` script has a built-in default prompt with domain terms (PV2, beyondRx, HighJump, putwall, FPSE, etc.) — no `--initial-prompt` flag needed unless customizing.

Whisper's `initial_prompt` parameter primes the model to correctly transcribe uncommon terms. This document tracks domain terms, known misrecognitions, and correction approaches.

## Domain Terms

These terms appear frequently in pharmacy/fulfillment meetings and are not in standard English dictionaries:

| Term | What It Is | Risk Level |
|------|-----------|------------|
| PV2 | Pharmacist Verification step 2 | High — often mis-transcribed |
| beyondRx | Internal fulfillment platform name | High — compound word, unusual casing |
| HighJump | Legacy WMS being deprecated | Medium — real word, may capitalize wrong |
| Tompkins | Automation vendor (Tompkins Robotics) | Low — real surname |
| putwall | Sort-to-light wall in fulfillment | High — not a real word |
| DEA | Drug Enforcement Administration | Low — common acronym |
| USP 797 | Compounding pharmacy standard | Medium — number may garble |
| HIPAA | Health Insurance Portability and Accountability Act | Low — common acronym |
| SLA | Service Level Agreement | Low — common acronym |
| Rx / non-Rx | Prescription / non-prescription | Low — common abbreviation |
| UPH | Units Per Hour | Medium — uncommon acronym |
| wave planning | Batch-based order release strategy | Low — real words |
| pick and pack | Fulfillment process steps | Low — real words |
| conveyance | Automated material transport | Low — real word |
| FPSE | Fulfillment Pharmacy Software Engineering | High — internal acronym |
| compounding | Preparing custom medications | Low — real word |

## Known Misrecognitions

Based on Whisper large-v3-turbo behavior with uncommon terms (without initial_prompt):

| Correct Term | Likely Misrecognitions |
|-------------|----------------------|
| PV2 | PB2, PV too, PV-2, peevee two |
| beyondRx | beyond RX, beyond our acts, beyond Rx, beyond racks |
| putwall | put wall, but wall, putt wall |
| FPSE | FPS, FPSC, FP essay |
| UPH | UPS, you pH |
| USP 797 | USP seven ninety seven, USP 7-97 |

## Supplementary Agent Correction

The `initial_prompt` in `record_meeting.py` is now the primary approach for domain term recognition. The speaker-mapping agent and discovery-synthesis-agent still operate on transcript text and can correct any remaining misrecognitions. Include this note when invoking either agent:

> "This transcript may contain misrecognitions of domain terms. Common corrections: PB2→PV2, put wall→putwall, beyond RX→beyondRx, FPS→FPSE. Please apply these corrections when you encounter them."

The `large-v3-turbo` model with `initial_prompt` handles most terms correctly. The highest-risk terms—**PV2**, **beyondRx**, and **putwall**—may still need occasional agent correction.
