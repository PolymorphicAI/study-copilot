"""
Study Copilot - AI-Powered Learning Platform
Main FastAPI Backend - Hugging Face Inference API Version
Uses free open-source models like Mistral, Llama, Zephyr
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import json
import requests

# Check for HF Token at startup
hf_token = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")

print("\n" + "="*70)
print("🎓 Study Copilot - Hugging Face Backend")
print("="*70)

if not hf_token:
    print("\n❌ ERROR: HUGGINGFACE_API_KEY not found!")
    print("\nTo enable Hugging Face AI features:")
    print("1. Get free token from: https://huggingface.co/settings/tokens")
    print("2. Create a 'read' token (takes 30 seconds)")
    print("3. Set it in terminal:")
    print("   export HUGGINGFACE_API_KEY='your-hf-token'")
    print("4. Restart this script")
    print("\nRunning in OFFLINE MODE with fallback cards.")
    print("="*70 + "\n")
    OFFLINE_MODE = True
    MODEL = None
else:
    print(f"\n✅ HUGGINGFACE_API_KEY found!")
    print(f"   Token (masked): {hf_token[:20]}...{hf_token[-10:]}")
    
    # Use a free open-source model
    # Options: mistralai/Mistral-7B-Instruct-v0.2, meta-llama/Llama-2-7b-chat, HuggingFaceH4/zephyr-7b-beta
    MODEL = "mistralai/Mistral-7B-Instruct-v0.2"  # Fast, accurate, free
    
    print(f"\n✅ Using model: {MODEL}")
    print("✅ Hugging Face Inference API configured!")
    print("="*70 + "\n")
    OFFLINE_MODE = False

app = FastAPI(title="Study Copilot API - Hugging Face", version="1.0.0")

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

def call_huggingface_api(prompt: str) -> str:
    """
    Call Hugging Face Inference API
    Free tier available at huggingface.co
    """
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1000,
            "temperature": 0.7,
        }
    }
    
    try:
        print("📡 Calling Hugging Face API...")
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{MODEL}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Hugging Face API Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, list) and len(data) > 0:
            if 'generated_text' in data[0]:
                return data[0]['generated_text']
        elif isinstance(data, dict) and 'generated_text' in data:
            return data['generated_text']
        
        print(f"Unexpected response format: {data}")
        return None
    
    except requests.exceptions.Timeout:
        print("❌ Hugging Face API timeout")
        return None
    except Exception as e:
        print(f"❌ Error calling Hugging Face: {e}")
        return None

def generate_cards_with_ai(topic: str, difficulty: str, num_cards: int) -> List[dict]:
    """
    Use Hugging Face to generate study cards
    """
    
    if OFFLINE_MODE:
        print(f"📖 OFFLINE MODE: Using fallback cards for '{topic}'")
        return get_fallback_cards(topic)
    
    prompt = f"""Generate exactly {num_cards} study cards for the topic: "{topic}" at {difficulty} level.

Create a mix of different card types:
1. Concept explanation cards
2. Code example cards
3. Quiz cards (multiple choice with 4 options)
4. Key takeaway cards
5. Practice challenge cards

Return ONLY a JSON array (NO markdown, NO text before/after):
[
  {{"type": "concept", "title": "What is [Topic]?", "content": "Clear explanation..."}},
  {{"type": "code", "title": "Simple Example", "content": "Explanation", "code_example": "# code here"}},
  {{"type": "quiz", "title": "Test", "content": "Question?", "quiz_options": [{{"option": "A", "text": "Answer", "correct": true}}, ...]}},
  {{"type": "takeaway", "title": "Key Points", "content": "1. Point one\\n2. Point two"}},
  {{"type": "challenge", "title": "Challenge", "content": "Exercise description"}}
]"""

    try:
        print(f"🤖 Generating {num_cards} cards for '{topic}' ({difficulty})...")
        
        response_text = call_huggingface_api(prompt)
        
        if not response_text:
            print("❌ No response from Hugging Face")
            return get_fallback_cards(topic)
        
        print(f"✅ Received response (length: {len(response_text)} chars)")
        
        # Extract JSON from response
        # The model might add extra text, so we need to find the JSON
        if "[" in response_text and "]" in response_text:
            json_start = response_text.index("[")
            json_end = response_text.rindex("]") + 1
            response_text = response_text[json_start:json_end]
        
        cards = json.loads(response_text.strip())
        
        # Add IDs and timestamps
        for i, card in enumerate(cards):
            card['id'] = f"{topic.replace(' ', '_')}_{i}_{datetime.now().timestamp()}"
            card['timestamp'] = datetime.now().isoformat()
        
        print(f"✅ Successfully generated {len(cards)} cards")
        return cards
    
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return get_fallback_cards(topic)
    except Exception as e:
        print(f"❌ Error: {e}")
        return get_fallback_cards(topic)

def get_fallback_cards(topic: str) -> List[dict]:
    """Fallback cards if AI fails"""
    return [
        {
            "id": f"{topic}_concept_0",
            "type": "concept",
            "title": f"Introduction to {topic}",
            "content": f"Welcome to {topic}! This is a placeholder. Ensure HUGGINGFACE_API_KEY is set.",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": f"{topic}_code_1",
            "type": "code",
            "title": "Sample Code",
            "content": "Example code",
            "code_example": f"# {topic} example\nprint('Hello {topic}!')",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": f"{topic}_quiz_2",
            "type": "quiz",
            "title": "Quiz",
            "content": f"What is {topic}?",
            "quiz_options": [
                {"option": "A", "text": "Option 1", "correct": False},
                {"option": "B", "text": "Correct", "correct": True},
                {"option": "C", "text": "Option 3", "correct": False},
                {"option": "D", "text": "Option 4", "correct": False}
            ],
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": f"{topic}_takeaway_3",
            "type": "takeaway",
            "title": "Key Points",
            "content": f"Key concepts:\n1. Concept 1\n2. Concept 2\n3. Concept 3",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": f"{topic}_challenge_4",
            "type": "challenge",
            "title": "Challenge",
            "content": f"Apply {topic} in a real-world scenario!",
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
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

def generate_cards_from_notes(notes_text: str, title: str) -> List[dict]:
    """Generate cards from notes"""
    
    if OFFLINE_MODE:
        return get_fallback_cards(title)
    
    prompt = f"""From these notes titled "{title}":

{notes_text[:2000]}

Generate 5-7 study cards mixing: concepts, code examples, quizzes, takeaways, challenges.
Return ONLY JSON: [{{"type": "concept", "title": "...", "content": "..."}}]"""

    try:
        print(f"🤖 Generating cards from: {title}...")
        response_text = call_huggingface_api(prompt)
        
        if not response_text:
            return get_fallback_cards(title)
        
        # Extract JSON
        if "[" in response_text:
            json_start = response_text.index("[")
            json_end = response_text.rindex("]") + 1
            response_text = response_text[json_start:json_end]
        
        cards = json.loads(response_text.strip())
        
        for i, card in enumerate(cards):
            card['id'] = f"{title.replace(' ', '_')}_{i}_{datetime.now().timestamp()}"
            card['timestamp'] = datetime.now().isoformat()
        
        return cards
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return get_fallback_cards(title)

# ============= API ENDPOINTS =============

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "running",
        "app": "Study Copilot API",
        "ai_provider": "Hugging Face (Free Models)",
        "model": MODEL,
        "offline_mode": OFFLINE_MODE,
        "message": "Set HUGGINGFACE_API_KEY to enable" if OFFLINE_MODE else "✅ Connected!"
    }

@app.post("/api/generate-cards")
async def generate_cards(request: GenerateCardsRequest):
    """Generate cards"""
    try:
        cards = generate_cards_with_ai(request.topic, request.difficulty, request.num_cards)
        
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
            "offline_mode": OFFLINE_MODE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload PDF"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="PDF only")
    
    try:
        content = await file.read()
        text = process_pdf_text(content)
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
            "source_file": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-notes")
async def upload_notes(request: UploadNotesRequest):
    """Upload notes"""
    try:
        cards = generate_cards_from_notes(request.text_content, request.title)
        
        session_id = f"notes_session_{datetime.now().timestamp()}"
        study_sessions[session_id] = {
            "title": request.title,
            "cards": cards,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "cards": cards
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check-answer")
async def check_answer(request: QuizAnswerRequest):
    """Check quiz answer"""
    for session in study_sessions.values():
        for card in session['cards']:
            if card['id'] == request.card_id and card['type'] == 'quiz':
                correct = next((o for o in card['quiz_options'] if o['correct']), None)
                is_correct = correct['option'] == request.selected_answer
                
                user_progress['quizzes_attempted'] += 1
                if is_correct:
                    user_progress['quizzes_correct'] += 1
                
                return {
                    "correct": is_correct,
                    "correct_answer": correct['option'],
                    "explanation": f"Correct: {correct['option']}"
                }
    
    raise HTTPException(status_code=404, detail="Card not found")

@app.post("/api/bookmark/{card_id}")
async def bookmark_card(card_id: str):
    """Bookmark card"""
    if card_id not in user_progress['bookmarks']:
        user_progress['bookmarks'].append(card_id)
    
    return {
        "success": True,
        "bookmarked": True,
        "total_bookmarks": len(user_progress['bookmarks'])
    }

@app.get("/api/progress")
async def get_progress():
    """Get progress"""
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
    """Get sessions"""
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
    """Get session"""
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="Not found")
    return study_sessions[session_id]

if __name__ == "__main__":
    import uvicorn
    
    print(f"Server: http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
