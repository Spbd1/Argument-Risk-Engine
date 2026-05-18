import type { ReviewDecision } from '../../api/types'
import { Button } from '../shared/Button'

const decisions: Array<{ value: ReviewDecision; label: string }> = [
  { value: 'correct', label: 'Correct' },
  { value: 'incorrect', label: 'Incorrect' },
  { value: 'partial', label: 'Partial' },
  { value: 'insufficient_evidence', label: 'Insufficient evidence' },
]

export function FeedbackControls({ decision, onDecision }: { decision: ReviewDecision; onDecision: (decision: ReviewDecision) => void }) {
  return <div className="segmented">{decisions.map(item => <Button key={item.value} variant={decision === item.value ? 'primary' : 'secondary'} onClick={() => onDecision(item.value)}>{item.label}</Button>)}</div>
}
