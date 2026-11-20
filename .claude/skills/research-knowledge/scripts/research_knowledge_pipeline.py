"""
Research Knowledge Curation Pipeline - GENERALIZED VERSION
Runs deep research on any subject matter. Uses only free APIs.
Synthesis done via Cursor Agent mode.

Setup:
    pip install requests tqdm

Environment variables (both have generous free tiers):
    export SERPER_API_KEY="xxx"      # serper.dev (2,500 free searches)
    export EXA_API_KEY="xxx"         # exa.ai (1,000 free searches/month)

Usage:
    # Interactive mode (guided setup)
    python research_knowledge_pipeline.py

    # With config file
    python research_knowledge_pipeline.py --config my_research.json

    # Quick mode with just a topic (generates default queries)
    python research_knowledge_pipeline.py --topic "supply chain optimization"

Config file format (my_research.json):
{
    "topic_name": "Supply Chain Optimization",
    "output_folder": "supply_chain_knowledge",
    "search_domains": {
        "Domain Name": [
            "search query 1",
            "search query 2"
        ]
    },
    "relevance_keywords": {
        "high": ["keyword1", "keyword2"],
        "medium": ["keyword3", "keyword4"],
        "low": ["keyword5", "keyword6"]
    }
}
"""

import os
import json
import time
import hashlib
import argparse
import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Try to import tqdm, fall back to simple progress if not available
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, desc=""):
        total = len(iterable) if hasattr(iterable, '__len__') else None
        for i, item in enumerate(iterable):
            if total:
                print(f"\r{desc}: {i+1}/{total}", end="", flush=True)
            yield item
        print()


# ============ CONFIGURATION ============

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")

SCRIPT_DIR = Path(__file__).parent
RESULTS_PER_QUERY = 12


@dataclass
class ResearchConfig:
    """Configuration for a research session"""
    topic_name: str
    output_folder: str
    search_domains: Dict[str, List[str]]
    relevance_keywords: Dict[str, List[str]]
    results_per_query: int = 12
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ResearchConfig':
        data = json.loads(json_str)
        return cls(**data)
    
    @classmethod
    def from_file(cls, path: str) -> 'ResearchConfig':
        with open(path, 'r') as f:
            return cls.from_json(f.read())
    
    def save(self, path: str):
        with open(path, 'w') as f:
            f.write(self.to_json())


@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str
    source: str
    query_domain: str


@dataclass  
class ContentChunk:
    id: str
    source_url: str
    title: str
    content: str
    chunk_index: int
    query_domain: str
    word_count: int
    relevance_score: float = 0.0


@dataclass
class VerifiedSource:
    """Tracks URL validation status from scraping"""
    url: str
    title: str  # Verified title (extracted from scraped content)
    status: str  # "verified" (scraped successfully) or "failed"
    scrape_timestamp: str
    word_count: int = 0
    query_domain: str = ""
    error_reason: str = ""
    search_title: str = ""  # Original title from search results (may differ)
    title_source: str = ""  # "scraped" or "search_fallback"


def generate_default_queries(topic: str) -> Dict[str, List[str]]:
    """Generate default search queries for a topic using common research patterns"""
    
    # Clean up topic for use in queries
    topic_lower = topic.lower()
    topic_title = topic.title()
    
    return {
        f"{topic_title} - Fundamentals": [
            f"what is {topic_lower} definition overview",
            f"{topic_lower} introduction guide beginners",
            f"{topic_lower} key concepts principles",
            f"{topic_lower} fundamentals explained",
            f"understanding {topic_lower} basics",
        ],
        f"{topic_title} - Best Practices": [
            f"{topic_lower} best practices industry",
            f"{topic_lower} optimization strategies",
            f"{topic_lower} tips and tricks experts",
            f"how to improve {topic_lower}",
            f"{topic_lower} common mistakes to avoid",
        ],
        f"{topic_title} - Technology & Tools": [
            f"{topic_lower} software tools comparison",
            f"{topic_lower} automation technology",
            f"best {topic_lower} platforms systems",
            f"{topic_lower} digital transformation",
            f"AI machine learning {topic_lower}",
        ],
        f"{topic_title} - Case Studies": [
            f"{topic_lower} case study success story",
            f"company {topic_lower} implementation example",
            f"{topic_lower} ROI results metrics",
            f"leading companies {topic_lower} strategy",
            f"{topic_lower} real world examples",
        ],
        f"{topic_title} - Trends & Future": [
            f"{topic_lower} trends 2024 2025",
            f"future of {topic_lower} predictions",
            f"{topic_lower} emerging innovations",
            f"{topic_lower} industry outlook forecast",
            f"{topic_lower} next generation developments",
        ],
        f"{topic_title} - Challenges & Solutions": [
            f"{topic_lower} challenges problems",
            f"{topic_lower} pain points solutions",
            f"overcoming {topic_lower} obstacles",
            f"{topic_lower} risk management",
            f"{topic_lower} troubleshooting common issues",
        ],
    }


def generate_default_keywords(topic: str) -> Dict[str, List[str]]:
    """Generate default relevance keywords from a topic"""
    
    # Split topic into individual words
    words = topic.lower().split()
    
    return {
        # High value - direct topic relevance
        "high": words + [
            topic.lower(),
            topic.lower().replace(' ', '-'),
            topic.lower().replace(' ', '_'),
        ],
        # Medium value - related concepts
        "medium": [
            "strategy", "optimization", "implementation", "best practice",
            "solution", "system", "process", "workflow", "automation",
            "technology", "platform", "software", "tool", "framework",
        ],
        # Low value - general business/tech terms
        "low": [
            "business", "company", "organization", "industry", "enterprise",
            "efficiency", "performance", "improvement", "innovation",
            "data", "analytics", "metrics", "roi", "results",
        ]
    }


def search_serper(query: str, num_results: int = 10) -> List[Dict]:
    """Search using Serper API"""
    if not SERPER_API_KEY:
        return []
    
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": num_results}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        results = response.json().get("organic", [])
        return [{"url": r["link"], "title": r.get("title", ""), "snippet": r.get("snippet", "")} 
                for r in results]
    except Exception as e:
        print(f"  ⚠️  Serper error: {e}")
        return []


def search_exa(query: str, num_results: int = 10) -> List[Dict]:
    """Search using Exa API"""
    if not EXA_API_KEY:
        return []
    
    url = "https://api.exa.ai/search"
    headers = {"x-api-key": EXA_API_KEY, "Content-Type": "application/json"}
    payload = {"query": query, "numResults": num_results, "useAutoprompt": True, "type": "neural"}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        results = response.json().get("results", [])
        return [{"url": r["url"], "title": r.get("title", ""), "snippet": r.get("text", "")[:500] if r.get("text") else ""} 
                for r in results]
    except Exception as e:
        print(f"  ⚠️  Exa error: {e}")
        return []


def scrape_with_jina(url: str) -> str:
    """Scrape using Jina Reader (FREE, no API key needed)"""
    jina_url = f"https://r.jina.ai/{url}"
    
    try:
        response = requests.get(jina_url, timeout=45, headers={"Accept": "text/markdown"})
        if response.status_code == 200:
            return response.text
    except Exception:
        pass
    return ""


def get_cached_content(url: str, cache_dir: Path) -> Optional[str]:
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_file = cache_dir / f"{url_hash}.txt"
    if cache_file.exists():
        return cache_file.read_text()
    return None


def cache_content(url: str, content: str, cache_dir: Path):
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_file = cache_dir / f"{url_hash}.txt"
    cache_file.write_text(content)


def chunk_content(content: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """Split content into chunks"""
    if not content or len(content) < 200:
        return []
    
    words = content.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        if len(chunk_words) >= 100:
            chunks.append(" ".join(chunk_words))
    
    return chunks


def extract_title_from_content(content: str, fallback_title: str) -> str:
    """
    Extract title from Jina Reader markdown output.
    Jina Reader typically returns content with a markdown H1 title at the top.
    Falls back to the search result title if no H1 found.
    """
    if not content:
        return fallback_title
    
    lines = content.strip().split('\n')
    
    # Check first 10 lines for a markdown H1 title
    for line in lines[:10]:
        line = line.strip()
        if line.startswith('# '):
            extracted = line[2:].strip()
            if extracted and len(extracted) > 3:  # Sanity check
                return extracted
    
    # Fallback to search result title
    return fallback_title


def calculate_relevance(text: str, keywords: Dict[str, List[str]]) -> float:
    """Keyword-based relevance scoring"""
    text_lower = text.lower()
    score = 0
    
    for keyword in keywords.get("high", []):
        score += text_lower.count(keyword.lower()) * 3
    for keyword in keywords.get("medium", []):
        score += text_lower.count(keyword.lower()) * 2
    for keyword in keywords.get("low", []):
        score += text_lower.count(keyword.lower()) * 1
    
    # Normalize by length
    word_count = len(text.split())
    if word_count > 0:
        score = score / (word_count / 100)
    
    return round(score, 2)


def generate_output(chunks: List[ContentChunk], config: ResearchConfig, output_dir: Path, 
                    verified_sources: List[VerifiedSource] = None):
    """Generate output files for Cursor Agent synthesis"""
    
    # Group chunks by domain
    domains: Dict[str, List[ContentChunk]] = {}
    for chunk in chunks:
        if chunk.query_domain not in domains:
            domains[chunk.query_domain] = []
        domains[chunk.query_domain].append(chunk)
    
    # Create per-domain files for synthesis
    for domain, domain_chunks in domains.items():
        safe_domain = domain.lower().replace(' ', '_').replace('&', 'and').replace('-', '_')
        safe_domain = ''.join(c for c in safe_domain if c.isalnum() or c == '_')
        domain_file = output_dir / f"chunks_{safe_domain}.md"
        
        # Take top 25 chunks per domain
        top_chunks = sorted(domain_chunks, key=lambda x: x.relevance_score, reverse=True)[:25]
        
        with open(domain_file, "w") as f:
            f.write(f"# {domain} - Raw Research Chunks\n\n")
            f.write(f"*Topic: {config.topic_name}*\n")
            f.write(f"*Top {len(top_chunks)} chunks for synthesis by Claude in Cursor*\n\n")
            f.write("---\n\n")
            
            for i, chunk in enumerate(top_chunks):
                f.write(f"## Chunk {i+1} (Relevance: {chunk.relevance_score})\n\n")
                f.write(f"**Source**: [{chunk.title}]({chunk.source_url})\n\n")
                f.write(chunk.content[:3000])
                f.write("\n\n---\n\n")
        
        print(f"  ✅ {domain_file.name}")
    
    # Master index file
    index_file = output_dir / "INDEX.md"
    with open(index_file, "w") as f:
        f.write(f"# {config.topic_name} - Knowledge Library Index\n\n")
        f.write(f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
        f.write("## How to Use\n\n")
        f.write("1. Open each domain file below in Cursor\n")
        f.write("2. Ask Claude (in Agent mode) to synthesize the insights\n")
        f.write(f"3. Claude will create a structured summary (e.g., `{config.topic_name.replace(' ', '-')}-Reference.md`)\n\n")
        f.write("## Synthesis Prompt\n\n")
        f.write("Copy this prompt to Cursor:\n\n")
        f.write("```\n")
        f.write(f"Synthesize the research chunks in the {config.output_folder} directory into a comprehensive reference document.\n")
        f.write("For each domain, extract:\n")
        f.write("1. Key insights and findings\n")
        f.write("2. Best practices\n")
        f.write("3. Actionable recommendations\n")
        f.write("4. Notable tools, technologies, or frameworks mentioned\n")
        f.write(f"Save as '{config.topic_name.replace(' ', '-')}-Reference.md' in the same directory.\n")
        f.write("```\n\n")
        f.write("## Domain Files\n\n")
        
        for domain in sorted(domains.keys()):
            safe_domain = domain.lower().replace(' ', '_').replace('&', 'and').replace('-', '_')
            safe_domain = ''.join(c for c in safe_domain if c.isalnum() or c == '_')
            filename = f"chunks_{safe_domain}.md"
            chunk_count = len(domains[domain])
            f.write(f"- [{domain}]({filename}) ({chunk_count} chunks)\n")
        
        f.write("\n## Statistics\n\n")
        f.write(f"- **Topic:** {config.topic_name}\n")
        f.write(f"- **Total chunks:** {len(chunks)}\n")
        f.write(f"- **Domains covered:** {len(domains)}\n")
        f.write(f"- **Unique sources:** {len(set(c.source_url for c in chunks))}\n")
    
    print(f"  ✅ {index_file.name}")
    
    # All chunks JSON for reference
    json_file = output_dir / "all_chunks.json"
    with open(json_file, "w") as f:
        json.dump([{
            "id": c.id, "url": c.source_url, "title": c.title,
            "content": c.content, "domain": c.query_domain,
            "relevance_score": c.relevance_score
        } for c in chunks], f, indent=2)
    
    print(f"  ✅ {json_file.name}")
    
    # URL Verification Log - THE SOURCE OF TRUTH FOR CITATIONS
    if verified_sources:
        verified_file = output_dir / "verified_sources.json"
        verified_list = []
        for vs in verified_sources:
            verified_list.append({
                "url": vs.url,
                "title": vs.title,  # Verified title (from scraped content)
                "title_source": vs.title_source,  # "scraped" or "search_fallback"
                "search_title": vs.search_title,  # Original title from Google/Exa
                "status": vs.status,
                "scrape_timestamp": vs.scrape_timestamp,
                "word_count": vs.word_count,
                "query_domain": vs.query_domain,
                "error_reason": vs.error_reason
            })
        
        scraped_titles = len([v for v in verified_list if v["title_source"] == "scraped"])
        
        with open(verified_file, "w") as f:
            json.dump({
                "verification_note": "URLs with status 'verified' were successfully scraped. Titles with title_source='scraped' were extracted from the actual page content.",
                "total_urls": len(verified_list),
                "verified_count": len([v for v in verified_list if v["status"] == "verified"]),
                "failed_count": len([v for v in verified_list if v["status"] == "failed"]),
                "titles_from_scrape": scraped_titles,
                "titles_from_search_fallback": len(verified_list) - scraped_titles,
                "sources": verified_list
            }, f, indent=2)
        print(f"  ✅ {verified_file.name} (URL verification log)")
        
        # Also create a simple markdown list of verified URLs for quick reference
        verified_md = output_dir / "VERIFIED_URLS.md"
        with open(verified_md, "w") as f:
            f.write(f"# Verified URLs - {config.topic_name}\n\n")
            f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
            f.write("**⚠️ CITATION RULE: Only cite URLs from this list. These URLs were successfully scraped and verified.**\n\n")
            f.write("## Verification Legend\n\n")
            f.write("- **Title (scraped)**: Title extracted from actual page content ✅\n")
            f.write("- **Title (search)**: Title from search results (page may have different title) ⚠️\n\n")
            f.write("## Verified Sources (Safe to Cite)\n\n")
            f.write("| # | Title | Title Source | URL | Domain |\n")
            f.write("|---|-------|--------------|-----|--------|\n")
            verified_count = 0
            for vs in verified_sources:
                if vs.status == "verified":
                    verified_count += 1
                    safe_title = vs.title.replace("|", "-")[:40]
                    title_badge = "✅ scraped" if vs.title_source == "scraped" else "⚠️ search"
                    f.write(f"| {verified_count} | {safe_title} | {title_badge} | {vs.url} | {vs.query_domain} |\n")
            f.write(f"\n**Total: {verified_count} verified sources**\n")
            f.write(f"- Titles extracted from content: {scraped_titles}\n")
            f.write(f"- Titles from search (fallback): {verified_count - scraped_titles}\n\n")
            
            failed = [vs for vs in verified_sources if vs.status == "failed"]
            if failed:
                f.write("## Failed URLs (DO NOT CITE)\n\n")
                f.write("These URLs could not be scraped. Do not cite them.\n\n")
                for vs in failed:
                    f.write(f"- ❌ {vs.url}\n")
        print(f"  ✅ {verified_md.name} (quick reference)")
    
    # Save config for reference
    config_file = output_dir / "research_config.json"
    config.save(str(config_file))
    print(f"  ✅ {config_file.name}")
    
    return domains


def interactive_setup() -> ResearchConfig:
    """Guide user through setting up a research configuration"""
    
    print("\n" + "=" * 60)
    print("🔬 Research Knowledge Pipeline - Interactive Setup")
    print("=" * 60)
    
    # Get topic
    print("\n📚 What topic would you like to research?")
    print("   Examples: 'warehouse automation', 'AI product management', 'cold chain logistics'")
    topic = input("\n   Topic: ").strip()
    
    if not topic:
        print("❌ Topic is required. Exiting.")
        exit(1)
    
    # Generate output folder name
    safe_folder = topic.lower().replace(' ', '_').replace('-', '_')
    safe_folder = ''.join(c for c in safe_folder if c.isalnum() or c == '_')
    default_folder = f"{safe_folder}_knowledge"
    
    print(f"\n📁 Output folder name (default: {default_folder}):")
    folder = input("   Folder: ").strip() or default_folder
    
    # Generate default queries
    print("\n🔍 Generating default search queries...")
    queries = generate_default_queries(topic)
    
    print("\n   Generated domains:")
    for domain, domain_queries in queries.items():
        print(f"   • {domain} ({len(domain_queries)} queries)")
    
    print("\n   Would you like to customize the search queries? (y/N)")
    customize = input("   Customize: ").strip().lower()
    
    if customize == 'y':
        print("\n   📝 To customize, edit the generated config file after this setup.")
        print("   You can add/remove domains and queries as needed.")
    
    # Generate default keywords
    keywords = generate_default_keywords(topic)
    
    print("\n✅ Configuration ready!")
    
    config = ResearchConfig(
        topic_name=topic,
        output_folder=folder,
        search_domains=queries,
        relevance_keywords=keywords,
    )
    
    # Save config
    config_path = SCRIPT_DIR / f"{safe_folder}_config.json"
    config.save(str(config_path))
    print(f"\n   💾 Config saved to: {config_path}")
    print(f"   Edit this file to customize queries before running.")
    
    print("\n   Continue with this configuration? (Y/n)")
    proceed = input("   Proceed: ").strip().lower()
    
    if proceed == 'n':
        print(f"\n   Edit {config_path} and run again with:")
        print(f"   python research_knowledge_pipeline.py --config {config_path}")
        exit(0)
    
    return config


def run_pipeline(config: ResearchConfig):
    """Execute the research pipeline"""
    
    print("\n" + "=" * 60)
    print(f"🚀 Research Knowledge Pipeline")
    print(f"   Topic: {config.topic_name}")
    print("=" * 60)
    
    # Setup directories
    output_dir = SCRIPT_DIR / config.output_folder
    cache_dir = output_dir / "cache"
    output_dir.mkdir(exist_ok=True)
    cache_dir.mkdir(exist_ok=True)
    
    # Check APIs
    print("\n🔑 API Status:")
    print(f"  {'✅' if SERPER_API_KEY else '❌'} Serper (free tier)")
    print(f"  {'✅' if EXA_API_KEY else '❌'} Exa (free tier)")
    print("  ✅ Jina Reader (no key needed)")
    print("  ✅ Synthesis via Cursor (your subscription)")
    
    if not SERPER_API_KEY and not EXA_API_KEY:
        print("\n❌ ERROR: At least one search API key is required!")
        print("Set SERPER_API_KEY or EXA_API_KEY environment variable.")
        return
    
    all_results: List[SearchResult] = []
    
    # Search
    print("\n" + "=" * 60)
    print("📡 PHASE 1: Searching sources...")
    print("=" * 60)
    
    total_queries = sum(len(queries) for queries in config.search_domains.values())
    print(f"\n   {len(config.search_domains)} domains, {total_queries} queries")
    
    for domain, queries in config.search_domains.items():
        print(f"\n🔍 {domain}")
        for query in queries:
            print(f"  → {query[:55]}...")
            serper_results = search_serper(query, config.results_per_query)
            exa_results = search_exa(query, config.results_per_query)
            
            for r in serper_results:
                all_results.append(SearchResult(
                    url=r["url"], title=r["title"], snippet=r["snippet"],
                    source="serper", query_domain=domain
                ))
            for r in exa_results:
                all_results.append(SearchResult(
                    url=r["url"], title=r["title"], snippet=r["snippet"],
                    source="exa", query_domain=domain
                ))
            time.sleep(0.3)
    
    # Dedupe
    seen: Dict[str, SearchResult] = {}
    for r in all_results:
        if r.url not in seen:
            seen[r.url] = r
    unique_results = list(seen.values())
    
    print(f"\n📊 Found {len(unique_results)} unique URLs from {len(all_results)} total results")
    
    # Scrape
    print("\n" + "=" * 60)
    print("📥 PHASE 2: Scraping & Verifying URLs...")
    print("=" * 60)
    print("(This takes 10-20 minutes - using free Jina Reader)")
    
    all_chunks: List[ContentChunk] = []
    verified_sources: List[VerifiedSource] = []
    scraped_count = 0
    failed_count = 0
    scrape_timestamp = datetime.now().isoformat()
    
    for result in tqdm(unique_results, desc="Scraping"):
        content = get_cached_content(result.url, cache_dir)
        
        if not content:
            content = scrape_with_jina(result.url)
            if content:
                cache_content(result.url, content, cache_dir)
                scraped_count += 1
                
                # Extract title from scraped content (verified title)
                extracted_title = extract_title_from_content(content, result.title)
                title_source = "scraped" if extracted_title != result.title else "search_fallback"
                
                # Log as verified - URL was successfully scraped
                verified_sources.append(VerifiedSource(
                    url=result.url,
                    title=extracted_title,  # Use verified title
                    status="verified",
                    scrape_timestamp=scrape_timestamp,
                    word_count=len(content.split()),
                    query_domain=result.query_domain,
                    search_title=result.title,  # Keep original for reference
                    title_source=title_source
                ))
            else:
                failed_count += 1
                # Log as failed - URL could not be scraped
                verified_sources.append(VerifiedSource(
                    url=result.url,
                    title=result.title,
                    status="failed",
                    scrape_timestamp=scrape_timestamp,
                    query_domain=result.query_domain,
                    error_reason="Scrape returned empty content",
                    search_title=result.title,
                    title_source="search_fallback"
                ))
            time.sleep(0.5)
        else:
            scraped_count += 1
            
            # Extract title from cached content
            extracted_title = extract_title_from_content(content, result.title)
            title_source = "scraped" if extracted_title != result.title else "search_fallback"
            
            # Cached content means it was previously verified
            verified_sources.append(VerifiedSource(
                url=result.url,
                title=extracted_title,  # Use verified title
                status="verified",
                scrape_timestamp=scrape_timestamp,
                word_count=len(content.split()),
                query_domain=result.query_domain,
                search_title=result.title,
                title_source=title_source
            ))
        
        if not content:
            continue
        
        # Get verified title for chunks
        verified_title = extract_title_from_content(content, result.title)
        
        for i, chunk_text in enumerate(chunk_content(content)):
            chunk_id = hashlib.md5(f"{result.url}_{i}".encode()).hexdigest()[:12]
            relevance = calculate_relevance(chunk_text, config.relevance_keywords)
            
            all_chunks.append(ContentChunk(
                id=chunk_id,
                source_url=result.url,
                title=verified_title,  # Use verified title from scraped content
                content=chunk_text,
                chunk_index=i,
                query_domain=result.query_domain,
                word_count=len(chunk_text.split()),
                relevance_score=relevance
            ))
    
    print(f"\n📊 Scraped {scraped_count} pages ({failed_count} failed)")
    print(f"📊 Created {len(all_chunks)} chunks")
    print(f"📊 URL verification log: {len(verified_sources)} URLs tracked")
    
    # Sort by relevance
    all_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
    
    # Generate output
    print("\n" + "=" * 60)
    print("📝 PHASE 3: Generating output files...")
    print("=" * 60)
    
    domains = generate_output(all_chunks, config, output_dir, verified_sources)
    
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\nOutput directory: {output_dir}")
    print(f"Topic: {config.topic_name}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Domains: {len(domains)}")
    print(f"Unique sources: {len(set(c.source_url for c in all_chunks))}")
    
    print("\n🎯 NEXT STEPS:")
    print(f"   1. Open the INDEX.md file in {output_dir}")
    print("   2. Use the synthesis prompt to have Claude create a reference document")
    print("   3. Or ask Claude directly to synthesize specific domain files")


def main():
    parser = argparse.ArgumentParser(
        description="Research Knowledge Curation Pipeline - Generalized Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Interactive mode (guided setup)
    python research_knowledge_pipeline.py

    # With config file
    python research_knowledge_pipeline.py --config my_research.json

    # Quick mode with just a topic
    python research_knowledge_pipeline.py --topic "supply chain optimization"
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to JSON config file'
    )
    
    parser.add_argument(
        '--topic', '-t',
        type=str,
        help='Research topic (generates default queries)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output folder name (default: derived from topic)'
    )
    
    args = parser.parse_args()
    
    # Determine configuration source
    if args.config:
        # Load from config file
        config = ResearchConfig.from_file(args.config)
        print(f"📄 Loaded config from: {args.config}")
    elif args.topic:
        # Generate from topic
        topic = args.topic
        safe_folder = topic.lower().replace(' ', '_').replace('-', '_')
        safe_folder = ''.join(c for c in safe_folder if c.isalnum() or c == '_')
        output_folder = args.output or f"{safe_folder}_knowledge"
        
        config = ResearchConfig(
            topic_name=topic,
            output_folder=output_folder,
            search_domains=generate_default_queries(topic),
            relevance_keywords=generate_default_keywords(topic),
        )
        print(f"🔍 Generated config for topic: {topic}")
    else:
        # Interactive mode
        config = interactive_setup()
    
    # Run the pipeline
    run_pipeline(config)


if __name__ == "__main__":
    main()

