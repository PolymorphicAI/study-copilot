# Study Copilot Setup & Installation Guide 🛠️

Follow this step-by-step guide to set up the Study Copilot platform on your local machine.

---

## 📌 Prerequisites

Before starting, ensure you have the following installed:
- **Python**: Version 3.8 or higher.
- **Web Browser**: Any modern web browser (Google Chrome, Firefox, Microsoft Edge, Safari).

---

## 🔑 Step 1: Get a Google Gemini API Key

1. Go to the [Google AI Studio (formerly Makersuite)](https://aistudio.google.com/).
2. Log in using your Google account.
3. Click **Create API Key**.
4. Copy the generated API key (it will begin with `AIzaSy`).

---

## 💻 Step 2: Backend Setup

### 1. Open the terminal
Open your terminal (Command Prompt/PowerShell on Windows, Terminal on macOS/Linux) and navigate to the project directory:
```bash
# Navigate to the Study Copilot folder
cd "path/to/Study Copilot"
```

### 2. Create a Python Virtual Environment
Creating a virtual environment isolates dependencies for this project:
- **Windows**:
  ```powershell
  python -m venv venv
  venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
Run the command below to install FastAPI, PyPDF2, Gemini integrations, and related packages:
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables
1. Go to the `backend/` directory.
2. Duplicate or rename `.env.example` to `.env`.
3. Open `.env` in a text editor and add your Gemini API Key:
   ```env
   GOOGLE_API_KEY=AIzaSyYourActualKeyGoesHere
   PORT=8000
   ```

---

## 🚀 Step 3: Run the Application

### 1. Start the FastAPI Server
With your virtual environment active, run:
```bash
# From the root directory:
python backend/main.py
```
Or run directly through uvicorn:
```bash
cd backend
uvicorn main:app --reload --port 8000
```
You should see output indicating that the backend server is running:
`INFO:     Uvicorn server running on http://0.0.0.0:8000 (Press CTRL+C to quit)`

*Note: You can verify the API is running by opening `http://localhost:8000/docs` in your browser to view the interactive API swagger documentation.*

### 2. Open the Frontend Application
1. Double-click or open `study-copilot-full.html` in your browser.
2. Look at the top right of the page: you should see a green status dot with **"Gemini Online"** (or **"Sandbox Mode"** if running locally without a key).
3. Type in a topic, choose a difficulty, and click **Start Learning**!

---

## 🔧 Troubleshooting

### 1. "Backend Offline" indicator in the browser
- Check if your FastAPI terminal process crashed. If so, restart it with `python backend/main.py`.
- Ensure the server is listening on port `8000` (the default port the frontend queries). If running on another port, change the `PORT` env variable.
- Check for CORS blocks. By default, CORS is set to allow all origins `["*"]` in `main.py`.

### 2. Cards loading but showing "Offline Sandbox Mode"
- This means your API key is missing or invalid. Check that the `.env` file exists in the `backend/` folder and contains `GOOGLE_API_KEY=AIzaSy...` (without spaces around the `=` sign).
- Restart the FastAPI server after changing the `.env` file for the new configuration to load.

### 3. PDF Upload fails or crashes
- Ensure the file you are uploading is a valid, readable PDF. Scan/OCR-less image-only PDFs may not extract text successfully using `PyPDF2`.
- Large PDF documents are automatically truncated at 15,000 characters by the backend to avoid exceeding the prompt limits of Gemini's context model.

### 4. Keyboard controls are not working
- Click anywhere on the webpage body outside of input textareas or input text forms. Focus needs to be on the document body for keydown event listeners to trigger.
