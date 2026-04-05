export function renderSkeleton(lines: number = 3): HTMLDivElement {
  const wrapper = document.createElement('div')
  wrapper.className = 'flex flex-col gap-3'
  for (let i = 0; i < lines; i++) {
    const bar = document.createElement('div')
    bar.className = 'skeleton h-4'
    if (i === lines - 1) {
      bar.style.width = '60%'
    }
    wrapper.appendChild(bar)
  }
  return wrapper
}

export function renderCardSkeleton(): HTMLDivElement {
  const card = document.createElement('div')
  card.className = 'card'
  card.appendChild(renderSkeleton(3))
  return card
}
