import { useEffect, useState } from 'react'
import { listReviewRecords } from '../../api/client'
import type { ReviewRecord } from '../../api/types'
import { Card } from '../shared/Card'
import { ReviewQueue } from './ReviewQueue'

export function ReviewPage() {
  const [records, setRecords] = useState<ReviewRecord[]>([])
  const reload = () => setRecords(listReviewRecords())
  useEffect(reload, [])
  return <Card className="stack"><div className="section-header"><div><h2>Review outputs</h2><p className="muted">Review prior analysis items, mark correctness, add corrected labels, and persist notes to the backend feedback endpoint.</p></div><strong>{records.length} items</strong></div><ReviewQueue records={records} onSaved={reload} /></Card>
}
