# API Endpoint Reference

This document summarizes the current FastAPI endpoints implemented in `backend/main.py`. It is intended as a quick reference for frontend contributors, backend contributors, and reviewers.

Default local backend URL:

```text
http://localhost:8000
```

Default frontend API base:

```text
http://localhost:8000/api
```

## Endpoint Table

| Method | Path | Purpose | Request | Success response |
| --- | --- | --- | --- | --- |
| `GET` | `/` | Backend health check and AI mode status. | None | App metadata and offline/Gemini mode. |
| `POST` | `/api/generate-cards` | Generate study cards from a topic. | JSON `GenerateCardsRequest` | Session id, cards, count, offline flag. |
| `POST` | `/api/upload-pdf` | Extract PDF text and generate cards. | Multipart PDF file named `file` | Session id, cards, source file, offline flag. |
| `POST` | `/api/upload-notes` | Generate cards from pasted notes. | JSON `UploadNotesRequest` | Session id, cards, offline flag. |
| `POST` | `/api/check-answer` | Validate a quiz answer. | JSON `QuizAnswerRequest` | Correct flag, correct answer, explanation. |
| `POST` | `/api/bookmark/{card_id}` | Save a card id to bookmarks. | Path parameter | Bookmark count and status. |
| `POST` | `/api/view/{card_id}` | Record a card view/completion. | Path parameter | Updated completed-card count. |
| `GET` | `/api/progress` | Read aggregate progress stats. | None | Cards completed, quiz stats, accuracy, bookmarks. |
| `GET` | `/api/sessions` | List generated study sessions. | None | Session summaries. |
| `GET` | `/api/session/{session_id}` | Read one stored session. | Path parameter | Full session record. |

## Request Models

### GenerateCardsRequest

```json
{
  "topic": "Stellar basics",
  "difficulty": "intermediate",
  "num_cards": 5
}
```

Validation:

- `topic`: 2 to 200 characters.
- `difficulty`: `beginner`, `intermediate`, or `advanced`.
- `num_cards`: integer from 3 to 10.

### UploadNotesRequest

```json
{
  "text_content": "Paste study notes or article text here.",
  "title": "Lecture notes"
}
```

Validation:

- `text_content`: 10 to 15,000 characters.
- `title`: 2 to 200 characters.

### QuizAnswerRequest

```json
{
  "card_id": "session_0_123456789",
  "selected_answer": "B"
}
```

## Response Examples

### Health Check

```http
GET /
```

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

### Generate Cards

```http
POST /api/generate-cards
Content-Type: application/json
```

```json
{
  "topic": "Stellar basics",
  "difficulty": "beginner",
  "num_cards": 5
}
```

```json
{
  "success": true,
  "session_id": "session_1234567890.0",
  "cards": [],
  "total_cards": 5,
  "offline_mode": true
}
```

`cards` contains the generated study card objects. The example uses an empty array placeholder to keep the response shape short.

### Upload PDF

```http
POST /api/upload-pdf
Content-Type: multipart/form-data
```

Request field:

```text
file=<example.pdf>
```

```json
{
  "success": true,
  "session_id": "pdf_session_1234567890.0",
  "cards": [],
  "source_file": "example.pdf",
  "offline_mode": true
}
```

### Upload Notes

```http
POST /api/upload-notes
Content-Type: application/json
```

```json
{
  "text_content": "These are notes about accounts, assets, and transactions.",
  "title": "Stellar lecture"
}
```

```json
{
  "success": true,
  "session_id": "notes_session_1234567890.0",
  "cards": [],
  "offline_mode": true
}
```

### Check Answer

```http
POST /api/check-answer
Content-Type: application/json
```

```json
{
  "card_id": "Stellar_basics_2_1234567890.0",
  "selected_answer": "B"
}
```

```json
{
  "correct": true,
  "correct_answer": "B",
  "explanation": "The correct answer is B: Start with core concepts"
}
```

### Progress

```http
GET /api/progress
```

```json
{
  "cards_completed": 3,
  "quizzes_attempted": 2,
  "quizzes_correct": 1,
  "accuracy": 50.0,
  "study_streak": 0,
  "bookmarks": 1
}
```

### Sessions

```http
GET /api/sessions
```

```json
{
  "sessions": [
    {
      "session_id": "session_1234567890.0",
      "topic": "Stellar basics",
      "num_cards": 5,
      "created_at": "2026-06-25T12:00:00",
      "offline_mode": true
    }
  ]
}
```

## Error Responses

Common errors:

| Status | Endpoint | Cause |
| --- | --- | --- |
| `400` | `/api/upload-pdf` | Uploaded file is not a PDF. |
| `400` | `/api/upload-pdf` | PDF cannot be read. |
| `400` | `/api/upload-pdf` | PDF contains no readable text. |
| `400` | `/api/check-answer` | Card is not a quiz card. |
| `400` | `/api/check-answer` | Quiz card has no correct option. |
| `404` | `/api/check-answer` | Card id is not found in stored sessions. |
| `404` | `/api/session/{session_id}` | Session id is not found. |
| `413` | `/api/upload-pdf` | PDF is larger than 10MB. |
| `422` | JSON endpoints | Request body fails Pydantic validation. |

Example error shape:

```json
{
  "detail": "Only PDF files are supported."
}
```

## State Notes

The current backend stores sessions, bookmarks, and progress in memory. Restarting the backend clears that state.

When Gemini is unavailable, endpoints can still return fallback cards with `offline_mode: true`.

