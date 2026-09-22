# Status

Stage: command-line prototype with optional live Jev integration.
Verified: 42 offline tests pass; dry run and live synthetic Jev workflow pass.

Latest: Replay owns a deep snapshot of order, events and interventions before any callback runs.

Next: Add regenerated sandbox tool responses alongside fixed recorded replay.

Repository: https://github.com/Ppetip/agent-black-box
Budget: one shared $3 cumulative Jev allowance across the portfolio, never per project or cycle.
No other paid compute authorized. Eight initial calls across all projects used 3,303 input tokens;
estimated total $0.000138726, with $0.08 conservatively reserved. See README for limits.
Live smoke responses are not production benchmarks. No model training performed.

2026-09-21 CI pass: added pinned, read-only Windows/Linux Python 3.11/3.13 checks for unit tests and offline CLI contracts. Local checks and all four hosted Windows/Linux Python 3.11/3.13 jobs pass. No additional Jev calls.

Hosted verification: https://github.com/Ppetip/agent-black-box/actions/runs/35590267896

2026-09-21 14:42 UTC budget fix: live clients require an existing ledger; explicit initialization refuses overwrite. Added four regression cases for missing/deleted/empty ledgers and preserved spending. All local tests, CLI checks, and four hosted Windows/Linux Python 3.11/3.13 jobs pass. No additional Jev calls.

Budget-fix hosted verification: https://github.com/Ppetip/agent-black-box/actions/runs/35614373431

2026-09-21 18:44 UTC: Ordered observation/decision replay now exposes only the context available at each decision, with interventions targeting event IDs. Local tests, offline CLI checks, and all four hosted matrix jobs pass. No additional Jev calls.

Feature-pass verification: https://github.com/Ppetip/agent-black-box/actions/runs/35640884254

2026-09-21 22:45 UTC: documented how to interpret this tool's outcomes separately from command success. The local Codex runner now shows a concise outcome summary for this project. Verified through common-runner checks and synthetic demo output; histories stay local.

2026-09-22 02:46 UTC: Recorded tool calls/results are matched before replay; inputs and pending calls are retained. Common-runner checks, new route and all four hosted jobs pass. No new Jev calls.

Evaluation-path verification: https://github.com/Ppetip/agent-black-box/actions/runs/35681190864

2026-09-22 10:48 UTC: Replay owns a deep snapshot of order, events and interventions before any callback runs. Callbacks cannot change later observations or evaluation labels by mutating the original inputs. All intervention values must serialize as strict JSON before the first callback; malformed future inputs cannot leave a partially executed replay. This is deterministic input isolation, not a security sandbox for untrusted Python callbacks. Published and verified: local checks and all four hosted matrix jobs pass. No new Jev calls.

Reliability verification: https://github.com/Ppetip/agent-black-box/actions/runs/35718636178
