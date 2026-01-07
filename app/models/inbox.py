from datetime import datetime
from app import db

class Inbox(db.Model):
    __tablename__ = "inbox"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)

    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
