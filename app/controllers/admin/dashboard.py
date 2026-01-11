from flask import Blueprint, render_template, session
from app.controllers.admin.middleware import admin_login_required

admin_dashboard_bp = Blueprint(
    'admin_dashboard',
    __name__,
    url_prefix='/admin'
)


@admin_dashboard_bp.route('/dashboard')
@admin_login_required
def dashboard():
    return render_template(
        'admin/view/main/dashboard.html',
        admin_username=session.get('admin_username')
    )
