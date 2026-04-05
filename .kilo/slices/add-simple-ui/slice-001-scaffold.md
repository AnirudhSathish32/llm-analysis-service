# Slice: ui-project-scaffold

**Parent task:** add-simple-ui
**Estimated effort:** 1 slice
**Dependencies:** none

## Purpose
Set up a TypeScript + Tailwind CSS frontend project that serves a clean UI for the LLM Analysis Service.

## Design System (from ui-ux-pro-max skill)

**Product type:** Developer Tool / API Dashboard — users submit text, upload documents, monitor usage
**Style:** Minimalism + Dark Mode — clean, utilitarian, data-first
**Stack:** TypeScript + Tailwind CSS + Vite (SPA, no framework)

### Tailwind Config Extensions
```ts
// tailwind.config.ts
theme.extend: {
  colors: {
    bg: { primary: '#0f1117', secondary: '#1a1d27', tertiary: '#242836' },
    text: { primary: '#e8eaed', secondary: '#9aa0b0' },
    accent: { DEFAULT: '#6c63ff', hover: '#7b73ff' },
    success: '#34d399',
    warning: '#fbbf24',
    error: '#f87171',
    border: { DEFAULT: '#2d3142', focus: '#6c63ff' },
  },
  fontFamily: {
    sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
    mono: ['"Fira Code"', 'monospace'],
  },
}
```

### CSS Base
- `@tailwind base` — reset + dark mode default on `<html>`
- `@tailwind components` — reusable component classes (`.btn`, `.card`, `.badge`, `.input`)
- `@tailwind utilities` — utility classes
- `darkMode: 'class'` in tailwind config for manual toggle
- `font-variant-numeric: tabular-nums` on data elements

### Spacing
- Tailwind default scale (4px base): 1 / 2 / 3 / 4 / 6 / 8 / 12
- Touch targets: `min-h-[44px] min-w-[44px]`
- Card padding: `p-4`
- Input padding: `py-3 px-3`

### Layout
- Mobile-first breakpoints: sm (640) / md (768) / lg (1024) / xl (1280)
- Max content width: `max-w-6xl`
- z-index scale: 10 (dropdowns) / 20 (modals) / 30 (toasts) / 100 (overlays)

### Anti-patterns to Avoid
- No emoji as icons (use Lucide SVG icons via `lucide-static` or inline SVG)
- No hover-only interactions (tap-friendly always)
- No arbitrary values in components (use theme tokens)
- No horizontal scroll on mobile
- No disabled zoom via viewport meta

## What to create
- `frontend/` directory at project root
- Vite + TypeScript project (`npm create vite@latest frontend -- --template vanilla-ts`)
- Tailwind CSS installed and configured (`npx tailwindcss init -p`)
- `frontend/src/index.html` — main page shell with tab container
- `frontend/src/style.css` — Tailwind directives + base styles
- `frontend/src/main.ts` — tab router + app bootstrap
- `frontend/src/api/client.ts` — typed API client for all endpoints
- `frontend/src/api/types.ts` — TypeScript interfaces for all request/response schemas
- `frontend/src/components/` — reusable UI components (Button, Card, Badge, Input, Toast)
- `frontend/src/tabs/` — tab modules (analyze, documents, metrics, settings)
- `frontend/src/config.ts` — API base URL, constants
- Update `docker-compose.yaml` to mount `frontend/` as volume for dev
- Update `app/main.py` to mount `/` serving Vite's `dist/` output
- Add `Dockerfile.frontend` for production build (multi-stage: node build → nginx or served by FastAPI)

## Acceptance criteria
- Navigating to `http://localhost:8000/` serves the UI
- UI has 4 tabs: Analyze, Documents, Metrics, Settings
- TypeScript compiles with zero errors (`tsc --noEmit` passes)
- Tailwind purges unused styles in production build
- Vite dev server with HMR for development
- Docker dev mount reflects changes without rebuild
- Dark mode is the default (`class="dark"` on `<html>`)
- All touch targets >= 44x44px
- No horizontal scroll at 375px viewport
- Contrast ratios meet 4.5:1 for body text
- All API calls are typed (no `any` in api client)
