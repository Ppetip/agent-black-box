# SPDX-License-Identifier: GPL-3.0-only
import copy
import unittest
from timeline import replay_events, demo

class TimelineTests(unittest.TestCase):
    def test_prefix_hides_future_observations_and_labels(self):
        events=[{'id':'d','type':'decision','expected_action':'escalate'}, {'id':'o','type':'observation','name':'policy','value':{'status':'ok'}}]
        seen=[]
        def agent(context):
            seen.append(context)
            return 'escalate'
        replay_events({'age_days':1},events,agent)
        self.assertEqual(seen,[{'order':{'age_days':1},'observations':{}}])

    def test_intervention_changes_only_subsequent_decisions(self):
        result=demo()
        a,b=result['baseline']['decisions'],result['intervened']['decisions']
        self.assertEqual(a[0],b[0])
        self.assertEqual(a[2],b[2])
        self.assertFalse(a[1]['passed'])
        self.assertTrue(b[1]['passed'])

    def test_invalid_late_event_prevents_all_callbacks(self):
        events=[{'id':'d','type':'decision','expected_action':'deny'},{'id':'bad','type':'unknown'}]
        seen=[]
        with self.assertRaises(ValueError): replay_events({'age_days':1},events,lambda c:seen.append(c))
        self.assertEqual(seen,[])

    def test_callback_mutation_cannot_change_later_context(self):
        events=[{'id':str(i),'type':'decision','expected_action':'deny'} for i in range(2)]
        order={'age_days':2}; seen=[]
        def agent(context):
            seen.append(context['order']['age_days'])
            context['order']['age_days']=999
            return 'deny'
        replay_events(order,events,agent)
        self.assertEqual(seen,[2,2]);self.assertEqual(order,{'age_days':2})
