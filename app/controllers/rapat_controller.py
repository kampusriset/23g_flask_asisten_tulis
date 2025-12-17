from flask import Blueprint, render_template, request, redirect, url_for
from app.models.rapat import Rapat
from app import db

rapat_bp = Blueprint("rapat_bp", __name__)

# --------------------------
# LIST RAPAT
# --------------------------
@rapat_bp.route("/rapat")
def rapat():
    rapats = Rapat.query.all()
    return render_template("view/fitur/rapat.html", rapats=rapats)

# --------------------------
# CREATE RAPAT
# --------------------------
@rapat_bp.route("/rapat/create", methods=["POST"])
def create_rapat():
    topik = request.form.get("topik")
    catatan = request.form.get("catatan")
    rapat = Rapat(
        topik=topik,
        catatan=catatan
    )
    db.session.add(rapat)
    db.session.commit()
    return redirect(url_for("rapat_bp.rapat"))
