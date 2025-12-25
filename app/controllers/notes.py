from dotenv import load_dotenv
import requests
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models.notes import Note
from app import db

notes_bp = Blueprint("notes_bp", __name__, url_prefix="/notes")


load_dotenv()


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}'


@notes_bp.route('/<int:note_id>/suggest', methods=['POST'])
def note_suggest(note_id):
    if not session.get('user_id'):
        return jsonify({'suggestion': ''}), 401

    data = request.get_json() or {}
    text = data.get('text', '').strip()

    if len(text) < 3:
        return jsonify({'suggestion': ''})

    last_words = text.split()[-3:]  # ambil 1–3 kata terakhir
    context = " ".join(last_words)

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Lanjutkan teks berikut dengan 1 atau 2 kata saja.\n"
                            "Contoh jawaban yang benar:\n"
                            "- dan\n"
                            "- sehingga\n"
                            "- untuk itu\n\n"
                            f"Teks:\n{context}\n\n"
                            "Jawaban:"
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.25,
            "maxOutputTokens": 100,
            "topP": 0.9
        }
    }

    try:
        response = requests.post(GEMINI_API_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

        print("Gemini response:", result)

        suggestion = ""
        candidates = result.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts")

            if parts and isinstance(parts, list):
                suggestion = parts[0].get("text", "").strip()

        return jsonify({'suggestion': suggestion})

    except Exception as e:
        print("Gemini ERROR:", e)
        return jsonify({'suggestion': ''})


# --------------------------
# AUTH GUARD
# --------------------------
def require_login():
    if not session.get("user_id"):
        return redirect(url_for("auth_bp.login"))
    return None


def get_user_notes(user_id):
    return Note.query.filter(
        Note.user_id == user_id,
        Note.deleted_at.is_(None)
    ).order_by(Note.updated_at.desc()).all()


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

    if not notes:
        return render_template(
            "view/fitur/notes/empty.html"
        )

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

    note = Note.query.filter(
        Note.id == note_id,
        Note.user_id == session["user_id"],
        Note.deleted_at.is_(None)
    ).first_or_404()

    note.soft_delete()   # 👈 PINDAH KE RECYCLE BIN
    db.session.commit()

    return redirect(url_for("notes_bp.index"))


@notes_bp.route("/recycle")
def trash():
    check = require_login()
    if check:
        return check

    deleted_notes = Note.query.filter(
        Note.user_id == session["user_id"],
        Note.deleted_at.isnot(None)
    ).order_by(Note.deleted_at.desc()).all()

    return render_template(
        "view/fitur/recycle/recycle.html",
        deleted_notes=deleted_notes
    )
