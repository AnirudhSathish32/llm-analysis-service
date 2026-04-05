export interface CardProps {
  children: HTMLElement | HTMLElement[]
  className?: string
}

export function renderCard(props: CardProps): HTMLDivElement {
  const card = document.createElement('div')
  card.className = `card ${props.className ?? ''}`
  const children = Array.isArray(props.children) ? props.children : [props.children]
  children.forEach((child) => card.appendChild(child))
  return card
}
