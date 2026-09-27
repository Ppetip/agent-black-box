# SPDX-License-Identifier: GPL-3.0-only
import copy
import unittest
from unittest.mock import patch
from reduce_workflow import reduce_failure
from workflow import run_workflow


def example():
    return {"order": {"age_days": 45}, "policy_results": [
        {"status": "timeout"}, {"status": "ok", "refund_window_days": 90},
        {"status": "ok", "refund_window_days": 30}], "expected_action": "deny"}


class ReductionTests(unittest.TestCase):
    def test_reduces_retry_and_unused_response_preserving_terminal_failure(self):
        result = reduce_failure(example())
        self.assertEqual(result["kept_original_indices"], [1])
        self.assertEqual(result["removed_original_indices"], [0, 2])
        self.assertEqual(result["status"], "one-deletion-minimal")
        self.assertEqual(result["reduced"]["final_action"], "refund")
        self.assertEqual(result["baseline"]["tool_calls"], 2)
        self.assertEqual(result["reduced"]["tool_calls"], 1)

    def test_different_failure_is_not_accepted_as_equivalent(self):
        result = reduce_failure(example())
        empty = [a for a in result["attempts"] if a["kept_original_indices"] == []]
        self.assertTrue(empty)
        self.assertTrue(all(a["final_action"] == "escalate" and not a["accepted"] for a in empty))

    def test_trial_limit_includes_baseline_and_never_claims_minimality_early(self):
        with patch("reduce_workflow.run_workflow", wraps=run_workflow) as run:
            result = reduce_failure({**example(), "max_trials": 1})
            self.assertEqual(run.call_count, 1)
        self.assertEqual(result["status"], "trial-limit")
        self.assertFalse(result["one_deletion_minimal"])
        self.assertEqual(result["trials"], 1)
        self.assertEqual(result["kept_original_indices"], [0, 1, 2])

    def test_matching_baseline_is_reported_without_reduction(self):
        result = reduce_failure({**example(), "expected_action": "refund"})
        self.assertEqual(result["status"], "not-a-failure")
        self.assertIsNone(result["one_deletion_minimal"])
        self.assertEqual(result["trials"], 1)
        self.assertEqual(result["attempts"], [])

    def test_empty_failed_queue_has_no_response_left_to_delete(self):
        result = reduce_failure({**example(), "policy_results": [], "max_trials": 1})
        self.assertEqual(result["status"], "one-deletion-minimal")
        self.assertEqual(result["retained_responses"], 0)
        self.assertEqual(result["reduced"]["final_action"], "escalate")

    def test_invalid_late_input_and_limits_fail_before_workflow_execution(self):
        bad = [{**example(), "max_trials": n} for n in (0, True, 201)]
        bad += [{**example(), "policy_results": [None, float("nan")]},
                {**example(), "expected_action": []}, {**example(), "extra": True}]
        for data in bad:
            with self.subTest(data=data), patch("reduce_workflow.run_workflow") as run:
                with self.assertRaises(ValueError): reduce_failure(data)
                run.assert_not_called()

    def test_complete_result_passes_independent_single_deletion_check(self):
        result = reduce_failure(example()); reduced = result["reduced_input"]
        queue = reduced["policy_results"]
        signature = (result["baseline"]["status"], result["baseline"]["final_action"])
        for i in range(len(queue)):
            trial = run_workflow(reduced["order"], queue[:i] + queue[i + 1:], max_steps=reduced["max_steps"])
            self.assertNotEqual((trial["status"], trial["final_action"]), signature)

    def test_repeatability_and_input_isolation(self):
        data = example(); original = copy.deepcopy(data)
        first = reduce_failure(data)
        self.assertEqual(first, reduce_failure(data)); self.assertEqual(data, original)
        first["reduced_input"]["order"]["age_days"] = 0
        self.assertEqual(data, original)
