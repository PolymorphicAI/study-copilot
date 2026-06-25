# Deployment Plan

This document outlines deployment options for Study Copilot's static frontend
and FastAPI backend, plus the environment and secret handling needed to run the
app outside local development.

## Current Architecture

Study Copilot is split into:

- `study-copilot-full.html`: a static HTML/CSS/JavaScript frontend.
- `backend/main.py`: a FastAPI backend with Gemini support and offline fallback.
- `backend/requirements.txt`: Python runtime dependencies.

The frontend currently calls:

- health endpoint: `http://localhost:8000/`
- API base: `http://localhost:8000/api`

The backend reads:

- `GOOGLE_API_KEY`: optional Gemini API key for live AI generation.
- `PORT`: optional server port, defaulting to `8000`.

## Recommended Deployment Shape

Deploy the frontend and backend separately:

1. Host the static frontend on a static site platform.
2. Host the FastAPI backend on a Python web service platform.
3. Configure the frontend to call the deployed backend API URL.
4. Configure the backend CORS policy for the deployed frontend URL.
5. Store AI provider secrets only in backend environment variables.

This keeps the API key off the client and lets the static frontend remain cheap
and cacheable.

## Static Frontend Hosting Options

### GitHub Pages

Best for:

- Free static previews.
- Simple demos.
- Documentation-style deployments.

Notes:

- Serves `study-copilot-full.html` directly.
- Requires the frontend API base URL to point at the deployed backend.
- Does not host the FastAPI backend.
- Works well for sandbox fallback mode when the backend is unavailable.

### Netlify

Best for:

- Simple static hosting with preview deploys.
- Easy custom domains.
- Environment-specific frontend variables if a build step is later added.

Notes:

- Current app has no build step, so it can publish the repository root or a
  small frontend directory if one is introduced later.
- If the API URL remains hard-coded in the HTML, each environment needs the
  right value committed or injected during deployment.

### Vercel

Best for:

- Static frontend previews.
- Branch deployments.
- Future frontend build tooling.

Notes:

- Current single-file frontend can be hosted as static output.
- The FastAPI backend should still run as a separate service unless the project
  is intentionally adapted to Vercel functions.

### Cloudflare Pages

Best for:

- Static hosting with global CDN.
- Preview deployments.
- Future edge routing in front of the API.

Notes:

- Current app can be published without a build command.
- Backend hosting remains separate.

## FastAPI Backend Hosting Options

### Render Web Service

Best for:

- Straightforward Python web service hosting.
- Environment variables through a dashboard.
- Small demos and early MVP deployments.

Suggested settings:

- Runtime: Python.
- Build command: `pip install -r backend/requirements.txt`
- Start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  - `GOOGLE_API_KEY`
  - `PORT`
  - future `ALLOWED_ORIGINS`

### Railway

Best for:

- Fast preview environments.
- Simple Python service deployment.
- Environment variable management.

Suggested settings:

- Install command: `pip install -r backend/requirements.txt`
- Start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- Expose the generated public service URL to the frontend.

### Fly.io

Best for:

- Container-based deployments.
- More control over regions and runtime.

Notes:

- Add a Dockerfile before using this path.
- Keep `GOOGLE_API_KEY` in Fly secrets.
- Use `$PORT` or the platform's configured internal port.

### VPS or VM

Best for:

- Full control.
- Long-running prototypes.
- Teams comfortable maintaining servers.

Suggested setup:

- Install Python 3.10+.
- Install `backend/requirements.txt`.
- Run `uvicorn main:app --host 0.0.0.0 --port 8000` from the `backend/`
  directory behind a process manager.
- Put HTTPS and domain routing in front of the service with a reverse proxy.

## Environment and Secrets

Backend-only variables:

| Variable | Required | Purpose | Secret? |
| --- | --- | --- | --- |
| `GOOGLE_API_KEY` | No | Enables live Gemini card generation. Without it, backend uses offline fallback. | Yes |
| `PORT` | No | Port used by the FastAPI service. Defaults to `8000`. | No |
| `ALLOWED_ORIGINS` | Future | Comma-separated frontend origins for production CORS. | No |

Rules:

- Never put `GOOGLE_API_KEY` in `study-copilot-full.html`.
- Never commit `.env` files with real secrets.
- Configure `GOOGLE_API_KEY` only in the backend host.
- Rotate the key if it is accidentally exposed in logs, screenshots, or commits.
- Keep local `.env` examples generic and non-sensitive.

## Required Code/Config Follow-ups

Before production deployment, the project should add a few small configuration
improvements:

1. Make the frontend API base configurable.
   - Current value is `http://localhost:8000/api`.
   - Hosted frontend should point to the deployed backend URL.
   - A simple first step is a single `API_BASE` constant documented per
     deployment environment.
2. Restrict backend CORS in production.
   - Current backend allows all origins.
   - Production should use configured frontend origins.
3. Add a deployment-specific health check.
   - `GET /` already returns backend status and mode.
   - Hosting platforms can use it for uptime checks.
4. Decide whether PDF uploads need size limits at the reverse proxy level.
   - Backend already caps PDF bytes in app code.
   - Platform request size limits should be documented too.

## Deployment Steps

### Backend first

1. Create a Python web service on the selected host.
2. Set the build command:
   - `pip install -r backend/requirements.txt`
3. Set the start command:
   - `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add `GOOGLE_API_KEY` as a backend secret if live AI generation is desired.
5. Deploy the service.
6. Open the backend URL and confirm `GET /` returns JSON.
7. Record the public API base URL, for example:
   - `https://study-copilot-api.example.com/api`

### Frontend second

1. Update the frontend API base for the deployed backend.
2. Create a static site deployment.
3. Publish `study-copilot-full.html`.
4. Open the deployed frontend.
5. Confirm the status indicator reports the deployed backend mode.
6. Generate cards from a topic.
7. Test PDF and notes flows if the backend host allows multipart uploads.

## Smoke Test Checklist

Run these after each deployment:

- [ ] `GET /` returns backend status JSON.
- [ ] Frontend status indicator changes from offline to online.
- [ ] Topic generation returns a deck.
- [ ] Notes upload returns a deck.
- [ ] PDF upload rejects non-PDF files.
- [ ] PDF upload handles a small valid PDF.
- [ ] Quiz answer checking returns correctness and explanation.
- [ ] Bookmark action returns a response.
- [ ] Progress drawer opens without a JavaScript error.
- [ ] Removing `GOOGLE_API_KEY` still allows offline fallback mode.

## Production Risks to Track

- The frontend API URL is currently hard-coded for local development.
- CORS is currently broad for local convenience.
- Backend progress/session storage is in process memory and will reset on
  restart.
- Uploaded PDF and notes text should not be logged or persisted without a
  retention policy.
- Free-tier backend services may sleep, which can make the frontend appear
  offline until the service wakes up.
- Large PDF uploads may hit platform request limits before reaching FastAPI.

## Recommended Initial Path

For the first hosted demo:

1. Deploy the backend to Render or Railway.
2. Set `GOOGLE_API_KEY` in the backend host.
3. Host the static frontend on Netlify, Vercel, Cloudflare Pages, or GitHub
   Pages.
4. Point `API_BASE` at the deployed backend.
5. Keep backend storage ephemeral and document that progress resets on restart.
6. Tighten CORS after the frontend URL is stable.

This path keeps the deployment simple while preserving the most important
security boundary: AI provider secrets stay on the backend only.
