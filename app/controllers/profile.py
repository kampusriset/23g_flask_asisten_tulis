

import os
from flask import Blueprint, render_template, session, redirect, url_for, request, flash, current_app
from werkzeug.utils import secure_filename
from app.models.user import User
from app import db

profile_bp = Blueprint('profile_bp', __name__)


@profile_bp.route('/profile')
def profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    return render_template('profile/profile.html', user=user, title='Profil Saya')


@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Anda harus login untuk mengedit profil.', 'error')
        return redirect(url_for('profile_bp.profile'))
    user = User.query.get(user_id)
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        file = request.files.get('profile_pic')
        # Validasi sederhana, bisa dikembangkan
        if username:
            user.username = username
        if email:
            user.email = email
        if file and file.filename:
            filename = secure_filename(file.filename)
            img_path = os.path.join('static', 'img', filename)
            file.save(os.path.join(current_app.root_path, img_path))
            user.profile_pic = f'img/{filename}'
        db.session.commit()
        flash('Profil berhasil diperbarui.', 'profile_success')
        return redirect(url_for('profile_bp.edit_profile'))
    return render_template('profile/edit_profile.html', user=user, title='Edit Profil')


# Route untuk mengganti password
@profile_bp.route('/profile/change-password', methods=['GET', 'POST'])
def change_password():
    user_id = session.get('user_id')
    if not user_id:
        flash('Anda harus login untuk mengganti password.', 'error')
        return redirect(url_for('profile_bp.profile'))
    user = User.query.get(user_id)
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        # Validasi sederhana, sesuaikan dengan implementasi password hash di model User
        if not user.check_password(current_password):
            flash('Password lama salah.', 'error')
        elif new_password != confirm_password:
            flash('Password baru dan konfirmasi tidak cocok.', 'error')
        elif not new_password:
            flash('Password baru tidak boleh kosong.', 'error')
        else:
            user.set_password(new_password)
            db.session.commit()
            flash('Password berhasil diubah.', 'success')
            return redirect(url_for('profile_bp.change_password'))
    return render_template('profile/change_password.html', user=user, title='Ganti Password')
