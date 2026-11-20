"""E1: every trace any source names has one record in export/<code>.md, and where a sheet source
carries a draft column, each export draft matches it. Also checks that each export record has
the sections the other scripts parse: the trace/medication header line, "Last messages before
the draft", "Provider draft" (`(no draft generated)` when none was), "Explanation", plus
"Message the provider sent" on an edits trace, "Judge verdicts" on an evals trace and the
per-trace ratings table on a rated trace. Sections may come in any order after the header.

Traces a source names: rating rows and section 9 sheet rows in ratings.md; the trace IDs in an
evals source's saved file (a table with a Trace ID column); the full trace IDs in a Slack
source's saved file. A legacy edits round has no section 9, so its rated traces are its edits
traces.

Modes:
  python3 -I check_export.py                       full check, prints problems, exit 0/1
  python3 -I check_export.py --ids                  print every trace ID in export/, one per
                                                     line (full `tr-<32 hex>` form), exit 0.
                                                     Lets the format checker verify trace IDs
                                                     against the export without reading it.
  python3 -I check_export.py --ratings-file <path>  also compares each export draft against the
                                                     draft column in a saved raw sheet read (same
                                                     formats load_ratings.py accepts), when
                                                     round.json ratings.draft_column is set.

Run from the round folder:  python3 -I <skill>/scripts/check_export.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.getcwd()
sys.path.insert(0, HERE)
import round_config as RC  # noqa: E402
import load_ratings as LR  # noqa: E402

TRACE_HEADER_RE = re.compile(r"^\*Trace (tr-[0-9a-fA-F]{32})\s*·\s*Medication: [^*]*\*", re.M)
REQUIRED_SECTIONS = ["**Last messages before the draft**", "**Provider draft**", "**Explanation**"]
SECTION_HEADS = ["Last messages before the draft", "Provider draft", "Message the provider sent",
                 "Explanation", "Judge verdicts", "Ratings (from"]
HEAD_RE = re.compile(r"^\*\*(?:" + "|".join(re.escape(h) for h in SECTION_HEADS) + r")", re.M)
NO_DRAFT = "(no draft generated)"
NO_DRAFT_RE = re.compile(r"^\(no draft[^)]*\)$", re.I)  # legacy exports word the marker differently
TRACE_RE = re.compile(r"\btr-[0-9a-fA-F]{32}\b")
JUDGE_LINE_RE = re.compile(r"^- ([^:\n]+): (pass|fail)\b\.?\s*(.*)$", re.M | re.I)


def section_text(record_text, head):
    """The body of one record section, up to the next known section heading."""
    m = re.search(r"^\*\*" + re.escape(head) + r"[^\n]*\n", record_text, re.M)
    if not m:
        return None
    rest = record_text[m.end():]
    n = HEAD_RE.search(rest)
    return (rest[:n.start()] if n else rest).strip()


def judge_verdicts(record_text):
    """[(judge, verdict, reason)] from a record's Judge verdicts section."""
    body = section_text(record_text, "Judge verdicts") or ""
    return [(j.strip(), v.lower(), r.strip()) for j, v, r in JUDGE_LINE_RE.findall(body)]


def source_traces(cfg):
    """kind -> set of traces each source names (see the module docstring)."""
    out = {}
    srows = LR.source_rows("ratings.md") if os.path.exists("ratings.md") else []
    kind_of = {s.get("code"): s["kind"] for s in RC.sources_of_kind(cfg, *RC.SHEET_KINDS)}
    if srows:
        for r in srows:
            out.setdefault(kind_of.get(r["source"], "ratings"), set()).add(r["trace"])
        out["edits-sent"] = {r["trace"] for r in srows if kind_of.get(r["source"]) == "edits" and r["sent"] == "yes"}
    elif os.path.exists("ratings.md"):
        sheets = RC.sources_of_kind(cfg, *RC.SHEET_KINDS)
        kind = sheets[0]["kind"] if sheets else "ratings"
        out[kind] = {r["trace"] for r in LR.rating_rows("ratings.md")}
    for s in RC.sources_of_kind(cfg, "evals", "slack"):
        f = s.get("file")
        if not f or not os.path.exists(f):
            out.setdefault("missing-files", set()).add(f"{s.get('code')} ({s['kind']}): {f}")
            continue
        text = open(f).read()
        if s["kind"] == "evals":
            ts = {RC.col(r, "trace id") for t in RC.parse_tables(text) for r in t if RC.col(r, "trace id")}
        else:
            ts = set(TRACE_RE.findall(text))
        out.setdefault(s["kind"], set()).update(ts)
    return out


def export_records(code):
    path = os.path.join("export", f"{code}.md")
    if not os.path.exists(path):
        return None
    text = open(path).read()
    records = []
    for part in re.split(r"\n(?=## \d+\. )", text)[1:]:
        m = TRACE_HEADER_RE.search(part)
        records.append({"trace": m.group(1) if m else None, "text": part})
    return records


def all_export_traces(codes):
    out = {}
    for c in codes:
        recs = export_records(c)
        if recs is None:
            continue
        for r in recs:
            if r["trace"]:
                out[r["trace"]] = c
    return out


def cmd_ids(codes):
    traces = sorted(all_export_traces(codes))
    for t in traces:
        print(t)
    return 0


def draft_text_of(record_text):
    """The draft text, or None when the record has no draft section or no draft was generated."""
    d = section_text(record_text, "Provider draft")
    return None if d is None or NO_DRAFT_RE.match(d) else d


def main():
    args = sys.argv[1:]
    cfg = RC.load(os.path.join(ROOT, "round.json"))
    codes = RC.batch_codes(cfg)
    if "--ids" in args:
        return cmd_ids(codes)

    ratings_file = None
    if "--ratings-file" in args:
        i = args.index("--ratings-file")
        if i + 1 >= len(args):
            print("check_export.py: --ratings-file needs a path", file=sys.stderr)
            return 1
        ratings_file = args[i + 1]

    problems = []
    missing_export = [c for c in codes if not os.path.exists(os.path.join("export", f"{c}.md"))]
    if missing_export:
        problems.append(f"missing export files for batches: {missing_export}")

    records_by_trace = {}
    for c in codes:
        recs = export_records(c)
        if recs is None:
            continue
        for i, r in enumerate(recs):
            if not r["trace"]:
                problems.append(f"export/{c}.md record {i+1}: no '*Trace ... Medication: ...*' header line")
                continue
            for sec in REQUIRED_SECTIONS:
                if sec not in r["text"]:
                    problems.append(f"export/{c}.md {r['trace'][:13]}: missing section {sec!r}")
            if r["trace"] in records_by_trace:
                problems.append(f"{r['trace'][:13]}: appears in both export/{records_by_trace[r['trace']]}.md and export/{c}.md")
            records_by_trace[r["trace"]] = c
    text_of = {}
    for c in codes:
        for r in export_records(c) or []:
            if r["trace"]:
                text_of[r["trace"]] = r["text"]

    rated_traces = {r["trace"] for r in LR.rating_rows("ratings.md")}
    named = source_traces(cfg)
    for f in sorted(named.pop("missing-files", set())):
        problems.append(f"source file not found: {f}")
    edits_traces = named.pop("edits-sent", None)
    if edits_traces is None:
        edits_traces = named.get("edits", set())
    all_named = set().union(rated_traces, *named.values())
    for t in sorted(all_named - set(records_by_trace)):
        problems.append(f"trace {t[:13]} named by a source has no export record")
    needs = [(rated_traces, "**Ratings (from", "the per-trace ratings table section"),
             (edits_traces, "**Message the provider sent**", "section '**Message the provider sent**'"),
             (named.get("evals", set()), "**Judge verdicts**", "section '**Judge verdicts**'")]
    for traces, head, what in needs:
        for t in sorted(traces & set(text_of)):
            if head not in text_of[t]:
                problems.append(f"export/{records_by_trace[t]}.md {t[:13]}: missing {what}")

    drafted = {}
    for s in RC.sources_of_kind(cfg, *RC.SHEET_KINDS):
        if s.get("draft_column"):
            drafted[s["draft_column"]] = s
    draft_column = next(iter(drafted), None)
    if len(drafted) > 1:
        print(f"draft-column check: sheet sources name {len(drafted)} draft columns; checking {draft_column!r}")
    if draft_column and ratings_file and os.path.exists(ratings_file):
        raw = [{(k or "").strip().lower(): v for k, v in r.items()} for r in LR.load_rows(ratings_file)]
        sheet_drafts = {}
        for r in raw:
            t = r.get("trace_id")
            d = r.get(draft_column.lower())
            if t and d:
                sheet_drafts[t] = d.strip()
        mismatches = 0
        for t, c in records_by_trace.items():
            if t in sheet_drafts:
                rec = next(r for r in export_records(c) if r["trace"] == t)
                draft = draft_text_of(rec["text"])
                if draft is not None and draft != sheet_drafts[t]:
                    mismatches += 1
                    problems.append(f"{t[:13]}: export draft differs from the sheet's {draft_column!r} column")
        print(f"draft-column check: {len(sheet_drafts)} traces compared, {mismatches} mismatches")
    elif draft_column and not ratings_file:
        print(f"draft-column check skipped: round.json names a draft column ({draft_column!r}) but no --ratings-file was given")

    if problems:
        print(f"check_export.py: {len(problems)} problem(s)")
        for p in problems:
            print(" -", p)
        return 1
    print(f"check_export.py: PASS ({len(records_by_trace)} export records, {len(rated_traces)} rated traces, "
          f"{len(all_named)} traces named by any source, all covered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
