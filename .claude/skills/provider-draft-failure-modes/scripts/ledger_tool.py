"""Failure-mode evidence ledger tool (provider-draft-failure-modes skill).

Usage (always `python3 -I`; the ledger path is `../Failure-Mode-Evidence-Ledger.md` from a round folder):
  ledger_tool.py check <ledger.md>            validate; exit 1 when a computed cell is stale or a row is malformed
  ledger_tool.py write <ledger.md>            recompute the computed cells of the Summary table in place
  ledger_tool.py prior <ledger.md> <out.md>   write a round's watch-list-prior.md from the rows with Status `held`

The ledger has three tables under the headings `## 1. Summary`, `## 2. Evidence` and `## 3. Notes`.
Hand-kept Summary columns: ID, Behavior, Ticket, Severity class, Jira priority now, Status.
Computed Summary columns: everything else (counts, bands, rubric level, last seen). Evidence rows
are the only source of counts. A draft is matched on the first 8 hex characters of its trace ID, so a
draft counts once across rounds and sources. See references/evidence-ledger.md.
"""
import re
import sys

S_COLS = ["ID", "Behavior", "Ticket", "Severity class", "Jira priority now", "Provider drafts", "Providers",
          "Eval-only drafts (era)", "Session-only providers", "Counted instances", "Band", "Band incl. eval",
          "Rubric level", "Last seen", "Status"]
HAND = ["ID", "Behavior", "Ticket", "Severity class", "Jira priority now", "Status"]
E_COLS = ["ID", "Round", "Date", "Source kind", "Trace IDs or handles", "Providers credited", "Model era",
          "In ticket text", "Source"]
N_COLS = ["ID", "Note"]

COUNT_KINDS = {"thumbs-down-note", "labeling-verdict", "edit", "edit+note", "slack", "reviewer-edit-on-good"}
EVAL_KIND, SESSION_KIND, SCAN_KIND = "eval-judge", "session", "phrase-scan"
OTHER_KINDS = {"audit", "unverified-claim", "thumbs-only"}
ALL_KINDS = COUNT_KINDS | {EVAL_KIND, SESSION_KIND, SCAN_KIND} | OTHER_KINDS
SEVERITIES = {"severe safety", "minor safety", "efficiency", "not a draft defect"}
TR = re.compile(r"tr-([0-9a-f]{8})[0-9a-f]*")


def split_row(line):
    cells = re.split(r"(?<!\\)\|", line.strip())
    return [c.strip().replace("\\|", "|") for c in cells[1:-1]]


def find_table(lines, heading):
    """(start, end) line indexes of the table under `heading` (header row to last table row)."""
    h = next((i for i, l in enumerate(lines) if l.strip() == heading), None)
    if h is None:
        raise SystemExit(f"missing heading: {heading}")
    s = next((i for i in range(h + 1, len(lines)) if lines[i].startswith("|")), None)
    if s is None:
        raise SystemExit(f"no table under: {heading}")
    e = s
    while e + 1 < len(lines) and lines[e + 1].startswith("|"):
        e += 1
    return s, e


def parse(lines, heading, cols):
    s, e = find_table(lines, heading)
    head = split_row(lines[s])
    if head != cols:
        raise SystemExit(f"{heading}: header is {head}, expected {cols}")
    rows = []
    for l in lines[s + 2:e + 1]:
        c = split_row(l)
        if len(c) != len(cols):
            raise SystemExit(f"{heading}: row has {len(c)} cells, expected {len(cols)}: {l[:100]}")
        rows.append(dict(zip(cols, c)))
    return rows


def cell(v):
    return str(v).replace("|", "/").replace("\n", " ").replace(" — ", "; ").replace("—", "-").strip()


def emit(cols, rows):
    out = ["| " + " | ".join(cols) + " |", "|" + " --- |" * len(cols)]
    out += ["| " + " | ".join(cell(r.get(c, "")) for c in cols) + " |" for r in rows]
    return out


def handles(text):
    text = re.sub(r"\([^)]*\)", " ", text)
    return {t for t in re.split(r"[,;\s]+", text.strip()) if t and t.lower() not in ("none", "-", "n/a")}


def compute(evidence):
    """Computed Summary cells for one failure mode from its evidence rows."""
    prov, creds, ev, ev_era, scan, sess, creds_ev, dates = set(), set(), set(), {}, set(), set(), set(), []
    for r in evidence:
        k, ids = r["Source kind"], r["Trace IDs or handles"]
        traces = {"tr-" + m.group(1) for m in TR.finditer(ids)}
        sessions = {t[len("session:"):] for t in re.split(r"[,;\s]+", ids) if t.startswith("session:")}
        if k != "unverified-claim" and r["Date"] != "unknown":
            dates.append((r["Date"], r["Round"]))
        if k in COUNT_KINDS:
            prov |= traces
            creds |= {h for h in handles(r["Providers credited"]) if not h.startswith("session:")}
        elif k == EVAL_KIND:
            ev |= traces
            creds_ev |= {h for h in handles(r["Providers credited"]) if not h.startswith("session:")}
            for t in traces:
                ev_era.setdefault(t, r["Model era"].strip() or "not stated")
        elif k == SCAN_KIND:
            scan |= traces
        elif k == SESSION_KIND:
            sess |= sessions
    scan_p = (scan - prov) if prov else set()
    scan_a = (scan - prov - ev) if (prov or ev) else set()
    drafts_p = prov | scan_p
    sess_only = sess - creds
    ev_only = ev - prov
    drafts_a = prov | ev | scan_a
    prov_all = creds | creds_ev
    inst_p = len(drafts_p) + len(sess_only)
    inst_a = len(drafts_a) + len(sess_only)

    def band(drafts, provs, inst, eval_rule):
        if eval_rule and len(ev) >= 5:  # Danny, 2026-11-10: 5+ distinct eval-judge drafts are common
            return "common"
        if drafts >= 5 and provs >= 2:
            return "common"
        return "recurring" if inst >= 2 else ("one-off" if inst == 1 else "none")

    b_p = band(len(drafts_p), len(creds), inst_p, False)
    b_a = band(len(drafts_a), len(prov_all), inst_a, True)
    if b_p == "none" and ev_only:
        b_p = "eval-only"
    eras = {}
    for t in ev_only:
        eras[ev_era[t]] = eras.get(ev_era[t], 0) + 1
    era_txt = "; ".join(f"{n} ({e})" for e, n in sorted(eras.items())) or "0"
    last = max(dates)[::-1] if dates else None
    return dict(drafts_p=len(drafts_p), providers=len(creds), ev_txt=era_txt, sess=len(sess_only), inst=inst_p,
                band=b_p, band_a=b_a, inst_a=inst_a, last=(f"{last[0]} {last[1]}" if last else "-"))


def base_sev(sev):
    return re.sub(r"\s*\[inferred\]\s*$", "", sev)


def level(sev, c):
    """priority-rubric.md section 0, applied to the band that counts eval drafts."""
    sev = base_sev(sev)
    b = c["band_a"]
    if sev == "not a draft defect":
        return "n/a"
    if sev == "severe safety":
        return "P0" if b in ("recurring", "common") else ("P1" if b == "one-off" else "P1 (no counted instance: needs your call)")
    if sev in ("minor safety", "efficiency"):
        return {"common": "P1", "recurring": "P2", "one-off": "below floor"}.get(b, "below floor (no counted evidence)")
    return "-"


def computed_row(srow, evidence):
    c = compute(evidence)
    out = dict(srow)
    out.update({"Provider drafts": c["drafts_p"], "Providers": c["providers"], "Eval-only drafts (era)": c["ev_txt"],
                "Session-only providers": c["sess"], "Counted instances": c["inst"], "Band": c["band"],
                "Band incl. eval": c["band_a"], "Rubric level": level(srow["Severity class"], c),
                "Last seen": c["last"]})
    return out


def load(path):
    lines = open(path).read().split("\n")
    return (lines, parse(lines, "## 1. Summary", S_COLS), parse(lines, "## 2. Evidence", E_COLS),
            parse(lines, "## 3. Notes", N_COLS))


def problems(srows, erows, nrows):
    ids = [r["ID"] for r in srows]
    errs = [f"duplicate Summary ID {i}" for i in {x for x in ids if ids.count(x) > 1}]
    for r in srows:
        if base_sev(r["Severity class"]) not in SEVERITIES:
            errs.append(f"{r['ID']}: Severity class '{r['Severity class']}' not allowed")
        if not r["Status"].strip():
            errs.append(f"{r['ID']}: empty Status")
    for i, r in enumerate(erows, 1):
        w = f"Evidence row {i} ({r['ID']})"
        if r["ID"] not in ids:
            errs.append(f"{w}: ID not in Summary")
        if r["Source kind"] not in ALL_KINDS:
            errs.append(f"{w}: Source kind '{r['Source kind']}' not allowed")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}|unknown", r["Date"]):
            errs.append(f"{w}: Date '{r['Date']}' is not YYYY-MM-DD")
        if not r["Source"].startswith("> **Source:**") or not r["Source"][len("> **Source:**"):].strip():
            errs.append(f"{w}: Source must start with '> **Source:**' and name a file and line, or a Jira key and date")
        if r["Source kind"] in COUNT_KINDS | {EVAL_KIND} and not TR.search(r["Trace IDs or handles"]):
            errs.append(f"{w}: kind {r['Source kind']} has no tr- trace ID")
        if re.search(r"tr-[0-9a-f]{0,7}(?![0-9a-f])", r["Trace IDs or handles"]):
            errs.append(f"{w}: malformed trace ID in '{r['Trace IDs or handles']}'")
    errs += [f"Note for unknown ID {n['ID']}" for n in nrows if n["ID"] not in ids]
    return errs


def main(argv):
    if len(argv) < 3 or argv[1] not in ("check", "write", "prior"):
        raise SystemExit(__doc__)
    mode, path = argv[1], argv[2]
    lines, srows, erows, nrows = load(path)
    errs = problems(srows, erows, nrows)
    by_id = {}
    for r in erows:
        by_id.setdefault(r["ID"], []).append(r)
    fresh = [computed_row(s, by_id.get(s["ID"], [])) for s in srows]
    if mode == "write":
        if errs:
            print("\n".join(errs))
            return 1
        s, e = find_table(lines, "## 1. Summary")
        lines[s:e + 1] = emit(S_COLS, fresh)
        open(path, "w").write("\n".join(lines))
        print(f"wrote {len(fresh)} Summary rows")
        return 0
    if mode == "check":
        for old, new in zip(srows, fresh):
            for c in S_COLS:
                old_v = str(old[c])
                # Ledgers written before v3.0 store the old rubric-level phrase. Do not rewrite them.
                if c == "Rubric level" and old_v == "P1 (audit-only: needs your call)":
                    old_v = "P1 (no counted instance: needs your call)"
                if c not in HAND and old_v != str(new[c]):
                    errs.append(f"{old['ID']}: {c} is '{old[c]}', evidence gives '{new[c]}'")
        print("\n".join(errs) if errs else f"OK: {len(srows)} failure modes, {len(erows)} evidence rows")
        return 1 if errs else 0
    if errs:
        print("\n".join(errs))
        return 1
    out = argv[3] if len(argv) > 3 else "watch-list-prior.md"
    # A round is a distinct Round value that names a round; comment, eval-ci, audit and session rows are not rounds.
    round_date = {}
    for r in erows:
        if r["Round"] not in ("comment", "eval-ci", "audit", "session", "n/a") and r["Date"] != "unknown":
            round_date[r["Round"]] = min(round_date.get(r["Round"], r["Date"]), r["Date"])
    rounds_order = sorted(round_date.values())
    W = ["# Watch list (prior)", "", "Generated by `ledger_tool.py prior` from the held rows of the evidence ledger.", "",
         "| Item | Behavior | Action types | Severity class | Counted drafts | Providers | Hold flag | First held | Rounds waited |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for s in srows:
        m = re.fullmatch(r"held(?::\s*(.+))?", s["Status"].strip().lower())
        if not m:
            continue
        ev = by_id.get(s["ID"], [])
        traces = sorted({"tr-" + x.group(1) for r in ev if r["Source kind"] in COUNT_KINDS | {EVAL_KIND, SCAN_KIND}
                         for x in TR.finditer(r["Trace IDs or handles"])})
        provs = sorted({h for r in ev if r["Source kind"] in COUNT_KINDS | {EVAL_KIND}
                        for h in handles(r["Providers credited"]) if not h.startswith("session:")})
        provs += sorted("session:" + h for h in
                        {t[len("session:"):] for r in ev if r["Source kind"] == SESSION_KIND
                         for t in re.split(r"[,;\s]+", r["Trace IDs or handles"]) if t.startswith("session:")})
        first = min((r["Date"] for r in ev if r["Date"] != "unknown"), default="-")
        waited = sum(1 for d in rounds_order if first != "-" and d > first)
        W.append(f"| {s['ID']} | {cell(s['Behavior'])} | - | {s['Severity class']} | {' '.join(traces) or 'none'} | "
                 f"{' '.join(provs) or 'none'} | {m.group(1) or 'none'} | {first} | {waited} |")
    open(out, "w").write("\n".join(W) + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
