# Study Copilot

Study Copilot is an AI-powered study buddy that turns a study topic, pasted notes, or PDF material into interactive micro-learning cards. It is built for short focused sessions where learners can move through concepts, quizzes, takeaways, code examples, and challenge prompts without setting up a full learning management system.

The current project is a lightweight prototype with a browser-based frontend, a FastAPI backend, Gemini-powered card generation, PDF parsing, local progress state, and an offline sandbox fallback for contributors who do not have an API key yet.

## What It Does

- Generates study cards from a topic and difficulty level.
- Converts pasted notes or articles into smaller learning cards.
- Extracts readable text from PDF uploads and turns it into study material.
- Mixes concept, quiz, takeaway, challenge, and code-oriented cards.
- Tracks local progress, bookmarks, quiz attempts, study streaks, and session activity in the browser experience.
- Falls back to sandbox cards when the backend or Gemini configuration is unavailable.

## Architecture Overview

| Area | Responsibility | Key files |
|------|----------------|-----------|
| Frontend | Single-page learning interface, card navigation, bookmarks, progress UI, keyboard shortcuts, and backend status display. | `study-copilot-full.html` |
| Backend | FastAPI service for card generation, quiz answers, note uploads, PDF uploads, health checks, and offline fallback responses. | `backend/main.py` |
| AI integration | Selects a supported Gemini model when `GOOGLE_API_KEY` is configured and normalizes generated card JSON. | `backend/main.py` |
| PDF parsing | Reads uploaded PDFs with PyPDF2 and truncates large extracted text before prompt generation. | `backend/main.py` |
| Developer setup | Local environment, API key configuration, server startup, and troubleshooting steps. | `SETUP_GUIDE.md`, `backend/requirements.txt` |

## Frontend and Backend Roles

The frontend is intentionally simple: `study-copilot-full.html` owns the learner-facing experience, collects input, renders cards, stores local progress, and calls the backend when live generation is available.

The backend owns API validation, Gemini configuration, fallback card creation, PDF text extraction, card normalization, and HTTP responses. It should stay focused on learning-content generation and avoid taking over browser-only state such as bookmarks or local progress unless a future issue explicitly adds persistence.

## Local Setup

For full setup instructions, see [`SETUP_GUIDE.md`](SETUP_GUIDE.md).

Quick start:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
python backend/main.py
```

Then open `study-copilot-full.html` in a browser. Add `GOOGLE_API_KEY` to `backend/.env` when you want live Gemini responses; without it, the app can still be explored through sandbox fallback cards.

## Contributor Map

Good first contribution areas include:

- Frontend accessibility and responsive UI polish.
- Card state handling, progress display, bookmarks, and keyboard navigation improvements.
- FastAPI endpoint validation, error messages, and response consistency.
- AI prompt quality, JSON normalization, and fallback behavior.
- PDF upload validation and clearer extraction limits.
- Tests, setup documentation, issue templates, and pull request hygiene.
- Stellar/Soroban research notes for learner identity, badges, credentials, and rewards.

Before starting, review the open issues, keep changes scoped to one issue, avoid committing secrets or `.env` files, and include manual verification steps in the pull request. The project contribution checklist lives in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Drips-Ready Roadmap

Study Copilot is not currently a deployed Stellar application. The Drips-ready path is to keep the learning app useful today while researching Stellar/Soroban features that can be introduced through scoped issues.

| Track | Candidate work |
|-------|----------------|
| Documentation | Keep setup, contribution, issue, and API notes clear for new contributors. |
| Product quality | Improve the study flow, card types, accessibility, and offline behavior. |
| Backend reliability | Add tests around FastAPI endpoints, PDF limits, fallback responses, and AI JSON parsing. |
| Stellar identity research | Explore wallet-based learner identity and portable learner profiles. |
| Soroban credentials research | Design proof-of-study badges, verifiable achievements, and credential records before any on-chain implementation. |
| Rewards research | Investigate study streaks or achievement rewards without promising production token flows. |

Related Drips application notes are in [`docs/drips-application-text.md`](docs/drips-application-text.md).

## Current Stellar/Soroban Exploration

Future research may include:

- Stellar wallet-based learner identity.
- Verifiable study achievements and badges.
- Soroban-based learning credential records.
- Study streak and achievement reward research.
- Portable learning progress and proof-of-study concepts.

These are exploration areas, not production deployment claims.

## License

MIT