export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(value)
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value)
}

export function formatMs(value: number): string {
  return `${formatNumber(Math.round(value))} ms`
}

export function getFileNameExtension(filename: string): string {
  const parts = filename.split('.')
  if (parts.length < 2) return ''
  return `.${parts[parts.length - 1]}`.toLowerCase()
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text)
}

export function setTheme(dark: boolean): void {
  document.documentElement.classList.toggle('dark', dark)
  localStorage.setItem('theme', dark ? 'dark' : 'light')
}

export function getPreferredTheme(): boolean {
  const stored = localStorage.getItem('theme')
  if (stored === 'light') return false
  if (stored === 'dark') return true
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}
