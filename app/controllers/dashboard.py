from flask import Blueprint, render_template, session, redirect, url_for
from app.models.user import User
from app.models.notes import Note
from app.models.rapat import Rapat
from datetime import datetime

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
    # Ambil daftar notes untuk sidebar/dashboard
    notes = Note.query.filter(
        Note.user_id == user_id,
        Note.deleted_at.is_(None)
    ).order_by(Note.updated_at.desc()).all()
    # Greeting berdasarkan jam lokal server
    hour = datetime.now().hour
    if 5 <= hour < 11:
        greet = "Selamat Pagi"
    elif 11 <= hour < 17:
        greet = "Selamat Siang"
    elif 17 <= hour < 20:
        greet = "Selamat Sore"
    else:
        greet = "Selamat Malam"

    # Ambil nama singkat dari username
    name = (user.username.split('@')
            [0].split('.')[0].capitalize() if user and user.username else "")
    greeting = f"{greet}, {name}" if name else greet
    # Ambil daftar rapat terbaru (maks 6)
    from sqlalchemy import desc
    rapats = Rapat.query.order_by(desc(Rapat.tanggal)).limit(6).all()

    return render_template("view/dashboard.html", user=user, notes=notes, rapats=rapats, greeting=greeting, title="Beranda")


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
