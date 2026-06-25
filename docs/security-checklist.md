# Security Checklist for AI and File Upload Features

This checklist covers Study Copilot features that accept user input, parse
uploaded files, call the AI provider, and render generated study cards.

Use it before merging changes to:

- topic generation
- notes upload
- PDF upload
- AI prompt construction
- generated card rendering
- API key handling
- error messages

## Current Safety Baseline

The current backend already includes several useful guardrails:

- `GOOGLE_API_KEY` is read from the environment instead of being hard-coded.
- The app falls back to offline sandbox mode when the AI provider is unavailable.
- Notes input is capped by `MAX_NOTES_CHARS`.
- PDF uploads are capped by `MAX_PDF_BYTES`.
- PDF uploads are checked for a `.pdf` filename suffix.
- PDF text extraction is wrapped in `HTTPException` handling.

These are good starting points, but the project still needs a consistent
pre-merge security review path for AI and upload changes.

## API Keys and Secrets

Required checks:

- [ ] No API keys, provider tokens, service credentials, or personal secrets are
      committed to the repository.
- [ ] New configuration values are loaded from environment variables or a local
      `.env` file that is ignored by git.
- [ ] Setup docs explain required secret names without including real values.
- [ ] Error responses and logs do not print API keys or provider request bodies.
- [ ] Client-side code never receives `GOOGLE_API_KEY` or any other backend
      secret.

Recommended practice:

- Keep provider initialization in backend code only.
- Add a short masked log if provider setup fails, not the full exception with
  sensitive request context.
- Document how to rotate a leaked key if a development key is accidentally
  exposed.

## File Uploads

Required checks for PDF uploads:

- [ ] Enforce a maximum upload size before or during file parsing.
- [ ] Reject missing filenames.
- [ ] Reject non-PDF uploads.
- [ ] Treat extension checks as a first pass only; do not assume suffix checks
      prove file safety.
- [ ] Limit extracted text before passing it to the AI provider.
- [ ] Do not store raw PDF bytes unless a feature explicitly requires it.
- [ ] Do not echo extracted PDF text in error messages.
- [ ] Return user-safe errors for malformed, encrypted, unreadable, or empty
      PDFs.

Recommended follow-ups:

- Inspect content type or file signature in addition to filename suffix.
- Add timeout handling for PDF parsing.
- Add tests for oversized PDF, wrong extension, empty PDF, and unreadable PDF.
- Consider rejecting PDFs with no extractable text before calling the AI model.

## Notes Input

Required checks:

- [ ] Enforce minimum and maximum note lengths on the backend.
- [ ] Do not store raw notes by default.
- [ ] Do not include raw notes in logs.
- [ ] Do not include raw notes in error responses.
- [ ] Trim or normalize input before sending it to the AI provider.
- [ ] Avoid assuming notes content is trustworthy just because it came from the
      user.

Recommended follow-ups:

- Add a clear retention policy before persisting notes.
- Add tests for too-short notes, too-long notes, and whitespace-only notes.
- Keep generated cards separate from original uploaded source text.

## Prompt Injection and AI Output

Prompt injection risks apply to topic text, pasted notes, PDF text, and any
future imported content.

Required checks:

- [ ] Prompts tell the model to ignore instructions in uploaded learning
      material that attempt to change system behavior.
- [ ] Prompts ask for structured output that matches the frontend card schema.
- [ ] Backend code validates model output before returning it to the frontend.
- [ ] Backend code has a fallback path when model output is missing, malformed,
      or too long.
- [ ] AI output is treated as untrusted user-facing content.
- [ ] AI output is not allowed to request secrets, credentials, or hidden
      application state from users.

Recommended output validation:

- Each card has `id`, `type`, `title`, `content`, and `timestamp`.
- Card `type` is one of the known frontend-rendered types.
- Quiz cards have options and exactly one correct option.
- Long text fields are capped before rendering.
- Unknown fields are ignored rather than blindly rendered.

## Frontend Rendering

Generated card content and titles are inserted into the DOM by the frontend.
Any field that can come from an AI response, uploaded file, or notes input
should be treated as untrusted.

Required checks:

- [ ] Do not render untrusted text with `innerHTML` unless it has been sanitized
      or strictly templated.
- [ ] Prefer `textContent` for card titles, explanations, notes, and PDF-derived
      text.
- [ ] Do not allow generated content to inject event handlers, scripts, iframes,
      or external tracking pixels.
- [ ] Keep SVG/button markup separate from untrusted user or AI text.
- [ ] Toast messages should use trusted static strings or escaped content.

Recommended follow-ups:

- Add a small escaping helper for AI-generated text.
- Add a rendering test with HTML-like content in card titles and explanations.
- Review each `innerHTML` use and classify it as trusted template or untrusted
  content insertion.

## API Error Messages

Required checks:

- [ ] Errors are specific enough for the user to recover.
- [ ] Errors do not expose stack traces.
- [ ] Errors do not expose provider internals, API keys, prompts, notes, or PDF
      text.
- [ ] Validation errors identify the field when possible.
- [ ] Upload and AI errors use stable error codes that the frontend can map to
      friendly messages later.

Examples:

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

```json
{
  "success": false,
  "error": {
    "code": "ai_generation_failed",
    "message": "Could not generate study cards. Please try again."
  }
}
```

## CORS and Local Development

The backend currently allows all origins. This is convenient for local static
frontend development, but production deployments should narrow it.

Required checks before production hosting:

- [ ] Replace wildcard CORS origins with configured allowed origins.
- [ ] Keep local development origins separate from production origins.
- [ ] Do not allow credentials with broad wildcard production origins.
- [ ] Document which frontend URL is expected to call the backend.

## Data Retention and Privacy

Required checks:

- [ ] Do not persist uploaded PDFs, raw notes, or extracted text unless the
      feature explicitly requires it.
- [ ] If persistence is added, document retention and deletion behavior.
- [ ] Keep generated cards and original source text separate.
- [ ] Avoid logging study topics, notes, or extracted PDF text in shared logs.
- [ ] Treat bookmarks, progress, and quiz results as learning history.

Recommended follow-ups:

- Add a local data clearing control before expanding browser persistence.
- Add a backend deletion endpoint before introducing authenticated storage.
- Document whether AI provider requests may include uploaded user content.

## Pre-PR Checklist

Use this before opening a PR that touches AI, notes, PDF, or rendering flows:

- [ ] No secrets are added to code, docs, examples, screenshots, or test files.
- [ ] New inputs have backend validation limits.
- [ ] Upload code rejects unsupported file types.
- [ ] AI prompts do not trust uploaded content as instructions.
- [ ] AI output is validated before the frontend renders it.
- [ ] Untrusted text is escaped or rendered with `textContent`.
- [ ] Error messages are user-safe and do not leak internals.
- [ ] Logs avoid raw notes, extracted PDF text, prompts, and provider responses.
- [ ] Tests or manual validation cover the new failure path.
- [ ] README or setup docs are updated if configuration changed.

## Suggested Test Cases

- Upload a non-PDF file with a `.txt` extension.
- Upload an oversized PDF.
- Upload an empty or image-only PDF.
- Paste notes below the minimum length.
- Paste notes above the maximum length.
- Use a topic containing HTML tags.
- Use notes containing prompt-injection text.
- Return a malformed AI card response and verify fallback behavior.
- Render card content containing `<script>` as text, not executable markup.
- Run the app without `GOOGLE_API_KEY` and verify sandbox fallback behavior.

## Open Follow-ups

- Add a normalized API error schema for upload and AI failures.
- Add server-side validation for generated card schema.
- Add escaping or sanitized rendering for AI-generated card fields.
- Add content-type or file-signature checks for PDF uploads.
- Replace broad production CORS settings with configured allowed origins.
