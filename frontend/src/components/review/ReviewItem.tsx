import { useState } from 'react'
import { submitReviewFeedback, updateReviewRecord } from '../../api/client'
import type { ReviewDecision, ReviewRecord } from '../../api/types'
import { Button } from '../shared/Button'
import { Badge } from '../shared/Badge'
import { FeedbackControls } from './FeedbackControls'

export function ReviewItem({ record, onSaved }: { record: ReviewRecord; onSaved: () => void }) {
  const [decision, setDecision] = useState<ReviewDecision>(record.feedback?.decision ?? 'correct')
  const [labels, setLabels] = useState(record.feedback?.corrected_labels?.join(', ') ?? '')
  const [notes, setNotes] = useState(record.feedback?.notes ?? '')
  const [saving, setSaving] = useState(false)
  const riskIds = Array.from(new Set(record.analysis.claims.flatMap(claim => claim.detected_risks.map(risk => risk.risk_id))))
  async function save() {
    setSaving(true)
    const feedback = { analysis_id: record.analysis.text_id, taxonomy_id: riskIds[0] ?? null, decision, notes, corrected_labels: labels.split(',').map(label => label.trim()).filter(Boolean) }
    try { await submitReviewFeedback(feedback); updateReviewRecord({ ...record, feedback }); onSaved() } finally { setSaving(false) }
  }
  return <article className="review-item">
    <div className="section-header compact"><div><h3>{record.analysis.text_id}</h3><p className="muted">{new Date(record.created_at).toLocaleString()}</p></div><Badge tone={record.feedback ? 'success' : 'warning'}>{record.feedback ? record.feedback.decision : 'unreviewed'}</Badge></div>
    <p className="quote-block">{record.source_text}</p>
    <p className="muted">Detected labels: {riskIds.length ? riskIds.join(', ') : 'none'}</p>
    <FeedbackControls decision={decision} onDecision={setDecision} />
    <label className="field-label">Corrected labels<input value={labels} onChange={event => setLabels(event.target.value)} placeholder="comma-separated taxonomy ids" /></label>
    <label className="field-label">Notes<textarea rows={4} value={notes} onChange={event => setNotes(event.target.value)} placeholder="Reviewer rationale, evidence notes, or follow-up questions" /></label>
    <Button onClick={save} disabled={saving}>{saving ? 'Saving…' : 'Save review notes'}</Button>
  </article>
}
