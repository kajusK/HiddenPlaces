"""Unit tests for app.utils. """
from unittest.mock import patch, mock_open
from urllib.error import URLError
from flask import request
from werkzeug.datastructures import MultiDict
from app.utils import GeoIp, get_visitor_ip, random_string


def test_geo_ip_full():
    """Tests the GeoIp info fetching when all fields are set. """
    data = '{"country_code":"CZ","country_name":"Czechia",' \
           '"city":"Prague","postal":"120 00","latitude":50.0761,' \
           '"longitude":14.4477,"IPv4":"1.2.3.4",' \
           '"state":"Hlavni mesto Praha"}'
    mopen = mock_open(read_data=data.encode('utf-8'))

    with patch('app.utils.urllib.request.urlopen', mopen) as mock:
        info = GeoIp('1.2.3.4')

    mock.assert_called_once_with("https://geolocation-db.com/json/1.2.3.4")
    assert info.valid
    assert info.country == "Czechia"
    assert info.country_code == "CZ"
    assert info.city == "Prague"
    assert info.lat == 50.0761
    assert info.lon == 14.4477


def test_geo_ip_partial():
    """Tests the GeoIp info fetching when not all fields are set. """
    data = '{"country_code":"US","country_name":"United States",' \
           '"city":null,"postal":null,"latitude":37.751,"longitude":-97.822,' \
           '"IPv4":"8.8.8.8","state":null}'
    mopen = mock_open(read_data=data.encode('utf-8'))

    with patch('app.utils.urllib.request.urlopen', mopen) as mock:
        info = GeoIp('8.8.8.8')

    mock.assert_called_once_with("https://geolocation-db.com/json/8.8.8.8")
    assert info.valid
    assert info.country == "United States"
    assert info.country_code == "US"
    assert info.city is None
    assert info.lat == 37.751
    assert info.lon == -97.822


def test_geo_ip_invalid():
    """Tests the GeoIp info fetching when receiving invalid response. """
    mopen = mock_open(read_data='crippled'.encode('utf-8'))
    with patch('app.utils.urllib.request.urlopen', mopen):
        info = GeoIp('8.8.8.8')
    assert not info.valid
    assert info.country is None
    assert info.country_code is None
    assert info.city is None
    assert info.lat is None
    assert info.lon is None


def test_geo_ip_no_response():
    """Tests the GeoIp info fetching when remote site in unreachable. """
    mopen = mock_open(read_data='{}'.encode('utf-8'))
    with patch('app.utils.urllib.request.urlopen', mopen) as mock_url:
        mock_url.side_effect = URLError("foo bar")
        info = GeoIp('8.8.8.8')
    assert not info.valid
    assert info.country is None
    assert info.country_code is None
    assert info.city is None
    assert info.lat is None
    assert info.lon is None


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
