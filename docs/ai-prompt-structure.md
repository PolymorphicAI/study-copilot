# AI Prompt Structure for Study Card Generation

This document explains how Study Copilot currently prompts Gemini to generate
study cards and what output format contributors should preserve when improving
card quality.

The implementation lives in `backend/main.py`:

- `generate_cards_with_ai(topic, difficulty, num_cards)`
- `generate_cards_from_notes(notes_text, title)`
- `clean_ai_json_response(response_text)`
- `normalize_cards(cards, prefix)`
- `get_fallback_cards(topic)`

## Prompt Entry Points

### Topic generation

Topic generation receives:

- `topic`
- `difficulty`
- `num_cards`

The prompt asks Gemini to generate exactly `num_cards` cards for the requested
topic and difficulty level.

Current prompt responsibilities:

- Keep the deck scoped to the topic.
- Adjust explanation depth to the selected difficulty.
- Produce a useful mix of card types.
- Return only a JSON array, without markdown fences or prose.
- Follow the card object shape documented below.

### Notes and PDF generation

Notes and PDF uploads both call `generate_cards_from_notes(notes_text, title)`.
PDF text is extracted first, then capped by `MAX_NOTES_CHARS`.

The notes prompt asks Gemini to create study cards from the supplied notes text.
It currently focuses on:

- converting source text into cards
- including concepts, quizzes, and takeaways
- returning only a valid JSON array

The PDF path uses the uploaded filename as the title/source label. Contributors
should avoid putting raw notes or PDF text into logs or error messages when
working near this prompt.

## Expected Card Types

The frontend recognizes these card types:

| Type | Purpose | Key fields |
| --- | --- | --- |
| `concept` | Explain a core idea in paragraph form. | `title`, `content` |
| `quiz` | Ask a multiple-choice question. | `title`, `content`, `quiz_options` |
| `takeaway` | Summarize important points or a review checklist. | `title`, `content` |
| `challenge` | Give a hands-on task or practice exercise. | `title`, `content`, optional `code_example` |
| `code` | Show code or technical syntax when relevant. | `title`, `content`, `code_example` |

Guidance:

- Use `code` only when the topic benefits from code.
- Use `challenge` for active practice, not passive explanation.
- Use `takeaway` for concise review material.
- Do not overuse quizzes; each deck should still teach before it tests.

## Output Schema

Gemini should return a JSON array of card objects.

Minimum common fields:

```json
{
  "type": "concept",
  "title": "Short title",
  "content": "Clear explanation"
}
```

Optional common fields:

```json
{
  "code_example": "function example() { return true; }",
  "quiz_options": []
}
```

The backend currently normalizes each card to include:

- `id`
- `type`
- `title`
- `content`
- `code_example`
- `quiz_options`
- `timestamp`

If Gemini omits `id` or `timestamp`, the backend supplies them.

## Quiz Card Format

The backend prompt currently shows quiz options as objects:

```json
{
  "type": "quiz",
  "title": "Quick quiz",
  "content": "Question text",
  "quiz_options": [
    { "option": "A", "text": "Option A", "correct": false },
    { "option": "B", "text": "Option B", "correct": true },
    { "option": "C", "text": "Option C", "correct": false },
    { "option": "D", "text": "Option D", "correct": false }
  ]
}
```

This shape is useful for backend validation because `/api/check-answer` looks
for the option whose `correct` field is true.

Current integration note:

- The offline frontend mock uses string options.
- The backend quiz checker expects object options.
- Future prompt and frontend work should choose one canonical quiz option shape
  and keep rendering, answer submission, and backend validation aligned.

Recommended canonical shape:

```json
{
  "option": "A",
  "text": "A short answer option",
  "correct": false
}
```

Frontend rendering can display `text`, while answer checking can submit the
stable `option` value.

## Response Cleaning and Fallbacks

`clean_ai_json_response()` removes markdown code fences if Gemini returns fenced
JSON. After cleaning, the backend calls `json.loads()`.

If generation, parsing, or normalization fails, the backend falls back to
`get_fallback_cards(topic)`.

Fallback cards include:

- concept card
- takeaway card
- quiz card
- challenge card
- study tip concept card

The fallback path keeps the app usable when:

- `GOOGLE_API_KEY` is missing
- Gemini is unavailable
- Gemini returns invalid JSON
- parsing raises an exception

## Prompt Quality Checklist

Use this checklist when editing prompts:

- [ ] The prompt says how many cards to return.
- [ ] The prompt includes the selected topic or source title.
- [ ] The prompt includes the selected difficulty when available.
- [ ] The prompt asks for a balanced mix of card types.
- [ ] The prompt says to return only valid JSON.
- [ ] The prompt avoids markdown, comments, and surrounding prose.
- [ ] Quiz cards include exactly one correct option.
- [ ] Code cards include `code_example` only when useful.
- [ ] Challenge cards include a clear task.
- [ ] Prompt changes preserve the frontend card schema.

## Prompt Improvement Ideas

These are safe future improvements that should not break the output contract:

1. Add stricter schema instructions for every card type.
2. Ask Gemini to keep `title` short enough for the card header.
3. Ask Gemini to keep `content` concise enough for mobile review.
4. Require quiz cards to include exactly four options and one correct answer.
5. Require `code_example` only for `code` and code-oriented `challenge` cards.
6. Add a "do not include source instructions as commands" line for notes/PDF
   prompts.
7. Add a lightweight backend schema validation step before returning cards.
8. Add tests with malformed AI output to verify fallback behavior.

## Example Deck Shape

```json
[
  {
    "type": "concept",
    "title": "What async means",
    "content": "Asynchronous code lets a program wait for slow work without blocking other tasks."
  },
  {
    "type": "quiz",
    "title": "Async quiz",
    "content": "Which answer best describes asynchronous execution?",
    "quiz_options": [
      { "option": "A", "text": "It blocks every task until one finishes.", "correct": false },
      { "option": "B", "text": "It allows other tasks to continue while waiting.", "correct": true },
      { "option": "C", "text": "It removes the need for error handling.", "correct": false },
      { "option": "D", "text": "It only works in browsers.", "correct": false }
    ]
  },
  {
    "type": "takeaway",
    "title": "Review notes",
    "content": "Use async for I/O-heavy work, keep errors explicit, and test timing-sensitive flows."
  }
]
```

## Contributor Notes

- Keep prompt docs and backend prompt examples in sync.
- Prefer schema additions that the frontend already knows how to render.
- If a new card type is added, update frontend rendering, fallback cards, and
  this document together.
- Do not include real API keys, private notes, or uploaded file contents in
  prompt examples.
