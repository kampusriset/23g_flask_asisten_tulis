from flask import Blueprint, request, jsonify, session
from app import db
from app.models.chat_history import ChatHistory
from app.models.setting import UserSetting
from app.ai_engine import call_ai

ai_chat_bp = Blueprint("ai_chat", __name__)

# ============================
# CHAT SYSTEM PROMPT
# ============================

CHAT_SYSTEM_PROMPT = """
Kamu adalah AI yang menjawab dengan sangat singkat, padat, dan langsung ke inti.
Jawaban maksimal 2–3 kalimat.
Jangan basa-basi.
Jawab hanya sesuai pertanyaan.
Hemat token.
"""

# ============================
# CHAT API
# ============================


@ai_chat_bp.route("/api/ai-chat", methods=["POST"])
def ai_chat():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    # ambil provider user
    setting = UserSetting.query.filter_by(user_id=user_id).first()
    ALLOWED_PROVIDERS = {"gemini", "openai", "groq", "deepseek"}

    provider = (setting.ai_provider if setting else "gemini")
    provider = provider.lower().strip()

    if provider not in ALLOWED_PROVIDERS:
        provider = "gemini"

    print("PROVIDER DARI DB =", repr(provider))

    # gabung system prompt + user message
    final_prompt = f"{CHAT_SYSTEM_PROMPT}\n\nUser:\n{user_message}"

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


# ============================
# CHAT HISTORY
# ============================

@ai_chat_bp.route("/api/ai-chat-history", methods=["GET", "DELETE"])
def ai_chat_history():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"history": []}) if request.method == "GET" else (
            jsonify({"error": "User not logged in"}), 401
        )

    if request.method == "GET":
        history = ChatHistory.query.filter_by(user_id=user_id)\
            .order_by(ChatHistory.created_at.asc()).all()

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


# ============================
# GENERIC AI QUERY
# ============================

@ai_chat_bp.route("/ai/query", methods=["POST"])
def ai_query():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    setting = UserSetting.query.filter_by(user_id=user_id).first()
    provider = setting.ai_provider if setting else "gemini"

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
