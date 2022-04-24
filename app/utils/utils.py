"""Various helper utilities."""
import random
from typing import Optional, Any
from flask import request, redirect, session, url_for
from flask import current_app as app
from flask_login import current_user


def get_visitor_ip() -> Optional[str]:
    """Gets visitors IP address

    Takes visitors behind a reverse proxy into account
    Returns:
        IP address string or None if not known
    """
    if 'X-Forwarded-For' in request.headers:
        header = request.headers.getlist("X-Forwarded-For")[0]
        return header.rpartition(' ')[-1]
    return request.remote_addr or None


def random_string(length: int = 10) -> str:
    """Generates a random string (e.g. for password)

    Args:
        length: length of the string
    """
    characters = list(map(chr, range(ord('a'), ord('z')+1)))
    characters += list(map(chr, range(ord('A'), ord('Z')+1)))
    characters += list(map(str, range(0, 10)))
    characters += list("!@#$%^&*()[],./")

    output = ""
    for _ in range(length):
        output += random.choice(characters)
    return output


class Url:
    """Custom URL generator."""
    url: str
    have_access: bool = True

    def __init__(self, url: str):
        """Initialize object with url address."""
        self.url = url

    @classmethod
    def get(cls, endpoint: str, **values: Any):
        """Initialize the url object, same arguments as the url_for."""
        url = cls(url_for(endpoint, **values))

        admin = getattr(app.view_functions[endpoint], 'auth_admin', False)
        moderator = getattr(app.view_functions[endpoint],
                            'auth_moderator', False)

        url.have_access = True
        if admin and not current_user.has_admin_rights():
            url.have_access = False
        if moderator and not current_user.has_moderator_rights():
            url.have_access = False

        return url

    @classmethod
    def for_return(cls, endpoint: str, **value: Any):
        """Stores current url in session for later return."""
        session['return_url'] = request.path
        return cls.get(endpoint, **value)

    @classmethod
    def get_return(cls):
        """Generates an url to return to last with_return call."""
        return cls(session.get('return_url', url_for('page.index')))

    def __str__(self) -> str:
        return self.url


def redirect_return():
    """Redirects back from page with url generated by url_return."""
    return redirect(str(Url.get_return()))
