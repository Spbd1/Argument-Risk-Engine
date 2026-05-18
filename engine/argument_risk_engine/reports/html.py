from __future__ import annotations

from html import escape
from typing import Any


def render_html_report(result: dict[str, Any]) -> str:
    claims = result.get("claims", []) or []
    risks = result.get("risks", []) or [risk for claim in claims for risk in claim.get("detected_risks", [])]
    findings = "".join(_risk_html(risk) for risk in risks) or "<p>No risk findings were detected by the current analysis configuration.</p>"
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Argument Risk Report</title></head>
<body>
  <h1>Argument Risk Report</h1>
  <p><strong>Analysis ID:</strong> {escape(str(result.get('analysis_id') or result.get('text_id', 'unknown')))}</p>
  <p><strong>Overall risk score:</strong> {escape(str(result.get('overall_risk_score', 0)))}</p>
  <p><strong>Risk level:</strong> {escape(str(result.get('risk_level', 'unknown')))}</p>
  <p><em>Metrics and reports are review aids only and do not claim scientific validation.</em></p>
  <h2>Summary</h2>
  <ul>
    <li>Claims reviewed: {len(claims)}</li>
    <li>Detected risks: {len(risks)}</li>
    <li>Needs human review: {escape(str(bool(result.get('needs_human_review', False))))}</li>
  </ul>
  <h2>Findings</h2>
  {findings}
</body>
</html>
"""


def _risk_html(risk: dict[str, Any]) -> str:
    return f"""<section>
  <h3>{escape(str(risk.get('label', risk.get('risk_id', 'Finding'))))}</h3>
  <ul>
    <li>Risk ID: <code>{escape(str(risk.get('risk_id', '')))}</code></li>
    <li>Category: {escape(str(risk.get('category', '')))}</li>
    <li>Severity: {escape(str(risk.get('severity', '')))}</li>
    <li>Confidence: {escape(str(risk.get('confidence', 0)))}</li>
    <li>Evidence: {escape(str(risk.get('evidence_span', '')))}</li>
    <li>Human review recommended: {escape(str(bool(risk.get('needs_human_review', False))))}</li>
  </ul>
  <p>{escape(str(risk.get('explanation', '')))}</p>
</section>"""
