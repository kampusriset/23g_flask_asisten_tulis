from math import ceil
from sqlalchemy import or_
from flask import request
import re
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
import io
from flask import send_file
from openpyxl import Workbook
from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for, request
from app.models.notes import Note
from app.models.rapat import Rapat
from datetime import date
from datetime import datetime, time


activity_bp = Blueprint("activity_bp", __name__, url_prefix="/activity")


def safe_filename(text):
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)   # buang simbol aneh
    text = re.sub(r"\s+", "_", text)       # spasi → _
    return text[:50]                       # batasi panjang


@activity_bp.route("/activity")
def activity():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    q = request.args.get("q", "")
    page = int(request.args.get("page", 1))
    per_page = 10
    activity_type = request.args.get("type", "all")  # "all", "note", "rapat"

    start = request.args.get("start_date")
    end = request.args.get("end_date")

    activities = []

    # -------------------
    # CATATAN
    # -------------------
    if activity_type in ["all", "note"]:
        notes_query = Note.query.filter(
            Note.user_id == user_id,
            Note.deleted_at.is_(None)
        )

        if q:
            notes_query = notes_query.filter(Note.title.ilike(f"%{q}%"))
        if start and end:
            notes_query = notes_query.filter(
                Note.created_at.between(start, end))

        notes = notes_query.all()

        for n in notes:
            activities.append({
                "type": "Catatan",
                "title": n.title or "Catatan",
                "date": n.created_at,
                "id": n.id
            })

    # -------------------
    # RAPAT
    # -------------------
    if activity_type in ["all", "rapat"]:
        rapat_query = Rapat.query.filter(Rapat.user_id == user_id)

        if q:
            rapat_query = rapat_query.filter(Rapat.topik.ilike(f"%{q}%"))
        if start and end:
            try:
                start_date = datetime.strptime(start, "%Y-%m-%d").date()
                end_date = datetime.strptime(end, "%Y-%m-%d").date()
                rapat_query = rapat_query.filter(
                    Rapat.tanggal.between(start_date, end_date)
                )
            except ValueError:
                pass

        rapats = rapat_query.all()

        for r in rapats:
            activities.append({
                "type": "Rapat",
                "title": r.topik,
                "date": datetime.combine(r.tanggal, time.min),
                "id": r.id
            })

    # -------------------
    # SORT & PAGINATION
    # -------------------
    activities.sort(key=lambda x: x["date"], reverse=True)

    total = len(activities)
    total_pages = ceil(total / per_page)
    start_i = (page - 1) * per_page
    end_i = start_i + per_page
    activities = activities[start_i:end_i]

    return render_template(
        "view/fitur/activity/activity.html",
        activities=activities,
        page=page,
        total_pages=total_pages,
        q=q,
        start_date=start,
        end_date=end,
        activity_type=activity_type
    )


@activity_bp.route("/activity/table")
def activity_table():
    # ambil semua param filter sama kayak route utama
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    q = request.args.get("q", "")
    activity_type = request.args.get("type", "all")
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    activities = []

    # ... sama kayak logic activity utama ...
    # CATATAN
    if activity_type in ["all", "note"]:
        notes_query = Note.query.filter(
            Note.user_id == user_id, Note.deleted_at.is_(None))
        if q:
            notes_query = notes_query.filter(Note.title.ilike(f"%{q}%"))
        if start and end:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            notes_query = notes_query.filter(
                Note.created_at.between(start_date, end_date))
        notes = notes_query.all()
        for n in notes:
            activities.append(
                {"type": "Catatan", "title": n.title or "Catatan", "date": n.created_at, "id": n.id})

    # RAPAT
    if activity_type in ["all", "rapat"]:
        rapat_query = Rapat.query.filter(Rapat.user_id == user_id)
        if q:
            rapat_query = rapat_query.filter(Rapat.topik.ilike(f"%{q}%"))
        if start and end:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
            rapat_query = rapat_query.filter(
                Rapat.tanggal.between(start_date, end_date))
        rapats = rapat_query.all()
        for r in rapats:
            activities.append({"type": "Rapat", "title": r.topik, "date": datetime.combine(
                r.tanggal, time.min), "id": r.id})

    # sort
    activities.sort(key=lambda x: x["date"], reverse=True)

    return render_template("view/fitur/activity/_activity_table.html", activities=activities)


@activity_bp.route("/export/excel")
def export_excel():
    user_id = session.get("user_id")

    start = request.args.get("start_date")
    end = request.args.get("end_date")

    wb = Workbook()
    ws = wb.active
    ws.append(["Tipe", "Judul / Topik", "Tanggal", "Peserta", "Isi"])

    notes = Note.query.filter(
        Note.user_id == user_id,
        Note.deleted_at.is_(None)
    )

    rapats = Rapat.query.filter(Rapat.user_id == user_id)

    if start and end:
        notes = notes.filter(Note.created_at.between(start, end))
        rapats = rapats.filter(Rapat.tanggal.between(start, end))

    for n in notes:
        ws.append([
            "Catatan",
            n.title,
            n.created_at.strftime("%Y-%m-%d"),
            "",
            n.content
        ])

    for r in rapats:
        ws.append([
            "Rapat",
            r.topik,
            r.tanggal.strftime("%Y-%m-%d"),
            r.peserta,
            r.catatan
        ])

    file = io.BytesIO()
    wb.save(file)
    file.seek(0)

    return send_file(
        file,
        as_attachment=True,
        download_name="activity.xlsx"
    )


@activity_bp.route("/export/pdf")
def export_activity_pdf():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    notes = Note.query.filter(
        Note.user_id == user_id,
        Note.deleted_at.is_(None)
    ).all()

    rapats = Rapat.query.filter(
        Rapat.user_id == user_id
    ).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    data = [[
        "Tipe",
        "Judul / Topik",
        "Tanggal",
        "Peserta",
        "Isi"
    ]]

    # CATATAN
    for n in notes:
        data.append([
            "Catatan",
            n.title or "Catatan Baru",
            n.created_at.strftime("%Y-%m-%d"),
            "-",
            Paragraph((n.content or "-")[:1500], styles["Normal"])
        ])

    # RAPAT
    for r in rapats:
        data.append([
            "Rapat",
            r.topik,
            r.tanggal.strftime("%Y-%m-%d"),
            r.peserta or "-",
            Paragraph((r.catatan or "-")[:1500], styles["Normal"])
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgray),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    doc.build([table])
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="activity.pdf",
        mimetype="application/pdf"
    )


@activity_bp.route("/export/note/<int:id>")
def export_note_pdf(id):
    n = Note.query.get_or_404(id)

    filename = safe_filename(n.title or "catatan") + ".pdf"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = [
        Paragraph(f"<b>Judul:</b> {n.title or 'Catatan'}", styles["Normal"]),
        Paragraph(
            f"<b>Tanggal:</b> {n.created_at.strftime('%d %b %Y')}",
            styles["Normal"]
        ),
        Spacer(1, 12),
        Paragraph(n.content or "-", styles["Normal"])
    ]

    doc.build(content)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )


@activity_bp.route("/export/rapat/<int:id>")
def export_rapat_pdf(id):
    r = Rapat.query.get_or_404(id)

    filename = safe_filename(r.topik or "rapat") + ".pdf"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = [
        Paragraph(f"<b>Topik:</b> {r.topik}", styles["Normal"]),
        Paragraph(
            f"<b>Tanggal:</b> {r.tanggal.strftime('%d %b %Y')}",
            styles["Normal"]
        ),
        Paragraph(
            f"<b>Peserta:</b> {r.peserta or '-'}",
            styles["Normal"]
        ),
        Spacer(1, 12),
        Paragraph("<b>Catatan Rapat:</b>", styles["Normal"]),
        Spacer(1, 6),
        Paragraph(r.catatan or "-", styles["Normal"])
    ]

    doc.build(content)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )
