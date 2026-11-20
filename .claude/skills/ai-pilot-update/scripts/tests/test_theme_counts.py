"""Regression test: theme_counts.py reproduces the published Week 1 numbers from Round 1's files.

Run from anywhere:  python3 -I <skill>/scripts/tests/test_theme_counts.py

Fixtures are frozen copies: round1-themes.md (themes.md version 1) and round1-tickets.json (the
filing ledger's priorities and labels plus Danny's two ticket rulings from the handoff, section 4).
The test adds the fields Step 2 writes from the live Jira read: every key is from pilot-1 and open,
since the published tab counts all 32 counted tickets.
The round folder is the live Round 1 folder; this test fails if someone edits its outputs.
Expected values come from the published Week 1 tab, except the clinical-judgment ticket cell:
the tab says 11 (1 P0, 5 P1), which went stale when Danny dropped a P1 (handoff section 4).
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(SKILL)))
ROUND = os.path.join(REPO, "Project-Galen/Phase-3/Discovery/Provider-Pilot-Feedback")
THEMES = os.path.join(HERE, "fixtures/round1-themes.md")

EXPECT_THEMES = {
    # theme label: (counted drafts, audit-only, raters, interviewee floor, tickets counted, by priority).
    # Round 1's row-map.md has no Counted column, so these also test the ledger allow-list path.
    "Re-asking for known facts": (9, 0, 4, 4, 2, {"P1": 1, "P2": 1}),
    "Length, repetition and buried asks": (4, 0, 1, 4, 3, {"P1": 2, "P2": 1}),
    "Pricing": (5, 7, 3, 0, 4, {"P1": 1, "P2": 3}),
    "Clinical judgment": (16, 0, 3, 1, 10, {"P0": 1, "P1": 4, "P2": 5}),
    "Medication status": (7, 0, 2, 2, 5, {"P1": 4, "P2": 1}),
    "Unclear instructions": (6, 2, 3, 0, 8, {"P1": 2, "P2": 6}),
}
EXPECT_ROUND = {"drafts": 77, "failure_modes": 46, "single_draft_fms": 36, "input_only_drafts": 15}
EXPECT_TICKETS = {"counted": 32, "by_priority": {"P0": 1, "P1": 14, "P2": 17},
                  "safety": 11, "efficiency": 21}


def week1_tickets():
    t = json.load(open(os.path.join(HERE, "fixtures/round1-tickets.json")))
    for v in t.values():
        v.update({"status_category": "To Do", "rounds": ["pilot-1"], "outside_round": False})
    return t


def run(tmp, tickets=None, rounds=(ROUND,), themes=THEMES, filed=()):
    out_json = os.path.join(tmp, "tc.json")
    args = [sys.executable, "-I", os.path.join(SKILL, "scripts/theme_counts.py"), "--themes", themes,
            "--out", os.path.join(tmp, "tc.md"), "--json", out_json]
    for r in rounds:
        args += ["--round", r]
    for r in filed:
        args += ["--filed-round", r]
    if tickets is not None:
        path = os.path.join(tmp, "tickets.json")
        json.dump(tickets, open(path, "w"))
        args += ["--tickets", path]
    r = subprocess.run(args, capture_output=True, text=True)
    return r.returncode, (json.load(open(out_json)) if r.returncode in (0, 3) else None), r.stderr + r.stdout


V2_HEADER = ("| Row | Trace | Reviewer | Provenance | Classification | Destination | Source | Evidence basis | Counted |\n"
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")


def write_round(path, slug, rows, fms, watch=None, exports=None):
    os.mkdir(path)
    json.dump({"slug": slug, "batches": [{"code": c, "action": "x"} for c in (exports or {})]},
              open(os.path.join(path, "round.json"), "w"))
    if exports:
        os.mkdir(os.path.join(path, "export"))
        for c, text in exports.items():
            open(os.path.join(path, "export", f"{c}.md"), "w").write(text)
    open(os.path.join(path, "row-map.md"), "w").write("# Row map\n\n" + V2_HEADER + "".join(f"| {r} |\n" for r in rows))
    open(os.path.join(path, "failure-modes.md"), "w").write("".join(f"| {f} |\n" for f in fms))
    if watch is not None:
        open(os.path.join(path, "watch-list.md"), "w").write(
            "| Item | Behavior | Action types | Severity class | Counted drafts | Providers | Hold flag | First held | Rounds waited |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n" + "".join(f"| {w} |\n" for w in watch))


def v2_round_checks(tmp):
    """A synthetic round built by provider-draft-failure-modes v2.0 (row-map.md has a Counted column)."""
    fails = []
    new, prior = os.path.join(tmp, "new"), os.path.join(tmp, "prior")
    t = "tr-" + "a" * 32
    write_round(new, "r2", [
        f"TA-001 | {t[:13]} | provider_1 | reviewer | x | FM-01 | thumbs-downs | reviewer-stated | yes",
        "TA-002 | tr-bbbbbbbbbb | eval | eval | x | FM-01 | evals | eval-judge | yes",
        "TA-003 | tr-cccccccccc | audit | inferred | x | FM-01 | audit | inferred | no",
        "SP-001 | tr-dddddddddd | scan | phrase-scan | - | FM-01 | scan | phrase-scan | yes",
        "TA-004 | tr-eeeeeeeeee | provider_2 | reviewer | x | FM-01 | edits | provider-edit | no",
        "TA-005 | tr-gggggggggg | audit | inferred | x | FM-01 | edits | provider-edit | no",
        "SA-001 | S1-Q3 | session_a | reviewer | x | FM-01 | interviews | reviewer-stated | yes",
    ], ["Failure mode | Behavior | Band | Filing call", "--- | --- | --- | ---",
        "FM-01 | x Filed: QCARE-1 | recurring | file", "FM-02 | y | one-off | hold: seen once, efficiency"],
        ["r2/FM-02 | x | send_message | efficiency | tr-ffffffffff | provider_1 | none | r2 | 0",
         "r1/FM-09 | y | send_message | efficiency | none | none | none | r1 | 1"],
        {"TA": f"*Trace tr-{'b' * 32} · Provider: provider_3*\n"})
    write_round(prior, "r1", [f"TB-001 | {t[:13]} | provider_1 | reviewer | x | FM-03 | thumbs-downs | reviewer-stated | yes"],
                ["FM-03 | y"])
    themes = os.path.join(tmp, "themes.md")
    open(themes, "w").write("## Themes\n\n| # | Theme | What goes wrong | Failure modes |\n| --- | --- | --- | --- |\n"
                            "| 1 | T | x | r2: FM-01, FM-02; r1: FM-03 |\n\n## Not in a theme\n\n"
                            "| Round | Failure mode | Reason | Ruled by |\n| --- | --- | --- | --- |\n")
    code, got, err = run(tmp, rounds=(new,), themes=themes)
    if code != 0:
        return [f"v2 round: exited {code}: {err}"]
    th, rnd = got["themes"][0], got["rounds"][0]
    have = (th["counted_drafts"], th["audit_only"], th["raters"], th["interviewee_floor"], th["by_source"])
    want = (3, 1, 2, 1, {"evals": 1, "scan": 1, "thumbs-downs": 1})  # raters: provider_1, eval export's provider_3
    if have != want:
        fails.append(f"v2 round: got {have}, want {want}")
    if rnd["single_draft_fms"] is not None or rnd["held"] != {"one_offs": 1, "watch_list": 2}:
        fails.append(f"v2 round: single_draft_fms {rnd['single_draft_fms']}, held {rnd['held']}")
    args = [sys.executable, "-I", os.path.join(SKILL, "scripts/theme_counts.py"), "--themes", themes, "--round", new,
            "--prior-round", prior, "--out", os.path.join(tmp, "p.md"), "--json", os.path.join(tmp, "p.json")]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        return fails + [f"v2 prior round: exited {r.returncode}: {r.stderr}"]
    th = json.load(open(os.path.join(tmp, "p.json")))["themes"][0]
    have = (th["counted_drafts"], th["raters"], th["by_round"]["r2"]["already_counted"])
    if have != (2, 1, 1):
        fails.append(f"v2 prior round: counted, raters, already counted {have}, want (2, 1, 1)")
    r = subprocess.run(args[:7] + ["--prior-round", new, "--out", os.path.join(tmp, "q.md"), "--json", os.path.join(tmp, "q.json")],
                       capture_output=True, text=True)
    if r.returncode != 2 or "both --round and --prior-round" not in r.stderr:
        fails.append(f"same round as --round and --prior-round: want exit 2, got {r.returncode}: {r.stderr}")
    return fails


def main():
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        code, got, err = run(tmp, week1_tickets())
    if code != 0:
        print("FAIL: theme_counts.py exited", code, err)
        return 1
    rnd = got["rounds"][0]
    for k, v in EXPECT_ROUND.items():
        if rnd[k] != v:
            fails.append(f"round {k}: got {rnd[k]}, want {v}")
    for row in got["themes"]:
        want = EXPECT_THEMES.get(row["name"])
        if want is None:
            fails.append(f"unexpected theme {row['name']}")
            continue
        have = (row["counted_drafts"], row["audit_only"], row["raters"], row["interviewee_floor"],
                row["tickets_counted"], row["tickets_by_priority"])
        if have != want:
            fails.append(f"{row['name']}: got {have}, want {want}")
    t = got["tickets"]
    have = {"counted": t["counted"], "by_priority": t["by_priority"],
            "safety": t["by_category"]["safety"], "efficiency": t["by_category"]["efficiency"]}
    if have != EXPECT_TICKETS:
        fails.append(f"tickets: got {have}, want {EXPECT_TICKETS}")
    if t["filed_by_round"] != {"pilot-1": 32} or t["outside_round"] != 0 or t["closed"]:
        fails.append(f"tickets: filed_by_round {t['filed_by_round']}, outside_round {t['outside_round']}, closed {t['closed']}")
    if got["unassigned"]:
        fails.append(f"unassigned FMs: {got['unassigned']}")

    with tempfile.TemporaryDirectory() as tmp:
        code, empty, err = run(tmp, rounds=())
        if code != 0:
            fails.append(f"no-round run exited {code}: {err}")
        elif empty["rounds"] or any(t["counted_drafts"] for t in empty["themes"]):
            fails.append("no-round run: expected an empty rounds list and zero counts")

    with tempfile.TemporaryDirectory() as tmp:
        code, got, err = run(tmp, week1_tickets(), rounds=())
        if code != 0 or got["tickets"]["counted"] != 32:
            fails.append(f"no-round run with tickets: want 32 open tickets, got exit {code} {got and got['tickets']}")

    with tempfile.TemporaryDirectory() as tmp:
        tk = week1_tickets()
        p1 = next(k for k, v in sorted(tk.items()) if v["priority"].startswith("P1") and v.get("counted", True))
        tk[p1]["status_category"] = "Done"
        tk["QCARE-900"] = {"priority": "P2 - Minor", "labels": ["efficiency"], "status_category": "To Do",
                           "counted": True, "rounds": [], "outside_round": True}
        tk["QCARE-901"] = {"priority": "P0 - Blocker", "labels": ["safety"], "status_category": "To Do",
                           "counted": True, "rounds": [], "outside_round": False}
        code, got, err = run(tmp, tk)
        t = got["tickets"] if got else {}
        want = {"counted": 32, "P1": 13, "P0": 1, "outside_round": 1, "closed": [p1]}
        have = {"counted": t.get("counted"), "P1": t.get("by_priority", {}).get("P1"), "P0": t.get("by_priority", {}).get("P0"),
                "outside_round": t.get("outside_round"), "closed": t.get("closed")}
        if code != 0 or have != want:
            fails.append(f"open-only scope: want {want}, got exit {code} {have} {err if code else ''}")

    with tempfile.TemporaryDirectory() as tmp:
        tk = week1_tickets()
        del tk[sorted(tk)[0]]["status_category"]
        code, _, err = run(tmp, tk)
        if code != 2 or "status_category" not in err:
            fails.append(f"missing status_category: want exit 2, got {code}: {err}")

    with tempfile.TemporaryDirectory() as tmp:
        tk = week1_tickets()
        del tk[sorted(tk)[0]]["rounds"]
        code, _, err = run(tmp, tk)
        if code != 2 or "no rounds" not in err:
            fails.append(f"missing rounds: want exit 2, got {code}: {err}")

    with tempfile.TemporaryDirectory() as tmp:
        tk = week1_tickets()
        k = sorted(tk)[0]
        tk[k].update({"status": "Blocked", "status_category": "In Progress"})
        code, got, err = run(tmp, tk)
        if code != 0 or got["tickets"]["counted"] != 32:
            fails.append(f"blocked ticket: want it counted as open (32), got exit {code} {got and got['tickets']['counted']} {err}")
        tk[k]["status_category"] = "Blocked"
        code, _, err = run(tmp, tk)
        if code != 2 or "status_category must be one of" not in err:
            fails.append(f"status as category: want exit 2, got {code}: {err}")

    with tempfile.TemporaryDirectory() as tmp:
        old = os.path.join(tmp, "old-round")
        os.mkdir(old)
        json.dump({"slug": "pilot-0"}, open(os.path.join(old, "round.json"), "w"))
        open(os.path.join(old, "failure-modes.md"), "w").write("| FM-01 | Old issue | Filed: QCARE-900 |\n")
        code, _, err = run(tmp, week1_tickets(), filed=(old,))
        if code != 2 or "QCARE-900, filed by pilot-0" not in err:
            fails.append(f"older round key missing: want exit 2, got {code}: {err}")
        tk = week1_tickets()
        tk["QCARE-900"] = {"priority": "P2 - Minor", "labels": ["efficiency"], "status_category": "To Do",
                           "counted": True, "rounds": ["pilot-0"], "outside_round": False}
        code, got, err = run(tmp, tk, filed=(old,))
        if code != 0 or got["tickets"]["counted"] != 33 or got["tickets"]["filed_by_round"].get("pilot-0") != 1:
            fails.append(f"older round key present: want 33 open, got exit {code} {got and got['tickets']} {err}")
        tk["QCARE-900"]["rounds"] = []
        tk["QCARE-900"]["outside_round"] = True
        code, _, err = run(tmp, tk, filed=(old,))
        if code != 2 or "QCARE-900 is filed by pilot-0 but its rounds list doesn't name it" not in err:
            fails.append(f"older round not in rounds list: want exit 2, got {code}: {err}")
        code, _, err = run(tmp, None, filed=(old,))
        if code != 2 or "--filed-round needs --tickets" not in err:
            fails.append(f"--filed-round without --tickets: want exit 2, got {code}: {err}")

    with tempfile.TemporaryDirectory() as tmp:
        tk = week1_tickets()
        tk[sorted(tk)[0]]["priority"] = None
        code, _, err = run(tmp, tk)
        if code != 2 or "has no priority for" not in err:
            fails.append(f"null priority: want exit 2 with a message, got {code}: {err}")
        tk = week1_tickets()
        tk[sorted(tk)[0]]["category"] = "clinical"
        code, _, err = run(tmp, tk)
        if code != 2 or "category must be safety, efficiency, neither or null" not in err:
            fails.append(f"unknown category: want exit 2 with a message, got {code}: {err}")
        tk = week1_tickets()
        tk[sorted(tk)[0]]["rounds"] = None
        code, _, err = run(tmp, tk)
        if code != 2 or "rounds must be a list" not in err:
            fails.append(f"null rounds: want exit 2 with a message, got {code}: {err}")

    with tempfile.TemporaryDirectory() as tmp:
        fails += v2_round_checks(tmp)

    themes_text = open(THEMES).read()
    for label, text, want in [
        ("FM in two themes", themes_text.replace("pilot-1: FM-11, FM-12,", "pilot-1: FM-01, FM-11, FM-12,"), "in two themes"),
        ("FM in a theme and not in a theme",
         themes_text.replace("| --- | --- | --- | --- |\n\n## Version log", "| --- | --- | --- | --- |\n| pilot-1 | FM-01 | test | test |\n\n## Version log"),
         "and in 'Not in a theme'"),
    ]:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "themes.md")
            open(path, "w").write(text)
            if text == themes_text:
                fails.append(f"{label}: fixture edit didn't apply")
                continue
            code, _, err = run(tmp, themes=path)
            if code != 2 or want not in err:
                fails.append(f"{label}: want exit 2, got {code}: {err}")

    for f in fails:
        print("FAIL:", f)
    print("PASS" if not fails else f"{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
