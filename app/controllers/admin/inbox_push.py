from flask import Blueprint, render_template, request, redirect, flash
from app.controllers.admin.middleware import admin_login_required
from app.models.user import User
from app.models.inbox import Inbox
from app import db

admin_inbox_bp = Blueprint(
    'admin_inbox',
    __name__,
    url_prefix='/admin/inbox'
)


@admin_inbox_bp.route('/', methods=['GET', 'POST'])
@admin_login_required
def push_inbox():
    users = User.query.all()

    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        target = request.form['target']

        if target == 'all':
            all_users = User.query.all()
            for user in all_users:
                inbox = Inbox(
                    user_id=user.id,
                    title=title,
                    message=message
                )
                db.session.add(inbox)

        else:
            inbox = Inbox(
                user_id=int(target),
                title=title,
                message=message
            )
            db.session.add(inbox)

        db.session.commit()
        flash("Inbox berhasil dikirim", "success")

        return redirect('/admin/inbox')

    return render_template(
        'admin/view/main/inbox_push.html',
        users=users
    )
