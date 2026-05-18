import { useRef, useState } from 'react'

import { importTaxonomyWorkbook } from '../../api/client'
import { Card } from '../shared/Card'

export function TaxonomyImportExportPanel() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [message, setMessage] = useState('Select a user-managed .xlsx taxonomy workbook to import.')
  const [busy, setBusy] = useState(false)

  async function onUpload() {
    const file = inputRef.current?.files?.[0]
    if (!file) {
      setMessage('Choose an .xlsx workbook first.')
      return
    }
    setBusy(true)
    try {
      const result = await importTaxonomyWorkbook(file)
      setMessage(`Imported ${result.entry_count} taxonomy entries with ${result.errors.length} errors and ${result.warnings.length} warnings.`)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Taxonomy import failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card>
      <h2>Taxonomy import/export</h2>
      <p className="muted">
        The real taxonomy workbook is imported from your local machine and is intentionally not committed to Git.
      </p>
      <input ref={inputRef} type="file" accept=".xlsx,.xls" />
      <button type="button" onClick={onUpload} disabled={busy}>{busy ? 'Importing…' : 'Import workbook'}</button>
      <p className="muted">{message}</p>
    </Card>
  )
}
