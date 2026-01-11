from dotenv import load_dotenv
import requests
import os
from flask import Blueprint, request, jsonify, session

# 🔑 Gemini API key + endpoint
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}'
load_dotenv()

ai_bp = Blueprint("ai_bp", __name__, url_prefix="/ai")

# --- GRAMMAR ENDPOINT ---
@ai_bp.route("/grammar", methods=["POST"])
def ai_grammar():
    if not session.get("user_id"):
        return jsonify({"grammar": ""}), 401

    data = request.get_json() or {}
    text = data.get("text", "").strip()
    if not text or len(text) < 2:
        return jsonify({"grammar": ""})

    prompt = (
        "Cek dan perbaiki grammar, ejaan, dan struktur kalimat pada teks berikut. "
        "Deteksi bahasa secara otomatis. Jika sudah benar, tampilkan teks aslinya. Jangan terjemahkan ke bahasa lain, hanya perbaiki jika ada kesalahan. "
        "Jawab hanya dengan hasil perbaikan, tanpa penjelasan atau terjemahan.\n"
        f"Teks:\n{text}\n\nHasil perbaikan:"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 800,
            "topP": 0.9
        }
    }

    try:
        response = requests.post(GEMINI_API_URL, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()

        grammar = ""
        candidates = result.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                grammar = parts[0].get("text", "").strip()

        return jsonify({"grammar": grammar})

    except Exception as e:
        print("Gemini AI Grammar ERROR:", e)
        return jsonify({"grammar": ""})

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


# --- TRANSLATE ENDPOINT ---
@ai_bp.route("/translate", methods=["POST"])
def ai_translate():
    if not session.get("user_id"):
        return jsonify({"translation": ""}), 401

    data = request.get_json() or {}
    text = data.get("text", "").strip()
    target_lang = data.get("target_lang", "en").strip()

    if not text or len(text) < 2:
        return jsonify({"translation": ""})

    # Prompt Gemini untuk translate
    lang_map = {
        "en": "English",
        "id": "Indonesian",
        "ar": "Arabic",
        "zh": "Chinese",
        "ja": "Japanese",
        "fr": "French",
        "de": "German",
        "es": "Spanish",
        "ru": "Russian",
        "ko": "Korean",
        "it": "Italian",
        "tr": "Turkish",
        "th": "Thai",
        "ms": "Malay",
        "pt": "Portuguese"
    }
    lang_name = lang_map.get(target_lang, "English")

    prompt = (
        f"Terjemahkan teks berikut ke dalam bahasa {lang_name}.\n"
        "- Jangan ubah makna\n"
        "- Jawab hanya dengan hasil terjemahan, tanpa penjelasan\n"
        f"Teks:\n{text}\n\nTerjemahan:"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 800,
            "topP": 0.9
        }
    }

    try:
        response = requests.post(GEMINI_API_URL, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()

        translation = ""
        candidates = result.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                translation = parts[0].get("text", "").strip()

        return jsonify({"translation": translation})

    except Exception as e:
        print("Gemini AI Translate ERROR:", e)
        return jsonify({"translation": ""})
