# Slice: ui-project-scaffold

**Parent task:** add-simple-ui
**Estimated effort:** 1 slice
**Dependencies:** none

## Purpose
Set up a standalone frontend project that serves a clean UI for the LLM Analysis Service.

## What to create
- `frontend/` directory at project root
- Minimal static file server: mount FastAPI `StaticFiles` + `FileResponse` for SPA routing
- Simple HTML/CSS/JS single-page app (no build tools, no npm dependencies)
- `index.html` — main page with navigation tabs
- `frontend/css/style.css` — clean, minimal styling (CSS variables, responsive)
- `frontend/js/app.js` — tab router + API client module
- Update `docker-compose.yaml` to mount `frontend/` as volume for dev
- Update `app/main.py` to mount `/` serving `frontend/index.html`

## Acceptance criteria
- Navigating to `http://localhost:8000/` serves the UI
- UI has 4 tabs: Analyze, Documents, Metrics, Settings
- API base URL configurable via `frontend/js/config.js`
- No build step required — plain HTML/CSS/JS
- Docker dev mount reflects changes without rebuild
