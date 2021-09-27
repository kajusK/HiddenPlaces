import pytest
import tempfile
import os
import flask
from app import create_app
from app.database import db as _db
from app.user.models import User
from .helpers import user1, user2, login, logout


@pytest.fixture(scope='session')
def app():
    db_fd, db_path = tempfile.mkstemp()
    overrides = {
        'SQLALCHEMY_DATABASE_URI': f"sqlite:///{db_path}",
        'SQLALCHEMY_ECHO': False,
        'WTF_CSRF_ENABLED': False
    }
    app = create_app(config_override=overrides)
    _db.init_app(app)
    yield app
    os.close(db_fd)
    os.unlink(db_path)


#@pytest.fixture(scope='session')
#def client(app):
#    item1 = User(
#        username=user1['name'],
#        email=user1['email'],
#        password=user1['pass']
#    )
#    item2 = User(
#        username=user2['name'],
#        email=user2['email'],
#        password=user2['pass'],
#        active=False
#    )
#    with app.test_client() as client:
#        with app.app_context():
#            _db.drop_all()
#            _db.create_all()
#            _db.session.add(item1)
#            _db.session.add(item2)
#            _db.session.commit()
#            yield client
#
#
#@pytest.fixture
#def login_default_user(client):
#    login(client, user1['name'], user1['pass'])
#    yield
#    logout(client)
