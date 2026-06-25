# AI Output Validation and Fallbacks

This document describes how Study Copilot currently handles AI-generated card
output, what can go wrong with malformed responses, and how contributors should
improve validation without breaking the offline fallback experience.

## Current Flow

AI card generation happens in `backend/main.py`.

Topic input:

1. `generate_cards()` receives `GenerateCardsRequest`.
2. `generate_cards_with_ai(topic, difficulty, num_cards)` builds the prompt.
3. Gemini returns text.
4. `clean_ai_json_response(response.text)` removes markdown fences if present.
5. `json.loads(...)` parses the cleaned text.
6. `normalize_cards(cards, topic)` fills missing common fields.
7. The endpoint returns cards and `offline_mode`.

Notes and PDF input:

1. `upload_notes()` or `upload_pdf()` receives user content.
2. PDF text is extracted and capped by `MAX_NOTES_CHARS`.
3. `generate_cards_from_notes(notes_text, title)` builds the prompt.
4. The same clean, parse, normalize, and fallback path is used.

## Current Validation

The backend currently validates input requests with Pydantic models and file
checks, then performs light validation on AI output.

Input validation includes:

- `topic` length.
- `difficulty` enum.
- `num_cards` range.
- notes text minimum and maximum length.
- PDF file extension.
- PDF byte size.
- extracted PDF text presence.

AI output handling includes:

- removing JSON code fences when present
- parsing with `json.loads`
- filling missing card fields in `normalize_cards`
- falling back to generated local cards on any exception

Current output normalization fills:

- `id`
- `type`
- `title`
- `content`
- `code_example`
- `quiz_options`
- `timestamp`

## Expected Card Shape

Each card should be an object with at least:

```json
{
  "type": "concept",
  "title": "Short title",
  "content": "Clear explanation"
}
```

Known card types:

- `concept`
- `quiz`
- `takeaway`
- `challenge`
- `code`

Quiz cards should include a `quiz_options` list. The prompt currently shows
options as objects:

```json
{
  "option": "A",
  "text": "Option text",
  "correct": false
}
```

For reliable backend validation, each quiz should have exactly one option where
`correct` is true.

## Malformed Output Risks

AI responses can fail in several ways:

| Risk | Example | Current behavior |
| --- | --- | --- |
| Markdown wrapper | ```json around the array | `clean_ai_json_response` strips common fences. |
| Extra prose | "Here are your cards: [...]" | `json.loads` fails, fallback cards are returned. |
| Invalid JSON | trailing commas, comments, single quotes | `json.loads` fails, fallback cards are returned. |
| Wrong root type | object instead of array | May normalize incorrectly or fail later. |
| Missing fields | no title or content | `normalize_cards` fills defaults. |
| Unknown card type | `flashcard` | Type passes through and frontend may render unexpectedly. |
| Bad quiz options | strings, no correct option, many correct options | Backend quiz validation may fail or frontend/backend may disagree. |
| Oversized text | very long content or code blocks | Frontend layout can become hard to scan. |
| Unsafe HTML | generated tags or event handlers | Frontend should treat AI text as untrusted. |

The current fallback behavior keeps the app usable, but it does not tell the
caller why the fallback happened.

## Fallback Behavior

The backend returns `get_fallback_cards(...)` when:

- the app is in offline mode
- no model is configured
- Gemini generation raises an exception
- response cleaning or JSON parsing fails
- normalization raises an exception

Fallback cards include:

- introduction concept card
- key takeaways card
- quick quiz card
- practice challenge card
- study tip concept card

Fallback cards are intentionally deterministic enough for demos and reviewer
flows, while still being generated around the requested topic/title.

## Validation Strategy

Future validation should be explicit and layered.

### 1. Parse validation

Require the cleaned AI response to be a JSON array.

Suggested checks:

- root value is a list
- list is not empty
- list length is within expected range

### 2. Card-level validation

Validate each card before normalization returns it.

Suggested checks:

- `type` is one of the supported card types
- `title` is a non-empty string
- `content` is a non-empty string
- `code_example` is present only when useful for `code` or `challenge`
- text fields have practical maximum lengths

### 3. Quiz validation

Quiz cards need stricter validation because the backend checks answers later.

Suggested checks:

- `quiz_options` is a list
- exactly four options are present
- each option has `option`, `text`, and `correct`
- exactly one option has `correct: true`
- option labels are stable, such as `A`, `B`, `C`, `D`

### 4. Sanitization boundary

AI output should be treated as untrusted text.

Suggested checks:

- avoid rendering generated text with raw `innerHTML`
- escape or sanitize title, content, and explanation fields
- keep trusted UI templates separate from AI-generated text

## Recommended Error Handling Improvements

Current generation functions catch all exceptions and return fallback cards. That
is good for demo resilience but makes debugging hard.

Recommended improvements:

1. Log a safe internal reason code when fallback is used.
2. Return a response field such as `fallback_used: true`.
3. Return a safe `fallback_reason` enum, such as:
   - `offline_mode`
   - `model_unavailable`
   - `invalid_json`
   - `invalid_schema`
   - `generation_error`
4. Avoid logging raw notes, PDF text, prompts, or full provider responses.
5. Add tests that feed malformed AI output into the parser/validator.

Example future response:

```json
{
  "success": true,
  "session_id": "session_123",
  "cards": [],
  "total_cards": 5,
  "offline_mode": false,
  "fallback_used": true,
  "fallback_reason": "invalid_json"
}
```

## Test Cases to Add

Backend tests should cover:

- valid JSON array with all supported card types
- fenced JSON array
- prose before JSON
- invalid JSON
- object root instead of array root
- empty array
- card with missing title
- card with unknown type
- quiz with no correct option
- quiz with two correct options
- oversized content field
- provider exception fallback

Manual checks should confirm:

- fallback cards still render when `GOOGLE_API_KEY` is missing
- topic generation remains usable in offline mode
- notes and PDF flows do not expose raw source text in errors

## Contributor Checklist

Use this checklist before changing AI generation behavior:

- [ ] Prompt output expectations are still valid JSON.
- [ ] Backend parsing rejects non-array roots.
- [ ] Unknown card types are rejected or mapped safely.
- [ ] Quiz option schema is consistent with frontend rendering.
- [ ] Fallback cards still render in offline mode.
- [ ] Safe fallback reason logging avoids secrets and raw user content.
- [ ] Tests cover malformed model output.
- [ ] Frontend rendering treats AI text as untrusted.

## Open Questions

- Should invalid cards be dropped individually, or should the entire deck fall
  back?
- Should fallback reasons be returned to the frontend or only logged?
- Should the backend enforce exact `num_cards` after validation?
- Should the frontend support both string and object quiz options during a
  migration period?
- Should generated card text have type-specific maximum lengths?
