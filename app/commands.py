"""Flask commands

Run flask help for list of possible commands
"""
import click
from flask.cli import AppGroup

from app.user.models import User
from app.user.constants import UserRole
from app.database import db
from app.utils.utils import random_string


user_cli = AppGroup('user')


@user_cli.command('add-root')
@click.argument('email')
@click.argument('first_name')
@click.argument('last_name')
def create_root(email: str, first_name: str, last_name: str) -> None:
    """Create the root user (id=0).

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
    """Reset the root password."""
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
