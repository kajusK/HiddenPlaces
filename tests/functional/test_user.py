from tests.helpers import login, logout, user1, user2
from flask import request
from app.user.models import User


def send_register(client, username, password1, password2, email):
    """ Fill the registration form """
    data = {
        'username': username,
        'password': password1,
        'confirm': password2,
        'email': email
    }
    return client.post('/user/register/', data=data, follow_redirects=True)


def test_login_logout(client):
    """ Test user is able to login and logout """
    # Valid login
    ret = login(client, user1['name'], user1['pass'])
    assert b'logged in' in ret.data

    ret = logout(client)
    assert b'logged out' in ret.data

    # Login to non-active user
    ret = login(client, user2['name'], user2['pass'])
    print(ret.data)
    assert b'not active' in ret.data

    # Invalid password
    ret = login(client, user1['name'], user1['pass']+'abcd')
    assert b'Invalid' in ret.data

    # Invalid user
    ret = login(client, 'somerandomuser', user1['pass'])
    assert b'Invalid' in ret.data


def test_login_next(client):
    """ Test user is redirected to next page upon login if next defined """
    login(client, user1['name'], user1['pass'])
    assert request.path == '/'
    # already logged in redirect
    client.get('/user/login?next=%2Fuser', follow_redirects=True)
    assert request.path == '/user/'
    client.get('/user/login', follow_redirects=True)
    assert request.path == '/'
    logout(client)

    login(client, user1['name'], user1['pass'], next='%2Fuser')
    assert request.path == '/user/'
    logout(client)

    # invalid next
    login(client, user1['name'], user1['pass'], next='https%3A%2F%2Fgoogle.com')
    assert request.path == '/'
    logout(client)
    res = login(client, user1['name'], user1['pass'], next='foo%2Fbar')
    assert res.status_code == 404
    logout(client)


def test_invalid_access(client):
    """ Test certain pages are not accessible when not logged in """
    logout(client)
    pages = ['/user/', '/user/logout/']
    for page in pages:
        client.get(page, follow_redirects=True)
        assert request.path == '/user/login/'
        assert request.args.get('next') == page


def test_valid_access(client, login_default_user):
    """ Test certain pages are accessible only when logged in """
    pages = ['/user/profile', '/user/logout']
    for page in pages:
        client.get(page)
        assert request.path == page


def test_register(client):
    """ Test register page is working as expected """
    res = send_register(client, user1['name'], '123456', '123456',
                        'foo@bar.com')
    print(res.data)
    assert b'Username already taken' in res.data

    res = send_register(client, 'foobar', '123456', '123456',
                        user1['email'])
    assert b'Email already taken' in res.data

    res = send_register(client, 'foobar', '123456', '123456',
                        'blah')
    print(res.data)
    assert b'Invalid email' in res.data

    res = send_register(client, 'foobar', '123456', 'abcdef',
                        'foo@bar')
    assert b'must match' in res.data

    res = send_register(client, 'foobar', '123456', '123456',
                        'foo@bar.cz')
    assert b'registered' in res.data
    assert request.path == '/user/login/'
    user = User.query.filter_by(username='foobar').first()
    assert user.username == 'foobar'
    assert user.email == 'foo@bar.cz'
    assert user.active
