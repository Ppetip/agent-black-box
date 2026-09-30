# SPDX-License-Identifier: GPL-3.0-only
"""CLI export boundaries with temporary synthetic inputs only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / "examples/workflow-reduction.json").read_text(encoding="utf-8"))


def run_cli(source, output=None):
    command = [sys.executable, str(ROOT / "reduce_workflow.py"), "--input", str(source)]
    if output is not None:
        command += ["--reproducer-output", str(output)]
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=30)


class ReproducerExportTests(unittest.TestCase):
    def test_export_replays_same_terminal_outcome_and_preserves_bounds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "source.json", root / "reproducer.json"
            for trial_limit in (1, 100):
                data = {**FIXTURE, "max_steps": 5, "max_trials": trial_limit}
                source.write_text(json.dumps(data), encoding="utf-8")
                target = output.with_name(f"reproducer-{trial_limit}.json")
                before = source.read_bytes()
                exported = run_cli(source, target)
                self.assertEqual(exported.returncode, 0, exported.stderr)
                report = json.loads(exported.stdout)
                saved = json.loads(target.read_text(encoding="utf-8"))
                self.assertEqual(saved, {**report["reduced_input"], "max_trials": trial_limit})
                self.assertEqual(report["reproducer_output"], str(target))
                self.assertEqual(source.read_bytes(), before)
                replay = run_cli(target)
                self.assertEqual(replay.returncode, 0, replay.stderr)
                replayed = json.loads(replay.stdout)
                self.assertEqual(replayed["baseline"], report["reduced"])
                self.assertEqual(replayed["max_trials"], trial_limit)
                self.assertEqual(replayed["expected_action"], data["expected_action"])

    def test_existing_file_directory_and_source_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "source.json"; existing = root / "existing.json"
            source.write_text(json.dumps(FIXTURE), encoding="utf-8")
            existing.write_text("preserve this", encoding="utf-8")
            for target in (source, existing, root):
                before = {p.name: p.read_bytes() for p in (source, existing)}
                result = run_cli(source, target)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertEqual({p.name: p.read_bytes() for p in (source, existing)}, before)

    def test_invalid_input_and_missing_parent_leave_no_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "input.json"; output = root / "output.json"
            for contents in ("{", json.dumps({**FIXTURE, "max_trials": 0}),
                             json.dumps({**FIXTURE, "policy_results": [float("nan")]})):
                source.write_text(contents, encoding="utf-8")
                result = run_cli(source, output)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertFalse(output.exists())
            source.write_text(json.dumps(FIXTURE), encoding="utf-8")
            result = run_cli(source, root / "missing" / "output.json")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "missing").exists())

    def test_default_is_read_only_and_matching_expectation_stays_nonfailure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / "source.json"
            source.write_text(json.dumps({**FIXTURE, "expected_action": "refund"}), encoding="utf-8")
            before = source.read_bytes()
            result = run_cli(source)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("reproducer_output", json.loads(result.stdout))
            self.assertEqual(list(root.iterdir()), [source])
            self.assertEqual(source.read_bytes(), before)
            output = root / "nonfailure.json"
            result = run_cli(source, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "not-a-failure")
            replay = run_cli(output)
            self.assertEqual(replay.returncode, 0, replay.stderr)
            self.assertEqual(json.loads(replay.stdout)["status"], "not-a-failure")
