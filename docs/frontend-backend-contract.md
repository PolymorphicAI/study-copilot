# Frontend and Backend Integration Contract

This document captures the contract between the static Study Copilot frontend in
`study-copilot-full.html` and the FastAPI backend in `backend/main.py`.

The goal is to make request payloads, response fields, and error handling
explicit so frontend and backend changes can be reviewed against one shared
source of truth.

## API Base

The frontend currently uses:

- Health endpoint: `http://localhost:8000/`
- API base: `http://localhost:8000/api`

Local development assumes CORS is enabled by the backend. The backend currently
allows all origins, methods, and headers.

## Shared Response Expectations

Successful API responses should:

- Return JSON.
- Include `success: true` for mutating or generation endpoints.
- Use stable field names that match the frontend consumers.
- Prefer explicit empty arrays over omitted fields when the frontend renders
  lists.

Error responses should:

- Return JSON.
- Include a user-safe message.
- Preserve the HTTP status code that best describes the failure.
- Avoid leaking API keys, provider stack traces, raw uploaded notes, or full PDF
  text.

Recommended error shape for future updates:

```json
{
  "success": false,
  "error": {
    "code": "invalid_pdf_type",
    "message": "Only PDF files are supported.",
    "field": "file"
  }
}
```

FastAPI currently returns validation and `HTTPException` errors using its
default `detail` shape. The frontend currently treats most non-OK responses as
generic connection failures, so a future implementation should normalize error
display after the backend standard is adopted.

## Endpoint Contract

### `GET /`

Purpose:

- Backend health check.
- AI provider availability display.

Frontend caller:

- `checkBackendConnection()`

Backend response:

```json
{
  "status": "healthy",
  "app": "Study Copilot",
  "version": "1.0.0",
  "ai_provider": "Google Gemini",
  "mode": "Active (AI)",
  "model": "gemini-1.5-flash",
  "offline_mode": false
}
```

Frontend reads:

- `mode`

Error behavior:

- Any failed request marks the backend offline and switches the frontend to
  sandbox behavior.

### `POST /api/generate-cards`

Purpose:

- Generate a study deck from a topic.

Frontend caller:

- Main generate flow when `activeTab === "topic"`.

Request:

```json
{
  "topic": "Photosynthesis",
  "difficulty": "intermediate",
  "num_cards": 5
}
```

Backend response:

```json
{
  "success": true,
  "session_id": "session_123",
  "cards": [],
  "total_cards": 5,
  "offline_mode": false
}
```

Frontend reads:

- `session_id`
- `cards`
- `total_cards` indirectly through card rendering

Notes:

- `difficulty` must be one of `beginner`, `intermediate`, or `advanced`.
- `num_cards` must stay within the backend validation range.

### `POST /api/upload-pdf`

Purpose:

- Generate a study deck from an uploaded PDF.

Frontend callers:

- Main PDF tab.
- Floating PDF upload overlay.

Request:

- Multipart `file`.
- The frontend also sends `difficulty` and `num_cards` form fields.

Backend response:

```json
{
  "success": true,
  "session_id": "pdf_session_123",
  "cards": [],
  "source_file": "notes.pdf",
  "offline_mode": false
}
```

Frontend reads:

- `session_id`
- `cards`

Current mismatch:

- `backend/main.py` currently accepts only `file` for this endpoint, so
  `difficulty` and `num_cards` are not used.

Error behavior:

- Non-PDF uploads should return `400`.
- Oversized PDFs should return `413`.
- Unreadable PDFs or PDFs with no readable text should return `400`.
- The frontend currently shows a generic upload failure toast for these cases.

### `POST /api/upload-notes`

Purpose:

- Generate a study deck from pasted notes.

Frontend callers:

- Main notes tab.
- Floating notes overlay.

Request:

```json
{
  "text_content": "Study notes text...",
  "title": "Paste Notes"
}
```

The frontend also sends `difficulty` and `num_cards` as query parameters.

Backend response:

```json
{
  "success": true,
  "session_id": "notes_session_123",
  "cards": [],
  "offline_mode": false
}
```

Frontend reads:

- `session_id`
- `cards`

Current mismatch:

- `backend/main.py` validates only `text_content` and `title`, so the current
  backend ignores `difficulty` and `num_cards`.

### `POST /api/check-answer`

Purpose:

- Validate a quiz answer and update quiz progress.

Frontend caller:

- Quiz answer selection flow.

Request:

```json
{
  "card_id": "card-1",
  "selected_answer": "A"
}
```

Backend response:

```json
{
  "correct": true,
  "correct_answer": "A",
  "explanation": "The correct answer is A: ..."
}
```

Frontend reads:

- `correct`
- `correct_answer`
- `explanation`

Error behavior:

- `400` when the card is not a quiz card.
- `400` when a quiz card has no correct option.
- `404` when the card id cannot be found in current backend memory.
- The frontend falls back to local cached validation when the request fails.

### `POST /api/bookmark/{card_id}`

Purpose:

- Bookmark the active study card.

Frontend caller:

- `toggleBookmarkCurrent()`

Backend response:

```json
{
  "success": true,
  "bookmarked": true,
  "total_bookmarks": 1
}
```

Frontend reads:

- `bookmarked`

Current mismatch:

- The frontend treats this as a toggle and removes the bookmark locally when
  `bookmarked` is false.
- The backend only appends missing ids and always returns `bookmarked: true`.

Recommended future contract:

- `POST /api/bookmark/{card_id}` should either be documented as add-only, or it
  should toggle and return the final state.
- If server-rendered bookmark lists are needed, the backend should return card
  summaries or expose a separate bookmark list endpoint.

### `POST /api/view/{card_id}`

Purpose:

- Record that a card was viewed.

Frontend caller:

- Intersection observer in `renderStudySession()`.

Backend response:

```json
{
  "success": true,
  "card_id": "card-1",
  "cards_completed": 1
}
```

Frontend reads:

- No fields are currently read from this response.

Contract note:

- The frontend can send repeated view events for the same card when it is
  observed again.
- A future contract should define whether this endpoint records raw view events
  or unique completed cards.

### `GET /api/progress`

Purpose:

- Populate drawer statistics.

Frontend caller:

- `renderDrawerStatistics()`

Backend response:

```json
{
  "cards_completed": 1,
  "quizzes_attempted": 2,
  "quizzes_correct": 1,
  "accuracy": 50.0,
  "study_streak": 0,
  "bookmarks": 1
}
```

Current frontend reads:

- `study_streak`
- `cards_viewed`
- `accuracy`
- `quizzes_correct`
- `quizzes_attempted`
- `bookmarks.length`
- `bookmarks.forEach(...)`

Current mismatch:

- The backend returns `cards_completed`, while the frontend reads
  `cards_viewed`.
- The backend returns `bookmarks` as a count, while the frontend expects an
  array of card objects.

Recommended future response:

```json
{
  "cards_viewed": 1,
  "cards_completed": 1,
  "quizzes_attempted": 2,
  "quizzes_correct": 1,
  "accuracy": 50.0,
  "study_streak": 0,
  "bookmarks": [
    {
      "id": "card-1",
      "title": "Intro",
      "type": "concept"
    }
  ]
}
```

### `GET /api/sessions`

Purpose:

- Populate the session history list in the drawer.

Frontend caller:

- `renderDrawerStatistics()`

Backend response:

```json
{
  "sessions": [
    {
      "session_id": "session_123",
      "topic": "Photosynthesis",
      "num_cards": 5,
      "created_at": "2026-06-26T00:00:00",
      "offline_mode": false
    }
  ]
}
```

Frontend reads:

- `sessions`
- `session_id`
- `topic`
- `difficulty`
- `num_cards`

Current mismatch:

- Session summaries do not include `difficulty`, but the frontend renders
  `sess.difficulty.toUpperCase()`.

Recommended future contract:

- Always include `difficulty`, or make the frontend handle missing difficulty.

### `GET /api/session/{session_id}`

Purpose:

- Load a previous study session.

Frontend caller:

- `loadSessionFromHistory(sessionId)`

Backend response:

Current responses are the stored session dictionaries. Their fields vary by
source:

- Topic sessions include `topic`, `cards`, `created_at`, and `offline_mode`.
- PDF sessions include `source`, `cards`, `created_at`, and `offline_mode`.
- Notes sessions include `title`, `cards`, `created_at`, and `offline_mode`.

Frontend reads:

- `cards`
- `session_id`
- `topic`

Current mismatch:

- The response does not include `session_id`.
- PDF and notes sessions may not include `topic`.

Recommended future response:

```json
{
  "session_id": "session_123",
  "topic": "Photosynthesis",
  "source": "topic",
  "difficulty": "intermediate",
  "cards": [],
  "created_at": "2026-06-26T00:00:00",
  "offline_mode": false
}
```

## Card Object Contract

The frontend card renderer expects each card to provide:

- `id`
- `type`
- `title`
- `content`
- `timestamp`

Optional fields:

- `code_example`
- `quiz_options`
- `quiz_answer` or equivalent local fallback answer data
- `quiz_explanation` or equivalent local fallback explanation data

Quiz option objects should provide:

- `option`
- `text`
- `correct`

## Frontend Fallback Rules

The frontend switches to sandbox mode when the health check fails. In sandbox
mode:

- Card generation uses local mock cards.
- Quiz validation uses locally stored mock answer fields.
- Bookmarks are stored in the in-memory `bookmarkedCardIds` set.
- Drawer statistics are computed from the current in-memory session.
- Past sessions are not available.

Backend contract changes should preserve this offline fallback path.

## Follow-up Checklist

- [ ] Normalize `cards_viewed` versus `cards_completed`.
- [ ] Decide whether progress bookmarks are a count, ids, or card summaries.
- [ ] Add `difficulty` handling to PDF and notes generation, or stop sending it.
- [ ] Add `num_cards` handling to PDF and notes generation, or stop sending it.
- [ ] Include `session_id` in `GET /api/session/{session_id}` responses.
- [ ] Include a stable display title for topic, PDF, and notes sessions.
- [ ] Include `difficulty` in session summaries or handle missing difficulty.
- [ ] Decide whether bookmark writes are add-only or toggle semantics.
- [ ] Define one shared API error schema and update frontend toast handling.
- [ ] Add lightweight contract tests for response field names.
