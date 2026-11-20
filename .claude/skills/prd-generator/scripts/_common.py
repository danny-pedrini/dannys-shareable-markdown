"""Shared parsing for the prd-generator scripts.

Reads SKILL.md `<eval_phase_map>`, the eval sections of evals.md, and the Step 3 plan briefs.
Every text slice is taken byte for byte from its source file, so extract_briefs.py --verify can
compare a brief file against the source with plain string equality.
"""
import hashlib
import os
import re

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")
EVALS_MD = os.path.join(SKILL_DIR, "evals.md")

PHASES = ("P", "D", "R")
HANDOFF_POINTS = ("H0", "H1", "H2")
GROUP_SLUGS = {
    "Fidelity": "fidelity",
    "Scope-Content": "scope-content",
    "Mechanical": "mechanical",
    "Round check": "round-check",
}
ROW7_KEY = "E38 (row 7)"
MAP_ROW = re.compile(r"^\| (E\d+) (.+?) \| (.+?) \|(.*)\|\s*$")
REPORT_ROW = re.compile(r"^\|\s*(E\d+(?: \(row 7\))?)\s*\|\s*(Pass|Fail \(ambiguous\)|Fail)\s*\|(.*)\|\s*$")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def phase_map():
    """Rows of `<eval_phase_map>`: id, name, group, phases (set of P, D, R)."""
    text = read(SKILL_MD)
    start = text.index("<eval_phase_map>")
    end = text.index("</eval_phase_map>")
    rows = []
    for line in text[start:end].splitlines():
        m = MAP_ROW.match(line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(4).split("|")]
        phases = {p for p, c in zip(PHASES, cells) if c}
        rows.append({"id": m.group(1), "name": m.group(2), "group": m.group(3), "phases": phases})
    if not rows:
        raise SystemExit("No rows parsed from SKILL.md <eval_phase_map>.")
    return rows


def assigned(phase):
    """Eval keys each group must report for a phase (P, D, R) or handoff point (H0, H1, H2)."""
    out = {}
    for row in phase_map():
        group = row["group"]
        if phase in HANDOFF_POINTS:
            if group == "Fidelity (handoff)":
                out.setdefault("fidelity", []).append(row["id"])
            continue
        if phase not in row["phases"]:
            continue
        if group.startswith("Mechanical"):
            out.setdefault("mechanical", []).append(row["id"])
            if "row 7: Fidelity" in group:
                out.setdefault("fidelity", []).append(ROW7_KEY)
        elif group in GROUP_SLUGS:
            out.setdefault(GROUP_SLUGS[group], []).append(row["id"])
    if phase == "P" or phase in HANDOFF_POINTS:
        out.pop("mechanical", None)
    return out


def eval_sections():
    """evals.md eval sections keyed by ID: from the `### Exx:` line up to the `---` separator."""
    text = read(EVALS_MD)
    defs_start = text.index("## Definitions")
    defs_end = text.index("## Retired Evals")
    body = text[defs_start:defs_end]
    heads = list(re.finditer(r"^### (E\d+):.*$", body, re.M))
    out = {}
    for i, h in enumerate(heads):
        stop = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        chunk = body[h.start():stop]
        sep = chunk.rfind("\n---\n")
        out[h.group(1)] = chunk[: sep + 1] if sep != -1 else chunk
    return out


def eval_names():
    return {row["id"]: row["name"] for row in phase_map()}


def contract_block():
    """SKILL.md Step 3 cross-section ownership contract, heading line through its last bullet."""
    text = read(SKILL_MD)
    start = text.index("**Cross-section ownership contract**")
    end = text.index("### Subagent A:", start)
    return text[start:end]


def plan_section(letter):
    """SKILL.md Step 3 section for plan subagent A, B, or C."""
    text = read(SKILL_MD)
    start = text.index("### Subagent %s:" % letter)
    nxt = re.compile(r"^### Subagent [A-C]:|^\*\*After all three return:\*\*", re.M)
    m = nxt.search(text, start + 1)
    return text[start : m.start() if m else len(text)]


def parse_report(path):
    """Rows of a QA report: list of (eval key, result, evidence)."""
    rows = []
    for line in read(path).splitlines():
        m = REPORT_ROW.match(line)
        if m:
            rows.append((m.group(1), m.group(2), m.group(3).strip()))
    return rows
