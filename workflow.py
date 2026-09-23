# SPDX-License-Identifier: GPL-3.0-only
"""Bounded local policy workflow. Tool results are supplied data, never live calls."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from app import ACTIONS, canonical, scripted_agent


def planner(context):
    observations = context["observations"]
    if "policy" not in observations:
        return "get_policy"
    policy = observations["policy"]
    if isinstance(policy, dict) and policy.get("status") == "timeout" and context["tool_calls"] < 2:
        return "get_policy"
    return scripted_agent(context)


def run_workflow(order, policy_results, agent=planner, max_steps=5):
    if (not isinstance(order, dict) or set(order) != {"age_days"}
            or type(order["age_days"]) is not int or order["age_days"] < 0):
        raise ValueError("order must contain only nonnegative integer age_days")
    if not isinstance(policy_results, list) or len(policy_results) > 1000:
        raise ValueError("policy_results must be an array of at most 1000 JSON values")
    if type(max_steps) is not int or not 1 <= max_steps <= 1000:
        raise ValueError("max_steps must be an integer from 1 to 1000")
    order, policy_results = copy.deepcopy((order, policy_results))
    canonical(policy_results)  # Preflight the entire queue before invoking callbacks.
    observations, trace, calls = {}, [], 0
    status, final_action = "step-limit", None
    for index in range(max_steps):
        context = {"order":copy.deepcopy(order),"observations":copy.deepcopy(observations),"tool_calls":calls}
        digest = hashlib.sha256(canonical(context).encode()).hexdigest()
        action = agent(copy.deepcopy(context))
        if not isinstance(action, str) or action not in ACTIONS | {"get_policy"}:
            raise ValueError("unknown workflow action")
        event = {"step":index,"action":action,"input_sha256":digest}
        if action == "get_policy":
            observation = copy.deepcopy(policy_results[calls]) if calls < len(policy_results) else {"status":"exhausted"}
            calls += 1
            observations["policy"] = observation
            event.update(tool_call_id=f"policy-{calls}",tool_input=copy.deepcopy(order),observation=copy.deepcopy(observation))
            trace.append(event)
        else:
            trace.append(event)
            final_action = action
            status = "escalated" if action == "escalate" else "decided"
            break
    return {"mode":"local-simulation","status":status,"final_action":final_action,"tool_calls":calls,
            "steps":len(trace),"trace":trace,"engine_external_side_effects":False,
            "limitation":"The planner generates the next action from prior observations; each get_policy consumes one supplied result. No external tools, refund execution or live-model quality measurement. Custom Python callbacks are trusted caller code, not OS-sandboxed; the step limit does not interrupt a hanging callback."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True,help="Authorized JSON with order, policy_results and optional max_steps")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or not {"order","policy_results"} <= set(data) or set(data) - {"order","policy_results","max_steps"}:
        parser.error("input must contain order, policy_results and optional max_steps")
    print(json.dumps(run_workflow(data["order"],data["policy_results"],max_steps=data.get("max_steps",5)),indent=2))

if __name__ == "__main__":
    main()
