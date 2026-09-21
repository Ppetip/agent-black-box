# Agent Black Box

A flight recorder and counterfactual debugger for tool-using agents.

**v0.1 development prototype Â· Python 3.11+ Â· GPL-3.0-only**

## What works

Replays a refund-policy sandbox; replaces one tool observation per trial; reports action changes and hashes the exact agent input. Evaluation answers are withheld from every agent callback. Includes an opt-in adapter for an already-installed local Ollama model.

## Run

No third-party Python dependencies. Clone this repository and run from its root:

```sh
python app.py
python app.py --trace examples/trace.json --interventions examples/interventions.json
```

For commands using a file under `runs/`, create that directory first (`mkdir runs`). Generated files are ignored by Git. The default demo is offline and uses invented data.

## Test

```sh
python -m unittest discover -s tests -v
```

28 tests pass on Windows and Linux with Python 3.11 and 3.13 (GitHub Actions).

## Architecture

`validate` checks trace shape. `replay` separates agent inputs from evaluation labels and makes a defensive copy. `diagnose` compares independent one-observation interventions against a baseline. The scripted agent provides a reproducible baseline; custom callables can be supplied through the Python API.

## Reproduced example

The synthetic stale-policy example refunds a 45-day-old order under a 90-day policy. Replacing the policy with a 30-day window repairs the failure; timeout and malformed-policy interventions escalate.

See [the captured output](examples/demo-output.json). Rerun `python app.py` to reproduce it.

## Limits

This is a single-decision sandbox, not a general production trace recorder. Interventions demonstrate sensitivity, not formal causal identification. The optional local model adapter has not been exercised against a running model. It never downloads a model. Custom callbacks run trusted local Python code.

## Next experiment

Add a multi-step trace schema and a held-out suite of seeded tool failures before building the comparison UI.

The [design brief](docs/DESIGN.md) describes the larger goal, including unimplemented milestones.

## Contribute

Describe an automation that failed in a surprising way and what the correct result should have been. Use invented or openly licensed examples. Include expected outcomes, edge cases and data provenance.

## License

Copyright (c) 2026 Ppetip. Original code is licensed under GNU GPL version 3 only; see [LICENSE](LICENSE).

### Optional local model

Run `python app.py --ollama-model YOUR_INSTALLED_MODEL` with a locally running Ollama server. This is opt-in, sends only the selected trace inputs to `127.0.0.1:11434`, and does not download models. Live Ollama inference has not been validated in this release.

## Latest development pass

Batch failure evaluation with unique IDs and failure-only repair-rate denominators.

Run `python suite.py` (or `--input cases.json`). Synthetic intervention coverage is not causal proof.

## Optional Jev workflow

Run `python jev_workflow.py` to preview the synthetic request without network access.
To opt into live calls, create a local `.env` using `.env.example`, set your TypeSafe key,
and point `JEV_BUDGET_DB` at one absolute SQLite path shared by all five projects.
Then run `python jev_workflow.py --live --env-file /absolute/path/to/.env`.
Do not commit the real configuration. No packages or model downloads are required.

The adapter pins `jev-1.13.0` and sends only the built-in synthetic fixture in this CLI.
Agent Black Box makes four replay calls; each other workflow makes one. The reusable
`Client.evaluate(state, questions)` interface supports bounded Choice questions.
Treat low-confidence decisions as abstentions; its 0.8 cutoff is a heuristic, not calibrated certainty.

The shared ledger allows at most $3 in cumulative reservations: one cent is permanently
reserved **before each attempt**, including timeouts and failed requests. It never retries
automatically. Concurrent processes share an atomic SQLite reservation. Never reset,
delete, replace or split the ledger to regain budget. This guard covers this client,
not unrelated account use. Provider billing remains authoritative.

[Official TypeSafe pricing](https://docs.typesafe.ai/models) checked 2026-09-21 lists
$0.042 per million input tokens and free output. One cent exceeds a full 65,536-input-token
request at that rate; the client also limits serialized input to 16KB. Estimates use
reported input tokens and exclude unknown failed-request usage. Calls fail closed on
2026-09-28 until pricing and the reservation bound are reviewed. Never extend the review
date without checking the provider's current terms.

[The HTTP API](https://docs.typesafe.ai/api) uses the fixed official TypeSafe endpoint.
Redirects are refused, responses are schema-checked, and error bodies/credentials are
not logged. Tests mock the provider and do not spend money.

`examples/jev-live-smoke.json` records a real 2026-09-21 model response on synthetic input.
It is a connectivity and workflow smoke check, not a quality benchmark or evidence of
training, generalization, speed or production reliability. Re-running it may change results.

Four-way live replay matches the rules baseline: stale policy refunds, fresh policy denies, timeout/malformed policy escalate.

## Continuous verification

[Offline checks](https://github.com/Ppetip/agent-black-box/actions/workflows/offline.yml) run tests and JSON CLI smoke checks on Windows/Linux with Python 3.11/3.13 for pushes and pull requests. Run `python verify_demos.py` locally. Actions are pinned to immutable commits, use read-only permissions, and receive no provider secrets. Jev tests use mocks; the CLI check uses its default dry run. The workflow does not run live inference.
