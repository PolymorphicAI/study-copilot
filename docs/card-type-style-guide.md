# Card Type Style Guide

Study Copilot lessons are built from reusable card types. This guide documents the visual and content conventions for the current `concept`, `code`, `quiz`, `takeaway`, and `challenge` cards in `study-copilot-full.html`.

Use this guide when updating card generation, offline sandbox cards, backend responses, or UI rendering.

## Shared Card Structure

Every study card should include:

- `id`: stable card identifier.
- `type`: one of the supported card types.
- `title`: short title shown in the card header.
- `content`: primary learning text shown in the card body.
- `timestamp`: ISO timestamp used for card metadata.

Optional fields:

- `code_example`: used by `code` and `challenge` cards.
- `quiz_options`: used by `quiz` cards.
- `quiz_answer` or local fallback answer data: used to validate quiz cards.
- `quiz_explanation` or local fallback explanation data: used after quiz submission.

All cards render inside `.learning-card` and receive a `data-type` attribute so type-specific border accents can be applied.

## Visual Conventions

Current card accents:

| Type | Border accent | Primary purpose |
| --- | --- | --- |
| `concept` | `var(--primary)` | Explain the main idea. |
| `code` | `var(--accent)` | Show runnable or illustrative syntax. |
| `quiz` | `var(--secondary)` | Check understanding with answer options. |
| `takeaway` | `#e2e8f0` | Summarize the most important points. |
| `challenge` | `#ec4899` | Ask the learner to apply the lesson. |

Shared visual rules:

- Keep titles concise enough to scan in the vertical card layout.
- Use `white-space: pre-wrap` friendly content so line breaks stay readable.
- Avoid long single-line text that can overflow the card on mobile.
- Keep type-specific icons decorative and do not rely on icons alone to communicate card type.
- Keep contrast high for card body text, quiz feedback, and code examples.

## Concept Cards

Use concept cards to introduce or explain the core idea for the lesson topic.

Content guidelines:

- Start with the main idea in plain language.
- Keep paragraphs short.
- Connect the concept to what the learner will do next.
- Avoid quiz questions or tasks in concept cards.

Example:

```json
{
  "type": "concept",
  "title": "Understanding: Stellar basics",
  "content": "Stellar is a network for fast asset movement. Focus first on accounts, assets, trustlines, and transactions before studying advanced wallet or contract flows."
}
```

## Code Cards

Use code cards to show syntax, configuration, or implementation patterns.

Content guidelines:

- Explain why the code matters before the snippet.
- Keep snippets short enough to fit in the card.
- Prefer realistic variable names.
- Include comments only when they clarify the learning point.
- Use `code_example` for the snippet so the copy button works.

Example:

```json
{
  "type": "code",
  "title": "Functional Implementation: API setup",
  "content": "Read the setup function and notice where configuration is passed into the module.",
  "code_example": "function initializeModule(config) {\\n  return config.env === 'staging';\\n}"
}
```

## Quiz Cards

Use quiz cards to check comprehension after a concept or code example.

Content guidelines:

- Ask one clear question.
- Provide 3-4 answer options.
- Make incorrect answers plausible but not misleading.
- Include an explanation that teaches after submission.
- Keep options similar in length when possible.

Example:

```json
{
  "type": "quiz",
  "title": "Module Validation Test",
  "content": "What is the main benefit of breaking a system into modules?",
  "quiz_options": [
    "It removes the need for testing.",
    "It makes behavior easier to isolate and reason about.",
    "It guarantees faster network calls.",
    "It automatically writes documentation."
  ],
  "quiz_answer": "It makes behavior easier to isolate and reason about.",
  "quiz_explanation": "Modules help developers reason about smaller pieces of behavior and test them independently."
}
```

UI notes:

- Quiz option buttons become disabled after an answer.
- Correct and incorrect states should include both color and visible feedback icons.
- Correct answers auto-advance after feedback is shown.
- Incorrect answers should keep the explanation visible so learners can review it.

## Takeaway Cards

Use takeaway cards to summarize the lesson into memorable points.

Content guidelines:

- Use short numbered or bulleted points.
- Restate the most practical ideas.
- Avoid introducing a new topic that was not covered earlier.
- Keep the card useful as a quick review artifact.

Example:

```json
{
  "type": "takeaway",
  "title": "Key takeaways: API setup",
  "content": "1. Keep configuration explicit.\\n2. Validate assumptions before calling external services.\\n3. Test both success and failure paths."
}
```

## Challenge Cards

Use challenge cards to ask the learner to apply what they just studied.

Content guidelines:

- Start with a concrete task.
- Keep the expected action clear.
- Include starter code when the task is code-related.
- Make the task achievable without leaving the lesson.

Example:

```json
{
  "type": "challenge",
  "title": "Hands-on Code Challenge",
  "content": "Task: Refactor this block so it reports the current configuration status.",
  "code_example": "const result = await initializeModule({ env: 'staging' });\\nif (result) {\\n  // Print configuration status message\\n}"
}
```

## Ordering Guidance

A balanced lesson should usually move from explanation to practice:

1. `concept`
2. `code`
3. `quiz`
4. `takeaway`
5. `challenge`

Generated lessons can repeat or omit types, but the learner should not see a challenge before enough context has been introduced.

## Pre-PR Checklist

Before changing card generation or card rendering:

- [ ] All new card data includes `id`, `type`, `title`, `content`, and `timestamp`.
- [ ] New card types are documented before being generated.
- [ ] Code and challenge cards use `code_example` when a snippet is shown.
- [ ] Quiz cards include options, a correct answer, and an explanation path.
- [ ] Card text stays readable on mobile widths.
- [ ] Type-specific styling does not rely on color alone.
- [ ] Offline sandbox cards and backend-generated cards follow the same conventions.

