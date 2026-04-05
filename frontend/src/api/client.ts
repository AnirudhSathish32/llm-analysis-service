import { config } from '../config.ts'
import type {
  AnalysisRequest,
  AnalysisResponse,
  DocumentUploadResponse,
  DocumentStatus,
  UsageResponse,
  UsageByTypeEntry,
  ApiError,
} from './types.ts'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${config.apiBaseUrl}${path}`
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })

  if (!response.ok) {
    const error = (await response.json().catch(() => ({
      detail: `HTTP ${response.status}`,
    }))) as ApiError
    throw { status: response.status, detail: error.detail }
  }

  if (response.status === 204) return undefined as unknown as T
  return (await response.json()) as T
}

export const apiClient = {
  analyze(payload: AnalysisRequest): Promise<AnalysisResponse> {
    return request<AnalysisResponse>('/v1/analysis', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },

  uploadDocument(file: File): Promise<DocumentUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    return request<DocumentUploadResponse>('/v1/documents', {
      method: 'POST',
      body: formData,
      headers: {},
    })
  },

  getDocument(documentId: string): Promise<DocumentStatus> {
    return request<DocumentStatus>(`/v1/documents/${documentId}`)
  },

  getUsage(): Promise<UsageResponse> {
    return request<UsageResponse>('/v1/metrics/usage')
  },

  getUsageByType(): Promise<UsageByTypeEntry[]> {
    return request<UsageByTypeEntry[]>('/v1/metrics/usage/by_type')
  },

  healthCheck(): Promise<{ status: string }> {
    return request<{ status: string }>('/health')
  },
}

export function isApiError(err: unknown): err is ApiError {
  return (
    typeof err === 'object' &&
    err !== null &&
    'status' in err &&
    'detail' in err
  )
}
