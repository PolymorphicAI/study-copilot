# Persistent Storage Research

Study Copilot currently stores generated sessions, bookmarks, quiz progress, and view counts in process memory. This keeps the prototype simple, but it also means history disappears when the backend restarts and cannot support real learner accounts, cross-device progress, or future credential and reward features.

This document compares storage options and recommends a practical MVP path.

## Current In-Memory Behavior

`backend/main.py` keeps state in two module-level objects:

- `study_sessions`, a dictionary of generated sessions keyed by session ID.
- `user_progress`, a dictionary with aggregate counters for completed cards, quizzes, bookmarks, and study streak.

The current API supports:

- generating topic-based sessions,
- generating sessions from pasted notes,
- generating sessions from PDF text,
- logging card views,
- toggling bookmarks,
- submitting quiz answers,
- listing session summaries,
- loading a previous session by ID.

This is enough for a demo, but the data is not durable and is shared by every learner using the same backend process.

## Storage Requirements

An MVP persistent store should support:

- session metadata and generated cards,
- per-card view and completion progress,
- bookmarks,
- quiz attempts,
- optional anonymous learner identifiers,
- deletion of learner history,
- simple local development setup,
- future migration to hosted deployment.

It should avoid storing raw pasted notes or extracted PDF text by default.

## Options

### SQLite

SQLite is an embedded relational database stored in a local file.

Benefits:

- Very small setup cost for local development.
- Works well with FastAPI prototypes and simple demos.
- Supports relational data for sessions, cards, progress, bookmarks, and quiz attempts.
- Easy to commit migration scripts without requiring a hosted service.
- Good fit for a single-instance deployment.

Tradeoffs:

- Not ideal for multiple backend replicas writing to the same database file.
- Requires a backup strategy if used beyond local demos.
- Concurrent write behavior is more limited than hosted Postgres.
- Needs care in serverless environments where the filesystem may be ephemeral.

### Postgres

Postgres is a hosted or self-managed relational database.

Benefits:

- Strong production default for relational app data.
- Handles concurrent users and multiple backend instances.
- Supports migrations, indexes, transactions, JSON fields, and analytics queries.
- Easy to model study sessions, cards, bookmarks, and quiz attempts.
- Can support future accounts, teams, or wallet-linked identity.

Tradeoffs:

- More setup than SQLite for new contributors.
- Requires credentials and secret management.
- Needs hosted database provisioning for deployment.
- May be more infrastructure than the prototype needs immediately.

### Supabase

Supabase provides hosted Postgres plus auth, APIs, and dashboard tools.

Benefits:

- Gives the project Postgres with a low-friction hosted setup.
- Built-in auth could help with future learner accounts.
- Row-level security can protect per-user session history.
- Dashboard is useful for maintainers and reviewers.
- Good path if the frontend later needs direct user-authenticated reads.

Tradeoffs:

- Adds a platform dependency.
- Requires careful row-level security configuration.
- Service keys and anon keys must be handled safely.
- Local development is heavier than a plain SQLite file.
- Direct frontend access should not bypass backend validation or privacy rules.

### File-Based JSON Storage

File-based storage writes sessions and progress to JSON files.

Benefits:

- Very easy to understand and debug.
- No external service needed.
- Useful for local prototypes, fixtures, or export/import features.

Tradeoffs:

- Harder to query, paginate, and migrate.
- Risky with concurrent writes.
- Easy to corrupt without careful locking and atomic writes.
- Poor fit for multi-user or multi-instance deployments.
- Privacy deletion and retention rules become harder to enforce consistently.

## Comparison

| Option | Setup | Durability | Multi-user fit | Deployment fit | Best use |
| --- | --- | --- | --- | --- | --- |
| SQLite | Low | Good on stable disk | Limited | Single instance | MVP persistence |
| Postgres | Medium | Strong | Strong | Production | Scalable backend |
| Supabase | Medium | Strong | Strong with RLS | Hosted app | Auth-backed product path |
| JSON files | Low | Fragile | Weak | Local only | Debug/export prototypes |

## Recommended MVP

Use SQLite first behind a small storage adapter interface.

SQLite is the best next step because it solves the biggest prototype limitation without forcing contributors to provision infrastructure. The adapter boundary keeps the project ready for Postgres or Supabase later.

The MVP should store:

- sessions,
- generated cards,
- card progress,
- bookmarks,
- quiz attempts.

The MVP should not store raw notes, extracted PDF text, full prompts, or raw AI provider responses unless a separate debug mode and retention policy are added.

## Suggested Schema Direction

Start with relational tables:

- `study_sessions`
- `study_cards`
- `card_progress`
- `bookmarks`
- `quiz_attempts`
- `learners` or `anonymous_learners` only when identity is introduced

Use UUIDs for primary keys instead of timestamp-only IDs. Keep `created_at`, `updated_at`, and optional `deleted_at` fields on user-owned data.

## Deployment Considerations

### Local Development

SQLite can be created automatically from migrations or startup initialization. The default database path should be configurable and ignored by git.

### Hosted Single Instance

SQLite can work when the host provides persistent disk and only one backend instance writes to the database. Backups should be documented before using it for real learner data.

### Hosted Multi-Instance

Move to Postgres or Supabase when the app needs multiple backend replicas, shared hosted state, or reliable multi-user access.

### Serverless

Avoid relying on local SQLite files in serverless environments unless the platform provides durable storage. Use hosted Postgres/Supabase instead.

## Migration Plan

1. Define a storage adapter with methods for sessions, cards, views, bookmarks, quiz attempts, and deletion.
2. Implement the current in-memory store behind the adapter to preserve behavior.
3. Add SQLite models and migrations.
4. Switch the FastAPI routes to use the adapter instead of module-level dictionaries directly.
5. Add tests for create, list, load, view, bookmark, quiz attempt, and delete flows.
6. Add configuration for the database URL or SQLite path.
7. Document when to move from SQLite to Postgres or Supabase.

## Risks And Mitigations

- Privacy risk: do not persist raw study materials by default.
- Data loss risk: document backup expectations when using SQLite.
- Concurrency risk: use Postgres/Supabase for multi-instance deployments.
- Migration risk: keep schema changes versioned and tested.
- Identity risk: keep anonymous history separate from any future public wallet identifier.

## Open Questions

- Should the MVP persist history automatically, or only after learners opt in?
- How should anonymous browser sessions map to backend learner records?
- Should generated cards expire after a retention window?
- Should bookmarks be exportable before a learner deletes session history?
- When should the project introduce hosted Postgres or Supabase as the default deployment path?
