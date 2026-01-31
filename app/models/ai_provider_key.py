from app import db


class AIProviderKey(db.Model):
    __tablename__ = "ai_provider_keys"

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), unique=True, nullable=False)
    api_key = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
