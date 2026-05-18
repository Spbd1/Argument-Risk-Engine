import type { AnalysisResponse, TaxonomyEntry, TaxonomyImportResult } from './types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api'

export async function analyzeText(text: string): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE}/analysis/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!response.ok) throw new Error('Analysis request failed')
  return response.json()
}

export async function fetchTaxonomy(): Promise<TaxonomyEntry[]> {
  const response = await fetch(`${API_BASE}/taxonomy`)
  if (!response.ok) throw new Error('Taxonomy request failed')
  const payload = await response.json()
  return payload.entries
}


export async function importTaxonomyWorkbook(file: File): Promise<TaxonomyImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${API_BASE}/taxonomy-workbench/import`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) throw new Error('Taxonomy workbook import failed')
  return response.json()
}
