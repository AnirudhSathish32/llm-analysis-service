const variantMap: Record<string, string> = {
  success: 'badge-success',
  warning: 'badge-warning',
  error: 'badge-error',
  info: 'badge-info',
}

export function renderBadge(text: string, variant: string = 'info'): HTMLSpanElement {
  const badge = document.createElement('span')
  badge.className = `badge ${variantMap[variant] ?? 'badge-info'}`
  badge.textContent = text
  return badge
}
