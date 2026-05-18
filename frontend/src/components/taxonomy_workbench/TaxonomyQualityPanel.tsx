import type { TaxonomyQualityReport } from '../../api/types'
import { Card } from '../shared/Card'

export function TaxonomyQualityPanel({ report }: { report?: TaxonomyQualityReport }) {
  return (
    <Card>
      <h2>Quality warnings</h2>
      {!report ? <p className="muted">Loading quality report…</p> : <><p><strong>{report.error_count}</strong> errors · <strong>{report.warning_count}</strong> warnings · {report.ok ? 'Ready' : 'Needs attention'}</p><ul className="issue-list">{[...report.errors, ...report.warnings].slice(0, 12).map((issue) => <li key={`${issue.code}-${issue.entry_id}-${issue.message}`}><strong>{issue.code}</strong> {issue.entry_id ? `(${issue.entry_id})` : ''}: {issue.message}</li>)}</ul></>}
    </Card>
  )
}
