# Bookmarks and Progress Storage Strategy

This document reviews the current bookmark and progress behavior in Study Copilot
and recommends an MVP storage approach for anonymous learners, with a path toward
durable sync when user identity is introduced.

## Current Behavior

### Frontend state

- `study-copilot-full.html` keeps bookmark state in `bookmarkedCardIds`, an
  in-memory `Set`.
- Offline bookmark toggles add or remove ids from that `Set`, then refresh the
  active card UI.
- Offline drawer statistics are derived from the current browser session:
  `currentCardIndex`, `studyCardsList`, and `bookmarkedCardIds`.
- The frontend does not currently read from `localStorage` or `sessionStorage`
  for bookmarks, viewed cards, study sessions, or progress.
- A browser refresh clears the anonymous bookmark and progress state unless the
  backend is online and still has its in-memory data.

### Backend state

- `backend/main.py` stores generated decks in the module-level
  `study_sessions` dictionary.
- `backend/main.py` stores aggregate progress in the module-level
  `user_progress` dictionary:
  - `cards_completed`
  - `quizzes_correct`
  - `quizzes_attempted`
  - `bookmarks`
  - `study_streak`
- `POST /api/bookmark/{card_id}` appends the card id to
  `user_progress["bookmarks"]` and always returns `bookmarked: true`.
- `POST /api/view/{card_id}` increments `cards_completed` every time the card
  is observed.
- `GET /api/progress` returns aggregate progress and a bookmark count.
- `GET /api/sessions` and `GET /api/session/{session_id}` read from
  `study_sessions`.
- This data is process memory only. It is reset by backend restarts, has no
  user boundary, and is shared by every browser using the same backend process.

### Contract gaps to resolve before persistence

- The frontend reads `stats.cards_viewed`, while `GET /api/progress` returns
  `cards_completed`.
- The frontend treats `stats.bookmarks` as an array of bookmarkable card
  objects, while the backend returns a bookmark count.
- The frontend online bookmark flow expects toggle behavior, but
  `POST /api/bookmark/{card_id}` only adds the card and never removes it.
- `POST /api/view/{card_id}` can double-count a card because every observed
  intersection sends another view event.

These gaps should be handled before any storage backend is made durable,
otherwise the durable layer will preserve inconsistent behavior.

## Data Inventory

| Data | Current source | Needed for MVP? | Privacy sensitivity |
| --- | --- | --- | --- |
| Bookmark card ids | `bookmarkedCardIds`, `user_progress["bookmarks"]` | Yes | Medium |
| Viewed card ids | `/api/view/{card_id}` aggregate count | Yes | Medium |
| Quiz attempts and correctness | `/api/check-answer` updates aggregate counts | Yes | Medium |
| Study session metadata | `study_sessions` | Yes | Medium |
| Generated card content | `study_sessions[session_id]["cards"]` | Optional | Medium to high |
| Uploaded notes/PDF text | request payloads and generated cards | No by default | High |
| Study streak | `user_progress["study_streak"]` | Optional | Medium |

Learning data can reveal a user's interests, school topics, professional
training, or uploaded private material. The MVP should store the least data
needed to preserve the learning experience.

## Options

### Option 1: Browser-only local storage

Use `localStorage` for anonymous progress and bookmarks, with versioned keys.

Example keys:

- `studyCopilot:v1:bookmarkedCardIds`
- `studyCopilot:v1:viewedCardIds`
- `studyCopilot:v1:quizStats`
- `studyCopilot:v1:sessions`

Benefits:

- Fast to implement.
- Works offline.
- Keeps anonymous learner data on the user's device.
- Avoids introducing accounts before the product needs them.
- Reduces backend persistence and compliance scope.

Tradeoffs:

- No multi-device sync.
- Data can be cleared by the browser.
- Shared devices may expose learning history to another local user.
- Large generated decks can exceed reasonable local storage limits if raw card
  content is stored without caps.

Best fit:

- MVP anonymous mode.
- Offline-first demos.
- Bookmarks, viewed-card ids, and compact session summaries.

### Option 2: Backend durable storage

Store progress and bookmarks in a database or file-backed store behind the API.

Benefits:

- Enables multi-device sync.
- Supports server-side analytics and continuity.
- Creates a clean path for accounts, classroom dashboards, or cohorts.

Tradeoffs:

- Requires user identity or anonymous device identity before records can be
  separated safely.
- Raises retention, deletion, and consent requirements.
- A global anonymous backend store would mix data between users unless scoped.
- Uploaded notes and generated content require extra care because they may be
  sensitive.

Best fit:

- Authenticated users.
- Product analytics after consent.
- Cross-device progress sync.

### Option 3: Hybrid local-first sync

Keep the browser as the source of truth for anonymous progress, then sync a
minimal server record after the user signs in or opts into backup.

Benefits:

- Preserves offline behavior.
- Gives users immediate persistence without accounts.
- Adds sync later without rewriting the whole frontend model.
- Lets the backend store only normalized progress records.

Tradeoffs:

- Requires conflict rules when local and remote records diverge.
- Needs stable card/session identifiers.
- More complex than either browser-only or backend-only storage.

Best fit:

- The long-term product direction.
- Users who start anonymously and later create an account.

## Recommendation

Use a browser-only local storage MVP now, then design the API around a future
hybrid model.

The immediate implementation should:

1. Keep anonymous bookmarks and progress in versioned `localStorage` keys.
2. Store compact ids and counters first, not raw uploaded notes.
3. Track viewed cards by id so `/api/view/{card_id}` is only called once per
   card per session.
4. Treat current backend memory as a demo/runtime cache, not durable storage.
5. Add a "clear local data" control before storing more learner history.
6. Align the frontend/backend progress contract before adding database storage.

Recommended MVP shape:

```json
{
  "version": 1,
  "updatedAt": "2026-06-26T00:00:00.000Z",
  "bookmarkedCardIds": ["card-1", "card-2"],
  "viewedCardIds": ["card-1"],
  "quizStats": {
    "attempted": 3,
    "correct": 2
  },
  "sessions": [
    {
      "sessionId": "session-1",
      "title": "Biology review",
      "createdAt": "2026-06-26T00:00:00.000Z",
      "cardCount": 12,
      "source": "topic"
    }
  ]
}
```

Avoid storing full uploaded notes, PDF text, or generated card bodies in
`localStorage` by default. If session restoration later requires card content,
store only recent sessions, enforce size limits, and provide a clear delete
path.

## Privacy and Sync Guidance

- Make anonymous local persistence explicit in UI copy when the feature ships.
- Provide local data deletion before retaining more than bookmarks and counters.
- Do not send local-only progress to the backend until user identity or consent
  exists.
- Do not persist uploaded source notes by default.
- If backend sync is added, separate records by user id or a scoped anonymous
  device id.
- Add deletion semantics alongside sync, not afterward.
- Use stable ids for cards and sessions before merging local and remote records.

## Future Implementation Checklist

- [ ] Normalize the progress response fields used by frontend and backend.
- [ ] Decide whether `bookmarks` means ids, count, or card summaries.
- [ ] Add real bookmark toggle semantics to the backend or keep toggles fully
      local for anonymous mode.
- [ ] Add a small frontend storage adapter around `localStorage`.
- [ ] Hydrate `bookmarkedCardIds` from the storage adapter on page load.
- [ ] Persist bookmark changes and viewed-card ids after each relevant action.
- [ ] Prevent repeated view events for the same card in one session.
- [ ] Add a manual clear-data action.
- [ ] Add tests for storage parsing, version fallback, and corrupted local data.
- [ ] Revisit backend persistence after user identity is available.

## Proposed Follow-up Issues

1. Implement a frontend local storage adapter for anonymous bookmarks.
2. Align `/api/progress` response fields with the drawer UI.
3. Add bookmark remove/toggle behavior for online mode.
4. Track viewed-card ids to prevent duplicate progress increments.
5. Design authenticated progress sync once user identity is in scope.
