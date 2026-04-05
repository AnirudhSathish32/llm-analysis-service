export interface AppConfig {
  apiBaseUrl: string
  maxTextLength: number
  maxUploadBytes: number
  allowedFileTypes: string[]
  rateLimitPerMinute: number
  autoRefreshIntervalMs: number
}

const stored = localStorage.getItem('app-config')
const parsed = stored ? (JSON.parse(stored) as Partial<AppConfig>) : {}

export const config: AppConfig = {
  apiBaseUrl: parsed.apiBaseUrl ?? '',
  maxTextLength: 10_000,
  maxUploadBytes: 5 * 1024 * 1024,
  allowedFileTypes: ['.pdf', '.txt', '.csv'],
  rateLimitPerMinute: 20,
  autoRefreshIntervalMs: 30_000,
}

export function updateConfig(updates: Partial<AppConfig>): void {
  const merged = { ...config, ...updates }
  localStorage.setItem('app-config', JSON.stringify(merged))
  Object.assign(config, updates)
}
