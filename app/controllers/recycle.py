from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.models.notes import Note
from app.models.rapat import Rapat
from app import db

recycle_bp = Blueprint(
    "recycle_bp",
    __name__,
    url_prefix="/trash"
)

# --------------------------
# AUTH GUARD
# --------------------------


def require_login():
    if not session.get("user_id"):
        return redirect(url_for("auth_bp.login"))
    return None


# --------------------------
# RECYCLE BIN HOME
# --------------------------
@recycle_bp.route("/")
def index():
    check = require_login()
    if check:
        return check

    user_id = session["user_id"]

    deleted_notes = Note.query.filter(
        Note.user_id == user_id,
        Note.deleted_at.isnot(None)
    ).order_by(Note.deleted_at.desc()).all()

    deleted_rapats = Rapat.query.filter(
        Rapat.user_id == user_id,
        Rapat.deleted_at.isnot(None)
    ).order_by(Rapat.deleted_at.desc()).all()

    return render_template(
        "view/fitur/recycle/recycle.html",
        deleted_notes=deleted_notes,
        deleted_rapats=deleted_rapats,
        title="Recycle Bin"
    )


# --------------------------
# RESTORE NOTE
# --------------------------
@recycle_bp.route("/notes/<int:note_id>/restore", methods=["POST"])
def restore_note(note_id):
    check = require_login()
    if check:
        return check

    note = Note.query.filter(
        Note.id == note_id,
        Note.user_id == session["user_id"],
        Note.deleted_at.isnot(None)
    ).first_or_404()

    note.restore()
    db.session.commit()

    return redirect(url_for("recycle_bp.index"))


# --------------------------
# RESTORE RAPAT
# --------------------------
@recycle_bp.route("/rapat/<int:rapat_id>/restore", methods=["POST"])
def restore_rapat(rapat_id):
    check = require_login()
    if check:
        return check

    rapat = Rapat.query.filter(
        Rapat.id == rapat_id,
        Rapat.user_id == session["user_id"],
        Rapat.deleted_at.isnot(None)
    ).first_or_404()

    rapat.restore()
    db.session.commit()

    return redirect(url_for("recycle_bp.index"))


# --------------------------
# FORCE DELETE NOTE
# --------------------------
@recycle_bp.route("/notes/<int:note_id>/force-delete", methods=["POST"])
def force_delete_note(note_id):
    check = require_login()
    if check:
        return check

    note = Note.query.filter(
        Note.id == note_id,
        Note.user_id == session["user_id"]
    ).first_or_404()

    db.session.delete(note)
    db.session.commit()

    return redirect(url_for("recycle_bp.index"))


# --------------------------
# FORCE DELETE RAPAT
# --------------------------
@recycle_bp.route("/rapat/<int:rapat_id>/force-delete", methods=["POST"])
def force_delete_rapat(rapat_id):
    check = require_login()
    if check:
        return check

    rapat = Rapat.query.filter(
        Rapat.id == rapat_id,
        Rapat.user_id == session["user_id"]
    ).first_or_404()

    db.session.delete(rapat)
    db.session.commit()

    return redirect(url_for("recycle_bp.index"))


# --------------------------
# DELETE ALL (NOTE + RAPAT)
# --------------------------
@recycle_bp.route("/delete_all", methods=["POST"])
def delete_all():
    check = require_login()
    if check:
        return check

    user_id = session["user_id"]

    Note.query.filter(
        Note.user_id == user_id,
        Note.deleted_at.isnot(None)
    ).delete(synchronize_session=False)

    Rapat.query.filter(
        Rapat.user_id == user_id,
        Rapat.deleted_at.isnot(None)
    ).delete(synchronize_session=False)

    db.session.commit()
    flash("Semua data di recycle bin dihapus permanen!", "success")

    return redirect(url_for("recycle_bp.index"))
