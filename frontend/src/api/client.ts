import type {
  ActiveProviderResponse,
  AnalysisRequest,
  AnalysisResponse,
  EvaluationResult,
  GeneratedReport,
  ProviderListResponse,
  ProviderProfile,
  ProviderTestResponse,
  ReportFormat,
  ReviewFeedback,
  ReviewRecord,
  TaxonomyCoverage,
  TaxonomyEntry,
  TaxonomyImportResult,
  TaxonomyPackSummary,
  TaxonomyQualityReport,
  TaxonomyValidationResult,
} from './types'

export const API_BASE = (import.meta.env.VITE_API_BASE ?? '/api').replace(/\/$/, '')
const REVIEW_KEY = 'are.review.records'
const REPORT_KEY = 'are.generated.reports'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  const contentType = response.headers.get('content-type') ?? ''
  const payload = contentType.includes('application/json') ? await response.json() : await response.text()
  if (!response.ok || (typeof payload === 'object' && payload !== null && 'detail' in payload)) {
    const detail = typeof payload === 'object' && payload !== null && 'detail' in payload ? String((payload as { detail: unknown }).detail) : response.statusText
    throw new Error(detail || `Request failed: ${response.status}`)
  }
  return payload as T
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

export function downloadText(content: string, filename: string, type = 'text/plain'): void {
  downloadBlob(new Blob([content], { type }), filename)
}

export async function analyzeText(payload: AnalysisRequest): Promise<AnalysisResponse> {
  return request<AnalysisResponse>('/analysis/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function fetchTaxonomy(params: URLSearchParams = new URLSearchParams()): Promise<TaxonomyEntry[]> {
  const query = params.toString()
  const payload = await request<{ entries: TaxonomyEntry[] }>(`/taxonomy${query ? `?${query}` : ''}`)
  return payload.entries
}

export async function fetchTaxonomyPacks(): Promise<TaxonomyPackSummary[]> {
  return (await request<{ packs: TaxonomyPackSummary[] }>('/taxonomy-workbench/packs')).packs
}

export async function fetchTaxonomyCoverage(): Promise<TaxonomyCoverage> {
  return request<TaxonomyCoverage>('/taxonomy-workbench/coverage')
}

export async function fetchTaxonomyQuality(): Promise<TaxonomyQualityReport> {
  return request<TaxonomyQualityReport>('/taxonomy-workbench/quality-report')
}

export async function validateTaxonomy(): Promise<TaxonomyValidationResult> {
  return request<TaxonomyValidationResult>('/taxonomy-workbench/validate', { method: 'POST' })
}

export async function importTaxonomyWorkbook(file: File): Promise<TaxonomyImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  return request<TaxonomyImportResult>('/taxonomy-workbench/import-excel', { method: 'POST', body: formData })
}

export async function exportTaxonomyWorkbook(): Promise<void> {
  const response = await fetch(`${API_BASE}/taxonomy-workbench/export-excel`)
  if (!response.ok) throw new Error('Taxonomy workbook export failed')
  const disposition = response.headers.get('content-disposition') ?? ''
  const filename = disposition.match(/filename="?([^";]+)"?/)?.[1] ?? 'taxonomy.xlsx'
  downloadBlob(await response.blob(), filename)
}

export async function updateTaxonomyActivation(riskId: string, activationStatus: string, enabledForClassification?: boolean): Promise<TaxonomyEntry> {
  const payload = await request<{ entry: TaxonomyEntry }>(`/taxonomy-workbench/entries/${encodeURIComponent(riskId)}/activation`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ activation_status: activationStatus, enabled_for_classification: enabledForClassification }),
  })
  return payload.entry
}

export async function fetchModelProviders(): Promise<ProviderProfile[]> {
  const payload = await request<ProviderListResponse>('/settings/model-providers')
  return payload.providers
}

export async function saveModelProvider(profile: ProviderProfile): Promise<ProviderProfile> {
  return request<ProviderProfile>(`/settings/model-providers/${encodeURIComponent(profile.provider_id)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
  })
}

export async function fetchActiveModelProvider(): Promise<ActiveProviderResponse> {
  return request<ActiveProviderResponse>('/settings/active-model-provider')
}

export async function setActiveModelProvider(providerId: string): Promise<ActiveProviderResponse> {
  return request<ActiveProviderResponse>('/settings/active-model-provider', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider_id: providerId }),
  })
}

export async function testModelProvider(providerId: string): Promise<ProviderTestResponse> {
  return request<ProviderTestResponse>(`/settings/model-providers/${encodeURIComponent(providerId)}/test`, { method: 'POST' })
}

export async function runEvaluation(): Promise<EvaluationResult> {
  return request<EvaluationResult>('/evaluation/run')
}

export async function submitReviewFeedback(feedback: ReviewFeedback): Promise<void> {
  await request<{ status: string }>('/review/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(feedback),
  })
}

function readStored<T>(key: string, fallback: T): T {
  try { return JSON.parse(localStorage.getItem(key) || '') as T } catch { return fallback }
}

function writeStored<T>(key: string, value: T): void {
  localStorage.setItem(key, JSON.stringify(value))
}

export function listReviewRecords(): ReviewRecord[] {
  return readStored<ReviewRecord[]>(REVIEW_KEY, [])
}

export function saveReviewRecord(record: ReviewRecord): void {
  const records = listReviewRecords().filter(item => item.id !== record.id)
  writeStored(REVIEW_KEY, [record, ...records].slice(0, 50))
}

export function updateReviewRecord(record: ReviewRecord): void {
  writeStored(REVIEW_KEY, listReviewRecords().map(item => item.id === record.id ? record : item))
}

export function listReports(): GeneratedReport[] {
  return readStored<GeneratedReport[]>(REPORT_KEY, [])
}

export function saveGeneratedReport(report: GeneratedReport): void {
  writeStored(REPORT_KEY, [report, ...listReports().filter(item => item.id !== report.id)].slice(0, 50))
}

export function downloadReport(report: GeneratedReport, format: ReportFormat): void {
  const content = format === 'json' ? report.json : format === 'html' ? report.html : report.markdown
  if (!content) throw new Error(`No ${format} preview is available for this report`)
  const extension = format === 'markdown' ? 'md' : format
  const type = format === 'json' ? 'application/json' : format === 'html' ? 'text/html' : 'text/markdown'
  downloadText(content, `${report.id}.${extension}`, type)
}

export async function fetchDemoReport(): Promise<string> {
  const response = await fetch(`${API_BASE}/reports/demo.md`)
  if (!response.ok) throw new Error('Could not fetch demo report')
  return response.text()
}
