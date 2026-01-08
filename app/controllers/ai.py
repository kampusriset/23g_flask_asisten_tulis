from dotenv import load_dotenv
import requests
import os
from flask import Blueprint, request, jsonify, session

load_dotenv()

ai_bp = Blueprint("ai_bp", __name__, url_prefix="/ai")

# 🔑 Gemini API key + endpoint
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}'


@ai_bp.route("/summarize", methods=["POST"])
def ai_summarize():
    if not session.get("user_id"):
        return jsonify({"summary": ""}), 401

    data = request.get_json() or {}
    text = data.get("text", "").strip()

    if len(text) < 20:
        return jsonify({"summary": ""})

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Ringkas teks berikut menjadi ringkasan yang singkat, jelas, "
                            "dan mudah dipahami.\n"
                            "- Gunakan bahasa Indonesia\n"
                            "- Jangan menambah informasi baru\n"
                            "- Fokus ke inti\n\n"
                            f"Teks:\n{text}\n\n"
                            "Ringkasan:"
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 800,
            "topP": 0.9
        }
    }

    try:
        response = requests.post(GEMINI_API_URL, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()

        summary = ""
        candidates = result.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                summary = parts[0].get("text", "").strip()

        return jsonify({"summary": summary})

    except Exception as e:
        print("Gemini AI Tool ERROR:", e)
        return jsonify({"summary": ""})
