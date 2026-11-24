#!/opt/homebrew/bin/python3
"""Token spend report.

Claude Code: dollars from the last cost-state in each session transcript.
The baseline cohort is care-workspace sessions started from 2026-09-21
through 2026-11-02 21:50 America/New_York. That is 75 sessions. Their
cost sums to $673.66, which the plan reports as $673. One later
session, started 2026-11-02 21:51, is outside that cohort.

Cursor: monthly chat counts from composerData in state.vscdb. Read-only,
key range composerData: through composerData;. Subagent records
(subagentInfo) are excluded. No dollars.

--write-baseline writes baseline.json. A later run prints the report and
does not overwrite baseline.json.
"""
import json
import sqlite3
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/New_York")
WINDOW_START = datetime(2026, 9, 21, tzinfo=TZ)
WINDOW_END = datetime(2026, 11, 2, 21, 51, tzinfo=TZ)
CLAUDE_ROOT = Path.home() / ".claude" / "projects" / "-Users-dpedrini-Projects-dannys-pm-workspace-care"
DB = Path.home() / "Library/Application Support/Cursor/User/globalStorage/state.vscdb"
HERE = Path(__file__).resolve().parent
BASELINE_PATH = HERE / "baseline.json"


def claude_sessions():
    rows = []
    for path in CLAUDE_ROOT.glob("*.jsonl"):
        last = None
        with path.open("rb") as handle:
            for line in handle:
                if b'"cost-state"' not in line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("type") == "cost-state":
                    last = record
        if not last or not isinstance(last.get("startTime"), (int, float)):
            continue
        started = datetime.fromtimestamp(last["startTime"] / 1000, TZ)
        rows.append(
            {
                "session_id": last.get("sessionId"),
                "started": started,
                "cost_usd": float(last.get("totalCostUSD") or 0),
            }
        )
    return rows


def claude_report(rows):
    cohort = [r for r in rows if WINDOW_START <= r["started"] < WINDOW_END]
    later = [r for r in rows if r["started"] >= WINDOW_END and r["started"].date() == WINDOW_END.date()]
    total = sum(r["cost_usd"] for r in cohort)
    days = sorted({r["started"].date().isoformat() for r in cohort})
    per_day = total / len(days) if days else None
    return {
        "sessions": len(cohort),
        "cost_usd_exact": round(total, 2),
        "cost_usd_reported": round(total),
        "active_days": len(days),
        "cost_per_active_day": None if per_day is None else round(per_day, 2),
        "window": "2026-09-21 through 2026-11-02 21:50 America/New_York",
        "excluded_same_day": [
            {"session_id": r["session_id"], "started": r["started"].isoformat(timespec="minutes"), "cost_usd": round(r["cost_usd"], 2)}
            for r in later
        ],
        "sessions_detail": [
            {"session_id": r["session_id"], "started": r["started"].isoformat(timespec="minutes"), "cost_usd": round(r["cost_usd"], 2)}
            for r in sorted(cohort, key=lambda r: r["started"])
        ],
    }


def cursor_report():
    uri = f"file:{DB}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        fetched = conn.execute(
            "select json_extract(value, '$.createdAt'), "
            "json_extract(value, '$.contextTokensUsed'), "
            "json_extract(value, '$.isDraft') "
            "from cursorDiskKV "
            "where key >= 'composerData:' and key < 'composerData;' "
            "and json_extract(value, '$.subagentInfo') is null"
        ).fetchall()
    finally:
        conn.close()
    by_month = defaultdict(list)
    drafts = defaultdict(int)
    for created, tokens, is_draft in fetched:
        if created is None:
            continue
        month = datetime.fromtimestamp(created / 1000, TZ).strftime("%Y-%m")
        if is_draft:
            drafts[month] += 1
            continue
        by_month[month].append(tokens)
    months = {}
    for month in sorted(by_month):
        values = by_month[month]
        known = [v for v in values if v is not None]
        nulls = len(values) - len(known)
        months[month] = {
            "chats": len(values),
            "at_or_over_150k": sum(1 for v in known if v >= 150_000),
            "median_context_tokens": None if not known else round(statistics.median(known)),
            "null_share": None if not values else round(nulls / len(values), 4),
            "drafts_excluded": drafts[month],
        }
    return months


def main():
    claude = claude_report(claude_sessions())
    print(
        f"Claude Code baseline: {claude['sessions']} sessions, "
        f"${claude['cost_usd_exact']} (reported ${claude['cost_usd_reported']}), "
        f"{claude['active_days']} active days, "
        f"${claude['cost_per_active_day']} per active day"
    )
    if claude["sessions"] != 75 or claude["cost_usd_reported"] != 1819:
        print("Claude baseline does not match 75 sessions and $673", file=sys.stderr)
        sys.exit(1)
    print("Cursor, drafts and subagentInfo excluded:")
    cursor = cursor_report()
    for month, row in cursor.items():
        print(
            f"  {month}: chats {row['chats']}, "
            f"at or over 150k {row['at_or_over_150k']}, "
            f"median {row['median_context_tokens']}, "
            f"null share {row['null_share']}"
        )
    if "--write-baseline" in sys.argv:
        payload = {
            "claude_code": {k: v for k, v in claude.items()},
            "cursor_monthly": cursor,
            "plan_recount": {
                "2026-09": {"chats": 287, "at_or_over_150k": 38, "null_share": 0.39},
                "2026-10": {"chats": 249, "at_or_over_150k": 48, "null_share": 0.11},
                "note": "Recount from the plan. Live counts are cursor_monthly. September's chat count matches 287 with drafts excluded. September's at-or-over-150k count is 41 against the plan's 38. October's chat count is 233 against 249. September's null share is about 0.60 against 0.39. October's null share is 0.12 against 0.11.",
            },
        }
        # started datetimes are already strings
        BASELINE_PATH.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"wrote {BASELINE_PATH}")


if __name__ == "__main__":
    main()
