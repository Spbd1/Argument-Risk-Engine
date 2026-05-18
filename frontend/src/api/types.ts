export type RiskLevel = 'low' | 'medium' | 'high' | 'critical' | string

export type AnalysisRequest = {
  text: string
  mode?: string
  model_provider_id?: string
  top_k?: number
  include_healthy_patterns?: boolean
  allow_deterministic_fallback?: boolean
  include_retrieval_diagnostics?: boolean
}

export type DetectedRisk = {
  risk_id: string
  category: string
  label: string
  severity: string
  confidence: number
  risk_score: number
  risk_level: RiskLevel
  evidence_span: string
  evidence_start_char: number
  evidence_end_char: number
  explanation: string
  false_positive_warning: string
  needs_human_review: boolean
}

export type HealthyPattern = {
  label?: string
  pattern?: string
  explanation?: string
  evidence_span?: string
  [key: string]: unknown
}

export type AnalyzedClaim = {
  claim_id: string
  text: string
  claim_type: string
  start_char: number
  end_char: number
  detected_risks: DetectedRisk[]
  healthy_patterns: HealthyPattern[]
  warnings: string[]
  retrieval_diagnostics: Record<string, unknown>
}

export type AnalysisResponse = {
  text_id: string
  mode: string
  model_provider_id: string
  model_name: string
  llm_used: boolean
  deterministic_fallback_used: boolean
  claims: AnalyzedClaim[]
  overall_risk_score: number
  risk_level: RiskLevel
  needs_human_review: boolean
  warnings: string[]
}

export type TaxonomyEntry = {
  id: string
  name: string
  pack: string
  canonical_category: string
  academic_status: string
  academic_consensus: string
  short_definition: string
  long_definition: string
  detection_level: string
  signals: string[]
  trigger_patterns: string[]
  minimum_evidence_requirement: string
  exclusion_criteria: string[]
  common_false_positives: string[]
  positive_examples: string[]
  negative_examples: string[]
  severity_guidance: string[]
  related_risks: string[]
  synonym_ids: string[]
  source_refs: string[]
  enabled_for_mvp: boolean
  enabled_for_retrieval: boolean
  enabled_for_classification: boolean
  requires_context: boolean
  requires_human_judgment: boolean
  false_positive_sensitivity: string
  activation_status: string
  healthy_suppressor: boolean
  model_assisted_allowed: boolean
  notes: string
}

export type TaxonomyFilters = {
  category: string
  pack: string
  academic_status: string
  academic_consensus: string
  detection_level: string
  activation_status: string
  enabled_for_classification: string
  false_positive_sensitivity: string
}

export type TaxonomyIssue = { code: string; message: string; severity: string; entry_id?: string; row_number?: number }
export type TaxonomyImportResult = { entry_count: number; errors: string[]; warnings: string[]; backup_paths?: string[] }
export type TaxonomyCoverage = {
  entry_count: number
  active_count: number
  enabled_for_classification_count: number
  review_required_count: number
  deprecated_count: number
  by_category: Record<string, number>
  by_pack: Record<string, number>
  by_detection_level: Record<string, number>
  by_academic_status: Record<string, number>
  by_activation_status: Record<string, number>
  missing_examples_count: number
  missing_false_positive_warnings_count: number
}
export type TaxonomyQualityReport = { ok: boolean; entry_count: number; active_classification_count: number; error_count: number; warning_count: number; errors: TaxonomyIssue[]; warnings: TaxonomyIssue[] }
export type TaxonomyPackSummary = { pack: string; entry_count: number; active_count: number; enabled_for_classification_count: number }
export type TaxonomyValidationResult = { ok: boolean; entry_count: number; active_classification_count: number; errors: TaxonomyIssue[]; warnings: TaxonomyIssue[] }

export type ProviderType = 'deterministic' | 'openai_compatible' | string
export type ProviderProfile = {
  provider_id: string
  label: string
  provider_type: ProviderType
  base_url: string
  model_name: string
  api_key_env_var: string
  timeout_seconds: number
  max_tokens: number
  temperature: number
  supports_json_mode: boolean | string
  supports_streaming: boolean | string
  enabled: boolean
}
export type ProviderListResponse = { providers: ProviderProfile[] }
export type ActiveProviderResponse = { provider_id: string; provider: ProviderProfile | null }
export type ProviderTestResponse = { provider_id: string; status: string; latency_ms: number; warnings: string[]; models: string[]; detail: string }

export type ReviewDecision = 'correct' | 'incorrect' | 'partial' | 'insufficient_evidence'
export type ReviewFeedback = { analysis_id: string; taxonomy_id?: string | null; decision: ReviewDecision; notes: string }
export type ReviewRecord = {
  id: string
  created_at: string
  analysis: AnalysisResponse
  source_text: string
  feedback?: ReviewFeedback & { corrected_labels?: string[] }
}

export type EvaluationResult = {
  items?: number
  analyses?: AnalysisResponse[]
  metrics?: Record<string, number>
  false_positives?: Array<Record<string, unknown>>
  false_negatives?: Array<Record<string, unknown>>
  evidence_span_misses?: Array<Record<string, unknown>>
  [key: string]: unknown
}

export type ReportFormat = 'json' | 'markdown' | 'html'
export type GeneratedReport = {
  id: string
  title: string
  created_at: string
  analysis_id?: string
  formats: ReportFormat[]
  json?: string
  markdown?: string
  html?: string
}
