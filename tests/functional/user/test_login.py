"""Functional test for user login/logout functionality."""
from flask import request
from html5validate import validate as validate_html
from app.user.models import LoginLog
from app.user.constants import LoginResult
import tests.helpers as helpers


def test_login_page(client):
    """
    GIVEN the flask client
    WHEN login page is loaded
    THEN it's correctly rendered and contains valid html data
    """
    response = client.get('/user/login')
    assert response.status_code == 200
    assert b'form' in response.data
    validate_html(response.data)


def test_login_logout(client):
    """
    GIVEN the flask client
    WHEN the user tries to log in/out
    THEN it's possible to log in with valid password and logout afterwards
    """
    user = helpers.users['root']
    response = helpers.login(client, user['email'], user['password'])
    assert response.status_code == 200
    assert request.path != '/user/login'
    assert b'logged in' in response.data

    log = LoginLog.get().all()[0]
    assert log.email == user['email']
    assert log.result == LoginResult.SUCCESS

    response = helpers.logout(client)
    assert response.status_code == 200
    assert request.path == '/user/login'
    assert b'logged out' in response.data


def test_login_invalid_password(client):
    """
    GIVEN the flask client
    WHEN the user tries to log in with invalid password
    THEN The password is rejected
    """
    user = helpers.users['root']
    response = helpers.login(client, user['email'], 'invalidpassword')
    assert request.path == '/user/login'
    assert b'Invalid email or password' in response.data

    log = LoginLog.get().all()[0]
    assert log.email == user['email']
    assert log.result == LoginResult.INVALID_PASSWORD


def test_login_invalid_user(client):
    """
    GIVEN the flask client
    WHEN the user tries to log in with invalid user account
    THEN The login attempt is rejected
    """
    email = 'invalid@invalid.com'
    response = helpers.login(client, email, 'invalidpassword')
    assert request.path == '/user/login'
    assert b'Invalid email or password' in response.data

    log = LoginLog.get().all()[0]
    assert log.email == email
    assert log.result == LoginResult.INVALID_EMAIL


def test_login_inactive(client):
    """
    GIVEN the flask client
    WHEN the user tries to log in to inactive user account
    THEN The password is rejected
    """
    user = helpers.user_inactive
    response = helpers.login(client, user['email'], user['password'])
    assert request.path == '/user/login'
    assert b'not active' in response.data

    log = LoginLog.get().all()[0]
    assert log.email == user['email']
    assert log.result == LoginResult.NOT_ACTIVE


def test_login_ban_expired(client):
    """
    GIVEN the flask client
    WHEN the user tries to log in to user that was banned before and is ok now
    THEN The user is logged in
    """
    user = helpers.user_ban_expired
    response = helpers.login(client, user['email'], user['password'])
    assert response.status_code == 200
    assert request.path != '/user/login'
    assert b'logged in' in response.data


def test_login_banned_temporary(client):
    """
    GIVEN the flask client
    WHEN the user tries to log in to user that is banned temporary
    THEN The login is rejected
    """
    user = helpers.user_ban_temporary
    response = helpers.login(client, user['email'], user['password'])
    assert response.status_code == 200
    assert request.path == '/user/login'
    assert b'banned until' in response.data

    log = LoginLog.get().all()[0]
    assert log.email == user['email']
    assert log.result == LoginResult.BANNED


def test_login_banned_permanent(client):
    """
    GIVEN the flask client
    WHEN the user tries to log in to user that is banned permanently
    THEN The login is rejected
    """
    user = helpers.user_ban_permanent
    response = helpers.login(client, user['email'], user['password'])
    assert response.status_code == 200
    assert request.path == '/user/login'
    assert b'banned permanently' in response.data

    log = LoginLog.get().all()[0]
    assert log.email == user['email']
    assert log.result == LoginResult.BANNED


def test_login_next_default(client):
    """
    GIVEN the flask client
    WHEN the user logs in
    THEN The user is redirected to default page
    """
    user = helpers.users['root']
    helpers.login(client, user['email'], user['password'])
    assert request.path == '/location/browse'


def test_login_next_default_already_logged(client, login_root):
    """
    GIVEN the flask client, user is logged in
    WHEN the user visits the login page
    THEN The user is redirected to default page
    """
    response = client.get('/user/login', follow_redirects=True)
    assert response.status_code == 200
    assert request.path == '/location/browse'


def test_login_next_valid(client):
    """
    GIVEN the flask client
    WHEN the user logs in with valid next path set
    THEN The user is redirected to next page
    """
    user = helpers.users['root']
    helpers.login(client, user['email'], user['password'],
                  next='%2Fuser%2Fprofile')
    assert request.path == '/user/profile'


def test_login_next_valid_already_logged(client, login_root):
    """
    GIVEN the flask client, user is logged in
    WHEN the user opens login page with valid next path set
    THEN The user is redirected to next page
    """
    response = client.get('/user/login?next=%2Fuser%2Fprofile',
                          follow_redirects=True)
    assert response.status_code == 200
    assert request.path == '/user/profile'


def test_login_next_forbidden(client):
    """
    GIVEN the flask client
    WHEN the user logs in with forbidden (external url) next path set
    THEN The user is redirected to default page
    """
    user = helpers.users['root']
    helpers.login(client, user['email'], user['password'],
                  next='https%3A%2F%2Fgoogle.com')
    assert request.path == '/location/browse'


def test_login_next_invalid(client):
    """
    GIVEN the flask client
    WHEN the user logs in with invalid next path set
    THEN The user is redirected to 404 page
    """
    user = helpers.users['root']
    response = helpers.login(client, user['email'], user['password'],
                             next='%2Ffoo')
    assert response.status_code == 404
    assert request.path == '/foo'
