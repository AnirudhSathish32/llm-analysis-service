export interface InputProps {
  label: string
  type?: string
  placeholder?: string
  value?: string
  id: string
  required?: boolean
  disabled?: boolean
  error?: string
  maxLength?: number
  multiline?: boolean
  rows?: number
}

export function renderInput(props: InputProps): HTMLDivElement {
  const wrapper = document.createElement('div')
  wrapper.className = 'flex flex-col gap-1'

  const label = document.createElement('label')
  label.className = 'label'
  label.setAttribute('for', props.id)
  label.textContent = props.label

  let input: HTMLInputElement | HTMLTextAreaElement

  if (props.multiline) {
    const textarea = document.createElement('textarea')
    textarea.id = props.id
    textarea.className = 'textarea'
    textarea.placeholder = props.placeholder ?? ''
    textarea.value = props.value ?? ''
    textarea.required = props.required ?? false
    textarea.disabled = props.disabled ?? false
    if (props.maxLength) textarea.maxLength = props.maxLength
    if (props.rows) textarea.rows = props.rows
    input = textarea
  } else {
    const textInput = document.createElement('input')
    textInput.id = props.id
    textInput.type = props.type ?? 'text'
    textInput.className = 'input'
    textInput.placeholder = props.placeholder ?? ''
    textInput.value = props.value ?? ''
    textInput.required = props.required ?? false
    textInput.disabled = props.disabled ?? false
    if (props.maxLength) textInput.maxLength = props.maxLength
    input = textInput
  }

  wrapper.appendChild(label)
  wrapper.appendChild(input)

  if (props.error) {
    const errorEl = document.createElement('p')
    errorEl.className = 'text-xs text-error mt-1'
    errorEl.setAttribute('role', 'alert')
    errorEl.textContent = props.error
    wrapper.appendChild(errorEl)
  }

  return wrapper
}
