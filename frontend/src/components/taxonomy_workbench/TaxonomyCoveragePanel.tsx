import type { TaxonomyCoverage } from '../../api/types'
import { Card } from '../shared/Card'

function CountMap({ title, values }: { title: string; values: Record<string, number> }) {
  return <div><h4>{title}</h4><div className="chips">{Object.entries(values).map(([key, value]) => <span className="badge" key={key}>{key}: {value}</span>)}</div></div>
}

export function TaxonomyCoveragePanel({ coverage }: { coverage?: TaxonomyCoverage }) {
  return (
    <Card>
      <h2>Coverage</h2>
      {!coverage ? <p className="muted">Loading coverage…</p> : <><div className="metric-grid"><div><strong>{coverage.entry_count}</strong><span>Total entries</span></div><div><strong>{coverage.active_count}</strong><span>Active</span></div><div><strong>{coverage.review_required_count}</strong><span>Review required</span></div><div><strong>{coverage.missing_false_positive_warnings_count}</strong><span>Missing FP warnings</span></div></div><CountMap title="By category" values={coverage.by_category} /><CountMap title="By pack" values={coverage.by_pack} /><CountMap title="By activation" values={coverage.by_activation_status} /></>}
    </Card>
  )
}
