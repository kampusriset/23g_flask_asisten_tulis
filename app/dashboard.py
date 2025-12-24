from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from .models import User

dashboard_bp = Blueprint('dashboard_bp', __name__)

# --------------------------
# DASHBOARD PAGE
# --------------------------


@dashboard_bp.route("/dashboard")
def dashboard():
    # Cek user login
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    # Ambil data user
    user = User.query.get(user_id)
    return render_template("view/dashboard.html", user=user, title="Dashboard")


# --------------------------
# FITUR BELUM TERSEDIA
# --------------------------
@dashboard_bp.route("/not-available")
def not_available():
    # Cek apakah user login
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    # Ambil data user
    user = User.query.get(user_id)
    return render_template("view/not_available.html", user=user, title="Fitur Belum Tersedia")


@dashboard_bp.route("/ai")
def ai():
    # Cek apakah user login
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    user = User.query.get(user_id)
    return render_template("view/ai.html", user=user, title="AI Assistant")


@dashboard_bp.route("/ai/query", methods=["POST"])
def ai_query():
    # Cek apakah user login
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "not_authenticated"}), 401

    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "invalid_prompt"}), 400

    # Simple mock responder for development
    def generate_mock_reply(text: str) -> str:
        low = text.lower()
        if "pagi" in low and ("saran" in low or "tips" in low):
            return "Berikut beberapa saran pagi: 1) Bangun lebih awal; 2) Minum air; 3) Tulis 3 tugas prioritas."
        if "ringkas" in low or "ringkasan" in low:
            return "(Mock) Untuk merangkum, kirim teks yang ingin diringkas setelah kata 'Ringkas:'"
        if "terjemah" in low or "translate" in low:
            return "(Mock) Untuk menerjemahkan, kirim 'Terjemah: <teks>'"
        if "grammar" in low or "perbaiki" in low or "tata bahasa" in low:
            return "(Mock) Kirim kalimat yang ingin diperbaiki setelah kata 'Perbaiki:'"
        return "[Mock] Saya menerima prompt Anda: " + text

    reply = generate_mock_reply(prompt)
    return jsonify({"reply": reply, "provider": "mock"})
