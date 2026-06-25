# API Error Response Standard

This document defines a consistent error response format for Study Copilot's
FastAPI backend and describes how the static frontend should consume those
errors.

The current app already raises useful HTTP status codes in several places, but
the response body shape is not yet standardized. A shared error format will let
the frontend show clearer recovery messages without parsing many different
backend shapes.

## Current Error Behavior

### Backend validation errors

Pydantic request models currently validate:

- `GenerateCardsRequest.topic`
- `GenerateCardsRequest.difficulty`
- `GenerateCardsRequest.num_cards`
- `UploadNotesRequest.text_content`
- `UploadNotesRequest.title`
- `QuizAnswerRequest.card_id`
- `QuizAnswerRequest.selected_answer`

FastAPI returns its default validation body for these failures, generally with
HTTP `422` and a `detail` array.

### Explicit backend errors

`backend/main.py` currently raises `HTTPException` for these cases:

| Area | Status | Current detail |
| --- | --- | --- |
| PDF size | `413` | `PDF is too large. Maximum size is 10MB.` |
| PDF parsing | `400` | `Could not read PDF: ...` |
| Empty PDF text | `400` | `No readable text found in the PDF.` |
| Non-PDF upload | `400` | `Only PDF files are supported.` |
| Non-quiz answer check | `400` | `Not a quiz card.` |
| Quiz without correct option | `400` | `Quiz card has no correct option.` |
| Unknown quiz card | `404` | `Card not found.` |
| Unknown session | `404` | `Session not found.` |

### Frontend behavior

`study-copilot-full.html` currently treats most non-OK API responses as generic
failures:

- generation failure: `Error generating study platform. Check API setup.`
- quiz validation fallback: `Connection lost. Validating locally...`
- bookmark failure: `Bookmark operation failed.`
- drawer failure: `Error retrieving progress analytics.`
- session load failure: `Failed to load past session.`
- notes failure: `Failed to process notes.`
- PDF failure: `Failed to upload PDF file.`

This protects users from raw backend internals, but it also hides recoverable
validation details such as unsupported file type, oversized PDF, or notes being
too short.

## Standard Error Shape

All backend errors should eventually return this shape:

```json
{
  "success": false,
  "error": {
    "code": "pdf_too_large",
    "message": "PDF is too large. Maximum size is 10MB.",
    "field": "file",
    "details": []
  }
}
```

Fields:

| Field | Required | Description |
| --- | --- | --- |
| `success` | Yes | Always `false` for error responses. |
| `error.code` | Yes | Stable machine-readable error code. |
| `error.message` | Yes | Safe user-facing summary. |
| `error.field` | No | Field name related to the error, when applicable. |
| `error.details` | No | Optional structured validation details. |
| `error.request_id` | No | Future correlation id for logs and support. |

Rules:

- `message` must be safe to display in the frontend.
- `code` should be stable enough for frontend mapping and tests.
- `details` should be structured data, not raw stack traces.
- Do not include API keys, prompts, raw notes, extracted PDF text, or provider
  stack traces.
- Keep HTTP status codes meaningful; the JSON shape does not replace status
  codes.

## Error Code Naming

Use short snake_case codes:

- `validation_failed`
- `pdf_too_large`
- `invalid_pdf_type`
- `pdf_unreadable`
- `pdf_no_text`
- `quiz_card_required`
- `quiz_answer_missing`
- `card_not_found`
- `session_not_found`
- `ai_generation_failed`
- `provider_unavailable`
- `internal_error`

Prefer domain-specific codes when the frontend can offer a better action. Use
`internal_error` only for unexpected failures.

## Examples

### Validation failure

HTTP status: `422`

```json
{
  "success": false,
  "error": {
    "code": "validation_failed",
    "message": "Please check the highlighted fields.",
    "details": [
      {
        "field": "num_cards",
        "message": "Input should be less than or equal to 10"
      }
    ]
  }
}
```

### PDF too large

HTTP status: `413`

```json
{
  "success": false,
  "error": {
    "code": "pdf_too_large",
    "message": "PDF is too large. Maximum size is 10MB.",
    "field": "file"
  }
}
```

### Unsupported file type

HTTP status: `400`

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

### No readable PDF text

HTTP status: `400`

```json
{
  "success": false,
  "error": {
    "code": "pdf_no_text",
    "message": "No readable text was found in the PDF.",
    "field": "file"
  }
}
```

### Card not found

HTTP status: `404`

```json
{
  "success": false,
  "error": {
    "code": "card_not_found",
    "message": "Card not found."
  }
}
```

### AI provider failure

HTTP status: `503`

```json
{
  "success": false,
  "error": {
    "code": "provider_unavailable",
    "message": "AI generation is temporarily unavailable. Try sandbox mode or retry later."
  }
}
```

## Endpoint Update Matrix

| Endpoint | Current errors | Recommended update |
| --- | --- | --- |
| `POST /api/generate-cards` | Pydantic `422`; possible provider/runtime failures | Normalize validation errors and return `ai_generation_failed` or `provider_unavailable` for model failures. |
| `POST /api/upload-pdf` | `400`, `413`, raw PDF parsing detail | Map upload failures to `invalid_pdf_type`, `pdf_too_large`, `pdf_unreadable`, and `pdf_no_text`. Avoid exposing parser exception text. |
| `POST /api/upload-notes` | Pydantic `422`; possible provider/runtime failures | Normalize validation errors and provider failures. |
| `POST /api/check-answer` | `400` for non-quiz/malformed quiz, `404` for missing card | Return `quiz_card_required`, `quiz_answer_missing`, and `card_not_found`. |
| `POST /api/bookmark/{card_id}` | No explicit error path today | Return `card_not_found` if bookmark ids become validated against stored sessions. |
| `POST /api/view/{card_id}` | No explicit error path today | Return `card_not_found` if view ids become validated against stored sessions. |
| `GET /api/progress` | No explicit error path today | Return `internal_error` only for unexpected failures. |
| `GET /api/sessions` | No explicit error path today | Return `internal_error` only for unexpected failures. |
| `GET /api/session/{session_id}` | `404` for missing session | Return `session_not_found`. |

## Frontend Consumption

Add a small helper for API calls once the backend standard exists.

Expected behavior:

- Try to parse JSON on non-OK responses.
- If `error.message` exists, show that message.
- If only FastAPI's legacy `detail` exists, map it to a generic safe message.
- Keep sandbox fallbacks for offline or connection failures.
- Do not show raw parser exceptions, provider exceptions, or stack traces.

Suggested helper shape:

```js
async function parseApiResponse(response, fallbackMessage) {
  let payload = null;
  try {
    payload = await response.json();
  } catch (_) {
    payload = null;
  }

  if (response.ok) return payload;

  const message = payload?.error?.message || fallbackMessage;
  const code = payload?.error?.code || "unknown_error";
  throw new Error(`${code}:${message}`);
}
```

The UI can later split the code and message if it needs code-specific behavior.

## Migration Plan

1. Add a backend error helper that produces the standard shape.
2. Add exception handlers for `HTTPException` and request validation errors.
3. Replace raw PDF parser details with safe error codes.
4. Update endpoint tests to assert both HTTP status and error code.
5. Add a frontend response parser for non-OK JSON.
6. Replace generic upload/notes/generation toasts with safe backend messages.
7. Keep legacy `detail` fallback until all routes use the standard shape.

## Implementation Checklist

- [ ] Add a reusable backend error response helper.
- [ ] Normalize FastAPI validation errors.
- [ ] Normalize explicit `HTTPException` responses.
- [ ] Hide raw PDF parser exception text from users.
- [ ] Add endpoint tests for representative errors.
- [ ] Add frontend parsing for `success: false` responses.
- [ ] Preserve offline sandbox fallback behavior.
- [ ] Document any new error codes next to the endpoint contract.
