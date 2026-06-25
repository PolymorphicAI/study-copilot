# Learning Credential Data Model

This document defines a proposed data model for Study Copilot achievements,
badges, and learning credentials.

The model is designed to support the current app first, while leaving room for
future Stellar wallet identity, Soroban credential records, portable progress,
and proof-of-study flows described in the project roadmap.

## Design Goals

- Represent meaningful study achievements without storing sensitive source
  material by default.
- Support lightweight frontend badges and backend records.
- Keep evidence separate from display metadata.
- Allow future verification through hashes, signatures, or Soroban records.
- Avoid putting raw notes, PDF text, or private study content on-chain.

## Current App Signals

Study Copilot already has several signals that can later become credential
evidence:

- Generated study sessions in `study_sessions`.
- Study cards with ids, titles, types, content, and timestamps.
- Quiz attempts and correctness counts in `user_progress`.
- Card view events from `/api/view/{card_id}`.
- Bookmarks from `/api/bookmark/{card_id}`.
- Study streak and aggregate progress from `/api/progress`.

These signals are currently in process memory. Credentials should not be treated
as durable or verifiable until storage, identity, and consent are implemented.

## Core Entities

### Learner Identity

Represents the learner who owns or claims a credential.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `learner_id` | string | Yes | Internal stable id. Can start as an anonymous local id. |
| `display_name` | string | No | Optional learner-facing name. |
| `wallet_public_key` | string | No | Future Stellar account public key. |
| `identity_provider` | string | No | `anonymous`, `wallet`, `email`, or future auth provider. |
| `created_at` | ISO datetime | Yes | Identity creation time. |
| `consent_version` | string | No | Version of credential/privacy consent accepted. |

Example:

```json
{
  "learner_id": "learner_123",
  "display_name": "Anonymous Learner",
  "wallet_public_key": "G...",
  "identity_provider": "wallet",
  "created_at": "2026-06-26T00:00:00Z",
  "consent_version": "credentials-v1"
}
```

### Learning Achievement

Represents an awarded achievement, badge, or credential claim.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `achievement_id` | string | Yes | Unique id for this achievement record. |
| `learner_id` | string | Yes | Owner of the achievement. |
| `achievement_type` | string | Yes | `session_completion`, `quiz_mastery`, `study_streak`, `topic_badge`, or `custom`. |
| `title` | string | Yes | Human-readable display title. |
| `description` | string | Yes | Short explanation of what was achieved. |
| `status` | string | Yes | `draft`, `issued`, `revoked`, or `expired`. |
| `criteria` | object | Yes | Rule that must be satisfied before issuing. |
| `evidence_ids` | string[] | Yes | References to evidence records. |
| `badge_metadata_id` | string | No | Optional display metadata. |
| `issuer` | object | Yes | App, organization, or future contract issuer. |
| `issued_at` | ISO datetime | No | Present when status is `issued`. |
| `expires_at` | ISO datetime | No | Optional expiration time. |
| `revoked_at` | ISO datetime | No | Present when revoked. |
| `revocation_reason` | string | No | Safe explanation for revocation. |

Example:

```json
{
  "achievement_id": "ach_001",
  "learner_id": "learner_123",
  "achievement_type": "quiz_mastery",
  "title": "Intermediate Biology Quiz Mastery",
  "description": "Completed a biology study deck with at least 80% quiz accuracy.",
  "status": "issued",
  "criteria": {
    "topic": "Biology",
    "difficulty": "intermediate",
    "minimum_cards_viewed": 8,
    "minimum_quiz_accuracy": 80
  },
  "evidence_ids": ["ev_001"],
  "badge_metadata_id": "badge_quiz_mastery_intermediate",
  "issuer": {
    "name": "Study Copilot",
    "type": "application"
  },
  "issued_at": "2026-06-26T00:00:00Z"
}
```

### Evidence and Proof

Evidence records explain why an achievement was issued. Proof fields allow the
evidence to become verifiable without exposing raw learning material.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `evidence_id` | string | Yes | Unique evidence record id. |
| `achievement_id` | string | Yes | Parent achievement. |
| `session_id` | string | No | Related study session id. |
| `source_type` | string | Yes | `topic`, `notes`, `pdf`, or `manual`. |
| `topic_or_title` | string | No | Safe display title, not raw notes. |
| `cards_viewed` | number | No | Count of viewed cards. |
| `total_cards` | number | No | Total cards in session. |
| `quizzes_attempted` | number | No | Attempt count. |
| `quizzes_correct` | number | No | Correct answer count. |
| `accuracy` | number | No | Rounded accuracy percentage. |
| `completed_at` | ISO datetime | No | When evidence was completed. |
| `content_hash` | string | No | Hash of normalized evidence payload. |
| `proof_hash` | string | No | Hash intended for public verification. |
| `signature` | string | No | Future backend or wallet signature. |
| `verification_method` | string | No | `backend`, `wallet_signature`, `soroban_record`, or `none`. |
| `soroban_record` | object | No | Future on-chain reference. |
| `privacy_level` | string | Yes | `private`, `shared`, or `public`. |

Example:

```json
{
  "evidence_id": "ev_001",
  "achievement_id": "ach_001",
  "session_id": "session_123",
  "source_type": "topic",
  "topic_or_title": "Biology",
  "cards_viewed": 10,
  "total_cards": 10,
  "quizzes_attempted": 5,
  "quizzes_correct": 4,
  "accuracy": 80,
  "completed_at": "2026-06-26T00:00:00Z",
  "content_hash": "sha256:...",
  "proof_hash": "sha256:...",
  "verification_method": "backend",
  "privacy_level": "private"
}
```

### Badge Metadata

Badge metadata controls presentation and categorization. It should remain
separate from proof data so badges can be updated visually without changing the
evidence record.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `badge_metadata_id` | string | Yes | Stable badge template id. |
| `name` | string | Yes | Display name. |
| `description` | string | Yes | Badge description. |
| `category` | string | Yes | `completion`, `mastery`, `streak`, `topic`, or `contribution`. |
| `level` | string | No | `bronze`, `silver`, `gold`, or custom level. |
| `image_uri` | string | No | Optional badge image. |
| `tags` | string[] | No | Search and display tags. |
| `criteria_summary` | string | Yes | Human-readable criteria. |
| `created_at` | ISO datetime | Yes | Template creation time. |
| `updated_at` | ISO datetime | No | Template update time. |

Example:

```json
{
  "badge_metadata_id": "badge_quiz_mastery_intermediate",
  "name": "Quiz Mastery",
  "description": "Awarded for high quiz accuracy in a study session.",
  "category": "mastery",
  "level": "silver",
  "image_uri": "/badges/quiz-mastery.svg",
  "tags": ["quiz", "accuracy", "study"],
  "criteria_summary": "Complete a deck with at least 80% quiz accuracy.",
  "created_at": "2026-06-26T00:00:00Z"
}
```

## Future Soroban Record

If credentials are later anchored to Soroban, the on-chain record should contain
only minimal verification data.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `network` | string | Yes | `testnet` or `mainnet`. |
| `contract_id` | string | Yes | Soroban contract id. |
| `transaction_hash` | string | Yes | Transaction that recorded or updated the credential. |
| `ledger_sequence` | number | No | Ledger sequence for lookup. |
| `issuer_public_key` | string | Yes | Issuer account or contract authority. |
| `subject_public_key` | string | No | Learner wallet public key when consented. |
| `proof_hash` | string | Yes | Hash of the off-chain credential proof. |
| `recorded_at` | ISO datetime | Yes | Time the record was anchored. |

Do not put raw notes, PDF text, full generated cards, quiz answers, or private
study history on-chain.

## Privacy Model

Credential privacy should be explicit and opt-in.

| Privacy level | Meaning | Suitable data |
| --- | --- | --- |
| `private` | Stored locally or in a private backend account only. | Full local evidence and learner progress. |
| `shared` | User can share with a link, export, or selected verifier. | Badge summary, criteria, and selected evidence fields. |
| `public` | Safe to show on a profile or anchor publicly. | Badge title, issuer, issued time, and proof hash. |

Privacy requirements:

- Do not store raw notes or PDF text in credential records by default.
- Do not publish source material, quiz answers, or generated card content
  on-chain.
- Hash evidence only after normalizing it into a stable, minimal payload.
- Let users delete private off-chain records when persistence is added.
- Treat wallet public keys as personal data because they can link activity
  across applications.
- Require consent before linking a learner identity to a public wallet record.

## Minimal MVP Data Shape

For the first backend implementation, start with a compact off-chain record:

```json
{
  "achievement": {
    "achievement_id": "ach_001",
    "learner_id": "learner_123",
    "achievement_type": "session_completion",
    "title": "Completed Biology Study Deck",
    "status": "issued",
    "criteria": {
      "minimum_cards_viewed": 10
    },
    "evidence_ids": ["ev_001"],
    "issuer": {
      "name": "Study Copilot",
      "type": "application"
    },
    "issued_at": "2026-06-26T00:00:00Z"
  },
  "evidence": {
    "evidence_id": "ev_001",
    "session_id": "session_123",
    "source_type": "topic",
    "topic_or_title": "Biology",
    "cards_viewed": 10,
    "total_cards": 10,
    "privacy_level": "private"
  }
}
```

This MVP avoids wallet requirements and on-chain writes while still giving the
frontend and backend a shared model.

## Implementation Notes

- Add identity and durable storage before issuing long-lived credentials.
- Generate stable session ids before using session data as evidence.
- Store evidence summaries separately from generated card content.
- Add revocation fields before public sharing or on-chain anchoring.
- Add tests for criteria evaluation and evidence payload normalization.
- Keep badge display metadata editable without changing evidence hashes.

## Open Questions

- Which achievements should be issued automatically versus manually claimed?
- Should anonymous users be able to export local credentials before sign-in?
- Which evidence fields are safe enough for public profile display?
- What user consent flow is needed before wallet linking?
- Should credentials expire when source sessions are deleted?
- Should future Soroban records represent every credential or only user-selected
  public credentials?
