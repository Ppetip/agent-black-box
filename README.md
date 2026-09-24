# Agent Black Box

A flight recorder and counterfactual debugger for tool-using agents.

**v0.1 development prototype Ãƒâ€šÃ‚Â· Python 3.11+ Ãƒâ€šÃ‚Â· GPL-3.0-only**

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

67 tests and eight offline CLI paths pass locally; hosted workflow-comparison verification is pending.

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

### First-time budget setup and recovery

For a genuinely new allowance only, run `python jev_client.py --init-budget /absolute/path/to/jev-budget.sqlite3` once, then use that exact path in `JEV_BUDGET_DB` for every app. Initialization refuses existing files, including empty files. Do not initialize a new ledger to replace lost spending history. Existing users keep their existing ledger and skip setup.

Live clients now open existing ledgers only, including at reservation time. A missing, mistyped, or empty ledger stops calls instead of silently recreating a zero balance. Restore missing history from a trusted backup; do not reset it. This prevents accidental recreation, not deliberate administrator modification or substitution of a different valid database.

## Latest reliability improvement

Run `python timeline.py`. The synthetic demo shows decisions before policy arrival, after a stale policy, and after a fresh policy. `replay_events(order, events, agent=..., replacements=...)` validates the entire event sequence before callbacks; agents cannot see future events or evaluation labels. Replacements target observation IDs, and later observations supersede earlier ones. This replays a fixed recorded sequence; it does not regenerate tools from changed actions or prove causality.

See [Reading results](docs/RESULTS.md) for outcome fields, denominators, abstentions and the limits of command success.

## New evaluation path

`python timeline.py --tool-events` demonstrates `tool_call` events (id, name, input) and `tool_result` events (id, call_id, value). Each result must match one earlier, unfinished call. Pending calls create no observation. Results update observations in arrival order; replacement keys may target result IDs. Tool inputs stay in the audit output; decisions receive only currently available order/observations. No actual tool is executed.

## Evaluation reliability

Replay owns a deep snapshot of order, events and interventions before any callback runs. Callbacks cannot change later observations or evaluation labels by mutating the original inputs. All intervention values must serialize as strict JSON before the first callback; malformed future inputs cannot leave a partially executed replay. This is deterministic input isolation, not a security sandbox for untrusted Python callbacks.

## Extended evaluation

Run `python regenerate.py` (Codex route `regenerate`). The pure local policy table regenerates result values from recorded `policy_tier` inputs: standard = 30 days, short = 14 days. Pending calls stay pending, unknown tools/inputs are rejected, and values remain hidden until their recorded arrival. The synthetic example improves from 1/2 to 2/2 expected decisions matched. This extends recorded replay with computed tool responses, but does not regenerate the action-dependent call plan or contact external tools. See `examples/extended-evaluation.json`.

## Input boundaries

Single-decision replay now captures its evaluation label before invoking a callback. Diagnosis and suites snapshot and validate every intervention before the first callback, so caller mutations cannot change later trials or turn failures into passes. Invalid late interventions produce no callback execution. This is input isolation, not a security sandbox for arbitrary Python callbacks.

## Bounded workflow simulation

Run `python workflow.py --input /absolute/path/to/workflow.json`. Input contains `order` with only `age_days`, `policy_results` (an ordered array of supplied JSON observations), and optional `max_steps` (1 to 1,000, default 5). The built-in planner requests policy data, retries one timeout, then selects refund, deny or escalation. Each requested policy call consumes the next supplied result; exhausted queues return an explicit exhausted observation. A changed response can therefore change which calls occur, unlike fixed recorded replay.

The CLI requires a file and never discovers private inputs automatically. `examples/workflow-timeout.json` is a clearly synthetic regression fixture, not real-task evidence. No expected-answer labels are accepted in the order. Inputs are validated and copied before callbacks run. The trace records generated actions, input hashes and simulated tool observations; final status is decided, escalated or step-limit. Invalid actions fail with an error. Terminal refund/deny values are decisions only: the engine performs no network calls, money movement or external writes.

The reusable `run_workflow` permits a trusted Python callback with observable order, prior observations and tool-call count. Future supplied results are hidden. Callbacks are not OS-sandboxed, and the step limit cannot interrupt a hanging callback. `engine_external_side_effects: false` describes only the simulation engine. This implements action-dependent call planning over a supplied response queue, not arbitrary real-tool execution or a live model benchmark.

## Compare supplied workflow scenarios

Run `python workflow_compare.py --input examples/workflow-comparison.json` for a synthetic regression example, or supply an explicitly authorized local file. Input has one `order`, optional `max_steps`, and 1 to 100 `scenarios`. Each scenario contains a unique nonempty `id`, a `policy_results` queue, and an explicit `expected_action`: `refund`, `deny`, `escalate`, or null to expect the step limit. The schema rejects extra fields. All queues and labels are copied and validated before any callback executes.

The report shows each full workflow, whether its final action matches the supplied expectation, and changes relative to the first scenario: final action, action sequence and tool-call count. `match_rate` divides matches by evaluated scenarios; it does not turn command success into task success. The checked-in example deliberately includes a stale-policy failure. Its labels are authored regression expectations, not independent judgments or measured model accuracy.

Each simulated run starts with empty engine observations and call count. No external tool runs, refunds or network requests occur. Invalid input stops before execution. A custom Python callback failure propagates and stops the comparison; arbitrary callback side effects cannot be rolled back. Custom callbacks are trusted code, may retain their own state across scenarios and are not sandboxed or interrupted by the step bound. Input isolation hides labels and future responses from callback arguments; it does not restrict what trusted Python code can access independently. Comparing several changed responses does not identify a minimal intervention or prove causality.
