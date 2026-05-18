import type { TaxonomyEntry } from '../../api/types'
import { Badge } from '../shared/Badge'

export function TaxonomyTable({ entries, selectedId, onSelect }: { entries: TaxonomyEntry[]; selectedId?: string; onSelect: (entry: TaxonomyEntry) => void }) {
  return (
    <div className="table-wrap">
      <table className="taxonomy-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Category</th>
            <th>Pack</th>
            <th>Detection</th>
            <th>Status</th>
            <th>Classification</th>
            <th>FP sensitivity</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.id} className={entry.id === selectedId ? 'selected-row' : ''} onClick={() => onSelect(entry)}>
              <td><code>{entry.id}</code></td>
              <td>{entry.name}</td>
              <td>{entry.canonical_category}</td>
              <td>{entry.pack}</td>
              <td>{entry.detection_level}</td>
              <td><Badge>{entry.activation_status}</Badge></td>
              <td>{entry.enabled_for_classification ? 'Enabled' : 'Disabled'}</td>
              <td>{entry.false_positive_sensitivity}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
