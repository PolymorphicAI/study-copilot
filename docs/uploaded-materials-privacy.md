# Uploaded Study Materials Privacy Notes

Study Copilot turns pasted notes and uploaded PDFs into study cards. Those inputs can contain private academic, professional, or personal information, so the product should treat uploaded study materials as sensitive by default.

## Sensitive Data Risks

Uploaded PDFs and pasted notes may include:

- Student names, emails, IDs, grades, feedback, accommodations, or advising notes.
- Class rosters, group project details, unpublished research, or exam preparation material.
- Workplace documents, meeting notes, customer details, internal processes, or credentials copied into notes by mistake.
- Health, financial, immigration, legal, or other regulated personal data.
- Copyrighted course packs, textbooks, slides, or articles with usage restrictions.
- Prompt-injection text intended to manipulate AI output or reveal system behavior.

The backend should not assume that study material is low-risk just because it is used for learning.

## Current Data Flow

The current backend reads uploaded PDFs in memory, extracts text with PyPDF2, truncates extracted content to `MAX_NOTES_CHARS`, and generates study cards from the extracted text. Pasted notes use the same card-generation path after Pydantic validates length limits.

Study sessions are currently kept in process memory through `study_sessions`. This is useful for the sandbox implementation, but it should not be treated as durable or privacy-reviewed storage.

## Storage Guidance

Do not store these by default:

- Raw uploaded PDF bytes.
- Full pasted notes or full extracted PDF text.
- Full AI prompts that contain user material.
- Full provider responses if they include copied user material.
- Filenames, document titles, or metadata that identify a learner, school, employer, client, or patient.

Allowed short-lived data:

- Generated study cards for the current session.
- Minimal session metadata needed to render the current learning flow.
- Aggregate counters such as cards viewed, quiz attempts, and bookmarks when they do not include source material.

If persistent storage is added later, it should require an explicit product decision, a visible user notice, and a deletion path.

## Retention And Deletion Recommendations

- Default to session-only retention for uploaded materials and extracted text.
- Delete raw file bytes immediately after text extraction.
- Delete extracted text after cards are generated unless the user explicitly saves the source material.
- Add a "delete session" flow before introducing accounts or durable backend storage.
- If saved materials become a feature, document retention duration, export behavior, and deletion guarantees.
- Keep server logs free of raw notes, extracted PDF text, prompts, and filenames.

## User-Facing Privacy Notes

Use short, plain-language copy near upload and notes entry points:

> Upload only study materials you are allowed to use. Avoid personal, confidential, or regulated information. Study Copilot uses your content to generate cards for this session.

For a future saved-materials feature:

> Saved materials stay available until you delete them. You can remove generated cards and source material from your account at any time.

For offline sandbox mode:

> Offline sandbox mode can show sample cards without sending your notes to an AI provider.

## AI Provider Considerations

- Make it clear when uploaded or pasted content may be sent to an AI provider.
- Avoid sending raw content when offline fallback cards are enough.
- Avoid including hidden metadata, credentials, or unrelated file contents in prompts.
- Prefer minimal prompts that include only the study material needed for the current generation request.
- Consider adding a privacy mode that disables provider calls and uses local fallback content only.

## Implementation Checklist

- Add frontend privacy notes near PDF upload and pasted notes controls.
- Add backend tests that confirm invalid PDF errors do not echo raw file content.
- Add logging guidance that excludes notes, PDF text, prompts, filenames, and provider responses.
- Add a deletion path before persistent study-session storage.
- Revisit this document when accounts, saved sessions, or Stellar wallet identity features are introduced.
