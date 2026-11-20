#!/usr/bin/env python3
"""
Feature Impact Sizing Calculator

Deterministic math engine for feature impact sizing.
Computes Low/Base/High scenarios from multiplicative factors.
ALL math goes through this script — the LLM never does calculations.

Model:  result = factor_1 × factor_2 × ... × factor_n
        Constants stay fixed; variable factors use scenario-specific values.

Usage:
    python sizing_calculator.py --input sizing_input.json
    python sizing_calculator.py --input sizing_input.json --output sizing_output.json
"""

from __future__ import annotations

import argparse
import json
import sys


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_currency(v: float) -> str:
    if v < 0:
        return f"-{fmt_currency(abs(v))}"
    if v >= 1_000_000:
        return f"${v:,.0f}"
    if v >= 1:
        return f"${v:,.2f}"
    if v >= 0.001:
        return f"${v:,.4f}"
    return f"${v:.6f}"


def fmt_value(v: float, unit: str) -> str:
    if unit == "$":
        return fmt_currency(v)
    if unit == "%":
        return f"{v * 100:.1f}%"
    if unit in ("units", "shipments", "errors", "packages"):
        return f"{v:,.0f} {unit}"
    if unit in ("hours", "minutes"):
        return f"{v:,.1f} {unit}"
    if unit in ("$/hr", "$/unit", "$/error", "$/shipment", "$/package"):
        return fmt_currency(v)
    return f"{v:,.4f}"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(data: dict) -> list:
    errors = []

    if "feature_name" not in data:
        errors.append("Missing 'feature_name'")

    if "factors" not in data or not isinstance(data.get("factors"), list):
        errors.append("Missing or invalid 'factors' array")
        return errors

    if len(data["factors"]) == 0:
        errors.append("'factors' array is empty — need at least one factor")
        return errors

    for i, f in enumerate(data["factors"]):
        label = f.get("name", f"factor[{i}]")
        if "name" not in f:
            errors.append(f"Factor {i}: missing 'name'")
        if f.get("is_constant"):
            if "value" not in f:
                errors.append(f"Factor '{label}': constant missing 'value'")
        else:
            for s in ("low", "base", "high"):
                if s not in f:
                    errors.append(f"Factor '{label}': variable missing '{s}' value")

    return errors


# ---------------------------------------------------------------------------
# Sanity check (Must-Fix #1: catch arithmetic errors in constants)
# ---------------------------------------------------------------------------

def check_derivation(factor: dict, tolerance_rel: float = 0.05, tolerance_abs: float = 1000.0) -> dict | None:
    """
    Verify a constant factor's `value` matches its `derivation` field.

    Two derivation methods supported:

    method="sum":
        components: [{"name": "...", "value": 12345}, ...]
        → expected_value = sum(components.value)

    method="formula":
        formula: human-readable string (for display)
        compute: "a / b * c"  — eval'd against inputs dict
        inputs: {"a": 100, "b": 2, "c": 5}
        → expected_value = eval(compute, inputs)

    Returns None if no derivation present.
    Returns dict with {"status": "PASS"|"FAIL", "expected", "actual", "delta_pct", "detail"}.
    """
    if not factor.get("is_constant"):
        return None
    deriv = factor.get("derivation")
    if not deriv:
        return None

    method = deriv.get("method")
    actual = factor["value"]
    expected = None
    detail = ""

    if method == "sum":
        components = deriv.get("components", [])
        if not components:
            return {"status": "FAIL", "expected": None, "actual": actual,
                    "delta_pct": None, "detail": "method=sum but no components provided"}
        expected = sum(c.get("value", 0) for c in components)
        breakdown = " + ".join(f"{c.get('name','?')} ${c.get('value',0):,.0f}" for c in components)
        detail = f"sum of components: {breakdown}"

    elif method == "formula":
        compute = deriv.get("compute")
        inputs = deriv.get("inputs", {})
        if not compute or not inputs:
            return {"status": "FAIL", "expected": None, "actual": actual,
                    "delta_pct": None, "detail": "method=formula requires 'compute' and 'inputs'"}
        try:
            # Restricted eval — only the inputs are available as variables
            expected = float(eval(compute, {"__builtins__": {}}, dict(inputs)))
        except Exception as e:
            return {"status": "FAIL", "expected": None, "actual": actual,
                    "delta_pct": None, "detail": f"formula eval failed: {e}"}
        formula_display = deriv.get("formula", compute)
        inputs_str = ", ".join(f"{k}={v}" for k, v in inputs.items())
        detail = f"formula '{formula_display}' with inputs ({inputs_str})"

    else:
        return {"status": "FAIL", "expected": None, "actual": actual,
                "delta_pct": None,
                "detail": f"unknown derivation method '{method}' (must be 'sum' or 'formula')"}

    delta = abs(actual - expected)
    delta_pct = delta / max(abs(expected), 1.0)
    within_tolerance = (delta_pct <= tolerance_rel) or (delta <= tolerance_abs)

    return {
        "status": "PASS" if within_tolerance else "FAIL",
        "expected": round(expected, 2),
        "actual": round(actual, 2),
        "delta": round(delta, 2),
        "delta_pct": round(delta_pct * 100, 2),
        "detail": detail,
    }


def run_sanity_checks(data: dict) -> list:
    """
    Returns a list of sanity check results, one per constant factor with a `derivation` field.
    Strict-mode enforcement (blocking on FAIL) happens in `run_sizing()`, not here.
    """
    results = []
    for f in data.get("factors", []):
        res = check_derivation(f)
        if res is None:
            continue
        results.append({
            "factor": f["name"],
            "value": f["value"],
            **res,
        })
    return results


# ---------------------------------------------------------------------------
# Scenario computation
# ---------------------------------------------------------------------------

def compute_scenario(
    scenario_name: str,
    factors: list,
    per_unit_divisor: float | None,
    per_unit_label: str,
) -> dict:
    steps = []
    result = 1.0
    factors_used = []

    steps.append(f"--- {scenario_name.upper()} SCENARIO ---")

    for f in factors:
        name = f["name"]
        unit = f.get("unit", "")

        if f.get("is_constant"):
            val = f["value"]
            source_note = f"  (from {f['source']})" if "source" in f else ""
            steps.append(f"  {name} = {fmt_value(val, unit)}{source_note}")
        else:
            val = f[scenario_name]
            steps.append(f"  {name} = {fmt_value(val, unit)}  ({scenario_name} scenario)")

        factors_used.append({"name": name, "value": val, "unit": unit})
        result *= val

    # Readable formula
    names_str = " × ".join(fu["name"] for fu in factors_used)
    values_str = " × ".join(fmt_value(fu["value"], fu["unit"]) for fu in factors_used)

    steps.append(f"")
    steps.append(f"  Formula: {names_str}")
    steps.append(f"        = {values_str}")
    steps.append(f"        = {fmt_currency(result)}")

    per_unit = None
    if per_unit_divisor and per_unit_divisor > 0:
        per_unit = result / per_unit_divisor
        steps.append(
            f"  Per-unit: {fmt_currency(result)} ÷ {per_unit_divisor:,.0f} {per_unit_label}"
            f" = {fmt_currency(per_unit)}"
        )

    return {
        "result": round(result, 2),
        "result_formatted": fmt_currency(round(result, 2)),
        "per_unit_result": round(per_unit, 4) if per_unit is not None else None,
        "per_unit_formatted": fmt_currency(round(per_unit, 4)) if per_unit is not None else None,
        "factors_used": factors_used,
        "calculation_steps": steps,
    }


# ---------------------------------------------------------------------------
# Main sizing logic
# ---------------------------------------------------------------------------

def run_sizing(data: dict, strict: bool = True) -> dict:
    errors = validate(data)
    if errors:
        return {"error": True, "validation_errors": errors}

    factors = data["factors"]
    per_unit_divisor = data.get("per_unit_divisor")
    per_unit_label = data.get("per_unit_label", "units")
    result_label = data.get("result_label", "Annual Impact")

    warnings = []

    # Sanity checks on constant derivations (Must-Fix #1)
    sanity_results = run_sanity_checks(data)
    sanity_failures = [r for r in sanity_results if r["status"] == "FAIL"]
    if sanity_failures and strict:
        return {
            "error": True,
            "sanity_check_failures": sanity_failures,
            "message": (
                "Constant factor derivation does not match declared value. "
                "Fix the JSON or run with --no-strict to override."
            ),
        }
    for r in sanity_results:
        if r["status"] == "FAIL":
            warnings.append(
                f"⚠️ SANITY CHECK FAIL — {r['factor']}: declared ${r['actual']:,.0f} "
                f"vs derived ${r['expected']:,.0f} (delta {r['delta_pct']}%). {r['detail']}"
            )

    # Sanity checks on variable factors
    for f in factors:
        if not f.get("is_constant") and f.get("unit") == "%":
            for s in ("low", "base", "high"):
                v = f.get(s, 0)
                if v > 1.0:
                    warnings.append(
                        f"⚠️ {f['name']} {s} = {v * 100:.0f}% (>{100}%). "
                        f"Percentages should be decimals (0.15 = 15%). Verify this is intentional."
                    )
        if not f.get("is_constant"):
            low, high = f.get("low", 0), f.get("high", 0)
            if low > high:
                warnings.append(
                    f"⚠️ {f['name']}: low ({low}) > high ({high}). "
                    f"Scenarios may be inverted."
                )

    scenarios = {}
    for s in ("low", "base", "high"):
        scenarios[s] = compute_scenario(s, factors, per_unit_divisor, per_unit_label)

    # Verify scenario ordering (low <= base <= high for savings)
    low_r = scenarios["low"]["result"]
    base_r = scenarios["base"]["result"]
    high_r = scenarios["high"]["result"]

    if not (low_r <= base_r <= high_r):
        warnings.append(
            f"Note: Scenario results are not in ascending order "
            f"(Low={fmt_currency(low_r)}, Base={fmt_currency(base_r)}, High={fmt_currency(high_r)}). "
            f"This can happen when factors interact — verify assumptions."
        )

    return {
        "feature_name": data.get("feature_name", ""),
        "metric_category": data.get("metric_category", ""),
        "result_label": result_label,
        "per_unit_label": per_unit_label,
        "scenarios": scenarios,
        "warnings": warnings,
        "sanity_checks": sanity_results,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Feature Impact Sizing Calculator — deterministic math engine"
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", help="Path to output JSON file (default: stdout)")
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Allow derivation mismatches as warnings instead of failing (default: strict).",
    )
    args = parser.parse_args()

    with open(args.input, "r") as fh:
        data = json.load(fh)

    result = run_sizing(data, strict=not args.no_strict)
    out = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(out)
        print(f"✅ Output written to {args.output}", file=sys.stderr)
    else:
        print(out)

    if result.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()
