#!/usr/bin/env python3
"""Check the structure of a skill's evals.md.

Usage: python3 -I check_evals_md.py <path to evals.md>

Checks:
  1. Each row in the Active Evals index has a definition section.
  2. Each definition section has an index row.
  3. IDs are unique in the index and among definitions.
  4. Each definition has Pass, Fail, Check type, a `check` or `judge` block,
     Source and Added.

Prints one line per problem and exits 1 on any problem. Prints one OK line and
exits 0 otherwise. A file with an empty index and no definitions (the scaffold)
passes. Standard library only. Reads the file; never writes.
"""
import re
import sys

ID_PATTERN = r"[A-Z]{1,3}-?\d+(?:-\d+)?"
DEF_HEADING = re.compile(r"^###\s+(" + ID_PATTERN + r")\s*:")
SECTION_HEADING = re.compile(r"^##\s+(.*?)\s*$")
FENCE = re.compile(r"^\s*```")
CHECK_BLOCK = re.compile(r"^\s*```(check|judge)\b")

REQUIRED_FIELDS = [
    ("Pass", re.compile(r"\*\*Pass:?\*\*|\*\*Pass\*\*:")),
    ("Fail", re.compile(r"\*\*Fail:?\*\*|\*\*Fail\*\*:")),
    ("Check type", re.compile(r"\*\*Check type:?\*\*|\*\*Check type\*\*:")),
    ("Source", re.compile(r"\*\*Source:?\*\*|\*\*Source\*\*:")),
    ("Added", re.compile(r"\*\*Added:?\*\*|\*\*Added\*\*:")),
]


def split_cells(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def is_separator(cells):
    return all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c)


def parse(lines):
    """Return (index_ids, definitions) where definitions maps ID -> list of lines."""
    index_ids = []
    definitions = {}
    duplicate_defs = []
    section = None
    in_fence = False
    in_index_table = False
    id_col = None
    current_def = None

    for line in lines:
        fence_line = bool(FENCE.match(line))
        if not in_fence:
            m = SECTION_HEADING.match(line)
            if m and not line.startswith("###"):
                section = m.group(1).lower()
                in_index_table = False
                current_def = None
                continue
            dm = DEF_HEADING.match(line)
            if dm and section is not None and section.startswith("definitions"):
                current_def = dm.group(1)
                if current_def in definitions:
                    duplicate_defs.append(current_def)
                else:
                    definitions[current_def] = []
                continue
            if line.startswith("###"):
                # A heading that is not an eval definition ends the current one.
                current_def = None

            if section is not None and section.startswith("active evals"):
                if line.lstrip().startswith("|"):
                    cells = split_cells(line)
                    if not in_index_table:
                        if cells and cells[0].lower() == "id":
                            in_index_table = True
                            id_col = 0
                        continue
                    if is_separator(cells):
                        continue
                    if id_col is not None and id_col < len(cells) and cells[id_col]:
                        index_ids.append(cells[id_col])
                else:
                    in_index_table = False

        if current_def is not None and section is not None and section.startswith("definitions"):
            definitions[current_def].append(line)
        if fence_line:
            in_fence = not in_fence

    return index_ids, definitions, duplicate_defs


def field_problems(eval_id, body_lines):
    problems = []
    text = "\n".join(body_lines)
    for name, pattern in REQUIRED_FIELDS:
        if not pattern.search(text):
            problems.append(f"{eval_id}: missing {name}")
    if not any(CHECK_BLOCK.match(line) for line in body_lines):
        problems.append(f"{eval_id}: missing check or judge block")
    return problems


def main(argv):
    if len(argv) != 2:
        print("usage: check_evals_md.py <path to evals.md>", file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError as err:
        print(f"ERROR cannot read {argv[1]}: {err}")
        return 2

    index_ids, definitions, duplicate_defs = parse(lines)
    problems = []

    seen = set()
    for eval_id in index_ids:
        if eval_id in seen:
            problems.append(f"{eval_id}: duplicate index row")
        seen.add(eval_id)
    for eval_id in duplicate_defs:
        problems.append(f"{eval_id}: duplicate definition section")

    for eval_id in sorted(seen - set(definitions)):
        problems.append(f"{eval_id}: index row has no definition section")
    for eval_id in sorted(set(definitions) - seen):
        problems.append(f"{eval_id}: definition section has no index row")

    for eval_id, body in definitions.items():
        problems.extend(field_problems(eval_id, body))

    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        return 1
    print(f"OK {len(seen)} evals, {len(definitions)} definitions")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
