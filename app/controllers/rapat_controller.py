from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.rapat import Rapat
from app import db
from flask import flash

rapat_bp = Blueprint("rapat_bp", __name__)

# --------------------------
# AUTH GUARD
# --------------------------


def require_login():
    if not session.get("user_id"):
        return redirect(url_for("auth_bp.login"))
    return None


# --------------------------
# LIST RAPAT (AKTIF)
# --------------------------
@rapat_bp.route("/rapat")
def rapat():
    check = require_login()
    if check:
        return check

    from sqlalchemy import desc
    from datetime import datetime
    import json
    import locale

    try:
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
    except:
        pass

    today = datetime.today()
    current_date = today.strftime('%d %B %Y')

    user_id = session["user_id"]

    rapats = Rapat.query.filter(
        Rapat.user_id == user_id,
        Rapat.deleted_at.is_(None)
    ).order_by(desc(Rapat.tanggal)).all()

    daftar_rapat = []
    for r in rapats:
        try:
            peserta_list = json.loads(r.peserta) if r.peserta else []
        except Exception:
            peserta_list = []

        daftar_rapat.append({
            "id": r.id,
            "topik": r.topik,
            "tanggal": r.tanggal,
            "catatan": r.catatan,
            "peserta_list": peserta_list
        })

    return render_template(
        "view/fitur/rapat/rapat.html",
        daftar_rapat=daftar_rapat,
        current_date=current_date,
        title="Rapat"
    )


# --------------------------
# DETAIL RAPAT
# --------------------------
@rapat_bp.route("/rapat/<int:id>")
def detail_rapat(id):
    check = require_login()
    if check:
        return check

    import json

    rapat = Rapat.query.filter(
        Rapat.id == id,
        Rapat.user_id == session["user_id"],
        Rapat.deleted_at.is_(None)
    ).first_or_404()

    try:
        peserta_list = json.loads(rapat.peserta) if rapat.peserta else []
    except Exception:
        peserta_list = []

    return render_template(
        "view/fitur/rapat/detail.html",
        rapat=rapat,
        peserta_list=peserta_list,
        title="Detail Rapat"
    )


# --------------------------
# CREATE RAPAT
# --------------------------
@rapat_bp.route("/rapat/create", methods=["POST"])
def create_rapat():
    check = require_login()
    if check:
        return check

    from datetime import datetime
    import json

    judul = request.form.get("judul")
    tanggal = request.form.get("tanggal")
    peserta = request.form.getlist("peserta[]")
    catatan = request.form.get("catatan")

    rapat = Rapat(
        topik=judul,
        tanggal=datetime.strptime(
            tanggal, "%Y-%m-%d").date() if tanggal else None,
        peserta=json.dumps(peserta),
        catatan=catatan,
        user_id=session["user_id"]
    )

    db.session.add(rapat)
    db.session.commit()
    flash("Rapat berhasil disimpan", "rapat_create")

    return redirect(url_for("rapat_bp.rapat"))


# --------------------------
# EDIT RAPAT
# --------------------------
@rapat_bp.route("/rapat/<int:id>/edit", methods=["POST"])
def edit_rapat(id):
    check = require_login()
    if check:
        return check

    from datetime import datetime
    import json

    rapat = Rapat.query.filter(
        Rapat.id == id,
        Rapat.user_id == session["user_id"],
        Rapat.deleted_at.is_(None)
    ).first_or_404()

    rapat.topik = request.form.get("topik")
    rapat.tanggal = datetime.strptime(
        request.form.get("tanggal"), "%Y-%m-%d"
    ).date() if request.form.get("tanggal") else None
    rapat.peserta = json.dumps(request.form.getlist("peserta[]"))
    rapat.catatan = request.form.get("catatan")

    db.session.commit()
    flash("Rapat berhasil diperbarui", "rapat_update")

    return redirect(url_for("rapat_bp.detail_rapat", id=rapat.id))


# --------------------------
# DELETE RAPAT (SOFT DELETE)
# --------------------------
@rapat_bp.route("/rapat/<int:id>/delete", methods=["POST"])
def delete_rapat(id):
    check = require_login()
    if check:
        return check

    rapat = Rapat.query.filter(
        Rapat.id == id,
        Rapat.user_id == session["user_id"],
        Rapat.deleted_at.is_(None)
    ).first_or_404()

    rapat.soft_delete()
    db.session.commit()
    flash("Rapat berhasil dipindahkan ke recycle bin", "rapat_delete")

    return redirect(url_for("rapat_bp.rapat"))
