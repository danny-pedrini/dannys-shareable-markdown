# Quality Checks

Run ALL checks before delivering any synthesis document.

## Pipeline & Source Verification

| Check | Criteria | How to Verify |
|-------|----------|---------------|
| ☐ Pipeline ran | Output directory exists with INDEX.md | `list_dir` on knowledge folder |
| ☐ Chunks read | You read the actual chunk files | Confirm you used `Read` on chunks |
| ☐ No shortcuts | Did NOT use `web_search` as substitute | Review your tool calls |

## Citation Verification (CRITICAL)

| Check | Criteria | How to Verify |
|-------|----------|---------------|
| ☐ Read verification log | Started by reading `VERIFIED_URLS.md` | Confirm `Read` was called |
| ☐ All citations in log | Every cited URL has `status: "verified"` in `verified_sources.json` | Cross-reference |
| ☐ No failed URLs cited | Did not cite any URL with `status: "failed"` | Check verification log |
| ☐ No placeholder URLs | No example.com, source.com, etc. | Search for "example" in synthesis |
| ☐ Inline format correct | `[Finding] — [Source: Title](url) *(verified)*` | Visual inspection |
| ☐ Sources table complete | All URLs mapped to verification status | Cross-reference with `VERIFIED_URLS.md` |

## Content Quality

| Check | Criteria |
|-------|----------|
| ☐ Actionability | PM can take action based on this |
| ☐ Structure | Follows appropriate pattern for research goal |
| ☐ Conflicts flagged | Contradictory sources are noted |
| ☐ Gaps identified | What we don't know is explicit |
| ☐ Executive summary | Busy reader can get value in 30 seconds |

## Final Audit

Before delivering, answer each question honestly:

1. **"Can I point to the chunk file for each finding?"** — If no, remove finding
2. **"Is each URL copy-pasted from chunk metadata?"** — If no, verify or remove
3. **"Would I be embarrassed if the user clicked every link?"** — If yes, re-verify
