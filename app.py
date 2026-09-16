"""Deterministic interventions for a support-agent sandbox. Python 3.11+."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ACTIONS = {"refund", "deny", "escalate"}

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

def validate(trace):
    if not isinstance(trace, dict) or trace.get("schema_version") != 1:
        raise ValueError("trace schema_version must be 1")
    if trace.get("expected_action") not in ACTIONS:
        raise ValueError("expected_action must be refund, deny, or escalate")
    order = trace.get("order", {})
    if not isinstance(order, dict) or type(order.get("age_days")) is not int or order["age_days"] < 0:
        raise ValueError("order.age_days must be a nonnegative integer")
    if not isinstance(trace.get("observations"), dict):
        raise ValueError("observations must be an object")
    return trace

def scripted_agent(trace):
    policy = trace["observations"].get("policy", {})
    if not isinstance(policy, dict) or policy.get("status") != "ok":
        return "escalate"
    limit = policy.get("refund_window_days")
    if type(limit) is not int or limit < 0:
        return "escalate"
    return "refund" if trace["order"]["age_days"] <= limit else "deny"

def ollama_agent(model):
    """Explicit opt-in; calls an existing local model, never downloads one."""
    if not model.strip():
        raise ValueError("model name required")
    def decide(trace):
        # Expected answer is deliberately withheld from the model.
        context = {k: trace[k] for k in ("order", "observations")}
        body = {"model": model, "stream": False, "format": "json",
                "options": {"temperature": 0, "num_predict": 80},
                "messages": [{"role": "system", "content":
                    'Decide a refund using the supplied policy. If unavailable or invalid, escalate. Return only JSON with action: refund, deny, or escalate.'},
                    {"role": "user", "content": canonical(context)}]}
        req = Request("http://127.0.0.1:11434/api/chat", data=canonical(body).encode(),
                      headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=120) as response:
            payload = json.load(response)
        action = json.loads(payload["message"]["content"]).get("action")
        if action not in ACTIONS:
            raise ValueError("model returned an invalid action")
        return action
    decide.engine = "local-llm"
    return decide

def replay(trace, agent=scripted_agent, intervention=None):
    changed = copy.deepcopy(validate(trace))
    if intervention:
        key, value = intervention
        if key not in changed["observations"]:
            raise ValueError("intervention names an unknown observation")
        changed["observations"][key] = copy.deepcopy(value)
    agent_input = {key: changed[key] for key in ("order", "observations")}
    fingerprint = hashlib.sha256(canonical(agent_input).encode()).hexdigest()
    action = agent(copy.deepcopy(agent_input))
    if action not in ACTIONS:
        raise ValueError("agent returned an invalid action")
    return {"action": action, "expected_action": trace["expected_action"],
            "passed": action == trace["expected_action"],
            "input_sha256": fingerprint}

def diagnose(trace, interventions, agent=scripted_agent):
    baseline = replay(trace, agent)
    trials = []
    for name, change in interventions.items():
        result = replay(trace, agent, (change["observation"], change["replacement"]))
        trials.append({"name": name, **result,
                       "repairs_failure": not baseline["passed"] and result["passed"]})
    return {"mode": "deterministic-sandbox" if agent is scripted_agent else getattr(agent, "engine", "custom-agent"),
            "baseline": baseline, "interventions": trials,
            "limitation": "One-variable interventions demonstrate sensitivity, not general causal proof. Local model reruns may vary."}

def demo():
    trace = {"schema_version": 1, "order": {"age_days": 45}, "expected_action": "deny",
             "observations": {"policy": {"status": "ok", "refund_window_days": 90}}}
    changes = {"fresh_policy": {"observation": "policy", "replacement": {"status": "ok", "refund_window_days": 30}},
               "timeout": {"observation": "policy", "replacement": {"status": "timeout"}},
               "malformed": {"observation": "policy", "replacement": {"status": "ok", "refund_window_days": "thirty"}}}
    return trace, changes

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path)
    parser.add_argument("--interventions", type=Path)
    parser.add_argument("--ollama-model", help="Optional existing local model; no model download")
    args = parser.parse_args()
    if bool(args.trace) != bool(args.interventions):
        parser.error("--trace and --interventions must be provided together")
    trace, changes = demo() if args.trace is None else (json.loads(args.trace.read_text()), json.loads(args.interventions.read_text()))
    agent = ollama_agent(args.ollama_model) if args.ollama_model else scripted_agent
    print(json.dumps(diagnose(trace, changes, agent), indent=2))

if __name__ == "__main__":
    main()
