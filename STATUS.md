# Status

Stage: command-line prototype with optional live Jev integration.
Verified: 89 tests and eleven offline CLI paths pass locally; all four hosted checks pass. Jev smoke results remain historical.

Latest: Explicit reproducer export saves a rerunnable reduced case while preserving input files and execution bounds.

Next: Collect independent workflow expectations and review differences in a real task-authorized trace.

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

2026-09-23 22:57 UTC: Added workflow.py with explicit input files, generated policy requests, one-time timeout retry, escalation on unavailable/malformed data, trace hashes and a hard decision-step bound. Engine has no external actions; trusted custom callbacks are not sandboxed or time-limited. Eight new regressions pass; no real-task accuracy claim or live calls. Check run 1c0f400feec446d3bdc45fc0533e704c. All four hosted Windows/Linux Python 3.11/3.13 jobs pass.

Workflow verification: https://github.com/Ppetip/agent-black-box/actions/runs/35931551626

2026-09-24 11:00 UTC: Added bounded scenario comparison with labels hidden from callback arguments and full preflight validation before any execution. Reports separate expectation matches from changes in final action, action path and tool calls. Local check 77ea8798775e4155839e678c20926e1a passed. All four hosted Windows/Linux Python 3.11/3.13 jobs pass. Synthetic fixtures verify code behavior only; no live calls.

Workflow-comparison verification: https://github.com/Ppetip/agent-black-box/actions/runs/35991001742

2026-09-26 23:00 UTC: Added a script-free local comparison report with escaped input and exclusive output creation. No server, external assets, live calls or action execution. Local check cea19b5ee5ce458fb6317617222ae0d6 passed. All four hosted Windows/Linux Python 3.11/3.13 jobs pass. Synthetic fixtures exercise report behavior only.

HTML-report verification: https://github.com/Ppetip/agent-black-box/actions/runs/36278385483

2026-09-27 07:00 UTC: The optional local AI Lab integration now exposes workflow and workflow-comparison routes, with explicit --input support and input-origin labels. Standalone commands remain available in this repository. All five common-runner check routes passed (280 app tests and 28 CLI paths total), plus 32 shared-runner regressions. Check run ffd76d632c9246f4969e0cbbbacb538f. Shared integration is local to the AI Lab workspace, not included in a standalone repository clone. Existing app-source hosted results remain applicable; this documentation update skips redundant hosted CI. No paid calls.

2026-09-27 15:00 UTC: Added deterministic single-response deletion reduction with explicit expectations, preflight validation, original-index audit and a 200-trial ceiling including baseline. No external actions. Local check bd0abeeab18e4612a54eb3b92fb2cff3 passed. All four hosted Windows/Linux Python 3.11/3.13 jobs pass. Synthetic regression evidence only; no formal causality or globally minimal-case claim.

Response-reduction verification: https://github.com/Ppetip/agent-black-box/actions/runs/36328492026

2026-09-27 19:00 UTC: The optional local runner now exposes reduce with authorized --input support, private saved reports and explicit summaries for matched baseline, trial limit and single-deletion minimality. Standalone reducer implementation is unchanged. All five common checks pass (288 app tests, 29 CLI paths), plus 38 shared-runner regressions. Check run 6cbc7ab369f64438ac08e746849d49a7. Shared integration stays local to the AI Lab workspace. App-source hosted evidence is unchanged; documentation-only update skips redundant CI. No live calls.

2026-09-28 03:00 UTC: Added two finite-space invariant tests covering 1,020 complete-search and 3,060 short-budget cases, using a separate terminal-outcome oracle for the fixed synthetic alphabet. Checks verify audit consistency, retained outcomes, budgets and claimed single-deletion minimality. Local check ff4d336a483948379fd4904efe645b95 passed. All four hosted Windows/Linux Python 3.11/3.13 jobs pass. Reducer implementation unchanged; no real-agent performance or causal claim.

Finite-reduction verification: https://github.com/Ppetip/agent-black-box/actions/runs/36372271156

2026-09-28 15:00 UTC: Official TypeSafe model pricing rechecked; the pinned Jev rate and free output are unchanged. Review window refreshed to September 28 through October 4 UTC, failing closed October 5. One-cent permanent reservation and the existing shared $3 cap/ledger remain unchanged. Added two mocked date-boundary tests; existing mocked calls now use the review-start date. Local check 10d3bcc5c43a42b1b5bbf4b998834a5e passed. All four hosted Windows/Linux Python 3.11/3.13 jobs pass. No live calls or ledger access during this update; historical smoke results remain historical.

Pricing-review verification: https://github.com/Ppetip/agent-black-box/actions/runs/36441134665

2026-09-29 23:00 UTC: Shared-runner routing changes pass existing replay, workflow and reduction checks; flagship implementation is unchanged. All five common checks pass (312 app tests, 31 CLI paths), plus 44 shared-runner regressions. Check run 5e891ea4ba6c48658f9dcb20c00c1d26. Shared integration stays local to the AI Lab workspace; app-source hosted evidence is unchanged. Documentation-only update skips redundant CI. No live calls.

2026-09-30 11:02 UTC: Optional --reproducer-output creates a new JSON reproducer only after validated local reduction. It preserves the reduced input plus original max_trials; default output remains read-only. Existing source/target files and directories are protected by exclusive creation, and parents are not created. Four new CLI regression methods verify rerun equality and bounds for complete/trial-limited reductions, no-overwrite behavior, invalid input/missing-parent failures, and unchanged default/nonfailure semantics. Outputs retain supplied observations and must stay private when inputs are private. Required common-runner check 1dfbc8f4e3b842c499994fe504c48af1 passes 89 tests and eleven CLI paths. All four hosted Windows/Linux Python 3.11/3.13 jobs pass. No external actions, paid calls or ledger changes.

Reproducer-export verification: https://github.com/Ppetip/agent-black-box/actions/runs/36706614300

2026-09-30 23:03 UTC: Shared local runner now offers Budget Cortex random-baseline with fixed seed 7, budget 22 and target 0.7; full comparisons and input origin appear in private reports. All five required common checks pass (326 app tests, 33 CLI paths), plus 50 shared-runner regressions. Check run 79735bdda73e449d86dd8b4d521efcb2. App implementation unchanged; prior exact-source hosted evidence retained and this documentation update skips redundant CI. Shared runner is local AI Lab integration, not bundled in standalone repositories. No live calls or ledger changes.
