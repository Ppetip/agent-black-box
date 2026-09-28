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

## Compare supplied workflow scenarios

Run `python workflow_compare.py --input examples/workflow-comparison.json` for a synthetic regression example, or supply an explicitly authorized local file. Input has one `order`, optional `max_steps`, and 1 to 100 `scenarios`. Each scenario contains a unique nonempty `id`, a `policy_results` queue, and an explicit `expected_action`: `refund`, `deny`, `escalate`, or null to expect the step limit. The schema rejects extra fields. All queues and labels are copied and validated before any callback executes.

The report shows each full workflow, whether its final action matches the supplied expectation, and changes relative to the first scenario: final action, action sequence and tool-call count. `match_rate` divides matches by evaluated scenarios; it does not turn command success into task success. The checked-in example deliberately includes a stale-policy failure. Its labels are authored regression expectations, not independent judgments or measured model accuracy.

Each simulated run starts with empty engine observations and call count. No external tool runs, refunds or network requests occur. Invalid input stops before execution. A custom Python callback failure propagates and stops the comparison; arbitrary callback side effects cannot be rolled back. Custom callbacks are trusted code, may retain their own state across scenarios and are not sandboxed or interrupted by the step bound. Input isolation hides labels and future responses from callback arguments; it does not restrict what trusted Python code can access independently. Comparing several changed responses does not identify a minimal intervention or prove causality.

## Read a workflow comparison in your browser

Run `python comparison_report.py --input examples/workflow-comparison.json --output /absolute/path/to/new-report.html`, then open that file in a browser. Replace the example with an explicitly authorized local scenario file to inspect your own supplied data. The page shows matched versus missed expectations, expected/actual actions, call-count and action-path differences from the first scenario, and expandable step details. Its summary describes supplied expectations, not production success or formal causality. The included example is synthetic.

The renderer uses the built-in local planner, not arbitrary callbacks or external tools. It validates all scenarios before creating the output, refuses to overwrite an existing file, and reports invalid input or file errors with a nonzero CLI exit. The HTML uses escaped text, no scripts, no external resources and a restrictive content policy. Opening or expanding a trace does not rerun the workflow. No server or package installation is required.

Reports include supplied scenario names and simulated observations, so keep real-input reports private unless their exact contents are authorized for sharing. The renderer does not remove secrets from input text. Generated reports are local artifacts, not automatically published files. This is a readable static comparison view; it does not edit scenarios, select a minimal intervention or execute a refund.

## Reduce a supplied failure case

Run `python reduce_workflow.py --input examples/workflow-reduction.json` for a synthetic regression example, or provide an explicitly authorized local file. Input requires `order`, `policy_results` and `expected_action` (refund, deny, escalate or null); optional `max_steps` uses the workflow limit and `max_trials` is 1 to 200, default 100. The baseline counts as one trial. All inputs are validated before execution. The reducer uses only the built-in deterministic planner and prints JSON; it runs no external tools, writes no files and accepts no custom callbacks.

If the baseline already matches the expectation, status is `not-a-failure` and no deletions are attempted. Otherwise, responses are removed one at a time, preserving their order. A deletion is accepted only when both final action and workflow status equal the original failed run. This prevents replacing a wrong refund with an unrelated escalation and calling it the same outcome. Every accepted deletion restarts the scan. The report contains original indices, attempted removals, original/reduced traces and a `reduced_input` object accepted by this reducer.

`one-deletion-minimal` means no single remaining response can be removed while preserving that status/action pair. `trial-limit` means the bounded search stopped without establishing that property. Neither means globally smallest or identifies the true cause. Queue deletion can change which call consumes a response, and preserving an outcome does not preserve its reasoning or failure cause. An empty queue can itself preserve an escalation failure; do not interpret that as a relevant source observation. Supplied expected actions still require independent review.

The checked-in example removes a timeout and an unused response while retaining the stale policy response that still leads to a refund. This is a controlled code regression, not evidence about a real agent's failure. Keep reports containing private supplied observations local.

## Finite reduction invariant checks

Two unittest methods enumerate a restricted synthetic space: all 85 response queues of length zero through three over timeout, null, 30-day and 90-day policy responses; step bounds 1, 2 and 3; and all four expected-action labels. This produces 1,020 complete-search cases, plus 3,060 cases with trial budgets 1, 2 and 3. A separately coded terminal-outcome oracle checks the baseline, every attempted deletion, retained indices, preserved outcome and single-deletion minimality when claimed. It does not call the production planner to calculate those expected terminal outcomes.

These checks passed for the fixed 45-day order. They do not cover arbitrary queues, values, callback planners or real models, and do not establish causality or a globally smallest case. The two methods count as two tests in the suite; generated cases are not independent performance samples. Run `python -m unittest discover -s tests -p test_reduction_invariants.py -v` to reproduce them locally without network access.
