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
    from app.controllers.inbox import inbox_bp      # ← TAMBAHAN
    from app.models.notes import Note
    from app.controllers.rapat_controller import rapat_bp
    from app.controllers.recycle import recycle_bp
    from app.controllers.profile import profile_bp
    from app.controllers.search import search_bp
    from app.controllers.ai import ai_bp
    from app.controllers.activity import activity_bp
    from app.controllers.admin.admin import admin_auth
    from app.controllers.admin.dashboard import admin_dashboard_bp
    from app.commands.seed_admin import seed_admin
    from app.controllers.admin.admin_crud import admin_crud_bp
    from app.controllers.admin.user_crud import admin_user_bp

    app.register_blueprint(gemini_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(inbox_bp)                # ← TAMBAHAN
    app.register_blueprint(rapat_bp)
    app.register_blueprint(recycle_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(admin_auth)
    app.register_blueprint(admin_dashboard_bp)
    app.cli.add_command(seed_admin)
    app.register_blueprint(admin_crud_bp)
    app.register_blueprint(admin_user_bp)

    @app.context_processor
    def inject_notes():
        if session.get("user_id"):
            notes = Note.query.filter(
                Note.user_id == session["user_id"],
                Note.deleted_at.is_(None)  # hanya catatan aktif
            ).order_by(Note.updated_at.desc()).all()
            return dict(notes=notes)  # sidebar pakai ini
        return dict(notes=[])

    # HOME ROUTE
    @app.route("/")
    def home():
        # kalau admin sudah login
        if session.get('admin_id'):
            return redirect("/admin/dashboard")

        # kalau user biasa sudah login
        if session.get('user_id'):
            return redirect("/dashboard")

        # belum login sama sekali
        return render_template("home/landingpage.html")

    # ADMIN HOME ROUTE
    @app.route("/admin")
    def admin_home():
        if session.get('admin_id'):
            return redirect("/admin/dashboard")
        return redirect("/admin/login")

    return app
