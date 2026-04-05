import { renderCard } from '../components/card.ts'
import { renderButton } from '../components/button.ts'
import { renderInput } from '../components/input.ts'
import { renderToggle } from '../components/toggle.ts'
import { showToast } from '../components/toast.ts'
import { config, updateConfig } from '../config.ts'
import { getPreferredTheme, setTheme } from '../utils/helpers.ts'

export function renderSettingsTab(): HTMLElement {
  const container = document.createElement('div')
  container.className = 'flex flex-col gap-6'

  const heading = document.createElement('h2')
  heading.className = 'text-lg font-medium text-text-primary'
  heading.textContent = 'Settings'
  container.appendChild(heading)

  container.appendChild(renderApiSettings())
  container.appendChild(renderAppearanceSettings())
  container.appendChild(renderDataSettings())

  return container
}

function renderApiSettings(): HTMLElement {
  const card = renderCard({ children: [] })

  const heading = document.createElement('h3')
  heading.className = 'text-sm font-medium text-text-secondary mb-3'
  heading.textContent = 'API Configuration'
  card.appendChild(heading)

  const inputWrapper = renderInput({
    label: 'API Base URL',
    id: 'api-base-url',
    placeholder: 'Leave empty to use current origin',
    value: config.apiBaseUrl,
  })
  card.appendChild(inputWrapper)

  const input = inputWrapper.querySelector('#api-base-url') as HTMLInputElement | null
  if (input) {
    input.addEventListener('change', () => {
      updateConfig({ apiBaseUrl: input.value.trim() })
      showToast({ message: 'API URL updated', type: 'success' })
    })
  }

  const info = document.createElement('p')
  info.className = 'text-xs text-text-secondary mt-2'
  info.textContent = `Rate limit: ${config.rateLimitPerMinute} requests/minute`
  card.appendChild(info)

  return card
}

function renderAppearanceSettings(): HTMLElement {
  const card = renderCard({ children: [] })

  const heading = document.createElement('h3')
  heading.className = 'text-sm font-medium text-text-secondary mb-3'
  heading.textContent = 'Appearance'
  card.appendChild(heading)

  const isDark = getPreferredTheme()
  const toggle = renderToggle({
    label: 'Dark mode',
    checked: isDark,
    id: 'theme-toggle',
    onChange: (checked) => {
      setTheme(checked)
    },
  })
  card.appendChild(toggle)

  return card
}

function renderDataSettings(): HTMLElement {
  const card = renderCard({ children: [] })

  const heading = document.createElement('h3')
  heading.className = 'text-sm font-medium text-text-secondary mb-3'
  heading.textContent = 'Data'
  card.appendChild(heading)

  const resetBtn = renderButton({
    label: 'Reset Local Data',
    variant: 'danger',
    className: 'min-h-[36px] h-9',
    onClick: () => {
      if (confirm('Clear all locally stored data? This cannot be undone.')) {
        localStorage.removeItem('recent-documents')
        localStorage.removeItem('app-config')
        showToast({ message: 'Local data cleared', type: 'success' })
      }
    },
  })
  card.appendChild(resetBtn)

  return card
}
