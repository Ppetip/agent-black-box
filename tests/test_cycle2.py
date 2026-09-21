import copy
import unittest
from suite import evaluate_suite, fixtures

class SuiteTests(unittest.TestCase):
    def test_failure_denominator(self):
        r = evaluate_suite(fixtures())
        self.assertEqual((r['cases'], r['baseline_failures'], r['repairable_failures']), (3, 1, 1))
    def test_input_unchanged(self):
        cases = fixtures(); old = copy.deepcopy(cases)
        evaluate_suite(cases); self.assertEqual(cases, old)
    def test_no_failures_rate_is_null(self):
        self.assertIsNone(evaluate_suite(fixtures()[1:])['repair_rate_among_failures'])
    def test_duplicate_id_rejected_before_agent(self):
        cases = fixtures(); cases[1]['id'] = cases[0]['id']
        def agent(_): self.fail('Agent must not run for invalid suite')
        with self.assertRaises(ValueError): evaluate_suite(cases, agent)
