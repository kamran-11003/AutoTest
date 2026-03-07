"""
HTML + JSON Reporter
Writes test execution results to data/test_results/
Uses only Python stdlib — no new dependencies.
"""

import sys
import json
import base64
import html as html_mod
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from execution.test_result import ExecutionReport, TestStatus

RESULTS_DIR = Path("data/test_results")


class Reporter:
    def __init__(self, output_dir: str = "data/test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, report: ExecutionReport, crawl_id: str) -> str:
        """Write HTML + JSON report.  Returns path to HTML file."""
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = f"report_{crawl_id}_{ts}"

        json_path = self.output_dir / f"{stem}.json"
        html_path = self.output_dir / f"{stem}.html"

        # JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)

        # HTML
        html_content = self._build_html(report, crawl_id, ts)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return str(html_path)

    # ── HTML Builder ───────────────────────────────────────────────────────

    def _build_html(self, report: ExecutionReport, crawl_id: str, ts: str) -> str:
        pass_color  = "#27ae60"
        fail_color  = "#e74c3c"
        err_color   = "#f39c12"
        skip_color  = "#95a5a6"

        pass_pct  = report.pass_rate
        fail_pct  = report.failure_rate
        err_pct   = max(0.0, round(100 - pass_pct - fail_pct, 1))
        stop_icon = {"completed": "✅", "budget_exhausted": "💸",
                     "time_limit": "⏱", "rl_stop": "🤖", "partial": "⚠️"}.get(
                         report.stop_reason, "ℹ️")

        # ── Results table rows ─────────────────────────────────────────
        rows_html = ""
        for r in report.results:
            color = {
                "passed":  pass_color,
                "failed":  fail_color,
                "error":   err_color,
                "skipped": skip_color,
            }.get(r.status.value if hasattr(r.status, "value") else r.status, err_color)

            # Embed screenshot if available
            img_tag = ""
            sp = r.screenshot_path
            if sp and Path(sp).exists():
                try:
                    with open(sp, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()
                    img_tag = f'<img src="data:image/png;base64,{b64}" style="max-width:200px;cursor:pointer;" onclick="this.style.maxWidth=this.style.maxWidth==\'200px\'?\'100%\':\'200px\'" />'
                except Exception:
                    pass

            safe_evidence = html_mod.escape(r.evidence or "")
            safe_error    = html_mod.escape(r.error_message or "")
            safe_value    = html_mod.escape(str(r.test_value or ""))
            safe_expected = html_mod.escape(str(r.expected_result or ""))

            rows_html += f"""
            <tr>
                <td style="font-family:monospace;font-size:12px">{html_mod.escape(r.test_id)}</td>
                <td style="color:{color};font-weight:bold">{(r.status.value if hasattr(r.status,"value") else r.status).upper()}</td>
                <td>{html_mod.escape(r.test_type)}</td>
                <td>{r.oracle_method.value if hasattr(r.oracle_method,"value") else r.oracle_method}</td>
                <td>{r.confidence}%</td>
                <td style="font-size:11px;max-width:200px;overflow:hidden">{safe_value}</td>
                <td style="font-size:11px;max-width:150px">{safe_expected}</td>
                <td style="font-size:11px">{safe_evidence[:120]}</td>
                <td style="font-size:11px;color:{fail_color}">{safe_error}</td>
                <td>{round(r.duration_ms)}ms</td>
                <td>{img_tag}</td>
            </tr>"""

        # ── RL Decision Bar ────────────────────────────────────────────
        total_dec = max(report.heuristic_decisions + report.llm_decisions + report.stop_decisions, 1)
        h_pct = round(report.heuristic_decisions / total_dec * 100)
        l_pct = round(report.llm_decisions        / total_dec * 100)
        s_pct = round(report.stop_decisions        / total_dec * 100)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AutoTestAI — Execution Report</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #f4f6f9; color: #2c3e50; }}
  .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 40px; }}
  .header h1 {{ margin: 0 0 8px; font-size: 28px; }}
  .header p  {{ margin: 0; opacity: 0.85; }}
  .container {{ max-width: 1400px; margin: 30px auto; padding: 0 20px; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 30px; }}
  .card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,.08); text-align: center; }}
  .card .value {{ font-size: 36px; font-weight: 700; }}
  .card .label {{ font-size: 12px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }}
  .section {{ background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,.08); margin-bottom: 24px; }}
  .section h2 {{ margin: 0 0 16px; font-size: 18px; border-bottom: 2px solid #f0f0f0; padding-bottom: 8px; }}
  .progress {{ height: 24px; border-radius: 12px; overflow: hidden; display: flex; background: #ecf0f1; }}
  .progress .seg {{ display: flex; align-items: center; justify-content: center; font-size: 12px; color: white; font-weight: 600; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ background: #667eea; color: white; padding: 10px 8px; text-align: left; white-space: nowrap; }}
  td {{ padding: 8px; border-bottom: 1px solid #f0f0f0; vertical-align: middle; }}
  tr:hover td {{ background: #fafbff; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
</style>
</head>
<body>
<div class="header">
  <h1>🤖 AutoTestAI — Execution Report</h1>
  <p>Crawl ID: <strong>{html_mod.escape(crawl_id)}</strong> &nbsp;|&nbsp; Generated: {ts} &nbsp;|&nbsp; Stop: {stop_icon} {html_mod.escape(report.stop_reason)}</p>
</div>
<div class="container">

  <!-- Summary Cards -->
  <div class="cards">
    <div class="card"><div class="value" style="color:#2c3e50">{report.total}</div><div class="label">Total Tests</div></div>
    <div class="card"><div class="value" style="color:{pass_color}">{report.passed}</div><div class="label">Passed ({pass_pct}%)</div></div>
    <div class="card"><div class="value" style="color:{fail_color}">{report.failed}</div><div class="label">Failed ({fail_pct}%)</div></div>
    <div class="card"><div class="value" style="color:{err_color}">{report.errors}</div><div class="label">Errors</div></div>
    <div class="card"><div class="value" style="color:#8e44ad">{report.api_calls_used}</div><div class="label">LLM Calls</div></div>
    <div class="card"><div class="value" style="color:#16a085">${report.api_cost:.3f}</div><div class="label">API Cost</div></div>
    <div class="card"><div class="value" style="color:#2980b9">{report.duration_s}s</div><div class="label">Duration</div></div>
  </div>

  <!-- Pass/Fail Bar -->
  <div class="section">
    <h2>📊 Pass / Fail Distribution</h2>
    <div class="progress">
      <div class="seg" style="width:{pass_pct}%;background:{pass_color}">{pass_pct}%</div>
      <div class="seg" style="width:{fail_pct}%;background:{fail_color}">{fail_pct}%</div>
      <div class="seg" style="width:{err_pct}%;background:{err_color}">{err_pct}%</div>
    </div>
    <div style="margin-top:8px;font-size:12px;color:#7f8c8d">
      <span style="color:{pass_color}">■ Passed</span> &nbsp;
      <span style="color:{fail_color}">■ Failed</span> &nbsp;
      <span style="color:{err_color}">■ Error/Unclear</span>
    </div>
  </div>

  <!-- RL Decision Breakdown -->
  <div class="section">
    <h2>🤖 RL Oracle Decisions</h2>
    <div class="progress" style="height:32px">
      <div class="seg" style="width:{h_pct}%;background:#27ae60">Heuristic {h_pct}%</div>
      <div class="seg" style="width:{l_pct}%;background:#8e44ad">LLM {l_pct}%</div>
      <div class="seg" style="width:{s_pct}%;background:#e74c3c">Stop {s_pct}%</div>
    </div>
    <div style="margin-top:8px;font-size:12px;color:#7f8c8d">
      Heuristic: {report.heuristic_decisions} &nbsp;|&nbsp;
      LLM: {report.llm_decisions} &nbsp;|&nbsp;
      Early Stop: {report.stop_decisions}
    </div>
  </div>

  <!-- Results Table -->
  <div class="section">
    <h2>📋 Full Results</h2>
    <div style="overflow-x:auto">
    <table>
      <thead><tr>
        <th>Test ID</th><th>Status</th><th>Type</th><th>Oracle</th>
        <th>Conf</th><th>Value</th><th>Expected</th>
        <th>Evidence</th><th>Error</th><th>Duration</th><th>Screenshot</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>
  </div>

</div><!-- /container -->
</body>
</html>"""
