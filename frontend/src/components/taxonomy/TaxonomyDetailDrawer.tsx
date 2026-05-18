import type { TaxonomyEntry } from '../../api/types'

function ListBlock({ title, items }: { title: string; items: string[] }) {
  return <section><h4>{title}</h4>{items.length ? <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul> : <p className="muted">None recorded.</p>}</section>
}

export function TaxonomyDetailDrawer({ entry, onClose }: { entry?: TaxonomyEntry; onClose: () => void }) {
  if (!entry) return <aside className="drawer"><p className="muted">Select an entry for definitions, signals, examples, false-positive warnings, references, and related risks.</p></aside>
  return (
    <aside className="drawer">
      <div className="drawer-header">
        <div><h3>{entry.name}</h3><code>{entry.id}</code></div>
        <button type="button" onClick={onClose}>Close</button>
      </div>
      <section><h4>Definitions</h4><p>{entry.short_definition || 'No short definition.'}</p><p className="muted">{entry.long_definition}</p></section>
      <ListBlock title="Signals" items={entry.signals} />
      <ListBlock title="Trigger patterns" items={entry.trigger_patterns} />
      <ListBlock title="Examples" items={[...entry.positive_examples.map((example) => `Positive: ${example}`), ...entry.negative_examples.map((example) => `Negative: ${example}`)]} />
      <ListBlock title="Exclusion criteria" items={entry.exclusion_criteria} />
      <ListBlock title="False-positive warnings" items={entry.common_false_positives} />
      <ListBlock title="Source references" items={entry.source_refs} />
      <ListBlock title="Related risks" items={entry.related_risks} />
    </aside>
  )
}
