# AI Error Message Policy

Study Copilot should keep learning flows usable when AI generation is unavailable while avoiding technical or sensitive details in user-facing responses.

## Current User-Facing Behavior

- The backend starts in offline sandbox mode when no AI provider is configured or provider setup fails.
- Topic, notes, and PDF study-card generation return offline fallback cards when live AI generation cannot be used.
- Fallback cards explain that live AI generation is temporarily unavailable and that offline practice cards are being shown instead.
- Responses do not expose API keys, environment variable values, provider stack traces, raw model errors, or internal exception text.

## Safe Message Pattern

Use concise messages that tell the learner what happened and what they can do next:

> AI generation is temporarily unavailable, so Study Copilot is showing offline practice cards instead. You can keep studying now and try live AI generation again later.

This wording is intentionally provider-neutral. It avoids naming secrets, configuration keys, internal model IDs, request payloads, or exception details.

## Implementation Notes

- Keep provider setup and generation exceptions out of API response bodies.
- Prefer stable fallback content over passing raw exception messages to the frontend.
- If structured error metadata is added later, use stable reason codes such as `ai_generation_unavailable` instead of raw exception strings.
- Backend logs may include operational details for maintainers, but logs should still avoid API key values and full prompt payloads.

## Review Checklist

- Does the message help the user continue or retry?
- Does it avoid stack traces, raw exception text, and secret names or values?
- Does it avoid exposing full prompts, notes, uploaded document text, or generated provider responses?
- Does offline fallback still work without a real AI API key?
