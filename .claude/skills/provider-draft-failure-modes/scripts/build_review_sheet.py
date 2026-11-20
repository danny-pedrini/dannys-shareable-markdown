"""Build ticket-review.md (Step 3.5): one card per planned ticket, grouped by frequency band
(`ticket-spec.md`, review card format), for Danny's row-by-row Gate 3 call.

Inputs: ticket-plan.md (T-id -> failure mode), the batch ledgers (via mechanical_check.py),
cluster_defs.py (FM rows, dedup text, mechanical spread), failure-modes.md (each FM's band and
counts, written by build_cluster.py and read by header name), ratings.md, ticket-drafts.md's
approval table (Draft/Ticket, Title, Recommended, Clinical blind, Provider blind; whichever of
those columns are present, read by header name so it works before or after Gate 3 fills in
Approved), and the ticket's own full draft (for a Rationale line, if the approval table does not
carry one).

Bands, in this order: common, recurring, one-off, none. Within a band, tickets sort by
recommended priority (P0 first), then counted drafts (most first). "Raised by" counts distinct
person reviewers; `audit`, `eval` and `scan` are not reviewers.

Each card ends with an empty "Your call:" line for Danny to fill in later (format:
round-folder-layout.md section 4, E8).
Run from the round folder:  python3 -I <skill>/scripts/build_review_sheet.py
"""
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.getcwd()
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import round_config as RC  # noqa: E402
from mechanical_check import ledger_rows, col  # noqa: E402
import load_ratings as LR  # noqa: E402
import cluster_defs as CD  # noqa: E402

cfg = RC.load(os.path.join(ROOT, "round.json"))
B = RC.batch_codes(cfg)
product_reviewer = RC.product_reviewer(cfg)
fm = {f["id"]: f for f in getattr(CD, "FM", [])}
SPREAD = getattr(CD, "SPREAD", {})

rows = {}
for b in B:
    for r in (ledger_rows(b) or []):
        rows[col(r, "row id")] = r

plan, plan_dedup = {}, {}
if not os.path.exists("ticket-plan.md"):
    print("build_review_sheet.py: ticket-plan.md not found", file=sys.stderr)
    sys.exit(1)
plan_text = open("ticket-plan.md").read()
for table in RC.parse_tables(plan_text):
    for trow in table:
        tid = RC.col(trow, "ticket")
        fm_id = RC.col(trow, "fm")
        if re.fullmatch(r"T-\d+", tid or "") and re.fullmatch(r"FM-\d+", fm_id or ""):
            plan[tid] = fm_id
            plan_dedup[tid] = RC.col(trow, "dedup")
if not plan:
    # Fall back to a narrow parse for a ticket-plan.md with different column headers.
    for l in plan_text.split("\n"):
        m = re.match(r"\| (T-\d+) \| (FM-\d+) \|", l)
        if m:
            plan[m.group(1)] = m.group(2)
if not plan:
    print("build_review_sheet.py: no ticket rows found in ticket-plan.md", file=sys.stderr)
    sys.exit(1)

draft_table = {}
if os.path.exists("ticket-drafts.md"):
    draft_table_rows = RC.parse_table_after(open("ticket-drafts.md").read(), "## 1.")
    for r in draft_table_rows:
        tid = RC.col(r, "draft") or RC.col(r, "ticket")
        if tid:
            draft_table[tid.strip()] = r

full_drafts = {}
if os.path.exists("ticket-drafts.md") and "## 4. Full ticket drafts" in open("ticket-drafts.md").read():
    tail = open("ticket-drafts.md").read().split("## 4. Full ticket drafts", 1)[1]
    for part in re.split(r"\n(?=### T-\d+\. )", tail):
        m = re.match(r"\s*### (T-\d+)\.\s*(.+)", part)
        if m:
            full_drafts[m.group(1)] = {"title": m.group(2).strip(), "text": part}


def rationale_of(tid):
    d = draft_table.get(tid, {})
    r = RC.col(d, "rationale")
    if r:
        return r
    text = full_drafts.get(tid, {}).get("text", "")
    m = re.search(r"^- Rationale:\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


ratings_by_trace = collections.defaultdict(set)
for rt in LR.rating_rows("ratings.md"):
    ratings_by_trace[rt["trace"][:13]].add(rt["ref"].split("·")[0].strip())

NON_PERSON = {"audit", "eval", "scan"}
BANDS = ["common", "recurring", "one-off", "none"]
fm_counts = {}
if os.path.exists("failure-modes.md"):
    for r in RC.parse_table_after(open("failure-modes.md").read(), "## 1. Summary"):
        fid = RC.col(r, "failure mode")
        if RC.col(r, "band"):
            fm_counts[fid] = dict(band=RC.col(r, "band"), drafts=RC.col(r, "counted drafts"),
                                  instances=RC.col(r, "counted instances"), providers=RC.col(r, "providers"),
                                  sources=RC.col(r, "sources"))


def prio_rank(p):
    m = re.match(r"\s*P(\d)", p or "")
    return int(m.group(1)) if m else 9


def int_or_0(s):
    return int(s) if (s or "").strip().isdigit() else 0

tickets = []
for tid in sorted(plan, key=lambda x: int(x[2:])):
    fm_id = plan[tid]
    if fm_id not in fm:
        print(f"build_review_sheet.py: SKIP {tid}: maps to {fm_id}, not in cluster_defs.FM "
              f"(already dropped or merged out; ticket-plan.md predates the rebuild)", file=sys.stderr)
        continue
    full_row_ids = fm[fm_id]["rows"].split()
    named = set(re.findall(r"\b[A-Z]{2}-\d{3}\b", plan_dedup.get(tid, "")))
    row_ids = [r for r in full_row_ids if r in named] or full_row_ids
    frows = [rows[r] for r in row_ids if r in rows]
    raising = collections.Counter(col(r, "reviewer") for r in frows if col(r, "reviewer") not in NON_PERSON)
    # Real traces only; a feedback-session row's Trace ID is a session reference, not a draft.
    traces = sorted({col(r, "trace id")[:13] for r in frows if col(r, "trace id").startswith("tr-")})
    rated_by = set()
    for t in traces:
        rated_by |= ratings_by_trace.get(t, set())
    n_raising = len(raising)
    c = fm_counts.get(fm_id, dict(band="not set", drafts="", instances="", providers="", sources=""))
    d = draft_table.get(tid, {})
    title = RC.col(d, "title") or full_drafts.get(tid, {}).get("title", fm[fm_id]["title"])

    def name(h):
        return f"{h} (you)" if h == product_reviewer else h

    def counted(counter):
        return ", ".join(f"{name(h)} ({n})" if n > 1 else name(h) for h, n in counter.most_common()) or "none"

    tickets.append(dict(
        tid=tid, fm=fm_id, band=c["band"], counts=c, title=title,
        recommended=RC.col(d, "recommended"), clinical_blind=RC.col(d, "clinical blind"),
        provider_blind=RC.col(d, "provider blind"), disagreement=RC.col(d, "disagreement"),
        rationale=rationale_of(tid), related=fm[fm_id].get("dedup", ""),
        behavior=fm[fm_id]["behavior"], expected=fm[fm_id]["expected"],
        raising=raising, raised_by_str=counted(raising), n_raising=n_raising,
        rated_by=sorted(rated_by), n_rated=len(rated_by), traces=traces,
        spread=SPREAD.get(fm_id, ""), rows=frows,
    ))

tickets.sort(key=lambda t: (BANDS.index(t["band"]) if t["band"] in BANDS else len(BANDS),
                            prio_rank(t["recommended"]), -int_or_0(t["counts"]["drafts"]), int(t["tid"][2:])))
counts = collections.Counter(t["band"] for t in tickets)
MEANING = {"common": "5+ counted drafts from 2+ providers",
           "recurring": "2+ counted instances",
           "one-off": "1 counted instance, filed because it's severe safety or moved to file at Gate 2",
           "none": "no counted instance. Severe safety goes to the product owner at Gate 2"}


def band_line(t):
    c = t["counts"]
    if t["band"] == "not set":
        return "- **Band not set** (failure-modes.md has no counts; rerun build_cluster.py)."
    p = c["providers"].strip()
    prov = "one provider" if "one provider" in p else "no providers" if p in ("", "none", "0") else f"{p} providers"
    return (f"- **Band {t['band']}:** {n_of(c['drafts'], 'counted draft')}, {n_of(c['instances'], 'counted instance')}, "
            f"{prov}; sources {c['sources']}.")


def n_of(n, word):
    return f"{n} {word}{'' if str(n).strip() == '1' else 's'}"


L = ["# Ticket review sheet (one card per ticket)", "",
     f"{len(tickets)} tickets, grouped by frequency band (`priority-rubric.md` section 2). The "
     "clustering rule makes one ticket per wrong behavior per action type, so a repeated pattern "
     "becomes one ticket per message type. Each card answers: is it an issue, is the priority "
     "right, who raised it, and how many of the reviewers who saw those drafts agreed.", "",
     "> **Source:** the ledgers in `ledger/` (reviewer quotes are redacted; patient messages are "
     "never quoted), `ticket-drafts.md`, `ratings.md`, `failure-modes.md` and `cluster_defs.py`. "
     "Reviewer counts are distinct reviewers with a row behind the ticket. \"Rated those drafts\" "
     "counts every reviewer who rated any draft the ticket cites, including thumbs-only and GOOD ratings.", "",
     "## 1. Bands", "",
     "| Band | Tickets | Meaning |", "| --- | --- | --- |"]
for b in BANDS + sorted(k for k in counts if k not in BANDS):
    if counts.get(b) or b in BANDS:
        L.append(f"| {b} | {counts.get(b, 0)} | {MEANING.get(b, 'counts not available')} |")
L += ["", "## 2. Summary table", "",
      "| Ticket | Band | Issue (short) | Recommended | Clinical blind | Provider blind | Counted drafts | Providers | Sources | Raised by | Reviewers raising it | Rated those drafts | Mechanical spread |",
      "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for t in tickets:
    short = t["title"].split(": ", 1)[1] if ": " in t["title"] else t["title"]
    short = re.sub(r"\s*\((?:tr-[0-9a-fA-F]{10}|sessions? \d{4}-\d{2}-\d{2}(?:, \d{4}-\d{2}-\d{2})*)\)\s*$", "", short)
    c = t["counts"]
    L.append(f"| {t['tid']} | {t['band']} | {short} | {t['recommended']} | {t['clinical_blind']} | {t['provider_blind']} | "
             f"{c['drafts']} | {c['providers']} | {c['sources']} | "
             f"{t['raised_by_str']} | {t['n_raising']} | {t['n_rated']} | {t['spread']} |")
L += ["", "## 3. Cards (same order as the table)", ""]
for t in tickets:
    L += [f"### {t['tid']}. {t['title']}", "",
          band_line(t),
          f"- **What's wrong:** {t['behavior']}",
          f"- **Expected:** {t['expected']}",
          f"- **Raised by:** {t['raised_by_str']}. **Reviewers who rated those drafts:** {', '.join(t['rated_by']) or 'none'} ({t['n_rated']}).",
          f"- **Drafts:** {', '.join(t['traces']) or ('feedback-session evidence, no single draft' if t['rows'] and all(not col(r, 'trace id').startswith('tr-') for r in t['rows']) else 'mechanical finding, no single draft')}",
          f"- **Priority:** recommended {t['recommended'] or 'n/a'}; clinical-quality blind {t['clinical_blind'] or 'n/a'}; provider blind {t['provider_blind'] or 'n/a'}." + (f" Disagreement: {t['disagreement']}." if t['disagreement'] else "")]
    if t["rationale"]:
        L.append(f"- **Why that priority:** {t['rationale']}")
    if t["related"]:
        L.append(f"- **Related tickets:** {t['related']}")
    L.append("- **Evidence:**")
    for r in t["rows"]:
        rv = col(r, "reviewer")
        q = col(r, "verbatim reviewer quote") if rv != "audit" else col(r, "atomic issue")
        who = {"audit": "legacy audit", "eval": f"eval {col(r, 'error tag').strip()}"}.get(rv, rv)
        L.append(f"  - {col(r, 'trace id')[:13] if col(r, 'trace id').startswith('tr-') else col(r, 'trace id')}, {who} ({col(r, 'verdict').upper() or 'n/a'}): \"{q}\"")
    L += ["- **Your call:**", ""]
open("ticket-review.md", "w").write("\n".join(L) + "\n")
print(f"wrote ticket-review.md: {len(tickets)} tickets; bands {dict(counts)}")
