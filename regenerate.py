# SPDX-License-Identifier: GPL-3.0-only
"""Regenerate synthetic policy results inside a fixed recorded event plan."""
import copy
import json
from timeline import replay_events, validate

WINDOWS = {"standard": 30, "short": 14}

def regenerate(events):
    events = copy.deepcopy(events)
    validate(events)
    calls = {}
    for event in events:
        if event["type"] == "tool_call":
            inputs = event["input"]
            if (event["name"] != "policy" or set(inputs) != {"policy_tier"}
                    or not isinstance(inputs["policy_tier"], str) or inputs["policy_tier"] not in WINDOWS):
                raise ValueError("synthetic policy calls require a standard or short policy_tier")
            calls[event["id"]] = inputs["policy_tier"]
    generated = []
    for event in events:
        if event["type"] == "tool_result":
            event["value"] = {"status": "ok", "refund_window_days": WINDOWS[calls[event["call_id"]]]}
            generated.append(event["id"])
    return {"events": events, "regenerated_result_ids": generated}

def demo():
    events = [{"id":"call","type":"tool_call","name":"policy","input":{"policy_tier":"standard"}},
              {"id":"waiting","type":"decision","expected_action":"escalate"},
              {"id":"result","type":"tool_result","call_id":"call","value":{"status":"ok","refund_window_days":90}},
              {"id":"decision","type":"decision","expected_action":"deny"}]
    generated = regenerate(events)
    order = {"age_days":45}
    return {"data":"synthetic-policy-regeneration", "baseline":replay_events(order,events),
            "intervened":replay_events(order,generated["events"]), **generated,
            "limitation":"Built-in synthetic policy table, not live business policy. Result values are regenerated, but tool calls, inputs and result arrival order remain fixed. No action-dependent replanning or external tools."}

if __name__ == "__main__":
    print(json.dumps(demo(),indent=2))
