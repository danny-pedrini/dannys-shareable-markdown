"""Ticket QA checks (Step 3/4 format checker, E14, E20, E21).

Modes:
  --tickets <file> [<file> ...]   banned words and filler (CLAUDE.md), the hard verification
                                  searches (forbidden-writing-patterns.md), em
                                  dashes, the session-artifact regex (E14), body length under
                                  32,000 characters per ticket, and the title pattern
                                  "<action[/action...]|all actions>: <text> (tr-<10 hex>)", or, for a
                                  ticket backed only by feedback-session evidence, ending
                                  "(session YYYY-MM-DD)" or "(sessions YYYY-MM-DD, YYYY-MM-DD)".
                                  Accepts a file with "### T-<n>. <title>" ticket headers (such as
                                  ticket-drafts.md) or a plain body file (such as bodies/*.md);
                                  the title check is skipped (reported, not failed) for a file
                                  with no such header.
  --writing <file> [<file> ...]   writing checks only (plain words, filler, hard searches, em
                                  dash), for E20. No title, length or session-artifact checks.
  --conflict                      E21: no filed failure mode has kind "conflict-flag" while
                                  round.json scope.conflict_flags_in_scope is false.
  --traces <file> [<file> ...]    every "tr-" ID in the file(s) is "tr-" plus exactly 10 hex
                                  characters and a prefix of a trace in export/*.md (read through
                                  check_export.py, never loaded whole). A line that starts
                                  "- Earlier round:" must instead cite a trace in the export/*.md
                                  of a round in round.json prior_rounds (v2.4). For
                                  ticket-drafts.md and ticket-comments.md.
  --threads <file> [<file> ...]   when round.json scope.draft_and_thread is true: each ticket that
                                  cites a trace in its Evidence bullets (not "Also:" lines) has a
                                  "## Draft and thread" section with exactly one "#### `tr-...`"
                                  subheading per cited trace and no other; a ticket that cites no
                                  trace (session-only) has no such section.

Quoted draft and reviewer text inside "## Draft and thread" sections, and inside quote marks
anywhere else, is exempt from the writing checks (both modes): a reviewer's or a draft's own
words are not this round's prose to police.

Prints every hit to stdout and exits non-zero on any. Run from the round folder:
  python3 -I <skill>/scripts/check_tickets.py --tickets ticket-drafts.md
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.getcwd()
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import round_config as RC  # noqa: E402

# ---- CLAUDE.md plain-word and filler lists ----
PLAIN_WORDS = ["utilize", "leverage", "facilitate", "in order to", "prior to", "subsequently", "delve", "landscape", "ecosystem"]
FILLER = ["It's worth noting", "It's important to", "Needless to say", "At this point in time", "moving forward", "going forward"]

# ---- forbidden-writing-patterns.md hard verification searches (code-checkable rows only;
# #7, exactly-three parallel lists, needs a human read and is not grepped here) ----
HARD_SEARCH_PHRASES = [
    "That's not",
    "And that matters", "That's the part everyone misses", "Which is exactly the point",
    "Here's the thing", "Let me be clear", "The truth is", "To be clear", "I'll be honest",
    "several", "a few", "some time",
    "In short", "At the end of the day", "To summarize", "In conclusion", "Bottom line:",
]
RE_LESS_MORE = re.compile(r"less a\b.*\bmore a\b", re.I)
RE_ANALOGY = re.compile(r"\bIt'?s the .* of\b", re.I)
# Deliberately narrow: an isolated 1-3 digit "N to M" or "N-M", not glued to another digit or
# hyphen (so it does not fire on a date like "2026-10-21" or a sheet tab name like
# "20261020-122854"). A date range such as "Oct 15 to 19" is excluded separately by MONTH_RE.
RE_RANGE = re.compile(r"(?<![\d-])\d{1,3}\s*(?:to|-)\s*\d{1,3}(?![\d-])")
RANGE_EXEMPT = re.compile(r"\[Assumption:[^\]]*\(needs validation\)\]|\[estimate range\]", re.I)
MONTH_RE = re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*$", re.I)
EM_DASH = "—"

# Suffix is a trace prefix, or (for a ticket backed only by interview or feedback-session evidence,
# with no trace) one or more session dates: "(session 2026-10-29)" or "(sessions 2026-10-29, 2026-11-02)".
TITLE_RE = re.compile(r"^(?:[a-z][a-z0-9_]*(?:/[a-z][a-z0-9_]*)*|all actions): .+ "
                      r"\((?:tr-[0-9a-fA-F]{10}|sessions? \d{4}-\d{2}-\d{2}(?:, \d{4}-\d{2}-\d{2})*)\)$")


def round_folder_filenames():
    """Basenames of files that actually live in the round folder (the session's own bookkeeping),
    as opposed to a file name that happens to name something in an external codebase (a prompt
    file such as voice_and_style.md, which a ticket may legitimately point engineers at)."""
    names = set()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for f in filenames:
            if f.lower().endswith((".md", ".py")):
                names.add(f.lower())
    return names


def session_artifact_patterns(cfg):
    codes = RC.batch_codes(cfg)
    pats = [r"\b(?:FM|T|C|D)-\d+\b", r"\bCR-[R\d]", r"\bcluster_defs\b", r"\bledger/"]
    if codes:
        pats.append(r"\b(?:" + "|".join(re.escape(c) for c in codes) + r")-\d{3}\b")
    return [re.compile(p) for p in pats]


FILE_TOKEN_RE = re.compile(r"\b[\w-]+\.(?:md|py)\b", re.I)


def strip_exempt(text):
    """Remove quoted draft/reviewer text the writing checks never apply to: the whole "Draft and
    thread" section, and anything inside double or curly quotes elsewhere."""
    text = re.sub(r"\n##\s*Draft and thread\b.*?(?=\n##\s|\Z)", "\n", text, flags=re.S)
    text = re.sub(r"[“\"][^”\"]*[”\"]", "", text)
    return text


def writing_hits(text):
    hits = []
    clean = strip_exempt(text)
    for w in PLAIN_WORDS:
        for m in re.finditer(rf"\b{re.escape(w)}\b", clean, re.I):
            hits.append(f"plain word {w!r}: ...{clean[max(0,m.start()-30):m.end()+30]!r}...")
    for w in FILLER:
        for m in re.finditer(re.escape(w), clean, re.I):
            hits.append(f"filler {w!r}: ...{clean[max(0,m.start()-30):m.end()+30]!r}...")
    if EM_DASH in clean:
        hits.append(f"em dash: hit count {clean.count(EM_DASH)}")
    for w in HARD_SEARCH_PHRASES:
        for m in re.finditer(re.escape(w), clean, re.I):
            hits.append(f"hard search {w!r}: ...{clean[max(0,m.start()-30):m.end()+30]!r}...")
    if RE_LESS_MORE.search(clean):
        hits.append("hard search: 'less a ... more a' contrast metaphor")
    if RE_ANALOGY.search(clean):
        hits.append("hard search: \"It's the X of Y\" analogy")
    for m in RE_RANGE.finditer(clean):
        window = clean[max(0, m.start() - 60):m.end() + 60]
        pre = clean[max(0, m.start() - 15):m.start()]
        if RANGE_EXEMPT.search(window) or MONTH_RE.search(pre):
            continue
        hits.append(f"vague range {m.group(0)!r}: ...{window!r}...")
    return hits


def split_tickets(path):
    """[(title_or_None, body_text), ...]. A "### T-<n>. <title>" file splits into one entry per
    ticket; any other file is one entry with no title to check."""
    text = open(path).read()
    if re.search(r"^### T-\d+\. ", text, re.M):
        if "## 4. Full ticket drafts" in text:
            text = text.split("## 4. Full ticket drafts", 1)[1]
        out = []
        for part in re.split(r"\n(?=### T-\d+\. )", text):
            m = re.match(r"\s*### T-\d+\.\s*(.+)", part)
            if m:
                out.append((m.group(1).strip(), part))
        return out
    return [(None, text)]


def ticket_body(part_text):
    if "## Problem" in part_text:
        body = part_text[part_text.index("## Problem"):]
    else:
        body = part_text
    return body.rstrip().rstrip("-").rstrip()


def check_tickets_mode(paths, cfg):
    problems = []
    sa_patterns = session_artifact_patterns(cfg)
    round_files = round_folder_filenames()
    n_tickets = 0
    for path in paths:
        if not os.path.exists(path):
            problems.append(f"{path}: not found")
            continue
        for title, part in split_tickets(path):
            n_tickets += 1
            label = f"{path}:{title or '(untitled)'}"
            if title is None:
                print(f"{label}: no '### T-n. <title>' header found; title pattern check skipped")
            elif not TITLE_RE.match(title):
                problems.append(f"{label}: title does not match '<action[/action]|all actions>: <text> (tr-<10 hex>)' "
                                f"or '(session YYYY-MM-DD)' or '(sessions YYYY-MM-DD, YYYY-MM-DD)'")
            body = ticket_body(part)
            if len(body) >= 32000:
                problems.append(f"{label}: body is {len(body)} characters, at or over Jira's 32,000 limit")
            clean = strip_exempt(body)
            for pat in sa_patterns:
                for m in pat.finditer(clean):
                    problems.append(f"{label}: session-artifact pattern {pat.pattern!r} matched {m.group(0)!r}")
            for m in FILE_TOKEN_RE.finditer(clean):
                if m.group(0).lower() in round_files:
                    problems.append(f"{label}: cites round-folder file {m.group(0)!r}")
            for h in writing_hits(body):
                problems.append(f"{label}: {h}")
    print(f"check_tickets.py --tickets: {n_tickets} ticket(s) checked across {len(paths)} file(s), {len(problems)} problem(s)")
    for p in problems:
        print(" -", p)
    return 1 if problems else 0


def check_writing_mode(paths):
    problems = []
    for path in paths:
        if not os.path.exists(path):
            problems.append(f"{path}: not found")
            continue
        for h in writing_hits(open(path).read()):
            problems.append(f"{path}: {h}")
    print(f"check_tickets.py --writing: {len(paths)} file(s) checked, {len(problems)} problem(s)")
    for p in problems:
        print(" -", p)
    return 1 if problems else 0


def check_conflict_mode(cfg):
    import cluster_defs as CD
    in_scope = RC.conflict_flags_in_scope(cfg)
    problems = []
    if not in_scope:
        for f in getattr(CD, "FM", []):
            status = getattr(CD, "STATUS", {}).get(f["id"], "")
            if f.get("kind") == "conflict-flag" and "Filed:" in status:
                problems.append(f"{f['id']}: kind is conflict-flag and it was filed ({status}), but scope.conflict_flags_in_scope is false")
    print(f"check_tickets.py --conflict: scope.conflict_flags_in_scope={in_scope}, {len(problems)} problem(s)")
    for p in problems:
        print(" -", p)
    return 1 if problems else 0


RE_TR_TOKEN = re.compile(r"\btr-[0-9a-zA-Z]+\b")
RE_HEX10 = re.compile(r"tr-[0-9a-fA-F]{10}")
RE_EARLIER = re.compile(r"^-\s+Earlier round:")


def check_traces_mode(paths, cfg):
    import check_export as CE
    known = {t[:13].lower() for t in CE.all_export_traces(RC.batch_codes(cfg))}
    # v2.4: a bullet that starts "- Earlier round:" cites a trace from a round in round.json
    # prior_rounds; every other trace must be in this round's export.
    prior = {t[:13].lower() for t in RC.prior_round_exports(cfg)}
    # The same ID may reappear on a line that is not an Earlier-round bullet (the "#### `tr-...`"
    # thread heading add_threads.py inserts, an Eval check bullet). It is fine there when an
    # "Earlier round:" bullet in any checked file cites it.
    cited_earlier = set()
    for path in paths:
        if os.path.exists(path):
            for line in open(path).read().split("\n"):
                if RE_EARLIER.match(line):
                    cited_earlier |= {m.group(0).lower() for m in RE_HEX10.finditer(line)}
    problems, n = [], 0
    for path in paths:
        if not os.path.exists(path):
            problems.append(f"{path}: not found")
            continue
        for i, line in enumerate(open(path).read().split("\n"), 1):
            earlier = bool(RE_EARLIER.match(line))
            for m in RE_TR_TOKEN.finditer(line):
                n += 1
                tok = m.group(0)
                if not RE_HEX10.fullmatch(tok):
                    problems.append(f"{path}:{i}: {tok!r} is not tr- plus exactly 10 hex characters")
                elif earlier:
                    if tok.lower() in known:
                        problems.append(f"{path}:{i}: {tok} is in this round's export; drop the 'Earlier round:' label")
                    elif tok.lower() not in prior:
                        problems.append(f"{path}:{i}: {tok} matches no trace in a prior_rounds export/*.md")
                elif tok.lower() not in known and tok.lower() in prior and tok.lower() in cited_earlier:
                    pass  # an earlier-round trace named again outside its Earlier round: bullet
                elif tok.lower() not in known:
                    hint = " (it is in a prior round's export: start the bullet with 'Earlier round:')" if tok.lower() in prior else ""
                    problems.append(f"{path}:{i}: {tok} matches no trace in export/*.md{hint}")
    print(f"check_tickets.py --traces: {n} trace ID(s) checked across {len(paths)} file(s), "
          f"{len(known)} export traces, {len(prior)} prior-round traces, {len(problems)} problem(s)")
    for p in problems:
        print(" -", p)
    return 1 if problems else 0


def evidence_traces(part):
    if "## Evidence" not in part:
        return []
    ev = part.split("## Evidence", 1)[1].split("\n## ", 1)[0]
    out = []
    for line in ev.split("\n"):
        if line.startswith("- ") and not line.lower().startswith("- also"):
            for t in RE_HEX10.findall(line):
                if t not in out:
                    out.append(t)
    return out


def check_threads_mode(paths, cfg):
    if not RC.draft_and_thread_in_scope(cfg):
        print("check_tickets.py --threads: scope.draft_and_thread is false; nothing to check")
        return 0
    problems, n = [], 0
    for path in paths:
        if not os.path.exists(path):
            problems.append(f"{path}: not found")
            continue
        for title, part in split_tickets(path):
            if title is None:
                continue
            n += 1
            label = f"{path}:{title}"
            cited = evidence_traces(part)
            has_sec = re.search(r"^##\s*Draft and thread\b", part, re.M)
            if not cited:
                if has_sec:
                    problems.append(f"{label}: cites no Evidence trace but has a Draft and thread section")
                continue
            if not has_sec:
                problems.append(f"{label}: cites {len(cited)} Evidence trace(s) and has no Draft and thread section")
                continue
            sec = part[has_sec.end():].split("\n## ", 1)[0]
            subs = re.findall(r"^#### `(tr-[0-9a-fA-F]{10})`", sec, re.M)
            for t in cited:
                if subs.count(t) != 1:
                    problems.append(f"{label}: Evidence trace {t} has {subs.count(t)} thread subheading(s), expected 1")
            for t in sorted(set(subs) - set(cited)):
                problems.append(f"{label}: thread subheading {t} is not an Evidence trace (an 'Also:' trace expanded?)")
    print(f"check_tickets.py --threads: {n} ticket(s) checked across {len(paths)} file(s), {len(problems)} problem(s)")
    for p in problems:
        print(" -", p)
    return 1 if problems else 0


def main():
    args = sys.argv[1:]
    for flag, fn in (("--traces", check_traces_mode), ("--threads", check_threads_mode)):
        if flag in args:
            rest = args[args.index(flag) + 1:]
            paths = [p for a in rest for p in (glob.glob(a) or [a])]
            if not paths:
                print(f"usage: check_tickets.py {flag} <file> [<file> ...]", file=sys.stderr)
                return 1
            return fn(paths, RC.load(os.path.join(ROOT, "round.json")))
    if "--tickets" in args:
        i = args.index("--tickets")
        rest = args[i + 1:]
        paths = [p for a in rest for p in (glob.glob(a) or [a])]
        if not paths:
            print("usage: check_tickets.py --tickets <file> [<file> ...]", file=sys.stderr)
            return 1
        cfg = RC.load(os.path.join(ROOT, "round.json"))
        return check_tickets_mode(paths, cfg)
    if "--writing" in args:
        i = args.index("--writing")
        rest = args[i + 1:]
        paths = [p for a in rest for p in (glob.glob(a) or [a])]
        if not paths:
            print("usage: check_tickets.py --writing <file> [<file> ...]", file=sys.stderr)
            return 1
        return check_writing_mode(paths)
    if "--conflict" in args:
        cfg = RC.load(os.path.join(ROOT, "round.json"))
        return check_conflict_mode(cfg)
    print("usage: check_tickets.py --tickets <file>... | --writing <file>... | --traces <file>... | "
          "--threads <file>... | --conflict", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
