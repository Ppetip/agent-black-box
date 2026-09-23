# Status

Stage: command-line prototype with optional live Jev integration.
Verified: 51 offline tests and all four hosted matrix jobs pass. Jev smoke results remain historical; no new live calls.

Latest: Single-decision replay now captures its evaluation label before invoking a callback.

Next: Add action-dependent sandbox call planning with independent expectations.

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

2026-09-22 22:50 UTC: Run `python regenerate.py` (Codex route `regenerate`). The pure local policy table regenerates result values from recorded `policy_tier` inputs: standard = 30 days, short = 14 days. Pending calls stay pending, unknown tools/inputs are rejected, and values remain hidden until their recorded arrival. The synthetic example improves from 1/2 to 2/2 expected decisions matched. This extends recorded replay with computed tool responses, but does not regenerate the action-dependent call plan or contact external tools. See `examples/extended-evaluation.json`. Common-runner checks pass. Published and verified: all four hosted Windows/Linux Python 3.11/3.13 jobs pass. No new Jev calls.

Extended evaluation verification: https://github.com/Ppetip/agent-black-box/actions/runs/35795054471

2026-09-23 06:53 UTC: Single-decision replay now captures its evaluation label before invoking a callback. Diagnosis and suites snapshot and validate every intervention before the first callback, so caller mutations cannot change later trials or turn failures into passes. Invalid late interventions produce no callback execution. This is input isolation, not a security sandbox for arbitrary Python callbacks. Checks pass; run ID d93bc8de860c4e44b49cd049c42afc20. No live calls. Hosted verification passed on all four OS/Python combinations.

2026-09-23 10:54 UTC verification follow-up: Published code and all four hosted jobs verified after the earlier approval-review usage-limit interruption. Existing check suites were not rerun solely to create history. Run: https://github.com/Ppetip/agent-black-box/actions/runs/35829382650

2026-09-23 14:55 UTC: Added guidance for interpreting saved-check freshness in the optional local Codex runner. A current check validates the replay implementation and its regression fixtures. It does not validate a newly supplied trace, intervention set or external agent callback. The shared runner now records check-source fingerprints and provides read-only status. All five current app checks passed (234 tests total), along with 24 local runner regressions. Run ID: 811900b822db42e390b5e1714afbbe25. App implementation unchanged; this documentation update skips redundant hosted CI. No live calls or new performance claim.
