import type { ActiveProviderResponse, AnalysisResponse, ProviderListResponse, ProviderProfile, ProviderTestResponse, TaxonomyCoverage, TaxonomyEntry, TaxonomyImportResult, TaxonomyPackSummary, TaxonomyQualityReport, TaxonomyValidationResult } from './types'

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

export async function fetchTaxonomy(params: URLSearchParams = new URLSearchParams()): Promise<TaxonomyEntry[]> {
  const query = params.toString()
  const response = await fetch(`${API_BASE}/taxonomy${query ? `?${query}` : ''}`)
  if (!response.ok) throw new Error('Taxonomy request failed')
  const payload = await response.json()
  return payload.entries
}

export async function searchTaxonomy(q: string): Promise<TaxonomyEntry[]> {
  const response = await fetch(`${API_BASE}/taxonomy/search?q=${encodeURIComponent(q)}`)
  if (!response.ok) throw new Error('Taxonomy search failed')
  const payload = await response.json()
  return payload.entries
}

export async function fetchTaxonomyPacks(): Promise<TaxonomyPackSummary[]> {
  const response = await fetch(`${API_BASE}/taxonomy-workbench/packs`)
  if (!response.ok) throw new Error('Taxonomy packs request failed')
  return (await response.json()).packs
}

export async function fetchTaxonomyCoverage(): Promise<TaxonomyCoverage> {
  const response = await fetch(`${API_BASE}/taxonomy-workbench/coverage`)
  if (!response.ok) throw new Error('Taxonomy coverage request failed')
  return response.json()
}

export async function fetchTaxonomyQuality(): Promise<TaxonomyQualityReport> {
  const response = await fetch(`${API_BASE}/taxonomy-workbench/quality-report`)
  if (!response.ok) throw new Error('Taxonomy quality request failed')
  return response.json()
}

export async function validateTaxonomy(): Promise<TaxonomyValidationResult> {
  const response = await fetch(`${API_BASE}/taxonomy-workbench/validate`, { method: 'POST' })
  if (!response.ok) throw new Error('Taxonomy validation failed')
  return response.json()
}

export async function importTaxonomyWorkbook(file: File): Promise<TaxonomyImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${API_BASE}/taxonomy-workbench/import-excel`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) throw new Error('Taxonomy workbook import failed')
  return response.json()
}

export function exportTaxonomyWorkbook(): void {
  window.location.href = `${API_BASE}/taxonomy-workbench/export-excel`
}

export async function updateTaxonomyActivation(riskId: string, activationStatus: string, enabledForClassification?: boolean): Promise<TaxonomyEntry> {
  const response = await fetch(`${API_BASE}/taxonomy-workbench/entries/${encodeURIComponent(riskId)}/activation`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ activation_status: activationStatus, enabled_for_classification: enabledForClassification }),
  })
  if (!response.ok) throw new Error('Activation update failed')
  const payload = await response.json()
  if (payload.detail) throw new Error(payload.detail)
  return payload.entry
}


export async function fetchModelProviders(): Promise<ProviderProfile[]> {
  const response = await fetch(`${API_BASE}/settings/model-providers`)
  if (!response.ok) throw new Error('Model providers request failed')
  const payload: ProviderListResponse = await response.json()
  return payload.providers
}

export async function saveModelProvider(profile: ProviderProfile): Promise<ProviderProfile> {
  const response = await fetch(`${API_BASE}/settings/model-providers/${encodeURIComponent(profile.provider_id)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
  })
  if (!response.ok) throw new Error('Model provider update failed')
  const payload = await response.json()
  if (payload.detail) throw new Error(payload.detail)
  return payload
}

export async function fetchActiveModelProvider(): Promise<ActiveProviderResponse> {
  const response = await fetch(`${API_BASE}/settings/active-model-provider`)
  if (!response.ok) throw new Error('Active provider request failed')
  return response.json()
}

export async function setActiveModelProvider(providerId: string): Promise<ActiveProviderResponse> {
  const response = await fetch(`${API_BASE}/settings/active-model-provider`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider_id: providerId }),
  })
  if (!response.ok) throw new Error('Active provider update failed')
  const payload = await response.json()
  if (payload.detail) throw new Error(payload.detail)
  return payload
}

export async function testModelProvider(providerId: string): Promise<ProviderTestResponse> {
  const response = await fetch(`${API_BASE}/settings/model-providers/${encodeURIComponent(providerId)}/test`, { method: 'POST' })
  if (!response.ok) throw new Error('Provider test failed')
  const payload = await response.json()
  if (payload.detail) throw new Error(payload.detail)
  return payload
}
