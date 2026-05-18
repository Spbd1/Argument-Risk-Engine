import type { ProviderProfile } from '../../api/types'
import { Button } from '../shared/Button'
import { Badge } from '../shared/Badge'

const examples = [
  'Everyone who supports that policy caused the problem, so their entire proposal should be rejected.',
  'The study has a small sample and wide confidence intervals, so the conclusion should be treated cautiously.',
  'If this reform passes, society will collapse within months and no family will be safe.',
]

export function TextInputPanel({ text, setText, providerId, providers, topK, setTopK, includeHealthy, setIncludeHealthy, allowFallback, setAllowFallback, loading, onAnalyze }: {
  text: string
  setText: (value: string) => void
  providerId: string
  providers: ProviderProfile[]
  topK: number
  setTopK: (value: number) => void
  includeHealthy: boolean
  setIncludeHealthy: (value: boolean) => void
  allowFallback: boolean
  setAllowFallback: (value: boolean) => void
  loading: boolean
  onAnalyze: () => void
}) {
  const provider = providers.find(item => item.provider_id === providerId)
  return <div className="stack">
    <div className="button-row examples">{examples.map((example, index) => <Button key={example} variant="secondary" onClick={() => setText(example)}>Load example {index + 1}</Button>)}</div>
    <textarea value={text} onChange={event => setText(event.target.value)} rows={10} placeholder="Paste or type an argument, policy claim, transcript excerpt, or source text for taxonomy-grounded analysis." />
    <div className="control-grid">
      <label className="field-label">Provider status <span><Badge tone={provider?.enabled === false ? 'warning' : 'success'}>{provider ? provider.label : providerId}</Badge></span></label>
      <label className="field-label">top_k<input type="number" min={1} max={50} value={topK} onChange={event => setTopK(Number(event.target.value))} /></label>
      <label className="check"><input type="checkbox" checked={includeHealthy} onChange={event => setIncludeHealthy(event.target.checked)} /> Include healthy patterns</label>
      <label className="check"><input type="checkbox" checked={allowFallback} onChange={event => setAllowFallback(event.target.checked)} /> Allow deterministic fallback</label>
    </div>
    <Button onClick={onAnalyze} disabled={loading || !text.trim()}>{loading ? 'Analyzing…' : 'Analyze text'}</Button>
  </div>
}
