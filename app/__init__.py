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
    
    app.register_blueprint(gemini_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(notes_bp)

    @app.context_processor
    def inject_notes():
        if session.get("user_id"):
            notes = Note.query.filter_by(
                user_id=session["user_id"]
            ).order_by(Note.updated_at.desc()).all()
            return dict(notes=notes)
        return dict(notes=[])

    # HOME ROUTE
    @app.route("/")
    def home():
        if session.get('user_id'):
            return redirect("/dashboard")
        return render_template("home/landingpage.html")
    return app
