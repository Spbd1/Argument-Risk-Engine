import type { AnalyzedClaim } from '../../api/types'
import { Badge } from '../shared/Badge'
import { EmptyState } from '../shared/EmptyState'
import { EvidenceHighlight } from './EvidenceHighlight'
import { RiskCard } from './RiskCard'

export function ClaimCard({ claim }: { claim: AnalyzedClaim }) {
  const firstRisk = claim.detected_risks[0]
  return <article className="claim-card">
    <div className="section-header compact"><div><h3>Claim {claim.claim_id}</h3><p className="muted">{claim.claim_type}</p></div><Badge>{claim.detected_risks.length} risks</Badge></div>
    <p className="claim-text">{firstRisk ? <EvidenceHighlight text={claim.text} start={Math.max(0, firstRisk.evidence_start_char - claim.start_char)} end={Math.max(0, firstRisk.evidence_end_char - claim.start_char)} /> : claim.text}</p>
    {claim.warnings.length ? <ul className="issue-list warning-list">{claim.warnings.map(warning => <li key={warning}>{warning}</li>)}</ul> : null}
    {claim.detected_risks.length ? <div className="risk-list">{claim.detected_risks.map(risk => <RiskCard key={`${claim.claim_id}-${risk.risk_id}`} risk={risk} />)}</div> : <EmptyState title="No risk labels" message="This claim did not match active taxonomy entries." />}
    {claim.healthy_patterns.length ? <div className="healthy-panel"><h4>Healthy patterns</h4>{claim.healthy_patterns.map((pattern, index) => <p key={index}><strong>{String(pattern.label ?? pattern.pattern ?? 'Healthy signal')}:</strong> {String(pattern.explanation ?? pattern.evidence_span ?? '')}</p>)}</div> : null}
  </article>
}
