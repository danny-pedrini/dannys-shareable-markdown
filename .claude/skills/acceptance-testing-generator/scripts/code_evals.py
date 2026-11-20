#!/usr/bin/env python3
"""Run the acceptance-testing-generator code evals and code prefilters.

Reads the document, the working-sections file, the Step 5 inventory, and the
requirement source. Prints one compact results table, the judge candidates,
and, when judge results are supplied, the new Active Evals table and the JSONL
log line. Writes nothing: Bash writes inside .claude/skills/ are denied, so the
parent pastes the printed table and line in with one Edit each.

Any change to an eval definition in evals.md must update this script in the
same change. Eval H2 checks that the report lists every active code eval ID
exactly once.

Usage (Step 11, first pass):
  python3 scripts/code_evals.py --doc DOC --mode comprehensive \
      --source PRD.md --working working-sections.md --inventory inventory.md

Usage (Step 11, second pass, after the parent runs the judge evals):
  python3 scripts/code_evals.py ... --judge '{"A4":"P","B1":"F: test 5 has no PRD basis"}' \
      --log-fields '{"ts":"2026-11-06T19:00:00Z","input_summary":"...","outcome":"success"}'

Usage (Step 13, UAT only, after the trace copy):
  python3 scripts/code_evals.py --doc DOC --mode uat --only H3 --trace TRACE.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_EVALS = SKILL_DIR / "evals.md"

ID_RE_DEFAULT = r"\b[A-Z]{2,5}-[0-9]{2,3}[a-z]?\b"
CLOSED_TAGS = {"[Staging]", "[UAT]", "[Prod]", "[Design]", "[Clinical]", "[Eng]"}
EXECUTOR_TAGS = {"[Design]", "[Clinical]", "[Eng]"}
COMP_COLS = ["Test #", "Req ID", "Area/Theme", "Requires Design", "Validation and Behavior", "Pass/Fail Note"]
UAT_COLS = ["Test #", "Area/Theme", "Validation and Behavior", "Pass/Fail Note"]
DEGRADED_KEYWORDS = [
    "no consent", "no response", "timeout", "time out", "service down", "below threshold",
    "unconfigured", "fallback", "as it does today", "bau", "fails", "failure", "unavailable",
    "couldn't", "cannot", "error",
]
STOPWORDS = {
    "about", "after", "again", "their", "there", "these", "those", "which", "while", "would",
    "should", "could", "where", "being", "other", "every", "within", "without", "never",
    "provider", "providers", "patient", "patients", "shows", "show", "test", "tests",
}
A5_RE = re.compile(
    r"pass rate|gold set|clinically appropriate|clinically correct|accuracy|precision|recall|"
    r"judge score|eval score|model quality|correct recommendation", re.I)
B2_RE = re.compile(
    r"[0-9]+(\.[0-9]+)?\s*(ms|s|sec|second|minute|min|hour|day|%|percent|character|item)s?\b", re.I)
C1_RE = re.compile(
    r"works correctly|works as expected|behaves as expected|behaves properly|is accurate|is correct|"
    r"performs well|is intuitive|is user.friendly|is reliable|functions correctly|as appropriate|"
    r"handled properly|displays correctly", re.I)
E5_RANGE_RE = re.compile(r"[0-9]+\s*(to|-)\s*[0-9]+")
E5_WORDS_RE = re.compile(
    r"utilize|leverage|facilitate|in order to|prior to|subsequently|delve|landscape|ecosystem|"
    r"It.s worth noting|moving forward|going forward", re.I)
G2_RE = re.compile(
    r"per the source|the source (says|states|asks|requires|directs|excludes|includes|omits)|"
    r"as the source|source (calls for|leaves)|deliberately (excluded|omitted) per", re.I)
B3_SUBSTITUTIONS = [
    ("center pane", "summary card"), ("completeness check", "chart validator"), ("held", "queued"),
    ("codified definition", "clinical rules"), ("next action", "recommendation"),
]
B3_STOP = {"NOTE", "TODO", "TBD", "PRD", "UAT", "EMR", "API", "JSON", "HTML", "AND", "THE", "WITH"}


# ---------------------------------------------------------------- parsing

def read(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def split_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    cells = re.split(r"(?<!\\)\|", body)
    return [c.strip() for c in cells]


def is_separator(line: str) -> bool:
    return bool(re.match(r"^\|\s*:?-{3,}", line.strip()))


def clean_id(cell: str) -> str:
    text = re.sub(r"~~|\*\*|➕|🔄", "", cell).strip()
    return text.split()[0] if text else ""


def tables(text: str) -> list[dict]:
    """Every markdown table: header cells, rows, start line, and heading above it."""
    out, lines, heading = [], text.splitlines(), ""
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^#{1,6} ", line):
            heading = line.lstrip("#").strip()
        if line.strip().startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1]):
            header = [re.sub(r"\*\*", "", c) for c in split_row(line)]
            rows, j = [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append((j + 1, split_row(lines[j]), lines[j]))
                j += 1
            out.append({"header": header, "rows": rows, "line": i + 1, "heading": heading})
            i = j
            continue
        i += 1
    return out


def test_tables(text: str) -> list[dict]:
    return [t for t in tables(text) if t["header"] and t["header"][0] == "Test #"]


def test_rows(text: str, mode: str) -> list[dict]:
    """Test rows, excluding bold category header rows."""
    rows = []
    for t in test_tables(text):
        hdr = t["header"]
        for lineno, cells, raw in t["rows"]:
            first = cells[0] if cells else ""
            tid = clean_id(first)
            is_header = first.startswith("**") and all(not c for c in cells[1:])
            if is_header or not tid:
                rows.append({"category": True, "line": lineno, "cells": cells, "raw": raw,
                             "heading": t["heading"], "header": hdr})
                continue
            row = {"category": False, "line": lineno, "cells": cells, "raw": raw, "id": tid,
                   "struck": "~~" in first, "heading": t["heading"], "header": hdr}
            for k, name in enumerate(hdr):
                row[name] = cells[k] if k < len(cells) else ""
            rows.append(row)
    return rows


def live_tests(rows: list[dict]) -> list[dict]:
    return [r for r in rows if not r["category"] and not r["struck"]]


def sections(text: str) -> dict[str, str]:
    """Heading text (level 2 and 3) mapped to its body."""
    out, current, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^#{2,3} (.+)$", line)
        if m:
            if current is not None:
                out[current] = "\n".join(buf)
            current, buf = m.group(1).strip(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        out[current] = "\n".join(buf)
    return out


def find_section(secs: dict[str, str], pattern: str) -> tuple[str, str] | None:
    for name, body in secs.items():
        if re.search(pattern, name, re.I):
            return name, body
    return None


def inventory_rows(text: str) -> list[dict]:
    for t in tables(text):
        hdr = [h.lower() for h in t["header"]]
        if hdr and hdr[0].startswith("req id"):
            out = []
            for _, cells, _ in t["rows"]:
                out.append({t["header"][k]: (cells[k] if k < len(cells) else "") for k in range(len(hdr))})
            return out
    return []


def col(row: dict, prefix: str) -> str:
    for k, v in row.items():
        if k.lower().startswith(prefix.lower()):
            return v
    return ""


def empty_cell(v: str) -> bool:
    return v.strip().lower() in {"", "-", "none", "n/a", "no", "none stated", "none named"}


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z'-]{4,}", text.lower()) if w not in STOPWORDS}


def norm_quotes(text: str) -> str:
    text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'")
    return re.sub(r"\s+", " ", text)


# ---------------------------------------------------------------- evals

class Ctx:
    def __init__(self, a):
        self.a = a
        self.mode = a.mode
        self.doc = read(a.doc)
        self.working = read(a.working)
        self.inventory_text = read(a.inventory)
        self.inventory = inventory_rows(self.inventory_text) if self.inventory_text else []
        self.sources = {p: read(p) for p in (a.source or [])}
        self.source_text = "\n".join(self.sources.values())
        self.prior = read(a.prior)
        self.id_re = re.compile(a.id_regex)
        self.rows = test_rows(self.doc, self.mode)
        self.live = live_tests(self.rows)
        self.secs = sections(self.doc)
        self.shared = a.shared == "yes"

    def validation(self, r: dict) -> str:
        return r.get("Validation and Behavior", "")

    def cites(self, r: dict) -> str:
        if self.mode == "comprehensive":
            return r.get("Req ID", "")
        return self.validation(r)

    def in_scope(self) -> list[str]:
        if self.a.in_scope:
            return [x.strip() for x in self.a.in_scope.split(",") if x.strip()]
        if self.inventory:
            ids = []
            for row in self.inventory:
                ids += self.id_re.findall(col(row, "Req ID"))
            return sorted(set(ids))
        return sorted(set(self.id_re.findall(self.source_text)))


def r_(result: str, detail: str = "", candidates: list[str] | None = None) -> dict:
    return {"r": result, "detail": detail, "candidates": candidates or []}


def ev_a1(c: Ctx) -> dict:
    scope = c.in_scope()
    if not scope:
        return r_("S", "no in-scope requirement IDs found; pass --in-scope or --inventory")
    found = set()
    for r in c.live:
        found |= set(c.id_re.findall(c.cites(r)))
    if c.mode == "comprehensive":
        cov = find_section(sections(c.working), r"coverage")
        found |= set(c.id_re.findall(cov[1] if cov else c.working))
    else:
        scope_sec = find_section(c.secs, r"^scope")
        found |= set(c.id_re.findall(scope_sec[1] if scope_sec else ""))
    missing = [i for i in scope if i not in found]
    if missing:
        return r_("F", "untraced: " + ", ".join(missing))
    return r_("P", f"{len(scope)} of {len(scope)} in-scope IDs accounted for")


def ev_a2(c: Ctx) -> dict:
    if not c.inventory:
        return r_("S", "Step 5 inventory not retained")
    misses = []
    for row in c.inventory:
        path = col(row, "Degraded")
        if empty_cell(path):
            continue
        rid = c.id_re.findall(col(row, "Req ID"))
        kws = [k for k in DEGRADED_KEYWORDS if k in path.lower()] or list(words(path))[:6]
        hit = False
        for t in c.live:
            text = (c.cites(t) + " " + t.get("Area/Theme", "") + " " + c.validation(t)).lower()
            if rid and not any(i.lower() in text for i in rid):
                continue
            if any(k in text for k in kws):
                hit = True
                break
        if not hit:
            misses.append(f"{'/'.join(rid) or '?'}: {path[:80]}")
    if misses:
        return r_("F", "no test for: " + "; ".join(misses))
    return r_("P", "every inventory degraded path has a test")


def ev_a3(c: Ctx) -> dict:
    if not c.inventory:
        return r_("S", "Step 5 inventory not retained")
    items = [col(row, "Non-goal") for row in c.inventory if not empty_cell(col(row, "Non-goal"))]
    if not items:
        return r_("S", "requirements declare no non-goals or out-of-scope items")
    hits = []
    for t in c.live:
        cite, area = c.cites(t), t.get("Area/Theme", "")
        if re.search(r"out of scope|non-goal", cite, re.I) and c.mode == "comprehensive":
            hits.append(f"test {t['id']}: Req ID cites scope item")
        elif re.search(r"scope\s*-\s*no\b", area, re.I):
            hits.append(f"test {t['id']}: absence check on a scope item")
        else:
            aw = words(re.sub(r"\*\*", "", area))
            for item in items:
                if len(aw & words(item)) >= 2:
                    hits.append(f"test {t['id']}: Area/Theme overlaps non-goal '{item[:50]}'")
                    break
    if hits:
        return r_("F", "; ".join(hits))
    return r_("P", f"{len(items)} non-goal items, no live test traces to one")


def ev_a5(c: Ctx) -> dict:
    cands = [f"test {t['id']} (line {t['line']}): {m.group(0)}"
             for t in c.live for m in A5_RE.finditer(c.validation(t))]
    if c.mode == "comprehensive":
        sec = find_section(c.secs, r"^purpose")
    else:
        sec = find_section(c.secs, r"out of scope") or find_section(c.secs, r"^scope")
    body = sec[1] if sec else ""
    present = bool(re.search(r"\b(AI|model|eval)\b.*\b(quality|eval|accuracy|owned|owner)", body, re.I))
    if c.a.ai == "unknown":
        return r_("J", "AI-behavior determination not supplied (--ai); judge the exclusion presence", cands)
    want = c.a.ai == "yes"
    if present and not want:
        return r_("F", "AI-scope exclusion present on a feature with no AI behavior")
    if want and not present:
        return r_("F", "AI-scope exclusion missing on an AI feature")
    if cands:
        return r_("J", "exclusion check passed; judge each hit: mechanism or measurement", cands)
    return r_("P", "no measurement phrases; exclusion matches the AI determination")


def ev_b2(c: Ctx) -> dict:
    fails = []
    for t in c.live:
        v = c.validation(t)
        if "[Assumption:" in v or "[estimate range]" in v:
            continue
        for m in B2_RE.finditer(v):
            num = re.match(r"[0-9]+(\.[0-9]+)?", m.group(0)).group(0)
            if not re.search(rf"(?<![0-9.]){re.escape(num)}(?![0-9])", c.source_text):
                fails.append(f"test {t['id']}: '{m.group(0)}' not in source")
    if not c.sources:
        return r_("S", "no --source supplied")
    if fails:
        return r_("F", "; ".join(fails))
    return r_("P", "every numeric pass condition appears in the source")


def ev_b3(c: Ctx) -> dict:
    if not c.sources:
        return r_("S", "no --source supplied")
    terms = set(t for t in re.findall(r"\b[A-Z][A-Z_]{3,}\b", c.source_text) if t not in B3_STOP)
    terms |= set(re.findall(r"`([^`\n]{2,40})`", c.source_text))
    terms |= set(re.findall(r"\*\*([^*\n]{3,40})\*\*", c.source_text))
    doc_l = c.doc.lower()
    cands = sorted(t for t in terms if t.lower().strip(" :.") not in doc_l)
    cands = [f"source term absent verbatim: {t}" for t in cands]
    src_l = c.source_text.lower()
    for orig, sub in B3_SUBSTITUTIONS:
        if orig in src_l and re.search(rf"\b{re.escape(sub)}\b", doc_l):
            cands.append(f"known substitution: doc uses '{sub}', source uses '{orig}'")
    if cands:
        return r_("J", f"{len(cands)} candidates for the judge", cands)
    return r_("P", "every candidate source term appears verbatim")


def ev_b4(c: Ctx) -> dict:
    lines = [ln for ln in c.doc.splitlines() if "[Source unreadable" in ln]
    unlinked = [ln[:80] for ln in lines if not re.search(r"https?://|/|\b[A-Z]+-\d+\b|\bid\b", ln, re.I)]
    failed = c.a.failed_source or []
    unmarked = [s for s in failed if not any(s in ln for ln in lines)]
    if unlinked or unmarked:
        parts = []
        if unlinked:
            parts.append("placeholder without link or ID: " + " | ".join(unlinked))
        if unmarked:
            parts.append("failed source not marked: " + ", ".join(unmarked))
        return r_("F", "; ".join(parts))
    if not failed:
        return r_("P", "no retrieval failure recorded")
    return r_("P", f"{len(failed)} failed sources marked with link or ID")


def ev_c1(c: Ctx) -> dict:
    hits = [f"test {t['id']}: {m.group(0)}" for t in c.live for m in C1_RE.finditer(c.validation(t))]
    if hits:
        return r_("F", "; ".join(hits))
    return r_("P", "no unqualified judgment phrases")


def ev_e1(c: Ctx) -> dict:
    want = COMP_COLS if c.mode == "comprehensive" else UAT_COLS
    issues = []
    tts = test_tables(c.doc)
    if not tts:
        return r_("F", "no acceptance tests table found")
    for t in tts:
        hdr = [h.strip() for h in t["header"]]
        if hdr != want:
            issues.append(f"line {t['line']}: header {hdr} != {want}")
    env_sec = find_section(c.secs, r"^purpose" if c.mode == "comprehensive" else r"^execution")
    env_body = env_sec[1] if env_sec else ""
    if c.mode == "comprehensive":
        if find_section(c.secs, r"^execution"):
            issues.append("Comprehensive has an Execution section")
        if not re.search(r"staging|uat|prod", env_body, re.I):
            issues.append("Purpose states no environment")
    else:
        if not env_sec:
            issues.append("UAT has no Execution section")
        elif not (re.search(r"setup by", env_body, re.I) and re.search(r"executed by", env_body, re.I)):
            issues.append("Execution lacks a document-level Setup By and Executed By")
    default_staging = bool(re.search(r"default[^.\n]*staging|staging[^.\n]*default", env_body, re.I))
    used_tags = set()
    prev_cat = None
    for r in c.rows:
        if r["category"]:
            if prev_cat is not None:
                issues.append(f"category header at line {prev_cat} has no tests")
            prev_cat = r["line"]
            continue
        prev_cat = None
        if r["struck"]:
            continue
        if not c.validation(r).strip():
            issues.append(f"test {r['id']}: empty Validation and Behavior")
        if c.mode == "comprehensive":
            if not r.get("Req ID", "").strip():
                issues.append(f"test {r['id']}: empty Req ID")
            if re.sub(r"\*\*", "", r.get("Requires Design", "")).strip() not in {"Yes", "No"}:
                issues.append(f"test {r['id']}: Requires Design not Yes or No")
        for tag in re.findall(r"\[[A-Za-z]+\]", r.get("Area/Theme", "")):
            used_tags.add(tag)
            if tag not in CLOSED_TAGS:
                issues.append(f"test {r['id']}: tag {tag} outside the closed six")
            if c.mode == "comprehensive" and tag in EXECUTOR_TAGS:
                issues.append(f"test {r['id']}: executor tag {tag} in Comprehensive")
            if tag == "[Staging]" and default_staging:
                issues.append(f"test {r['id']}: [Staging] restates the default")
            if tag not in env_body and tag.strip("[]") not in env_body:
                issues.append(f"test {r['id']}: tag {tag} not explained in the environment statement")
    if prev_cat is not None:
        issues.append(f"category header at line {prev_cat} has no tests")
    for t in tables(env_body):
        for _, cells, _ in t["rows"]:
            tag = re.search(r"\[[A-Za-z]+\]", cells[0] if cells else "")
            if tag and tag.group(0) not in used_tags:
                issues.append(f"legend entry {tag.group(0)} used by no row")
    if issues:
        return r_("F", "; ".join(dict.fromkeys(issues)))
    return r_("P", f"{len(tts)} test tables, columns and tags clean")


def id_key(tid: str) -> tuple[str, int, str]:
    m = re.match(r"^([A-Z]+-)?0*([0-9]+)([a-z]?)$", tid)
    if not m:
        return ("?", -1, tid)
    return (m.group(1) or "", int(m.group(2)), m.group(3))


def ev_e2(c: Ctx) -> dict:
    ids = [r["id"] for r in c.rows if not r["category"]]
    issues = []
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        issues.append("duplicate IDs: " + ", ".join(dupes))
    by_prefix: dict[str, list[tuple[int, str]]] = {}
    for i in ids:
        p, n, s = id_key(i)
        if n < 0:
            issues.append(f"unparseable ID {i}")
            continue
        by_prefix.setdefault(p, []).append((n, s))
    if not c.shared:
        for p, nums in by_prefix.items():
            if any(s for _, s in nums):
                issues.append(f"{p or 'numeric'}: sub-IDs before sharing")
            base = sorted({n for n, _ in nums})
            if base and base != list(range(1, max(base) + 1)):
                gaps = sorted(set(range(1, max(base) + 1)) - set(base))
                issues.append(f"{p or 'numeric'} gaps: {gaps}")
    elif c.prior:
        prior_ids = {r["id"] for r in test_rows(c.prior, c.mode) if not r["category"]}
        gone = sorted(prior_ids - set(ids))
        if gone:
            issues.append("shared IDs removed instead of struck: " + ", ".join(gone))
    if issues:
        return r_("F", "; ".join(issues))
    note = "" if (not c.shared or c.prior) else "; reuse not diffed (no --prior)"
    return r_("P", f"{len(ids)} IDs unique{note}")


E3_REQUIRED = {
    "comprehensive": [r"^purpose", r"model these criteria assume", r"^acceptance tests",
                      r"test data", r"environment prerequisites", r"sign-?off", r"revision markers"],
    "uat": [r"^purpose", r"model these criteria assume", r"^execution", r"^scope", r"^acceptance tests",
            r"test data", r"sign-?off", r"revision markers"],
}
E3_FORBIDDEN = {
    "comprehensive": [r"^source", r"^execution", r"^scope", r"precedence", r"discrepanc",
                      r"tests beyond", r"potential requirement gaps", r"coverage", r"key success",
                      r"appendix", r"what is it"],
    "uat": [r"coverage", r"dedup", r"candidate requirements", r"environment prerequisites",
            r"key success", r"appendix", r"what is it", r"discrepanc"],
}


def ev_e3(c: Ctx) -> dict:
    issues = []
    for pat in E3_REQUIRED[c.mode]:
        hit = find_section(c.secs, pat)
        if not hit:
            issues.append(f"missing section /{pat}/")
        elif not re.sub(r"\s|\|", "", hit[1]) and not re.search(r"tests", pat):
            issues.append(f"empty section '{hit[0]}'")
    for pat in E3_FORBIDDEN[c.mode]:
        hit = find_section(c.secs, pat)
        if hit:
            issues.append(f"section must not appear: '{hit[0]}'")
    if c.mode == "comprehensive" and re.search(r"(requirements|mocks) win", c.doc, re.I):
        issues.append("Comprehensive publishes a precedence sentence")
    if c.mode == "uat" and not re.search(r"(requirements|mocks) win|source of truth|precedence", c.doc, re.I):
        issues.append("UAT states no source precedence")
    has_log = bool(find_section(c.secs, r"change log"))
    if c.shared and not has_log:
        issues.append("shared doc has no Change log")
    if not c.shared and has_log:
        issues.append("Change log on a doc not yet shared")
    if c.mode == "uat":
        for t in test_tables(c.doc):
            text = " ".join(raw for _, _, raw in t["rows"])
            if not re.search(r"launch|smoke", text, re.I):
                issues.append(f"section '{t['heading']}' has no launch-readiness or smoke test")
    if issues:
        return r_("F", "; ".join(issues))
    return r_("P", "required sections present, forbidden sections absent")


def ev_e4(c: Ctx) -> dict:
    pats = {
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "phone": r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b",
        "email": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
        "DOB": r"\b(0?[1-9]|1[0-2])/(0?[1-9]|[12]\d|3[01])/(19|20)\d{2}\b|\bDOB\b|date of birth",
        "long digits": r"\b\d{7,}\b",
    }
    cands = []
    for n, line in enumerate(c.doc.splitlines(), 1):
        for name, pat in pats.items():
            if re.search(pat, line, re.I) and not re.search(r"https?://", line):
                cands.append(f"line {n}: {name}")
    td = find_section(c.secs, r"test data")
    cands.append("judge names paired with clinical detail in '" + (td[0] if td else "Test data requirements") + "'")
    return r_("J", f"{len(cands) - 1} identifier-pattern hits", cands)


def ev_e5(c: Ctx) -> dict:
    hits = []
    for n, line in enumerate(c.doc.splitlines(), 1):
        if "\u2014" in line:
            hits.append(f"line {n}: em dash")
        if E5_RANGE_RE.search(line) and "[estimate range]" not in line and "[Assumption:" not in line:
            for m in E5_RANGE_RE.finditer(line):
                if not re.search(r"\d{4}-\d{2}-\d{2}", line[max(0, m.start() - 6):m.end() + 6]):
                    hits.append(f"line {n}: untagged range '{m.group(0)}'")
                    break
        for m in E5_WORDS_RE.finditer(line):
            hits.append(f"line {n}: '{m.group(0)}'")
    if hits:
        return r_("F", "; ".join(hits))
    return r_("P", "clean")


def expand_ids(text: str) -> list[str]:
    out = []
    for m in re.finditer(r"\b[Tt]ests? ([0-9]+[a-z]?(?:(?: ?, ?| and | to | through )[0-9]+[a-z]?)*)", text):
        chunk = m.group(1)
        for a, b in re.findall(r"([0-9]+) (?:to|through) ([0-9]+)", chunk):
            out += [str(x) for x in range(int(a), int(b) + 1)]
        chunk = re.sub(r"[0-9]+ (?:to|through) [0-9]+", "", chunk)
        out += re.findall(r"[0-9]+[a-z]?", chunk)
    return out


def ev_f1(c: Ctx) -> dict:
    defined = {r["id"] for r in c.rows if not r["category"]}
    oq = set()
    for text in c.sources.values():
        sec = find_section(sections(text), r"still open")
        if sec:
            oq |= set(re.findall(r"^\|\s*([0-9]+)\s*\|", sec[1], re.M))
    heads = {re.sub(r"^(the|a|an) ", "", h.lower()) for h in c.secs}
    dangling = []
    for n, line in enumerate(c.doc.splitlines(), 1):
        if re.match(r"^\|\s*(~~)?[0-9A-Z]", line) and line.count("|") > 3:
            body = "|".join(split_row(line)[1:])
        else:
            body = line
        for tid in expand_ids(body):
            if tid not in defined:
                dangling.append(f"line {n}: test {tid}")
        for q in re.findall(r"PRD Open question ([0-9]+)", body):
            if q not in oq:
                dangling.append(f"line {n}: PRD Open question {q}")
        for s in re.findall(r'(?:the|in the|see the) [`"]([^"`]{3,40})[`"] section', body, re.I):
            if re.sub(r"^(the|a|an) ", "", s.lower()) not in heads:
                dangling.append(f"line {n}: section '{s}'")
    if dangling:
        return r_("F", "; ".join(dangling))
    return r_("P", "every cited test, open question, and quoted section resolves")


def ev_f2(c: Ctx) -> dict:
    if not c.a.multi_source:
        return r_("S", "single-source run")
    issues, owner = [], {}
    by_section: dict[str, set[str]] = {}
    for r in c.rows:
        if r["category"]:
            continue
        p = id_key(r["id"])[0]
        by_section.setdefault(r["heading"], set()).add(p)
    for sec, prefixes in by_section.items():
        if len(prefixes) != 1:
            issues.append(f"section '{sec}' mixes prefixes {sorted(prefixes)}")
        for p in prefixes:
            if p in owner and owner[p] != sec:
                issues.append(f"prefix {p} used by '{owner[p]}' and '{sec}'")
            owner.setdefault(p, sec)
    if c.prior:
        prior_owner = {}
        for r in test_rows(c.prior, c.mode):
            if not r["category"]:
                prior_owner.setdefault(id_key(r["id"])[0], r["heading"])
        for p, sec in owner.items():
            if p in prior_owner and prior_owner[p] != sec:
                issues.append(f"prefix {p} moved from '{prior_owner[p]}' to '{sec}'")
    if issues:
        return r_("F", "; ".join(issues))
    return r_("P", f"{len(owner)} prefixes, one per section")


def ev_f3(c: Ctx) -> dict:
    if not c.shared:
        return r_("S", "document not yet shared")
    if not c.prior:
        return r_("S", "prior shared version not supplied (--prior)")
    old = {r["id"]: r for r in test_rows(c.prior, c.mode) if not r["category"]}
    new = {r["id"]: r for r in c.rows if not r["category"]}
    issues = []
    for tid, r in new.items():
        if tid not in old and "➕" not in r["raw"]:
            issues.append(f"test {tid}: added without ➕")
        elif tid in old and not r["struck"]:
            if norm_quotes(c.validation(old[tid])) != norm_quotes(c.validation(r)) and "🔄" not in r["raw"]:
                issues.append(f"test {tid}: changed without 🔄")
        if r["struck"] and not re.search(r"(covered|see|moved|replaced|by test)", r["raw"], re.I):
            issues.append(f"test {tid}: struck with no reason or pointer")
    for tid in old:
        if tid not in new:
            issues.append(f"test {tid}: removed instead of struck")
    if issues:
        return r_("F", "; ".join(issues))
    return r_("P", "every difference from the prior shared version is marked")


def ev_g1(c: Ctx) -> dict:
    src = norm_quotes(c.source_text)
    cands = []
    for n, line in enumerate(c.doc.splitlines(), 1):
        for span in re.findall(r'"([^"]+)"', norm_quotes(line)):
            if len(span.split()) >= 4 and span not in src:
                cands.append(f"line {n}: \"{span[:90]}\"")
    if not c.sources:
        return r_("J", "no --source supplied; every span is a candidate", cands)
    if cands:
        return r_("J", f"{len(cands)} spans with no verbatim source match", cands)
    return r_("P", "every quoted span of 4+ words matches a source verbatim")


def ev_g2(c: Ctx) -> dict:
    cands = []
    for n, line in enumerate(c.doc.splitlines(), 1):
        for m in G2_RE.finditer(line):
            cands.append(f"line {n}: {line.strip()[:120]}")
            break
    if cands:
        return r_("J", f"{len(cands)} directive claims to check against the source", cands)
    return r_("P", "no source-directive claims")


def ev_g3(c: Ctx) -> dict:
    tests = {r["id"]: r for r in c.rows if not r["category"]}
    cands = []
    for label, text in (("doc", c.doc), ("working", c.working)):
        for t in tables(text):
            if t["header"] and t["header"][0] == "Test #":
                continue
            for lineno, _, raw in t["rows"]:
                for tid in expand_ids(raw):
                    if tid in tests:
                        cands.append(f"{label} line {lineno} cites test {tid} (doc line {tests[tid]['line']})")
    if cands:
        return r_("J", f"{len(cands)} meta-row and test pairs", cands)
    return r_("P", "no meta-row cites a test")


def ev_h2(c: Ctx, report_ids: list[str], active_code: list[str]) -> dict:
    missing = [i for i in active_code if report_ids.count(i) == 0]
    dupes = [i for i in active_code if report_ids.count(i) > 1]
    if missing or dupes:
        return r_("F", f"missing {missing}, duplicated {dupes}")
    return r_("P", f"{len(active_code)} active code eval IDs, each listed once")


def ev_h3(c: Ctx) -> dict:
    if c.mode != "uat":
        return r_("S", "Comprehensive run")
    if not c.a.trace:
        return r_("S", "trace not yet written; run with --trace after the Step 13 copy")
    trace = json.loads(read(c.a.trace))
    paths = [str(s.get("path", "")) + " " + str(s.get("id", "")) for s in trace.get("context_sources", [])]
    if any("references/uat-mode.md" in p for p in paths):
        return r_("P", "context_sources includes references/uat-mode.md")
    return r_("F", "context_sources lacks references/uat-mode.md")


CODE_EVALS = {
    "A1": ev_a1, "A2": ev_a2, "A3": ev_a3, "A5": ev_a5, "B2": ev_b2, "B3": ev_b3, "B4": ev_b4,
    "C1": ev_c1, "E1": ev_e1, "E2": ev_e2, "E3": ev_e3, "E4": ev_e4, "E5": ev_e5, "F1": ev_f1,
    "F2": ev_f2, "F3": ev_f3, "G1": ev_g1, "G2": ev_g2, "G3": ev_g3, "H3": ev_h3,
}


# ---------------------------------------------------------------- evals.md

def active_table(evals_text: str) -> tuple[list[str], list[dict]]:
    """Raw lines of the Active Evals table, and its parsed rows."""
    lines = evals_text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip() == "## Active Evals")
    t = next(t for t in tables("\n".join(lines[start:])) if t["header"][:2] == ["ID", "Name"])
    raw = [lines[start + t["line"] - 1], lines[start + t["line"]]] + [r[2] for r in t["rows"]]
    rows = [dict(zip(t["header"], cells)) for _, cells, _ in t["rows"]]
    return raw, rows


def last_result(r: str, detail: str, date: str, old: str) -> str:
    if r == "P":
        return f"Pass ({date})"
    if r == "F":
        return f"Fail ({date}, {detail})" if detail else f"Fail ({date})"
    if r == "S":
        return f"Skipped ({date}, {detail})" if detail else f"Skipped ({date})"
    return old


def parse_judge(arg: str | None) -> dict[str, tuple[str, str]]:
    if not arg:
        return {}
    data = json.loads(Path(arg).read_text() if Path(arg).is_file() else arg)
    out = {}
    for k, v in data.items():
        m = re.match(r"^\s*([PFS])\s*:?\s*(.*)$", str(v))
        if not m:
            raise SystemExit(f"--judge value for {k} must start with P, F, or S")
        out[k] = (m.group(1), m.group(2).strip())
    return out


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doc", required=True, help="the written acceptance testing document")
    ap.add_argument("--mode", required=True, choices=["comprehensive", "uat"])
    ap.add_argument("--source", action="append", help="requirement source file; repeat the flag per file")
    ap.add_argument("--working", help="working-sections.md from the session scratchpad")
    ap.add_argument("--inventory", help="the retained Step 5 inventory")
    ap.add_argument("--prior", help="prior shared version of the document (E2, F2, F3)")
    ap.add_argument("--shared", choices=["yes", "no"], default="no", help="intake answer")
    ap.add_argument("--ai", choices=["yes", "no", "unknown"], default="unknown", help="Step 5 AI determination")
    ap.add_argument("--multi-source", action="store_true", help="UAT run over more than one requirement document")
    ap.add_argument("--failed-source", action="append", help="ID or link of a source that failed retrieval")
    ap.add_argument("--in-scope", help="comma-separated in-scope requirement IDs; default from the inventory")
    ap.add_argument("--id-regex", default=ID_RE_DEFAULT, help="requirement ID pattern")
    ap.add_argument("--trace", help="committed trace file (H3)")
    ap.add_argument("--evals", default=str(DEFAULT_EVALS), help="evals.md path")
    ap.add_argument("--only", help="comma-separated eval IDs to run")
    ap.add_argument("--judge", help="JSON object or file of judge results, e.g. {\"A4\":\"P\"}")
    ap.add_argument("--log-fields", help="JSON object of invocation-log fields to merge")
    ap.add_argument("--date", default=dt.date.today().isoformat(), help="date for Last Result")
    a = ap.parse_args()

    c = Ctx(a)
    evals_raw, evals_rows = active_table(read(a.evals))
    active = [row["ID"] for row in evals_rows]
    active_code = [row["ID"] for row in evals_rows if "Code" in row.get("Check", "")]
    only = {x.strip() for x in a.only.split(",")} if a.only else None
    judge = parse_judge(a.judge)

    results: dict[str, dict] = {}
    for eid in active:
        if only and eid not in only:
            continue
        if eid == "H2":
            continue
        if eid in CODE_EVALS:
            try:
                results[eid] = CODE_EVALS[eid](c)
            except Exception as exc:  # a crash is a visible skip, never a silent pass
                results[eid] = r_("S", f"script error: {exc}")
        elif eid in active_code:
            results[eid] = r_("S", "no script implementation")
        else:
            results[eid] = r_("J", "pure judge, run in the parent")
    if not only:
        results["H2"] = ev_h2(c, list(results) + ["H2"], active_code)
    ordered = [e for e in active if e in results]

    for eid, (r, detail) in judge.items():
        if eid in results and results[eid]["r"] == "J":
            results[eid] = r_(r, detail)

    counts = {k: sum(1 for e in ordered if results[e]["r"] == k) for k in "PFSJ"}
    print(f"**Code evals: {len(ordered)} listed, {counts['P']} passed, {counts['F']} failed, "
          f"{counts['S']} skipped, {counts['J']} awaiting judge**\n")
    print("| Eval | Result | Detail |\n| --- | --- | --- |")
    for e in ordered:
        print(f"| {e} | {results[e]['r']} | {results[e]['detail'].replace('|', '/')} |")

    pending = [e for e in ordered if results[e]["r"] == "J"]
    if pending:
        print("\n## Judge candidates\n")
        for e in pending:
            print(f"### {e}: {results[e]['detail']}")
            for cand in results[e]["candidates"] or ["(no prefilter: judge the whole document)"]:
                print(f"- {cand}")
            print()
        if judge or a.log_fields:
            print(f"Judge results still missing for: {', '.join(pending)}. Supply them with --judge.",
                  file=sys.stderr)
        return 0

    print("\n## Active Evals table (paste with one Edit)\n")
    print(evals_raw[0])
    print(evals_raw[1])
    for raw, row in zip(evals_raw[2:], evals_rows):
        eid = row["ID"]
        cells = split_row(raw)
        if eid in results:
            cells[-1] = last_result(results[eid]["r"], results[eid]["detail"], a.date, cells[-1])
        print("| " + " | ".join(cells) + " |")

    log = {
        "ts": None, "skill": "acceptance-testing-generator", "input_summary": None, "duration_s": None,
        "tool_calls": None, "outcome": None, "notes": None, "version": None,
        "mode": "Comprehensive" if a.mode == "comprehensive" else "UAT",
        "eval_results": [{"id": e, "r": results[e]["r"]} for e in ordered],
        "assignment_edits": None, "assignment_total": None,
    }
    if a.log_fields:
        extra = json.loads(Path(a.log_fields).read_text() if Path(a.log_fields).is_file() else a.log_fields)
        extra.pop("eval_results", None)
        log.update(extra)
    print("\n## Invocation log line (append with one Edit)\n")
    print(json.dumps(log, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
