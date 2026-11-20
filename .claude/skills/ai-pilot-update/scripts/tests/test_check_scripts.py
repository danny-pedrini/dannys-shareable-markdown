"""Synthetic tests for check_facts.py and check_doc.py.

Run: python3 -I <skill>/scripts/tests/test_check_scripts.py
Builds a passing update folder in a temp directory, then applies one mutation per check and
confirms the script fails with the expected message. Exits non-zero on any unexpected result.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)

FEATURE = {
    "doc": {
        "sections": ["TL;DR", "2. What the feedback says", "4. Bug tickets", "5. What we're changing", "6. Ramp plan"],
        "theme_table": {"theme": "Theme", "drafts": "Drafts flagged", "interviews": "Providers interviewed who raised it",
                        "tickets": "Tickets", "evals": "Caught by evals today"},
        "number_exempt_tokens": ["Sonnet 5.5"],
    },
    "owners": [{"name": "[teammate]", "email": "teammate@example.com"}],
    "evals": {"owner": {"name": "[teammate]", "email": "teammate@example.com"}},
    "metrics": {"values_publishable": False},
    "sizing": {"superseded": ["$1.9M", "30%"]},
    "ramp": {"steps": [{"step": "1% of patients", "date": "2026-11-10"}]},
    "banned_link_patterns": ["fathom.video"],
}

COUNTS = {
    "rounds": [{"drafts": 10}],
    "themes": [
        {"n": 1, "name": "Pricing", "counted_drafts": 5, "audit_only": 7, "interviewee_floor": 0,
         "tickets_counted": 4, "tickets_by_priority": {"P1": 1, "P2": 3}},
        {"n": 2, "name": "Re-asks", "counted_drafts": 9, "audit_only": 0, "interviewee_floor": 4,
         "tickets_counted": 2, "tickets_by_priority": {"P1": 1, "P2": 1}},
    ],
    "tickets": {"counted": 6, "by_priority": {"P0": 0, "P1": 2, "P2": 4}, "filed_by_round": {"pilot-2": 7},
                "outside_round": 0, "closed": ["QCARE-9"], "not_counted": {}},
}

TICKETS = {"QCARE-1": {"priority": "P1", "labels": ["efficiency"], "status": "To Do", "status_category": "To Do",
                       "rounds": ["pilot-2"], "outside_round": False, "read_at": "2026-11-10T15:06Z"}}

RUN_LOG = "# run-log\n2026-11-10T15:00:00Z | Step 0 | step_start |\n"

SOURCES = """| ID | Resource | Link or path | Tool | Read at (UTC) | OK | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| S-01 | Interview synthesis | Project/synthesis.md | Read | 2026-11-10T15:05Z | yes | |
| S-02 | Metrics sheet | (internal link) | sheets read_range | 2026-11-10T15:05Z | yes | |
| S-03 | doctor relationship judge | your-org/ai@abc:judges/doctor_relationship/prompts/v1.md | github get_file_contents | 2026-11-10T15:05Z | yes | blob 123 |
| S-04 | Launch brief | (internal link) | docs read_document | 2026-11-10T15:05Z | yes | |
"""

FACTS = """| ID | Fact | Value | Kind | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| F-001 | Update date | Nov 10, 2026 | ruling | Step 0, 2026-11-10 | |
| F-002 | Week | 2 | ruling | Step 0, 2026-11-10 | |
| F-003 | Drafts | 10 | computed | theme-counts.json#rounds.0.drafts | |
| F-004 | Re-asks flagged | 9 | computed | theme-counts.json#themes.1.counted_drafts | |
| F-005 | Re-asks interviewees | 4 | read | S-01 | |
| F-006 | Interviews | 5 | read | S-01 | |
| F-007 | Pricing flagged | 5 | computed | theme-counts.json#themes.0.counted_drafts | |
| F-008 | Pricing found on review | 7 | computed | theme-counts.json#themes.0.audit_only | |
| F-009 | Pricing interviewees | 3 | read | S-01 | |
| F-010 | Counted tickets | 6 | computed | theme-counts.json#tickets.counted | |
| F-011 | Pricing tickets | 4 | computed | theme-counts.json#themes.0.tickets_counted | |
| F-012 | P1 tickets | 2 | computed | theme-counts.json#tickets.by_priority.P1 | |
| F-013 | Next ramp date | Nov 10 | ruling | feature.json#ramp.steps.0.date | |
| F-014 | Metric value: A2 median handle time | 4.6 | read | S-02 | minutes |
| F-015 | Re-asks P1 tickets | 1 | computed | theme-counts.json#themes.1.tickets_by_priority.P1 | |
| F-016 | P0 tickets | 0 | computed | theme-counts.json#tickets.by_priority.P0 | |
| F-017 | Savings at a 20% cut | 1.17 | read | S-04 | $M |
| F-018 | Savings lost per 5 points short | 0.79 | derived | F-017 | formula: F-017 / 4 |
| F-019 | Interview date | Nov 2 | read | S-01 | |
"""

CLAIMS = """| ID | Speaker | Date | Claim | Verbatim quote | Source and location | Theme | Corroborated by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IC-01 | [teammate] | Nov 2 | Edits are mostly deletions | "I would say it's more deletion than adding to it." | S-01, quote index 1 | Re-asks | S-01 |
"""

COVERAGE = """| Theme | Verdict | Judges | Rule quoted | Files | Fix row |
| --- | --- | --- | --- | --- | --- |
| Re-asks | Partly | doctor relationship | "asks the patient for information the chart or thread already answers" | S-03 | Re-asks that no rule requires |
| Pricing | Gap | - | none in any run-set judge | S-03 | Pricing and instruction clarity |
"""

UPDATE = """# Feature: Pilot Week 2 Update

Nov 10, 2026 | Author

## TL;DR

- **Providers want shorter drafts.** We filed 6 tickets this week.

## 2. What the feedback says

| # | Theme | What goes wrong | Drafts flagged | Providers interviewed who raised it | Tickets | Caught by evals today |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Re-asks | Asks for facts the chart has | 9 | 4 of 5 | 2 (1 P1) | Partly: doctor relationship |
| 2 | Pricing | Price placeholders before a choice | 5, plus 7 more found on review | 3 of 5 | 4 (1 P1) | Gap (unit tests only) |

Doctor relationship fails a draft that "asks the patient for information the chart or thread already answers."

*"I would say it's more deletion than adding to it."* ([teammate], Nov 2)

## 4. Bug tickets

| Priority | Definition | Count |
| --- | --- | --- |
| P0 | Serious safety issue | 0 |
| P1 | Minor safety issue | 2 |
| P2 | Efficiency issue | 4 |

See QCARE-1.

## 5. What we're changing

**Eval considerations:** [teammate] owns these changes.

| Gap | What closes it |
| --- | --- |
| Re-asks that no rule requires | Extend doctor relationship |
| Pricing and instruction clarity | Narrow checks |

## 6. Ramp plan

1% of patients on Nov 10, per the launch brief. Savings are $1.17M; every 5 points short loses $0.29M.
"""

APPX = ("loses $0.29M.\n", "loses $0.29M.\n\n## Appendix A: P0 and P1 tickets\n\n| Priority | Label | The draft should... |\n"
        "| --- | --- | --- |\n| P1 | Efficiency | Name the GLP-1 drug |\n\n"
        "P2 tickets are on the epic.\n")
APPX_ROW = ("| P1 | Efficiency | [Name the GLP-1", "| P0 | Safety | Stop the re-ask |\n| P1 | Efficiency | [Name the GLP-1")
EPIC_READ = ("| S-04 |", "| S-05 | Epic QCARE-7 | (internal link) | jira search | 2026-11-10T15:06Z | yes | |\n| S-04 |")

FILES = {"feature.json": json.dumps(FEATURE), "theme-counts.json": json.dumps(COUNTS), "tickets.json": json.dumps(TICKETS),
         "run-log.md": RUN_LOG, "sources.md": SOURCES, "facts.md": FACTS, "interview-claims.md": CLAIMS,
         "eval-coverage.md": COVERAGE, "update.md": UPDATE}


def build(tmp, changes=None):
    d = tempfile.mkdtemp(dir=tmp)
    for name, text in FILES.items():
        for old, new in (changes or {}).get(name, []):
            if old not in text:
                raise AssertionError(f"mutation target not found in {name}: {old!r}")
            text = text.replace(old, new)
        with open(os.path.join(d, name), "w") as fh:
            fh.write(text)
    return d


def run(script, d, extra=()):
    p = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, script), "--feature", "feature.json", *extra],
                       cwd=d, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


CASES = [
    # (name, script, file changes, extra files, extra args, expected substring or None for pass)
    ("facts pass", "check_facts.py", {}, {}, [], None),
    ("derived formula stale", "check_facts.py", {"facts.md": [("| 0.79 | derived", "| 0.5 | derived")]}, {}, [], "formula F-017 / 4 gives"),
    ("computed value wrong", "check_facts.py", {"facts.md": [("| Drafts | 10 |", "| Drafts | 11 |")]}, {}, [], "Value '11' but"),
    ("source read before run", "check_facts.py", {"sources.md": [("| sheets read_range | 2026-11-10T15:05Z", "| sheets read_range | 2026-11-09T10:00Z")]}, {}, [], "before this run started"),
    ("ruling date drifted", "check_facts.py", {"facts.md": [("| Next ramp date | Nov 10 |", "| Next ramp date | Nov 11 |")]}, {}, [], "feature.json#ramp.steps.0.date is"),
    ("ticket not read this run", "check_facts.py", {"tickets.json": [('"read_at": "2026-11-10T15:06Z"', '"read_at": "2026-11-03T15:06Z"')]}, {}, [], "re-read Jira"),
    ("ticket status category missing", "check_facts.py", {"tickets.json": [('"status_category": "To Do", ', '')]}, {}, [], "missing status_category"),
    ("doc pass", "check_doc.py", {}, {}, [], None),
    ("theme count wrong", "check_doc.py", {"update.md": [("| 9 | 4 of 5 |", "| 10 | 4 of 5 |")]}, {}, [], "themes: Re-asks: drafts cell"),
    ("session artifact", "check_doc.py", {"update.md": [("We filed 6 tickets this week.", "We filed 6 tickets this week, see FM-12.")]}, {}, [], "artifacts: 'FM-12'"),
    ("quote unattributed", "check_doc.py", {"update.md": [(" ([teammate], Nov 2)", "")]}, {}, [], "no (name, date) attribution"),
    ("quote misattributed", "check_doc.py", {"update.md": [("([teammate], Nov 2)", "([teammate], Nov 2)")]}, {}, [], "is attributed to ([teammate], Nov 2)"),
    ("quote conflict", "check_doc.py", {"interview-claims.md": [("| Re-asks | S-01 |", "| Re-asks | CONFLICT with S-01 notes |")]}, {}, [], "attribution conflict"),
    ("bullet too long", "check_doc.py", {"update.md": [("We filed 6 tickets this week.", "We filed 6 tickets this week. Drafts improved. Providers noticed. The team agreed. Work continues.")]}, {}, [], "length: 6 sentences"),
    ("ramp date missing", "check_doc.py", {"feature.json": [('"2026-11-10"', '"2026-11-17"')]}, {}, [], "ramp: 1% of patients date Nov 17"),
    ("metric value unpublishable", "check_doc.py", {"update.md": [("Savings are", "Median handle time is 4.6 minutes. Savings are")]}, {}, [], "metrics: F-014"),
    ("gap without fix row", "check_doc.py", {"update.md": [("| Pricing and instruction clarity | Narrow checks |\n", "")]}, {}, [], "fix row 'Pricing and instruction clarity' is not in the eval-changes table"),
    ("judge not named", "check_doc.py", {"update.md": [("| Partly: doctor relationship |", "| Partly |")]}, {}, [], "does not name judge 'doctor relationship'"),
    ("link not opened", "check_doc.py", {"update.md": [("launch brief", "launch brief")]}, {}, [], "links:"),
    ("priority table wrong", "check_doc.py", {"update.md": [("| P2 | Efficiency issue | 4 |", "| P2 | Efficiency issue | 3 |")]}, {}, [], "tickets: priority table P2"),
    ("superseded figure", "check_doc.py", {"update.md": [("Savings are $1.17M", "Savings are $1.17M, down from $1.9M")]}, {}, [], "superseded: '$1.9M'"),
    ("existing tickets ok", "check_doc.py", {"update.md": [("We filed 6 tickets this week.", "We filed 6 tickets this week and added evidence to 3 existing tickets.")]}, {}, [], None),
    ("ticket phrase wrong", "check_doc.py", {"update.md": [("We filed 6 tickets this week.", "We filed 5 tickets this week.")]}, {}, [], "tickets: '5 tickets'"),
    ("round filed count ok", "check_doc.py", {"update.md": [("We filed 6 tickets this week.", "The round filed 7 tickets; 6 tickets are open.")]}, {}, [], None),
    ("appendix A ok", "check_doc.py", {"update.md": [APPX], "sources.md": [EPIC_READ]}, {}, [], None),
    ("appendix A closed ticket", "check_doc.py", {"update.md": [APPX], "tickets.json": [('"status_category": "To Do"', '"status_category": "Done"')]},
     {}, [], "appendix A: QCARE-1 is closed"),
    ("appendix A P2 ticket", "check_doc.py", {"update.md": [APPX], "tickets.json": [('"priority": "P1"', '"priority": "P2"')]}, {}, [], "priority 'P2'"),
    ("appendix A dropped ticket", "check_doc.py", {"update.md": [APPX], "tickets.json": [('"outside_round": false', '"outside_round": false, "counted": false')]},
     {}, [], "QCARE-1 is not counted"),
    ("appendix A unknown ticket", "check_doc.py", {"update.md": [APPX, APPX_ROW], "sources.md": [EPIC_READ]}, {}, [], "QCARE-55 is not in tickets.json"),
    ("appendix A unlinked row", "check_doc.py", {"update.md": [APPX, ("| P1 | Efficiency | [Name the GLP-1", "| P1 | Safety | Check QCARE-99 first |\n| P1 | Efficiency | [Name the GLP-1")], "sources.md": [EPIC_READ]},
     {}, [], "has no linked Jira ticket"),
    ("appendix A dash row", "check_doc.py", {"update.md": [APPX, ("/QCARE-1) |\n", "/QCARE-1) |\n| - | - | - |\n")], "sources.md": [EPIC_READ]},
     {}, [], "'| - | - | - |' has no linked Jira ticket"),
    ("appendix A ticket missing", "check_doc.py", {"update.md": [APPX], "sources.md": [EPIC_READ], "tickets.json": [('"read_at": "2026-11-10T15:06Z"}}', '"read_at": "2026-11-10T15:06Z"}, '
     '"QCARE-2": {"priority": "P0", "status_category": "In Progress", "rounds": ["pilot-2"], "outside_round": false, "read_at": "2026-11-10T15:06Z"}}')]},
     {}, [], "QCARE-2 is an open, counted P0 ticket but isn't listed"),
    ("url digits are not a range", "check_doc.py", {"update.md": [("We filed 6 tickets this week.", "We filed 6 tickets this week (report).")],
     "sources.md": [("| S-04 |", "| S-05 | Report | (internal link) | docs read_document | 2026-11-10T15:06Z | yes | |\n| S-04 |")]}, {}, [], None),
    ("prose range still fails", "check_doc.py", {"update.md": [("We filed 6 tickets this week.", "We filed 6 tickets this week, with 5 to 10 days of work left.")]}, {}, [], "vague range '5 to 10'"),
    ("number not in ledger", "check_doc.py", {"update.md": [("We filed 6 tickets this week.", "We filed 6 tickets this week across 12 providers.")]}, {}, [], "numbers: 12"),
    ("danny line lost", "check_doc.py", {}, {"update-danny-1.md": UPDATE + "\nDanny's added line.\n", "update-agent-1.md": UPDATE},
     ["--danny", "update-danny-1.md:update-agent-1.md"], "a line Danny wrote"),
    ("danny line kept", "check_doc.py", {"update.md": [("## 6. Ramp plan", "Danny's added line.\n\n## 6. Ramp plan")]},
     {"update-danny-1.md": UPDATE + "\nDanny's added line.\n", "update-agent-1.md": UPDATE}, ["--danny", "update-danny-1.md:update-agent-1.md"], None),
]


def main():
    tmp = tempfile.mkdtemp(prefix="ai-pilot-update-tests-")
    failures = 0
    try:
        for name, script, changes, extra_files, args, expect in CASES:
            d = build(tmp, changes)
            for fname, text in extra_files.items():
                with open(os.path.join(d, fname), "w") as fh:
                    fh.write(text)
            code, out = run(script, d, args)
            ok = (code == 0) if expect is None else (code != 0 and expect in out)
            print(f"{'ok  ' if ok else 'FAIL'} {name}")
            if not ok:
                failures += 1
                print("     expected:", "pass" if expect is None else repr(expect))
                print("     " + out.strip().replace("\n", "\n     "))
    finally:
        shutil.rmtree(tmp)
    print("PASS" if not failures else f"FAIL: {failures} case(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
