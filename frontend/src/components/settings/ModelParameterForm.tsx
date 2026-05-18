import type { ProviderProfile } from '../../api/types'

const numericFields = [
  { key: 'timeout_seconds', label: 'Timeout (seconds)', min: 1, step: 1 },
  { key: 'max_tokens', label: 'Max tokens', min: 0, step: 1 },
  { key: 'temperature', label: 'Temperature', min: 0, step: 0.1 },
] as const

export function ModelParameterForm({ profile, onChange }: { profile: ProviderProfile; onChange: (profile: ProviderProfile) => void }) {
  const update = (key: keyof ProviderProfile, value: string | number | boolean) => onChange({ ...profile, [key]: value })

  return <div className="settings-form">
    <label className="field-label">Base URL
      <input value={profile.base_url} placeholder="http://localhost:1234/v1" onChange={event => update('base_url', event.target.value)} />
    </label>
    <label className="field-label">Model name
      <input value={profile.model_name} placeholder="local-model or gpt-4.1-mini" onChange={event => update('model_name', event.target.value)} />
    </label>
    <label className="field-label">API key environment variable
      <input value={profile.api_key_env_var} placeholder="OPENAI_API_KEY" onChange={event => update('api_key_env_var', event.target.value)} />
      <span className="muted">Enter the environment variable name only. Raw paid API keys are never stored in the browser.</span>
    </label>
    {numericFields.map(field => <label className="field-label" key={field.key}>{field.label}
      <input type="number" min={field.min} step={field.step} value={profile[field.key]} onChange={event => update(field.key, Number(event.target.value))} />
    </label>)}
  </div>
}
