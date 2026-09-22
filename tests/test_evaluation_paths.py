# SPDX-License-Identifier: GPL-3.0-only
import unittest
from timeline import replay_events

class ToolEventTests(unittest.TestCase):
    def events(self):
        return [{'id':'c','type':'tool_call','name':'policy','input':{'order_id':'synthetic'}}, {'id':'d0','type':'decision','expected_action':'escalate'}, {'id':'r','type':'tool_result','call_id':'c','value':{'status':'ok','refund_window_days':90}}, {'id':'d1','type':'decision','expected_action':'deny'}]
    def test_result_is_hidden_until_arrival_and_replaceable(self):
        baseline=replay_events({'age_days':45},self.events())
        fixed=replay_events({'age_days':45},self.events(),replacements={'r':{'status':'ok','refund_window_days':30}})
        self.assertEqual(baseline['decisions'][0],fixed['decisions'][0])
        self.assertEqual([x['action'] for x in baseline['decisions']],['escalate','refund'])
        self.assertTrue(fixed['decisions'][1]['passed']);self.assertEqual(fixed['pending_calls'],[])
        self.assertEqual(fixed['tool_events'][0]['input'],{'order_id':'synthetic'})
    def test_unmatched_and_duplicate_results_rejected(self):
        for events in [self.events()[2:],self.events()+[dict(self.events()[2],id='second')]]:
            calls=[]
            with self.assertRaises(ValueError):replay_events({'age_days':1},events,lambda c:calls.append(c))
            self.assertEqual(calls,[])
    def test_unresolved_call_stays_pending_without_fabricated_observation(self):
        result=replay_events({'age_days':1},self.events()[:2])
        self.assertEqual(result['pending_calls'],['c']);self.assertEqual(result['decisions'][0]['action'],'escalate')
