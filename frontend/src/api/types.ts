export type AnalysisRequest = { text: string }
export type Risk = { taxonomy_id: string; name: string; severity: string; confidence: number; score: number; explanation: string; evidence: { quote: string; start: number; end: number }; mitigation: string }
export type Claim = { text: string; risks: Risk[] }
export type AnalysisResponse = { analysis_id: string; summary: Record<string, unknown>; claims: Claim[]; risks: Risk[] }

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
  description?: string
  keywords?: string[]
  severity?: string
  active?: boolean
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
export type TaxonomyIssue = { code: string; message: string; severity: string; entry_id?: string; row_number?: number }
export type TaxonomyQualityReport = { ok: boolean; entry_count: number; active_classification_count: number; error_count: number; warning_count: number; errors: TaxonomyIssue[]; warnings: TaxonomyIssue[] }
export type TaxonomyPackSummary = { pack: string; entry_count: number; active_count: number; enabled_for_classification_count: number }
export type TaxonomyValidationResult = { ok: boolean; entry_count: number; active_classification_count: number; errors: TaxonomyIssue[]; warnings: TaxonomyIssue[] }

export type ProviderType = 'deterministic' | 'openai_compatible'
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
