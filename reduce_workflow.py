# SPDX-License-Identifier: GPL-3.0-only
"""Bounded deletion reduction of supplied local workflow response queues."""
import argparse
import json
from pathlib import Path
from app import ACTIONS
from workflow import prepare_inputs, run_workflow


def reduce_failure(data):
    required = {"order", "policy_results", "expected_action"}
    if not isinstance(data, dict) or not required <= set(data) or set(data) - required - {"max_steps", "max_trials"}:
        raise ValueError("input requires order, policy_results, expected_action and optional max_steps/max_trials")
    expected = data["expected_action"]
    if expected is not None and (not isinstance(expected, str) or expected not in ACTIONS):
        raise ValueError("expected_action must be refund, deny, escalate or null")
    limit = data.get("max_trials", 100)
    if type(limit) is not int or not 1 <= limit <= 200:
        raise ValueError("max_trials must be an integer from 1 to 200, including the baseline run")
    order, queue, bound = prepare_inputs(data["order"], data["policy_results"], data.get("max_steps", 5))
    baseline = run_workflow(order, queue, max_steps=bound)
    kept, trials, attempts = list(range(len(queue))), 1, []
    current = baseline
    is_failure = baseline["final_action"] != expected
    index = 0
    if is_failure:
        while index < len(kept) and trials < limit:
            candidate = kept[:index] + kept[index + 1:]
            result = run_workflow(order, [queue[i] for i in candidate], max_steps=bound)
            trials += 1
            accepted = (result["status"], result["final_action"]) == (baseline["status"], baseline["final_action"])
            attempts.append({"removed_original_index": kept[index], "kept_original_indices": candidate,
                             "status": result["status"], "final_action": result["final_action"], "accepted": accepted})
            if accepted:
                kept, current, index = candidate, result, 0
            else:
                index += 1
    complete = index == len(kept) if is_failure else None
    return {"mode": "local-workflow-reduction", "expected_action": expected,
            "status": "not-a-failure" if not is_failure else "one-deletion-minimal" if complete else "trial-limit",
            "one_deletion_minimal": complete, "trials": trials, "max_trials": limit,
            "original_responses": len(queue), "retained_responses": len(kept),
            "kept_original_indices": kept, "removed_original_indices": [i for i in range(len(queue)) if i not in kept],
            "reduced_input": {"order": order, "policy_results": [queue[i] for i in kept],
                              "expected_action": expected, "max_steps": bound},
            "baseline": baseline, "reduced": current, "attempts": attempts,
            "limitation": "Built-in deterministic local planner only. Reduction preserves terminal status and final action, not the entire trace or failure cause. Single-response deletions preserve order but can change which simulated call consumes a response. One-deletion-minimal does not mean globally smallest or prove causality. Trial-limit means minimality remains unverified. Supplied expectations are not independently verified ground truth."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--reproducer-output", type=Path,
                        help="Save the reduced input to a new JSON file; existing files are never overwritten")
    args = parser.parse_args()
    try:
        result = reduce_failure(json.loads(args.input.read_text(encoding="utf-8-sig")))
        if args.reproducer_output is not None:
            # Serialize before opening; retain the caller's trial budget on rerun.
            reproducer = {**result["reduced_input"], "max_trials": result["max_trials"]}
            payload = json.dumps(reproducer, indent=2, allow_nan=False) + "\n"
            with args.reproducer_output.open("x", encoding="utf-8", newline="\n") as output:
                output.write(payload)
            result["reproducer_output"] = str(args.reproducer_output)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
