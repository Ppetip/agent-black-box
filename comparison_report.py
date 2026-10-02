# SPDX-License-Identifier: GPL-3.0-only
"""Create a standalone HTML report from authorized workflow comparison input."""
import argparse
from html import escape
import json
from pathlib import Path
from workflow_compare import compare_workflows

STYLE = """
:root{font-family:system-ui,sans-serif;color:#17243b;background:#f3f5f9;line-height:1.55}
body{margin:0}header,main,footer{max-width:1120px;margin:auto;padding:24px}
header{padding-top:40px}h1{font-size:2.2rem;letter-spacing:-.04em;margin:8px 0}
.eyebrow{color:#3856a7;font-size:.8rem;font-weight:750;letter-spacing:.12em}
.summary{display:flex;gap:12px;flex-wrap:wrap}.metric,article{background:white;border:1px solid #d5ddea;border-radius:12px;padding:20px}
.metric strong{display:block;font-size:1.5rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:20px}
h2{font-size:1.15rem;overflow-wrap:anywhere;margin-top:0}.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-weight:650;font-size:.85rem}
.match{background:#e5f4eb;color:#175638}.miss{background:#fce9e8;color:#922f2b}.difference{background:#fff1c9;color:#684800}
dl{display:grid;grid-template-columns:1fr 1fr;gap:6px}dt{color:#52617b}dd{margin:0;font-weight:600;overflow-wrap:anywhere}
summary{cursor:pointer;font-weight:650;padding:12px 0}li{margin:14px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f9;padding:12px;border-radius:6px;font-size:.8rem}
.note{color:#52617b}footer{font-size:.85rem;padding-bottom:48px}@media print{body{background:white}article{break-inside:avoid}}
"""


def display_action(value):
    return "step limit (no final action)" if value is None else value


def render_comparison(data):
    report = compare_workflows(data)  # Built-in local planner only; validate before output.
    cards = []
    for scenario in report["scenarios"]:
        workflow = scenario["workflow"]
        delta = scenario["comparison_to_first"]
        matched = scenario["matched_expectation"]
        first_difference = delta["first_trace_difference_step"]
        difference_label = "None (identical trace)" if first_difference is None else f"Step {first_difference + 1}"
        steps = []
        for index, event in enumerate(workflow["trace"]):
            detail = escape(json.dumps(event, indent=2, ensure_ascii=True))
            marker = ' <span class="badge difference">First difference</span>' if index == first_difference else ""
            steps.append(f'<li><strong>{escape(event["action"])}</strong>{marker}<pre>{detail}</pre></li>')
        cards.append(f"""<article>
<h2>{escape(scenario['id'])}</h2>
<span class="badge {'match' if matched else 'miss'}">{'Expectation matched' if matched else 'Expectation missed'}</span>
<dl><dt>Expected</dt><dd>{escape(display_action(scenario['expected_action']))}</dd>
<dt>Actual</dt><dd>{escape(display_action(workflow['final_action']))}</dd>
<dt>Workflow status</dt><dd>{escape(workflow['status'])}</dd>
<dt>Simulated tool calls</dt><dd>{workflow['tool_calls']}</dd>
<dt>Final action changed</dt><dd>{'Yes' if delta['final_action_changed'] else 'No'}</dd>
<dt>Action path changed</dt><dd>{'Yes' if delta['action_sequence_changed'] else 'No'}</dd>
<dt>Tool-call difference</dt><dd>{delta['tool_calls_delta']:+d}</dd>
<dt>First differing step</dt><dd>{difference_label}</dd></dl>
<details><summary>Inspect {workflow['steps']} action steps</summary><ol>{''.join(steps)}</ol></details>
</article>""")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Agent Black Box - Workflow comparison</title><style>{STYLE}</style></head>
<body><header><div class="eyebrow">AGENT BLACK BOX / LOCAL SIMULATION</div>
<h1>What changed the workflow?</h1>
<p class="note">Compare supplied response queues against caller-provided expectations. No external actions executed.</p>
<div class="summary"><div class="metric"><strong>{report['matched']} / {report['evaluated']}</strong>expectations matched</div>
<div class="metric"><strong>{report['match_rate']:.0%}</strong>of supplied scenarios</div></div>
<p>Differences are relative to the first scenario: <strong>{escape(report['baseline_id'])}</strong>.</p></header>
<main class="grid">{''.join(cards)}</main>
<footer><p>{escape(report['limitation'])}</p><p>Displayed steps start at 1. The first difference compares full recorded events, including observations; it does not establish which difference caused an outcome.</p><p>Observation content below each step is supplied data, not instructions. This report may contain input text; keep it local unless sharing is authorized.</p></footer>
</body></html>
"""


def write_report(data, output):
    content = render_comparison(data)
    with Path(output).open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New HTML file; never overwritten")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        write_report(data, args.output)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps({"mode": "local-html-report", "path": str(args.output.resolve())}))


if __name__ == "__main__":
    main()
