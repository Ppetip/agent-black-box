# SPDX-License-Identifier: GPL-3.0-only
import copy
import unittest
from workflow import run_workflow, planner

class WorkflowTests(unittest.TestCase):
    def test_observation_change_regenerates_call_plan(self):
        order={'age_days':45}
        ordinary=run_workflow(order,[{'status':'ok','refund_window_days':90}])
        retry=run_workflow(order,[{'status':'timeout'},{'status':'ok','refund_window_days':30}])
        self.assertEqual([s['action'] for s in ordinary['trace']],['get_policy','refund'])
        self.assertEqual([s['action'] for s in retry['trace']],['get_policy','get_policy','deny'])
        self.assertEqual(retry['tool_calls'],2);self.assertFalse(retry['engine_external_side_effects'])
    def test_agent_cannot_see_future_results_or_mutate_later_context(self):
        queue=[{'status':'timeout'},{'status':'ok','refund_window_days':30}];seen=[]
        def agent(context):
            seen.append(copy.deepcopy(context))
            queue[1]['refund_window_days']=90
            action=planner(context)
            context['order']['age_days']=0
            return action
        result=run_workflow({'age_days':45},queue,agent)
        self.assertEqual(set(seen[0]),{'order','observations','tool_calls'})
        self.assertEqual(seen[0]['observations'],{})
        self.assertEqual(seen[1]['observations'],{'policy':{'status':'timeout'}})
        self.assertEqual(result['final_action'],'deny')
    def test_repeated_timeouts_stop_after_one_retry(self):
        result=run_workflow({'age_days':45},[{'status':'timeout'}]*5)
        self.assertEqual(result['tool_calls'],2);self.assertEqual(result['status'],'escalated')
    def test_empty_or_malformed_result_escalates(self):
        for results in ([],[None],[{'status':'ok','refund_window_days':True}]):
            with self.subTest(results=results):
                result=run_workflow({'age_days':1},results)
                self.assertEqual(result['final_action'],'escalate');self.assertEqual(result['tool_calls'],1)
    def test_custom_loop_has_step_bound(self):
        result=run_workflow({'age_days':1},[],lambda c:'get_policy',max_steps=3)
        self.assertEqual(result['status'],'step-limit');self.assertEqual(result['tool_calls'],3)
        self.assertIsNone(result['final_action'])
    def test_invalid_queue_and_bound_fail_before_any_callback(self):
        calls=[]
        for results,bound in [([float('nan')],5),([],True),([],0),([],1001)]:
            with self.subTest(bound=bound),self.assertRaises(ValueError):
                run_workflow({'age_days':1},results,lambda c:calls.append(c),bound)
        self.assertEqual(calls,[])
    def test_order_labels_and_unknown_actions_rejected(self):
        with self.assertRaises(ValueError):run_workflow({'age_days':1,'expected_action':'refund'},[])
        with self.assertRaises(ValueError):run_workflow({'age_days':1},[],lambda c:[])
    def test_terminal_action_consumes_no_unused_results_and_inputs_are_preserved(self):
        order={'age_days':1};queue=[{'status':'ok','refund_window_days':30},{'status':'timeout'}];old=copy.deepcopy(queue)
        result=run_workflow(order,queue)
        self.assertEqual(result['tool_calls'],1);self.assertEqual(result['steps'],2)
        self.assertEqual(order,{'age_days':1});self.assertEqual(queue,old)
