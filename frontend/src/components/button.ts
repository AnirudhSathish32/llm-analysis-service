export interface ButtonProps {
  label: string
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  disabled?: boolean
  loading?: boolean
  icon?: string
  onClick?: () => void
  type?: 'button' | 'submit'
  className?: string
}

export function renderButton(props: ButtonProps): HTMLButtonElement {
  const btn = document.createElement('button')
  btn.type = props.type ?? 'button'
  btn.className = `btn btn-${props.variant ?? 'primary'} ${props.className ?? ''}`
  btn.disabled = props.disabled ?? false
  btn.setAttribute('aria-label', props.label)

  if (props.loading) {
    btn.disabled = true
    btn.innerHTML = `
      <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span>Processing...</span>
    `
  } else {
    const content = props.icon
      ? `<svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${props.icon}</svg><span>${props.label}</span>`
      : `<span>${props.label}</span>`
    btn.innerHTML = content
  }

  if (props.onClick) {
    btn.addEventListener('click', props.onClick)
  }

  return btn
}
