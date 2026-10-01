# SPDX-License-Identifier: GPL-3.0-only
"""Locate trace differences without inferring their causal importance."""
import copy
import unittest
from workflow_compare import compare_workflows


def compare(first, second, max_steps=5):
    return compare_workflows({"order":{"age_days":45}, "max_steps":max_steps,
        "scenarios":[{"id":"base", "policy_results":first, "expected_action":"deny"},
                     {"id":"variant", "policy_results":second, "expected_action":"deny"}]})


class TraceDifferenceTests(unittest.TestCase):
    def test_observation_difference_is_visible_when_actions_stay_the_same(self):
        first = [{"status":"ok", "refund_window_days":30}]
        second = [{"status":"ok", "refund_window_days":31}]
        before = copy.deepcopy((first, second))
        result = compare(first, second)
        delta = result["scenarios"][1]["comparison_to_first"]
        self.assertEqual(delta["first_trace_difference_step"], 0)
        self.assertFalse(delta["final_action_changed"])
        self.assertFalse(delta["action_sequence_changed"])
        self.assertEqual((first, second), before)

    def test_common_retry_prefix_locates_later_changed_observation(self):
        first = [{"status":"timeout"}, {"status":"ok", "refund_window_days":30}]
        second = [{"status":"timeout"}, {"status":"ok", "refund_window_days":90}]
        result = compare(first, second)
        base, variant = result["scenarios"]
        self.assertEqual(base["workflow"]["trace"][0], variant["workflow"]["trace"][0])
        self.assertEqual(variant["comparison_to_first"]["first_trace_difference_step"], 1)
        self.assertTrue(variant["comparison_to_first"]["final_action_changed"])

    def test_unused_responses_object_order_and_labels_do_not_change_trace(self):
        first = [{"status":"ok", "refund_window_days":30}]
        second = [{"refund_window_days":30, "status":"ok"}, {"unused":"synthetic"}]
        data = {"order":{"age_days":45}, "scenarios":[
            {"id":"a", "policy_results":first, "expected_action":"deny"},
            {"id":"b", "policy_results":second, "expected_action":"refund"}]}
        result = compare_workflows(data)
        self.assertEqual(result["matched"], 1)
        for scenario in result["scenarios"]:
            self.assertIsNone(scenario["comparison_to_first"]["first_trace_difference_step"])

    def test_json_boolean_and_integer_observations_are_distinguished(self):
        # Python dict equality would equate these payloads; strict JSON does not.
        first = [{"status":"ok", "refund_window_days":True}]
        second = [{"status":"ok", "refund_window_days":1}]
        self.assertEqual(first, second)
        result = compare(first, second, max_steps=1)
        self.assertEqual(result["scenarios"][1]["comparison_to_first"]["first_trace_difference_step"], 0)
        for scenario in result["scenarios"]:
            self.assertEqual(scenario["workflow"]["status"], "step-limit")
