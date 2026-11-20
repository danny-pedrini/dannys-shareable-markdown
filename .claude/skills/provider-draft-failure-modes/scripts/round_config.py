"""Shared helper every script in this folder imports. Run with `python3 -I`, which keeps the
script's own directory and the current directory off `sys.path`, so every script inserts both
explicitly before importing a sibling script or a round-folder defs file:

    import os, sys
    HERE = os.path.dirname(os.path.abspath(__file__))
    ROOT = os.getcwd()
    sys.path.insert(0, HERE)   # sibling scripts in this folder (round_config, mechanical_check, ...)
    sys.path.insert(0, ROOT)   # round-folder defs files (cluster_defs.py, report_defs.py)

No round-specific content lives here: every round fact comes from `round.json` in the current
directory (the round folder), never from a literal in this file.
"""
import glob
import json
import os
import re
import sys


def load(path="round.json"):
    """Read round.json from the current directory. Exits with a clear message if it is missing
    or malformed; scripts never guess a round fact that round.json does not supply."""
    if not os.path.exists(path):
        print(f"round_config: {path} not found in {os.getcwd()} (run scripts from the round folder)", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path) as fh:
            cfg = json.load(fh)
    except json.JSONDecodeError as e:
        print(f"round_config: {path} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    if SPREAD_CODE in batch_codes(cfg) or SPREAD_CODE in [s.get("code") for s in cfg.get("sources", [])]:
        print(f"round_config: {SPREAD_CODE} is reserved for spread rows in row-map.md; "
              f"rename that batch or source code in {path}", file=sys.stderr)
        sys.exit(1)
    return cfg


SPREAD_CODE = "SP"
SOURCE_KINDS = ("thumbs-downs", "labeling", "edits", "evals", "interviews", "slack")
SHEET_KINDS = ("thumbs-downs", "labeling", "edits")


def sources(cfg):
    """Every source, as round.json `sources[]` gives it. A legacy round (no `sources[]`) reads its
    `ratings` block as one source, of kind `edits` when the round has an `edits_pass` block and
    `thumbs-downs` otherwise, with code None. Each legacy `extra_sources` entry reads as an
    `interviews` source with its batch code and no `providers` map; its free-text `kind` is ignored."""
    if "sources" in cfg:
        return list(cfg["sources"])
    out = []
    if cfg.get("ratings"):
        kind = "edits" if cfg.get("edits_pass") else "thumbs-downs"
        out.append(dict(cfg["ratings"], code=None, kind=kind, legacy=True))
    for e in cfg.get("extra_sources", []) or []:
        out.append({"code": e.get("code"), "kind": "interviews", "file": e.get("file"), "legacy": True})
    return out


def sources_of_kind(cfg, *kinds):
    return [s for s in sources(cfg) if s.get("kind") in kinds]


def session_batches(cfg):
    """Batch codes whose rows are interview sessions (an `interviews` source, or a batch whose
    action is `feedback_session`)."""
    codes = {s.get("code") for s in sources_of_kind(cfg, "interviews")}
    codes |= {b["code"] for b in batches(cfg) if b.get("action") == "feedback_session"}
    return {c for c in codes if c}


def session_provider(cfg, batch, handle):
    """The provider an interview row's Reviewer stands for. A rater handle (in `reviewers[]` or
    a map value) is itself. A session handle takes its value from any interviews source's
    `providers` map, or is itself when it maps to null. A handle no map holds is
    `unresolved:<handle>` when any source has a map; with no maps (legacy), it is itself. Session
    handles are stable across a round's interviews sources, so one handle gives one provider."""
    maps = [s.get("providers") or {} for s in sources_of_kind(cfg, "interviews") if "providers" in s]
    if handle in reviewers(cfg) or any(handle in m.values() for m in maps):
        return handle
    for m in maps:
        if handle in m:
            return m[handle] or handle
    return f"unresolved:{handle}" if maps else handle


def batches(cfg):
    """The batches list, in round.json order."""
    return cfg.get("batches", [])


def batch_codes(cfg):
    return [b["code"] for b in batches(cfg)]


def action_map(cfg):
    """code -> action (the prompt action name, used in ticket titles)."""
    return {b["code"]: b["action"] for b in batches(cfg)}


def label_map(cfg):
    """code -> label (the human batch name, e.g. 'Prescribe (initial)')."""
    return {b["code"]: b.get("label", b["code"]) for b in batches(cfg)}


def batch_cap(cfg):
    return cfg.get("batch_cap", 16)


def reviewers(cfg):
    return cfg.get("reviewers", [])


def product_reviewer(cfg):
    return cfg.get("product_reviewer")


def jira_site(cfg):
    return cfg.get("jira", {}).get("site", "").rstrip("/")


def jira_browse(cfg, key):
    site = jira_site(cfg)
    return f"{site}/browse/{key}" if site else key


def jira_project(cfg):
    return cfg.get("jira", {}).get("project")


def jira_epic(cfg):
    return cfg.get("jira", {}).get("epic")


def report_paths(cfg):
    r = cfg.get("report", {})
    return r.get("file"), r.get("csv")


def evidence_opener(cfg):
    return cfg.get("evidence_opener", "")


def source_links(cfg):
    return cfg.get("source_links", [])


def scope(cfg):
    return cfg.get("scope", {})


def conflict_flags_in_scope(cfg):
    return bool(scope(cfg).get("conflict_flags_in_scope", False))


def draft_and_thread_in_scope(cfg):
    return bool(scope(cfg).get("draft_and_thread", True))


def generation(cfg):
    return cfg.get("generation", {})


EXPORT_TRACE_RE = re.compile(r"^\*Trace (tr-[0-9a-fA-F]{32})\s*·\s*Medication: [^*]*\*", re.M)


def prior_round_dirs(cfg):
    """Absolute folders of the rounds in `prior_rounds` (paths relative to the round folder,
    oldest first). A folder that does not exist is still listed; callers decide what that means."""
    return [os.path.abspath(p) for p in cfg.get("prior_rounds", []) or []]


def prior_round_exports(cfg):
    """{full trace ID: (export file path, action)} for every record in each prior round's
    `export/*.md` (the same record format as this round's export). The action comes from that
    round's own round.json `batches[]` when the file's stem is a batch code there, else the stem.
    A trace in two prior exports takes the later round's record. Used by `check_tickets.py
    --traces` and `make_thread_blocks.py` to resolve an `Earlier round:` Evidence bullet (v2.4)."""
    out = {}
    for d in prior_round_dirs(cfg):
        actions = {}
        try:
            with open(os.path.join(d, "round.json")) as fh:
                actions = {b["code"]: b.get("action", b["code"]) for b in json.load(fh).get("batches", [])}
        except (OSError, ValueError, KeyError, TypeError):
            pass
        for path in sorted(glob.glob(os.path.join(d, "export", "*.md"))):
            stem = os.path.splitext(os.path.basename(path))[0]
            with open(path) as fh:
                text = fh.read()
            for m in EXPORT_TRACE_RE.finditer(text):
                out[m.group(1)] = (path, actions.get(stem, stem))
    return out


def judges_doc(cfg):
    return cfg.get("judges_doc")


def repo_root():
    """The repo root, found from this script's location (<repo>/.claude/skills/<skill>/scripts/),
    so repo-relative paths in round.json resolve from any round folder, including a scratch copy."""
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))


def repo_path(rel):
    """Absolute path for a repo-root-relative path from round.json, or None."""
    return os.path.join(repo_root(), rel) if rel else None


# ---------------------------------------------------------------------------
# Generic markdown-table parsing, shared by every script that reads a ledger,
# dedup verdict table, filing ledger, or any other pipe-delimited table. No
# script hand-rolls its own column-position parser against a format that can
# shift; this keys rows by header name instead.
# ---------------------------------------------------------------------------

def parse_tables(text):
    """Return every markdown table in `text` as a list of tables, each a list of row-dicts
    keyed by lower-cased header text. A table ends at the first non-`|` line (or EOF) after
    its header and separator row."""
    out = []
    header, rows = None, []

    def flush():
        if header is not None and rows:
            out.append(rows[:])

    for line in text.split("\n"):
        line = line.rstrip()
        if not line.startswith("|"):
            flush()
            header, rows[:] = None, []
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            rows = []
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue  # separator row
        rows.append({header[i]: (cells[i] if i < len(cells) else "") for i in range(len(header))})
    flush()
    return out


def parse_table_after(text, marker):
    """The first markdown table that starts after the literal substring `marker` (e.g. a
    section heading). Returns [] if the marker or a table after it is not found."""
    idx = text.find(marker)
    if idx < 0:
        return []
    tables = parse_tables(text[idx:])
    return tables[0] if tables else []


def gate3_dropped(consolidate=None):
    """FMs whose ticket the product owner dropped at Gate 3: the ticket-drafts.md "Not filed"
    Dropped rows and the tickets merged into them, mapped to FMs through ticket-plan.md, plus
    any FM `consolidate` (cluster_defs.CONSOLIDATE) folds into one of those. Empty before Gate 3."""
    if not (os.path.exists("ticket-drafts.md") and os.path.exists("ticket-plan.md")):
        return set()
    plan, merged_from, mf = {}, {}, None
    for l in open("ticket-plan.md"):
        if l.startswith("| Ticket |"):
            hdr = [c.strip().lower() for c in l.strip().strip("|").split("|")]
            mf = hdr.index("merged from") if "merged from" in hdr else None
            continue
        m = re.match(r"\| (T-\d+) \| (FM-\d+) \|", l)
        if m:
            plan[m.group(1)] = m.group(2)
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            if mf is not None and mf < len(cells):
                merged_from[m.group(1)] = re.findall(r"FM-\d+", cells[mf])
    text = open("ticket-drafts.md").read()
    if "## 2. Not filed" not in text:
        return set()
    absorbed, dropped = {}, set()
    for l in text.split("## 2. Not filed", 1)[1].split("\n## ", 1)[0].split("\n"):
        m = re.match(r"\|\s*(T-\d+)\s*\|\s*Merged into\s*(T-\d+)\s*\|", l)
        if m:
            absorbed[m.group(1)] = m.group(2)
        m = re.match(r"\|\s*(T-\d+)\s*\|\s*Dropped\b", l)
        if m:
            dropped.add(m.group(1))

    def ends_dropped(t):
        seen = {t}
        while t not in dropped and t in absorbed and absorbed[t] not in seen:
            t = absorbed[t]
            seen.add(t)
        return t in dropped
    ts = dropped | {a for a in absorbed if ends_dropped(a)}
    out = {f for t in ts for f in [plan.get(t)] + merged_from.get(t, []) if f}
    return out | {a for f in list(out) for a in (consolidate or {}).get(f, "").split()}


def col(row, name):
    """Fetch a column from a parsed row by case-insensitive prefix match on its header, the
    way the original Round 3 scripts did (so a header like 'Rating ref' still matches a lookup
    of 'rating ref', and a header with a footnote mark still matches a lookup of its prefix)."""
    name = name.lower()
    for k, v in row.items():
        if k.startswith(name):
            return v
    return ""
