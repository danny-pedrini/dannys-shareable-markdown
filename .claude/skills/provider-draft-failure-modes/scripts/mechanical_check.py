"""Step 2b mechanical checks, the coverage rules in `ledger-schema.md` section 2: every rating
row maps to a ledger row (CHECK 1), every rating with reviewer text has a reviewer row (CHECK 2),
every input-issue row names its input (CHECK 4), every ledger row line parses (CHECK 5). When the
round has those sources: every edited draft has an edit row (CHECK 6), every failed judge verdict
has a `judge:` row (CHECK 7), every trace a Slack report names has a `slack` row (CHECK 8), and
every evals and Slack source file was found (CHECK 9). Batch codes and
sources come from `round.json` in the current directory.

`ledger_rows` and `col` are imported by other scripts in this folder (`build_cluster.py`,
`build_cluster_analysis.py`, `make_second_opinion_input.py`, `compare_second_opinion.py`).

Prints counts and failures only; never prints draft or reviewer text.
Run from the round folder:  python3 -I <skill>/scripts/mechanical_check.py
"""
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.getcwd()
sys.path.insert(0, HERE)
import round_config as RC  # noqa: E402
import load_ratings as LR  # noqa: E402
import check_export as CE  # noqa: E402
import counting as K  # noqa: E402

REVIEWER = {"reviewer-stated", "reviewer-edit-on-good"}


def ratings():
    """Every rating row, with its reviewer handle and timestamp split out (the key the ledger's
    Rating ref column uses: trace ID plus handle plus minute)."""
    out = []
    for r in LR.rating_rows(os.path.join(ROOT, "ratings.md")):
        handle, ts = LR.split_ref(r["ref"])
        if handle is None:
            continue
        out.append({"row": r["sheet_row"], "trace": r["trace"], "handle": handle, "ts": ts,
                     "has_text": r["text_type"] != "default note only"})
    return out


def batch_traces(code):
    path = os.path.join(ROOT, "export", code + ".md")
    if not os.path.exists(path):
        return set()
    return set(re.findall(r"^\*Trace (tr-[0-9a-fA-F]{32})", open(path).read(), re.M))


def ledger_rows(code):
    path = os.path.join(ROOT, "ledger", code + ".md")
    if not os.path.exists(path):
        return None
    out, header = [], None
    for l in open(path).read().split("\n"):
        if not l.startswith("|"):
            header = None if not l.strip() else header
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set(cells[0]) <= set("-: "):
            continue
        if not header[0].startswith("row id"):
            continue
        out.append(dict(zip(header, cells)))
    return out


def col(d, name):
    for k, v in d.items():
        if k.startswith(name):
            return v
    return ""


def main():
    cfg = RC.load(os.path.join(ROOT, "round.json"))
    batches = RC.batch_codes(cfg)
    R = ratings()
    print(f"ratings.md rows: {len(R)}; traces: {len({r['trace'] for r in R})}")
    t2b = {}
    for b in batches:
        for t in batch_traces(b):
            t2b[t] = b
    rows, missing = [], []
    for b in batches:
        lr = ledger_rows(b)
        if lr is None:
            missing.append(b)
            continue
        for r in lr:
            r["_batch"] = b
        rows += lr
        prov = collections.Counter(col(r, "provenance") for r in lr)
        cls = collections.Counter(col(r, "classification") for r in lr)
        print(f"{b}: {len(lr)} rows; provenance {dict(prov)}; classification {dict(cls)}")
    if missing:
        print("MISSING LEDGERS:", missing)
    # CHECK 5 (v1.1): every row line in a ledger file must be parsed. A blank line inside the
    # table (an agent appending rows after one) ends the table for the parser, which then drops
    # the rows after it without any error, so count the raw row lines against the parsed rows.
    lost = []
    for b in batches:
        p = os.path.join(ROOT, "ledger", b + ".md")
        if os.path.exists(p):
            raw = sum(1 for l in open(p) if re.match(rf"^\| {re.escape(b)}-\d{{3}} \|", l))
            parsed = len(ledger_rows(b) or [])
            if raw != parsed:
                lost.append(f"{b} ({raw} row lines, {parsed} parsed)")
    print(f"CHECK 5 ledger rows all parsed: {'PASS' if not lost else 'FAIL: ' + ', '.join(lost) + ' (look for a blank line inside the table)'}")
    REF = re.compile(r"([a-z0-9_]+)\s*\u00b7\s*(\d{4}-\d\d-\d\d \d\d:\d\d)")
    by_key = collections.defaultdict(list)
    by_trace = collections.defaultdict(list)
    for r in rows:
        t = col(r, "trace id")
        by_trace[t].append(r)
        for m in REF.finditer(col(r, "rating ref")):
            by_key[(t, m.group(1), m.group(2))].append(r)
    done = [r for r in R if t2b.get(r["trace"]) not in missing]
    f1 = [r for r in done if (r["trace"], r["handle"], r["ts"]) not in by_key]

    def is_reviewer_row(x):
        p = col(x, "provenance")
        return p in REVIEWER or (p == "input-issue" and col(x, "evidence basis") in REVIEWER | {"provider-edit+note"})
    f2 = [r for r in done if r["has_text"] and not any(is_reviewer_row(x) for x in by_key.get((r["trace"], r["handle"], r["ts"]), []))]
    records = {}
    for b in batches:
        if b in missing:
            continue
        for rec in CE.export_records(b) or []:
            if rec["trace"]:
                records[rec["trace"]] = rec["text"]
    named = CE.source_traces(cfg)
    unread = sorted(named.pop("missing-files", set()))
    if RC.sources_of_kind(cfg, "evals", "slack"):
        print(f"CHECK 9 evals and Slack source files read: {'PASS' if not unread else 'FAIL: not found: ' + ', '.join(unread)}")
    edits_sent = named.pop("edits-sent", None)
    if edits_sent is None:
        edits_sent = named.get("edits", set())
    f4 = [col(r, "row id") for r in rows if col(r, "classification") == "input-issue" and not col(r, "input named").strip(" -")]
    f4b = [col(r, "row id") for r in rows if col(r, "provenance") == "input-issue" and col(r, "classification") != "input-issue"]
    show = lambda rs: ", ".join(f"sheet row {r['row']} ({r['trace'][:13]} {r['handle']} {r['ts']})" for r in rs)
    print(f"CHECK 1 rating rows mapped: {len(done)-len(f1)}/{len(done)} {'PASS' if not f1 else 'FAIL: ' + show(f1)}")
    nt = sum(r["has_text"] for r in done)
    print(f"CHECK 2 text ratings with reviewer row: {nt-len(f2)}/{nt} {'PASS' if not f2 else 'FAIL: ' + show(f2)}")
    print(f"CHECK 4 input-issue rows with Input named: {'PASS' if not f4 else 'FAIL: ' + ', '.join(f4)}")
    kinds = {s.get("kind") for s in RC.sources(cfg)}
    f6 = f7 = f8 = []
    if "edits" in kinds:
        edited = []
        for t in sorted(edits_sent & set(records)):
            sent = CE.section_text(records[t], "Message the provider sent")
            draft = CE.draft_text_of(records[t])
            if sent and sent != "(none recorded)" and draft is not None and content(sent) != content(draft):
                edited.append(t)
        f6 = [t for t in edited if not any(K.basis(x) in ("provider-edit", "provider-edit+note") for x in by_trace[t])]
        print(f"CHECK 6 edited drafts with an edit row: {len(edited)-len(f6)}/{len(edited)} "
              f"{'PASS' if not f6 else 'FAIL: ' + ', '.join(t[:13] for t in f6)}")
    if "evals" in kinds:
        fails = [(t, j) for t, txt in sorted(records.items()) for j, v, _ in CE.judge_verdicts(txt) if v == "fail"]
        f7 = [(t, j) for t, j in fails
              if not any(col(x, "error tag").strip() == f"judge:{j}" for x in by_trace[t])]
        print(f"CHECK 7 failed judge verdicts with a judge row: {len(fails)-len(f7)}/{len(fails)} "
              f"{'PASS' if not f7 else 'FAIL: ' + ', '.join(f'{t[:13]} {j}' for t, j in f7)}")
    if "slack" in kinds:
        reported = sorted(named.get("slack", set()))
        f8 = [t for t in reported if not any(K.basis(x) == "slack" for x in by_trace[t])]
        print(f"CHECK 8 Slack-reported traces with a slack row: {len(reported)-len(f8)}/{len(reported)} "
              f"{'PASS' if not f8 else 'FAIL: ' + ', '.join(t[:13] for t in f8)}")
    if f4b:
        print("WARN provenance input-issue but classification not input-issue:", ", ".join(f4b))
    known = {(r["trace"], r["handle"], r["ts"]) for r in R}
    stray = [k for k in by_key if k not in known]
    if stray:
        print("WARN ledger Rating refs not in ratings.md:", [(k[0][:13], k[1], k[2]) for k in stray])
    nocls = [col(r, "row id") for r in rows if col(r, "provenance") != "thumbs-only" and not col(r, "classification")]
    if nocls:
        print("WARN rows with no Classification:", ", ".join(nocls))
    wrongb = [col(r, "row id") for r in rows if t2b.get(col(r, "trace id")) not in (r["_batch"], None)]
    if wrongb:
        print("WARN rows whose trace belongs to another batch:", ", ".join(wrongb))
    sys.exit(1 if (f1 or f2 or f4 or f6 or f7 or f8 or unread or missing or lost) else 0)


def content(s):
    """A message at content level: platform tokens dropped, whitespace and case folded."""
    return re.sub(r"\s+", " ", re.sub(r"\{\{[^}]*\}\}", " ", s)).strip().lower()


if __name__ == "__main__":
    main()
