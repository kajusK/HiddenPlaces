"""Functional test for user invitation functionality."""
import re
from html5validate import validate as validate_html
from app.models.user import Invitation, User, InvitationState
import tests.helpers as helpers


def test_invitation_page(client, login_root):
    """
    GIVEN the flask client, root user logged in
    WHEN invitation page is loaded
    THEN it's correctly rendered and contains valid html data
    """
    response = client.get('/user/invite')
    assert response.status_code == 200
    assert b'form' in response.data
    validate_html(response.data)


def test_invite_by_admin(client, login_admin, outbox):
    """
    GIVEN the flask client, admin user is logged in
    WHEN invitation is requested
    THEN the invitation is created (pre-aproved) and email is sent
    """
    user = User.get_by_email(helpers.users['admin1']['email'])
    data = {
        'name': 'John Wick',
        'email': 'john@wick.com',
        'reason': 'We need him!'
    }

    response = client.post('/user/invite', data=data, follow_redirects=True)
    assert b'invited' in response.data

    invitation = Invitation.get().first()
    assert invitation.email == data['email']
    assert invitation.name == data['name']
    assert invitation.reason == data['reason']
    assert invitation.invited_by == user
    assert invitation.approved_by == user
    assert invitation.state == InvitationState.APPROVED

    assert len(outbox) == 1
    assert 'were invited' in outbox[0].subject
    assert outbox[0].recipients == [data['email']]
    url = re.search(r'href="([^"]*)"', outbox[0].html).group(1)
    token = url.split('/')[-1]
    assert Invitation.check_token(token) == invitation


def test_invite_by_moderator(client, login_moderator, outbox):
    """
    GIVEN the flask client, moderator user is logged in
    WHEN invitation is requested
    THEN the invitation is created (waiting for approval ), email is not sent
    """
    data = {
        'name': 'John Wick',
        'email': 'john@wick.com',
        'reason': 'We need him!'
    }

    response = client.post('/user/invite', data=data, follow_redirects=True)
    assert b'waiting for approval' in response.data

    invitation = Invitation.get().first()
    assert invitation.email == data['email']
    assert invitation.state == InvitationState.WAITING
    assert invitation.approved_by is None
    assert len(outbox) == 0


def test_invite_insufficient_access(client, login_user):
    """
    GIVEN the flask client, normal user is logged in
    WHEN invitation is requested
    THEN the access to invitation form is denied
    """
    data = {
        'name': 'John Wick',
        'email': 'john@wick.com',
        'reason': 'We need him!'
    }

    response = client.post('/user/invite', data=data, follow_redirects=True)
    assert response.status_code == 403

    invitation = Invitation.get().first()
    assert invitation.email != data['email']


def test_invite_already_invited(client, login_root):
    """
    GIVEN the flask client, root user is logged in
    WHEN invitation with already invited email is requested
    THEN the corresponding error is shown and invitation is denied
    """
    data = {
        'name': 'John Wick',
        'email': helpers.invitations['waiting']['email'],
        'reason': 'We need him!'
    }

    response = client.post('/user/invite', data=data, follow_redirects=True)
    assert b'already invited' in response.data


def test_invite_already_registered(client, login_root):
    """
    GIVEN the flask client, root user is logged in
    WHEN invitation with already registered user is requested
    THEN the corresponding error is shown and invitation is denied
    """
    data = {
        'name': 'John Wick',
        'email': helpers.users['moderator1']['email'],
        'reason': 'We need him!'
    }

    response = client.post('/user/invite', data=data, follow_redirects=True)
    assert b'already used by existing user' in response.data
