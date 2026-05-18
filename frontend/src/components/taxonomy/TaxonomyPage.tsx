import { useEffect, useMemo, useState } from 'react'
import { fetchTaxonomy } from '../../api/client'
import type { TaxonomyEntry, TaxonomyFilters as Filters } from '../../api/types'
import { Card } from '../shared/Card'
import { ErrorState } from '../shared/ErrorState'
import { LoadingState } from '../shared/LoadingState'
import { TaxonomyDetailDrawer } from './TaxonomyDetailDrawer'
import { TaxonomyFilters } from './TaxonomyFilters'
import { TaxonomyTable } from './TaxonomyTable'

const emptyFilters: Filters = { category: '', pack: '', academic_status: '', academic_consensus: '', detection_level: '', activation_status: '', enabled_for_classification: '', false_positive_sensitivity: '' }

export function TaxonomyPage() {
  const [entries, setEntries] = useState<TaxonomyEntry[]>([])
  const [query, setQuery] = useState('')
  const [filters, setFilters] = useState<Filters>(emptyFilters)
  const [selected, setSelected] = useState<TaxonomyEntry | undefined>()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => { fetchTaxonomy().then(setEntries).catch((err) => setError(err instanceof Error ? err.message : 'Could not load taxonomy')).finally(() => setLoading(false)) }, [])

  const filtered = useMemo(() => entries.filter((entry) => {
    const haystack = [entry.id, entry.name, entry.short_definition, entry.long_definition, ...entry.signals, ...entry.trigger_patterns].join(' ').toLowerCase()
    const matchesQuery = !query || haystack.includes(query.toLowerCase())
    const matchesFilters = Object.entries(filters).every(([key, value]) => !value || (key === 'category' ? entry.canonical_category === value : String(entry[key as keyof TaxonomyEntry]) === value))
    return matchesQuery && matchesFilters
  }), [entries, filters, query])

  return (
    <Card>
      <div className="section-header"><div><h2>Taxonomy</h2><p className="muted">Inspect, search, filter, and open full risk details from Chrome.</p></div><strong>{filtered.length} / {entries.length}</strong></div>
      <input className="search-box" placeholder="Search by name, id, signal, trigger pattern, or definition" value={query} onChange={(event) => setQuery(event.target.value)} />
      <TaxonomyFilters entries={entries} filters={filters} onChange={setFilters} />
      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}
      <div className="taxonomy-layout"><TaxonomyTable entries={filtered} selectedId={selected?.id} onSelect={setSelected} /><TaxonomyDetailDrawer entry={selected} onClose={() => setSelected(undefined)} /></div>
    </Card>
  )
}
