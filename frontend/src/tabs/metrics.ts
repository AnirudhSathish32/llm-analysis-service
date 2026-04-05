import { renderCard } from '../components/card.ts'
import { renderButton } from '../components/button.ts'
import { renderToggle } from '../components/toggle.ts'
import { showToast } from '../components/toast.ts'
import { apiClient, isApiError } from '../api/client.ts'
import { config } from '../config.ts'
import { formatCurrency, formatNumber, formatMs } from '../utils/helpers.ts'
import type { UsageResponse, UsageByTypeEntry } from '../api/types.ts'

export function renderMetricsTab(): HTMLElement {
  const container = document.createElement('div')
  container.className = 'flex flex-col gap-6'

  const headerRow = document.createElement('div')
  headerRow.className = 'flex items-center justify-between flex-wrap gap-3'

  const heading = document.createElement('h2')
  heading.className = 'text-lg font-medium text-text-primary'
  heading.textContent = 'Usage Metrics'
  headerRow.appendChild(heading)

  const controls = document.createElement('div')
  controls.className = 'flex items-center gap-3'

  const refreshBtn = renderButton({
    label: 'Refresh',
    variant: 'secondary',
    className: 'min-h-[36px] h-9 px-3',
    onClick: () => loadMetrics(),
  })
  controls.appendChild(refreshBtn)

  const autoRefreshToggle = renderToggle({
    label: 'Auto-refresh',
    checked: false,
    id: 'auto-refresh-toggle',
    onChange: (checked) => toggleAutoRefresh(checked),
  })
  controls.appendChild(autoRefreshToggle)

  headerRow.appendChild(controls)
  container.appendChild(headerRow)

  const cardsContainer = document.createElement('div')
  cardsContainer.id = 'metrics-cards'
  cardsContainer.className = 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4'
  container.appendChild(cardsContainer)

  const derivedContainer = document.createElement('div')
  derivedContainer.id = 'derived-metrics'
  derivedContainer.className = 'grid grid-cols-1 sm:grid-cols-2 gap-4'
  container.appendChild(derivedContainer)

  const tableContainer = document.createElement('div')
  tableContainer.id = 'metrics-table'
  container.appendChild(tableContainer)

  loadMetrics()

  return container
}

let autoRefreshTimer: ReturnType<typeof setInterval> | null = null

function toggleAutoRefresh(enabled: boolean): void {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
    autoRefreshTimer = null
  }
  if (enabled) {
    autoRefreshTimer = setInterval(() => loadMetrics(), config.autoRefreshIntervalMs)
  }
}

async function loadMetrics(): Promise<void> {
  const cardsContainer = document.getElementById('metrics-cards')
  const derivedContainer = document.getElementById('derived-metrics')
  const tableContainer = document.getElementById('metrics-table')

  if (cardsContainer) {
    cardsContainer.innerHTML = ''
    for (let i = 0; i < 4; i++) {
      const card = document.createElement('div')
      card.className = 'card'
      card.innerHTML = '<div class="skeleton h-4 w-20 mb-2"></div><div class="skeleton h-6 w-32"></div>'
      cardsContainer.appendChild(card)
    }
  }

  try {
    const [usage, byType] = await Promise.all([
      apiClient.getUsage(),
      apiClient.getUsageByType(),
    ])

    renderSummaryCards(cardsContainer, usage)
    renderDerivedMetrics(derivedContainer, usage)
    renderBreakdownTable(tableContainer, byType)
  } catch (err) {
    if (isApiError(err)) {
      showToast({ message: err.detail, type: 'error' })
      renderMetricsError(cardsContainer, derivedContainer, tableContainer)
    } else {
      showToast({ message: 'Failed to load metrics.', type: 'error' })
      renderMetricsError(cardsContainer, derivedContainer, tableContainer)
    }
  }
}

function renderMetricsError(
  cards: HTMLElement | null,
  derived: HTMLElement | null,
  table: HTMLElement | null,
): void {
  if (cards) cards.innerHTML = ''
  if (derived) derived.innerHTML = ''
  if (!table) return
  table.innerHTML = ''

  const card = renderCard({ children: [] })
  const msg = document.createElement('p')
  msg.className = 'text-sm text-error mb-3'
  msg.textContent = 'Failed to load metrics'
  card.appendChild(msg)

  const retryBtn = renderButton({
    label: 'Retry',
    variant: 'secondary',
    className: 'min-h-[36px] h-9',
    onClick: () => loadMetrics(),
  })
  card.appendChild(retryBtn)
  table.appendChild(card)
}

function renderSummaryCards(container: HTMLElement | null, usage: UsageResponse): void {
  if (!container) return
  container.innerHTML = ''

  const stats: [string, string][] = [
    ['Total Requests', formatNumber(usage.total_requests)],
    ['Total Tokens', formatNumber(usage.total_tokens)],
    ['Total Cost', formatCurrency(usage.total_cost_usd)],
    ['Avg Duration', formatMs(usage.avg_duration_ms)],
  ]

  for (const [label, value] of stats) {
    const card = renderCard({ children: [] })
    const labelEl = document.createElement('p')
    labelEl.className = 'text-sm text-text-secondary mb-1'
    labelEl.textContent = label
    card.appendChild(labelEl)

    const valueEl = document.createElement('p')
    valueEl.className = 'text-2xl font-semibold text-text-primary font-mono tabular-nums'
    valueEl.textContent = value
    card.appendChild(valueEl)

    container.appendChild(card)
  }
}

function renderDerivedMetrics(container: HTMLElement | null, usage: UsageResponse): void {
  if (!container) return
  container.innerHTML = ''

  const costPerToken = usage.total_tokens > 0 ? usage.total_cost_usd / usage.total_tokens : 0
  const costPerQuery = usage.total_requests > 0 ? usage.total_cost_usd / usage.total_requests : 0

  const metrics: [string, string][] = [
    ['Cost per Token', `$${costPerToken.toFixed(6)}`],
    ['Cost per Query', formatCurrency(costPerQuery)],
  ]

  for (const [label, value] of metrics) {
    const card = renderCard({ children: [] })
    const labelEl = document.createElement('p')
    labelEl.className = 'text-sm text-text-secondary mb-1'
    labelEl.textContent = label
    card.appendChild(labelEl)

    const valueEl = document.createElement('p')
    valueEl.className = 'text-xl font-semibold text-text-primary font-mono tabular-nums'
    valueEl.textContent = value
    card.appendChild(valueEl)

    container.appendChild(card)
  }
}

function renderBreakdownTable(container: HTMLElement | null, entries: UsageByTypeEntry[]): void {
  if (!container) return
  container.innerHTML = ''

  if (entries.length === 0) {
    const empty = document.createElement('div')
    empty.className = 'card text-center py-8'
    empty.innerHTML = `
      <p class="text-sm text-text-secondary">No data yet</p>
      <p class="text-xs text-text-secondary mt-1">Run an analysis to see metrics here</p>
    `
    container.appendChild(empty)
    return
  }

  const card = renderCard({ children: [] })

  const heading = document.createElement('h3')
  heading.className = 'text-sm font-medium text-text-secondary mb-3'
  heading.textContent = 'Breakdown by Type'
  card.appendChild(heading)

  const table = document.createElement('table')
  table.className = 'w-full text-sm'

  const thead = document.createElement('thead')
  thead.innerHTML = `
    <tr class="border-b border-border">
      <th scope="col" class="text-left py-2 pr-4 text-text-secondary font-medium">Type</th>
      <th scope="col" class="text-right py-2 pr-4 text-text-secondary font-medium">Requests</th>
      <th scope="col" class="text-right py-2 pr-4 text-text-secondary font-medium">Tokens</th>
      <th scope="col" class="text-right py-2 text-text-secondary font-medium">Cost</th>
    </tr>
  `
  table.appendChild(thead)

  const tbody = document.createElement('tbody')
  for (const entry of entries) {
    const row = document.createElement('tr')
    row.className = 'border-b border-border/50'
    row.innerHTML = `
      <td class="py-2 pr-4">
        <span class="badge badge-info capitalize">${entry.analysis_type.replace('_', ' ')}</span>
      </td>
      <td class="py-2 pr-4 text-right font-mono tabular-nums text-text-primary">${formatNumber(entry.total_requests)}</td>
      <td class="py-2 pr-4 text-right font-mono tabular-nums text-text-primary">${formatNumber(entry.total_tokens)}</td>
      <td class="py-2 text-right font-mono tabular-nums text-text-primary">${formatCurrency(entry.total_cost_usd)}</td>
    `
    tbody.appendChild(row)
  }
  table.appendChild(tbody)
  card.appendChild(table)

  container.appendChild(card)
}
