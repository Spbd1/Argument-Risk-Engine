from __future__ import annotations

from typing import Any

from argument_risk_engine.reports.json_export import LIMITATIONS_NOTE


def render_markdown_report(result: dict[str, Any]) -> str:
    claims = result.get("claims", []) or []
    risks = result.get("risks", []) or [risk for claim in claims for risk in claim.get("detected_risks", [])]
    lines = [
        "# Argument Risk Report",
        "",
        f"Analysis ID: `{result.get('analysis_id') or result.get('text_id', 'unknown')}`",
        f"Overall risk score: **{result.get('overall_risk_score', 0)}**",
        f"Risk level: **{result.get('risk_level', 'unknown')}**",
        "",
        f"> {LIMITATIONS_NOTE}",
        "",
        "## Summary",
        "",
        f"- Claims reviewed: {len(claims)}",
        f"- Detected risks: {len(risks)}",
        f"- Needs human review: {bool(result.get('needs_human_review', False))}",
        "",
        "## Findings",
        "",
    ]
    if not risks:
        lines.append("No risk findings were detected by the current analysis configuration.")
    for risk in risks:
        lines.extend(
            [
                f"### {risk.get('label', risk.get('risk_id', 'Finding'))}",
                "",
                f"- Risk ID: `{risk.get('risk_id', '')}`",
                f"- Category: {risk.get('category', '')}",
                f"- Severity: {risk.get('severity', '')}",
                f"- Confidence: {risk.get('confidence', 0)}",
                f"- Evidence: {risk.get('evidence_span', '')}",
                f"- Human review recommended: {bool(risk.get('needs_human_review', False))}",
                "",
                str(risk.get("explanation", "")),
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"
