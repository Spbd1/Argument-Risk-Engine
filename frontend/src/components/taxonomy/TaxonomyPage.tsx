import { useEffect, useState } from 'react'
import { fetchTaxonomy } from '../../api/client'
import type { TaxonomyEntry } from '../../api/types'
import { Card } from '../shared/Card'
import { TaxonomyTable } from './TaxonomyTable'
export function TaxonomyPage() { const [entries, setEntries] = useState<TaxonomyEntry[]>([]); useEffect(() => { fetchTaxonomy().then(setEntries).catch(() => setEntries([])) }, []); return <Card><h2>Taxonomy</h2><TaxonomyTable entries={entries} /></Card> }
