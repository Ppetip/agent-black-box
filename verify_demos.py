# SPDX-License-Identifier: GPL-3.0-only
"""Offline CLI contract checks. No key, env file, package install or live provider."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
COMMANDS = [['app.py'], ['jev_workflow.py'], ['suite.py'], ['timeline.py']]

COMMANDS.append(['timeline.py', '--tool-events'])

COMMANDS.append(['regenerate.py'])

COMMANDS.append(['workflow.py', '--input', 'examples/workflow-timeout.json'])

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

if __name__ == "__main__":
    main()
