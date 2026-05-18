import type { EvaluationResult } from '../../api/types'
import { EmptyState } from '../shared/EmptyState'

function rows(result: EvaluationResult, key: 'false_positives' | 'false_negatives' | 'evidence_span_misses') { return (result[key] ?? []) as Array<Record<string, unknown>> }
export function ErrorAnalysisTable({ result }: { result: EvaluationResult }) {
  const sections = [
    ['False positives', rows(result, 'false_positives')],
    ['False negatives', rows(result, 'false_negatives')],
    ['Evidence span misses', rows(result, 'evidence_span_misses')],
  ] as const
  if (sections.every(([, items]) => !items.length)) return <EmptyState title="No detailed error rows" message="The backend returned aggregate evaluation output only. Raw evaluation JSON remains available below." />
  return <div className="stack">{sections.map(([title, items]) => <section key={title}><h3>{title}</h3>{items.length ? <div className="table-wrap"><table><tbody>{items.map((item, index) => <tr key={index}><td><pre>{JSON.stringify(item, null, 2)}</pre></td></tr>)}</tbody></table></div> : <p className="muted">None reported.</p>}</section>)}</div>
}
