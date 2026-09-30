# SPDX-License-Identifier: GPL-3.0-only
"""Offline CLI contract checks. No key, env file, package install or live provider."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
COMMANDS = [['app.py'], ['jev_workflow.py'], ['suite.py'], ['timeline.py']]

COMMANDS.append(['timeline.py', '--tool-events'])

COMMANDS.append(['regenerate.py'])

COMMANDS.append(['workflow.py', '--input', 'examples/workflow-timeout.json'])
COMMANDS.append(['workflow_compare.py', '--input', 'examples/workflow-comparison.json'])
COMMANDS.append(['reduce_workflow.py', '--input', 'examples/workflow-reduction.json'])

def main():
    for args in COMMANDS:
        result = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True,
                                text=True, encoding="utf-8", timeout=30, check=True)
        payload = json.loads(result.stdout)
        if not isinstance(payload, dict) or not payload:
            raise ValueError("CLI must return a nonempty JSON object")
        if args[0] == "jev_workflow.py" and payload.get("mode") != "dry-run-no-network":
            raise ValueError("Jev CLI default must remain a dry run")
        print("PASS: " + " ".join(args))
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "comparison.html"
        result = subprocess.run([sys.executable, "comparison_report.py", "--input",
                                 "examples/workflow-comparison.json", "--output", str(output)],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30, check=True)
        payload = json.loads(result.stdout)
        if payload.get("mode") != "local-html-report" or not output.read_text(encoding="utf-8").startswith("<!doctype html>"):
            raise ValueError("report CLI must create a standalone HTML report")
        print("PASS: comparison_report.py (temporary synthetic report)")
        reproducer = Path(directory) / "reproducer.json"
        result = subprocess.run([sys.executable, "reduce_workflow.py", "--input",
                                 "examples/workflow-reduction.json", "--reproducer-output", str(reproducer)],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30, check=True)
        payload = json.loads(result.stdout)
        saved = json.loads(reproducer.read_text(encoding="utf-8"))
        if saved != {**payload["reduced_input"], "max_trials": payload["max_trials"]}:
            raise ValueError("saved reproducer must preserve reduced input and trial limit")
        print("PASS: reduce_workflow.py --reproducer-output (temporary synthetic case)")


if __name__ == "__main__":
    main()
