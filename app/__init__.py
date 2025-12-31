from flask import Flask, render_template, redirect, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init DB
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprint
    from app.controllers.user import auth_bp
    from app.controllers.dashboard import dashboard_bp
    from app.controllers.notes import notes_bp
    from app.controllers.gemini import gemini_bp
    from app.models.notes import Note
    from app.controllers.rapat_controller import rapat_bp
    from app.controllers.recycle import recycle_bp
    from app.controllers.profile import profile_bp
    from app.controllers.search import search_bp

    app.register_blueprint(gemini_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(rapat_bp)
    app.register_blueprint(recycle_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(search_bp)

    @app.context_processor
    def inject_notes():
        if session.get("user_id"):
            notes = Note.query.filter(
                Note.user_id == session["user_id"],
                Note.deleted_at.is_(None)  # hanya catatan aktif
            ).order_by(Note.updated_at.desc()).all()
            return dict(notes=notes)  # <-- ini sidebar selalu pakai ini
        return dict(notes=[])

    # HOME ROUTE

    @app.route("/")
    def home():
        if session.get('user_id'):
            return redirect("/dashboard")
        return render_template("home/landingpage.html")
    return app
