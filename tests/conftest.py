import pytest
import tests.helpers as helpers
from sqlalchemy.orm import sessionmaker
from app import create_app
from app.database import db
from app.extensions import mail
from app.user.models import User, Invitation, Ban

Session = sessionmaker()


@pytest.fixture(scope='session')
def app():
    """Createsflask application"""
    app = create_app('tests.config.TestConfig')
    with app.app_context():
        db.create_all()
        yield app


@pytest.fixture(scope='session')
def filled_db(app):
    """Prefills the database with testing data."""
    items = []
    items.append(map(lambda x: User(**x), helpers.users.values()))
    items.append(map(lambda x: Ban(**x), helpers.bans))
    items.append(map(lambda x: Invitation(**x), helpers.invitations.values()))

    for item in items:
        for entry in item:
            db.session.add(entry)
    db.session.commit()


@pytest.fixture
def session(app, monkeypatch):
    """Creates a new database session for test functions."""
    connection = db.engine.connect()
    transaction = connection.begin()

    # Patch Flask-SQLAlchemy to use our connection
    monkeypatch.setattr(db, 'get_engine', lambda *args, **kwargs: connection)
    try:
        yield db
    finally:
        db.session.remove()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(filled_db, app, session):
    """Creates flask testing client."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def outbox(app):
    with mail.record_messages() as outbox:
        yield outbox


@pytest.fixture(scope='session')
def req_context(app):
    with app.test_request_context() as context:
        yield context


@pytest.fixture
def login_root(client):
    """Logs in as root user."""
    user = helpers.users['root']
    helpers.login(client, user['email'], user['password'])


@pytest.fixture
def login_admin(client):
    """Logs in as admin user."""
    user = helpers.users['admin1']
    helpers.login(client, user['email'], user['password'])


@pytest.fixture
def login_moderator(client):
    """Logs in as moderator user."""
    user = helpers.users['moderator1']
    helpers.login(client, user['email'], user['password'])


@pytest.fixture
def login_user(client):
    """Logs in as normal user."""
    user = helpers.users['user1']
    helpers.login(client, user['email'], user['password'])


@pytest.fixture
def login_newbie(client):
    """Logs in as newbie user."""
    user = helpers.users['newbie1']
    helpers.login(client, user['email'], user['password'])
