"""Functional test for user registration functionality."""
from flask import request
from html5validate import validate as validate_html
from app.user.models import Invitation, User
from app.user.constants import UserRole, InvitationState
import tests.helpers as helpers


def test_register_page(client):
    """
    GIVEN the flask client with existing invitation
    WHEN registration page is loaded
    THEN it's correctly rendered and contains valid html data
    """
    invitation = Invitation.get_by_email(
        helpers.invitations['approved']['email'])
    response = client.get(f'/user/register/{invitation.get_token()}')
    assert response.status_code == 200
    assert b'form' in response.data
    validate_html(response.data)


def test_register_user(client):
    """
    GIVEN the flask client with existing invitation
    WHEN user tries to register
    THEN the registration is processed, user is redirected to login page
    """
    invitation = Invitation.get_by_email(
        helpers.invitations['approved']['email'])
    email = 'john@wick.com'
    password = '123abcdEFGH,.'

    data = {
        'first_name': 'John',
        'last_name': 'Wick',
        'email': email,
        'password': password,
        'confirm': password,
        'rules_agree': True
    }
    response = client.post(f'/user/register/{invitation.get_token()}',
                           data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'registered' in response.data
    assert request.path == '/user/login'

    user = User.get_by_email(email)
    assert user.first_name == 'John'
    assert user.last_name == 'Wick'
    assert user.email == email
    assert user.role == UserRole.NEWBIE
    assert user.check_password(password)
    assert user.active

    assert invitation.user == user
    assert invitation.state == InvitationState.REGISTERED


def test_register_user_already_exist(client):
    """
    GIVEN the flask client with existing invitation
    WHEN user tries to register with email that is already used
    THEN the registration fails with corresponding error
    """
    invitation = Invitation.get_by_email(
        helpers.invitations['approved']['email'])
    email = helpers.users['root']['email']

    data = {
        'first_name': 'John',
        'last_name': 'Wick',
        'email': email,
        'password': '123asdbSDA',
        'confirm': '123asdbSDA',
        'rules_agree': True
    }
    response = client.post(f'/user/register/{invitation.get_token()}',
                           data=data, follow_redirects=True)
    assert request.path.startswith('/user/register')
    assert b'already used' in response.data


def test_invitation_invalid_state(client, subtests):
    """
    GIVEN the flask client with existing invitation
    WHEN user invitation is not in approved state
    THEN the registration fails with corresponding error
    """
    types = ['waiting', 'denied', 'registered']
    invitations = []
    for inv_type in types:
        invitations.append(Invitation.get_by_email(
            helpers.invitations[inv_type]['email']))

    for invitation in invitations:
        with subtests.test(state=invitation.state):
            data = {
                'first_name': 'John',
                'last_name': 'Wick',
                'email': 'john@wick.com',
                'password': '123asdbSDA',
                'confirm': '123asdbSDA',
                'rules_agree': True
            }
            response = client.post(
                f'/user/register/{invitation.get_token()}', data=data,
                follow_redirects=True)
            assert request.path == '/user/login'
            assert b'no longer valid' in response.data


def test_invitation_invalid_token(client):
    """
    GIVEN the flask client with existing invitation
    WHEN user supplies invalid registration token
    THEN the registration fails with corresponding error
    """
    response = client.get('/user/register/foobar', follow_redirects=True)
    assert response.status_code == 200
    assert request.path == '/user/login'
    assert b'no longer valid' in response.data


def test_register_user_page_rules(client):
    """
    GIVEN the flask client with existing invitation
    WHEN user tries to register without rules agree checked
    THEN the registration fails with corresponding error
    """
    invitation = Invitation.get_by_email(
        helpers.invitations['approved']['email'])
    data = {
        'first_name': 'John',
        'last_name': 'Wick',
        'email': 'john@wick.com',
        'password': '123asdbSDA',
        'confirm': '123asdbSDA',
    }
    response = client.post(f'/user/register/{invitation.get_token()}',
                           data=data, follow_redirects=True)
    assert request.path.startswith('/user/register')
    assert b'must agree with page rules' in response.data


def test_register_user_invalid_password(client):
    """
    GIVEN the flask client with existing invitation
    WHEN user tries to register with unacceptable password
    THEN the registration fails with corresponding error
    """
    invitation = Invitation.get_by_email(
        helpers.invitations['approved']['email'])
    data = {
        'first_name': 'John',
        'last_name': 'Wick',
        'email': 'john@wick.com',
        'password': 'ab',
        'confirm': 'cd',
        'rules_agree': True
    }
    response = client.post(f'/user/register/{invitation.get_token()}',
                           data=data, follow_redirects=True)
    assert b'Passwords must match' in response.data
    assert request.path.startswith('/user/register')

    data['confirm'] = 'ab'
    response = client.post(f'/user/register/{invitation.get_token()}',
                           data=data, follow_redirects=True)
    assert b'Password must have' in response.data
    assert request.path.startswith('/user/register')
