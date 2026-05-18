import type { TaxonomyEntry, TaxonomyFilters as Filters } from '../../api/types'

const filterFields: Array<keyof Filters> = ['category', 'pack', 'academic_status', 'academic_consensus', 'detection_level', 'activation_status', 'enabled_for_classification', 'false_positive_sensitivity']

function unique(entries: TaxonomyEntry[], field: keyof TaxonomyEntry): string[] {
  return Array.from(new Set(entries.map((entry) => String(entry[field] ?? '')).filter(Boolean))).sort()
}

export function TaxonomyFilters({ entries, filters, onChange }: { entries: TaxonomyEntry[]; filters: Filters; onChange: (filters: Filters) => void }) {
  function setFilter(name: keyof Filters, value: string) {
    onChange({ ...filters, [name]: value })
  }

  return (
    <div className="filter-grid">
      {filterFields.map((field) => {
        const options = field === 'category' ? unique(entries, 'canonical_category') : field === 'enabled_for_classification' ? ['true', 'false'] : unique(entries, field as keyof TaxonomyEntry)
        return (
          <label key={field} className="field-label">
            <span>{field.replaceAll('_', ' ')}</span>
            <select value={filters[field]} onChange={(event) => setFilter(field, event.target.value)}>
              <option value="">All</option>
              {options.map((option) => <option key={option} value={option}>{option}</option>)}
            </select>
          </label>
        )
      })}
    </div>
  )
}
