import os
import requests
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from app import db
from app.models.chat_history import ChatHistory
from app.models.setting import UserSetting
from dotenv import load_dotenv

load_dotenv()

gemini_bp = Blueprint('gemini', __name__)

# ============================
# API KEYS
# ============================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1/models/"
    f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
)

# ============================
# AI ROUTER
# ============================


def call_ai(provider, prompt):

    try:
        # ================= GEMINI =================
        if provider == "gemini":
            if not GEMINI_API_KEY:
                return "Model saat ini masih belum tersedia."

            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }

            r = requests.post(GEMINI_API_URL, json=payload, timeout=60)
            r.raise_for_status()

            data = r.json()
            return data.get("candidates", [{}])[0] \
                .get("content", {}).get("parts", [{}])[0].get("text", "")

        # ================= OPENAI =================
        if provider == "openai":
            if not OPENAI_API_KEY:
                return "Model saat ini masih belum tersedia."

            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            r.raise_for_status()

            return r.json()["choices"][0]["message"]["content"]

        # ================= GROQ =================
        if provider == "groq":
            if not GROQ_API_KEY:
                return "Model saat ini masih belum tersedia."

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            r.raise_for_status()

            return r.json()["choices"][0]["message"]["content"]

        # ================= DEEPSEEK =================
        if provider == "deepseek":
            if not DEEPSEEK_API_KEY:
                return "Model saat ini masih belum tersedia."

            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            r = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            r.raise_for_status()

            return r.json()["choices"][0]["message"]["content"]

        return "Model saat ini masih belum tersedia."

    except Exception:
        # 🔥 SEMUA ERROR MASUK SINI
        return "Model saat ini masih belum tersedia."


# ============================
# CHAT API
# ============================

# ============================
# CHAT AI SYSTEM PROMPT
# ============================

CHAT_SYSTEM_PROMPT = """
Kamu adalah AI yang menjawab dengan sangat singkat, padat, dan langsung ke inti.
Jawaban maksimal 2–3 kalimat.
Jangan basa-basi.
Jawab hanya sesuai pertanyaan.
Hemat token.
"""


@gemini_bp.route("/api/ai-chat", methods=["POST"])
@gemini_bp.route("/api/ai-chat", methods=["POST"])
def ai_chat():
    data = request.get_json() or {}
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    # 🔥 ambil provider user
    setting = UserSetting.query.filter_by(user_id=user_id).first()
    provider = setting.ai_provider if setting else "gemini"

    # 🔥 PROMPT KHUSUS CHAT AI (bukan global)
    final_prompt = (
        CHAT_SYSTEM_PROMPT
        + "\n\nUser:\n"
        + user_message
    )

    try:
        ai_text = call_ai(provider, final_prompt)

        chat = ChatHistory(
            user_id=user_id,
            user_input=user_message,
            ai_output=ai_text
        )
        db.session.add(chat)
        db.session.commit()

        return jsonify({
            "reply": ai_text,
            "provider": provider
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================
# CHAT HISTORY
# ============================

@gemini_bp.route("/api/ai-chat-history", methods=["GET", "DELETE"])
def ai_chat_history():
    user_id = session.get("user_id")

    if not user_id:
        if request.method == "GET":
            return jsonify({"history": []})
        return jsonify({"error": "User not logged in"}), 401

    if request.method == "GET":
        history = ChatHistory.query.filter_by(user_id=user_id).order_by(
            ChatHistory.created_at.asc()
        ).all()

        return jsonify({
            "history": [
                {
                    "user_input": h.user_input,
                    "ai_output": h.ai_output,
                    "created_at": h.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }
                for h in history
            ]
        })

    ChatHistory.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"message": "Chat history deleted"})


@gemini_bp.route("/ai/query", methods=["POST"])
def ai_query():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json() or {}
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    setting = UserSetting.query.filter_by(user_id=user_id).first()
    provider = setting.ai_provider if setting else "gemini"

    try:
        ai_text = call_ai(provider, prompt)

        chat = ChatHistory(
            user_id=user_id,
            user_input=prompt,
            ai_output=ai_text
        )
        db.session.add(chat)
        db.session.commit()

        return jsonify({
            "reply": ai_text,
            "provider": provider
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
