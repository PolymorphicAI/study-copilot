# Study Session Data Model

Study Copilot currently keeps sessions and progress in memory while the app is running. This document proposes a data model for generated study decks, card progress, bookmarks, and quiz attempts so future work can add persistence without changing the learning experience.

## Current Behavior

The FastAPI backend stores generated sessions in `study_sessions` and aggregate progress in `user_progress` in `backend/main.py`.

Current session sources include:

- `/api/generate-cards` for topic-based card generation.
- `/api/upload-notes` for pasted notes.
- `/api/upload-pdf` for extracted PDF text.

The frontend keeps the active deck in `studyCardsList`, tracks the active `currentSessionId`, and calls backend endpoints for card views, bookmarks, quiz answers, progress, session history, and session reloads.

## Goals

- Preserve generated decks so learners can resume previous study sessions.
- Track card-level progress without relying only on aggregate counters.
- Support bookmarks, quiz attempts, and future progress analytics.
- Avoid storing raw notes or extracted PDF text by default.
- Leave room for future user accounts, wallet identity, and portable credentials.

## Core Entities

### StudySession

Represents one generated deck from a topic, notes upload, or PDF upload.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Stable session identifier. Avoid timestamp-only IDs in persistent storage. |
| `user_id` | string or null | Optional until accounts exist. Can later map to wallet identity or auth user. |
| `source_type` | enum | `topic`, `notes`, `pdf`, or `sandbox`. |
| `source_title` | string | User-facing topic, notes title, or PDF filename. |
| `difficulty` | enum | `beginner`, `intermediate`, or `advanced` when available. |
| `card_count` | integer | Number of generated cards. |
| `ai_provider` | string | Provider/model family used for the generation when known. |
| `offline_mode` | boolean | Whether fallback cards were used. |
| `created_at` | timestamp | Session creation time. |
| `updated_at` | timestamp | Last progress or metadata update. |
| `completed_at` | timestamp or null | Set when the learner finishes the deck. |
| `deleted_at` | timestamp or null | Soft delete marker for privacy-friendly removal. |

### StudyCard

Represents a generated learning card within a session.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Stable card identifier. |
| `session_id` | string | Parent `StudySession.id`. |
| `position` | integer | Zero-based or one-based order within the deck. |
| `type` | enum | `concept`, `quiz`, `takeaway`, `challenge`, or `code`. |
| `title` | string | Short learner-facing title. |
| `content` | text | Main card body. |
| `code_example` | text or null | Optional code block for code/challenge cards. |
| `quiz_options` | JSON or related rows | Options for quiz cards. |
| `created_at` | timestamp | Card generation time. |

For relational storage, `quiz_options` can be normalized into a `QuizOption` table. For a small MVP, a JSON column is acceptable as long as validation enforces one correct answer.

### CardProgress

Represents a learner's interaction with one card.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Stable progress row identifier. |
| `user_id` | string or null | Optional until accounts exist. |
| `session_id` | string | Parent session. |
| `card_id` | string | Parent card. |
| `first_viewed_at` | timestamp or null | First time the card became active. |
| `last_viewed_at` | timestamp or null | Most recent view time. |
| `view_count` | integer | Count of meaningful views, not every scroll event. |
| `completed` | boolean | True when a learner reaches the card or answers it if quiz-based. |
| `completed_at` | timestamp or null | Completion time. |

### Bookmark

Represents a learner-saved card.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Stable bookmark identifier. |
| `user_id` | string or null | Optional until accounts exist. |
| `session_id` | string | Session containing the card. |
| `card_id` | string | Saved card. |
| `created_at` | timestamp | Bookmark time. |
| `deleted_at` | timestamp or null | Allows undo/history without hard delete. |

Use a unique constraint on `user_id + card_id` when accounts exist. Before accounts, use a browser session ID or temporary learner ID if persistence is introduced.

### QuizAttempt

Represents one submitted answer for a quiz card.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Stable attempt identifier. |
| `user_id` | string or null | Optional until accounts exist. |
| `session_id` | string | Parent session. |
| `card_id` | string | Quiz card. |
| `selected_option` | string | Submitted option identifier or text. |
| `is_correct` | boolean | Whether the answer matched the correct option. |
| `answered_at` | timestamp | Submission time. |

## Suggested Relationships

```text
StudySession 1 -> many StudyCard
StudySession 1 -> many CardProgress
StudyCard 1 -> many CardProgress
StudyCard 1 -> many Bookmark
StudyCard 1 -> many QuizAttempt
User 1 -> many StudySession (future)
User 1 -> many Bookmark (future)
User 1 -> many QuizAttempt (future)
```

## API Shape

The existing API can keep its current response shape while adding stable fields:

- `POST /api/generate-cards` returns `session_id`, `cards`, `total_cards`, and `offline_mode`.
- `POST /api/upload-notes` returns the same session shape.
- `POST /api/upload-pdf` returns the same session shape plus `source_file`.
- `POST /api/view/{card_id}` should eventually write or update `CardProgress`.
- `POST /api/bookmark/{card_id}` should eventually toggle a `Bookmark` row.
- `POST /api/quiz-answer` should eventually write a `QuizAttempt` row.
- `GET /api/sessions` should list session summaries without returning full card bodies.
- `GET /api/session/{session_id}` can return the full deck for resume.

## Privacy And Retention

- Do not store raw pasted notes or extracted PDF text by default.
- Store generated cards and source metadata only when the learner expects session history.
- Provide a delete path that removes sessions, cards, bookmarks, progress, and quiz attempts.
- Avoid storing full provider prompts or raw AI responses unless explicitly needed for debugging.
- If debugging logs are added, redact user material and expire logs quickly.
- Treat PDF filenames and notes titles as potentially sensitive.
- When wallet identity is added, avoid tying sensitive study content directly to public on-chain identifiers.

## MVP Storage Recommendation

For a first persistent version, use SQLite or Postgres with the entities above and keep raw source material out of the database. Store only:

- session metadata,
- generated cards,
- card progress,
- bookmarks,
- quiz attempts.

This keeps the product useful while reducing the privacy risk of retaining full study materials.

## Migration Plan

1. Replace timestamp-only session IDs with UUIDs.
2. Add a storage adapter interface for sessions, cards, progress, bookmarks, and quiz attempts.
3. Implement an in-memory adapter that preserves current behavior.
4. Add a SQLite or Postgres adapter behind the same interface.
5. Update endpoints to write through the adapter.
6. Add tests for creating, listing, loading, bookmarking, viewing, answering, and deleting sessions.
7. Add a user-facing setting for clearing local or persisted history.

## Open Questions

- Should anonymous learners get a temporary local user ID before account support exists?
- How long should generated decks persist by default?
- Should bookmarks survive if the parent session is deleted?
- Should quiz attempts keep every answer or only the latest answer per card?
- Should future wallet-linked credentials store only achievement proofs instead of study content?
