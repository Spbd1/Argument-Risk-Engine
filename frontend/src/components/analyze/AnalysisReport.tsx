import type { AnalysisResponse } from '../../api/types'
import { Badge } from '../shared/Badge'
import { ClaimCard } from './ClaimCard'
import { ExportButtons } from './ExportButtons'

function tone(level: string) { return level === 'high' || level === 'critical' ? 'danger' : level === 'medium' ? 'warning' : 'success' }
export function AnalysisReport({ result, sourceText }: { result: AnalysisResponse; sourceText: string }) {
  const riskCount = result.claims.reduce((count, claim) => count + claim.detected_risks.length, 0)
  const healthyCount = result.claims.reduce((count, claim) => count + claim.healthy_patterns.length, 0)
  return <section className="stack report">
    <div className="section-header"><div><h2>Analysis report</h2><p className="muted">Analysis ID: {result.text_id} · {result.llm_used ? 'LLM assisted' : 'Deterministic'}{result.deterministic_fallback_used ? ' · fallback used' : ''}</p></div><Badge tone={tone(result.risk_level)}>{result.risk_level}</Badge></div>
    <div className="metric-grid"><div><strong>{result.overall_risk_score.toFixed(2)}</strong><span>Overall score</span></div><div><strong>{riskCount}</strong><span>Risk labels</span></div><div><strong>{healthyCount}</strong><span>Healthy patterns</span></div><div><strong>{result.claims.length}</strong><span>Claims</span></div></div>
    {result.warnings.length ? <div className="warning"><strong>Warnings</strong><ul>{result.warnings.map(warning => <li key={warning}>{warning}</li>)}</ul></div> : null}
    <ExportButtons result={result} sourceText={sourceText} />
    {result.claims.map(claim => <ClaimCard key={claim.claim_id} claim={claim} />)}
  </section>
}
