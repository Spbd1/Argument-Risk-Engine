def render_markdown_report(result: dict[str, object]) -> str:
    return f"# Argument Risk Report\n\nAnalysis: {result.get('analysis_id')}\n\nRisks: {len(result.get('risks', []))}\n"
