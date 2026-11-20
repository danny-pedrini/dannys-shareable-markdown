"""Build the data sections of the cluster-analysis report and the rating-rows CSV (Step 5).

Inputs (round folder): cluster_defs.py, report_defs.py, ledger/*.md (via mechanical_check.py),
row-map.md, ratings.md, export/*.md (medication lines and action types only), thread-blocks/*.md
(name-anonymized messages and drafts), ticket-drafts.md (filed ticket bodies and the "Not filed"
table), ticket-comments.md, filing-ledger.md, ticket-plan.md, round.json.

The hand-written prose lives in cluster_analysis_prose.md and is stitched in at the
{{TABLES_A}} and {{TABLES_B}} markers; report and CSV file names come from round.json.

Evidence by source: each unit's counted drafts are split by derived source kind (counting.py).
Section 3c lists the failure modes held without a ticket or dropped at Gate 3. The trace
table covers every rated or counted trace. The CSV carries one row per rating plus one per
non-rating evidence row (an edit, a failed judge verdict, a Slack report or a session mention),
with a `source` column.
Run from the round folder:  python3 -I <skill>/scripts/build_cluster_analysis.py
"""
import collections
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.getcwd()
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import round_config as RC  # noqa: E402
import counting as K  # noqa: E402
from mechanical_check import ledger_rows, col  # noqa: E402
import load_ratings as LR  # noqa: E402
import report_defs as R  # noqa: E402
import cluster_defs as CD  # noqa: E402

cfg = RC.load(os.path.join(ROOT, "round.json"))
B = RC.batch_codes(cfg)
ACT = RC.action_map(cfg)
JIRA = RC.jira_site(cfg) + "/browse/"
REPORT_FILE, CSV_FILE = RC.report_paths(cfg)
if not REPORT_FILE or not CSV_FILE:
    print("build_cluster_analysis.py: round.json report.file and report.csv must both be set", file=sys.stderr)
    sys.exit(1)

CAT = R.CAT
ORDER = list(getattr(R, "CATEGORIES", []))
if not ORDER:
    ORDER = sorted({v[0] for v in CAT.values()})

# ---- ledger rows ----
rows = {}
for b in B:
    for r in (ledger_rows(b) or []):
        rows[col(r, "row id")] = r
fm = {f["id"]: f for f in getattr(CD, "FM", [])}
dest = {}
for l in open("row-map.md"):
    m = re.match(r"\| ([A-Z]{2}-\d{3}) \| [^|]+\| [^|]+\| [^|]+\| [^|]+\| ([^|]+) \|", l)
    if m:
        dest[m.group(1)] = m.group(2).strip()
SESSIONS = RC.session_batches(cfg)
RATING_MAP, DEFAULT_KIND = K.rating_sources(cfg)
SPREAD_BACKED = collections.defaultdict(set)  # FM -> counted spread traces, as build_cluster.py decided
for r in RC.parse_table_after(open("row-map.md").read(), "| Row |"):
    if RC.col(r, "row").startswith(f"{RC.SPREAD_CODE}-") and RC.col(r, "counted") == "yes":
        SPREAD_BACKED[RC.col(r, "destination")].add(RC.col(r, "trace")[:13])
KIND_WORDS = {"thumbs-downs": "thumbs-downs", "labeling": "labeling", "edits": "edits", "evals": "evals",
              "interviews": "interviews", "slack": "Slack", "ratings": "ratings", "scan": "phrase scan"}


def kind_of(r):
    return K.source_kind(r, cfg, SESSIONS, RATING_MAP, DEFAULT_KIND)


TRACE_RATERS = K.trace_raters("ratings.md")


def people(r):
    """The providers behind an evidence row. A legacy edit-diff row carries Reviewer `audit`, but
    the edit is the trace's rater's (`priority-rubric.md` section 2)."""
    rv = col(r, "reviewer")
    if rv not in K.NON_PERSON:
        return {rv}
    if K.basis(r) in ("provider-edit", "provider-edit+note"):
        return set(TRACE_RATERS.get(col(r, "trace id"), ()))
    return set()


def who_label(r):
    """How an evidence row names its source: a reviewer handle, a provider edit, a legacy checklist
    row, or an eval judge."""
    rv = col(r, "reviewer")
    if K.is_audit(r):
        return "legacy audit"
    if rv == "eval":
        return f"eval judge {col(r, 'error tag').replace('judge:', '').strip()}"
    if rv in K.NON_PERSON:
        return f"{', '.join(sorted(people(r))) or 'provider'} (edit)"
    return f"{rv} ({col(r, 'verdict').upper()})"

# ---- ticket plan and filed keys ----
plan = {}
merged_from = {}  # T-n -> FM ids the plan folded into that ticket (the plan's "Merged from" column)
_mf_idx = None
for l in open("ticket-plan.md"):
    if l.startswith("| Ticket |"):
        _hdr = [c.strip().lower() for c in l.strip().strip("|").split("|")]
        _mf_idx = _hdr.index("merged from") if "merged from" in _hdr else None
        continue
    m = re.match(r"\| (T-\d+) \| (FM-\d+) \|", l)
    if m:
        plan[m.group(1)] = m.group(2)
        _cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if _mf_idx is not None and _mf_idx < len(_cells):
            merged_from[m.group(1)] = re.findall(r"FM-\d+", _cells[_mf_idx])
keys = {}
for l in open("filing-ledger.md"):
    m = re.match(r"\| (T-\d+) \| ([A-Z]+-\d+) \| ([^|]+) \| ([^|]+) \|", l)
    if m:
        keys[m.group(1)] = (m.group(2), m.group(3).strip(), m.group(4).strip())

# "Merged into" and "Dropped" lines in ticket-drafts.md's "Not filed" table drive consolidation,
# instead of a hard-coded map of which tickets got absorbed into which.
absorbed, dropped = {}, set()
if "## 2. Not filed" in open("ticket-drafts.md").read():
    section = open("ticket-drafts.md").read().split("## 2. Not filed", 1)[1].split("\n## ", 1)[0]
    for l in section.split("\n"):
        m = re.match(r"\|\s*(T-\d+)\s*\|\s*Merged into\s*(T-\d+)\s*\|", l)
        if m:
            absorbed[m.group(1)] = m.group(2)
        m = re.match(r"\|\s*(T-\d+)\s*\|\s*Dropped\b", l)
        if m:
            dropped.add(m.group(1))


def merge_target(t):
    """Follow a chain of "Merged into" lines to the first filed ticket, or to its end."""
    seen = {t}
    while t in absorbed and t not in keys and absorbed[t] not in seen:
        t = absorbed[t]
        seen.add(t)
    return t


def warn(msg):
    print(f"build_cluster_analysis.py: warning: {msg}", file=sys.stderr)


for t in sorted(dropped, key=lambda x: int(x[2:])):
    if t not in plan:
        warn(f"{t} is Dropped in ticket-drafts.md but has no ticket-plan.md row")
    if t in keys:
        warn(f"{t} is Dropped in ticket-drafts.md but filed in filing-ledger.md as {keys[t][0]}")
for a in sorted(absorbed, key=lambda x: int(x[2:])):
    into = merge_target(a)
    if a in keys:
        warn(f"{a} is filed as {keys[a][0]} but also Merged into {absorbed[a]}; it stays its own ticket")
    elif into in absorbed and into not in keys:
        warn(f"{a}: the Merged into chain loops back on itself; its FMs stay unplaced")
    elif into not in keys and into not in dropped:
        warn(f"{a} is Merged into {into}, which is neither filed nor dropped; its FMs stay unplaced")
    if a not in plan:
        warn(f"{a} is Merged into {absorbed[a]} but has no ticket-plan.md row")
    elif plan[a] not in fm:
        warn(f"{a}'s plan FM {plan[a]} is not in cluster_defs.FM")

_dropped_t = dropped | {a for a in absorbed if merge_target(a) in dropped}
dropped_fms = {f for t in _dropped_t for f in [plan.get(t)] + merged_from.get(t, []) if f}
dropped_fms |= {a for f in list(dropped_fms) for a in getattr(CD, "CONSOLIDATE", {}).get(f, "").split()}

# A row an EXISTING unit explicitly claims (its optional `rows` override) is excluded from the
# filed ticket for the same failure mode, so a split failure mode's rows are never double-counted.
existing_claimed = collections.defaultdict(set)
for item in R.EXISTING:
    rows_override = (item.get("rows") or "").split()
    if rows_override:
        for f in item["fms"].split():
            existing_claimed[f].update(rows_override)

# A "Merged from" FM joins a ticket only when no ticket's plan, absorbed ticket or whole-FM
# EXISTING unit already holds it, so one FM never lands in two units.
_owned = {plan[t] for t in keys if t in plan}
_owned |= {plan[a] for a in absorbed if a in plan and merge_target(a) in keys}
_owned |= {f for item in R.EXISTING if not item.get("rows") for f in item["fms"].split()}



def unclaimed(f):
    """f's rows no EXISTING unit claims; None when an EXISTING unit claims every one."""
    left = [r for r in fm[f]["rows"].split() if r not in existing_claimed.get(f, set())]
    return None if not left and f in existing_claimed else left


units = collections.OrderedDict()  # unit id -> dict
for t in sorted(keys, key=lambda x: int(x[2:])):
    k, title, pr = keys[t]
    fm_id = plan.get(t)
    if fm_id is None or fm_id not in fm:
        print(f"build_cluster_analysis.py: {t} (filed as {k}) has no ticket-plan.md row mapping it to a failure mode", file=sys.stderr)
        sys.exit(1)
    full_rows = fm[fm_id]["rows"].split()
    unit_rows = [r for r in full_rows if r not in existing_claimed.get(fm_id, set())]
    units[k] = {"key": k, "title": title, "priority": pr, "status": "Filed", "fms": [fm_id], "rows": unit_rows, "t": t}
    # Failure modes the ticket plan merged into this ticket (the plan's "Merged from" column).
    for a_fm in merged_from.get(t, []):
        if a_fm in fm and a_fm not in _owned and unclaimed(a_fm) is not None:
            _owned.add(a_fm)
            units[k]["fms"].append(a_fm)
            units[k]["rows"] += [r for r in unclaimed(a_fm) if r not in units[k]["rows"]]
for a in absorbed:
    into = merge_target(a)
    if into not in keys or a not in plan:
        continue
    k = keys[into][0]
    for a_fm in [plan[a]] + [f for f in merged_from.get(a, []) if f not in _owned]:
        if a_fm in fm and a_fm not in units[k]["fms"] and unclaimed(a_fm) is not None:
            _owned.add(a_fm)
            units[k]["fms"].append(a_fm)
            units[k]["rows"] += [r for r in unclaimed(a_fm) if r not in units[k]["rows"]]

comments = {}
if os.path.exists("ticket-comments.md"):
    for b in re.split(r"\n(?=### C-\d+\. )", open("ticket-comments.md").read())[1:]:
        m = re.match(r"### (C-\d+)\. Comment on ((?:[A-Z]+)-\d+) \((.*)\)", b)
        if not m:
            continue
        body = "\n".join(l for l in b.split("\n")[1:] if not re.match(r"- (Source failure mode|Purpose)\b", l)).strip()
        comments[m.group(2)] = (m.group(3).strip(), body)

for item in R.EXISTING:
    uid = item["unit"]
    if item.get("rows"):
        rows_for_unit = item["rows"].split()
    else:
        rows_for_unit = " ".join(fm[f]["rows"] for f in item["fms"].split() if f in fm).split()
    units[uid] = {"key": item["key"], "title": item.get("title", item["key"]), "priority": "existing ticket",
                  "status": item.get("status", "Existing ticket"), "fms": item["fms"].split(), "rows": rows_for_unit, "t": None}
# FMs that cluster_defs.CONSOLIDATE absorbed, in case the plan's optional "Merged from" left one out.
_placed = {f for u in units.values() if u["t"] is not None for f in u["fms"]}
_placed |= {f for item in R.EXISTING if not item.get("rows") for f in item["fms"].split()}
for u in units.values():
    if u["t"] is None:
        continue
    for f in list(u["fms"]):
        for a_fm in getattr(CD, "CONSOLIDATE", {}).get(f, "").split():
            if a_fm in fm and a_fm not in _placed and unclaimed(a_fm) is not None:
                _placed.add(a_fm)
                u["fms"].append(a_fm)
                u["rows"] += [r for r in unclaimed(a_fm) if r not in u["rows"]]

if set(units) != set(CAT):
    print("build_cluster_analysis.py: units and report_defs.CAT disagree:", set(units) ^ set(CAT), file=sys.stderr)
    sys.exit(1)
row_unit = {}
for uid, u in units.items():
    for r in u["rows"]:
        row_unit[r] = uid

# ---- ticket text (Problem first paragraph, first Expected bullet) ----
tick = {}
if "## 4. Full ticket drafts" in open("ticket-drafts.md").read():
    for b in re.split(r"\n(?=### T-\d+\. )", open("ticket-drafts.md").read().split("## 4. Full ticket drafts", 1)[1]):
        m = re.match(r"\s*### (T-\d+)\. ", b)
        if not m or "## Problem" not in b or "## Expected behavior" not in b or "## Evidence" not in b:
            continue
        prob = b.split("## Problem", 1)[1].split("\n## ", 1)[0].strip().split("\n\n")[0]
        exp = b.split("## Expected behavior", 1)[1].split("\n## ", 1)[0].strip().split("\n")[0].lstrip("- ")
        exp = re.sub(r"\s*\((?:[^()]*https?://[^()]*|[^()]*Clinical Guidelines[^()]*)\)", "", exp)
        trs = []
        for line in b.split("## Evidence", 1)[1].split("\n## ", 1)[0].split("\n"):
            if line.startswith("- ") and not line.lower().startswith("- also"):
                trs += [x for x in re.findall(r"tr-[0-9a-fA-F]{10}", line) if x not in trs]
        tick[m.group(1)] = (prob, exp, trs)

# ---- export metadata ----
meta = {}
for b in B:
    path = f"export/{b}.md"
    if not os.path.exists(path):
        continue
    for p in re.split(r"\n(?=## \d+\. )", open(path).read())[1:]:
        m = re.search(r"\*Trace (tr-[0-9a-fA-F]{32})\s*·\s*Medication: ([^*·]*?)\s*(?:·|\*)", p)
        if m:
            meta[m.group(1)[:13]] = (m.group(1), ACT.get(b, b), m.group(2).strip())
_prior_text = {}
for _full, (_path, _act) in RC.prior_round_exports(cfg).items():  # earlier-round traces a ticket cites (v2.4)
    if _path not in _prior_text:
        _prior_text[_path] = open(_path).read()
    _m = re.search(re.escape(_full) + r"\s*·\s*Medication: ([^*·]*?)\s*(?:·|\*)", _prior_text[_path])
    meta.setdefault(_full[:13], (_full, _act, _m.group(1).strip() if _m else ""))
blocks = {}
for b in B + ["EARLIER"]:
    path = f"thread-blocks/{b}.md"
    if not os.path.exists(path):
        continue
    for part in re.split(r"\n(?=### `tr-)", open(path).read()):
        m = re.match(r"### `(tr-[0-9a-fA-F]{10})`", part)
        if m:
            blocks[m.group(1)] = part.strip()

# ---- ratings ----
ratings = []
for rt in LR.rating_rows("ratings.md"):
    ratings.append(dict(sheet_row=str(rt["sheet_row"]), label_id=rt["label_id"], trace=rt["trace"],
                          ref=rt["ref"], verdict=rt["verdict"], tags=rt["tags"],
                          text_type=rt["text_type"], text=rt["text"]))
ref_rows = collections.defaultdict(list)
for rid, r in rows.items():
    ref = col(r, "rating ref")
    if ref:
        ref_rows[(col(r, "trace id")[:13], ref)].append(rid)


def unit_label(uid):
    return units[uid]["key"] if "(" not in uid else uid


def dest_label(rid):
    d = dest.get(rid, "")
    if rid in row_unit:
        return unit_label(row_unit[rid])
    if d in dropped_fms:
        return "failure mode (dropped by the product owner)"
    if d.startswith("FM-"):
        return "failure mode (held, no ticket)"
    if d.lower().startswith("decision"):
        return "logged"  # a working decision-item ID is never published
    return d


for rt in ratings:
    rids = ref_rows.get((rt["trace"][:13], rt["ref"]), [])
    rt["rows"] = rids
    rt["dest"] = sorted({dest_label(r) for r in rids}) or ["coverage only (no issue row)"]


def stats(u):
    rs = [rows[r] for r in u["rows"] if r in rows]
    # Only real traces count as drafts. A feedback-session row carries a session reference in the
    # Trace ID column (for example "session-2026-10-29"), which is not a draft.
    traces = sorted({col(r, "trace id")[:13] for r in rs if col(r, "trace id").startswith("tr-")})
    revs = collections.Counter(p for r in rs for p in people(r))
    ev = collections.Counter("legacy audit" if K.is_audit(r) else "eval judge" if col(r, "reviewer") == "eval"
                             else K.basis(r) for r in rs)
    verd = collections.Counter(col(r, "verdict").upper() for r in rs if col(r, "reviewer") not in ("audit", "scan"))
    if u["t"] and u["t"] in tick:
        traces += [x for x in tick[u["t"]][2] if x not in traces]
    spread_map = getattr(CD, "SPREAD", {})
    spread = "; ".join(spread_map[f] for f in u["fms"] if f in spread_map)
    return traces, revs, ev, verd, spread


def by_source(u):
    """kind -> counted drafts (trace prefixes) behind the unit, per `priority-rubric.md` section 2."""
    out = collections.defaultdict(set)
    for r in [rows[r] for r in u["rows"] if r in rows]:
        if K.counts(r):
            out[kind_of(r)].add(col(r, "trace id")[:13])
    direct = set().union(*out.values()) if out else set()
    sp = {t for f in u["fms"] for t in SPREAD_BACKED.get(f, ())} - direct
    if sp:
        out["scan"] = sp
    return out


def by_source_str(u):
    s = by_source(u)
    return ", ".join(f"{KIND_WORDS.get(k, k)} {len(v)}" for k, v in sorted(s.items())) or "none"


OUT = []


def w(*a):
    OUT.extend(a)


def dist(sel):
    c = collections.Counter(CAT[u][0] for u in sel)
    n = len(sel) or 1
    return [(k, c[k], round(100 * c[k] / n)) for k in ORDER]


filed = [u for u in units if units[u]["status"].startswith("Filed")]
w("## 2. Distribution by category", "",
  f"| Category | Filed tickets ({len(filed)}) | Share | With existing-ticket rows ({len(units)}) | Share |",
  "| --- | --- | --- | --- | --- |")
d1, d2 = dict((k, (n, p)) for k, n, p in dist(filed)), dict((k, (n, p)) for k, n, p in dist(list(units)))
for k in ORDER:
    w(f"| {k} | {d1[k][0]} | {d1[k][1]}% | {d2[k][0]} | {d2[k][1]}% |")


def cl(d):
    return sum(d[k][0] for k in ORDER if k.startswith("Clinical safety"))


nf, nu = len(filed) or 1, len(units) or 1
w(f"| **Clinical (core + edge case)** | **{cl(d1)}** | **{round(100*cl(d1)/nf)}%** | **{cl(d2)}** | **{round(100*cl(d2)/nu)}%** |",
  f"| **Non-clinical** | **{len(filed)-cl(d1)}** | **{100-round(100*cl(d1)/nf)}%** | **{len(units)-cl(d2)}** | **{100-round(100*cl(d2)/nu)}%** |", "")
TYPES = []  # unique action types in batch order; several batch codes can share one action type
for b in B:
    if ACT.get(b, b) not in TYPES:
        TYPES.append(ACT.get(b, b))
w(f"### Category by action type (all {len(units)} rows; a row spanning several action types counts once per type)", "",
  "| Category | " + " | ".join(TYPES) + " |", "| --- | " + " | ".join("---" for _ in TYPES) + " |")
at = collections.defaultdict(collections.Counter)
for uid, u in units.items():
    types = {r[:2] for r in u["rows"]} | {b for f in u["fms"] if f in fm for b in fm[f]["types"].split()}
    for t_ in {ACT.get(b, b) for b in types if b in B}:
        at[CAT[uid][0]][t_] += 1
for k in ORDER:
    w(f"| {k} | " + " | ".join(str(at[k][t_]) for t_ in TYPES) + " |")
w("", f"### Category by evidence type (all {len(units)} rows)", "",
  "| Category | Rows backed by 2+ reviewers | 1 reviewer | Eval judge only | Mechanical count only |",
  "| --- | --- | --- | --- | --- |")
ec = collections.defaultdict(collections.Counter)
for uid, u in units.items():
    _, revs, ev, _, _ = stats(u)
    ec[CAT[uid][0]]["2+" if len(revs) >= 2 else "1" if revs else "eval" if ev["eval judge"] else "0"] += 1
for k in ORDER:
    w(f"| {k} | {ec[k]['2+']} | {ec[k]['1']} | {ec[k]['eval']} | {ec[k]['0']} |")
w("")
w("## 3. Failure modes", "", f"### 3a. Summary (all {len(units)} rows)", "",
  "| Ticket | Failure mode | Status | Priority | Category | Secondary | Judge that should catch it | Drafts | Reviewers | Evidence | Counted drafts by source |",
  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
for k in ORDER:
    for uid, u in units.items():
        if CAT[uid][0] != k:
            continue
        traces, revs, ev, verd, spread = stats(u)
        evs = ", ".join(f"{a} {b}" for a, b in ev.items()) or "mechanical count"
        w(f"| [{unit_label(uid)}]({JIRA}{u['key']}) | {re.sub(r' \((?:tr-[0-9a-fA-F]{10}|sessions? \d{4}-\d{2}-\d{2}(?:, \d{4}-\d{2}-\d{2})*)\)\s*$', '', u['title'])} | {'filed' if u['t'] else 'existing'} | {u['priority'].split(' - ')[0]} | {CAT[uid][0]} | {CAT[uid][1]} | {CAT[uid][2]} | {len(traces)} | {len(revs)} | {evs} | {by_source_str(u)} |")
w("", "### 3b. Detail, grouped by category", "")
cited = []
for k in ORDER:
    w(f"#### {k}", "")
    for uid, u in units.items():
        if CAT[uid][0] != k:
            continue
        traces, revs, ev, verd, spread = stats(u)
        cited += [x for x in traces if x not in cited]
        if u["t"] and u["t"] in tick:
            prob, exp, _ = tick[u["t"]]
        elif u["key"] in comments:
            body = comments[u["key"]][1]
            prob = body.split("\n\n")[0]
            exp = re.split(r"\n\n", body)[-1]
        else:
            prob = exp = ""
        w(f"##### [{unit_label(uid)}]({JIRA}{u['key']}): {u['title']}", "",
          f"- **Status:** {u['status']}. **Priority:** {u['priority']}.",
          f"- **Category:** {CAT[uid][0]}" + (f"; secondary {CAT[uid][1]}" if CAT[uid][1] else "") + f". **Judge that should catch it:** {CAT[uid][2]}.",
          f"- **What goes wrong:** {prob}",
          f"- **{'Expected' if u['t'] else 'Ask on the ticket'}:** {exp}",
          f"- **Evidence:** {len(traces)} draft(s); reviewers {', '.join(f'{a} ({b})' if b > 1 else a for a, b in revs.items()) or 'none'}; verdicts {', '.join(f'{a} {b}' for a, b in verd.items()) or 'none'}; " + (", ".join(f"{a} {b}" for a, b in ev.items()) or "mechanical count only") + (f". **Mechanical spread:** {spread}" if spread else "") + ".",
          f"- **Counted drafts by source:** {by_source_str(u)}.",
          "- **Traces:** " + ", ".join(f"[{x}](#{x})" for x in traces), "")
        for r in u["rows"]:
            if r not in rows:
                continue
            Rr = rows[r]
            q = col(Rr, "verbatim reviewer quote") if not K.is_audit(Rr) else col(Rr, "atomic issue")
            q = " ".join(q.split())
            q = re.sub(r"\s*\((?:[^()]*\bCR-[^()]*)\)", "", q)
            q = re.sub(r"\s*\b(?:added|amended|moved) in 2[a-d]\b[^.;)]*", "", q).strip()
            w(f"  - `{col(Rr, 'trace id')[:13]}` {who_label(Rr)}: {q[:400]}{' ...' if len(q) > 400 else ''}")
        w("")

# ---- held failure modes (no ticket this round) ----
in_unit = {f for u in units.values() for f in u["fms"]}
fm_summary = {}
if os.path.exists("failure-modes.md"):
    for r in RC.parse_table_after(open("failure-modes.md").read(), "## 1. Summary"):
        fm_summary[RC.col(r, "failure mode")] = r
held = []
for fid, f in fm.items():
    s = fm_summary.get(fid, {})
    call = RC.col(s, "filing call")
    if fid in in_unit or call.startswith("merged") or (fid not in dropped_fms and call.startswith(("file", "comment"))):
        continue
    why = call.split(":", 1)[1].strip() if call.startswith(("hold", "product owner")) else "no ticket this round"
    if call.startswith("product owner"):
        why = f"for the product owner: {why}"
    if fid in dropped_fms:
        why = "dropped by the product owner"
    held.append((f["title"], ", ".join(ACT.get(t, t) for t in f["types"].split()),
                 RC.col(s, "severity class") or "not set", RC.col(s, "counted drafts") or "",
                 RC.col(s, "providers") or "", why))
w("### 3c. Held or dropped without a ticket", "",
  f"{len(held)} failure modes got no ticket and no comment this round."
  + (" Held ones are recorded in the evidence ledger, so a second occurrence files."
     if hasattr(CD, "SEVERITY") else ""), "",
  "| Failure mode | Action types | Severity class | Counted drafts | Providers | Why |",
  "| --- | --- | --- | --- | --- | --- |")
for h in held:
    w("| " + " | ".join(x.replace("|", "/") for x in h) + " |")
w("")

by_trace = collections.defaultdict(list)
for rt in ratings:
    by_trace[rt["trace"][:13]].append(rt)
unrated_other = collections.defaultdict(set)  # trace -> held or dropped labels of its counted rows
for rid, r in rows.items():
    if K.counts(r) and dest.get(rid, "").startswith("FM-"):
        by_trace.setdefault(col(r, "trace id")[:13], [])
        if rid not in row_unit:
            unrated_other[col(r, "trace id")[:13]].add(dest_label(rid))
for f, ts in SPREAD_BACKED.items():
    if f in in_unit:
        for t in ts:
            by_trace.setdefault(t, [])
w(f"## 4. Trace table (all {len(by_trace)} drafts)", "",
  "One row per draft that was rated or backs a counted failure mode. The last two columns are "
  "empty for the Evals team to fill with judge results.", "",
  "| Trace ID | Action type | Medication | Ratings | GOOD | BAD | Reviewers (verdict) | Failure modes a reviewer or eval judge raised | Failure modes from mechanical count only | Other outcomes | Judge pass/fail | Judge notes |",
  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
tr_units = collections.defaultdict(lambda: {"rev": set(), "mech": set()})
for uid, u in units.items():
    traces, _, _, _, _ = stats(u)
    urs = [rows[r] for r in u["rows"] if r in rows]
    rev_tr = {col(r, "trace id")[:13] for r in urs if col(r, "reviewer") not in K.NON_PERSON}
    judges = collections.defaultdict(set)
    for r in urs:
        if col(r, "reviewer") == "eval":
            judges[col(r, "trace id")[:13]].add(col(r, "error tag").replace("judge:", "").strip())
    for x in traces:
        if x in rev_tr:
            tr_units[x]["rev"].add(unit_label(uid))
        elif x in judges:
            tr_units[x]["rev"].add(f"{unit_label(uid)} (eval judge {', '.join(sorted(judges[x]))})")
        else:
            tr_units[x]["mech"].add(unit_label(uid))
    for x in by_source(u).get("scan", ()):
        tr_units[x]["mech"].add(unit_label(uid))
for x in tr_units:
    tr_units[x]["mech"] -= tr_units[x]["rev"]


def batch_of(action):
    for code, a in ACT.items():
        if a == action:
            return code
    return ""


for tr in sorted(by_trace, key=lambda x: (B.index(batch_of(meta[x][1])) if meta.get(x) and batch_of(meta[x][1]) in B else len(B), x)):
    rts = by_trace[tr]
    full, act, med = meta.get(tr, (tr, "", ""))
    g = sum(1 for x in rts if x["verdict"].lower() == "good")
    bd = len(rts) - g
    who = ", ".join(f"{x['ref'].split(' · ')[0]} {x['verdict'].upper()}" for x in rts)
    ds = sorted({d for x in rts for d in x["dest"]})
    tk = [d for d in ds if re.match(r"[A-Z]+-\d+", d)]
    other = [d for d in ds if d not in tk and not d.startswith("coverage only")]
    if not rts:
        other = sorted(unrated_other.get(tr, ()))
    rv_ = sorted(tr_units[tr]["rev"] | set(tk))
    mc_ = sorted(tr_units[tr]["mech"] - set(rv_))
    w(f"| {full} | {act} | {med} | {len(rts)} | {g} | {bd} | {who} | {', '.join(rv_)} | {', '.join(mc_)} | {', '.join(other)} | | |")
w("")
w("{{SPLIT}}")
w("## 6. Trace appendix (every draft cited above)", "",
  "Each entry: the messages shown to the model before the draft (most recent last), the full "
  "draft, and every rating on that draft. Names are replaced with placeholders; nothing else is "
  "changed. Reviewer comments are as recorded in the ratings, with some details shown as [redacted].", "")
for tr in cited:
    full, act, med = meta.get(tr, (tr, "", ""))
    w(f'<a id="{tr}"></a>', "", f"### {tr} ({act})", "", f"- **Full trace ID:** `{full}`", f"- **Medication on the action:** {med}",
      "- **Tickets:** " + ", ".join(sorted({unit_label(row_unit[r]) for r in row_unit if r in rows and col(rows[r], 'trace id')[:13] == tr})), "")
    if tr in blocks:
        blk = blocks[tr].split("\n", 1)[1].strip()
        w(blk.replace("**Messages before the draft**", "**Messages before the draft (most recent last)**"), "", "**Ratings on this draft**", "")
    else:
        w("**Ratings on this draft**", "")
    for x in by_trace[tr]:
        txt = " ".join(x["text"].split()) or "(verdict only)"
        w(f"- {x['ref'].split(' · ')[0]} ({x['verdict'].upper()}, {x['ref'].split(' · ')[1]} UTC; tags: {x['tags'] or 'none'}): {txt}")
    if not by_trace.get(tr):
        w("- Not rated; the evidence is in the failure-mode detail above.")
    w("")
def rating_kind(x):
    return RATING_MAP.get((x["trace"], x["ref"]), DEFAULT_KIND or "ratings")


# Non-rating evidence: a ledger row with no Rating ref that a provider, an eval judge, Slack or a
# session backs (legacy checklist rows and thumbs-only rows are not evidence items).
extra = []
for rid, r in rows.items():
    t = col(r, "trace id")
    if (K.is_trace(t) and col(r, "rating ref").strip()) or K.is_audit(r) or col(r, "provenance") == "thumbs-only":
        continue
    kind = kind_of(r)
    if kind not in ("edits", "evals", "slack", "interviews"):
        continue
    full, act, med = meta.get(t[:13], (t, ACT.get(rid[:2], ""), ""))
    rv = col(r, "reviewer")
    if rv in K.NON_PERSON and kind == "edits":
        rv = ", ".join(sorted(K.credited(r, K.trace_raters("ratings.md"), {}))) or rv
    d = dest_label(rid)
    extra.append(dict(full=full, act=act, med=med, rv=rv, verdict=col(r, "verdict").upper(),
                      tags=col(r, "error tag"), dest=[d], kind=kind))

w(f"## 7. Evidence table (all {len(ratings) + len(extra)} evidence items)", "",
  f"One row per rating, plus one per edit, failed judge verdict, Slack report or session mention "
  f"that no rating carries. The same rows are in `{CSV_FILE}`.", "",
  "| Label ID | Trace ID | Source | Reviewer | Rated (UTC) | Verdict | Tags | Outcome |",
  "| --- | --- | --- | --- | --- | --- | --- | --- |")
with open(CSV_FILE, "w", newline="") as fh:
    cw = csv.writer(fh)
    cw.writerow(["label_id", "trace_id", "action_type", "medication", "reviewer", "rated_at_utc", "verdict", "tags", "outcome", "failure_mode_tickets", "categories", "judge_pass_fail", "judge_notes", "source"])
    for x in ratings:
        full, act, med = meta.get(x["trace"][:13], (x["trace"], "", ""))
        rv, at_ = x["ref"].split(" · ") if " · " in x["ref"] else (x["ref"], "")
        tk = [d for d in x["dest"] if re.match(r"[A-Z]+-\d+", d)]
        cats = sorted({CAT[u][0] for u in units if unit_label(u) in tk})
        src = rating_kind(x)
        w(f"| {x['label_id']} | {full} | {KIND_WORDS.get(src, src)} | {rv} | {at_} | {x['verdict'].upper()} | {x['tags']} | {'; '.join(x['dest'])} |")
        # CSV outcome follows the spec's enum: ticket keys live in failure_mode_tickets, so a row that
        # maps to a filed or existing ticket has a blank outcome unless it also has a non-ticket outcome.
        csv_outcome = "; ".join(d for d in x["dest"] if d not in tk)
        cw.writerow([x["label_id"], full, act, med, rv, at_, x["verdict"].upper(), x["tags"], csv_outcome, "; ".join(tk), "; ".join(cats), "", "", src])
    for x in extra:
        tk = [d for d in x["dest"] if re.match(r"[A-Z]+-\d+", d)]
        cats = sorted({CAT[u][0] for u in units if unit_label(u) in tk})
        w(f"| | {x['full']} | {KIND_WORDS.get(x['kind'], x['kind'])} | {x['rv']} | | {x['verdict']} | {x['tags']} | {'; '.join(x['dest'])} |")
        cw.writerow(["", x["full"], x["act"], x["med"], x["rv"], "", x["verdict"], x["tags"],
                     "; ".join(d for d in x["dest"] if d not in tk), "; ".join(tk), "; ".join(cats), "", "", x["kind"]])
w("")
prose = open("cluster_analysis_prose.md").read()
ta, tb = "\n".join(OUT).split("{{SPLIT}}")
open(REPORT_FILE, "w").write(prose.replace("{{TABLES_A}}", ta).replace("{{TABLES_B}}", tb))
print("units", len(units), "cited traces", len(cited), "ratings", len(ratings), "other evidence rows", len(extra),
      "held", len(held),
      "dist filed", {k: d1[k][0] for k in ORDER}, "all", {k: d2[k][0] for k in ORDER})
