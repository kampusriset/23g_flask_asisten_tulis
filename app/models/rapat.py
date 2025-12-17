from flask_sqlalchemy import SQLAlchemy
from datetime import date
from app import db

class Rapat(db.Model):
    __tablename__ = "rapats"

    id = db.Column(db.Integer, primary_key=True)
    topik = db.Column(db.String(200), nullable=False)
    catatan = db.Column(db.Text)
    tanggal = db.Column(db.Date, default=date.today)
