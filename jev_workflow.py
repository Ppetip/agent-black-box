# SPDX-License-Identifier: GPL-3.0-only
import argparse
import json
from pathlib import Path
from jev_client import Client, JevError, MODEL, choice, selected
import app

def request_data():
    trace, _ = app.demo()
    return {k: trace[k] for k in ("order", "observations")}, choice(
        "Decide using the supplied refund policy. Refund within its nonnegative integer window (inclusive), deny outside it, escalate if missing or invalid.",
        {"refund": "Eligible within policy window", "deny": "Outside policy window", "escalate": "Missing or invalid policy"})

def run(client):
    trace, changes = app.demo()
    calls = []
    def agent(context):
        _, questions = request_data()
        response = client.evaluate(context, questions)
        calls.append(response["usage"])
        return selected(response, "escalate")
    agent.engine = "jev-live-synthetic-sandbox"
    return {"comparison": app.diagnose(trace, changes, agent),
            "rules_baseline": app.diagnose(trace, changes), "usage": calls,
            "limitation": "Four synthetic replay calls; model sensitivity is not causal proof or a benchmark."}

def main():
    parser = argparse.ArgumentParser(description="Preview the synthetic Jev request; --live explicitly opts into paid calls.")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    if not args.live:
        state, questions = request_data()
        print(json.dumps({"mode": "dry-run-no-network", "model": MODEL, "state": state, "questions": questions}, indent=2))
        return
    if args.env_file is None:
        parser.error("--live requires --env-file with the shared budget ledger")
    try:
        client = Client(args.env_file)
        result = run(client)
        print(json.dumps({"mode": "live-model-on-synthetic-data", "model": MODEL, **result, "budget": client.budget.summary()}, indent=2))
    except JevError as exc:
        parser.exit(1, str(exc) + "\n")

if __name__ == "__main__":
    main()
