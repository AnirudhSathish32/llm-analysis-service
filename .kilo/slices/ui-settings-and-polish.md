# Slice: ui-settings-and-polish

**Parent task:** add-simple-ui
**Estimated effort:** 1 slice
**Dependencies:** ui-project-scaffold

## Purpose
Build the Settings tab and apply final polish across the UI.

## What to create
In `frontend/js/tabs/settings.js`:
- API base URL input (default: current origin)
- Rate limit display (shows current limit if available)
- Provider status indicators (Anthropic/Gemini — based on last response)
- Reset localStorage button (clears recent documents, cached settings)
- Dark/light theme toggle (CSS variable swap)

Polish across all tabs:
- Consistent error toast component
- Loading skeleton states
- Responsive layout (mobile-friendly)
- Keyboard shortcuts: Ctrl+1-4 for tab navigation
- Favicon and page title

## Acceptance criteria
- Settings tab persists API URL in localStorage
- Theme toggle switches between light and dark modes
- Error toasts appear consistently across all tabs
- Layout works on mobile viewport (375px width)
- Tab keyboard shortcuts work
- No console errors on page load
- All tabs have consistent styling and spacing
