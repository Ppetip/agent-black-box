# SPDX-License-Identifier: GPL-3.0-only
import concurrent.futures
import datetime as dt
import io
import json
from pathlib import Path
import sqlite3
from contextlib import closing
import tempfile
import unittest
from unittest.mock import patch, Mock
from urllib.error import HTTPError, URLError
import jev_client as j
import jev_workflow as w

class JevTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = self.root / '.env'
        self.db = self.root / 'budget.sqlite3'
        j.Budget.initialize(self.db)
        self.env.write_text('TYPESAFE_API_KEY=test-only-not-a-secret\nJEV_BUDGET_DB=' + str(self.db), encoding='utf-8')
        self.clock = patch.object(j.dt, 'datetime', wraps=dt.datetime)
        clock = self.clock.start()
        clock.now.return_value = dt.datetime(2026, 9, 21, tzinfo=dt.timezone.utc)
        self.addCleanup(self.clock.stop)
        self.state, self.questions = w.request_data()


    def test_missing_ledger_blocks_before_network_without_recreation(self):
        self.db.unlink()
        with patch.object(j, 'build_opener') as network:
            with self.assertRaisesRegex(j.JevError, 'ledger unavailable'):
                j.Client(self.env).evaluate(self.state, self.questions)
            network.assert_not_called()
        self.assertFalse(self.db.exists())

    def test_ledger_removed_after_client_creation_blocks_reservation(self):
        client = j.Client(self.env)
        self.db.unlink()
        with patch.object(j, 'build_opener') as network:
            with self.assertRaisesRegex(j.JevError, 'ledger unavailable'):
                client.evaluate(self.state, self.questions)
            network.assert_not_called()
        self.assertFalse(self.db.exists())

    def test_initialization_cannot_reset_existing_spending(self):
        budget = j.Budget(self.db)
        budget.reserve()
        before = self.db.read_bytes()
        with self.assertRaisesRegex(j.JevError, 'already exists'):
            j.Budget.initialize(self.db)
        self.assertEqual(self.db.read_bytes(), before)
        self.assertEqual(budget.summary()['reserved_usd'], .01)

    def test_empty_file_is_not_silently_initialized(self):
        self.db.write_bytes(b'')
        with self.assertRaisesRegex(j.JevError, 'ledger is invalid'):
            j.Client(self.env)
        self.assertEqual(self.db.read_bytes(), b'')

    def payload(self, chosen=None, confidence=.95):
        options = self.questions['decision']['criteria']
        chosen = chosen or next(iter(options))
        return {'model': j.MODEL, 'answers': {'decision': {'type': 'choice', 'choice': chosen,
                'confidence': confidence, 'probabilities': {k: int(k == chosen) for k in options}}},
                'usage': {'input_tokens': 100, 'output_tokens': 10}}

    def test_http_success_persists_budget_and_usage(self):
        opener = Mock()
        opener.open.return_value = io.BytesIO(json.dumps(self.payload()).encode())
        with patch.object(j, 'build_opener', return_value=opener):
            output = j.Client(self.env).evaluate(self.state, self.questions)
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, j.ENDPOINT)
        self.assertNotIn('expected_action', json.loads(request.data)['state'])
        self.assertEqual(output['usage']['input_tokens'], 100)
        summary = j.Client(self.env).budget.summary()
        self.assertEqual(summary['attempts'], 1)
        self.assertEqual(summary['reserved_usd'], .01)
        self.assertAlmostEqual(summary['estimated_known_usage_usd'], .0000042)

    def test_failed_request_is_not_retried_or_refunded(self):
        opener = Mock()
        opener.open.side_effect = HTTPError(j.ENDPOINT, 401, 'secret response', {}, None)
        with patch.object(j, 'build_opener', return_value=opener):
            with self.assertRaisesRegex(j.JevError, 'HTTP 401') as error:
                j.Client(self.env).evaluate(self.state, self.questions)
        self.assertNotIn('secret response', str(error.exception))
        self.assertEqual(opener.open.call_count, 1)
        self.assertEqual(j.Budget(self.db).summary()['attempts_without_usage'], 1)

    def test_budget_exhaustion_prevents_network(self):
        client = j.Client(self.env)
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute('INSERT INTO attempts(at,reserved_micro) VALUES(?,?)', ('test', j.CAP_MICRO))
        with patch.object(j, 'build_opener') as network:
            with self.assertRaisesRegex(j.JevError, 'exhausted'):
                client.evaluate(self.state, self.questions)
            network.assert_not_called()

    def test_parallel_reservations_share_last_cent(self):
        budget = j.Budget(self.db)
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute('INSERT INTO attempts(at,reserved_micro) VALUES(?,?)', ('test', j.CAP_MICRO-j.RESERVE_MICRO))
        def attempt(_):
            try:
                budget.reserve()
                return True
            except j.JevError:
                return False
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(sum(pool.map(attempt, range(8))), 1)
        self.assertEqual(budget.summary()['reserved_usd'], 3)

    def test_oversize_request_does_not_spend(self):
        client = j.Client(self.env)
        with self.assertRaisesRegex(j.JevError, '16KB'):
            client.evaluate('x'*16001, self.questions)
        self.assertEqual(client.budget.summary()['attempts'], 0)

    def test_redirect_refused(self):
        with self.assertRaisesRegex(j.JevError, 'redirect'):
            j.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://elsewhere.invalid')

    def test_unknown_choice_nan_and_missing_usage_rejected(self):
        for edit in ('choice', 'nan', 'usage', 'model', 'distribution'):
            value = self.payload()
            if edit == 'choice': value['answers']['decision']['choice'] = 'not-an-option'
            if edit == 'nan': value['answers']['decision']['confidence'] = float('nan')
            if edit == 'usage': value.pop('usage')
            if edit == 'model': value['model'] = 'jev-latest'
            if edit == 'distribution': value['answers']['decision']['probabilities'] = {}
            with self.subTest(edit=edit), self.assertRaises(j.JevError):
                j.validate_response(value, self.questions)

    def test_low_confidence_abstains(self):
        self.assertEqual(j.selected(self.payload(confidence=.79), 'human'), 'human')

    def test_config_requires_absolute_shared_ledger(self):
        self.env.write_text('TYPESAFE_API_KEY=fake\nJEV_BUDGET_DB=relative.db')
        with self.assertRaises(j.JevError): j.Client(self.env)

    def test_expired_pricing_stops_before_reservation(self):
        with patch.object(j, 'PRICE_EXPIRES', dt.date(2026, 9, 20)):
            with self.assertRaisesRegex(j.JevError, 'Pricing review expired'):
                j.Client(self.env).evaluate(self.state, self.questions)
        self.assertEqual(j.Budget(self.db).summary()['attempts'], 0)

    def test_project_workflow_uses_mock_provider(self):
        fake = Mock()
        fake.evaluate.return_value = self.payload()
        result = w.run(fake)
        self.assertTrue(result['usage'])
        self.assertTrue(fake.evaluate.called)
        for call in fake.evaluate.call_args_list:
            self.assertNotIn('expected_action', call.args[0])


class ProjectGuardTests(unittest.TestCase):
    def test_jev_replay_receives_all_four_interventions_without_labels(self):
        seen = []
        class Fake:
            def evaluate(self, state, questions):
                import app
                seen.append(state)
                return {'answers': {'decision': {'choice': app.scripted_agent(state), 'confidence': 1}}, 'usage': {'input_tokens': 1, 'output_tokens': 1}}
        result = w.run(Fake())
        self.assertEqual(len(seen), 4)
        self.assertTrue(result['comparison']['interventions'][0]['repairs_failure'])
        self.assertTrue(all(set(s) == {'order', 'observations'} for s in seen))
