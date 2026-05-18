import { useEffect, useState } from 'react'
import { fetchTaxonomyCoverage, fetchTaxonomyPacks, fetchTaxonomyQuality } from '../../api/client'
import type { TaxonomyCoverage, TaxonomyPackSummary, TaxonomyQualityReport } from '../../api/types'
import { Card } from '../shared/Card'
import { TaxonomyActivationPanel } from './TaxonomyActivationPanel'
import { TaxonomyCoveragePanel } from './TaxonomyCoveragePanel'
import { TaxonomyImportExportPanel } from './TaxonomyImportExportPanel'
import { TaxonomyQualityPanel } from './TaxonomyQualityPanel'

export function TaxonomyWorkbenchPage() {
  const [coverage, setCoverage] = useState<TaxonomyCoverage>()
  const [quality, setQuality] = useState<TaxonomyQualityReport>()
  const [packs, setPacks] = useState<TaxonomyPackSummary[]>([])
  const [refreshKey, setRefreshKey] = useState(0)
  const reload = () => setRefreshKey((key) => key + 1)

  useEffect(() => { fetchTaxonomyCoverage().then(setCoverage); fetchTaxonomyQuality().then(setQuality); fetchTaxonomyPacks().then(setPacks) }, [refreshKey])

  return (
    <div className="workbench-grid">
      <Card><h2>Taxonomy Workbench</h2><p className="muted">Chrome-first controls for Excel import/export, validation, coverage review, quality warnings, and YAML-backed activation.</p><div className="chips">{packs.map((pack) => <span className="badge" key={pack.pack}>{pack.pack}: {pack.entry_count}</span>)}</div></Card>
      <TaxonomyImportExportPanel onChanged={reload} />
      <TaxonomyCoveragePanel coverage={coverage} />
      <TaxonomyQualityPanel report={quality} />
      <TaxonomyActivationPanel refreshKey={refreshKey} onChanged={reload} />
    </div>
  )
}
