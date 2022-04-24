"""Functional test for user profiles functionality."""
from flask_login import current_user
from html5validate import validate as validate_html


def test_profile_our_page(client, login_root):
    """
    GIVEN the flask client, root user logged in
    WHEN profile page is loaded
    THEN it's correctly rendered and contains valid html data
    """
    response = client.get('/user/profile')
    assert response.status_code == 200
    validate_html(response.data)


def test_profile_user_page(client, login_root):
    """
    GIVEN the flask client, root user logged in
    WHEN other user's profile page is loaded
    THEN it's correctly rendered and contains valid html data
    """
    response = client.get('/user/1')
    assert response.status_code == 200
    validate_html(response.data)


def test_profile_nonexistent(client, login_root):
    """
    GIVEN the flask client, root user logged in
    WHEN Non existent user profile is requested
    THEN 404 is returned
    """
    response = client.get('/user/1000')
    assert response.status_code == 404


def test_profile_edit(client, login_root):
    """
    GIVEN the flask client, root user logged in
    WHEN User edits the profile
    THEN the profile is updated accordingly
    """
    data = {
        'about': '**foo** [bar](blah)'
    }
    response = client.post('/user/edit', data=data, follow_redirects=True)
    assert b'changes were saved' in response.data

    assert current_user.about == data['about']
    response = client.get('/user/profile')
    assert b'<strong>foo</strong> <a href="blah">bar</a>' in response.data
