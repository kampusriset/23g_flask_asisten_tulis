from flask import Blueprint, render_template, session, redirect, url_for
from app.models.user import User
from app.models.notes import Note
from app.models.rapat import Rapat
from datetime import datetime, date, timedelta
from sqlalchemy import or_
from flask import request


search_bp = Blueprint('search_bp', __name__)
# --------------------------
# SEARCH MODAL (partial)
# --------------------------


@search_bp.route("/search")
def search_modal():
    # Require login like other pages
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    user = User.query.get(user_id)

    # Hitung batas hari ini (UTC-based, consistent with Note.created_at default)
    today = date.today()
    start_dt = datetime(today.year, today.month, today.day)
    end_dt = start_dt + timedelta(days=1)

    notes_today = Note.query.filter(
        Note.user_id == user_id,
        Note.deleted_at.is_(None),
        Note.created_at >= start_dt,
        Note.created_at < end_dt
    ).order_by(Note.updated_at.desc()).all()

    rapats_today = Rapat.query.filter(Rapat.tanggal == today).all()

    return render_template("view/fitur/search/search.html", user=user, notes_today=notes_today, rapats_today=rapats_today)


@search_bp.route("/datasearch")
def data_search():
    user_id = session.get("user_id")
    if not user_id:
        return ""

    q = request.args.get("q", "").strip()

    notes = []
    rapats = []

    if q:
        notes = Note.query.filter(
            Note.user_id == user_id,
            Note.deleted_at.is_(None),
            or_(
                Note.title.ilike(f"%{q}%"),
                Note.content.ilike(f"%{q}%")
            )
        ).order_by(Note.updated_at.desc()).all()

        rapats = Rapat.query.filter(
            or_(
                Rapat.topik.ilike(f"%{q}%"),
                Rapat.catatan.ilike(f"%{q}%"),
                Rapat.peserta.ilike(f"%{q}%")
            )
        ).order_by(Rapat.tanggal.desc()).all()

    return render_template(
        "view/fitur/search/search_result.html",
        notes_today=notes,
        rapats_today=rapats,
        query=q
    )
