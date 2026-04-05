export interface ToastOptions {
  message: string
  type?: 'error' | 'success'
  duration?: number
}

export function showToast(options: ToastOptions): void {
  const container = document.getElementById('toast-container')
  if (!container) return

  const toast = document.createElement('div')
  toast.className = `toast toast-${options.type ?? 'error'}`
  toast.setAttribute('role', 'alert')
  toast.setAttribute('aria-live', 'polite')

  const icon =
    options.type === 'success'
      ? '<svg class="w-4 h-4 flex-shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>'
      : '<svg class="w-4 h-4 flex-shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/></svg>'

  toast.innerHTML = `
    ${icon}
    <p class="text-sm flex-1">${options.message}</p>
    <button class="btn-ghost min-h-[24px] min-w-[24px] h-6 w-6 p-0 flex items-center justify-center rounded" aria-label="Dismiss">
      <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
    </button>
  `

  const dismissBtn = toast.querySelector('button')
  if (dismissBtn) {
    dismissBtn.addEventListener('click', () => {
      toast.remove()
    })
  }

  container.appendChild(toast)

  const duration = options.duration ?? 4000
  setTimeout(() => {
    if (toast.parentNode) toast.remove()
  }, duration)
}
