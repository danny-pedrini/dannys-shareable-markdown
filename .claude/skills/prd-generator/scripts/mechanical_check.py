"""Mechanical QA for prd-generator phases D and R (references/qa-subagent-briefs.md section 2).

    python3 .claude/skills/prd-generator/scripts/mechanical_check.py --run <run> --phase D --round 1 \
        --artifact <PRD path> --intake <run>/intake-transcript.md \
        [--pre-revision <run>/pre-revision-1.md --touch-list <run>/gate-3.md]

Runs E13, E14, E15, E18, E28, E29, E30, E32, E33, E36, E37 and E38 (every Hard verification row but
row 7, which the Fidelity judge reads) exactly as each Logic block in evals.md states. Writes
<run>/qa-reports/<phase>-round-<n>-mechanical.md and prints the verdict line plus failing rows.
A Logic block that does not cleanly resolve reports `Fail (ambiguous)` with its reason.
Keep each check in step with its Logic block: when evals.md changes one, change it here too.
"""
import argparse
import os
import re
import sys

import _common as c

PASS, FAIL, AMBIG = "Pass", "Fail", "Fail (ambiguous)"
FORBIDDEN = os.path.join(c.SKILL_DIR, "..", "..", "..", "forbidden-writing-patterns.md")
KNOWN_ROWS = {"0", "1", "3", "4", "5", "6", "7", "8", "8b", "9"}
ABBREV = ["e.g.", "i.e.", "U.S.", "etc.", "vs.", "approx.", "Dr.", "Mr.", "Ms.", "No."]
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
BARE_URL = re.compile(r"(?<![(<])\bhttps?://[^\s)>|]+")


# ---------- text helpers ----------

def norm(s):
    return s.replace("\u2019", "'").replace("\u2018", "'")


def strip_fences(text):
    return re.sub(r"^```.*?^```[^\n]*$", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.M | re.S)


def strip_code_spans(text):
    return re.sub(r"`[^`\n]*`", "", text)


def drop_link_targets(text):
    return LINK.sub(lambda m: "%s[%s]()" % (m.group(1), m.group(2)), text)


def drop_links_and_urls(text):
    return BARE_URL.sub("", LINK.sub("", text))


def headers(text):
    """(level, title, line index) for every markdown header outside fenced code."""
    out = []
    for i, line in enumerate(strip_fences(text).splitlines()):
        m = re.match(r"^(#{1,6}) (.+?)\s*#*\s*$", line)
        if m:
            out.append((len(m.group(1)), norm(m.group(2).strip()), i))
    return out


def section(text, title, level=2):
    """Lines under a header until the next header of the same or a higher level, or None."""
    lines = text.splitlines()
    hs = headers(text)
    for n, (lv, t, i) in enumerate(hs):
        if lv == level and t == title:
            end = len(lines)
            for lv2, _, j in hs[n + 1:]:
                if lv2 <= level:
                    end = j
                    break
            return "\n".join(lines[i + 1:end])
    return None


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [x.strip() for x in re.split(r"(?<!\\)\|", s)]


def tables(block):
    """Markdown tables in a block: list of (header cells, data rows)."""
    out = []
    lines = block.splitlines() if block else []
    i = 0
    while i < len(lines) - 1:
        if lines[i].strip().startswith("|") and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            head = [re.sub(r"\*\*", "", x) for x in split_row(lines[i])]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            out.append((head, rows))
            i = j
        else:
            i += 1
    return out


def sentences(s):
    protected = s
    for a in ABBREV:
        protected = protected.replace(a, a.replace(".", "\u2024"))
    parts = re.split(r"(?<=[.!?])\s+", protected.strip())
    return [p.replace("\u2024", ".") for p in parts if p.strip()]


def story_tables(text):
    block = section(text, "User stories", 3)
    return [t for t in tables(block) if t[0] and t[0][0].replace("  ", " ").startswith("ID")]


def story_rows(text):
    rows = []
    for head, data in story_tables(text):
        for r in data:
            rows.append(dict(zip(head, r)))
    return rows


def short(s, n=90):
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 3] + "..."


# ---------- checks ----------

def e13(doc, ctx):
    body = section(doc, "TL;DR")
    if body is None:
        return FAIL, "No `## TL;DR` header"
    body = body.strip()
    fails = []
    if re.search(r"\n\s*\n", body):
        fails.append("more than one paragraph")
    if re.search(r"^\s*([-*] |\d+\. )", body, re.M):
        fails.append("bullet or numbered list")
    if re.search(r"^### ", body, re.M):
        fails.append("sub-header")
    sents = sentences(body.replace("\n", " "))
    if len(sents) > 5:
        fails.append("%d sentences (max 5)" % len(sents))
    for s in sents:
        if s.count("\u2014") + s.count(";") >= 2:
            fails.append("run-on sentence with 2+ em dashes or semicolons: \"%s\"" % short(s))
    if fails:
        return FAIL, "TL;DR has %s" % "; ".join(fails)
    return PASS, "TL;DR is one paragraph of %d sentences" % len(sents)


DOC_STATUS = {"Status", "PM", "Tech lead", "Design lead", "Clinical lead", "Last updated"}
RELATED = {"Background docs", "Sizing", "Acceptance criteria", "Prototype", "Mocks", "Dashboard requirements", "Eval bar"}


def table_after(doc, label):
    idx = doc.find(label)
    if idx == -1:
        return None
    found = tables(doc[idx:])
    return found[0] if found else None


def e14(doc, ctx):
    intake = ctx["intake_text"].lower()
    fails, ambig = [], []
    for label, allowed in (("**Doc status**", DOC_STATUS), ("**Related docs**", RELATED)):
        t = table_after(doc, label)
        if t is None:
            fails.append("%s table not found" % label.strip("*"))
            continue
        for row in t[1]:
            m = re.match(r"^\*\*(.+?)\*\*$", row[0]) if row else None
            if not m:
                continue
            field = m.group(1)
            if field in allowed:
                continue
            if field.lower() in intake:
                ambig.append("'%s' (intake mentions it; confirm Danny requested it)" % field)
            else:
                fails.append("'%s' in %s" % (field, label.strip("*")))
    if fails:
        return FAIL, "Fields outside the template: %s" % "; ".join(fails + ambig)
    if ambig:
        return AMBIG, "Extra fields: %s" % "; ".join(ambig)
    return PASS, "Doc status and Related docs hold only template fields"


def e15(doc, ctx):
    m = re.search(r"```\s*mermaid", doc, re.I)
    return (FAIL, "Mermaid block found") if m else (PASS, "No occurrences of ```mermaid found")


def e18(doc, ctx):
    fails = []
    for m in LINK.finditer(doc):
        tgt = m.group(3)
        if tgt.startswith("#"):
            continue
        if tgt.startswith(("/Users/", "./", "../")) or "://" not in tgt:
            fails.append("local or relative link target `%s`" % tgt)
    text = drop_link_targets(doc)
    pats = [
        (r"\bintake\s*(?:Q|question|#)\s*#?\d+", re.I),
        (r"\bGate [123]\b", 0),
        (r"\bgate-\d", re.I),
        (r"\breviewer row", re.I),
        (r"\bfinding #", re.I),
        (r"\bfinding \d+", re.I),
    ]
    for p, flags in pats:
        for m in re.finditer(p, text, flags):
            fails.append("session-artifact citation \"%s\"" % m.group(0))
    for m in re.finditer(r"\b[A-Z]{2,}-\d{3,}\b", drop_links_and_urls(doc)):
        fails.append("unlinked ticket ID %s" % m.group(0))
    if fails:
        return FAIL, "; ".join(sorted(set(fails)))
    return PASS, "Every link is hosted; no session-artifact citations"


H2_ORDER = ["Approvals", "TL;DR", "What problem are we solving?", "How will we know it worked?",
            "What are we not doing?", "What are we building?", "How does it roll out?", "What could go wrong?",
            "What do we need from others?", "What's still open?", "Appendix", "Revision markers", "Change log"]
H2_REQUIRED = {"Approvals", "TL;DR", "What problem are we solving?", "How will we know it worked?",
               "What are we building?", "How does it roll out?", "What could go wrong?"}
H3_ALLOWED = {"How will we know it worked?": ["Goals", "Metrics"],
              "What are we not doing?": ["Non-goals", "Out of scope"],
              "What are we building?": ["User stories"],
              "Appendix": ["Alternatives considered"]}
H3_REQUIRED = {"How will we know it worked?": ["Goals", "Metrics"], "What are we building?": ["User stories"]}
COLUMNS = {"story": ["ID · P", "User story", "Today", "What good looks like"],
           "metrics": ["Type", "Metric", "Baseline", "Target", "Source"],
           "rollout": ["Stage", "Audience", "Exit criteria"],
           "risks": ["Risk", "Mitigation", "Owner"],
           "dependencies": ["Dependency", "Owner", "What we need", "Blocks launch?"],
           "open questions": ["#", "Question", "Why it matters", "Owner", "Needed by"]}


def e28(doc, ctx):
    fails = []
    hs = headers(doc)
    h2 = [t for lv, t, _ in hs if lv == 2]
    for t in h2:
        if t not in H2_ORDER:
            fails.append("unknown or renamed header `## %s`" % t)
    known = [t for t in h2 if t in H2_ORDER]
    idx = [H2_ORDER.index(t) for t in known]
    if idx != sorted(idx) or len(set(idx)) != len(idx):
        fails.append("`## ` headers out of order or repeated: %s" % ", ".join(known))
    for t in sorted(H2_REQUIRED - set(known), key=H2_ORDER.index):
        fails.append("missing `## %s`" % t)
    if "Change log" in known and known[-1] != "Change log":
        fails.append("`## Change log` is not last")
    parent = None
    seen = {}
    for lv, t, _ in hs:
        if lv == 2:
            parent = t
        elif lv == 3:
            allowed = H3_ALLOWED.get(parent, [])
            if t not in allowed:
                fails.append("unknown or misplaced `### %s` under `## %s`" % (t, parent))
            else:
                seen.setdefault(parent, []).append(t)
    for p, subs in seen.items():
        order = [H3_ALLOWED[p].index(s) for s in subs]
        if order != sorted(order):
            fails.append("`### ` headers out of order under `## %s`" % p)
    for p, req in H3_REQUIRED.items():
        if p in known:
            for r in req:
                if r not in seen.get(p, []):
                    fails.append("missing `### %s` under `## %s`" % (r, p))
    checks = [
        ("story", tables(section(doc, "User stories", 3) or "")),
        ("metrics", tables(section(doc, "Metrics", 3) or "")[:1]),
        ("rollout", tables(section(doc, "How does it roll out?") or "")[:1]),
        ("risks", tables(section(doc, "What could go wrong?") or "")[:1]),
        ("dependencies", tables(section(doc, "What do we need from others?") or "")[:1]),
        ("open questions", tables(section(doc, "What's still open?") or "")[:1]),
    ]
    for name, ts in checks:
        for head, _ in ts:
            got = [" ".join(h.split()) for h in head]
            if got != COLUMNS[name]:
                fails.append("%s table columns are `%s`, expected `%s`" % (name, " | ".join(got), " | ".join(COLUMNS[name])))
    if fails:
        return FAIL, "; ".join(fails)
    return PASS, "All required sections present in template order with required columns"


def e29(doc, ctx):
    fails = []
    body = strip_code_spans(strip_fences(drop_link_targets(doc)))
    body_no_auto = re.sub(r"<https?://[^>]+>", "", body)
    for m in re.finditer(r"<[A-Za-z][^>]*>", body_no_auto):
        fails.append("placeholder `%s`" % m.group(0))
    for s in ("@Name", "Draft / In review / Approved", "Yes / No", "<!--", "Template usage"):
        if s in doc:
            fails.append("`%s`" % s)
    if re.search(r"(?<![A-Za-z])N/A(?![A-Za-z])", doc):
        fails.append("`N/A`")
    lines = doc.splitlines()
    hs = [(lv, t, i) for lv, t, i in headers(doc) if lv in (2, 3, 4)]
    for n, (lv, t, i) in enumerate(hs):
        if lv not in (2, 3):
            continue
        nxt = hs[n + 1] if n + 1 < len(hs) else None
        stop = nxt[2] if nxt else len(lines)
        empty = all(not l.strip() for l in lines[i + 1:stop])
        if empty and (nxt is None or nxt[0] <= lv):
            fails.append("empty section `%s %s`" % ("#" * lv, t))
    if fails:
        return FAIL, "; ".join(fails)
    return PASS, "No template residue or empty sections"


DIRECTION = re.compile(r"\b(up|down|hold|improve|maintain|no regression|increase|decrease)\b", re.I)


def e30(doc, ctx):
    block = section(doc, "How will we know it worked?")
    ts = [t for t in tables(block or "") if "Baseline" in t[0] and "Target" in t[0]]
    if not ts:
        return FAIL, "No metrics table with Baseline and Target columns"
    head, rows = ts[0]
    b, t = head.index("Baseline"), head.index("Target")
    fails = []
    for r in rows:
        if len(r) <= max(b, t):
            fails.append("short row `%s`" % short(" | ".join(r)))
            continue
        base, tgt = r[b], r[t]
        name = r[1] if len(r) > 1 else r[0]
        if not (re.search(r"\d", base) or "[TBD: needs data]" in base or "None (new metric)" in base):
            fails.append("%s: baseline `%s`" % (name, base or "empty"))
        if not (re.search(r"\d", tgt) or "[TBD: needs data]" in tgt):
            why = "directional" if DIRECTION.search(tgt) else "no number"
            fails.append("%s: target `%s` (%s)" % (name, tgt or "empty", why))
    if fails:
        return FAIL, "; ".join(fails)
    return PASS, "Every metrics row has a baseline and a numeric target or TBD tag"


FIG = re.compile(r"\$\s?\d[\d,.]*\s*(?:[KMBkmb]\b|million\b|billion\b|thousand\b)?|\d[\d,.]*\s*%")


def norm_fig(s):
    s = s.lower().replace(" ", "").replace(",", "").rstrip(".")
    return s.replace("million", "m").replace("billion", "b").replace("thousand", "k")


def c1_answer(intake):
    lines = intake.splitlines()
    for i, line in enumerate(lines):
        if re.search(r"\bC1\b", line):
            out = [line]
            for nxt in lines[i + 1:]:
                if re.search(r"^\s*(#+ |\**[A-L]\d+\b)", nxt):
                    break
                out.append(nxt)
            return "\n".join(out)
    return None


def e32(doc, ctx):
    body = section(doc, "What problem are we solving?")
    if body is None:
        return FAIL, "No `## What problem are we solving?` header"
    lines = body.splitlines()
    fails = []

    def find(prefix):
        for i, l in enumerate(lines):
            if l.strip().startswith(prefix):
                return i
        return None

    def has_evidence(chunk):
        return bool(re.search(r"\]\([^)]*://", chunk)) or "[Assumption:" in chunk

    u, bz, fi = find("**User problem:**"), find("**Business problem:**"), find("**Feature impact:**")
    if u is None:
        fails.append("(1) no `**User problem:**` line")
    elif not ("needs a way to" in lines[u] and "because" in lines[u]):
        fails.append("(1) User problem line lacks \"needs a way to\" or \"because\"")
    if u is not None and bz is not None and not has_evidence("\n".join(lines[u:bz])):
        fails.append("(2) no evidence link or Assumption tag for the user problem")
    if bz is None:
        fails.append("(3) no `**Business problem:**` line")
    elif not has_evidence("\n".join(lines[bz:])):
        fails.append("(3) no evidence link or Assumption tag for the business problem")
    if fi is None or (bz is not None and fi < bz):
        fails.append("(4) no `**Feature impact:**` line after the Business problem line")
    elif not (re.search(r"\d", lines[fi]) or "[TBD: needs data]" in lines[fi]):
        fails.append("(4) Feature impact line has no figure or TBD tag")
    if fi is not None and not fails:
        figs = [norm_fig(f) for f in FIG.findall(lines[fi])]
        if figs:
            c1 = c1_answer(ctx["intake_text"])
            src = None
            if c1 is not None:
                src = norm_fig(c1)
            elif ctx["phase"] == "R" and (ctx["pre_text"] or ctx["touch_text"]):
                pre_fi = [l for l in ctx["pre_text"].splitlines() if l.strip().startswith("**Feature impact:**")]
                src = norm_fig(" ".join(pre_fi) + " " + ctx["touch_text"])
            if src is None:
                return AMBIG, "(5) no C1 answer found in the intake transcript and no revise-mode source routed"
            missing = [f for f in figs if f not in src]
            if missing:
                fails.append("(5) Feature impact figure(s) %s not in the sized-impact source" % ", ".join(missing))
    if fails:
        return FAIL, "; ".join(fails)
    return PASS, "POV sentence, evidence for both problems, and a Feature impact figure matching its source"


MARKER = re.compile(r"(\u2795|\U0001F504|~~).*$", re.S)


def e33(doc, ctx):
    fails = []
    for s in ("**Given**", "**When**", "**Then**"):
        if s in doc:
            fails.append("`%s`" % s)
    for line in doc.splitlines():
        if re.search(r"\bGiven\b.*\bWhen\b.*\bThen\b", line):
            fails.append("Given/When/Then in \"%s\"" % short(line))
    for row in story_rows(doc):
        cell = row.get("What good looks like", "")
        n = len(sentences(MARKER.sub("", cell)))
        if n > 2:
            fails.append("%s: What good looks like has %d sentences" % (row.get("ID · P", "?"), n))
    if fails:
        return FAIL, "; ".join(fails)
    return PASS, "No Given/When/Then; every What good looks like cell has 2 sentences or fewer"


ID_CELL = re.compile(r"^[A-Z]{2,6}-\d{2,}[a-z]? \u00b7 P[012]$")
ID_ONLY = re.compile(r"\b([A-Z]{2,6})-(\d{2,})([a-z]?)\b")


def ids_and_stories(text):
    out = {}
    for row in story_rows(text):
        cell = row.get("ID · P", "")
        m = ID_ONLY.search(cell)
        if m:
            out[m.group(0)] = re.sub(r"~~|\u2795|\U0001F504", "", row.get("User story", "")).strip()
    return out


def e36(doc, ctx):
    fails = []
    cells = [row.get("ID · P", "") for row in story_rows(doc)]
    if not cells:
        return FAIL, "No story table found under `### User stories`"
    for cell in cells:
        if not ID_CELL.match(cell):
            fails.append("malformed `%s`" % cell)
    ids = [ID_ONLY.search(x).group(0) for x in cells if ID_ONLY.search(x)]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        fails.append("duplicate IDs %s" % ", ".join(dup))
    if ctx["phase"] == "R":
        if not ctx["pre_text"]:
            return AMBIG, "Phase R with no pre-revision copy routed"
        pre = ids_and_stories(ctx["pre_text"])
        now = ids_and_stories(doc)
        touch = ctx["touch_text"]
        removed = set()
        for line in touch.splitlines():
            if re.search(r"remov|delet|\bcut\b|drop|strik|struck", line, re.I):
                removed.update(m.group(0) for m in ID_ONLY.finditer(line))
        for i in pre:
            if i not in now and i not in removed:
                fails.append("%s missing and the touch list does not remove it" % i)
            if i in now and i in removed and now[i] != pre[i]:
                fails.append("removed ID %s reappears on a different story" % i)
        top = {}
        for i in pre:
            m = ID_ONLY.match(i)
            top[m.group(1)] = max(top.get(m.group(1), 0), int(m.group(2)))
        for i in now:
            if i in pre:
                continue
            m = ID_ONLY.match(i)
            if m.group(1) in top and int(m.group(2)) < top[m.group(1)]:
                fails.append("new ID %s is below the prefix's highest number %d" % (i, top[m.group(1)]))
    if fails:
        return FAIL, "; ".join(fails)
    return PASS, "%d story IDs, well formed and unique" % len(ids)


ALLOW = {"PRD", "TL", "DR", "AI", "GA", "ID", "PM", "P0", "P1", "P2"}


def e37(doc, ctx):
    lines = doc.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    text = "\n".join(lines)
    text = strip_code_spans(strip_fences(text))
    text = BARE_URL.sub(" ", drop_link_targets(text))
    text = re.sub(r"\[TBD:[^\]]*\]", " ", text)
    prefixes = {m.group(1) for m in ID_ONLY.finditer(doc)}
    text = ID_ONLY.sub(" ", text)
    seen, fails = set(), []
    for m in re.finditer(r"\b[A-Z][A-Z0-9&]{1,}\b", text):
        tok = m.group(0)
        if tok in seen or tok in ALLOW or tok in prefixes:
            continue
        seen.add(tok)
        before = text[: m.start()].rstrip()
        after = text[m.end():]
        inside = before.endswith("(") and after.lstrip().startswith(")") and re.search(r"\w\s*\($", before)
        follows = re.match(r"^\s*\(([^)]*[a-z][^)]*)\)", after)
        if not (inside or follows):
            fails.append(tok)
    if fails:
        return FAIL, "No expansion at first use: %s" % ", ".join(fails)
    return PASS, "Every acronym is expanded at first use"


def forbidden_rows():
    path = os.path.normpath(FORBIDDEN)
    if not os.path.exists(path):
        return None, path
    text = c.read(path)
    start = text.find("## Hard verification searches")
    end = text.find("\n## ", start + 1)
    rows = set(re.findall(r"^\|\s*(\d+b?)\s*\|", text[start:end], re.M))
    return rows, path


TAG = re.compile(r"\[Assumption:|\[estimate range\]")
PLAIN = [r"\butiliz\w*", r"\bleverag\w*", r"\bfacilitat\w*", r"\bin order to\b", r"\bprior to\b",
         r"\bsubsequently\b", r"\bdelv\w*", r"\blandscapes?\b", r"\becosystems?\b"]
FILLER = ["It's worth noting", "It's important to", "Needless to say", "At this point in time", "moving forward", "going forward"]


def sentence_of(text, pos):
    a = max(text.rfind(". ", 0, pos), text.rfind("\n", 0, pos))
    b_candidates = [x for x in (text.find(". ", pos), text.find("\n", pos)) if x != -1]
    b = min(b_candidates) if b_candidates else len(text)
    return text[a + 1:b + 1]


def e38(doc, ctx):
    rows, path = forbidden_rows()
    if rows is None:
        return AMBIG, "forbidden-writing-patterns.md not found at %s" % path
    unknown = rows - KNOWN_ROWS
    if unknown:
        return AMBIG, "forbidden-writing-patterns.md has rows %s the script does not implement" % ", ".join(sorted(unknown))
    text = norm(doc)
    fails = []
    if "\u2014" in text:
        fails.append("row 0: %d em dash(es)" % text.count("\u2014"))
    if "That's not" in text:
        fails.append("row 1: \"That's not\"")
    for s in re.split(r"(?<=[.!?])\s+", text):
        if re.search(r"\bless a\b", s, re.I) and re.search(r"\bmore a\b", s, re.I):
            fails.append("row 3: \"%s\"" % short(s))
    for p in ("And that matters", "That's the part everyone misses", "Which is exactly the point"):
        if p in text:
            fails.append("row 4: \"%s\"" % p)
    for m in re.finditer(r"It's the .* of", text):
        fails.append("row 5: \"%s\"" % short(m.group(0)))
    for p in ("Here's the thing", "Let me be clear", "The truth is", "To be clear", "I'll be honest"):
        for m in re.finditer(r"(?:^|[.!?]\s+|\|\s*|^\s*[-*]\s+|\*\*\s*)" + re.escape(p), text, re.M):
            fails.append("row 6: \"%s\"" % p)
    scrubbed = BARE_URL.sub(" ", drop_link_targets(text))
    scrubbed = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " ", scrubbed)
    scrubbed = re.sub(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", " ", scrubbed)
    for m in re.finditer(r"\d+\s*(to|-)\s*\d+", scrubbed):
        if not TAG.search(sentence_of(scrubbed, m.start())):
            fails.append("row 8: \"%s\"" % m.group(0))
    for m in re.finditer(r"\b(several|a few|some time)\b", scrubbed, re.I):
        if not TAG.search(sentence_of(scrubbed, m.start())):
            fails.append("row 8b: \"%s\"" % m.group(0))
    blocks = [b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
    tail = (blocks[-1] if blocks else "") + "\n" + "\n".join([l for l in text.splitlines() if re.match(r"^\s*[-*] ", l)][-3:])
    for p in ("In short", "At the end of the day", "To summarize", "In conclusion", "Bottom line:"):
        if p in tail:
            fails.append("row 9: \"%s\"" % p)
    for p in PLAIN:
        for m in re.finditer(p, text, re.I):
            fails.append("plain words: \"%s\"" % m.group(0))
    for p in FILLER:
        if re.search(re.escape(p), text, re.I):
            fails.append("filler: \"%s\"" % p)
    if fails:
        return FAIL, "; ".join(fails)
    return PASS, "Zero matches across every search but row 7 (Fidelity reads row 7)"


CHECKS = [("E13", e13), ("E14", e14), ("E15", e15), ("E18", e18), ("E28", e28), ("E29", e29), ("E30", e30),
          ("E32", e32), ("E33", e33), ("E36", e36), ("E37", e37), ("E38", e38)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--phase", required=True, choices=["D", "R"])
    ap.add_argument("--round", required=True, type=int)
    ap.add_argument("--artifact", required=True)
    ap.add_argument("--intake", default=None)
    ap.add_argument("--pre-revision", default=None)
    ap.add_argument("--touch-list", default=None)
    a = ap.parse_args()

    assigned = c.assigned(a.phase).get("mechanical", [])
    doc = c.read(a.artifact)
    ctx = {
        "phase": a.phase,
        "intake_text": c.read(a.intake) if a.intake and os.path.exists(a.intake) else "",
        "pre_text": c.read(a.pre_revision) if a.pre_revision and os.path.exists(a.pre_revision) else "",
        "touch_text": c.read(a.touch_list) if a.touch_list and os.path.exists(a.touch_list) else "",
    }
    results = []
    for eid, fn in CHECKS:
        if eid not in assigned:
            continue
        try:
            res, ev = fn(doc, ctx)
        except Exception as exc:  # a Logic block that cannot resolve on this artifact
            res, ev = AMBIG, "script error: %s" % exc
        results.append((eid, res, ev.replace("|", "\\|")))
    missing = [e for e in assigned if e not in dict((r[0], 1) for r in results)]
    for e in missing:
        results.append((e, AMBIG, "assigned to Mechanical but the script has no check for it"))

    passed = sum(1 for r in results if r[1] == PASS)
    verdict = "**QA Results (Mechanical): phase %s, %d checked, %d passed, %d failed**" % (
        a.phase, len(results), passed, len(results) - passed)
    lines = [verdict, "", "Run by `scripts/mechanical_check.py` on `%s` (sha256 %s)." % (a.artifact, c.sha256(a.artifact)), "",
             "| Eval | Result | Evidence |", "|---|---|---|"]
    lines += ["| %s | %s | %s |" % r for r in results]
    out_dir = os.path.join(a.run, "qa-reports")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "%s-round-%d-mechanical.md" % (a.phase, a.round))
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(verdict)
    for r in results:
        if r[1] != PASS:
            print("| %s | %s | %s |" % r)
    print("report:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
