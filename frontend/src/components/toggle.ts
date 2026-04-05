export interface ToggleProps {
  label: string
  checked: boolean
  id: string
  onChange: (checked: boolean) => void
}

export function renderToggle(props: ToggleProps): HTMLDivElement {
  const wrapper = document.createElement('div')
  wrapper.className = 'flex items-center gap-3'

  const toggle = document.createElement('button')
  toggle.type = 'button'
  toggle.id = props.id
  toggle.setAttribute('role', 'switch')
  toggle.setAttribute('aria-checked', String(props.checked))
  toggle.setAttribute('aria-label', props.label)
  toggle.className = `relative inline-flex h-6 w-11 min-w-[44px] items-center rounded-full transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-bg-primary ${
    props.checked ? 'bg-accent' : 'bg-bg-tertiary border border-border'
  }`

  const knob = document.createElement('span')
  knob.className = `inline-block h-4 w-4 rounded-full bg-white transition-transform duration-150 ${
    props.checked ? 'translate-x-6' : 'translate-x-1'
  }`
  toggle.appendChild(knob)

  toggle.addEventListener('click', () => {
    const newState = !props.checked
    props.onChange(newState)
  })

  const label = document.createElement('label')
  label.setAttribute('for', props.id)
  label.className = 'text-sm text-text-secondary cursor-pointer'
  label.textContent = props.label

  wrapper.appendChild(toggle)
  wrapper.appendChild(label)

  return wrapper
}
