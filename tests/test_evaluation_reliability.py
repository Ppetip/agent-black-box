# SPDX-License-Identifier: GPL-3.0-only
import unittest
from timeline import replay_events
from app import scripted_agent

class ReplayIsolationTests(unittest.TestCase):
    def fixture(self):
        return [{'id':'before','type':'decision','expected_action':'escalate'},
                {'id':'policy','type':'observation','name':'policy','value':{'status':'ok','refund_window_days':90}},
                {'id':'after','type':'decision','expected_action':'deny'}]

    def test_callback_cannot_change_future_recording_or_labels(self):
        events=self.fixture(); order={'age_days':45}
        def agent(context):
            events[1]['value']['refund_window_days']=0
            events[2]['expected_action']='refund'
            order['age_days']=0
            return scripted_agent(context)
        result=replay_events(order,events,agent)
        self.assertEqual(result['decisions'][1]['action'],'refund')
        self.assertFalse(result['decisions'][1]['passed'])

    def test_callback_cannot_change_future_intervention(self):
        changes={'policy':{'status':'ok','refund_window_days':30}}
        def agent(context):
            changes['policy']['refund_window_days']=90
            return scripted_agent(context)
        result=replay_events({'age_days':45},self.fixture(),agent,changes)
        self.assertEqual(result['decisions'][1]['action'],'deny')

    def test_invalid_future_value_rejected_before_callback(self):
        calls=[]
        with self.assertRaises(ValueError):
            replay_events({'age_days':45},self.fixture(),lambda c:calls.append(c),{'policy':float('nan')})
        self.assertEqual(calls,[])
