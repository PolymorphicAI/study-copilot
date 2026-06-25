import importlib
import sys

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def backend_module(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    sys.modules.pop("backend.main", None)

    module = importlib.import_module("backend.main")
    module.OFFLINE_MODE = True
    module.MODEL_NAME = None
    module.study_sessions.clear()
    module.user_progress.update(
        {
            "cards_completed": 0,
            "quizzes_correct": 0,
            "quizzes_attempted": 0,
            "bookmarks": [],
            "study_streak": 0,
        }
    )
    return module


@pytest.fixture()
def client(backend_module):
    with TestClient(backend_module.app) as test_client:
        yield test_client


def test_root_health_endpoint_reports_offline_mode(client):
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "running"
    assert payload["app"] == "Study Copilot API"
    assert payload["version"] == "1.0.0"
    assert payload["ai_provider"] == "Google Gemini"
    assert payload["offline_mode"] is True
    assert payload["mode"] == "OFFLINE SANDBOX"
    assert payload["model"] is None


def test_generate_cards_accepts_valid_payload_without_real_ai(client, backend_module, monkeypatch):
    generated_cards = [
        {
            "id": "card-1",
            "type": "concept",
            "title": "Photosynthesis basics",
            "content": "Plants convert light into chemical energy.",
            "timestamp": "2026-06-26T00:00:00",
        }
    ]

    def fake_generate_cards(topic, difficulty, num_cards):
        assert topic == "Photosynthesis"
        assert difficulty == "intermediate"
        assert num_cards == 3
        return generated_cards

    monkeypatch.setattr(backend_module, "generate_cards_with_ai", fake_generate_cards)

    response = client.post(
        "/api/generate-cards",
        json={"topic": "Photosynthesis", "difficulty": "intermediate", "num_cards": 3},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["cards"] == generated_cards
    assert payload["total_cards"] == 1
    assert payload["offline_mode"] is True
    assert payload["session_id"] in backend_module.study_sessions
    assert backend_module.study_sessions[payload["session_id"]]["topic"] == "Photosynthesis"


@pytest.mark.parametrize(
    ("payload", "expected_error_fragment"),
    [
        ({"difficulty": "beginner", "num_cards": 5}, "Field required"),
        ({"topic": "AI", "difficulty": "expert", "num_cards": 5}, "String should match pattern"),
        ({"topic": "AI", "difficulty": "beginner", "num_cards": 2}, "greater than or equal to 3"),
        ({"topic": "AI", "difficulty": "beginner", "num_cards": 11}, "less than or equal to 10"),
    ],
)
def test_generate_cards_rejects_invalid_payloads(client, payload, expected_error_fragment):
    response = client.post("/api/generate-cards", json=payload)

    assert response.status_code == 422
    assert expected_error_fragment in response.text


def seed_quiz_session(backend_module):
    backend_module.study_sessions["session-test"] = {
        "topic": "Testing",
        "created_at": "2026-06-26T00:00:00",
        "offline_mode": True,
        "cards": [
            {
                "id": "quiz-card-1",
                "type": "quiz",
                "title": "Testing quiz",
                "content": "Which option is correct?",
                "quiz_options": [
                    {"option": "A", "text": "Incorrect", "correct": False},
                    {"option": "B", "text": "Correct", "correct": True},
                    {"option": "C", "text": "Incorrect", "correct": False},
                    {"option": "D", "text": "Incorrect", "correct": False},
                ],
                "timestamp": "2026-06-26T00:00:00",
            },
            {
                "id": "concept-card-1",
                "type": "concept",
                "title": "Not a quiz",
                "content": "This card cannot be answered.",
                "timestamp": "2026-06-26T00:00:00",
            },
        ],
    }


def test_check_answer_marks_correct_selection(client, backend_module):
    seed_quiz_session(backend_module)

    response = client.post(
        "/api/check-answer",
        json={"card_id": "quiz-card-1", "selected_answer": "B"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["correct"] is True
    assert payload["correct_answer"] == "B"
    assert "Correct" in payload["explanation"]
    assert backend_module.user_progress["quizzes_attempted"] == 1
    assert backend_module.user_progress["quizzes_correct"] == 1


def test_check_answer_marks_incorrect_selection(client, backend_module):
    seed_quiz_session(backend_module)

    response = client.post(
        "/api/check-answer",
        json={"card_id": "quiz-card-1", "selected_answer": "A"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["correct"] is False
    assert payload["correct_answer"] == "B"
    assert backend_module.user_progress["quizzes_attempted"] == 1
    assert backend_module.user_progress["quizzes_correct"] == 0


def test_check_answer_rejects_unknown_card(client, backend_module):
    seed_quiz_session(backend_module)

    response = client.post(
        "/api/check-answer",
        json={"card_id": "missing-card", "selected_answer": "A"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Card not found."


def test_check_answer_rejects_non_quiz_card(client, backend_module):
    seed_quiz_session(backend_module)

    response = client.post(
        "/api/check-answer",
        json={"card_id": "concept-card-1", "selected_answer": "A"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Not a quiz card."


def test_check_answer_requires_selected_answer(client):
    response = client.post("/api/check-answer", json={"card_id": "quiz-card-1"})

    assert response.status_code == 422
    assert "selected_answer" in response.text
