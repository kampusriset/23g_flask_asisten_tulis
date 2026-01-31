from dotenv import load_dotenv
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from app.models.notes import Note
from app.models.setting import UserSetting
from app import db
from app.ai_engine import call_ai
from app.services.note_prompt_service import (
    note_suggest_prompt,
    note_summarize_prompt,
    note_summarize_bullet_prompt
)


load_dotenv()

notes_bp = Blueprint("notes_bp", __name__, url_prefix="/notes")


# =========================
# HELPERS
# =========================
def require_login():
    if not session.get("user_id"):
        return redirect(url_for("auth_bp.login"))
    return None


def get_user_notes(user_id):
    return Note.query.filter(
        Note.user_id == user_id,
        Note.deleted_at.is_(None)
    ).order_by(Note.updated_at.desc()).all()


def get_ai_provider():
    user_id = session.get("user_id")
    if not user_id:
        return "gemini"  # fallback default
    setting = UserSetting.query.filter_by(user_id=user_id).first()
    return setting.ai_provider if setting and setting.ai_provider else "gemini"


# =========================
# AI ROUTES
# =========================
@notes_bp.route('/<int:note_id>/suggest', methods=['POST'])
def note_suggest(note_id):
    if not session.get('user_id'):
        return jsonify({'suggestion': ''}), 401

    text = (request.get_json() or {}).get('text', '').strip()
    if len(text) < 3:
        return jsonify({'suggestion': ''})

    last_words = " ".join(text.split()[-3:])
    prompt = note_suggest_prompt(last_words)
    provider = get_ai_provider()
    suggestion = call_ai(provider, prompt, temperature=0.25, max_tokens=100)
    return jsonify({'suggestion': suggestion})


@notes_bp.route('/<int:note_id>/summarize', methods=['POST'])
def note_summarize(note_id):
    if not session.get('user_id'):
        return jsonify({'summary': ''}), 401

    text = (request.get_json() or {}).get('text', '').strip()
    if len(text) < 20:
        return jsonify({'summary': ''})

    prompt = note_summarize_prompt(text)
    provider = get_ai_provider()
    summary = call_ai(provider, prompt, temperature=0.3, max_tokens=2000)
    return jsonify({'summary': summary})


@notes_bp.route('/<int:note_id>/summarize-bullet', methods=['POST'])
def note_summarize_bullet(note_id):
    if not session.get('user_id'):
        return jsonify({'summary': ''}), 401

    text = (request.get_json() or {}).get('text', '').strip()
    if len(text) < 20:
        return jsonify({'summary': ''})

    prompt = note_summarize_bullet_prompt(text)
    provider = get_ai_provider()
    bullet_summary = call_ai(
        provider, prompt, temperature=0.25, max_tokens=2000)
    return jsonify({'summary': bullet_summary})


# =========================
# NOTES HOME
# =========================
@notes_bp.route("/")
def index():
    check = require_login()
    if check:
        return check

    user_id = session["user_id"]
    notes = get_user_notes(user_id)

    if not notes:
        return render_template("view/fitur/notes/empty.html", title="Empty")

    return redirect(url_for("notes_bp.edit", note_id=notes[0].id))


# =========================
# EDIT / VIEW CATATAN
# =========================
@notes_bp.route("/<int:note_id>", methods=["GET", "POST"])
def edit(note_id):
    check = require_login()
    if check:
        return check

    user_id = session["user_id"]

    note = Note.query.filter(
        Note.id == note_id,
        Note.user_id == user_id,
        Note.deleted_at.is_(None)
    ).first_or_404()

    if request.method == "POST":
        note.title = request.form.get("title")
        note.content = request.form.get("content")
        db.session.commit()
        return redirect(url_for("notes_bp.edit", note_id=note.id))

    page_title = note.title.strip() if getattr(
        note, 'title', None) and note.title.strip() else "Catatan"
    return render_template("view/fitur/notes/edit.html", note=note, title=page_title)


# =========================
# TAMBAH CATATAN BARU
# =========================
@notes_bp.route("/new")
def new_note():
    check = require_login()
    if check:
        return check

    user_id = session["user_id"]
    note = Note(user_id=user_id, title="", content="")
    db.session.add(note)
    db.session.commit()
    flash("Catatan baru berhasil dibuat", "note_create")
    return redirect(url_for("notes_bp.edit", note_id=note.id))


# =========================
# HAPUS CATATAN
# =========================
@notes_bp.route("/<int:note_id>/delete", methods=["POST"])
def delete(note_id):
    check = require_login()
    if check:
        return check

    note = Note.query.filter(
        Note.id == note_id,
        Note.user_id == session["user_id"],
        Note.deleted_at.is_(None)
    ).first_or_404()

    note.soft_delete()
    db.session.commit()
    flash("Catatan dipindahkan ke Recycle Bin", "note_delete")
    return redirect(url_for("notes_bp.index"))


# =========================
# RECYCLE BIN
# =========================
@notes_bp.route("/recycle")
def trash():
    check = require_login()
    if check:
        return check

    deleted_notes = Note.query.filter(
        Note.user_id == session["user_id"],
        Note.deleted_at.isnot(None)
    ).order_by(Note.deleted_at.desc()).all()

    return render_template("view/fitur/recycle/recycle.html", deleted_notes=deleted_notes)
