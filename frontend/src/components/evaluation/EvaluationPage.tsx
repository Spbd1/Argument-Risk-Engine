import { useState } from 'react'
import { downloadText, runEvaluation } from '../../api/client'
import type { EvaluationResult } from '../../api/types'
import { Button } from '../shared/Button'
import { Card } from '../shared/Card'
import { ErrorState } from '../shared/ErrorState'
import { LoadingState } from '../shared/LoadingState'
import { MetricsCards } from './MetricsCards'
import { ErrorAnalysisTable } from './ErrorAnalysisTable'

export function EvaluationPage() {
  const [result, setResult] = useState<EvaluationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  async function run() { setLoading(true); setError(''); try { setResult(await runEvaluation()) } catch (err) { setError(err instanceof Error ? err.message : 'Evaluation failed') } finally { setLoading(false) } }
  return <Card className="stack"><div className="section-header"><div><h2>Evaluation</h2><p className="muted">Run the backend mini evaluation set and inspect metrics, false positives, false negatives, and evidence span misses.</p></div><Button onClick={run} disabled={loading}>{loading ? 'Running…' : 'Run evaluation'}</Button></div>{loading ? <LoadingState label="Running evaluation…" /> : null}{error ? <ErrorState message={error} /> : null}{result ? <><MetricsCards result={result} /><ErrorAnalysisTable result={result} /><details><summary>Raw evaluation JSON</summary><pre>{JSON.stringify(result, null, 2)}</pre></details><Button variant="secondary" onClick={() => downloadText(JSON.stringify(result, null, 2), 'evaluation.json', 'application/json')}>Export evaluation JSON</Button></> : <p className="muted">No evaluation run yet.</p>}</Card>
}
