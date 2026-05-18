import type { GeneratedReport, ReportFormat } from '../../api/types'

export function ReportPreview({ report, format }: { report?: GeneratedReport; format: ReportFormat }) {
  if (!report) return <p className="muted">Select a generated report to preview Markdown, HTML, or JSON.</p>
  const content = format === 'json' ? report.json : format === 'html' ? report.html : report.markdown
  if (!content) return <p className="muted">This report does not include {format} content.</p>
  return format === 'html' ? <iframe className="report-frame" srcDoc={content} title={report.title} /> : <pre className="report-preview">{content}</pre>
}
