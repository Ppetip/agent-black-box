# SPDX-License-Identifier: GPL-3.0-only
"""Compare supplied local workflow scenarios against caller-provided expectations."""
import argparse
import copy
import json
from pathlib import Path
from app import ACTIONS
from workflow import planner, prepare_inputs, run_workflow


def compare_workflows(data, agent=planner):
    if (not isinstance(data, dict) or not {"order", "scenarios"} <= set(data)
            or set(data) - {"order", "scenarios", "max_steps"}):
        raise ValueError("input requires order, scenarios and optional max_steps")
    data = copy.deepcopy(data)
    scenarios = data["scenarios"]
    if not isinstance(scenarios, list) or not 1 <= len(scenarios) <= 100:
        raise ValueError("scenarios must contain 1 to 100 entries")
    prepared, identifiers = [], set()
    for scenario in scenarios:
        if not isinstance(scenario, dict) or set(scenario) != {"id", "policy_results", "expected_action"}:
            raise ValueError("each scenario requires only id, policy_results and expected_action")
        identifier, expected = scenario["id"], scenario["expected_action"]
        if not isinstance(identifier, str) or not identifier.strip() or identifier in identifiers:
            raise ValueError("scenario IDs must be unique nonempty strings")
        identifiers.add(identifier)
        if expected is not None and (not isinstance(expected, str) or expected not in ACTIONS):
            raise ValueError("expected_action must be refund, deny, escalate or null for step-limit")
        order, queue, bound = prepare_inputs(data["order"], scenario["policy_results"], data.get("max_steps", 5))
        prepared.append((identifier, expected, order, queue, bound))
    # All inputs and labels are owned and validated before the first trusted callback.
    results = []
    for identifier, expected, order, queue, bound in prepared:
        result = run_workflow(order, queue, agent=agent, max_steps=bound)
        actions = [event["action"] for event in result["trace"]]
        if not results:
            baseline_action, baseline_actions, baseline_calls = result["final_action"], actions, result["tool_calls"]
        results.append({"id": identifier, "expected_action": expected,
                        "matched_expectation": result["final_action"] == expected,
                        "comparison_to_first": {
                            "final_action_changed": result["final_action"] != baseline_action,
                            "action_sequence_changed": actions != baseline_actions,
                            "tool_calls_delta": result["tool_calls"] - baseline_calls},
                        "workflow": result})
    matched = sum(item["matched_expectation"] for item in results)
    return {"mode": "local-scenario-comparison", "baseline_id": results[0]["id"],
            "evaluated": len(results), "matched": matched, "match_rate": matched / len(results),
            "scenarios": results,
            "limitation": "Matches reflect supplied expectations, not independently verified ground truth. Changing response queues compares simulated paths, not formal causality or real-model quality. Each run restarts engine state; trusted custom callbacks may retain their own state or side effects and are not sandboxed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Authorized JSON with order and labeled scenarios")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        result = compare_workflows(data)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
