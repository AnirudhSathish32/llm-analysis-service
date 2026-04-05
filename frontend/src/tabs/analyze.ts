import { renderButton } from '../components/button.ts'
import { renderCard } from '../components/card.ts'
import { renderBadge } from '../components/badge.ts'
import { renderInput } from '../components/input.ts'
import { showToast } from '../components/toast.ts'
import { renderSkeleton } from '../components/skeleton.ts'
import { apiClient, isApiError } from '../api/client.ts'
import { config } from '../config.ts'
import type { AnalysisResponse } from '../api/types.ts'

export function renderAnalyzeTab(): HTMLElement {
  const container = document.createElement('div')
  container.className = 'flex flex-col gap-6'

  const form = document.createElement('form')
  form.className = 'flex flex-col gap-4'
  form.noValidate = false
  form.addEventListener('submit', handleSubmit)

  const textInput = renderInput({
    label: 'Text to analyze',
    id: 'analyze-text',
    placeholder: 'Paste your text here...',
    multiline: true,
    rows: 8,
    maxLength: config.maxTextLength,
    required: true,
  })
  form.appendChild(textInput)

  const charCounter = document.createElement('p')
  charCounter.className = 'text-xs text-text-secondary text-right'
  charCounter.id = 'char-counter'
  charCounter.textContent = `0 / ${config.maxTextLength.toLocaleString()}`
  form.appendChild(charCounter)

  const textarea = textInput.querySelector('#analyze-text') as HTMLTextAreaElement | null
  if (textarea) {
    textarea.addEventListener('input', () => {
      const len = textarea.value.length
      charCounter.textContent = `${len.toLocaleString()} / ${config.maxTextLength.toLocaleString()}`
      submitBtn.disabled = len === 0 || len > config.maxTextLength
      charCounter.classList.toggle('text-error', len > config.maxTextLength)
      charCounter.classList.toggle('text-text-secondary', len <= config.maxTextLength)
    })
  }

  const selectWrapper = document.createElement('div')
  const selectLabel = document.createElement('label')
  selectLabel.className = 'label'
  selectLabel.setAttribute('for', 'analysis-type')
  selectLabel.textContent = 'Analysis type'

  const select = document.createElement('select')
  select.id = 'analysis-type'
  select.className = 'select'
  select.innerHTML = `
    <option value="summary">Summary</option>
    <option value="key_points">Key Points</option>
  `
  selectWrapper.appendChild(selectLabel)
  selectWrapper.appendChild(select)
  form.appendChild(selectWrapper)

  const docInputWrapper = renderInput({
    label: 'Document ID (optional)',
    id: 'document-id',
    placeholder: 'UUID for RAG-augmented analysis',
  })
  form.appendChild(docInputWrapper)

  const submitBtn = renderButton({
    label: 'Analyze',
    variant: 'primary',
    type: 'submit',
    disabled: true,
  })
  form.appendChild(submitBtn)

  container.appendChild(form)

  const resultContainer = document.createElement('div')
  resultContainer.id = 'analyze-result'
  container.appendChild(resultContainer)

  return container
}

let skeletonTimer: ReturnType<typeof setTimeout> | null = null

async function handleSubmit(event: Event): Promise<void> {
  event.preventDefault()
  const form = event.target as HTMLFormElement

  const textarea = form.querySelector('#analyze-text') as HTMLTextAreaElement
  const select = form.querySelector('#analysis-type') as HTMLSelectElement
  const docInput = form.querySelector('#document-id') as HTMLInputElement
  const resultContainer = document.getElementById('analyze-result')

  if (!textarea || !select) return

  if (!textarea.value.trim()) {
    textarea.focus()
    return
  }

  if (textarea.value.length > config.maxTextLength) {
    textarea.focus()
    showToast({ message: `Text exceeds maximum length of ${config.maxTextLength.toLocaleString()} characters.`, type: 'error' })
    return
  }

  const payload = {
    text: textarea.value,
    analysis_type: select.value as 'summary' | 'key_points',
    prompt_version: 'v1',
    document_id: docInput?.value.trim() || undefined,
  }

  if (!resultContainer) return
  resultContainer.innerHTML = ''

  skeletonTimer = setTimeout(() => {
    resultContainer.appendChild(renderSkeleton(3))
  }, 300)

  const submitBtn = form.querySelector('button[type="submit"]') as HTMLButtonElement
  if (submitBtn) {
    submitBtn.disabled = true
    submitBtn.innerHTML = `
      <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span>Processing...</span>
    `
  }

  try {
    const response = await apiClient.analyze(payload)
    if (skeletonTimer) {
      clearTimeout(skeletonTimer)
      skeletonTimer = null
    }
    renderResult(resultContainer, response)
  } catch (err) {
    if (skeletonTimer) {
      clearTimeout(skeletonTimer)
      skeletonTimer = null
    }
    resultContainer.innerHTML = ''

    if (isApiError(err)) {
      if (err.status === 429) {
        renderErrorState(resultContainer, 'Rate limit exceeded', 'Please wait a moment and try again.', true)
      } else {
        renderErrorState(resultContainer, 'Request failed', err.detail, false)
      }
    } else {
      renderErrorState(resultContainer, 'Unexpected error', 'An unexpected error occurred. Please try again.', false)
    }
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false
      submitBtn.innerHTML = '<span>Analyze</span>'
    }
  }
}

function renderErrorState(container: HTMLElement, title: string, message: string, showRetry: boolean): void {
  container.innerHTML = ''

  const card = renderCard({ children: [] })

  const header = document.createElement('div')
  header.className = 'flex items-center gap-2 mb-3'
  header.appendChild(renderBadge('Failed', 'error'))
  card.appendChild(header)

  const titleEl = document.createElement('p')
  titleEl.className = 'text-sm font-medium text-error mb-1'
  titleEl.textContent = title
  card.appendChild(titleEl)

  const messageEl = document.createElement('p')
  messageEl.className = 'text-sm text-text-secondary mb-4'
  messageEl.textContent = message
  card.appendChild(messageEl)

  if (showRetry) {
    const retryBtn = renderButton({
      label: 'Retry',
      variant: 'secondary',
      className: 'min-h-[36px] h-9',
      onClick: () => {
        const form = document.querySelector('form')
        if (form) {
          const submitEvent = new Event('submit', { cancelable: true })
          form.dispatchEvent(submitEvent)
        }
      },
    })
    card.appendChild(retryBtn)
  }

  container.appendChild(card)
}

function renderResult(container: HTMLElement, response: AnalysisResponse): void {
  container.innerHTML = ''

  const card = renderCard({ children: [] })

  const header = document.createElement('div')
  header.className = 'flex items-center gap-2 mb-3 flex-wrap'

  const statusBadge = renderBadge(
    response.status === 'completed' ? 'Completed' : 'Failed',
    response.status === 'completed' ? 'success' : 'error'
  )
  header.appendChild(statusBadge)

  if (response.cached) {
    header.appendChild(renderBadge('Cached', 'info'))
  }

  if (response.provider) {
    header.appendChild(renderBadge(response.provider, 'info'))
  }

  if (response.rag_chunks_used !== null && response.rag_chunks_used > 0) {
    header.appendChild(renderBadge(`${response.rag_chunks_used} RAG chunks`, 'info'))
  }

  card.appendChild(header)

  if (response.status === 'completed' && response.result?.content) {
    const content = document.createElement('div')
    content.className = 'text-sm text-text-primary whitespace-pre-wrap leading-relaxed'
    content.textContent = response.result.content as string
    card.appendChild(content)
  }

  if (response.status === 'failed') {
    const errorEl = document.createElement('div')
    errorEl.className = 'mt-3 p-3 bg-error/10 border border-error/20 rounded-lg'
    errorEl.innerHTML = `<p class="text-sm text-error">Analysis failed. Check the server logs for details.</p>`
    const retryBtn = renderButton({
      label: 'Retry',
      variant: 'secondary',
      className: 'min-h-[36px] h-9 mt-3',
      onClick: () => {
        const form = document.querySelector('form')
        if (form) {
          form.dispatchEvent(new Event('submit', { cancelable: true }))
        }
      },
    })
    errorEl.appendChild(retryBtn)
    card.appendChild(errorEl)
  }

  if (response.citations && response.citations.length > 0) {
    const citationsHeading = document.createElement('h3')
    citationsHeading.className = 'text-sm font-medium text-text-secondary mt-4 mb-2'
    citationsHeading.textContent = 'Citations'
    card.appendChild(citationsHeading)

    const table = document.createElement('table')
    table.className = 'w-full text-sm'

    const thead = document.createElement('thead')
    thead.innerHTML = `
      <tr class="border-b border-border">
        <th scope="col" class="text-left py-2 pr-4 text-text-secondary font-medium">#</th>
        <th scope="col" class="text-left py-2 pr-4 text-text-secondary font-medium">Page</th>
        <th scope="col" class="text-left py-2 text-text-secondary font-medium">Source</th>
      </tr>
    `
    table.appendChild(thead)

    const tbody = document.createElement('tbody')
    for (const citation of response.citations) {
      const row = document.createElement('tr')
      row.className = 'border-b border-border/50'
      row.innerHTML = `
        <td class="py-2 pr-4 font-mono text-text-primary">${citation.chunk_index}</td>
        <td class="py-2 pr-4 text-text-primary">${citation.page}</td>
        <td class="py-2 text-text-secondary">${citation.source}</td>
      `
      tbody.appendChild(row)
    }
    table.appendChild(tbody)
    card.appendChild(table)
  }

  container.appendChild(card)
}
