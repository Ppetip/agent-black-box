"""Run independent synthetic failure cases; never tune on final-test outcomes."""
import argparse
import copy
import json
from pathlib import Path
from app import demo, diagnose, scripted_agent, prepare_diagnosis


def evaluate_suite(cases, agent=scripted_agent):
    if not isinstance(cases, list) or not cases or len(cases) > 200:
        raise ValueError("provide between 1 and 200 cases")
    cases = copy.deepcopy(cases)
    ids = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"] or case["id"] in ids:
            raise ValueError("unique case IDs required")
        ids.add(case["id"])
        case["trace"], case["interventions"] = prepare_diagnosis(case.get("trace"), case.get("interventions"))
    results = [{"id": c["id"], **diagnose(copy.deepcopy(c["trace"]), copy.deepcopy(c["interventions"]), agent)} for c in cases]
    failed = [r for r in results if not r["baseline"]["passed"]]
    repaired = sum(any(t["repairs_failure"] for t in r["interventions"]) for r in failed)
    return {"cases": len(results), "baseline_failures": len(failed), "repairable_failures": repaired,
            "repair_rate_among_failures": repaired / len(failed) if failed else None,
            "results": results, "limitation": "Candidate-intervention coverage on synthetic cases, not causal proof or held-out production performance."}


def fixtures():
    cases = []
    for age, expected in ((45, "deny"), (10, "refund"), (91, "deny")):
        trace, changes = demo()
        trace["order"]["age_days"] = age
        trace["expected_action"] = expected
        cases.append({"id": f"synthetic-age-{age}", "trace": trace, "interventions": changes})
    return cases


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path)
    a = p.parse_args()
    print(json.dumps(evaluate_suite(json.loads(a.input.read_text(encoding="utf-8")) if a.input else fixtures()), indent=2))


if __name__ == "__main__":
    main()
