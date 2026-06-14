"""
Study Copilot - AI-Powered Learning Platform
Main FastAPI Backend - Gemini Version with Model Detection
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
import os
from datetime import datetime
import json
import sys

# Check for API Key at startup
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("\n" + "="*70)
    print("⚠️  WARNING: GOOGLE_API_KEY not found!")
    print("="*70)
    print("\nTo enable Gemini AI features:")
    print("1. Get your API key from: https://makersuite.google.com/app/apikey")
    print("2. Set it in your terminal:")
    print("   export GOOGLE_API_KEY='your-key-here'")
    print("3. Restart this script")
    print("\nRunning in OFFLINE MODE with fallback cards.")
    print("="*70 + "\n")
    OFFLINE_MODE = True
    MODEL_NAME = None
else:
    print("\n✅ GOOGLE_API_KEY found! Configuring Gemini AI...")
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured successfully!")
        
        # List available models and find the best one
        print("\n📋 Checking available models...")
        available_models = []
        try:
            models = genai.list_models()
            for model in models:
                # Print available models
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
                    print(f"   ✓ {model.name}")
            
            # Select the best available model
            # Priority: gemini-2.0 > gemini-1.5-pro > gemini-1.5-flash > gemini-pro
            MODEL_NAME = None
            for preferred_model in [
                'models/gemini-2.0-flash',
                'models/gemini-1.5-pro',
                'models/gemini-1.5-flash',
                'models/gemini-pro',
            ]:
                if preferred_model in available_models:
                    MODEL_NAME = preferred_model
                    print(f"\n✅ Selected model: {MODEL_NAME}")
                    break
            
            if not MODEL_NAME and available_models:
                # Fallback to first available model
                MODEL_NAME = available_models[0]
                print(f"\n⚠️  Using available model: {MODEL_NAME}")
            
            if MODEL_NAME:
                OFFLINE_MODE = False
            else:
                print("\n❌ No compatible models found!")
                OFFLINE_MODE = True
                MODEL_NAME = None
        
        except Exception as e:
            print(f"⚠️  Could not list models: {e}")
            print("Trying fallback models...")
            # Try common models
            try:
                test_model = genai.GenerativeModel('gemini-pro')
                test_model.generate_content("test")
                MODEL_NAME = 'gemini-pro'
                OFFLINE_MODE = False
                print(f"✅ Using fallback model: {MODEL_NAME}")
            except:
                OFFLINE_MODE = True
                MODEL_NAME = None
            
    except Exception as e:
        print(f"⚠️  Error configuring Gemini: {e}")
        print("Running in OFFLINE MODE with fallback cards.")
        OFFLINE_MODE = True
        MODEL_NAME = None

app = FastAPI(title="Study Copilot API", version="1.0.0")

# CORS middleware to allow frontend requests
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

def generate_cards_with_ai(topic: str, difficulty: str, num_cards: int) -> List[dict]:
    """
    Use Gemini to generate study cards based on topic
    """
    
    if OFFLINE_MODE or not MODEL_NAME:
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
        print(f"   Using model: {MODEL_NAME}")
        
        # Use the detected model - remove 'models/' prefix if present
        model_name = MODEL_NAME.replace('models/', '')
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        response_text = response.text
        
        print(f"✅ Received response from Gemini (length: {len(response_text)} chars)")
        
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
    
    except Exception as e:
        print(f"❌ Error generating cards: {e}")
        print("   Returning fallback cards instead")
        return get_fallback_cards(topic)

def get_fallback_cards(topic: str) -> List[dict]:
    """Fallback cards if AI generation fails or offline mode"""
    return [
        {
            "id": f"{topic}_concept_0",
            "type": "concept",
            "title": f"Introduction to {topic}",
            "content": f"Welcome to {topic}! This is a placeholder card shown because the Gemini AI is currently unavailable. To see real AI-generated content, ensure your GOOGLE_API_KEY is properly set and your API has access to Gemini models.",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": f"{topic}_code_1",
            "type": "code",
            "title": "Sample Code",
            "content": "Here's an example of how to work with this topic",
            "code_example": f"# Example code for {topic}\nprint('Learning {topic}!')\n# Replace with real content when AI is available",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": f"{topic}_quiz_2",
            "type": "quiz",
            "title": "Quick Quiz",
            "content": f"What is {topic}?",
            "quiz_options": [
                {"option": "A", "text": "Definition or concept 1", "correct": False},
                {"option": "B", "text": "The correct definition", "correct": True},
                {"option": "C", "text": "Alternative definition", "correct": False},
                {"option": "D", "text": "Another alternative", "correct": False}
            ],
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": f"{topic}_takeaway_3",
            "type": "takeaway",
            "title": "Key Points",
            "content": f"Remember these key points about {topic}:\n1. First important concept\n2. Second important concept\n3. Third important concept",
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": f"{topic}_challenge_4",
            "type": "challenge",
            "title": "Practice Challenge",
            "content": f"Try to apply {topic} in a real-world scenario. Think about how you can use these concepts today!",
            "timestamp": datetime.now().isoformat()
        }
    ]

def process_pdf_text(file_content: bytes) -> str:
    """Extract text from PDF (using PyPDF2)"""
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
    """Generate study cards from user's notes using Gemini"""
    
    if OFFLINE_MODE or not MODEL_NAME:
        print(f"📖 OFFLINE MODE: Using fallback cards for notes")
        return get_fallback_cards(title)
    
    prompt = f"""You are a study assistant. I have these notes titled "{title}":

{notes_text[:3000]}  

Generate 5-7 engaging study cards from this content. Mix different types:
- Concept explanations for key ideas
- Code examples if there's any code
- Quiz questions to test understanding
- Key takeaways summarizing main points
- Practice challenges

Return ONLY valid JSON (NO markdown formatting), matching this structure:
[{{"type": "concept", "title": "...", "content": "..."}}, ...]"""

    try:
        print(f"🤖 Generating cards from notes: {title}...")
        model_name = MODEL_NAME.replace('models/', '')
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        response_text = response.text
        
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
    mode = "OFFLINE SANDBOX" if OFFLINE_MODE else "CONNECTED TO GEMINI"
    return {
        "status": "running",
        "app": "Study Copilot API",
        "version": "1.0.0",
        "ai_provider": "Google Gemini",
        "mode": mode,
        "model": MODEL_NAME,
        "offline_mode": OFFLINE_MODE,
        "message": "To unlock dynamic real-time AI study cards, please set your GOOGLE_API_KEY and ensure your API has access to Gemini models." if OFFLINE_MODE else "✅ Connected to Gemini AI!"
    }

@app.post("/api/generate-cards")
async def generate_cards(request: GenerateCardsRequest):
    """
    Generate study cards for a topic using Gemini
    """
    try:
        cards = generate_cards_with_ai(
            topic=request.topic,
            difficulty=request.difficulty,
            num_cards=request.num_cards
        )
        
        # Save to session
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
            "message": "⚠️ Offline mode - using fallback cards" if OFFLINE_MODE else "✅ Generated by Gemini AI"
        }
    
    except Exception as e:
        print(f"Error in /api/generate-cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF and generate study cards from it
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        print(f"📄 Processing PDF: {file.filename}")
        # Read PDF content
        content = await file.read()
        text = process_pdf_text(content)
        print(f"✅ Extracted {len(text)} characters from PDF")
        
        # Generate cards from extracted text
        cards = generate_cards_from_notes(text, file.filename)
        
        # Save session
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
        print(f"Error in /api/upload-pdf: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-notes")
async def upload_notes(request: UploadNotesRequest):
    """
    Generate cards from pasted text notes
    """
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
        print(f"Error in /api/upload-notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check-answer")
async def check_answer(request: QuizAnswerRequest):
    """
    Check if a quiz answer is correct
    """
    # Find the card
    for session in study_sessions.values():
        for card in session['cards']:
            if card['id'] == request.card_id:
                if card['type'] != 'quiz':
                    raise HTTPException(status_code=400, detail="Not a quiz card")
                
                # Check if answer is correct
                correct_option = None
                for option in card['quiz_options']:
                    if option['correct']:
                        correct_option = option
                        break
                
                is_correct = correct_option['option'] == request.selected_answer
                
                # Update progress
                user_progress['quizzes_attempted'] += 1
                if is_correct:
                    user_progress['quizzes_correct'] += 1
                
                return {
                    "correct": is_correct,
                    "correct_answer": correct_option['option'],
                    "explanation": f"The correct answer is {correct_option['option']}: {correct_option['text']}"
                }
    
    raise HTTPException(status_code=404, detail="Card not found")

@app.post("/api/bookmark/{card_id}")
async def bookmark_card(card_id: str):
    """Add card to bookmarks"""
    if card_id not in user_progress['bookmarks']:
        user_progress['bookmarks'].append(card_id)
    
    return {
        "success": True,
        "bookmarked": True,
        "total_bookmarks": len(user_progress['bookmarks'])
    }

@app.get("/api/progress")
async def get_progress():
    """Get user's study progress"""
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
    """Get all study sessions"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "topic": session.get('topic', session.get('title', 'Unknown')),
                "num_cards": len(session['cards']),
                "created_at": session['created_at'],
                "offline_mode": session.get('offline_mode', False)
            }
            for sid, session in study_sessions.items()
        ]
    }

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get specific study session"""
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return study_sessions[session_id]

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🎓 Study Copilot Backend Starting...")
    print("="*70)
    print(f"Mode: {'🔴 OFFLINE SANDBOX' if OFFLINE_MODE else '🟢 CONNECTED TO GEMINI'}")
    if MODEL_NAME:
        print(f"Model: {MODEL_NAME}")
    print(f"Server: http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)