from flask import jsonify, request
from sqlalchemy import func, extract
from sqlalchemy import desc
from flask import Blueprint, render_template, session, redirect, url_for
import calendar
from app.models.user import User
from app.models.notes import Note
from app.models.rapat import Rapat
from datetime import datetime, date, timedelta

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
    elif 11 <= hour < 15:
        greet = "Selamat Siang"
    elif 15 <= hour < 18:
        greet = "Selamat Sore"
    else:
        greet = "Selamat Malam"

    # Ambil nama singkat dari username
    name = (user.username.split('@')
            [0].split('.')[0].capitalize() if user and user.username else "")
    greeting = f"{greet}, {name}" if name else greet

    # Ambil daftar rapat terbaru (maks 6) sesuai user yang login
    rapats = Rapat.query.filter(
        Rapat.user_id == user_id
    ).order_by(desc(Rapat.tanggal)).limit(6).all()

    return render_template(
        "view/dashboard.html",
        user=user,
        notes=notes,
        rapats=rapats,
        greeting=greeting,
        title="Beranda"
    )


@dashboard_bp.route("/dashboard/chart-data")
def chart_data():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    filter_type = request.args.get("filter", "weekly")
    year = int(request.args.get("year", datetime.now().year))
    month = int(request.args.get("month", datetime.now().month))

    labels = []
    notes_data = []
    rapat_data = []

    # ======================
    # WEEKLY (7 hari)
    # ======================
    if filter_type == "weekly":
        today = date.today()
        start_date = today - timedelta(days=6)

        labels = [
            (start_date + timedelta(days=i)).strftime("%d %b")
            for i in range(7)
        ]

        notes = (
            Note.query
            .filter(
                Note.user_id == user_id,
                Note.deleted_at.is_(None),
                func.date(Note.created_at) >= start_date
            )
            .with_entities(func.date(Note.created_at), func.count())
            .group_by(func.date(Note.created_at))
            .all()
        )

        rapats = (
            Rapat.query
            .filter(
                Rapat.user_id == user_id,
                func.date(Rapat.created_at) >= start_date
            )
            .with_entities(func.date(Rapat.created_at), func.count())
            .group_by(func.date(Rapat.created_at))
            .all()
        )

        notes_dict = {d.strftime("%d %b"): c for d, c in notes}
        rapat_dict = {d.strftime("%d %b"): c for d, c in rapats}

        notes_data = [notes_dict.get(l, 0) for l in labels]
        rapat_data = [rapat_dict.get(l, 0) for l in labels]

    # ======================
    # MONTHLY (per hari)
    # ======================
    elif filter_type == "monthly":
        days_in_month = calendar.monthrange(year, month)[1]
        labels = [str(i) for i in range(1, days_in_month + 1)]

        notes = (
            Note.query
            .filter(
                Note.user_id == user_id,
                extract("year", Note.created_at) == year,
                extract("month", Note.created_at) == month,
                Note.deleted_at.is_(None)
            )
            .with_entities(extract("day", Note.created_at), func.count())
            .group_by(extract("day", Note.created_at))
            .all()
        )

        rapats = (
            Rapat.query
            .filter(
                Rapat.user_id == user_id,
                extract("year", Rapat.created_at) == year,
                extract("month", Rapat.created_at) == month
            )
            .with_entities(extract("day", Rapat.created_at), func.count())
            .group_by(extract("day", Rapat.created_at))
            .all()
        )

        notes_dict = {int(d): c for d, c in notes}
        rapat_dict = {int(d): c for d, c in rapats}

        notes_data = [notes_dict.get(i, 0)
                      for i in range(1, days_in_month + 1)]
        rapat_data = [rapat_dict.get(i, 0)
                      for i in range(1, days_in_month + 1)]

    # ======================
    # YEARLY (per bulan)
    # ======================
    elif filter_type == "yearly":
        labels = [
            "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
            "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
        ]

        notes = (
            Note.query
            .filter(
                Note.user_id == user_id,
                extract("year", Note.created_at) == year,
                Note.deleted_at.is_(None)
            )
            .with_entities(extract("month", Note.created_at), func.count())
            .group_by(extract("month", Note.created_at))
            .all()
        )

        rapats = (
            Rapat.query
            .filter(
                Rapat.user_id == user_id,
                extract("year", Rapat.created_at) == year
            )
            .with_entities(extract("month", Rapat.created_at), func.count())
            .group_by(extract("month", Rapat.created_at))
            .all()
        )

        notes_dict = {int(m): c for m, c in notes}
        rapat_dict = {int(m): c for m, c in rapats}

        notes_data = [notes_dict.get(i, 0) for i in range(1, 13)]
        rapat_data = [rapat_dict.get(i, 0) for i in range(1, 13)]

    return jsonify({
        "labels": labels,
        "notes": notes_data,
        "rapat": rapat_data
    })


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
