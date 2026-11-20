#!/usr/bin/env python3
"""
Delivery forecast scheduler for the Outbound Fulfillment domain roadmap.

Resource-constrained greedy scheduler that assigns delivery months to
stack-ranked initiatives based on capacity, dependencies, and parallelism.

Usage:
    python3 delivery_forecast.py --config config.json
    echo '{ ... }' | python3 delivery_forecast.py --stdin

Input JSON schema:
{
  "capacity": {
    "engineers": 6,
    "utilization": 0.8,
    "start_date": "2026-07-01",
    "end_date": "2026-12-31"
  },
  "initiatives": [
    {
      "rank": 1,
      "name": "Polybagger Printer Integration",
      "eng_weeks": 4,
      "goal": "Cost-to-Serve",
      "annual_impact": "$154K",
      "dependencies": [],
      "team_size": 2,
      "external": false,
      "fixed_delivery": null
    }
  ]
}

Output: JSON with delivery forecasts, capacity utilization, and warnings.
"""

import json
import sys
import argparse
import math
from datetime import date, timedelta
from typing import Optional


def parse_date(s: str) -> date:
    return date.fromisoformat(s)


def delivery_label(end_date: date, start_date: date) -> str:
    """Specific month name for the upcoming quarter (first full quarter of
    post-MVP work), 'QX YYYY' for any quarter beyond that."""
    start_q = (start_date.month - 1) // 3 + 1
    start_year = start_date.year
    upcoming_q = start_q
    upcoming_year = start_year

    end_q = (end_date.month - 1) // 3 + 1
    end_year = end_date.year

    if end_year == upcoming_year and end_q == upcoming_q:
        return end_date.strftime("%B")
    else:
        return f"Q{end_q} {end_year}"


def default_team_size(eng_weeks: int, max_capacity: float) -> int:
    """Heuristic: small items get 2 engineers, medium 3, large get up to max."""
    if eng_weeks <= 4:
        return min(2, int(max_capacity))
    elif eng_weeks <= 12:
        return min(3, int(max_capacity))
    else:
        return min(4, int(max_capacity))


def schedule(config: dict) -> dict:
    cap = config["capacity"]
    engineers = cap["engineers"]
    utilization = cap["utilization"]
    effective_capacity = engineers * utilization
    start_date = parse_date(cap["start_date"])
    end_date = parse_date(cap.get("end_date", "2026-12-31"))

    total_calendar_weeks = max(1, (end_date - start_date).days // 7)
    total_available_eng_weeks = effective_capacity * total_calendar_weeks

    initiatives = config["initiatives"]

    # Build a weekly capacity grid (how many engineers are free each week)
    grid_weeks = total_calendar_weeks + 52  # buffer for overflow
    capacity_used = [0.0] * grid_weeks  # engineers committed per week

    def week_index(d: date) -> int:
        return max(0, (d - start_date).days // 7)

    def index_to_date(idx: int) -> date:
        return start_date + timedelta(weeks=idx)

    def find_earliest_start(needed_engineers: float, duration_weeks: int,
                            earliest: int) -> Optional[int]:
        """Find the earliest contiguous block where needed_engineers are free."""
        candidate = earliest
        while candidate + duration_weeks <= grid_weeks:
            fits = True
            for w in range(candidate, candidate + duration_weeks):
                if capacity_used[w] + needed_engineers > effective_capacity + 0.01:
                    fits = False
                    candidate = w + 1
                    break
            if fits:
                return candidate
        return None

    def reserve_capacity(start_week: int, duration_weeks: int,
                         needed_engineers: float):
        for w in range(start_week, start_week + duration_weeks):
            capacity_used[w] += needed_engineers

    # Index initiatives by name for dependency lookup
    results = {}
    scheduled = {}  # name -> {start_week, end_week, end_date}

    # Process in rank order
    sorted_initiatives = sorted(initiatives, key=lambda x: x["rank"])

    warnings = []

    for init in sorted_initiatives:
        name = init["name"]
        eng_weeks = init["eng_weeks"]
        deps = init.get("dependencies", [])
        external = init.get("external", False)
        fixed_delivery = init.get("fixed_delivery")
        team_size_override = init.get("team_size")

        # External work (done by another team) — doesn't consume our capacity
        if external:
            if fixed_delivery:
                # Parse fixed delivery as a month or quarter
                results[name] = {
                    "rank": init["rank"],
                    "name": name,
                    "eng_weeks": eng_weeks,
                    "delivery": fixed_delivery,
                    "start_date": None,
                    "end_date": None,
                    "team_size": 0,
                    "duration_weeks": eng_weeks,
                    "external": True,
                    "note": "Work owned by external team; does not consume domain eng capacity"
                }
                # For dependency tracking, estimate when it's done
                # Try to parse fixed_delivery as a date hint
                scheduled[name] = {
                    "start_week": 0,
                    "end_week": eng_weeks,
                    "end_date": None
                }
            continue

        # Determine team size
        if team_size_override:
            team_size = min(team_size_override, effective_capacity)
        else:
            team_size = default_team_size(eng_weeks, effective_capacity)

        duration_weeks = max(1, math.ceil(eng_weeks / team_size))

        # Earliest start = max(start_date, all dependencies complete)
        earliest_week = 0
        for dep in deps:
            if dep in scheduled:
                dep_end = scheduled[dep]["end_week"]
                earliest_week = max(earliest_week, dep_end)
            else:
                warnings.append(
                    f"{name}: dependency '{dep}' not found in scheduled initiatives"
                )

        # Find capacity slot
        slot = find_earliest_start(team_size, duration_weeks, earliest_week)

        if slot is None:
            warnings.append(
                f"{name}: cannot fit within capacity grid ({eng_weeks} eng-wks, "
                f"team size {team_size})"
            )
            results[name] = {
                "rank": init["rank"],
                "name": name,
                "eng_weeks": eng_weeks,
                "delivery": "Overflow — exceeds available capacity",
                "team_size": team_size,
                "duration_weeks": duration_weeks,
                "external": False,
                "warning": "Could not schedule within available capacity"
            }
            continue

        reserve_capacity(slot, duration_weeks, team_size)

        init_start = index_to_date(slot)
        init_end = index_to_date(slot + duration_weeks)
        label = delivery_label(init_end, start_date)

        scheduled[name] = {
            "start_week": slot,
            "end_week": slot + duration_weeks,
            "end_date": init_end
        }

        results[name] = {
            "rank": init["rank"],
            "name": name,
            "eng_weeks": eng_weeks,
            "team_size": team_size,
            "duration_weeks": duration_weeks,
            "start_date": init_start.isoformat(),
            "end_date": init_end.isoformat(),
            "delivery": label,
            "external": False
        }

    # Capacity summary
    total_scheduled = sum(
        r["eng_weeks"] for r in results.values() if not r.get("external")
    )
    h2_scheduled = sum(
        r["eng_weeks"] for r in results.values()
        if not r.get("external")
        and r.get("end_date")
        and r["end_date"] <= end_date.isoformat()
    )

    # Per-month and per-quarter breakdown
    months = {}
    quarters = {}
    for w in range(total_calendar_weeks):
        d = index_to_date(w)
        m_key = d.strftime("%Y-%m")
        q_num = (d.month - 1) // 3 + 1
        q_key = f"{d.year}-Q{q_num}"

        if m_key not in months:
            months[m_key] = {"available": 0.0, "used": 0.0}
        months[m_key]["available"] += effective_capacity
        months[m_key]["used"] += capacity_used[w]

        if q_key not in quarters:
            quarters[q_key] = {"available": 0.0, "used": 0.0}
        quarters[q_key]["available"] += effective_capacity
        quarters[q_key]["used"] += capacity_used[w]

    # Round for readability
    for v in months.values():
        v["available"] = round(v["available"], 1)
        v["used"] = round(v["used"], 1)
        v["utilization_pct"] = round(v["used"] / v["available"] * 100, 1) if v["available"] > 0 else 0
    for v in quarters.values():
        v["available"] = round(v["available"], 1)
        v["used"] = round(v["used"], 1)
        v["utilization_pct"] = round(v["used"] / v["available"] * 100, 1) if v["available"] > 0 else 0

    output = {
        "capacity_assumptions": {
            "engineers": engineers,
            "utilization": utilization,
            "effective_eng_weeks_per_week": effective_capacity,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_calendar_weeks": total_calendar_weeks,
            "total_available_eng_weeks": round(total_available_eng_weeks, 1)
        },
        "schedule": sorted(results.values(), key=lambda x: x["rank"]),
        "capacity_by_month": dict(sorted(months.items())),
        "capacity_by_quarter": dict(sorted(quarters.items())),
        "summary": {
            "total_eng_weeks_scheduled": total_scheduled,
            "h2_eng_weeks_scheduled": h2_scheduled,
            "h2_available_eng_weeks": round(total_available_eng_weeks, 1),
            "h2_utilization_pct": round(h2_scheduled / total_available_eng_weeks * 100, 1) if total_available_eng_weeks > 0 else 0,
            "overflow_initiatives": [
                r["name"] for r in results.values()
                if r.get("end_date") and r["end_date"] > end_date.isoformat()
            ]
        },
        "warnings": warnings
    }

    return output


def main():
    parser = argparse.ArgumentParser(description="Delivery forecast scheduler")
    parser.add_argument("--config", help="Path to config JSON file")
    parser.add_argument("--stdin", action="store_true", help="Read config from stdin")
    args = parser.parse_args()

    if args.stdin:
        config = json.load(sys.stdin)
    elif args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        parser.error("Provide --config <file> or --stdin")

    result = schedule(config)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
