"""
Study Copilot - AI-Powered Learning Platform
Main FastAPI Backend - Grok Version (X.AI)
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import json
import requests

# Check for API Key at startup - try XAI_API_KEY first, then GROK_API_KEY
api_key = os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY")

print("\n" + "="*70)
print("🎓 Study Copilot - Grok Backend Startup")
print("="*70)

if not api_key:
    print("\n❌ ERROR: XAI_API_KEY not found!")
    print("\nTo enable Grok AI features, you MUST set your API key:")
    print("\n   export XAI_API_KEY='your-actual-grok-key-here'")
    print("\nThen restart this script.")
    print("\nGet your Grok API key from: https://console.x.ai/")
    print("\n⚠️  Running in OFFLINE MODE with fallback cards only.")
    print("="*70 + "\n")
    OFFLINE_MODE = True
elif api_key.startswith("your-") or api_key == "placeholder":
    print("\n⚠️  WARNING: XAI_API_KEY is set to a placeholder!")
    print(f"   Current value: {api_key}")
    print("\nYou must set your REAL API key from https://console.x.ai/")
    print("\nThen run:")
    print("   export XAI_API_KEY='your-real-key-here'")
    print("   python backend/main_grok.py")
    print("\n⚠️  Running in OFFLINE MODE with fallback cards only.")
    print("="*70 + "\n")
    OFFLINE_MODE = True
else:
    print(f"\n✅ XAI_API_KEY found!")
    print(f"   Key (masked): {api_key[:20]}...{api_key[-10:]}")
    print("\n✅ Grok API configured successfully!")
    print("="*70 + "\n")
    OFFLINE_MODE = False

app = FastAPI(title="Study Copilot API - Grok", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= DATA MODELS =============

class StudyCard(BaseModel):
    id: str
    type: str
    title: str
    content: str
    code_example: Optional[str] = None
    quiz_options: Optional[List[dict]] = None
    timestamp: str

class GenerateCardsRequest(BaseModel):
    topic: str
    difficulty: str = "beginner"
    num_cards: int = 5

class QuizAnswerRequest(BaseModel):
    card_id: str
    selected_answer: str

class UploadNotesRequest(BaseModel):
    text_content: str
    title: str

# ============= IN-MEMORY STORAGE =============

study_sessions = {}
user_progress = {
    "cards_completed": 0,
    "quizzes_correct": 0,
    "quizzes_attempted": 0,
    "bookmarks": [],
    "study_streak": 0
}

# ============= HELPER FUNCTIONS =============

def call_grok_api(prompt: str) -> str:
    """
    Call Grok API directly using requests library
    Compatible with OpenAI API format
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "grok-beta",
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        print("📡 Calling Grok API...")
        # Try the correct X.AI endpoint
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Grok API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
        
        data = response.json()
        return data['choices'][0]['message']['content']
    
    except requests.exceptions.Timeout:
        print("❌ Grok API timeout - request took too long")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Grok API - check internet connection")
        return None
    except Exception as e:
        print(f"❌ Error calling Grok API: {e}")
        return None

def generate_cards_with_ai(topic: str, difficulty: str, num_cards: int) -> List[dict]:
    """
    Use Grok to generate study cards
    """
    
    if OFFLINE_MODE:
        print(f"📖 OFFLINE MODE: Using fallback cards for '{topic}'")
        return get_fallback_cards(topic)
    
    prompt = f"""Generate exactly {num_cards} study cards for the topic: "{topic}" at {difficulty} level.

Create a mix of different card types:
1. Concept explanation cards (explain key ideas simply)
2. Code example cards (working code snippets with explanations)
3. Quiz cards (multiple choice with 4 options)
4. Key takeaway cards (summarize important points)
5. Practice challenge cards (hands-on exercises)

Return ONLY a JSON array with this exact structure (NO markdown, NO code blocks):
[
  {{
    "type": "concept",
    "title": "What is [Topic]?",
    "content": "Clear explanation here..."
  }},
  {{
    "type": "code",
    "title": "Simple Example",
    "content": "Explanation of what the code does",
    "code_example": "# Python code here\\nprint('hello')"
  }},
  {{
    "type": "quiz",
    "title": "Test Your Knowledge",
    "content": "What is the main purpose of [concept]?",
    "quiz_options": [
      {{"option": "A", "text": "Answer 1", "correct": false}},
      {{"option": "B", "text": "Answer 2", "correct": true}},
      {{"option": "C", "text": "Answer 3", "correct": false}},
      {{"option": "D", "text": "Answer 4", "correct": false}}
    ]
  }},
  {{
    "type": "takeaway",
    "title": "Key Points",
    "content": "1. Point one\\n2. Point two\\n3. Point three"
  }},
  {{
    "type": "challenge",
    "title": "Build This!",
    "content": "Description of hands-on challenge"
  }}
]

Make it engaging, practical, and easy to understand. Use real examples. Return ONLY valid JSON."""

    try:
        print(f"🤖 Generating {num_cards} cards for '{topic}' ({difficulty})...")
        print(f"   Using model: Grok (X.AI)")
        
        response_text = call_grok_api(prompt)
        
        if not response_text:
            print("❌ No response from Grok")
            return get_fallback_cards(topic)
        
        print(f"✅ Received response from Grok (length: {len(response_text)} chars)")
        
        # Clean up the response (remove markdown code blocks if present)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        cards = json.loads(response_text.strip())
        
        # Add IDs and timestamps
        for i, card in enumerate(cards):
            card['id'] = f"{topic.replace(' ', '_')}_{i}_{datetime.now().timestamp()}"
            card['timestamp'] = datetime.now().isoformat()
        
        print(f"✅ Successfully generated {len(cards)} cards")
        return cards
    
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON response: {e}")
        if response_text:
            print(f"   Response was: {response_text[:200]}")
        return get_fallback_cards(topic)
    except Exception as e:
        print(f"❌ Error generating cards: {e}")
        return get_fallback_cards(topic)

def get_fallback_cards(topic: str) -> List[dict]:
    """Fallback cards if AI generation fails"""
    return [
        {
            "id": f"{topic}_concept_0",
            "type": "concept",
            "title": f"Introduction to {topic}",
            "content": f"Welcome to {topic}! This is a placeholder card. To see AI-generated content, ensure your GROK_API_KEY is set and valid. Get one at https://console.x.ai/",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": f"{topic}_code_1",
            "type": "code",
            "title": "Sample Code",
            "content": "Example of working with this topic",
            "code_example": f"# Example for {topic}\nprint('Learning {topic}!')\n# Real code will appear when Grok is connected",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": f"{topic}_quiz_2",
            "type": "quiz",
            "title": "Quick Quiz",
            "content": f"What is {topic}?",
            "quiz_options": [
                {"option": "A", "text": "Option 1", "correct": False},
                {"option": "B", "text": "Correct answer", "correct": True},
                {"option": "C", "text": "Option 3", "correct": False},
                {"option": "D", "text": "Option 4", "correct": False}
            ],
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": f"{topic}_takeaway_3",
            "type": "takeaway",
            "title": "Key Points",
            "content": f"Key concepts about {topic}:\n1. First important concept\n2. Second important concept\n3. Third important concept",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": f"{topic}_challenge_4",
            "type": "challenge",
            "title": "Practice Challenge",
            "content": f"Apply {topic} in a real-world scenario. How would you use these concepts in practice?",
            "timestamp": datetime.now().isoformat()
        }
    ]

def process_pdf_text(file_content: bytes) -> str:
    """Extract text from PDF"""
    try:
        import PyPDF2
        import io
        
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

def generate_cards_from_notes(notes_text: str, title: str) -> List[dict]:
    """Generate study cards from text notes using Grok"""
    
    if OFFLINE_MODE:
        return get_fallback_cards(title)
    
    prompt = f"""You are a study assistant. I have these notes titled "{title}":

{notes_text[:3000]}

Generate 5-7 engaging study cards from this content. Mix different types:
- Concept explanations for key ideas
- Code examples if there's code
- Quiz questions to test understanding
- Key takeaways summarizing main points
- Practice challenges

Return ONLY valid JSON (NO markdown):
[{{"type": "concept", "title": "...", "content": "..."}}, ...]"""

    try:
        print(f"🤖 Generating cards from notes: {title}...")
        response_text = call_grok_api(prompt)
        
        if not response_text:
            return get_fallback_cards(title)
        
        # Clean up response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        cards = json.loads(response_text.strip())
        
        # Add metadata
        for i, card in enumerate(cards):
            card['id'] = f"{title.replace(' ', '_')}_{i}_{datetime.now().timestamp()}"
            card['timestamp'] = datetime.now().isoformat()
        
        print(f"✅ Generated {len(cards)} cards from notes")
        return cards
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return get_fallback_cards(title)

# ============= API ENDPOINTS =============

@app.get("/")
async def root():
    """Health check"""
    mode = "OFFLINE SANDBOX" if OFFLINE_MODE else "CONNECTED TO GROK"
    return {
        "status": "running",
        "app": "Study Copilot API",
        "version": "1.0.0",
        "ai_provider": "Grok (X.AI)",
        "mode": mode,
        "offline_mode": OFFLINE_MODE,
        "message": "To unlock AI features, set GROK_API_KEY environment variable" if OFFLINE_MODE else "✅ Connected to Grok AI!"
    }

@app.post("/api/generate-cards")
async def generate_cards(request: GenerateCardsRequest):
    """Generate study cards"""
    try:
        cards = generate_cards_with_ai(
            topic=request.topic,
            difficulty=request.difficulty,
            num_cards=request.num_cards
        )
        
        session_id = f"session_{datetime.now().timestamp()}"
        study_sessions[session_id] = {
            "topic": request.topic,
            "cards": cards,
            "created_at": datetime.now().isoformat(),
            "offline_mode": OFFLINE_MODE
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "cards": cards,
            "total_cards": len(cards),
            "offline_mode": OFFLINE_MODE,
            "message": "⚠️ Offline - fallback cards" if OFFLINE_MODE else "✅ Generated by Grok AI"
        }
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload PDF and generate cards"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files supported")
    
    try:
        print(f"📄 Processing PDF: {file.filename}")
        content = await file.read()
        text = process_pdf_text(content)
        print(f"✅ Extracted {len(text)} characters")
        
        cards = generate_cards_from_notes(text, file.filename)
        
        session_id = f"pdf_session_{datetime.now().timestamp()}"
        study_sessions[session_id] = {
            "source": file.filename,
            "cards": cards,
            "created_at": datetime.now().isoformat(),
            "offline_mode": OFFLINE_MODE
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "cards": cards,
            "source_file": file.filename,
            "offline_mode": OFFLINE_MODE
        }
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-notes")
async def upload_notes(request: UploadNotesRequest):
    """Generate cards from text notes"""
    try:
        print(f"📝 Processing notes: {request.title}")
        cards = generate_cards_from_notes(request.text_content, request.title)
        
        session_id = f"notes_session_{datetime.now().timestamp()}"
        study_sessions[session_id] = {
            "title": request.title,
            "cards": cards,
            "created_at": datetime.now().isoformat(),
            "offline_mode": OFFLINE_MODE
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "cards": cards,
            "offline_mode": OFFLINE_MODE
        }
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check-answer")
async def check_answer(request: QuizAnswerRequest):
    """Check quiz answer"""
    for session in study_sessions.values():
        for card in session['cards']:
            if card['id'] == request.card_id:
                if card['type'] != 'quiz':
                    raise HTTPException(status_code=400, detail="Not a quiz card")
                
                correct_option = None
                for option in card['quiz_options']:
                    if option['correct']:
                        correct_option = option
                        break
                
                is_correct = correct_option['option'] == request.selected_answer
                
                user_progress['quizzes_attempted'] += 1
                if is_correct:
                    user_progress['quizzes_correct'] += 1
                
                return {
                    "correct": is_correct,
                    "correct_answer": correct_option['option'],
                    "explanation": f"Correct! The answer is {correct_option['option']}: {correct_option['text']}"
                }
    
    raise HTTPException(status_code=404, detail="Card not found")

@app.post("/api/bookmark/{card_id}")
async def bookmark_card(card_id: str):
    """Bookmark a card"""
    if card_id not in user_progress['bookmarks']:
        user_progress['bookmarks'].append(card_id)
    
    return {
        "success": True,
        "bookmarked": True,
        "total_bookmarks": len(user_progress['bookmarks'])
    }

@app.get("/api/progress")
async def get_progress():
    """Get user progress"""
    accuracy = 0
    if user_progress['quizzes_attempted'] > 0:
        accuracy = (user_progress['quizzes_correct'] / user_progress['quizzes_attempted']) * 100
    
    return {
        "cards_completed": user_progress['cards_completed'],
        "quizzes_attempted": user_progress['quizzes_attempted'],
        "quizzes_correct": user_progress['quizzes_correct'],
        "accuracy": round(accuracy, 1),
        "study_streak": user_progress['study_streak'],
        "bookmarks": len(user_progress['bookmarks'])
    }

@app.get("/api/sessions")
async def get_sessions():
    """Get all sessions"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "topic": session.get('topic', session.get('title', 'Unknown')),
                "num_cards": len(session['cards']),
                "created_at": session['created_at']
            }
            for sid, session in study_sessions.items()
        ]
    }

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get specific session"""
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return study_sessions[session_id]

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🎓 Study Copilot Backend with Grok (X.AI)")
    print("="*70)
    print(f"Mode: {'🔴 OFFLINE' if OFFLINE_MODE else '🟢 GROK AI ENABLED'}")
    print(f"AI Provider: Grok (X.AI)")
    print(f"Server: http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)