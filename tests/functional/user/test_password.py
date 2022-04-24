"""Functional test for user password changing."""
import re
from html5validate import validate as validate_html
from app.models.user import User
import tests.helpers as helpers


def test_change_password_page(client, login_root):
    """
    GIVEN the flask client and logged in user
    WHEN the change password page is loaded
    THEN it's correctly rendered and contains valid html data
    """
    response = client.get('/user/change_password')
    assert response.status_code == 200
    assert b'form' in response.data
    validate_html(response.data)


def test_forgotten_password_page(client):
    """
    GIVEN the flask client
    WHEN the forgotten password page is loaded
    THEN it's correctly rendered and contains valid html data
    """
    response = client.get('/user/forgotten_password')
    assert response.status_code == 200
    assert b'form' in response.data
    validate_html(response.data)


def test_reset_password_page(client):
    """
    GIVEN the flask client
    WHEN the reset password page is loaded
    THEN it's correctly rendered and contains valid html data
    """
    token = User.get_by_id(0).get_reset_token()
    response = client.get(f'/user/password_reset/{token}')
    assert response.status_code == 200
    assert b'form' in response.data
    validate_html(response.data)


def test_change_password(client, login_root):
    """
    GIVEN the flask client and logged in user
    WHEN user tries to change the password
    THEN its changed correctly
    """
    user = helpers.users['root']
    new_password = "abcd1234EFG,."
    data = {
        'old_password': user['password'],
        'password': new_password,
        'confirm': new_password
    }
    response = client.post('/user/change_password', data=data,
                           follow_redirects=True)
    assert response.status_code == 200
    assert b'was changed' in response.data
    assert User.get_by_email(user['email']).check_password(new_password)


def test_change_password_invalid_old(client, login_root):
    """
    GIVEN the flask client and logged in user
    WHEN user tries to change the password, but enters invalid old password
    THEN the change is rejected
    """
    user = helpers.users['root']
    new_password = "abcd1234EFG,."
    data = {
        'old_password': 'invalid',
        'password': new_password,
        'confirm': new_password
    }
    response = client.post('/user/change_password', data=data,
                           follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid' in response.data
    assert not User.get_by_email(user['email']).check_password(new_password)


def test_forgotten_password(client, outbox):
    """
    GIVEN the flask client and email outbox
    WHEN user requests the forgotten password reset
    THEN the password reset link is set over email and it's valid
    """
    user = helpers.users['root']
    data = {'email': user['email']}
    response = client.post('/user/forgotten_password', data=data,
                           follow_redirects=True)
    assert b'was requested' in response.data

    assert len(outbox) == 1
    assert 'reset request' in outbox[0].subject
    assert outbox[0].recipients == [user['email']]
    url = re.search(r'href="([^"]*)"', outbox[0].html).group(1)
    token = url.split('/')[-1]
    assert User.check_reset_token(token).email == user['email']


def test_reset_password(client):
    """
    GIVEN the flask client
    WHEN user tries to change forgotten password with valid token
    THEN the password is changed
    """
    user = User.get_by_email(helpers.users['root']['email'])
    new_password = "abcd1234EFG,."
    data = {
        'password': new_password,
        'confirm': new_password
    }
    response = client.post(f'/user/password_reset/{user.get_reset_token()}',
                           data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'was changed' in response.data
    assert user.check_password(new_password)


def test_reset_password_invalid_token(client):
    """
    GIVEN the flask client
    WHEN user tries to change forgotten password with invalid token
    THEN the error message is shown
    """
    data = {
        'password': "foo",
        'confirm': "foo"
    }
    response = client.post('/user/password_reset/foo', data=data,
                           follow_redirects=True)
    assert response.status_code == 200
    assert b'no longer valid' in response.data
