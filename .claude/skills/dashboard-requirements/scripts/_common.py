"""Shared parsing for the dashboard-requirements scripts.

Reads the eval phase map from SKILL.md and eval sections from evals.md, so the
scripts never carry their own copy of either.
"""

import glob
import json
import os
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
EVALS_MD = SKILL_DIR / "evals.md"
TEMPLATE_MD = SKILL_DIR / "references" / "template.md"

PHASES = ("P", "I", "D", "R")
MERGED = "merged"
MERGED_GROUPS = ("Definitions", "Structure", "Presentation")
MERGED_PHASES = ("D", "R")
JUDGMENT_GROUPS = ("Fidelity",) + MERGED_GROUPS

ROW_ID = re.compile(r"^\|\s*(E\d\d)\b")


def phase_map():
    """Rows of SKILL.md <eval_phase_map>: id, name, group, and a cell per phase."""
    text = SKILL_MD.read_text(encoding="utf-8")
    block = text.split("<eval_phase_map>", 1)[1].split("</eval_phase_map>", 1)[0]
    rows = []
    for line in block.splitlines():
        m = ROW_ID.match(line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        eid, _, name = cells[0].partition(" ")
        row = {"id": eid, "name": name.strip(), "group": cells[1]}
        for phase, cell in zip(PHASES, cells[2:6]):
            row[phase] = cell
        rows.append(row)
    return rows


def active(row, phase, final=False):
    cell = row.get(phase, "")
    if not cell:
        return False
    if cell == "final phase":
        return final
    return True


def assigned_ids(phase, group, final=False):
    """Eval IDs one subagent or script checks in a phase, in phase-map order."""
    groups = MERGED_GROUPS if group == MERGED else (group,)
    return [
        r["id"]
        for r in phase_map()
        if r["group"] in groups and active(r, phase, final)
    ]


def judgment_units(phase):
    """Judgment subagents a phase spawns: Fidelity, plus merged in D and R."""
    units = []
    for group in ("Fidelity",) + MERGED_GROUPS:
        if phase in MERGED_PHASES and group in MERGED_GROUPS:
            if MERGED not in units and assigned_ids(phase, MERGED):
                units.append(MERGED)
            continue
        if assigned_ids(phase, group):
            units.append(group)
    return units


def eval_sections():
    """Map eval ID to its verbatim section in evals.md, heading through the last line before '---'."""
    text = EVALS_MD.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^### (E\d\d):", text, flags=re.M):
        start = m.start()
        end = text.find("\n---\n", start)
        if end == -1:
            end = len(text)
        out[m.group(1)] = text[start:end].rstrip("\n")
    return out


def suite_rules():
    """The suite design rules paragraph, verbatim."""
    text = EVALS_MD.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("**Suite design rules:**"):
            return line
    raise SystemExit("evals.md has no '**Suite design rules:**' paragraph")


def build_slice(phase, group, final=False, ids=None):
    """Slice text for one group and phase: suite rules, then each section verbatim."""
    sections = eval_sections()
    ids = ids or assigned_ids(phase, group, final)
    missing = [i for i in ids if i not in sections]
    if missing:
        raise SystemExit(f"evals.md has no section for: {', '.join(missing)}")
    parts = [
        f"# Eval slice: phase {phase}, group {group}",
        "IDs: " + ", ".join(ids),
        suite_rules(),
    ]
    parts += [sections[i] for i in ids]
    return "\n\n---\n\n".join(parts) + "\n"


def slice_path(run, phase, group):
    return Path(run) / f"evals-{phase}-{group}.md"


def report_rows(text):
    """Table rows of a QA report: (first cell, result, evidence)."""
    rows = []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", s.strip("|"))]
        if len(cells) < 2 or set(cells[0]) <= set("-: "):
            continue
        if cells[0].lower() in ("eval", "check"):
            continue
        evidence = cells[2] if len(cells) > 2 else ""
        rows.append((cells[0], cells[1], evidence))
    return rows


READ_VERB = re.compile(r"^(get|list|read|search|fetch|query|find|describe)_")
WRITE_VERB = re.compile(
    r"(^|_)(create|update|comment|send|post|append|delete|write|set|modify|edit|transition|upload|add|reply"
    r"|share|trash|move|copy|schedule|destructive|make|insert|replace|duplicate|label|mark|forward|push|merge"
    r"|deploy)(_|$)"
)


def e21(ledger):
    """E21 Logic on a ledger file. Returns (result, evidence)."""
    ledger = Path(ledger)
    if not ledger.exists():
        return "Fail (ambiguous)", f"no ledger at {ledger}"
    bad = []
    for n, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            bad.append(f"line {n} is not JSON")
            continue
        if rec.get("write", None) is not False:
            bad.append(f"line {n} write={rec.get('write', 'missing')}: {line.strip()}")
        name = re.sub(r".*__", "", str(rec.get("tool", "")))
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()
        if not READ_VERB.search(name) and WRITE_VERB.search(name):
            bad.append(f"line {n} tool '{name}': {line.strip()}")
    if bad:
        return "Fail", "; ".join(bad)
    return "Pass", "every ledger line has write false; no tool name carries a write verb"


def claude_projects_dir():
    base = os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")
    return Path(base) / "projects"


def find_transcript(agent_id):
    """Path to a subagent's Claude Code transcript, or None (for example in Cursor)."""
    agent_id = agent_id.removeprefix("agent-")
    pattern = str(claude_projects_dir() / "*" / "*" / "subagents" / f"agent-{agent_id}.jsonl")
    hits = glob.glob(pattern)
    return Path(hits[0]) if hits else None


def final_message(transcript):
    """Text blocks of the last assistant message in a transcript, joined in order."""
    blocks_by_msg = {}
    last_id = None
    with open(transcript, encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("type") != "assistant":
                continue
            msg = rec.get("message") or {}
            mid = msg.get("id") or rec.get("uuid")
            content = msg.get("content")
            texts = []
            if isinstance(content, str):
                texts = [content]
            elif isinstance(content, list):
                texts = [c.get("text", "") for c in content if c.get("type") == "text"]
            if texts:
                blocks_by_msg.setdefault(mid, []).extend(texts)
                last_id = mid
    if last_id is None:
        return None
    return "\n\n".join(blocks_by_msg[last_id])


def read_meta(transcript):
    meta = Path(str(transcript).removesuffix(".jsonl") + ".meta.json")
    if not meta.exists():
        return {}
    return json.loads(meta.read_text(encoding="utf-8"))
