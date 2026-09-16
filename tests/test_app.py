import copy
import unittest
from app import demo, diagnose, replay, scripted_agent

class ReplayTests(unittest.TestCase):
    def test_stale_policy_is_repaired(self):
        t, changes = demo(); result = diagnose(t, changes)
        self.assertFalse(result['baseline']['passed'])
        self.assertEqual([r['name'] for r in result['interventions'] if r['repairs_failure']], ['fresh_policy'])
    def test_does_not_modify_original(self):
        t, c = demo(); old = copy.deepcopy(t); diagnose(t, c); self.assertEqual(t, old)
    def test_replay_is_stable(self):
        t, _ = demo(); self.assertEqual(replay(t), replay(t))
    def test_failure_has_safe_action(self):
        t, _ = demo(); self.assertEqual(replay(t, intervention=('policy', None))['action'], 'escalate')
    def test_unknown_intervention_rejected(self):
        t, _ = demo()
        with self.assertRaises(ValueError): replay(t, intervention=('unknown', {}))
    def test_invalid_trace_rejected(self):
        t, _ = demo(); t['order']['age_days'] = -1
        with self.assertRaises(ValueError): replay(t)
    def test_ground_truth_hidden_from_custom_agent(self):
        t, _ = demo()
        def agent(context):
            self.assertEqual(set(context), {'order', 'observations'})
            return 'deny'
        self.assertTrue(replay(t, agent)['passed'])
    def test_agent_mutation_does_not_change_hash(self):
        t, _ = demo()
        def agent(context):
            context['order']['age_days'] = 999
            return 'refund'
        self.assertEqual(replay(t, agent)['input_sha256'], replay(t)['input_sha256'])
    def test_malformed_order_rejected(self):
        t, _ = demo(); t['order'] = None
        with self.assertRaises(ValueError): replay(t)
    def test_custom_agent_label_is_honest(self):
        t, c = demo()
        self.assertEqual(diagnose(t, c, lambda _: 'deny')['mode'], 'custom-agent')
    def test_boundary(self):
        t, _ = demo(); t['order']['age_days'] = 90; self.assertEqual(scripted_agent(t), 'refund')
    def test_invalid_agent_result_rejected(self):
        t, _ = demo()
        with self.assertRaises(ValueError): replay(t, lambda _: 'delete')

if __name__ == '__main__': unittest.main()
