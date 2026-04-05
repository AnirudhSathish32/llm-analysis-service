# Slice: ui-settings-and-polish

**Parent task:** add-simple-ui
**Estimated effort:** 1 slice
**Dependencies:** slice-001-scaffold

## Purpose
Build the Settings tab and apply final polish across the UI.

## What to create
In `frontend/src/tabs/settings.ts`:
- API base URL input (default: current origin)
- Rate limit display (shows current limit if available)
- Provider status indicators (Anthropic/Gemini — based on last response)
- Reset localStorage button (clears recent documents, cached settings)
- Dark/light theme toggle (Tailwind `dark` class on `<html>`)

Polish across all tabs:
- Consistent error toast component (`frontend/src/components/toast.ts`)
- Loading skeleton states (`frontend/src/components/skeleton.ts`)
- Responsive layout (mobile-first Tailwind breakpoints)
- Keyboard shortcuts: Ctrl+1-4 for tab navigation
- Favicon and page title
- Lucide SVG icons for all iconography (no emojis)

### Component usage
- `Toggle` component for theme switch
- `Button` component with `variant="danger"` for reset
- `Card` component for settings sections
- `Toast` component (shared across all tabs)
- `Skeleton` component for loading placeholders

## Acceptance criteria
- Settings tab persists API URL in localStorage
- Theme toggle switches between light and dark modes (adds/removes `dark` class on `<html>`)
- Error toasts appear consistently across all tabs
- Layout works on mobile viewport (375px width)
- Tab keyboard shortcuts work
- No console errors on page load
- All tabs have consistent styling and spacing
- Light mode contrast meets 4.5:1 for body text (not just dark mode)
- Theme preference respects `prefers-color-scheme` on first visit
- Toast auto-dismisses in 3-5s with manual close option
- Reset action shows confirmation dialog before clearing
- `prefers-reduced-motion` respected (no animations when enabled)
- Focus states visible: 2-4px ring on all interactive elements (`focus:ring-2 focus:ring-accent`)
- No horizontal scroll at any breakpoint (375 / 768 / 1024 / 1440)
- z-index scale enforced: 10 (dropdowns) / 20 (modals) / 30 (toasts) / 100 (overlays)
- All CSS uses Tailwind utility classes (no raw hex in component styles)
- `tsc --noEmit` passes with zero errors across entire frontend
- `npm run build` produces optimized production bundle
