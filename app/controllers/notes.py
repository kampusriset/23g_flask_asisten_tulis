from dotenv import load_dotenv
import requests
import os
from flask import Blueprint, request, jsonify, session
from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.notes import Note
from app import db

notes_bp = Blueprint("notes_bp", __name__, url_prefix="/notes")


load_dotenv()

notes_bp = Blueprint('notes_bp', __name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}'


@notes_bp.route('/<int:note_id>/suggest', methods=['POST'])
def note_suggest(note_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'suggestion': ''}), 401

    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'suggestion': ''})

    # === DISINI BANG TARUH PAYLOAD ===
    payload = {
        "contents": [
            {"parts": [
                {"text": f"Lanjutkan teks berikut secara cerdas, tapi pendek-pendek, satu atau dua kata/frasa saja:\n{text}"}]}
        ],
        "temperature": 0.5,
        "max_output_tokens": 10
    }

    try:
        response = requests.post(GEMINI_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        suggestion = result.get('candidates', [{}])[0].get(
            'content', {}).get('parts', [{}])[0].get('text', '')
        return jsonify({'suggestion': suggestion})
    except Exception as e:
        return jsonify({'suggestion': '', 'error': str(e)})


# --------------------------
# AUTH GUARD
# --------------------------
def require_login():
    if not session.get("user_id"):
        return redirect(url_for("auth_bp.login"))
    return None


def get_user_notes(user_id):
    return Note.query.filter_by(user_id=user_id)\
        .order_by(Note.updated_at.desc()).all()


# --------------------------
# NOTES HOME
# --------------------------
@notes_bp.route("/")
def index():
    check = require_login()
    if check:
        return check

    user_id = session["user_id"]
    notes = get_user_notes(user_id)

    # kalau belum ada catatan → buat satu
    if not notes:
        note = Note(user_id=user_id, title="", content="")
        db.session.add(note)
        db.session.commit()
        return redirect(url_for("notes_bp.edit", note_id=note.id))

    # kalau ada → buka catatan terakhir
    return redirect(url_for("notes_bp.edit", note_id=notes[0].id))


# --------------------------
# EDIT / VIEW CATATAN
# --------------------------
@notes_bp.route("/<int:note_id>", methods=["GET", "POST"])
def edit(note_id):
    check = require_login()
    if check:
        return check

    user_id = session["user_id"]

    note = Note.query.filter_by(
        id=note_id,
        user_id=user_id
    ).first_or_404()

    if request.method == "POST":
        note.title = request.form.get("title")
        note.content = request.form.get("content")
        db.session.commit()

        return redirect(url_for("notes_bp.edit", note_id=note.id))

    return render_template(
        "view/fitur/notes/edit.html",
        note=note
    )


# --------------------------
# TAMBAH CATATAN BARU
# --------------------------
@notes_bp.route("/new")
def new_note():
    check = require_login()
    if check:
        return check

    user_id = session["user_id"]
    note = Note(user_id=user_id, title="", content="")
    db.session.add(note)
    db.session.commit()
    return redirect(url_for("notes_bp.edit", note_id=note.id))


# --------------------------
# HAPUS CATATAN
# --------------------------
@notes_bp.route("/<int:note_id>/delete", methods=["POST"])
def delete(note_id):
    check = require_login()
    if check:
        return check

    user_id = session["user_id"]

    note = Note.query.filter_by(
        id=note_id,
        user_id=user_id
    ).first_or_404()

    db.session.delete(note)
    db.session.commit()

    return redirect(url_for("notes_bp.index"))
