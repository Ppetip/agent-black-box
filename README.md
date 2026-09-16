# Agent Black Box

A flight recorder and counterfactual debugger for tool-using agents.

**v0.1 development prototype · Python 3.11+ · GPL-3.0-only**

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

12 tests passed locally on Python 3.13. Other Python versions have not yet been exercised.

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

Run `python app.py --ollama-model YOUR_INSTALLED_MODEL` with a locally running Ollama server. This is opt-in, sends only the selected trace inputs to `127.0.0.1:11434`, and does not download models. Live inference has not been validated in this release.
