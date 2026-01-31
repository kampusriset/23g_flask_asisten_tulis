from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.ai_provider_key import AIProviderKey

admin_ai_bp = Blueprint("admin_ai", __name__, url_prefix="/admin")

PROVIDERS = ["gemini", "openai", "groq", "deepseek"]


@admin_ai_bp.route("/ai-keys", methods=["GET", "POST"])
def ai_keys():
    if request.method == "POST":
        provider = request.form.get("provider")
        api_key = request.form.get("api_key")

        if provider not in PROVIDERS or not api_key:
            flash("Data tidak valid", "error")
            return redirect(url_for("admin_ai.ai_keys"))

        record = AIProviderKey.query.filter_by(provider=provider).first()
        if record:
            record.api_key = api_key
            record.is_active = True
        else:
            record = AIProviderKey(
                provider=provider,
                api_key=api_key
            )
            db.session.add(record)

        db.session.commit()
        flash("API Key berhasil disimpan", "success")
        return redirect(url_for("admin_ai.ai_keys"))

    keys = AIProviderKey.query.all()
    return render_template("admin/view/main/ai_keys.html", keys=keys, providers=PROVIDERS)


@admin_ai_bp.route("/ai-keys/<int:key_id>/toggle", methods=["POST"])
def toggle_ai_key(key_id):
    record = AIProviderKey.query.get_or_404(key_id)
    record.is_active = not record.is_active
    db.session.commit()

    flash(
        f"API Key {record.provider.upper()} "
        f"{'diaktifkan' if record.is_active else 'dinonaktifkan'}",
        "success"
    )
    return redirect(url_for("admin_ai.ai_keys"))


@admin_ai_bp.route("/ai-keys/<int:key_id>/delete", methods=["POST"])
def delete_ai_key(key_id):
    record = AIProviderKey.query.get_or_404(key_id)
    db.session.delete(record)
    db.session.commit()

    flash(f"API Key {record.provider.upper()} dihapus", "success")
    return redirect(url_for("admin_ai.ai_keys"))
