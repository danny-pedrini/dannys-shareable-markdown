"""Gate 1 checks on the fact ledger (evals G1-1, G1-6a, G1-7a and G1-10; formats in references/ledger-formats.md).

Run from the update folder:
    python3 -I <skill>/scripts/check_facts.py [--feature ../../feature.json]

Checks:
  sources.md  every row has an ID, a resource, a tool, a UTC read time at or after the run's first
              run-log event, and OK = yes. A row with OK = no passes only if a later row for the same
              link or path has OK = yes (Danny fixed access and the run re-read it).
  facts.md    unique F- IDs; a value; a kind of read, computed, derived or ruling; and a source that
              resolves:
                read      S- IDs that exist in sources.md with OK = yes
                computed  <file>.json#<dot.path> that exists and whose value matches the Value cell
                derived   F- IDs that exist, plus "formula: <arithmetic over F- IDs>" in Notes,
                          evaluated and compared to Value (1% tolerance), or
                          "formula (manual): ..." for the Gate 1 grader to recompute
                ruling    feature.json#<dot.path> that resolves (a date, number or boolean there must
                          match the Value), or "Gate <n>, YYYY-MM-DD" or "Step 0, YYYY-MM-DD"
  tickets.json  every key has priority, labels, status, status_category, rounds and outside_round,
                and a read_at at or after the run start.
Prints every problem and exits non-zero on any.
"""
import argparse
import datetime
import json
import os
import re
import sys

ROW = re.compile(r"^\| ([SF]-\d+) \|")
TS = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z)")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_ts(s):
    m = TS.search(s or "")
    if not m:
        return None
    v = m.group(1)
    fmt = "%Y-%m-%dT%H:%M:%SZ" if v.count(":") == 2 else "%Y-%m-%dT%H:%MZ"
    return datetime.datetime.strptime(v, fmt).replace(tzinfo=datetime.timezone.utc)


def run_start():
    if not os.path.exists("run-log.md"):
        return None
    for line in open("run-log.md"):
        t = parse_ts(line.split("|")[0]) if "|" in line else None
        if t:
            return t
    return None


def resolve(obj, path):
    for part in path.split("."):
        if isinstance(obj, list):
            if not part.isdigit() or int(part) >= len(obj):
                return None, False
            obj = obj[int(part)]
        elif isinstance(obj, dict):
            if part not in obj:
                return None, False
            obj = obj[part]
        else:
            return None, False
    return obj, True


def num(v):
    return float(re.search(r"-?\d+(?:\.\d+)?", str(v).replace(",", "")).group(0))


def ruling_matches(got, value):
    """Dates, numbers and booleans in feature.json must match the Value; longer text is checked by the grader."""
    if isinstance(got, bool):
        return value.strip().lower() in (("yes", "true") if got else ("no", "false"))
    if isinstance(got, (int, float)):
        return norm(got) == norm(value)
    if isinstance(got, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", got):
        d = datetime.date.fromisoformat(got)
        return value.strip() in (got, f"{d.strftime('%b')} {d.day}", f"{d.strftime('%b')} {d.day}, {d.year}")
    return True


def norm(v):
    s = str(v).strip().replace(",", "").replace("$", "")
    try:
        f = float(s)
        return str(int(f)) if f == int(f) else str(f)
    except ValueError:
        return re.sub(r"\s+", " ", s).lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feature", default="../../feature.json")
    a = ap.parse_args()
    problems = []
    start = run_start()
    if start is None:
        problems.append("run-log.md is missing or has no events; the run start is unknown")

    for f in ("sources.md", "facts.md"):
        if not os.path.exists(f):
            problems.append(f"{f} is missing")
    if problems and not os.path.exists("facts.md"):
        return report(problems)

    sources, ok_ids, by_link = {}, set(), {}
    for line in open("sources.md"):
        if not ROW.match(line):
            continue
        c = cells(line)
        if len(c) < 6:
            problems.append(f"sources.md {c[0]}: expected 7 columns (ID, Resource, Link or path, Tool, Read at, OK, Notes)")
            continue
        sid, res, link, tool, read_at, ok = c[:6]
        sources[sid] = c
        for name, val in (("Resource", res), ("Link or path", link), ("Tool", tool)):
            if not val:
                problems.append(f"sources.md {sid}: {name} is empty")
        t = parse_ts(read_at)
        if t is None:
            problems.append(f"sources.md {sid}: Read at {read_at!r} is not a UTC time like 2026-11-10T15:02Z")
        elif start and t < start - datetime.timedelta(minutes=1):
            problems.append(f"sources.md {sid}: read at {read_at}, before this run started ({start:%Y-%m-%dT%H:%MZ}); re-read it this run")
        by_link.setdefault(link, []).append((t, ok.lower(), sid))
        if ok.lower() == "yes":
            ok_ids.add(sid)
    for link, reads in by_link.items():
        reads.sort(key=lambda r: r[0] or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc))
        if reads[-1][1] != "yes":
            problems.append(f"sources.md {reads[-1][2]}: the latest read of {link} is not OK; the run should have stopped (SKILL.md stop rule)")

    feature = None
    if os.path.exists(a.feature):
        feature = json.load(open(a.feature))
    facts, seen = [], set()
    for line in open("facts.md"):
        if ROW.match(line) and line.startswith("| F-"):
            facts.append(cells(line))
    if not facts:
        problems.append("facts.md has no F- rows")
    ids = {c[0] for c in facts}
    values = {c[0]: c[2] for c in facts if len(c) > 2}
    for c in facts:
        if len(c) < 5:
            problems.append(f"facts.md {c[0]}: expected 6 columns (ID, Fact, Value, Kind, Source, Notes)")
            continue
        fid, fact, value, kind, src = c[:5]
        notes = c[5] if len(c) > 5 else ""
        if fid in seen:
            problems.append(f"facts.md {fid}: duplicate ID")
        seen.add(fid)
        if not value:
            problems.append(f"facts.md {fid}: Value is empty")
        if kind == "read":
            refs = re.findall(r"S-\d+", src)
            if not refs:
                problems.append(f"facts.md {fid}: kind read needs S- source IDs")
            for r in refs:
                if r not in sources:
                    problems.append(f"facts.md {fid}: source {r} is not in sources.md")
                elif r not in ok_ids:
                    problems.append(f"facts.md {fid}: source {r} was not read OK")
        elif kind == "computed":
            m = re.match(r"([\w.-]+\.json)#([\w.]+)$", src)
            if not m:
                problems.append(f"facts.md {fid}: kind computed needs <file>.json#<dot.path>, got {src!r}")
            elif not os.path.exists(m.group(1)):
                problems.append(f"facts.md {fid}: {m.group(1)} does not exist")
            else:
                got, found = resolve(json.load(open(m.group(1))), m.group(2))
                if not found:
                    problems.append(f"facts.md {fid}: {src} does not resolve")
                elif norm(got) != norm(value):
                    problems.append(f"facts.md {fid}: Value {value!r} but {src} is {got!r}")
        elif kind == "derived":
            refs = re.findall(r"F-\d+", src)
            if not refs:
                problems.append(f"facts.md {fid}: kind derived needs F- input IDs")
            for r in refs:
                if r not in ids:
                    problems.append(f"facts.md {fid}: input {r} is not in facts.md")
            fm = re.search(r"formula:\s*([^;]+)", notes, re.I)
            if "formula" not in notes.lower():
                problems.append(f"facts.md {fid}: kind derived needs 'formula:' in Notes")
            elif fm and "(manual)" not in notes.lower().split("formula")[1][:12]:
                expr = fm.group(1).strip()
                if re.fullmatch(r"[F\-\d\s.+*/()]+", expr):
                    try:
                        val = eval(re.sub(r"F-\d+", lambda m: f"({num(values.get(m.group(0)))})", expr), {"__builtins__": {}})
                        want = float(re.search(r"-?\d+(?:\.\d+)?", value.replace(",", "")).group(0))
                        if abs(val - want) > max(0.01 * abs(want), 1e-9):
                            problems.append(f"facts.md {fid}: formula {expr} gives {val:g}, Value is {value}; recompute after any change to its inputs")
                    except (TypeError, ValueError, AttributeError, ZeroDivisionError, SyntaxError):
                        problems.append(f"facts.md {fid}: formula {expr} does not evaluate from its inputs' values")
                else:
                    problems.append(f"facts.md {fid}: formula {expr!r} is not plain arithmetic over F- IDs; write 'formula (manual): ...' for the Gate 1 grader")
        elif kind == "ruling":
            m = re.match(r"feature\.json#([\w.]+)$", src)
            if m:
                got, found = resolve(feature, m.group(1)) if feature is not None else (None, False)
                if feature is None:
                    problems.append(f"facts.md {fid}: {a.feature} not found")
                elif not found:
                    problems.append(f"facts.md {fid}: {src} does not resolve")
                elif not ruling_matches(got, value):
                    problems.append(f"facts.md {fid}: Value {value!r} but {src} is {got!r}")
            elif not re.match(r"(?:Gate \d|Step 0), \d{4}-\d{2}-\d{2}", src):
                problems.append(f"facts.md {fid}: kind ruling needs feature.json#<path>, 'Gate <n>, YYYY-MM-DD' or 'Step 0, YYYY-MM-DD'")
        else:
            problems.append(f"facts.md {fid}: kind {kind!r} is not read, computed, derived or ruling")

    if os.path.exists("tickets.json"):
        for k, v in json.load(open("tickets.json")).items():
            for field in ("priority", "labels", "status", "status_category", "rounds", "outside_round", "read_at"):
                if field not in v:
                    problems.append(f"tickets.json {k}: missing {field}")
            t = parse_ts(v.get("read_at", ""))
            if t is None:
                problems.append(f"tickets.json {k}: read_at is not a UTC time")
            elif start and t < start - datetime.timedelta(minutes=1):
                problems.append(f"tickets.json {k}: read at {v['read_at']}, before this run started; re-read Jira")
    return report(problems, len(sources), len(facts))


def report(problems, n_sources=0, n_facts=0):
    print(f"check_facts.py: {n_sources} sources, {n_facts} facts, {len(problems)} problem(s)")
    for p in problems:
        print(" -", p)
    print("PASS" if not problems else "FAIL")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
