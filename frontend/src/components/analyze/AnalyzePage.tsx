import { useEffect, useState } from 'react'
import { analyzeText, fetchActiveModelProvider, fetchModelProviders, saveReviewRecord } from '../../api/client'
import type { AnalysisResponse, ProviderProfile } from '../../api/types'
import { Card } from '../shared/Card'
import { ErrorState } from '../shared/ErrorState'
import { LoadingState } from '../shared/LoadingState'
import { AnalysisReport } from './AnalysisReport'
import { TextInputPanel } from './TextInputPanel'

export function AnalyzePage() {
  const [text, setText] = useState('Everyone always caused this problem because of that policy.')
  const [providerId, setProviderId] = useState('deterministic_baseline')
  const [providers, setProviders] = useState<ProviderProfile[]>([])
  const [topK, setTopK] = useState(8)
  const [includeHealthy, setIncludeHealthy] = useState(true)
  const [allowFallback, setAllowFallback] = useState(true)
  const [result, setResult] = useState<AnalysisResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => { Promise.all([fetchModelProviders(), fetchActiveModelProvider()]).then(([items, active]) => { setProviders(items); setProviderId(active.provider_id) }).catch(() => undefined) }, [])

  async function run() {
    setLoading(true); setError('')
    try {
      const analysis = await analyzeText({ text, model_provider_id: providerId, top_k: topK, include_healthy_patterns: includeHealthy, allow_deterministic_fallback: allowFallback })
      setResult(analysis)
      saveReviewRecord({ id: analysis.text_id, created_at: new Date().toISOString(), analysis, source_text: text })
    } catch (err) { setError(err instanceof Error ? err.message : 'Unknown analysis error') } finally { setLoading(false) }
  }

  return <div className="page-grid two-column">
    <Card className="stack"><div className="section-header"><div><h2>Analyze text</h2><p className="muted">Choose the active backend provider, tune retrieval breadth, and produce a reviewable risk report.</p></div></div>
      <label className="field-label">Model provider<select value={providerId} onChange={event => setProviderId(event.target.value)}>{providers.length ? providers.map(provider => <option key={provider.provider_id} value={provider.provider_id}>{provider.label}</option>) : <option value={providerId}>{providerId}</option>}</select></label>
      <TextInputPanel text={text} setText={setText} providerId={providerId} providers={providers} topK={topK} setTopK={setTopK} includeHealthy={includeHealthy} setIncludeHealthy={setIncludeHealthy} allowFallback={allowFallback} setAllowFallback={setAllowFallback} loading={loading} onAnalyze={run} />
      {error ? <ErrorState message={error} title="Analysis failed" /> : null}
    </Card>
    <Card className="stack">{loading ? <LoadingState label="Analyzing text with backend…" /> : result ? <AnalysisReport result={result} sourceText={text} /> : <p className="muted">Run an analysis to see scores, claim cards, risk cards, highlighted evidence, healthy patterns, warnings, and export controls.</p>}</Card>
  </div>
}
