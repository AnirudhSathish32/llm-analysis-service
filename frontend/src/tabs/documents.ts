import { renderButton } from '../components/button.ts'
import { renderCard } from '../components/card.ts'
import { renderBadge } from '../components/badge.ts'
import { renderInput } from '../components/input.ts'
import { showToast } from '../components/toast.ts'
import { apiClient, isApiError } from '../api/client.ts'
import { config } from '../config.ts'
import { getFileNameExtension, copyToClipboard } from '../utils/helpers.ts'
import type { DocumentUploadResponse } from '../api/types.ts'

export function renderDocumentsTab(): HTMLElement {
  const container = document.createElement('div')
  container.className = 'flex flex-col gap-6'

  const uploadSection = document.createElement('div')
  uploadSection.className = 'flex flex-col gap-4'

  const dropZone = document.createElement('div')
  dropZone.className =
    'border-2 border-dashed border-border rounded-xl p-8 text-center cursor-pointer hover:border-accent transition-colors min-h-[120px] flex flex-col items-center justify-center gap-2'
  dropZone.setAttribute('role', 'button')
  dropZone.setAttribute('tabindex', '0')
  dropZone.setAttribute('aria-label', 'Upload document. Click or drag and drop.')

  dropZone.innerHTML = `
    <svg class="w-8 h-8 text-text-secondary mx-auto" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
      <polyline points="17 8 12 3 7 8"/>
      <line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
    <p class="text-sm text-text-secondary">Drop a file here or click to browse</p>
    <p class="text-xs text-text-secondary">PDF, TXT, CSV (max ${formatBytes(config.maxUploadBytes)})</p>
  `

  const fileInput = document.createElement('input')
  fileInput.type = 'file'
  fileInput.accept = '.pdf,.txt,.csv'
  fileInput.className = 'hidden'
  fileInput.id = 'file-upload'

  dropZone.addEventListener('click', () => fileInput.click())
  dropZone.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      fileInput.click()
    }
  })

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault()
    dropZone.classList.add('border-accent', 'bg-bg-tertiary')
  })

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-accent', 'bg-bg-tertiary')
  })

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault()
    dropZone.classList.remove('border-accent', 'bg-bg-tertiary')
    if (!e.dataTransfer) return
    const file = e.dataTransfer.files[0]
    if (file) handleFileUpload(file, resultContainer)
  })

  uploadSection.appendChild(dropZone)
  uploadSection.appendChild(fileInput)

  const resultContainer = document.createElement('div')
  resultContainer.id = 'upload-result'
  uploadSection.appendChild(resultContainer)

  container.appendChild(uploadSection)

  const statusSection = document.createElement('div')
  statusSection.className = 'flex flex-col gap-4'

  const statusInputWrapper = renderInput({
    label: 'Document ID',
    id: 'status-doc-id',
    placeholder: 'Paste document UUID',
  })
  statusSection.appendChild(statusInputWrapper)

  const checkBtn = renderButton({
    label: 'Check Status',
    variant: 'secondary',
    onClick: () => checkDocumentStatus(),
  })
  statusSection.appendChild(checkBtn)

  const statusResultContainer = document.createElement('div')
  statusResultContainer.id = 'status-result'
  statusSection.appendChild(statusResultContainer)

  container.appendChild(statusSection)

  const recentSection = renderRecentDocuments()
  container.appendChild(recentSection)

  return container
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(0)} MB`
}

function validateFile(file: File): string | null {
  const ext = getFileNameExtension(file.name)
  if (!config.allowedFileTypes.includes(ext)) {
    return `Unsupported file type "${ext}". Allowed: ${config.allowedFileTypes.join(', ')}`
  }
  if (file.size > config.maxUploadBytes) {
    return `File too large (${formatBytes(file.size)}). Maximum: ${formatBytes(config.maxUploadBytes)}`
  }
  return null
}

async function handleFileUpload(file: File, container: HTMLElement): Promise<void> {
  const error = validateFile(file)
  if (error) {
    showToast({ message: error, type: 'error' })
    return
  }

  container.innerHTML = ''
  const skeleton = document.createElement('div')
  skeleton.className = 'card'
  skeleton.innerHTML = '<div class="skeleton h-4 w-32 mb-2"></div><div class="skeleton h-4 w-48"></div>'
  container.appendChild(skeleton)

  try {
    const response = await apiClient.uploadDocument(file)
    renderUploadResult(container, response)
    addRecentDocument(response)
    showToast({ message: 'Document uploaded successfully', type: 'success' })
  } catch (err) {
    if (isApiError(err)) {
      showToast({ message: err.detail, type: 'error' })
    } else {
      showToast({ message: 'Upload failed.', type: 'error' })
    }
    container.innerHTML = ''
  }
}

function renderUploadResult(container: HTMLElement, response: DocumentUploadResponse): void {
  container.innerHTML = ''

  const card = renderCard({ children: [] })

  const header = document.createElement('div')
  header.className = 'flex items-center gap-2 mb-3'
  header.appendChild(renderBadge(response.status, response.status === 'ready' ? 'success' : response.status === 'failed' ? 'error' : 'warning'))
  card.appendChild(header)

  const fields: [string, string][] = [
    ['Filename', response.filename],
    ['Document ID', response.document_id],
    ['Chunks', String(response.chunk_count)],
  ]

  for (const [label, value] of fields) {
    const row = document.createElement('div')
    row.className = 'flex items-center justify-between py-2 border-b border-border/50 last:border-0'

    const labelEl = document.createElement('span')
    labelEl.className = 'text-sm text-text-secondary'
    labelEl.textContent = label
    row.appendChild(labelEl)

    const valueEl = document.createElement('span')
    valueEl.className = 'text-sm text-text-primary font-mono'
    valueEl.textContent = value
    row.appendChild(valueEl)

    if (label === 'Document ID') {
      const copyBtn = renderButton({
        label: 'Copy',
        variant: 'ghost',
        className: 'min-h-[32px] min-w-[32px] h-8 w-8 px-2 py-1',
        onClick: () => {
          copyToClipboard(value).then(() => {
            showToast({ message: 'Copied to clipboard', type: 'success' })
          })
        },
      })
      row.appendChild(copyBtn)
    }

    card.appendChild(row)
  }

  container.appendChild(card)
}

async function checkDocumentStatus(): Promise<void> {
  const input = document.getElementById('status-doc-id') as HTMLInputElement | null
  const container = document.getElementById('status-result')
  if (!input || !container || !input.value.trim()) return

  container.innerHTML = ''
  const skeleton = document.createElement('div')
  skeleton.className = 'card'
  skeleton.innerHTML = '<div class="skeleton h-4 w-32 mb-2"></div><div class="skeleton h-4 w-48"></div>'
  container.appendChild(skeleton)

  try {
    const response = await apiClient.getDocument(input.value.trim())
    container.innerHTML = ''

    const card = renderCard({ children: [] })
    const header = document.createElement('div')
    header.className = 'flex items-center gap-2 mb-3'
    header.appendChild(renderBadge(response.status, response.status === 'ready' ? 'success' : response.status === 'failed' ? 'error' : 'warning'))
    card.appendChild(header)

    const fields: [string, string][] = [
      ['Filename', response.filename],
      ['Status', response.status],
      ['Chunks', response.chunk_count !== null ? String(response.chunk_count) : 'N/A'],
      ['Created', new Date(response.created_at).toLocaleString()],
    ]

    for (const [label, value] of fields) {
      const row = document.createElement('div')
      row.className = 'flex items-center justify-between py-2 border-b border-border/50 last:border-0'
      row.innerHTML = `
        <span class="text-sm text-text-secondary">${label}</span>
        <span class="text-sm text-text-primary font-mono">${value}</span>
      `
      card.appendChild(row)
    }

    container.appendChild(card)
  } catch (err) {
    container.innerHTML = ''
    if (isApiError(err)) {
      if (err.status === 404) {
        const card = renderCard({ children: [] })
        const msg = document.createElement('p')
        msg.className = 'text-sm text-text-secondary'
        msg.textContent = 'Document not found. Check the ID and try again.'
        card.appendChild(msg)
        container.appendChild(card)
      } else {
        showToast({ message: err.detail, type: 'error' })
      }
    } else {
      showToast({ message: 'Failed to check status.', type: 'error' })
    }
  }
}

function renderRecentDocuments(): HTMLElement {
  const section = document.createElement('div')
  section.className = 'flex flex-col gap-4'

  const heading = document.createElement('h2')
  heading.className = 'text-lg font-medium text-text-primary'
  heading.textContent = 'Recent Documents'
  section.appendChild(heading)

  const docs = getRecentDocuments()
  if (docs.length === 0) {
    const empty = document.createElement('p')
    empty.className = 'text-sm text-text-secondary'
    empty.textContent = 'No documents uploaded yet.'
    section.appendChild(empty)
    return section
  }

  const list = document.createElement('div')
  list.className = 'flex flex-col gap-2'

  for (const doc of docs) {
    const item = document.createElement('div')
    item.className = 'flex items-center justify-between py-2 px-3 bg-bg-secondary border border-border rounded-lg'
    item.innerHTML = `
      <div class="flex flex-col min-w-0">
        <span class="text-sm text-text-primary truncate">${doc.filename}</span>
        <span class="text-xs text-text-secondary font-mono truncate">${doc.document_id}</span>
      </div>
      <span class="badge badge-${doc.status === 'ready' ? 'success' : doc.status === 'failed' ? 'error' : 'warning'} flex-shrink-0 ml-2">${doc.status}</span>
    `
    list.appendChild(item)
  }

  section.appendChild(list)
  return section
}

interface RecentDoc {
  document_id: string
  filename: string
  status: string
}

function getRecentDocuments(): RecentDoc[] {
  const stored = localStorage.getItem('recent-documents')
  if (!stored) return []
  try {
    return JSON.parse(stored) as RecentDoc[]
  } catch {
    return []
  }
}

function addRecentDocument(doc: { document_id: string; filename: string; status: string }): void {
  const docs = getRecentDocuments()
  docs.unshift({ document_id: doc.document_id, filename: doc.filename, status: doc.status })
  const trimmed = docs.slice(0, 10)
  localStorage.setItem('recent-documents', JSON.stringify(trimmed))
}
