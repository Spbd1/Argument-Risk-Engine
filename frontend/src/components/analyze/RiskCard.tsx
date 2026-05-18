import type { Risk } from '../../api/types'
import { Badge } from '../shared/Badge'
export function RiskCard({ risk }: { risk: Risk }) { return <div className="risk-card"><Badge>{risk.severity}</Badge><strong>{risk.name}</strong><p>{risk.explanation}</p><small>Evidence: “{risk.evidence.quote}”</small></div> }
