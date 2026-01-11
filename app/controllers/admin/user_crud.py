from flask import Blueprint, render_template, request, redirect, flash
from app.models.user import User
from app import db
from app.controllers.admin.middleware import admin_login_required

admin_user_bp = Blueprint(
    'admin_user',
    __name__,
    url_prefix='/admin/users'
)


@admin_user_bp.route('/')
@admin_login_required
def index():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template(
        'admin/view/main/user_crud.html',
        users=users
    )


@admin_user_bp.route('/create', methods=['POST'])
@admin_login_required
def create():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # basic validation
    if User.query.filter(
        (User.username == username) | (User.email == email)
    ).first():
        flash('Username atau email sudah dipakai')
        return redirect('/admin/users')

    user = User(
        username=username,
        email=email
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    flash('User berhasil ditambahkan')
    return redirect('/admin/users')


@admin_user_bp.route('/delete/<int:id>')
@admin_login_required
def delete(id):
    user = User.query.get_or_404(id)

    db.session.delete(user)
    db.session.commit()

    flash('User berhasil dihapus')
    return redirect('/admin/users')
