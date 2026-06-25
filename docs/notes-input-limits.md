# Notes Analyzer Input Limits

This document describes the current input limits for the Study Copilot notes analyzer flow and the expected behavior when pasted notes are too short, too long, or difficult for the model to process.

The relevant backend implementation lives in `backend/main.py`.

## Current Limits

| Input | Current limit | Source |
| --- | --- | --- |
| Notes body | Minimum 10 characters | `UploadNotesRequest.text_content` |
| Notes body | Maximum 15,000 characters | `MAX_NOTES_CHARS` |
| Notes title | Minimum 2 characters | `UploadNotesRequest.title` |
| Notes title | Maximum 200 characters | `UploadNotesRequest.title` |
| PDF-derived text | Truncated to 15,000 characters | `extract_pdf_text()` |

The notes endpoint is:

```text
POST /api/upload-notes
```

The frontend calls it with a JSON body like:

```json
{
  "text_content": "Pasted study notes or article text...",
  "title": "Paste Notes"
}
```

## Recommended Contributor Guidance

For best card quality, pasted notes should usually be:

- At least one short paragraph.
- Focused on one lesson topic.
- Under the 15,000 character backend limit.
- Free of unrelated boilerplate, navigation text, or copied page chrome.
- Split into multiple submissions when the content covers several unrelated topics.

Very long notes can reduce response quality because the model has less room to reason, summarize, and produce well-structured cards.

## Current Behavior

### Empty Notes

The frontend blocks empty pasted notes before calling the backend and shows a validation toast.

### Too Short

The backend requires `text_content` to be at least 10 characters. If a request is shorter than that, FastAPI/Pydantic validation rejects it with a `422` response.

Current frontend behavior does not pre-check the 10 character minimum; it only checks whether the notes field is empty.

### Too Long

The backend request model rejects `text_content` longer than `MAX_NOTES_CHARS`, currently 15,000 characters, with a `422` validation response.

The notes generation helper also slices text to `MAX_NOTES_CHARS` before building the model prompt:

```python
notes_text = notes_text[:MAX_NOTES_CHARS]
```

For PDF uploads, extracted PDF text is similarly truncated to 15,000 characters before card generation.

### Model or API Failure

If Gemini is unavailable, offline mode is active, or generation fails, the backend returns fallback cards for the provided title instead of failing the entire notes flow.

## Security and Privacy Notes

Contributors should avoid pasting sensitive notes during demos or tests.

Do not include:

- API keys
- Passwords
- Wallet seed phrases
- Private classroom records
- Personally identifiable student data
- Proprietary article text that should not be sent to an AI provider

The app should treat pasted notes as user-provided content that may be sent to the configured model provider when live AI mode is available.

## Future Improvement Ideas

- Add frontend validation for the 10 character minimum.
- Add a visible character counter for the 15,000 character limit.
- Warn users before truncating long PDF-derived text.
- Show clearer error messages for `422` validation responses.
- Suggest splitting long notes into multiple lessons.
- Add a token-estimate helper if the backend later supports model-specific context windows.
- Document whether future deployments store notes, discard them, or keep only generated cards.

## Pre-PR Checklist

Before changing notes analyzer input behavior:

- [ ] Update this document if `MAX_NOTES_CHARS` changes.
- [ ] Keep frontend validation aligned with backend request validation.
- [ ] Verify short notes, long notes, and empty notes behavior.
- [ ] Avoid logging raw pasted notes in production paths.
- [ ] Preserve offline fallback behavior for demos without a model key.

