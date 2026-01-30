from flask import Blueprint, render_template, request, redirect, session
from app.extensions import db
from app.models.setting import UserSetting
from app.models.user import User

setting_bp = Blueprint("setting", __name__, url_prefix="/setting")


@setting_bp.route("/", methods=["GET"])
def index():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    setting = UserSetting.query.filter_by(user_id=user_id).first()
    if not setting:
        setting = UserSetting(user_id=user_id, dark_mode=False)
        db.session.add(setting)
        db.session.commit()

    user = User.query.get(user_id)

    return render_template(
        "view/fitur/setting/setting.html",
        user=user,
        dark_mode=setting.dark_mode,
        ai_provider=setting.ai_provider
    )


@setting_bp.route("/toggle-dark", methods=["POST"])
def toggle_dark():
    user_id = session.get("user_id")
    if not user_id:
        return "", 401

    setting = UserSetting.query.filter_by(user_id=user_id).first()

    if not setting:
        setting = UserSetting(user_id=user_id, dark_mode=True)
        db.session.add(setting)
    else:
        setting.dark_mode = not setting.dark_mode

    db.session.commit()
    return "", 204


@setting_bp.route("/set-ai-provider", methods=["POST"])
def set_ai_provider():
    user_id = session.get("user_id")
    if not user_id:
        return "", 401

    data = request.get_json()
    provider = data.get("provider")

    if provider not in ["gemini", "openai", "groq", "deepseek"]:
        return {"error": "Invalid provider"}, 400

    setting = UserSetting.query.filter_by(user_id=user_id).first()
    setting.ai_provider = provider

    db.session.commit()
    return {"success": True}
