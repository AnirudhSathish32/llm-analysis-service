import './style.css'
import { renderAnalyzeTab } from './tabs/analyze.ts'
import { renderDocumentsTab } from './tabs/documents.ts'
import { renderMetricsTab } from './tabs/metrics.ts'
import { renderSettingsTab } from './tabs/settings.ts'
import { getPreferredTheme, setTheme } from './utils/helpers.ts'
import { config } from './config.ts'

interface TabDef {
  id: string
  label: string
  render: () => HTMLElement
}

const tabs: TabDef[] = [
  { id: 'analyze', label: 'Analyze', render: renderAnalyzeTab },
  { id: 'documents', label: 'Documents', render: renderDocumentsTab },
  { id: 'metrics', label: 'Metrics', render: renderMetricsTab },
  { id: 'settings', label: 'Settings', render: renderSettingsTab },
]

let activeTab = tabs[0]

function init(): void {
  setTheme(getPreferredTheme())
  resolveApiBaseUrl()
  renderNav()
  switchTab(tabs[0])
  setupKeyboardShortcuts()
}

function resolveApiBaseUrl(): void {
  if (!config.apiBaseUrl) {
    config.apiBaseUrl = window.location.origin
  }
}

function renderNav(): void {
  const nav = document.getElementById('tab-nav')
  if (!nav) return

  for (const tab of tabs) {
    const btn = document.createElement('button')
    btn.type = 'button'
    btn.className =
      'px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors min-h-[44px] focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-bg-secondary'
    btn.setAttribute('role', 'tab')
    btn.setAttribute('aria-selected', 'false')
    btn.setAttribute('aria-controls', 'tab-content')
    btn.textContent = tab.label
    btn.dataset.tabId = tab.id

    btn.addEventListener('click', () => {
      switchTab(tab)
    })

    nav.appendChild(btn)
  }
}

function switchTab(tab: TabDef): void {
  activeTab = tab

  const nav = document.getElementById('tab-nav')
  if (nav) {
    for (const btn of nav.querySelectorAll('button')) {
      const isActive = btn.dataset.tabId === tab.id
      btn.setAttribute('aria-selected', String(isActive))
      if (isActive) {
        btn.className = btn.className.replace(
          'text-text-secondary',
          'text-text-primary'
        )
        btn.classList.add('bg-bg-tertiary', 'text-text-primary')
        btn.classList.remove('text-text-secondary')
      } else {
        btn.classList.remove('bg-bg-tertiary', 'text-text-primary')
        btn.classList.add('text-text-secondary')
      }
    }
  }

  const content = document.getElementById('tab-content')
  if (content) {
    content.innerHTML = ''
    content.appendChild(tab.render())
  }
}

function setupKeyboardShortcuts(): void {
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key >= '1' && e.key <= '4') {
      e.preventDefault()
      const index = parseInt(e.key, 10) - 1
      if (tabs[index]) {
        switchTab(tabs[index])
      }
    }
  })
}

init()
