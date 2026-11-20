"""Step 1: turn a saved read of the ratings tab into `ratings.md`.

Accepts one input file, any of:
  - `.json`: either a bare list of rows (header row first, each row a list of cell strings --
    this is the shape a Sheets read returns when saved as JSON rows), or `{"rows": [...]}` in
    the same shape, or a list of row objects (dicts keyed by column name).
  - `.csv`: comma-separated, header row first.
  - `.tsv`: tab-separated, header row first.

Expected columns (any order, matched by name): label_id, eval_run_id, trace_id, session_id,
message_id, verdict, note, labeler, created_at, priority, failure_modes, details. `details` is a
JSON string holding `reasons` (per-tag reviewer text) and `expected_flag_for`. `failure_modes` is
a bracketed, comma-separated tag list, e.g. `[dosage_medication_mismatch]` or `[]`.

Writes `ratings.md` in the current directory (the round folder): headline counts, a per-reviewer
table, repeats, tags, `expected_flag_for` values, one subsection per tag naming its rows, a
per-trace roll-up, and the row table every other script parses (`rating_rows()` below).

A round with more than one sheet source (round.json `sources[]` of kind `thumbs-downs`,
`labeling` or `edits`) passes one `<code>=<file>` argument per source. `ratings.md` then gains
section 9, "Rows by source", which `source_rows()` parses: every sheet row's source code, trace,
Rating ref (blank on an edits row with no rating), whether a sent message is recorded, and the
sender. An edits sheet needs `trace_id` and its `sent_column`; its rows without a verdict load
into section 9 only. A rating sheet needs `trace_id`, `verdict`, `labeler` and `created_at`.
Every row bound for the row table needs a label ID of 36 hex-or-dash characters. A label ID
two sheets both hold enters the row table once; repeats within one sheet all stay. Each code is
passed once.

Run from the round folder:
  python3 -I <skill>/scripts/load_ratings.py <saved-sheet-file>              legacy, one source
  python3 -I <skill>/scripts/load_ratings.py <CODE>=<file> [<CODE>=<file>]   one per sheet source
"""
import collections
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round_config as RC  # noqa: E402

EXPECTED_COLS = ["label_id", "eval_run_id", "trace_id", "session_id", "message_id", "verdict",
                  "note", "labeler", "created_at", "priority", "failure_modes", "details"]
DEFAULT_NOTES = {"positive feedback", "negative feedback"}

# The row table format every script parses. `ref` is "<handle> · <YYYY-MM-DD HH:MM>" (UTC).
ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*([0-9a-fA-F-]{36})\s*\|\s*(tr-[0-9a-fA-F]{32})\s*\|\s*"
    r"([a-z0-9_]+\s*·\s*\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s*\|\s*(good|bad)\s*\|\s*"
    r"([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*$"
)
REF_RE = re.compile(r"([a-z0-9_]+)\s*·\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})")


def rating_rows(path="ratings.md"):
    """Parse every row of the fixed rating-row table out of `ratings.md`, wherever it sits in
    the file. Used by mechanical_check.py, build_cluster_analysis.py and others, so the table's
    position or section number never has to be round-specific."""
    out = []
    for line in open(path):
        m = ROW_RE.match(line.rstrip("\n"))
        if m:
            sheet_row, label_id, trace, ref, verdict, tags, text_type, text = m.groups()
            out.append(dict(sheet_row=int(sheet_row), label_id=label_id, trace=trace,
                             ref=ref.strip(), verdict=verdict, tags=tags.strip(),
                             text_type=text_type.strip(), text=text.strip()))
    return out


SOURCES_HEADING = "## 9. Rows by source"


def source_rows(path="ratings.md"):
    """Section 9 rows: dicts with source, trace, ref, sent ("yes"/"no") and sender. Empty when
    the round has one legacy source; callers then treat every rating row as that source's."""
    if not os.path.exists(path):
        return []
    rows = RC.parse_table_after(open(path).read(), SOURCES_HEADING)
    return [dict(source=RC.col(r, "source"), trace=RC.col(r, "trace id"), ref=RC.col(r, "rating ref"),
                 sent=RC.col(r, "sent message"), sender=RC.col(r, "sender")) for r in rows]


def split_ref(ref):
    m = REF_RE.match(ref)
    return m.groups() if m else (None, None)


def normalize_labeler(value):
    """Strip the `+...` suffix and the domain: `teammate@example.com` -> `tfearon`."""
    local = value.split("@", 1)[0]
    return local.split("+", 1)[0]


def redact(s):
    """Best-effort pattern redaction (dates, ages, weights, BMI) for free-text reviewer
    comments. This is NOT a guarantee: it catches the patterns Round 3 saw, not every way PHI
    can appear. Review the output before treating it as safe to share outside the review team."""
    if not s:
        return s
    months = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
    s = re.sub(r"\b\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?\s*(?:lbs?|pounds)\b", "[redacted]", s, flags=re.I)
    s = re.sub(r"\b\d+(?:\.\d+)?\s*(?:lbs?|pounds)\b", "[redacted]", s, flags=re.I)
    s = re.sub(r"\b\d{1,3}\s*(?:-year-old|years old|years of age)\b", "[redacted]", s, flags=re.I)
    s = re.sub(rf"\b{months}\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s*\d{{0,4}}\b", "[redacted]", s, flags=re.I)
    s = re.sub(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b", "[redacted]", s)
    s = re.sub(r"\bBMI\s*(?:of|is|:)?\s*\d+(?:\.\d+)?\b", "BMI [redacted]", s, flags=re.I)
    s = re.sub(r"\b\w+\s+weeks\s+postpartum\b", "[redacted] postpartum", s, flags=re.I)
    return s


def parse_tags(raw):
    """`[dosage_medication_mismatch]`, `[a,b]` or `[]` -> ['dosage_medication_mismatch'] etc."""
    raw = (raw or "").strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    return [t.strip() for t in raw.split(",") if t.strip()]


def load_rows(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        with open(path) as fh:
            data = json.load(fh)
        if isinstance(data, dict) and "rows" in data:
            data = data["rows"]
        if not data:
            return []
        if isinstance(data[0], dict):
            return list(data)
        header = [h.strip().lower() for h in data[0]]
        return [dict(zip(header, [str(c) if c is not None else "" for c in r])) for r in data[1:]]
    delim = "\t" if ext == ".tsv" else ","
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delim)
        return [{(k or "").strip().lower(): (v or "") for k, v in r.items()} for r in reader]


def build(rows, src=None):
    src = src or {}
    sent_col, sender_col = src.get("sent_column"), src.get("sender_column")
    out = []
    for i, r in enumerate(rows, start=2):  # sheet row 1 is the header
        labeler = r.get("labeler", "")
        handle = normalize_labeler(labeler) if labeler else ""
        created_at = (r.get("created_at") or "").strip()
        ts = created_at[:16] if len(created_at) >= 16 else created_at
        ref = f"{handle} · {ts}" if handle and ts else ""
        verdict = (r.get("verdict") or "").strip().lower()
        tags = parse_tags(r.get("failure_modes", ""))
        details_raw = r.get("details") or "{}"
        try:
            details = json.loads(details_raw) if isinstance(details_raw, str) else (details_raw or {})
        except json.JSONDecodeError:
            details = {}
        reasons = details.get("reasons", {}) or {}
        expected_flag_for = details.get("expected_flag_for", []) or []
        note = (r.get("note") or "").strip()
        is_default_note = note.lower() in DEFAULT_NOTES
        has_reasons = bool(reasons)
        has_custom_note = bool(note) and not is_default_note
        if has_reasons and has_custom_note:
            text_type = "reasons+note"
        elif has_reasons:
            text_type = "reasons"
        elif has_custom_note:
            text_type = "custom note"
        else:
            text_type = "default note only"
        pieces = [f"[{tag}] {redact(' '.join(str(text).split()))}" for tag, text in reasons.items()]
        if has_custom_note:
            pieces.append(redact(" ".join(note.split())))
        text = " // ".join(pieces).replace("|", "/")
        out.append(dict(sheet_row=i, label_id=str(r.get("label_id") or "").strip(), trace=r.get("trace_id", ""),
                         ref=ref, handle=handle, created_at=created_at, verdict=verdict, tags=tags,
                         text_type=text_type, text=text, expected_flag_for=expected_flag_for,
                         session_id=r.get("session_id", ""), message_id=r.get("message_id", ""),
                         eval_run_id=r.get("eval_run_id", ""), priority=r.get("priority", ""),
                         source=src.get("code") or "",
                         sent="yes" if sent_col and (r.get(sent_col.lower()) or "").strip() else "no",
                         sender=normalize_labeler((r.get(sender_col.lower()) or "").strip()) if sender_col else ""))
    return out


def is_rating(r):
    return r["verdict"] in ("good", "bad") and bool(r["ref"])


def render(rows, all_rows=None):
    n = len(rows)
    traces = {r["trace"] for r in rows}
    label_ids = {r["label_id"] for r in rows}
    good = sum(1 for r in rows if r["verdict"] == "good")
    bad = sum(1 for r in rows if r["verdict"] == "bad")
    with_text = [r for r in rows if r["text_type"] != "default note only"]
    with_reasons = [r for r in rows if r["text_type"] in ("reasons", "reasons+note")]
    bad_with_reasons = [r for r in with_reasons if r["verdict"] == "bad"]
    bad_no_reason = [r for r in rows if r["verdict"] == "bad" and r["text_type"] == "default note only"]
    custom_note = [r for r in rows if r["text_type"] in ("custom note", "reasons+note")]
    default_only = [r for r in rows if r["text_type"] == "default note only"]
    ts_sorted = sorted(r["created_at"] for r in rows if r["created_at"])
    window = f"{ts_sorted[0][:16]} to {ts_sorted[-1][:16]}" if ts_sorted else "unknown"
    always_blank = [c for c in ("eval_run_id", "session_id", "message_id", "priority")
                    if all(not r.get(c) for r in rows)]

    L = ["# Round ratings (ratings tab, loaded by `load_ratings.py`)", "",
         "> **Source:** the saved sheet read passed to `load_ratings.py`. Labeler addresses are "
         "normalized to handles (strip any `+...` suffix and the domain). Reviewer text below is "
         "redacted on a best-effort pattern basis only (dates, ages, weights, BMI); re-check it "
         "before treating this file as safe to read outside the review team.", "",
         "## 1. Headline counts", "",
         "| Measure | Value |", "| --- | --- |",
         f"| Label rows | {n} |", f"| Distinct trace IDs | {len(traces)} |",
         f"| Distinct label IDs | {len(label_ids)} |", f"| Rating window (UTC) | {window} |",
         f"| Blank in every row | {', '.join(always_blank) or 'none'} |",
         f"| Verdicts | good {good}, bad {bad} |",
         f"| Rows with reviewer text (`reasons` or a custom note) | {len(with_text)} |",
         f"| Rows with `reasons` | {len(with_reasons)} |",
         f"| Rows with a custom `note` | {len(custom_note)} |",
         f"| Rows with only the tool's default note and no reasons | {len(default_only)} |",
         f"| Bad rows with no reason text | {len(bad_no_reason)} |",
         f"| Rows with a non-empty `expected_flag_for` | {sum(1 for r in rows if r['expected_flag_for'])} |",
         ""]

    by_rev = collections.OrderedDict()
    for r in rows:
        h = r["handle"] or "(unknown)"
        d = by_rev.setdefault(h, {"rows": 0, "good": 0, "bad": 0, "text": 0, "bad_reason": 0})
        d["rows"] += 1
        d["good"] += r["verdict"] == "good"
        d["bad"] += r["verdict"] == "bad"
        d["text"] += r["text_type"] != "default note only"
        d["bad_reason"] += r["verdict"] == "bad" and r["text_type"] in ("reasons", "reasons+note")
    L += ["## 2. Verdicts and text per reviewer", "",
          "| Reviewer | Rows | Good | Bad | Rows with reviewer text | Bad rows with reasons |",
          "| --- | --- | --- | --- | --- | --- |"]
    for h, d in by_rev.items():
        L.append(f"| {h} | {d['rows']} | {d['good']} | {d['bad']} | {d['text']} | {d['bad_reason']} |")
    L.append(f"| **Total** | {n} | {good} | {bad} | {len(with_text)} | {len(bad_with_reasons)} |")
    L.append("")

    per_trace = collections.defaultdict(list)
    for r in rows:
        per_trace[r["trace"]].append(r)
    by_count = collections.Counter(len(v) for v in per_trace.values())
    multi_rev = sum(1 for v in per_trace.values() if len({x["handle"] for x in v}) > 1)
    same_rev_repeat = sum(1 for v in per_trace.values()
                           if any(c > 1 for c in collections.Counter(x["handle"] for x in v).values()))
    split_verdict = sum(1 for v in per_trace.values() if len({x["verdict"] for x in v}) > 1)
    dup_keys = collections.Counter((r["trace"], r["handle"], r["ref"]) for r in rows if r["ref"])
    dup_count = sum(1 for c in dup_keys.values() if c > 1)
    L += ["## 3. Repeats", "",
          "| Rows per trace | Traces |", "| --- | --- |"]
    for k in sorted(by_count):
        L.append(f"| {k} | {by_count[k]} |")
    L += ["",
          f"- Traces rated by more than one reviewer: {multi_rev}.",
          f"- Traces where the same reviewer rated more than once: {same_rev_repeat}. "
          "When this happens, keep every row (the mechanical check maps all of them); the latest "
          "by `created_at` is the one that should drive classification.",
          f"- Traces with a good and a bad verdict across reviewers: {split_verdict}.",
          f"- Duplicate (trace, reviewer, minute) keys: {dup_count}.", ""]

    tag_rows = collections.defaultdict(list)
    for r in rows:
        for t in r["tags"]:
            tag_rows[t].append(r)
    multi_tag = sum(1 for r in rows if len(r["tags"]) > 1)
    L += ["## 4. Tags", "", "| Tag | Tag instances | Rows |", "| --- | --- | --- |"]
    for t in sorted(tag_rows, key=lambda x: -len(tag_rows[x])):
        L.append(f"| `{t}` | {len(tag_rows[t])} | {len(tag_rows[t])} |")
    no_tag = sum(1 for r in rows if not r["tags"])
    L.append(f"| *(no tag)* | | {no_tag} |")
    L += ["", f"Rows carrying more than one tag: {multi_tag}.", ""]

    efl = [r for r in rows if r["expected_flag_for"]]
    L += ["## 5. `expected_flag_for`", ""]
    if not efl:
        L.append(f"**Empty in all {n} rows.** No value to report; classify rows without this field.")
    else:
        L.append("| Sheet row | Trace | Reviewer | Value |")
        L.append("| --- | --- | --- | --- |")
        for r in efl:
            L.append(f"| {r['sheet_row']} | {r['trace'][:13]} | {r['handle']} | {r['expected_flag_for']} |")
    L.append("")

    L += ["## 6. Rows per tag", "",
          "Every tag that appears, with the rows carrying it. Which tag (if any) is ambiguous "
          "enough to need a second opinion is a round-specific call for `plan.md`, not this script.", ""]
    for t in sorted(tag_rows, key=lambda x: -len(tag_rows[x])):
        L += [f"### `{t}`", "", "| Sheet row | Trace | Reviewer | Verdict |", "| --- | --- | --- | --- |"]
        for r in tag_rows[t]:
            L.append(f"| {r['sheet_row']} | {r['trace'][:13]} | {r['handle']} | {r['verdict']} |")
        L.append("")

    L += ["## 7. Per-trace roll-up", "",
          "| Trace ID | Rows | Ratings (reviewer: verdict) | Verdicts split |",
          "| --- | --- | --- | --- |"]
    for tr in sorted(per_trace):
        v = per_trace[tr]
        who = ", ".join(f"{x['handle']}: {x['verdict']}" for x in v)
        split = "yes" if len({x["verdict"] for x in v}) > 1 else ""
        L.append(f"| {tr} | {len(v)} | {who} | {split} |")
    L.append("")

    L += [f"## 8. All {n} rating rows", "",
          "`Rating ref` is `<handle> · <YYYY-MM-DD HH:MM>` (UTC), the key the mechanical "
          "check uses together with the trace ID. `Text type` is `default note only` (no "
          "reviewer text), `reasons`, `custom note`, or `reasons+note`. The action type is not "
          "in the sheet; it joins from the export.", "",
          "| Sheet row | Label ID | Trace ID | Rating ref | Verdict | Tags | Text type | Reviewer text (redacted) |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        tags = ",".join(r["tags"]) or "none"
        L.append(f"| {r['sheet_row']} | {r['label_id']} | {r['trace']} | {r['ref']} | {r['verdict']} | "
                  f"{tags} | {r['text_type']} | {r['text']} |")
    L.append("")
    if all_rows is not None:
        L += [SOURCES_HEADING, "",
              "Every sheet row, by source code. `Rating ref` is blank on an edits row with no rating. "
              "`Sent message` is `yes` when the edits sheet records the message the provider sent.", "",
              "| Source | Sheet row | Trace ID | Rating ref | Sent message | Sender |",
              "| --- | --- | --- | --- | --- | --- |"]
        for r in all_rows:
            ref = r["ref"] if is_rating(r) else ""
            L.append(f"| {r['source']} | {r['sheet_row']} | {r['trace']} | {ref} | {r['sent']} | {r['sender']} |")
        L.append("")
    return "\n".join(L) + "\n"


def read_input(path):
    if not os.path.exists(path):
        print(f"load_ratings.py: {path} not found", file=sys.stderr)
        sys.exit(1)
    return [{(k or "").strip().lower(): v for k, v in r.items()} for r in load_rows(path)]


def require(raw_rows, cols, path):
    missing = [c for c in cols if raw_rows and c not in raw_rows[0]]
    if missing:
        print(f"load_ratings.py: {path} is missing expected columns: {missing}", file=sys.stderr)
        sys.exit(1)


def require_label_ids(rows, path):
    """Every row bound for the row table needs a label ID of 36 hex-or-dash characters, the form ROW_RE parses."""
    rated = [r for r in rows if is_rating(r)]
    blank = [str(r["sheet_row"]) for r in rated if not r["label_id"]]
    bad = [str(r["sheet_row"]) for r in rated if r["label_id"] and not re.fullmatch(r"[0-9a-fA-F-]{36}", r["label_id"])]
    for rs, what in ((blank, "no label_id"), (bad, "a label_id that isn't 36 hex-or-dash characters")):
        if rs:
            print(f"load_ratings.py: {path} has rated rows with {what} (sheet rows {', '.join(rs)})", file=sys.stderr)
    if blank or bad:
        sys.exit(1)


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: load_ratings.py <saved-sheet-file.json|.csv|.tsv> | <CODE>=<file> [<CODE>=<file> ...]",
              file=sys.stderr)
        sys.exit(1)
    if len(args) == 1 and "=" not in args[0]:
        raw_rows = read_input(args[0])
        require(raw_rows, ("trace_id", "verdict", "labeler", "created_at"), args[0])
        rows = build(raw_rows)
        require_label_ids(rows, args[0])
        open("ratings.md", "w").write(render(rows))
        print(f"wrote ratings.md: {len(rows)} rows, {len({r['trace'] for r in rows})} distinct traces")
        return
    cfg = RC.load()
    by_code = {s.get("code"): s for s in RC.sources_of_kind(cfg, *RC.SHEET_KINDS)}
    codes = [a.partition("=")[0] for a in args]
    repeated = sorted({c for c in codes if codes.count(c) > 1})
    if repeated:
        print(f"load_ratings.py: source code passed more than once: {', '.join(repeated)}", file=sys.stderr)
        sys.exit(1)
    all_rows = []
    for a in args:
        code, _, path = a.partition("=")
        src = by_code.get(code)
        if src is None:
            print(f"load_ratings.py: {code} is not a sheet source in round.json sources[] "
                  f"(sheet kinds: {', '.join(RC.SHEET_KINDS)})", file=sys.stderr)
            sys.exit(1)
        raw_rows = read_input(path)
        if src["kind"] == "edits":
            require(raw_rows, ["trace_id"] + [c.lower() for c in (src.get("sent_column"),) if c], path)
        else:
            require(raw_rows, ("trace_id", "verdict", "labeler", "created_at"), path)
        built = build(raw_rows, src)
        require_label_ids(built, path)
        all_rows += built
    # A duplicate is the same label ID in another sheet; repeats within one sheet are all kept.
    rows, ids = [], {}
    for r in all_rows:
        if not is_rating(r):
            continue
        if not ids.get(r["label_id"], {r["source"]}) - {r["source"]}:
            rows.append(r)
        ids.setdefault(r["label_id"], set()).add(r["source"])
    dups = sum(1 for r in all_rows if is_rating(r)) - len(rows)
    open("ratings.md", "w").write(render(rows, all_rows))
    print(f"wrote ratings.md: {len(rows)} rating rows, {len({r['trace'] for r in rows})} distinct traces, "
          f"{len(all_rows)} sheet rows from {len(args)} sources"
          + (f"; {dups} duplicate rating{'s' * (dups != 1)} across sheets kept once (section 9 keeps every copy)" if dups else ""))


if __name__ == "__main__":
    main()
