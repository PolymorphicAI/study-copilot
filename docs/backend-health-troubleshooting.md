# Backend Health Check Troubleshooting

Study Copilot uses the FastAPI root endpoint as the backend health check:

```text
GET http://localhost:8000/
```

The frontend also probes this endpoint before deciding whether to use the backend or fall back to local sandbox cards.

## Expected Health Response

When the backend is running, the root endpoint should return JSON similar to:

```json
{
  "status": "running",
  "app": "Study Copilot API",
  "version": "1.0.0",
  "ai_provider": "Google Gemini",
  "mode": "OFFLINE SANDBOX",
  "model": null,
  "offline_mode": true
}
```

`mode` and `offline_mode` depend on whether a valid Gemini model is available:

- `OFFLINE SANDBOX` / `true`: backend is healthy, but Gemini is not active.
- `CONNECTED TO GEMINI` / `false`: backend is healthy and a Gemini model was selected.

## Start the Backend

From the repository root:

```bash
python backend/main.py
```

Or from the backend directory:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Then open:

```text
http://localhost:8000/
```

You can also open the FastAPI docs:

```text
http://localhost:8000/docs
```

## Common Failure Causes

### Server Not Running

Symptoms:

- Browser shows `Backend Offline`.
- `http://localhost:8000/` does not load.
- Terminal has no running FastAPI or Uvicorn process.

Fix:

1. Start the backend again with `python backend/main.py`.
2. Watch the terminal for import errors or dependency errors.
3. Keep the backend terminal open while testing the frontend.

### Wrong Port

The frontend currently checks `http://localhost:8000/` and sends API calls to `http://localhost:8000/api`.

Symptoms:

- Backend is running, but on a different port.
- FastAPI docs work at another URL, but the frontend still says `Backend Offline`.

Fix:

1. Run the backend on port `8000`.
2. If a different port is required, update the frontend `API_BASE` and health check URL consistently.

### Missing Dependencies

Symptoms:

- Backend exits immediately.
- Terminal shows `ModuleNotFoundError`.
- Uvicorn cannot import `main`.

Fix:

```bash
pip install -r backend/requirements.txt
```

Then restart the backend.

### Missing or Invalid Environment Variables

The backend can run without `GOOGLE_API_KEY`, but Gemini will not be active.

Symptoms:

- Health check returns `OFFLINE SANDBOX`.
- Cards still generate, but they use fallback content.
- Frontend may show `Sandbox Mode`.

Fix:

1. Create or update `backend/.env`.
2. Set `GOOGLE_API_KEY=...` when testing live Gemini output.
3. Restart the backend after changing `.env`.

Do not commit real API keys.

### AI Provider Errors

Symptoms:

- Health check works, but card generation falls back to sandbox content.
- Gemini model discovery fails.
- Requests to generate cards return generic fallback cards.

Possible causes:

- Invalid Gemini key.
- Network failure to the AI provider.
- Model name no longer available.
- Provider quota or rate limit issue.

Fix:

1. Confirm `GOOGLE_API_KEY` is valid.
2. Restart the backend and re-check `mode`.
3. Try a small topic generation request.
4. If fallback still appears, inspect backend terminal logs.

### CORS or Browser Blocking

Symptoms:

- `http://localhost:8000/` works directly in the browser.
- Frontend still reports `Backend Offline`.
- Browser devtools show a blocked request.

Fix:

1. Confirm the backend includes CORS middleware.
2. Confirm the frontend is calling `http://localhost:8000/`.
3. Refresh the frontend after restarting the backend.
4. Check browser devtools Network and Console panels for the exact blocked request.

## Quick Verification Checklist

- [ ] `python backend/main.py` starts without crashing.
- [ ] `http://localhost:8000/` returns JSON.
- [ ] `status` is `running`.
- [ ] `mode` is either `OFFLINE SANDBOX` or `CONNECTED TO GEMINI`.
- [ ] `http://localhost:8000/docs` opens.
- [ ] The frontend status badge changes from `Connecting...`.
- [ ] `.env` changes were followed by a backend restart.

