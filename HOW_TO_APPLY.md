# Study Copilot Working Fix Pack

This pack fixes the main backend blockers I found in the live repo.

## What this replaces

- `backend/main.py`
- `backend/requirements.txt`
- `backend/.env.example`

It also adds:

- `test_gemini_api.py`
- `VERIFY_STUDY_COPILOT.md`

## How to apply

From Git Bash, place this folder beside your cloned repo, then run:

```bash
bash apply-study-copilot-working-fixes.sh /path/to/study-copilot
```

Example:

```bash
bash apply-study-copilot-working-fixes.sh ~/Documents/study-copilot
```

Then verify:

```bash
cd ~/Documents/study-copilot
python -m venv venv
source venv/Scripts/activate  # Git Bash on Windows
pip install -r backend/requirements.txt
python -m py_compile backend/main.py
python backend/main.py
```

Open:

```text
http://localhost:8000
http://localhost:8000/docs
```

Then open `study-copilot-full.html` in your browser.
