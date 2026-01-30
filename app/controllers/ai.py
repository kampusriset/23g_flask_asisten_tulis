from dotenv import load_dotenv
import os
import requests
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from app.models.setting import UserSetting
from app.ai_engine import call_ai

load_dotenv()

ai_bp = Blueprint("ai_bp", __name__, url_prefix="/ai")


@ai_bp.route("/", methods=["GET"])
def ai_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    # Ambil provider dari DB
    setting = UserSetting.query.filter_by(user_id=user_id).first()
    active_provider = setting.ai_provider.capitalize(
    ) if setting and setting.ai_provider else "tidak tersedia"

    return render_template(
        "view/fitur/AI/ai.html",  # pastikan ai.html di templates/fitur/AI/
        title="AI Tools",
        active_provider=active_provider
    )


# =========================
# helper ambil provider
# =========================
def get_provider():
    setting = UserSetting.query.filter_by(
        user_id=session.get("user_id")
    ).first()

    return setting.ai_provider if setting else "gemini"


# =========================
# GRAMMAR
# =========================
@ai_bp.route("/grammar", methods=["POST"])
def ai_grammar():
    if not session.get("user_id"):
        return jsonify({"grammar": ""}), 401

    text = (request.get_json() or {}).get("text", "").strip()
    if len(text) < 2:
        return jsonify({"grammar": ""})

    prompt = f"""
Cek dan perbaiki grammar, ejaan, dan struktur kalimat.
Deteksi bahasa otomatis.
Jika sudah benar, tampilkan teks aslinya.

Jawab hanya hasil akhir, tanpa penjelasan.

Teks:
{text}
"""

    provider = get_provider()
    result = call_ai(provider, prompt)

    return jsonify({"grammar": result})


# =========================
# SUMMARIZE
# =========================
@ai_bp.route("/summarize", methods=["POST"])
def ai_summarize():
    if not session.get("user_id"):
        return jsonify({"summary": ""}), 401

    text = (request.get_json() or {}).get("text", "").strip()
    if len(text) < 20:
        return jsonify({"summary": ""})

    prompt = f"""
Ringkas teks berikut:

- Bahasa Indonesia
- Singkat
- Jelas
- Fokus inti
- Jangan menambah informasi baru

Teks:
{text}

Ringkasan:
"""

    provider = get_provider()
    result = call_ai(provider, prompt)

    return jsonify({"summary": result})


# =========================
# TRANSLATE
# =========================
@ai_bp.route("/translate", methods=["POST"])
def ai_translate():
    if not session.get("user_id"):
        return jsonify({"translation": ""}), 401

    data = request.get_json() or {}
    text = data.get("text", "").strip()
    target = data.get("target_lang", "en")

    if len(text) < 2:
        return jsonify({"translation": ""})

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

    lang = lang_map.get(target, "English")

    prompt = f"""
Terjemahkan teks berikut ke bahasa {lang}.

- Jangan ubah makna
- Jangan beri penjelasan
- Jawab hanya hasil terjemahan

Teks:
{text}

Terjemahan:
"""

    provider = get_provider()
    result = call_ai(provider, prompt)

    return jsonify({"translation": result})
