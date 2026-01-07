from flask import Blueprint, render_template, session, redirect, url_for
from datetime import datetime

from app import db
from app.models.inbox import Inbox

inbox_bp = Blueprint("inbox", __name__, url_prefix="/inbox")


@inbox_bp.route("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    messages = (
        Inbox.query
        .filter_by(user_id=session["user_id"])
        .order_by(Inbox.created_at.desc())
        .all()
    )

    unread_count = Inbox.query.filter_by(
        user_id=session["user_id"],
        is_read=False
    ).count()

    return render_template(
        "view/fitur/inbox/inbox.html",
        messages=messages,
        unread_count=unread_count
    )


@inbox_bp.route("/read/<int:id>")
def read(id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    msg = Inbox.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first_or_404()

    if not msg.is_read:
        msg.is_read = True
        msg.read_at = datetime.utcnow()
        db.session.commit()

    return redirect(url_for("inbox.index"))
