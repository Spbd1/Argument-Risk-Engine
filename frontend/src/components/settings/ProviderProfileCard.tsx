import type { ProviderProfile, ProviderTestResponse } from '../../api/types'
import { Badge } from '../shared/Badge'
import { Button } from '../shared/Button'
import { Card } from '../shared/Card'
import { ModelParameterForm } from './ModelParameterForm'
import { ProviderTestPanel } from './ProviderTestPanel'

function isRemote(profile: ProviderProfile) {
  return profile.base_url.startsWith('https://') && !profile.base_url.includes('localhost') && !profile.base_url.includes('127.0.0.1')
}

function jsonModeVerified(profile: ProviderProfile) {
  return profile.supports_json_mode === true || profile.supports_json_mode === 'yes' || profile.supports_json_mode === 'true'
}

export function ProviderProfileCard({ profile, activeProviderId, testResult, isTesting, onChange, onSave, onSelect, onTest }: {
  profile: ProviderProfile
  activeProviderId: string
  testResult?: ProviderTestResponse
  isTesting: boolean
  onChange: (profile: ProviderProfile) => void
  onSave: (profile: ProviderProfile) => void
  onSelect: (providerId: string) => void
  onTest: (providerId: string) => void
}) {
  const active = profile.provider_id === activeProviderId
  const remote = isRemote(profile)
  return <Card>
    <div className="section-header">
      <div>
        <h3>{profile.label}</h3>
        <p className="muted">{profile.provider_id} · {profile.provider_type}</p>
      </div>
      <Badge>{active ? 'Active' : profile.enabled ? 'Available' : 'Disabled'}</Badge>
    </div>
    {remote ? <p className="warning">Paid or remote provider: configure secrets in backend environment variables, not localStorage.</p> : null}
    {!jsonModeVerified(profile) ? <p className="warning">JSON mode has not been verified for this provider/model.</p> : null}
    {profile.provider_type === 'deterministic'
      ? <p>Works offline with no API key and no paid provider dependency.</p>
      : <ModelParameterForm profile={profile} onChange={onChange} />}
    <div className="button-row">
      <Button onClick={() => onSelect(profile.provider_id)} disabled={active}>Select active provider</Button>
      <Button onClick={() => onSave(profile)}>Save profile</Button>
    </div>
    <ProviderTestPanel profile={profile} result={testResult} isTesting={isTesting} onTest={() => onTest(profile.provider_id)} />
  </Card>
}
