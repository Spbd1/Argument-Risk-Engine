import type { ReviewRecord } from '../../api/types'
import { EmptyState } from '../shared/EmptyState'
import { ReviewItem } from './ReviewItem'

export function ReviewQueue({ records, onSaved }: { records: ReviewRecord[]; onSaved: () => void }) {
  if (!records.length) return <EmptyState title="No prior analyses" message="Run an analysis first; recent outputs are saved locally for review and feedback submission." />
  return <div className="review-list">{records.map(record => <ReviewItem key={record.id} record={record} onSaved={onSaved} />)}</div>
}
