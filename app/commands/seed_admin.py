import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from app import db
from app.models.admin import Admin


@click.command('seed-admin')
@with_appcontext
def seed_admin():
    username = 'admin'
    password = 'admin123'

    admin = Admin.query.filter_by(username=username).first()
    if admin:
        click.echo('Admin sudah ada 👍')
        return

    admin = Admin(
        username=username,
        password_hash=generate_password_hash(password),
        is_active=True
    )

    db.session.add(admin)
    db.session.commit()

    click.echo('Admin berhasil dibuat 🚀')
    click.echo(f'Username: {username}')
    click.echo(f'Password: {password}')
