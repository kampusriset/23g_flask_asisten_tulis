
from flask import Blueprint, render_template, request, redirect, url_for
from app.models.rapat import Rapat
from app import db

rapat_bp = Blueprint("rapat_bp", __name__)

# --------------------------
# DELETE RAPAT
# --------------------------
@rapat_bp.route("/rapat/<int:id>/delete", methods=["POST"])
def delete_rapat(id):
    rapat = Rapat.query.get_or_404(id)
    db.session.delete(rapat)
    db.session.commit()
    return redirect(url_for('rapat_bp.rapat'))

# --------------------------
# LIST RAPAT
# --------------------------

@rapat_bp.route("/rapat")
def rapat():
    from sqlalchemy import desc
    import json
    rapats = Rapat.query.order_by(desc(Rapat.tanggal)).all()
    daftar_rapat = []
    for r in rapats:
        try:
            peserta_list = json.loads(r.peserta) if r.peserta else []
        except Exception:
            peserta_list = []
        daftar_rapat.append({
            'id': r.id,
            'topik': r.topik,
            'tanggal': r.tanggal,
            'catatan': r.catatan,
            'peserta_list': peserta_list
        })
    return render_template("view/fitur/rapat/rapat.html", daftar_rapat=daftar_rapat)

# --------------------------
# DETAIL RAPAT
# --------------------------
@rapat_bp.route("/rapat/<int:id>")
def detail_rapat(id):
    rapat = Rapat.query.get_or_404(id)
    import json
    try:
        peserta_list = json.loads(rapat.peserta) if rapat.peserta else []
    except Exception:
        peserta_list = []
    return render_template("view/fitur/rapat/detail.html", rapat=rapat, peserta_list=peserta_list)

# --------------------------
# CREATE RAPAT
# --------------------------


@rapat_bp.route("/rapat/create", methods=["POST"])
def create_rapat():
    judul = request.form.get("judul")
    tanggal = request.form.get("tanggal")
    peserta = request.form.getlist("peserta[]")
    catatan = request.form.get("catatan")
    from datetime import datetime
    import json
    rapat = Rapat(
        topik=judul,
        tanggal=datetime.strptime(tanggal, "%Y-%m-%d").date() if tanggal else None,
        peserta=json.dumps(peserta),
        catatan=catatan
    )
    db.session.add(rapat)
    db.session.commit()
    return redirect("/rapat")
