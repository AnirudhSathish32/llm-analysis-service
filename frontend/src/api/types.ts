export interface Citation {
  chunk_index: number
  page: string
  source: string
}

export interface AnalysisRequest {
  text: string
  analysis_type: 'summary' | 'key_points'
  prompt_version?: string
  document_id?: string
}

export interface AnalysisResponse {
  request_id: string
  status: 'completed' | 'failed'
  result: Record<string, unknown> | null
  cached: boolean
  provider: string | null
  rag_chunks_used: number | null
  citations: Citation[] | null
}

export interface DocumentUploadResponse {
  document_id: string
  filename: string
  status: 'ready' | 'processing' | 'failed'
  chunk_count: number
}

export interface DocumentStatus {
  document_id: string
  filename: string
  status: 'processing' | 'ready' | 'failed'
  chunk_count: number | null
  created_at: string
}

export interface UsageResponse {
  total_requests: number
  total_tokens: number
  total_cost_usd: number
  avg_duration_ms: number
}

export interface UsageByTypeEntry {
  analysis_type: string
  total_requests: number
  total_tokens: number
  total_cost_usd: number
}

export interface ApiError {
  status: number
  detail: string
}
