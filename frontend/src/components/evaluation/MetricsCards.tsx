import type { EvaluationResult } from '../../api/types'

export function MetricsCards({ result }: { result: EvaluationResult }) {
  const metrics = result.metrics ?? {}
  const fallback = { Items: Number(result.items ?? 0), Analyses: result.analyses?.length ?? 0 }
  const entries = Object.keys(metrics).length ? Object.entries(metrics) : Object.entries(fallback)
  return <div className="metric-grid">{entries.map(([name, value]) => <div key={name}><strong>{typeof value === 'number' ? value.toFixed(Number.isInteger(value) ? 0 : 2) : String(value)}</strong><span>{name.replaceAll('_', ' ')}</span></div>)}</div>
}
