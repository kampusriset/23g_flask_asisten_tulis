from flask import Flask, render_template, redirect, session
from config import Config

from app.extensions import db, migrate
from app.models.setting import UserSetting


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # INIT EXTENSIONS
    db.init_app(app)
    migrate.init_app(app, db)

    # REGISTER BLUEPRINT
    from app.controllers.user import auth_bp
    from app.controllers.dashboard import dashboard_bp
    from app.controllers.notes import notes_bp
    from app.controllers.gemini import gemini_bp
    from app.controllers.inbox import inbox_bp
    from app.controllers.setting import setting_bp
    from app.controllers.rapat_controller import rapat_bp
    from app.controllers.recycle import recycle_bp
    from app.controllers.profile import profile_bp
    from app.controllers.search import search_bp
    from app.controllers.ai import ai_bp
    from app.controllers.activity import activity_bp
    from app.controllers.admin.admin import admin_auth
    from app.controllers.admin.dashboard import admin_dashboard_bp
    from app.controllers.admin.admin_crud import admin_crud_bp
    from app.controllers.admin.user_crud import admin_user_bp
    from app.commands.seed_admin import seed_admin
    from app.models.notes import Note
    from app.controllers.admin.inbox_push import admin_inbox_bp
    from app.models.setting import UserSetting

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(gemini_bp)
    app.register_blueprint(inbox_bp)
    app.register_blueprint(setting_bp)
    app.register_blueprint(rapat_bp)
    app.register_blueprint(recycle_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(admin_auth)
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_crud_bp)
    app.register_blueprint(admin_user_bp)
    app.cli.add_command(seed_admin)
    app.register_blueprint(admin_inbox_bp)

    # SIDEBAR NOTES

    @app.context_processor
    def inject_notes():
        if session.get("user_id"):
            notes = Note.query.filter(
                Note.user_id == session["user_id"],
                Note.deleted_at.is_(None)
            ).order_by(Note.updated_at.desc()).all()
            return dict(notes=notes)
        return dict(notes=[])

    # GLOBAL DARK MODE
    @app.context_processor
    def inject_dark_mode():
        dark_mode = False
        if session.get("user_id"):
            setting = UserSetting.query.filter_by(
                user_id=session["user_id"]
            ).first()
            if setting:
                dark_mode = setting.dark_mode
        return dict(dark_mode=dark_mode)

    # HOME
    @app.route("/")
    def home():
        if session.get("admin_id"):
            return redirect("/admin/dashboard")
        if session.get("user_id"):
            return redirect("/dashboard")
        return render_template("home/landingpage.html")

    # ADMIN HOME
    @app.route("/admin")
    def admin_home():
        if session.get("admin_id"):
            return redirect("/admin/dashboard")
        if session.get("user_id"):
            return redirect("/dashboard")
        return redirect("/admin/login")

    return app
