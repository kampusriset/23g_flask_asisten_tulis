from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.models.notes import Note
from app import db

recycle_bp = Blueprint(
    "recycle_bp",
    __name__,
    url_prefix="/notes/trash"
)


def require_login():
    if not session.get("user_id"):
        return redirect(url_for("auth_bp.login"))
    return None


@recycle_bp.route("/")
def index():
    check = require_login()
    if check:
        return check

    deleted_notes = Note.query.filter(
        Note.user_id == session["user_id"],
        Note.deleted_at.isnot(None)
    ).order_by(Note.deleted_at.desc()).all()

    return render_template(
        "view/fitur/recycle/recycle.html",
        # gunakan nama berbeda agar tidak menimpa `notes` dari context processor
        deleted_notes=deleted_notes
    )


@recycle_bp.route("/<int:note_id>/restore", methods=["POST"])
def restore(note_id):
    check = require_login()
    if check:
        return check

    note = Note.query.filter(
        Note.id == note_id,
        Note.user_id == session["user_id"]
    ).first_or_404()

    note.restore()
    db.session.commit()

    return redirect(url_for("recycle_bp.index"))


@recycle_bp.route("/delete_all", methods=['POST'])
def delete_all():
    check = require_login()
    if check:
        return check

    # ambil semua note yang dihapus user itu sendiri
    deleted_notes = Note.query.filter(
        Note.user_id == session["user_id"],
        Note.deleted_at.isnot(None)
    ).all()

    for note in deleted_notes:
        db.session.delete(note)
    db.session.commit()
    flash('Semua catatan dihapus permanen!', 'success')
    return redirect(url_for('recycle_bp.index'))


@recycle_bp.route("/<int:note_id>/force-delete", methods=["POST"])
def force_delete(note_id):
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
