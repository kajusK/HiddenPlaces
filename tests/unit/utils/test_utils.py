"""Unit tests for app.utils. """
from flask import request
from werkzeug.datastructures import MultiDict
from app.utils.utils import get_visitor_ip, random_string


def test_get_visitor_ip_direct(app):
    """Tests getting visitors IP when accessed directly."""
    with app.test_request_context('/'):
        # pylint: disable=assigning-non-slot
        request.remote_addr = "1.2.3.4"
        address = get_visitor_ip()
        assert address == "1.2.3.4"


def test_get_visitor_ip_proxy(app):
    """Tests getting visitors IP when accessed over reverse proxy."""
    with app.test_request_context('/'):
        # pylint: disable=assigning-non-slot
        request.remote_addr = "1.2.3.4"
        request.headers = MultiDict([('X-Forwarded-For', '8.8.8.8')])
        address = get_visitor_ip()
        assert address == "8.8.8.8"


def test_get_visitor_ip_none(app):
    """Tests getting visitors IP when accessed over reverse proxy."""
    with app.test_request_context('/'):
        # pylint: disable=assigning-non-slot
        request.remote_addr = ""
        address = get_visitor_ip()
        assert address is None


def test_random_string():
    """Tests if the function generates random strings of expected length."""
    for i in range(5, 10):
        data = []
        for j in range(10):
            output = random_string(i)
            assert len(output) == i
            data.append(output)
        assert len(set(data)) == 10
