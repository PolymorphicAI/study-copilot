# Backend API Manual Test Script

Use these `curl` commands to manually verify the Study Copilot FastAPI backend while developing locally. The examples avoid real API keys and work in offline sandbox mode when `GOOGLE_API_KEY` is not configured.

## Prerequisites

Start the backend from the repository root:

```bash
python backend/main.py
```

The examples assume the backend is listening on `http://localhost:8000`.

```bash
BASE_URL="http://localhost:8000"
```

On Windows PowerShell, use:

```powershell
$env:BASE_URL = "http://localhost:8000"
```

## Health check

Verify that the API is running and see whether the backend is using Gemini or offline sandbox mode.

```bash
curl -s "$BASE_URL/" | python -m json.tool
```

Expected fields include:

- `status`
- `app`
- `version`
- `mode`
- `offline_mode`

## Generate study cards

Create a short card deck from a topic. `num_cards` must be between 3 and 10.

```bash
curl -s -X POST "$BASE_URL/api/generate-cards" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Stellar smart contracts",
    "difficulty": "beginner",
    "num_cards": 5
  }' | python -m json.tool
```

Useful checks:

- `success` is `true`.
- `session_id` is present.
- `total_cards` matches the generated card count.
- `cards` is a JSON array.
- `offline_mode` is `true` when no Gemini key is configured.

## Upload notes

Turn pasted notes into cards without using a PDF file.

```bash
curl -s -X POST "$BASE_URL/api/upload-notes" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Active Recall Notes",
    "text_content": "Active recall means testing yourself before rereading. Spaced repetition schedules review over time so weak topics return more often."
  }' | python -m json.tool
```

Useful checks:

- `success` is `true`.
- `session_id` starts with `notes_session_`.
- The response includes generated `cards`.

## Optional progress check

After viewing cards or answering quizzes through the frontend, inspect progress state:

```bash
curl -s "$BASE_URL/api/progress" | python -m json.tool
```

## Optional session listing

List sessions created during the current backend process:

```bash
curl -s "$BASE_URL/api/sessions" | python -m json.tool
```

## Negative checks

Verify validation errors remain readable:

```bash
curl -s -X POST "$BASE_URL/api/generate-cards" \
  -H "Content-Type: application/json" \
  -d '{"topic":"x","difficulty":"expert","num_cards":99}' | python -m json.tool
```

The response should describe validation failures instead of returning a server crash.

## Secret handling

Do not paste real `GOOGLE_API_KEY` values into shell history, issue comments, screenshots, or pull request descriptions. Use `backend/.env.example` as the placeholder reference and keep real `.env` files local.