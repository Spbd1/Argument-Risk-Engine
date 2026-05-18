import type { AnalysisResponse, GeneratedReport } from '../../api/types'
import { downloadText, saveGeneratedReport } from '../../api/client'
import { Button } from '../shared/Button'

export function analysisToMarkdown(result: AnalysisResponse, sourceText: string): string {
  const lines = [`# Argument Risk Analysis`, '', `Analysis ID: ${result.text_id}`, `Provider: ${result.model_provider_id} (${result.model_name})`, `Overall risk score: ${result.overall_risk_score.toFixed(2)}`, `Risk level: ${result.risk_level}`, `Needs human review: ${result.needs_human_review ? 'yes' : 'no'}`, '', '## Source text', '', sourceText, '', '## Claims']
  result.claims.forEach(claim => {
    lines.push('', `### ${claim.claim_id}`, claim.text)
    if (!claim.detected_risks.length) lines.push('', 'No detected taxonomy risks.')
    claim.detected_risks.forEach(risk => lines.push('', `- **${risk.label}** (${risk.risk_level}, score ${risk.risk_score.toFixed(2)}): ${risk.explanation}`, `  - Evidence: “${risk.evidence_span}”`))
    if (claim.healthy_patterns.length) lines.push('', `Healthy patterns: ${claim.healthy_patterns.map(item => String(item.label ?? item.pattern ?? 'signal')).join(', ')}`)
  })
  if (result.warnings.length) lines.push('', '## Warnings', ...result.warnings.map(warning => `- ${warning}`))
  return lines.join('\n')
}

export function ExportButtons({ result, sourceText }: { result: AnalysisResponse; sourceText: string }) {
  const markdown = analysisToMarkdown(result, sourceText)
  const json = JSON.stringify(result, null, 2)
  const saveReport = () => saveGeneratedReport({
    id: result.text_id,
    title: `Analysis ${result.text_id}`,
    created_at: new Date().toISOString(),
    analysis_id: result.text_id,
    formats: ['json', 'markdown', 'html'],
    json,
    markdown,
    html: `<article><pre>${markdown.replace(/[&<>]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[char] ?? char))}</pre></article>`,
  } satisfies GeneratedReport)
  return <div className="button-row">
    <Button variant="secondary" onClick={() => downloadText(json, `${result.text_id}.json`, 'application/json')}>Export JSON</Button>
    <Button variant="secondary" onClick={() => downloadText(markdown, `${result.text_id}.md`, 'text/markdown')}>Export Markdown</Button>
    <Button variant="secondary" onClick={() => navigator.clipboard.writeText(markdown)}>Copy report</Button>
    <Button variant="secondary" onClick={saveReport}>Save to Reports</Button>
  </div>
}
