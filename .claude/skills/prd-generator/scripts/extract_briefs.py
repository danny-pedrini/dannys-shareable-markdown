"""Write the plan and QA brief files for one prd-generator run (SKILL.md Step 1 item 7).

    python3 .claude/skills/prd-generator/scripts/extract_briefs.py --run <run> --all
    python3 .claude/skills/prd-generator/scripts/extract_briefs.py --run <run> --verify

--all writes to <run>/briefs/:
  plan-A.md, plan-B.md, plan-C.md   the subagent's SKILL.md Step 3 section plus the ownership contract
  <P|D|R>-<group>.md                each judgment group's evals active in that phase, from evals.md;
                                    Scope-Content also carries the ownership contract
  H-fidelity.md                     E44, for the handoff check
--verify checks every marked block is byte-identical to its source, and that each QA brief holds
exactly the evals <eval_phase_map> assigns its group. Exits non-zero on any problem.
"""
import argparse
import os
import re
import sys

import _common as c

BEGIN = "<!-- source: %s -->\n"
END = "<!-- end source -->\n"
MARK = re.compile(r"<!-- source: (.+?) -->\n(.*?)<!-- end source -->\n", re.S)
ROW7_NOTE = (
    "E38 below covers only Hard verification search row 7 (exactly-three parallel lists) in "
    "`forbidden-writing-patterns.md`. `scripts/mechanical_check.py` runs every "
    "other row. Report it as `E38 (row 7)`.\n\n"
)


def block(label, text):
    return BEGIN % label + text + ("" if text.endswith("\n") else "\n") + END


def source_text(label):
    if label == "SKILL.md contract":
        return c.contract_block()
    if label.startswith("SKILL.md plan "):
        return c.plan_section(label[-1])
    if label.startswith("evals.md "):
        return c.eval_sections()[label.split()[1]]
    raise KeyError(label)


def qa_brief(phase, slug, keys):
    title = "handoff check" if phase == "H" else "phase %s" % phase
    head = "# Eval brief: %s, group %s\n\n" % (title, slug)
    head += "Eval definitions copied verbatim from evals.md. Report one row per eval, in this order.\n\n"
    parts = [head]
    if slug == "scope-content":
        parts.append("## Cross-section ownership contract\n\n" + block("SKILL.md contract", c.contract_block()) + "\n")
    parts.append("## Evals\n\n")
    sections = c.eval_sections()
    for key in keys:
        eid = key.split()[0]
        if key == c.ROW7_KEY:
            parts.append(ROW7_NOTE)
        parts.append(block("evals.md %s" % eid, sections[eid]) + "\n")
    return "".join(parts)


def plan_brief(letter):
    head = "# Plan brief: subagent %s\n\nYour section and the cross-section ownership contract, copied from SKILL.md Step 3. Do not read SKILL.md.\n\n" % letter
    return head + block("SKILL.md plan %s" % letter, c.plan_section(letter)) + "\n" + block("SKILL.md contract", c.contract_block())


def targets():
    """(filename, content) for every brief file."""
    out = [("plan-%s.md" % x, plan_brief(x)) for x in "ABC"]
    for phase in c.PHASES:
        for slug, keys in c.assigned(phase).items():
            if slug in ("mechanical", "round-check"):
                continue
            out.append(("%s-%s.md" % (phase, slug), qa_brief(phase, slug, keys)))
    out.append(("H-fidelity.md", qa_brief("H", "fidelity", c.assigned("H0")["fidelity"])))
    return out


def write_all(folder):
    os.makedirs(folder, exist_ok=True)
    for name, content in targets():
        with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
            f.write(content)
        print("wrote", os.path.join(folder, name))


def verify(folder):
    problems = []
    expected = dict(targets())
    for name, content in expected.items():
        path = os.path.join(folder, name)
        if not os.path.exists(path):
            problems.append("%s: missing" % name)
            continue
        text = c.read(path)
        for label, body in MARK.findall(text):
            try:
                src = source_text(label)
            except KeyError:
                problems.append("%s: unknown source label %r" % (name, label))
                continue
            if body != src and body != src + "\n":
                problems.append("%s: block %r differs from its source" % (name, label))
        if name.startswith("plan-"):
            continue
        phase, slug = name[:-3].split("-", 1)
        want = c.assigned("H0" if phase == "H" else phase).get(slug, [])
        got = [lbl.split()[1] for lbl, _ in MARK.findall(text) if lbl.startswith("evals.md ")]
        if got != [k.split()[0] for k in want]:
            problems.append("%s: holds %s, <eval_phase_map> assigns %s" % (name, got, want))
    for p in problems:
        print("FAIL", p)
    if not problems:
        print("PASS: %d brief files match their sources and the phase map" % len(expected))
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--all", action="store_true")
    mode.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    folder = os.path.join(a.run, "briefs")
    if a.all:
        write_all(folder)
        return 0
    return verify(folder)


if __name__ == "__main__":
    sys.exit(main())
