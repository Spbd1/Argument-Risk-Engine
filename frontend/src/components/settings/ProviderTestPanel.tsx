import type { ProviderProfile, ProviderTestResponse } from '../../api/types'
import { Button } from '../shared/Button'
import { Badge } from '../shared/Badge'

export function ProviderTestPanel({ profile, result, isTesting, onTest }: { profile: ProviderProfile; result?: ProviderTestResponse; isTesting: boolean; onTest: () => void }) {
  const status = result?.status ?? (profile.enabled ? 'not tested' : 'not configured')
  return <div className="provider-test-panel">
    <div className="button-row">
      <Button onClick={onTest} disabled={isTesting}>{isTesting ? 'Testing…' : 'Test connection'}</Button>
      <Badge>{status}</Badge>
      {result ? <span className="muted">{result.latency_ms} ms</span> : null}
    </div>
    {result?.detail ? <p>{result.detail}</p> : null}
    {result?.models?.length ? <p className="muted">Models: {result.models.slice(0, 5).join(', ')}{result.models.length > 5 ? '…' : ''}</p> : null}
    {result?.warnings?.length ? <ul className="issue-list">{result.warnings.map(warning => <li key={warning} className="error">{warning}</li>)}</ul> : null}
  </div>
}
