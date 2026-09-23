# SPDX-License-Identifier: GPL-3.0-only
import copy
import unittest
from app import demo, replay, diagnose, scripted_agent
from suite import evaluate_suite, fixtures

class CallbackBoundaryTests(unittest.TestCase):
    def test_single_replay_label_is_not_changed_by_callback(self):
        trace,_=demo()
        def agent(context):
            trace['expected_action']='refund'
            return 'refund'
        r=replay(trace,agent)
        self.assertEqual(r['expected_action'],'deny');self.assertFalse(r['passed'])
    def test_diagnosis_owns_all_trials_before_callback(self):
        trace,changes=demo();expected=diagnose(copy.deepcopy(trace),copy.deepcopy(changes))
        def agent(context):
            trace['order']['age_days']=0
            changes.clear()
            return scripted_agent(context)
        result=diagnose(trace,changes,agent)
        self.assertEqual(result['baseline'],expected['baseline'])
        self.assertEqual(result['interventions'],expected['interventions'])
    def test_invalid_late_intervention_prevents_all_callbacks(self):
        trace,changes=demo();changes['bad']={'observation':'missing','replacement':None};called=[]
        with self.assertRaises(ValueError):diagnose(trace,changes,lambda c:called.append(c))
        self.assertEqual(called,[])
    def test_suite_preflights_late_case_before_any_callback(self):
        cases=fixtures();cases[-1]['interventions']['bad']={'observation':'policy','replacement':float('nan')};called=[]
        with self.assertRaises(ValueError):evaluate_suite(cases,lambda c:called.append(c))
        self.assertEqual(called,[])
    def test_suite_owns_future_cases(self):
        cases=fixtures();expected=evaluate_suite(copy.deepcopy(cases))
        def agent(context):
            cases[-1]['trace']['order']['age_days']=0
            return scripted_agent(context)
        self.assertEqual(evaluate_suite(cases,agent)['results'][1:][0]['baseline'],expected['results'][1:][0]['baseline'])
        # Check the actually modified last case as well.
        cases=fixtures()
        self.assertEqual(evaluate_suite(cases,agent)['results'][-1]['baseline'],expected['results'][-1]['baseline'])
