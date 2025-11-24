from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import User
from . import db

auth_bp = Blueprint('auth_bp', __name__)


# --------------------------
# REGISTER
# --------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Cek password sama
        if password != confirm_password:
            flash("Password tidak sama, Bang!", "error")
            return redirect(url_for("auth_bp.register"))

        # Cek username atau email udah ada
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username atau email sudah dipakai, Bang!", "error")
            return redirect(url_for("auth_bp.register"))

        # Buat user baru
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Register berhasil, silakan login!", "success")
        return redirect(url_for("auth_bp.login"))

    return render_template("auth/register.html", title="Register")


# --------------------------
# LOGIN
# --------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier").strip()  # username/email
        password = request.form.get("password")

        # Cari user berdasarkan username atau email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if not user or not user.check_password(password):
            flash("Username/email atau password salah! 🥲", "error")
            return redirect(url_for("auth_bp.login"))

        # Simpan session
        session["user_id"] = user.id

        return redirect(url_for("dashboard_bp.dashboard"))

    return render_template("auth/login.html", title="Login")


# --------------------------
# LOGOUT
# --------------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth_bp.login"))
