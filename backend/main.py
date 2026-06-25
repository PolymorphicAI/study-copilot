"""
Study Copilot - AI-Powered Learning Platform
FastAPI backend with Gemini support and offline fallback mode.
"""

from __future__ import annotations

import io
import json
import os
from datetime import datetime
from typing import Any, Optional

import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

APP_NAME = "Study Copilot API"
APP_VERSION = "1.0.0"
MAX_PDF_BYTES = 10 * 1024 * 1024
MAX_NOTES_CHARS = 15000
AI_FALLBACK_MESSAGE = (
    "AI generation is temporarily unavailable, so Study Copilot is showing offline practice cards instead."
)
AI_FALLBACK_GUIDANCE = "You can keep studying now and try live AI generation again later."

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_CANDIDATES = [
    "models/gemini-2.0-flash",
    "models/gemini-1.5-flash",
    "models/gemini-1.5-pro",
    "models/gemini-pro",
]

OFFLINE_MODE = True
MODEL_NAME: Optional[str] = None

if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        available_models = []
        try:
            for model in genai.list_models():
                if "generateContent" in getattr(model, "supported_generation_methods", []):
                    available_models.append(model.name)
        except Exception:
            available_models = []

        for candidate in MODEL_CANDIDATES:
            if not available_models or candidate in available_models:
                MODEL_NAME = candidate
                OFFLINE_MODE = False
                break
    except Exception:
        OFFLINE_MODE = True
        MODEL_NAME = None


app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StudyCard(BaseModel):
    id: str
    type: str
    title: str
    content: str
    code_example: Optional[str] = None
    quiz_options: Optional[list[dict[str, Any]]] = None
    timestamp: str


class GenerateCardsRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    difficulty: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    num_cards: int = Field(default=5, ge=3, le=10)


class QuizAnswerRequest(BaseModel):
    card_id: str
    selected_answer: str


class UploadNotesRequest(BaseModel):
    text_content: str = Field(..., min_length=10, max_length=MAX_NOTES_CHARS)
    title: str = Field(default="Uploaded Notes", min_length=2, max_length=200)


study_sessions: dict[str, dict[str, Any]] = {}

user_progress = {
    "cards_completed": 0,
    "quizzes_correct": 0,
    "quizzes_attempted": 0,
    "bookmarks": [],
    "study_streak": 0,
}


def now_iso() -> str:
    return datetime.now().isoformat()


def make_card_id(prefix: str, index: int) -> str:
    safe_prefix = "".join(ch if ch.isalnum() else "_" for ch in prefix).strip("_")
    return f"{safe_prefix}_{index}_{datetime.now().timestamp()}"


def get_fallback_cards(topic: str) -> list[dict[str, Any]]:
    return [
        {
            "id": make_card_id(topic, 0),
            "type": "concept",
            "title": f"Introduction to {topic}",
            "content": (
                f"Welcome to {topic}. {AI_FALLBACK_MESSAGE} {AI_FALLBACK_GUIDANCE}"
            ),
            "timestamp": now_iso(),
        },
        {
            "id": make_card_id(topic, 1),
            "type": "takeaway",
            "title": "Key Takeaways",
            "content": f"1. Start with the basics of {topic}.\n2. Practice with examples.\n3. Review your weak areas.",
            "timestamp": now_iso(),
        },
        {
            "id": make_card_id(topic, 2),
            "type": "quiz",
            "title": "Quick Quiz",
            "content": f"What is the best first step when learning {topic}?",
            "quiz_options": [
                {"option": "A", "text": "Skip the basics", "correct": False},
                {"option": "B", "text": "Start with core concepts", "correct": True},
                {"option": "C", "text": "Memorize random facts", "correct": False},
                {"option": "D", "text": "Avoid practice", "correct": False},
            ],
            "timestamp": now_iso(),
        },
        {
            "id": make_card_id(topic, 3),
            "type": "challenge",
            "title": "Practice Challenge",
            "content": f"Write down three real-world examples where {topic} could be useful.",
            "timestamp": now_iso(),
        },
        {
            "id": make_card_id(topic, 4),
            "type": "concept",
            "title": "Study Tip",
            "content": "Use short sessions, active recall, and spaced repetition to retain more.",
            "timestamp": now_iso(),
        },
    ]


def clean_ai_json_response(response_text: str) -> str:
    cleaned = response_text.strip()

    if "```json" in cleaned:
        cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0]
    elif "```" in cleaned:
        cleaned = cleaned.split("```", 1)[1].split("```", 1)[0]

    return cleaned.strip()


def normalize_cards(cards: list[dict[str, Any]], prefix: str) -> list[dict[str, Any]]:
    normalized = []

    for index, card in enumerate(cards):
        normalized.append(
            {
                "id": card.get("id") or make_card_id(prefix, index),
                "type": card.get("type", "concept"),
                "title": card.get("title", "Study Card"),
                "content": card.get("content", ""),
                "code_example": card.get("code_example"),
                "quiz_options": card.get("quiz_options"),
                "timestamp": card.get("timestamp") or now_iso(),
            }
        )

    return normalized


def generate_cards_with_ai(topic: str, difficulty: str, num_cards: int) -> list[dict[str, Any]]:
    if OFFLINE_MODE or not MODEL_NAME:
        return get_fallback_cards(topic)

    prompt = f"""
Generate exactly {num_cards} study cards for the topic "{topic}" at {difficulty} level.

Create a useful mix of:
- concept cards
- quiz cards with four options
- takeaway cards
- challenge cards
- code cards only when relevant

Return only a valid JSON array. Do not include markdown.

Expected shape:
[
  {{
    "type": "concept",
    "title": "Short title",
    "content": "Clear explanation"
  }},
  {{
    "type": "quiz",
    "title": "Quick quiz",
    "content": "Question text",
    "quiz_options": [
      {{"option": "A", "text": "Option A", "correct": false}},
      {{"option": "B", "text": "Option B", "correct": true}},
      {{"option": "C", "text": "Option C", "correct": false}},
      {{"option": "D", "text": "Option D", "correct": false}}
    ]
  }}
]
""".strip()

    try:
        model = genai.GenerativeModel(MODEL_NAME.replace("models/", ""))
        response = model.generate_content(prompt)
        cards = json.loads(clean_ai_json_response(response.text))
        return normalize_cards(cards, topic)
    except Exception:
        return get_fallback_cards(topic)


def generate_cards_from_notes(notes_text: str, title: str) -> list[dict[str, Any]]:
    notes_text = notes_text[:MAX_NOTES_CHARS]

    if OFFLINE_MODE or not MODEL_NAME:
        return get_fallback_cards(title)

    prompt = f"""
Turn the following notes into 5 to 7 engaging study cards.

Title: {title}

Notes:
{notes_text}

Return only a valid JSON array. Do not include markdown.
""".strip()

    try:
        model = genai.GenerativeModel(MODEL_NAME.replace("models/", ""))
        response = model.generate_content(prompt)
        cards = json.loads(clean_ai_json_response(response.text))
        return normalize_cards(cards, title)
    except Exception:
        return get_fallback_cards(title)


def extract_pdf_text(file_content: bytes) -> str:
    if len(file_content) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="PDF is too large. Maximum size is 10MB.")

    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read PDF: {exc}") from exc

    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in the PDF.")

    return text[:MAX_NOTES_CHARS]


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "status": "running",
        "app": APP_NAME,
        "version": APP_VERSION,
        "ai_provider": "Google Gemini",
        "mode": "OFFLINE SANDBOX" if OFFLINE_MODE else "CONNECTED TO GEMINI",
        "model": MODEL_NAME,
        "offline_mode": OFFLINE_MODE,
    }


@app.post("/api/generate-cards")
async def generate_cards(request: GenerateCardsRequest) -> dict[str, Any]:
    cards = generate_cards_with_ai(
        topic=request.topic,
        difficulty=request.difficulty,
        num_cards=request.num_cards,
    )

    session_id = f"session_{datetime.now().timestamp()}"
    study_sessions[session_id] = {
        "topic": request.topic,
        "cards": cards,
        "created_at": now_iso(),
        "offline_mode": OFFLINE_MODE,
    }

    return {
        "success": True,
        "session_id": session_id,
        "cards": cards,
        "total_cards": len(cards),
        "offline_mode": OFFLINE_MODE,
    }


@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    text = extract_pdf_text(content)
    cards = generate_cards_from_notes(text, file.filename)

    session_id = f"pdf_session_{datetime.now().timestamp()}"
    study_sessions[session_id] = {
        "source": file.filename,
        "cards": cards,
        "created_at": now_iso(),
        "offline_mode": OFFLINE_MODE,
    }

    return {
        "success": True,
        "session_id": session_id,
        "cards": cards,
        "source_file": file.filename,
        "offline_mode": OFFLINE_MODE,
    }


@app.post("/api/upload-notes")
async def upload_notes(request: UploadNotesRequest) -> dict[str, Any]:
    cards = generate_cards_from_notes(request.text_content, request.title)

    session_id = f"notes_session_{datetime.now().timestamp()}"
    study_sessions[session_id] = {
        "title": request.title,
        "cards": cards,
        "created_at": now_iso(),
        "offline_mode": OFFLINE_MODE,
    }

    return {
        "success": True,
        "session_id": session_id,
        "cards": cards,
        "offline_mode": OFFLINE_MODE,
    }


@app.post("/api/check-answer")
async def check_answer(request: QuizAnswerRequest) -> dict[str, Any]:
    for session in study_sessions.values():
        for card in session["cards"]:
            if card["id"] == request.card_id:
                if card.get("type") != "quiz":
                    raise HTTPException(status_code=400, detail="Not a quiz card.")

                correct_option = next(
                    (option for option in card.get("quiz_options", []) if option.get("correct")),
                    None,
                )

                if not correct_option:
                    raise HTTPException(status_code=400, detail="Quiz card has no correct option.")

                is_correct = correct_option["option"] == request.selected_answer
                user_progress["quizzes_attempted"] += 1

                if is_correct:
                    user_progress["quizzes_correct"] += 1

                return {
                    "correct": is_correct,
                    "correct_answer": correct_option["option"],
                    "explanation": f"The correct answer is {correct_option['option']}: {correct_option['text']}",
                }

    raise HTTPException(status_code=404, detail="Card not found.")


@app.post("/api/bookmark/{card_id}")
async def bookmark_card(card_id: str) -> dict[str, Any]:
    if card_id not in user_progress["bookmarks"]:
        user_progress["bookmarks"].append(card_id)

    return {
        "success": True,
        "bookmarked": True,
        "total_bookmarks": len(user_progress["bookmarks"]),
    }


@app.post("/api/view/{card_id}")
async def view_card(card_id: str) -> dict[str, Any]:
    user_progress["cards_completed"] += 1
    return {
        "success": True,
        "card_id": card_id,
        "cards_completed": user_progress["cards_completed"],
    }


@app.get("/api/progress")
async def get_progress() -> dict[str, Any]:
    accuracy = 0.0
    if user_progress["quizzes_attempted"] > 0:
        accuracy = (user_progress["quizzes_correct"] / user_progress["quizzes_attempted"]) * 100

    return {
        "cards_completed": user_progress["cards_completed"],
        "quizzes_attempted": user_progress["quizzes_attempted"],
        "quizzes_correct": user_progress["quizzes_correct"],
        "accuracy": round(accuracy, 1),
        "study_streak": user_progress["study_streak"],
        "bookmarks": len(user_progress["bookmarks"]),
    }


@app.get("/api/sessions")
async def get_sessions() -> dict[str, Any]:
    return {
        "sessions": [
            {
                "session_id": session_id,
                "topic": session.get("topic", session.get("title", session.get("source", "Unknown"))),
                "num_cards": len(session["cards"]),
                "created_at": session["created_at"],
                "offline_mode": session.get("offline_mode", False),
            }
            for session_id, session in study_sessions.items()
        ]
    }


@app.get("/api/session/{session_id}")
async def get_session(session_id: str) -> dict[str, Any]:
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    return study_sessions[session_id]


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
