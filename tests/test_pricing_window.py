# SPDX-License-Identifier: GPL-3.0-only
import datetime as dt
import unittest
from unittest.mock import Mock, patch
from urllib.error import URLError
import jev_client as j


class PricingWindowTests(unittest.TestCase):
    def client(self):
        # No real credentials or ledger: isolate the pre-network date guard.
        client = object.__new__(j.Client)
        client.key = 'test-only-not-a-secret'
        client.budget = Mock()
        return client

    def test_dates_outside_review_window_never_reserve_or_contact_provider(self):
        for date in (j.PRICE_CHECKED-dt.timedelta(days=1), j.PRICE_EXPIRES,
                     j.PRICE_EXPIRES+dt.timedelta(days=1)):
            client = self.client()
            now = dt.datetime.combine(date, dt.time(), dt.timezone.utc)
            with self.subTest(date=date), patch.object(j.dt, 'datetime', wraps=dt.datetime) as clock, patch.object(j, 'build_opener') as network:
                clock.now.return_value = now
                with self.assertRaisesRegex(j.JevError, 'Pricing review expired'):
                    client.evaluate('synthetic', j.choice('Choose', {'yes':'Yes','no':'No'}))
                client.budget.reserve.assert_not_called()
                network.assert_not_called()

    def test_window_edges_allow_one_mock_attempt_and_retain_failed_reservation(self):
        self.assertLessEqual(65536*j.INPUT_NANO_USD, j.RESERVE_MICRO*1000)
        for date in (j.PRICE_CHECKED, j.PRICE_EXPIRES-dt.timedelta(days=1)):
            client = self.client()
            now = dt.datetime.combine(date, dt.time(), dt.timezone.utc)
            opener = Mock(); opener.open.side_effect = URLError('offline test')
            with self.subTest(date=date), patch.object(j.dt, 'datetime', wraps=dt.datetime) as clock, patch.object(j, 'build_opener', return_value=opener):
                clock.now.return_value = now
                with self.assertRaisesRegex(j.JevError, 'reservation retained, no retry'):
                    client.evaluate('synthetic', j.choice('Choose', {'yes':'Yes','no':'No'}))
                client.budget.reserve.assert_called_once_with()
                opener.open.assert_called_once()
                client.budget.record_usage.assert_not_called()
