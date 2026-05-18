export type AnalysisRequest = { text: string }
export type Risk = { taxonomy_id: string; name: string; severity: string; confidence: number; score: number; explanation: string; evidence: { quote: string; start: number; end: number }; mitigation: string }
export type Claim = { text: string; risks: Risk[] }
export type AnalysisResponse = { analysis_id: string; summary: Record<string, unknown>; claims: Claim[]; risks: Risk[] }
export type TaxonomyEntry = { id: string; name: string; description: string; severity: string; keywords: string[]; active: boolean }

export type TaxonomyImportResult = { entry_count: number; errors: string[]; warnings: string[] }
