# Study Copilot 🚀

Study Copilot is an AI-powered, immersive learning platform that translates any study topic, text notes, or PDF documents into high-impact micro-learning cards. Featuring a vertical scrolling experience inspired by modern social media feeds, Study Copilot delivers a seamless, gamified studying workflow that makes learning engaging and accessible on both desktop and mobile devices.

---

## 🎨 System Architecture

Below is a high-level representation of how the HTML5/Vanilla JS frontend interacts with the FastAPI Python backend and the Google Gemini API.

```
       +---------------------------------------------+
       |               User Browser                  |
       |  (study-copilot-full.html / HTML/CSS/JS)   |
       +----------------------+----------------------+
                              |
              HTTP API Call   |   JSON Response
             (fetch requests) |  (Sanitized Cards)
                              v
       +----------------------+----------------------+
       |             FastAPI Web Server              |
       |             (backend/main.py)               |
       +-------+--------------+---------------+------+
               |              |               |
               |              |               | PDF Text
        In-memory Data        | Pydantic      | Extraction
         (Session/Stats)      | Validation    | (PyPDF2)
                              v               v
                   +----------+---------------+------+
                   |      Google Gemini API          |
                   |      (gemini-1.5-flash)         |
                   +---------------------------------+
```

---

## ✨ Features

- **TikTok-Style Vertical Flow**: Swipe or scroll vertically through bite-sized learning cards that snap cleanly to the viewport.
- **Micro-Learning Segment Types**:
  - 📚 **Concept (Concept Card)**: Crystal-clear, focused explanations of core terms.
  - 💻 **Code (Code Card)**: Live code blocks highlighting practical syntax applications with a built-in copy utility.
  - 🎯 **Quiz (Quiz Card)**: Dynamic multiple-choice questions validated by the backend. Correct answers trigger an animated countdown to auto-scroll you forward.
  - 💡 **Takeaway (Takeaway Card)**: Condensed summaries of essential concepts.
  - 🚀 **Challenge (Challenge Card)**: Real-world practice problems with starter snippets to test your comprehension.
- **Multiple Material Parsers**:
  - **Topic Generator**: Query the AI directly with a search prompt.
  - **PDF Text Extractor**: Upload standard PDF chapters to extract core segments.
  - **Notes Analyzer**: Paste raw class summaries or articles.
- **Gamified Statistics Drawer**: Tracks your daily learning streak, cards viewed, quiz completion counts, accuracy rates, and holds your bookmarked study decks.
- **Keyboard Navigation**: Speed-study with Arrow Up / Down keys for swiping and keys `1`, `2`, `3`, `4` to pick quiz answers.
- **Offline Sandbox Fallback**: If the backend server is down, the frontend automatically falls back to offline emulation mode so you can preview the platform.

---

## 🛠️ Technology Stack

### Frontend
- **Structure & Layout**: Semantic HTML5, CSS Variables, and Flexbox/CSS Grid.
- **Design & Themes**: Custom glassmorphism, responsive snapping container, inline SVG icons, and Outfit & Space Mono Google Fonts.
- **Scripting**: Pure Vanilla JS (no third-party frameworks, libraries, or builders).

### Backend
- **Engine**: Python 3.8+ & FastAPI.
- **AI Model**: Google Gemini API (`gemini-1.5-flash` model).
- **Libraries**:
  - `google-generativeai` for AI calls.
  - `PyPDF2` for local text extraction from multipart file uploads.
  - `python-multipart` for forms processing.
  - `pydantic` for data validation schemas.
  - `python-dotenv` for config management.
  - `uvicorn` as the ASGI production web server.

---

## 🔌 API Documentation

Detailed specifications for endpoints exposed at `http://localhost:8000/api/`:

| Method | Endpoint | Description | Payload Schema | Response Schema |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | API Health & AI Status | None | `{status, app, ai_provider, mode}` |
| **POST** | `/api/generate-cards` | Generates study deck | `{topic, difficulty, num_cards}` | `{success, session_id, cards, total_cards}` |
| **POST** | `/api/upload-pdf` | Generates cards from PDF | Form data (`file`, `difficulty`, `num_cards`) | `{success, session_id, cards, source_file}` |
| **POST** | `/api/upload-notes` | Generates cards from notes | `{text_content, title}` | `{success, session_id, cards}` |
| **POST** | `/api/check-answer` | Validates a quiz option | `{card_id, selected_answer}` | `{correct, correct_answer, explanation}` |
| **POST** | `/api/bookmark/{card_id}` | Bookmarks/Saves study card | URL parameter | `{success, bookmarked, total_bookmarks}` |
| **POST** | `/api/view/{card_id}` | Logs a card read event | URL parameter | `{success, cards_viewed}` |
| **GET** | `/api/progress` | Retrieves user metrics | None | `{cards_viewed, quizzes_attempted, quizzes_correct, accuracy, bookmarks, study_streak}` |
| **GET** | `/api/sessions` | Lists created session logs | None | `{sessions: [...]}` |
| **GET** | `/api/session/{session_id}` | Retrieves session cards | URL parameter | `{session_id, topic, cards, created_at}` |

---

## 🚀 Quick Start (Installation)

Please refer to the detailed [SETUP_GUIDE.md](file:///c:/Users/Gideon/Desktop/workspace/Study%20Copilot/SETUP_GUIDE.md) to set up and run the application locally.
