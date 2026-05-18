from argument_risk_engine.reports.markdown import render_markdown_report

from backend.app.services.analyzer_service import analyze


def demo_report() -> str:
    return render_markdown_report(analyze("Everyone always caused this problem."))
