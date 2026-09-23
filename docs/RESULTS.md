# Reading replay results

A zero CLI exit code means replay completed, not that the agent made the expected decision.

- `baseline.passed` compares the baseline action with the externally supplied expected action.
- `interventions[].repairs_failure` is true only when a failing baseline becomes a matching decision.
- The default synthetic stale-policy example deliberately fails before a policy replacement fixes it.
- In `timeline.py`, each `decisions[].passed` concerns that event alone. Compare baseline and intervened counts separately: the current synthetic fixture matches 2/3 versus 3/3 decisions.
- In `suite.py`, `repairable_failures` counts failing cases repaired by at least one candidate intervention. The denominator for the repair rate is baseline failures, not all cases.

These are sensitivity checks on recorded/synthetic inputs, not formal causality or production accuracy. Expected labels are withheld from agent callbacks. Inspect individual actions and input hashes when a summary seems surprising.

## Saved-check freshness in the local AI Lab workflow

When using the optional AI Lab workspace integration, run `python lab.py status` from the workspace root. This reads saved results without rerunning tests or inference and lists the latest checks for every tool. The shared runner is a local integration, not part of a standalone clone of this repository; standalone checks remain documented in README.

`check_passed` records command/test completion. `freshness` is separate:

- `current`: the explicit source inputs and Python runtime match the completed check.
- `source-or-runtime-changed`: rerun checks after relevant code or runtime changes.
- `changed-during-checks`: inputs changed while checks ran; that run cannot verify one stable version.
- `unverified-legacy`: an older result has no source fingerprint.
- `not-run`: no saved check exists for this tool.

Fingerprints cover project Python files, tests, checked-in example JSON/JSONL paths, workflow YAML and shared runner Python files. They omit documentation, .env, databases, private run outputs and arbitrary analysis input files. Current does not prove unchanged external dependencies or OS state. Saved reports are private local cache records, not signed attestations. A later demo never replaces a check result, and a current failing check is still a failure.

A current check validates the replay implementation and its regression fixtures. It does not validate a newly supplied trace, intervention set or external agent callback.
