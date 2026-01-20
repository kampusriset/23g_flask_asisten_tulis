from flask import Blueprint, render_template, request, redirect, session, flash
from app.models.admin import Admin

admin_auth = Blueprint(
    'admin_auth',
    __name__,
    url_prefix='/admin'
)


@admin_auth.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_id'):
        return redirect('/admin/dashboard')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(
            username=username,
            is_active=True
        ).first()

        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            return redirect('/admin/dashboard')

        flash('Username atau password salah', 'login_error')

    return render_template('admin/auth/login.html')


@admin_auth.route('/logout')
def logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    return redirect('/admin/login')
