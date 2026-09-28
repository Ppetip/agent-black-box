# SPDX-License-Identifier: GPL-3.0-only
"""Finite synthetic invariant checks, not a real-agent quality benchmark."""
import itertools
import unittest
from reduce_workflow import reduce_failure

RESPONSES = (None, {"status": "timeout"},
             {"status": "ok", "refund_window_days": 30},
             {"status": "ok", "refund_window_days": 90})


def terminal(queue, steps):
    """Independent outcome oracle for this fixed age/alphabet and 1..3 steps."""
    if steps == 1:
        return "step-limit", None
    policy = queue[0] if queue else None
    if policy == {"status": "timeout"}:
        if steps == 2:
            return "step-limit", None
        policy = queue[1] if len(queue) > 1 else None
    if policy == {"status": "ok", "refund_window_days": 30}:
        return "decided", "deny"
    if policy == {"status": "ok", "refund_window_days": 90}:
        return "decided", "refund"
    return "escalated", "escalate"


def cases():
    for size in range(4):
        for queue in itertools.product(RESPONSES, repeat=size):
            for steps, expected in itertools.product((1, 2, 3), (None, "deny", "refund", "escalate")):
                yield {"order": {"age_days": 45}, "policy_results": list(queue),
                       "max_steps": steps, "expected_action": expected}


class ReductionInvariantTests(unittest.TestCase):
    def audit(self, data, result):
        queue, steps = data["policy_results"], data["max_steps"]
        signature = terminal(queue, steps)
        self.assertEqual((result["baseline"]["status"], result["baseline"]["final_action"]), signature)
        self.assertEqual(result["trials"], 1 + len(result["attempts"]))
        self.assertLessEqual(result["trials"], data["max_trials"])
        kept = list(range(len(queue)))
        for attempt in result["attempts"]:
            self.assertIn(attempt["removed_original_index"], kept)
            candidate = [i for i in kept if i != attempt["removed_original_index"]]
            self.assertEqual(attempt["kept_original_indices"], candidate)
            outcome = terminal([queue[i] for i in candidate], steps)
            self.assertEqual((attempt["status"], attempt["final_action"]), outcome)
            self.assertEqual(attempt["accepted"], outcome == signature)
            if attempt["accepted"]:
                kept = candidate
        self.assertEqual(result["kept_original_indices"], kept)
        self.assertEqual(result["removed_original_indices"], [i for i in range(len(queue)) if i not in kept])
        reduced = [queue[i] for i in kept]
        self.assertEqual(result["reduced_input"]["policy_results"], reduced)
        self.assertEqual(result["retained_responses"], len(reduced))
        self.assertEqual((result["reduced"]["status"], result["reduced"]["final_action"]), signature)
        if signature[1] == data["expected_action"]:
            self.assertEqual(result["status"], "not-a-failure")
            self.assertEqual(result["trials"], 1)
            self.assertIsNone(result["one_deletion_minimal"])
        elif result["status"] == "one-deletion-minimal":
            self.assertTrue(result["one_deletion_minimal"])
            for i in range(len(reduced)):
                self.assertNotEqual(terminal(reduced[:i] + reduced[i + 1:], steps), signature)
        else:
            self.assertEqual(result["status"], "trial-limit")
            self.assertFalse(result["one_deletion_minimal"])
            self.assertEqual(result["trials"], data["max_trials"])

    def test_complete_search_and_audit_against_independent_finite_oracle(self):
        count = 0
        for data in cases():
            data["max_trials"] = 200
            with self.subTest(data=data):
                result = reduce_failure(data)
                self.audit(data, result)
                self.assertNotEqual(result["status"], "trial-limit")
            count += 1
        self.assertEqual(count, 1020)

    def test_early_stops_preserve_outcome_and_honor_trial_budget(self):
        count = 0
        for data in cases():
            for limit in (1, 2, 3):
                data["max_trials"] = limit
                with self.subTest(data=data):
                    self.audit(data, reduce_failure(data))
                count += 1
        self.assertEqual(count, 3060)
