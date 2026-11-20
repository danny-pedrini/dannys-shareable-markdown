"""Step 2c builder: maps every ledger row to one destination and writes failure-modes.md,
row-map.md and input-issues.md. Fails if any row is unmapped or mapped twice.
Batch codes and actions come from round.json; failure modes, input-issue owners and every other
round fact come from cluster_defs.py in the round folder.

Counts each failure mode by `priority-rubric.md` section 2 (through counting.py): counted drafts,
counted instances, providers, sources, band, and the filing call from
`SEVERITY`, the dedup category in `STATUS`, held-topic flags, `WATCH` matches, `CONSOLIDATE` and
Gate 2 moves in `CALL`. A round whose cluster_defs.py has no `SEVERITY` dict (built before skill
v2.0) gets counts but no filing call. Held failure modes are recorded in the evidence ledger
(`ledger_tool.py`), which also supplies `watch-list-prior.md` (`ledger_tool.py prior`).
Run from the round folder:  python3 -I <skill>/scripts/build_cluster.py
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
import counting as K  # noqa: E402
from mechanical_check import ledger_rows, col  # noqa: E402
import cluster_defs as C  # noqa: E402

FM = getattr(C, "FM", [])
OTHER = getattr(C, "OTHER", {})
DECISIONS = getattr(C, "DECISIONS", {})
PENDING = getattr(C, "PENDING", "")
STATUS = getattr(C, "STATUS", {})
SPREAD = getattr(C, "SPREAD", {})
SPREAD_TRACES = getattr(C, "SPREAD_TRACES", {})
V2 = hasattr(C, "SEVERITY")
SEVERITY = getattr(C, "SEVERITY", {})
WATCH = getattr(C, "WATCH", {})
CONSOLIDATE = getattr(C, "CONSOLIDATE", {})
CALL = getattr(C, "CALL", {})
FLAG_EXTRA = getattr(C, "FLAG_EXTRA", {})
INPUT_OWNERS = getattr(C, "INPUT_OWNERS", {})
INPUT_NOTES = getattr(C, "INPUT_NOTES", [])
SEVERITIES = ("severe safety", "minor safety", "efficiency")
CALLS = ("file", "hold", "product owner", "comment")
WATCH_COLS = ["Item", "Behavior", "Action types", "Severity class", "Counted drafts", "Providers",
              "Hold flag", "First held", "Rounds waited"]

for f in FM:
    f.setdefault("kind", "draft")  # a missing kind means "draft", never a conflict-flag ticket
FM = sorted(FM, key=lambda f: int(f["id"][3:]))
fmi = {f["id"]: f for f in FM}

cfg = RC.load(os.path.join(ROOT, "round.json"))
B = RC.batch_codes(cfg)
ACTION = RC.action_map(cfg)

rows = {}
for b in B:
    for r in (ledger_rows(b) or []):
        rows[col(r, "row id")] = r
dest = collections.defaultdict(list)
for f in FM:
    for rid in f.get("rows", "").split():
        dest[rid].append(f["id"])
for rid, (d, why) in OTHER.items():
    dest[rid].append(d)
for rid, r in rows.items():
    if not dest.get(rid):
        if col(r, "provenance") == "thumbs-only":
            dest[rid].append("coverage only (thumbs-only)")
        elif re.search(r"no (additional )?issue found", col(r, "atomic issue"), re.I):
            dest[rid].append("coverage only (audit, no issue)")  # legacy rows from before v3.0
errs = ([f"{k}: unmapped" for k in rows if not dest.get(k)]
        + [f"{k}: mapped {v}" for k, v in dest.items() if len(v) > 1]
        + [f"{k}: not a ledger row" for k in dest if k not in rows])
if V2:
    errs += [f"{f['id']}: kind='draft' with no SEVERITY entry" for f in FM
             if f["kind"] == "draft" and f["id"] not in SEVERITY]
    errs += [f"{k}: SEVERITY {v!r} is not one of {SEVERITIES}" for k, v in SEVERITY.items() if v not in SEVERITIES]
errs += [f"{k}: CALL {v!r} is not one of {CALLS}" for k, v in CALL.items() if v not in CALLS]
errs += [f"{d}: key {k} is not an id in FM" for d, m in (("CONSOLIDATE", CONSOLIDATE), ("WATCH", WATCH),
         ("SPREAD_TRACES", SPREAD_TRACES), ("CALL", CALL), ("SEVERITY", SEVERITY))
         for k in m if k not in fmi]
absorbed_by = {}
for k, v in CONSOLIDATE.items():
    for a in v.split():
        if a not in fmi or a == k:
            errs.append(f"CONSOLIDATE {k}: {a} is not another FM")
        elif a in absorbed_by:
            errs.append(f"CONSOLIDATE: {a} absorbed by both {absorbed_by[a]} and {k}")
        else:
            absorbed_by[a] = k
errs += [f"CONSOLIDATE: {k} absorbs FMs but is itself absorbed by {absorbed_by[k]}" for k in CONSOLIDATE if k in absorbed_by]
for k, v in SPREAD_TRACES.items():
    errs += [f"SPREAD_TRACES {k}: {t!r} is not a full tr-<32 hex> trace ID" for t in v.split()
             if not re.fullmatch(r"tr-[0-9a-fA-F]{32}", t)]
if errs:
    print("MAPPING ERRORS:\n" + "\n".join(errs))
    sys.exit(1)


def read_watch(path):
    if not os.path.exists(path):
        return None
    tables = RC.parse_tables(open(path).read())
    items = []
    for t in tables:
        if t and "item" in t[0] and "rounds waited" in t[0]:
            items += t
    return {RC.col(i, "item"): i for i in items}


def ids(cell):
    return [] if cell.strip().lower() in ("", "none", "-") else cell.split()


def n_of(n, word):
    return f"{n} {word}{'s' * (n != 1)}"


PRIOR = read_watch("watch-list-prior.md")
if V2 and PRIOR is None:
    print("note: no watch-list-prior.md; the prior watch list is empty")
PRIOR = PRIOR or {}
missing = [f"WATCH {k}: {i} is not an item in watch-list-prior.md" for k, v in WATCH.items() for i in v.split() if i not in PRIOR]
if missing:
    print("MAPPING ERRORS:\n" + "\n".join(missing))
    sys.exit(1)

SESSIONS = RC.session_batches(cfg)
RATING_MAP, DEFAULT_KIND = K.rating_sources(cfg)
RATERS = K.trace_raters("ratings.md")
EXPORT_PROVIDER = K.export_providers(B)
KIND_WORDS = {"thumbs-downs": "thumbs-downs", "labeling": "labeling", "edits": "edits", "evals": "evals",
              "interviews": "interviews", "slack": "Slack", "ratings": "ratings", "scan": "phrase scan",
              "prior": "prior watch list"}


def held_topic(f):
    m = re.search(r"HELD:\s*([^()|;]+?)\s*(?:\(|$|;|\|)", f.get("flags", ""))
    return m.group(1).strip() if m else None


def dedup_category(fid):
    s = STATUS.get(fid, "").split("|")[0].strip().lower().replace("\u2019", "'")
    if not s:
        return "pending"
    head, _, rest = s.partition(":")
    first_clause = rest.split(";")[0]
    if head.startswith(("won't do", "wont do")) or (
            head.startswith("recurrence") and re.search(r"closed,?\s+won'?t do", first_clause)):
        return "won't do"  # clustering-and-dedup.md section 5: a closed Won't Do recurrence is flagged, never filed
    for c in ("new", "regression"):
        if s.startswith(c):
            return c
    return "comment"


def counted_group(fid):
    """Counts for fid with every FM it absorbs pooled in, each draft and provider once."""
    members = [fid] + CONSOLIDATE.get(fid, "").split()
    rids = [x for m in members for x in fmi[m].get("rows", "").split()]
    rs = [rows[x] for x in rids]
    direct, via_drafts, kinds = set(), set(), set()
    backed = False
    for r in rs:
        if K.counts(r):
            direct.add(col(r, "trace id"))
            via_drafts |= K.credited(r, RATERS, EXPORT_PROVIDER)
            kinds.add(K.source_kind(r, cfg, SESSIONS, RATING_MAP, DEFAULT_KIND))
            backed = backed or K.basis(r) in K.PROVIDER_BASES
    spread_all = {t for m in members for t in SPREAD_TRACES.get(m, "").split()}
    spread = (spread_all - direct) if backed else set()
    if spread:
        kinds.add("scan")
    sess = set()
    for x, r in zip(rids, rs):
        if x.split("-")[0] in SESSIONS and not K.is_trace(col(r, "trace id")) and not K.not_counted_row(r) \
                and K.basis(r) in K.ALWAYS:
            sess.add(RC.session_provider(cfg, x.split("-")[0], col(r, "reviewer").strip()))
    watch_drafts, watch_items, watch_flags = set(), [], set()
    for m in members:
        for i in WATCH.get(m, "").split():
            it = PRIOR[i]
            watch_items.append(i)
            d = ids(RC.col(it, "counted drafts"))
            watch_drafts |= set(d)
            for p in ids(RC.col(it, "providers")):
                if p.startswith("session:"):
                    sess.add(p[len("session:"):])
                else:
                    (via_drafts if d else sess).add(p)
            fl = RC.col(it, "hold flag").strip()
            if fl and fl.lower() != "none":
                watch_flags.add(fl)
    # The ledger keys a draft on `tr-` plus 8 hex characters; this round's IDs can be longer.
    seen8 = {t[:11] for t in direct | spread}
    watch_new = {t for t in watch_drafts if t[:11] not in seen8}
    if watch_new:
        kinds.add("prior")
    drafts = direct | spread | watch_new
    sess_only = sess - via_drafts
    if sess:
        kinds.add("interviews")
    instances = len(drafts) + len(sess_only)
    if instances == 0:
        band = "none"
    elif len(drafts) >= 5 and len(via_drafts) >= 2:
        band = "common"
    elif instances >= 2:
        band = "recurring"
    else:
        band = "one-off"
    sev = [SEVERITY[m] for m in members if m in SEVERITY]
    sev = min(sev, key=SEVERITIES.index) if sev else None
    return dict(members=members, direct=direct, spread=spread, spread_all=spread_all, backed=backed,
                drafts=drafts, via_drafts=via_drafts, providers=via_drafts | sess, sess_only=sess_only,
                instances=instances, band=band, kinds=kinds,
                watch_items=watch_items, watch_flags=watch_flags, severity=sev)


def level(sev, band, moved):
    """priority-rubric.md section 0 (v3.0): severe safety is P0 at 2+ instances and P1 at one.
    Zero counted instances has no level until the product owner files a severe-safety row.
    Minor safety and efficiency are P2 when recurring and P1 when common. One-offs below severe safety hold."""
    if sev == "severe safety":
        if band == "none":
            return "P1" if moved else "-"
        return "P0" if band in ("recurring", "common") else "P1"
    if moved and band in ("one-off", "none"):
        band = "recurring"  # a one-off moved to file at Gate 2 scores at its recurring level
    if sev in ("minor safety", "efficiency"):
        return {"common": "P1", "recurring": "P2"}.get(band, "-")
    return "-"


def filing_call(f, g):
    """(call, why) per `clustering-and-dedup.md` section 2a."""
    fid = f["id"]
    if fid in absorbed_by:
        return "merged", f"merged into {absorbed_by[fid]}"
    if not V2:
        return "-", "not set: cluster_defs.py has no SEVERITY (built before skill v2.0)"
    if fid in CALL:
        return CALL[fid], "product owner's Gate 2 call"
    topic = held_topic(f)
    if topic:
        return "product owner", f"held topic: {topic}"
    if g["watch_flags"]:
        return "product owner", f"matches a held watch-list item ({', '.join(sorted(g['watch_flags']))})"
    cat = dedup_category(fid)
    if cat == "won't do":
        return "product owner", "matches a Won't Do ticket"
    sev = g["severity"] or "no severity"
    n = g["instances"]
    if n == 0:
        return ("product owner", "no counted instance, severe safety") if sev == "severe safety" else ("hold", f"no counted instance, {sev}")
    if n == 1 and sev != "severe safety":
        return "hold", f"seen once, {sev}"
    if cat == "pending":
        return "pending dedup", f"clears the floor, {sev}"
    if cat == "comment":
        return "comment", "an existing ticket covers it or it goes to re-eval"
    parts = [f"{n_of(len(g['drafts']), 'draft')} from {n_of(len(g['via_drafts']), 'provider')}"] if g["drafts"] else []
    if g["sess_only"]:
        parts.append(n_of(len(g["sess_only"]), "session provider"))
    return "file", f"{' plus '.join(parts)}, {sev}"


G = {f["id"]: counted_group(f["id"]) for f in FM}
CALLED = {f["id"]: filing_call(f, G[f["id"]]) for f in FM}


def cell(s):
    return s.replace(" | ", "; ").replace("|", "/")


def providers_cell(g):
    p = g["providers"]
    if not p:
        return "none"
    return f"{len(p)}" + (" (one provider)" if len(p) == 1 else "")


def stats(f):
    rs = [rows[x] for x in f.get("rows", "").split()]
    # Only real traces are drafts; a feedback-session row's Trace ID is a session reference.
    drafts = sorted({col(r, "trace id")[:13] for r in rs if col(r, "trace id").startswith("tr-")})
    prov = collections.Counter(K.basis(r) for r in rs)
    revs = sorted({col(r, "reviewer") for r in rs if col(r, "reviewer") not in K.NON_PERSON})
    return rs, drafts, prov, revs


def status(f):
    return STATUS.get(f["id"], "")


L = ["# Failure modes (Step 2c)", "",
     "Every ledger row maps to exactly one failure mode, to `input-issues.md`, to a decision "
     "item, to 'not a failure mode', or to 'logged' (proof rule). `row-map.md` lists every row.", "",
     f"> **Source:** the batch ledgers in `ledger/` after Step 2b QA, and `existing-tickets.md`. "
     f"Generated by `build_cluster.py` from `cluster_defs.py`.", "",
     f"**Dedup status:** {PENDING}.", "",
     "## 1. Summary", "",
     "Counts follow `priority-rubric.md` section 2. Counted drafts include spread drafts and prior "
     "watch-list drafts; providers count those credited through drafts or sessions. A failure mode "
     "that absorbs others (`CONSOLIDATE`) carries the pooled counts.", "",
     "| Failure mode | Behavior | Action types | Drafts with evidence rows | Mechanical spread | Evidence mix | Reviewers | Dedup status | Flags "
     "| Severity class | Counted drafts | Counted instances | Providers | Sources | Band | Level (rubric) | Filing call |",
     "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for f in FM:
    rs, drafts, prov, revs = stats(f) if f.get("rows") else ([], [], collections.Counter(), [])
    mix = ", ".join(f"{k} {v}" for k, v in prov.items()) or "mechanical only"
    g, (call, why) = G[f["id"]], CALLED[f["id"]]
    srcs = ", ".join(KIND_WORDS.get(k, k) for k in sorted(g["kinds"])) or "none"
    lvl = level(g["severity"], g["band"], CALL.get(f["id"]) == "file") if V2 else "-"
    L.append(f"| {f['id']} | {f['title']} | {f['types']} | {len(drafts)} | {SPREAD.get(f['id'],'')} | {mix} | {', '.join(revs) or 'none'} "
             f"| {cell(status(f))} | {cell(f.get('flags',''))} "
             f"| {g['severity'] or 'not set'} | {len(g['drafts'])} | {g['instances']} | {providers_cell(g)} | {srcs} | {g['band']} | {lvl} | {call}: {why} |")
L += ["", "## 2. Failure modes", ""]
for f in FM:
    rs, drafts, prov, revs = stats(f) if f.get("rows") else ([], [], collections.Counter(), [])
    L += [f"### {f['id']}: {f['title']}", "",
          f"- **Action types:** {', '.join(ACTION.get(t, t) for t in f['types'].split())}",
          f"- **Kind:** {f['kind']}",
          f"- **Wrong behavior:** {f['behavior']}",
          f"- **Expected behavior:** {f['expected']}",
          f"- **Ledger rows:** {f.get('rows') or 'none (mechanical finding)'}",
          f"- **Drafts ({len(drafts)}):** {', '.join(drafts) or 'see note'}",
          f"- **Evidence:** {', '.join(f'{k} {v}' for k, v in prov.items()) or 'mechanical only'}; reviewers: {', '.join(revs) or 'none'}"]
    if f.get("other"):
        L.append(f"- **Other action types and notes:** {f['other']}")
    if f.get("flags"):
        L.append(f"- **Flags:** {f['flags']}")
    g, (call, why) = G[f["id"]], CALLED[f["id"]]
    L += [f"- **Severity class:** {g['severity'] or 'not set'}",
          f"- **Counts:** {n_of(len(g['drafts']), 'counted draft')} ({len(g['direct'])} from rows, {len(g['spread'])} spread"
          + (f", {len(g['drafts'] - g['direct'] - g['spread'])} from the prior watch list" if g["watch_items"] else "")
          +           f"), {n_of(g['instances'], 'counted instance')}, providers: {', '.join(sorted(g['providers'])) or 'none'}; "
          f"band {g['band']}"
          + (f"; pooled with {' '.join(g['members'][1:])}" if len(g["members"]) > 1 else ""),
          f"- **Filing call:** {call}: {why}"]
    if g["watch_items"]:
        L.append(f"- **Watch-list match:** {' '.join(g['watch_items'])}")
    if g["spread_all"] and not g["backed"]:
        L.append(f"- **Spread not counted:** {n_of(len(g['spread_all']), 'draft')}; no counted draft backed by provider evidence or an eval failure")
    L += [f"- **Dedup tickets:** {f.get('dedup','')}", f"- **Dedup status:** {status(f)}", ""] + ([f"- **Mechanical spread:** {SPREAD[f['id']]}"] if f["id"] in SPREAD else [])
L += ["## 3. Decision items", ""]
for k, v in DECISIONS.items():
    mapped = [rid for rid, d in dest.items() if d == [f"decision {k}"]]
    L.append(f"- **{k}.** {v}" + (f" Rows: {', '.join(sorted(mapped))}." if mapped else ""))
L += ["", "## 4. Not a failure mode", "", "| Row | Trace | Reviewer | Reason |", "| --- | --- | --- | --- |"]
for rid, (d, why) in OTHER.items():
    if d == "not a failure mode":
        L.append(f"| {rid} | {col(rows[rid],'trace id')[:13]} | {col(rows[rid],'reviewer')} | {why} |")
L += ["", "## 5. Logged, not filed (proof rule: depends on chart data the export does not show)", "", "| Row | Trace | Reason |", "| --- | --- | --- |"]
for rid, (d, why) in OTHER.items():
    if d == "logged":
        L.append(f"| {rid} | {col(rows[rid],'trace id')[:13]} | {why} |")
L += ["", "## 6. Classification disagreements from the 2b second opinion (gate decision)", "",
      "| Row | Ledger | Second opinion | Where it lands now |", "| --- | --- | --- | --- |"]
for b in B:
    p = os.path.join("ledger", "qa", f"{b}-second-opinion-diff.md")
    if not os.path.exists(p):
        continue
    for l in open(p):
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) > 6 and re.fullmatch(rf"{b}-\d{{3}}", c[0]):
            if c[3].split()[0] == c[5].split()[0]:
                continue
            L.append(f"| {c[0]} | {c[3]} | {c[5]} | {dest[c[0]][0]} |")
L += ["", "## 7. Reviewer disagreements", "",
      "Contradictions between reviewer claims on the same draft are listed in section 4 when a "
      "rule or the thread settles them; otherwise they are a decision item in section 3."]
open("failure-modes.md", "w").write(("\n".join(L) + "\n").replace(" — ", "; ").replace("—", "-"))

# row map
def row_counted(rid, r):
    d = dest[rid][0]
    if not d.startswith("FM-"):
        return "no"
    if K.counts(r):
        return "yes"
    if rid.split("-")[0] in SESSIONS and not K.is_trace(col(r, "trace id")) and not K.not_counted_row(r) \
            and K.basis(r) in K.ALWAYS:
        return "yes"
    return "no"


M = ["# Row map (Step 2c)", "",
     "Every ledger row and its one destination, then one `SP-<nnn>` row per spread draft "
     "(`SPREAD_TRACES`). `Source` is the row's derived source kind; `Counted` is `yes` when the row "
     "backs a counted draft or a session instance for its failure mode (`priority-rubric.md` "
     "section 2). Generated by `build_cluster.py`.", "",
     "| Row | Trace | Reviewer | Provenance | Classification | Destination | Source | Evidence basis | Counted |",
     "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for rid in sorted(rows, key=lambda x: (B.index(x[:2]) if x[:2] in B else len(B), x)):
    r = rows[rid]
    M.append(f"| {rid} | {col(r,'trace id')[:13]} | {col(r,'reviewer')} | {col(r,'provenance')} | {col(r,'classification')} | {dest[rid][0]} "
             f"| {K.source_kind(r, cfg, SESSIONS, RATING_MAP, DEFAULT_KIND)} | {K.basis(r) or '-'} | {row_counted(rid, r)} |")
n_sp = 0
for f in FM:
    g = G[absorbed_by.get(f["id"], f["id"])]
    for t in SPREAD_TRACES.get(f["id"], "").split():
        n_sp += 1
        M.append(f"| {RC.SPREAD_CODE}-{n_sp:03d} | {t[:13]} | scan | phrase-scan | - | {f['id']} | scan | phrase-scan "
                 f"| {'yes' if g['backed'] and t not in g['direct'] else 'no'} |")
open("row-map.md", "w").write(("\n".join(M) + "\n").replace(" — ", "; ").replace("—", "-"))


# Held failure modes go to the evidence ledger (references/evidence-ledger.md), not to a watch-list.md.
if V2:
    pending = sorted(f["id"] for f in FM if CALLED[f["id"]][0] in ("product owner", "pending dedup"))
    if pending:
        print(f"note: {len(pending)} FMs await a product-owner call or dedup ({' '.join(pending)}); "
              "the ledger update waits until Gate 2 records each call in CALL")

# input issues
FLAG = sorted({rid for rid, r in rows.items() if col(r, "classification") == "input-issue" and col(r, "conflict-flag basis").strip(" -")} | set(FLAG_EXTRA),
              key=lambda x: (B.index(x[:2]) if x[:2] in B else len(B), x))
inrows = {k for k, v in dest.items() if v == ["input-issue"]}
owned = {x for v in INPUT_OWNERS.values() for x in v.split()}
assert inrows == owned, (inrows - owned, owned - inrows)
gen = RC.generation(cfg)
ratings_url = " and ".join(s["url"] for s in RC.sources_of_kind(cfg, *RC.SHEET_KINDS) if s.get("url"))
I = ["# Input issues", "",
     "Defects that would remain even if the model wrote a perfect message from its inputs. "
     "Grouped by owner. This is not a ticket list.", "",
     f"> **Source:** ledger rows classified `input-issue` after Step 2b (extractor, adjudicator "
     f"and independent second opinion; disagreements are in `failure-modes.md` section 6). "
     + (f"Reviewer comments come from the ratings sheet {ratings_url} . " if ratings_url else "")
     + f"Conflict-flag basis: `generation-provenance.md` (every prompt commit through the "
     f"{gen.get('bound_utc', 'generation bound')}) and `prompt-provenance.md`.", ""]
for own, ids in INPUT_OWNERS.items():
    I += [f"## {own}", "", "| Row | Trace | Action | Reviewer | Issue | Input named (and what the draft would have written) | Missed conflict flag |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for rid in ids.split():
        r = rows[rid]
        I.append(f"| {rid} | {col(r,'trace id')[:13]} | {ACTION.get(rid[:2], rid[:2])} | {col(r,'reviewer')} | {col(r,'atomic issue')} | {col(r,'input named')} | {('yes: ' + FLAG_EXTRA[rid]) if rid in FLAG_EXTRA else ('yes: no prompt instructs flagging' if rid in FLAG else '')} |")
    I.append("")
I += ["## Missed conflict flags", "",
      f"In {len(FLAG)} rows above, the provider's decision conflicts with a protocol and the "
      f"draft does not flag it. No prompt in the window checked instructs the model to flag "
      f"this kind of conflict, so these are input issues, not draft defects, and are logged "
      f"here for Clinical Quality rather than filed."]
if INPUT_NOTES:
    I += ["", "## Related input issues found during 2b", ""]
    I += [f"- {n}" for n in INPUT_NOTES]
open("input-issues.md", "w").write(("\n".join(I) + "\n").replace(" — ", "; ").replace("—", "-"))
c = collections.Counter(v[0] if v[0].startswith(("FM", "decision")) is False else ("failure mode" if v[0].startswith("FM") else "decision item") for v in dest.values())
print("rows:", len(rows), "| destinations:", dict(c), "| FMs:", len(FM), "| input issues:", len(inrows))
