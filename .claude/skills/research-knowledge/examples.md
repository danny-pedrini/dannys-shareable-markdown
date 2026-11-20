# Example Interactions

## Example 1: Starting a Research Session

**User:** I want to research order batching algorithms for our warehouse

**Agent Response:**

Great topic. Let me help you set up and run this research.

**Research Objectives (confirm these work for you):**
1. Understand types of batching algorithms (wave, cluster, zone)
2. Learn best practices for batch optimization
3. Identify key metrics and benchmarks
4. Find tools/systems that implement batching
5. Discover implementation challenges and solutions

**Running the pipeline now:**
```bash
PIPELINE="/Users/dpedrini/Library/CloudStorage/GoogleDrive-you@example.com/My Drive/Cursor Files/.claude/skills/research-knowledge/scripts/research_knowledge_pipeline.py"
python "$PIPELINE" --topic "order batching algorithms warehouse"
```

This generates ~30 search queries across 6 domains: Fundamentals, Best Practices, Technology & Tools, Case Studies, Trends & Future, Challenges & Solutions.

**Estimated time:** 15-20 minutes

I will wait for pipeline completion before synthesizing. All citations will be verified against chunk files.

Want me to customize the search queries before running, or proceed with defaults?

---

## Example 2: Synthesis Request

**User:** Synthesize the order_batching_knowledge research into a reference doc

**Agent Steps:**

1. **Verify pipeline ran:**
   ```
   list_dir → order_batching_knowledge/
   ✅ INDEX.md exists
   ✅ chunks_*.md files exist
   ```

2. **Read verification log and chunks:**
   ```
   Read → VERIFIED_URLS.md
   Read → INDEX.md
   Read → chunks_fundamentals.md
   Read → chunks_best_practices.md
   ... (all domain chunks)
   ```

3. **Generate synthesis with verified citations:**

   ```markdown
   # Order Batching Algorithms - Knowledge Synthesis

   *Generated: January 8, 2026 | Sources: 47 unique sources across 6 domains*

   ## Executive Summary
   - **Wave batching** remains dominant (70%+) but **waveless** is growing
   - Optimal batch sizes: 8-15 orders depending on SKU diversity
   - **ML-based batching** shows 15-25% efficiency gains over rule-based
   - Key ROI: Travel time reduction (40-60% of picker time)

   ## Key Takeaways
   1. **Batch composition > batch size** — SKU overlap outperforms proximity
      by 20%+ — [Source: Supply Chain Brain](https://...) *(verified)*
   2. **Real-time batching requires WES** — Legacy WMS can't adapt to
      dynamic flows — [Source: Logistics Mgmt](https://...) *(verified)*

   ## Sources (Verified)
   | # | Source Title | URL | Chunk File |
   |---|-------------|-----|------------|
   | 1 | Supply Chain Brain | https://... | chunks_best_practices.md |
   ```

4. **Run citation audit** against `VERIFIED_URLS.md` before delivering.
