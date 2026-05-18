import type { Claim } from '../../api/types'
import { RiskCard } from './RiskCard'
export function ClaimCard({ claim }: { claim: Claim }) { return <article className="claim"><h3>{claim.text}</h3>{claim.risks.length ? claim.risks.map(risk => <RiskCard key={risk.taxonomy_id} risk={risk} />) : <p className="muted">No taxonomy match.</p>}</article> }
