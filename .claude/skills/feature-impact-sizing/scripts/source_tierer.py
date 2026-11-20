#!/usr/bin/env python3
"""
Source Quality Tierer

Classifies research sources into quality tiers (A / B / C) based on
source domain, publication type, and content signals.

Tier definitions:
  A — Research firms, peer-reviewed journals, government data
  B — Trade publications, industry associations, reputable vendor research
  C — Blog posts, opinion pieces, vendor marketing, forums, unrecognized

Usage:
    python source_tierer.py --input sources.json
    python source_tierer.py --input sources.json --output tiered_sources.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Domain classification lists
# ---------------------------------------------------------------------------

TIER_A_DOMAINS = {
    # Research & consulting firms
    "gartner.com",
    "mckinsey.com",
    "deloitte.com",
    "bcg.com",
    "bain.com",
    "accenture.com",
    "capgemini.com",
    "kpmg.com",
    "ey.com",
    "pwc.com",
    "forrester.com",
    "idc.com",
    # Government & regulatory
    "bls.gov",
    "fda.gov",
    "cdc.gov",
    "census.gov",
    "dol.gov",
    "gao.gov",
    "nist.gov",
    "osha.gov",
    "cms.gov",
    # Academic & peer-reviewed
    "pubmed.ncbi.nlm.nih.gov",
    "scholar.google.com",
    "nature.com",
    "sciencedirect.com",
    "springer.com",
    "wiley.com",
    "jstor.org",
    "hbr.org",
    "tandfonline.com",
    # Industry standards bodies
    "apics.org",
    "ascm.org",
    "ispe.org",
    "ashp.org",
    "ieee.org",
}

TIER_B_DOMAINS = {
    # Supply chain & logistics trade publications
    "supplychaindive.com",
    "supplychainbrain.com",
    "logisticsmgmt.com",
    "dcvelocity.com",
    "mmh.com",
    "mhlnews.com",
    "inboundlogistics.com",
    "freightwaves.com",
    # Healthcare trade publications
    "modernhealthcare.com",
    "fiercehealthcare.com",
    "beckershospitalreview.com",
    "healthcareitnews.com",
    "pharmacytimes.com",
    "drugchannels.net",
    # Industry associations
    "mhi.org",
    "werc.org",
    "cscmp.org",
    "ism.org",
    "warehousingeducation.org",
    # Business & tech (reputable)
    "forbes.com",
    "bloomberg.com",
    "reuters.com",
    "wsj.com",
    "ft.com",
    "techcrunch.com",
    "wired.com",
    "zdnet.com",
    "technologyreview.com",
    # Major vendor research portals (when presenting data, not marketing)
    "aws.amazon.com",
    "cloud.google.com",
    "azure.microsoft.com",
    "zebra.com",
    "honeywell.com",
}

# Content keywords that suggest rigorous methodology → upgrade potential
TIER_UPGRADE_PATTERNS = [
    r"peer.?review",
    r"meta.?analysis",
    r"systematic review",
    r"randomized",
    r"longitudinal study",
    r"controlled trial",
    r"annual report",
    r"industry benchmark",
    r"benchmark report",
    r"state of .+ report",
    r"market research",
    r"survey of \d+",
    r"sample size",
    r"n\s*=\s*\d{2,}",
]

# Content signals that indicate low rigor → downgrade potential
TIER_DOWNGRADE_PATTERNS = [
    r"\bblog\b",
    r"\bopinion\b",
    r"\blisticle\b",
    r"\b(?:top|best) \d+\b",
    r"\bsponsored\b",
    r"\badvertorial\b",
    r"\bpress release\b",
    r"\binfographic\b",
]

TIER_C_DOMAINS = {
    "reddit.com",
    "quora.com",
    "medium.com",
    "wordpress.com",
    "blogspot.com",
    "linkedin.com",
    "substack.com",
    "hubspot.com",
    "wikipedia.org",
}


# ---------------------------------------------------------------------------
# Classification logic
# ---------------------------------------------------------------------------

def extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def domain_matches(domain: str, domain_set: set) -> str | None:
    """Check if domain matches any entry in the set (exact or subdomain)."""
    for d in domain_set:
        if domain == d or domain.endswith(f".{d}"):
            return d
    return None


def classify_source(source: dict) -> dict:
    url = source.get("url", "")
    title = source.get("title", "").lower()
    context = source.get("context", "").lower()
    combined = f"{title} {context}"

    domain = extract_domain(url)
    tier = "C"
    reasons = []

    # Step 1: Domain-based classification
    match = domain_matches(domain, TIER_A_DOMAINS)
    if match:
        tier = "A"
        reasons.append(f"Domain '{domain}' is a recognized A-tier source ({match})")
    else:
        match = domain_matches(domain, TIER_B_DOMAINS)
        if match:
            tier = "B"
            reasons.append(f"Domain '{domain}' is a recognized B-tier source ({match})")
        else:
            match = domain_matches(domain, TIER_C_DOMAINS)
            if match:
                tier = "C"
                reasons.append(f"Domain '{domain}' is a known C-tier source ({match})")

    # Step 2: Content-based upgrades (max one tier)
    if tier != "A":
        for pattern in TIER_UPGRADE_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                old_tier = tier
                tier = "A" if tier == "B" else "B"
                reasons.append(
                    f"Upgraded {old_tier}→{tier}: content suggests rigorous methodology "
                    f"(matched: '{pattern}')"
                )
                break

    # Step 3: Content-based downgrades (max one tier)
    for pattern in TIER_DOWNGRADE_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE) or re.search(pattern, url, re.IGNORECASE):
            if tier in ("A", "B"):
                old_tier = tier
                tier = "B" if tier == "A" else "C"
                reasons.append(
                    f"Downgraded {old_tier}→{tier}: content appears informal "
                    f"(matched: '{pattern}')"
                )
            break

    # Step 4: Default reason if no classification matched
    if not reasons:
        reasons.append(f"Domain '{domain}' not in recognized tier lists → defaulted to C")

    return {
        **source,
        "tier": tier,
        "tier_reasons": reasons,
        "domain": domain,
    }


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def tier_sources(sources: list) -> dict:
    tiered = [classify_source(s) for s in sources]

    counts = {"A": 0, "B": 0, "C": 0}
    for s in tiered:
        counts[s["tier"]] += 1

    warnings = []
    ab_total = counts["A"] + counts["B"]

    if ab_total == 0:
        warnings.append(
            "⚠️ ALL SOURCES ARE C-TIER. "
            "Impact estimates should be treated as directional only. "
            "Consider additional research from research firms or trade publications."
        )
    elif ab_total == 1:
        warnings.append(
            "Only 1 A/B-tier source found. "
            "Consider additional research for higher confidence."
        )

    if counts["C"] > ab_total > 0:
        warnings.append(
            "Majority of sources are C-tier. "
            "Base-case calculations use tier-weighted averaging to reduce C-tier influence."
        )

    return {
        "sources": tiered,
        "summary": {
            "total": len(tiered),
            "tier_A": counts["A"],
            "tier_B": counts["B"],
            "tier_C": counts["C"],
        },
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Source Quality Tierer — A/B/C classification")
    parser.add_argument("--input", required=True, help="Path to input JSON (array or {sources: [...]})")
    parser.add_argument("--output", help="Path to output JSON file (default: stdout)")
    args = parser.parse_args()

    with open(args.input, "r") as fh:
        data = json.load(fh)

    if isinstance(data, list):
        sources = data
    elif isinstance(data, dict) and "sources" in data:
        sources = data["sources"]
    else:
        print(
            "Error: Input must be a JSON array or object with 'sources' key.",
            file=sys.stderr,
        )
        sys.exit(1)

    result = tier_sources(sources)
    out = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(out)
        print(f"✅ Output written to {args.output}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
