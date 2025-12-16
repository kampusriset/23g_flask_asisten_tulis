from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---- Helper functions ----

    def set_password(self, password):
        """Generate hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Compare password with stored hash."""
        return check_password_hash(self.password_hash, password)
