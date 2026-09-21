# SPDX-License-Identifier: GPL-3.0-only
"""Ordered observation/decision replay with prefix-only agent visibility."""
import copy
import hashlib
import json
from app import ACTIONS, canonical, scripted_agent


def validate(events):
    if not isinstance(events, list) or not 1 <= len(events) <= 1000:
        raise ValueError("provide 1 to 1000 ordered events")
    ids = set()
    for event in events:
        if not isinstance(event, dict) or not isinstance(event.get("id"), str) or not event["id"] or event["id"] in ids:
            raise ValueError("unique event IDs required")
        ids.add(event["id"])
        if event.get("type") == "observation":
            if set(event) != {"id", "type", "name", "value"} or not isinstance(event["name"], str) or not event["name"]:
                raise ValueError("observation requires name and value")
        elif event.get("type") == "decision":
            if set(event) != {"id", "type", "expected_action"} or event["expected_action"] not in ACTIONS:
                raise ValueError("decision requires a valid expected_action")
        else:
            raise ValueError("unknown event type")
    canonical(events)


def replay_events(order, events, agent=scripted_agent, replacements=None):
    """Replay a fixed recorded sequence; actions do not synthesize future tools."""
    validate(events)
    if not isinstance(order, dict) or type(order.get("age_days")) is not int or order["age_days"] < 0:
        raise ValueError("order.age_days must be a nonnegative integer")
    replacements = {} if replacements is None else replacements
    observation_ids = {e["id"] for e in events if e["type"] == "observation"}
    if not isinstance(replacements, dict) or not set(replacements) <= observation_ids:
        raise ValueError("replacement must name an observation event ID")
    observations, decisions = {}, []
    for event in events:
        if event["type"] == "observation":
            observations[event["name"]] = copy.deepcopy(replacements.get(event["id"], event["value"]))
        else:
            context = {"order": copy.deepcopy(order), "observations": copy.deepcopy(observations)}
            digest = hashlib.sha256(canonical(context).encode()).hexdigest()
            action = agent(context)
            if action not in ACTIONS:
                raise ValueError("invalid agent action")
            decisions.append({"event_id": event["id"], "action": action,
                              "passed": action == event["expected_action"], "input_sha256": digest})
    return {"decisions": decisions, "limitation": "Fixed recorded sequence on synthetic data; no regenerated tool calls, production side effects, or causal proof."}


def demo():
    events = [{"id": "before", "type": "decision", "expected_action": "escalate"},
              {"id": "stale", "type": "observation", "name": "policy", "value": {"status": "ok", "refund_window_days": 90}},
              {"id": "after-stale", "type": "decision", "expected_action": "deny"},
              {"id": "fresh", "type": "observation", "name": "policy", "value": {"status": "ok", "refund_window_days": 30}},
              {"id": "after-fresh", "type": "decision", "expected_action": "deny"}]
    order = {"age_days": 45}
    return {"data": "synthetic-recorded-events", "baseline": replay_events(order, events),
            "intervened": replay_events(order, events, replacements={"stale": {"status": "ok", "refund_window_days": 30}})}

if __name__ == "__main__":
    print(json.dumps(demo(), indent=2))
