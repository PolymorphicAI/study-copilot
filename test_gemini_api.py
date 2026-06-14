"""
Simple Gemini configuration diagnostic for Study Copilot.
Run from the repository root after setting GOOGLE_API_KEY.
"""

import os
import sys

try:
    import google.generativeai as genai
except ImportError:
    print("google-generativeai is not installed. Run: pip install -r backend/requirements.txt")
    sys.exit(1)


def main() -> int:
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("GOOGLE_API_KEY is not set.")
        print("Create backend/.env or export GOOGLE_API_KEY before running this check.")
        return 1

    try:
        genai.configure(api_key=api_key)
        models = list(genai.list_models())
        usable = [
            model.name
            for model in models
            if "generateContent" in getattr(model, "supported_generation_methods", [])
        ]

        if not usable:
            print("Gemini key is configured, but no generateContent-capable models were found.")
            return 1

        print("Gemini configuration looks okay.")
        print("Available generateContent models:")
        for model_name in usable:
            print(f"- {model_name}")

        return 0
    except Exception as exc:
        print(f"Gemini check failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
