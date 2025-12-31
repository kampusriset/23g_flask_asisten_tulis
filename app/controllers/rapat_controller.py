from flask import Blueprint, render_template, request, redirect, url_for
from app.models.rapat import Rapat
from app import db

rapat_bp = Blueprint("rapat_bp", __name__)

# --------------------------
# EDIT RAPAT
# --------------------------


@rapat_bp.route("/rapat/<int:id>/edit", methods=["POST"])
def edit_rapat(id):
    rapat = Rapat.query.get_or_404(id)
    topik = request.form.get("topik")
    tanggal = request.form.get("tanggal")
    peserta = request.form.getlist("peserta[]")
    catatan = request.form.get("catatan")
    from datetime import datetime
    import json
    rapat.topik = topik
    rapat.tanggal = datetime.strptime(
        tanggal, "%Y-%m-%d").date() if tanggal else None
    rapat.peserta = json.dumps(peserta)
    rapat.catatan = catatan
    db.session.commit()
    return redirect(url_for('rapat_bp.detail_rapat', id=rapat.id))

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
    from datetime import datetime
    import locale
    try:
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
    except:
        pass
    today = datetime.today()
    current_date = today.strftime('%d %B %Y')
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
    # Set browser page title to 'Rapat' to match sidebar
    # (Kept separate comment for clarity)
    return render_template("view/fitur/rapat/rapat.html", daftar_rapat=daftar_rapat, current_date=current_date, title="Rapat")

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
    return render_template("view/fitur/rapat/detail.html", rapat=rapat, peserta_list=peserta_list, title="Detail Rapat")

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
        tanggal=datetime.strptime(
            tanggal, "%Y-%m-%d").date() if tanggal else None,
        peserta=json.dumps(peserta),
        catatan=catatan
    )
    db.session.add(rapat)
    db.session.commit()
    return redirect("/rapat")
