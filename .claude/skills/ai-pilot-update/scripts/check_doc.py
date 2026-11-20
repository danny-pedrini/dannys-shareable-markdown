"""Checks on update.md: the code evals for Gate 2 in evals.md, plus the links check for G3-6.

Run from the update folder:
    python3 -I <skill>/scripts/check_doc.py [--feature ../../feature.json] [--themes ../../themes.md]
        [--danny update-danny-1.md:update-agent-1.md ...]

Reads update.md, facts.md, sources.md, tickets.json, theme-counts.json, eval-coverage.md,
interview-claims.md and feature.json (formats: references/ledger-formats.md and
references/feature-file-schema.md). Checks:
  writing     plain words, filler, the hard verification searches, em dashes (quoted text exempt;
              the numeric-range search skips link targets and URLs)
  artifacts   no session artifacts (FM-, T-, D-, F-, S- IDs, row IDs, trace IDs, reviewer handles,
              gate names, working-file names) and no banned links
  links       every non-mailto link was opened this run (its key is in sources.md or tickets.json)
  structure   the H2 headings in feature.json doc.sections, in that order
  numbers     every number outside quotes, links and exempt tokens appears in a facts.md Value
  quotes      every quoted passage of 5 or more words appears verbatim in interview-claims.md,
              eval-coverage.md or facts.md; an interview quote is followed by (name, Mon D) matching
              its interview-claims.md row, and a quote marked CONFLICT is absent
  length      no paragraph or list item over 4 sentences; sentences with 2 or more commas print as
              REVIEW lines for the grader's clause check (they do not fail)
  metrics     while feature.json metrics.values_publishable is false, no "Metric value" fact's Value
              appears in update.md
  ramp        every dated ramp step in feature.json appears in update.md as "Mon D"
  superseded  no figure in feature.json sizing.superseded appears outside quotes
  themes      theme table cells match theme-counts.json; interviewee count is at or above the floor;
              the evals cell starts with the eval-coverage.md verdict and names its judges
  eval gaps   every Gap or Partly theme with a fix row has that row in the eval-changes table;
              a Gap with no fix row fails
  tickets     the priority table counts match tickets in theme-counts.json (open tickets only);
              "<N> tickets" phrases use the open counted total, a theme's count, a round's filed
              count, or the open count filed outside a round ("<N> existing tickets" is exempt;
              the numbers check still requires it in facts.md)
  appendix A  every "Appendix A" table row links a Jira ticket; every linked key is in tickets.json,
              open, counted, in a round or filed outside one, and P0 or P1; every such ticket in
              tickets.json is listed (the epic pointer line is not a row)
  owners      each feature.json owner named in the doc has a mailto link; the eval-changes owner
              is linked in the paragraph above the eval-changes table
  danny       with --danny snapshot:base, every line in Danny's snapshot that is not in the base (the
              agent's version just before his edit) is still in update.md; with no base, every
              snapshot line must survive
Prints every problem and exits non-zero on any.
"""
import argparse
import datetime
import json
import os
import re
import sys

PLAIN_WORDS = ["utilize", "leverage", "facilitate", "in order to", "prior to", "subsequently", "delve", "landscape", "ecosystem"]
FILLER = ["It's worth noting", "It's important to", "Needless to say", "At this point in time", "moving forward", "going forward"]
HARD_SEARCH_PHRASES = [
    "That's not",
    "And that matters", "That's the part everyone misses", "Which is exactly the point",
    "Here's the thing", "Let me be clear", "The truth is", "To be clear", "I'll be honest",
    "several", "a few", "some time",
    "In short", "At the end of the day", "To summarize", "In conclusion", "Bottom line:",
]
RE_LESS_MORE = re.compile(r"less a\b.*\bmore a\b", re.I)
RE_ANALOGY = re.compile(r"\bIt'?s the .* of\b", re.I)
RE_RANGE = re.compile(r"(?<![\d-])\d{1,3}\s*(?:to|-)\s*\d{1,3}(?![\d-])")
RANGE_EXEMPT = re.compile(r"\[Assumption:[^\]]*\(needs validation\)\]|\[estimate range\]", re.I)
MONTH_RE = re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*$", re.I)
EM_DASH = "\u2014"

ARTIFACTS = [r"\b(?:FM|T|D|F|S|C)-\d+\b", r"\b[A-Z]{2}-\d{3}\b", r"\btr-[0-9a-f]{6,}\b", r"\bprovider_\d+\b",
             r"\bsession_[a-z]\b", r"\bGate \d\b", r"\brow-map\b", r"\bfiling-ledger\b", r"\btheme-counts\b",
             r"\bfacts\.md\b", r"\bsources\.md\b", r"\beval-coverage\b", r"\binterview-claims\b", r"\bG\d-\d+\b"]
NUM_WORDS = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8",
             "nine": "9", "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
             "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19", "twenty": "20"}
LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
QUOTE = re.compile(r"[\u201c\"]([^\u201d\"]+)[\u201d\"]")


def strip_quotes(text):
    return QUOTE.sub("", text)


def writing_hits(text):
    hits = []
    clean = strip_quotes(text)
    for w in PLAIN_WORDS:
        for m in re.finditer(rf"\b{re.escape(w)}\b", clean, re.I):
            hits.append(f"plain word {w!r}: ...{clean[max(0, m.start()-30):m.end()+30]!r}...")
    for w in FILLER:
        for m in re.finditer(re.escape(w), clean, re.I):
            hits.append(f"filler {w!r}: ...{clean[max(0, m.start()-30):m.end()+30]!r}...")
    if EM_DASH in clean:
        hits.append(f"em dash: {clean.count(EM_DASH)} hit(s)")
    for w in HARD_SEARCH_PHRASES:
        for m in re.finditer(rf"\b{re.escape(w)}\b", clean, re.I):
            hits.append(f"hard search {w!r}: ...{clean[max(0, m.start()-30):m.end()+30]!r}...")
    if RE_LESS_MORE.search(clean):
        hits.append("hard search: 'less a ... more a' contrast metaphor")
    if RE_ANALOGY.search(clean):
        hits.append("hard search: \"It's the X of Y\" analogy")
    # Link targets and bare URLs hold document IDs such as "1-6g_x7xy", which are not numeric ranges in prose.
    prose = re.sub(r"\]\([^)\s]+\)|https?://\S+", " ", clean)
    for m in RE_RANGE.finditer(prose):
        window = prose[max(0, m.start() - 60):m.end() + 60]
        if RANGE_EXEMPT.search(window) or MONTH_RE.search(prose[max(0, m.start() - 15):m.start()]):
            continue
        hits.append(f"vague range {m.group(0)!r}: ...{window!r}...")
    return hits


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def tables(text):
    """[(heading_context, paragraph_before, header_cells, rows)] for every markdown table."""
    out, lines, i = [], text.split("\n"), 0
    heading = ""
    while i < len(lines):
        l = lines[i]
        if l.startswith("#"):
            heading = l.lstrip("#").strip()
        if l.startswith("|") and i + 1 < len(lines) and re.match(r"^\|\s*:?-{3}", lines[i + 1]):
            j, before = i - 1, ""
            while j >= 0 and not lines[j].strip():
                j -= 1
            if j >= 0:
                before = lines[j]
            header, rows, i = cells(l), [], i + 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            out.append((heading, before, header, rows))
            continue
        i += 1
    return out


def plain(s):
    s = LINK.sub(lambda m: m.group(1), s)
    return re.sub(r"[*_`]", "", s).strip()


LIST_ITEM = re.compile(r"^(?:[-*+]|\d+\.)\s+")
SENT_END = re.compile(r"(?<=[.!?])[\"\u201d)*_]*\s+(?=[A-Z\"\u201c(*_])")


def prose_units(text):
    """Each paragraph and each list item, with tables and headings left out."""
    units, cur = [], []
    for l in text.split("\n"):
        s = l.strip()
        if not s or s.startswith("|") or s.startswith("#") or LIST_ITEM.match(s):
            if cur:
                units.append(" ".join(cur))
                cur = []
            if LIST_ITEM.match(s):
                units.append(LIST_ITEM.sub("", s))
            continue
        cur.append(s)
    if cur:
        units.append(" ".join(cur))
    return units


def sentences(unit):
    t = re.sub(r"[*_`]", "", strip_quotes(LINK.sub(lambda m: m.group(1), unit))).strip()
    t = re.sub(r"\([^()]*\)", "", t)
    return [s for s in SENT_END.split(t) if re.search(r"[A-Za-z]{2}", s)]


def first_int(s):
    m = re.search(r"\d+", plain(s))
    return int(m.group(0)) if m else None


def url_key(url):
    for pat in (r"docs\.google\.com/(?:document|spreadsheets|presentation)/d/([\w-]+)",
                r"atlassian\.net/browse/([A-Z][A-Z0-9]+-\d+)", r"/pages/(\d+)", r"/dashboards/(\d+)",
                r"slack\.com/archives/(\w+/p\d+)", r"github\.com/(.+?)(?:\?|#|$)"):
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return url.split("?")[0].split("#")[0]


def number_tokens(text, exempt):
    t = text
    for e in exempt:
        t = t.replace(e, " ")
    t = LINK.sub(lambda m: m.group(1), t)
    t = re.sub(r"https?://\S+", " ", t)
    t = strip_quotes(t)
    t = re.sub(r"\b[A-Z][A-Z0-9]+-\d+\b", " ", t)        # ticket keys
    t = re.sub(r"\bP[0-3]s?\b", " ", t)                   # priority names
    t = re.sub(r"\b[A-Z]\d+[a-z]?\b", " ", t)             # metric codes such as A8a
    t = re.sub(r"^\s*#+\s*\d+\\?\.", " ", t, flags=re.M)  # numbered headings
    t = re.sub(r"^\s*\d+\.\s", " ", t, flags=re.M)        # ordered list markers
    t = re.sub(r"\bsections? \d+\b", " ", t, flags=re.I)
    t = re.sub(r"^\|\s*\d+\s*\|", "|", t, flags=re.M)     # table rank column
    toks = re.findall(r"\d[\d,]*(?:\.\d+)?", t)
    toks += [NUM_WORDS[w.lower()] for w in re.findall(r"\b(" + "|".join(NUM_WORDS) + r")\b", t, re.I)]
    return [x.replace(",", "") for x in toks]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feature", default="../../feature.json")
    ap.add_argument("--themes", default="../../themes.md")
    ap.add_argument("--danny", nargs="*", default=[])
    a = ap.parse_args()
    need = ["update.md", "facts.md", "sources.md", "theme-counts.json", "eval-coverage.md", a.feature]
    missing = [f for f in need if not os.path.exists(f)]
    if missing:
        print("check_doc.py: missing " + ", ".join(missing))
        print("FAIL")
        return 1
    doc = open("update.md").read()
    feature = json.load(open(a.feature))
    counts = json.load(open("theme-counts.json"))
    sources_text = open("sources.md").read()
    tickets = json.load(open("tickets.json")) if os.path.exists("tickets.json") else {}
    problems, review = [], []

    problems += [f"writing: {h}" for h in writing_hits(doc)]

    body = LINK.sub(lambda m: m.group(1), doc)
    for p in ARTIFACTS:
        for m in re.finditer(p, body):
            problems.append(f"artifacts: {m.group(0)!r} near ...{body[max(0, m.start()-30):m.end()+30]!r}...")
    for m in LINK.finditer(doc):
        url = m.group(2)
        for pat in feature.get("banned_link_patterns", []) + ["fathom.video"]:
            if pat in url:
                problems.append(f"artifacts: banned link {url} ({pat})")
        if url.startswith("mailto:"):
            continue
        k = url_key(url)
        if k not in sources_text and k not in tickets:
            problems.append(f"links: {url} was not opened this run (no {k!r} in sources.md or tickets.json)")

    h2 = [plain(l[3:]) for l in doc.split("\n") if l.startswith("## ")]
    want = feature.get("doc", {}).get("sections", [])
    pos = 0
    for s in want:
        hit = next((i for i in range(pos, len(h2)) if h2[i].startswith(s)), None)
        if hit is None:
            problems.append(f"structure: missing or out of order: H2 starting {s!r}")
        else:
            pos = hit + 1

    fact_vals = " ".join(cells(l)[2] for l in open("facts.md") if l.startswith("| F-") and len(cells(l)) > 2)
    fact_toks = set(number_tokens(fact_vals, []))
    fact_toks |= set(re.findall(r"\d+(?:\.\d+)?", fact_vals.replace(",", "")))
    exempt = feature.get("doc", {}).get("number_exempt_tokens", [])
    for tok in sorted(set(number_tokens(doc, exempt)), key=lambda x: float(x)):
        if tok not in fact_toks:
            problems.append(f"numbers: {tok} is in update.md but in no facts.md Value")

    claims = open("interview-claims.md").read() if os.path.exists("interview-claims.md") else ""
    norm = lambda s: re.sub(r"\s+", " ", s.replace("\u2019", "'").replace("\\", "")).strip().lower()
    quotable = norm(claims + open("eval-coverage.md").read() + open("facts.md").read())
    claim_rows = [cells(l) for l in claims.split("\n") if l.startswith("| IC-")]
    for m in QUOTE.finditer(doc):
        q = m.group(1).strip().rstrip(".,;:!?")
        if len(q.split()) < 5:
            continue
        if norm(q) not in quotable:
            problems.append(f"quotes: not verbatim in interview-claims.md, eval-coverage.md or facts.md: {q[:80]!r}")
            continue
        rows = [r for r in claim_rows if len(r) > 4 and norm(q) in norm(r[4])]
        if not rows:
            continue
        if any(len(r) > 7 and "CONFLICT" in r[7] for r in rows):
            problems.append(f"quotes: {q[:60]!r} has an attribution conflict in interview-claims.md; leave it out")
            continue
        att = re.match(r"\s*[\"\u201d.,*_]*\s*\(([^,()]+),\s*([A-Z][a-z]{2} \d{1,2})\)", doc[m.end():m.end() + 200])
        if not att:
            problems.append(f"quotes: {q[:60]!r} has no (name, date) attribution right after it")
            continue
        who, when = att.group(1).strip(), att.group(2)
        if not any(who in (r[1], r[1].split()[0]) and when == r[2] for r in rows):
            problems.append(f"quotes: {q[:60]!r} is attributed to ({who}, {when}); interview-claims.md has "
                            + ", ".join(f"({r[1]}, {r[2]})" for r in rows))

    for u in prose_units(doc):
        n = len(sentences(u))
        if n > 4:
            problems.append(f"length: {n} sentences in one bullet or paragraph: {u[:80]!r}")
        for s in sentences(u):
            if s.count(",") >= 2:
                review.append(f"clauses: 2 or more commas; the grader checks for 3 or more clauses: {s[:100]!r}")

    if not feature.get("metrics", {}).get("values_publishable", False):
        for l in open("facts.md"):
            c = cells(l)
            if l.startswith("| F-") and len(c) > 2 and c[1].lower().startswith("metric value"):
                v = plain(c[2])
                if v and re.search(rf"(?<![\d.]){re.escape(v)}(?![\d.])", body):
                    problems.append(f"metrics: {c[0]} ({c[1]}) value {v!r} is in update.md, but metric values are not publishable")

    for old in feature.get("sizing", {}).get("superseded", []):
        if re.search(rf"(?<![\w.$]){re.escape(old)}(?![\w.])", strip_quotes(body)):
            problems.append(f"superseded: {old!r} is a superseded figure (feature.json sizing.superseded)")

    for st in feature.get("ramp", {}).get("steps", []):
        if st.get("date"):
            d = datetime.date.fromisoformat(st["date"])
            label = f"{d.strftime('%b')} {d.day}"
            if label not in body:
                problems.append(f"ramp: {st['step']} date {label} (feature.json ramp) is not in update.md")

    labels = {t["name"]: t for t in counts["themes"]}
    cov = {}
    for l in open("eval-coverage.md"):
        c = cells(l)
        if l.startswith("|") and len(c) >= 6 and c[0] in labels:
            cov[c[0]] = {"verdict": c[1], "judges": [j.strip() for j in c[2].split(",") if j.strip() and j.strip() != "-"],
                         "fix": c[5]}
    tcols = feature.get("doc", {}).get("theme_table", {})
    eval_rows, prio_rows, eval_before = None, None, ""
    for heading, before, header, rows in tables(doc):
        hp = [plain(h) for h in header]
        if tcols.get("theme", "Theme") in hp and tcols.get("drafts", "Drafts flagged") in hp:
            ix = {k: hp.index(v) for k, v in {"theme": tcols.get("theme", "Theme"), "drafts": tcols.get("drafts", "Drafts flagged"),
                                               "interviews": tcols.get("interviews", "Providers interviewed who raised it"),
                                               "tickets": tcols.get("tickets", "Tickets"),
                                               "evals": tcols.get("evals", "Caught by evals today")}.items() if v in hp}
            for r in rows:
                name = plain(r[ix["theme"]])
                t = labels.get(name)
                if t is None:
                    problems.append(f"themes: table theme {name!r} is not in theme-counts.json")
                    continue
                d = plain(r[ix["drafts"]])
                if first_int(d) != t["counted_drafts"]:
                    problems.append(f"themes: {name}: drafts cell {d!r}, counted drafts are {t['counted_drafts']}")
                if t["audit_only"] and str(t["audit_only"]) not in re.findall(r"\d+", d)[1:]:
                    problems.append(f"themes: {name}: drafts cell {d!r} does not show {t['audit_only']} audit-only drafts separately")
                if "interviews" in ix:
                    n = first_int(r[ix["interviews"]])
                    if n is None or n < t["interviewee_floor"]:
                        problems.append(f"themes: {name}: interviewee cell {r[ix['interviews']]!r} is below the session-row floor {t['interviewee_floor']}")
                if "tickets" in ix and "tickets_counted" in t:
                    tc = plain(r[ix["tickets"]])
                    if first_int(tc) != t["tickets_counted"]:
                        problems.append(f"themes: {name}: tickets cell {tc!r}, counted tickets are {t['tickets_counted']}")
                    for p in ("P0", "P1"):
                        n = t["tickets_by_priority"].get(p, 0)
                        shown = re.search(rf"(\d+) {p}", tc)
                        if (shown and int(shown.group(1)) != n) or (n and not shown):
                            problems.append(f"themes: {name}: tickets cell {tc!r}, {p} count is {n}")
                if "evals" in ix:
                    e = plain(r[ix["evals"]])
                    cv = cov.get(name)
                    if cv is None:
                        problems.append(f"themes: {name}: no row in eval-coverage.md")
                    else:
                        if not e.lower().startswith(cv["verdict"].lower()):
                            problems.append(f"themes: {name}: evals cell {e!r}, eval-coverage.md verdict is {cv['verdict']!r}")
                        if cv["verdict"].lower() in ("yes", "partly"):
                            for j in cv["judges"]:
                                if j.lower() not in e.lower():
                                    problems.append(f"themes: {name}: evals cell {e!r} does not name judge {j!r}")
        elif hp and hp[0] == "Gap":
            eval_rows, eval_before = rows, before
        elif hp[:3] == ["Priority", "Definition", "Count"]:
            prio_rows = rows

    if cov:
        gap_labels = {plain(r[0]) for r in (eval_rows or [])}
        for name, cv in cov.items():
            if cv["verdict"].lower() not in ("gap", "partly"):
                continue
            fixes = [f.strip() for f in cv["fix"].split(";") if f.strip()]
            if not fixes or fixes == ["-"]:
                if cv["verdict"].lower() == "gap":
                    problems.append(f"eval gaps: {name} is a Gap with no fix row in eval-coverage.md")
                continue
            for f in fixes:
                if f.lower().startswith("none:"):
                    continue
                if f not in gap_labels:
                    problems.append(f"eval gaps: {name}: fix row {f!r} is not in the eval-changes table")

    tk = counts.get("tickets")
    if tk:
        if prio_rows is not None:
            total = 0
            for r in prio_rows:
                n = first_int(r[2])
                total += n or 0
                want_n = tk["by_priority"].get(plain(r[0]), 0)
                if n != want_n:
                    problems.append(f"tickets: priority table {plain(r[0])} count {r[2]!r}, counted is {want_n}")
            if total != tk["counted"]:
                problems.append(f"tickets: priority table sums to {total}, counted total is {tk['counted']}")
        allowed = {tk["counted"], tk.get("outside_round", 0)}
        allowed |= set(tk.get("filed_by_round", {}).values()) | {t.get("tickets_counted") for t in counts["themes"]}
        for m in re.finditer(r"\b(\d+)( \w+)? tickets\b", strip_quotes(body)):
            if (m.group(2) or "").strip().lower() == "existing":
                continue
            if int(m.group(1)) not in allowed:
                problems.append(f"tickets: {m.group(0)!r} matches no ticket count in theme-counts.json")

    appx = re.search(r"^## Appendix A\b.*?(?=^## |\Z)", doc, re.M | re.S)
    if appx:
        def unlisted_because(v):
            why = []
            if v.get("status_category") == "Done":
                why.append("closed")
            if not v.get("counted", True):
                why.append("not counted")
            if not (v.get("rounds") or v.get("outside_round")):
                why.append("in no round and not filed outside one")
            if (v.get("priority") or "").split(" ")[0] not in ("P0", "P1"):
                why.append(f"priority {v.get('priority')!r}")
            return why

        lines = appx.group(0).splitlines()
        sep = lambda l: re.match(r"^\|\s*:?-{3}", l.strip()) is not None
        rows = [l for i, l in enumerate(lines)
                if l.startswith("|") and not sep(l) and not (i + 1 < len(lines) and sep(lines[i + 1]))]
        listed = set()
        for l in rows:
            keys = re.findall(r"/browse/([A-Z][A-Z0-9]+-\d+)\b", l)
            if not keys:
                problems.append(f"appendix A: row {l.strip()[:60]!r} has no linked Jira ticket")
            listed |= set(keys)
        for k in sorted(listed):
            v = tickets.get(k)
            if v is None:
                problems.append(f"appendix A: {k} is not in tickets.json")
            elif unlisted_because(v):
                problems.append(f"appendix A: {k} is {', '.join(unlisted_because(v))}; Appendix A lists open, counted P0 and P1 tickets only")
        for k in sorted(k for k, v in tickets.items() if k not in listed and not unlisted_because(v)):
            problems.append(f"appendix A: {k} is an open, counted {tickets[k]['priority']} ticket but isn't listed")

    for o in feature.get("owners", []):
        if o.get("email") and o["name"] in body and f"(mailto:{o['email']})" not in doc:
            problems.append(f"owners: {o['name']} is named but never linked as mailto:{o['email']}")
    eo = feature.get("evals", {}).get("owner", {})
    if eval_rows is not None and eo.get("email") and f"mailto:{eo['email']}" not in eval_before:
        problems.append(f"owners: the paragraph above the eval-changes table does not link {eo.get('name')} (mailto:{eo['email']})")

    squash = lambda l: re.sub(r"\s+", " ", l).strip()
    have = {squash(l) for l in doc.split("\n")}
    for pair in a.danny:
        snap, _, base = pair.partition(":")
        if not os.path.exists(snap) or (base and not os.path.exists(base)):
            problems.append(f"danny: {pair}: file not found")
            continue
        before = {squash(l) for l in open(base)} if base else set()
        for l in open(snap):
            s = squash(l)
            if s and s not in before and s not in have:
                problems.append(f"danny: a line Danny wrote ({snap}) is no longer in update.md: {s[:90]!r}")

    print(f"check_doc.py: {len(problems)} problem(s)")
    for p in problems:
        print(" -", p)
    for r in review:
        print(" REVIEW", r)
    print("PASS" if not problems else "FAIL")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
