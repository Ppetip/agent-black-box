# SPDX-License-Identifier: GPL-3.0-only
import copy
import unittest
from regenerate import regenerate, demo
from timeline import replay_events

class RegenerationTests(unittest.TestCase):
    def events(self):
        return [{'id':'c','type':'tool_call','name':'policy','input':{'policy_tier':'short'}},
                {'id':'r','type':'tool_result','call_id':'c','value':{'status':'timeout'}}]
    def test_call_inputs_control_generated_value_and_source_is_preserved(self):
        events=self.events();before=copy.deepcopy(events)
        result=regenerate(events)
        self.assertEqual(result['events'][1]['value']['refund_window_days'],14)
        self.assertEqual(events,before)
        self.assertEqual(result['regenerated_result_ids'],['r'])
    def test_pending_calls_do_not_fabricate_result_arrival(self):
        result=regenerate(self.events()[:1])
        self.assertEqual(result['regenerated_result_ids'],[])
        self.assertEqual(replay_events({'age_days':1},result['events'])['pending_calls'],['c'])
    def test_unknown_tools_or_extra_inputs_rejected(self):
        for name,inputs in [('network',{'policy_tier':'short'}),('policy',{'policy_tier':'missing'}),('policy',{'policy_tier':'short','expected':'deny'})]:
            events=self.events();events[0].update(name=name,input=inputs)
            with self.subTest(name=name,inputs=inputs),self.assertRaises(ValueError):regenerate(events)
    def test_generated_values_remain_hidden_before_recorded_arrival(self):
        result=demo()
        self.assertEqual(result['baseline']['decisions'][0],result['intervened']['decisions'][0])
        self.assertFalse(result['baseline']['decisions'][1]['passed'])
        self.assertTrue(result['intervened']['decisions'][1]['passed'])
