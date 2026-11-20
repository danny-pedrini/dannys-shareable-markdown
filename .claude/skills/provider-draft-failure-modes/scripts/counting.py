"""Shared counting rules (`priority-rubric.md` section 2) and row-source derivation
(`round-folder-layout.md` section 1). A library: build_cluster.py, mechanical_check.py and
build_cluster_analysis.py import it, so every script counts a draft the same way.

    basis(row)         the row's Evidence basis; legacy `inferred` rows with a blank basis read
                       as `inferred`
    is_audit(row)      legacy row: Evidence basis `inferred` (a blank basis on Provenance `inferred`
                       reads the same). Not counted. New rounds do not write it.
    counts(row)        the row's basis is on the allow-list (phrase-scan is handled by the caller)
    source_kind(...)   the row's derived source kind: interviews, evals, edits, slack, a sheet
                       source's kind, or audit
    credited(...)      the providers a counted row credits
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round_config as RC  # noqa: E402

ALWAYS = {"reviewer-stated", "reviewer-edit-on-good", "eval-judge", "slack", "provider-edit+note", "note"}
PROVIDER_BASES = ALWAYS | {"provider-edit"}
NON_PERSON = {"audit", "eval", "scan"}
UNRESOLVED = "unresolved"  # the one handle every unresolved reviewer shares; sender_n and provider_n stay as written
PROVIDER_FIELD_RE = re.compile(r"^\*Trace (tr-[0-9a-fA-F]{32})[^*\n]*·\s*Provider:\s*([a-z0-9_]+)", re.M)


def basis(row):
    eb = RC.col(row, "evidence basis").strip()
    if eb:
        return eb
    prov = RC.col(row, "provenance").strip()
    return "inferred" if prov == "inferred" else prov


def is_audit(row):
    return basis(row) == "inferred"


def is_trace(t):
    return t.startswith("tr-")


def not_counted_row(row):
    a = RC.col(row, "atomic issue").lower()
    return "not counted:" in a or a.startswith("audited, no issue found") or a.startswith("thumbs only")


def counts(row):
    """True when the row backs a counted draft: a `tr-` trace and an allow-listed Evidence basis
    (`provider-edit` at Confidence high only)."""
    if not is_trace(RC.col(row, "trace id")) or not_counted_row(row):
        return False
    b = basis(row)
    if b == "provider-edit":
        return RC.col(row, "confidence").strip().lower().startswith("high")
    return b in ALWAYS


def rating_sources(cfg):
    """((trace, rating ref) -> sheet source kind, default kind). A legacy round has one sheet
    source, so every rating maps to its kind. A rating two sheets both hold takes the first
    sheet's kind. The default is the sheets' kind when they share one, else `ratings`."""
    import load_ratings as LR
    sheets = RC.sources_of_kind(cfg, *RC.SHEET_KINDS)
    kind_of = {s.get("code"): s["kind"] for s in sheets}
    kinds = {s["kind"] for s in sheets}
    default = kinds.pop() if len(kinds) == 1 else "ratings"
    out = {}
    for r in LR.source_rows("ratings.md"):
        if r["ref"]:
            out.setdefault((r["trace"], r["ref"]), kind_of.get(r["source"], "ratings"))
    return out, default


def source_kind(row, cfg, sessions, rating_map, default_kind):
    t = RC.col(row, "trace id")
    if not is_trace(t):
        code = RC.col(row, "row id").split("-")[0]
        return "interviews" if code in sessions else "audit"
    b = basis(row)
    if b == "inferred":
        return "audit"
    if b == "eval-judge":
        return "evals"
    if b in ("provider-edit", "provider-edit+note"):
        return "edits"
    if b == "slack":
        return "slack"
    ref = RC.col(row, "rating ref").replace(" · dup", "").strip()
    if ref:
        return rating_map.get((t, ref), default_kind or "ratings")
    return default_kind or "ratings"


def trace_raters(path="ratings.md"):
    """trace -> set of rater handles, from the ratings.md row table."""
    import load_ratings as LR
    out = {}
    if not os.path.exists(path):
        return out
    for r in LR.rating_rows(path):
        h, _ = LR.split_ref(r["ref"])
        if h:
            out.setdefault(r["trace"], set()).add(h)
    return out


def export_providers(codes):
    """trace -> the export record's optional `Provider:` handle."""
    out = {}
    for c in codes:
        p = os.path.join("export", f"{c}.md")
        if os.path.exists(p):
            for t, h in PROVIDER_FIELD_RE.findall(open(p).read()):
                out[t] = h
    return out


def credited(row, raters, export_provider):
    """The providers a counted row credits (rubric section 2 table)."""
    t = RC.col(row, "trace id")
    rev = RC.col(row, "reviewer").strip()
    b = basis(row)
    if b == "eval-judge":
        return {export_provider[t]} if t in export_provider else set()
    if b == "provider-edit" and rev in NON_PERSON:
        return set(raters.get(t, set()))
    if rev == "unresolved":
        return {UNRESOLVED}  # every unresolved reviewer is one person, however many drafts carry it (v2.4)
    if rev and rev not in NON_PERSON:
        return {rev}
    return set()
