from flask import Blueprint, render_template, request, redirect, session
from app import db
from app.models.setting import UserSetting
from app.models.user import User

setting_bp = Blueprint("setting", __name__, url_prefix="/setting")


@setting_bp.route("/", methods=["GET", "POST"])
def index():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    setting = UserSetting.query.filter_by(user_id=user_id).first()
    if not setting:
        setting = UserSetting(user_id=user_id)
        db.session.add(setting)
        db.session.commit()

    if request.method == "POST":
        setting.dark_mode = "dark_mode" in request.form
        db.session.commit()
        return redirect("/setting")

    user = User.query.get(user_id)

    return render_template(
        "view/fitur/setting/setting.html",
        user=user,
        setting=setting
    )
