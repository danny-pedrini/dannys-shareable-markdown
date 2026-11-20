#!/usr/bin/env python3
"""Mechanical QA for feature-brief-writer Step 6 (evals G1, G2, G6).

    python3 .claude/skills/feature-brief-writer/scripts/mechanical_check.py \
        --run <run> --round <n> --brief <brief path>

Runs G1, G2, and G6 exactly as their Logic blocks in evals.md state. Writes
<run>/qa-reports/round-<n>-mechanical.md in the judge-report format in
references/run-formats.md, and prints the verdict line plus failing rows.
Adapted from .claude/skills/prd-generator/scripts/mechanical_check.py.
Keep each check in step with its Logic block: when evals.md changes one, change it here too.

Exit codes: 0 report written, 2 usage or input error.
"""
import argparse
import json
import os
import re
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.normpath(os.path.join(SKILL_DIR, "..", "..", ".."))
TEMPLATE = os.path.join(ROOT, "Templates", "Feature-Brief-Template.md")
FORBIDDEN = os.path.join(ROOT, "forbidden-writing-patterns.md")

PASS, FAIL = "Pass", "Fail"
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
BARE_URL = re.compile(r"(?<![(<])\bhttps?://[^\s)>|]+")
FIXES = {
    "G1": "Restore the header, byline, or Appendix list to match the template and gate-1.md; never edit the template to fit.",
    "G2": "Rewrite each hit in plain words (forbidden-writing-patterns.md fix column), then re-run.",
    "G6": "The run should have stopped. Report the failed call to Danny and resume only from primary content.",
}


# ---------- text helpers ----------

def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def norm(s):
    return s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')


def strip_fences(text):
    """Blank out fenced code, keeping the line count so line numbers still match."""
    return re.sub(r"^\s*```.*?^\s*```[^\n]*$", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.M | re.S)


def strip_code_spans(text):
    return re.sub(r"`[^`\n]*`", "", text)


def drop_link_targets(text):
    return LINK.sub(lambda m: "%s[%s]()" % (m.group(1), m.group(2)), text)


def link_text_only(text):
    return LINK.sub(lambda m: m.group(2), text)


def unbold(s):
    return re.sub(r"\*\*|__", "", s).strip()


def headers(text):
    """(level, title, 1-based line) for every markdown header outside fenced code."""
    out = []
    for i, line in enumerate(strip_fences(text).splitlines(), 1):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if m:
            out.append((len(m.group(1)), norm(unbold(m.group(2))), i))
    return out


def table_cells(text, column):
    """Every data cell of `column` in the first markdown table that has it."""
    lines = text.splitlines()
    for i in range(len(lines) - 1):
        if lines[i].strip().startswith("|") and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            head = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if column not in head:
                continue
            k = head.index(column)
            cells = []
            for row in lines[i + 2:]:
                if not row.strip().startswith("|"):
                    break
                parts = [c.strip() for c in row.strip().strip("|").split("|")]
                cells.append(parts[k] if k < len(parts) else "")
            return cells
    return None


def gate1_fields(path):
    """Feature name, options header, and Appendix list from gate-1.md (run-formats.md)."""
    text = read(path)
    m = re.search(r"^# Gate 1:\s*(.+?)\s*$", text, re.M)
    feature = m.group(1) if m else None
    m = re.search(r"^Options header:\s*(.+?)\s*$", text, re.M)
    fallback = norm(m.group(1)) if m else None
    appendix = []
    m = re.search(r"^Appendix:\s*$", text, re.M)
    if m:
        for line in text[m.end():].splitlines()[1:]:
            item = re.match(r"^\s*-\s+(.+?)\s*$", line)
            if not item:
                break
            appendix.append(norm(item.group(1)))
    return feature, fallback, appendix


def canonical_headers():
    """The fenced block under "## Canonical header sequence" in the template."""
    text = read(TEMPLATE)
    start = text.index("## Canonical header sequence")
    m = re.search(r"^```\s*\n(.*?)^```", text[start:], re.M | re.S)
    return [l.strip() for l in m.group(1).splitlines() if l.strip()]


def short(s, n=80):
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 3] + "..."


# ---------- checks ----------

BYLINE = re.compile(r"^[A-Z][\w.'\- ]+ \| (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}$")
PLACEHOLDER = re.compile(r"<[A-Za-z][\w \-]*>")


def g1(doc, gate1):
    """G1 Template conformance, Logic steps 1 to 5."""
    if not os.path.exists(gate1):
        return FAIL, "gate-1.md", "gate-1.md not found at %s" % gate1
    feature, fallback, appendix = gate1_fields(gate1)
    if not feature or not fallback or not appendix:
        return FAIL, "gate-1.md", "ambiguous: gate-1.md lacks the feature name, Options header, or Appendix list"
    if not (fallback.startswith("What are our other options") and fallback.endswith("?")):
        return FAIL, "gate-1.md", "ambiguous: Options header `%s` must start with " \
            "\"What are our other options\" and end with \"?\"" % fallback
    expected = []
    for line in canonical_headers():
        line = line.replace("<X>", feature)
        if line.startswith("## What are our other options"):
            line = "## " + fallback
        lv = len(line) - len(line.lstrip("#"))
        expected.append((lv, norm(line[lv:].strip())))
    fails, locs = [], []
    hs = headers(doc)
    got = [(lv, t) for lv, t, _ in hs if lv <= 2]
    # (1) H1 and H2 sequence
    if got != expected:
        for n in range(max(len(got), len(expected))):
            g = got[n] if n < len(got) else None
            e = expected[n] if n < len(expected) else None
            if g != e:
                line = [i for lv, t, i in hs if lv <= 2][n] if g else "end"
                fails.append("(1) header %d is %s, expected %s" % (
                    n + 1, "`%s %s`" % ("#" * g[0], g[1]) if g else "missing",
                    "`%s %s`" % ("#" * e[0], e[1]) if e else "nothing"))
                locs.append("line %s" % line)
                break
        extra = [t for t in got if got.count(t) > 1]
        if extra:
            fails.append("(1) repeated headers: %s" % ", ".join(sorted({"`%s %s`" % ("#" * l, t) for l, t in extra})))
        n_h1 = sum(1 for lv, _ in got if lv == 1)
        if n_h1 != 1:
            fails.append("(1) %d H1 headers, expected 1" % n_h1)
    # (2) H3s under Appendix, matching the Gate 1 list, lettered with no gap
    parent, h3 = None, []
    for lv, t, i in hs:
        if lv <= 2:
            parent = t
        elif lv == 3:
            h3.append((t, i))
            if parent != "Appendix":
                fails.append("(2) `### %s` sits under `%s`, not Appendix" % (short(t, 50), parent))
                locs.append("line %d" % i)
        else:
            fails.append("(2) H%d `%s` is not allowed" % (lv, short(t, 50)))
            locs.append("line %d" % i)
    titles = [t for t, _ in h3]
    if titles != appendix:
        fails.append("(2) Appendix H3s are %s; gate-1.md lists %s" % (
            [short(t, 40) for t in titles], appendix))
    letters = [a[0] for a in appendix if re.match(r"^[A-Z]\. ", a)]
    if letters != [chr(65 + k) for k in range(len(appendix))]:
        fails.append("(2) gate-1.md Appendix letters %s are not A, B, C with no gap" % letters)
    # (3) byline after the H1
    lines = doc.splitlines()
    h1s = [i for lv, t, i in hs if lv == 1]
    h1 = next((i for lv, t, i in hs if (lv, t) == expected[0]), h1s[0] if h1s else None)
    if h1 is None:
        fails.append("(3) no H1, so no byline to check")
    else:
        k = next((j for j in range(h1, len(lines)) if lines[j].strip()), None)
        nxt = lines[k].strip() if k is not None else ""
        if not BYLINE.match(link_text_only(nxt)):
            fails.append("(3) line after the H1 is `%s`, not `<Name> | <Mon D, YYYY>`" % short(nxt, 60))
            locs.append("line %s" % (k + 1 if k is not None else "end"))
    # (4) leftover placeholders outside code
    body = strip_code_spans(strip_fences(drop_link_targets(doc)))
    body = re.sub(r"<https?://[^>]+>", "", body)
    for n, line in enumerate(body.splitlines(), 1):
        for m in PLACEHOLDER.finditer(line):
            fails.append("(4) placeholder `%s`" % m.group(0))
            locs.append("line %d" % n)
    # (5) Appendix pointers
    for n, line in enumerate(strip_fences(doc).splitlines(), 1):
        for m in re.finditer(r"\bAppendix ([A-Z])\b", line):
            if m.group(1) not in letters:
                fails.append("(5) pointer `Appendix %s` has no sub-section on the Gate 1 list" % m.group(1))
                locs.append("line %d" % n)
    if fails:
        return FAIL, "; ".join(sorted(set(locs), key=locs.index)) or "headers", "; ".join(fails)
    return PASS, "headers", "%d H1/H2 headers match the template; Appendix H3s %s match gate-1.md; byline present" % (
        len(got), [t[:2] for t in titles])


IMPLEMENTED_ROWS = {"0", "1", "3", "4", "5", "6", "8", "8b", "9"}
JUDGE_ROWS = {"7"}  # row 7 is read by the Writing judge (G5)
TAG = re.compile(r"\[Assumption:|\[estimate range\]")
PLAIN = [r"\butiliz\w*", r"\bleverag\w*", r"\bfacilitat\w*", r"\bin order to\b", r"\bprior to\b",
         r"\bsubsequently\b", r"\bdelv\w*", r"\blandscapes?\b", r"\becosystems?\b"]
FILLER = ["It's worth noting", "It's important to", "Needless to say", "At this point in time",
          "moving forward", "going forward"]
SESSION = [(r"\bledger L\d+", re.I), (r"\([^)\n]*\bL\d+\b[^)\n]*\)", 0), (r"\bgate[ -]1\b", re.I),
           (r"\bintake Q\d+", re.I), (r"\bround \d+\b", re.I)]


def forbidden_rows():
    text = read(FORBIDDEN)
    start = text.index("## Hard verification searches")
    end = text.find("\n## ", start + 1)
    return set(re.findall(r"^\|\s*(\d+b?)\s*\|", text[start:end if end != -1 else None], re.M))


def sentence_at(line, pos):
    a = max(line.rfind(". ", 0, pos), -1)
    b = line.find(". ", pos)
    return line[a + 1:b + 1 if b != -1 else len(line)]


def g2(doc):
    """G2 Hard writing searches, on the brief with fenced code, blockquotes, and link targets removed."""
    unknown = forbidden_rows() - IMPLEMENTED_ROWS - JUDGE_ROWS
    if unknown:
        return FAIL, "forbidden-writing-patterns.md", \
            "ambiguous: rows %s have no check in this script" % ", ".join(sorted(unknown))
    text = norm(drop_link_targets(strip_fences(doc)))
    # Blank `>` blockquote lines (verbatim quoted copy) but keep line numbers.
    text = "\n".join("" if re.match(r"^\s*>", l) else l for l in text.split("\n"))
    scrub = BARE_URL.sub(" ", text)
    scrub = re.sub(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b", " ", scrub)
    hits = []

    def hit(n, label, s):
        hits.append(("line %d" % n, "%s: \"%s\"" % (label, short(s, 60))))

    for n, line in enumerate(text.splitlines(), 1):
        if "\u2014" in line:
            hit(n, "row 0 em dash", line[max(0, line.index("\u2014") - 25):line.index("\u2014") + 25])
        if "That's not" in line:
            hit(n, "row 1", "That's not")
        for s in re.split(r"(?<=[.!?])\s+", line):
            if re.search(r"\bless a\b", s, re.I) and re.search(r"\bmore a\b", s, re.I):
                hit(n, "row 3", s)
        for p in ("And that matters", "That's the part everyone misses", "Which is exactly the point"):
            if p in line:
                hit(n, "row 4", p)
        for m in re.finditer(r"It's the .* of", line):
            hit(n, "row 5", m.group(0))
        for p in ("Here's the thing", "Let me be clear", "The truth is", "To be clear", "I'll be honest"):
            if re.search(r"(?:^|[.!?]\s+|\|\s*|^\s*[-*]\s+(?:\[ \]\s+)?|\*\*\s*)" + re.escape(p), line):
                hit(n, "row 6", p)
        for p in PLAIN:
            for m in re.finditer(p, line, re.I):
                hit(n, "plain words", m.group(0))
        for p in FILLER:
            if re.search(re.escape(p), line, re.I):
                hit(n, "filler", p)
        for p, flags in SESSION:
            for m in re.finditer(p, line, flags):
                hit(n, "session-artifact citation", m.group(0))
    for n, line in enumerate(scrub.splitlines(), 1):
        for m in re.finditer(r"\d+\s*(to|-)\s*\d+", line):
            if not TAG.search(sentence_at(line, m.start())):
                hit(n, "row 8 range", m.group(0))
        for m in re.finditer(r"\b(several|a few|some time)\b", line, re.I):
            if "[Assumption:" not in sentence_at(line, m.start()):
                hit(n, "row 8b vague quantity", m.group(0))
    blocks = [b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
    bullets = [l for l in text.splitlines() if re.match(r"^\s*[-*] ", l)][-3:]
    tail = (blocks[-1] if blocks else "") + "\n" + "\n".join(bullets)
    for p in ("In short", "At the end of the day", "To summarize", "In conclusion", "Bottom line:"):
        if p in tail:
            hits.append(("final paragraph or last 3 bullets", "row 9: \"%s\"" % p))
    if hits:
        locs = []
        for loc, _ in hits:
            if loc not in locs:
                locs.append(loc)
        return FAIL, ", ".join(locs), "%d hit(s): %s" % (len(hits), "; ".join(h for _, h in hits))
    return PASS, "whole brief", "Zero hits on rows 0, 1, 3, 4, 5, 6, 8, 8b, 9, the plain-word and filler bans, " \
        "and session-artifact citations (row 7 goes to the Writing judge)"


def g6(run, rnd):
    """G6 Stop discipline, over mcp-calls.jsonl, preflight.md, and link-check.md."""
    fails, locs = [], []
    paths = {k: os.path.join(run, k) for k in ("mcp-calls.jsonl", "preflight.md", "link-check.md")}
    missing = [k for k, p in paths.items() if not os.path.exists(p)]
    if missing:
        return FAIL, ", ".join(missing), "missing file(s): %s" % ", ".join(missing)
    calls = []
    for n, raw in enumerate(read(paths["mcp-calls.jsonl"]).splitlines(), 1):
        if not raw.strip():
            continue
        try:
            calls.append(json.loads(raw))
        except json.JSONDecodeError:
            fails.append("mcp-calls.jsonl line %d is not valid JSON" % n)
            locs.append("mcp-calls.jsonl line %d" % n)
    by_n = {c.get("n"): c for c in calls}
    for k, c in enumerate(calls):
        r = c.get("retry_of")
        if r is not None:
            target = by_n.get(r)
            if target is None or target.get("ok") is not False:
                fails.append("call %s retries call %s, which is not a failed call" % (c.get("n"), r))
                locs.append("mcp-calls.jsonl n=%s" % c.get("n"))
            elif target.get("retry_of") is not None:
                fails.append("call %s is a second retry (call %s was already a retry)" % (c.get("n"), r))
                locs.append("mcp-calls.jsonl n=%s" % c.get("n"))
        if c.get("ok") is not False or str(c.get("step")) == "8":
            continue
        nxt = calls[k + 1] if k + 1 < len(calls) else None
        if nxt is None:
            fails.append("call %s (%s on %s) failed with no retry" % (c.get("n"), c.get("tool"), c.get("resource")))
        elif nxt.get("retry_of") != c.get("n"):
            fails.append("call %s failed and the next call (%s) is not its retry" % (c.get("n"), nxt.get("n")))
        elif (nxt.get("tool"), nxt.get("resource")) != (c.get("tool"), c.get("resource")):
            fails.append("call %s retried with a different tool or resource" % c.get("n"))
        elif nxt.get("ok") is not True:
            fails.append("call %s failed again on retry (call %s)" % (c.get("n"), nxt.get("n")))
        else:
            continue
        locs.append("mcp-calls.jsonl n=%s" % c.get("n"))
    for name in ("preflight.md", "link-check.md"):
        cells = table_cells(read(paths[name]), "Result")
        if cells is None:
            fails.append("%s has no table with a Result column" % name)
            locs.append(name)
            continue
        for k, cell in enumerate(cells, 1):
            if cell != "OK":
                fails.append("%s row %d is `%s`" % (name, k, short(cell, 60)))
                locs.append("%s row %d" % (name, k))
    m = re.search(r"^Round:\s*(\d+)\s*$", read(paths["link-check.md"]), re.M)
    if not m or int(m.group(1)) != rnd:
        fails.append("link-check.md Round is %s, current round is %d" % (m.group(1) if m else "missing", rnd))
        locs.append("link-check.md")
    if fails:
        return FAIL, ", ".join(dict.fromkeys(locs)) or "run folder", "; ".join(fails)
    n_failed = sum(1 for c in calls if c.get("ok") is False and str(c.get("step")) != "8")
    return PASS, "run folder", "%d MCP calls, %d failure(s) each retried once and recovered; preflight and " \
        "link-check rows all OK; link-check Round %d" % (len(calls), n_failed, rnd)


# ---------- report ----------

def previous_fails(run, rnd):
    path = os.path.join(run, "qa-reports", "round-%d-mechanical.md" % (rnd - 1))
    if rnd < 2 or not os.path.exists(path):
        return set()
    return set(re.findall(r"^\|\s*(G\d)\s*\|\s*Fail", read(path), re.M))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--round", required=True, type=int)
    ap.add_argument("--brief", required=True)
    ap.add_argument("--gate1", default=None, help="defaults to <run>/gate-1.md")
    a = ap.parse_args()
    if not os.path.exists(a.brief):
        print(json.dumps({"error": "brief not found: %s" % a.brief}))
        return 2
    gate1 = a.gate1 or os.path.join(a.run, "gate-1.md")
    doc = read(a.brief)
    before = previous_fails(a.run, a.round)
    rows = []
    for eid, fn, args in (("G1", g1, (doc, gate1)), ("G2", g2, (doc,)), ("G6", g6, (a.run, a.round))):
        try:
            res, loc, ev = fn(*args)
        except Exception as exc:  # a Logic block that cannot resolve on this input
            res, loc, ev = FAIL, "n/a", "ambiguous: script error: %s" % exc
        fix = FIXES[eid] if res == FAIL else "n/a"
        pn = ("persistent" if eid in before else "new") if res == FAIL else "n/a"
        rows.append((eid, res, loc, ev.replace("|", "\\|"), fix, pn))
    passed = sum(1 for r in rows if r[1] == PASS)
    verdict = "**Mechanical check, round %d: %d checked, %d passed, %d failed**" % (
        a.round, len(rows), passed, len(rows) - passed)
    out = [verdict, "", "Run by `scripts/mechanical_check.py` on `%s`." % a.brief, "",
           "| Eval | Result | Location | Evidence | Recommended fix | Persistent or new |",
           "|---|---|---|---|---|---|"]
    out += ["| %s | %s | %s | %s | %s | %s |" % r for r in rows]
    os.makedirs(os.path.join(a.run, "qa-reports"), exist_ok=True)
    path = os.path.join(a.run, "qa-reports", "round-%d-mechanical.md" % a.round)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(verdict)
    for r in rows:
        if r[1] != PASS:
            print("| %s | %s | %s | %s |" % r[:4])
    print("report:", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
