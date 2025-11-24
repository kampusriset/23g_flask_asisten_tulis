from flask import Blueprint, render_template, session, redirect, url_for
from .models import User

dashboard_bp = Blueprint('dashboard_bp', __name__)

# --------------------------
# DASHBOARD PAGE
# --------------------------


@dashboard_bp.route("/dashboard")
def dashboard():
    # Cek user login
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth_bp.login"))

    # Ambil data user
    user = User.query.get(user_id)
    return render_template("view/dashboard.html", user=user, title="Dashboard")


# --------------------------
# FITUR BELUM TERSEDIA
# --------------------------
@dashboard_bp.route("/not-available")
def not_available():
    user_id = session.get("user_id")
    user = None
    if user_id:
        user = User.query.get(user_id)

    return render_template("view/not_available.html", user=user, title="Fitur Belum Tersedia")
