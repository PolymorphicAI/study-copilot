# Offline Sandbox Mode

Study Copilot includes fallback behavior so reviewers and contributors can demo the learning flow even when the backend or Gemini API is unavailable.

There are two related fallback paths:

- Frontend sandbox mode: `study-copilot-full.html` generates local demo cards when the FastAPI backend cannot be reached.
- Backend fallback mode: `backend/main.py` returns generated fallback cards when the backend is running but Gemini is not configured or cannot generate content.

## When It Activates

Frontend sandbox mode activates when the browser cannot reach the backend health endpoint at `http://localhost:8000/`.

Common triggers:

- The FastAPI server is not running.
- The server is running on a different port.
- A local firewall, browser policy, or CORS issue blocks the request.
- The health request times out or fails before the app starts a learning session.

Backend fallback mode activates when `backend/main.py` is reachable but the Gemini integration is not available.

Common triggers:

- `GOOGLE_API_KEY` is missing from `backend/.env`.
- The configured Gemini key is invalid.
- Gemini model discovery fails.
- A Gemini request fails during card generation, PDF upload, or notes upload.

## What Reviewers Should See

When the backend is offline:

1. The status indicator changes to `Backend Offline`.
2. Starting a topic, PDF, or notes flow shows a sandbox toast.
3. The app creates local demo study cards after a short loading state.
4. Quiz cards, navigation, and bookmarks remain usable for a frontend demo.

When the backend is online but Gemini is unavailable:

1. The backend health response reports offline fallback state.
2. The frontend may show `Sandbox Mode`.
3. API calls still return structured study cards from backend fallback helpers.
4. Progress, bookmark, and session endpoints continue to respond from backend memory.

## How to Test Frontend Sandbox Mode

1. Make sure no backend is running on port `8000`.
2. Open `study-copilot-full.html` in a browser.
3. Wait for the status indicator to show `Backend Offline`.
4. Enter a topic such as `Stellar basics`.
5. Click `Start Learning`.

Expected result:

- The app shows a sandbox/offline toast.
- A local lesson opens with multiple study cards.
- Keyboard navigation still works.
- Quiz answer feedback works from locally cached mock answers.
- Bookmark toggles are stored locally for the current browser session.

## How to Test Backend Fallback Mode

1. Start the backend without a valid Gemini key:

   ```bash
   python backend/main.py
   ```

2. Open the health endpoint:

   ```text
   http://localhost:8000/
   ```

3. Confirm the response includes an offline fallback mode.
4. Open `study-copilot-full.html`.
5. Generate cards from a topic, PDF, or pasted notes.

Expected result:

- The frontend reaches the backend instead of using local mock generation.
- The backend returns fallback study cards.
- The UI still opens the normal lesson view.

## Limitations

Offline sandbox mode is for demos and contributor testing. It is not a substitute for live AI validation.

Known limitations:

- Local frontend cards are generic and are not based on the exact topic, PDF, or notes content.
- Frontend-only sandbox state is not persisted across browser sessions.
- Backend fallback cards are deterministic helper content, not Gemini output.
- Progress and sessions are in-memory backend state and reset when the server restarts.
- PDF parsing issues can only be fully validated with the backend running.
- Live Gemini model behavior still needs a valid `GOOGLE_API_KEY`.

## Contributor Notes

When changing offline or fallback behavior, verify both paths:

- Backend stopped: frontend local sandbox mode.
- Backend running without Gemini: backend fallback mode.
- Backend running with Gemini: live generation path, when a valid key is available.

Keep fallback messaging clear so reviewers can tell whether they are seeing live AI output, backend fallback output, or frontend-only demo cards.

