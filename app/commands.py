"""Flask commands

Run flask help for list of possible commands
"""
import os
import click
from flask.cli import AppGroup

from app.user.models import User
from app.user.constants import UserRole
from app.database import db
from app.utils.utils import random_string


user_cli = AppGroup('user', help="User management")
translate_cli = AppGroup('translate', help="Translation utilities")


@user_cli.command('add-root')
@click.argument('email')
@click.argument('first_name')
@click.argument('last_name')
def create_root(email: str, first_name: str, last_name: str) -> None:
    """Creates the root user (id=0).

    Run like `flask user add-root foobar@example.com John Wick`
    """
    if User.get_by_id(0):
        print("Root user already exists!")
        return

    password = random_string()
    User.create(id=0,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=UserRole.ROOT)
    db.session.commit()

    print("Created a new admin user")
    print("Use following credentials to login:")
    print(f"  email: {email}")
    print(f"  password: {password}")
    print()
    print("Don't forget to change your password after first login")


@user_cli.command('reset-root-pwd')
def reset_root_pwd() -> None:
    """Resets the root password."""
    root = User.get_by_id(0)
    if not root:
        print("Root user doesn't exist!")
        return

    password = random_string()
    root.set_password(password)
    root.active = True
    db.session.commit()

    print("Password restarted.")
    print("Use following credentials to login:")
    print(f"  email: {root.email}")
    print(f"  password: {password}")
    print()
    print("Don't forget to change your password after first login")


@translate_cli.command('init')
@click.argument('language')
def translate_init(language: str) -> None:
    """Initializes a new translation language

    Args:
        language: Language shortcut
    """
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('Extract command failed')
    if os.system('pybabel init -i messages.pot -d app/translations -l ' +
                 language):
        raise RuntimeError('Init command failed')
    os.remove('messages.pot')


@translate_cli.command('update')
def translate_update() -> None:
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('Extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('Update command failed')
    os.remove('messages.pot')


@translate_cli.command('compile')
def translate_compile():
    """Compile all languages."""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('Compile command failed')
