"""Helpers for testing."""
from datetime import datetime, timedelta
from app.user.constants import UserRole, InvitationState

users = dict(
    root={'first_name': 'Root',
          'last_name': 'Superuser',
          'password': 'Ro0TP4S$',
          'email': 'root@page.com',
          'id': 0,
          'role': UserRole.ROOT},
    admin1={'first_name': 'First',
            'last_name': 'Admin',
            'password': '5rX9tOxVCIv4',
            'email': 'admin@page.com',
            'role': UserRole.ADMIN},
    admin2={'first_name': 'Second',
            'last_name': 'Admin',
            'password': '6rX9tOxVCIv4',
            'email': 'admin2@page.com',
            'role': UserRole.ADMIN},
    moderator1={'first_name': 'First',
                'last_name': 'Moderator',
                'password': 'HaNpRuCCzc7g',
                'email': 'moderator@page.com',
                'role': UserRole.MODERATOR},
    moderator2={'first_name': 'Second',
                'last_name': 'Moderator',
                'password': 'PaRpRuCCzc7g',
                'email': 'moderator2@page.com',
                'role': UserRole.MODERATOR},
    contributor1={'first_name': 'First',
                  'last_name': 'Contributor',
                  'password': 'D8PulC6XuXEB',
                  'email': 'contributor@page.com',
                  'role': UserRole.CONTRIBUTOR},
    contributor2={'first_name': 'Second',
                  'last_name': 'Contributor',
                  'password': 'B8iulC6XuXEB',
                  'email': 'contributor2@page.com',
                  'role': UserRole.CONTRIBUTOR},
    user1={'first_name': 'First',
           'last_name': 'User',
           'password': 'GpTsS5jOxCwz',
           'email': 'user@page.com',
           'role': UserRole.USER},
    user2={'first_name': 'Second',
           'last_name': 'User',
           'password': 'NpPsS5jOxCwz',
           'email': 'user2@page.com',
           'role': UserRole.USER},
    newbie1={'first_name': 'First',
             'last_name': 'Newbie',
             'password': 'GpTsS5jOxCwz',
             'email': 'newbie@page.com',
             'role': UserRole.NEWBIE},
    newbie2={'first_name': 'Second',
             'last_name': 'Newbie',
             'password': 'dsa7TsS5jOxCwz',
             'email': 'newbie2@page.com',
             'role': UserRole.NEWBIE}
)

user_ban_expired = users['moderator2']
user_ban_temporary = users['user2']
user_ban_permanent = users['newbie2']
user_inactive = users['contributor2']
user_inactive['active'] = False

bans = [
    {
        'reason': 'Ban expired',
        'until': datetime.utcnow() - timedelta(days=1),
        'permanent': False,
        'creator_id': 0,
        'user_id': list(users.values()).index(user_ban_expired)
    },
    {
        'reason': 'Ban will expire',
        'until': datetime.utcnow() + timedelta(days=1),
        'permanent': False,
        'creator_id': 1,
        'user_id': list(users.values()).index(user_ban_temporary)
    },
    {
        'reason': 'Permanent ban',
        'until': datetime.utcnow() - timedelta(days=1),
        'permanent': True,
        'creator_id': 2,
        'user_id': list(users.values()).index(user_ban_permanent)
    },
]

invitations = dict(
    waiting={'email': 'foo@bar.com',
             'name': 'John Wick',
             'reason': 'Professional needed',
             'invited_by_id': 0},
    denied={'email': 'foo2@bar.com',
            'name': 'That Joker',
            'reason': 'Little bit of insanity needed',
            'invited_by_id': 1,
            'state': InvitationState.DENIED},
    approved={'email': 'foo3@bar.com',
              'name': 'The Witcher',
              'reason': 'Your blade is needed, my Lord',
              'invited_by_id': 3,
              'state': InvitationState.APPROVED},
    registered={'email': 'newbie2@page.com',
                'name': 'My Friend',
                'reason': 'Friend of mine',
                'invited_by_id': 2,
                'state': InvitationState.REGISTERED,
                'user_id': 4},
)


def login(client, email, password, next=None):
    data = {
        'email': email,
        'password': password,
        'remember_me': False
    }
    path = '/user/login'
    if next:
        path += f'?next={next}'
    return client.post(path, data=data, follow_redirects=True)


def logout(client):
    return client.get('/user/logout', follow_redirects=True)
