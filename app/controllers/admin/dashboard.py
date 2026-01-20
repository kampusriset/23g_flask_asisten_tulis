from sqlalchemy import func
from flask import Blueprint, render_template, session
from app.controllers.admin.middleware import admin_login_required
from app.models.user import User
from app.models.inbox import Inbox
from app import db
from datetime import date, timedelta

admin_dashboard_bp = Blueprint(
    'admin_dashboard',
    __name__,
    url_prefix='/admin'
)


@admin_dashboard_bp.route('/dashboard')
@admin_login_required
def dashboard():

    total_users = User.query.count()

    days = []
    user_counts = []

    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)

        count = User.query.filter(
            func.date(User.created_at) == d
        ).count()

        days.append(d.strftime('%d %b'))
        user_counts.append(count or 0)

    return render_template(
        'admin/view/main/dashboard.html',
        admin_username=session.get('admin_username'),
        total_users=total_users,
        days=days,
        user_counts=user_counts
    )
