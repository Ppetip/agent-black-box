# SPDX-License-Identifier: GPL-3.0-only
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from comparison_report import render_comparison, write_report


def data(identifier="scenario", observation=None, expected="escalate"):
    return {"order": {"age_days": 45}, "scenarios": [
        {"id": identifier, "policy_results": [observation], "expected_action": expected}]}


class Elements(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags = []; self.attributes = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag); self.attributes.extend(attrs)


class ComparisonReportTests(unittest.TestCase):
    def test_summary_discloses_failed_expectation(self):
        page = render_comparison(data(observation={"status": "ok", "refund_window_days": 90}, expected="deny"))
        self.assertIn("0 / 1", page)
        self.assertIn("Expectation missed", page)
        self.assertIn("<dd>deny</dd>", page)
        self.assertIn("<dd>refund</dd>", page)
        self.assertIn("not independently verified ground truth", page)

    def test_untrusted_id_and_observation_cannot_add_active_html(self):
        attack = '<script>alert(1)</script><img src="https://invalid.example" onerror="alert(2)">'
        page = render_comparison(data(identifier=attack, observation={"note": attack}))
        parsed = Elements(); parsed.feed(page)
        self.assertNotIn("script", parsed.tags); self.assertNotIn("img", parsed.tags)
        self.assertFalse(any(key in {"src", "href", "onerror"} for key, _ in parsed.attributes))
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("default-src 'none'", page)
        self.assertIn("Inspect 2 action steps", page)

    def test_step_limit_is_not_rendered_as_a_terminal_action(self):
        supplied = {**data(expected=None), "max_steps": 1}
        page = render_comparison(supplied)
        self.assertIn("step limit (no final action)", page)
        self.assertIn("Expectation matched", page)
        self.assertIn("<dd>step-limit</dd>", page)

    def test_existing_report_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.html"
            output.write_text("original", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                write_report(data(), output)
            self.assertEqual(output.read_text(encoding="utf-8"), "original")

    def test_invalid_input_creates_no_report(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.html"
            with self.assertRaises(ValueError):
                write_report({"order": {"age_days": 45}, "scenarios": []}, output)
            self.assertFalse(output.exists())

    def test_report_is_repeatable_standalone_and_written_to_requested_path(self):
        supplied = data()
        self.assertEqual(render_comparison(supplied), render_comparison(supplied))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.html"
            write_report(supplied, output)
            page = output.read_text(encoding="utf-8")
            self.assertTrue(page.startswith("<!doctype html>"))
            self.assertIn('<html lang="en">', page)
            self.assertIn("<details>", page)
            self.assertEqual(list(Path(directory).iterdir()), [output])
