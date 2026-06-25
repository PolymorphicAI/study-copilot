# PDF Upload Validation Plan

This plan defines the validation rules Study Copilot should apply to PDF uploads before parsing them into study cards. The current backend already rejects non-`.pdf` filenames, limits PDF payloads to 10 MB, and returns clear errors when PyPDF2 cannot read a file or extracts no text.

## Goals

- Keep PDF uploads predictable for learners.
- Protect backend memory, CPU, and AI generation limits.
- Avoid leaking parser internals or uploaded document content through error messages.
- Make future PDF handling changes easy to test.

## Accepted File Rules

- Accept files only when the submitted filename ends with `.pdf`, case-insensitively.
- Require a non-empty filename so anonymous multipart fields are rejected.
- Treat filename checks as a first-pass guard, not a full security boundary.
- In a follow-up implementation, inspect the file signature and reject content that does not start with the PDF header `%PDF-`.
- Keep generated study cards and API responses free of the original binary content.

## Size Limits

- Keep the current maximum upload size at `MAX_PDF_BYTES` (`10 * 1024 * 1024`, or 10 MB).
- Return HTTP 413 when the raw file content exceeds that size.
- Truncate extracted text to `MAX_NOTES_CHARS` before card generation so AI requests stay bounded.
- Consider adding a lower configurable limit for hosted deployments with small memory budgets.
- Document any deployment-specific limit in environment or hosting notes if it differs from the default.

## Invalid PDF Handling

- Return HTTP 400 when the parser cannot read the PDF.
- Return HTTP 400 when extraction succeeds but no readable text is found.
- Keep parser exception details out of public API responses in a future hardening pass; use stable messages such as `Could not read PDF.` and log details separately.
- Avoid sending unreadable, encrypted, or image-only PDF content to AI generation.
- Show frontend copy that suggests trying a text-based PDF or using the notes upload path.

## Security And Performance Notes

- Parse uploaded PDFs from memory only after enforcing the raw byte size limit.
- Never store uploaded PDFs unless a future privacy-reviewed storage design is added.
- Avoid logging full extracted text, raw bytes, filenames that may contain sensitive data, or generated prompts.
- Add rate limiting before exposing upload-heavy endpoints publicly.
- Consider malware scanning only if uploaded files are stored or shared with other users.
- Revisit parser choice if PyPDF2 fails common learner documents or shows security advisories.

## Backend Test Plan

Add focused tests for:

- Missing multipart file returns a validation error.
- Non-PDF filename returns HTTP 400.
- Oversized content returns HTTP 413.
- Invalid PDF bytes return HTTP 400.
- Empty or image-only PDFs return HTTP 400 when no text is extracted.
- Valid text PDF calls card generation without requiring a real AI API key.

These tests should force offline mode or mock card generation so they do not require `GOOGLE_API_KEY`.

## Future Implementation Checklist

- Add a PDF magic-header check before invoking PyPDF2.
- Replace raw parser exception text in API responses with a stable user-safe error.
- Add PDF upload error tests under the backend test suite.
- Add frontend messaging for invalid, unreadable, oversized, and image-only PDFs.
- Add deployment notes for upload size limits and privacy expectations.
