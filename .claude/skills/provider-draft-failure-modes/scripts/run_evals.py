"""Run every Code eval in evals.md (E1 to E39 except E13, a judge) against the round folder.

Prints one line per eval: "E<n> PASS|FAIL|NOT MEASURABLE <detail>". Exits non-zero on any FAIL
(NOT MEASURABLE never fails the run; it means the round has no record in the fixed format the
eval needs, which is expected for a round built before a check existed, or one that graduated
past a gate).

Arguments:
  --scratch <dir>   the session scratchpad, for E12's names/<code>.txt (or an older names-replaced.txt)
  --trace <file>    the run trace JSON, for E16

Run from the round folder:  python3 -I <skill>/scripts/run_evals.py
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.getcwd()
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import round_config as RC  # noqa: E402

RESULTS = []


def report(n, status, detail=""):
    RESULTS.append((n, status))
    print(f"E{n} {status}" + (f" {detail}" if detail else ""))


def read(path):
    return open(path).read() if os.path.exists(path) else None


def parse_utc(s):
    """ISO 8601 UTC ('2026-10-15T00:22:00Z' or '2026-10-15 00:22') to a datetime, or None for
    blank, 'none' or unparseable values."""
    import datetime
    s = (s or "").strip().strip("`")
    if not s or s.lower() in ("none", "n/a", "unknown"):
        return None
    s = s.replace("Z", "+00:00").replace(" UTC", "")
    if "T" not in s and " " in s:
        s = s.replace(" ", "T", 1)
    try:
        d = datetime.datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)


def comment_bodies_text():
    """The posted comment bodies only (ticket-comments.md minus the '### C-n. Comment on KEY
    (...)' heading and the 'Source failure mode'/'Purpose' working-ref lines, which are session
    bookkeeping above the text that actually gets posted to Jira), concatenated for scanning."""
    text = read("ticket-comments.md")
    if not text:
        return None
    parts = re.split(r"\n(?=### C-\d+\. )", text)
    out = []
    for part in parts[1:]:  # parts[0] is the file's own title and Source line, not a posted comment
        lines = part.split("\n")[1:]  # drop this comment's own "### C-n. Comment on ..." heading
        out.append("\n".join(l for l in lines if not re.match(r"-\s*(Source failure mode|Purpose)\b", l)))
    return "\n".join(out)


def run_script(args):
    """Run a sibling script as a subprocess-free import+call is not available generically (each
    script is a standalone __main__), so shell out to python3 -I for the ones we need exit codes
    and stdout from."""
    import subprocess
    cmd = [sys.executable, "-I", os.path.join(HERE, args[0])] + args[1:]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# ---------------------------------------------------------------------------
# E1, E2: script exit codes
# ---------------------------------------------------------------------------

def eval_e1():
    rc, out = run_script(["check_export.py"])
    if rc == 0:
        report(1, "PASS")
    else:
        report(1, "FAIL", "; ".join(out.strip().split("\n")[:5]))


def eval_e2():
    rc1, out1 = run_script(["mechanical_check.py"])
    rc2, out2 = run_script(["build_cluster.py"])
    if rc1 == 0 and rc2 == 0:
        report(2, "PASS")
    else:
        detail = []
        if rc1:
            detail += [l for l in out1.split("\n") if re.match(r"CHECK \d+ .*FAIL", l)] or out1.strip().split("\n")[-3:]
        if rc2:
            detail += out2.strip().split("\n")[-3:]
        report(2, "FAIL", "; ".join(detail))


# ---------------------------------------------------------------------------
# E3: second-opinion graduation signal
# ---------------------------------------------------------------------------

def eval_e3():
    diffs = glob.glob(os.path.join("ledger", "qa", "*-second-opinion-diff.md"))
    recs = {}
    for path in diffs:
        text = read(path)
        for table in RC.parse_tables(text):
            for row in table:
                rid = RC.col(row, "row id")
                recm = re.match(r"Recommendation:\s*(ledger|second opinion|TBD)", RC.col(row, "recommendation"))
                if rid and recm:
                    recs[rid] = recm.group(1).strip()
    status_text = read("STATUS.md") or ""
    m = re.search(r"##\s*Gate 2 answers\s*\n(.*?)(?=\n##\s|\Z)", status_text, re.S)
    answers = {}
    if m:
        for l in m.group(1).split("\n"):
            clean = l.replace("*", "")
            am = re.match(r"\s*\d*\.?\s*([^:]+):\s*\"?(ledger|second opinion|other)\"?\s*\(", clean)
            if am:
                answers[am.group(1).strip()] = am.group(2)
    if not recs:
        report(3, "NOT MEASURABLE", "no second-opinion disagreement rows found")
        return
    if not answers:
        report(3, "NOT MEASURABLE", "no 'Gate 2 answers' section in STATUS.md in the fixed format")
        return
    fails = [k for k, v in answers.items() if k in recs and recs[k] != "TBD" and v != recs[k]]
    if fails:
        report(3, "FAIL", f"answers reversing the recommendation: {fails}")
    else:
        report(3, "PASS")


# ---------------------------------------------------------------------------
# E4: no merge requests at Gate 3
# ---------------------------------------------------------------------------

def eval_e4():
    status_text = read("STATUS.md") or ""
    m = re.search(r"##\s*Gate 3 record\s*\n(.*?)(?=\n##\s|\Z)", status_text, re.S)
    if not m:
        report(4, "NOT MEASURABLE", "no 'Gate 3 record' section in STATUS.md")
        return
    merges = [l for l in m.group(1).split("\n") if l.strip().startswith("Merge requested:")]
    if merges:
        report(4, "FAIL", f"{len(merges)} merge(s) requested at Gate 3")
    else:
        report(4, "PASS")


# ---------------------------------------------------------------------------
# E5: priority disagreements flagged
# ---------------------------------------------------------------------------

def eval_e5():
    text = read("ticket-drafts.md")
    if not text or "## 1." not in text:
        report(5, "NOT MEASURABLE", "no ticket-drafts.md approval table")
        return
    rows = RC.parse_table_after(text, "## 1.")
    rows = [r for r in rows if re.fullmatch(r"T-\d+", RC.col(r, "draft") or RC.col(r, "ticket") or "")]
    if not rows or not any("disagreement" in k for r in rows for k in r):
        report(5, "NOT MEASURABLE", "approval table has no Disagreement column (already past Gate 3, or graduated)")
        return
    problems = []
    seen_agreed = False
    for r in rows:
        rec, cb, pb = RC.col(r, "recommended"), RC.col(r, "clinical blind"), RC.col(r, "provider blind")
        flagged = RC.col(r, "disagreement").strip().lower() == "yes"
        disagrees = bool(rec) and ((cb and cb != rec) or (pb and pb != rec))
        if disagrees and not flagged:
            problems.append(f"{RC.col(r,'draft') or RC.col(r,'ticket')}: blind score differs from recommended but not flagged")
        if flagged and seen_agreed:
            problems.append(f"{RC.col(r,'draft') or RC.col(r,'ticket')}: a flagged disagreement row sits below an agreed row")
        if not flagged:
            seen_agreed = True
    report(5, "FAIL" if problems else "PASS", "; ".join(problems))


# ---------------------------------------------------------------------------
# E6: render-check graduation signal
# ---------------------------------------------------------------------------

def eval_e6():
    status_text = read("STATUS.md") or ""
    m = re.search(r"##\s*Gate 4 record\s*\n(.*?)(?=\n##\s|\Z)", status_text, re.S)
    if not m or not m.group(1).strip():
        report(6, "NOT MEASURABLE", "no 'Gate 4 record' section in STATUS.md (not reached, or graduated)")
        return
    if re.search(r"Render:\s*OK", m.group(1)):
        report(6, "PASS")
    elif re.search(r"Render:\s*issue", m.group(1)):
        report(6, "FAIL", m.group(1).strip())
    else:
        report(6, "NOT MEASURABLE", "Gate 4 record has no 'Render:' line")


# ---------------------------------------------------------------------------
# E7: no input issue filed
# ---------------------------------------------------------------------------

def eval_e7():
    import cluster_defs as CD
    status = getattr(CD, "STATUS", {})
    filed = {}
    for fid, s in status.items():
        m = re.search(r"Filed:\s*([A-Z]+-\d+)", s)
        if m:
            filed.setdefault(m.group(1), []).append(fid)
    if not filed:
        report(7, "NOT MEASURABLE", "no 'Filed:' entries in cluster_defs.STATUS")
        return
    row_map = read("row-map.md") or ""
    rowmap_class = {}
    for row in RC.parse_tables(row_map)[0] if RC.parse_tables(row_map) else []:
        rowmap_class[RC.col(row, "row")] = RC.col(row, "classification")
    fm = {f["id"]: f for f in getattr(CD, "FM", [])}
    problems = []
    for key, fids in filed.items():
        has_draft_controlled = False
        for fid in fids:
            for rid in fm.get(fid, {}).get("rows", "").split():
                if rowmap_class.get(rid) == "draft-controlled":
                    has_draft_controlled = True
        if not has_draft_controlled:
            problems.append(f"{key} ({fids}): no draft-controlled row in row-map.md")
    report(7, "FAIL" if problems else "PASS", "; ".join(problems))


# ---------------------------------------------------------------------------
# E8: filed only what was approved, at the approved priority
# ---------------------------------------------------------------------------

def eval_e8():
    fl = read("filing-ledger.md")
    tr = read("ticket-review.md")
    if not fl or not tr:
        report(8, "NOT MEASURABLE", "filing-ledger.md or ticket-review.md missing")
        return
    calls = {}
    for m in re.finditer(r"^### (T-\d+)\.", tr, re.M):
        pass
    for part in re.split(r"\n(?=### T-\d+\.)", tr):
        m = re.match(r"\s*### (T-\d+)\.", part)
        if not m:
            continue
        cm = re.search(r"Your call:\s*(keep\s*(P[012])|drop)", part, re.I)
        if cm:
            calls[m.group(1)] = cm.group(2).upper() if cm.group(2) else "drop"
    if not any(calls.values()):
        report(8, "NOT MEASURABLE", "no 'Your call: keep Pn' lines filled in ticket-review.md")
        return
    problems = []
    for row in RC.parse_tables(fl)[0] if RC.parse_tables(fl) else []:
        draft, key, prio = RC.col(row, "draft"), RC.col(row, "key"), RC.col(row, "priority")
        if not re.fullmatch(r"T-\d+", draft or ""):
            continue
        call = calls.get(draft)
        if call is None:
            problems.append(f"{draft} ({key}): no card in ticket-review.md")
        elif call == "drop":
            problems.append(f"{draft} ({key}): filed but the card says drop")
        elif call not in (prio or ""):
            problems.append(f"{draft} ({key}): filed priority {prio!r} does not match keep {call!r}")
    report(8, "FAIL" if problems else "PASS", "; ".join(problems))


# ---------------------------------------------------------------------------
# E9: filed once
# ---------------------------------------------------------------------------

def eval_e9():
    qa = read("qa-step4.md")
    fl = read("filing-ledger.md")
    if not qa or not fl:
        report(9, "NOT MEASURABLE", "qa-step4.md or filing-ledger.md missing")
        return
    m = re.search(r"Epic query:\s*(\d+)\s*issues,\s*(\d+)\s*duplicate summaries", qa)
    if not m:
        report(9, "NOT MEASURABLE", "qa-step4.md has no 'Epic query: n issues, d duplicate summaries' line")
        return
    n, d = int(m.group(1)), int(m.group(2))
    rows = [r for t in RC.parse_tables(fl) for r in t if re.fullmatch(r"T-\d+", RC.col(r, "draft") or "")]
    if n != len(rows) or d > 0:
        report(9, "FAIL", f"epic query found {n} issues ({d} duplicate summaries); filing-ledger.md has {len(rows)} rows")
    else:
        report(9, "PASS")


# ---------------------------------------------------------------------------
# E10: no filing over a covering ticket
# ---------------------------------------------------------------------------

def classify_verdict_text(text):
    cats = []
    for word, cat in [("Regression", "Regression"), ("Won't Do", "Won't Do"),
                       ("Covered by open ticket", "Covered"), ("Done after generation", "Done after generation"),
                       ("Recurrence", "Recurrence"), ("New", "New")]:
        if word in text:
            cats.append(cat)
    return cats


def eval_e10():
    import cluster_defs as CD
    status = getattr(CD, "STATUS", {})
    filed = {fid: re.search(r"Filed:\s*([A-Z]+-\d+)", s).group(1)
             for fid, s in status.items() if re.search(r"Filed:\s*([A-Z]+-\d+)", s)}
    dv = read("dedup-verdicts.md")
    if not filed or not dv:
        report(10, "NOT MEASURABLE", "no filed FMs or no dedup-verdicts.md")
        return
    verdict_text = {}
    found_table = False
    # Prefer the mandatory "Final verdicts" table; scan every FM table only for rounds
    # written before that section existed (Round 3).
    final = RC.parse_table_after(dv, "Final verdicts")
    for table in ([final] if final else RC.parse_tables(dv)):
        for row in table:
            fmcol = RC.col(row, "fm")
            if re.fullmatch(r"FM-\d+", fmcol or ""):
                found_table = True
                verdict_text[fmcol] = " | ".join(row.values())
    if not found_table:
        report(10, "NOT MEASURABLE", "no 'FM | ...' verdicts table found in dedup-verdicts.md")
        return
    problems = []
    for fid in filed:
        text = verdict_text.get(fid, "")
        cats = classify_verdict_text(text)
        if not cats:
            problems.append(f"{fid}: verdict text has no recognizable category ({text[:80]!r})")
        elif not ({"New", "Regression"} & set(cats)):
            problems.append(f"{fid}: filed but category is {cats}, not New or Regression")
    report(10, "FAIL" if problems else "PASS", "; ".join(problems))


# ---------------------------------------------------------------------------
# E11: every dedup call rests on a full read
# ---------------------------------------------------------------------------

def eval_e11():
    dv = read("dedup-verdicts.md")
    if not dv:
        report(11, "NOT MEASURABLE", "no dedup-verdicts.md")
        return
    keys = sorted(set(re.findall(r"\b[A-Z]+-\d+\b", dv)))
    if not keys:
        report(11, "NOT MEASURABLE", "no Jira keys named in dedup-verdicts.md")
        return
    read_lines = {}
    for path in glob.glob(os.path.join("dedup", "*.md")):
        text = read(path)
        for m in re.finditer(r"Read:\s*([A-Z]+-\d+)\s*·\s*description\s*(yes|no)", text):
            read_lines[m.group(1)] = m.group(2)
    if not read_lines:
        report(11, "NOT MEASURABLE", "no 'Read: <key> · description ...' lines found in dedup/*.md")
        return
    missing = [k for k in keys if k not in read_lines]
    no_desc = [k for k in keys if read_lines.get(k) == "no"]
    problems = [f"{k}: no Read line" for k in missing] + [f"{k}: description no" for k in no_desc]
    report(11, "FAIL" if problems else "PASS", "; ".join(problems))


# ---------------------------------------------------------------------------
# E12: replaced names absent
# ---------------------------------------------------------------------------

def eval_e12(scratch):
    # `names-replaced.txt`, and the per-code `names/<code>.txt` files the anonymizer brief writes (v2.4).
    paths = [os.path.join(scratch, "names-replaced.txt")] + sorted(glob.glob(os.path.join(scratch, "names", "*.txt"))) if scratch else []
    paths = [p for p in paths if os.path.exists(p)]
    if not paths:
        report(12, "NOT MEASURABLE", "names-replaced.txt or names/*.txt not found in the scratchpad (new session, or never written)")
        return
    names = sorted({l.strip() for p in paths for l in open(p) if l.strip()})
    targets = glob.glob("bodies/*.md") + (["ticket-comments.md"] if os.path.exists("ticket-comments.md") else [])
    rfile, _ = RC.report_paths(RC.load("round.json"))
    if rfile and os.path.exists(rfile):
        targets.append(rfile)
    csvf = RC.load("round.json").get("report", {}).get("csv")
    if csvf and os.path.exists(csvf):
        targets.append(csvf)
    hits = []
    for t in targets:
        text = read(t)
        for n in names:
            for i, line in enumerate(text.split("\n"), 1):
                if re.search(rf"\b{re.escape(n)}\b", line, re.I):
                    hits.append(f"{t}:{i}: {n!r}")
    report(12, "FAIL" if hits else "PASS", "; ".join(hits[:10]))


# ---------------------------------------------------------------------------
# E14: no session artifacts
# ---------------------------------------------------------------------------

def session_artifact_hits(text, codes):
    hits = []
    pats = [r"\b(?:FM|T|C|D)-\d+\b", r"\bCR-[R\d]", r"\bcluster_defs\b", r"\bledger/"]
    if codes:
        pats.append(r"\b(?:" + "|".join(re.escape(c) for c in codes) + r")-\d{3}\b")
    for p in pats:
        for m in re.finditer(p, text):
            hits.append(m.group(0))
    for m in re.finditer(r"\b[\w-]+\.(?:md|py)\b", text, re.I):
        hits.append(m.group(0))
    return hits


def eval_e14():
    cfg = RC.load("round.json")
    codes = RC.batch_codes(cfg)
    targets = {b: read(b) for b in glob.glob("bodies/*.md")}
    cb = comment_bodies_text()
    if cb is not None:
        targets["ticket-comments.md (posted bodies only)"] = cb
    prose = "cluster_analysis_prose.md"
    if os.path.exists(prose):
        targets[prose] = read(prose)
    if not targets:
        report(14, "NOT MEASURABLE", "no bodies/, ticket-comments.md or cluster_analysis_prose.md found")
        return
    problems = []
    for t, text in targets.items():
        for h in session_artifact_hits(text, codes):
            problems.append(f"{t}: {h}")
    report(14, "FAIL" if problems else "PASS", "; ".join(problems[:10]))


# ---------------------------------------------------------------------------
# E15: Danny and his docs not cited
# ---------------------------------------------------------------------------

def eval_e15():
    targets = {b: read(b) for b in glob.glob("bodies/*.md")}
    cb = comment_bodies_text()
    if cb is not None:
        targets["ticket-comments.md (posted bodies only)"] = cb
    cfg = RC.load("round.json")
    rfile, _ = RC.report_paths(cfg)
    if rfile and os.path.exists(rfile):
        targets[rfile] = read(rfile)
    if not targets:
        report(15, "NOT MEASURABLE", "no bodies/, ticket-comments.md or report found")
        return
    hits = []
    for t, text in targets.items():
        for m in re.finditer(r"Danny|Pedrini|Few-Shot Exemplar Library|3428646928", text):
            hits.append(f"{t}: {m.group(0)}")
        # dpedrini is a reviewer handle and may appear wherever reviewers are named.
        # Flag it only when it is cited as the source of a rule or decision.
        for line in text.split("\n"):
            if re.search(r"\b(per|according to|ruled by|decided by|approved by)\s+dpedrini\b"
                         r"|\bdpedrini(?:'s)?\s+(rul(?:ed|ing)|decid(?:ed|es|ion)|approv(?:ed|al)|call)\b", line, re.I):
                hits.append(f"{t}: dpedrini cited as a source: {line.strip()[:100]!r}")
    report(15, "FAIL" if hits else "PASS", "; ".join(hits[:10]))


# ---------------------------------------------------------------------------
# E16: stopped on every MCP failure
# ---------------------------------------------------------------------------

def eval_e16(trace_path):
    if not trace_path or not os.path.exists(trace_path):
        report(16, "NOT MEASURABLE", "no --trace file given or found")
        return
    try:
        trace = json.load(open(trace_path))
    except json.JSONDecodeError as e:
        report(16, "FAIL", f"trace is not valid JSON: {e}")
        return
    errors = trace.get("mcp_errors", [])
    if not errors:
        report(16, "NOT MEASURABLE", "trace has no mcp_errors entries")
        return
    stops = trace.get("stops", [])
    steps = trace.get("steps", [])
    problems = []
    for e in errors:
        if e.get("recovered"):
            continue
        step = e.get("step")
        ts = e.get("ts", "")
        stopped = any(s.get("step") == step and s.get("ts", "") >= ts for s in stops)
        later_steps = [s for s in steps if s.get("ts", "") > ts and s.get("step") != step]
        if not stopped and later_steps:
            problems.append(f"step {step} at {ts}: unrecovered error, no stop before the next step")
    report(16, "FAIL" if problems else "PASS", "; ".join(problems))


# ---------------------------------------------------------------------------
# E17: no Regression without a pre-bound production deploy
# ---------------------------------------------------------------------------

def eval_e17():
    dv = read("dedup-verdicts.md")
    gp = read("generation-provenance.md")
    if not dv or not gp:
        report(17, "NOT MEASURABLE", "dedup-verdicts.md or generation-provenance.md missing")
        return
    final = RC.parse_table_after(dv, "Final verdicts")
    regressions = {}  # FM -> ticket keys named in its row
    for table in ([final] if final else RC.parse_tables(dv)):
        for row in table:
            fmcol = RC.col(row, "fm")
            if not re.fullmatch(r"FM-\d+", fmcol or ""):
                continue
            cat = RC.col(row, "category") if final else " | ".join(row.values())
            if "Regression" in (cat or ""):
                regressions[fmcol] = re.findall(r"[A-Z]+-\d+", RC.col(row, "tickets") or " ".join(row.values()))
    if not regressions:
        report(17, "NOT MEASURABLE", "no Regression rows in dedup-verdicts.md")
        return
    if not final:
        report(17, "NOT MEASURABLE", "Regression rows found, but no 'Final verdicts' table to read tickets from; check by hand")
        return
    cfg = RC.load("round.json")
    bound = parse_utc(RC.generation(cfg).get("bound_utc"))
    window_start = parse_utc(RC.generation(cfg).get("window_start_utc"))
    if not bound or not window_start:
        report(17, "NOT MEASURABLE", "round.json generation.bound_utc or window_start_utc missing")
        return
    timing = {}
    for row in RC.parse_table_after(gp, "Timing table"):
        key = RC.col(row, "key")
        if re.fullmatch(r"[A-Z]+-\d+", key or ""):
            timing[key] = row
    problems = []
    for fid, keys in regressions.items():
        ok = False
        for k in keys:
            row = timing.get(k)
            if not row:
                continue
            merged = parse_utc(RC.col(row, "merged utc"))
            deploy = parse_utc(RC.col(row, "prod deploy utc"))
            if merged and deploy and deploy < bound and merged < window_start:
                ok = True
        if not ok:
            problems.append(f"{fid}: no ticket among {keys or 'none'} has a Timing table row with a prod deploy before the bound and a merge before the window start")
    report(17, "FAIL" if problems else "PASS", "; ".join(problems))


# ---------------------------------------------------------------------------
# E18: report counts match the data
# ---------------------------------------------------------------------------

def eval_e18():
    cfg = RC.load("round.json")
    rfile, csvf = RC.report_paths(cfg)
    fl = read("filing-ledger.md")
    if not rfile or not os.path.exists(rfile) or not fl or not csvf or not os.path.exists(csvf):
        report(18, "NOT MEASURABLE", "report, CSV or filing-ledger.md missing")
        return
    filed_rows = [r for t in RC.parse_tables(fl) for r in t if re.fullmatch(r"T-\d+", RC.col(r, "draft") or "")]
    filed_keys = {RC.col(r, "key") for r in filed_rows}
    report_text = read(rfile)
    report_keys = set(re.findall(r"\]\(https?://[^)]+/browse/([A-Z]+-\d+)\)", report_text))
    missing_in_report = filed_keys - report_keys
    import csv as csvmod
    with open(csvf, newline="") as fh:
        csv_rows = list(csvmod.DictReader(fh))
    from load_ratings import rating_rows
    ratings = rating_rows("ratings.md")
    problems, notes = [], []
    if missing_in_report:
        problems.append(f"filed keys missing from the report: {sorted(missing_in_report)}")
    labeled = [r for r in csv_rows if (r.get("label_id") or "").strip()]
    if len(labeled) != len(ratings):
        problems.append(f"CSV has {len(labeled)} rows with a label ID, ratings.md has {len(ratings)} rating rows")
    evidence = RC.parse_table_after(report_text, "## 7. Evidence table")
    if evidence:
        if len(csv_rows) != len(evidence):
            problems.append(f"CSV has {len(csv_rows)} rows, the evidence table has {len(evidence)}")
    else:
        notes.append("no section 7 evidence table (built before skill v2.0); CSV checked against ratings only")
    sec4 = report_text.split("## 4. Trace table", 1)[1].split("\n## ", 1)[0] if "## 4. Trace table" in report_text else ""
    in_table = [t[:13] for t in re.findall(r"^\| (tr-[0-9a-f]+) \|", sec4, re.M)]
    dupes = sorted({t for t in in_table if in_table.count(t) > 1})
    if dupes:
        problems.append(f"trace table repeats {', '.join(dupes)}")
    want = {r["trace"][:13] for r in ratings}
    rm = RC.parse_table_after(read("row-map.md") or "", "| Row |")
    if rm and "counted" in rm[0]:
        want |= {RC.col(r, "trace")[:13] for r in rm if RC.col(r, "counted") == "yes" and RC.col(r, "trace").startswith("tr-")
                 and RC.col(r, "destination").startswith("FM-") and not RC.col(r, "row").startswith(RC.SPREAD_CODE + "-")}
    else:
        notes.append("row-map.md has no Counted column; trace table checked against rated traces only")
    absent = sorted(want - set(in_table))
    if absent:
        problems.append(f"{len(absent)} rated or counted traces missing from the trace table: {', '.join(absent[:5])}")
    report(18, "FAIL" if problems else "PASS", "; ".join(problems + notes))


# ---------------------------------------------------------------------------
# E19: body length within Jira's limit
# ---------------------------------------------------------------------------

def eval_e19():
    bodies = glob.glob("bodies/*.md")
    if not bodies:
        report(19, "NOT MEASURABLE", "no bodies/*.md found")
        return
    over = [b for b in bodies if len(read(b)) >= 32000]
    qa = read("qa-step4.md") or ""
    m = re.search(r"Description not truncated[^\n|]*\|\s*(\d+)\s*/\s*(\d+)", qa)
    trunc_problem = None
    if m and m.group(1) != m.group(2):
        trunc_problem = f"truncation check {m.group(1)}/{m.group(2)}"
    problems = [f"{b}: {len(read(b))} chars" for b in over] + ([trunc_problem] if trunc_problem else [])
    report(19, "FAIL" if problems else "PASS", "; ".join(problems))


# ---------------------------------------------------------------------------
# E20: writing checklist
# ---------------------------------------------------------------------------

def eval_e20():
    import tempfile
    targets = glob.glob("bodies/*.md")
    cb = comment_bodies_text()
    tmp_comments = None
    if cb is not None:
        fd, tmp_comments = tempfile.mkstemp(suffix=".md", prefix="e20-comment-bodies-")
        with os.fdopen(fd, "w") as fh:
            fh.write(cb)
        targets.append(tmp_comments)
    if os.path.exists("cluster_analysis_prose.md"):
        targets.append("cluster_analysis_prose.md")
    if not targets:
        report(20, "NOT MEASURABLE", "no bodies/, ticket-comments.md or cluster_analysis_prose.md found")
        return
    try:
        rc, out = run_script(["check_tickets.py", "--writing"] + targets)
    finally:
        if tmp_comments and os.path.exists(tmp_comments):
            os.remove(tmp_comments)
    report(20, "PASS" if rc == 0 else "FAIL", "" if rc == 0 else "; ".join(out.strip().split("\n")[1:6]))


# ---------------------------------------------------------------------------
# E21: no conflict-flag ticket while the scope is off
# ---------------------------------------------------------------------------

def eval_e21():
    rc, out = run_script(["check_tickets.py", "--conflict"])
    report(21, "PASS" if rc == 0 else "FAIL", "" if rc == 0 else "; ".join(out.strip().split("\n")[1:6]))


# ---------------------------------------------------------------------------
# E22: report categories and judges are valid
# ---------------------------------------------------------------------------

def eval_e22():
    if not os.path.exists("report_defs.py"):
        report(22, "NOT MEASURABLE", "no report_defs.py (Step 5 not reached)")
        return
    import report_defs as R
    cfg = RC.load("round.json")
    # The taxonomy is the skill's, not the round's: read it from the spec's category table.
    spec_path = os.path.join(os.path.dirname(HERE), "references", "cluster-report-spec.md")
    valid_cats = {RC.col(r, "category") for r in RC.parse_table_after(read(spec_path) or "", "Seven categories")}
    round_cats = set(getattr(R, "CATEGORIES", []))
    if valid_cats and round_cats and round_cats != valid_cats:
        report(22, "FAIL", f"report_defs.CATEGORIES differs from the spec taxonomy: {sorted(round_cats ^ valid_cats)}")
        return
    valid_cats = valid_cats or round_cats
    judges_doc = cfg.get("judges_doc")
    judges_path = RC.repo_path(judges_doc)
    known_judges = set()
    if judges_path and os.path.exists(judges_path):
        known_judges = set(re.findall(r"`([a-z_]+)`", read(judges_path) or ""))
    problems = []
    for key, (primary, secondary, judges) in getattr(R, "CAT", {}).items():
        if valid_cats and primary not in valid_cats:
            problems.append(f"{key}: primary category {primary!r} not in the taxonomy")
        if secondary and valid_cats and secondary not in valid_cats:
            problems.append(f"{key}: secondary category {secondary!r} not in the taxonomy")
        if known_judges:
            for j in re.split(r",\s*", judges):
                jn = j.split(" (")[0].strip()
                if not jn.startswith(("none dedicated", "none confirmed")) and jn.split()[0] not in known_judges:
                    problems.append(f"{key}: judge {jn!r} not found in the judge doc")
    if not known_judges:
        problems = [p for p in problems if "judge" not in p]
        note = " (judge doc not readable from here; judge names not checked)"
    else:
        note = ""
    report(22, "FAIL" if problems else "PASS", "; ".join(problems) + note)


# ---------------------------------------------------------------------------
# E23 to E25: the filing floor, the watch list and the scale (priority-rubric.md sections 0 and 2)
# ---------------------------------------------------------------------------

def fm_summary():
    """failure-modes.md section 1 rows keyed by FM id, or None when no row has a filing call
    (a round built before skill v2.0)."""
    rows = {RC.col(r, "failure mode"): r for r in RC.parse_table_after(read("failure-modes.md") or "", "## 1. Summary")}
    if not any(RC.col(r, "filing call") and not RC.col(r, "filing call").startswith("-") for r in rows.values()):
        return None
    return rows


def round_defs():
    """(CALL, CONSOLIDATE, decision-item IDs) from cluster_defs.py."""
    import cluster_defs as C
    return getattr(C, "CALL", {}), getattr(C, "CONSOLIDATE", {}), set(getattr(C, "DECISIONS", {}))


def plan_fms(text):
    return {RC.col(r, "ticket"): r for r in RC.parse_table_after(text, "| Ticket |") if re.fullmatch(r"T-\d+", RC.col(r, "ticket"))}


def eval_e23():
    fms, fl, tp = fm_summary(), read("filing-ledger.md"), read("ticket-plan.md")
    if fms is None or not fl or not tp:
        report(23, "NOT MEASURABLE", "no filing calls in failure-modes.md (built before skill v2.0), or no filing-ledger.md or ticket-plan.md")
        return
    call, _, decisions = round_defs()
    plan = plan_fms(tp)
    problems, n = [], 0
    for r in (r for t in RC.parse_tables(fl) for r in t if re.fullmatch(r"T-\d+", RC.col(r, "draft") or "")):
        t, key = RC.col(r, "draft"), RC.col(r, "key")
        fid = RC.col(plan.get(t, {}), "fm")
        if fid in decisions or (fid and not fid.startswith("FM-")):
            continue
        if fid not in fms:
            problems.append(f"{t} ({key}): no ticket-plan.md FM in failure-modes.md")
            continue
        n += 1
        inst = int(RC.col(fms[fid], "counted instances") or 0)
        severe = RC.col(fms[fid], "severity class") == "severe safety"
        if inst >= 2 or (inst >= 1 and severe) or call.get(fid) == "file":
            continue
        problems.append(f"{t} ({key}, {fid}): {inst} counted instance(s), {RC.col(fms[fid], 'severity class') or 'no severity'}, "
                        "no Gate 2 'file' call")
    report(23, "FAIL" if problems else "PASS", "; ".join(problems) or f"{n} filed Bugs checked")


def ledger_path():
    """The evidence ledger: `ledger` in round.json, else the folder above the round folder."""
    return RC.load("round.json").get("ledger") or os.path.join("..", "Failure-Mode-Evidence-Ledger.md")


def ledger_module():
    import ledger_tool
    return ledger_tool


def eval_e24():
    fms = fm_summary()
    if fms is None:
        report(24, "NOT MEASURABLE", "no filing calls in failure-modes.md (built before skill v2.0)")
        return
    _, consolidate, _ = round_defs()
    dropped = RC.gate3_dropped(consolidate)
    held = [f for f, r in fms.items() if RC.col(r, "filing call").startswith("hold") and f not in dropped]
    path = ledger_path()
    if not os.path.exists(path):
        report(24, "NOT MEASURABLE", f"no evidence ledger at {path}")
        return
    LT = ledger_module()
    _, srows, _, nrows = LT.load(path)
    note = {n["ID"]: n["Note"] for n in nrows}
    slug = RC.load("round.json").get("slug", "round")
    held_rows = [s for s in srows if s["Status"].strip().lower().startswith("held")]
    keys = lambda f: (f"{slug}/{f}", f"UNT-{slug}-{f.replace('-', '')}")  # noqa: E731  (the seeded rows use the UNT form)
    missing = [f for f in held if not any(k in note.get(s["ID"], "") for s in held_rows for k in keys(f))]
    report(24, "FAIL" if missing else "PASS",
           f"held but not a `held` ledger row (its Note must carry `{slug}/<FM id>`): {', '.join(missing)}" if missing
           else f"{len(held)} held failure modes, all on the evidence ledger")


def eval_e25():
    fms, tp = fm_summary(), read("ticket-plan.md")
    if fms is None or not tp:
        report(25, "NOT MEASURABLE", "no filing calls in failure-modes.md (built before skill v2.0), or no ticket-plan.md")
        return
    _, _, decisions = round_defs()
    problems, checked, unscored = [], 0, []
    for t, r in plan_fms(tp).items():
        fid = RC.col(r, "fm")
        if fid in decisions or (fid and not fid.startswith("FM-")):
            continue
        lvl = RC.col(fms.get(fid, {}), "level")
        if lvl in ("", "-"):
            unscored.append(t)
            continue
        checked += 1
        rec = RC.col(r, "recommended priority")
        if (re.match(r"P\d", rec) or [""])[0] != lvl:
            s = fms[fid]
            problems.append(f"{t} ({fid}): plan recommends {rec or 'nothing'}, the scale gives {lvl} "
                            f"({RC.col(s, 'severity class')}, {RC.col(s, 'band')})")
    note = f"; no rubric level for {', '.join(unscored)}" if unscored else ""
    if not checked and not problems:
        report(25, "NOT MEASURABLE", "no ticket-plan.md row has a rubric level" + note)
        return
    report(25, "FAIL" if problems else "PASS", ("; ".join(problems) or f"{checked} plan rows match the scale") + note)


# ---------------------------------------------------------------------------
# E26 to E29: token-efficiency guards (v2.1): nesting, resume continuity, dedup QA and
# format-checker key coverage
# ---------------------------------------------------------------------------

SESSION_RE = re.compile(r"\bsession ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b")
ARTIFACT_PREFIXES = {"FM", "T", "C", "D", "CR", "SP"}


def run_log_sessions():
    """[(ts, session id, resumed)] from run-log.md `note` events that name a session, in log
    order, or None when run-log.md is missing."""
    text = read("run-log.md")
    if text is None:
        return None
    out = []
    for line in text.split("\n"):
        m = re.match(r"^(\S+) \| [^|]+ \| note \|(.*)$", line)
        s = SESSION_RE.search(m.group(2)) if m else None
        if s:
            out.append((m.group(1), s.group(1), "resumed from STATUS.md" in m.group(2)))
    return out


def jira_keys(text):
    """Jira keys in text, minus session-artifact IDs (FM-, T-, C-, D-, CR-, SP- and batch-code rows)."""
    skip = ARTIFACT_PREFIXES | set(RC.batch_codes(RC.load("round.json")))
    return {k for k in re.findall(r"\b[A-Z][A-Z0-9]*-\d+\b", text or "") if k.split("-")[0] not in skip}


def eval_e26():
    sess = run_log_sessions()
    if not sess:
        report(26, "NOT MEASURABLE", "no `note` event in run-log.md names a session ID")
        return
    base = os.path.expanduser(os.path.join("~", ".claude", "projects"))
    problems, n, found = [], 0, []
    for sid in dict.fromkeys(s for _, s, _ in sess):
        metas = glob.glob(os.path.join(base, "*", sid, "subagents", "*.meta.json"))
        if metas:
            found.append(sid)
        for f in metas:
            try:
                meta = json.load(open(f))
            except (OSError, json.JSONDecodeError):
                continue
            n += 1
            depth = meta.get("spawnDepth")
            if isinstance(depth, int) and depth > 1:
                problems.append(f"session {sid[:8]}: {os.path.basename(f)} ({meta.get('agentType')}) has spawnDepth {depth}")
    if not found:
        report(26, "NOT MEASURABLE", f"no subagent metadata under {base} for the {len(set(s for _, s, _ in sess))} logged session(s)")
        return
    report(26, "FAIL" if problems else "PASS", "; ".join(problems[:10]) or f"{n} subagents in {len(found)} session(s), none nested")


def eval_e27():
    sess = run_log_sessions()
    if not sess:
        report(27, "NOT MEASURABLE", "no `note` event in run-log.md names a session ID")
        return
    problems, seen = [], []
    for ts, sid, resumed in sess:
        if sid in seen:
            continue
        if seen and not resumed:
            problems.append(f"session {sid[:8]} ({ts}): its first note does not say 'resumed from STATUS.md'")
        seen.append(sid)
    status, log = read("STATUS.md") or "", read("run-log.md") or ""
    for gate, section in (("Gate 2", "Gate 2 answers"), ("Gate 3", "Gate 3 record")):
        m = re.search(rf"^## {section}\s*$(.*?)(?=^## |\Z)", status, re.M | re.S)
        decisions = [l for l in (m.group(1) if m else "").split("\n") if l.strip() and not l.lstrip().startswith("#")]
        if decisions and not re.search(rf"\| gate_answered \|.*\bgate=`?{gate}\b", log):
            problems.append(f"STATUS.md '{section}' holds {len(decisions)} line(s) and run-log.md has no gate_answered for {gate}")
    report(27, "FAIL" if problems else "PASS", "; ".join(problems) or f"{len(seen)} session(s), resumes and gate answers logged")


def eval_e28():
    dv, qas = read("dedup-verdicts.md"), sorted(glob.glob("dedup-qa-*.md"))
    if not dv or not qas:
        report(28, "NOT MEASURABLE", "no dedup-verdicts.md or no dedup-qa-*.md")
        return
    reread = set()
    for path in qas:
        for row in RC.parse_table_after(read(path), "Tickets read"):
            reread |= jira_keys(RC.col(row, "key"))
    missing = sorted(jira_keys(dv) - reread)
    report(28, "FAIL" if missing else "PASS",
           f"cited in dedup-verdicts.md with no dedup QA 'Tickets read' row: {', '.join(missing)}" if missing
           else f"{len(reread)} keys reread by dedup QA")


def eval_e29():
    drafts = (read("ticket-drafts.md") or "") + "\n" + (read("ticket-comments.md") or "")
    qas = sorted(glob.glob("qa-step3-format*.md"))
    if not drafts.strip() or not qas:
        report(29, "NOT MEASURABLE", "no ticket-drafts.md or ticket-comments.md, or no qa-step3-format*.md")
        return
    verified = {}
    for path in qas:
        for row in RC.parse_table_after(read(path), "Jira keys verified"):
            for k in jira_keys(RC.col(row, "key")):
                verified[k] = RC.col(row, "method").strip("` ")
    if not verified:
        report(29, "NOT MEASURABLE", "no 'Jira keys verified' table in qa-step3-format*.md (built before skill v2.1)")
        return
    problems = []
    for k in sorted(jira_keys(drafts)):
        method = verified.get(k)
        if method is None:
            problems.append(f"{k}: not in 'Jira keys verified'")
        elif not re.match(r"(full read|scope cell \(dedup-qa-[^)]+\.md\))", method):
            problems.append(f"{k}: method {method!r} is not 'full read' or 'scope cell (<dedup-qa file>)'")
    report(29, "FAIL" if problems else "PASS", "; ".join(problems[:10]) or f"{len(verified)} keys verified")


def eval_e30():
    path = ledger_path()
    fl, cl = read("filing-ledger.md"), read("comment-ledger.md")
    if not os.path.exists(path) or not (fl or cl):
        report(30, "NOT MEASURABLE", f"no evidence ledger at {path}, or no filing-ledger.md or comment-ledger.md")
        return
    problems = []
    rc, out = run_script(["ledger_tool.py", "check", path])
    if rc:
        problems.append("ledger_tool.py check: " + out.strip().split("\n")[0])
    _, srows, _, _ = ledger_module().load(path)
    have = {s["Ticket"] for s in srows}
    filed = {RC.col(r, "key") for t in RC.parse_tables(fl or "") for r in t if re.fullmatch(r"T-\d+", RC.col(r, "draft") or "")}
    posted = {RC.col(r, "target") for t in RC.parse_tables(cl or "") for r in t if re.fullmatch(r"C-\d+", RC.col(r, "comment") or "")}
    missing = sorted((filed | posted) - have)
    if missing:
        problems.append("filed or commented keys with no ledger row: " + ", ".join(missing))
    report(30, "FAIL" if problems else "PASS", "; ".join(problems) or f"ledger consistent; {len(filed | posted)} filed or commented keys all have a row")


def eval_e31():
    fl = read("filing-ledger.md")
    if not fl:
        report(31, "NOT MEASURABLE", "no filing-ledger.md")
        return
    rows = [r for t in RC.parse_tables(fl) for r in t if re.fullmatch(r"T-\d+", RC.col(r, "draft") or "")]
    if not rows:
        report(31, "NOT MEASURABLE", "no filed rows in filing-ledger.md")
        return
    bad = [RC.col(r, "key") for r in rows if RC.col(r, "priority").strip().upper().startswith("P3")]
    report(31, "FAIL" if bad else "PASS",
           f"new tickets filed at P3: {', '.join(bad)}" if bad else f"{len(rows)} filed tickets, none at P3")


def source_records():
    """{trace prefix (tr- plus 10 hex): record text} from this round's export/*.md and every
    prior_rounds export (an `Earlier round:` bullet's block comes from one)."""
    cfg = RC.load("round.json")
    out = {}
    paths = sorted(glob.glob(os.path.join("export", "*.md")))
    for path in paths:
        for part in re.split(r"\n(?=## \d+\. )", read(path))[1:]:
            m = RC.EXPORT_TRACE_RE.search(part)
            if m:
                out[m.group(1)[:13]] = part
    for full, (path, _a) in RC.prior_round_exports(cfg).items():
        if full[:13] not in out:
            for part in re.split(r"\n(?=## \d+\. )", read(path))[1:]:
                m = RC.EXPORT_TRACE_RE.search(part)
                if m and m.group(1) == full:
                    out[full[:13]] = part
                    break
    return out


def eval_e32():
    blocks = sorted(glob.glob(os.path.join("thread-blocks", "*.md")))
    if not blocks:
        report(32, "NOT MEASURABLE", "no thread-blocks/*.md")
        return
    records = source_records()
    url_re = re.compile(r"https?://[^\s<>\"]*[^\s<>\".,;:!?)\]]")
    problems, n = [], 0
    for path in blocks:
        for part in re.split(r"\n(?=### `tr-)", read(path)):
            m = re.match(r"### `(tr-[0-9a-fA-F]{10})`", part)
            if not m:
                continue
            n += 1
            rec = records.get(m.group(1))
            if rec is None:
                problems.append(f"{path} {m.group(1)}: no export record to compare with")
                continue
            # A block holds only the messages before the draft and the draft itself.
            head, _, rest = rec.partition("**Provider draft**")
            rec = head + rest.split("**Explanation**", 1)[0]
            lines = part.split("\n")
            for u in sorted(set(url_re.findall(rec))):
                if not any(u in l for l in lines):
                    problems.append(f"{path} {m.group(1)}: URL not on one line: {u}")
            toks = set(rec.split())
            run = []  # consecutive non-blank blockquote lines of one message or draft
            for l in lines + [""]:
                if l.startswith("> ") and l[2:].strip():
                    run.append(l[2:].strip())
                    continue
                if l.strip() == ">":
                    continue  # a paragraph break inside the same quote
                for a, b in zip(run, run[1:]):
                    ta, tb = a.split()[-1], b.split()[0]
                    if re.search(r"[A-Za-z0-9]$", ta) and re.match(r"[A-Za-z0-9]", tb) \
                            and any((ta + tb) in t for t in toks):
                        problems.append(f"{path} {m.group(1)}: a line ends mid-word or mid-URL: ...{ta} | {tb}...")
                run = []
    report(32, "FAIL" if problems else "PASS",
           "; ".join(problems[:6]) if problems else f"{n} thread blocks, no URL or word split across lines")


def eval_e33():
    text = read("ticket-comments.md")
    qas = sorted(glob.glob("qa-step3-format*.md"))
    if not text or not qas:
        report(33, "NOT MEASURABLE", "no ticket-comments.md or no qa-step3-format*.md")
        return
    targets = {}
    for m in re.finditer(r"^### C-\d+\. Comment on ([A-Z][A-Z0-9]*-\d+)\b", text, re.M):
        targets[m.group(1)] = True
    verified = {}  # key -> every Method any qa-step3-format*.md round recorded for it
    for path in qas:
        for row in RC.parse_table_after(read(path), "Jira keys verified"):
            for k in jira_keys(RC.col(row, "key")):
                verified.setdefault(k, []).append(RC.col(row, "method").strip("` "))
    if not verified:
        report(33, "NOT MEASURABLE", "no 'Jira keys verified' table in qa-step3-format*.md")
        return
    bad = [f"{k} ({'; '.join(verified.get(k, ['not in the table']))})" for k in sorted(targets)
           if not any(m.startswith("full read") for m in verified.get(k, []))]
    report(33, "FAIL" if bad else "PASS",
           ("comment targets without a full read: " + ", ".join(bad)) if bad
           else f"{len(targets)} comment targets, each read in full")


def eval_e34():
    import counting as K
    files = [f for f in ("ticket-drafts.md", "ticket-comments.md") if os.path.exists(f)]
    if not files or not os.path.exists("ratings.md"):
        report(34, "NOT MEASURABLE", "no ticket-drafts.md or ticket-comments.md, or no ratings.md")
        return
    raters = {t[:13]: hs for t, hs in K.trace_raters("ratings.md").items()}
    form = re.compile(r"^- `?(tr-[0-9a-fA-F]{10})`? \([^)]*\)\.\s+([a-z]+_\d+) \((?:GOOD|BAD)\):")
    problems, n = [], 0
    for path in files:
        for i, l in enumerate(read(path).split("\n"), 1):
            m = form.match(l)
            if m:
                n += 1
                if m.group(2) not in raters.get(m.group(1), set()):
                    problems.append(f"{path}:{i}: {m.group(1)} uses the Rating form for {m.group(2)}, who left no rating on it")
    report(34, "FAIL" if problems else "PASS", "; ".join(problems[:6]) if problems else f"{n} Rating-form bullets, each backed by a rating")


def eval_e35():
    files = [f for f in ("ticket-drafts.md", "ticket-comments.md") if os.path.exists(f)]
    if "ticket-drafts.md" not in files:
        report(35, "NOT MEASURABLE", "no ticket-drafts.md")
        return
    problems = []
    for mode in ("--traces", "--threads"):
        rc, out = run_script(["check_tickets.py", mode] + (files if mode == "--traces" else ["ticket-drafts.md"]))
        if rc:
            problems += [l.strip() for l in out.split("\n") if l.startswith(" -")][:3] or [f"check_tickets.py {mode} exited {rc}"]
    report(35, "FAIL" if problems else "PASS", "; ".join(problems) or "every cited trace resolves (an Earlier round: bullet in a prior_rounds export) and has its thread block")


def eval_e36():
    fm = read("failure-modes.md")
    if not fm:
        report(36, "NOT MEASURABLE", "no failure-modes.md")
        return
    problems = []
    cells = {}
    for r in RC.parse_table_after(fm, "## 1. Summary"):
        cells[RC.col(r, "failure mode")] = RC.col(r, "providers").strip()
    n = 0
    for m in re.finditer(r"^### (FM-\d+):.*?^- \*\*Counts:\*\*[^\n]*?providers: ([^;\n]*);", fm, re.S | re.M):
        n += 1
        fid, listed = m.group(1), [h.strip() for h in m.group(2).split(",") if h.strip() and h.strip() != "none"]
        bad = [h for h in listed if h.startswith("unresolved:tr-")]
        if listed.count("unresolved") > 1:
            bad.append("unresolved listed twice")
        if bad:
            problems.append(f"{fid}: {', '.join(bad)} (every unresolved reviewer is one provider, named `unresolved`)")
        cell = cells.get(fid, "")
        want = len(listed)
        got = int(cell.split()[0]) if cell[:1].isdigit() else 0 if cell == "none" else None
        if got is not None and got != want:
            problems.append(f"{fid}: Providers column says {got}, Counts line lists {want}")
    if not n:
        report(36, "NOT MEASURABLE", "no failure-mode Counts lines in failure-modes.md")
        return
    report(36, "FAIL" if problems else "PASS", "; ".join(problems[:6]) or f"{n} failure modes; unresolved reviewers count once")


def eval_e37():
    # Run make_blind.py in a temp folder holding round.json and ONE draft file, so most batch codes
    # have no file whatever the round holds, and the round's real blind file is never rewritten.
    import shutil
    import subprocess
    import tempfile
    one = next((f for f in sorted(glob.glob("ticket-drafts-*.md")) if "blind" not in f and "### T-" in read(f)), None)
    if not one:
        report(37, "NOT MEASURABLE", "no ticket-drafts-<code>.md holds a ticket")
        return
    tmp = tempfile.mkdtemp()
    try:
        shutil.copy("round.json", tmp)
        shutil.copy(one, tmp)
        p = subprocess.run([sys.executable, "-I", os.path.join(HERE, "make_blind.py")], cwd=tmp, capture_output=True, text=True)
        out = (p.stdout or "") + (p.stderr or "")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    report(37, "FAIL" if p.returncode else "PASS", out.strip().split("\n")[-1][:200] if p.returncode else out.strip().split("\n")[0][:200])


def eval_e38():
    """A round at v3.0 or later writes no checklist row (Evidence basis inferred, Reviewer audit,
    or band audit-only). A round whose ledger still has the pre-v3.0 coverage phrase is not scored."""
    import counting as K
    from mechanical_check import ledger_rows, col
    legacy, hits = False, []
    for b in RC.batch_codes(RC.load("round.json")):
        for r in ledger_rows(b) or []:
            basis, reviewer = K.basis(r), col(r, "reviewer").strip()
            atomic = col(r, "atomic issue")
            if "audited, no issue found" in atomic or (
                    col(r, "provenance") == "inferred" and basis == "provider-edit" and reviewer == "audit"):
                legacy = True
            if basis == "inferred" or reviewer == "audit":
                hits.append(col(r, "row id") or b)
    bands = [RC.col(r, "failure mode") for r in RC.parse_table_after(read("failure-modes.md") or "", "## 1. Summary")
             if RC.col(r, "band") == "audit-only"]
    if legacy:
        report(38, "NOT MEASURABLE", "ledger still has pre-v3.0 checklist rows; this round is not scored")
        return
    problems = []
    if hits:
        problems.append("checklist rows: " + ", ".join(hits[:8]))
    if bands:
        problems.append("band audit-only: " + ", ".join(bands[:8]))
    report(38, "FAIL" if problems else "PASS", "; ".join(problems) or "no inferred basis, audit reviewer, or audit-only band")


def eval_e39():
    """A ledger Expected-behavior cell never cites a clinical-rules row whose Status
    contains 'superseded by'. A round with no such status is not scored (rounds before v3.1)."""
    text = read("clinical-rules.md")
    if not text:
        report(39, "NOT MEASURABLE", "no clinical-rules.md")
        return
    dead = set()
    for table in RC.parse_tables(text):
        for row in table:
            rid = RC.col(row, "id").strip().strip("`")
            if rid.startswith("CR-") and "superseded by" in RC.col(row, "status").lower():
                dead.add(rid)
    if not dead:
        report(39, "NOT MEASURABLE", "no clinical-rules row has Status containing 'superseded by'; a round built before v3.1 is not scored")
        return
    from mechanical_check import ledger_rows, col
    problems = []
    for b in RC.batch_codes(RC.load("round.json")):
        for r in ledger_rows(b) or []:
            cited = set(re.findall(r"CR-[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*", col(r, "expected behavior")))
            hit = sorted(cited & dead)
            if hit:
                problems.append(f"{col(r, 'row id') or b}: {', '.join(hit)}")
    report(39, "FAIL" if problems else "PASS", "; ".join(problems[:6]) or f"{len(dead)} superseded rows; none cited in an Expected-behavior cell")


def safe(n, fn, *args):
    """Run one eval in isolation. An uncaught exception (a missing file an eval's own guard did
    not anticipate, a malformed table, ...) is reported as NOT MEASURABLE for that eval only, so
    one eval's bug or a round's missing artifact never stops the rest of the suite from running."""
    before = len(RESULTS)
    try:
        fn(*args)
    except Exception as e:
        if len(RESULTS) == before:
            report(n, "NOT MEASURABLE", f"eval raised {type(e).__name__}: {e}")
    if len(RESULTS) == before:
        report(n, "NOT MEASURABLE", "eval did not report a result")


def main():
    args = sys.argv[1:]
    scratch = None
    if "--scratch" in args:
        scratch = args[args.index("--scratch") + 1]
    trace_path = None
    if "--trace" in args:
        trace_path = args[args.index("--trace") + 1]

    if not os.path.exists("round.json"):
        print("run_evals.py: round.json not found; run from the round folder", file=sys.stderr)
        sys.exit(1)

    safe(1, eval_e1)
    safe(2, eval_e2)
    safe(3, eval_e3)
    safe(4, eval_e4)
    safe(5, eval_e5)
    safe(6, eval_e6)
    safe(7, eval_e7)
    safe(8, eval_e8)
    safe(9, eval_e9)
    safe(10, eval_e10)
    safe(11, eval_e11)
    safe(12, eval_e12, scratch)
    print("E13 NOT MEASURABLE judge eval; spawn the E13 subagent separately")
    safe(14, eval_e14)
    safe(15, eval_e15)
    safe(16, eval_e16, trace_path)
    safe(17, eval_e17)
    safe(18, eval_e18)
    safe(19, eval_e19)
    safe(20, eval_e20)
    safe(21, eval_e21)
    safe(22, eval_e22)
    safe(23, eval_e23)
    safe(24, eval_e24)
    safe(25, eval_e25)
    safe(26, eval_e26)
    safe(27, eval_e27)
    safe(28, eval_e28)
    safe(29, eval_e29)
    safe(30, eval_e30)
    safe(31, eval_e31)
    safe(32, eval_e32)
    safe(33, eval_e33)
    safe(34, eval_e34)
    safe(35, eval_e35)
    safe(36, eval_e36)
    safe(37, eval_e37)
    safe(38, eval_e38)
    safe(39, eval_e39)

    fails = [n for n, s in RESULTS if s == "FAIL"]
    passes = [n for n, s in RESULTS if s == "PASS"]
    nm = [n for n, s in RESULTS if s == "NOT MEASURABLE"]
    print(f"\n{len(passes)} PASS, {len(fails)} FAIL, {len(nm)} NOT MEASURABLE (of {len(RESULTS)} code evals; E13 is a judge)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
