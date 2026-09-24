# SPDX-License-Identifier: GPL-3.0-only
import copy
import unittest
from workflow import planner
from workflow_compare import compare_workflows


def scenario(identifier, queue, expected="deny"):
    return {"id": identifier, "policy_results": queue, "expected_action": expected}


def payload(*scenarios):
    return {"order": {"age_days": 45}, "scenarios": list(scenarios)}


class WorkflowComparisonTests(unittest.TestCase):
    def test_explicit_failure_and_path_changes_are_reported(self):
        result = compare_workflows(payload(
            scenario("stale", [{"status": "ok", "refund_window_days": 90}]),
            scenario("retry", [{"status": "timeout"}, {"status": "ok", "refund_window_days": 30}])))
        self.assertEqual((result["evaluated"], result["matched"], result["match_rate"]), (2, 1, .5))
        self.assertEqual(result["baseline_id"], "stale")
        self.assertFalse(result["scenarios"][0]["matched_expectation"])
        self.assertEqual(result["scenarios"][1]["comparison_to_first"], {
            "final_action_changed": True, "action_sequence_changed": True, "tool_calls_delta": 1})

    def test_retry_difference_can_preserve_final_action(self):
        fresh = {"status": "ok", "refund_window_days": 30}
        result = compare_workflows(payload(scenario("base", [fresh]), scenario("retry", [{"status": "timeout"}, fresh])))
        delta = result["scenarios"][1]["comparison_to_first"]
        self.assertFalse(delta["final_action_changed"])
        self.assertTrue(delta["action_sequence_changed"])
        self.assertEqual(result["matched"], 2)

    def test_invalid_late_scenario_executes_no_callbacks(self):
        valid = scenario("first", [])
        invalids = [scenario("last", [float("nan")]), scenario("first", []),
                    scenario("last", [], []), {"id": "last", "policy_results": []}]
        for invalid in invalids:
            calls = []
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                compare_workflows(payload(valid, invalid), agent=lambda c: calls.append(c))
            self.assertEqual(calls, [])

    def test_input_bounds_and_unexpected_fields_fail_before_callbacks(self):
        base = payload(scenario("one", []))
        invalids = [payload(), payload(*[scenario(str(i), []) for i in range(101)]),
                    {**base, "max_steps": True}, {**base, "extra": "untrusted"},
                    {**base, "order": {"age_days": 45, "expected_action": "deny"}}]
        for invalid in invalids:
            calls = []
            with self.subTest(invalid_keys=list(invalid)), self.assertRaises(ValueError):
                compare_workflows(invalid, agent=lambda c: calls.append(c))
            self.assertEqual(calls, [])

    def test_callback_cannot_mutate_later_owned_inputs_or_expectations(self):
        data = payload(scenario("first", [], "escalate"),
                       scenario("second", [{"status": "ok", "refund_window_days": 30}]))
        seen = []
        def callback(context):
            seen.append(copy.deepcopy(context))
            data["scenarios"][1]["expected_action"] = "refund"
            data["scenarios"][1]["policy_results"][0]["refund_window_days"] = 90
            action = planner(context)
            context["order"]["age_days"] = 0
            return action
        result = compare_workflows(data, agent=callback)
        self.assertEqual(result["matched"], 2)
        self.assertEqual(result["scenarios"][1]["expected_action"], "deny")
        self.assertTrue(all(set(context) == {"order", "observations", "tool_calls"} for context in seen))

    def test_null_expectation_means_step_limit_and_engine_restarts(self):
        data = {**payload(scenario("one", [], None), scenario("two", [], None)), "max_steps": 1}
        result = compare_workflows(data)
        for entry in result["scenarios"]:
            self.assertTrue(entry["matched_expectation"])
            self.assertEqual(entry["workflow"]["status"], "step-limit")
            self.assertEqual(entry["workflow"]["tool_calls"], 1)
            self.assertEqual(entry["workflow"]["trace"][0]["tool_call_id"], "policy-1")

    def test_repeatability_and_input_preservation_with_builtin_planner(self):
        data = payload(scenario("one", [], "escalate"))
        original = copy.deepcopy(data)
        self.assertEqual(compare_workflows(data), compare_workflows(data))
        self.assertEqual(data, original)

    def test_callback_failure_propagates_and_does_not_start_later_scenario(self):
        calls = []
        def callback(context):
            calls.append(context)
            raise RuntimeError("callback failed")
        with self.assertRaisesRegex(RuntimeError, "callback failed"):
            compare_workflows(payload(scenario("one", []), scenario("two", [])), agent=callback)
        self.assertEqual(len(calls), 1)
