"""Theme rollup for one update: counts per theme, per round and across rounds, from round outputs only.

Run from the update folder:
    python3 -I <skill>/scripts/theme_counts.py --themes ../../themes.md \
        --round <round dir> [--round <round dir> ...] [--tickets tickets.json] \
        [--filed-round <round dir> ...] [--prior-round <round dir> ...] \
        [--out theme-counts.md] [--json theme-counts.json]

--round names every new round, whatever its sources. --filed-round names every other filed round
in feature.json rounds[]. Only its "Filed:" keys are read: each must be in tickets.json with that
round in its rounds list. --prior-round names every rounds[] entry with first_update set (a round a
prior update already counted); a draft it counted under a theme doesn't count again under that
theme, though it can count under another. A round can be both --filed-round and --prior-round.

With no --round (no new round since the prior update), it writes zero counts and an empty rounds
list; the feedback section then says no round came in.

Reads, per round: round.json (slug, reviewers), row-map.md, failure-modes.md (the "Filed:" keys),
and watch-list.md when present. A row-map.md with a Counted column (provider-draft-failure-modes
v2.0) gives each row's counted flag and source kind. An older one doesn't, so the script reads the
round's ledger/*.md files read-only for Evidence basis and Confidence, and applies the rubric's
allow-list from that skill's counting.py.
Reads themes.md (references/feature-file-schema.md section 2). Reads tickets.json when given: the
live Jira read written in Step 2 ({"KEY": {"priority": "P1", "labels": [...], "status": "...",
"status_category": "To Do", "counted": true, "category": null, "reason": "", "rounds": ["pilot-1"],
"outside_round": false}}; references/ledger-formats.md section 3). "counted": false and "category"
apply Danny's ticket rulings from feature.json; Jira labels set the category otherwise.

Ticket scope (feature.json rulings, 2026-11-05): every ticket count is open tickets only (status
category not Done). The doc-wide counts cover every key in tickets.json with a round or filed
outside a round, so they don't depend on --round. A theme's ticket count covers the --round
rounds' keys in that theme. Keys from the ramp-gate query alone (no round, not outside a round)
are never counted.

Definitions (references/data-methods.md section 1):
  counted draft           a distinct tr- trace with a counted row in the theme, from any source
                          (priority-rubric.md section 2), minus drafts a --prior-round counted
                          under the theme
  by source               counted drafts per source kind; a draft two sources back counts under each
  audit-only draft        a distinct tr- trace with an audit row (source audit, Evidence basis
                          inferred) in the theme and no counted row; an uncounted provider edit
                          is supporting evidence, never audit
  raters                  distinct providers credited through counted tr- rows, by the rubric's
                          table (priority-rubric.md section 2): a legacy audit-reviewer edit row
                          credits the trace's rater, an eval row the export's provider
  interviewee floor       distinct people on session rows (Trace not tr-) in the theme; the doc's
                          count comes from the syntheses and must be at or above this floor
  single-draft FM         a failure mode whose rows cover exactly one distinct tr- trace (older
                          rounds only; a v2.0 round reports held one-offs instead)
  held one-off            a failure mode this round held at one counted instance (failure-modes.md
                          Band one-off, Filing call hold); watch_list counts every watch-list.md row
  input-only draft        a tr- trace with no row mapped to a failure mode and at least one input-issue row

Exit codes: 0 OK; 2 bad input (missing file, theme names an FM the round doesn't have, an FM in
two themes or in a theme and "Not in a theme", a filed key missing from tickets.json or not
naming its round, a key missing status_category, rounds or outside_round, rounds not a list, a
category other than safety, efficiency, neither or null, a null or empty priority, a
status_category other than To Do, In Progress or Done, --filed-round without --tickets); 3 a
round has failure modes with no theme (list printed; Gate 1 assigns them).

Jira files the Blocked status under In Progress, so a blocked ticket is open.

Done tickets drop out of every count and are listed as "closed" for the grader. The doc reports
the open count's change, never a closed-ticket count.
"""
import argparse
import glob
import json
import os
import re
import sys

ROW = re.compile(r"^\| ([A-Z]{2}-\d{3}) \|")
FM_ROW = re.compile(r"^\| (FM-\d+) \|")
KEY = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
CATEGORIES = ("To Do", "In Progress", "Done")
NON_PERSON = ("audit", "eval", "scan")
FAILURE_MODE_SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                    "provider-draft-failure-modes", "scripts")


def counting():
    """provider-draft-failure-modes' counting.py and round_config.py, the one copy of the rubric's
    allow-list. Loaded only for a round whose row-map.md has no Counted column."""
    if not os.path.exists(os.path.join(FAILURE_MODE_SCRIPTS, "counting.py")):
        die(f"missing {FAILURE_MODE_SCRIPTS}/counting.py (needed to count an older round's rows)")
    sys.dont_write_bytecode = True  # that skill's scripts/__pycache__ is tracked; never rewrite it from here
    sys.path.insert(0, FAILURE_MODE_SCRIPTS)
    import counting as K
    import round_config as RC
    return K, RC


def die(msg, code=2):
    print(f"theme_counts.py: {msg}", file=sys.stderr)
    sys.exit(code)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def read_filed(d):
    fms, filed = [], {}
    for line in open(os.path.join(d, "failure-modes.md")):
        m = FM_ROW.match(line)
        if m:
            fms.append(m.group(1))
            keys = []
            for seg in re.findall(r"Filed: ([^|]*)", line):
                keys += KEY.findall(re.split(r"\(", seg)[0])
            filed[m.group(1)] = sorted(set(keys))
    return fms, filed


def read_ledger_round(d):
    for f in ("round.json", "failure-modes.md"):
        if not os.path.exists(os.path.join(d, f)):
            die(f"{d}: missing {f} (a provider-draft-failure-modes output; this skill never rebuilds it)")
    _, filed = read_filed(d)
    return json.load(open(os.path.join(d, "round.json")))["slug"], sorted({k for ks in filed.values() for k in ks})


def read_round(d):
    for f in ("round.json", "row-map.md", "failure-modes.md"):
        if not os.path.exists(os.path.join(d, f)):
            die(f"{d}: missing {f} (a provider-draft-failure-modes output; this skill never rebuilds it)")
    meta = json.load(open(os.path.join(d, "round.json")))
    rows, header = [], None
    for line in open(os.path.join(d, "row-map.md")):
        if line.startswith("| Row |"):
            header = [h.lower() for h in cells(line)]
        elif ROW.match(line):
            c = cells(line)
            row = {"row": c[0], "trace": c[1], "reviewer": c[2], "dest": c[5]}
            if header and "counted" in header:
                row["counted"] = c[header.index("counted")] == "yes"
                row["source"] = c[header.index("source")] if "source" in header else ""
                row["basis"] = c[header.index("evidence basis")] if "evidence basis" in header else ""
            rows.append(row)
    fms, filed = read_filed(d)
    if not rows:
        die(f"{d}/row-map.md has no rows")
    v2 = "counted" in rows[0]
    if v2:
        credit_rows(d, meta, rows)
    else:
        count_legacy_rows(d, meta, rows)
    return {"slug": meta["slug"], "name": meta.get("round", meta["slug"]), "v2": v2,
            "raters": set(meta.get("reviewers") or []), "rows": rows, "fms": fms, "filed": filed,
            "held": read_watch(d)}


def count_legacy_rows(d, meta, rows):
    """Set each row's counted flag and source kind from the round's ledgers, read-only, through
    the rubric's allow-list (a row-map.md built before provider-draft-failure-modes v2.0)."""
    K, RC = counting()
    led = {}
    for p in sorted(glob.glob(os.path.join(d, "ledger", "*.md"))):
        for t in RC.parse_tables(open(p).read()):
            for r in t:
                if RC.col(r, "row id"):
                    led[RC.col(r, "row id")] = r
    missing = [x["row"] for x in rows if x["row"] not in led]
    if missing:
        die(f"{d}: row-map.md has no Counted column and ledger/*.md lacks rows {', '.join(missing[:5])}")
    sheets = RC.sources_of_kind(meta, *RC.SHEET_KINDS)
    sheet_kind = sheets[0]["kind"] if len({s["kind"] for s in sheets}) == 1 else "ratings"
    by_basis = {"eval-judge": "evals", "provider-edit": "edits", "provider-edit+note": "edits", "slack": "slack"}
    raters, export_provider = credit_maps(d, meta, K, RC)
    for x in rows:
        r = led[x["row"]]
        x["counted"] = K.counts(r)
        x["source"] = ("interviews" if not tr(x["trace"]) else "audit" if K.is_audit(r)
                       else by_basis.get(K.basis(r), sheet_kind))
        x["credited"] = K.credited(r, raters, export_provider) if x["counted"] else set()


def credit_maps(d, meta, K, RC):
    """(trace -> raters from ratings.md, trace -> the eval export's Provider: handle), read-only."""
    cwd = os.getcwd()
    os.chdir(d)
    try:
        return K.trace_raters("ratings.md"), K.export_providers(RC.batch_codes(meta))
    finally:
        os.chdir(cwd)


def credit_rows(d, meta, rows):
    """Each counted row's credited providers, by the rubric's table (priority-rubric.md section 2).
    The row map shortens traces, so the maps are keyed by the same prefix."""
    K, RC = counting()
    raters, export_provider = credit_maps(d, meta, K, RC)
    short = lambda m: {t[:13]: v for t, v in m.items()}  # noqa: E731
    raters, export_provider = short(raters), short(export_provider)
    for x in rows:
        row = {"trace id": x["trace"], "reviewer": x["reviewer"], "evidence basis": x["basis"]}
        x["credited"] = K.credited(row, raters, export_provider) if x["counted"] and tr(x["trace"]) else set()


def read_watch(d):
    """The round's held one-offs (failure-modes.md summary rows with Band one-off and Filing call
    hold) and its watch-list.md row count, which adds audit-only holds and carried prior items.
    None for a round with no watch list."""
    p = os.path.join(d, "watch-list.md")
    if not os.path.exists(p):
        return None
    rows = [cells(l) for l in open(p) if l.startswith("| ") and not l.startswith(("| Item |", "| ---"))]
    header, one_offs = None, 0
    for line in open(os.path.join(d, "failure-modes.md")):
        if line.startswith("| Failure mode |"):
            header = [h.lower() for h in cells(line)]
        elif header and FM_ROW.match(line) and "band" in header and "filing call" in header:
            c = cells(line)
            one_offs += c[header.index("band")] == "one-off" and c[header.index("filing call")].startswith("hold")
        elif header and not line.startswith("|"):
            header = None
    return {"one_offs": one_offs, "watch_list": len(rows)}


def read_themes(path):
    if not os.path.exists(path):
        die(f"missing {path}")
    text = open(path).read()
    ver = re.search(r"^Version: (\S+)", text, re.M)
    themes, dropped, section = [], set(), None
    for line in text.split("\n"):
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        if not line.startswith("| ") or line.startswith("| ---") or line.startswith("| #") or line.startswith("| Round"):
            continue
        c = cells(line)
        if section == "themes" and len(c) >= 4:
            fm_map = {}
            for part in c[3].split(";"):
                if ":" not in part:
                    continue
                slug, ids = part.split(":", 1)
                fm_map[slug.strip()] = ["FM-%02d" % int(x) for x in re.findall(r"FM-(\d+)", ids)]
            themes.append({"n": c[0], "name": c[1], "fm": fm_map})
        elif section == "not in a theme" and len(c) >= 2:
            for x in re.findall(r"FM-(\d+)", c[1]):
                dropped.add((c[0], "FM-%02d" % int(x)))
    if not themes:
        die(f"{path} has no rows under '## Themes'")
    return (ver.group(1) if ver else "?"), themes, dropped


def tr(t):
    return t.startswith("tr-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--themes", required=True)
    ap.add_argument("--round", action="append", default=[])
    ap.add_argument("--filed-round", action="append", default=[])
    ap.add_argument("--prior-round", action="append", default=[])
    ap.add_argument("--tickets")
    ap.add_argument("--out", default="theme-counts.md")
    ap.add_argument("--json", default="theme-counts.json")
    a = ap.parse_args()
    if a.filed_round and not a.tickets:
        die("--filed-round needs --tickets: it checks older rounds' filed keys against the live Jira read")

    rounds = [read_round(d) for d in a.round]
    priors = [read_round(d) for d in a.prior_round]
    overlap = sorted({r["slug"] for r in rounds} & {p["slug"] for p in priors})
    if overlap:
        die(f"a round can't be both --round and --prior-round: {', '.join(overlap)}")
    version, themes, dropped = read_themes(a.themes)
    tickets = json.load(open(a.tickets)) if a.tickets else None
    already = {}  # theme number -> drafts a prior update counted under it
    for t in themes:
        already[t["n"]] = {x["trace"] for p in priors for x in p["rows"]
                           if x["dest"] in t["fm"].get(p["slug"], []) and x["counted"] and tr(x["trace"])}

    unassigned = []
    for r in rounds:
        assigned = {f for t in themes for f in t["fm"].get(r["slug"], [])}
        seen = {}
        for t in themes:
            for f in t["fm"].get(r["slug"], []):
                if f not in r["fms"]:
                    die(f"themes.md theme '{t['name']}' names {r['slug']}:{f}, which {r['slug']}/failure-modes.md does not have")
                if f in seen:
                    die(f"themes.md puts {r['slug']}:{f} in two themes: '{seen[f]}' and '{t['name']}'")
                if (r["slug"], f) in dropped:
                    die(f"themes.md puts {r['slug']}:{f} in theme '{t['name']}' and in 'Not in a theme'")
                seen[f] = t["name"]
        for f in r["fms"]:
            if f not in assigned and (r["slug"], f) not in dropped:
                unassigned.append(f"{r['slug']}:{f}")

    out = {"themes_version": version, "rounds": [], "themes": [], "unassigned": unassigned}
    for r in rounds:
        traces = {x["trace"] for x in r["rows"] if tr(x["trace"])}
        per_fm = {f: {x["trace"] for x in r["rows"] if x["dest"] == f and tr(x["trace"])} for f in r["fms"]}
        has_fm = {x["trace"] for x in r["rows"] if x["dest"].startswith("FM-") and tr(x["trace"])}
        has_input = {x["trace"] for x in r["rows"] if x["dest"] == "input-issue" and tr(x["trace"])}
        out["rounds"].append({
            "slug": r["slug"], "name": r["name"], "drafts": len(traces), "failure_modes": len(r["fms"]),
            "single_draft_fms": None if r["v2"] else sum(1 for f in per_fm if len(per_fm[f]) == 1),
            "no_draft_fms": sum(1 for f in per_fm if len(per_fm[f]) == 0),
            "input_only_drafts": len(has_input - has_fm),
            "held": r["held"],
        })

    all_keys = set()
    for t in themes:
        row = {"n": t["n"], "name": t["name"], "by_round": {}, "counted": set(), "seen": set(),
               "audit_rows": set(), "by_source": {}, "raters": set(), "interviewee_floor": set(), "tickets": set()}
        for r in rounds:
            fms = set(t["fm"].get(r["slug"], []))
            rs = [x for x in r["rows"] if x["dest"] in fms]
            cnt = {x["trace"] for x in rs if x["counted"] and tr(x["trace"])}
            new = cnt - already[t["n"]]
            aud = {x["trace"] for x in rs if tr(x["trace"]) and x["source"] == "audit"}
            people = {p for x in rs if x["counted"] and tr(x["trace"]) and x["trace"] in new for p in x["credited"]}
            sess = {x["reviewer"] for x in rs if not tr(x["trace"]) and x["reviewer"] not in NON_PERSON}
            keys = {k for f in fms for k in r["filed"].get(f, [])}
            src = {}
            for x in rs:
                if x["counted"] and x["trace"] in new:
                    src.setdefault(x["source"] or "unknown", set()).add(x["trace"])
            row["by_round"][r["slug"]] = {"fms": len(fms), "counted_drafts": len(new), "already_counted": len(cnt - new),
                                          "audit_only": len(aud - cnt), "raters": len(people),
                                          "by_source": {k: len(v) for k, v in sorted(src.items())},
                                          "interviewee_floor": len(sess), "tickets": sorted(keys)}
            row["counted"] |= new
            row["seen"] |= cnt
            row["audit_rows"] |= aud
            for k, v in src.items():
                row["by_source"].setdefault(k, set()).update(v)
            row["raters"] |= people
            row["interviewee_floor"] |= {f"{r['slug']}:{s}" for s in sess}
            row["tickets"] |= keys
        all_keys |= row["tickets"]
        out["themes"].append(row)

    ticket_summary = None
    if tickets is not None:
        missing = sorted(k for k in all_keys if k not in tickets)
        if missing:
            die(f"tickets.json has no live Jira read for: {', '.join(missing)}")

        for field in ("status_category", "rounds", "outside_round"):
            lacking = sorted(k for k, v in tickets.items() if field not in v)
            if lacking:
                die(f"tickets.json has no {field} for: {', '.join(lacking)} (references/ledger-formats.md section 3)")
        not_list = sorted(k for k, v in tickets.items() if not isinstance(v["rounds"], list))
        if not_list:
            die(f"tickets.json rounds must be a list, empty when no round filed the key: {', '.join(not_list)}")
        bad_category = sorted(f"{k} ({v['category']!r})" for k, v in tickets.items() if v.get("category") not in (None, "safety", "efficiency", "neither"))
        if bad_category:
            die(f"tickets.json category must be safety, efficiency, neither or null: {', '.join(bad_category)}")
        no_priority = sorted(k for k, v in tickets.items() if not isinstance(v.get("priority"), str) or not v["priority"].strip())
        if no_priority:
            die(f"tickets.json has no priority for: {', '.join(no_priority)} (re-read each from Jira)")
        bad = sorted(f"{k} ({v['status_category']!r})" for k, v in tickets.items() if v["status_category"] not in CATEGORIES)
        if bad:
            die(f"tickets.json status_category must be one of {', '.join(CATEGORIES)} (Jira's status category, not the status): {', '.join(bad)}")
        ledgers = [(r["slug"], sorted({k for ks in r["filed"].values() for k in ks})) for r in rounds]
        ledgers += [read_ledger_round(d) for d in a.filed_round]
        for slug, keys in ledgers:
            for k in keys:
                if k not in tickets:
                    die(f"tickets.json has no live Jira read for {k}, filed by {slug}")
                if slug not in tickets[k]["rounds"]:
                    die(f"tickets.json {k} is filed by {slug} but its rounds list doesn't name it")

        def is_open(k):
            return tickets[k]["status_category"] != "Done"

        def split(keys):
            counted = [k for k in keys if tickets[k].get("counted", True) and is_open(k)]
            pri = {}
            for k in counted:
                p = tickets[k]["priority"].split(" ")[0]
                pri[p] = pri.get(p, 0) + 1
            return counted, pri
        scope = sorted(k for k, v in tickets.items() if v.get("rounds") or v.get("outside_round"))
        counted, pri = split(scope)
        cats = {"safety": 0, "efficiency": 0, "neither": 0}
        for k in counted:
            labels = tickets[k].get("labels", [])
            cat = tickets[k].get("category") or ("safety" if "safety" in labels else "efficiency" if "efficiency" in labels else "neither")
            cats[cat] += 1
        by_round = {}
        for k in scope:
            if tickets[k].get("counted", True):
                for s in tickets[k].get("rounds", []):
                    by_round[s] = by_round.get(s, 0) + 1
        ticket_summary = {"counted": len(counted), "by_priority": pri, "by_category": cats,
                          "filed_by_round": by_round,
                          "outside_round": sum(1 for k in counted if tickets[k].get("outside_round")),
                          "closed": [k for k in scope if tickets[k].get("counted", True) and not is_open(k)],
                          "not_counted": {k: tickets[k].get("reason", "") for k in scope if not tickets[k].get("counted", True)}}
        for row in out["themes"]:
            c, p = split(sorted(row["tickets"]))
            row["tickets_counted"] = len(c)
            row["tickets_by_priority"] = p
    out["tickets"] = ticket_summary

    lines = [f"# Theme counts (themes.md version {version})", "",
             "Generated by `theme_counts.py` from round outputs. Do not edit by hand; rerun instead.", "",
             "## Rounds", "",
             "| Round | Drafts | Failure modes | Single-draft FMs (older rounds) | Held one-offs (watch-list rows) "
             "| FMs with no draft (interview only) | Input-only drafts |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in out["rounds"]:
        sd = "-" if r["single_draft_fms"] is None else r["single_draft_fms"]
        held = f"{r['held']['one_offs']} ({r['held']['watch_list']})" if r["held"] else "-"
        lines.append(f"| {r['slug']} | {r['drafts']} | {r['failure_modes']} | {sd} | {held} | {r['no_draft_fms']} | {r['input_only_drafts']} |")
    src_s = lambda d: ", ".join(f"{k} {len(v) if isinstance(v, set) else v}" for k, v in sorted(d.items())) or "-"  # noqa: E731
    lines += ["", "## Themes (all rounds)", "",
              "| # | Theme | Counted drafts | By source | Audit-only drafts | Raters | Interviewee floor (session rows) | Tickets (counted) | By priority |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in out["themes"]:
        audit_only = row["audit_rows"] - row["seen"]
        pri = row.get("tickets_by_priority")
        pri_s = ", ".join(f"{v} {k}" for k, v in sorted(pri.items())) if pri is not None else "(no tickets.json)"
        tc = row.get("tickets_counted", len(row["tickets"]))
        lines.append(f"| {row['n']} | {row['name']} | {len(row['counted'])} | {src_s(row['by_source'])} | {len(audit_only)} | {len(row['raters'])} | "
                     f"{len(row['interviewee_floor'])} | {tc} | {pri_s} |")
    lines += ["", "## Themes by round", "",
              "| # | Round | FMs | Counted drafts | Already counted by a prior update | By source | Audit-only | Raters | Interviewee floor | Ticket keys |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in out["themes"]:
        for slug, b in row["by_round"].items():
            lines.append(f"| {row['n']} | {slug} | {b['fms']} | {b['counted_drafts']} | {b['already_counted']} | {src_s(b['by_source'])} "
                         f"| {b['audit_only']} | {b['raters']} | {b['interviewee_floor']} | {', '.join(b['tickets']) or '-'} |")
    if ticket_summary:
        lines += ["", "## Tickets (live Jira, from tickets.json)", "",
                  f"Open and counted, every filed round plus outside a round: {ticket_summary['counted']}. "
                  f"By priority: {', '.join(f'{v} {k}' for k, v in sorted(ticket_summary['by_priority'].items()))}. "
                  f"Safety: {ticket_summary['by_category']['safety']}. Efficiency: {ticket_summary['by_category']['efficiency']}. "
                  f"Neither label: {ticket_summary['by_category']['neither']}. "
                  f"Open outside a round: {ticket_summary['outside_round']}. "
                  f"Filed by round (counted, any status): {', '.join(f'{k} {v}' for k, v in sorted(ticket_summary['filed_by_round'].items())) or 'none'}."]
        if ticket_summary["closed"]:
            lines.append(f"- Closed, not counted: {', '.join(ticket_summary['closed'])}")
        for k, why in ticket_summary["not_counted"].items():
            lines.append(f"- Not counted: {k} ({why or 'no reason recorded'})")
    if unassigned:
        lines += ["", "## Failure modes with no theme (Gate 1 assigns them)", ""] + [f"- {u}" for u in unassigned]
    open(a.out, "w").write("\n".join(lines) + "\n")

    for row in out["themes"]:
        row["audit_only"] = len(row.pop("audit_rows") - row.pop("seen"))
        row["counted_drafts"] = len(row.pop("counted"))
        row["by_source"] = {k: len(v) for k, v in sorted(row["by_source"].items())}
        row["raters"] = len(row["raters"])
        row["interviewee_floor"] = len(row["interviewee_floor"])
        row["tickets"] = sorted(row["tickets"])
    json.dump(out, open(a.json, "w"), indent=1, default=sorted)
    print(f"wrote {a.out} and {a.json}: {len(themes)} themes over {len(rounds)} round(s); {len(unassigned)} unassigned")
    return 3 if unassigned else 0


if __name__ == "__main__":
    sys.exit(main())
