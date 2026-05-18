import { useEffect, useState } from 'react'
import { fetchActiveModelProvider, fetchModelProviders, saveModelProvider, setActiveModelProvider, testModelProvider } from '../../api/client'
import type { ProviderProfile, ProviderTestResponse } from '../../api/types'
import { Card } from '../shared/Card'
import { ProviderProfileCard } from './ProviderProfileCard'

export function ModelSettingsPage() {
  const [providers, setProviders] = useState<ProviderProfile[]>([])
  const [activeProviderId, setActiveProviderId] = useState('deterministic_baseline')
  const [tests, setTests] = useState<Record<string, ProviderTestResponse>>({})
  const [testingId, setTestingId] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    Promise.all([fetchModelProviders(), fetchActiveModelProvider()])
      .then(([providerList, active]) => {
        setProviders(providerList)
        setActiveProviderId(active.provider_id)
      })
      .catch(error => setMessage(error instanceof Error ? error.message : 'Unable to load model settings'))
  }, [])

  const updateProvider = (profile: ProviderProfile) => setProviders(items => items.map(item => item.provider_id === profile.provider_id ? profile : item))
  const saveProvider = (profile: ProviderProfile) => saveModelProvider(profile).then(saved => {
    updateProvider(saved)
    setMessage(`Saved ${saved.label}`)
  }).catch(error => setMessage(error instanceof Error ? error.message : 'Save failed'))
  const selectProvider = (providerId: string) => setActiveModelProvider(providerId).then(active => {
    setActiveProviderId(active.provider_id)
    setMessage(`Active provider set to ${active.provider_id}`)
  }).catch(error => setMessage(error instanceof Error ? error.message : 'Selection failed'))
  const runTest = (providerId: string) => {
    setTestingId(providerId)
    testModelProvider(providerId)
      .then(result => setTests(current => ({ ...current, [providerId]: result })))
      .catch(error => setMessage(error instanceof Error ? error.message : 'Provider test failed'))
      .finally(() => setTestingId(''))
  }

  return <section id="model-settings" className="settings-page stack">
    <Card>
      <h2>Model Settings</h2>
      <p className="muted">Configure deterministic, local OpenAI-compatible, paid remote, or custom OpenAI-compatible providers. Provider metadata can be stored in the dashboard; paid secrets must be supplied to the backend through environment variables.</p>
      {message ? <p className="muted">{message}</p> : null}
    </Card>
    <div className="provider-grid">
      {providers.map(profile => <ProviderProfileCard
        key={profile.provider_id}
        profile={profile}
        activeProviderId={activeProviderId}
        testResult={tests[profile.provider_id]}
        isTesting={testingId === profile.provider_id}
        onChange={updateProvider}
        onSave={saveProvider}
        onSelect={selectProvider}
        onTest={runTest}
      />)}
    </div>
  </section>
}
