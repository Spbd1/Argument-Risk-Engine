import { useState } from 'react'
import { analyzeText } from '../../api/client'
import type { AnalysisResponse } from '../../api/types'
import { Card } from '../shared/Card'
import { ErrorState } from '../shared/ErrorState'
import { AnalysisReport } from './AnalysisReport'
import { TextInputPanel } from './TextInputPanel'

export function AnalyzePage() {
  const [text, setText] = useState('Everyone always caused this problem because of that policy.')
  const [result, setResult] = useState<AnalysisResponse | null>(null)
  const [error, setError] = useState('')
  async function run() { setError(''); try { setResult(await analyzeText(text)) } catch (err) { setError(err instanceof Error ? err.message : 'Unknown error') } }
  return <Card><h2>Analyze</h2><TextInputPanel text={text} setText={setText} onAnalyze={run} />{error && <ErrorState message={error} />}{result && <AnalysisReport result={result} />}</Card>
}
