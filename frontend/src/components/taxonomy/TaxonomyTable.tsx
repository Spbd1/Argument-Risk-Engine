import type { TaxonomyEntry } from '../../api/types'
export function TaxonomyTable({ entries }: { entries: TaxonomyEntry[] }) { return <table><tbody>{entries.map(entry => <tr key={entry.id}><td>{entry.id}</td><td>{entry.name}</td><td>{entry.severity}</td></tr>)}</tbody></table> }
