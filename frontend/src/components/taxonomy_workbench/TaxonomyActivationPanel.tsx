import { useEffect, useState } from 'react'
import { fetchTaxonomy, updateTaxonomyActivation } from '../../api/client'
import type { TaxonomyEntry } from '../../api/types'
import { Card } from '../shared/Card'

export function TaxonomyActivationPanel({ refreshKey, onChanged }: { refreshKey: number; onChanged: () => void }) {
  const [entries, setEntries] = useState<TaxonomyEntry[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [message, setMessage] = useState('Choose an entry to activate or deactivate. A timestamped YAML backup is created before changes.')
  const selected = entries.find((entry) => entry.id === selectedId)

  useEffect(() => { fetchTaxonomy().then((items) => { setEntries(items); setSelectedId((current) => current || items[0]?.id || '') }).catch(() => setMessage('Could not load activation entries.')) }, [refreshKey])

  async function apply(status: string) {
    if (!selected) return
    if (status === 'active' && selected.false_positive_sensitivity === 'high' && !window.confirm('This entry has high false-positive sensitivity. Activate anyway?')) return
    try {
      const updated = await updateTaxonomyActivation(selected.id, status, status === 'active')
      setEntries((items) => items.map((entry) => entry.id === updated.id ? updated : entry))
      setMessage(`${updated.id} set to ${updated.activation_status}.`)
      onChanged()
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Activation update failed')
    }
  }

  return (
    <Card>
      <h2>Activation controls</h2>
      <select value={selectedId} onChange={(event) => setSelectedId(event.target.value)}>{entries.map((entry) => <option key={entry.id} value={entry.id}>{entry.name} ({entry.activation_status})</option>)}</select>
      {selected && <p className="muted">{selected.id} · false-positive sensitivity: <strong>{selected.false_positive_sensitivity}</strong> · classification {selected.enabled_for_classification ? 'enabled' : 'disabled'}</p>}
      <div className="button-row"><button type="button" onClick={() => apply('active')}>Activate</button><button type="button" onClick={() => apply('review_required')}>Deactivate / review</button><button type="button" onClick={() => apply('deprecated')}>Deprecate</button></div>
      <p className="muted">{message}</p>
    </Card>
  )
}
