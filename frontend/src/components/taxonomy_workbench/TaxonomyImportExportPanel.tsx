import { useRef, useState } from 'react'

import { exportTaxonomyWorkbook, importTaxonomyWorkbook, validateTaxonomy } from '../../api/client'
import type { TaxonomyValidationResult } from '../../api/types'
import { Card } from '../shared/Card'

export function TaxonomyImportExportPanel({ onChanged }: { onChanged: () => void }) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [message, setMessage] = useState('Select a user-managed .xlsx taxonomy workbook to import.')
  const [validation, setValidation] = useState<TaxonomyValidationResult | null>(null)
  const [busy, setBusy] = useState(false)

  async function onUpload() {
    const file = inputRef.current?.files?.[0]
    if (!file) return setMessage('Choose an .xlsx workbook first.')
    if (!file.name.endsWith('.xlsx')) return setMessage('Only .xlsx workbooks can be imported.')
    setBusy(true)
    try {
      const result = await importTaxonomyWorkbook(file)
      setMessage(`Imported ${result.entry_count} taxonomy entries with ${result.errors.length} errors and ${result.warnings.length} warnings. Backups: ${result.backup_paths?.length ?? 0}.`)
      onChanged()
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Taxonomy import failed')
    } finally {
      setBusy(false)
    }
  }

  async function onValidate() {
    setBusy(true)
    try {
      const result = await validateTaxonomy()
      setValidation(result)
      setMessage(`Validation ${result.ok ? 'passed' : 'found issues'}: ${result.errors.length} errors, ${result.warnings.length} warnings. No files were modified.`)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Validation failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card>
      <h2>Taxonomy import/export</h2>
      <p className="muted">Import a local .xlsx taxonomy workbook, validate without changing files, or download a fresh .xlsx export.</p>
      <div className="button-row"><input ref={inputRef} type="file" accept=".xlsx" /><button type="button" onClick={onUpload} disabled={busy}>{busy ? 'Working…' : 'Import Excel'}</button><button type="button" onClick={() => exportTaxonomyWorkbook()}>Export Excel</button><button type="button" onClick={onValidate} disabled={busy}>Validate taxonomy</button></div>
      <p className="muted">{message}</p>
      {validation && <ul className="issue-list">{[...validation.errors, ...validation.warnings].slice(0, 6).map((issue) => <li key={`${issue.code}-${issue.entry_id}-${issue.message}`}>{issue.severity}: {issue.message}</li>)}</ul>}
    </Card>
  )
}
