import type { AnalysisResponse } from '../../api/types'
import { ClaimCard } from './ClaimCard'
export function AnalysisReport({ result }: { result: AnalysisResponse }) { return <section><h2>Report</h2><p>Analysis ID: {result.analysis_id}</p><p>Risks: {String(result.summary.risk_count ?? 0)}</p>{result.claims.map((claim, idx) => <ClaimCard key={idx} claim={claim} />)}</section> }
