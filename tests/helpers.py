user1 = {
    'name': 'user1',
    'pass': '123456',
    'email': 'user1@foo.bar'
}

user2 = {
    'name': 'user2',
    'pass': 'abcdef',
    'email': 'user2@foo.bar'
}


def login(client, username, password, next=None):
    data = {
        'username': username,
        'password': password,
        'remember_me': False
    }
    path = '/user/login/'
    if next:
        path += f'?next={next}'
    return client.post(path, data=data, follow_redirects=True)


def logout(client):
    return client.get('/user/logout', follow_redirects=True)
