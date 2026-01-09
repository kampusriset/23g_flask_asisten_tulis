from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from app import db


class Rapat(db.Model):
    __tablename__ = "rapats"

    id = db.Column(db.Integer, primary_key=True)
    topik = db.Column(db.String(200), nullable=False)
    catatan = db.Column(db.Text)
    tanggal = db.Column(db.Date, default=date.today)
    peserta = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('rapats', lazy=True))

    # ⏱️ TIMESTAMP
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # 🗑️ SOFT DELETE
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

    def restore(self):
        self.deleted_at = None
