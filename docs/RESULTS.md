# Reading replay results

A zero CLI exit code means replay completed, not that the agent made the expected decision.

- `baseline.passed` compares the baseline action with the externally supplied expected action.
- `interventions[].repairs_failure` is true only when a failing baseline becomes a matching decision.
- The default synthetic stale-policy example deliberately fails before a policy replacement fixes it.
- In `timeline.py`, each `decisions[].passed` concerns that event alone. Compare baseline and intervened counts separately: the current synthetic fixture matches 2/3 versus 3/3 decisions.
- In `suite.py`, `repairable_failures` counts failing cases repaired by at least one candidate intervention. The denominator for the repair rate is baseline failures, not all cases.

These are sensitivity checks on recorded/synthetic inputs, not formal causality or production accuracy. Expected labels are withheld from agent callbacks. Inspect individual actions and input hashes when a summary seems surprising.
