#!/usr/bin/env python3
"""Run every Code eval the phase map assigns to Mechanical in a phase, and print the report.

Each check implements its evals.md Logic block. When a block does not resolve on
the artifact, the check reports Fail (ambiguous) and names the judgment
subagent to route it to. When an evals.md Logic block no longer matches the
hash this script was written against, the check reports Fail (ambiguous) until
the script is updated to the new Logic.

Usage:
  mechanical-checks.py --phase D --artifact DOC --run RUN [--final] [--out RUN/qa-reports/D-round-1-mechanical.md]

Artifact: plan.md (P), the inventory (I), the document (D, R).
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c  # noqa: E402

ROUTE = {"P": "Structure", "I": "Fidelity", "D": "merged judgment", "R": "merged judgment"}

# sha256 of each Code eval's ```check block body in evals.md when this script was written.
LOGIC_HASHES = {
    "E01": "36e02d0233f68bfa388ffa7dd481fcc185e9515500a2a0cf1d28b0db86aecc26",
    "E02": "7cae6c187e8f629b468388b1d5587a5ae978eab3d2edcf90f5e7d3cc5edf54f8",
    "E03": "edfb79e05400b60ac926a8e9403ee0d0416a6f3a50fa097b3887af99a8c1dd53",
    "E07": "cdb59ac8a5a0d6818301c529c243401a7103de028aa3f3a183d5db1d02ed1ac4",
    "E08": "a72576e815f7bad25ac044eff15c89b6f90a1b3351428e6c849964f37f7f18b1",
    "E17": "bb9e01c3db033d6f1b566ae511dcd1a6b37a7351683d80b80fbf52d315c65ef7",
    "E21": "b17abdac5d82cd5a6f39a6d1bfe4efb011894473f99b0b31f0112ee99dac1807",
    "E22": "2c907e9cb1199b55123faf4a0b7cdd4197975a998acb03faf4f55044b840d8a6",
    "E23": "4fdd7200b2e09a2031fb6b7dcf8d40a03b73ff633495689ac3297139730c6a83",
    "E26": "7e7b1f19575f2d33afd78339b861e325d93bd9f28cf9283af80bf07674b2d876",
    "E28": "4da225d62b579c5238c77b440c79b634f8cf29d94a849fc00d593e829769c4f4",
    "E29": "6e0b3932e3792306fcabfff77e5b1ceefa0681584c7883bb8b5a35b49df3d44b",
    "E30": "ba0fa6d7aa1f3163262d28411b42d3274ca7551e33ce4c10fec28c8aa1a59e00",
    "E31": "d8ae0f29c5efb4e353c30766205275b1a14358e96c193fd7749f5b15901d59e8",
    "E32": "d364d9ffee85887b9e078551d109c1c4bc75484842af6253f305ad657edfff2a",
    "E33": "9070823959111cf2b1ed083965ef42994d55b00daa07458d7c6786b7492af8ed",
    "E35": "c688b2d3b84db7f4a9276a1143bcfe894ada26a2cb752fe20fc31bc4176c6af6",
    "E39": "6ef601ca57403fd4edcfdc6066ce6cd038e909f42ef0c17024e096436dbcb5e6",
    "E41": "7b2fda52ee49dd274254bc2afe1be590a2baf3a1e1feb16b0d182072b5dc1cdb",
    "E44": "8d5c4aa822a901763ca11798f291fd0c9065f68af999b9d033d6aff698a7621c",
}

ID_ROW = re.compile(r"^\|\s*([OABC])([0-9]+)\s*\|")
LIST_MARKER = re.compile(r"^\s*([-*+]|\d+\.)\s")
HEADER = re.compile(r"^#{1,3}\s")


# ---------- helpers ----------

def logic_block(section):
    m = re.search(r"```check\n(.*?)\n```", section, flags=re.S)
    return m.group(1) if m else None


def logic_hash(section):
    block = logic_block(section)
    return hashlib.sha256(block.encode("utf-8")).hexdigest() if block is not None else None


def cells(line):
    parts = [x.strip() for x in re.split(r"(?<!\\)\|", line.strip())]
    if parts and parts[0] == "":
        parts = parts[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return parts


def prose_blocks(lines):
    """Consecutive non-blank lines not starting with |, #, >, or a list marker. Returns (start line, text)."""
    blocks, cur, start, fence = [], [], None, False
    for n, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            fence = not fence
            if cur:
                blocks.append((start, " ".join(cur)))
                cur = []
            continue
        s = line.strip()
        is_prose = (not fence and s and not s.startswith(("|", "#", ">")) and not LIST_MARKER.match(line))
        if is_prose:
            if not cur:
                start = n
            cur.append(s)
        elif cur:
            blocks.append((start, " ".join(cur)))
            cur = []
    if cur:
        blocks.append((start, " ".join(cur)))
    return blocks


def sentences(text):
    """E26 splitting: [.!?] followed by a space or end, with e.g., i.e., vs., section marks, decimals, and dates non-terminal."""
    t = re.sub(r"\b([eE])\.([gG])\.", r"\1\x00\2\x00", text)
    t = re.sub(r"\b([iI])\.([eE])\.", r"\1\x00\2\x00", t)
    t = re.sub(r"\b(vs)\.", "\\1\x00", t, flags=re.I)
    out, last = [], 0
    for m in re.finditer(r"[.!?](?:\*\*|\*|[\"')\]])*(?=\s|$)", t):
        out.append(t[last:m.end()])
        last = m.end()
    out.append(t[last:])
    return [s.replace("\x00", ".").strip() for s in out if s.strip()]


def section_lines(lines, start_pred, stop_pred):
    """Lines after the first line matching start_pred, up to the first line matching stop_pred."""
    out, inside = [], False
    for n, line in enumerate(lines, 1):
        if inside and stop_pred(line):
            break
        if inside:
            out.append((n, line))
        elif start_pred(line):
            inside = True
    return out


def quote(s, limit=160):
    s = s.replace("|", "\\|").replace("\n", " ").strip()
    return s if len(s) <= limit else s[: limit - 3] + "..."


PASS = "Pass"
FAIL = "Fail"


def ambiguous(ctx, reason):
    return "Fail (ambiguous)", f"{reason}; route to the {ROUTE[ctx['phase']]} subagent"


# ---------- P ----------

def e01(ctx):
    labels = ["Summary", "Stakeholders", "Informed", "Build, rollout, and arm assignment", "Exposure and population",
              "Business outcomes", "Hero metrics", "Reconciling metrics", "Driver metrics", "Guardrail metrics",
              "Slices", "Next steps for ADS", "Open questions", "Change log"]
    low = ctx["text"].lower()
    missing = [x for x in labels if x.lower() not in low]
    if missing:
        return FAIL, "zero matches for: " + ", ".join(missing)
    return PASS, f"all {len(labels)} canonical labels matched"


def e02(ctx):
    pat = re.compile(r"```(sql|lookml)|^\s*(SELECT|WITH)\b.*\bFROM\b|^\s*(dimension|measure|explore|view):\s")
    hits = []
    for n, line in enumerate(ctx["lines"], 1):
        if "not a Looker build spec" in line or "What this is not" in line:
            continue
        if pat.search(line):
            hits.append(f"line {n}: {quote(line)}")
    return (FAIL, "; ".join(hits)) if hits else (PASS, "no build-spec pattern matched")


def e03(ctx):
    problems, found = [], []
    for name in ("data-analytics-eng-reviewer", "pm-exec-reviewer"):
        hits = [(n, line) for n, line in enumerate(ctx["lines"], 1) if name in line]
        if not hits:
            problems.append(f"{name}: no match")
            continue
        for n, line in hits:
            rest = LIST_MARKER.sub("", line.replace(name, ""), count=1)
            if not rest.strip():
                problems.append(f"{name} line {n} has no rationale")
            else:
                found.append(f"{name} line {n}")
    return (FAIL, "; ".join(problems)) if problems else (PASS, "rationale present: " + ", ".join(found))


def e39(ctx):
    path = Path(ctx["run"]) / "intake-transcript.md"
    if not path.exists():
        return FAIL, f"no intake transcript at {path}"
    bad, heading, q, a = [], None, 0, 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^### Q[0-9]+", line):
            if heading and not (q == 1 and a == 1):
                bad.append(heading)
            heading, q, a = line, 0, 0
        if re.match(r"^\*\*Question:\*\* +[^ ]", line):
            q += 1
        if re.match(r"^\*\*Answer:\*\* +[^ ]", line):
            a += 1
    if heading and not (q == 1 and a == 1):
        bad.append(heading)
    if heading is None:
        bad.append("NO BLOCKS")
    return (FAIL, "; ".join(bad)) if bad else (PASS, "every block has one Question line and one Answer line")


# ---------- I ----------

def inventory_rows(ctx):
    return [(n, cells(line)) for n, line in enumerate(ctx["lines"], 1) if re.match(r"^\|\s*\d", line)]


def e07(ctx):
    rows = inventory_rows(ctx)
    if not rows:
        return ambiguous(ctx, "no inventory rows start with '| <digit>'")
    bad = []
    for n, cs in rows:
        empty = [str(i) for i in range(3, 9) if i > len(cs) or not cs[i - 1]]
        if empty:
            bad.append(f"row {cs[0]} (line {n}) empty column(s) {', '.join(empty)}")
    return (FAIL, "; ".join(bad)) if bad else (PASS, f"{len(rows)} rows, columns 3 through 8 non-empty")


def e08(ctx):
    rows = inventory_rows(ctx)
    if not rows:
        return ambiguous(ctx, "no inventory rows start with '| <digit>'")
    pat = re.compile(r"^(PRD|sizing|inventory file|comment|synthesis|prototype|explicit recommendation)\b", re.I)
    bad = [f"row {cs[0]}: '{quote(cs[7] if len(cs) > 7 else '', 60)}'" for n, cs in rows
           if len(cs) < 8 or not pat.match(cs[7])]
    return (FAIL, "; ".join(bad)) if bad else (PASS, f"{len(rows)} Provenance cells start with an allowed tag")


# ---------- D and R ----------

def e17(ctx):
    pat = re.compile(r"```(sql|lookml)|^\s*(SELECT|WITH)\b.*\bFROM\b|^\s*(dimension|measure|explore|view):\s|\bLookML\b"
                     r"|Looker explore|tile layout|event_name|\bschema\b|client events?\b"
                     r"|\bevents?\b[^.|]*\bcarr(y|ies|ying)\b", re.I)
    hits, excluded = [], False
    for n, line in enumerate(ctx["lines"], 1):
        s = line.strip()
        if s.startswith("**What this is not:**"):
            excluded = True
            continue
        if excluded and (s.startswith("**") or HEADER.match(line)):
            excluded = False
        if excluded:
            continue
        if pat.search(line):
            hits.append(f"line {n}: {quote(line)}")
    return (FAIL, "; ".join(hits)) if hits else (PASS, "no build-spec pattern outside the What this is not block")


def e21_check(ctx):
    return c.e21(Path(ctx["run"]) / "mcp-ledger.jsonl")


TAG = re.compile(r"\[Assumption:[^\]]*\]|\[estimate range\]")


def e22(ctx):
    lines, hits = ctx["lines"], []

    def scan(name, pattern, flags=0, strip=None, subset=None):
        rx = re.compile(pattern, flags)
        for n, line in (subset if subset is not None else enumerate(lines, 1)):
            probe = line
            for s in strip or []:
                probe = re.sub(s, " ", probe)
            m = rx.search(probe)
            if m:
                hits.append(f"{name} line {n}: '{quote(m.group(0), 60)}'")

    em = sum(line.count("\u2014") for line in lines)
    if em:
        hits.append(f"em dash count {em}")
    scan("That's not", r"That[’']s not")
    scan("less a/more a", r"less a .* more a")
    scan("self-applause", r"And that matters|That[’']s the part everyone misses|Which is exactly the point")
    scan("analogy", r"It[’']s the .* of")
    scan("opener", r"^(Here[’']s the thing|Let me be clear|The truth is|To be clear|I[’']ll be honest)")
    scan("range", r"\b[0-9]+\s*(to|-)\s*[0-9]+\b",
         strip=[TAG.pattern, r"[0-9]{4}-[0-9]{2}-[0-9]{2}", r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4}", r"§[0-9]+(\.[0-9]+)?"])
    scan("vague quantity", r"\b(several|a few|some time)\b", re.I, strip=[TAG.pattern])
    blocks = prose_blocks(lines)
    bullets = [(n, line) for n, line in enumerate(lines, 1) if LIST_MARKER.match(line)][-3:]
    tail = ([(blocks[-1][0], blocks[-1][1])] if blocks else []) + bullets
    scan("recap", r"In short|At the end of the day|To summarize|In conclusion|Bottom line:", re.I, subset=tail)
    scan("plain word", r"\b(utilize|leverage|facilitate|in order to|prior to|subsequently|delve|landscape|ecosystem)\b",
         re.I)
    scan("filler", r"It[’']s worth noting|It[’']s important to|Needless to say|At this point in time|moving forward"
         r"|going forward", re.I)
    return (FAIL, "; ".join(hits)) if hits else (PASS, "zero matches on every hard search, plain-word, and filler row")


def canonical_headers():
    text = c.TEMPLATE_MD.read_text(encoding="utf-8")
    block = text.split("## Canonical header sequence", 1)[1].split("```", 2)[1]
    out = []
    for line in block.strip("\n").splitlines():
        header = re.split(r"\s{2,}", line.strip())[0]
        out.append((header, "multi-build only" in line))
    return out


TIERS = ["### Hero metrics", "### Reconciling metrics", "### Driver metrics", "### Guardrail metrics"]


def e23(ctx):
    actual = [line.rstrip() for line in ctx["lines"] if HEADER.match(line)]
    build = next((h[len("## A. "):] for h in actual if h.startswith("## A. ")), None)
    norm = []
    for h in actual:
        if h.startswith("## A. "):
            h = "## A. [Build]"
        elif h.startswith("## B. "):
            h = "## B. [Second build]"
        elif h.startswith("# ") and build:
            h = h.replace(build, "[Build]", 1)
        norm.append(h)
    multi = any(h.startswith("## B. ") for h in actual)
    expected = []
    for header, multi_only in canonical_headers():
        if multi_only and not multi:
            continue
        expected.append(header)
        if header == "## B. [Second build]":
            expected += TIERS
    filtered = [h for h in norm if h in set(expected)]
    if filtered == expected:
        return PASS, f"{len(expected)} canonical headers present once each, in order"
    diff = []
    for i in range(max(len(filtered), len(expected))):
        got = filtered[i] if i < len(filtered) else "(none)"
        want = expected[i] if i < len(expected) else "(none)"
        if got != want:
            diff.append(f"position {i + 1}: expected '{want}', found '{got}'")
            break
    missing = [h for h in expected if h not in filtered]
    if missing:
        diff.append("missing: " + ", ".join(missing))
    return FAIL, "; ".join(diff)


def e26(ctx):
    bad = []
    for start, text in prose_blocks(ctx["lines"]):
        ss = sentences(text)
        if len(ss) > 4:
            bad.append(f"block at line {start}: {len(ss)} sentences: '{quote(text, 80)}'")
        for s in ss:
            words = len(s.split())
            if words > 35:
                bad.append(f"line {start}: {words} words: '{quote(s, 80)}'")
    return (FAIL, "; ".join(bad)) if bad else (PASS, "no prose block over 4 sentences, no sentence over 35 words")


def e28(ctx):
    bad, rows, inside = [], 0, False
    for n, line in enumerate(ctx["lines"], 1):
        if re.match(r"^#{2,3}\s", line):
            inside = line.startswith("### Guardrail metrics") or line.startswith("## C. Shared guardrails")
            continue
        if inside and re.match(r"^\|\s*[ABC][0-9]+\s*\|", line):
            rows += 1
            cs = [x for x in cells(line) if x]
            if not cs or "alarm" not in cs[-1].lower():
                bad.append(cs[0] if cs else f"line {n}")
    if bad:
        return FAIL, "no alarm clause in the Good cell of: " + ", ".join(bad)
    return PASS, f"{rows} guardrail rows carry an alarm clause"


def e29(ctx):
    eight = ["#", "Metric", "Definition (numerator / denominator)", "Grain", "Window", "Baseline", "Target", "Good"]
    six = ["#", "Metric", "Definition (numerator / denominator)", "Grain", "Window", "Good"]
    lines, bad, checked = ctx["lines"], [], 0
    for i, line in enumerate(lines):
        s = line.rstrip()
        if s.startswith("## O.") or s.startswith("### Hero metrics"):
            want = eight
        elif s.startswith(("### Reconciling metrics", "### Driver metrics", "### Guardrail metrics",
                           "## C. Shared guardrails")):
            want = six
        else:
            continue
        header = next((x for x in lines[i + 1:] if x.strip().startswith("|")), None)
        checked += 1
        got = [x for x in cells(header)] if header else []
        if got != want:
            bad.append(f"under '{s}': {quote(header or '(no table)', 120)}")
    if not checked:
        return ambiguous(ctx, "no Business outcomes or tier headers found")
    return (FAIL, "; ".join(bad)) if bad else (PASS, f"{checked} table headers match")


def e30(ctx):
    line = next((x for x in ctx["lines"] if "What ADS should build" in x), None)
    if line is None:
        return FAIL, "no 'What ADS should build' line"
    m = re.search(r"([0-9]+) metrics across", line)
    rows = sum(1 for x in ctx["lines"] if ID_ROW.match(x))
    if not m:
        return FAIL, f"no numeral before 'metrics across'; {rows} ID rows"
    stated = int(m.group(1))
    if stated != rows:
        return FAIL, f"Summary says {stated}; {rows} ID rows"
    return PASS, f"Summary says {stated}; {rows} ID rows"


def e31(ctx):
    seqs = {}
    for line in ctx["lines"]:
        m = ID_ROW.match(line)
        if m:
            seqs.setdefault(m.group(1), []).append(int(m.group(2)))
    bad = [f"{p}: {s}" for p, s in seqs.items() if s != list(range(1, len(s) + 1))]
    if bad:
        return FAIL, "; ".join(bad)
    return PASS, ", ".join(f"{p}1 to {p}{len(s)}" for p, s in seqs.items()) or "no ID rows"


def e32(ctx):
    valid, bad = set(), []
    for line in ctx["lines"]:
        m = ID_ROW.match(line)
        if m:
            valid.add(m.group(1) + m.group(2))
    for n, line in enumerate(ctx["lines"], 1):
        text = ID_ROW.sub("|", line, count=1) if ID_ROW.match(line) else line
        tokens = []
        for r in re.finditer(r"\b([OABC])([0-9]+)\s+(?:through|to)\s+\1([0-9]+)\b", text):
            lo, hi = int(r.group(2)), int(r.group(3))
            tokens += [(r.start(), f"{r.group(1)}{k}") for k in range(lo, hi + 1)]
        for t in re.finditer(r"\b[OABC][0-9]+\b", text):
            tokens.append((t.start(), t.group(0)))
        for pos, tok in tokens:
            if re.search(r"\bformer\s*$", text[:pos], re.I):
                continue
            if tok not in valid:
                bad.append(f"{tok} at line {n}: '{quote(line, 80)}'")
    return (FAIL, "; ".join(dict.fromkeys(bad))) if bad else (PASS, f"every ID token resolves to one of {len(valid)} rows")


def e33(ctx):
    bad = []
    for n, line in enumerate(ctx["lines"], 1):
        for m in re.finditer(r"TBD", line):
            window = line[max(0, m.start() - 1):]
            if not re.match(r"\[TBD:\s*[^\]\s][^\]]*\]", window):
                bad.append(f"bare TBD line {n}: '{quote(line, 80)}'")
        if "[owner]" in line:
            bad.append(f"[owner] line {n}")
    body = section_lines(ctx["lines"], lambda x: x.startswith("## 5. Open questions"),
                         lambda x: re.match(r"^##\s", x) is not None)
    table = [(n, x) for n, x in body if x.strip().startswith("|")]
    for n, x in table[1:]:
        cs = cells(x)
        if set("".join(cs)) <= set("-: "):
            continue
        if len(cs) < 2 or not cs[1]:
            bad.append(f"empty Owner cell line {n}")
    return (FAIL, "; ".join(bad)) if bad else (PASS, "every TBD is tagged, no [owner], every Open questions row has an owner")


SUMMARY_LABELS = ["**What ADS should build:**", "**Primary outcome and sizing:**", "**Hard dependency:**",
                  "**Launch date:**", "**Links:**", "**What this is not:**", "**Scope notes:**"]
REQUIRED = ["**What ADS should build:**", "**Primary outcome and sizing:**", "**Launch date:**", "**Links:**",
            "**What this is not:**"]
BUDGET = {"**What ADS should build:**": 1, "**Primary outcome and sizing:**": 2, "**Hard dependency:**": 1,
          "**Launch date:**": 1, "**Scope notes:**": 2}


def e35(ctx):
    body = section_lines(ctx["lines"], lambda x: x.rstrip() == "## Summary",
                         lambda x: x.startswith("### Stakeholders"))
    if not body:
        return FAIL, "no '## Summary' section before '### Stakeholders'"
    bad, seen, in_not = [], [], False
    for n, line in body:
        s = line.strip()
        if not s:
            continue
        label = next((x for x in SUMMARY_LABELS if s.startswith(x)), None)
        if label is None:
            if s.startswith("- ") and in_not:
                continue
            bad.append(f"line {n} unlabeled or not allowed: '{quote(s, 60)}'")
            continue
        in_not = label == "**What this is not:**"
        seen.append(label)
        if label in BUDGET:
            count = len(sentences(s[len(label):].strip()))
            if count > BUDGET[label]:
                bad.append(f"{label.strip('*:')} has {count} sentences, budget {BUDGET[label]}")
    order = [SUMMARY_LABELS.index(x) for x in seen]
    if order != sorted(order) or len(set(seen)) != len(seen):
        bad.append("labels out of order or repeated: " + ", ".join(x.strip("*:") for x in seen))
    for x in REQUIRED:
        if x not in seen:
            bad.append(f"required label missing: {x.strip('*:')}")
    return (FAIL, "; ".join(bad)) if bad else (PASS, f"{len(seen)} allowed labels, in order, within budget")


# ---------- every phase ----------

def e41(ctx):
    phase, run = ctx["phase"], ctx["run"]
    evals_text = c.EVALS_MD.read_text(encoding="utf-8")
    sections = c.eval_sections()
    bad, ok = [], []
    for unit in c.judgment_units(phase):
        before = len(bad)
        path = c.slice_path(run, phase, unit)
        if not path.exists():
            bad.append(f"{path.name} missing")
            continue
        got = path.read_text(encoding="utf-8")
        ids = c.assigned_ids(phase, unit)
        listed = re.search(r"^IDs: (.*)$", got, flags=re.M)
        listed_ids = [x.strip() for x in listed.group(1).split(",")] if listed else []
        if listed_ids != ids:
            bad.append(f"{path.name} lists {listed_ids}, phase map assigns {ids}")
        for eid in ids:
            if sections[eid] not in got or sections[eid] not in evals_text:
                bad.append(f"{path.name}: {eid} section not byte-identical to evals.md")
        if got != c.build_slice(phase, unit):
            bad.append(f"{path.name} differs from a fresh slice")
        if len(bad) == before:
            ok.append(f"{path.name} ({len(ids)} evals)")
    return (FAIL, "; ".join(bad)) if bad else (PASS, "; ".join(ok))


def e44(ctx):
    mpath = Path(ctx["run"]) / "qa-reports" / "manifest.jsonl"
    if not mpath.exists():
        return PASS, "no manifest: no subagent transcripts on this host, so E44 does not apply"
    entries = [json.loads(x) for x in mpath.read_text(encoding="utf-8").splitlines() if x.strip()]
    bad = []
    for e in entries:
        if e.get("agent_type") != "dashboard-qa":
            bad.append(f"{e['agent_id']} ({e.get('role')}) is {e.get('agent_type')}")
        if (e.get("spawn_depth") or 0) > 1:
            bad.append(f"{e['agent_id']} spawnDepth {e.get('spawn_depth')}")
    starts = [e["ts"] for e in entries if e.get("ts")]
    since = datetime.strptime(min(starts), "%Y-%m-%dT%H:%M:%SZ").timestamp() - 3600 if starts else 0
    dirs = {str(Path(e["transcript"]).parent) for e in entries if e.get("transcript")}
    for d in dirs:
        for meta in Path(d).glob("*.meta.json"):
            if os.path.getmtime(meta) < since:
                continue
            depth = json.loads(meta.read_text(encoding="utf-8")).get("spawnDepth") or 0
            if depth > 1:
                bad.append(f"{meta.name} spawnDepth {depth}")
    if bad:
        return FAIL, "; ".join(bad)
    return PASS, f"{len(entries)} manifest agents are dashboard-qa; no subagent above spawnDepth 1"


CHECKS = {
    "E01": e01, "E02": e02, "E03": e03, "E39": e39,
    "E07": e07, "E08": e08,
    "E17": e17, "E21": e21_check, "E22": e22, "E23": e23, "E26": e26, "E28": e28, "E29": e29,
    "E30": e30, "E31": e31, "E32": e32, "E33": e33, "E35": e35,
    "E41": e41, "E44": e44,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", required=True, choices=c.PHASES)
    ap.add_argument("--artifact", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--final", action="store_true", help="Final QA phase of the run; adds E21")
    ap.add_argument("--out", help="Also write the report to this path")
    ap.add_argument("--print-hashes", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args()

    sections = c.eval_sections()
    if a.print_hashes:
        for eid in sorted(CHECKS):
            print(f'    "{eid}": "{logic_hash(sections[eid])}",')
        return

    text = Path(a.artifact).read_text(encoding="utf-8")
    ctx = {"phase": a.phase, "run": a.run, "text": text, "lines": text.splitlines()}
    ids = c.assigned_ids(a.phase, "Mechanical", a.final)
    rows = []
    for eid in ids:
        fn = CHECKS.get(eid)
        if fn is None:
            result, evidence = ambiguous(ctx, f"{eid} has no implementation in mechanical-checks.py")
        elif LOGIC_HASHES.get(eid) != logic_hash(sections.get(eid, "")):
            result, evidence = ambiguous(ctx, f"{eid} Logic block changed since mechanical-checks.py was written")
        else:
            try:
                result, evidence = fn(ctx)
            except Exception as exc:  # a Logic block that does not resolve on this artifact
                result, evidence = ambiguous(ctx, f"{eid} raised {type(exc).__name__}: {exc}")
        rows.append((eid, result, quote(evidence, 600)))
    passed = sum(1 for _, r, _ in rows if r == PASS)
    out = [f"**QA Results (Mechanical): {a.phase}, {len(rows)} checked, {passed} passed, {len(rows) - passed} failed**",
           "", "| Eval | Result | Evidence |", "|---|---|---|"]
    out += [f"| {e} | {r} | {ev} |" for e, r, ev in rows]
    report = "\n".join(out) + "\n"
    sys.stdout.write(report)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
