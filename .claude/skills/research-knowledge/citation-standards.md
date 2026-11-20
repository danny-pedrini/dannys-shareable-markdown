# Citation Verification Protocol

Every finding in a synthesis MUST have a verified citation. This document defines what "verified" means and how to enforce it.

## What "Verified" Means

| Verification Level | What It Proves | Tool |
|---|---|---|
| **URL was valid at scrape time** | Jina Reader successfully fetched content | `research_knowledge_pipeline.py` |
| **Title was extracted from page** | Title came from actual scraped content | `extract_title_from_content()` |
| **URL appears in chunks** | URL came from pipeline (not fabricated) | `Grep` / `Read` on chunks |
| **URL is still live now** | **NOT VERIFIED** — agent cannot make HTTP requests | None available |

The pipeline generates `verified_sources.json` and `VERIFIED_URLS.md` — these are the source of truth.

## Title Verification

The pipeline extracts titles from actual scraped content, not just search results:

| Title Source | Badge in VERIFIED_URLS.md | Reliability |
|---|---|---|
| `scraped` | ✅ scraped | High — extracted from actual page content |
| `search_fallback` | ⚠️ search | Medium — from Google/Exa, may not match page |

Prefer citing sources with `title_source: "scraped"` when possible.

## Verification Steps

### Step 1: Check the Verification Log

Before citing ANY URL, confirm it appears in `verified_sources.json` with `status: "verified"`:

```bash
# Read the verification whitelist
Read → {topic}_knowledge/VERIFIED_URLS.md

# Check a specific URL
grep "example.com" {topic}_knowledge/verified_sources.json

# List all verified URLs
grep '"status": "verified"' {topic}_knowledge/verified_sources.json
```

Only cite URLs that appear in the verification log with `status: "verified"`.

### Step 2: Extract Insight from Chunk

When you find valuable content in a chunk file, note:
- The insight/finding
- The exact source URL from the chunk metadata
- Confirm it's in `VERIFIED_URLS.md`

### Step 3: Format the Citation

**Inline format:**
```
[Finding statement] — [Source: Title](url) *(verified)*
```

**Example:**
```
Wave batching remains the dominant approach in high-volume warehouses — [Source: Supply Chain Digest](https://www.supplychaindigest.com/article/wave-batching-2024) *(verified)*
```

The `*(verified)*` tag indicates the URL was successfully scraped by the pipeline.

## Citation Rules

**DO:**
- Check `VERIFIED_URLS.md` first
- Only cite URLs with `status: "verified"` in `verified_sources.json`
- Use exact URL from chunk metadata (don't modify)
- Include `*(verified)*` tag to indicate provenance

**DON'T:**
- `— Source: example.com` (placeholder URL)
- `— [Industry Report]` (no URL)
- `— (various sources)` (vague attribution)
- `— https://made-up-url.com` (fabricated URL)
- Cite a URL not in `verified_sources.json`
- Cite a URL with `status: "failed"`

## When a URL Is Not Verified

If you want to cite something but the URL is not in the verification log:
1. DO NOT include the finding
2. Note it as a "Research Gap" in the synthesis
3. Be explicit: "Source could not be verified"

## Citation Failure Modes

| Failure | Example | Why It's Bad |
|---|---|---|
| Fabricated URL | `[Source](https://made-up.com/article)` | User clicks, gets 404 |
| Placeholder URL | `[Source](https://example.com)` | Obviously fake |
| Vague attribution | `— Various sources` | Unverifiable |
| Memory-based claim | `Studies show that...` (no cite) | Could be hallucination |
| URL mismatch | Cite URL A, content from URL B | Misleading |
