#!/usr/bin/env python3
"""Print or write the evals.md slice one QA subagent needs.

A slice holds the suite design rules plus the verbatim evals.md section of every
eval the phase map assigns to that group in that phase. Group "merged" is the one
D and R judgment subagent that checks the Definitions, Structure, and
Presentation evals together.

Usage:
  eval-slice.py --phase D --group Fidelity [--final] [--out FILE]
  eval-slice.py --phase D --run RUN_DIR [--final]     # every judgment slice for the phase
  eval-slice.py --id E15                              # one eval's section, for a fix
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", choices=c.PHASES)
    ap.add_argument("--group", help="Fidelity, Definitions, Structure, Presentation, Mechanical, or merged")
    ap.add_argument("--run", help="Run folder; writes evals-<phase>-<group>.md for every judgment subagent")
    ap.add_argument("--final", action="store_true", help="Final QA phase of the run; includes E21")
    ap.add_argument("--id", help="Print one eval's section and exit")
    ap.add_argument("--out", help="Write the slice here instead of stdout")
    a = ap.parse_args()

    if a.id:
        sections = c.eval_sections()
        if a.id not in sections:
            sys.exit(f"No section for {a.id} in evals.md")
        print(sections[a.id])
        return

    if not a.phase:
        ap.error("--phase is required unless --id is given")

    if a.run:
        for unit in c.judgment_units(a.phase):
            path = c.slice_path(a.run, a.phase, unit)
            path.write_text(c.build_slice(a.phase, unit, a.final), encoding="utf-8")
            print(f"{path}  {', '.join(c.assigned_ids(a.phase, unit, a.final))}")
        return

    if not a.group:
        ap.error("--group or --run is required with --phase")
    ids = c.assigned_ids(a.phase, a.group, a.final)
    if not ids:
        sys.exit(f"No evals assigned to {a.group} in phase {a.phase}")
    text = c.build_slice(a.phase, a.group, a.final)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"{a.out}  {', '.join(ids)}")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
