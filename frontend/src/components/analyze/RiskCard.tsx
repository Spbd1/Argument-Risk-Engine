import type { DetectedRisk } from '../../api/types'
import { Badge } from '../shared/Badge'

function tone(level: string) { return level === 'high' || level === 'critical' ? 'danger' : level === 'medium' ? 'warning' : 'info' }
export function RiskCard({ risk }: { risk: DetectedRisk }) {
  return <article className="risk-card">
    <div className="section-header compact"><div><h4>{risk.label}</h4><p className="muted">{risk.risk_id} · {risk.category}</p></div><Badge tone={tone(risk.risk_level)}>{risk.risk_level}</Badge></div>
    <dl className="inline-stats"><div><dt>Score</dt><dd>{risk.risk_score.toFixed(2)}</dd></div><div><dt>Confidence</dt><dd>{Math.round(risk.confidence * 100)}%</dd></div><div><dt>Severity</dt><dd>{risk.severity}</dd></div></dl>
    <p>{risk.explanation}</p>
    {risk.evidence_span ? <p className="evidence"><strong>Evidence:</strong> “{risk.evidence_span}”</p> : null}
    {risk.false_positive_warning ? <p className="warning">{risk.false_positive_warning}</p> : null}
    {risk.needs_human_review ? <Badge tone="warning">Human review recommended</Badge> : null}
  </article>
}
