from flask import Blueprint, render_template, request, redirect, flash
from werkzeug.security import generate_password_hash
from app.models.admin import Admin
from app import db
from app.controllers.admin.middleware import admin_login_required

admin_crud_bp = Blueprint(
    'admin_crud',
    __name__,
    url_prefix='/admin/admins'
)


@admin_crud_bp.route('/')
@admin_login_required
def index():
    admins = Admin.query.all()
    return render_template('admin/view/main/admin_crud.html', admins=admins)


@admin_crud_bp.route('/create', methods=['POST'])
@admin_login_required
def create():
    admin = Admin(
        username=request.form['username'],
        password_hash=generate_password_hash(request.form['password']),
        is_active=True
    )
    db.session.add(admin)
    db.session.commit()
    flash('Admin berhasil ditambahkan')
    return redirect('/admin/admins')


@admin_crud_bp.route('/delete/<int:id>')
@admin_login_required
def delete(id):
    admin = Admin.query.get_or_404(id)
    db.session.delete(admin)
    db.session.commit()
    flash('Admin dihapus')
    return redirect('/admin/admins')
