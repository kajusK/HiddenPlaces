"""Generic page functionality testing."""
from flask import request
from flask_login import current_user


def test_page_not_found(client, login_root):
    """
    GIVEN the flask client, user is logged in
    WHEN the user visits non-existent page
    THEN The user is presented with 404 page
    """
    response = client.get('/foo/bar')
    assert response.status_code == 404


def test_login_required(client):
    """
    GIVEN the flask client
    WHEN the user visits non-public page
    THEN The user is redirected to login page with next argument correctly set
    """
    client.get('/location/browse', follow_redirects=True)
    assert request.path == '/user/login'
    assert request.args.get('next') == '/location/browse'


def test_update_last_seen(client, login_root):
    """
    GIVEN The flask client, user is logged in
    WHEN The user visits any page
    THEN The last seen time of the user was updated accordingly
    """
    last_seen = current_user.last_seen
    client.get('/location/browse')
    assert last_seen != current_user.last_seen


def test_logging(app):
    """
    GIVEN the flask application
    WHEN the error is logged to app.logger
    THEN the error is stored in the log file
    """
    app.logger.error("foo bar")
    with open(app.config['LOGGING_LOCATION']) as f:
        assert "foo bar" in f.readlines()[-1]
