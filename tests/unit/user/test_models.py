"""Test User module database models"""
from app.models.user import User, UserRole
from app.database import db


def test_new_user(session):
    """
    GIVEN a user model
    WHEN new user is created
    THEN check the password, active and role is set accordingly
    """
    user = User.create(first_name="John",
                       last_name="Wick",
                       email="john@wick.com",
                       password="random_password")
    db.session.commit()

    assert user.check_password("random_password")
    assert user.password != "random_password"
    assert user.active is True
    assert user.role == UserRole.NEWBIE
