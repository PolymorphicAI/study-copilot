#!/usr/bin/env bash
set -e

TARGET_REPO="$1"

if [ -z "$TARGET_REPO" ]; then
  echo "Usage: bash apply-study-copilot-working-fixes.sh /path/to/study-copilot"
  exit 1
fi

if [ ! -d "$TARGET_REPO" ]; then
  echo "Target repo folder not found: $TARGET_REPO"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$TARGET_REPO/backend"

cp "$SCRIPT_DIR/backend/main.py" "$TARGET_REPO/backend/main.py"
cp "$SCRIPT_DIR/backend/requirements.txt" "$TARGET_REPO/backend/requirements.txt"
cp "$SCRIPT_DIR/backend/.env.example" "$TARGET_REPO/backend/.env.example"
cp "$SCRIPT_DIR/test_gemini_api.py" "$TARGET_REPO/test_gemini_api.py"
cp "$SCRIPT_DIR/VERIFY_STUDY_COPILOT.md" "$TARGET_REPO/VERIFY_STUDY_COPILOT.md"

echo "Applied Study Copilot backend fixes to: $TARGET_REPO"
echo ""
echo "Next:"
echo "cd "$TARGET_REPO""
echo "python -m venv venv"
echo "source venv/Scripts/activate"
echo "pip install -r backend/requirements.txt"
echo "python -m py_compile backend/main.py"
echo "python backend/main.py"
