# CORS Configuration

Study Copilot serves a static single-file frontend from `study-copilot-full.html` and a FastAPI backend from `backend/main.py`. The frontend calls the backend at `http://localhost:8000/api`, so browser CORS behavior matters during local setup and future deployments.

## Current Local Configuration

The primary backend enables FastAPI CORS middleware in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This development default allows the frontend to work whether reviewers open `study-copilot-full.html` directly from disk, serve it from a local static server, or run it from another localhost port.

The same permissive local pattern also appears in the alternate backend entrypoints:

- `backend/main_grok.py`
- `backend/main_huggingface.py`

## Local Development Notes

Use the default local setup unless you are testing a deployment-like environment:

1. Start the backend with `python backend/main.py`.
2. Confirm the API is available at `http://localhost:8000/docs`.
3. Open `study-copilot-full.html` in a browser.
4. Use the status indicator to confirm the frontend can reach the backend or has fallen back to sandbox mode.

If the frontend cannot reach the backend, check these items first:

- The backend process is running and listening on port `8000`.
- The browser is calling `http://localhost:8000/api`, which is the current `API_BASE` in `study-copilot-full.html`.
- The backend was restarted after any code or environment changes.
- The browser devtools Network tab shows a response from the backend instead of a blocked preflight request.

## Production Recommendation

Do not keep `allow_origins=["*"]` for a production deployment that serves real user traffic. Replace it with an explicit list of trusted frontend origins.

Example:

```python
ALLOWED_ORIGINS = [
    "https://study-copilot.example.com",
    "https://www.study-copilot.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

Deployment owners should make the final origin list match the actual hosted frontend domains. If a preview environment is used, add only the specific preview hostnames that need backend access.

## Troubleshooting CORS Errors

Common browser messages include:

- `No 'Access-Control-Allow-Origin' header is present`
- `Response to preflight request doesn't pass access control check`
- `CORS policy: Request header field ... is not allowed`

Use this checklist:

1. Confirm the request URL matches the running backend host and port.
2. Confirm the frontend origin is included in `allow_origins`.
3. Confirm the HTTP method is included in `allow_methods`.
4. Confirm any custom headers are included in `allow_headers`.
5. Restart the backend after changing middleware configuration.
6. Retry in a fresh browser tab to avoid stale failed preflight cache behavior.

If the backend is unavailable, the frontend may show offline or sandbox behavior instead of a CORS-specific message. In that case, verify the backend health endpoint before changing CORS settings.

