from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask import redirect, session

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init DB
    db.init_app(app)

    # Register blueprint
    from .auth import auth_bp
    from .dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    # HOME ROUTE → render template
    @app.route("/")
    def home():
        # cek session, kalau user udah login redirect ke dashboard
        if session.get('user_id'):
            return redirect("/dashboard")

        # kalau belum login, tampilkan landing page
        return render_template("home/landingpage.html")

    return app
